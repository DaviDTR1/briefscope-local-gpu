# Changelog

All notable changes to **BriefScope LOCAL GPU** are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [1.7.6] - 2026-06-19

### Changed
- **Embeddings now run on Ollama instead of sentence-transformers.** Document
  search embeddings are computed by the bundled Ollama server (`/api/embed`,
  GPU-accelerated) and passed to ChromaDB explicitly, dropping the
  `sentence-transformers`/torch dependency to lower resource usage and image
  size. Default model is `nomic-embed-text` (`mxbai-embed-large`, `bge-m3` and
  `qwen3-embedding` also available); the model is pulled into Ollama
  automatically on first use. Switching the embedding model invalidates
  previously indexed documents — re-upload them so they are re-embedded.

## [1.7.5] - 2026-06-19

### Changed
- **Web search toggle restyled.** When active it now shows an inverted solid fill
  (accent background with the icon in the background color); both the attachment
  (＋) and web search buttons get a clearly visible border in their normal/inactive
  state.
- **Documents are always "ready to show".** The Creator agent no longer adds
  optimization metadata or non-deliverable sections to a document — ATS/SEO keyword
  lists (e.g. a "Palabras clave ATS" block), internal notes or version notes are
  out. Keywords are woven naturally into the real content; any such remark is sent
  to the user in chat instead. Such a section is only included when the user
  explicitly asks for it; the agent may recommend it in chat but never inserts it
  unprompted.
- **README and assets aligned across variants.** The READMEs now document the
  optional web search and the three-agent architecture (main / researcher /
  creator), and the logo is identical across all variants.

### Fixed
- **Chat input resets after sending.** The message box now returns to its base
  size after a message is sent instead of keeping the height it grew to while
  typing.

## [1.7.4] - 2026-06-16

### Added
- **Web search for the local agents.** A per-project globe toggle next to the
  attachment (＋) button turns web search on or off for a chat (remembered per
  project in the browser), in both local-Ollama and cloud modes. When on, the
  permitted agents gain a `buscar_en_web` tool backed by DuckDuckGo via the `ddgs`
  package — no API key required. **Settings → Local** gains a *Web Search* section
  to choose which agents may search (Researcher and/or Creator; default: Researcher
  only). The button is the master per-project switch; Settings is the global
  per-agent permission list. Off → no agent searches; on → only the permitted ones.
- **Design-focused web search for the Creator.** When the Creator is granted web
  search, it uses it solely for document-design references — color palettes, font
  pairings, layouts, and presentation/typography best practices (Canva, Adobe,
  Nielsen Norman Group, Presentation Zen, Duarte, Google Fonts, Coolors, Material
  Design, and others) — never as a source of factual content for the document.

## [1.7.3] - 2026-06-16

### Changed
- **Stronger anti-overlap guidance for generated slides.** The PPTX format guide
  and the presentation type guide now require the anti-overflow contract
  (`auto_size=MSO_AUTO_SIZE.NONE` + `word_wrap=True`, fixed box sized to its
  content, gaps between columns/cards, inner card margins) on **every** text box
  and card — not just the main bullet box — to stop narrow labels from growing
  sideways and overlapping neighbouring shapes.
- **More creative freedom within constraints.** The design guide now explicitly
  encourages exploring custom palettes, layouts, covers and type pairings, as
  long as they fit the document's tone and objective and preserve strong contrast
  and clear organization. The creator agent prompt echoes this.

## [1.7.2] - 2026-06-16

### Added
- **Root path redirects to the UI.** A request to `/` now redirects to the SPA
  at `/ui/` (using a `307` to `{root_path}/ui/`), so opening the bare host —
  e.g. http://localhost:8080 — lands on the app. The redirect honors the kernel's
  `root_path` prefix, so it works both standalone and behind QueAI/Traefik.
## [1.7.1] - 2026-06-16

### Added
- **Run standalone without QueAI.** New **self-contained**
  `docker-compose.standalone.yml` plus a README "Run standalone" section. It
  defines every service, its own private network and volumes, so a single
  command runs the whole stack: `docker compose -f docker-compose.standalone.yml
  up -d --build`, then open http://localhost:8080/ui/. It publishes the app port
  and blanks `ROOT_PATH` so the UI, REST API and `/docs` all serve at the host
  root instead of behind the kernel's `/api/...` prefix — no base compose
  file, extra `-f` flag or manual network needed.

### Changed
- README reframed so QueAI is **optional** rather than a prerequisite; the two
  run modes (standalone vs. QueAI plugin) are now documented side by side.

## [1.7.0] - 2026-06-16

### Added
- **Attachment references reach the agent without polluting the history.** When a
  document is attached via the chat "+" button, the message sent to the agent now
  carries an ephemeral reference to the just-attached file(s) (`agent_context`),
  so the agent knows they were added this turn. The user's stored and displayed
  message stays clean — that reference is never saved to the conversation history.

