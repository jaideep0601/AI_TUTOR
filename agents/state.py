"""
agents/state.py
───────────────
Shared TypedDict state that flows through the LangGraph state machine.

Design decision: Using a flat TypedDict (rather than nested Pydantic models)
keeps LangGraph serialization simple and avoids deep copy overhead.  All
fields have defaults so any node can run without upstream dependencies.
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional
from typing_extensions import TypedDict


class TutorState(TypedDict, total=False):
    # ── Input ─────────────────────────────────────────────────────────────────
    question: str                    # raw student question
    student_answer: Optional[str]    # for evaluation mode

    # ── NLP analysis ──────────────────────────────────────────────────────────
    intent: str                      # Ask | Explain | Quiz | Evaluate
    entities: List[Dict[str, str]]   # [{text, label}, …]
    topics: List[str]                # noun-chunk topics
    bloom_level: str                 # Bloom's taxonomy level

    # ── Retrieval ─────────────────────────────────────────────────────────────
    retrieved_docs: List[Any]        # List[Document]
    compressed_context: str          # after compression
    sources: List[str]               # source file names

    # ── Planning ──────────────────────────────────────────────────────────────
    plan: str                        # Planner's teaching plan
    next_action: str                 # route decision

    # ── Answer / Quiz ─────────────────────────────────────────────────────────
    answer: str                      # tutor's answer
    quiz: Optional[Dict[str, Any]]   # quiz JSON
    evaluation: Optional[Dict[str, Any]]  # rubric evaluation result

    # ── Session tracking ──────────────────────────────────────────────────────
    session_topics: List[str]        # all topics discussed
    weak_topics: List[str]           # topics with low scores
    quiz_scores: List[float]         # per-quiz percentage scores
    reteach_triggered: bool          # whether reteach mode is active

    # ── Meta ──────────────────────────────────────────────────────────────────
    error: Optional[str]             # error message if any node fails
    turn_count: int                  # conversation turns
