#!/usr/bin/env python
"""Seed or reseed the Vista Flare SQLite database from CSV files."""
from __future__ import annotations

import csv
import sys
from pathlib import Path

# Ensure project root is in sys.path
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from backend.app.core.config import settings
from backend.app.core.database import Base, SessionLocal, engine
from backend.app.models.database_models import (
    Company,
    Job,
    LearningResource,
    Role,
    RoleSkill,
    Skill,
    SkillAlias,
)

SEED_DIR = PROJECT_ROOT / "data" / "seed"


def read_csv(filename: str) -> list[dict[str, str]]:
    path = SEED_DIR / filename
    if not path.exists():
        print(f"Warning: {path} not found.")
        return []
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def seed_database(reset: bool = False) -> None:
    print("=" * 60)
    print("Vista Flare - Database Seeding")
    print("=" * 60)

    if reset:
        print("Dropping existing tables...")
        Base.metadata.drop_all(bind=engine)

    print("Creating tables...")
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()
    try:
        # 1. Roles
        roles_data = read_csv("roles.csv")
        if roles_data:
            db.query(Role).delete()
            for row in roles_data:
                db.add(
                    Role(
                        id=int(row["role_id"]),
                        name=row["role_name"],
                        category=row.get("category", "General"),
                    )
                )
            db.commit()
            print(f"[OK] Seeded {len(roles_data)} roles")

        # 2. Skills
        skills_data = read_csv("skills.csv")
        if skills_data:
            db.query(Skill).delete()
            for row in skills_data:
                db.add(
                    Skill(
                        id=int(row["skill_id"]),
                        name=row["skill_name"],
                        category=row.get("category", "General"),
                    )
                )
            db.commit()
            print(f"[OK] Seeded {len(skills_data)} skills")

        # 3. Role Skills
        role_skills_data = read_csv("role_skills.csv")
        if role_skills_data:
            db.query(RoleSkill).delete()
            for i, row in enumerate(role_skills_data, start=1):
                db.add(
                    RoleSkill(
                        id=i,
                        role_id=int(row["role_id"]),
                        role_name=row["role_name"],
                        skill_name=row["skill_name"],
                        importance=float(row.get("importance", 0.7)),
                        skill_level=row.get("skill_level", "intermediate"),
                        required_or_preferred=row.get("required_or_preferred", "required"),
                    )
                )
            db.commit()
            print(f"[OK] Seeded {len(role_skills_data)} role-skill mappings")

        # 4. Skill Aliases
        aliases_data = read_csv("skill_aliases.csv")
        if aliases_data:
            db.query(SkillAlias).delete()
            for i, row in enumerate(aliases_data, start=1):
                db.add(
                    SkillAlias(
                        id=i,
                        alias=row["alias"],
                        normalized_skill=row["normalized_skill"],
                    )
                )
            db.commit()
            print(f"[OK] Seeded {len(aliases_data)} skill aliases")

        # 5. Companies
        companies_data = read_csv("companies.csv")
        if companies_data:
            db.query(Company).delete()
            for row in companies_data:
                db.add(
                    Company(
                        id=int(row["company_id"]),
                        name=row["company_name"],
                        country=row.get("company_country", "Global"),
                        city=row.get("company_city", "Remote"),
                        industry=row.get("company_industry", "Technology"),
                        size=row.get("company_size", "1000+"),
                        website=row.get("company_website", "https://example.com"),
                    )
                )
            db.commit()
            print(f"[OK] Seeded {len(companies_data)} companies")

        # 6. Jobs
        jobs_data = read_csv("jobs.csv")
        if jobs_data:
            db.query(Job).delete()
            for row in jobs_data:
                db.add(
                    Job(
                        id=int(row["job_id"]),
                        company_id=int(row.get("company_id", 1)),
                        company_name=row.get("company_name", "Tech Corp"),
                        job_title=row["job_title"],
                        normalized_role=row.get("normalized_role", row["job_title"]),
                        job_category=row.get("job_category", "Technology"),
                        employment_type=row.get("employment_type", "Full-time"),
                        experience_level=row.get("experience_level", "Mid"),
                        work_mode=row.get("work_mode", "Hybrid"),
                        location=row.get("location", "Remote"),
                        country=row.get("country", "US"),
                        city=row.get("city", "Remote"),
                        salary_min=float(row["salary_min"]) if row.get("salary_min") else None,
                        salary_max=float(row["salary_max"]) if row.get("salary_max") else None,
                        salary_currency=row.get("salary_currency", "USD"),
                        salary_period=row.get("salary_period", "yearly"),
                        required_skills=row.get("required_skills", ""),
                        posting_date=row.get("posting_date", "2024-01-01"),
                        source=row.get("source", "vista_flare_seed"),
                    )
                )
            db.commit()
            print(f"[OK] Seeded {len(jobs_data)} jobs")

        # 7. Learning Resources
        learning_data = read_csv("learning_resources.csv")
        if learning_data:
            db.query(LearningResource).delete()
            for row in learning_data:
                db.add(
                    LearningResource(
                        id=int(row["resource_id"]),
                        skill=row["skill"],
                        resource_title=row["resource_title"],
                        platform=row.get("platform", "Online"),
                        resource_type=row.get("resource_type", "Course"),
                        url=row["url"],
                        difficulty=row.get("difficulty", "Intermediate"),
                        duration=row.get("duration", "4 weeks"),
                        free_or_paid=row.get("free_or_paid", "Free"),
                        provider=row.get("provider", "Open Education"),
                        description=row.get("description", ""),
                        last_verified=row.get("last_verified", "2024-01-01"),
                    )
                )
            db.commit()
            print(f"[OK] Seeded {len(learning_data)} learning resources")

        print("=" * 60)
        print("Database seeding completed successfully!")
        print("=" * 60)
    finally:
        db.close()


if __name__ == "__main__":
    reset_flag = "--reset" in sys.argv
    seed_database(reset=reset_flag)
