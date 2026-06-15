"""
Research store — intermediate Markdown reports produced by the researcher agent.

Files live in RESEARCH_DIR (under the persistent /data volume) and are NOT
exposed through the /files download route: they are an internal hand-off
artifact between the researcher and the document-creator agent, not a
user-facing deliverable.

Path handling mirrors routers/files._safe_path to prevent traversal: no '/',
'\\' or '..' in names (risk mitigation §6).
"""
from __future__ import annotations

import re
from datetime import datetime, timezone

from app.config import RESEARCH_DIR
from app.logging_config import logger


def _safe_research_path(filename: str):
    if "/" in filename or "\\" in filename or ".." in filename:
        raise ValueError("Invalid report name.")
    path = RESEARCH_DIR / filename
    return path


def save_research(nombre: str, contenido_md: str) -> str:
    """Persist a structured Markdown research report and return its filename."""
    safe_name = re.sub(r"[^\w\-]", "_", nombre) or "research"
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    filename = f"{safe_name}_{timestamp}.md"
    dest = RESEARCH_DIR / filename
    dest.write_text(contenido_md, encoding="utf-8")
    logger.info("Research saved: %s (%d bytes)", filename, dest.stat().st_size)
    return filename


def read_research(filename: str) -> str:
    """Read a previously saved research report by filename."""
    path = _safe_research_path(filename)
    if not path.exists():
        # Tolerate the agent passing a name without extension.
        alt = _safe_research_path(f"{filename}.md")
        if alt.exists():
            path = alt
        else:
            return f"The research report '{filename}' was not found."
    return path.read_text(encoding="utf-8")


def list_research() -> list[str]:
    if not RESEARCH_DIR.exists():
        return []
    files = [f for f in RESEARCH_DIR.iterdir() if f.is_file() and f.suffix == ".md"]
    files.sort(key=lambda f: f.stat().st_mtime, reverse=True)
    return [f.name for f in files]
