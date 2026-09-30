from src.graph.neo4j_client import Neo4jClient


def save_results(results):

    client = Neo4jClient()

    try:

        client.verify_connection()

        rows = list(
            results.values()
        )

        query = """
        UNWIND $rows AS row

        MATCH (p:Person {
            person_id: row.person_id
        })

        SET
            p.degree = coalesce(p.degree, row.degree),
            p.degree_centrality =
                row.degree_centrality,
            p.betweenness =
                row.betweenness,
            p.pagerank =
                row.pagerank,
            p.community_id =
                row.community_id,
            p.community_size =
                row.community_size

        RETURN count(p) AS updated
        """

        records = client.execute_read(
            query,
            {
                "rows": rows
            }
        )

        updated = (
            records[0]["updated"]
            if records
            else 0
        )

        print(
            f"[OK] Intelligence saved "
            f"for {updated:,} persons"
        )

    finally:

        client.close()