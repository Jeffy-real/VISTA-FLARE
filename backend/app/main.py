"""Vista Flare - AI-Powered Career & Skill Matching Platform.

FastAPI application entry point.
"""
from contextlib import asynccontextmanager
import asyncio
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from backend.app.api import api_router
from backend.app.core.config import PROJECT_ROOT, settings
from backend.app.core.database import SessionLocal, init_db
from backend.app.services.job_ingestion import ingest_external_jobs


async def _scheduled_ingestion() -> None:
    """Single-instance opt-in refresh loop; disabled by default.

    Deploy this only in one API worker. Provider-level run guards prevent
    overlapping refreshes inside the process and preserve cached results on
    upstream failure.
    """
    while True:
        await asyncio.sleep(max(5, settings.ingestion_interval_minutes * 60))
        db = SessionLocal()
        try:
            await asyncio.to_thread(ingest_external_jobs, db)
        finally:
            db.close()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize database on startup."""
    init_db()
    task = asyncio.create_task(_scheduled_ingestion()) if settings.enable_ingestion_scheduler else None
    try:
        yield
    finally:
        if task:
            task.cancel()
            await asyncio.gather(task, return_exceptions=True)


app = FastAPI(
    title="Vista Flare",
    description="AI-Powered Career & Skill Matching Platform",
    version="1.0.0",
    lifespan=lifespan,
)

# Configure CORS for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(api_router)

# Mount static reports directory for plots and confusion matrices
reports_dir = PROJECT_ROOT / "reports"
if reports_dir.exists():
    app.mount("/reports", StaticFiles(directory=str(reports_dir)), name="reports")


@app.get("/")
async def root() -> dict:
    """Root endpoint."""
    return {
        "name": "Vista Flare",
        "version": "1.0.0",
        "description": "AI-Powered Career & Skill Matching Platform",
    }


@app.get("/health")
async def health_check() -> dict:
    """Root health check endpoint."""
    return {
        "status": "healthy",
        "app_name": "Vista Flare",
        "version": "1.0.0",
    }
