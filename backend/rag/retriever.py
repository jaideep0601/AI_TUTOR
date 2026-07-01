import numpy as np
from langchain_core.documents import Document
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings

from backend.config.settings import settings
from backend.ingest.embedder import get_collection

HYDE_PROMPT = (
    "Write a short, plausible answer (2-4 sentences) to the following question. "
    "It does not need to be factually correct, it only needs to resemble the kind "
    "of passage that would answer the question.\n\nQuestion: {query}"
)


def _get_llm() -> ChatGoogleGenerativeAI:
    return ChatGoogleGenerativeAI(
        model="gemini-2.5-flash-lite",
        google_api_key=settings.GEMINI_API_KEY,
        temperature=0.3,
    )


def _get_embeddings_model() -> GoogleGenerativeAIEmbeddings:
    return GoogleGenerativeAIEmbeddings(
        model="models/gemini-embedding-001",
        google_api_key=settings.GEMINI_API_KEY,
    )


def generate_hyde_document(query: str) -> str:
    llm = _get_llm()
    response = llm.invoke(HYDE_PROMPT.format(query=query))
    return response.content


def _mmr(query_vector: list[float], candidate_vectors: list[list[float]], top_k: int, lambda_mult: float = 0.5) -> list[int]:
    query_arr = np.array(query_vector)
    candidates_arr = np.array(candidate_vectors)

    def cosine_sim(a: np.ndarray, b: np.ndarray) -> float:
        denom = (np.linalg.norm(a) * np.linalg.norm(b)) or 1e-10
        return float(np.dot(a, b) / denom)

    selected: list[int] = []
    remaining = list(range(len(candidate_vectors)))

    while remaining and len(selected) < top_k:
        best_idx = None
        best_score = -float("inf")
        for idx in remaining:
            relevance = cosine_sim(query_arr, candidates_arr[idx])
            diversity = max(
                (cosine_sim(candidates_arr[idx], candidates_arr[sel]) for sel in selected),
                default=0.0,
            )
            score = lambda_mult * relevance - (1 - lambda_mult) * diversity
            if score > best_score:
                best_score = score
                best_idx = idx
        selected.append(best_idx)
        remaining.remove(best_idx)

    return selected


def retrieve(query: str, session_id: str) -> list[Document]:
    collection = get_collection(session_id)
    if collection.count() == 0:
        return []

    hyde_text = generate_hyde_document(query)
    embeddings_model = _get_embeddings_model()
    hyde_vector = embeddings_model.embed_query(hyde_text)

    fetch_k = min(max(settings.TOP_K * 3, settings.TOP_K), collection.count())
    results = collection.query(
        query_embeddings=[hyde_vector],
        n_results=fetch_k,
        include=["documents", "metadatas", "embeddings"],
    )

    documents_text = results["documents"][0]
    metadatas = results["metadatas"][0]
    candidate_vectors = results["embeddings"][0]

    if not documents_text:
        return []

    selected_indices = _mmr(hyde_vector, candidate_vectors, settings.TOP_K)

    return [
        Document(page_content=documents_text[i], metadata=metadatas[i])
        for i in selected_indices
    ]
