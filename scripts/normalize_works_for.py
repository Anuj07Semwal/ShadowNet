from pathlib import Path
import pandas as pd

from src.data_paths import resolve_processed_dir, resolve_raw_dir


RAW_FILE = resolve_raw_dir() / "neo4j" / "relationships" / "WORKS_FOR.csv"
OUT_FILE = resolve_processed_dir() / "relationships_works_for.csv"


def main():

    print("=" * 70)
    print("NORMALIZE WORKS_FOR RELATIONSHIPS")
    print("=" * 70)

    if not RAW_FILE.exists():
        if OUT_FILE.exists():
            print(f"Raw WORKS_FOR source missing; keeping existing {OUT_FILE}")
            return
        raise FileNotFoundError(
            f"Missing input file: {RAW_FILE}"
        )

    df = pd.read_csv(RAW_FILE)

    print(f"Input rows: {len(df):,}")
    print(f"Columns: {list(df.columns)}")

    required = [
        "person_id",
        "organization_id",
        "relationship",
    ]

    missing = [
        column
        for column in required
        if column not in df.columns
    ]

    if missing:
        raise ValueError(
            f"Missing columns: {missing}"
        )

    # Keep only the required columns
    df = df[
        [
            "person_id",
            "organization_id",
            "relationship",
        ]
    ].copy()

    # Build the unified relationship schema
    df.insert(
        0,
        "relationship_id",
        [
            f"WORKS_FOR_{i:06d}"
            for i in range(1, len(df) + 1)
        ],
    )

    df.rename(
        columns={
            "person_id": "source_id",
            "organization_id": "target_id",
        },
        inplace=True,
    )

    df.insert(
        2,
        "source_type",
        "Person",
    )

    df.insert(
        5,
        "target_type",
        "Organization",
    )

    df["confidence"] = 1.0
    df["provenance"] = "synthetic"

    # Final unified schema
    df = df[
        [
            "relationship_id",
            "source_id",
            "source_type",
            "relationship",
            "target_id",
            "target_type",
            "confidence",
            "provenance",
        ]
    ]

    OUT_FILE.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    df.to_csv(
        OUT_FILE,
        index=False,
    )

    print()
    print(f"✓ Output: {OUT_FILE}")
    print(f"✓ Relationships: {len(df):,}")
    print()
    print(df.head(5).to_string(index=False))


if __name__ == "__main__":
    main()
