import sqlite3
import os
import hashlib
from typing import Optional
from datetime import datetime

from src.data_paths import resolve_processed_dir

DB_PATH = os.getenv("CNAS_REGISTRY_DB") or str(resolve_processed_dir() / "registry.db")


def _connect():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    return conn


def init_db():
    conn = _connect()
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS documents (
            document_id TEXT PRIMARY KEY,
            content_hash TEXT,
            source_path TEXT,
            status TEXT,
            ingested_at TEXT
        )
        """
    )

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS chunks (
            document_id TEXT,
            chunk_id TEXT,
            vector_id TEXT,
            content_hash TEXT,
            PRIMARY KEY (document_id, chunk_id)
        )
        """
    )

    conn.commit()
    conn.close()


def compute_hash(text: bytes) -> str:
    return hashlib.sha256(text).hexdigest()


def get_document(document_id: str) -> Optional[dict]:
    conn = _connect()
    cur = conn.cursor()
    cur.execute("SELECT document_id, content_hash, source_path, status, ingested_at FROM documents WHERE document_id = ?", (document_id,))
    row = cur.fetchone()
    conn.close()
    if not row:
        return None
    return {
        "document_id": row[0],
        "content_hash": row[1],
        "source_path": row[2],
        "status": row[3],
        "ingested_at": row[4]
    }


def upsert_document(document_id: str, content_hash: str, source_path: str, status: str = "processed"):
    conn = _connect()
    cur = conn.cursor()
    now = datetime.utcnow().isoformat()
    cur.execute(
        "REPLACE INTO documents (document_id, content_hash, source_path, status, ingested_at) VALUES (?, ?, ?, ?, ?)",
        (document_id, content_hash, source_path, status, now)
    )
    conn.commit()
    conn.close()


def upsert_chunk(document_id: str, chunk_id: str, vector_id: str, content_hash: str):
    conn = _connect()
    cur = conn.cursor()
    cur.execute(
        "REPLACE INTO chunks (document_id, chunk_id, vector_id, content_hash) VALUES (?, ?, ?, ?)",
        (document_id, chunk_id, vector_id, content_hash)
    )
    conn.commit()
    conn.close()


def list_chunks(document_id: str):
    conn = _connect()
    cur = conn.cursor()
    cur.execute("SELECT chunk_id, vector_id, content_hash FROM chunks WHERE document_id = ?", (document_id,))
    rows = cur.fetchall()
    conn.close()
    return [
        {"chunk_id": r[0], "vector_id": r[1], "content_hash": r[2]} for r in rows
    ]
