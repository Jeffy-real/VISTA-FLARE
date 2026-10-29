"""Backend-only adapters for supported external job providers.

Every adapter returns provider-neutral records. Credentials are read only from
server settings and are never returned by this module or an API response.
"""
from __future__ import annotations

import html
import re
import time
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Iterable

import httpx
import pandas as pd

from backend.app.core.config import Settings, get_settings

PROJECT_ROOT = Path(__file__).resolve().parents[3]
SEED_DIR = PROJECT_ROOT / "data" / "seed"


class ProviderFetchError(RuntimeError):
    """A safe provider-level failure suitable for an ingestion run record."""


class BaseJobProvider(ABC):
    name: str
    display_name: str
    requires_credentials: bool = False
    min_refresh_minutes: int = 0

    def __init__(self) -> None:
        self.last_error: str | None = None

    @property
    @abstractmethod
    def configured(self) -> bool:
        """Whether every required server-side setting is present, not a health claim."""

    @abstractmethod
    def fetch_jobs(self, limit: int = 50) -> list[dict[str, Any]]:
        """Fetch and validate provider data at the boundary."""


class HTTPJobProvider(BaseJobProvider):
    """Synchronous transport with capped retries and rate-limit handling."""

    def __init__(self, settings: Settings | None = None) -> None:
        super().__init__()
        self.settings = settings or get_settings()

    def _get_json(self, url: str, *, params: dict[str, Any] | None = None) -> dict[str, Any]:
        attempts = max(0, self.settings.job_provider_max_retries) + 1
        last_message = "provider request failed"
        with httpx.Client(timeout=max(1.0, self.settings.job_provider_timeout_seconds), follow_redirects=True) as client:
            for attempt in range(attempts):
                try:
                    response = client.get(url, params=params, headers={"Accept": "application/json", "User-Agent": "VistaFlare/1.0"})
                    if response.status_code == 429:
                        retry_after = response.headers.get("Retry-After")
                        pause = min(10.0, float(retry_after)) if retry_after and retry_after.isdigit() else min(4.0, 0.5 * (2 ** attempt))
                        last_message = "rate limited"
                        if attempt + 1 < attempts:
                            time.sleep(pause)
                            continue
                        raise ProviderFetchError(last_message)
                    if 500 <= response.status_code < 600:
                        last_message = f"upstream HTTP {response.status_code}"
                        if attempt + 1 < attempts:
                            time.sleep(min(4.0, 0.5 * (2 ** attempt)))
                            continue
                        raise ProviderFetchError(last_message)
                    response.raise_for_status()
                    payload = response.json()
                    if not isinstance(payload, dict):
                        raise ProviderFetchError("invalid JSON response shape")
                    return payload
                except (httpx.HTTPError, ValueError, ProviderFetchError) as exc:
                    last_message = str(exc) or exc.__class__.__name__
                    if attempt + 1 < attempts and not isinstance(exc, ProviderFetchError):
                        time.sleep(min(4.0, 0.5 * (2 ** attempt)))
                        continue
                    break
        raise ProviderFetchError(last_message)


class LocalSeedJobProvider(BaseJobProvider):
    """Local fixture catalog; it is never labelled as an external refresh."""
    name = "seed"
    display_name = "Vista Flare seed catalog"

    def __init__(self, seed_path: Path | None = None) -> None:
        super().__init__()
        self.seed_path = seed_path or (SEED_DIR / "jobs.csv")

    @property
    def configured(self) -> bool:
        return self.seed_path.exists()

    def fetch_jobs(self, limit: int = 200) -> list[dict[str, Any]]:
        if not self.seed_path.exists():
            self.last_error = "seed catalog unavailable"
            return []
        return pd.read_csv(self.seed_path).head(limit).to_dict(orient="records")


class ArbeitnowJobProvider(HTTPJobProvider):
    """Arbeitnow public API adapter. Its documented public API needs no key."""
    name = "arbeitnow"
    display_name = "Arbeitnow"
    API_URL = "https://www.arbeitnow.com/api/job-board-api"

    @property
    def configured(self) -> bool:
        return True

    def fetch_jobs(self, limit: int = 50) -> list[dict[str, Any]]:
        self.last_error = None
        records: list[dict[str, Any]] = []
        next_url: str | None = self.API_URL
        pages = 0
        while next_url and len(records) < limit and pages < 10:
            try:
                payload = self._get_json(next_url)
            except ProviderFetchError as exc:
                self.last_error = str(exc)
                return []
            data = payload.get("data")
            if not isinstance(data, list):
                self.last_error = "invalid response: data is not a list"
                return []
            for item in data:
                if not isinstance(item, dict) or not item.get("slug") or not item.get("title"):
                    continue
                records.append({
                    "provider_id": item["slug"], "company_name": item.get("company_name") or "Unknown",
                    "job_title": item["title"], "normalized_role": item["title"], "employment_type": "Full-time",
                    "work_mode": "Remote" if item.get("remote") else "On-site / unspecified",
                    "location": item.get("location") or "Unspecified", "country": "Unspecified",
                    "city": item.get("location") or None, "required_skills": item.get("tags") or [],
                    "posting_date": item.get("created_at"), "source": "Arbeitnow", "source_url": item.get("url"),
                    "description": item.get("description"), "raw_metadata": item,
                })
                if len(records) >= limit:
                    break
            links = payload.get("links") if isinstance(payload.get("links"), dict) else {}
            next_url = links.get("next") if isinstance(links.get("next"), str) else None
            pages += 1
        return records


