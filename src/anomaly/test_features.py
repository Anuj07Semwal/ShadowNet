from pathlib import Path

import pandas as pd

from src.anomaly.feature_engineering import (
    clean_transactions,
    create_transaction_features,
)


DATA_PATH = Path(
    str(resolve_processed_dir() / "relationships_transactions.csv")
)


def main():

    print("=" * 70)
    print("LOADING TRANSACTION DATA")
    print("=" * 70)

    print(f"File: {DATA_PATH}")

    df = pd.read_csv(DATA_PATH)

    print(f"Rows: {len(df):,}")
    print(f"Columns: {len(df.columns)}")

    print("\nColumns:")

    for column in df.columns:
        print(f"  - {column}")

    print("\n" + "=" * 70)
    print("CLEANING TRANSACTIONS")
    print("=" * 70)

    df = clean_transactions(df)

    print(
        f"✓ Clean transactions: {len(df):,}"
    )

    print("\n" + "=" * 70)
    print("CREATING FEATURES")
    print("=" * 70)

    df = create_transaction_features(df)

    print(
        f"✓ Feature dataframe: "
        f"{len(df):,} rows"
    )

    print("\nFeature columns:")

    for column in df.columns:
        print(f"  - {column}")

    print("\nSample:")

    print(
        df[
            [
                "relationship_id",
                "source_id",
                "target_id",
                "amount",
                "amount_zscore",
                "source_transaction_count",
                "source_mean_amount",
                "source_amount_ratio",
                "hour",
                "is_night",
            ]
        ].head(10).to_string(index=False)
    )

    print("\n✓ Feature engineering successful")


if __name__ == "__main__":
    main()