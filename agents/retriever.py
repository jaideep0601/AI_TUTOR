"""
agents/retriever.py
───────────────────
Retriever agent — wraps the full advanced RAG pipeline (HyDE + MMR + rerank
+ compress) into a LangGraph node.

It also applies the teaching plan from the Planner and the Bloom's level to
shape the generated answer's depth and framing.
"""

from __future__ import annotations

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from loguru import logger

from agents.state import TutorState
from config.llm_factory import get_llm
from rag.pipeline import retrieve_and_rerank, rag_answer
from rag.compressor import compress_context

_SOCRATIC_ANSWER_PROMPT = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            (
                "You are Socrates, an AI tutor. Your persona:\n"
                "  • Guide with questions, not just answers.\n"
                "  • Calibrate depth to Bloom's level: {bloom}.\n"
                "  • Follow this teaching plan if set: {plan}\n"
                "  • Cite sources as [Source: filename].\n"
                "  • End every Explain-mode response with one Socratic follow-up question.\n"
                "Use ONLY the context below. If the answer isn't there, say so.\n"
            ),
        ),
        (
            "human",
            "CONTEXT:\n{context}\n\nSTUDENT QUESTION: {question}\n\nTutor response:",
        ),
    ]
)


def retriever_node(state: TutorState) -> TutorState:
    """
    LangGraph node: Retriever.

    Runs advanced RAG and stores results in state.
    """
    question = state.get("question", "")
    intent = state.get("intent", "Ask")
    bloom = state.get("bloom_level", "Remember")
    plan = state.get("plan", "")

    logger.info(f"[Retriever] question={question[:60]}…  bloom={bloom}")

    # ── Retrieval + re-ranking ────────────────────────────────────────────────
    docs = retrieve_and_rerank(question, use_hyde=True)

    if not docs:
        answer = (
            "I couldn't find relevant information in the knowledge base. "
            "Please upload documents on this topic first."
        )
        return {
            **state,
            "retrieved_docs": [],
            "compressed_context": "",
            "sources": [],
            "answer": answer,
        }

    # ── Compression ──────────────────────────────────────────────────────────
    context = compress_context(question, docs)
    sources = list({d.metadata.get("source", "unknown") for d in docs})

    # ── Answer generation with Socratic persona ───────────────────────────────
    llm = get_llm(temperature=0.4)
    chain = _SOCRATIC_ANSWER_PROMPT | llm | StrOutputParser()
    answer = chain.invoke(
        {
            "context": context,
            "question": question,
            "bloom": bloom,
            "plan": plan or "No specific plan — follow the natural flow.",
        }
    )

    logger.info(f"[Retriever] answer={len(answer)} chars  sources={sources}")
    return {
        **state,
        "retrieved_docs": docs,
        "compressed_context": context,
        "sources": sources,
        "answer": answer,
    }
