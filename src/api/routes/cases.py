import csv
from pathlib import Path
from fastapi import APIRouter

from src.api.services.neo4j_service import Neo4jService

router = APIRouter(prefix="/api/cases", tags=["Cases"])
neo4j = Neo4jService()


def _firs_path() -> Path:
    return Path(__file__).resolve().parents[3] / "data" / "processed" / "firs.csv"


def _fallback_cases(limit: int = 10) -> list[dict]:
    path = _firs_path()
    if not path.exists():
        return []
    cases = []
    with path.open(newline="", encoding="utf-8", errors="ignore") as f:
        reader = csv.DictReader(f)
        for i, row in enumerate(reader):
            if i >= limit:
                break
            conf = float(row.get("confidence") or 0.85)
            risk = round(conf * 100, 1)
            priority = "High" if conf >= 0.9 else "Medium" if conf >= 0.85 else "Low"
            cases.append({
                "id": row.get("fir_id"),
                "name": f"{row.get('fir_id')} - {row.get('crime_type', 'Investigation')}",
                "title": row.get("crime_type") or "Active FIR Case",
                "priority": priority,
                "risk_score": risk,
                "evidence_count": 4,
                "status": "Active" if priority == "High" else "Open",
                "owner": row.get("station_id") or "Investigation Bureau",
            })
    return cases


def _fallback_evidence(case_id: str) -> list[dict]:
    path = _firs_path()
    if not path.exists():
        return []
    with path.open(newline="", encoding="utf-8", errors="ignore") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row.get("fir_id") == case_id:
                return [
                    {
                        "type": "INCIDENT_REPORT",
                        "entity_id": case_id,
                        "entity_name": row.get("station_id") or "Police Station",
                        "title": row.get("crime_type") or "Crime Report",
                        "summary": row.get("acts_list") or "Official FIR filing.",
                        "confidence": float(row.get("confidence") or 0.85),
                    },
                    {
                        "type": "STATUTE_SECTION",
                        "entity_id": f"{case_id}-sec",
                        "entity_name": row.get("sections_list") or "IPC Applicable",
                        "title": "Legal Charge / Statute",
                        "summary": f"Booked under sections: {row.get('sections_list')}",
                        "confidence": 0.9,
                    },
                ]
    return []


@router.get("")
def list_cases():
    try:
        rows = neo4j.execute(
            """
            MATCH (p:Person)
            OPTIONAL MATCH (p)-[r]->(m)
            WITH p,
                 count(r) AS evidence_count,
                 coalesce(p.community_id, 'Unassigned') AS community_id,
                 coalesce(p.pagerank, 0.0) AS pagerank,
                 coalesce(p.degree, COUNT { (p)--() }, 0) AS degree
            RETURN
                p.person_id AS id,
                coalesce(p.name, p.person_id) AS name,
                coalesce(p.name, p.person_id) AS title,
                CASE
                    WHEN pagerank >= 0.05 THEN 'High'
                    WHEN pagerank >= 0.02 THEN 'Medium'
                    ELSE 'Low'
                END AS priority,
                round(pagerank * 100, 2) AS risk_score,
                evidence_count,
                CASE
                    WHEN pagerank >= 0.05 THEN 'Active'
                    WHEN pagerank >= 0.02 THEN 'Monitoring'
                    ELSE 'Open'
                END AS status,
                community_id AS owner
            ORDER BY risk_score DESC, evidence_count DESC
            LIMIT 10
            """
        )
        if not rows:
            rows = _fallback_cases(10)

        return {"cases": rows}
    except Exception as exc:
        fallback = _fallback_cases(10)
        return {"cases": fallback, "status": "degraded" if not fallback else "operational"}


@router.get("/{case_id}/evidence")
def case_evidence(case_id: str):
    try:
        rows = neo4j.execute(
            """
            MATCH (p:Person {person_id: $case_id})
            OPTIONAL MATCH (p)-[r]-(n)
            RETURN
                type(r) AS type,
                coalesce(
                    n.name,
                    n.person_id,
                    n.fir_id,
                    n.account_id,
                    n.phone_id,
                    n.vehicle_id,
                    n.location_id,
                    n.organization_id,
                    labels(n)[0]
                ) AS title,
                coalesce(n.person_id, n.id, n.fir_id, n.account_id, n.phone_id, n.vehicle_id, n.location_id, n.organization_id) AS entity_id,
                n.name AS entity_name,
                coalesce(r.evidence, 'Linked to network entity') AS summary,
                coalesce(r.confidence, 0.75) AS confidence
            LIMIT 20
            """,
            {"case_id": case_id},
        )
        if not rows:
            rows = _fallback_evidence(case_id)

        return {"case_id": case_id, "evidence": rows}
    except Exception as exc:
        return {"case_id": case_id, "evidence": _fallback_evidence(case_id), "status": "degraded", "error": str(exc)}
