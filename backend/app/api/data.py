"""Data API routes for roles, skills, companies, jobs, and resources."""
from typing import Any, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func
from sqlalchemy.orm import Session

from backend.app.core.database import get_db
from backend.app.models.database_models import Company, Job, LearningResource, Role, RoleSkill, Skill, SkillAlias
from backend.app.schemas.prediction import CompanyDetail, JobDetail, LearningResourceDetail, RoleDetail

router = APIRouter(prefix="/api", tags=["data"])


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
            "skills": j.required_skills.split(", ") if j.required_skills else [],
            "posting_date": j.posting_date,
        }
        for j in jobs
    ]


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
