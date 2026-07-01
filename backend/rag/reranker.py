import numpy as np
from langchain_core.documents import Document
from langchain_google_genai import GoogleGenerativeAIEmbeddings

from backend.config.settings import settings

SIMILARITY_THRESHOLD = 0.3


def _get_embeddings_model() -> GoogleGenerativeAIEmbeddings:
    return GoogleGenerativeAIEmbeddings(
        model="models/gemini-embedding-001",
        google_api_key=settings.GEMINI_API_KEY,
    )


def _cosine_similarity(a: list[float], b: list[float]) -> float:
    a_arr, b_arr = np.array(a), np.array(b)
    denom = (np.linalg.norm(a_arr) * np.linalg.norm(b_arr)) or 1e-10
    return float(np.dot(a_arr, b_arr) / denom)


def rerank(query: str, documents: list[Document], top_n: int | None = None) -> list[Document]:
    if not documents:
        return []

    embeddings_model = _get_embeddings_model()
    query_vector = embeddings_model.embed_query(query)
    doc_vectors = embeddings_model.embed_documents([doc.page_content for doc in documents])

    scored = [
        (doc, _cosine_similarity(query_vector, doc_vector))
        for doc, doc_vector in zip(documents, doc_vectors)
    ]
    filtered = [pair for pair in scored if pair[1] >= SIMILARITY_THRESHOLD]
    filtered.sort(key=lambda pair: pair[1], reverse=True)

    limit = top_n or settings.TOP_K
    return [doc for doc, _score in filtered[:limit]]
