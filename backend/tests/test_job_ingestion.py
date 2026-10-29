"""Deterministic ingestion tests (providers are entirely mocked)."""
from datetime import datetime, timedelta

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.app.core.database import Base
from backend.app.models.database_models import Job
from backend.app.services.job_ingestion import ingest_jobs, normalize_job


class FakeProvider:
    def __init__(self, records=None, error=None):
        self.records, self.last_error, self.error = records or [], None, error

    def fetch_jobs(self, limit=100):
        if self.error:
            self.last_error = self.error
        return self.records


def session():
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False})
    Base.metadata.create_all(engine)
    return sessionmaker(bind=engine)()


def test_normalize_rejects_malformed_and_ingest_dedupes():
    assert normalize_job({}, "fake") is None
    db = session()
    records = [{"id": "a", "title": "Python Engineer"}, {"id": "a", "title": "Duplicate"}]
    result = ingest_jobs(db, FakeProvider(records), "fake")
    assert result["upserted"] == 1
    assert db.query(Job).count() == 1


def test_provider_failure_preserves_existing_job():
    db = session()
    ingest_jobs(db, FakeProvider([{"id": "a", "title": "Engineer"}]), "fake")
    result = ingest_jobs(db, FakeProvider(error="offline"), "fake")
    assert result["status"] == "failed"
    assert db.query(Job).one().active is True


def test_upsert_and_stale_policy():
    db = session()
    ingest_jobs(db, FakeProvider([{"id": "a", "title": "Old"}, {"id": "b", "title": "New"}]), "fake")
    ingest_jobs(db, FakeProvider([{"id": "b", "title": "Updated"}]), "fake", stale_after_hours=0)
    old = db.query(Job).filter(Job.provider_id == "a").one()
    new = db.query(Job).filter(Job.provider_id == "b").one()
    assert new.job_title == "Updated"
    assert old.stale is True and old.active is False
