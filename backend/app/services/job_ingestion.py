"""Provider ingestion, normalization, deduplication, and durable upserts."""
from __future__ import annotations

import json
import threading
from datetime import datetime, timedelta, timezone
from typing import Any

from sqlalchemy.orm import Session

from backend.app.core.config import get_settings
from backend.app.models.database_models import (
    AlertPreference, IngestionRun, Job, JobChangeEvent, JobObservation,
    Notification, ProviderHealth, Roadmap, SavedJob,
)
from backend.app.services.job_provider import BaseJobProvider, configured_external_providers

# The DB run check below covers shared deployments; this keeps in-process manual
# and scheduled requests from racing before SQLite has written its status row.
_lock = threading.Lock()


def _now() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)


def _error_category(value: str | None) -> str | None:
    if not value:
        return None
    lowered = value.lower()
    if "credential" in lowered or "unauthor" in lowered or "forbidden" in lowered:
        return "authentication"
    if "rate" in lowered or "429" in lowered:
        return "rate_limited"
    if "timeout" in lowered or "connect" in lowered or "network" in lowered:
        return "network"
    if "invalid" in lowered or "json" in lowered:
        return "invalid_response"
    return "provider_error"


def normalize_job(raw: dict[str, Any], provider_name: str, source_kind: str = "external") -> dict[str, Any] | None:
    """Convert provider records to the Job shape; malformed records are skipped."""
    if not isinstance(raw, dict):
        return None
    title = str(raw.get("job_title") or raw.get("title") or "").strip()
    provider_id = raw.get("provider_id") or raw.get("id") or raw.get("slug") or raw.get("url")
    if not title or provider_id is None:
        return None
    tags = raw.get("required_skills", raw.get("tags", []))
    if isinstance(tags, (list, tuple)):
        tags = ", ".join(str(x) for x in tags if x is not None)
    metadata = raw.get("raw_metadata", raw)
    try:
        raw_metadata = json.dumps(metadata, default=str) if not isinstance(metadata, str) else metadata
    except (TypeError, ValueError):
        raw_metadata = None
    return {
        "provider_name": provider_name, "provider_id": str(provider_id), "source_kind": source_kind,
        "source_url": raw.get("source_url") or raw.get("url"), "description": raw.get("description"),
        "raw_metadata": raw_metadata, "company_name": raw.get("company_name") or raw.get("company") or "Unknown",
        "job_title": title, "normalized_role": raw.get("normalized_role") or title,
        "job_category": raw.get("job_category"), "employment_type": raw.get("employment_type"),
        "experience_level": raw.get("experience_level"), "work_mode": raw.get("work_mode"),
        "location": raw.get("location"), "country": raw.get("country"), "city": raw.get("city"),
        "salary_min": raw.get("salary_min"), "salary_max": raw.get("salary_max"),
        "salary_currency": raw.get("salary_currency"), "salary_period": raw.get("salary_period"),
        "required_skills": tags, "posting_date": str(raw.get("posting_date"))[:32] if raw.get("posting_date") else None,
        "source": raw.get("source") or provider_name,
    }


def _set_health(db: Session, provider_name: str, *, status: str, checked: datetime,
                success: bool = False, error: str | None = None) -> ProviderHealth:
    health = db.query(ProviderHealth).filter_by(provider_name=provider_name).first()
    if not health:
        health = ProviderHealth(provider_name=provider_name)
    health.status = status
    health.last_checked = checked
    health.last_error = _error_category(error)
    if success:
        health.last_success = checked
        health.last_error = None
        health.consecutive_failures = 0
    elif status != "throttled":
        health.consecutive_failures = (health.consecutive_failures or 0) + 1
    db.add(health)
    return health


def _changed_fields(job: Job, item: dict[str, Any]) -> bool:
    return any(getattr(job, field, None) != item.get(field) for field in (
        "salary_min", "salary_max", "salary_currency", "salary_period", "required_skills",
        "job_title", "description", "source_url", "employment_type", "work_mode",
    ))


