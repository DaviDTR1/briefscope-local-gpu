# BriefScope — LOCAL GPU

**Document-analysis agent for the [QueAI](https://github.com/queai-project/QueAI)
kernel.** Upload your documents, ask questions about them, and let the agent
research, summarize and generate downloadable deliverables — running **fully
offline with NVIDIA GPU acceleration**: the LLM runs in a bundled Ollama
container exposed to the GPU, and embeddings run locally via sentence-transformers.

> This is the **LOCAL GPU** variant. It requires an NVIDIA GPU and the NVIDIA
> Container Toolkit. By default it needs **no API keys and no internet** once
> the model and embedding weights are downloaded. It can optionally be pointed
> at a cloud provider from the Settings UI. For other backends see the
> [other variants](#other-variants).

---

## What it does

- **Projects** — group documents and conversations into isolated workspaces.
- **Document ingestion** — extract text from PDF, DOCX, XLSX, TXT, MD and more,
  with token counting per document.
- **Adaptive retrieval** — for a small corpus the agent reads the full context;
  once the corpus crosses a configurable token threshold it switches to **RAG**
  (vector search over ChromaDB) and retrieves the most relevant chunks.
- **Multi-agent orchestration** — an orchestrator delegates to a creator agent
  to research and produce deliverables.
- **File generation** — produces downloadable PDF, DOCX, PPTX, XLSX, MD and TXT
  files through two complementary engines (see [File generation](#file-generation)).
- **Streaming chat** — responses stream over Server-Sent Events; conversation
  history is kept and automatically compacted to save tokens.
- **Bilingual UI** — Spanish/English switch in the frontend.

## Architecture

```
client → Traefik (PathPrefix /api/briefscope_local_gpu) → FastAPI app
                                                            ├── Ollama (LLM, bundled container, NVIDIA GPU)
                                                            ├── ChromaDB (vector store, bundled container)
                                                            └── sentence-transformers (embeddings, in-process)
```

- **Backend**: FastAPI (`app/`), SQLAlchemy for project/conversation metadata
  (SQLite under `data/`), served by uvicorn on port `8080`.
- **LLM**: a bundled `ollama/ollama` container (`briefscope_ollama_gpu`) with
  the GPU reserved via Docker's `deploy.resources` (NVIDIA driver), reached over
  HTTP on the shared `queai_network`.
- **Vector store**: a bundled `chromadb/chroma` container
  (`briefscope_chroma_gpu`). Data persists in its own Docker volume.
- **Embeddings**: sentence-transformers, run in-process via ChromaDB.
- **Frontend**: a React (Vite + TypeScript) single-page app served from
  `frontend_dist/` at `/ui`.

Key REST routes (all under the plugin root path `/api/briefscope_local_gpu`):

| Route | Purpose |
|---|---|
| `/health` | Healthcheck used by the kernel |
| `/ui` | Single-page frontend |
| `/projects` | Create / list / delete projects |
| `/documents` | Upload and manage documents |
| `/chat` | Streaming chat (SSE) |
| `/config` | Read / update configuration (model, embedding, RAG, history) |
| `/files` | Download generated deliverables |

## Requirements

- A running [QueAI](https://github.com/queai-project/QueAI) kernel (Docker +
  Docker Compose v2).
- An **NVIDIA GPU** and the **NVIDIA Container Toolkit**
  ([install guide](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/install-guide.html)).
- Enough VRAM for the chosen Ollama model (the default `llama3.2` needs ~2 GB).
- Internet access **only** on first use, to download the model and embedding
  weights. After that it runs offline.

## Install

### As a QueAI plugin (recommended)

1. Make this plugin available to your kernel (clone it into the kernel's
   `plugins/` directory, or install it from the marketplace if registered).
2. Open the kernel hub at `http://localhost:8473/manager/`.
3. Find **BriefScope LOCAL GPU** in the catalog and install it.
4. Open the plugin UI. It works out of the box; use **Settings** to change the
   Ollama model or the embedding model.

### Standalone (development)

```bash
docker compose up -d --build
```

This brings up the app, GPU-enabled Ollama and ChromaDB on the external
`queai_network`. The app expects that network to exist (the kernel creates it);
create it manually with `docker network create queai_network` if you run the
plugin on its own.

## Configuration

Runtime parameters are entered through the plugin **Settings** UI and persisted
to `data/config.json` (which survives container restarts via the plugin's Docker
volume). A `.env.example` documents the environment defaults and recommended
models.

`docker-compose.yml` sets these environment variables automatically — do not
change them:

| Variable | Value | Meaning |
|---|---|---|
| `ROOT_PATH` | `/api/briefscope_local_gpu` | Traefik path prefix / FastAPI `root_path` |
| `LLM_MODE` | `local` | Selects the local (Ollama) path |
| `OLLAMA_HOST` | `http://briefscope_ollama_gpu:11434` | Bundled GPU Ollama container |

Tunable from the Settings UI:

- **Ollama model** — downloaded automatically on first use if not present.
  Recommended GPU models are listed in `.env.example`
  (`llama3.2`, `phi4-mini`, `mistral`, `deepseek-r1:7b`, up to `llama3.1:70b`
  for high-end GPUs).
- **Embedding model** — local sentence-transformers model used for document
  search. Recommended models (English and multilingual) are listed in
  `.env.example`. **Changing it invalidates previously indexed documents —
  re-upload them** so they are re-embedded with the new model.
- **RAG token threshold**, **RAG top-K**, **history compaction**.

## File generation

Two engines work together:

- **Rapid mode (Markdown-based)** — the agent writes Markdown, then converts:
  pandoc → DOCX, WeasyPrint → PDF (full Unicode + CSS), `markdown` → HTML.
- **Code mode (Python)** — the agent runs reportlab / python-docx /
  python-pptx / openpyxl to produce PDF, DOCX, PPTX and XLSX with precise
  layout.

Generated files are written under `generated/` and offered through the `/files`
download route in the UI.

## Building the frontend from source

The UI is built from the shared `briefscope-frontend` project:

```bash
cd ../briefscope-frontend
npm install
npm run build      # type-check + production build into dist/
```

Copy the `dist/` output into this plugin's `frontend_dist/` so it ships inside
the container image.

## Other variants

BriefScope ships in four interchangeable variants — same UI and features,
different LLM/embedding backend:

| Variant | LLM & embeddings | Keys / internet |
|---|---|---|
| **LOCAL GPU** (this one) | Ollama + local sentence-transformers (NVIDIA GPU) | none, offline |
| LOCAL CPU | Ollama + local sentence-transformers (CPU) | none, offline |
| CLOUD OpenAI | OpenAI GPT + OpenAI embeddings | OpenAI key, outbound |
| CLOUD Gemini | Google Gemini + Google embeddings | Google key, outbound |

## Documentation & policies

- [CHANGELOG.md](CHANGELOG.md)
- [CONTRIBUTING.md](CONTRIBUTING.md)
- [SECURITY.md](SECURITY.md)
- [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md)
- QueAI plugin contract: [PLUGIN_DEVELOPMENT.md](https://github.com/queai-project/QueAI/blob/main/docs/PLUGIN_DEVELOPMENT.md)

## License

MIT — see [LICENSE](LICENSE).
