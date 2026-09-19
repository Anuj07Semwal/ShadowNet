from pathlib import Path

import pandas as pd

from src.data_paths import resolve_processed_dir
from src.graph.neo4j_client import Neo4jClient


PROCESSED_DIR = resolve_processed_dir()


def find_column(df, candidates):

    for candidate in candidates:

        if candidate in df.columns:
            return candidate

    raise ValueError(
        f"None of {candidates} found. "
        f"Available: {list(df.columns)}"
    )


def load_edge_file(
    client,
    filename,
    relationship_type,
    source_candidates,
    target_candidates
):

    path = PROCESSED_DIR / filename

    if not path.exists():

        print(f"⚠ Missing: {path}")

        return

    df = pd.read_csv(path)

    source_column = find_column(
        df,
        source_candidates
    )

    target_column = find_column(
        df,
        target_candidates
    )

    rows = []

    for index, row in df.iterrows():

        source_id = row[source_column]
        target_id = row[target_column]

        if pd.isna(source_id) or pd.isna(target_id):
            continue

        rows.append({
            "relationship_id":
                f"{filename}_{index}",

            "source_id":
                str(source_id),

            "target_id":
                str(target_id)
        })

    query = f"""
    UNWIND $rows AS row

    MATCH (source)
    WHERE
        source.fir_id = row.source_id
        OR source.person_id = row.source_id
        OR source.crime_id = row.source_id
        OR source.station_id = row.source_id
        OR source.statute_id = row.source_id

    MATCH (target)
    WHERE
        target.fir_id = row.target_id
        OR target.person_id = row.target_id
        OR target.crime_id = row.target_id
        OR target.station_id = row.target_id
        OR target.statute_id = row.target_id

    MERGE (source)-[r:{relationship_type} {{
        relationship_id: row.relationship_id
    }}]->(target)
    """

    client.execute(
        query,
        {"rows": rows}
    )

    print(
        f"✓ {relationship_type}: "
        f"{len(rows):,}"
    )


def main():

    client = Neo4jClient()

    try:

        client.verify_connection()

        load_edge_file(
            client,
            "source_fir_person_edges.csv",
            "MENTIONS",
            ["fir_id", "source_id"],
            ["person_id", "target_id"]
        )

        load_edge_file(
            client,
            "source_fir_crime_edges.csv",
            "HAS_CRIME",
            ["fir_id", "source_id"],
            ["crime_id", "target_id"]
        )

        load_edge_file(
            client,
            "source_fir_station_edges.csv",
            "REPORTED_AT",
            ["fir_id", "source_id"],
            ["station_id", "target_id"]
        )

        load_edge_file(
            client,
            "source_crime_statute_edges.csv",
            "HAS_STATUTE",
            ["crime_id", "source_id"],
            ["statute_id", "target_id"]
        )

    finally:

        client.close()


if __name__ == "__main__":
    main()