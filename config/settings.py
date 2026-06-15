"""
config/settings.py
──────────────────
Single source of truth for all configuration.
Uses pydantic-settings so every value can be overridden via environment
variables or a .env file — no magic strings scattered across the codebase.
"""

from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ── LLM ──────────────────────────────────────────────────────────────────
    openai_api_key: str = Field(default="", alias="OPENAI_API_KEY")
    llm_model: str = Field(default="gpt-4o", alias="LLM_MODEL")
    llm_temperature: float = Field(default=0.3, alias="LLM_TEMPERATURE")
    llm_max_tokens: int = Field(default=2048, alias="LLM_MAX_TOKENS")

    # ── Embeddings ────────────────────────────────────────────────────────────
    embedding_model: str = Field(
        default="text-embedding-3-small", alias="EMBEDDING_MODEL"
    )

    # ── ChromaDB ─────────────────────────────────────────────────────────────
    chroma_persist_dir: str = Field(
        default="./chroma_db", alias="CHROMA_PERSIST_DIR"
    )
    chroma_collection: str = Field(
        default="ai_tutor_docs", alias="CHROMA_COLLECTION"
    )

    # ── RAG ──────────────────────────────────────────────────────────────────
    chunk_size: int = Field(default=512, alias="CHUNK_SIZE")
    chunk_overlap: int = Field(default=64, alias="CHUNK_OVERLAP")
    mmr_k: int = Field(default=6, alias="MMR_K")
    mmr_fetch_k: int = Field(default=20, alias="MMR_FETCH_K")
    relevance_threshold: float = Field(default=0.35, alias="RELEVANCE_THRESHOLD")

    # ── LangSmith ─────────────────────────────────────────────────────────────
    langchain_tracing_v2: bool = Field(default=False, alias="LANGCHAIN_TRACING_V2")
    langchain_api_key: str = Field(default="", alias="LANGCHAIN_API_KEY")
    langchain_project: str = Field(
        default="ai-tutor-agent", alias="LANGCHAIN_PROJECT"
    )

    # ── Export ────────────────────────────────────────────────────────────────
    export_dir: str = Field(default="./exports", alias="EXPORT_DIR")

    # ── Streamlit ─────────────────────────────────────────────────────────────
    streamlit_port: int = Field(default=8501, alias="STREAMLIT_PORT")

    @field_validator("openai_api_key")
    @classmethod
    def warn_if_missing_key(cls, v: str) -> str:
        if not v:
            import warnings
            warnings.warn(
                "OPENAI_API_KEY is not set. LLM calls will fail.",
                stacklevel=2,
            )
        return v

    def configure_langsmith(self) -> None:
        """Push LangSmith env vars so LangChain picks them up automatically."""
        if self.langchain_tracing_v2:
            os.environ["LANGCHAIN_TRACING_V2"] = "true"
            os.environ["LANGCHAIN_API_KEY"] = self.langchain_api_key
            os.environ["LANGCHAIN_PROJECT"] = self.langchain_project
        else:
            os.environ["LANGCHAIN_TRACING_V2"] = "false"

    @property
    def chroma_persist_path(self) -> Path:
        p = Path(self.chroma_persist_dir)
        p.mkdir(parents=True, exist_ok=True)
        return p

    @property
    def export_path(self) -> Path:
        p = Path(self.export_dir)
        p.mkdir(parents=True, exist_ok=True)
        return p


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return a cached Settings singleton."""
    settings = Settings()
    settings.configure_langsmith()
    return settings
