"""Protected maintenance endpoint for external job ingestion."""
from typing import Any

from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy.orm import Session

from backend.app.core.config import get_settings
from backend.app.core.database import get_db
from backend.app.services.job_ingestion import ingest_external_jobs

router = APIRouter(prefix="/api/admin", tags=["maintenance"])


@router.post("/jobs/ingest")
def trigger_job_ingestion(
    limit: int = 100,
    provider: str | None = None,
    x_ingestion_secret: str | None = Header(default=None),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    settings = get_settings()
    expected = settings.ingestion_admin_secret
    if not expected or x_ingestion_secret != expected:
        raise HTTPException(status_code=403, detail="Invalid ingestion credentials")
    return ingest_external_jobs(db, max(1, min(limit, 500)), provider_name=provider)
