# ─────────────────────────────────────────────────────────────────────────────
# AI Tutor Agent — Makefile
# ─────────────────────────────────────────────────────────────────────────────
.PHONY: install spacy run ingest test lint clean help

PYTHON     ?= python3
PIP        ?= pip3
APP_FILE   := ui/app.py
DOCS_DIR   ?= ./docs
PORT       ?= 8501

help:   ## Show this help message
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
	  awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-18s\033[0m %s\n", $$1, $$2}'

# ── Setup ─────────────────────────────────────────────────────────────────────
install:  ## Install all Python dependencies
	$(PIP) install --upgrade pip
	$(PIP) install -r requirements.txt

spacy:    ## Download spaCy English model
	$(PYTHON) -m spacy download en_core_web_sm

setup: install spacy  ## Full setup (install + spaCy model)
	@cp -n .env.example .env || true
	@echo "✅ Setup complete. Edit .env with your API keys."

# ── Development ───────────────────────────────────────────────────────────────
run:      ## Launch the Streamlit UI
	$(PYTHON) -m streamlit run $(APP_FILE) \
	  --server.port $(PORT) \
	  --server.headless true \
	  --browser.gatherUsageStats false

run-dev:  ## Launch with auto-reload
	$(PYTHON) -m streamlit run $(APP_FILE) \
	  --server.port $(PORT) \
	  --server.runOnSave true

# ── Ingestion ─────────────────────────────────────────────────────────────────
ingest:   ## Ingest all documents from DOCS_DIR (default: ./docs)
	@echo "📥 Ingesting documents from $(DOCS_DIR)…"
	$(PYTHON) -c "from ingest.pipeline import ingest_directory; \
	  results = ingest_directory('$(DOCS_DIR)'); \
	  [print(f\"  ✅ {r['source']}: {r['chunks_ingested']} chunks\") for r in results]; \
	  print(f\"\n📚 Total files processed: {len(results)}\")"

ingest-file:  ## Ingest a single FILE=path/to/file.pdf
	@echo "📥 Ingesting $(FILE)…"
	$(PYTHON) -c "from ingest.pipeline import ingest_file; \
	  r = ingest_file('$(FILE)'); \
	  print(f\"✅ {r['source']}: {r['chunks_ingested']} new chunks ingested\")"

kb-stats: ## Show knowledge base statistics
	$(PYTHON) -c "from ingest.pipeline import get_kb_stats; \
	  s = get_kb_stats(); \
	  print(f\"Total chunks: {s['total_chunks']}\"); \
	  print(f\"Sources: {', '.join(s['unique_sources']) or 'none'}\")"

# ── Testing ───────────────────────────────────────────────────────────────────
test:     ## Run the full test suite
	$(PYTHON) -m pytest tests/ -v --tb=short

test-nlp: ## Run only NLP tests
	$(PYTHON) -m pytest tests/test_nlp.py -v

test-ingest: ## Run only ingestion tests
	$(PYTHON) -m pytest tests/test_ingest.py -v

test-agents: ## Run only agent tests
	$(PYTHON) -m pytest tests/test_agents.py -v

test-cov: ## Run tests with coverage report
	$(PYTHON) -m pytest tests/ --cov=. --cov-report=term-missing --cov-report=html

# ── Linting / formatting ──────────────────────────────────────────────────────
lint:     ## Run ruff linter
	$(PYTHON) -m ruff check . || true

format:   ## Auto-format with black
	$(PYTHON) -m black . || true

# ── Cleanup ───────────────────────────────────────────────────────────────────
clean:    ## Remove caches and build artifacts
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .pytest_cache -exec rm -rf {} + 2>/dev/null || true
	find . -name "*.pyc" -delete 2>/dev/null || true
	find . -name ".coverage" -delete 2>/dev/null || true

clean-db: ## ⚠ Delete ChromaDB vector store (irreversible)
	@read -p "Delete chroma_db/ ? [y/N] " confirm && \
	  [ "$$confirm" = "y" ] && rm -rf chroma_db/ && echo "✅ Deleted." || echo "Aborted."

clean-exports: ## Delete generated PDF reports
	rm -f exports/*.pdf && echo "✅ Exports cleared."
