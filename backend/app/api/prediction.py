"""Prediction and Career Intelligence API routes."""
from typing import Any
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.app.core.database import get_db
from backend.app.core.auth import optional_user
from backend.app.models.database_models import Role, User
from backend.app.schemas.prediction import (
    CareerRecommendation,
    HealthResponse,
    PredictionRequest,
    PredictionResponse,
    SkillAnalysisRequest,
    SkillAnalysisResponse,
)
from backend.app.services.predictor import get_prediction_service
from backend.app.services.inference_tracing import InferenceTraceRecorder
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
        status="healthy" if (model_loaded and db_connected and service.model_type == "tensorflow") else "degraded",
        app_name="Vista Flare",
        model_loaded=model_loaded,
        model_type=service.model_type,
        model_load_error=service.model_load_error,
        database_connected=db_connected,
    )


@router.post("/predict", response_model=PredictionResponse)
async def predict_careers(
    request: PredictionRequest,
    db: Session = Depends(get_db),
    user: User | None = Depends(optional_user),
) -> PredictionResponse:
    """Get top three recommendations and a trace of this actual inference."""
    trace = InferenceTraceRecorder(db, user.id if user else None)
    try:
        trace.stage("request_received", "completed")
        if not request.skills:
            trace.stage("input_validated", "failed")
            trace.fail("validation_error")
            raise HTTPException(status_code=400, detail="Skills list cannot be empty")
        trace.stage("input_validated", "completed", skill_count=len(request.skills))
        service = get_prediction_service()
        payload = [s.model_dump() for s in request.skills]
        trace.stage("skills_normalized", "completed", **service.normalized_skill_summary(payload))
        trace.stage("features_encoded", "running")
        features = service.prepare_features(payload)
        trace.stage("features_encoded", "completed", input_feature_count=int(features.shape[1]))
        trace.stage("model_loaded_selected", "completed", model_type=service.model_type or "unavailable")
        trace.stage("inference_executed", "running")
        recommendations, output_count = service.predict_features(features)
        trace.stage("inference_executed", "completed")
        trace.stage("scores_validated", "completed", output_class_count=output_count)
        trace.stage("top_3_ranked", "completed", result_count=len(recommendations))
        trace.stage("response_returned", "completed")
        trace.succeed(
            model_type=service.model_type,
            input_feature_count=int(features.shape[1]),
            output_class_count=output_count,
            top_results=recommendations,
        )

        return PredictionResponse(
            model=service.model_type or "unknown",
            model_version="ANN-v1",
            recommendations=[CareerRecommendation(**r) for r in recommendations],
            trace_id=trace.trace_id,
            trace_access_token=trace.access_token,
        )
    except HTTPException:
        raise
    except RuntimeError as e:
        trace.stage("inference_executed", "failed")
        trace.fail("model_unavailable" if "not loaded" in str(e).lower() else "model_execution_error")
        raise HTTPException(status_code=503, detail=str(e))
    except ValueError as e:
        trace.stage("input_validated", "failed")
        trace.fail("validation_error")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        trace.stage("inference_executed", "failed")
        trace.fail("unexpected_error")
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")


@router.post("/analyze-skills", response_model=SkillAnalysisResponse)
async def analyze_skills(
    request: SkillAnalysisRequest,
    db: Session = Depends(get_db),
) -> SkillAnalysisResponse:
    """Perform deterministic skill gap analysis, company matching, and roadmap generation."""
    try:
        service = get_prediction_service()
        role = db.query(Role).filter(Role.name.ilike(request.target_role)).first()
        if not role:
            raise HTTPException(status_code=404, detail=f"Target role not found: {request.target_role}")
        # Run ANN model to get model confidence if possible
        ai_match = service.score_for_role(
            [s.model_dump() for s in request.skills], role.name
        )

        return analyze_skill_gap(
            target_role=role.name,
            user_skills=[s.model_dump() for s in request.skills],
            db=db,
            ai_match_score=ai_match,
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Skill analysis failed: {str(e)}")
