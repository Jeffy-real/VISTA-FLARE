"""Job Market Analytics API routes."""
from __future__ import annotations

from typing import Any, List
from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from backend.app.core.database import get_db
from backend.app.models.database_models import Company, Job, Role
from backend.app.schemas.prediction import MarketOverviewResponse

router = APIRouter(prefix="/api/market", tags=["market"])


@router.get("/overview", response_model=MarketOverviewResponse)
async def get_market_overview(db: Session = Depends(get_db)) -> MarketOverviewResponse:
    """Get aggregated job-market statistics."""
    total_jobs = db.query(Job).count()
    total_companies = db.query(Company).count()
    total_roles = db.query(Role).count()

    # Average salary
    avg_sal_res = db.query(func.avg(Job.salary_min), func.avg(Job.salary_max)).first()
    avg_salary = 0.0
    if avg_sal_res and avg_sal_res[0] and avg_sal_res[1]:
        avg_salary = round((float(avg_sal_res[0]) + float(avg_sal_res[1])) / 2, 2)

    # Work mode breakdown
    work_modes: dict[str, int] = {}
    wm_records = db.query(Job.work_mode, func.count(Job.id)).group_by(Job.work_mode).all()
    for wm, cnt in wm_records:
        work_modes[wm or "Unspecified"] = cnt

    # Top demanded roles
    role_records = (
        db.query(
            Job.normalized_role,
            func.count(Job.id).label("count"),
            func.avg(Job.salary_min).label("avg_min"),
            func.avg(Job.salary_max).label("avg_max"),
        )
        .group_by(Job.normalized_role)
        .order_by(func.count(Job.id).desc())
        .limit(10)
        .all()
    )
    top_roles = [
        {
            "role": r.normalized_role,
            "count": r.count,
            "avg_salary_min": round(float(r.avg_min), 0) if r.avg_min else None,
            "avg_salary_max": round(float(r.avg_max), 0) if r.avg_max else None,
        }
        for r in role_records
    ]

    # In-demand skills frequency
    skill_counts: dict[str, int] = {}
    all_jobs = db.query(Job.required_skills).all()
    total_skill_mentions = 0
    for j in all_jobs:
        if j.required_skills:
            for s in [s.strip() for s in j.required_skills.split(",") if s.strip()]:
                skill_counts[s] = skill_counts.get(s, 0) + 1
                total_skill_mentions += 1

    sorted_skills = sorted(skill_counts.items(), key=lambda x: x[1], reverse=True)[:12]
    top_skills = [
        {
            "skill": s[0],
            "count": s[1],
            "percentage": round((s[1] / max(total_jobs, 1)) * 100, 1),
        }
        for s in sorted_skills
    ]

    return MarketOverviewResponse(
        total_jobs=total_jobs,
        total_companies=total_companies,
        total_roles=total_roles,
        avg_salary=avg_salary,
        work_mode_distribution=work_modes,
        top_demanded_roles=top_roles,
        top_in_demand_skills=top_skills,
    )


@router.get("/roles")
async def get_market_roles(db: Session = Depends(get_db)) -> List[dict[str, Any]]:
    """Get market demand metrics for all career roles."""
    records = (
        db.query(
            Job.normalized_role,
            Job.job_category,
            func.count(Job.id).label("count"),
            func.avg(Job.salary_min).label("avg_min"),
            func.avg(Job.salary_max).label("avg_max"),
        )
        .group_by(Job.normalized_role, Job.job_category)
        .order_by(func.count(Job.id).desc())
        .all()
    )
    return [
        {
            "role": r.normalized_role,
            "category": r.job_category,
            "job_count": r.count,
            "salary_range": f"${float(r.avg_min):,.0f} - ${float(r.avg_max):,.0f}" if r.avg_min and r.avg_max else "Salary not disclosed",
            "avg_min": float(r.avg_min) if r.avg_min else None,
            "avg_max": float(r.avg_max) if r.avg_max else None,
        }
        for r in records
    ]


@router.get("/skills")
async def get_market_skills(db: Session = Depends(get_db)) -> List[dict[str, Any]]:
    """Get skill demand ranking across all postings."""
    skill_counts: dict[str, int] = {}
    all_jobs = db.query(Job.required_skills).all()
    for j in all_jobs:
        if j.required_skills:
            for s in [s.strip() for s in j.required_skills.split(",") if s.strip()]:
                skill_counts[s] = skill_counts.get(s, 0) + 1

    sorted_skills = sorted(skill_counts.items(), key=lambda x: x[1], reverse=True)
    return [{"skill": s[0], "mention_count": s[1]} for s in sorted_skills]


@router.get("/salaries")
async def get_market_salaries(db: Session = Depends(get_db)) -> List[dict[str, Any]]:
    """Get salary insights by role category."""
    records = (
        db.query(
            Job.job_category,
            func.count(Job.id).label("job_count"),
            func.avg(Job.salary_min).label("avg_min"),
            func.avg(Job.salary_max).label("avg_max"),
            func.min(Job.salary_min).label("min_sal"),
            func.max(Job.salary_max).label("max_sal"),
        )
        .group_by(Job.job_category)
        .all()
    )
    return [
        {
            "category": r.job_category,
            "job_count": r.job_count,
            "avg_min": round(float(r.avg_min), 0) if r.avg_min else None,
            "avg_max": round(float(r.avg_max), 0) if r.avg_max else None,
            "min_salary": float(r.min_sal) if r.min_sal else None,
            "max_salary": float(r.max_sal) if r.max_sal else None,
        }
        for r in records
    ]
