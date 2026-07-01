from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import END, StateGraph

from backend.agents.evaluator import evaluator_node
from backend.agents.planner import planner_node
from backend.agents.quiz_generator import quiz_generator_node
from backend.agents.retriever_agent import retriever_node
from backend.agents.state import TutorState
from backend.config.settings import settings

SOCRATIC_SYSTEM_PROMPT = (
    "You are a warm, patient Socratic tutor. You help students learn by guiding them "
    "toward understanding rather than simply giving answers outright. Use the provided "
    "context from the student's own study material when relevant. Ask clarifying or "
    "leading questions when appropriate, keep explanations clear and concise, and "
    "encourage the student's curiosity."
)


def _get_llm() -> ChatGoogleGenerativeAI:
    return ChatGoogleGenerativeAI(
        model="gemini-2.5-flash-lite",
        google_api_key=settings.GEMINI_API_KEY,
        temperature=0.5,
    )


def responder_node(state: TutorState) -> TutorState:
    context = "\n\n".join(state["retrieved_chunks"])
    history_text = "\n".join(
        f"{turn['role']}: {turn['content']}" for turn in state["chat_history"][-10:]
    )

    prompt = (
        f"{SOCRATIC_SYSTEM_PROMPT}\n\n"
        f"Context from study material:\n{context}\n\n"
        f"Conversation so far:\n{history_text}\n\n"
        f"Student's latest message: {state['user_message']}"
    )

    llm = _get_llm()
    response = llm.invoke(prompt)

    state["llm_response"] = response.content
    state["chat_history"].append({"role": "assistant", "content": response.content})

    return state


def _route_after_retrieval(state: TutorState) -> str:
    if state["intent"] == "QUIZ":
        return "quiz_generator"
    if state["intent"] == "EVALUATE":
        return "evaluator"
    return "responder"


def build_graph():
    graph = StateGraph(TutorState)

    graph.add_node("planner", planner_node)
    graph.add_node("retriever", retriever_node)
    graph.add_node("quiz_generator", quiz_generator_node)
    graph.add_node("evaluator", evaluator_node)
    graph.add_node("responder", responder_node)

    graph.set_entry_point("planner")
    graph.add_edge("planner", "retriever")
    graph.add_conditional_edges(
        "retriever",
        _route_after_retrieval,
        {
            "quiz_generator": "quiz_generator",
            "evaluator": "evaluator",
            "responder": "responder",
        },
    )
    graph.add_edge("quiz_generator", END)
    graph.add_edge("evaluator", END)
    graph.add_edge("responder", END)

    return graph.compile()


tutor_graph = build_graph()
