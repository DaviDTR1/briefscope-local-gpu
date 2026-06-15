"""
LLM entry point for the chat router.

Drives the multi-agent system through a single, provider-agnostic runtime
(LangChain). The same code path serves Anthropic, OpenAI, Google and Ollama —
the provider is chosen inside app.services.llm.provider.

stream_chat yields raw strings consumed unchanged by routers/chat.py:
plain text, '{"__thinking__": ...}' and '{"__file_ready__": ...}' markers.
"""
from __future__ import annotations

from typing import AsyncGenerator

from app import config
from app.agents.context import RunContext
from app.agents import runtime
# Re-exported for the local plugin variants' config UI.
from app.services.llm.provider import list_ollama_models, supports_nested_tool_calling  # noqa: F401


def _resolve_mode() -> str:
    """Resolve the effective orchestration mode.

    - "agentic"  -> always orchestrator with sub-agents-as-tools.
    - "pipeline" -> always deterministic researcher -> creator flow.
    - "auto"     -> orchestrated when the active model handles nested
                    tool-calling well, otherwise pipeline (plan §6 mitigation).
    """
    mode = config.get("orchestration_mode", "auto")
    if mode == "auto":
        return "agentic" if supports_nested_tool_calling() else "pipeline"
    return mode


async def stream_chat(
    messages: list[dict],
    *,
    instructions: str = "",
    doc_context: str = "",
    doc_names: list[str] | None = None,
    project_id: int = 0,
    tools_enabled: bool = True,  # kept for signature compatibility
) -> AsyncGenerator[str, None]:
    ctx = RunContext(
        project_id=project_id,
        doc_context=doc_context,
        instructions=instructions,
        doc_names=doc_names or [],
    )
    mode = _resolve_mode()
    if mode == "pipeline":
        async for chunk in runtime.run_pipeline(messages, ctx):
            yield chunk
    else:
        async for chunk in runtime.run_orchestrated(messages, ctx):
            yield chunk
