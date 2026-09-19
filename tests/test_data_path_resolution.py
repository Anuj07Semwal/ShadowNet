from pathlib import Path

from src.data_paths import resolve_data_dir, resolve_processed_dir, resolve_raw_dir


def test_resolve_raw_dir_accepts_current_dataset_layout():
    raw_dir = resolve_raw_dir()
    assert raw_dir.exists(), f"Expected raw dataset directory, got {raw_dir}"
    assert raw_dir.name in {"CNAS_Prototype_Data", "raw"}


def test_resolve_processed_dir_uses_project_data_folder():
    processed_dir = resolve_processed_dir()
    assert processed_dir.exists(), f"Expected processed data directory, got {processed_dir}"
    assert processed_dir.name == "processed"
    assert (processed_dir / "persons.csv").exists()


def test_resolve_data_dir_handles_nested_project_roots():
    project_root = Path(__file__).resolve().parents[1]
    data_dir = resolve_data_dir()
    assert data_dir.exists(), f"Expected data dir, got {data_dir}"
    assert data_dir.is_dir()
    assert data_dir.parent == project_root
