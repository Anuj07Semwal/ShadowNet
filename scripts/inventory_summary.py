from pathlib import Path
import pandas as pd

from src.data_paths import resolve_raw_dir


RAW_DIR = resolve_raw_dir()


def main():

    rows = []

    for file in sorted(RAW_DIR.glob("*.csv")):

        df = pd.read_csv(file)

        rows.append({
            "file": file.name,
            "rows": len(df),
            "columns": len(df.columns),
            "missing_cells": int(df.isna().sum().sum()),
            "duplicate_rows": int(df.duplicated().sum())
        })

    result = pd.DataFrame(rows)

    print(result.to_string(index=False))

    result.to_csv(
        "data/reports/dataset_summary.csv",
        index=False
    )


if __name__ == "__main__":
    main()