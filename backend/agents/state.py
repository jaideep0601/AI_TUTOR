from typing import TypedDict


class TutorState(TypedDict):
    session_id: str
    user_message: str
    intent: str
    retrieved_chunks: list[str]
    bloom_tags: list[str]
    llm_response: str
    quiz_json: dict
    evaluation_result: dict
    weak_topics: list[str]
    chat_history: list[dict]


def new_state(session_id: str) -> TutorState:
    return TutorState(
        session_id=session_id,
        user_message="",
        intent="",
        retrieved_chunks=[],
        bloom_tags=[],
        llm_response="",
        quiz_json={},
        evaluation_result={},
        weak_topics=[],
        chat_history=[],
    )
