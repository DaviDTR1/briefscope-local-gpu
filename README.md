# BriefScope — LOCAL GPU

**Document-analysis agent.** Upload your documents, ask questions about them, and
let the agent research, summarize and generate downloadable deliverables —
running **fully offline with NVIDIA GPU acceleration**: the LLM runs in a bundled
Ollama container exposed to the GPU, and embeddings run locally via
sentence-transformers.

> Runs **two ways**: as a plugin inside the
> [QueAI](https://github.com/queai-project/QueAI) kernel, or fully
> **standalone** with nothing but Docker — see
> [Run standalone (without QueAI)](#run-standalone-without-queai).

> This is the **LOCAL GPU** variant. It requires an NVIDIA GPU and the NVIDIA
> Container Toolkit. By default it needs **no API keys and no internet** once
> the model and embedding weights are downloaded — the only runtime feature that
> reaches the internet is the **optional web search**, which is off by default.
> It can optionally be pointed at a cloud provider from the Settings UI. For
> other backends see the [other variants](#other-variants).

---

## What it does

- **Projects** — group documents and conversations into isolated workspaces.
- **Document ingestion** — extract text from PDF, DOCX, XLSX, TXT, MD and more,
  with token counting per document.
- **Adaptive retrieval** — for a small corpus the agent reads the full context;
  once the corpus crosses a configurable token threshold it switches to **RAG**
  (vector search over ChromaDB) and retrieves the most relevant chunks.
- **Multi-agent orchestration** — a main agent is the only one that talks to the
  user and delegates as needed: a research agent investigates the project's
  documents (and, when enabled, the web) to produce thorough reports, and a
  creator agent turns the gathered content into polished, downloadable deliverables.
- **File generation** — produces downloadable PDF, DOCX, PPTX, XLSX, MD and TXT
  files through two complementary engines (see [File generation](#file-generation)).
- **Web search (optional)** — a per-project globe toggle next to the attachment
  (＋) button lets permitted agents pull live results from the web via DuckDuckGo
  (the `ddgs` package, no API key). Off by default; which agents may search is
  configurable in **Settings → Local → Web Search**. Using it is the only feature
  that reaches the internet at runtime.
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

- **Docker + Docker Compose v2** — that's all you need to run it.
- An **NVIDIA GPU** and the **NVIDIA Container Toolkit**
  ([install guide](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/install-guide.html)).
- Enough VRAM for the chosen Ollama model (the default `llama3.2` needs ~2 GB).
- Internet access **only** on first use, to download the model and embedding
  weights. After that it runs offline, unless you enable the optional web search.

QueAI is **optional**: it's only needed if you want to run BriefScope as a
managed plugin alongside other plugins. To run it on its own, skip straight to
[Run standalone (without QueAI)](#run-standalone-without-queai).

## Run standalone (without QueAI)

BriefScope is a self-contained FastAPI app plus bundled GPU-enabled Ollama and
ChromaDB containers. It does not need the kernel, Traefik or any other plugin to
run — only Docker and the NVIDIA Container Toolkit. No API keys are required.

```bash
# Build and start everything (app + GPU Ollama + ChromaDB)
docker compose -f docker-compose.standalone.yml up -d --build

# Then open the UI
#    http://localhost:8080/ui/
```

It works out of the box — the default Ollama model is pulled automatically on
first use (allow a few minutes the first time). Use **Settings** to change the
Ollama model or the embedding model. To pre-pull a model yourself:

```bash
docker exec briefscope_ollama_gpu ollama pull llama3.2
```

`docker-compose.standalone.yml` is **self-contained**: it defines every service
(app + GPU Ollama + ChromaDB), its own private network and volumes, publishes
the app on host port `8080`, and blanks `ROOT_PATH` so the UI, REST API and
interactive docs (`/docs`) all live at the host root instead of behind the
kernel's `/api/...` path prefix. You do **not** need the base
`docker-compose.yml`, a second `-f` flag, or a manually created network. Want a
different port? Edit the `8080:8080` mapping in that file. To stop and remove
everything:

```bash
docker compose -f docker-compose.standalone.yml down
```

## Install as a QueAI plugin

If you do run the [QueAI](https://github.com/queai-project/QueAI) kernel, install
BriefScope as a plugin instead:

1. Make this plugin available to your kernel (clone it into the kernel's
   `plugins/` directory, or install it from the marketplace if registered).
2. Open the kernel hub at `http://localhost:8473/manager/`.
3. Find **BriefScope LOCAL GPU** in the catalog and install it.
4. Open the plugin UI. It works out of the box; use **Settings** to change the
   Ollama model or the embedding model.

In this mode the kernel provides the `queai_network` and Traefik routes the app
at `/api/briefscope_local_gpu`; the base `docker-compose.yml` is used as-is (no
standalone override).

## Configuration

Runtime parameters are entered through the plugin **Settings** UI and persisted
to `data/config.json` (which survives container restarts via the plugin's Docker
volume). A `.env.example` documents the environment defaults and recommended
models.

`docker-compose.yml` sets these environment variables automatically:

| Variable | Value | Meaning |
|---|---|---|
| `ROOT_PATH` | `/api/briefscope_local_gpu` | FastAPI `root_path` / kernel path prefix. Blanked to `""` in `docker-compose.standalone.yml` so everything serves at the host root. |
| `LLM_MODE` | `local` | Selects the local (Ollama) path. Leave as-is. |
| `OLLAMA_HOST` | `http://briefscope_ollama_gpu:11434` | Bundled GPU Ollama container. Leave as-is. |

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
