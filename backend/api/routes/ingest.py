from fastapi import APIRouter, Form, UploadFile

from backend.api.schemas import IngestResponse
from backend.ingest.chunker import chunk_text
from backend.ingest.embedder import embed_and_store
from backend.ingest.loader import load_document

router = APIRouter()


@router.post("/ingest", response_model=IngestResponse)
async def ingest(file: UploadFile, session_id: str = Form(...)):
    text = await load_document(file)
    documents = chunk_text(text, source=file.filename or "unknown")
    result = embed_and_store(documents, session_id, filename=file.filename or "unknown")

    return IngestResponse(chunks_stored=result["chunks_stored"], filename=file.filename or "unknown")
