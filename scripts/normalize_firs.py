from pathlib import Path
import pandas as pd

from src.data_paths import resolve_processed_dir, resolve_raw_dir


RAW_DIR = resolve_raw_dir()
OUT_DIR = resolve_processed_dir()

df = pd.read_csv(
    RAW_DIR / "source_fir_records_cleaned.csv"
)

firs = pd.DataFrame({
    "fir_id": df["fir_id"],
    "record_uid": df["fir_id"],
    "image_id": pd.NA,
    "station_id": df["police_station"],
    "date": pd.to_datetime(
        df["year"],
        format="%Y",
        errors="coerce"
    ),
    "year": df["year"],
    "crime_type": df["crime_type"],
    "acts_list": df["summary"],
    "sections_list": df["statute"],
    "completeness_pct": pd.NA,
    "confidence": df["confidence"],
    "source": df.get("data_provenance", "fir")
})

firs.to_csv(
    OUT_DIR / "firs.csv",
    index=False
)

print(f"FIRs created: {len(firs)}")