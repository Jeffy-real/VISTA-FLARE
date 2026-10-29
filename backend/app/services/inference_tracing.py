"""Privacy-preserving instrumentation for real career inference requests."""
from __future__ import annotations

import hashlib
import json
import secrets
import time
import uuid
from datetime import datetime, timedelta
from typing import Any

from sqlalchemy.orm import Session

from backend.app.core.config import get_settings
from backend.app.models.database_models import InferenceTrace


def _now() -> datetime:
    return datetime.utcnow()


class InferenceTraceRecorder:
    def __init__(self, db: Session, user_id: int | None = None) -> None:
        self.db = db
        self.started = time.perf_counter()
        self.access_token = secrets.token_urlsafe(24)
        settings = get_settings()
        self.trace = InferenceTrace(
            id=str(uuid.uuid4()),
            access_token_hash=hashlib.sha256(self.access_token.encode("utf-8")).hexdigest(),
            user_id=user_id,
            created_at=_now(),
            expires_at=_now() + timedelta(hours=max(1, settings.inference_trace_retention_hours)),
            status="running",
            stages_json="[]",
            top_results_json="[]",
        )
        self.db.add(self.trace)
        self.db.flush()

    @property
    def trace_id(self) -> str:
        return self.trace.id

    def stage(self, name: str, status: str, **details: Any) -> None:
        stages = json.loads(self.trace.stages_json or "[]")
        stages.append({"name": name, "status": status, "at": _now().isoformat(), **details})
        self.trace.stages_json = json.dumps(stages)
        self.trace.updated_at = _now()

    def succeed(self, *, model_type: str | None, input_feature_count: int, output_class_count: int,
                top_results: list[dict[str, Any]]) -> None:
        self.trace.status = "completed"
        self.trace.model_type = model_type or "unavailable"
        self.trace.model_version = "ANN-v1"
        self.trace.input_feature_count = input_feature_count
        self.trace.output_class_count = output_class_count
        self.trace.duration_ms = round((time.perf_counter() - self.started) * 1000, 3)
        self.trace.completed_at = _now()
        # Roles and scores are useful operational output; no input profile is retained.
        self.trace.top_results_json = json.dumps(top_results)
        self.trace.updated_at = _now()
        self.db.commit()

    def fail(self, category: str, *, model_type: str | None = None) -> None:
        self.trace.status = "failed"
        self.trace.model_type = model_type or "unavailable"
        self.trace.model_version = "ANN-v1"
        self.trace.error_category = category
        self.trace.duration_ms = round((time.perf_counter() - self.started) * 1000, 3)
        self.trace.completed_at = _now()
        self.trace.updated_at = _now()
        self.db.commit()


def serialize_trace(trace: InferenceTrace) -> dict[str, Any]:
    return {
        "trace_id": trace.id,
        "created_at": trace.created_at.isoformat(),
        "completed_at": trace.completed_at.isoformat() if trace.completed_at else None,
        "status": trace.status,
        "model_type": trace.model_type,
        "model_version": trace.model_version,
        "duration_ms": trace.duration_ms,
        "input_feature_count": trace.input_feature_count,
        "output_class_count": trace.output_class_count,
        "error_category": trace.error_category,
        "stages": json.loads(trace.stages_json or "[]"),
        "top_results": json.loads(trace.top_results_json or "[]"),
    }
