from fastapi import APIRouter

from src.api.services.neo4j_service import Neo4jService

router = APIRouter(prefix="/api/cases", tags=["Cases"])
neo4j = Neo4jService()


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
                 coalesce(p.degree, 0) AS degree
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

        return {"cases": rows}
    except Exception as exc:
        return {"cases": [], "status": "degraded", "error": str(exc)}


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

        return {"case_id": case_id, "evidence": rows}
    except Exception as exc:
        return {"case_id": case_id, "evidence": [], "status": "degraded", "error": str(exc)}
