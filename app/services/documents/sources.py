"""
Read full SOURCE documents (the files the user uploaded) on demand.

Unlike ``store.read_generated`` — which reads documents the agent *generated* —
this reads the ORIGINAL uploaded documents straight from the database
(``Document.content_text``), scoped to the project.

A whole document is returned when it fits within the per-read character budget
(``source_read_max_chars``). Larger documents (e.g. a full book) are served in
sequential parts so an agent can read the entire work across several calls; RAG
search (``buscar_en_documentos``) remains available for targeted lookups.
"""
from __future__ import annotations

import math
import re

from app import config
from app import models
from app.database import SessionLocal


def _match(docs: list, nombre: str):
    """Find an uploaded document by name (exact, then ignoring extension, then
    as a substring). Returns the matched Document or None."""
    target = (nombre or "").strip().lower()
    if not target:
        return None
    for d in docs:                                    # exact filename
        if d.filename.lower() == target:
            return d
    stem = re.sub(r"\.[^.]+$", "", target)
    for d in docs:                                    # match ignoring extension
        if re.sub(r"\.[^.]+$", "", d.filename.lower()) == stem:
            return d
    for d in docs:                                    # substring fallback
        if target in d.filename.lower():
            return d
    return None


def read_source_document(project_id: int, nombre: str, parte: int = 1) -> str:
    """Return the text of an uploaded source document, whole or by part.

    If the document fits within ``source_read_max_chars`` it is returned in full.
    Otherwise it is split into sequential parts and the requested ``parte`` is
    returned, with a note telling the caller how to read the next part.
    """
    max_chars = int(config.get("source_read_max_chars", 120_000))
    try:
        parte = int(parte)
    except (TypeError, ValueError):
        parte = 1

    db = SessionLocal()
    try:
        docs = (
            db.query(models.Document)
            .filter(models.Document.project_id == project_id)
            .all()
        )
        if not docs:
            return "No documents have been loaded into this project yet."

        doc = _match(docs, nombre)
        if doc is None:
            names = ", ".join(d.filename for d in docs)
            return (
                f"No source document matching '{nombre}' was found. "
                f"Available documents: {names}."
            )

        text = doc.content_text or ""
        if not text.strip():
            return (
                f"The document '{doc.filename}' has no extractable text "
                "(it may be a scanned/image PDF). Try buscar_en_documentos, or "
                "ask the user to re-upload a text-based version."
            )

        total = len(text)
        if total <= max_chars:
            return (
                f'<documento_fuente nombre="{doc.filename}" completo="true">\n'
                f"{text}\n</documento_fuente>"
            )

        total_parts = math.ceil(total / max_chars)
        parte = max(1, min(parte, total_parts))
        start = (parte - 1) * max_chars
        fragment = text[start:start + max_chars]
        if parte < total_parts:
            nav = (
                f"To continue reading, call leer_documento_fuente with "
                f"nombre='{doc.filename}' and parte={parte + 1}."
            )
        else:
            nav = "This was the LAST part — you have now read the whole document."
        return (
            f'<documento_fuente nombre="{doc.filename}" parte="{parte}" '
            f'de="{total_parts}" completo="false">\n'
            f"{fragment}\n</documento_fuente>\n"
            f"[The document is large and is delivered in {total_parts} parts. {nav}]"
        )
    finally:
        db.close()
