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

A Markdown table converts to a real Word table:
```markdown
| Metric | Q1 | Q2 | Total |
|--------|---:|---:|------:|
| Sales  | 1000 | 1200 | 2200 |
| Costs  |  400 |  450 |  850 |
```
(The `---:` alignment makes numeric columns right-aligned.)

Common mistakes:
- Tables need the separator row `|---|---|`.
- Use Markdown headings (`#`, `##`, `###`) so Word generates real heading styles (and a table of contents if needed).
- Do not put raw HTML; pandoc treats it as literal text.

## Code path — `generar_documento_codigo`
Only for fine control: custom paragraph styles, exact column widths, headers/footers, positioned images, charts. You write Python with **python-docx**.

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

For brand identity, set document **styles** once instead of formatting each
paragraph (call `consultar_guia_diseno()` for the palette + a DOCX styles recipe):
```python
from docx.shared import Pt, RGBColor
doc.styles["Normal"].font.name = "Lato"; doc.styles["Normal"].font.size = Pt(11)
h1 = doc.styles["Heading 1"]; h1.font.color.rgb = RGBColor(0x1E, 0x29, 0x3B)
```

### Table with a banded style + right-aligned numbers
```python
from docx.shared import Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH
rows = [("Metric", "Q1", "Q2", "Total"),
        ("Sales", "1,000", "1,200", "2,200"),
        ("Costs", "400", "450", "850")]
table = doc.add_table(rows=1, cols=4)
table.style = "Light Grid Accent 1"           # built-in banded style
for c, text in enumerate(rows[0]):
    table.rows[0].cells[c].paragraphs[0].add_run(text).bold = True
for row in rows[1:]:
    cells = table.add_row().cells
    for c, val in enumerate(row):
        p = cells[c].paragraphs[0]
        p.add_run(val)
        if c > 0:                              # numeric columns: right-align
            p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
```

### Figure / chart (matplotlib image, in memory, no temp files)
```python
from io import BytesIO
from docx.shared import Inches
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
fig, ax = plt.subplots(figsize=(6.5, 3.4), dpi=200)
ax.plot([1, 2, 3, 4], [12, 18, 15, 23], marker="o", color="#1E293B")
ax.set_title("Revenue up 12% QoQ"); fig.tight_layout()
buf = BytesIO(); fig.savefig(buf, format="png", bbox_inches="tight"); buf.seek(0)
plt.close(fig)
doc.add_picture(buf, width=Inches(6.0))
doc.paragraphs[-1].alignment = WD_ALIGN_PARAGRAPH.CENTER
```

Common mistakes:
- Do not forget `guardar_documento(doc)` at the end.
- For font color/size work on `run.font` (not on the paragraph).
- `add_heading` with `level=0` creates a document title, not an H1.
- Add a picture only if it is a **real** chart/image you actually generated or were
  given — never a placeholder box.

**Quick decision:** standard editable text? → fast path. Word-specific layout, a
styled table or an embedded chart? → code path.

## Deliver complete content (no template)

Fill the document with all the real information you have. Do **not** deliver an
empty template or a skeleton with blanks, sample text or "fill here" lines unless
the user **explicitly** asked for a template or form. If extra material, an image,
an additional section or a reusable blank version could help, **suggest it in your
chat reply** — never leave gaps, placeholders or "space to add X" inside the file.
