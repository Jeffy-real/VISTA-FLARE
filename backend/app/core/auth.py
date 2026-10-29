"""Cookie session authentication and CSRF protection."""
from datetime import datetime, timedelta
import hashlib, hmac, secrets
from fastapi import Depends, HTTPException, Request
from sqlalchemy.orm import Session
from backend.app.core.config import get_settings
from backend.app.core.database import get_db
from backend.app.models.database_models import User, UserSession

def hash_password(password: str) -> str:
    salt = secrets.token_bytes(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 310_000)
    return f"pbkdf2_sha256$310000${salt.hex()}${digest.hex()}"

def verify_password(password: str, encoded: str) -> bool:
    try:
        _, rounds, salt, digest = encoded.split("$")
        candidate = hashlib.pbkdf2_hmac("sha256", password.encode(), bytes.fromhex(salt), int(rounds))
        return hmac.compare_digest(candidate.hex(), digest)
    except (ValueError, TypeError):
        return False

def _token_hash(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()

def create_session(db: Session, user: User) -> tuple[str, str]:
    settings = get_settings()
    raw = secrets.token_urlsafe(48)
    csrf = secrets.token_urlsafe(32)
    db.add(UserSession(token_hash=_token_hash(raw), user_id=user.id, csrf_token=csrf,
                       expires_at=datetime.utcnow() + timedelta(seconds=settings.session_max_age)))
    db.commit()
    return raw, csrf

def current_session(request: Request, db: Session = Depends(get_db)) -> UserSession:
    token = request.cookies.get(get_settings().session_cookie_name)
    if not token:
        raise HTTPException(401, "Authentication required")
    session = db.query(UserSession).filter(UserSession.token_hash == _token_hash(token)).first()
    if not session or session.expires_at <= datetime.utcnow():
        raise HTTPException(401, "Authentication required")
    return session

def current_user(session: UserSession = Depends(current_session), db: Session = Depends(get_db)) -> User:
    user = db.query(User).filter(User.id == session.user_id).first()
    if not user:
        raise HTTPException(401, "Authentication required")
    return user


def optional_user(request: Request, db: Session = Depends(get_db)) -> User | None:
    """Resolve a session when present without making a public endpoint private."""
    token = request.cookies.get(get_settings().session_cookie_name)
    if not token:
        return None
    session = db.query(UserSession).filter(UserSession.token_hash == _token_hash(token)).first()
    if not session or session.expires_at < datetime.utcnow():
        return None
    return db.query(User).filter(User.id == session.user_id).first()

def require_csrf(request: Request, session: UserSession = Depends(current_session)) -> UserSession:
    supplied = request.headers.get("X-CSRF-Token")
    if not supplied or not hmac.compare_digest(supplied, session.csrf_token):
        raise HTTPException(403, "CSRF validation failed")
    return session
