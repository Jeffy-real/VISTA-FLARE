"""Authentication, CSRF, and tenant-isolation coverage."""
from uuid import uuid4

from fastapi.testclient import TestClient

from backend.app.main import app


def test_users_are_isolated_and_mutations_require_csrf():
    suffix = uuid4().hex
    one, two = TestClient(app), TestClient(app)
    email_one, email_two = f"one-{suffix}@example.com", f"two-{suffix}@example.com"
    try:
        assert one.post("/api/auth/register", json={"email": email_one, "password": "correct horse", "display_name": "One"}).status_code == 201
        assert two.post("/api/auth/register", json={"email": email_two, "password": "correct horse", "display_name": "Two"}).status_code == 201
        # Keep the test independent of any prior local test data for a reused SQLite id.
        from backend.app.core.database import SessionLocal
        from backend.app.models.database_models import SavedJob, User
        db = SessionLocal()
        db.query(SavedJob).filter(SavedJob.user_id == one.get("/api/auth/me").json()["id"], SavedJob.job_id == 1).delete()
        db.commit()
        db.close()
        assert one.post("/api/saved-jobs", json={"job_id": 1}).status_code == 403
        csrf = one.cookies.get("vista_flare_csrf")
        assert one.post("/api/saved-jobs", json={"job_id": 1}, headers={"X-CSRF-Token": csrf}).status_code == 201
        assert one.get("/api/saved-jobs").json()[0]["job_id"] == 1
        assert two.get("/api/saved-jobs").json() == []
    finally:
        from backend.app.core.database import SessionLocal
        from backend.app.models.database_models import Application, Roadmap, SavedJob, User, UserSession
        db = SessionLocal()
        users = db.query(User).filter(User.email.in_([email_one, email_two])).all()
        ids = [u.id for u in users]
        for model in (UserSession, SavedJob, Application, Roadmap):
            db.query(model).filter(model.user_id.in_(ids)).delete(synchronize_session=False)
        for user in users:
            db.delete(user)
        db.commit()
        db.close()
