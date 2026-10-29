"""Data API routes for roles, skills, companies, jobs, and resources."""
from datetime import datetime, timedelta
from typing import Any, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, or_
from sqlalchemy.orm import Session

from backend.app.core.database import get_db
from backend.app.models.database_models import Company, Job, LearningResource, Role, RoleSkill, Skill, SkillAlias
from backend.app.schemas.prediction import CompanyDetail, JobDetail, LearningResourceDetail, RoleDetail

router = APIRouter(prefix="/api", tags=["data"])


def _job_tokens(value: str | None) -> set[str]:
    return {token.strip().lower() for token in (value or "").replace(";", ",").split(",") if token.strip()}


def _job_freshness(job: Job) -> tuple[str, str]:
    """Label persisted data honestly; this endpoint never calls a provider."""
    if job.source_kind == "seed":
        return "seed_demo", "Seed/demo"
    if job.stale or not job.active:
        return "stale", "Stale"
    if job.last_checked and job.last_checked >= datetime.utcnow() - timedelta(hours=6):
        return "recently_refreshed", "Recently refreshed"
    return "cached", "Cached"


def _job_search_payload(job: Job, match_score: float | None = None, matched_skills: list[str] | None = None) -> dict[str, Any]:
    freshness, freshness_label = _job_freshness(job)
    return {
        "id": job.id, "company": job.company_name, "title": job.job_title, "role": job.normalized_role,
        "category": job.job_category, "employment_type": job.employment_type, "experience_level": job.experience_level,
        "work_mode": job.work_mode, "location": job.location, "country": job.country, "city": job.city,
        "salary_min": job.salary_min, "salary_max": job.salary_max, "currency": job.salary_currency,
        "salary_period": job.salary_period, "skills": sorted(_job_tokens(job.required_skills)), "posting_date": job.posting_date,
        "source": job.source, "provider_name": job.provider_name, "provider_id": job.provider_id,
        "source_url": job.source_url, "source_kind": job.source_kind, "active": job.active, "stale": job.stale,
        "first_seen": job.first_seen.isoformat() if job.first_seen else None,
        "last_seen": job.last_seen.isoformat() if job.last_seen else None,
        "last_checked": job.last_checked.isoformat() if job.last_checked else None,
        "freshness": freshness, "freshness_label": freshness_label,
        "match_score": match_score, "matched_skills": matched_skills or [],
    }


@router.get("/skills")
async def list_skills(
    category: Optional[str] = Query(None),
    limit: int = Query(200, le=500),
    db: Session = Depends(get_db),
) -> list[dict[str, Any]]:
    """List all skills."""
    query = db.query(Skill)
    if category:
        query = query.filter(Skill.category == category)
    skills = query.limit(limit).all()
    return [{"id": s.id, "name": s.name, "category": s.category} for s in skills]


@router.get("/roles")
async def list_roles(
    category: Optional[str] = Query(None),
    limit: int = Query(100, le=200),
    db: Session = Depends(get_db),
) -> list[dict[str, Any]]:
    """List all career roles."""
    query = db.query(Role)
    if category:
        query = query.filter(Role.category == category)
    roles = query.limit(limit).all()
    return [{"id": r.id, "name": r.name, "category": r.category} for r in roles]


@router.get("/roles/{role_id}", response_model=RoleDetail)
async def get_role(role_id: int, db: Session = Depends(get_db)) -> RoleDetail:
    """Get detailed information about a role."""
    role = db.query(Role).filter(Role.id == role_id).first()
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")

    # Get role skills
    role_skills = db.query(RoleSkill).filter(RoleSkill.role_name == role.name).all()
    skills_data = [
        {
            "skill": rs.skill_name,
            "importance": rs.importance,
            "level": rs.skill_level,
            "required": rs.required_or_preferred == "required",
        }
        for rs in role_skills
    ]

    # Get job counts and salary info
    job_stats = (
        db.query(
            func.count(Job.id).label("count"),
            func.avg(Job.salary_min).label("avg_min"),
            func.avg(Job.salary_max).label("avg_max"),
        )
        .filter(Job.normalized_role == role.name)
        .first()
    )

    return RoleDetail(
        id=role.id,
        name=role.name,
        category=role.category,
        skills=skills_data,
        job_count=job_stats.count or 0,
        avg_salary_min=float(job_stats.avg_min) if job_stats.avg_min else None,
        avg_salary_max=float(job_stats.avg_max) if job_stats.avg_max else None,
    )


