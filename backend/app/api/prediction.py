"""Prediction and Career Intelligence API routes."""
from typing import Any
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.app.core.database import get_db
from backend.app.models.database_models import Role
from backend.app.schemas.prediction import (
    CareerRecommendation,
    HealthResponse,
    PredictionRequest,
    PredictionResponse,
    SkillAnalysisRequest,
    SkillAnalysisResponse,
)
from backend.app.services.predictor import get_prediction_service
from backend.app.services.skill_gap import analyze_skill_gap

router = APIRouter(prefix="/api", tags=["prediction"])


@router.get("/health", response_model=HealthResponse)
async def api_health(db: Session = Depends(get_db)) -> HealthResponse:
    """Check API, ML model, and database operational status."""
    service = get_prediction_service()
    model_loaded = service.model is not None

    db_connected = False
    try:
        db.query(Role).count()
        db_connected = True
    except Exception:
        db_connected = False

    return HealthResponse(
        status="healthy" if (model_loaded and db_connected) else "degraded",
        app_name="Vista Flare",
        model_loaded=model_loaded,
        database_connected=db_connected,
    )


@router.post("/predict", response_model=PredictionResponse)
async def predict_careers(
    request: PredictionRequest,
    db: Session = Depends(get_db),
) -> PredictionResponse:
    """Get top 3 career recommendations from the trained Deep Learning ANN model."""
    try:
        service = get_prediction_service()
        recommendations = service.predict([s.model_dump() for s in request.skills])

        return PredictionResponse(
            model=service.model_type or "unknown",
            model_version="ANN-v1",
            recommendations=[CareerRecommendation(**r) for r in recommendations],
        )
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")


@router.post("/analyze-skills", response_model=SkillAnalysisResponse)
async def analyze_skills(
    request: SkillAnalysisRequest,
    db: Session = Depends(get_db),
) -> SkillAnalysisResponse:
    """Perform deterministic skill gap analysis, company matching, and roadmap generation."""
    try:
        service = get_prediction_service()
        # Run ANN model to get model confidence if possible
        ai_match = None
        try:
            preds = service.predict([s.model_dump() for s in request.skills], top_k=10)
            for p in preds:
                if p["role"].lower() == request.target_role.lower():
                    ai_match = p["score"]
                    break
        except Exception:
            pass

        return analyze_skill_gap(
            target_role=request.target_role,
            user_skills=[s.model_dump() for s in request.skills],
            db=db,
            ai_match_score=ai_match,
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Skill analysis failed: {str(e)}")
