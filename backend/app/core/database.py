"""SQLite database setup and seed loading."""
from __future__ import annotations

import csv
from pathlib import Path
from typing import Generator

from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import Session, declarative_base, sessionmaker

from backend.app.core.config import PROJECT_ROOT, get_settings

settings = get_settings()
engine = create_engine(settings.database_url, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

SEED_DIR = PROJECT_ROOT / "data" / "seed"


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    # Import models to register them with Base.metadata
    from backend.app.models.database_models import (Application, Company, Job, LearningResource, Roadmap, Role,
        RoleSkill, SavedJob, Skill, SkillAlias, User, UserSession, IngestionRun, ProviderHealth,
        JobObservation, JobChangeEvent, AlertPreference, Notification, PracticeProgress, InferenceTrace)

    Base.metadata.create_all(bind=engine)
    _migrate_job_columns()
    _migrate_ingestion_columns()
    _prune_expired_inference_traces()
    db = SessionLocal()
    try:
        if db.query(Role).count() == 0:
            _seed_roles(db)
        if db.query(Skill).count() == 0:
            _seed_skills(db)
        if db.query(RoleSkill).count() == 0:
            _seed_role_skills(db)
        if db.query(SkillAlias).count() == 0:
            _seed_aliases(db)
        if db.query(Company).count() == 0:
            _seed_companies(db)
        if db.query(Job).count() == 0:
            _seed_jobs(db)
        if db.query(LearningResource).count() == 0:
            _seed_learning(db)
        db.commit()
    finally:
        db.close()


def _read_csv(filename: str) -> list[dict[str, str]]:
    with open(SEED_DIR / filename, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def _migrate_job_columns() -> None:
    """Add ingestion columns to databases created by older releases."""
    columns = {
        "provider_name": "VARCHAR", "provider_id": "VARCHAR", "source_url": "VARCHAR",
        "description": "TEXT", "raw_metadata": "TEXT", "first_seen": "DATETIME",
        "last_seen": "DATETIME", "last_checked": "DATETIME", "active": "BOOLEAN DEFAULT 0",
        "stale": "BOOLEAN DEFAULT 0", "source_kind": "VARCHAR DEFAULT 'seed'",
    }
    existing = {c["name"] for c in inspect(engine).get_columns("jobs")}
    with engine.begin() as conn:
        for name, declaration in columns.items():
            if name not in existing:
                conn.execute(text(f"ALTER TABLE jobs ADD COLUMN {name} {declaration}"))
        conn.execute(text("CREATE UNIQUE INDEX IF NOT EXISTS uq_jobs_provider_record ON jobs(provider_name, provider_id)"))


def _migrate_ingestion_columns() -> None:
    """Add run counters without rebuilding existing ingestion history."""
    if "ingestion_runs" not in inspect(engine).get_table_names():
        return
    existing = {c["name"] for c in inspect(engine).get_columns("ingestion_runs")}
    with engine.begin() as conn:
        if "created_count" not in existing:
            conn.execute(text("ALTER TABLE ingestion_runs ADD COLUMN created_count INTEGER DEFAULT 0"))
        if "updated_count" not in existing:
            conn.execute(text("ALTER TABLE ingestion_runs ADD COLUMN updated_count INTEGER DEFAULT 0"))


def _prune_expired_inference_traces() -> None:
    """Bound operational telemetry retention without touching application data."""
    from datetime import datetime
    from backend.app.models.database_models import InferenceTrace

    db = SessionLocal()
    try:
        db.query(InferenceTrace).filter(InferenceTrace.expires_at < datetime.utcnow()).delete(
            synchronize_session=False
        )
        db.commit()
    finally:
        db.close()


def _seed_roles(db: Session) -> None:
    from backend.app.models.database_models import Role

    for row in _read_csv("roles.csv"):
        db.add(Role(id=int(row["role_id"]), name=row["role_name"], category=row["category"]))


def _seed_skills(db: Session) -> None:
    from backend.app.models.database_models import Skill

    for row in _read_csv("skills.csv"):
        db.add(Skill(id=int(row["skill_id"]), name=row["skill_name"], category=row["category"]))


def _seed_role_skills(db: Session) -> None:
    from backend.app.models.database_models import RoleSkill

    for i, row in enumerate(_read_csv("role_skills.csv"), start=1):
        db.add(
            RoleSkill(
                id=i,
                role_id=int(row["role_id"]),
                role_name=row["role_name"],
                skill_name=row["skill_name"],
                importance=float(row["importance"]),
                skill_level=row["skill_level"],
                required_or_preferred=row["required_or_preferred"],
            )
        )


def _seed_aliases(db: Session) -> None:
    from backend.app.models.database_models import SkillAlias

    for i, row in enumerate(_read_csv("skill_aliases.csv"), start=1):
        db.add(SkillAlias(id=i, alias=row["alias"], normalized_skill=row["normalized_skill"]))


def _seed_companies(db: Session) -> None:
    from backend.app.models.database_models import Company

    for row in _read_csv("companies.csv"):
        db.add(
            Company(
                id=int(row["company_id"]),
                name=row["company_name"],
                country=row["company_country"],
                city=row["company_city"],
                industry=row["company_industry"],
                size=row["company_size"],
                website=row["company_website"],
            )
        )


def _seed_jobs(db: Session) -> None:
    from backend.app.models.database_models import Job

    for row in _read_csv("jobs.csv"):
        db.add(
            Job(
                id=int(row["job_id"]),
                company_id=int(row["company_id"]),
                company_name=row["company_name"],
                job_title=row["job_title"],
                normalized_role=row["normalized_role"],
                job_category=row["job_category"],
                employment_type=row["employment_type"],
                experience_level=row["experience_level"],
                work_mode=row["work_mode"],
                location=row["location"],
                country=row["country"],
                city=row["city"],
                salary_min=float(row["salary_min"]),
                salary_max=float(row["salary_max"]),
                salary_currency=row["salary_currency"],
                salary_period=row["salary_period"],
                required_skills=row["required_skills"],
                posting_date=row["posting_date"],
                source=row["source"],
                source_kind="seed",
                active=False,
                stale=False,
            )
        )


def _seed_learning(db: Session) -> None:
    from backend.app.models.database_models import LearningResource

    for row in _read_csv("learning_resources.csv"):
        db.add(
            LearningResource(
                id=int(row["resource_id"]),
                skill=row["skill"],
                resource_title=row["resource_title"],
                platform=row["platform"],
                resource_type=row["resource_type"],
                url=row["url"],
                difficulty=row["difficulty"],
                duration=row["duration"],
                free_or_paid=row["free_or_paid"],
                provider=row["provider"],
                description=row["description"],
                last_verified=row["last_verified"],
            )
        )