## [1.6.0] - 2026-06-16

### Added
- **Attach-documents button in the chat bar.** The chat input now has a "＋"
  button that uploads files straight into the current project, like modern AI
  chats (alongside the existing documents panel).
- **More code examples in the format guides** (figures, tables, charts, layouts):
  native PPTX tables and charts plus a big-number layout; python-docx styled
  tables and embedded matplotlib figures; reportlab platypus tables and chart
  images; HTML KPI-card layouts; and an Excel line chart, icon-set rule and
  dashboard/KPI skeleton.

### Fixed
- **Slides no longer overflow.** The PPTX guidance now mandates a content budget,
  a fixed text box inside the safe area, `word_wrap=True` + `auto_size=NONE`
  (instead of the box-growing autofit that pushed text off the slide), and
  splitting dense slides.
- **No meta-description titles on slides.** Cover titles/subtitles and slide
  headlines must state the real subject, never describe the file or its format
  (e.g. "Resumen extenso (en bullets)").

## [1.5.0] - 2026-06-15

### Added
- **Research-backed best practices baked into every type guide.** Each document
  type guide now carries evidence-based guidance gathered from web research, plus
  concrete color palettes (HEX), layout options and structure recommendations:
  - **CV** — ATS-first rules so the document is reliably parsed by applicant
    tracking systems (single column, standard headings, no tables/images in the
    ATS-safe layout, web-safe fonts), plus conservative and creative palettes and
    two layout options.
  - **Cover letter (carta)** — length and paragraph structure, block style, and
    letterhead palette/layout options.
  - **Professional report** — executive-summary guidance, heading hierarchy,
    margins and corporate/modern/elegant palettes.
  - **Presentation** — assertion-evidence, 10/20/30 and 6x6 rules, type sizes and
    dark/light/corporate palettes with two layout patterns.
  - **Invoice/quote** — required legal/tax elements, numeric alignment and
    total emphasis rules, plus professional palettes.
  - **Dashboard** — F/Z reading order, 5-9 metric ceiling, chart-type-per-data
    and sequential/diverging palettes.
  - **Brochure/flyer** — hero headline and single-CTA rules, font/color limits,
    and bold/tech/premium palettes with two layouts.
  - **Article/essay** — readability rules (measure, font size, line height,
    subheading cadence) and reading-friendly palettes with two layouts.

## [1.4.2] - 2026-06-15

### Changed
- **Documents are delivered complete, not as templates.** The orchestrator,
  creator agent and every format/type guide now state that the file must be a
  finished document filled with the real information — never an empty skeleton
  with blanks or "space to add X" — unless the user explicitly asks for a
  template/form. Ideas for extra content (images, sections, a reusable blank
  version) are offered as suggestions in the chat reply, not left as gaps in the
  file.
- **No more phantom files.** When several formats are requested (e.g. Word *and*
  PDF), the creator now generates one file per format with its own call and must
  confirm each before reporting it; it must never announce or invent a file that
  was not actually generated. The orchestrator reports only the files that truly
  appear in `[GENERATED_FILES]`. Fixes the case where a PDF was announced but not
  produced.

### Added
- New type guides to broaden the catalog of document possibilities:
  `folleto` (brochure / flyer / one-pager), `cv` (résumé) and `articulo`
  (article / essay / blog post).

## [1.4.1] - 2026-06-15

### Changed
- **Document creator: no placeholders or fake assets.** The creator agent and the
  PPTX format / presentation type guides now forbid filling documents with content
  that is not real: no fake image captions (e.g. "[Imagen sin copyright] ..."), no
  placeholder QR codes or store/library links, and no reader tips or
  meta-commentary embedded in the document. Images and links are inserted only
  when a real asset exists; if a visual would help, the agent suggests it in the
  chat reply, and reader suggestions are surfaced in chat instead of printed in
  the file.

## [1.4.0] - 2026-06-15

### Added
- **Design system guide** (`prompts/guides/diseno.md`) and a new
  `consultar_guia_diseno` tool: curated color palettes (with hex), font pairings,
  a spacing scale and ready-to-use visual recipes (PPTX with an embedded chart,
  branded PDF/HTML CSS, XLSX conditional formatting + chart, DOCX styles). The
  creator agent now consults it before designing and reuses one palette + one
  font pairing across each document.
- `matplotlib` and `Pillow` dependencies for charts and image handling in code
  mode (embeddable into PPTX/PDF/DOCX).
- `fonts-liberation` and `fonts-lato` system fonts in the Docker image so the
  default and recipe typography renders correctly.

### Changed
- Upgraded the default PDF/HTML stylesheet (Slate Professional palette: serif
  headings, sans body, accent color, soft surface, banded tables, page numbers).
- Enriched the per-format guides (PPTX/XLSX/PDF/DOCX) with chart,
  conditional-formatting and styling recipes plus pointers to the design guide.

### Note
- The new dependencies and fonts require rebuilding the Docker image.

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
