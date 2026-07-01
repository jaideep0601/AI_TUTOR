from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

from backend.config.settings import settings


def chunk_text(text: str, source: str) -> list[Document]:
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=settings.CHUNK_SIZE,
        chunk_overlap=settings.CHUNK_OVERLAP,
    )
    raw_chunks = splitter.split_text(text)

    documents: list[Document] = []
    for index, chunk in enumerate(raw_chunks):
        documents.append(
            Document(
                page_content=chunk,
                metadata={
                    "source": source,
                    "page": index // 3,
                    "chunk_index": index,
                },
            )
        )
    return documents
