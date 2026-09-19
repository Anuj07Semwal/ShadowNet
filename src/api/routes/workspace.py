from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

from fastapi import APIRouter, Cookie, Depends, HTTPException

from src.api.routes.auth import _require_session


router = APIRouter(prefix="/api/workspace", tags=["Workspace"])

_uploads: dict[str, list[dict[str, Any]]] = {}
_investigations: dict[str, list[dict[str, Any]]] = {}


def current_user(shadownet_session: str | None = Cookie(default=None)) -> str:
    _, _, user = _require_session(shadownet_session)
    return user.username


def record_upload(username: str, filename: str, size_bytes: int) -> dict[str, Any]:
    upload = {
        "id": str(uuid4()),
        "created_at": datetime.now(timezone.utc).isoformat(),
        "filename": filename,
        "size_bytes": size_bytes,
        "status": "received",
    }
    _uploads.setdefault(username, []).insert(0, upload)
    return upload


@router.get("/dashboard")
def dashboard(username: str = Depends(current_user)):
    investigations = _investigations.get(username, [])
    uploads = _uploads.get(username, [])
    return {
        "username": username,
        "investigation_count": len(investigations),
        "upload_count": len(uploads),
        "evidence_match_count": sum(item.get("matching_records", 0) for item in investigations),
        "recent_investigations": investigations[:8],
        "recent_uploads": uploads[:8],
    }


@router.delete("/investigations/{investigation_id}")
def delete_investigation(investigation_id: str, username: str = Depends(current_user)):
    investigations = _investigations.get(username, [])
    before = len(investigations)
    _investigations[username] = [item for item in investigations if item["id"] != investigation_id]
    if len(_investigations[username]) == before:
        raise HTTPException(status_code=404, detail="Investigation was not found.")
    return {"status": "deleted", "id": investigation_id}
