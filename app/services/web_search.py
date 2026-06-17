"""
Web search backend.

Provider-agnostic DuckDuckGo search via the standalone ``ddgs`` package, wrapped
so the multi-agent runtime can expose it as a LangChain StructuredTool. No API
key is required and it works the same whatever chat provider is configured, which
keeps the shared agent runtime fully provider-agnostic. In the local variants the
creator agent uses it to look up document-design references (palettes, fonts,
layouts, quality guides).
"""
from __future__ import annotations

from app.logging_config import logger


def search_web(query: str, max_results: int = 5) -> str:
    """Run a DuckDuckGo text search and return a numbered, model-friendly digest.

    Always returns a string (never raises): import errors, network failures and
    empty results are reported as readable text the agent can reason about.
    """
    query = (query or "").strip()
    if not query:
        return "Empty query: provide search terms to look up on the web."

    try:
        from ddgs import DDGS
    except ImportError:
        logger.error("ddgs package not installed — web search unavailable")
        return (
            "Web search is unavailable: the 'ddgs' dependency is not installed "
            "in this deployment."
        )

    try:
        results = DDGS().text(query, max_results=max_results)
    except Exception as exc:  # network, rate-limit, parsing…
        logger.exception("Web search failed for %r: %s", query, exc)
        return f"Web search failed: {exc}"

    results = list(results or [])
    if not results:
        return f"No web results were found for: '{query}'."

    lines = [f"Web results for '{query}':", ""]
    for i, r in enumerate(results, 1):
        title = (r.get("title") or "").strip()
        href = (r.get("href") or r.get("url") or "").strip()
        body = (r.get("body") or "").strip()
        lines.append(f"{i}. {title}")
        if href:
            lines.append(f"   {href}")
        if body:
            lines.append(f"   {body}")
    return "\n".join(lines)
