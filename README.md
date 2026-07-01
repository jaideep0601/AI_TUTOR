# AI Tutor Agent

A full-stack AI tutoring application. Upload your notes (PDF/DOCX/TXT), ask questions,
get Socratic explanations, generate quizzes, and track your learning progress — all
powered by a LangGraph agent pipeline backed by Google Gemini.

- **Backend:** FastAPI, LangChain, LangGraph, ChromaDB, Google Gemini API, spaCy
- **Frontend:** Next.js 14 (App Router), TypeScript, Tailwind CSS, Zustand, Framer Motion, Recharts

> **Note on model names:** `gemini-1.5-flash` and `models/embedding-001` have since
> been retired by Google. This project uses `gemini-2.5-flash` (chat) and
> `models/gemini-embedding-001` (embeddings) instead — both confirmed working on the
> free tier. If Google retires these too, run `curl "https://generativelanguage.googleapis.com/v1beta/models?key=$GEMINI_API_KEY"`
> to see what's currently available and update the model names in `backend/agents/*.py`,
> `backend/rag/*.py`, and `backend/ingest/embedder.py`.

## Project Structure

```
ai-tutor/
├── backend/    # FastAPI + LangGraph agent pipeline
└── frontend/   # Next.js app
```

## Prerequisites

- Python 3.11+
- Node.js 18+
- A free [Google Gemini API key](https://aistudio.google.com/app/apikey)

## Backend Setup

```bash
cd ai-tutor/backend
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

pip install -r requirements.txt
python -m spacy download en_core_web_sm

cp .env.example .env
# edit .env and set GEMINI_API_KEY=<your key>

cd ..                            # back to ai-tutor/ — required so `backend` resolves as a package
uvicorn backend.api.main:app --reload --port 8000
```

> `uvicorn backend.api.main:app` must be run from `ai-tutor/` (the parent of the
> `backend` package), not from inside `backend/` — otherwise you'll get
> `ModuleNotFoundError: No module named 'backend'`. The venv stays active either way
> since activation only changes `PATH`/`PYTHONHOME`, not your working directory.

The API will be available at `http://localhost:8000`. Interactive docs at
`http://localhost:8000/docs`.

### Backend environment variables (`backend/.env`)

| Variable | Default | Description |
|---|---|---|
| `GEMINI_API_KEY` | — | Your Google Gemini API key (required) |
| `CHROMA_DB_PATH` | `./chroma_db` | Path for the persistent Chroma vector store |
| `COLLECTION_NAME` | `tutor` | Base collection name (suffixed per session) |
| `CHUNK_SIZE` | `512` | Chunk size for document splitting |
| `CHUNK_OVERLAP` | `64` | Overlap between chunks |
| `TOP_K` | `6` | Number of chunks retrieved per query |
| `CORS_ORIGINS` | `["http://localhost:3000"]` | Allowed CORS origins |

## Frontend Setup

```bash
cd ai-tutor/frontend
npm install

cp .env.local.example .env.local
# NEXT_PUBLIC_API_URL=http://localhost:8000/api

npm run dev
```

The app will be available at `http://localhost:3000`.

## Running Both Servers

Open two terminals:

```bash
# Terminal 1 — backend
cd ai-tutor/backend && uvicorn backend.api.main:app --reload --port 8000

# Terminal 2 — frontend
cd ai-tutor/frontend && npm run dev
```

Then visit `http://localhost:3000`, click **Start Learning**, upload some notes, and
start chatting with the tutor.

## How It Works

1. **Ingest** — Uploaded documents are parsed (PyMuPDF/python-docx), chunked with
   `RecursiveCharacterTextSplitter`, embedded with Gemini's `embedding-001`, and
   stored in a per-session ChromaDB collection.
2. **Chat** — Each message flows through a LangGraph pipeline:
   `planner` (intent classification) → `retriever` (HyDE + MMR retrieval + rerank +
   Bloom tagging) → one of `responder` / `quiz_generator` / `evaluator` depending on
   intent.
3. **Progress** — The frontend polls `/api/progress` every 10s to show Bloom's
   taxonomy coverage, quiz score history, and weak topics.

## Notes

- Session state (chat history, weak topics, vectors) is stored server-side, keyed by
  a UUID generated client-side on first load and sent via the `X-Session-Id` header.
- The backend uses an in-memory session store — restarting the backend clears chat
  history and progress (vector data in ChromaDB persists on disk).
