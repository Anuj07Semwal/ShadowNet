from pathlib import Path

import pandas as pd

from src.data_paths import resolve_processed_dir
from src.graph.neo4j_client import Neo4jClient


PROCESSED_DIR = resolve_processed_dir()
FIR_FILE = PROCESSED_DIR / "firs.csv"


def clean_value(value):
    if pd.isna(value):
        return None

    if hasattr(value, "item"):
        try:
            return value.item()
        except Exception:
            pass

    return value


def normalize_id(value):
    if value is None:
        return None

    value = str(value).strip()

    if value == "" or value.lower() == "nan":
        return None

    return value


def load_fir_graph():

    if not FIR_FILE.exists():
        print(f"⚠ Missing: {FIR_FILE}")
        return

    df = pd.read_csv(FIR_FILE)

    client = Neo4jClient()

    try:

        client.verify_connection()

        # =================================================
        # 1. PoliceStation nodes
        # =================================================

        stations = {}

        for _, row in df.iterrows():

            station_id = normalize_id(
                clean_value(row.get("station_id"))
            )

            if station_id:
                stations[station_id] = {
                    "station_id": station_id
                }

        if stations:

            client.execute(
                """
                UNWIND $rows AS row

                MERGE (s:PoliceStation {
                    station_id: row.station_id
                })
                """,
                {
                    "rows": list(stations.values())
                }
            )

        print(
            f"✓ PoliceStation: "
            f"{len(stations):,} nodes"
        )

        # =================================================
        # 2. Crime nodes
        # =================================================

        crimes = {}

        for _, row in df.iterrows():

            crime_type = normalize_id(
                clean_value(row.get("crime_type"))
            )

            if not crime_type:
                continue

            crime_id = "CRIME_" + crime_type

            crimes[crime_id] = {
                "crime_id": crime_id,
                "name": crime_type
            }

        if crimes:

            client.execute(
                """
                UNWIND $rows AS row

                MERGE (c:Crime {
                    crime_id: row.crime_id
                })

                SET c.name = row.name
                """,
                {
                    "rows": list(crimes.values())
                }
            )

        print(
            f"✓ Crime: "
            f"{len(crimes):,} nodes"
        )

        # =================================================
        # 3. FIR -> PoliceStation
        # =================================================

        fir_station_edges = []

        for _, row in df.iterrows():

            fir_id = normalize_id(
                clean_value(row.get("fir_id"))
            )

            station_id = normalize_id(
                clean_value(row.get("station_id"))
            )

            if not fir_id or not station_id:
                continue

            fir_station_edges.append({
                "fir_id": fir_id,
                "station_id": station_id
            })

        if fir_station_edges:

            client.execute(
                """
                UNWIND $rows AS row

                MATCH (f:FIR {
                    fir_id: row.fir_id
                })

                MATCH (s:PoliceStation {
                    station_id: row.station_id
                })

                MERGE (f)-[:FILED_AT]->(s)
                """,
                {
                    "rows": fir_station_edges
                }
            )

        print(
            f"✓ FIR -> PoliceStation: "
            f"{len(fir_station_edges):,}"
        )

        # =================================================
        # 4. FIR -> Crime
        # =================================================

        fir_crime_edges = []

        for _, row in df.iterrows():

            fir_id = normalize_id(
                clean_value(row.get("fir_id"))
            )

            crime_type = normalize_id(
                clean_value(row.get("crime_type"))
            )

            if not fir_id or not crime_type:
                continue

            crime_id = "CRIME_" + crime_type

            fir_crime_edges.append({
                "fir_id": fir_id,
                "crime_id": crime_id
            })

        if fir_crime_edges:

            client.execute(
                """
                UNWIND $rows AS row

                MATCH (f:FIR {
                    fir_id: row.fir_id
                })

                MATCH (c:Crime {
                    crime_id: row.crime_id
                })

                MERGE (f)-[:ABOUT_CRIME]->(c)
                """,
                {
                    "rows": fir_crime_edges
                }
            )

        print(
            f"✓ FIR -> Crime: "
            f"{len(fir_crime_edges):,}"
        )

        # =================================================
        # 5. Statute nodes
        # =================================================

        statutes = {}

        for _, row in df.iterrows():

            sections = clean_value(
                row.get("sections_list")
            )

            if not sections:
                continue

            for section in str(sections).split("|"):

                section = section.strip()

                if not section:
                    continue

                statute_id = "STATUTE_" + section

                statutes[statute_id] = {
                    "statute_id": statute_id,
                    "section": section
                }

        if statutes:

            client.execute(
                """
                UNWIND $rows AS row

                MERGE (s:Statute {
                    statute_id: row.statute_id
                })

                SET s.section = row.section
                """,
                {
                    "rows": list(statutes.values())
                }
            )

        print(
            f"✓ Statute: "
            f"{len(statutes):,} nodes"
        )

        # =================================================
        # 6. Crime -> Statute
        # =================================================

        crime_statute_edges = set()

        for _, row in df.iterrows():

            crime_type = normalize_id(
                clean_value(row.get("crime_type"))
            )

            sections = clean_value(
                row.get("sections_list")
            )

            if not crime_type or not sections:
                continue

            crime_id = "CRIME_" + crime_type

            for section in str(sections).split("|"):

                section = section.strip()

                if not section:
                    continue

                statute_id = "STATUTE_" + section

                crime_statute_edges.add(
                    (
                        crime_id,
                        statute_id
                    )
                )

        edges = [
            {
                "crime_id": crime_id,
                "statute_id": statute_id
            }
            for crime_id, statute_id
            in crime_statute_edges
        ]

        if edges:

            client.execute(
                """
                UNWIND $rows AS row

                MATCH (c:Crime {
                    crime_id: row.crime_id
                })

                MATCH (s:Statute {
                    statute_id: row.statute_id
                })

                MERGE (c)-[:UNDER_STATUTE]->(s)
                """,
                {
                    "rows": edges
                }
            )

        print(
            f"✓ Crime -> Statute: "
            f"{len(edges):,}"
        )

        print()
        print("✓ FIR graph loaded successfully")

    finally:

        client.close()


if __name__ == "__main__":
    load_fir_graph()
