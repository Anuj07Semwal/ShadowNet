from pathlib import Path
import pandas as pd

from src.data_paths import resolve_processed_dir, resolve_raw_dir


RAW_DIR = resolve_raw_dir()
OUT_DIR = resolve_processed_dir()

df = pd.read_csv(
    RAW_DIR / "synthetic_calls.csv"
)

calls = pd.DataFrame({
    "relationship_id": df["call_id"],
    "source_id": df["caller_person_id"],
    "source_type": "Person",
    "relationship": "CALLED",
    "target_id": df["receiver_person_id"],
    "target_type": "Person",
    "timestamp": df["timestamp"],
    "source_document": pd.NA,
    "confidence": 1.0,
    "provenance": df.get("data_provenance", "synthetic"),
    "duration_sec": df["duration_seconds"],
    "communication_type": df["call_type"]
})

calls.to_csv(
    OUT_DIR / "relationships_calls.csv",
    index=False
)

print(f"Calls created: {len(calls)}")