from pathlib import Path
import pandas as pd
import json

from src.data_paths import resolve_raw_dir


RAW_DIR = resolve_raw_dir()
REPORT_DIR = Path("data/reports")

REPORT_DIR.mkdir(parents=True, exist_ok=True)


def inspect_csv(file_path):
    try:
        df = pd.read_csv(file_path)

        report = {
            "file": file_path.name,
            "rows": len(df),
            "columns": len(df.columns),
            "column_names": list(df.columns),
            "missing_values": {
                col: int(df[col].isna().sum())
                for col in df.columns
            },
            "duplicate_rows": int(df.duplicated().sum()),
            "dtypes": {
                col: str(df[col].dtype)
                for col in df.columns
            }
        }

        # Check duplicate IDs where possible
        id_columns = [
            col for col in df.columns
            if col.endswith("_id") or col == "id"
        ]

        report["duplicate_ids"] = {}

        for col in id_columns:
            report["duplicate_ids"][col] = int(
                df[col].duplicated().sum()
            )

        return report

    except Exception as e:
        return {
            "file": file_path.name,
            "error": str(e)
        }


def main():

    csv_files = sorted(RAW_DIR.glob("*.csv"))

    print(f"Found {len(csv_files)} CSV files")

    inventory = []

    for file in csv_files:

        print(f"Inspecting: {file.name}")

        result = inspect_csv(file)

        inventory.append(result)

    output_file = REPORT_DIR / "data_inventory.json"

    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(
            inventory,
            f,
            indent=4
        )

    print()
    print("Inventory completed.")
    print(f"Report: {output_file}")


if __name__ == "__main__":
    main()