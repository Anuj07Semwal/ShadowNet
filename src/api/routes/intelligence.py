from fastapi import APIRouter

from src.api.services.neo4j_service import Neo4jService

router = APIRouter(prefix="/api/intelligence", tags=["Intelligence"])
neo4j = Neo4jService()


@router.get("/summary")
def intelligence_summary():
    try:
        entity_rows = neo4j.execute(
            """
            MATCH (n)
            WITH labels(n)[0] AS label, count(n) AS count
            RETURN label, count
            ORDER BY count DESC
            """
        )
        entity_counts = {
            row["label"]: row["count"]
            for row in entity_rows
            if row.get("label")
        }

        total_nodes = sum(entity_counts.values())
        relationship_count = neo4j.execute(
            "MATCH ()-[r]->() RETURN count(r) AS count"
        )[0]["count"]

        community_count = neo4j.execute(
            """
            MATCH (p:Person)
            WHERE p.community_id IS NOT NULL
            RETURN count(DISTINCT p.community_id) AS count
            """
        )[0].get("count", 0)

        anomaly_rows = neo4j.execute(
            """
            MATCH (n)
            WHERE n.is_anomaly = true OR n.anomaly_score IS NOT NULL
            RETURN count(n) AS anomaly_count,
                   avg(toFloat(coalesce(n.anomaly_score, 0))) AS avg_risk
            """
        )

        anomaly_count = anomaly_rows[0].get("anomaly_count", 0) if anomaly_rows else 0
        avg_risk = anomaly_rows[0].get("avg_risk", 0) if anomaly_rows else 0
        overall_score = min(100, round((float(avg_risk) if avg_risk is not None else 0) * 100, 1))

        high_priority_entities = neo4j.execute(
            """
            MATCH (p:Person)
            WHERE p.pagerank IS NOT NULL
            RETURN count(p) AS count
            """
        )[0].get("count", 0)

        graph_density = 0.0
        if total_nodes > 1:
            graph_density = round((2 * relationship_count) / (total_nodes * (total_nodes - 1)), 6)

        return {
            "network": {
                "total_nodes": total_nodes,
                "relationships": relationship_count,
                "communities": community_count,
                "graph_density": graph_density,
            },
            "risk": {
                "overall_score": overall_score,
                "anomaly_count": anomaly_count,
                "high_priority_entities": high_priority_entities,
            },
            "entities": entity_counts,
            "status": "operational",
        }
    except Exception as exc:
        return {
            "status": "degraded",
            "error": str(exc),
            "network": {
                "total_nodes": 0,
                "relationships": 0,
                "communities": 0,
                "graph_density": 0.0,
            },
            "risk": {
                "overall_score": 0,
                "anomaly_count": 0,
                "high_priority_entities": 0,
            },
            "entities": {},
        }


@router.get("/network")
def live_graph_stats():
    try:
        stats = intelligence_summary()
        if stats.get("status") == "degraded":
            return {
                "graph_name": "CNAS Criminal Network",
                "node_count": 0,
                "relationship_count": 0,
                "community_count": 0,
                "top_risk_areas": [],
                "status": "degraded",
            }

        network = stats["network"]
        return {
            "graph_name": "CNAS Criminal Network",
            "node_count": network["total_nodes"],
            "relationship_count": network["relationships"],
            "community_count": network["communities"],
            "top_risk_areas": [
                "Financial laundering",
                "Communication network",
                "Entity resolution",
            ],
            "status": "operational",
        }
    except Exception as exc:
        return {
            "graph_name": "CNAS Criminal Network",
            "node_count": 0,
            "relationship_count": 0,
            "community_count": 0,
            "top_risk_areas": [],
            "status": "degraded",
            "error": str(exc),
        }