@router.get("/companies")
async def list_companies(
    industry: Optional[str] = Query(None),
    limit: int = Query(50, le=200),
    db: Session = Depends(get_db),
) -> list[dict[str, Any]]:
    """List all companies."""
    query = db.query(Company)
    if industry:
        query = query.filter(Company.industry == industry)
    companies = query.limit(limit).all()

    result = []
    for c in companies:
        job_count = db.query(Job).filter(Job.company_id == c.id).count()
        result.append(
            {
                "id": c.id,
                "name": c.name,
                "country": c.country,
                "city": c.city,
                "industry": c.industry,
                "size": c.size,
                "website": c.website,
                "job_count": job_count,
            }
        )
    return result


@router.get("/companies/{company_id}")
async def get_company(company_id: int, db: Session = Depends(get_db)) -> dict[str, Any]:
    """Get detailed information about a company."""
    company = db.query(Company).filter(Company.id == company_id).first()
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")

    jobs = db.query(Job).filter(Job.company_id == company_id).all()

    return {
        "id": company.id,
        "name": company.name,
        "country": company.country,
        "city": company.city,
        "industry": company.industry,
        "size": company.size,
        "website": company.website,
        "jobs": [
            {
                "id": j.id,
                "title": j.job_title,
                "role": j.normalized_role,
                "location": j.location,
                "salary_range": f"{j.salary_currency} {j.salary_min:,.0f} - {j.salary_max:,.0f}" if j.salary_min else None,
                "salary_period": j.salary_period,
                "source": j.source,
                "provider_name": j.provider_name,
                "provider_id": j.provider_id,
                "source_url": j.source_url,
                "source_kind": j.source_kind,
                "active": j.active,
                "stale": j.stale,
                "first_seen": j.first_seen,
                "last_seen": j.last_seen,
                "last_checked": j.last_checked,
            }
            for j in jobs
        ],
    }


@router.get("/jobs")
async def list_jobs(
    role: Optional[str] = Query(None),
    location: Optional[str] = Query(None),
    limit: int = Query(50, le=200),
    db: Session = Depends(get_db),
) -> list[dict[str, Any]]:
    """List job postings."""
    query = db.query(Job)
    if role:
        query = query.filter(Job.normalized_role == role)
    if location:
        query = query.filter(Job.location.ilike(f"%{location}%"))
    jobs = query.limit(limit).all()

    return [
        {
            "id": j.id,
            "company": j.company_name,
            "title": j.job_title,
            "role": j.normalized_role,
            "category": j.job_category,
            "employment_type": j.employment_type,
            "experience_level": j.experience_level,
            "work_mode": j.work_mode,
            "location": j.location,
            "country": j.country,
            "city": j.city,
            "salary_min": j.salary_min,
            "salary_max": j.salary_max,
                "currency": j.salary_currency,
                "salary_period": j.salary_period,
                "skills": j.required_skills.split(", ") if j.required_skills else [],
                "posting_date": j.posting_date,
                "source": j.source,
                "provider_name": j.provider_name,
                "provider_id": j.provider_id,
                "source_url": j.source_url,
                "source_kind": j.source_kind,
                "active": j.active,
                "stale": j.stale,
                "first_seen": j.first_seen,
                "last_seen": j.last_seen,
                "last_checked": j.last_checked,
        }
        for j in jobs
    ]


