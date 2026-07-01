from backend.agents.state import TutorState, new_state

sessions: dict[str, TutorState] = {}


def get_session(session_id: str) -> TutorState:
    if session_id not in sessions:
        sessions[session_id] = new_state(session_id)
    return sessions[session_id]


def update_session(session_id: str, state: TutorState) -> None:
    sessions[session_id] = state
