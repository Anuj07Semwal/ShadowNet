import csv
from pathlib import Path

from fastapi import APIRouter, Cookie, Depends, HTTPException
from src.api.services.neo4j_service import Neo4jService
from src.api.routes.auth import _require_session

router = APIRouter(
    prefix="/api/persons",
    tags=["Persons"]
)

neo4j = Neo4jService()


def _processed_path(filename: str) -> Path:
    return Path(__file__).resolve().parents[3] / "data" / "processed" / filename


def _raw_path(filename: str) -> Path:
    return Path(__file__).resolve().parents[3] / "data" / "documents" / "raw" / "CNAS_Prototype_Data" / filename


def _person_anomaly_records(person_id: str) -> list[dict]:
    path = _processed_path("transaction_anomalies.csv")
    if not path.exists():
        return []
    with path.open(newline="", encoding="utf-8") as stream:
        rows = csv.DictReader(stream)
        anomalies = []
        for row in rows:
            if row.get("person_id") != person_id or row.get("is_anomaly", "").lower() != "true":
                continue
            score = float(row.get("anomaly_score") or 0)
            anomalies.append({
                "id": row.get("transaction_id") or row.get("relationship_id"),
                "type": row.get("anomaly_type") or "anomalous transaction",
                "severity": "high" if score >= 0.9 else "medium" if score >= 0.7 else "low",
                "date": row.get("timestamp"),
                "transaction_id": row.get("transaction_id") or row.get("relationship_id"),
                "amount": float(row.get("amount") or 0),
                "channel": row.get("channel"),
                "score": score,
                "reason": row.get("reason"),
            })
    return sorted(anomalies, key=lambda item: item["score"], reverse=True)


def _verified_cases(person_id: str) -> list[dict]:
    path = _raw_path("source_fir_records_cleaned.csv")
    if not path.exists():
        return []
    with path.open(newline="", encoding="utf-8") as stream:
        rows = csv.DictReader(stream)
        return [
            {
                "id": row.get("fir_id"),
                "source": "source_fir_records_cleaned.csv",
                "status": "recorded source entry",
                "date": row.get("year"),
                "title": row.get("crime_type") or "Verified source record",
                "station": row.get("police_station"),
                "summary": row.get("summary"),
                "confidence": float(row.get("confidence") or 0),
            }
            for row in rows
            if row.get("person_id") == person_id
        ]


def _risk_profile(person_id: str, person: dict) -> dict:
    anomalies = _person_anomaly_records(person_id)
    max_score = max((item["score"] for item in anomalies), default=0.0)
    count_factor = min(len(anomalies) / 10, 1.0)
    score = round(min(100, (max_score * 70) + (count_factor * 30)), 1)
    community_id = person.get("community_id")
    associations = []
    if community_id is not None:
        associations.append({
            "id": str(community_id),
            "type": "community_id",
            "label": str(community_id),
            "source": "authorized graph property",
        })
    return {
        "score": score,
        "band": "high" if score >= 70 else "medium" if score >= 35 else "low",
        "method": "Triage score based only on persisted transaction anomaly scores and anomaly count; it is not a criminality judgment.",
        "factors": [
            {"name": "Highest anomaly score", "value": round(max_score * 100, 1), "unit": "%"},
            {"name": "Anomalous transaction count", "value": len(anomalies), "unit": "records"},
        ],
        "anomalies": anomalies,
        "associations": associations,
        "cases": _verified_cases(person_id),
        "history": [],
    }


def _entity(item, entity_type, id_keys, name_keys=()):
    item = item or {}
    entity_id = next((item.get(key) for key in id_keys if item.get(key) is not None), None)
    name = next((item.get(key) for key in name_keys if item.get(key) is not None), None)
    return {
        "id": entity_id,
        "name": name or entity_id,
        "type": entity_type,
        "properties": item,
    }


def _profile_graph(person_id, person, connections, phones, vehicles, locations, organizations, accounts, transactions, emails):
    nodes = [{"id": person_id, "type": "person", "label": person.get("name") or person_id}]
    edges = []
    seen = {person_id}

    def add_entity(entity, relationship):
        entity_id = entity.get("id")
        if not entity_id:
            return
        if entity_id not in seen:
            nodes.append({"id": entity_id, "type": entity["type"].lower(), "label": entity.get("name") or entity_id})
            seen.add(entity_id)
        edges.append({"source": person_id, "target": entity_id, "relationship": relationship})

    for connection in connections:
        entity = _entity(connection.get("properties"), (connection.get("labels") or ["entity"])[0].lower(), [
            "person_id", "organization_id", "vehicle_id", "location_id", "phone_id", "account_id", "fir_id", "id"
        ], ["name", "organization_name", "location_name", "phone_number", "registration_number"])
        entity["id"] = connection.get("id") or entity["id"]
        entity["name"] = connection.get("name") or entity["name"]
        entity["type"] = (connection.get("labels") or ["entity"])[0].lower()
        add_entity(entity, connection.get("relationship") or "CONNECTED_TO")

    for items, relationship in ((phones, "USES"), (vehicles, "OWNS"), (locations, "VISITED"), (organizations, "WORKS_FOR"), (accounts, "OWNS_ACCOUNT")):
        for item in items:
            add_entity(item, relationship)

    for transaction in transactions:
        transaction_id = transaction.get("transaction_id")
        if transaction_id:
            add_entity({"id": transaction_id, "name": transaction_id, "type": "transaction"}, "TRANSACTED_WITH")

    for email in emails:
        other_id = email.get("other_person_id")
        if other_id:
            add_entity({"id": other_id, "name": email.get("other_person_name") or other_id, "type": "person"}, "EMAILED")

    return {"nodes": nodes, "edges": edges}


