"""Resume matching and interview coach behavior."""
from uuid import uuid4

from fastapi.testclient import TestClient

from backend.app.main import app


def _client():
    client = TestClient(app)
    email = f"coach-{uuid4().hex}@example.com"
    assert client.post("/api/auth/register", json={"email": email, "password": "correct horse", "display_name": "Coach"}).status_code == 201
    return client, email


def test_resume_text_alias_matching_and_truthful_job_checklist():
    client, _ = _client()
    response = client.post("/api/resume/analyze", data={"resume_text": "Built services with Python and Postgres. I do not claim Rust." , "job_id": "1"})
    assert response.status_code == 200
    body = response.json()
    assert body["ephemeral"] is True
    assert "Python" in body["skills"]
    assert "Rust" not in body["skills"]
    comparison = body["job_comparison"]
    assert set(comparison) == {"job_id", "matched_skills", "missing_skills", "checklist"}
    assert all(item["status"] in {"matched", "missing"} for item in comparison["checklist"])


def test_resume_file_validation_and_graceful_missing_parser():
    client, _ = _client()
    assert client.post("/api/resume/analyze", files={"file": ("resume.txt", b"Python")}).status_code == 415
    assert client.post("/api/resume/analyze", files={"file": ("resume.pdf", b"not pdf", "application/pdf")}).status_code == 415
    # A valid signature either extracts when an optional parser is installed or clearly reports it is unavailable.
    response = client.post("/api/resume/analyze", files={"file": ("resume.pdf", b"%PDF-1.4\n", "application/pdf")})
    assert response.status_code in {415, 422}
    if response.status_code == 415:
        assert "extraction is unavailable" in response.json()["detail"]


def test_interview_output_is_deterministic_and_progress_is_private():
    one, _ = _client(); two, _ = _client()
    first = one.get("/api/interview/roles/1")
    second = one.get("/api/interview/roles/1")
    assert first.status_code == second.status_code == 200
    assert first.json()["questions"] == second.json()["questions"]
    csrf = one.cookies.get("vista_flare_csrf")
    saved = one.put("/api/interview/roles/1/progress", data={"notes": "private", "completed_questions": "[0]"}, headers={"X-CSRF-Token": csrf})
    assert saved.status_code == 200
    assert one.get("/api/interview/roles/1").json()["progress"]["notes"] == "private"
    assert two.get("/api/interview/roles/1").json()["progress"]["notes"] == ""
