"""
Decides whether to use full in-context or RAG based on total document token count.
Formats document context as XML for the system prompt.
"""
from typing import List
from app import config
from app.services import rag as rag_service


def build_document_context(
    project_id: int,
    documents: List[dict],      # [{"id": int, "filename": str, "content_text": str, "token_count": int}]
    query: str,
) -> tuple[str, bool]:
    """
    Returns (xml_context, used_rag).
    - If total tokens < threshold → inject all docs in-context.
    - If total tokens >= threshold → activate RAG and inject only relevant chunks.
    """
    threshold = config.get("rag_threshold_tokens", 100_000)
    top_k     = config.get("rag_top_k", 15)
    total_tokens = sum(d["token_count"] for d in documents)

    if total_tokens < threshold:
        return _format_full_context(documents), False
    else:
        chunks = rag_service.retrieve(project_id, query, top_k=top_k)
        return rag_service.format_rag_context(chunks), True


def _format_full_context(documents: List[dict]) -> str:
    if not documents:
        return ""
    parts = []
    for doc in documents:
        parts.append(
            f'  <documento id="{doc["id"]}" nombre="{doc["filename"]}">\n'
            f'{doc["content_text"][:50000]}\n'   # safety cap at 50k chars per doc
            f'  </documento>'
        )
    return "<archivos_fuente>\n" + "\n".join(parts) + "\n</archivos_fuente>"