def _strip_html(value: Any) -> str | None:
    if not value:
        return None
    return html.unescape(re.sub(r"<[^>]+>", " ", str(value))).strip()


def _parse_salary(value: Any) -> tuple[float | None, float | None, str | None, str | None]:
    """Conservative parser: ambiguous compensation stays unknown."""
    text = str(value or "").strip()
    if not text:
        return None, None, None, None
    numbers = [float(part.replace(",", "")) for part in re.findall(r"\d[\d,]*(?:\.\d+)?", text)]
    if not numbers:
        return None, None, None, None
    currency = "USD" if "$" in text or "USD" in text.upper() else None
    lowered = text.lower()
    period = "hour" if "hour" in lowered or "/hr" in lowered else "year" if "year" in lowered or "annual" in lowered else None
    return min(numbers), max(numbers), currency, period


class RemotiveJobProvider(HTTPJobProvider):
    """Remotive adapter preserving the mandatory attribution and listing URL."""
    name = "remotive"
    display_name = "Remotive"
    API_URL = "https://remotive.com/api/remote-jobs"
    # Public documentation advises a maximum of four pulls per day.
    min_refresh_minutes = 360

    @property
    def configured(self) -> bool:
        return True

    def fetch_jobs(self, limit: int = 50) -> list[dict[str, Any]]:
        self.last_error = None
        try:
            payload = self._get_json(self.API_URL, params={"limit": max(1, min(limit, 100))})
        except ProviderFetchError as exc:
            self.last_error = str(exc)
            return []
        jobs = payload.get("jobs")
        if not isinstance(jobs, list):
            self.last_error = "invalid response: jobs is not a list"
            return []
        results = []
        for item in jobs:
            if not isinstance(item, dict) or item.get("id") is None or not item.get("title"):
                continue
            low, high, currency, period = _parse_salary(item.get("salary"))
            results.append({
                "provider_id": item["id"], "company_name": item.get("company_name") or "Unknown",
                "job_title": item["title"], "normalized_role": item["title"], "job_category": item.get("category"),
                "employment_type": (item.get("job_type") or "").replace("_", " ").title() or None,
                "work_mode": "Remote", "location": item.get("candidate_required_location") or "Remote",
                "country": item.get("candidate_required_location") or "Remote", "salary_min": low, "salary_max": high,
                "salary_currency": currency, "salary_period": period, "posting_date": item.get("publication_date"),
                "source": "Remotive", "source_url": item.get("url"), "description": _strip_html(item.get("description")),
                "raw_metadata": item,
            })
        return results


class AdzunaJobProvider(HTTPJobProvider):
    """Adzuna adapter using its documented app_id/app_key server-side auth."""
    name = "adzuna"
    display_name = "Adzuna"
    API_ROOT = "https://api.adzuna.com/v1/api/jobs"

    @property
    def configured(self) -> bool:
        return bool(self.settings.adzuna_app_id and self.settings.adzuna_app_key)

    def fetch_jobs(self, limit: int = 50) -> list[dict[str, Any]]:
        self.last_error = None
        if not self.configured:
            self.last_error = "missing required Adzuna credentials"
            return []
        results: list[dict[str, Any]] = []
        page = 1
        page_size = max(1, min(self.settings.job_provider_page_size, 50, limit))
        while len(results) < limit and page <= 10:
            params: dict[str, Any] = {
                "app_id": self.settings.adzuna_app_id, "app_key": self.settings.adzuna_app_key,
                "results_per_page": page_size, "content-type": "application/json",
            }
            if self.settings.adzuna_query:
                params["what"] = self.settings.adzuna_query
            try:
                payload = self._get_json(f"{self.API_ROOT}/{self.settings.adzuna_country}/search/{page}", params=params)
            except ProviderFetchError as exc:
                self.last_error = str(exc)
                return []
            rows = payload.get("results")
            if not isinstance(rows, list):
                self.last_error = "invalid response: results is not a list"
                return []
            for item in rows:
                if not isinstance(item, dict) or item.get("id") is None or not item.get("title"):
                    continue
                company = item.get("company") if isinstance(item.get("company"), dict) else {}
                location = item.get("location") if isinstance(item.get("location"), dict) else {}
                category = item.get("category") if isinstance(item.get("category"), dict) else {}
                results.append({
                    "provider_id": item["id"], "company_name": company.get("display_name") or "Unknown",
                    "job_title": item["title"], "normalized_role": item.get("title"), "job_category": category.get("label"),
                    "location": location.get("display_name"), "country": self.settings.adzuna_country.upper(),
                    "salary_min": item.get("salary_min"), "salary_max": item.get("salary_max"), "salary_period": "year",
                    "posting_date": item.get("created"), "source": "Adzuna", "source_url": item.get("redirect_url"),
                    "description": _strip_html(item.get("description")), "raw_metadata": item,
                })
                if len(results) >= limit:
                    break
            if len(rows) < page_size:
                break
            page += 1
        return results


def configured_external_providers(settings: Settings | None = None) -> list[BaseJobProvider]:
    """Return only providers eligible for a real request, never a seed fallback."""
    resolved = settings or get_settings()
    candidates: list[BaseJobProvider] = [ArbeitnowJobProvider(resolved), RemotiveJobProvider(resolved), AdzunaJobProvider(resolved)]
    return [provider for provider in candidates if provider.configured]


def provider_catalog(settings: Settings | None = None) -> Iterable[BaseJobProvider]:
    resolved = settings or get_settings()
    return (ArbeitnowJobProvider(resolved), RemotiveJobProvider(resolved), AdzunaJobProvider(resolved))
