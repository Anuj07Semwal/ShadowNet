from pathlib import Path
import pandas as pd

from src.data_paths import resolve_processed_dir, resolve_raw_dir


RAW_DIR = resolve_raw_dir()
OUT_DIR = resolve_processed_dir()

OUT_DIR.mkdir(parents=True, exist_ok=True)


def normalize_synthetic():

    df = pd.read_csv(
        RAW_DIR / "synthetic_persons.csv"
    )

    result = df.copy()
    result["community_id"] = pd.NA
    result["source"] = df.get("data_provenance", "synthetic")
    result["source_role"] = df.get("source_role", pd.NA)
    result["confidence"] = 1.0

    return result


def normalize_fir():

    df = pd.read_csv(
        RAW_DIR / "source_persons_pseudonymized.csv"
    )

    result = df.copy()
    result["community_id"] = pd.NA
    result["source"] = df.get("data_provenance", "fir")
    result["source_role"] = df.get("source_role", pd.NA)
    result["confidence"] = df.get("source_avg_confidence", 1.0)

    return result


def main():

    synthetic = normalize_synthetic()
    fir = normalize_fir()

    persons = pd.concat(
        [synthetic, fir],
        ignore_index=True
    )

    mapping_path = OUT_DIR / "person_name_mapping.csv"
    if mapping_path.exists():
        mapping = pd.read_csv(
            mapping_path,
            usecols=["person_id", "full_name"],
        ).drop_duplicates(subset=["person_id"])
        persons = persons.merge(mapping, on="person_id", how="left")
        persons["name"] = persons["full_name"].fillna(persons.get("name"))
        persons["name"] = persons["name"].fillna(persons["person_id"])
        persons = persons.drop(columns=["full_name"])
    else:
        persons["name"] = persons["person_id"]

    # Validate IDs
    persons = persons.drop_duplicates(
        subset=["person_id"]
    )

    persons.to_csv(
        OUT_DIR / "persons.csv",
        index=False
    )

    print(f"Persons created: {len(persons)}")


if __name__ == "__main__":
    main()