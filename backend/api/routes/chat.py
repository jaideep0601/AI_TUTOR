from fastapi import APIRouter

from backend.agents.graph import tutor_graph
from backend.api.schemas import ChatRequest
from backend.memory.session_store import get_session, update_session

router = APIRouter()


@router.post("/chat")
async def chat(request: ChatRequest):
    state = get_session(request.session_id)
    state["user_message"] = request.message

    result_state = tutor_graph.invoke(state)
    update_session(request.session_id, result_state)

    intent = result_state["intent"]

    if intent == "QUIZ":
        return {"questions": result_state["quiz_json"].get("questions", [])}

    if intent == "EVALUATE":
        return result_state["evaluation_result"]

    return {
        "response": result_state["llm_response"],
        "intent": intent,
        "bloom_tags": result_state["bloom_tags"],
    }
