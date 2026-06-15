"""
ingest/vector_store.py
──────────────────────
Manages the ChromaDB vector store: initialise, upsert, query.
Uses OpenAI text-embedding-3-small via LangChain's OpenAIEmbeddings.

Deduplication strategy: we compute a chunk_id from (file_hash + chunk_index)
and use it as the ChromaDB document id.  Re-ingesting the same file is a
no-op because Chroma's add() is idempotent when ids are supplied.
"""

from __future__ import annotations

import hashlib
from typing import List, Optional

import chromadb
from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings
from loguru import logger

from config.settings import get_settings


def _make_chunk_id(doc: Document) -> str:
    """Stable ID from file hash + chunk index."""
    file_hash = doc.metadata.get("file_hash", "unknown")
    chunk_idx = doc.metadata.get("chunk_index", 0)
    raw = f"{file_hash}::{chunk_idx}"
    return hashlib.sha256(raw.encode()).hexdigest()[:32]


def get_embeddings() -> OpenAIEmbeddings:
    cfg = get_settings()
    return OpenAIEmbeddings(
        model=cfg.embedding_model,
        openai_api_key=cfg.openai_api_key,
    )


def get_vector_store() -> Chroma:
    """Return (or create) the persistent Chroma vector store."""
    cfg = get_settings()
    client = chromadb.PersistentClient(path=str(cfg.chroma_persist_path))
    store = Chroma(
        client=client,
        collection_name=cfg.chroma_collection,
        embedding_function=get_embeddings(),
    )
    return store


def ingest_chunks(chunks: List[Document]) -> int:
    """
    Embed and upsert chunks into ChromaDB.

    Returns the number of *new* chunks actually added (deduplicated).
    """
    store = get_vector_store()

    # Generate stable ids and check which already exist
    ids = [_make_chunk_id(c) for c in chunks]
    existing = set(store.get(ids=ids)["ids"])

    new_chunks = [c for c, cid in zip(chunks, ids) if cid not in existing]
    new_ids = [cid for cid in ids if cid not in existing]

    if not new_chunks:
        logger.info("All chunks already exist in vector store — skipping.")
        return 0

    store.add_documents(documents=new_chunks, ids=new_ids)
    logger.info(f"Ingested {len(new_chunks)} new chunks (skipped {len(chunks) - len(new_chunks)} duplicates).")
    return len(new_chunks)


def get_retriever(
    search_type: str = "mmr",
    k: int | None = None,
    fetch_k: int | None = None,
):
    """
    Return a LangChain retriever configured for MMR diversity search.

    MMR (Maximal Marginal Relevance) balances relevance with diversity,
    reducing redundant chunks in the context window.
    """
    cfg = get_settings()
    store = get_vector_store()
    return store.as_retriever(
        search_type=search_type,
        search_kwargs={
            "k": k or cfg.mmr_k,
            "fetch_k": fetch_k or cfg.mmr_fetch_k,
            "lambda_mult": 0.6,   # 0 = max diversity, 1 = max relevance
        },
    )


def similarity_search_with_scores(
    query: str,
    k: int = 10,
) -> List[tuple[Document, float]]:
    """Return (doc, cosine_similarity) pairs for re-ranking."""
    store = get_vector_store()
    return store.similarity_search_with_relevance_scores(query, k=k)


def collection_stats() -> dict:
    """Return basic stats about the current collection."""
    cfg = get_settings()
    client = chromadb.PersistentClient(path=str(cfg.chroma_persist_path))
    try:
        col = client.get_collection(cfg.chroma_collection)
        count = col.count()
        sources = set()
        results = col.get(include=["metadatas"])
        for meta in results.get("metadatas", []):
            if meta and "source" in meta:
                sources.add(meta["source"])
        return {"total_chunks": count, "unique_sources": list(sources)}
    except Exception:
        return {"total_chunks": 0, "unique_sources": []}
