from pathlib import Path
import pandas as pd

from src.data_paths import resolve_processed_dir, resolve_raw_dir


RAW_DIR = resolve_raw_dir()
OUT_DIR = resolve_processed_dir()

df = pd.read_csv(
    RAW_DIR / "synthetic_emails.csv"
)

emails = pd.DataFrame({
    "relationship_id": df["email_id"],
    "source_id": df["sender_person_id"],
    "source_type": "Person",
    "relationship": "EMAILED",
    "target_id": df["receiver_person_id"],
    "target_type": "Person",
    "timestamp": df["timestamp"],
    "subject": df.get("subject", pd.NA),
    "direction": df.get("direction", pd.NA),
    "source_document": pd.NA,
    "confidence": 1.0,
    "provenance": df.get("data_provenance", "synthetic")
})

emails.to_csv(
    OUT_DIR / "relationships_emails.csv",
    index=False
)