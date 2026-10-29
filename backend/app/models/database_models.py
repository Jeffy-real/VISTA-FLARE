"""SQLAlchemy ORM models for Vista Flare."""
from __future__ import annotations

from datetime import date, datetime
from sqlalchemy import DateTime, ForeignKey
from sqlalchemy.orm import relationship

from sqlalchemy import Boolean, Column, DateTime, Float, Integer, String, Text, UniqueConstraint

from backend.app.core.database import Base


class Role(Base):
    __tablename__ = "roles"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False, index=True)
    category = Column(String, index=True)


class Skill(Base):
    __tablename__ = "skills"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False, index=True)
    category = Column(String, index=True)


class RoleSkill(Base):
    __tablename__ = "role_skills"

    id = Column(Integer, primary_key=True)
    role_id = Column(Integer, index=True)
    role_name = Column(String, index=True)
    skill_name = Column(String, index=True)
    importance = Column(Float)
    skill_level = Column(String)
    required_or_preferred = Column(String)


class SkillAlias(Base):
    __tablename__ = "skill_aliases"

    id = Column(Integer, primary_key=True)
    alias = Column(String, unique=True, index=True)
    normalized_skill = Column(String, index=True)


class Company(Base):
    __tablename__ = "companies"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    country = Column(String)
    city = Column(String)
    industry = Column(String)
    size = Column(String)
    website = Column(String)


class Job(Base):
    __tablename__ = "jobs"
    __table_args__ = (
        UniqueConstraint("provider_name", "provider_id", name="uq_jobs_provider_record"),
    )

    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, index=True)
    company_name = Column(String, index=True)
    job_title = Column(String, index=True)
    normalized_role = Column(String, index=True)
    job_category = Column(String, index=True)
    employment_type = Column(String)
    experience_level = Column(String)
    work_mode = Column(String)
    location = Column(String)
    country = Column(String)
    city = Column(String)
    salary_min = Column(Float)
    salary_max = Column(Float)
    salary_currency = Column(String)
    salary_period = Column(String)
    required_skills = Column(String)
    posting_date = Column(String)
    source = Column(String)
    provider_name = Column(String, index=True)
    provider_id = Column(String, index=True)
    source_url = Column(String)
    description = Column(Text)
    raw_metadata = Column(Text)
    first_seen = Column(DateTime, index=True)
    last_seen = Column(DateTime, index=True)
    last_checked = Column(DateTime, index=True)
    active = Column(Boolean, default=False, nullable=False, index=True)
    stale = Column(Boolean, default=False, nullable=False, index=True)
    source_kind = Column(String, default="seed", nullable=False, index=True)


class LearningResource(Base):
    __tablename__ = "learning_resources"

    id = Column(Integer, primary_key=True, index=True)
    skill = Column(String, index=True)
    resource_title = Column(String)
    platform = Column(String)
    resource_type = Column(String)
    url = Column(String)
    difficulty = Column(String)
    duration = Column(String)
    free_or_paid = Column(String)
    provider = Column(String)
    description = Column(Text)
    last_verified = Column(String)


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(320), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    display_name = Column(String(120), nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)


class UserProfile(Base):
    """Normalized private profile payload kept separate from authentication data."""
    __tablename__ = "user_profiles"
    __table_args__ = (UniqueConstraint("user_id", name="uq_user_profile_user"),)
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    profile_json = Column(Text, nullable=False, default="{}")
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)


class UserSession(Base):
    __tablename__ = "user_sessions"
    id = Column(Integer, primary_key=True)
    token_hash = Column(String(64), unique=True, nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    csrf_token = Column(String(64), nullable=False)
    expires_at = Column(DateTime, nullable=False, index=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)


class Roadmap(Base):
    __tablename__ = "roadmaps"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    target_role = Column(String(200), nullable=False)
    content = Column(Text, nullable=False)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)


