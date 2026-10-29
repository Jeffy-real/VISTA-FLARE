"""Read-only model-workflow and operational-status endpoints."""
from __future__ import annotations

import hashlib
import hmac
from datetime import datetime
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func
from sqlalchemy.orm import Session

from backend.app.core.auth import current_user, optional_user
from backend.app.core.config import get_settings
from backend.app.core.database import get_db
from backend.app.models.database_models import InferenceTrace, IngestionRun, Job, ProviderHealth, User
from backend.app.services.inference_tracing import serialize_trace
from backend.app.services.job_ingestion import _error_category
from backend.app.services.job_provider import provider_catalog
from backend.app.services.model_metadata import get_comparison, get_confusion_row, get_model_metadata
from backend.app.services.predictor import get_prediction_service

router = APIRouter(prefix="/api/workflows", tags=["AI & model workflows"])


def _model_health(db: Session) -> dict[str, Any]:
    service = get_prediction_service()
    recent = db.query(InferenceTrace).filter(InferenceTrace.status == "completed").order_by(InferenceTrace.completed_at.desc()).first()
    if service.model_type == "tensorflow":
        active = "TensorFlow ANN"
        status = "healthy"
    elif service.model_type == "sklearn":
        active = "scikit-learn fallback"
        status = "degraded"
    else:
        active = "Unavailable"
        status = "unavailable"
    error = service.model_load_error or ""
    category = "tensorflow_unavailable" if "tensorflow" in error.lower() else "artifact_unavailable" if "artifact" in error.lower() else None
    return {
        "status": status, "active_model": active, "model_type": service.model_type or "unavailable",
        "last_successful_inference": recent.completed_at.isoformat() if recent and recent.completed_at else None,
        "last_inference_duration_ms": recent.duration_ms if recent else None, "last_error_category": category,
    }


def _provider_status(db: Session) -> dict[str, Any]:
    health = {row.provider_name: row for row in db.query(ProviderHealth).all()}
    runs = db.query(IngestionRun).order_by(IngestionRun.started_at.desc()).limit(50).all()
    latest_by_provider: dict[str, IngestionRun] = {}
    for run in runs:
        latest_by_provider.setdefault(run.provider_name, run)
    providers = []
    for provider in provider_catalog(get_settings()):
        row = health.get(provider.name)
        latest = latest_by_provider.get(provider.name)
        providers.append({
            "provider": provider.name, "display_name": provider.display_name,
            "configuration": "configured" if provider.configured else "unconfigured",
            "requires_credentials": provider.requires_credentials,
            "operational_status": row.status if row else "unverified",
            "last_checked": row.last_checked.isoformat() if row and row.last_checked else None,
            "last_success": row.last_success.isoformat() if row and row.last_success else None,
            "last_error_category": _error_category(row.last_error) if row else None,
            "refresh_minimum_minutes": provider.min_refresh_minutes or None,
            "latest_run": {
                "status": latest.status, "fetched": latest.fetched_count or 0, "upserted": latest.upserted_count or 0,
                "created": latest.created_count or 0, "updated": latest.updated_count or 0,
                "completed_at": latest.completed_at.isoformat() if latest.completed_at else None,
            } if latest else None,
        })
    return {
        "providers": providers,
        "external_listing_count": db.query(Job).filter(Job.source_kind == "external").count(),
        "seed_listing_count": db.query(Job).filter(Job.source_kind == "seed").count(),
    }


