"""
RAG service using ChromaDB + sentence-transformers embeddings.
"""
from __future__ import annotations

import re
from typing import List
import chromadb
from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction
from app.config import CHROMA_HOST, CHROMA_PORT
from app import config as _cfg

_client: chromadb.ClientAPI | None = None
_embed_fn: SentenceTransformerEmbeddingFunction | None = None
_embed_model: str | None = None


def _get_client() -> chromadb.ClientAPI:
    global _client
    if _client is None:
        _client = chromadb.HttpClient(host=CHROMA_HOST, port=CHROMA_PORT)
    return _client


def _get_embed_fn() -> SentenceTransformerEmbeddingFunction:
    """Return the embedding function for the model selected in config.

    The model is configurable (config "embedding_model" / EMBEDDING_MODEL env).
    The instance is cached and rebuilt only when the selected model changes, so
    a model switch from the UI takes effect without a restart. Note that
    documents indexed with a previous model must be re-uploaded, since embedding
    dimensions differ between models.
    """
    global _embed_fn, _embed_model
    desired = _cfg.get("embedding_model", "all-MiniLM-L6-v2")
    if _embed_fn is None or _embed_model != desired:
        _embed_fn = SentenceTransformerEmbeddingFunction(
            model_name=desired, device="cpu"
        )
        _embed_model = desired
    return _embed_fn


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
    col = client.get_or_create_collection(
        name=_collection_name(project_id),
        embedding_function=_get_embed_fn(),
    )
    chunks = _chunk_text(text)
    ids = [f"doc{document_id}_chunk{i}" for i in range(len(chunks))]
    metadatas = [{"document_id": document_id, "filename": filename, "chunk": i}
                 for i in range(len(chunks))]
    col.upsert(documents=chunks, ids=ids, metadatas=metadatas)


def delete_document(project_id: int, document_id: int) -> None:
    client = _get_client()
    try:
        col = client.get_collection(
            name=_collection_name(project_id),
            embedding_function=_get_embed_fn(),
        )
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
        col = client.get_collection(
            name=_collection_name(project_id),
            embedding_function=_get_embed_fn(),
        )
    except Exception:
        return []
    results = col.query(query_texts=[query], n_results=min(top_k, col.count()))
    if not results or not results["documents"]:
        return []
    items = []
    for doc, meta in zip(results["documents"][0], results["metadat