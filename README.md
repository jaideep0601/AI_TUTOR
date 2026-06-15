<<<<<<< HEAD
# 🎓 AI Tutor Agent

> A production-grade, multi-agent AI tutoring system built with LangChain, LangGraph, ChromaDB, and Streamlit.

---

## Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Features](#features)
- [Project Structure](#project-structure)
- [Quick Start](#quick-start)
- [Configuration](#configuration)
- [Usage](#usage)
- [Make Commands](#make-commands)
- [LangSmith Tracing](#langsmith-tracing)
- [PDF Report Export](#pdf-report-export)
- [Testing](#testing)
- [Design Decisions](#design-decisions)

---

## Overview

AI Tutor Agent is a Socratic tutoring system that ingests your study documents (PDF, DOCX, TXT) and teaches through conversation. It doesn't just answer questions — it adapts to your learning level, quizzes you, tracks weak areas, and re-teaches topics where you struggle.

**Core stack:**

| Layer | Technology |
|---|---|
| LLM | OpenAI GPT-4o via LiteLLM (swappable) |
| Orchestration | LangGraph state machine |
| Retrieval | ChromaDB + MMR + Cross-encoder re-ranking |
| Embeddings | OpenAI `text-embedding-3-small` |
| NLP | spaCy (entities, intent, Bloom's taxonomy) |
| UI | Streamlit |
| Tracing | LangSmith (opt-in) |
| Export | ReportLab PDF |

---

## Architecture

```
Student Query
     │
     ▼
┌────────────┐    NLP preprocessing
│  Planner   │◄── (spaCy intent + Bloom's)
│   Agent    │
└─────┬──────┘
      │  next_action
      ├──────────────► Retriever Agent
      │                  │ HyDE expansion
      │                  │ MMR retrieval (ChromaDB)
      │                  │ Cross-encoder re-rank
      │                  │ LLMLingua compression
      │                  └─► Socratic answer
      │
      ├──────────────► QuizGenerator Agent
      │                  │ Context-aware MCQ / short-answer
      │                  │ JSON-mode structured output
      │                  └─► Quiz displayed to student
      │
      └──────────────► Evaluator Agent
                         │ MCQ: letter-match scoring
                         │ Short-answer: LLM rubric scoring
                         │ Weak-topic tracking
                         └─► Adaptive reteach trigger
```

---

## Features

### 1. Document Ingestion Pipeline
- Supports PDF, DOCX, DOC, TXT, MD
- `RecursiveCharacterTextSplitter` (chunk_size=512, overlap=64)
- SHA-256 chunk deduplication — re-ingesting the same file is a no-op
- Rich metadata per chunk (source, page, file hash, Bloom's level)

### 2. Multi-Agent Orchestration (LangGraph)
- **Planner**: NLP preprocessing, intent detection, routing
- **Retriever**: Advanced RAG → Socratic answer generation
- **QuizGenerator**: Adaptive MCQ + short-answer in JSON mode
- **Evaluator**: Rubric scoring, weak-topic tracking, reteach trigger
- Conditional edges driven by `state["next_action"]`

### 3. Advanced RAG
- **HyDE** (Hypothetical Document Embeddings): embeds a synthetic answer instead of the raw query for better recall
- **MMR retrieval** (k=6, fetch_k=20): balances relevance with diversity
- **Cross-encoder re-ranking**: `ms-marco-MiniLM-L-6-v2` re-scores (query, passage) pairs
- **LLMLingua-style compression**: LLM extracts only sentences relevant to the question

### 4. NLP Preprocessing (spaCy)
- Named entity extraction (PERSON, ORG, GPE, PRODUCT, …)
- Noun-chunk topic extraction
- Rule-based intent classifier: Ask / Explain / Quiz / Evaluate
- Bloom's taxonomy tagger on queries and retrieved chunks

### 5. Adaptive Quiz System
- Alternates MCQ and short-answer each turn for variety
- Prioritises weak topics automatically
- Rubric scoring with `key_points` coverage check
- Rolling score history → weak areas flagged at <60%
- Automatic reteach loop when score is low

### 6. Streamlit UI
- Socratic tutor persona (Socrates avatar)
- File uploader with live ingestion feedback
- Sidebar: KB stats, topics covered, weak area pills, score chart
- PDF session report download button
- Source citations collapsible under each answer

### 7. LangSmith Tracing
- Toggle via `LANGCHAIN_TRACING_V2=true` in `.env`
- Zero code changes required — purely env-flag driven

### 8. PDF Export
- ReportLab-generated session performance report
- Includes: score summary, topic coverage, weak areas, score history table

---

## Project Structure

```
ai_tutor/
├── config/
│   ├── __init__.py
│   ├── settings.py          # Pydantic-settings config singleton
│   └── llm_factory.py       # LiteLLM-backed LLM factory
│
├── ingest/
│   ├── __init__.py
│   ├── loaders.py           # PDF / DOCX / TXT loaders
│   ├── chunker.py           # RecursiveCharacterTextSplitter
│   ├── vector_store.py      # ChromaDB manager + deduplication
│   └── pipeline.py          # High-level ingest_file / ingest_directory
│
├── rag/
│   ├── __init__.py
│   ├── hyde.py              # HyDE query expansion
│   ├── compressor.py        # Cross-encoder re-ranking + LLM compression
│   └── pipeline.py          # Full RAG pipeline
│
├── nlp/
│   ├── __init__.py
│   └── processor.py         # spaCy NLP + intent + Bloom's tagger
│
├── agents/
│   ├── __init__.py
│   ├── state.py             # TutorState TypedDict
│   ├── planner.py           # Planner agent node
│   ├── retriever.py         # Retriever agent node
│   ├── quiz_generator.py    # QuizGenerator agent node
│   ├── evaluator.py         # Evaluator agent node
│   └── graph.py             # LangGraph wiring + run_tutor()
│
├── ui/
│   ├── __init__.py
│   ├── app.py               # Streamlit chat application
│   └── exporter.py          # ReportLab PDF report generator
│
├── tests/
│   ├── __init__.py
│   ├── test_nlp.py
│   ├── test_ingest.py
│   └── test_agents.py
│
├── exports/                 # Generated PDF reports
├── chroma_db/               # ChromaDB persistent store (gitignored)
├── docs/                    # Drop study documents here for `make ingest`
│
├── .env.example
├── requirements.txt
├── Makefile
├── README.md
└── ARCHITECTURE.md
```

---

## Quick Start

### 1. Clone and install

```bash
git clone <repo-url>
cd ai_tutor
make setup          # installs deps + downloads spaCy model
```

### 2. Configure environment

```bash
cp .env.example .env
# Edit .env — at minimum set OPENAI_API_KEY
```

### 3. Ingest your documents

```bash
mkdir docs
cp /path/to/your/notes.pdf docs/
make ingest                    # ingests everything in ./docs
# OR
make ingest-file FILE=notes.pdf
```

### 4. Launch the tutor

```bash
make run
# Opens http://localhost:8501
```

---

## Configuration

All settings are in `.env`. Key variables:

| Variable | Default | Description |
|---|---|---|
| `OPENAI_API_KEY` | — | Required |
| `LLM_MODEL` | `gpt-4o` | Any LiteLLM model string |
| `EMBEDDING_MODEL` | `text-embedding-3-small` | OpenAI embedding model |
| `CHUNK_SIZE` | `512` | Characters per chunk |
| `CHUNK_OVERLAP` | `64` | Overlap between chunks |
| `MMR_K` | `6` | Chunks returned to LLM |
| `MMR_FETCH_K` | `20` | Candidates for MMR + re-ranking |
| `RELEVANCE_THRESHOLD` | `0.35` | Min cosine similarity to include chunk |
| `LANGCHAIN_TRACING_V2` | `false` | Enable LangSmith tracing |
| `LANGCHAIN_API_KEY` | — | LangSmith API key |

### Swapping the LLM

Change `LLM_MODEL` in `.env` to any LiteLLM-supported model:

```bash
LLM_MODEL=gemini/gemini-1.5-pro          # Google Gemini
LLM_MODEL=anthropic/claude-3-5-sonnet-20241022  # Anthropic
LLM_MODEL=ollama/llama3                  # Local Ollama
```

No code changes required.

---

## Usage

### Chat commands

| What you type | What happens |
|---|---|
| `What is osmosis?` | Factual retrieval (Ask mode) |
| `Explain how DNA replication works` | Socratic explanation (Explain mode) |
| `Quiz me on photosynthesis` | Generates MCQ or short-answer |
| `B` (after a quiz) | Evaluates your MCQ answer |
| `Osmosis is the movement of water across a membrane` | Evaluates your short-answer |
| `Explain it again` | Re-explanation (especially after low score) |

### Uploading documents

Use the **sidebar uploader** or drop files into `docs/` and run `make ingest`.

---

## Make Commands

```bash
make setup          # Install deps + spaCy model
make run            # Launch Streamlit UI
make run-dev        # Launch with auto-reload
make ingest         # Ingest ./docs directory
make ingest-file FILE=path/to/file.pdf
make kb-stats       # Show knowledge base stats
make test           # Run full test suite
make test-nlp       # NLP tests only
make test-ingest    # Ingestion tests only
make test-agents    # Agent tests only
make test-cov       # Tests with coverage report
make lint           # Run ruff linter
make clean          # Remove caches
make clean-db       # Delete ChromaDB (with confirmation)
make clean-exports  # Delete generated PDFs
```

---

## LangSmith Tracing

Enable full distributed tracing for every LangGraph node, LLM call, and retrieval step:

```bash
# In .env
LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY=ls__your_key_here
LANGCHAIN_PROJECT=ai-tutor-agent
```

View traces at [smith.langchain.com](https://smith.langchain.com). Each conversation turn creates a full trace tree showing:
- Planner routing decision
- HyDE expansion token cost
- MMR retrieval latency + chunk scores
- Cross-encoder re-ranking scores
- LLM answer generation

---

## PDF Report Export

Click **"Download PDF Report"** in the sidebar at any time. The report includes:
- Session summary (student name, date, turns)
- Quiz performance table (avg, best, worst score)
- Topics covered
- Weak areas flagged
- Score history bar breakdown

---

## Testing

```bash
make test           # all tests
make test-cov       # with HTML coverage report at htmlcov/index.html
```

Tests are designed to run **without API keys** — all LLM and vector-store calls are mocked.

```bash
pytest tests/test_nlp.py -v      # 14 pure-Python tests, ~0.1s
pytest tests/test_ingest.py -v   # chunker tests, no external calls
pytest tests/test_agents.py -v   # routing + scoring tests, mocked LLM
```
=======
# AI_TUTOR
A multi-agent AI tutoring system with adaptive quizzing and Socratic learning powered by LLMs
>>>>>>> a6eebc7f48a7eae3214c3e6b85406def4cc627ce
