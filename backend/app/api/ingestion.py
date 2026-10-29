"""Protected maintenance and operational status endpoints for external job ingestion."""
from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy.orm import Session

from backend.app.core.config import PROJECT_ROOT, get_settings
from backend.app.core.database import get_db
from backend.app.models.database_models import (
    Application,
    Company,
    InferenceTrace,
    IngestionRun,
    Job,
    LearningResource,
    ProviderHealth,
    Roadmap,
    Role,
    RoleSkill,
    SavedJob,
    Skill,
    SkillAlias,
    User,
    UserSession,
)
from backend.app.services.job_ingestion import ingest_external_jobs
from backend.app.services.job_provider import provider_catalog

router = APIRouter(prefix="/api/admin", tags=["maintenance"])


def _verify_admin(x_ingestion_secret: str | None) -> None:
    settings = get_settings()
    expected = settings.ingestion_admin_secret
    if not expected or not x_ingestion_secret or x_ingestion_secret.strip() != expected.strip():
        raise HTTPException(status_code=403, detail="Invalid or missing admin ingestion credentials")


@router.get("/status")
def get_admin_status(
    x_ingestion_secret: str | None = Header(default=None),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    """Protected operational status report: database paths, record counts, provider health, and runs."""
    _verify_admin(x_ingestion_secret)
    settings = get_settings()

    db_path = str(PROJECT_ROOT / "data" / "vista_flare.db")
    db_size = os.path.getsize(db_path) if os.path.exists(db_path) else 0

    # Real table record counts from SQLite
    counts = {
        "roles": db.query(Role).count(),
        "skills": db.query(Skill).count(),
        "role_skills": db.query(RoleSkill).count(),
        "skill_aliases": db.query(SkillAlias).count(),
        "companies": db.query(Company).count(),
        "jobs_total": db.query(Job).count(),
        "jobs_external": db.query(Job).filter(Job.source_kind == "external").count(),
        "jobs_seed": db.query(Job).filter(Job.source_kind == "seed").count(),
        "jobs_active": db.query(Job).filter(Job.active.is_(True)).count(),
        "jobs_stale": db.query(Job).filter(Job.stale.is_(True)).count(),
        "learning_resources": db.query(LearningResource).count(),
        "users": db.query(User).count(),
        "user_sessions": db.query(UserSession).count(),
        "roadmaps": db.query(Roadmap).count(),
        "saved_jobs": db.query(SavedJob).count(),
        "applications": db.query(Application).count(),
        "inference_traces": db.query(InferenceTrace).count(),
        "ingestion_runs": db.query(IngestionRun).count(),
        "provider_health": db.query(ProviderHealth).count(),
    }

    # Provider status
    health_map = {row.provider_name: row for row in db.query(ProviderHealth).all()}
    providers_summary = []
    for provider in provider_catalog(settings):
        h = health_map.get(provider.name)
        providers_summary.append({
            "provider": provider.name,
            "display_name": provider.display_name,
            "configuration": "configured" if provider.configured else "unconfigured",
            "requires_credentials": provider.requires_credentials,
            "operational_status": (
                "Missing server credentials" if not provider.configured
                else h.status.capitalize() if h and h.status
                else "Unverified"
            ),
            "last_checked": h.last_checked.isoformat() if h and h.last_checked else None,
            "last_success": h.last_success.isoformat() if h and h.last_success else None,
            "last_error": h.last_error if h else None,
            "consecutive_failures": h.consecutive_failures if h else 0,
        })

    # Recent ingestion runs
    runs = db.query(IngestionRun).order_by(IngestionRun.started_at.desc()).limit(20).all()
    runs_summary = [
        {
            "id": r.id,
            "provider_name": r.provider_name,
            "started_at": r.started_at.isoformat() if r.started_at else None,
            "completed_at": r.completed_at.isoformat() if r.completed_at else None,
            "status": r.status,
            "fetched_count": r.fetched_count,
            "upserted_count": r.upserted_count,
            "created_count": r.created_count,
            "updated_count": r.updated_count,
            "error": r.error,
        }
        for r in runs
    ]

    # Sample recent external listings
    recent_external = (
        db.query(Job)
        .filter(Job.source_kind == "external")
        .order_by(Job.last_seen.desc())
        .limit(10)
        .all()
    )
    external_samples = [
        {
            "id": j.id,
            "job_title": j.job_title,
            "company_name": j.company_name,
            "source": j.source,
            "source_url": j.source_url,
            "location": j.location,
            "posting_date": j.posting_date,
            "first_seen": j.first_seen.isoformat() if j.first_seen else None,
            "last_seen": j.last_seen.isoformat() if j.last_seen else None,
            "active": j.active,
            "stale": j.stale,
        }
        for j in recent_external
    ]

    return {
        "status": "authorized",
        "database": {
            "resolved_url": settings.database_url,
            "resolved_path": db_path,
            "exists": os.path.exists(db_path),
            "size_bytes": db_size,
        },
        "counts": counts,
        "providers": providers_summary,
        "recent_runs": runs_summary,
        "external_samples": external_samples,
        "scheduler": {
            "enabled": settings.enable_ingestion_scheduler,
            "interval_minutes": settings.ingestion_interval_minutes,
            "stale_after_hours": settings.ingestion_stale_after_hours,
        },
    }


@router.post("/jobs/ingest")
def trigger_job_ingestion(
    limit: int = 50,
    provider: str | None = None,
    x_ingestion_secret: str | None = Header(default=None),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    """Trigger manual provider refresh with server-side validation and atomic database upserts."""
    _verify_admin(x_ingestion_secret)
    bounded_limit = max(1, min(limit, 200))
    return ingest_external_jobs(db, bounded_limit, provider_name=provider)

