import subprocess
import sys
import os
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent

scripts = [
    "inventory.py",
    "inventory_summary.py",
    "normalize_persons.py",
    "normalize_phones.py",
    "normalize_vehicles.py",
    "normalize_locations.py",
    "normalize_organizations.py",
    "normalize_accounts.py",
    "normalize_firs.py",
    "normalize_calls.py",
    "normalize_emails.py",
    "normalize_transactions.py",
    "normalize_visits.py",
    "normalize_works_for.py",
    "combine_relationships.py",
    "validate_relationships.py",
]


pipeline_ok = True

for script in scripts:

    print()
    print("=" * 60)
    print(f"Running {script}")
    print("=" * 60)

    result = subprocess.run(
            [sys.executable, str(PROJECT_ROOT / "scripts" / script)],
            cwd=PROJECT_ROOT,
            env={
              **__import__("os").environ,
              "PYTHONPATH": str(PROJECT_ROOT),
            },
    )

    if result.returncode != 0:

        print(
            f"Pipeline stopped at {script}"
        )
        pipeline_ok = False
        break


if pipeline_ok:
    print()
    print("=" * 60)
    print("Loading processed data into Neo4j")
    print("=" * 60)

    result = subprocess.run(
        [sys.executable, "-m", "src.graph.run_ingestion"],
        cwd=PROJECT_ROOT,
        env={
            **os.environ,
            "PYTHONPATH": str(PROJECT_ROOT),
        },
    )
    pipeline_ok = result.returncode == 0


if not pipeline_ok:
    raise SystemExit(1)