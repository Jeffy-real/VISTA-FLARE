"""Integration tests for Vista Flare FastAPI endpoints."""
import pytest
from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.services.predictor import get_prediction_service

client = TestClient(app)


def test_health_endpoint():
    """Verify system health check."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["app_name"] == "Vista Flare"


def test_api_health_endpoint():
    """Verify API health with model and database status."""
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    expected_status = "healthy" if get_prediction_service().model_type == "tensorflow" else "degraded"
    assert data["status"] == expected_status
    assert data["model_loaded"] is True
    assert data["database_connected"] is True


def test_predict_endpoint_success():
    """Verify that POST /api/predict returns top 3 career recommendations."""
    payload = {
        "skills": [
            {"name": "Python", "level": "advanced"},
            {"name": "SQL", "level": "advanced"},
            {"name": "Machine Learning", "level": "intermediate"},
        ]
    }
    response = client.post("/api/predict", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["model"] == get_prediction_service().model_type
    assert data["model_version"] == "ANN-v1"
    recs = data["recommendations"]
    assert len(recs) == 3
    assert [r["rank"] for r in recs] == [1, 2, 3]
    for r in recs:
        assert isinstance(r["role"], str)
        assert len(r["role"]) > 0
        assert 0.0 <= r["score"] <= 1.0


def test_predict_endpoint_empty_skills_fails():
    """Verify that empty skills list returns 400."""
    response = client.post("/api/predict", json={"skills": []})
    assert response.status_code in [400, 422]


def test_analyze_skills_endpoint():
    """Verify POST /api/analyze-skills returns gap analysis and roadmap."""
    payload = {
        "target_role": "Data Scientist",
        "skills": [
            {"name": "Python", "level": "advanced"},
            {"name": "SQL", "level": "intermediate"},
        ],
    }
    response = client.post("/api/analyze-skills", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["target_role"] == "Data Scientist"
    assert "strong_skills" in data
    assert "developing_skills" in data
    assert "missing_skills" in data
    assert "company_matches" in data
    assert "roadmap" in data
    assert len(data["roadmap"]) == 5  # 5-stage personalized roadmap


def test_analyze_skills_rejects_unknown_role():
    response = client.post(
        "/api/analyze-skills",
        json={"target_role": "Not A Real Role", "skills": [{"name": "Python"}]},
    )
    assert response.status_code == 404


def test_model_metrics_endpoint():
    """Verify GET /api/model/metrics returns authentic evaluation metrics."""
    response = client.get("/api/model/metrics?model=ann")
    assert response.status_code == 200
    data = response.json()
    assert data["model"] == "ann"
    assert "accuracy" in data
    assert "top_3_accuracy" in data
    assert "f1_weighted" in data
    assert data["accuracy"] > 0.60
    assert data["top_3_accuracy"] > 0.80


def test_model_comparison_endpoint():
    """Verify GET /api/model/comparison returns multi-model benchmark table."""
    response = client.get("/api/model/comparison")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 3  # ANN, CNN, LSTM
    model_names = [m["Model"] for m in data]
    assert any("ANN" in name for name in model_names)
    assert any("CNN" in name for name in model_names)
    assert any("LSTM" in name for name in model_names)


def test_get_skills_endpoint():
    """Verify GET /api/skills returns skill taxonomy."""
    response = client.get("/api/skills")
    assert response.status_code == 200
    skills = response.json()
    assert len(skills) > 0


def test_get_roles_endpoint():
    """Verify GET /api/roles returns career roles."""
    response = client.get("/api/roles")
    assert response.status_code == 200
    roles = response.json()
    assert len(roles) >= 80


def test_get_companies_endpoint():
    """Verify GET /api/companies returns hiring organizations."""
    response = client.get("/api/companies")
    assert response.status_code == 200
    companies = response.json()
    assert len(companies) > 0


def test_get_jobs_endpoint():
    """Verify GET /api/jobs returns job postings."""
    response = client.get("/api/jobs")
    assert response.status_code == 200
    jobs = response.json()
    assert len(jobs) > 0
