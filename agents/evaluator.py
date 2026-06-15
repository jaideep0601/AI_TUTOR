"""
agents/evaluator.py
───────────────────
Evaluator agent — scores student answers against the active quiz rubric.

Scoring scheme (0–100):
  MCQ:          100 if correct letter, 0 otherwise.
  Short-answer: LLM rubric scorer.  Checks for key-points coverage and
                accuracy, returns a 0–100 integer with feedback.

Weak-topic tracking:
  Any topic where the rolling score drops below WEAK_THRESHOLD (60) is
  added to state.weak_topics.  The Planner checks this list on the next
  turn and can trigger a reteach loop.
"""

from __future__ import annotations

import json
import re
from typing import Any, Dict, List

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from loguru import logger

from agents.state import TutorState
from config.llm_factory import get_llm

WEAK_THRESHOLD = 60.0  # below this → flag as weak topic

_RUBRIC_SYSTEM = """\
You are a strict but fair academic grader.
Evaluate the student's answer against the model answer and key points.
Respond ONLY with valid JSON — no markdown, no commentary.

Schema:
{
  "score": <integer 0-100>,
  "correct_concepts": ["<concept covered>"],
  "missing_concepts": ["<concept missed>"],
  "feedback": "<2-3 sentence constructive feedback>",
  "grade": "<Excellent|Good|Partial|Incorrect>"
}
"""

_RUBRIC_PROMPT = ChatPromptTemplate.from_messages(
    [
        ("system", _RUBRIC_SYSTEM),
        (
            "human",
            (
                "QUESTION: {question}\n"
                "MODEL ANSWER: {model_answer}\n"
                "KEY POINTS: {key_points}\n"
                "STUDENT ANSWER: {student_answer}\n\n"
                "JSON evaluation:"
            ),
        ),
    ]
)


def _clean_json(raw: str) -> str:
    raw = raw.strip()
    raw = re.sub(r"^```(?:json)?", "", raw, flags=re.I).strip()
    return re.sub(r"```$", "", raw).strip()


def _score_mcq(quiz: Dict[str, Any], student_answer: str) -> Dict[str, Any]:
    """Simple letter-match scoring for MCQ."""
    correct = quiz.get("correct_answer", "").strip().upper()[:1]
    given = student_answer.strip().upper()[:1]
    score = 100 if given == correct else 0
    return {
        "score": score,
        "correct_concepts": [quiz.get("question", "")] if score == 100 else [],
        "missing_concepts": [] if score == 100 else [quiz.get("explanation", "")],
        "feedback": (
            f"✅ Correct! {quiz.get('explanation', '')}"
            if score == 100
            else f"❌ Incorrect. The right answer was **{correct}**. {quiz.get('explanation', '')}"
        ),
        "grade": "Excellent" if score == 100 else "Incorrect",
    }


def _score_short_answer(
    quiz: Dict[str, Any],
    student_answer: str,
) -> Dict[str, Any]:
    """LLM rubric scoring for short-answer questions."""
    llm = get_llm(temperature=0.0, max_tokens=500)
    chain = _RUBRIC_PROMPT | llm | StrOutputParser()
    raw = chain.invoke(
        {
            "question": quiz.get("question", ""),
            "model_answer": quiz.get("correct_answer", ""),
            "key_points": json.dumps(quiz.get("key_points", [])),
            "student_answer": student_answer,
        }
    )
    try:
        return json.loads(_clean_json(raw))
    except json.JSONDecodeError:
        logger.error(f"[Evaluator] JSON parse error: {raw[:200]}")
        return {
            "score": 50,
            "correct_concepts": [],
            "missing_concepts": [],
            "feedback": "Could not parse evaluation. Please try again.",
            "grade": "Partial",
        }


def evaluator_node(state: TutorState) -> TutorState:
    """
    LangGraph node: Evaluator.
    """
    student_answer = state.get("student_answer", "")
    quiz = state.get("quiz")

    if not quiz or quiz.get("type") == "error":
        return {
            **state,
            "answer": "No active quiz to evaluate. Ask me to quiz you first!",
            "evaluation": None,
        }

    logger.info(f"[Evaluator] quiz_type={quiz.get('type')}  student_answer={student_answer[:60]}")

    # ── Score ─────────────────────────────────────────────────────────────────
    q_type = quiz.get("type", "short_answer")
    if q_type == "mcq":
        evaluation = _score_mcq(quiz, student_answer)
    else:
        evaluation = _score_short_answer(quiz, student_answer)

    score = float(evaluation.get("score", 0))

    # ── Update weak topics ────────────────────────────────────────────────────
    topic = quiz.get("topic", "general")
    weak_topics: List[str] = list(state.get("weak_topics", []))
    if score < WEAK_THRESHOLD:
        if topic not in weak_topics:
            weak_topics.append(topic)
            logger.info(f"[Evaluator] Added weak topic: {topic} (score={score})")
    else:
        # Student improved — remove from weak list
        weak_topics = [t for t in weak_topics if t != topic]

    # ── Quiz score history ────────────────────────────────────────────────────
    quiz_scores: List[float] = list(state.get("quiz_scores", []))
    quiz_scores.append(score)

    # ── Reteach trigger ───────────────────────────────────────────────────────
    reteach = score < WEAK_THRESHOLD

    # ── Format answer for display ─────────────────────────────────────────────
    grade = evaluation.get("grade", "?")
    feedback = evaluation.get("feedback", "")
    missing = evaluation.get("missing_concepts", [])

    answer_parts = [
        f"**Score: {score:.0f}/100** — {grade}",
        "",
        feedback,
    ]
    if missing:
        answer_parts += ["", "**Concepts to revisit:**", *[f"• {m}" for m in missing]]
    if reteach:
        answer_parts += ["", "🔄 _I'll revisit this topic in my next explanation._"]

    answer_text = "\n".join(answer_parts)

    return {
        **state,
        "evaluation": evaluation,
        "quiz_scores": quiz_scores,
        "weak_topics": weak_topics,
        "reteach_triggered": reteach,
        "answer": answer_text,
    }
