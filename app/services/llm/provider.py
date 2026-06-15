"""
Unified LLM provider factory (LangChain).

Single source of truth for building a chat model, regardless of backend:
Anthropic, OpenAI, Google Gemini (cloud) or Ollama (local). Because every
provider is returned as a LangChain ``BaseChatModel``, the rest of the agent
code (runtime, tools, orchestration) is completely provider-agnostic — there
is no separate "cloud loop" and "local loop" anymore.

This is the file (together with requirements.txt) that differs between the
cloud and local plugin variants: the cloud variant does not ship
``langchain-ollama``; the local variants do. Everything else in app/agents/
and app/services/ is identical across the three variants.
"""
from __future__ import annotations

from typing import Any

import httpx

from app import config


def build_llm(*, temperature: float = 0.3, max_tokens: int = 4096) -> Any:
    """Return a LangChain chat model for the configured provider.

    Raises ValueError with a user-facing message when a required API key is
    missing or the provider is unknown (surfaced to the UI as an error event).
    """
    mode = config.get("llm_mode", "cloud")
    if mode == "local":
        return _build_ollama(temperature)

    provider = config.get("cloud_provider", "anthropic")
    model_name = config.get("cloud_model", "")
    return _build_cloud(provider, model_name, temperature, max_tokens)


def _build_cloud(provider: str, model_name: str, temperature: float, max_tokens: int) -> Any:
    if provider == "anthropic":
        api_key = config.get("anthropic_api_key", "")
        if not api_key:
            raise ValueError("[Error: Anthropic API key not configured. Go to Settings.]")
        from langchain_anthropic import ChatAnthropic
        return ChatAnthropic(
            model=model_name or "claude-4-5-haiku",
            api_key=api_key,
            max_tokens=max_tokens,
            temperature=temperature,
        )
    if provider == "openai":
        api_key = config.get("openai_api_key", "")
        if not api_key:
            raise ValueError("[Error: OpenAI API key not configured. Go to Settings.]")
        from langchain_openai import ChatOpenAI
        return ChatOpenAI(
            model=model_name or "gpt-4o-mini",
            api_key=api_key,
            temperature=temperature,
            streaming=True,
        )
    if provider == "google":
        api_key = config.get("google_api_key", "")
        if not api_key:
            raise ValueError("[Error: Google API key not configured. Go to Settings.]")
        from langchain_google_genai import ChatGoogleGenerativeAI
        return ChatGoogleGenerativeAI(
            model=model_name or "gemini-2.5-flash",
            google_api_key=api_key,
            temperature=temperature,
        )
    raise ValueError(
        f"[Error: unknown cloud provider '{provider}'. Configure it in Settings.]"
    )


def _build_ollama(temperature: float) -> Any:
    host = config.get("ollama_host", "http://localhost:11434")
    model = config.get("ollama_model", "")
    try:
        from langchain_ollama import ChatOllama
    except ImportError as exc:  # pragma: no cover - only in cloud variant
        raise ValueError(
            "[Error: langchain-ollama is not installed in this variant. "
            "Use a LOCAL build of BriefScope.]"
        ) from exc
    return ChatOllama(
        model=model or "llama3.1",
        base_url=host,
        temperature=temperature,
    )


def supports_nested_tool_calling() -> bool:
    """Best-effort capability check used to auto-select the orchestration mode.

    Nested tool-calling (an orchestrator that calls sub-agents which themselves
    call tools) is reliable on frontier cloud models but flaky or unsupported on
    most local/Ollama models. When this returns False the runtime falls back to
    the deterministic pipeline flow (plan §6 risk mitigation).
    """
    mode = config.get("llm_mode", "cloud")
    if mode == "local":
        # Local Ollama models: assume weak nested tool-calling by default.
        return False

    provider = config.get("cloud_provider", "anthropic")
    model = (config.get("cloud_model", "") or "").lower()

    if provider == "anthropic":
        # Claude 3.x/4.x handle nested tool use well.
        return True
    if provider == "openai":
        # gpt-4o / gpt-4.1 / o-series handle it; older 3.5 is unreliable.
        return not model.startswith("gpt-3.5")
    if provider == "google":
        # Gemini 1.5 flash/pro nested tool use is unreliable; 2.x is solid.
        return "2." in model or "2-" in model
    return False


async def list_ollama_models() -> list[str]:
    """List available Ollama models (used by the local variants' config UI)."""
    host = config.get("ollama_host", "http://localhost:11434")
    try:
        async with httpx.AsyncClient(timeout=50) as client:
            r = await client.get(f"{host}/api/tags")
            r.raise_for_status()
            return [m["name"] for m in r.json().get("models", [])]
    except Exception:
        return []
