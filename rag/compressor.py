"""
rag/compressor.py
─────────────────
Two-stage context refinement:

1. Relevance re-ranking  — score each retrieved chunk against the query
   using a cross-encoder (sentence-transformers/cross-encoder/ms-marco-MiniLM-L-6-v2).
   This is a lighter, faster model than the bi-encoder used for retrieval, but
   it sees (query, passage) pairs so it produces much more accurate scores.

2. LLMLingua-style compression — after re-ranking, we prompt the LLM to
   extract only the sentences genuinely relevant to the question.  This
   dramatically reduces context tokens and improves answer focus.

Design decision: We cap compression at MAX_COMPRESSED_CHARS to avoid
pathological cases where the compressor strips everything useful.
"""

from __future__ import annotations

from typing import List, Tuple

from langchain_core.documents import Document
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from loguru import logger

from config.llm_factory import get_llm
from config.settings import get_settings

# ── Cross-encoder re-ranker ───────────────────────────────────────────────────
try:
    from sentence_transformers import CrossEncoder

    _CE_MODEL = "cross-encoder/ms-marco-MiniLM-L-6-v2"
    _cross_encoder: CrossEncoder | None = None


    def _get_cross_encoder() -> CrossEncoder:
        global _cross_encoder
        if _cross_encoder is None:
            logger.info(f"Loading cross-encoder: {_CE_MODEL}")
            _cross_encoder = CrossEncoder(_CE_MODEL)
        return _cross_encoder

except ImportError:
    _get_cross_encoder = None  # type: ignore
    logger.warning("sentence-transformers not installed — re-ranking disabled.")


def rerank_documents(
    query: str,
    docs: List[Document],
    top_k: int | None = None,
) -> List[Tuple[Document, float]]:
    """
    Re-rank docs by cross-encoder relevance.

    Returns list of (Document, score) sorted descending.
    Falls back to input order if cross-encoder is unavailable.
    """
    cfg = get_settings()
    k = top_k or cfg.mmr_k

    if not docs:
        return []

    if _get_cross_encoder is None:
        logger.warning("Re-ranking skipped (sentence-transformers missing).")
        return [(d, 1.0) for d in docs[:k]]

    ce = _get_cross_encoder()
    pairs = [(query, doc.page_content) for doc in docs]
    scores = ce.predict(pairs).tolist()
    ranked = sorted(zip(docs, scores), key=lambda x: x[1], reverse=True)
    logger.debug(
        f"Re-ranked {len(docs)} chunks → top score {ranked[0][1]:.3f} | "
        f"bottom score {ranked[-1][1]:.3f}"
    )
    return ranked[:k]


# ── LLMLingua-style compressor ────────────────────────────────────────────────
MAX_COMPRESSED_CHARS = 3000

_COMPRESS_PROMPT = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            (
                "You are a precision context extractor. "
                "Given a question and a set of retrieved passages, "
                "extract ONLY the sentences that are directly relevant to answering the question. "
                "Preserve the original wording. Remove redundancy. "
                "Output plain text only, no bullet points, no commentary."
            ),
        ),
        (
            "human",
            "QUESTION: {question}\n\nPASSAGES:\n{context}\n\nExtracted relevant sentences:",
        ),
    ]
)


def compress_context(query: str, docs: List[Document]) -> str:
    """
    Compress retrieved context using LLM extraction.

    1. Join chunks into a single block.
    2. Ask the LLM to keep only sentences relevant to the query.
    3. Return compressed string (capped at MAX_COMPRESSED_CHARS).
    """
    if not docs:
        return ""

    raw_context = "\n\n---\n\n".join(
        f"[Source: {d.metadata.get('source', '?')}]\n{d.page_content}" for d in docs
    )

    llm = get_llm(temperature=0.0, max_tokens=1000)
    chain = _COMPRESS_PROMPT | llm | StrOutputParser()
    compressed = chain.invoke({"question": query, "context": raw_context})
    compressed = compressed[:MAX_COMPRESSED_CHARS]
    logger.debug(
        f"Context: {len(raw_context)} → {len(compressed)} chars after compression."
    )
    return compressed
