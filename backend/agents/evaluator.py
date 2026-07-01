import json

from langchain_google_genai import ChatGoogleGenerativeAI

from backend.agents.state import TutorState
from backend.config.settings import settings

SYSTEM_PROMPT = (
    "You are a strict but fair grader. You are given a student's answer and relevant "
    "context from their study material. Evaluate the answer for correctness and "
    "completeness. Respond ONLY with valid JSON matching this schema: "
    '{"correct": bool, "score": int (0-10), "feedback": str, "correct_answer": str}. '
    "Do not include markdown code fences or any extra text."
)


def _get_llm() -> ChatGoogleGenerativeAI:
    return ChatGoogleGenerativeAI(
        model="gemini-2.5-flash-lite",
        google_api_key=settings.GEMINI_API_KEY,
        temperature=0.2,
    )


def _parse_json_response(raw_text: str) -> dict:
    cleaned = raw_text.strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.strip("`")
        if cleaned.lower().startswith("json"):
            cleaned = cleaned[4:]
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        return {
            "correct": False,
            "score": 0,
            "feedback": "Could not parse grading response.",
            "correct_answer": "",
        }


def evaluator_node(state: TutorState) -> TutorState:
    context = "\n\n".join(state["retrieved_chunks"])
    llm = _get_llm()

    prompt = (
        f"{SYSTEM_PROMPT}\n\n"
        f"Context:\n{context}\n\n"
        f"Student's answer:\n{state['user_message']}"
    )
    response = llm.invoke(prompt)
    result = _parse_json_response(response.content)

    state["evaluation_result"] = result

    if not result.get("correct", False):
        topic = state["retrieved_chunks"][0][:80] if state["retrieved_chunks"] else state["user_message"][:80]
        if topic not in state["weak_topics"]:
            state["weak_topics"].append(topic)

    state["chat_history"].append({"role": "assistant", "content": json.dumps(result)})

    return state
