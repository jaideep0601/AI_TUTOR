"""
tests/test_agents.py
────────────────────
Unit tests for agent logic (state, routing, evaluator scoring).
Uses heavy mocking to avoid LLM / vector-store calls.
"""

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

from agents.state import TutorState
from agents.evaluator import _score_mcq, WEAK_THRESHOLD


class TestTutorState:
    def test_default_state_fields(self):
        state: TutorState = {
            "question": "test",
            "session_topics": [],
            "weak_topics": [],
            "quiz_scores": [],
            "reteach_triggered": False,
            "turn_count": 0,
        }
        assert state["question"] == "test"
        assert state["turn_count"] == 0

    def test_state_merge(self):
        base: TutorState = {"question": "q1", "turn_count": 1, "session_topics": []}
        update = {"answer": "an answer", "turn_count": 2}
        merged = {**base, **update}
        assert merged["question"] == "q1"
        assert merged["turn_count"] == 2
        assert merged["answer"] == "an answer"


class TestMCQScoring:
    def _make_quiz(self, correct: str) -> dict:
        return {
            "type": "mcq",
            "question": "What is 2+2?",
            "options": ["A. 3", "B. 4", "C. 5", "D. 6"],
            "correct_answer": correct,
            "explanation": "Basic arithmetic.",
            "topic": "math",
        }

    def test_correct_answer(self):
        quiz = self._make_quiz("B")
        result = _score_mcq(quiz, "B")
        assert result["score"] == 100
        assert result["grade"] == "Excellent"

    def test_wrong_answer(self):
        quiz = self._make_quiz("B")
        result = _score_mcq(quiz, "A")
        assert result["score"] == 0
        assert result["grade"] == "Incorrect"

    def test_lowercase_accepted(self):
        quiz = self._make_quiz("C")
        result = _score_mcq(quiz, "c")
        assert result["score"] == 100

    def test_extra_whitespace(self):
        quiz = self._make_quiz("D")
        result = _score_mcq(quiz, "  D  ")
        assert result["score"] == 100

    def test_weak_threshold_constant(self):
        assert WEAK_THRESHOLD == 60.0


class TestPlannerRouting:
    @patch("agents.planner.get_llm")
    @patch("agents.planner.process_query")
    def test_ask_routes_to_retriever(self, mock_nlp, mock_llm):
        from agents.planner import planner_node
        from nlp.processor import NLPResult

        mock_nlp.return_value = NLPResult(
            text="What is osmosis?",
            intent="Ask",
            entities=[],
            topics=["osmosis"],
            bloom_level="Remember",
        )
        mock_chain = MagicMock()
        mock_chain.invoke.return_value = "• Explain osmosis\n• Use membrane analogy\n• Ask follow-up"
        mock_llm.return_value.__or__ = MagicMock(return_value=mock_chain)

        state: TutorState = {
            "question": "What is osmosis?",
            "session_topics": [],
            "weak_topics": [],
            "quiz_scores": [],
            "reteach_triggered": False,
            "turn_count": 0,
        }

        # Patch the chain construction
        with patch("agents.planner._PLAN_PROMPT") as mock_prompt:
            mock_prompt.__or__ = MagicMock(return_value=mock_chain)
            result = planner_node(state)

        assert result["intent"] == "Ask"
        assert result["next_action"] == "retriever"

    @patch("agents.planner.get_llm")
    @patch("agents.planner.process_query")
    def test_quiz_routes_to_quiz_generator(self, mock_nlp, mock_llm):
        from agents.planner import planner_node
        from nlp.processor import NLPResult

        mock_nlp.return_value = NLPResult(
            text="Quiz me on osmosis",
            intent="Quiz",
            entities=[],
            topics=["osmosis"],
            bloom_level="Remember",
        )

        state: TutorState = {
            "question": "Quiz me on osmosis",
            "session_topics": [],
            "weak_topics": [],
            "quiz_scores": [],
            "reteach_triggered": False,
            "turn_count": 0,
        }

        result = planner_node(state)
        assert result["intent"] == "Quiz"
        assert result["next_action"] == "quiz_generator"
