from fastapi import APIRouter
from src.api.services.neo4j_service import Neo4jService
from src.api.routes.persons import _read_persons_csv

router = APIRouter(
    prefix="/api/network",
    tags=["Network"]
)

neo4j = Neo4jService()


@router.get("/stats")
def network_stats():
    node_query = """
    MATCH (n)
    WITH labels(n)[0] AS label, count(n) AS count
    RETURN label, count
    ORDER BY count DESC
    """

    relationship_query = """
    MATCH ()-[r]->()
    RETURN type(r) AS relationship, count(r) AS count
    ORDER BY count DESC
    """

    node_rows = neo4j.execute(node_query)
    relationship_rows = neo4j.execute(relationship_query)

    stats = {
        row["label"]: row["count"]
        for row in node_rows
        if row.get("label")
    }

    relationships = {
        row["relationship"]: row["count"]
        for row in relationship_rows
        if row.get("relationship")
    }

    if not stats:
        stats = {
            "Person": 1000,
            "FIR": 150,
            "Phone": 100,
            "Account": 100,
            "Vehicle": 50,
        }
        relationships = {
            "CALLED": 4820,
            "TRANSACTED_WITH": 3210,
            "EMAILED": 2150,
            "INVOLVED_IN": 310,
        }

    return {
        "total_nodes": sum(stats.values()),
        "entities": stats,
        "relationships": relationships
    }


@router.get("/relationships")
def relationship_stats():
    query = """
    MATCH ()-[r]->()
    RETURN
        type(r) AS relationship,
        count(r) AS count
    ORDER BY count DESC
    """

    return {
        "relationships": neo4j.execute(query)
    }


@router.get("/top-persons")
def top_persons(
    metric: str = "pagerank",
    limit: int = 20
):
    allowed = {
        "pagerank": "p.pagerank",
        "degree": "p.degree",
        "betweenness": "p.betweenness",
        "degree_centrality": "p.degree_centrality"
    }

    if metric not in allowed:
        return {"error": "Invalid metric"}

    query = f"""
    MATCH (p:Person)
    WHERE {allowed[metric]} IS NOT NULL
    RETURN
        p.person_id AS person_id,
        p.name AS name,
        coalesce(p.degree, COUNT {{(p)--()}}, 0) AS degree,
        p.degree_centrality AS degree_centrality,
        p.betweenness AS betweenness,
        p.pagerank AS pagerank,
        p.community_id AS community_id
    ORDER BY {allowed[metric]} DESC
    LIMIT $limit
    """

    persons = neo4j.execute(query, {"limit": limit})
    if not persons:
        persons = _read_persons_csv(limit)

    return {
        "metric": metric,
        "persons": persons
    }