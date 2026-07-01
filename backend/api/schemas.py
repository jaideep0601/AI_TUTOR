from pydantic import BaseModel


class ChatRequest(BaseModel):
    session_id: str
    message: str


class ChatResponse(BaseModel):
    response: str
    intent: str
    bloom_tags: list[str]


class IngestResponse(BaseModel):
    chunks_stored: int
    filename: str


class QuizResponse(BaseModel):
    questions: list[dict]


class ProgressResponse(BaseModel):
    topics_covered: list[str]
    weak_topics: list[str]
    quiz_scores: list[int]
    bloom_distribution: dict[str, int]
