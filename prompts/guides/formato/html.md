# Format guide: HTML

A single path: **`generar_documento_markdown`** with `formato: "html"`.

Write the document in **Markdown** and the engine wraps it in a self-contained, styled HTML5 page (a single file, no external dependencies).

Contract:
- `formato`: `"html"`
- `contenido_markdown`: the document in Markdown (tables, lists, code with basic highlighting, quotes).
- `nombre_archivo`: without extension.
- `estilo_css` (optional): full CSS that replaces the default style. Use it for brand colors, typography or your own layout. If you omit it, a clean professional style is applied.

Use it for standalone pages, browsable reports, fact sheets or any deliverable to be viewed in a browser.

Common mistakes:
- Do not wrap the content in `<html>`/`<body>`: the engine already generates the full page. Pass only Markdown.
- If you want your own CSS it goes **entirely** in `estilo_css`, not embedded in the Markdown.
- Markdown tables require the separator row `|---|---|`.

### CRITICAL: Markdown inside raw HTML wrappers
When you wrap a section in a raw HTML tag for layout (columns, cards), **Markdown inside that tag is NOT parsed unless you add `markdown="1"` to the tag.** Otherwise `### Heading` and `- bullet` appear as literal text.

```html
<div class="skills-grid" markdown="1">

### AI & Data
- LangChain, LangGraph, LangSmith

### Backend & Cloud
- FastAPI, Flask, SQLAlchemy

</div>
```
Leave a blank line after the opening tag, and add the CSS (`.skills-grid { column-count: 2; }`) in `estilo_css`. Alternatively, write the inner content as pure HTML (`<h3>`, `<ul><li>`) with no Markdown inside the wrapper. Never mix Markdown syntax into a raw `<div>`/`<td>` that lacks `markdown="1"`.

For PDF from the same content, use `formato: "pdf"` (same engine, same CSS).

## Deliver complete content (no template)

Fill the document with all the real information you have. Do **not** deliver an
empty template or a skeleton with blanks, sample text or "fill here" lines unless
the user **explicitly** asked for a template or form. If extra material, an image,
an additional section or a reusable blank version could help, **suggest it in your
chat reply** — never leave gaps, placeholders or "space to add X" inside the file.
