"""
agents/quiz_generator.py
────────────────────────
QuizGenerator agent — generates MCQ and short-answer questions from
retrieved context.  Uses JSON mode for structured, parseable output.

Quiz schema:
{
  "type": "mcq" | "short_answer",
  "question": str,
  "options": ["A. …", "B. …", "C. …", "D. …"],   # MCQ only
  "correct_answer": str,                            # "A" or free text
  "explanation": str,
  "topic": str,
  "bloom_level": str,
  "difficulty": "easy" | "medium" | "hard"
}

Design decision: We generate both MCQ and short-answer in one call and
alternate types to keep sessions varied.  The quiz is stored in state.quiz
so the Evaluator agent can score it later.
"""

from __future__ import annotations

import json
import re
from typing import Any, Dict

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from loguru import logger

from agents.state import TutorState
from config.llm_factory import get_llm
from rag.pipeline import retrieve_and_rerank
from rag.compressor import compress_context

_QUIZ_SYSTEM = """\
You are a quiz author generating educational questions.
Respond ONLY with a single valid JSON object — no markdown, no preamble.

Schema:
{
  "type": "mcq",
  "question": "<question text>",
  "options": ["A. <opt>", "B. <opt>", "C. <opt>", "D. <opt>"],
  "correct_answer": "<A|B|C|D>",
  "explanation": "<why this answer is correct>",
  "topic": "<main topic>",
  "bloom_level": "<Bloom level>",
  "difficulty": "<easy|medium|hard>"
}

OR for short-answer:
{
  "type": "short_answer",
  "question": "<question text>",
  "correct_answer": "<ideal answer>",
  "key_points": ["<point 1>", "<point 2>", "<point 3>"],
  "topic": "<main topic>",
  "bloom_level": "<Bloom level>",
  "difficulty": "<easy|medium|hard>"
}
"""

_QUIZ_PROMPT = ChatPromptTemplate.from_messages(
    [
        ("system", _QUIZ_SYSTEM),
        (
            "human",
            (
                "Generate a {quiz_type} question at {bloom} Bloom's level "
                "based on the following context.\n\n"
                "CONTEXT:\n{context}\n\n"
                "TOPIC FOCUS: {topics}\n\n"
                "JSON:"
            ),
        ),
    ]
)

_QUIZ_TYPES = ["mcq", "short_answer"]


def _clean_json(raw: str) -> str:
    """Strip markdown fences if the model wraps JSON in ```."""
    raw = raw.strip()
    raw = re.sub(r"^```(?:json)?", "", raw, flags=re.I).strip()
    raw = re.sub(r"```$", "", raw).strip()
    return raw


def quiz_generator_node(state: TutorState) -> TutorState:
    """
    LangGraph node: QuizGenerator.
    """
    question = state.get("question", "")
    bloom = state.get("bloom_level", "Understand")
    topics = state.get("topics", [])
    turn = state.get("turn_count", 0)
    weak_topics = state.get("weak_topics", [])

    logger.info(f"[QuizGenerator] bloom={bloom}  topics={topics[:3]}")

    # Prefer weak topics if available (adaptive behaviour)
    focus_topics = weak_topics[:2] if weak_topics else topics[:2]
    focus_str = ", ".join(focus_topics) or question[:60]

    # Retrieve context (may already be in state; if not, re-fetch)
    docs = state.get("retrieved_docs") or retrieve_and_rerank(question or focus_str)
    context = state.get("compressed_context") or compress_context(focus_str, docs or [])

    if not context:
        return {
            **state,
            "answer": "Please upload study materials before requesting a quiz.",
            "quiz": None,
        }

    # Alternate MCQ / short_answer each turn for variety
    quiz_type = _QUIZ_TYPES[turn % 2]

    llm = get_llm(temperature=0.5, max_tokens=600)
    chain = _QUIZ_PROMPT | llm | StrOutputParser()
    raw = chain.invoke(
        {
            "quiz_type": quiz_type,
            "bloom": bloom,
            "context": context,
            "topics": focus_str,
        }
    )

    quiz: Dict[str, Any] = {}
    try:
        quiz = json.loads(_clean_json(raw))
    except json.JSONDecodeError as e:
        logger.error(f"[QuizGenerator] JSON parse failed: {e}\nRaw: {raw[:200]}")
        quiz = {"type": "error", "question": raw, "error": str(e)}

    # Present the question nicely as the answer text
    answer_text = _format_quiz_for_display(quiz)

    return {
        **state,
        "quiz": quiz,
        "answer": answer_text,
        "retrieved_docs": docs or [],
        "compressed_context": context,
    }


def _format_quiz_for_display(quiz: Dict[str, Any]) -> str:
    """Format quiz dict as a readable string for the chat UI."""
    if quiz.get("type") == "error":
        return f"⚠️ Quiz generation failed: {quiz.get('error', 'unknown error')}"

    q_type = quiz.get("type", "?")
    question = quiz.get("question", "")
    difficulty = quiz.get("difficulty", "?")
    bloom = quiz.get("bloom_level", "?")

    header = f"📝 **Quiz** ({q_type.replace('_', ' ').title()} | {difficulty} | {bloom})\n\n"
    body = f"**Q:** {question}\n"

    if q_type == "mcq":
        options = quiz.get("options", [])
        body += "\n".join(options) + "\n"
        body += "\n_Type your answer (A / B / C / D) to be evaluated._"
    else:
        body += "\n_Write your answer below to be evaluated._"

    return header + body
