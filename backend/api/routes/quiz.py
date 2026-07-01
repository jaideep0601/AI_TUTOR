from fastapi import APIRouter

from backend.agents.quiz_generator import quiz_generator_node
from backend.agents.retriever_agent import retriever_node
from backend.api.schemas import QuizResponse
from backend.memory.session_store import get_session, update_session

router = APIRouter()


@router.get("/quiz", response_model=QuizResponse)
async def quiz(session_id: str):
    state = get_session(session_id)
    state["intent"] = "QUIZ"
    state["user_message"] = state["user_message"] or "Quiz me on the material."

    state = retriever_node(state)
    state = quiz_generator_node(state)
    update_session(session_id, state)

    return QuizResponse(questions=state["quiz_json"].get("questions", []))
