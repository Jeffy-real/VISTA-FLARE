"""Skill Gap Analysis, Company Matching, and Career Roadmap Engine for Vista Flare."""
from __future__ import annotations

from typing import Any, List, Optional
from sqlalchemy.orm import Session

from backend.app.models.database_models import Company, Job, LearningResource, Role, RoleSkill
from backend.app.schemas.prediction import (
    CompanyMatch,
    RoadmapStage,
    SkillAnalysisResponse,
    SkillMatch,
)
from backend.app.services.predictor import get_prediction_service

LEVEL_VALUES = {
    "missing": 0.0,
    "beginner": 0.35,
    "intermediate": 0.65,
    "advanced": 0.85,
    "expert": 1.0,
}


def analyze_skill_gap(
    target_role: str,
    user_skills: List[dict[str, Any]],
    db: Session,
    ai_match_score: Optional[float] = None,
) -> SkillAnalysisResponse:
    """Perform deterministic skill-gap analysis, company matching, and generate a personalized roadmap."""
    predictor = get_prediction_service()
    aliases = predictor.aliases

    # 1. Fetch role
    role = db.query(Role).filter(Role.name.ilike(target_role)).first()
    category = role.category if role else "General Tech"

    # 2. Fetch role required skills
    role_skills = db.query(RoleSkill).filter(RoleSkill.role_name.ilike(target_role)).all()
    if not role_skills and role:
        role_skills = db.query(RoleSkill).filter(RoleSkill.role_id == role.id).all()

    # Normalize user skills dictionary
    user_skill_map: dict[str, str] = {}
    for item in user_skills:
        raw_name = str(item.get("name", "")).strip()
        lvl = str(item.get("level", "intermediate")).lower()
        canonical = predictor._canonicalize_skill(raw_name)
        if canonical:
            user_skill_map[canonical] = lvl

    strong_skills: List[SkillMatch] = []
    developing_skills: List[SkillMatch] = []
    missing_skills: List[SkillMatch] = []

    total_importance = 0.0
    matched_importance = 0.0

    for rs in role_skills:
        skill_name = predictor._canonicalize_skill(rs.skill_name)
        imp = float(rs.importance)
        req_level = str(rs.skill_level).lower()
        req_val = LEVEL_VALUES.get(req_level, 0.65)
        total_importance += imp

        if skill_name in user_skill_map:
            u_level = user_skill_map[skill_name]
            u_val = LEVEL_VALUES.get(u_level, 0.65)

            if u_val >= req_val:
                strong_skills.append(
                    SkillMatch(
                        skill=rs.skill_name,
                        importance=imp,
                        user_level=u_level.capitalize(),
                        required_level=req_level.capitalize(),
                        status="strong",
                        explanation=f"Matches target competency ({u_level.capitalize()} >= {req_level.capitalize()}).",
                    )
                )
                matched_importance += imp
            else:
                developing_skills.append(
                    SkillMatch(
                        skill=rs.skill_name,
                        importance=imp,
                        user_level=u_level.capitalize(),
                        required_level=req_level.capitalize(),
                        status="developing",
                        explanation=f"Foundational capability present ({u_level.capitalize()}), recommended to advance to {req_level.capitalize()}.",
                    )
                )
                matched_importance += imp * (u_val / req_val)
        else:
            missing_skills.append(
                SkillMatch(
                    skill=rs.skill_name,
                    importance=imp,
                    user_level="None",
                    required_level=req_level.capitalize(),
                    status="missing",
                    explanation=f"Key requirement with {imp:.1f} priority weighting for {target_role}.",
                )
            )

    skill_match_score = round(matched_importance / total_importance, 4) if total_importance > 0 else 0.5

    # 3. Find learning resources for missing and developing skills
    gap_skills = [s.skill for s in missing_skills] + [s.skill for s in developing_skills]
    resources = (
        db.query(LearningResource)
        .filter(LearningResource.skill.in_(gap_skills))
        .limit(12)
        .all()
    )
    # Fallback to general resources if specific ones aren't populated
    if not resources:
        resources = db.query(LearningResource).limit(6).all()

    resource_dicts = [
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

    # 4. Deterministic Company Matching
    companies = db.query(Company).all()
    company_matches: List[CompanyMatch] = []
    user_skill_set = set(user_skill_map.keys())

    for c in companies:
        open_jobs = db.query(Job).filter(Job.company_id == c.id).all()
        # Role-relevant jobs
        relevant_jobs = [j for j in open_jobs if target_role.lower() in j.normalized_role.lower() or j.job_category == category]
        
        # Collect required skills for this company's relevant jobs
        comp_skills = set()
        for j in (relevant_jobs or open_jobs):
            if j.required_skills:
                for s in j.required_skills.split(", "):
                    comp_skills.add(predictor._canonicalize_skill(s))

        matched = list(user_skill_set.intersection(comp_skills))
        comp_score = round(len(matched) / max(len(comp_skills), 1), 2)
        if comp_score == 0.0 and relevant_jobs:
            comp_score = 0.55  # baseline industry alignment

        company_matches.append(
            CompanyMatch(
                company_id=c.id,
                company_name=c.name,
                industry=c.industry,
                location=f"{c.city}, {c.country}",
                match_score=min(1.0, max(0.40, comp_score)),
                matched_skills=matched[:4],
                open_jobs_count=len(relevant_jobs) or len(open_jobs),
            )
        )

    company_matches.sort(key=lambda x: x.match_score, reverse=True)
    top_companies = company_matches[:6]

    # 5. Personalized Career Roadmap
    missing_names = [s.skill for s in missing_skills]
    developing_names = [s.skill for s in developing_skills]
    strong_names = [s.skill for s in strong_skills]

    roadmap = generate_roadmap(target_role, category, strong_names, developing_names, missing_names)

    return SkillAnalysisResponse(
        target_role=target_role,
        role_category=category,
        ai_match_score=ai_match_score,
        skill_match_score=skill_match_score,
        strong_skills=strong_skills,
        developing_skills=developing_skills,
        missing_skills=missing_skills,
        learning_resources=resource_dicts,
        company_matches=top_companies,
        roadmap=roadmap,
    )


def generate_roadmap(
    role: str,
    category: str,
    strong: List[str],
    developing: List[str],
    missing: List[str],
) -> List[RoadmapStage]:
    """Generate a 5-stage personalized career roadmap based on skill gaps."""
    # Split missing skills into stages
    p1 = missing[:2] if len(missing) >= 2 else missing
    p2 = missing[2:5] if len(missing) > 2 else developing[:2]
    p3 = missing[5:8] if len(missing) > 5 else developing[2:4]

    return [
        RoadmapStage(
            stage_number=1,
            stage_name="Foundational Essentials",
            description=f"Establish bedrock competencies and solidify foundational toolsets required for {role}.",
            skills=p1 or ["Problem Solving", "Version Control (Git)"],
            suggested_projects=[
                f"Build a clean starter portfolio project demonstrating core syntax and fundamentals.",
                f"Implement automated unit tests and basic CI automation.",
            ],
            estimated_weeks=3,
        ),
        RoadmapStage(
            stage_number=2,
            stage_name="Core Role Competencies",
            description=f"Close critical skill gaps with hands-on practice in high-impact tools.",
            skills=p2 or ["Data Processing", "API Architecture"],
            suggested_projects=[
                f"End-to-end {role} workflow processing structured datasets with clean error handling.",
                f"Build and document an integration module connecting multiple services.",
            ],
            estimated_weeks=5,
        ),
        RoadmapStage(
            stage_number=3,
            stage_name="Advanced Specialization & Tooling",
            description=f"Elevate your engineering depth in production scenarios, optimizations, and cloud deployment.",
            skills=p3 or ["Cloud Deployment", "System Monitoring"],
            suggested_projects=[
                f"Deploy a containerized cloud microservice with observability, metrics, and automated tests.",
                f"Perform performance tuning and latency optimization on a benchmark workload.",
            ],
            estimated_weeks=4,
        ),
        RoadmapStage(
            stage_number=4,
            stage_name="Capstone Industry Project",
            description=f"Synthesize all skills into a demonstrable showcase project ready for technical recruiters.",
            skills=[role + " Architecture", "Production Deployment"],
            suggested_projects=[
                f"Production-grade {role} capstone showcasing full lifecycle development, documentation, and live demo.",
            ],
            estimated_weeks=4,
        ),
        RoadmapStage(
            stage_number=5,
            stage_name="Career Readiness & Interview Prep",
            description=f"Refine your technical communication, portfolio walkthroughs, and system design answers.",
            skills=["System Design", "Behavioral & Technical Interviews", "Portfolio Presentation"],
            suggested_projects=[
                f"Publish comprehensive README, architecture diagrams, and recorded demo on GitHub.",
                f"Complete 10 mock technical interview challenges focused on {role}.",
            ],
            estimated_weeks=2,
        ),
    ]
