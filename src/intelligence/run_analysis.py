from src.intelligence.graph_loader import (
    load_person_graph
)

from src.intelligence.analyze_person import (
    analyze_graph
)

from src.intelligence.save_results import (
    save_results
)


def main():

    print("=" * 70)
    print("CNAS GRAPH INTELLIGENCE ENGINE")
    print("=" * 70)

    print()
    print("[1/3] Loading Person graph...")

    graph = load_person_graph()

    print()
    print("[2/3] Running graph algorithms...")

    results = analyze_graph(
        graph
    )

    print()
    print("[3/3] Saving results to Neo4j...")

    save_results(
        results
    )

    print()
    print(
        "[OK] CNAS graph intelligence "
        "pipeline completed"
    )


if __name__ == "__main__":
    main()