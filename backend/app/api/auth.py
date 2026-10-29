from datetime import datetime
import json
from fastapi import APIRouter, Depends, HTTPException, Request, Response
from sqlalchemy.orm import Session
from backend.app.core.auth import create_session, current_session, current_user, hash_password, require_csrf, verify_password
from backend.app.core.config import get_settings
from backend.app.core.database import get_db
from backend.app.models.database_models import Application, Job, Roadmap, SavedJob, User, UserProfile, UserSession
from backend.app.schemas.auth import ApplicationRequest, ApplicationUpdate, JourneyImportRequest, LoginRequest, ProfileUpdate, RegisterRequest, RoadmapRequest, SavedJobRequest

router = APIRouter(prefix="/api", tags=["auth"])

def _validate_email(email: str) -> str:
    email = email.strip().lower()
    if "@" not in email or email.startswith("@") or email.endswith("@"):
        raise HTTPException(422, "A valid email is required")
    return email

def _set_session(response: Response, raw: str, csrf: str) -> None:
    s = get_settings()
    response.set_cookie(s.session_cookie_name, raw, max_age=s.session_max_age, httponly=True, secure=s.secure_cookies, samesite="lax", path="/")
    response.set_cookie(s.csrf_cookie_name, csrf, max_age=s.session_max_age, httponly=False, secure=s.secure_cookies, samesite="lax", path="/")

@router.post("/auth/register", status_code=201)
def register(payload: RegisterRequest, response: Response, db: Session = Depends(get_db)):
    email = _validate_email(payload.email)
    if db.query(User).filter(User.email == email).first(): raise HTTPException(409, "Email already registered")
    user = User(email=email, password_hash=hash_password(payload.password), display_name=payload.display_name.strip())
    db.add(user); db.commit(); db.refresh(user)
    raw, csrf = create_session(db, user); _set_session(response, raw, csrf)
    return {"id": user.id, "email": user.email, "display_name": user.display_name}

@router.post("/auth/login")
def login(payload: LoginRequest, response: Response, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == _validate_email(payload.email)).first()
    if not user or not verify_password(payload.password, user.password_hash): raise HTTPException(401, "Invalid credentials")
    raw, csrf = create_session(db, user); _set_session(response, raw, csrf)
    return {"id": user.id, "email": user.email, "display_name": user.display_name}

@router.post("/auth/logout")
def logout(response: Response, session: UserSession = Depends(require_csrf), db: Session = Depends(get_db)):
    db.delete(session); db.commit()
    s = get_settings(); response.delete_cookie(s.session_cookie_name); response.delete_cookie(s.csrf_cookie_name)
    return {"ok": True}

@router.get("/auth/me")
def me(user: User = Depends(current_user)):
    return {"id": user.id, "email": user.email, "display_name": user.display_name}

@router.get("/profile")
def profile(user: User = Depends(current_user)):
    return {"id": user.id, "email": user.email, "display_name": user.display_name}

@router.post("/profile/import", status_code=201)
def import_profile_journey(payload: JourneyImportRequest, user: User = Depends(current_user), _: UserSession = Depends(require_csrf), db: Session = Depends(get_db)):
    """Import guest journey data only after an explicit authenticated user action."""
    allowed = {key: value for key, value in payload.data.items() if key in {"skills", "selected-role", "recommendations", "analysis-history"}}
    if sum(len(key) + len(value or "") for key, value in allowed.items()) > 500_000:
        raise HTTPException(413, "Guest journey data is too large")
    item = db.query(UserProfile).filter_by(user_id=user.id).first()
    if not item:
        item = UserProfile(user_id=user.id, profile_json="{}"); db.add(item)
    existing = json.loads(item.profile_json or "{}")
    existing.update(allowed)
    item.profile_json = json.dumps(existing, separators=(",", ":"))
    db.commit()
    return {"ok": True, "imported_keys": list(allowed), "user_id": user.id}

@router.patch("/profile")
def update_profile(payload: ProfileUpdate, user: User = Depends(current_user), _: UserSession = Depends(require_csrf), db: Session = Depends(get_db)):
    user.display_name = payload.display_name.strip(); db.commit(); return profile(user)

@router.get("/roadmap")
def list_roadmaps(user: User = Depends(current_user), db: Session = Depends(get_db)):
    return [{"id": x.id, "target_role": x.target_role, "content": x.content} for x in db.query(Roadmap).filter(Roadmap.user_id == user.id).all()]

@router.get("/roadmap/{roadmap_id}")
def get_roadmap(roadmap_id: int, user: User = Depends(current_user), db: Session = Depends(get_db)):
    item = db.query(Roadmap).filter(Roadmap.id == roadmap_id, Roadmap.user_id == user.id).first()
    if not item: raise HTTPException(404, "Roadmap not found")
    return {"id": item.id, "target_role": item.target_role, "content": item.content, "updated_at": item.updated_at}

