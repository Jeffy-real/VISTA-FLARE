"""Deterministic checks for persisted intelligence behavior (no network)."""
from datetime import datetime, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.app.core.database import Base
from backend.app.models.database_models import (AlertPreference, Job, JobChangeEvent, JobObservation,
    Notification, User)
from backend.app.services.job_ingestion import ingest_jobs
from backend.app.api.intelligence import market_trends
from backend.app.services.job_ingestion import _create_alerts


class Provider:
    last_error = None
    def __init__(self, rows): self.rows = rows
    def fetch_jobs(self, limit=100): return self.rows


def db_session():
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False})
    Base.metadata.create_all(engine)
    return sessionmaker(bind=engine)()


def test_events_and_notifications_are_deduplicated_and_owned():
    db = db_session()
    owner = User(email="a@example.com", password_hash="x", display_name="A")
    other = User(email="b@example.com", password_hash="x", display_name="B")
    db.add_all([owner, other]); db.flush()
    db.add_all([AlertPreference(user_id=owner.id, target_roles="Engineer"), AlertPreference(user_id=other.id, target_roles="Designer")]); db.commit()
    ingest_jobs(db, Provider([{"id": "j", "title": "Engineer", "normalized_role": "Engineer"}]), "fake")
    ingest_jobs(db, Provider([{"id": "j", "title": "Engineer", "normalized_role": "Engineer"}]), "fake")
    assert db.query(JobChangeEvent).count() == 1
    assert db.query(Notification).filter_by(user_id=owner.id).count() == 1
    assert db.query(Notification).filter_by(user_id=other.id).count() == 0


def test_trends_report_persisted_sample_and_source_metadata():
    db = db_session()
    job = Job(provider_name="fake", provider_id="j", job_title="Engineer", normalized_role="Engineer", company_name="Acme")
    db.add(job); db.flush()
    now = datetime.utcnow()
    db.add_all([JobObservation(job_id=job.id, observed_at=now, salary_min=10, salary_max=20, active=True),
                JobObservation(job_id=job.id, observed_at=now + timedelta(days=1), salary_min=12, salary_max=22, active=True)])
    db.commit()
    response = market_trends("Engineer", db, User(id=1, email="x", password_hash="x", display_name="x"))
    assert response["sample_size"] == 2
    assert response["source"] == "persisted job observations"
    assert len(response["points"]) == 2