@router.get("/overview")
def workflow_overview(db: Session = Depends(get_db)) -> dict[str, Any]:
    return {
        "model_health": _model_health(db), "providers": _provider_status(db),
        "system_workflow": [
            {"id": "skills", "label": "User skills", "purpose": "Receives selected skill names and levels.", "input": "User selection", "output": "SkillInput[]", "module": "backend/app/api/prediction.py", "endpoint": "POST /api/predict"},
            {"id": "normalize", "label": "Skill normalization", "purpose": "Maps aliases to the model vocabulary.", "input": "SkillInput[]", "output": "Canonical skill names", "module": "backend/app/services/predictor.py", "endpoint": "POST /api/predict"},
            {"id": "encode", "label": "Feature encoding", "purpose": "Creates and scales the numerical skill vector.", "input": "Canonical skills", "output": "373-feature vector", "module": "backend/app/services/predictor.py", "endpoint": "POST /api/predict"},
            {"id": "infer", "label": "Model inference", "purpose": "Runs TensorFlow ANN or the identified fallback.", "input": "Feature vector", "output": "Career-class score vector", "module": "backend/app/services/predictor.py", "endpoint": "POST /api/predict"},
            {"id": "rank", "label": "Top-3 career predictions", "purpose": "Ranks classifier scores; these are not hiring probabilities.", "input": "Class scores", "output": "Three roles and scores", "module": "backend/app/services/predictor.py", "endpoint": "POST /api/predict"},
            {"id": "gap", "label": "Skill-gap analysis", "purpose": "Compares a selected role against role-skill mappings.", "input": "Target role + user skills", "output": "Strengths and gaps", "module": "backend/app/services/skill_gap.py", "endpoint": "POST /api/analyze-skills"},
            {"id": "roadmap", "label": "Resources & roadmap", "purpose": "Builds learning stages from stored resources and role mappings.", "input": "Skill gaps", "output": "Learning resources and roadmap", "module": "backend/app/services/skill_gap.py", "endpoint": "POST /api/analyze-skills"},
            {"id": "jobs", "label": "Job & company matching", "purpose": "Filters persisted jobs and computes an explainable overlap score.", "input": "Skills + target role", "output": "Job results and companies", "module": "backend/app/api/data.py", "endpoint": "GET /api/job-search"},
        ],
        "system_architecture": [
            {"id": "frontend", "label": "React frontend", "kind": "synchronous", "module": "frontend/src", "endpoint": "Browser routes"},
            {"id": "api", "label": "FastAPI", "kind": "synchronous", "module": "backend/app/api", "endpoint": "/api/*"},
            {"id": "auth", "label": "Authentication", "kind": "synchronous", "module": "backend/app/core/auth.py", "endpoint": "/api/auth/*"},
            {"id": "services", "label": "Career services", "kind": "synchronous", "module": "backend/app/services", "endpoint": "/api/predict, /api/analyze-skills"},
            {"id": "model", "label": "Model inference", "kind": "inference", "module": "backend/app/services/predictor.py", "endpoint": "POST /api/predict"},
            {"id": "database", "label": "SQLite", "kind": "database", "module": "data/vista_flare.db", "endpoint": "SQLAlchemy"},
            {"id": "ingestion", "label": "Job ingestion", "kind": "background", "module": "backend/app/services/job_ingestion.py", "endpoint": "POST /api/admin/jobs/ingest"},
            {"id": "providers", "label": "External providers", "kind": "external", "module": "backend/app/services/job_provider.py", "endpoint": "Provider HTTPS APIs"},
        ],
    }


@router.get("/models/{model}")
def model_workflow(model: str) -> dict[str, Any]:
    return get_model_metadata(model)


@router.get("/comparison")
def model_comparison() -> dict[str, Any]:
    return {"comparison": get_comparison()}


@router.get("/models/{model}/confusion")
def model_confusion(model: str, class_name: str | None = Query(None)) -> dict[str, Any]:
    return get_confusion_row(model, class_name)


@router.get("/providers")
def provider_workflow_status(db: Session = Depends(get_db)) -> dict[str, Any]:
    return _provider_status(db)


@router.get("/model-health")
def model_workflow_health(db: Session = Depends(get_db)) -> dict[str, Any]:
    return _model_health(db)


@router.get("/inference-traces")
def inference_traces(limit: int = Query(20, ge=1, le=100), db: Session = Depends(get_db), user: User = Depends(current_user)) -> dict[str, Any]:
    traces = db.query(InferenceTrace).filter(InferenceTrace.user_id == user.id).order_by(InferenceTrace.created_at.desc()).limit(limit).all()
    return {"items": [serialize_trace(trace) for trace in traces], "retention_hours": get_settings().inference_trace_retention_hours}


@router.get("/inference-traces/{trace_id}")
def inference_trace(trace_id: str, trace_access_token: str | None = Query(None), db: Session = Depends(get_db), user: User | None = Depends(optional_user)) -> dict[str, Any]:
    trace = db.query(InferenceTrace).filter(InferenceTrace.id == trace_id).first()
    if not trace:
        raise HTTPException(status_code=404, detail="Inference trace not found")
    is_owner = bool(user and trace.user_id == user.id)
    provided_hash = hashlib.sha256(trace_access_token.encode("utf-8")).hexdigest() if trace_access_token else ""
    has_capability = bool(trace.access_token_hash and hmac.compare_digest(trace.access_token_hash, provided_hash))
    if not (is_owner or has_capability):
        raise HTTPException(status_code=403, detail="Not authorized to view this inference trace")
    return serialize_trace(trace)
