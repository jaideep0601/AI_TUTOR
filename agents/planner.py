"""
agents/planner.py
─────────────────
Planner agent — the "orchestrator" node in the LangGraph graph.

Responsibilities:
  1. Run NLP preprocessing on the incoming question.
  2. Decide which sub-agent should handle the turn based on intent + context.
  3. Build a short teaching plan string that later agents can reference.
  4. Set `next_action` to route the graph to the correct next node.

The Planner does NOT call the LLM for routing — this keeps latency low and
the routing logic deterministic and auditable.  It only calls the LLM when
it needs to generate a scaffolded teaching plan (Explain / Reteach modes).
"""

from __future__ import annotations

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from loguru import logger

from agents.state import TutorState
from config.llm_factory import get_llm
from nlp.processor import process_query

_PLAN_PROMPT = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            (
                "You are a master curriculum designer. "
                "Given a student's question and the detected Bloom's taxonomy level, "
                "write a SHORT (3 bullet) teaching plan: what concept to cover first, "
                "what analogy or example to use, and what follow-up question to pose. "
                "Be terse — this plan is for internal use only."
            ),
        ),
        (
            "human",
            "Question: {question}\nBloom's level: {bloom}\nTopics: {topics}",
        ),
    ]
)


def planner_node(state: TutorState) -> TutorState:
    """
    LangGraph node: Planner.

    Mutates state with: intent, entities, topics, bloom_level, plan, next_action.
    """
    question = state.get("question", "")
    reteach = state.get("reteach_triggered", False)
    logger.info(f"[Planner] question={question[:60]}…  reteach={reteach}")

    # ── NLP preprocessing ─────────────────────────────────────────────────────
    nlp_result = process_query(question)

    # ── Determine routing intent ───────────────────────────────────────────────
    # Reteach overrides intent: switch to Explain mode for weak topics
    effective_intent = "Explain" if reteach else nlp_result.intent

    # ── Build teaching plan (only for Explain-mode turns to save tokens) ───────
    plan = ""
    if effective_intent in ("Explain", "Ask"):
        llm = get_llm(temperature=0.3, max_tokens=300)
        chain = _PLAN_PROMPT | llm | StrOutputParser()
        plan = chain.invoke(
            {
                "question": question,
                "bloom": nlp_result.bloom_level,
                "topics": ", ".join(nlp_result.topics[:5]) or "general",
            }
        )

    # ── Routing decision ──────────────────────────────────────────────────────
    # next_action drives the conditional edge in the graph
    action_map = {
        "Ask": "retriever",
        "Explain": "retriever",
        "Quiz": "quiz_generator",
        "Evaluate": "evaluator",
    }
    next_action = action_map.get(effective_intent, "retriever")

    # Accumulate session topics
    session_topics = list(state.get("session_topics", []))
    for t in nlp_result.topics:
        if t not in session_topics:
            session_topics.append(t)

    updates: TutorState = {
        "intent": effective_intent,
        "entities": nlp_result.entities,
        "topics": nlp_result.topics,
        "bloom_level": nlp_result.bloom_level,
        "plan": plan,
        "next_action": next_action,
        "session_topics": session_topics,
        "turn_count": state.get("turn_count", 0) + 1,
    }
    logger.info(f"[Planner] intent={effective_intent}  next_action={next_action}")
    return {**state, **updates}
