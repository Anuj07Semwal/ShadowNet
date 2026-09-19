from __future__ import annotations

from pathlib import Path


def project_root() -> Path:
    """Return the repository root regardless of the current working directory."""
    candidates = [
        Path(__file__).resolve().parents[1],
        Path.cwd(),
    ]

    for candidate in candidates:
        if (candidate / "pyproject.toml").exists() or (candidate / "src").exists():
            return candidate

    return candidates[0]


def resolve_data_dir() -> Path:
    root = project_root()
    preferred = root / "data"
    if preferred.exists():
        return preferred

    for parent in [root, *root.parents]:
        candidate = parent / "data"
        if candidate.exists():
            return candidate

    return preferred


def resolve_raw_dir() -> Path:
    data_dir = resolve_data_dir()
    candidates = [
        data_dir / "raw" / "CNAS_Prototype_Data",
        data_dir / "documents" / "raw" / "CNAS_Prototype_Data",
        data_dir / "raw",
        data_dir / "documents" / "raw",
        data_dir,
    ]
    for candidate in candidates:
        if candidate.exists():
            return candidate
    return data_dir / "raw"


def resolve_processed_dir() -> Path:
    data_dir = resolve_data_dir()
    candidates = [
        data_dir / "processed",
        data_dir / "documents" / "processed",
    ]
    for candidate in candidates:
        if candidate.exists():
            return candidate
    return data_dir / "processed"


def resolve_document_dir() -> Path:
    data_dir = resolve_data_dir()
    candidates = [
        data_dir / "documents",
        data_dir,
    ]
    for candidate in candidates:
        if candidate.exists():
            return candidate
    return data_dir / "documents"