@router.post("/roadmap", status_code=201)
def save_roadmap(payload: RoadmapRequest, user: User = Depends(current_user), _: UserSession = Depends(require_csrf), db: Session = Depends(get_db)):
    item = Roadmap(user_id=user.id, target_role=payload.target_role, content=payload.content); db.add(item); db.commit(); db.refresh(item)
    return {"id": item.id, "target_role": item.target_role, "content": item.content}

@router.patch("/roadmap/{roadmap_id}")
def update_roadmap(roadmap_id: int, payload: RoadmapRequest, user: User = Depends(current_user), _: UserSession = Depends(require_csrf), db: Session = Depends(get_db)):
    item = db.query(Roadmap).filter(Roadmap.id == roadmap_id, Roadmap.user_id == user.id).first()
    if not item: raise HTTPException(404, "Roadmap not found")
    item.target_role = payload.target_role; item.content = payload.content; db.commit(); db.refresh(item)
    return {"id": item.id, "target_role": item.target_role, "content": item.content, "updated_at": item.updated_at}

@router.delete("/roadmap/{roadmap_id}")
def delete_roadmap(roadmap_id: int, user: User = Depends(current_user), _: UserSession = Depends(require_csrf), db: Session = Depends(get_db)):
    item = db.query(Roadmap).filter(Roadmap.id == roadmap_id, Roadmap.user_id == user.id).first()
    if not item: raise HTTPException(404, "Roadmap not found")
    db.delete(item); db.commit(); return {"ok": True}

@router.get("/saved-jobs")
def saved_jobs(user: User = Depends(current_user), db: Session = Depends(get_db)):
    return [{"id": x.id, "job_id": x.job_id, "created_at": x.created_at, "job": {"title": x.job.job_title, "company": x.job.company_name, "source_url": x.job.source_url, "source": x.job.source, "active": x.job.active, "stale": x.job.stale} if x.job else None} for x in db.query(SavedJob).filter(SavedJob.user_id == user.id).all()]

@router.post("/saved-jobs", status_code=201)
def save_job(payload: SavedJobRequest, user: User = Depends(current_user), _: UserSession = Depends(require_csrf), db: Session = Depends(get_db)):
    if not db.query(Job).filter(Job.id == payload.job_id).first(): raise HTTPException(404, "Job not found")
    if db.query(SavedJob).filter_by(user_id=user.id, job_id=payload.job_id).first(): raise HTTPException(409, "Job already saved")
    item = SavedJob(user_id=user.id, job_id=payload.job_id); db.add(item); db.commit(); db.refresh(item); return {"id": item.id, "job_id": item.job_id}

@router.delete("/saved-jobs/{job_id}")
def delete_saved_job(job_id: int, user: User = Depends(current_user), _: UserSession = Depends(require_csrf), db: Session = Depends(get_db)):
    item = db.query(SavedJob).filter_by(user_id=user.id, job_id=job_id).first()
    if not item: raise HTTPException(404, "Saved job not found")
    db.delete(item); db.commit(); return {"ok": True}

@router.get("/applications")
def applications(user: User = Depends(current_user), db: Session = Depends(get_db)):
    return [{"id": x.id, "job_id": x.job_id, "status": x.status, "notes": x.notes, "application_date": x.applied_at, "job": {"title": x.job.job_title, "company": x.job.company_name} if x.job else None} for x in db.query(Application).filter(Application.user_id == user.id).all()]

@router.post("/applications", status_code=201)
def create_application(payload: ApplicationRequest, user: User = Depends(current_user), _: UserSession = Depends(require_csrf), db: Session = Depends(get_db)):
    if not db.query(Job).filter(Job.id == payload.job_id).first(): raise HTTPException(404, "Job not found")
    item = Application(user_id=user.id, job_id=payload.job_id, status=payload.status, notes=payload.notes, applied_at=datetime.utcnow()); db.add(item); db.commit(); db.refresh(item)
    return {"id": item.id, "job_id": item.job_id, "status": item.status, "notes": item.notes}

@router.patch("/applications/{application_id}")
def update_application(application_id: int, payload: ApplicationUpdate, user: User = Depends(current_user), _: UserSession = Depends(require_csrf), db: Session = Depends(get_db)):
    item = db.query(Application).filter(Application.id == application_id, Application.user_id == user.id).first()
    if not item: raise HTTPException(404, "Application not found")
    item.status = payload.status; item.notes = payload.notes; db.commit(); db.refresh(item)
    return {"id": item.id, "job_id": item.job_id, "status": item.status, "notes": item.notes}

@router.delete("/applications/{application_id}")
def delete_application(application_id: int, user: User = Depends(current_user), _: UserSession = Depends(require_csrf), db: Session = Depends(get_db)):
    item = db.query(Application).filter(Application.id == application_id, Application.user_id == user.id).first()
    if not item: raise HTTPException(404, "Application not found")
    db.delete(item); db.commit(); return {"ok": True}
