from pathlib import Path

import pandas as pd

from src.data_paths import resolve_processed_dir
from src.graph.neo4j_client import Neo4jClient


PROCESSED_DIR = resolve_processed_dir()


NODE_CONFIG = {

    "persons.csv": {
        "label": "Person",
        "id_column": "person_id",
        "id_property": "person_id"
    },

    "phones.csv": {
        "label": "Phone",
        "id_column": "phone_id",
        "id_property": "phone_id"
    },

    "vehicles.csv": {
        "label": "Vehicle",
        "id_column": "vehicle_id",
        "id_property": "vehicle_id"
    },

    "locations.csv": {
        "label": "Location",
        "id_column": "location_id",
        "id_property": "location_id"
    },

    "organizations.csv": {
        "label": "Organization",
        "id_column": "organization_id",
        "id_property": "organization_id"
    },

    "accounts.csv": {
        "label": "Account",
        "id_column": "account_id",
        "id_property": "account_id"
    },

    "firs.csv": {
        "label": "FIR",
        "id_column": "fir_id",
        "id_property": "fir_id"
    }
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


def load_node_file(
    client,
    filename,
    config
):

    path = PROCESSED_DIR / filename

    if not path.exists():

        print(f"⚠ Missing: {path}")

        return 0

    df = pd.read_csv(path)

    label = config["label"]
    id_column = config["id_column"]
    id_property = config["id_property"]

    records = []

    for _, row in df.iterrows():

        properties = {}

        for column in df.columns:

            value = clean_value(row[column])

            if value is not None:

                properties[column] = value

        node_id = clean_value(
            row[id_column]
        )

        if node_id is None:

            continue

        records.append({
            "node_id": node_id,
            "properties": properties
        })

    query = f"""
    UNWIND $rows AS row

    MERGE (n:{label} {{{id_property}: row.node_id}})

    SET n += row.properties
    """

    client.execute(
        query,
        {"rows": records}
    )

    print(
        f"✓ {label}: "
        f"{len(records):,} nodes loaded"
    )

    return len(records)


def load_all_nodes():

    client = Neo4jClient()

    try:

        client.verify_connection()

        total = 0

        for filename, config in NODE_CONFIG.items():

            total += load_node_file(
                client,
                filename,
                config
            )

        print()
        print(
            f"Total nodes processed: {total:,}"
        )

    finally:

        client.close()


if __name__ == "__main__":
    load_all_nodes()