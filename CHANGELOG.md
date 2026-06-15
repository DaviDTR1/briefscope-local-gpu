# Changelog

All notable changes to **BriefScope LOCAL GPU** are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [1.3.1] - 2026-06-15

### Added

- The researcher and orchestrator can now read a full **source** document the
  user uploaded — new `leer_documento_fuente` tool — not only search fragments
  via RAG. A whole document is returned when it fits the read budget; larger
  documents (e.g. a full book) are delivered in sequential parts so the entire
  work can be read across several calls. New `source_read_max_chars` setting
  controls the per-read budget. Before delegating, the orchestrator also frames
  the requirements/criteria the investigation must meet, and the researcher
  checks its report against them before saving.

## [1.3.0] - 2026-06-15

### Added

- New **researcher** sub-agent (`investigador`). The main agent now delegates
  detailed investigation over the project documents — in-depth summaries, study
  plans, reports, analyses — to a dedicated research agent. The researcher
  searches the documents via RAG, reads documents and saved reports, writes the
  full report in Markdown, saves it, and returns a brief description plus the
  saved report name (which the main agent can hand to the document creator when a
  downloadable file is wanted).
- The main agent (orchestrator) now focuses on simple tasks it can resolve
  itself (a quick RAG lookup, reading a document or a saved report, direct
  answers) and delegates complex investigation and document generation to the
  researcher and creator sub-agents respectively.

## [1.2.0] - 2026-06-14

### Fixed

- Markdown written inside raw HTML wrappers (for example a multi-column layout
  `<div>`) is now parsed instead of leaking through as literal `###`/`-` text in
  generated documents. The Markdown engine enables the `md_in_html` and
  `attr_list` extensions, and the agent format guides document the required
  `markdown="1"` attribute.
- Chat state and any in-progress streamed reply are now preserved when switching
  between projects. A reply that arrives while you are viewing another project is
  kept, so returning no longer loses the message or requires a page reload.

### Changed

- Streaming responses no longer auto-scroll the chat on every token; the view
  scrolls only when a new message begins, letting you read at your own pace.

### Added

- Informative agent logs (agent start/finish, each tool entered with a safe
  argument summary, tool results, and sub-agent delegations) so advanced users
  can follow the agent's behavior.

## [1.1.0] - 2026-06-14

### Fixed

- Generated documents are now scoped per project: each deliverable is stored
  under a per-project folder (`generated/project_<id>`) and only appears in the
  project that created it. Previously all projects shared a single folder, so
  files generated in one project leaked into every other project.

### Added

- Per-document metadata sidecar (title, creation timestamp, format and owning
  project) saved next to each generated file and surfaced in the files panel.
- The file list in the UI now shows each document's title and creation date.

### Changed

- The `/files` list, download and delete endpoints now require a `project_id`
  and operate strictly within that project's folder.

## [1.0.0] - 2026-06-14

First public release as a QueAI plugin.

### Added

- Document-analysis agent over user-uploaded documents (PDF, DOCX, XLSX, TXT,
  MD and more), organized into projects.
- Retrieval strategy that adapts to corpus size: full-context for small
  corpora, RAG (ChromaDB vector search) above a configurable token threshold.
- Multi-agent orchestration (orchestrator + creator) for research and
  deliverable generation.
- Downloadable file generation in two engines:
  - **Rapid mode** (Markdown → DOCX via pandoc, → PDF via WeasyPrint, → HTML).
  - **Code mode** (Python: reportlab / python-docx / python-pptx / openpyxl)
    for PDF, DOCX, PPTX and XLSX with precise layout.
- Streaming chat responses (SSE) with conversation history and automatic
  history compaction to save tokens.
- React frontend with a Spanish/English language switcher.
- Settings UI to choose the Ollama model and the local embedding model, and to
  tune RAG / history parameters; configuration persists to `data/config.json`.
- User-selectable local embedding model (sentence-transformers), with
  recommended models documented in `.env.example`.
- QueAI integration: `manifest.json`, Traefik `PathPrefix` routing, healthcheck
  endpoint, and bundled GPU Ollama + ChromaDB services via `docker-compose.yml`.

### Notes

- Runs **fully offline with NVIDIA GPU acceleration**: LLM via a bundled Ollama
  container exposed to the GPU, embeddings in-process via sentence-transformers.
  No API keys or internet required after the model and embedding weights are
  downloaded on first use.
- Requires the **NVIDIA Container Toolkit** on the host.
- Changing the embedding model invalidates previously indexed documents — they
  must be re-uploaded so they are re-embedded with the new model.

[Unreleased]: https://github.com/queai-project/QueAI
[1.0.0]: https://github.com/queai-project/QueAI
