"""Deterministic, evidence-preserving resume matching and interview coaching."""
from __future__ import annotations
import importlib.util, io, re, zipfile
from typing import Any
from fastapi import HTTPException, UploadFile
from sqlalchemy.orm import Session
from backend.app.models.database_models import Job, Role, RoleSkill, Skill, SkillAlias
from backend.app.services.predictor import get_prediction_service

MAX_RESUME_BYTES = 5 * 1024 * 1024

def _skill_catalog(db: Session):
    aliases = {a.alias.strip().lower(): a.normalized_skill for a in db.query(SkillAlias).all()}
    names = {s.name for s in db.query(Skill).all()}
    aliases.update(get_prediction_service().aliases)
    return aliases, names

def match_skills(text: str, db: Session) -> list[str]:
    """Find only skills explicitly present in the seeded vocabulary or aliases."""
    aliases, names = _skill_catalog(db); lowered = text.lower(); found = set()
    for candidate in sorted(names | set(aliases.values()), key=len, reverse=True):
        if re.search(r"(?<![\w+#.])" + re.escape(candidate.lower()) + r"(?![\w+#.])", lowered): found.add(candidate)
    for alias, canonical in aliases.items():
        if re.search(r"(?<![\w+#.])" + re.escape(alias) + r"(?![\w+#.])", lowered): found.add(canonical)
    return sorted(found, key=str.casefold)

def compare_job(text: str, job: Job, db: Session) -> dict[str, Any]:
    predictor = get_prediction_service(); found = {predictor._canonicalize_skill(x).casefold() for x in match_skills(text, db)}
    required = list(dict.fromkeys(x.strip() for x in (job.required_skills or "").split(",") if x.strip()))
    matched = [x for x in required if predictor._canonicalize_skill(x).casefold() in found]
    missing = [x for x in required if x not in matched]
    return {"job_id": job.id, "matched_skills": matched, "missing_skills": missing,
            "checklist": [{"skill": x, "status": "matched" if x in matched else "missing"} for x in required]}

async def extract_upload(upload: UploadFile) -> str:
    name = (upload.filename or "").lower(); suffix = "." + name.rsplit(".", 1)[-1] if "." in name else ""
    if suffix not in {".pdf", ".docx"}: raise HTTPException(415, "Only PDF and DOCX resumes are supported")
    data = await upload.read(MAX_RESUME_BYTES + 1)
    if len(data) > MAX_RESUME_BYTES: raise HTTPException(413, "Resume exceeds the 5 MB limit")
    if suffix == ".pdf" and not data.startswith(b"%PDF"): raise HTTPException(415, "Uploaded file is not a valid PDF")
    if suffix == ".docx" and not data.startswith(b"PK"): raise HTTPException(415, "Uploaded file is not a valid DOCX")
    package = "pypdf" if suffix == ".pdf" else "docx"
    if importlib.util.find_spec(package) is None:
        raise HTTPException(415, f"{suffix[1:].upper()} extraction is unavailable; install {package} to enable it")
    try:
        if suffix == ".pdf":
            from pypdf import PdfReader
            return "\n".join(page.extract_text() or "" for page in PdfReader(io.BytesIO(data)).pages)
        from docx import Document
        with zipfile.ZipFile(io.BytesIO(data)) as archive:
            if "word/document.xml" not in archive.namelist(): raise ValueError("invalid document")
            if sum(info.file_size for info in archive.infolist()) > 20 * 1024 * 1024:
                raise ValueError("expanded document is too large")
            if any(info.filename.startswith(("/", "\\")) or ".." in info.filename.split("/") for info in archive.infolist()):
                raise ValueError("unsafe archive path")
        return "\n".join(p.text for p in Document(io.BytesIO(data)).paragraphs)
    except Exception as exc:
        raise HTTPException(422, "Resume text could not be safely extracted") from exc

def coach_for_role(role: Role, db: Session) -> dict[str, Any]:
    skills = db.query(RoleSkill).filter(RoleSkill.role_id == role.id).order_by(RoleSkill.id).all()
    names = [s.skill_name for s in skills]
    questions = [f"Describe a project where you used {s}. What was your contribution and outcome?" for s in names[:5]]
    questions += [f"How would you approach a production problem in {role.name}?", f"How do you explain your {role.name} work to a non-technical stakeholder?"]
    return {"role": role.name, "role_id": role.id, "skills": names, "questions": questions,
            "project_checklist": [f"Build and document a small {role.name} project demonstrating {s}." for s in names[:3]]}
