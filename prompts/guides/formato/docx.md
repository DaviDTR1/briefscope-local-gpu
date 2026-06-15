# Format guide: DOCX (Word)

Two paths. The fast one covers most cases.

## Fast path — `generar_documento_markdown` (recommended)
Write the document in **Markdown** and pandoc converts it to a rich, **editable** `.docx` (headings as Word styles, tables, lists, bold/italic, quotes, code).

Contract:
- `formato`: `"docx"`
- `contenido_markdown`: the document in Markdown (GitHub Flavored Markdown).
- `nombre_archivo`: without extension.
- `estilo_css`: **ignored** for DOCX (pandoc uses the default Word template).

Use it for reports, letters, memos, proposals, minutes — any text document the user wants to open and edit in Word.

Common mistakes:
- Tables need the separator row `|---|---|`.
- Use Markdown headings (`#`, `##`, `###`) so Word generates real heading styles (and a table of contents if needed).
- Do not put raw HTML; pandoc treats it as literal text.

## Code path — `generar_documento_codigo`
Only for fine control: custom paragraph styles, exact column widths, headers/footers, positioned images. You write Python with **python-docx**.

Contract:
- `formato`: `"docx"`
- `codigo_python`: build a `Document()` and end with `guardar_documento(doc)` (or `doc.save(OUTPUT_PATH)`).
- `nombre_archivo`: without extension.

Minimal example:
```python
from docx import Document
from docx.shared import Pt, RGBColor
doc = Document()
h = doc.add_heading("Title", level=1)
doc.add_paragraph("Body text.")
guardar_documento(doc)
```

Common mistakes:
- Do not forget `guardar_documento(doc)` at the end.
- For font color/size work on `run.font` (not on the paragraph).
- `add_heading` with `level=0` creates a document title, not an H1.

**Quick decision:** standard editable text? → fast path. Word-specific layout? → code path.
