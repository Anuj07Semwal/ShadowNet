from pathlib import Path
import pandas as pd

from src.data_paths import resolve_processed_dir, resolve_raw_dir


RAW_DIR = resolve_raw_dir()
OUT_DIR = resolve_processed_dir()

df = pd.read_csv(
    RAW_DIR / "synthetic_accounts.csv"
)

accounts = df.copy()
accounts["source"] = df.get("data_provenance", "synthetic")

accounts = accounts.drop_duplicates(
    subset=["account_id"]
)

accounts.to_csv(
    OUT_DIR / "accounts.csv",
    index=False
)