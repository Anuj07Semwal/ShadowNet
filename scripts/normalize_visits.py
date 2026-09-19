from pathlib import Path
import pandas as pd

from src.data_paths import resolve_processed_dir, resolve_raw_dir


RAW_DIR = resolve_raw_dir()
OUT_DIR = resolve_processed_dir()

df = pd.read_csv(
    RAW_DIR / "synthetic_visits.csv"
)

visits = pd.DataFrame({
    "relationship_id": df["visit_id"],
    "source_id": df["person_id"],
    "source_type": "Person",
    "relationship": "VISITED",
    "target_id": df["location_id"],
    "target_type": "Location",
    "timestamp": df["timestamp"],
    "source_document": pd.NA,
    "confidence": 1.0,
    "provenance": df.get("data_provenance", "synthetic"),
    "purpose": df.get("purpose", pd.NA),
    "is_anomaly": df.get("is_injected_anomaly", False),
    "anomaly_type": df.get("anomaly_type", pd.NA)
})

visits.to_csv(
    OUT_DIR / "relationships_visits.csv",
    index=False
)