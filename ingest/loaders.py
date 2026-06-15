"""
ingest/loaders.py
─────────────────
Unified document loading for PDF, DOCX, and TXT files.
Returns a list of LangChain Document objects with rich metadata.
"""

from __future__ import annotations

import hashlib
from pathlib import Path
from typing import List

from langchain_core.documents import Document
from langchain_community.document_loaders import (
    PyPDFLoader,
    UnstructuredWordDocumentLoader,
    TextLoader,
)
from loguru import logger


SUPPORTED_EXTENSIONS = {".pdf", ".docx", ".doc", ".txt", ".md"}


def _file_hash(path: Path) -> str:
    """MD5 hash of file contents — used for deduplication."""
    h = hashlib.md5()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def load_document(file_path: str | Path) -> List[Document]:
    """
    Load a single document from disk.

    Returns a list of Document objects (one per page for PDFs, one per
    paragraph for DOCX, one per file for TXT).  Each Document carries
    source, file_type, and file_hash in its metadata.
    """
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {path}")

    ext = path.suffix.lower()
    if ext not in SUPPORTED_EXTENSIONS:
        raise ValueError(
            f"Unsupported file type '{ext}'. "
            f"Supported: {SUPPORTED_EXTENSIONS}"
        )

    logger.info(f"Loading document: {path.name} ({ext})")
    file_hash = _file_hash(path)

    if ext == ".pdf":
        loader = PyPDFLoader(str(path))
    elif ext in {".docx", ".doc"}:
        loader = UnstructuredWordDocumentLoader(str(path))
    else:  # .txt or .md
        loader = TextLoader(str(path), encoding="utf-8")

    docs = loader.load()

    # Enrich metadata on every page/chunk
    for doc in docs:
        doc.metadata.update(
            {
                "source": path.name,
                "file_path": str(path.resolve()),
                "file_type": ext.lstrip("."),
                "file_hash": file_hash,
            }
        )

    logger.info(f"  → {len(docs)} document sections loaded from {path.name}")
    return docs


def load_directory(dir_path: str | Path) -> List[Document]:
    """
    Recursively load all supported documents from a directory.
    """
    dir_path = Path(dir_path)
    all_docs: List[Document] = []
    files = [
        f
        for f in dir_path.rglob("*")
        if f.is_file() and f.suffix.lower() in SUPPORTED_EXTENSIONS
    ]

    if not files:
        logger.warning(f"No supported files found in {dir_path}")
        return []

    for file in files:
        try:
            docs = load_document(file)
            all_docs.extend(docs)
        except Exception as e:
            logger.error(f"Failed to load {file}: {e}")

    logger.info(f"Total sections loaded from directory: {len(all_docs)}")
    return all_docs
