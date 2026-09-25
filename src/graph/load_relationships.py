from pathlib import Path

import pandas as pd

from src.data_paths import resolve_processed_dir
from src.graph.neo4j_client import Neo4jClient


PROCESSED_DIR = resolve_processed_dir()

RELATIONSHIP_FILES = [
    "relationships_calls.csv",
    "relationships_emails.csv",
    "relationships_transactions.csv",
    "relationships_visits.csv",
    "relationships_works_for.csv",
]

NODE_LABELS = {
    "Person": "Person",
    "Phone": "Phone",
    "Vehicle": "Vehicle",
    "Location": "Location",
    "Organization": "Organization",
    "Account": "Account",
    "FIR": "FIR",
}

NODE_ID_PROPERTIES = {
    "Person": "person_id",
    "Phone": "phone_id",
    "Vehicle": "vehicle_id",
    "Location": "location_id",
    "Organization": "organization_id",
    "Account": "account_id",
    "FIR": "fir_id",
}


def clean_value(value):

    if pd.isna(value):

        return None

    if hasattr(value, "item"):

        try:
            return value.item()

        except Exception:
            pass

    return value


def load_relationship_file(
    client,
    filename
):

    path = PROCESSED_DIR / filename

    if not path.exists():

        print(f"⚠ Missing: {path}")

        return 0

    df = pd.read_csv(path)

    required_columns = [
        "relationship_id",
        "source_id",
        "source_type",
        "relationship",
        "target_id",
        "target_type"
    ]

    missing = [
        column
        for column in required_columns
        if column not in df.columns
    ]

    if missing:

        raise ValueError(
            f"{filename} missing columns: {missing}"
        )

    records = []

    for _, row in df.iterrows():

        record = {}

        for column in df.columns:

            record[column] = clean_value(
                row[column]
            )

        records.append(record)

    # Relationship and endpoint labels cannot safely be parameterized in
    # Cypher, so group by all three values and use indexed node properties.

    total = 0
    skipped = 0

    for (relationship_type, source_type, target_type), group in df.groupby(
        ["relationship", "source_type", "target_type"], dropna=False
    ):

        source_label = NODE_LABELS.get(source_type)
        target_label = NODE_LABELS.get(target_type)
        source_property = NODE_ID_PROPERTIES.get(source_type)
        target_property = NODE_ID_PROPERTIES.get(target_type)

        if not source_label or not target_label:
            print(f"⚠ Skipping unsupported endpoint types: {source_type} -> {target_type}")
            continue

        rows = []

        for _, row in group.iterrows():

            properties = {}

            for column in df.columns:

                if column in [
                    "relationship_id",
                    "source_id",
                    "source_type",
                    "relationship",
                    "target_id",
                    "target_type"
                ]:
                    continue

                value = clean_value(row[column])

                if value is not None:

                    properties[column] = value

            rows.append({
                "relationship_id": clean_value(
                    row["relationship_id"]
                ),
                "source_id": clean_value(
                    row["source_id"]
                ),
                "target_id": clean_value(
                    row["target_id"]
                ),
                "properties": properties
            })

        query = f"""
        UNWIND $rows AS row

        MATCH (source:{source_label} {{{source_property}: row.source_id}})
        MATCH (target:{target_label} {{{target_property}: row.target_id}})

        MERGE (source)-[r:{relationship_type} {{
            relationship_id: row.relationship_id
        }}]->(target)

        SET r += row.properties
        """

        batch_size = 1000
        batch_failed = False
        for i in range(0, len(rows), batch_size):
            chunk = rows[i:i + batch_size]
            summary = client.execute(
                query,
                {"rows": chunk}
            )
            if summary is None:
                batch_failed = True
                skipped += len(chunk)
                print(f"  ⚠ {relationship_type}: Neo4j rejected batch {i // batch_size + 1} ({len(chunk):,} rows)")

        if not batch_failed:
            total += len(rows)
            print(
                f"  ✓ {relationship_type}: "
                f"{len(rows):,}"
            )

    print(
        f"✓ {filename}: {total:,} relationships"
    )

    if skipped:
        print(f"⚠ {filename}: {skipped:,} rows skipped after Neo4j errors")

    return total


def load_all_relationships():

    client = Neo4jClient()

    try:

        client.verify_connection()

        total = 0

        for filename in RELATIONSHIP_FILES:

            total += load_relationship_file(
                client,
                filename
            )

        print()
        print(
            f"Total relationships processed: "
            f"{total:,}"
        )

    finally:

        client.close()


if __name__ == "__main__":
    load_all_relationships()
