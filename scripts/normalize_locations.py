from pathlib import Path
import pandas as pd

from src.data_paths import resolve_processed_dir, resolve_raw_dir


RAW_DIR = resolve_raw_dir()
OUT_DIR = resolve_processed_dir()

df = pd.read_csv(
    RAW_DIR / "synthetic_locations.csv"
)

locations = df.copy()
locations["source"] = df.get("data_provenance", "synthetic")

locations = locations.drop_duplicates(
    subset=["location_id"]
)

locations.to_csv(
    OUT_DIR / "locations.csv",
    index=False
)

print(f"Locations created: {len(locations)}")