"""Authenticated career-intelligence notifications and persisted market trends."""
from __future__ import annotations

import json
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy import func
from sqlalchemy.orm import Session

from backend.app.core.auth import current_user, require_csrf
from backend.app.core.database import get_db
from backend.app.models.database_models import (AlertPreference, IngestionRun, Notification,
    ProviderHealth, JobObservation, User, Job)
from backend.app.services.job_ingestion import _error_category

router = APIRouter(prefix="/api", tags=["career intelligence"])


def _csv(value: str | None) -> list[str]:
    return [x.strip() for x in (value or "").replace(";", ",").split(",") if x.strip()]


@router.get("/notifications")
def list_notifications(unread_only: bool = False, limit: int = 50, db: Session = Depends(get_db), user: User = Depends(current_user)):
    q = db.query(Notification).filter(Notification.user_id == user.id)
    if unread_only: q = q.filter(Notification.read_at.is_(None))
    return [{"id": n.id, "title": n.title, "message": n.message, "type": n.notification_type,
             "event_id": n.event_id, "created_at": n.created_at.isoformat(), "read_at": n.read_at.isoformat() if n.read_at else None}
            for n in q.order_by(Notification.created_at.desc()).limit(min(limit, 200)).all()]


@router.get("/notifications/{notification_id}")
def get_notification(notification_id: int, db: Session = Depends(get_db), user: User = Depends(current_user)):
    n = db.query(Notification).filter_by(id=notification_id, user_id=user.id).first()
    if not n: raise HTTPException(404, "Notification not found")
    return {"id": n.id, "title": n.title, "message": n.message, "type": n.notification_type,
            "event_id": n.event_id, "created_at": n.created_at.isoformat(), "read_at": n.read_at.isoformat() if n.read_at else None}


@router.post("/notifications/{notification_id}/read")
def mark_notification_read(notification_id: int, db: Session = Depends(get_db), user: User = Depends(current_user), _: object = Depends(require_csrf)):
    n = db.query(Notification).filter_by(id=notification_id, user_id=user.id).first()
    if not n: raise HTTPException(404, "Notification not found")
    n.read_at = n.read_at or datetime.utcnow(); db.commit()
    return {"status": "ok", "id": n.id, "read_at": n.read_at.isoformat()}


@router.get("/alert-preferences")
def get_alert_preferences(db: Session = Depends(get_db), user: User = Depends(current_user)):
    p = db.query(AlertPreference).filter_by(user_id=user.id).first()
    if not p: return {"enabled": True, "target_roles": [], "skills": [], "saved_jobs": True}
    return {"enabled": p.enabled, "target_roles": _csv(p.target_roles), "skills": _csv(p.skills), "saved_jobs": p.saved_jobs}


@router.put("/alert-preferences")
def set_alert_preferences(payload: dict, db: Session = Depends(get_db), user: User = Depends(current_user), _: object = Depends(require_csrf)):
    p = db.query(AlertPreference).filter_by(user_id=user.id).first()
    if not p: p = AlertPreference(user_id=user.id); db.add(p)
    p.enabled = bool(payload.get("enabled", True)); p.saved_jobs = bool(payload.get("saved_jobs", True))
    p.target_roles = ",".join(map(str, payload.get("target_roles", [])))
    p.skills = ",".join(map(str, payload.get("skills", [])))
    db.commit()
    return get_alert_preferences(db, user)


@router.get("/provider-status")
@router.get("/refresh-status")
def refresh_status(db: Session = Depends(get_db), user: User = Depends(current_user)):
    providers = [{"provider": p.provider_name, "status": p.status, "last_checked": p.last_checked.isoformat(),
                  "last_success": p.last_success.isoformat() if p.last_success else None, "last_error": _error_category(p.last_error),
                  "consecutive_failures": p.consecutive_failures} for p in db.query(ProviderHealth).all()]
    runs = [{"provider": r.provider_name, "status": r.status, "started_at": r.started_at.isoformat(),
             "completed_at": r.completed_at.isoformat() if r.completed_at else None, "error": _error_category(r.error),
             "fetched_count": r.fetched_count or 0, "upserted_count": r.upserted_count or 0,
             "created_count": r.created_count or 0, "updated_count": r.updated_count or 0}
            for r in db.query(IngestionRun).order_by(IngestionRun.started_at.desc()).limit(20).all()]
    return {"providers": providers, "recent_runs": runs}


@router.get("/market-trends")
def market_trends(role: str | None = None, db: Session = Depends(get_db), user: User = Depends(current_user)):
    q = db.query(JobObservation).join(JobObservation.job)
    if role: q = q.filter(func.lower(Job.normalized_role) == role.lower())
    rows = q.order_by(JobObservation.observed_at.asc()).all()
    points = {}
    for row in rows:
        day = row.observed_at.date().isoformat()
        points.setdefault(day, {"date": day, "observations": 0, "active_jobs": 0, "salary_min_avg": None, "salary_max_avg": None})
        p = points[day]; p["observations"] += 1; p["active_jobs"] += int(row.active)
        mins = [x.salary_min for x in rows if x.observed_at.date().isoformat() == day and x.salary_min is not None]
        maxs = [x.salary_max for x in rows if x.observed_at.date().isoformat() == day and x.salary_max is not None]
        p["salary_min_avg"] = round(sum(mins) / len(mins), 2) if mins else None; p["salary_max_avg"] = round(sum(maxs) / len(maxs), 2) if maxs else None
    return {"points": list(points.values()), "sample_size": len(rows), "source": "persisted job observations",
            "source_metadata": {"providers": sorted({r.job.provider_name for r in rows}), "observation_count": len(rows), "role_filter": role}}
