from pathlib import Path
import pandas as pd

from src.data_paths import resolve_processed_dir, resolve_raw_dir


RAW_DIR = resolve_raw_dir()
OUT_DIR = resolve_processed_dir()

df = pd.read_csv(
    RAW_DIR / "synthetic_phones.csv"
)

phones = df.copy()
phones["source"] = df.get("data_provenance", "synthetic")

phones = phones.drop_duplicates(
    subset=["phone_id"]
)

phones.to_csv(
    OUT_DIR / "phones.csv",
    index=False
)

print(f"Phones created: {len(phones)}")