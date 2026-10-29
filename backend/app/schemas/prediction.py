"""Pydantic schemas for Vista Flare API."""
from __future__ import annotations

from typing import Any, List, Optional
from pydantic import BaseModel, ConfigDict, Field


class SkillInput(BaseModel):
    name: str
    level: Optional[str] = "intermediate"


class PredictionRequest(BaseModel):
    skills: List[SkillInput]


class CareerRecommendation(BaseModel):
    rank: int
    role: str
    score: float = Field(..., ge=0.0, le=1.0)


class PredictionResponse(BaseModel):
    model_config = ConfigDict(protected_namespaces=())
    model: str
    model_version: str
    recommendations: List[CareerRecommendation]
    trace_id: Optional[str] = None
    trace_access_token: Optional[str] = None


class SkillMatch(BaseModel):
    skill: str
    importance: float
    user_level: str
    required_level: str
    status: str  # "strong", "developing", "missing"
    explanation: str


class RoadmapStage(BaseModel):
    stage_number: int
    stage_name: str
    description: str
    skills: List[str]
    suggested_projects: List[str]
    estimated_weeks: int


class CompanyMatch(BaseModel):
    company_id: int
    company_name: str
    industry: str
    location: str
    match_score: float
    matched_skills: List[str]
    open_jobs_count: int


class SkillAnalysisRequest(BaseModel):
    target_role: str
    skills: List[SkillInput]


class SkillAnalysisResponse(BaseModel):
    target_role: str
    role_category: str
    ai_match_score: Optional[float] = None
    skill_match_score: float
    strong_skills: List[SkillMatch]
    developing_skills: List[SkillMatch]
    missing_skills: List[SkillMatch]
    learning_resources: List[dict[str, Any]]
    company_matches: List[CompanyMatch]
    roadmap: List[RoadmapStage]


class RoleDetail(BaseModel):
    id: int
    name: str
    category: str
    skills: List[dict[str, Any]]
    job_count: int
    avg_salary_min: Optional[float]
    avg_salary_max: Optional[float]


class JobDetail(BaseModel):
    id: int
    company_name: str
    job_title: str
    normalized_role: str
    job_category: str
    employment_type: str
    experience_level: str
    work_mode: str
    location: str
    country: str
    city: str
    salary_min: Optional[float]
    salary_max: Optional[float]
    salary_currency: str
    required_skills: str


class CompanyDetail(BaseModel):
    id: int
    name: str
    country: str
    city: str
    industry: str
    size: str
    website: str
    job_count: int


class LearningResourceDetail(BaseModel):
    id: int
    skill: str
    resource_title: str
    platform: str
    resource_type: str
    url: str
    difficulty: str
    duration: str
    free_or_paid: str
    provider: str
    description: str


class ModelMetrics(BaseModel):
    model_config = ConfigDict(protected_namespaces=())
    model: str
    model_version: str
    accuracy: float
    top_3_accuracy: float
    precision_weighted: float
    recall_weighted: float
    f1_weighted: float
    num_skills: int
    num_classes: int
    training_samples: int
    architecture: str
    trained_at: str


class HealthResponse(BaseModel):
    model_config = ConfigDict(protected_namespaces=())
    status: str
    app_name: str
    model_loaded: bool
    model_type: Optional[str] = None
    model_load_error: Optional[str] = None
    database_connected: bool


class MarketOverviewResponse(BaseModel):
    total_jobs: int
    total_companies: int
    total_roles: int
    avg_salary: float
    work_mode_distribution: dict[str, int]
    top_demanded_roles: List[dict[str, Any]]
    top_in_demand_skills: List[dict[str, Any]]
