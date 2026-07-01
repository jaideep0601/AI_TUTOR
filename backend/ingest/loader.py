import io

import docx
import fitz
from fastapi import UploadFile


async def load_document(file: UploadFile) -> str:
    filename = file.filename or ""
    extension = filename.lower().rsplit(".", 1)[-1] if "." in filename else ""
    raw_bytes = await file.read()

    if extension == "pdf":
        return _load_pdf(raw_bytes)
    if extension == "docx":
        return _load_docx(raw_bytes)
    if extension == "txt":
        return raw_bytes.decode("utf-8", errors="ignore")

    raise ValueError(f"Unsupported file type: {extension}")


def _load_pdf(raw_bytes: bytes) -> str:
    text_parts: list[str] = []
    with fitz.open(stream=raw_bytes, filetype="pdf") as pdf_doc:
        for page in pdf_doc:
            text_parts.append(page.get_text())
    return "\n".join(text_parts)


def _load_docx(raw_bytes: bytes) -> str:
    document = docx.Document(io.BytesIO(raw_bytes))
    return "\n".join(paragraph.text for paragraph in document.paragraphs)
