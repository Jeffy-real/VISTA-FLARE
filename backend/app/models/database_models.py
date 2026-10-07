"""SQLAlchemy ORM models for Vista Flare."""
from __future__ import annotations

from datetime import date, datetime

from sqlalchemy import Column, Float, Integer, String, Text

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
