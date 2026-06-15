"""
tests/test_ingest.py
────────────────────
Unit tests for the ingestion pipeline.
Mocks external dependencies (ChromaDB, embeddings).
"""

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

from ingest.chunker import chunk_documents
from langchain_core.documents import Document


class TestChunker:
    def _make_docs(self, text: str, n: int = 1) -> list:
        return [
            Document(
                page_content=text,
                metadata={"source": f"test_{i}.txt", "file_hash": f"hash{i}", "chunk_index": 0},
            )
            for i in range(n)
        ]

    def test_basic_chunking(self):
        long_text = "This is a test sentence. " * 100
        docs = self._make_docs(long_text)
        chunks = chunk_documents(docs, chunk_size=200, chunk_overlap=20)
        assert len(chunks) > 1
        for c in chunks:
            assert len(c.page_content) <= 250  # some tolerance for splitter

    def test_metadata_preserved(self):
        docs = self._make_docs("Hello world. " * 50)
        chunks = chunk_documents(docs, chunk_size=100, chunk_overlap=10)
        for c in chunks:
            assert "source" in c.metadata
            assert "chunk_index" in c.metadata
            assert "total_chunks" in c.metadata

    def test_short_doc_single_chunk(self):
        docs = self._make_docs("Short text.")
        chunks = chunk_documents(docs, chunk_size=512, chunk_overlap=64)
        assert len(chunks) == 1

    def test_multiple_docs(self):
        docs = self._make_docs("Sentence. " * 60, n=3)
        chunks = chunk_documents(docs, chunk_size=100, chunk_overlap=10)
        sources = {c.metadata["source"] for c in chunks}
        assert len(sources) == 3

    def test_chunk_size_respected(self):
        docs = self._make_docs("a " * 1000)
        chunks = chunk_documents(docs, chunk_size=100, chunk_overlap=10)
        for c in chunks:
            assert len(c.page_content) <= 150  # allow splitter buffer

    def test_char_count_metadata(self):
        docs = self._make_docs("Hello world. " * 50)
        chunks = chunk_documents(docs, chunk_size=100, chunk_overlap=10)
        for c in chunks:
            assert c.metadata["char_count"] == len(c.page_content)
