from backend.agents.state import TutorState
from backend.nlp.intent import classify_intent


def planner_node(state: TutorState) -> TutorState:
    intent = classify_intent(state["user_message"])
    state["intent"] = intent

    state["chat_history"].append({"role": "user", "content": state["user_message"]})

    return state
