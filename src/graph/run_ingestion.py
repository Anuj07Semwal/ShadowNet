from src.graph.create_constraints import create_constraints
from src.graph.load_nodes import load_all_nodes
from src.graph.load_relationships import load_all_relationships
from src.graph.neo4j_client import Neo4jClient


def reset_graph():
    client = Neo4jClient()
    try:
        client.verify_connection()
        client.execute("MATCH (n) DETACH DELETE n")
        print("✓ Existing graph cleared")
    finally:
        client.close()


def main():

    print("=" * 70)
    print("CNAS KNOWLEDGE GRAPH INGESTION")
    print("=" * 70)

    print("\n[1/4] Clearing stale graph data...")
    reset_graph()

    print("\n[2/4] Creating constraints...")
    create_constraints()

    print("\n[3/4] Loading nodes...")
    load_all_nodes()

    print("\n[4/4] Loading relationships...")
    load_all_relationships()

    print("\n" + "=" * 70)
    print("✓ CNAS GRAPH INGESTION COMPLETED")
    print("=" * 70)


if __name__ == "__main__":
    main()