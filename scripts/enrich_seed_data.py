#!/usr/bin/env python
"""Enrich seed datasets for jobs and verified learning resources."""
from __future__ import annotations

import random
from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SEED_DIR = PROJECT_ROOT / "data" / "seed"


def enrich_jobs():
    roles = pd.read_csv(SEED_DIR / "roles.csv")
    companies = pd.read_csv(SEED_DIR / "companies.csv")
    role_skills = pd.read_csv(SEED_DIR / "role_skills.csv")
    existing_jobs = pd.read_csv(SEED_DIR / "jobs.csv")

    role_to_skills = {}
    for role_name, group in role_skills.groupby("role_name"):
        top_skills = group.sort_values("importance", ascending=False)["skill_name"].head(5).tolist()
        role_to_skills[role_name] = ", ".join(top_skills)

    salary_ranges = {
        "Data & AI": (95000, 185000),
        "Software Development": (90000, 175000),
        "Cloud & Infrastructure": (100000, 180000),
        "Cybersecurity": (95000, 170000),
        "Database & Enterprise": (90000, 160000),
        "Product & Business": (105000, 190000),
        "Design & UX": (85000, 155000),
        "Architecture & Consulting": (120000, 210000),
        "Technical Communication": (75000, 135000),
    }

    work_modes = ["Remote", "Hybrid", "On-site"]
    exp_levels = ["Junior", "Mid", "Senior", "Lead"]

    new_jobs = list(existing_jobs.to_dict("records"))
    next_id = max(j["job_id"] for j in new_jobs) + 1 if new_jobs else 1

    random.seed(42)

    for _, role_row in roles.iterrows():
        role_name = role_row["role_name"]
        category = role_row["category"]
        count_existing = sum(1 for j in new_jobs if j.get("normalized_role") == role_name)
        needed = max(0, 2 - count_existing)

        sal_min_base, sal_max_base = salary_ranges.get(category, (85000, 160000))
        role_skills_str = role_to_skills.get(role_name, "Problem Solving, Communication, Analytical Skills")

        for _ in range(needed):
            company = companies.sample(1, random_state=random.randint(1, 10000)).iloc[0]
            exp = random.choice(exp_levels)
            mode = random.choice(work_modes)

            mult = {"Junior": 0.8, "Mid": 1.0, "Senior": 1.3, "Lead": 1.6}[exp]
            sal_min = round((sal_min_base * mult) / 1000) * 1000
            sal_max = round((sal_max_base * mult) / 1000) * 1000

            job_title = f"{exp} {role_name}" if exp != "Mid" else role_name
            loc = f"{company['company_city']}, {company['company_country']}" if mode != "Remote" else "Remote"
            city = company["company_city"] if mode != "Remote" else "Remote"

            new_jobs.append(
                {
                    "job_id": next_id,
                    "company_id": int(company["company_id"]),
                    "company_name": company["company_name"],
                    "job_title": job_title,
                    "normalized_role": role_name,
                    "job_category": category,
                    "employment_type": "Full-time",
                    "experience_level": exp,
                    "work_mode": mode,
                    "location": loc,
                    "country": company["company_country"],
                    "city": city,
                    "salary_min": sal_min,
                    "salary_max": sal_max,
                    "salary_currency": "USD",
                    "salary_period": "yearly",
                    "required_skills": role_skills_str,
                    "posting_date": f"2024-02-{random.randint(1, 28):02d}",
                    "source": "vista_flare_seed",
                }
            )
            next_id += 1

    df_jobs = pd.DataFrame(new_jobs)
    df_jobs.to_csv(SEED_DIR / "jobs.csv", index=False)
    print(f"[OK] Saved {len(df_jobs)} jobs covering {df_jobs['normalized_role'].nunique()} roles.")