@router.get("")
def get_persons(limit: int = 50):

    query = """
    MATCH (p:Person)
    RETURN
        p.person_id AS person_id,
        coalesce(p.name, p.person_id) AS name,
        p.source AS source,
        p.source_role AS source_role,
        p.confidence AS confidence,
        p.degree AS degree,
        p.degree_centrality AS degree_centrality,
        p.betweenness AS betweenness,
        p.pagerank AS pagerank,
        p.community_id AS community_id,
        p.community_size AS community_size
    LIMIT $limit
    """

    return {
        "count": limit,
        "persons": neo4j.execute(
            query,
            {"limit": limit}
        )
    }


@router.get("/{person_id}")
def get_person(person_id: str):

    query = """
    MATCH (p:Person {person_id: $person_id})
    RETURN
        p.person_id AS person_id,
        coalesce(p.name, p.person_id) AS name,
        p.source AS source,
        p.source_role AS source_role,
        p.confidence AS confidence,
        p.degree AS degree,
        p.degree_centrality AS degree_centrality,
        p.betweenness AS betweenness,
        p.pagerank AS pagerank,
        p.community_id AS community_id,
        p.community_size AS community_size
    """

    result = neo4j.execute(
        query,
        {"person_id": person_id}
    )

    if not result:
        raise HTTPException(
            status_code=404,
            detail="Person not found"
        )

    return result[0]


@router.get("/{person_id}/profile")
def get_person_profile(person_id: str, shadownet_session: str | None = Cookie(default=None)):
    _require_session(shadownet_session)
    person_rows = neo4j.execute(
        """
        MATCH (p:Person {person_id: $person_id})
        RETURN properties(p) AS properties
        """,
        {"person_id": person_id},
    )
    if not person_rows:
        raise HTTPException(status_code=404, detail="Person not found")

    person = person_rows[0].get("properties") or {}
    connections = neo4j.execute(
        """
        MATCH (p:Person {person_id: $person_id})-[r]-(other)
        RETURN
            coalesce(other.person_id, other.organization_id, other.vehicle_id,
                     other.location_id, other.phone_id, other.account_id,
                     other.fir_id, other.id) AS id,
            coalesce(other.name, other.organization_name, other.location_name,
                     other.phone_number, other.registration_number,
                     other.person_id, other.organization_id, other.vehicle_id,
                     other.location_id, other.phone_id, other.account_id,
                     other.fir_id, other.id) AS name,
            labels(other) AS labels,
            properties(other) AS properties,
            type(r) AS relationship,
            CASE WHEN startNode(r) = p THEN 'outgoing' ELSE 'incoming' END AS direction,
            properties(r) AS relationship_properties
        ORDER BY relationship, name
        LIMIT 500
        """,
        {"person_id": person_id},
    )

    phones = [
        _entity(row.get("row"), "Phone", ["phone_id"], ["phone_number"])
        for row in neo4j.execute("MATCH (n:Phone {person_id: $person_id}) RETURN properties(n) AS row", {"person_id": person_id})
    ]
    vehicles = [
        _entity(row.get("row"), "Vehicle", ["vehicle_id"], ["registration_number", "make"])
        for row in neo4j.execute("MATCH (n:Vehicle {owner_person_id: $person_id}) RETURN properties(n) AS row", {"person_id": person_id})
    ]
    locations = []
    for row in neo4j.execute(
            """
            MATCH (p:Person {person_id: $person_id})-[r:VISITED]-(n:Location)
            RETURN properties(n) AS row, r.timestamp AS visited_at, r.purpose AS purpose
            ORDER BY visited_at DESC
            """,
            {"person_id": person_id},
        ):
        location = _entity(row.get("row"), "Location", ["location_id"], ["location_name", "city"])
        location["properties"]["visited_at"] = row.get("visited_at")
        location["properties"]["purpose"] = row.get("purpose")
        locations.append(location)
    organizations = [
        _entity(row.get("row"), "Organization", ["organization_id"], ["organization_name", "name"])
        for row in neo4j.execute(
            """
            MATCH (p:Person {person_id: $person_id})-[r:WORKS_FOR]-(n:Organization)
            RETURN properties(n) AS row
            """,
            {"person_id": person_id},
        )
    ]
    accounts = [
        _entity(row.get("row"), "Account", ["account_id"], ["account_number_masked", "bank_name"])
        for row in neo4j.execute("MATCH (n:Account {person_id: $person_id}) RETURN properties(n) AS row", {"person_id": person_id})
    ]
    transactions = neo4j.execute(
        """
        MATCH (source:Account)-[r:TRANSFERRED_MONEY]->(target:Account)
        WHERE source.person_id = $person_id OR target.person_id = $person_id
        RETURN
            r.relationship_id AS transaction_id,
            r.timestamp AS timestamp,
            r.amount AS amount,
            r.channel AS transaction_type,
            r.is_anomaly AS is_anomaly,
            r.anomaly_type AS anomaly_type,
            source.account_id AS sender_account_id,
            source.person_id AS sender_person_id,
            target.account_id AS receiver_account_id,
            target.person_id AS receiver_person_id
        ORDER BY timestamp DESC
        LIMIT 200
        """,
        {"person_id": person_id},
    )
    emails = neo4j.execute(
        """
        MATCH (p:Person {person_id: $person_id})-[r:EMAILED]-(other:Person)
        RETURN other.person_id AS other_person_id, other.name AS other_person_name,
               r.relationship_id AS email_id, r.timestamp AS timestamp,
               r.confidence AS confidence, r.provenance AS provenance
        ORDER BY timestamp DESC
        LIMIT 200
        """,
        {"person_id": person_id},
    )

    relationships = [
        {
            "id": row.get("id"),
            "name": row.get("name"),
            "type": (row.get("labels") or ["entity"])[0].lower(),
            "relationship": row.get("relationship"),
            "direction": row.get("direction"),
            "confidence": (row.get("relationship_properties") or {}).get("confidence"),
            "properties": row.get("properties") or {},
        }
        for row in connections
    ]

    return {
        "id": person_id,
        "name": person.get("name") or person_id,
        "basic": person,
        "locations": locations,
        "vehicles": vehicles,
        "organizations": organizations,
        "phones": phones,
        "emails": emails,
        "accounts": accounts,
        "transactions": transactions,
        "relationships": relationships,
        "risk": _risk_profile(person_id, person),
        "graph": _profile_graph(person_id, person, connections, phones, vehicles, locations, organizations, accounts, transactions, emails),
    }


