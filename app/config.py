"""
Persistent configuration for BriefScope.

Source of truth: /data/config.json  (persists across container restarts)
Env vars: Only OLLAMA_HOST, OLLAMA_MODEL and EMBEDDING_MODEL are read — as a
          convenience for local installs. Cloud API keys are never read from env vars;
          the user sets them via the frontend UI.
"""
from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

# Paths
# App base dir = the package root (/code in the container). DATA_DIR and
# GENERATED_DIR default to paths RELATIVE to the app — not the FS root — so the
# plugin is self-contained. Both remain overridable via env vars.
BASE_DIR      = Path(__file__).resolve().parent.parent
DATA_DIR      = Path(os.getenv("DATA_DIR",      str(BASE_DIR / "data")))
GENERATED_DIR = Path(os.getenv("GENERATED_DIR", str(BASE_DIR / "generated")))
DB_PATH       = DATA_DIR / "briefscope.db"
# ChromaDB runs as a separate server reached over HTTP (HttpClient).
# Host/port are FIXED per variant — Chroma persists its own data in its container.
CHROMA_HOST   = "briefscope_chroma_gpu"
CHROMA_PORT   = 8000
CONFIG_FILE   = DATA_DIR / "config.json"
# Intermediate research reports written by the researcher agent.
# Persistent (lives under DATA_DIR) but separate from user-facing deliverables
# in GENERATED_DIR, so it is never exposed through the /files download route.
RESEARCH_DIR  = DATA_DIR / "research"

DATA_DIR.mkdir(parents=True, exist_ok=True)
GENERATED_DIR.mkdir(parents=True, exist_ok=True)
RESEARCH_DIR.mkdir(parents=True, exist_ok=True)

# Defaults — cloud keys start empty, user fills them via the UI
_DEFAULTS: dict[str, Any] = {
    "llm_mode":           os.getenv("LLM_MODE", "cloud"),
    "cloud_provider":     "anthropic",
    "cloud_model":        "claude-3-5-haiku-20241022",
    "anthropic_api_key":  "",
    "openai_api_key":     "",
    "google_api_key":     "",
    "ollama_host":        os.getenv("OLLAMA_HOST",  "http://host.docker.internal:11434"),
    "ollama_model":       os.getenv("OLLAMA_MODEL", "llama3.2"),
    # Local embedding model, computed by the bundled Ollama server (/api/embed).
    # Pulled into Ollama on first use. Selectable from the UI; recommendations
    # are listed in .env.example.
    "embedding_model":    os.getenv("EMBEDDING_MODEL", "nomic-embed-text"),
    "rag_threshold_tokens": 100_000,
    "rag_top_k":            15,
    "rag_chunk_size":       1200,
    "rag_chunk_overlap":    200,
    # Per-read character budget for leer_documento_fuente (reading a full source
    # document). Documents larger than this are served in sequential parts. Lower
    # it for models with a small context window.
    "source_read_max_chars": 120_000,
    "history_compact_after": 6,
    # --- Multi-agent orchestration ---
    # "auto":     pick the flow from model capability (default). Cloud frontier
    #             models -> agentic; local/weak models -> pipeline.
    # "agentic":  orchestrator reasons with sub-agents-as-tools.
    # "pipeline": deterministic researcher -> creator fallback for weak models
    #             that handle nested tool-calling poorly (risk mitigation seccion 6).
    "orchestration_mode":    "auto",
    "max_delegations":       4,     # global cap on sub-agent calls per turn
    "agent_max_rounds":      8,     # max tool rounds inside a single agent
    "agent_max_depth":       2,     # orchestrator -> sub-agent nesting cap
    # --- Web search ---
    # Which sub-agents may use the buscar_en_web tool WHEN the per-project web
    # search switch is ON. By default only the researcher. The user can add
    # "creador" from Settings (the creator uses it for design references). An
    # empty list disables web search for everyone.
    "web_search_agents":     ["investigador"],
}


def _load() -> dict[str, Any]:
    if CONFIG_FILE.exists():
        try:
            stored = json.loads(CONFIG_FILE.read_text(encoding="utf-8"))
            return {**_DEFAULTS, **stored}
        except Exception:
            pass
    return dict(_DEFAULTS)


def _save(cfg: dict[str, Any]) -> None:
    CONFIG_FILE.write_text(json.dumps(cfg, indent=2, ensure_ascii=False), encoding="utf-8")


# In-memory config — loaded once at import time
_cfg: dict[str, Any] = _load()


def get(key: str, default: Any = None) -> Any:
    return _cfg.get(key, default)


def all_settings() -> dict[str, Any]:
    return dict(_cfg)


def update(changes: dict[str, Any]) -> dict[str, Any]:
    """Apply partial update, persist to disk, return full config."""
    global _cfg
    _cfg.update({k: v for k, v in changes.items() if v is not None})
    _save(_cfg)
    return dict(_cfg)


def is_cloud_ready() -> bool:
    """True if the active cloud provider has an API key configured."""
    provider = get("cloud_provider", "anthropic")
    key_map = {
        "anthropic": "anthropic_api_key",
        "openai":    "openai_api_key",
        "google":    "google_api_key",
    }
    return bool(get(key_map.get(provider, ""), ""))
