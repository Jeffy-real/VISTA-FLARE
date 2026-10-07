"""Shared utilities for the Vista Flare data and model pipeline."""
from __future__ import annotations

import json
import random
from pathlib import Path
from typing import Dict, Iterable, List, Tuple

import numpy as np
import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = PROJECT_ROOT / "data"
SEED_DIR = DATA_DIR / "seed"
PROCESSED_DIR = DATA_DIR / "processed"
MODELS_DIR = PROJECT_ROOT / "models"
ARTIFACTS_DIR = PROJECT_ROOT / "artifacts"
REPORTS_DIR = PROJECT_ROOT / "reports"
PLOTS_DIR = REPORTS_DIR / "plots"
CONFUSION_DIR = REPORTS_DIR / "confusion_matrices"
CLASSIFICATION_DIR = REPORTS_DIR / "classification_reports"

RANDOM_SEED = 42
LEVEL_VALUES = {
    "missing": 0.0,
    "beginner": 0.35,
    "intermediate": 0.65,
    "advanced": 0.85,
    "expert": 1.0,
}
LEVEL_ORDER = ["beginner", "intermediate", "advanced", "expert"]

SUPPLEMENTAL_SKILLS = [
    "Artificial Intelligence", "Natural Language Processing", "Large Language Models", "Apex", "Spring", ".NET",
    "Laravel", "React Native", "Objective-C", "Mobile Development", "NoSQL", "Data Modeling",
    "Business Intelligence", "Dashboard Design", "Feature Engineering", "Model Evaluation", "Model Deployment",
    "Experiment Tracking", "MLflow", "Hugging Face", "Prompt Engineering", "Vector Databases", "RAG",
    "LangChain", "OpenAI API", "Claude API", "MLOps", "Model Monitoring", "A/B Testing",
    "Time Series Analysis", "Forecasting", "Bayesian Statistics", "Optimization", "Operations Research",
    "Financial Modeling", "Risk Analysis", "Fraud Detection", "Recommendation Systems", "Search",
    "Information Retrieval", "Speech Recognition", "Image Processing", "OpenCV", "CUDA", "GPU Computing",
    "Embedded Systems", "Firmware", "Distributed Systems", "Event-Driven Architecture", "Serverless",
    "Cloud Architecture", "Cloud Security", "Identity and Access Management", "IAM", "VPC", "Load Balancing",
    "Observability", "Monitoring", "Prometheus", "Grafana", "Logging", "Splunk", "Datadog",
    "Networking", "TCP/IP", "DNS", "Firewalls", "VPN", "Zero Trust", "Threat Modeling",
    "Vulnerability Assessment", "Malware Analysis", "Threat Intelligence", "Security Operations",
    "Compliance", "GDPR", "SOC 2", "ISO 27001", "NIST", "Secure SDLC", "Code Review",
    "Static Analysis", "Dynamic Analysis", "SAST", "DAST", "Secrets Management", "Incident Management",
    "Backup and Recovery", "Disaster Recovery", "High Availability", "Performance Tuning", "Caching",
    "Message Queues", "RabbitMQ", "Celery", "gRPC", "WebSockets", "OAuth", "JWT", "Authentication",
    "Authorization", "Postman", "Swagger", "OpenAPI", "Domain-Driven Design", "Clean Architecture",
    "Design Patterns", "SOLID", "Functional Programming", "Concurrency", "Multithreading", "Memory Management",
    "Compiler Design", "Game Development", "Unity", "Unreal Engine", "AR/VR", "Blockchain", "Solidity",
    "Smart Contracts", "Web3", "Quality Assurance", "Manual Testing", "Automation Testing", "Cypress",
    "Playwright", "Mocha", "Chai", "Vitest", "Storybook", "Webpack", "Vite", "Babel",
    "Tailwind CSS", "Sass", "Responsive Design", "Accessibility", "WCAG", "Design Systems",
    "Interaction Design", "Visual Design", "Information Architecture", "Usability Testing", "Content Strategy",
    "Technical Documentation", "API Documentation", "Markdown", "Diagramming", "Stakeholder Management",
    "Requirements Analysis", "Process Modeling", "UML", "BPMN", "Change Management", "Risk Management",
    "Budgeting", "Roadmapping", "Product Strategy", "Market Research", "Customer Discovery", "Analytics",
    "Google Analytics", "Mixpanel", "Amplitude", "CRM", "HubSpot", "ServiceNow", "Workday",
    "Oracle ERP", "SAP S/4HANA", "ABAP", "Business Process Mapping", "Training", "Mentoring",
    "Presentation Skills", "Negotiation", "Critical Thinking", "Creativity", "Adaptability", "Time Management",
    "Customer Support", "IT Support", "Troubleshooting", "Windows Server", "Active Directory", "PowerShell",
    "Bash", "Shell Scripting", "Scripting", "Regular Expressions", "Data Cleaning", "Data Governance",
    "Data Quality", "Master Data Management", "Metadata Management", "Data Catalogs", "Data Privacy",
    "Data Ethics", "Data Storytelling", "Report Automation", "KPI Design", "OKRs", "Experiment Design",
    "Causal Inference", "Survey Design", "Qualitative Research", "Quantitative Research", "Persona Development",
    "Journey Mapping", "Design Thinking", "Service Design", "Brand Design", "Typography", "Color Theory",
    "Motion Design", "Video Editing", "Copywriting", "Localization", "Internationalization", "RESTful Services",
    "Batch Processing", "Stream Processing", "Lakehouse", "Data Lake", "Delta Lake", "Data Mesh", "ELT",
    "Data Pipelines", "Big Data", "Cloud Storage", "Containerization", "Infrastructure as Code",
    "Release Management", "Build Automation", "Configuration Management", "Package Management",
]


