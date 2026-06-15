"""
ingest/chunker.py
─────────────────
Splits raw Document objects into overlapping chunks using
RecursiveCharacterTextSplitter.  Chunk metadata is preserved and
augmented with chunk-level info (index, total, char_count).
"""

from __future__ import annotations

from typing import List

from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from loguru import logger

from config.settings import get_settings


def chunk_documents(
    documents: List[Document],
    chunk_size: int | None = None,
    chunk_overlap: int | None = None,
) -> List[Document]:
    """
    Split documents into chunks.

    Args:
        documents:     List of loaded Document objects.
        chunk_size:    Characters per chunk (defaults to settings).
        chunk_overlap: Overlap between consecutive chunks (defaults to settings).

    Returns:
        List of chunked Document objects with updated metadata.
    """
    cfg = get_settings()
    size = chunk_size or cfg.chunk_size
    overlap = chunk_overlap or cfg.chunk_overlap

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=size,
        chunk_overlap=overlap,
        length_function=len,
        separators=["\n\n", "\n", ". ", "! ", "? ", " ", ""],
        is_separator_regex=False,
    )

    chunks = splitter.split_documents(documents)

    # Augment metadata with per-source chunk index so we can cite precisely
    source_counter: dict[str, int] = {}
    for chunk in chunks:
        src = chunk.metadata.get("source", "unknown")
        idx = source_counter.get(src, 0)
        source_counter[src] = idx + 1
        chunk.metadata["chunk_index"] = idx
        chunk.metadata["char_count"] = len(chunk.page_content)

    # Back-fill total_chunks now that we know the counts
    for chunk in chunks:
        src = chunk.metadata.get("source", "unknown")
        chunk.metadata["total_chunks"] = source_counter[src]

    logger.info(
        f"Chunking complete: {len(documents)} docs → {len(chunks)} chunks "
        f"(size={size}, overlap={overlap})"
    )
    return chunks
