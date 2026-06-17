"""
Config router — reads and writes DATA_DIR/config.json via the frontend UI.

Local variant: the user can run on a local Ollama model OR on a cloud provider,
so both the Ollama fields and the cloud API keys are exposed and editable. The
active LLM mode is reported (read-only here; it comes from config / LLM_MODE env).
"""
from __future__ import annotations
from typing import List, Optional
from fastapi import APIRouter
from pydantic import BaseModel
from app import config
from app.services.llm.provider import list_ollama_models

router = APIRouter()


class ConfigOut(BaseModel):
    llm_mode:              str
    cloud_provider:        str
    cloud_model:           str
    ollama_host:           str
    ollama_model:          str
    anthropic_api_key_set: bool
    openai_api_key_set:    bool
    google_api_key_set:    bool
    cloud_ready:           bool
    embedding_model:       str
    rag_threshold_tokens:  int
    rag_top_k:             int
    history_compact_after: int
    web_search_agents:     List[str]


class ConfigUpdate(BaseModel):
    cloud_provider:        Optional[str] = None
    cloud_model:           Optional[str] = None
    ollama_host:           Optional[str] = None
    ollama_model:          Optional[str] = None
    anthropic_api_key:     Optional[str] = None
    openai_api_key:        Optional[str] = None
    google_api_key:        Optional[str] = None
    embedding_model:       Optional[str] = None
    rag_threshold_tokens:  Optional[int] = None
    rag_top_k:             Optional[int] = None
    history_compact_after: Optional[int] = None
    web_search_agents:     Optional[List[str]] = None


class ConfigStatus(BaseModel):
    llm_mode:    str
    cloud_ready: bool | None
    needs_setup: bool


@router.get("/", response_model=ConfigOut)
def get_config():
    cfg = config.all_settings()
    return ConfigOut(
        llm_mode              = cfg["llm_mode"],
        cloud_provider        = cfg["cloud_provider"],
        cloud_model           = cfg["cloud_model"],
        ollama_host           = cfg["ollama_host"],
        ollama_model          = cfg["ollama_model"],
        anthropic_api_key_set = bool(cfg.get("anthropic_api_key")),
        openai_api_key_set    = bool(cfg.get("openai_api_key")),
        google_api_key_set    = bool(cfg.get("google_api_key")),
        cloud_ready           = config.is_cloud_ready(),
        embedding_model       = cfg["embedding_model"],
        rag_threshold_tokens  = cfg["rag_threshold_tokens"],
        rag_top_k             = cfg["rag_top_k"],
        history_compact_after = cfg["history_compact_after"],
        web_search_agents     = cfg.get("web_search_agents", ["investigador"]),
    )


@router.post("/", response_model=ConfigOut)
def update_config(body: ConfigUpdate):
    changes: dict = {}
    raw = body.model_dump()
    for field in ("cloud_provider", "cloud_model", "ollama_host", "ollama_model",
                  "anthropic_api_key", "openai_api_key", "google_api_key",
                  "embedding_model",
                  "rag_threshold_tokens", "rag_top_k", "history_compact_after"):
        if raw[field] is not None:
            changes[field] = raw[field]
    if raw.get("web_search_agents") is not None:
        allowed = {"investigador", "creador"}
        changes["web_search_agents"] = [a for a in raw["web_search_agents"] if a in allowed]
    config.update(changes)
    return get_config()


@router.get("/status", response_model=ConfigStatus)
def get_status():
    cfg = config.all_settings()
    mode = cfg["llm_mode"]
    if mode == "cloud":
        ready = config.is_cloud_ready()
        needs_setup = not ready
    else:
        # Local Ollama mode is considered ready once a host/model is set.
        ready = None
        needs_setup = not bool(cfg.get("ollama_model"))
    return ConfigStatus(llm_mode=mode, cloud_ready=ready, needs_setup=needs_setup)


@router.get("/ollama/models")
async def get_ollama_models():
    return {"models": await list_ollama_models()}
