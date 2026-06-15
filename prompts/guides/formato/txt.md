# Format guide: TXT (plain text)

A single path: **`generar_documento_markdown`** with `formato: "txt"`.

Write the content in **Markdown** and the engine reduces it to readable plain text (removes `#` headings, bold, italics, links, images and code blocks, keeping the text).

Contract:
- `formato`: `"txt"`
- `contenido_markdown`: the content. You can use light Markdown; it will be cleaned up.
- `nombre_archivo`: without extension.
- `estilo_css`: ignored.

Use it for notes, logs, output that will be pasted into another tool, or when the user explicitly asks for plain text without formatting.

Common mistakes:
- Do not expect pretty tables: in plain text the Markdown table syntax is kept as-is. If you need aligned columns, format them yourself with spaces.
- To keep exact line breaks, write them directly in the content.

If the user wants to keep the Markdown formatting (headings, lists) raw, use `formato: "md"` instead.