@router.get("/{person_id}/network")
def get_person_network(person_id: str):
    person = get_person(person_id)

    query = """
    MATCH (p:Person {person_id: $person_id})-[r]-(other)
    RETURN
        coalesce(
            other.person_id,
            other.fir_id,
            other.account_id,
            other.phone_id,
            other.vehicle_id,
            other.location_id,
            other.organization_id,
            labels(other)[0]
        ) AS id,
        coalesce(
            other.name,
            other.person_id,
            other.fir_id,
            other.account_id,
            other.phone_id,
            other.vehicle_id,
            other.location_id,
            other.organization_id,
            labels(other)[0]
        ) AS name,
        labels(other) AS type,
        type(r) AS relationship
    ORDER BY type(r), id
    LIMIT 200
    """

    connections = neo4j.execute(query, {"person_id": person_id})

    return {
        "person_id": person_id,
        "name": person.get("name") or person_id,
        "degree": person.get("degree"),
        "degree_centrality": person.get("degree_centrality"),
        "betweenness": person.get("betweenness"),
        "pagerank": person.get("pagerank"),
        "community": person.get("community_id"),
        "community_size": person.get("community_size"),
        "connections": connections,
    }


@router.get("/{person_id}/anomalies")
def get_person_anomalies(person_id: str):
    query = """
    MATCH (p:Person {person_id: $person_id})-[r]-(t:Transaction)
    WHERE coalesce(r.is_anomaly, t.is_anomaly, false) = true
       OR coalesce(r.anomaly_score, t.anomaly_score, 0) > 0
    RETURN
        coalesce(t.id, r.id) AS transaction_id,
        t.amount AS amount,
        t.timestamp AS timestamp,
        coalesce(r.anomaly_score, t.anomaly_score, 0) AS anomaly_score,
        coalesce(r.is_anomaly, t.is_anomaly, false) AS is_anomaly
    ORDER BY anomaly_score DESC
    LIMIT 50
    """

    rows = neo4j.execute(query, {"person_id": person_id})
    return {
        "person_id": person_id,
        "count": len(rows),
        "anomalies": rows,
    }


@router.get("/{person_id}/connections")
def get_connections(person_id: str):

    query = """
    MATCH (p:Person {person_id: $person_id})-[r]-(other)
    RETURN
        p.person_id AS source,
        type(r) AS relationship,
        labels(other) AS target_type,
        coalesce(
            other.person_id,
            other.fir_id,
            other.account_id,
            other.phone_id,
            other.vehicle_id,
            other.location_id,
            other.organization_id
        ) AS target
    LIMIT 500
    """

    return {
        "person_id": person_id,
        "connections": neo4j.execute(
            query,
            {"person_id": person_id}
        )
    }