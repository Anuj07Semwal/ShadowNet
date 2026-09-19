import csv
from pathlib import Path

from fastapi import APIRouter, Depends, Query

from src.graph.investigation_service import GraphInvestigationService
from src.api.dependencies import get_graph_service


router = APIRouter(
    prefix="/api/transactions",
    tags=["Transactions"]
)


def _serialize_value(value):
    if value is None:
        return None
    if hasattr(value, "isoformat"):
        return value.isoformat()
    if isinstance(value, dict):
        return {key: _serialize_value(val) for key, val in value.items()}
    if isinstance(value, list):
        return [_serialize_value(item) for item in value]
    return value


@router.get("")
def list_transactions(
    limit: int = Query(100, ge=1, le=1000),
    graph: GraphInvestigationService = Depends(get_graph_service)
):
    path = Path(__file__).resolve().parents[3] / "data" / "processed" / "transaction_anomalies.csv"
    if not path.exists():
        return {"count": 0, "transactions": []}
    with path.open(newline="", encoding="utf-8") as stream:
        rows = list(csv.DictReader(stream))
    rows.sort(key=lambda row: (row.get("is_anomaly", "").lower() == "true", float(row.get("anomaly_score") or 0)), reverse=True)
    rows = rows[:limit]
    person_ids = [row.get("person_id", "") for row in rows] + [row.get("target_id", "") for row in rows]
    name_rows = graph.client.execute_read(
        """
        MATCH (p:Person)
        WHERE p.person_id IN $person_ids
        RETURN p.person_id AS person_id, coalesce(p.name, p.person_id) AS name
        """,
        {"person_ids": [item for item in person_ids if item]},
    )
    names = {row["person_id"]: row["name"] for row in name_rows}
    serialized = []
    for row in rows:
        score = float(row.get("anomaly_score") or 0)
        source_person = row.get("person_id") or row.get("source_id")
        target_person = row.get("target_id")
        serialized.append({
            "transaction_id": row.get("transaction_id") or row.get("relationship_id") or "UNKNOWN_TRANSACTION",
            "person_id": source_person,
            "person_name": names.get(source_person, source_person),
            "related_person_id": target_person,
            "related_person_name": names.get(target_person, target_person),
            "amount": float(row.get("amount") or 0),
            "timestamp": _serialize_value(row.get("timestamp")),
            "channel": row.get("channel"),
            "anomaly_type": row.get("anomaly_type"),
            "reason": row.get("reason"),
            "is_anomaly": row.get("is_anomaly", "").lower() == "true",
            "anomaly_score": score,
            "severity": "high" if score >= 0.9 else "medium" if score >= 0.7 else "low",
        })

    return {
        "count": len(serialized),
        "transactions": serialized,
    }