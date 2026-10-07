"""Job data provider abstraction supporting local seeds and external job sources."""
from __future__ import annotations

import json
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, List, Optional

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[3]
SEED_DIR = PROJECT_ROOT / "data" / "seed"


class BaseJobProvider(ABC):
    """Abstract base class for job data providers."""

    @abstractmethod
    def fetch_jobs(self, limit: int = 50) -> List[dict[str, Any]]:
        """Fetch job postings."""
        pass


class LocalSeedJobProvider(BaseJobProvider):
    """Fallback and local seed provider reading from data/seed/jobs.csv."""

    def __init__(self, seed_path: Optional[Path] = None):
        self.seed_path = seed_path or (SEED_DIR / "jobs.csv")

    def fetch_jobs(self, limit: int = 200) -> List[dict[str, Any]]:
        if not self.seed_path.exists():
            return []
        df = pd.read_csv(self.seed_path)
        return df.head(limit).to_dict(orient="records")


class ArbeitnowJobProvider(BaseJobProvider):
    """Fetches public tech job listings from Arbeitnow API (free, open, no auth required)."""

    API_URL = "https://www.arbeitnow.com/api/job-board-api"

    def fetch_jobs(self, limit: int = 50) -> List[dict[str, Any]]:
        import httpx

        try:
            with httpx.Client(timeout=10.0) as client:
                response = client.get(self.API_URL)
                if response.status_code != 200:
                    return []
                data = response.json()
                items = data.get("data", [])
                standardized = []
                for item in items[:limit]:
                    standardized.append(
                        {
                            "company_name": item.get("company_name", "Unknown"),
                            "job_title": item.get("title", ""),
                            "normalized_role": item.get("title", ""),
                            "job_category": "Software Development",
                            "employment_type": "Full-time",
                            "experience_level": "Mid",
                            "work_mode": "Remote" if item.get("remote") else "Hybrid",
                            "location": item.get("location", "Remote"),
                            "country": "Global",
                            "city": item.get("location", "Remote"),
                            "salary_min": None,
                            "salary_max": None,
                            "salary_currency": "USD",
                            "salary_period": "yearly",
                            "required_skills": ", ".join(item.get("tags", [])),
                            "posting_date": item.get("created_at", "2024-01-01")[:10],
                            "source": "Arbeitnow API",
                            "source_url": item.get("url", ""),
                        }
                    )
                return standardized
        except Exception:
            # Safe network failure fallback
            return []


class CompositeJobProvider(BaseJobProvider):
    """Combines external provider with automatic fallback to local seed data."""

    def __init__(self):
        self.local_provider = LocalSeedJobProvider()
        self.external_provider = ArbeitnowJobProvider()

    def fetch_jobs(self, limit: int = 100, use_external: bool = False) -> List[dict[str, Any]]:
        if use_external:
            ext_jobs = self.external_provider.fetch_jobs(limit=limit)
            if ext_jobs:
                return ext_jobs
        return self.local_provider.fetch_jobs(limit=limit)