def ensure_directories() -> None:
    for path in [PROCESSED_DIR, MODELS_DIR, ARTIFACTS_DIR, PLOTS_DIR, CONFUSION_DIR, CLASSIFICATION_DIR]:
        path.mkdir(parents=True, exist_ok=True)


def set_global_seed(seed: int = RANDOM_SEED) -> None:
    random.seed(seed)
    np.random.seed(seed)
    try:
        import tensorflow as tf

        tf.keras.utils.set_random_seed(seed)
        tf.config.experimental.enable_op_determinism()
    except Exception:
        pass


def normalize_skill_name(name: str) -> str:
    if name is None:
        return ""
    cleaned = str(name).strip()
    if not cleaned:
        return ""
    special = {
        "c#": "C#",
        "c++": "C++",
        ".net": ".NET",
        "dbt": "dbt",
        "node.js": "Node.js",
        "next.js": "Next.js",
        "vue.js": "Vue",
        "react.js": "React",
        "powerbi": "Power BI",
        "power bi": "Power BI",
        "github actions": "GitHub Actions",
        "ci/cd": "CI/CD",
        "rest api": "REST API",
        "llms": "LLMs",
        "aws": "AWS",
        "sql": "SQL",
        "html": "HTML",
        "css": "CSS",
        "nlp": "NLP",
        "owasp": "OWASP",
        "soc": "SOC",
        "siem": "SIEM",
        "iam": "IAM",
        "vpc": "VPC",
        "jwt": "JWT",
        "oauth": "OAuth",
        "gdpr": "GDPR",
        "sast": "SAST",
        "dast": "DAST",
        "grpc": "gRPC",
    }
    key = cleaned.lower().replace("_", " ").strip()
    if key in special:
        return special[key]
    return " ".join(word if word.isupper() else word.capitalize() for word in cleaned.replace("_", " ").split())


def load_aliases() -> Dict[str, str]:
    aliases_path = SEED_DIR / "skill_aliases.csv"
    aliases: Dict[str, str] = {}
    if aliases_path.exists():
        df = pd.read_csv(aliases_path)
        for _, row in df.iterrows():
            alias = str(row["alias"]).strip().lower()
            normalized = normalize_skill_name(row["normalized_skill"])
            aliases[alias] = normalized
            aliases[alias.replace(".", "").replace(" ", "")] = normalized
    return aliases


