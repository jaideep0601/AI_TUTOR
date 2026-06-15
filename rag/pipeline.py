"""
rag/pipeline.py
───────────────
Orchestrates the full advanced RAG pipeline:

  query → HyDE expansion → MMR retrieval → cross-encoder re-rank
        → LLMLingua compression → answer generation

Each stage is independently importable so agents can call them à la carte.
"""

from __future__ import annotations

from typing import List

from langchain_core.documents import Document
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from loguru import logger

from config.llm_factory import get_llm
from config.settings import get_settings
from ingest.vector_store import get_retriever, similarity_search_with_scores
from rag.hyde import expand_query_with_hyde
from rag.compressor import rerank_documents, compress_context


# ── Answer generation prompt ─────────────────────────────────────────────────
_ANSWER_PROMPT = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            (
                "You are Socrates, an AI tutor who guides students to understanding "
                "through clear explanation and gentle questioning. "
                "Use ONLY the provided context to answer. "
                "If the context doesn't contain the answer, say so honestly. "
                "Cite the source document where possible."
            ),
        ),
        (
            "human",
            "CONTEXT:\n{context}\n\nSTUDENT QUESTION: {question}\n\nTutor answer:",
        ),
    ]
)


def retrieve(
    query: str,
    use_hyde: bool = True,
) -> List[Document]:
    """
    Retrieve relevant chunks using MMR (optionally with HyDE expansion).
    """
    retrieval_query = expand_query_with_hyde(query) if use_hyde else query
    retriever = get_retriever()
    docs = retriever.invoke(retrieval_query)
    logger.info(f"Retrieved {len(docs)} chunks for query: {query[:60]}…")
    return docs


def retrieve_and_rerank(
    query: str,
    use_hyde: bool = True,
) -> List[Document]:
    """
    Retrieve with MMR then re-rank with cross-encoder.
    Returns only the top-k most relevant docs.
    """
    cfg = get_settings()
    # Fetch more candidates for re-ranking (fetch_k from settings)
    raw_results = similarity_search_with_scores(
        expand_query_with_hyde(query) if use_hyde else query,
        k=cfg.mmr_fetch_k,
    )
    docs = [doc for doc, score in raw_results if score >= cfg.relevance_threshold]
    logger.info(
        f"{len(raw_results)} candidates → {len(docs)} above threshold "
        f"({cfg.relevance_threshold})"
    )
    ranked = rerank_documents(query, docs, top_k=cfg.mmr_k)
    return [doc for doc, _ in ranked]


def rag_answer(
    question: str,
    use_hyde: bool = True,
    compress: bool = True,
) -> dict:
    """
    Full RAG pipeline: retrieve → (optionally compress) → answer.

    Returns:
      {answer, sources, context_used}
    """
    docs = retrieve_and_rerank(question, use_hyde=use_hyde)

    if not docs:
        return {
            "answer": (
                "I couldn't find relevant information in the knowledge base. "
                "Please upload documents covering this topic."
            ),
            "sources": [],
            "context_used": "",
        }

    context = compress_context(question, docs) if compress else "\n\n".join(
        d.page_content for d in docs
    )

    llm = get_llm(streaming=False)
    chain = _ANSWER_PROMPT | llm | StrOutputParser()
    answer = chain.invoke({"context": context, "question": question})

    sources = list(
        {d.metadata.get("source", "unknown") for d in docs}
    )

    return {
        "answer": answer,
        "sources": sources,
        "context_used": context,
        "docs": docs,
    }