def enrich_learning():
    existing_learning = pd.read_csv(SEED_DIR / "learning_resources.csv")
    curated = [
        # Programming & CS
        {"skill": "Python", "resource_title": "Python for Everybody Specialization", "platform": "Coursera", "resource_type": "Specialization", "url": "https://www.coursera.org/specializations/python", "difficulty": "Beginner", "duration": "4 months", "free_or_paid": "Free audit", "provider": "University of Michigan", "description": "Learn to program and analyze data with Python.", "last_verified": "2024-03-01"},
        {"skill": "Python", "resource_title": "Scientific Computing with Python", "platform": "freeCodeCamp", "resource_type": "Course", "url": "https://www.freecodecamp.org/learn/scientific-computing-with-python/", "difficulty": "Intermediate", "duration": "300 hours", "free_or_paid": "Free", "provider": "freeCodeCamp", "description": "Hands-on data structures and algorithms in Python.", "last_verified": "2024-03-01"},
        {"skill": "SQL", "resource_title": "Databases and SQL for Data Science", "platform": "Coursera", "resource_type": "Course", "url": "https://www.coursera.org/learn/sql-for-data-science", "difficulty": "Beginner", "duration": "4 weeks", "free_or_paid": "Free audit", "provider": "IBM", "description": "Master relational databases, SQL queries, and aggregation.", "last_verified": "2024-03-01"},
        {"skill": "SQL", "resource_title": "Relational Database Certification", "platform": "freeCodeCamp", "resource_type": "Course", "url": "https://www.freecodecamp.org/learn/relational-database/", "difficulty": "Intermediate", "duration": "300 hours", "free_or_paid": "Free", "provider": "freeCodeCamp", "description": "PostgreSQL, Bash, and relational database design.", "last_verified": "2024-03-01"},
        {"skill": "JavaScript", "resource_title": "JavaScript Algorithms and Data Structures", "platform": "freeCodeCamp", "resource_type": "Course", "url": "https://www.freecodecamp.org/learn/javascript-algorithms-and-data-structures-v8/", "difficulty": "Beginner", "duration": "300 hours", "free_or_paid": "Free", "provider": "freeCodeCamp", "description": "Core JavaScript fundamentals, ES6, OOP, and functional programming.", "last_verified": "2024-03-01"},
        {"skill": "TypeScript", "resource_title": "TypeScript Handbook & Documentation", "platform": "Microsoft Learn", "resource_type": "Documentation", "url": "https://www.typescriptlang.org/docs/handbook/intro.html", "difficulty": "Intermediate", "duration": "Self-paced", "free_or_paid": "Free", "provider": "Microsoft", "description": "Official comprehensive guide to static typing with TypeScript.", "last_verified": "2024-03-01"},
        {"skill": "React", "resource_title": "Full Stack Open: Deep Dive to Modern Web Development", "platform": "University of Helsinki", "resource_type": "Course", "url": "https://fullstackopen.com/en/", "difficulty": "Intermediate", "duration": "12 weeks", "free_or_paid": "Free", "provider": "University of Helsinki", "description": "Deep dive into React, Redux, Node.js, REST and GraphQL.", "last_verified": "2024-03-01"},
        {"skill": "Node.js", "resource_title": "Back End Development and APIs", "platform": "freeCodeCamp", "resource_type": "Course", "url": "https://www.freecodecamp.org/learn/back-end-development-and-apis/", "difficulty": "Intermediate", "duration": "300 hours", "free_or_paid": "Free", "provider": "freeCodeCamp", "description": "Build microservices and RESTful APIs using Node.js and Express.", "last_verified": "2024-03-01"},

        # Data Science & Machine Learning
        {"skill": "Machine Learning", "resource_title": "Machine Learning Specialization", "platform": "Coursera", "resource_type": "Specialization", "url": "https://www.coursera.org/specializations/machine-learning-introduction", "difficulty": "Intermediate", "duration": "3 months", "free_or_paid": "Free audit", "provider": "DeepLearning.AI / Stanford", "description": "Supervised and unsupervised learning, best practices, and recommender systems by Andrew Ng.", "last_verified": "2024-03-01"},
        {"skill": "Deep Learning", "resource_title": "Deep Learning Specialization", "platform": "Coursera", "resource_type": "Specialization", "url": "https://www.coursera.org/specializations/deep-learning", "difficulty": "Advanced", "duration": "5 months", "free_or_paid": "Free audit", "provider": "DeepLearning.AI", "description": "Neural networks, CNNs, RNNs, transformers, and sequence models.", "last_verified": "2024-03-01"},
        {"skill": "TensorFlow", "resource_title": "TensorFlow Developer Professional Certificate", "platform": "Coursera", "resource_type": "Specialization", "url": "https://www.coursera.org/professional-certificates/tensorflow-in-practice", "difficulty": "Intermediate", "duration": "4 months", "free_or_paid": "Free audit", "provider": "DeepLearning.AI", "description": "Build and train neural network models in TensorFlow & Keras.", "last_verified": "2024-03-01"},
        {"skill": "PyTorch", "resource_title": "Deep Learning with PyTorch: A 60 Minute Blitz", "platform": "PyTorch", "resource_type": "Tutorial", "url": "https://pytorch.org/tutorials/beginner/deep_learning_60min_blitz.html", "difficulty": "Intermediate", "duration": "3 hours", "free_or_paid": "Free", "provider": "Linux Foundation / Meta", "description": "Hands-on tensor basics and neural networks with autograd.", "last_verified": "2024-03-01"},
        {"skill": "Pandas", "resource_title": "Kaggle Pandas Course", "platform": "Kaggle Learn", "resource_type": "Interactive Course", "url": "https://www.kaggle.com/learn/pandas", "difficulty": "Beginner", "duration": "4 hours", "free_or_paid": "Free", "provider": "Kaggle", "description": "Hands-on data manipulation, indexing, grouping, and cleaning.", "last_verified": "2024-03-01"},
        {"skill": "Natural Language Processing", "resource_title": "Natural Language Processing Specialization", "platform": "Coursera", "resource_type": "Specialization", "url": "https://www.coursera.org/specializations/natural-language-processing", "difficulty": "Advanced", "duration": "4 months", "free_or_paid": "Free audit", "provider": "DeepLearning.AI", "description": "Sentiment analysis, word embeddings, sequence models, and transformers.", "last_verified": "2024-03-01"},
        {"skill": "Computer Vision", "resource_title": "Computer Vision Basics", "platform": "Coursera", "resource_type": "Course", "url": "https://www.coursera.org/learn/computer-vision-basics", "difficulty": "Intermediate", "duration": "4 weeks", "free_or_paid": "Free audit", "provider": "University at Buffalo", "description": "Image processing, edge detection, filtering, and feature matching.", "last_verified": "2024-03-01"},
        {"skill": "Large Language Models", "resource_title": "Generative AI with Large Language Models", "platform": "Coursera", "resource_type": "Course", "url": "https://www.coursera.org/learn/generative-ai-with-llms", "difficulty": "Advanced", "duration": "3 weeks", "free_or_paid": "Free audit", "provider": "DeepLearning.AI & AWS", "description": "Transformer architecture, RLHF, fine-tuning, and model deployment.", "last_verified": "2024-03-01"},

        # Cloud & DevOps
        {"skill": "Docker", "resource_title": "Docker for Developers", "platform": "freeCodeCamp", "resource_type": "Tutorial", "url": "https://www.freecodecamp.org/news/the-docker-handbook/", "difficulty": "Intermediate", "duration": "10 hours", "free_or_paid": "Free", "provider": "freeCodeCamp", "description": "Containers, Dockerfiles, volumes, networks, and compose.", "last_verified": "2024-03-01"},
        {"skill": "Kubernetes", "resource_title": "Introduction to Kubernetes", "platform": "edX", "resource_type": "Course", "url": "https://www.edx.org/learn/kubernetes/the-linux-foundation-introduction-to-kubernetes", "difficulty": "Intermediate", "duration": "14 weeks", "free_or_paid": "Free audit", "provider": "The Linux Foundation", "description": "Container orchestration, pods, deployments, services, and cluster management.", "last_verified": "2024-03-01"},
        {"skill": "AWS", "resource_title": "AWS Cloud Practitioner Essentials", "platform": "AWS Skill Builder", "resource_type": "Course", "url": "https://explore.skillbuilder.aws/learn/course/external/view/elearning/134/aws-cloud-practitioner-essentials", "difficulty": "Beginner", "duration": "6 hours", "free_or_paid": "Free", "provider": "Amazon Web Services", "description": "Foundational understanding of the AWS Cloud platform, services, and security.", "last_verified": "2024-03-01"},
        {"skill": "Google Cloud", "resource_title": "Google Cloud Computing Foundations", "platform": "Google Cloud Skills Boost", "resource_type": "Course", "url": "https://www.cloudskillsboost.google/course_templates/153", "difficulty": "Beginner", "duration": "10 hours", "free_or_paid": "Free", "provider": "Google Cloud", "description": "Infrastructure, BigQuery, Compute Engine, and cloud networking.", "last_verified": "2024-03-01"},
        {"skill": "Linux", "resource_title": "Introduction to Linux", "platform": "edX", "resource_type": "Course", "url": "https://www.edx.org/learn/linux/the-linux-foundation-introduction-to-linux", "difficulty": "Beginner", "duration": "14 weeks", "free_or_paid": "Free audit", "provider": "The Linux Foundation", "description": "Linux command line, file system hierarchy, permissions, and scripting.", "last_verified": "2024-03-01"},
        {"skill": "Git", "resource_title": "Git & GitHub Crash Course", "platform": "freeCodeCamp", "resource_type": "Tutorial", "url": "https://www.freecodecamp.org/news/git-and-github-crash-course/", "difficulty": "Beginner", "duration": "2 hours", "free_or_paid": "Free", "provider": "freeCodeCamp", "description": "Version control, branching, pull requests, and collaboration.", "last_verified": "2024-03-01"},

        # Cybersecurity
        {"skill": "Cybersecurity", "resource_title": "Google Cybersecurity Professional Certificate", "platform": "Coursera", "resource_type": "Professional Certificate", "url": "https://www.coursera.org/professional-certificates/google-cybersecurity", "difficulty": "Beginner", "duration": "6 months", "free_or_paid": "Free audit", "provider": "Google", "description": "SIEM tools, Python automation, threat intelligence, and network security.", "last_verified": "2024-03-01"},
        {"skill": "Penetration Testing", "resource_title": "Penetration Testing Fundamentals", "platform": "Cybrary", "resource_type": "Course", "url": "https://www.cybrary.it/course/penetration-testing-and-ethical-hacking", "difficulty": "Intermediate", "duration": "15 hours", "free_or_paid": "Free", "provider": "Cybrary", "description": "Vulnerability scanning, exploitation, Metasploit, and reporting.", "last_verified": "2024-03-01"},
        {"skill": "Network Security", "resource_title": "Networking Basics", "platform": "Cisco Networking Academy", "resource_type": "Course", "url": "https://www.netacad.com/courses/networking/networking-basics", "difficulty": "Beginner", "duration": "22 hours", "free_or_paid": "Free", "provider": "Cisco", "description": "Protocols, IP addressing, routing, switching, and security fundamentals.", "last_verified": "2024-03-01"},

        # Design & UX
        {"skill": "UI/UX Design", "resource_title": "Google UX Design Professional Certificate", "platform": "Coursera", "resource_type": "Professional Certificate", "url": "https://www.coursera.org/professional-certificates/google-ux-design", "difficulty": "Beginner", "duration": "6 months", "free_or_paid": "Free audit", "provider": "Google", "description": "User research, wireframing, Figma prototyping, and usability testing.", "last_verified": "2024-03-01"},
        {"skill": "Figma", "resource_title": "Figma for UI Designers", "platform": "freeCodeCamp", "resource_type": "Course", "url": "https://www.freecodecamp.org/news/learn-figma-to-design-mobile-and-web-apps/", "difficulty": "Beginner", "duration": "4 hours", "free_or_paid": "Free", "provider": "freeCodeCamp", "description": "Design components, autolayout, responsive constraints, and design systems.", "last_verified": "2024-03-01"},

        # Business, Product & Management
        {"skill": "Product Management", "resource_title": "Digital Product Management: Modern Fundamentals", "platform": "Coursera", "resource_type": "Course", "url": "https://www.coursera.org/learn/uva-darden-digital-product-management", "difficulty": "Beginner", "duration": "4 weeks", "free_or_paid": "Free audit", "provider": "University of Virginia", "description": "Product roadmaps, user stories, agile execution, and growth metrics.", "last_verified": "2024-03-01"},
        {"skill": "Agile", "resource_title": "Applied Scrum for Agile Project Management", "platform": "edX", "resource_type": "Course", "url": "https://www.edx.org/learn/agile/university-of-maryland-applied-scrum-for-agile-project-management", "difficulty": "Beginner", "duration": "5 weeks", "free_or_paid": "Free audit", "provider": "University of Maryland", "description": "Scrum ceremonies, sprint planning, backlogs, and agile delivery.", "last_verified": "2024-03-01"},
    ]

    all_resources = list(existing_learning.to_dict("records"))
    existing_titles = {r["resource_title"].strip().lower() for r in all_resources}
    next_id = max(r["resource_id"] for r in all_resources) + 1 if all_resources else 1

    for c in curated:
        if c["resource_title"].strip().lower() not in existing_titles:
            c["resource_id"] = next_id
            all_resources.append(c)
            next_id += 1

    df_learning = pd.DataFrame(all_resources)
    df_learning.to_csv(SEED_DIR / "learning_resources.csv", index=False)
    print(f"[OK] Saved {len(df_learning)} learning resources covering {df_learning['skill'].nunique()} skills.")


def main():
    print("=" * 60)
    print("Enriching Seed Data")
    print("=" * 60)
    enrich_jobs()
    enrich_learning()
    print("=" * 60)


if __name__ == "__main__":
    main()
