"""Tests for Vista Flare Deep Learning model and prediction service."""
import pytest
import numpy as np

from backend.app.services.predictor import get_prediction_service


def test_prediction_service_initialization():
    """Verify that prediction service loads artifacts and TensorFlow model."""
    service = get_prediction_service()
    assert service is not None
    assert service.model is not None
    assert service.model_type in ["tensorflow", "sklearn"]
    assert service.skill_encoder is not None
    assert service.label_encoder is not None
    assert len(service.skill_encoder.get("skills", [])) == 373
    assert len(service.label_encoder.get("roles", [])) == 85


def test_encode_profile_valid():
    """Verify skill vector encoding dimensions and values."""
    service = get_prediction_service()
    skills = [
        {"name": "Python", "level": "advanced"},
        {"name": "SQL", "level": "intermediate"},
        {"name": "Machine Learning", "level": "expert"},
    ]
    vec = service.encode_profile(skills)
    assert isinstance(vec, np.ndarray)
    assert vec.shape == (373,)
    assert vec.max() <= 1.0
    assert vec.min() >= 0.0
    # At least some features must be positive
    assert np.count_nonzero(vec) >= 3


def test_predict_returns_top_3_unique():
    """Verify that predictions return exactly 3 unique roles in descending score order."""
    service = get_prediction_service()
    skills = [
        {"name": "Python", "level": "advanced"},
        {"name": "SQL", "level": "advanced"},
        {"name": "Machine Learning", "level": "intermediate"},
    ]
    recs = service.predict(skills, top_k=3)
    assert len(recs) == 3

    # Check ranks 1, 2, 3
    assert [r["rank"] for r in recs] == [1, 2, 3]

    # Check distinct roles
    roles = [r["role"] for r in recs]
    assert len(set(roles)) == 3

    # Check valid probabilities
    for r in recs:
        assert 0.0 <= r["score"] <= 1.0

    # Check descending order of scores
    assert recs[0]["score"] >= recs[1]["score"] >= recs[2]["score"]


def test_predict_handles_unknown_skills_gracefully():
    """Verify that unknown skills do not crash prediction."""
    service = get_prediction_service()
    skills = [
        {"name": "Alien Telepathy", "level": "expert"},
        {"name": "Sub-atomic Origami", "level": "advanced"},
    ]
    # An entirely unknown skill vector is all zeros, but should still produce valid top 3 roles without crashing
    recs = service.predict(skills, top_k=3)
    assert len(recs) == 3
    assert len(set([r["role"] for r in recs])) == 3
    for r in recs:
        assert 0.0 <= r["score"] <= 1.0


def test_predict_raises_on_empty_skills():
    """Verify that empty skill list raises ValueError."""
    service = get_prediction_service()
    with pytest.raises(ValueError, match="Skills list cannot be empty"):
        service.predict([], top_k=3)


def test_canonicalize_skill_aliases():
    """Verify canonicalization of common variations and aliases."""
    service = get_prediction_service()
    assert service._canonicalize_skill("python") == "Python"
    assert service._canonicalize_skill("react.js") == "React"
    assert service._canonicalize_skill("powerbi") == "Power BI"
    assert service._canonicalize_skill("aws") == "AWS"
