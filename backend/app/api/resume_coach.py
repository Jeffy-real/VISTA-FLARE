"""Authenticated ephemeral resume matching and deterministic interview practice."""
import json
from typing import Optional
from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy.orm import Session
from backend.app.core.auth import current_user, require_csrf
from backend.app.core.database import get_db
from backend.app.core.database import Base, engine
from backend.app.models.database_models import Job, PracticeProgress, Role, User, UserSession
from backend.app.services.resume_coach import coach_for_role, compare_job, extract_upload, match_skills

# Test clients may call routes without entering FastAPI's lifespan; this is
# idempotent and also supports upgrading an existing SQLite database.
Base.metadata.create_all(bind=engine)

router = APIRouter(prefix="/api", tags=["resume-coach"])

@router.post("/resume/analyze")
async def analyze_resume(file: Optional[UploadFile] = File(None), resume_text: Optional[str] = Form(None), job_id: Optional[int] = Form(None), user: User = Depends(current_user), db: Session = Depends(get_db)):
    if file is None and not resume_text: raise HTTPException(422, "Provide a PDF/DOCX file or resume_text")
    text = resume_text if resume_text is not None else await extract_upload(file)
    if len(text) > 500_000: raise HTTPException(413, "Resume text exceeds the 500 KB limit")
    result = {"skills": match_skills(text, db), "ephemeral": True}
    if job_id is not None:
        job = db.query(Job).filter(Job.id == job_id).first()
        if not job: raise HTTPException(404, "Job not found")
        result["job_comparison"] = compare_job(text, job, db)
    return result

@router.get("/interview/roles/{role_id}")
def interview_coach(role_id: int, user: User = Depends(current_user), db: Session = Depends(get_db)):
    role = db.query(Role).filter(Role.id == role_id).first()
    if not role: raise HTTPException(404, "Role not found")
    result = coach_for_role(role, db); progress = db.query(PracticeProgress).filter_by(user_id=user.id, role_id=role.id).first()
    result["progress"] = {"notes": progress.notes, "completed_questions": json.loads(progress.completed_questions)} if progress else {"notes": "", "completed_questions": []}
    return result

@router.put("/interview/roles/{role_id}/progress")
def save_progress(role_id: int, notes: str = Form(""), completed_questions: str = Form("[]"), user: User = Depends(current_user), _: UserSession = Depends(require_csrf), db: Session = Depends(get_db)):
    if not db.query(Role).filter(Role.id == role_id).first(): raise HTTPException(404, "Role not found")
    try:
        completed = json.loads(completed_questions)
        if not isinstance(completed, list) or len(notes) > 100_000: raise ValueError
    except (ValueError, TypeError, json.JSONDecodeError): raise HTTPException(422, "completed_questions must be a JSON list")
    item = db.query(PracticeProgress).filter_by(user_id=user.id, role_id=role_id).first()
    if not item: item = PracticeProgress(user_id=user.id, role_id=role_id); db.add(item)
    item.notes, item.completed_questions = notes, json.dumps(completed, separators=(",", ":")); db.commit()
    return {"ok": True, "role_id": role_id, "notes": notes, "completed_questions": completed}