class SavedJob(Base):
    __tablename__ = "saved_jobs"
    __table_args__ = (UniqueConstraint("user_id", "job_id", name="uq_saved_jobs_user_job"),)
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    job_id = Column(Integer, ForeignKey("jobs.id"), nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    job = relationship("Job")


class Application(Base):
    __tablename__ = "applications"
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    job_id = Column(Integer, ForeignKey("jobs.id"), nullable=False)
    status = Column(String(40), nullable=False, default="saved")
    notes = Column(Text)
    applied_at = Column(DateTime)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    job = relationship("Job")


class PracticeProgress(Base):
    """Private, user-owned interview practice notes and progress."""
    __tablename__ = "practice_progress"
    __table_args__ = (UniqueConstraint("user_id", "role_id", name="uq_practice_user_role"),)
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    role_id = Column(Integer, ForeignKey("roles.id"), nullable=False, index=True)
    notes = Column(Text, nullable=False, default="")
    completed_questions = Column(Text, nullable=False, default="[]")
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)


class IngestionRun(Base):
    __tablename__ = "ingestion_runs"
    id = Column(Integer, primary_key=True)
    provider_name = Column(String, nullable=False, index=True)
    started_at = Column(DateTime, nullable=False, index=True)
    completed_at = Column(DateTime)
    status = Column(String, nullable=False, index=True)
    fetched_count = Column(Integer, default=0)
    upserted_count = Column(Integer, default=0)
    created_count = Column(Integer, default=0)
    updated_count = Column(Integer, default=0)
    error = Column(Text)


class ProviderHealth(Base):
    __tablename__ = "provider_health"
    id = Column(Integer, primary_key=True)
    provider_name = Column(String, unique=True, nullable=False, index=True)
    status = Column(String, nullable=False)
    last_checked = Column(DateTime, nullable=False, index=True)
    last_success = Column(DateTime)
    last_error = Column(Text)
    consecutive_failures = Column(Integer, nullable=False, default=0)


class InferenceTrace(Base):
    """Sanitized, request-correlated inference telemetry.

    The trace deliberately stores no submitted skill names, resumes, or other
    profile content. Anonymous callers receive an opaque one-time access token;
    signed-in users can retrieve only their own traces.
    """
    __tablename__ = "inference_traces"

    id = Column(String(36), primary_key=True)
    access_token_hash = Column(String(64), nullable=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    completed_at = Column(DateTime)
    expires_at = Column(DateTime, nullable=False, index=True)
    status = Column(String(24), nullable=False, default="running", index=True)
    model_type = Column(String(64))
    model_version = Column(String(64))
    duration_ms = Column(Float)
    input_feature_count = Column(Integer)
    output_class_count = Column(Integer)
    error_category = Column(String(64))
    stages_json = Column(Text, nullable=False, default="[]")
    top_results_json = Column(Text, nullable=False, default="[]")


class JobObservation(Base):
    __tablename__ = "job_observations"
    id = Column(Integer, primary_key=True)
    job_id = Column(Integer, ForeignKey("jobs.id"), nullable=False, index=True)
    observed_at = Column(DateTime, nullable=False, index=True)
    salary_min = Column(Float)
    salary_max = Column(Float)
    active = Column(Boolean, nullable=False, default=True)
    required_skills = Column(Text)
    job = relationship("Job")


class JobChangeEvent(Base):
    __tablename__ = "job_change_events"
    __table_args__ = (UniqueConstraint("dedupe_key", name="uq_job_change_dedupe"),)
    id = Column(Integer, primary_key=True)
    job_id = Column(Integer, ForeignKey("jobs.id"), nullable=False, index=True)
    event_type = Column(String, nullable=False, index=True)
    detected_at = Column(DateTime, nullable=False, index=True)
    details = Column(Text)
    dedupe_key = Column(String, nullable=False)
    job = relationship("Job")


class AlertPreference(Base):
    __tablename__ = "alert_preferences"
    __table_args__ = (UniqueConstraint("user_id", name="uq_alert_preferences_user"),)
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    enabled = Column(Boolean, nullable=False, default=True)
    target_roles = Column(Text, default="")
    skills = Column(Text, default="")
    saved_jobs = Column(Boolean, nullable=False, default=True)


class Notification(Base):
    __tablename__ = "notifications"
    __table_args__ = (UniqueConstraint("user_id", "dedupe_key", name="uq_notification_dedupe"),)
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    event_id = Column(Integer, ForeignKey("job_change_events.id"), index=True)
    title = Column(String, nullable=False)
    message = Column(Text, nullable=False)
    notification_type = Column(String, nullable=False, default="job_change")
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    read_at = Column(DateTime)
    dedupe_key = Column(String, nullable=False)
