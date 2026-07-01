from fastapi import APIRouter

from backend.api.schemas import ProgressResponse
from backend.memory.session_store import get_session

router = APIRouter()

BLOOM_LEVELS = ["remember", "understand", "apply", "analyse", "evaluate", "create"]


@router.get("/progress", response_model=ProgressResponse)
async def progress(session_id: str):
    state = get_session(session_id)

    bloom_distribution = {level: 0 for level in BLOOM_LEVELS}
    for tag in state["bloom_tags"]:
        if tag in bloom_distribution:
            bloom_distribution[tag] += 1

    topics_covered = list({chunk[:60] for chunk in state["retrieved_chunks"]})

    quiz_scores: list[int] = []
    evaluation = state.get("evaluation_result") or {}
    if evaluation and "score" in evaluation:
        quiz_scores.append(evaluation["score"])

    return ProgressResponse(
        topics_covered=topics_covered,
        weak_topics=state["weak_topics"],
        quiz_scores=quiz_scores,
        bloom_distribution=bloom_distribution,
    )
