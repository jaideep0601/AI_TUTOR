"""
rag/hyde.py
───────────
HyDE — Hypothetical Document Embeddings (Gao et al., 2022).

Instead of embedding the raw user query (which may be short / ambiguous),
we ask the LLM to generate a *hypothetical* answer to the query, then embed
that synthetic passage.  The resulting embedding sits much closer in the
semantic space to real answer documents, improving retrieval recall.

Design decision: We keep the hypothetical document short (≤150 words) to
stay within the embedding model's sweet spot and avoid hallucinated noise
dominating the vector.
"""

from __future__ import annotations

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from loguru import logger

from config.llm_factory import get_llm

_HYDE_PROMPT = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            (
                "You are a knowledgeable tutor. Write a concise, factual passage "
                "(≤150 words) that would directly answer the student's question. "
                "Do NOT say 'I don't know'. Produce a plausible, educational answer."
            ),
        ),
        ("human", "{question}"),
    ]
)


def expand_query_with_hyde(question: str) -> str:
    """
    Generate a hypothetical document for the question and return it.

    This string is used *instead of* the raw question for the embedding lookup.
    The original question is still passed to the answer-generation chain.
    """
    llm = get_llm(temperature=0.4, max_tokens=300)
    chain = _HYDE_PROMPT | llm | StrOutputParser()
    hypothetical = chain.invoke({"question": question})
    logger.debug(f"HyDE expansion ({len(hypothetical)} chars) for: {question[:60]}…")
    return hypothetical
