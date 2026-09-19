from pathlib import Path
import pandas as pd

from src.data_paths import resolve_processed_dir, resolve_raw_dir


RAW_DIR = resolve_raw_dir()
OUT_DIR = resolve_processed_dir()

df = pd.read_csv(
    RAW_DIR / "synthetic_vehicles.csv"
)

vehicles = df.copy()
vehicles["source"] = df.get("data_provenance", "synthetic")

vehicles = vehicles.drop_duplicates(
    subset=["vehicle_id"]
)

vehicles.to_csv(
    OUT_DIR / "vehicles.csv",
    index=False
)

print(f"Vehicles created: {len(vehicles)}")