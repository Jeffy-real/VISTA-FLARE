"""API routes package."""
from fastapi import APIRouter

from backend.app.api.data import router as data_router
from backend.app.api.market import router as market_router
from backend.app.api.model import router as model_router
from backend.app.api.prediction import router as prediction_router

api_router = APIRouter()
api_router.include_router(prediction_router)
api_router.include_router(data_router)
api_router.include_router(market_router)
api_router.include_router(model_router)
