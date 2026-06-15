"""
nlp/processor.py
────────────────
NLP preprocessing pipeline using spaCy.

Responsibilities:
  1. Entity extraction — named entities (PERSON, ORG, GPE, PRODUCT, …)
     plus noun chunks as "topics".
  2. Intent classification — rule-based classifier maps the question into
     one of four pedagogical modes understood by the LangGraph agents:
       Ask      — factual retrieval ("What is…", "Who invented…")
       Explain  — conceptual explanation ("How does…", "Why is…")
       Quiz     — generate practice questions ("Quiz me on…", "Test me…")
       Evaluate — assess student-supplied answer ("Is this right?", "Did I…")

  3. Bloom's taxonomy tagger — labels each retrieved chunk with a Bloom's
     level (Remember, Understand, Apply, Analyze, Evaluate, Create) based
     on the verbs and complexity of the text.  Used by the Planner agent to
     scaffold learning sequences.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from functools import lru_cache
from typing import Dict, List

from loguru import logger

# ── spaCy lazy load ───────────────────────────────────────────────────────────
try:
    import spacy

    @lru_cache(maxsize=1)
    def _nlp():
        try:
            return spacy.load("en_core_web_sm")
        except OSError:
            logger.warning(
                "spaCy model 'en_core_web_sm' not found. "
                "Run: python -m spacy download en_core_web_sm"
            )
            return None

except ImportError:
    logger.warning("spaCy not installed — NLP features degraded.")
    _nlp = lambda: None  # noqa: E731


# ── Intent classification ─────────────────────────────────────────────────────
_ASK_PATTERNS = re.compile(
    r"\b(what|who|when|where|which|define|tell me|list|name)\b", re.I
)
_EXPLAIN_PATTERNS = re.compile(
    r"\b(how|why|explain|describe|elaborate|clarify|compare|contrast|difference)\b", re.I
)
_QUIZ_PATTERNS = re.compile(
    r"\b(quiz|test|question|practice|exam|exercise|challenge|assess)\b", re.I
)
_EVALUATE_PATTERNS = re.compile(
    r"\b(is this|am i|correct|right|wrong|evaluate|check|grade|review|my answer)\b", re.I
)

IntentType = str  # "Ask" | "Explain" | "Quiz" | "Evaluate"


def classify_intent(text: str) -> IntentType:
    """
    Rule-based intent classifier.  Returns the dominant pedagogical intent.

    Priority order: Evaluate > Quiz > Explain > Ask (default).
    """
    if _EVALUATE_PATTERNS.search(text):
        return "Evaluate"
    if _QUIZ_PATTERNS.search(text):
        return "Quiz"
    if _EXPLAIN_PATTERNS.search(text):
        return "Explain"
    return "Ask"


# ── Entity & topic extraction ─────────────────────────────────────────────────
@dataclass
class NLPResult:
    text: str
    intent: IntentType
    entities: List[Dict[str, str]] = field(default_factory=list)
    topics: List[str] = field(default_factory=list)
    bloom_level: str = "Remember"


def extract_entities(text: str) -> List[Dict[str, str]]:
    """Return [{text, label}] for named entities."""
    nlp = _nlp()
    if nlp is None:
        return []
    doc = nlp(text)
    return [{"text": ent.text, "label": ent.label_} for ent in doc.ents]


def extract_topics(text: str) -> List[str]:
    """Return unique noun chunks as topic strings."""
    nlp = _nlp()
    if nlp is None:
        return []
    doc = nlp(text)
    seen = set()
    topics = []
    for chunk in doc.noun_chunks:
        t = chunk.text.strip().lower()
        if len(t) > 2 and t not in seen:
            seen.add(t)
            topics.append(t)
    return topics


# ── Bloom's taxonomy tagger ───────────────────────────────────────────────────
_BLOOM_LEVELS = {
    "Create":    re.compile(r"\b(design|create|build|compose|construct|develop|formulate|plan)\b", re.I),
    "Evaluate":  re.compile(r"\b(evaluate|judge|critique|justify|assess|defend|argue|prioritize)\b", re.I),
    "Analyze":   re.compile(r"\b(analyze|differentiate|examine|investigate|compare|contrast|break down)\b", re.I),
    "Apply":     re.compile(r"\b(apply|use|demonstrate|solve|compute|calculate|implement|execute)\b", re.I),
    "Understand": re.compile(r"\b(explain|describe|interpret|summarize|paraphrase|classify|discuss)\b", re.I),
    "Remember":  re.compile(r"\b(define|list|name|recall|identify|state|recognize|repeat)\b", re.I),
}

_BLOOM_ORDER = ["Create", "Evaluate", "Analyze", "Apply", "Understand", "Remember"]


def tag_bloom_level(text: str) -> str:
    """
    Assign a Bloom's taxonomy level to a text chunk.
    Returns the *highest* level found (Create > Evaluate > … > Remember).
    """
    for level in _BLOOM_ORDER:
        if _BLOOM_LEVELS[level].search(text):
            return level
    return "Remember"


# ── Unified processor ─────────────────────────────────────────────────────────
def process_query(text: str) -> NLPResult:
    """
    Run the full NLP pipeline on a student query.
    Returns an NLPResult with intent, entities, topics, and Bloom's level.
    """
    intent = classify_intent(text)
    entities = extract_entities(text)
    topics = extract_topics(text)
    bloom = tag_bloom_level(text)
    return NLPResult(
        text=text,
        intent=intent,
        entities=entities,
        topics=topics,
        bloom_level=bloom,
    )
