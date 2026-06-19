"""
RAG service using ChromaDB with embeddings computed by Ollama.

Embeddings are produced by the bundled Ollama server (`/api/embed`) instead of
sentence-transformers, so the local image stays small (no torch) and CPU setups
can use a light model such as `nomic-embed-text`. We compute the vectors here and
pass them to ChromaDB explicitly, so Chroma never needs its own embedding model.
On the GPU variant Ollama uses the NVIDIA GPU automatically, so embedding also
benefits from GPU acceleration.

The embedding model is configurable ("embedding_model" / EMBEDDING_MODEL env) and
is pulled into Ollama on first use if not already present. Switching the model
invalidates previously indexed documents (vector dimensions differ) — re-upload
them so they are re-embedded with the new model.
"""
from __future__ import annotations

from typing import List
import httpx
import chromadb
from app.config import CHROMA_HOST, CHROMA_PORT
from app import config as _cfg

_DEFAULT_EMBED_MODEL = "nomic-embed-text"

_client: chromadb.ClientAPI | None = None
# Embedding models already confirmed present / pulled in Ollama (per process).
_pulled: set[str] = set()


def _get_client() -> chromadb.ClientAPI:
    global _client
    if _client is None:
        _client = chromadb.HttpClient(host=CHROMA_HOST, port=CHROMA_PORT)
    return _client


def _embed_model() -> str:
    return _cfg.get("embedding_model", _DEFAULT_EMBED_MODEL) or _DEFAULT_EMBED_MODEL


def _ollama_host() -> str:
    return (_cfg.get("ollama_host", "http://localhost:11434") or "").rstrip("/")


def _ensure_model(host: str, model: str) -> None:
    """Pull the embedding model into Ollama once if it is not present yet.

    Mirrors the LLM behaviour ("downloaded automatically on first use"). Best
    effort: if the check or pull fails we let the embed call surface the real
    error instead of masking it.
    """
    if model in _pulled:
        return
    try:
        with httpx.Client(timeout=30) as c:
            tags = c.get(f"{host}/api/tags").json().get("models", [])
        present: set[str] = set()
        for m in tags:
            name = m.get("name", "")
            present.add(name)
            present.add(name.split(":")[0])
        if model not in present and model.split(":")[0] not in present:
            # Streaming pull; wait for completion (first use only, can take a while).
            with httpx.Client(timeout=None) as c:
                c.post(f"{host}/api/pull", json={"model": model, "stream": False})
    except Exception:
        pass
    _pulled.add(model)


def _embed(texts: List[str]) -> List[List[float]]:
    """Compute embeddings for a batch of texts via Ollama's /api/embed."""
    if not texts:
        return []
    host, model = _ollama_host(), _embed_model()
    _ensure_model(host, model)
    with httpx.Client(timeout=300) as c:
        r = c.post(f"{host}/api/embed", json={"model": model, "input": texts})
        r.raise_for_status()
        data = r.json()
    return data["embeddings"]


def _collection_name(project_id: int) -> str:
    return f"project_{project_id}"


def _chunk_text(text: str, chunk_size: int | None = None, overlap: int | None = None) -> List[str]:
    chunk_size = chunk_size or _cfg.get("rag_chunk_size", 1200)
    overlap    = overlap    or _cfg.get("rag_chunk_overlap", 200)
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        start += chunk_size - overlap
    return chunks


def index_document(project_id: int, document_id: int, filename: str, text: str) -> None:
    client = _get_client()
    col = client.get_or_create_collection(name=_collection_name(project_id))
    chunks = _chunk_text(text)
    if not chunks:
        return
    ids = [f"doc{document_id}_chunk{i}" for i in range(len(chunks))]
    metadatas = [{"document_id": document_id, "filename": filename, "chunk": i}
                 for i in range(len(chunks))]
    embeddings = _embed(chunks)
    col.upsert(ids=ids, documents=chunks, embeddings=embeddings, metadatas=metadatas)


def delete_document(project_id: int, document_id: int) -> None:
    client = _get_client()
    try:
        col = client.get_collection(name=_collection_name(project_id))
        col.delete(where={"document_id": document_id})
    except Exception:
        pass


def delete_project(project_id: int) -> None:
    client = _get_client()
    try:
        client.delete_collection(_collection_name(project_id))
    except Exception:
        pass


def retrieve(project_id: int, query: str, top_k: int | None = None) -> List[dict]:
    top_k = top_k or _cfg.get("rag_top_k", 15)
    client = _get_client()
    try:
        col = client.get_collection(name=_collection_name(project_id))
    except Exception:
        return []
    count = col.count()
    if count == 0:
        return []
    query_embeddings = _embed([query])
    results = col.query(query_embeddings=query_embeddings, n_results=min(top_k, count))
    if not results or not results["documents"]:
        return []
    items = []
    for doc, meta in zip(results["documents"][0], results["metadatas"][0]):
        items.append({
            "filename": meta.get("filename", ""),
            "chunk":    meta.get("chunk", 0),
            "text":     doc,
        })
    return items


def format_rag_context(chunks: List[dict]) -> str:
    parts = []
    for i, c in enumerate(chunks, 1):
        header = '  <fragmento id="' + str(i) + '" archivo="' + c["filename"] + '" chunk="' + str(c["chunk"]) + '">'
        frag = header + "\n" + c["text"] + "\n  </fragmento>"
        parts.append(frag)
    return "<fragmentos_relevantes>\n" + "\n".join(parts) + "\n</fragmentos_relevantes>"
