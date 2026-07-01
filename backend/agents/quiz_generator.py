import json

from langchain_google_genai import ChatGoogleGenerativeAI

from backend.agents.state import TutorState
from backend.config.settings import settings

QUIZ_PROMPT_PREFIX = (
    "You are a quiz generator for a tutoring app. Using ONLY the context provided, "
    "generate exactly 3 multiple-choice questions. Respond ONLY with valid JSON "
    "matching this schema: "
    '{"questions": [{"question": str, "options": [str, str, str, str], "answer": str, '
    '"explanation": str, "bloom_level": str}]}. '
    "bloom_level must be one of: remember, understand, apply, analyse, evaluate, create. "
    "Do not include markdown code fences or any extra text.\n\n"
    "Context:\n"
)


def _get_llm() -> ChatGoogleGenerativeAI:
    return ChatGoogleGenerativeAI(
        model="gemini-2.5-flash-lite",
        google_api_key=settings.GEMINI_API_KEY,
        temperature=0.4,
    )


def _parse_json_response(raw_text: str) -> dict:
    cleaned = raw_text.strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.strip("`")
        if cleaned.lower().startswith("json"):
            cleaned = cleaned[4:]
    try:
        parsed = json.loads(cleaned)
        if "questions" not in parsed:
            return {"questions": []}
        return parsed
    except json.JSONDecodeError:
        return {"questions": []}


def quiz_generator_node(state: TutorState) -> TutorState:
    context = "\n\n".join(state["retrieved_chunks"])
    llm = _get_llm()

    response = llm.invoke(QUIZ_PROMPT_PREFIX + context)
    result = _parse_json_response(response.content)

    state["quiz_json"] = result
    state["chat_history"].append({"role": "assistant", "content": json.dumps(result)})

    return state
