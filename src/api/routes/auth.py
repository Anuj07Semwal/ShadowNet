import base64
import hashlib
import hmac
import secrets
import time
from dataclasses import dataclass

from fastapi import APIRouter, Cookie, Header, HTTPException, Response
from pydantic import BaseModel, Field

from src.config import settings


router = APIRouter(prefix="/api/auth", tags=["Authentication"])


@dataclass
class User:
    username: str
    role: str
    password_hash: str
    password_changed_at: float


@dataclass
class Session:
    username: str
    csrf_token: str
    created_at: float


class LoginRequest(BaseModel):
    username: str = Field(min_length=3, max_length=100)
    password: str = Field(min_length=8, max_length=200)


class PasswordRequest(BaseModel):
    password: str = Field(min_length=15, max_length=200)


class ResetPasswordRequest(PasswordRequest):
    code: str = Field(min_length=20, max_length=300)


class ChangePasswordRequest(PasswordRequest):
    current_password: str = Field(min_length=8, max_length=200)


class SessionResponse(BaseModel):
    username: str
    role: str
    csrf_token: str
    password_age_days: int
    password_review_days: int
    password_review_due: bool


_users: dict[str, User] = {}
_sessions: dict[str, Session] = {}


def _password_hash(password: str, salt: bytes | None = None) -> str:
    salt = salt or secrets.token_bytes(16)
    derived = hashlib.scrypt(password.encode(), salt=salt, n=16384, r=8, p=1)
    return "scrypt$" + base64.urlsafe_b64encode(salt).decode() + "$" + base64.urlsafe_b64encode(derived).decode()


def _password_matches(password: str, encoded: str) -> bool:
    try:
        _, salt_value, expected_value = encoded.split("$", 2)
        salt = base64.urlsafe_b64decode(salt_value.encode())
        actual = hashlib.scrypt(password.encode(), salt=salt, n=16384, r=8, p=1)
        expected = base64.urlsafe_b64decode(expected_value.encode())
        return hmac.compare_digest(actual, expected)
    except (ValueError, TypeError):
        return False


def _get_user(username: str) -> User | None:
    if not _users:
        if not settings.auth_username or not settings.auth_password:
            return None
        _users[settings.auth_username] = User(
            username=settings.auth_username,
            role=settings.auth_role,
            password_hash=_password_hash(settings.auth_password),
            password_changed_at=time.time(),
        )
    return _users.get(username)


def _session_response(user: User, csrf_token: str) -> SessionResponse:
    age_days = max(0, int((time.time() - user.password_changed_at) // 86400))
    review_days = settings.auth_password_review_days
    return SessionResponse(
        username=user.username,
        role=user.role,
        csrf_token=csrf_token,
        password_age_days=age_days,
        password_review_days=review_days,
        password_review_due=age_days >= review_days,
    )


def _require_session(session_id: str | None) -> tuple[str, Session, User]:
    session = _sessions.get(session_id or "")
    if not session or time.time() - session.created_at > settings.auth_session_ttl_seconds:
        if session_id:
            _sessions.pop(session_id, None)
        raise HTTPException(status_code=401, detail="Authentication is required.")
    user = _get_user(session.username)
    if not user:
        _sessions.pop(session_id or "", None)
        raise HTTPException(status_code=401, detail="Authentication is required.")
    return session_id or "", session, user


def _require_csrf(session: Session, csrf_token: str | None) -> None:
    if not csrf_token or not hmac.compare_digest(csrf_token, session.csrf_token):
        raise HTTPException(status_code=403, detail="Invalid CSRF token.")


def _set_session_cookie(response: Response, session_id: str) -> None:
    response.set_cookie(
        "shadownet_session",
        session_id,
        httponly=True,
        secure=settings.auth_cookie_secure,
        samesite="lax",
        max_age=settings.auth_session_ttl_seconds,
        path="/",
    )


@router.post("/login", response_model=SessionResponse)
def login(payload: LoginRequest, response: Response):
    user = _get_user(payload.username)
    if not user or not _password_matches(payload.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid username or password.")

    session_id = secrets.token_urlsafe(32)
    csrf_token = secrets.token_urlsafe(32)
    _sessions[session_id] = Session(user.username, csrf_token, time.time())
    _set_session_cookie(response, session_id)
    return _session_response(user, csrf_token)


@router.get("/session", response_model=SessionResponse)
def current_session(shadownet_session: str | None = Cookie(default=None)):
    _, session, user = _require_session(shadownet_session)
    return _session_response(user, session.csrf_token)


@router.post("/logout")
def logout(
    response: Response,
    shadownet_session: str | None = Cookie(default=None),
    csrf_token: str | None = Header(default=None, alias="X-CSRF-Token"),
):
    session_id, session, _ = _require_session(shadownet_session)
    _require_csrf(session, csrf_token)
    _sessions.pop(session_id, None)
    response.delete_cookie("shadownet_session", path="/")
    return {"status": "logged_out"}


@router.post("/change-password")
def change_password(
    payload: ChangePasswordRequest,
    shadownet_session: str | None = Cookie(default=None),
    csrf_token: str | None = Header(default=None, alias="X-CSRF-Token"),
):
    _, session, user = _require_session(shadownet_session)
    _require_csrf(session, csrf_token)
    if not _password_matches(payload.current_password, user.password_hash):
        raise HTTPException(status_code=401, detail="Current password is incorrect.")
    user.password_hash = _password_hash(payload.password)
    user.password_changed_at = time.time()
    return {"status": "password_changed"}


@router.post("/reset-password")
def reset_password(payload: ResetPasswordRequest):
    if not settings.auth_reset_code or not hmac.compare_digest(payload.code, settings.auth_reset_code):
        raise HTTPException(status_code=401, detail="Invalid password reset code.")
    if not _users:
        _get_user(settings.auth_username or "")
    user = _users.get(settings.auth_username or "")
    if not user:
        raise HTTPException(status_code=503, detail="Password reset is not configured.")
    user.password_hash = _password_hash(payload.password)
    user.password_changed_at = time.time()
    for session_id, session in list(_sessions.items()):
        if session.username == user.username:
            _sessions.pop(session_id, None)
    return {"status": "password_reset"}