def ingest_jobs(db: Session, provider: Any, provider_name: str = "arbeitnow", limit: int = 100,
                source_kind: str = "external", stale_after_hours: int | None = None,
                min_refresh_minutes: int | None = None) -> dict[str, Any]:
    """Fetch and upsert one provider atomically; failed pulls do not delete cached jobs."""
    checked = _now()
    if not _lock.acquire(blocking=False):
        return {"status": "busy", "provider": provider_name, "checked": checked.isoformat(), "upserted": 0}
    try:
        active_run = db.query(IngestionRun).filter(
            IngestionRun.provider_name == provider_name, IngestionRun.status == "running"
        ).first()
        if active_run:
            return {"status": "busy", "provider": provider_name, "checked": checked.isoformat(), "upserted": 0}

        health = db.query(ProviderHealth).filter_by(provider_name=provider_name).first()
        refresh_window = min_refresh_minutes if min_refresh_minutes is not None else int(getattr(provider, "min_refresh_minutes", 0) or 0)
        if health and health.last_success and refresh_window and checked - health.last_success < timedelta(minutes=refresh_window):
            _set_health(db, provider_name, status="throttled", checked=checked)
            db.commit()
            return {"status": "throttled", "provider": provider_name, "checked": checked.isoformat(), "upserted": 0}

        run = IngestionRun(provider_name=provider_name, started_at=checked, status="running")
        db.add(run)
        db.flush()
        try:
            records = provider.fetch_jobs(limit=limit)
        except Exception as exc:
            records = []
            provider.last_error = f"{exc.__class__.__name__}"
        if getattr(provider, "last_error", None):
            run.status = "failed"; run.completed_at = _now(); run.error = _error_category(provider.last_error)
            _set_health(db, provider_name, status="unhealthy", checked=checked, error=provider.last_error)
            db.commit()
            return {"status": "failed", "provider": provider_name, "error": run.error, "upserted": 0}
        if not isinstance(records, list):
            run.status = "failed"; run.completed_at = _now(); run.error = "invalid_response"
            _set_health(db, provider_name, status="unhealthy", checked=checked, error=run.error)
            db.commit()
            return {"status": "failed", "provider": provider_name, "error": run.error, "upserted": 0}

        run.fetched_count = len(records)
        normalized: list[dict[str, Any]] = []
        seen: set[tuple[str, str]] = set()
        for raw in records:
            item = normalize_job(raw, provider_name, source_kind)
            key = (provider_name, item["provider_id"]) if item else None
            if item and key not in seen:
                seen.add(key)
                normalized.append(item)

        created_count = 0
        updated_count = 0
        for item in normalized:
            job = db.query(Job).filter(Job.provider_name == provider_name, Job.provider_id == item["provider_id"]).first()
            if job is None:
                job = Job(**item, first_seen=checked)
                db.add(job)
                db.flush()
                event_type = "new"
                created_count += 1
            else:
                event_type = "updated" if _changed_fields(job, item) else None
                for key, value in item.items():
                    setattr(job, key, value)
                if event_type:
                    updated_count += 1
            job.last_seen = checked
            job.last_checked = checked
            job.active = source_kind != "seed"
            job.stale = False
            db.add(JobObservation(job_id=job.id, observed_at=checked, salary_min=job.salary_min,
                                  salary_max=job.salary_max, active=job.active, required_skills=job.required_skills))
            if event_type:
                event = JobChangeEvent(
                    job_id=job.id, event_type=event_type, detected_at=checked,
                    details=json.dumps({"title": job.job_title}), dedupe_key=f"{job.id}:{event_type}:{checked.isoformat()}",
                )
                db.add(event)
                db.flush()
                _create_alerts(db, event, job)

        hours = get_settings().ingestion_stale_after_hours if stale_after_hours is None else stale_after_hours
        cutoff = checked - timedelta(hours=max(0, hours))
        # Only a complete successful pull reaches this block; a partial/failed
        # response can never deactivate otherwise valid cached listings.
        stale_marked = db.query(Job).filter(
            Job.provider_name == provider_name, Job.source_kind == source_kind, Job.last_seen < cutoff,
        ).update({"stale": True, "active": False}, synchronize_session=False)
        run.status = "ok"; run.completed_at = _now(); run.upserted_count = len(normalized)
        run.created_count = created_count; run.updated_count = updated_count
        _set_health(db, provider_name, status="healthy", checked=checked, success=True)
        db.commit()
        return {
            "status": "ok", "provider": provider_name, "checked": checked.isoformat(),
            "fetched": len(records), "upserted": len(normalized), "created": created_count,
            "updated": updated_count, "stale_marked": stale_marked,
        }
    finally:
        _lock.release()


def _tokens(value: str | None) -> set[str]:
    return {x.strip().lower() for x in (value or "").replace(";", ",").split(",") if x.strip()}


def _create_alerts(db: Session, event: JobChangeEvent, job: Job) -> None:
    """Create at most one notification per user/event using persisted signals only."""
    users = db.query(AlertPreference).filter(AlertPreference.enabled.is_(True)).all()
    for pref in users:
        matched = pref.saved_jobs and db.query(SavedJob).filter_by(user_id=pref.user_id, job_id=job.id).first() is not None
        matched = matched or bool(_tokens(pref.target_roles) & _tokens(job.normalized_role))
        matched = matched or bool(_tokens(pref.skills) & _tokens(job.required_skills))
        if not matched:
            roadmap = db.query(Roadmap).filter_by(user_id=pref.user_id).all()
            matched = any((r.target_role or "").lower() in (job.normalized_role or "").lower() for r in roadmap)
        if matched:
            db.add(Notification(user_id=pref.user_id, event_id=event.id, dedupe_key=str(event.id),
                                title=f"Job {event.event_type}", message=f"{job.job_title} at {job.company_name}"))


def ingest_external_jobs(db: Session, limit: int = 100, provider_name: str | None = None) -> dict[str, Any]:
    """Refresh configured providers independently so one outage does not block others."""
    providers = configured_external_providers()
    if provider_name:
        providers = [provider for provider in providers if provider.name == provider_name]
    if not providers:
        return {"status": "unconfigured", "runs": []}
    runs = [ingest_jobs(db, provider, provider.name, limit, "external") for provider in providers]
    return {"status": "ok" if any(run["status"] == "ok" for run in runs) else "no_success", "runs": runs}
