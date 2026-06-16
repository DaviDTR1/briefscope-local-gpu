# Format guide: MD (Markdown)

A single path: **`generar_documento_markdown`** with `formato: "md"`.

Deliver the document as a `.md` file **exactly as you write it** (no conversion). The content is saved in full, preserving headings, lists, tables, bold, links and code blocks.

Contract:
- `formato`: `"md"`
- `contenido_markdown`: the final document in Markdown.
- `nombre_archivo`: without extension.
- `estilo_css`: ignored.

Use it when the user wants the reusable Markdown source (READMEs, technical documentation, notes they will edit in another editor, content for a system that already renders Markdown).

Common mistakes:
- Make sure the Markdown syntax is valid (table separator rows, closing code blocks with ```).
- If what the user wants is a **rendered** document (not the source), choose `pdf`, `docx` or `html`.

## Deliver complete content (no template)

Fill the document with all the real information you have. Do **not** deliver an
empty template or a skeleton with blanks, sample text or "fill here" lines unless
the user **explicitly** asked for a template or form. If extra material, an image,
an additional section or a reusable blank version could help, **suggest it in your
chat reply** — never leave gaps, placeholders or "space to add X" inside the file.
