"""
ingest/pipeline.py
──────────────────
High-level ingestion pipeline:  file → load → chunk → embed → store.
This is what the Streamlit UI and `make ingest` both call.
"""

from __future__ import annotations

import tempfile
from pathlib import Path
from typing import List

from loguru import logger

from ingest.loaders import load_document
from ingest.chunker import chunk_documents
from ingest.vector_store import ingest_chunks, collection_stats


def ingest_file(file_path: str | Path) -> dict:
    """
    Full pipeline for a single file.

    Returns a summary dict:
      {source, sections_loaded, chunks_created, chunks_ingested}
    """
    path = Path(file_path)
    docs = load_document(path)
    chunks = chunk_documents(docs)
    ingested = ingest_chunks(chunks)

    result = {
        "source": path.name,
        "sections_loaded": len(docs),
        "chunks_created": len(chunks),
        "chunks_ingested": ingested,
    }
    logger.info(f"Ingestion summary: {result}")
    return result


def ingest_uploaded_bytes(
    file_bytes: bytes, filename: str
) -> dict:
    """
    Ingest a file supplied as raw bytes (e.g. from Streamlit uploader).
    Writes to a temporary file so the loaders can work with a real path.
    """
    suffix = Path(filename).suffix
    with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
        tmp.write(file_bytes)
        tmp_path = Path(tmp.name)

    try:
        return ingest_file(tmp_path)
    finally:
        tmp_path.unlink(missing_ok=True)


def ingest_directory(dir_path: str | Path) -> List[dict]:
    """Ingest every supported document in a directory."""
    from ingest.loaders import SUPPORTED_EXTENSIONS

    dir_path = Path(dir_path)
    results = []
    for f in dir_path.rglob("*"):
        if f.is_file() and f.suffix.lower() in SUPPORTED_EXTENSIONS:
            try:
                results.append(ingest_file(f))
            except Exception as e:
                logger.error(f"Failed to ingest {f}: {e}")
    return results


def get_kb_stats() -> dict:
    """Quick stats about the current knowledge base."""
    return collection_stats()
