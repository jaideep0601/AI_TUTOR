import chromadb
from langchain_core.documents import Document
from langchain_google_genai import GoogleGenerativeAIEmbeddings

from backend.config.settings import settings

_chroma_client = chromadb.PersistentClient(path=settings.CHROMA_DB_PATH)


def _get_embeddings_model() -> GoogleGenerativeAIEmbeddings:
    return GoogleGenerativeAIEmbeddings(
        model="models/gemini-embedding-001",
        google_api_key=settings.GEMINI_API_KEY,
    )


def get_collection(session_id: str):
    return _chroma_client.get_or_create_collection(name=f"{settings.COLLECTION_NAME}_{session_id}")


def embed_and_store(documents: list[Document], session_id: str, filename: str) -> dict:
    if not documents:
        return {"chunks_stored": 0}

    embeddings_model = _get_embeddings_model()
    texts = [doc.page_content for doc in documents]
    vectors = embeddings_model.embed_documents(texts)

    collection = get_collection(session_id)
    ids = [f"{filename}-{doc.metadata['chunk_index']}" for doc in documents]
    metadatas = [doc.metadata for doc in documents]

    collection.add(
        ids=ids,
        embeddings=vectors,
        documents=texts,
        metadatas=metadatas,
    )

    return {"chunks_stored": len(documents)}