def canonicalize_skill(name: str, aliases: Dict[str, str] | None = None) -> str:
    aliases = aliases or load_aliases()
    raw = str(name).strip()
    if not raw:
        return ""
    key = raw.lower()
    compact = key.replace(".", "").replace(" ", "")
    if key in aliases:
        return aliases[key]
    if compact in aliases:
        return aliases[compact]
    return normalize_skill_name(raw)


def load_seed_data() -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    roles = pd.read_csv(SEED_DIR / "roles.csv")
    skills = pd.read_csv(SEED_DIR / "skills.csv")
    role_skills = pd.read_csv(SEED_DIR / "role_skills.csv")
    aliases = load_aliases()
    skills["skill_name"] = skills["skill_name"].map(lambda x: canonicalize_skill(x, aliases))
    role_skills["skill_name"] = role_skills["skill_name"].map(lambda x: canonicalize_skill(x, aliases))
    return roles, skills, role_skills


def build_skill_vocabulary() -> List[str]:
    roles, skills, role_skills = load_seed_data()
    aliases = load_aliases()
    names = set(skills["skill_name"].dropna().map(lambda x: canonicalize_skill(x, aliases)))
    names.update(role_skills["skill_name"].dropna().map(lambda x: canonicalize_skill(x, aliases)))
    names.update(canonicalize_skill(s, aliases) for s in SUPPLEMENTAL_SKILLS)
    names = {n for n in names if n and n.lower() != "nan"}
    return sorted(names)


def encode_profile(skills: Iterable[Dict[str, str | float]], skill_to_index: Dict[str, int], aliases: Dict[str, str] | None = None) -> np.ndarray:
    aliases = aliases or load_aliases()
    vector = np.zeros(len(skill_to_index), dtype=np.float32)
    for item in skills:
        if isinstance(item, str):
            name = item
            level_value = 0.75
        else:
            name = str(item.get("name", ""))
            raw_level = item.get("level", "intermediate")
            if isinstance(raw_level, (int, float)):
                level_value = float(raw_level)
            else:
                level_value = LEVEL_VALUES.get(str(raw_level).lower(), 0.65)
        canonical = canonicalize_skill(name, aliases)
        idx = skill_to_index.get(canonical)
        if idx is not None:
            vector[idx] = max(vector[idx], max(0.0, min(1.0, level_value)))
    return vector


def load_processed_training() -> tuple[np.ndarray, np.ndarray, list[str], list[str], pd.DataFrame]:
    examples_path = PROCESSED_DIR / "training_examples.csv"
    skill_map_path = ARTIFACTS_DIR / "skill_mapping.json"
    role_map_path = ARTIFACTS_DIR / "role_mapping.json"
    if not examples_path.exists():
        raise FileNotFoundError("Missing processed training data. Run scripts/generate_training_data.py first.")
    if not skill_map_path.exists() or not role_map_path.exists():
        raise FileNotFoundError("Missing mappings. Run scripts/generate_training_data.py first.")
    with open(skill_map_path, "r", encoding="utf-8") as f:
        skill_mapping = json.load(f)
    with open(role_map_path, "r", encoding="utf-8") as f:
        role_mapping = json.load(f)
    skill_names = skill_mapping["skills"]
    role_names = role_mapping["roles"]
    skill_to_index = {name: i for i, name in enumerate(skill_names)}
    role_to_index = {name: i for i, name in enumerate(role_names)}
    df = pd.read_csv(examples_path)
    X = np.zeros((len(df), len(skill_names)), dtype=np.float32)
    for i, row in df.iterrows():
        skills = json.loads(row["skills_json"])
        X[i] = encode_profile(skills, skill_to_index)
    y = df["role_name"].map(role_to_index).values.astype(np.int64)
    return X, y, skill_names, role_names, df


def save_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
