from pathlib import Path
import pandas as pd

from src.data_paths import resolve_processed_dir


PROCESSED_DIR = resolve_processed_dir()


def main():

    files = [
        "relationships_calls.csv",
        "relationships_emails.csv",
        "relationships_transactions.csv",
        "relationships_visits.csv"
    ]

    frames = []

    for file in files:

        path = PROCESSED_DIR / file

        if path.exists():

            df = pd.read_csv(path)

            frames.append(df)

            print(
                f"Loaded {file}: {len(df)}"
            )

    relationships = pd.concat(
        frames,
        ignore_index=True,
        sort=False
    )

    relationships.to_csv(
        PROCESSED_DIR / "relationships.csv",
        index=False
    )

    print()
    print(
        f"Total relationships: "
        f"{len(relationships)}"
    )


if __name__ == "__main__":
    main()