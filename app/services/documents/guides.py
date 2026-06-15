"""
Knowledge guides for high-quality document generation.

Two kinds of guides live under ``prompts/guides``:

  formato/<fmt>.md  — per-format technical guide: which engine to use, the exact
                      contract each generation tool expects, and the common
                      mistakes to avoid so the file is produced without errors.

  tipo/<tipo>.md    — per-document-type playbook: how to structure a *kind* of
                      document well (professional report, presentation, invoice,
                      letter, data dashboard...). Each file declares a short
                      description in a leading ``<!-- desc: ... -->`` comment so
                      the agent can browse the catalog and load the one it needs.
"""
from __future__ import annotations

import re
from pathlib import Path

_GUIDES_DIR = Path(__file__).resolve().parent.parent.parent.parent / "prompts" / "guides"
_FORMAT_DIR = _GUIDES_DIR / "formato"
_TYPE_DIR = _GUIDES_DIR / "tipo"

_DESC_RE = re.compile(r"<!--\s*desc:\s*(.+?)\s*-->", re.IGNORECASE | re.DOTALL)


def read_format_guide(formato: str) -> str:
    """Return the full format guide for ``formato`` (pdf, docx, pptx, ...)."""
    key = formato.lower().strip().lstrip(".")
    path = _FORMAT_DIR / f"{key}.md"
    if path.is_file():
        return path.read_text(encoding="utf-8")
    available = ", ".join(sorted(p.stem for p in _FORMAT_DIR.glob("*.md"))) or "(none)"
    return (
        f"There is no format guide for '{formato}'. Available formats: {available}. "
        "Use well-structured Markdown (fast mode) or Python code (code mode)."
    )


def read_type_guide(tipo: str) -> str:
    """Return the full type guide for ``tipo`` (reporte_profesional, factura...)."""
    key = re.sub(r"[^\w]+", "_", tipo.lower().strip()).strip("_")
    path = _TYPE_DIR / f"{key}.md"
    if path.is_file():
        return path.read_text(encoding="utf-8")
    return (
        f"There is no type guide '{tipo}'.\n\n{type_guides_catalog()}\n\n"
        "If none fits, design the document with your own professional judgment."
    )


def list_type_guides() -> list[tuple[str, str]]:
    """Return [(slug, description)] for every available type guide."""
    out: list[tuple[str, str]] = []
    if not _TYPE_DIR.is_dir():
        return out
    for path in sorted(_TYPE_DIR.glob("*.md")):
        text = path.read_text(encoding="utf-8")
        m = _DESC_RE.search(text)
        desc = m.group(1).strip() if m else "(no description)"
        out.append((path.stem, desc))
    return out


def type_guides_catalog() -> str:
    """Render the type-guide catalog (slug + short description) for the prompt."""
    guides = list_type_guides()
    if not guides:
        return "No type guides available."
    lines = [f"- `{slug}` — {desc}" for slug, desc in guides]
    return "Available type guides (load with consultar_guia_tipo):\n" + "\n".join(lines)
