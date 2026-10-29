"""API routes package."""
from fastapi import APIRouter

from backend.app.api.data import router as data_router
from backend.app.api.market import router as market_router
from backend.app.api.model import router as model_router
from backend.app.api.prediction import router as prediction_router
from backend.app.api.auth import router as auth_router
from backend.app.api.ingestion import router as ingestion_router
from backend.app.api.resume_coach import router as resume_coach_router
from backend.app.api.intelligence import router as intelligence_router
from backend.app.api.workflows import router as workflows_router

api_router = APIRouter()
api_router.include_router(prediction_router)
api_router.include_router(data_router)
api_router.include_router(market_router)
api_router.include_router(model_router)
api_router.include_router(auth_router)
api_router.include_router(ingestion_router)
api_router.include_router(resume_coach_router)
api_router.include_router(intelligence_router)
api_router.include_router(workflows_router)
