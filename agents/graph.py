"""
agents/graph.py
───────────────
LangGraph state machine wiring Planner → Retriever / QuizGenerator / Evaluator.

Graph topology:

         ┌─────────┐
  START ─►  Planner ├──── next_action="retriever"  ──────► Retriever ──► END
         └────┬────┘
              │       next_action="quiz_generator" ──► QuizGenerator ──► END
              │
              └───── next_action="evaluator"       ──►   Evaluator  ──► END

All nodes write to the shared TutorState TypedDict.
Conditional routing is driven by state["next_action"] set by the Planner.
"""

from __future__ import annotations

from functools import lru_cache

from langgraph.graph import StateGraph, END

from agents.state import TutorState
from agents.planner import planner_node
from agents.retriever import retriever_node
from agents.quiz_generator import quiz_generator_node
from agents.evaluator import evaluator_node


def _route(state: TutorState) -> str:
    """Conditional edge: read next_action and route to the correct node."""
    return state.get("next_action", "retriever")


@lru_cache(maxsize=1)
def build_graph():
    """
    Build and compile the LangGraph state machine.
    Cached so we compile once per process.
    """
    graph = StateGraph(TutorState)

    # ── Register nodes ────────────────────────────────────────────────────────
    graph.add_node("planner", planner_node)
    graph.add_node("retriever", retriever_node)
    graph.add_node("quiz_generator", quiz_generator_node)
    graph.add_node("evaluator", evaluator_node)

    # ── Entry point ───────────────────────────────────────────────────────────
    graph.set_entry_point("planner")

    # ── Conditional routing from Planner ──────────────────────────────────────
    graph.add_conditional_edges(
        "planner",
        _route,
        {
            "retriever": "retriever",
            "quiz_generator": "quiz_generator",
            "evaluator": "evaluator",
        },
    )

    # ── Terminal edges ────────────────────────────────────────────────────────
    graph.add_edge("retriever", END)
    graph.add_edge("quiz_generator", END)
    graph.add_edge("evaluator", END)

    return graph.compile()


def run_tutor(state: TutorState) -> TutorState:
    """
    Public entry point: invoke the compiled graph with the current state.
    Returns the updated state after all nodes have executed.
    """
    app = build_graph()
    return app.invoke(state)
