import networkx as nx

from src.graph.neo4j_client import Neo4jClient


RELATIONSHIP_TYPES = [
    "CALLED",
    "EMAILED",
    "TRANSFERRED_MONEY",
]


def load_person_graph():

    client = Neo4jClient()

    try:

        client.verify_connection()

        query = """
        MATCH (a:Person)-[r]->(b:Person)
        WHERE type(r) IN $relationship_types

        RETURN
            a.person_id AS source,
            b.person_id AS target,
            type(r) AS relationship_type
        """

        records = client.execute_read(
            query,
            {
                "relationship_types":
                    RELATIONSHIP_TYPES
            }
        )

        graph = nx.Graph()

        for record in records:

            source = record["source"]
            target = record["target"]
            relationship_type = record[
                "relationship_type"
            ]

            if source is None or target is None:
                continue

            if graph.has_edge(source, target):

                graph[source][target]["weight"] += 1

                graph[source][target][
                    "relationship_types"
                ].add(relationship_type)

                graph[source][target]["distance"] = (
                    1 / graph[source][target]["weight"]
                )

            else:

                graph.add_edge(
                    source,
                    target,
                    weight=1,
                    distance=1.0,
                    relationship_types={
                        relationship_type
                    }
                )

        print(
            f"[OK] NetworkX graph loaded: "
            f"{graph.number_of_nodes():,} persons"
        )

        print(
            f"[OK] NetworkX edges: "
            f"{graph.number_of_edges():,}"
        )

        return graph

    finally:

        client.close()