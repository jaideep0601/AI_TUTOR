"""
config/llm_factory.py
─────────────────────
Thin factory that returns a LangChain-compatible ChatLiteLLM instance.
Swapping the underlying model is a one-line .env change (LLM_MODEL=...).

Supported LiteLLM prefixes (examples):
  gpt-4o                  → OpenAI
  gemini/gemini-1.5-pro   → Google
  anthropic/claude-3-5-sonnet-20241022  → Anthropic
  ollama/llama3           → local Ollama
"""

from __future__ import annotations

from langchain_community.chat_models import ChatLiteLLM

from config.settings import get_settings


def get_llm(
    temperature: float | None = None,
    max_tokens: int | None = None,
    streaming: bool = False,
) -> ChatLiteLLM:
    """
    Return a ChatLiteLLM instance configured from settings.

    Args:
        temperature: Override LLM_TEMPERATURE from settings.
        max_tokens:  Override LLM_MAX_TOKENS from settings.
        streaming:   Enable token streaming (used by Streamlit callbacks).
    """
    cfg = get_settings()
    return ChatLiteLLM(
        model=cfg.llm_model,
        temperature=temperature if temperature is not None else cfg.llm_temperature,
        max_tokens=max_tokens if max_tokens is not None else cfg.llm_max_tokens,
        streaming=streaming,
        api_key=cfg.openai_api_key,
    )