@router.get("/job-search")
async def search_jobs(
    q: Optional[str] = Query(None, max_length=200),
    target_role: Optional[str] = Query(None, max_length=200),
    skills: Optional[str] = Query(None, max_length=2000),
    work_mode: Optional[str] = Query(None, max_length=60),
    experience_level: Optional[str] = Query(None, max_length=60),
    provider: Optional[str] = Query(None, max_length=60),
    freshness: Optional[str] = Query(None, pattern="^(external|seed|all)$"),
    sort: str = Query("relevance", pattern="^(relevance|recent)$"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=50),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    """Search persisted listings and compute an explainable, non-hiring match score."""
    query = db.query(Job)
    if q:
        needle = f"%{q.strip()}%"
        query = query.filter(or_(Job.job_title.ilike(needle), Job.company_name.ilike(needle), Job.location.ilike(needle), Job.required_skills.ilike(needle)))
    if work_mode:
        query = query.filter(Job.work_mode.ilike(work_mode))
    if experience_level:
        query = query.filter(Job.experience_level.ilike(experience_level))
    if provider:
        query = query.filter(Job.provider_name == provider)
    if freshness == "external":
        query = query.filter(Job.source_kind == "external")
    elif freshness == "seed":
        query = query.filter(Job.source_kind == "seed")

    submitted_skills = _job_tokens(skills)
    role_needle = (target_role or "").strip().lower()
    ranked: list[tuple[Job, float | None, list[str]]] = []
    for job in query.order_by(Job.last_checked.desc().nullslast(), Job.id.desc()).limit(1000).all():
        required = _job_tokens(job.required_skills)
        overlap = sorted(submitted_skills & required)
        if submitted_skills or role_needle:
            skill_component = len(overlap) / max(1, len(submitted_skills))
            role_component = 1.0 if role_needle and role_needle in (job.normalized_role or "").lower() else 0.0
            # Relevance only: skills 70%, target-role title match 30%.
            score = round((skill_component * 0.70 + role_component * 0.30) * 100, 1)
        else:
            score = None
        ranked.append((job, score, overlap))
    if sort == "relevance" and (submitted_skills or role_needle):
        ranked.sort(key=lambda item: (item[1] or 0, item[0].last_checked or datetime.min), reverse=True)
    total = len(ranked)
    start = (page - 1) * page_size
    selected = ranked[start:start + page_size]
    return {
        "items": [_job_search_payload(job, score, overlap) for job, score, overlap in selected],
        "page": page, "page_size": page_size, "total": total,
        "score_explanation": "Relevance combines submitted-skill overlap (70%) and target-role title match (30%). It is not a hiring probability.",
    }


@router.get("/jobs/{job_id}")
async def get_job(job_id: int, db: Session = Depends(get_db)) -> dict[str, Any]:
    """Get detailed job information."""
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    return {
        "id": job.id,
        "company": job.company_name,
        "title": job.job_title,
        "role": job.normalized_role,
        "category": job.job_category,
        "employment_type": job.employment_type,
        "experience_level": job.experience_level,
        "work_mode": job.work_mode,
        "location": job.location,
        "country": job.country,
        "city": job.city,
        "salary_min": job.salary_min,
        "salary_max": job.salary_max,
        "currency": job.salary_currency,
        "skills": job.required_skills.split(", ") if job.required_skills else [],
        "posting_date": job.posting_date,
        "source": job.source,
        "salary_period": job.salary_period,
        "provider_name": job.provider_name,
        "provider_id": job.provider_id,
        "source_url": job.source_url,
        "description": job.description,
        "source_kind": job.source_kind,
        "active": job.active,
        "stale": job.stale,
        "first_seen": job.first_seen,
        "last_seen": job.last_seen,
        "last_checked": job.last_checked,
    }


@router.get("/learning")
async def list_learning_resources(
    skill: Optional[str] = Query(None),
    limit: int = Query(50, le=200),
    db: Session = Depends(get_db),
) -> list[dict[str, Any]]:
    """List learning resources."""
    query = db.query(LearningResource)
    if skill:
        query = query.filter(LearningResource.skill == skill)
    resources = query.limit(limit).all()

    return [
        {
            "id": r.id,
            "skill": r.skill,
            "title": r.resource_title,
            "platform": r.platform,
            "type": r.resource_type,
            "url": r.url,
            "difficulty": r.difficulty,
            "duration": r.duration,
            "free_or_paid": r.free_or_paid,
            "provider": r.provider,
            "description": r.description,
        }
        for r in resources
    ]
