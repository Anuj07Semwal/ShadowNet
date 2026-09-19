from fastapi import APIRouter, Depends, Query

from src.graph.investigation_service import GraphInvestigationService
from src.api.dependencies import get_graph_service


router = APIRouter(
    prefix="/api/anomalies",
    tags=["Anomalies"]
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
def list_anomalies(
    limit: int = Query(100, ge=1, le=1000),
    graph: GraphInvestigationService = Depends(get_graph_service)
):
    query = """
    MATCH (t:Transaction)

    WHERE t.is_anomaly = true

    OPTIONAL MATCH (p:Person)-[]-(t)

    RETURN
        t.id AS transaction_id,
        collect(DISTINCT p.person_id) AS person_ids,
        collect(DISTINCT p.name) AS person_names,
        t.amount AS amount,
        t.timestamp AS timestamp,
        t.anomaly_score AS anomaly_score,
        t.is_anomaly AS is_anomaly

    ORDER BY t.anomaly_score DESC
    LIMIT $limit
    """

    records = graph.client.execute_read(
        query,
        {"limit": limit}
    )

    serialized = []
    for record in records:
        item = dict(record)
        item["transaction_id"] = item.get("transaction_id") or "UNKNOWN_TRANSACTION"
        item["timestamp"] = _serialize_value(item.get("timestamp"))
        serialized.append(item)

    return {
        "count": len(serialized),
        "anomalies": serialized,
    }