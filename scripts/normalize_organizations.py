from pathlib import Path
import pandas as pd

from src.data_paths import resolve_processed_dir, resolve_raw_dir


RAW_DIR = resolve_raw_dir()
OUT_DIR = resolve_processed_dir()

df = pd.read_csv(
    RAW_DIR / "synthetic_organizations.csv"
)

organizations = df.copy()
organizations["source"] = df.get("data_provenance", "synthetic")

organizations = organizations.drop_duplicates(
    subset=["organization_id"]
)

organizations.to_csv(
    OUT_DIR / "organizations.csv",
    index=False
)

print(
    f"Organizations created: {len(organizations)}"
)