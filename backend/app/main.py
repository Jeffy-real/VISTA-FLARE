"""Vista Flare - AI-Powered Career & Skill Matching Platform.

FastAPI application entry point.
"""
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from backend.app.api import api_router
from backend.app.core.config import PROJECT_ROOT, settings
from backend.app.core.database import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize database on startup."""
    init_db()
    yield


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
