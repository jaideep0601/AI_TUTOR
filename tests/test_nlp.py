"""
tests/test_nlp.py
─────────────────
Unit tests for the NLP preprocessing layer.
Pure Python logic — no external API calls.
"""

import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from nlp.processor import (
    classify_intent,
    tag_bloom_level,
    process_query,
    NLPResult,
)


class TestIntentClassifier:
    def test_ask_intent(self):
        assert classify_intent("What is photosynthesis?") == "Ask"
        assert classify_intent("Define osmosis") == "Ask"

    def test_explain_intent(self):
        assert classify_intent("How does DNA replication work?") == "Explain"
        assert classify_intent("Explain the water cycle") == "Explain"

    def test_quiz_intent(self):
        assert classify_intent("Quiz me on photosynthesis") == "Quiz"
        assert classify_intent("Give me a practice question") == "Quiz"

    def test_evaluate_intent(self):
        assert classify_intent("Is this answer correct?") == "Evaluate"
        assert classify_intent("Check my work") == "Evaluate"

    def test_evaluate_priority_over_quiz(self):
        assert classify_intent("Check if my test answer is correct") == "Evaluate"

    def test_default_to_ask(self):
        assert classify_intent("Tell me something interesting") == "Ask"


class TestBloomTagger:
    def test_remember_level(self):
        assert tag_bloom_level("Define the term osmosis") == "Remember"

    def test_understand_level(self):
        assert tag_bloom_level("Explain how DNA replication works") == "Understand"

    def test_apply_level(self):
        assert tag_bloom_level("Calculate the area of a circle") == "Apply"

    def test_analyze_level(self):
        assert tag_bloom_level("Compare and contrast mitosis and meiosis") == "Analyze"

    def test_evaluate_level(self):
        assert tag_bloom_level("Evaluate the effectiveness of this argument") == "Evaluate"

    def test_create_level(self):
        assert tag_bloom_level("Design a new experiment to test this") == "Create"

    def test_higher_wins(self):
        text = "Design and define a new experimental framework"
        level = tag_bloom_level(text)
        assert level == "Create"


class TestProcessQuery:
    def test_returns_nlp_result(self):
        result = process_query("What is machine learning?")
        assert isinstance(result, NLPResult)
        assert result.intent == "Ask"
        assert result.bloom_level in {
            "Remember", "Understand", "Apply", "Analyze", "Evaluate", "Create"
        }
        assert isinstance(result.topics, list)
        assert isinstance(result.entities, list)

    def test_quiz_query(self):
        result = process_query("Quiz me on neural networks")
        assert result.intent == "Quiz"

    def test_explain_query(self):
        result = process_query("How does backpropagation work?")
        assert result.intent == "Explain"
