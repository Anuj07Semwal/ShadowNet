import csv
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from fastapi import APIRouter, Cookie, Header, HTTPException, Query
from pydantic import BaseModel

from src.api.routes.auth import _require_csrf, _require_session
from src.config import settings
from src.graph.neo4j_client import Neo4jClient


router = APIRouter(prefix="/api/review-queue", tags=["Review Queue"])


class ReviewDecision(BaseModel):
    status: str


def _current_session(
    shadownet_session: str | None,
) -> tuple[str, Any, Any]:
    return _require_session(shadownet_session)


def _source_path() -> Path:
    return Path(__file__).resolve().parents[3] / "data" / "processed" / "transaction_anomalies.csv"


def _priority(score: float) -> str:
    if score >= 0.9:
        return "high"
    if score >= 0.7:
        return "medium"
    return "low"


def _load_anomalies() -> list[dict[str, Any]]:
    path = _source_path()
    if not path.exists():
        return []
    with path.open(newline="", encoding="utf-8") as stream:
        rows = csv.DictReader(stream)
        return [row for row in rows if row.get("is_anomaly", "").lower() == "true"]


def _stored_states(review_ids: list[str]) -> dict[str, dict[str, Any]]:
    if not review_ids:
        return {}
    client = Neo4jClient()
    try:
        records = client.execute_read(
            """
            MATCH (item:ReviewItem)
            WHERE item.review_id IN $review_ids
            RETURN item.review_id AS review_id, item.status AS status,
                   item.updated_at AS updated_at, item.updated_by AS updated_by
            """,
            {"review_ids": review_ids},
        )
        return {record["review_id"]: record for record in records}
    finally:
        client.close()


def _person_names(person_ids: list[str]) -> dict[str, str]:
    if not person_ids:
        return {}
    client = Neo4jClient()
    try:
        records = client.execute_read(
            """
            MATCH (person:Person)
            WHERE person.person_id IN $person_ids
            RETURN person.person_id AS person_id,
                   coalesce(person.name, person.person_id) AS name
            """,
            {"person_ids": person_ids},
        )
        return {record["person_id"]: record["name"] for record in records}
    finally:
        client.close()


def _serialize(row: dict[str, Any], state: dict[str, Any], names: dict[str, str], anomaly_count: int = 1) -> dict[str, Any]:
    score = float(row.get("anomaly_score") or 0)
    person_id = row.get("person_id") or row.get("source_id") or ""
    target_id = row.get("target_id") or ""
    return {
        "id": row.get("transaction_id") or row.get("relationship_id"),
        "status": state.get("status", "pending"),
        "priority": _priority(score),
        "created_at": row.get("timestamp"),
        "updated_at": state.get("updated_at"),
        "type": "transaction_anomaly",
        "title": "Unusual transaction activity",
        "transaction_id": row.get("transaction_id") or row.get("relationship_id"),
        "person_id": person_id,
        "person_name": names.get(person_id, person_id),
        "related_person_id": target_id,
        "related_person_name": names.get(target_id, target_id),
        "amount": float(row.get("amount") or 0),
        "channel": row.get("channel"),
        "anomaly_type": row.get("anomaly_type"),
        "anomaly_score": score,
        "anomaly_count": anomaly_count,
        "reason": row.get("reason"),
        "source": "transaction_anomalies.csv",
    }


@router.get("")
def list_review_queue(
    status: str = Query("pending", pattern="^(pending|approved|rejected|all)$"),
    limit: int = Query(50, ge=1, le=200),
    shadownet_session: str | None = Cookie(default=None),
):
    _current_session(shadownet_session)
    rows = _load_anomalies()
    states = _stored_states([row.get("transaction_id") or row.get("relationship_id") or "" for row in rows])
    if status != "all":
        rows = [row for row in rows if states.get(row.get("transaction_id") or row.get("relationship_id") or "", {}).get("status", "pending") == status]
    counts: dict[str, int] = {}
    for row in rows:
        person_id = row.get("person_id") or row.get("source_id") or ""
        counts[person_id] = counts.get(person_id, 0) + 1
    rows = sorted(rows, key=lambda row: (
        float(row.get("anomaly_score") or 0),
        counts.get(row.get("person_id") or row.get("source_id") or "", 0),
        row.get("timestamp") or "",
    ), reverse=True)[:limit]
    ids = [row.get("person_id", "") for row in rows] + [row.get("target_id", "") for row in rows]
    names = _person_names([item for item in ids if item])
    return {"count": len(rows), "items": [_serialize(row, states.get(row.get("transaction_id") or row.get("relationship_id") or "", {}), names, counts.get(row.get("person_id") or row.get("source_id") or "", 1)) for row in rows]}


@router.patch("/{review_id}")
def decide_review_item(
    review_id: str,
    decision: ReviewDecision,
    shadownet_session: str | None = Cookie(default=None),
    csrf_token: str | None = Header(default=None, alias="X-CSRF-Token"),
):
    _, session, user = _current_session(shadownet_session)
    _require_csrf(session, csrf_token)
    if decision.status not in {"approved", "rejected", "pending"}:
        raise HTTPException(status_code=422, detail="Status must be approved, rejected or pending.")
    if not any((row.get("transaction_id") or row.get("relationship_id")) == review_id for row in _load_anomalies()):
        raise HTTPException(status_code=404, detail="Review item was not found.")

    now = datetime.now(timezone.utc).isoformat()
    client = Neo4jClient()
    try:
        client.execute_write(
            """
            MERGE (item:ReviewItem {review_id: $review_id})
            SET item.status = $status, item.updated_at = $updated_at,
                item.updated_by = $updated_by
            """,
            {"review_id": review_id, "status": decision.status, "updated_at": now, "updated_by": user.username},
        )
    finally:
        client.close()
    return {"id": review_id, "status": decision.status, "updated_at": now}
