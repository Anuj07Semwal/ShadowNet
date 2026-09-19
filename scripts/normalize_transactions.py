from pathlib import Path
import pandas as pd

from src.data_paths import resolve_processed_dir, resolve_raw_dir


RAW_DIR = resolve_raw_dir()
OUT_DIR = resolve_processed_dir()

df = pd.read_csv(
    RAW_DIR / "synthetic_transactions.csv"
)

transactions = pd.DataFrame({
    "relationship_id": df["transaction_id"],
    "source_id": df["sender_account_id"],
    "source_type": "Account",
    "relationship": "TRANSFERRED_MONEY",
    "target_id": df["receiver_account_id"],
    "target_type": "Account",
    "timestamp": df["timestamp"],
    "source_document": pd.NA,
    "confidence": 1.0,
    "provenance": df.get("data_provenance", "synthetic"),
    "amount": df["amount"],
    "channel": df["transaction_type"],
    "is_anomaly": df.get("is_injected_anomaly", False),
    "anomaly_type": df.get("anomaly_type", pd.NA)
})

transactions.to_csv(
    OUT_DIR / "relationships_transactions.csv",
    index=False
)