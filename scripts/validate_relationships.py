from pathlib import Path
import pandas as pd

from src.data_paths import resolve_processed_dir


DIR = resolve_processed_dir()


def main():

    persons = pd.read_csv(
        DIR / "persons.csv"
    )

    phones = pd.read_csv(
        DIR / "phones.csv"
    )

    vehicles = pd.read_csv(
        DIR / "vehicles.csv"
    )

    locations = pd.read_csv(
        DIR / "locations.csv"
    )

    organizations = pd.read_csv(
        DIR / "organizations.csv"
    )

    accounts = pd.read_csv(
        DIR / "accounts.csv"
    )

    relationships = pd.read_csv(
        DIR / "relationships.csv"
    )

    valid_ids = set()

    valid_ids.update(
        persons["person_id"].astype(str)
    )

    valid_ids.update(
        phones["phone_id"].astype(str)
    )

    valid_ids.update(
        vehicles["vehicle_id"].astype(str)
    )

    valid_ids.update(
        locations["location_id"].astype(str)
    )

    valid_ids.update(
        organizations["organization_id"].astype(str)
    )

    valid_ids.update(
        accounts["account_id"].astype(str)
    )

    relationships["source_exists"] = (
        relationships["source_id"]
        .astype(str)
        .isin(valid_ids)
    )

    relationships["target_exists"] = (
        relationships["target_id"]
        .astype(str)
        .isin(valid_ids)
    )

    invalid_source = (
        ~relationships["source_exists"]
    ).sum()

    invalid_target = (
        ~relationships["target_exists"]
    ).sum()

    print("Relationship validation")
    print("-----------------------")
    print(
        f"Total: {len(relationships)}"
    )
    print(
        f"Invalid source IDs: {invalid_source}"
    )
    print(
        f"Invalid target IDs: {invalid_target}"
    )

    if invalid_source == 0 and invalid_target == 0:
        print()
        print("✓ All relationship IDs resolve.")
    else:
        print()
        print("⚠ Invalid relationships found.")

        bad = relationships[
            (~relationships["source_exists"])
            | (~relationships["target_exists"])
        ]

        bad.to_csv(
            DIR / "invalid_relationships.csv",
            index=False
        )


if __name__ == "__main__":
    main()