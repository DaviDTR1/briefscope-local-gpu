# Format guide: PDF

There are **two paths** to produce a PDF. Choose based on visual complexity.

## Fast path — `generar_documento_markdown` (recommended by default)
Write the document in **Markdown** and the engine converts it to PDF (Markdown → HTML → PDF with WeasyPrint). Supports full Unicode, tables, lists, quotes, code and **your own CSS**.

Contract:
- `formato`: `"pdf"`
- `contenido_markdown`: the document in Markdown.
- `nombre_archivo`: without extension, only letters/numbers/hyphens.
- `estilo_css` (optional): full CSS rules (`@page`, `body`, `h1`, `table`...). If you omit it, a default professional style is applied (A4, clean typography, tables with a colored header).

Use it for reports, memos, documentation, proposals and any document that is structured text. For a branded finish, pass your own `estilo_css`.

**For a polished look, call `consultar_guia_diseno()`** and build `estilo_css` from
a chosen palette + font pairing (it has a ready-to-copy branded CSS recipe). If you
omit `estilo_css`, a refined default style is applied (soft surface, serif headings,
banded tables, page numbers).

### Tables, figures and charts on the fast path
- **Tables:** write a Markdown table (with the `|---|---|` row). Right-align numeric
  columns with `|---:|`. Style it in `estilo_css` (`th { background:#1E293B; color:#fff }`).
- **Figures / charts:** embed a **real** image with `![caption](path)` only if you
  actually have the image on disk (e.g. a chart you generated). The engine resolves
  local paths. Never write a placeholder image tag. If a chart would help and you
  cannot generate it here, use the code path below or suggest it in chat.
- **Two-column / card layouts:** wrap a block in a `<div class="...">` and read the
  raw-HTML rule below.

Common mistakes to avoid:
- Do not include the `<html>` or `<style>` block: only Markdown (and optionally CSS separately in `estilo_css`).
- Markdown tables need the separator row `|---|---|`.
- For CSS page breaks use `page-break-before: always;` on a selector.

### CRITICAL: Markdown inside raw HTML wrappers
When you wrap a section in a raw HTML tag for layout (columns, cards, a header band), **Markdown written inside that tag is NOT parsed unless you add `markdown="1"` to the tag.** Without it, `### Heading` and `- bullet` come out as literal text (a frequent bug in CVs and dashboards with multi-column skill lists).

Two correct options:

1. **Add `markdown="1"` to the wrapper and leave a blank line** before the Markdown content (preferred — keep writing Markdown):

   ```html
   <div class="skills-grid" markdown="1">

   ### AI & Data
   - LangChain, LangGraph, LangSmith
   - RAG, hybrid search, rerankers

   ### Backend & Cloud
   - FastAPI, Flask, SQLAlchemy
   - AWS: Lambda, SQS, DynamoDB

   </div>
   ```
   Pair it with CSS in `estilo_css`, e.g. `.skills-grid { column-count: 2; column-gap: 28px; }` (or `display:grid; grid-template-columns:1fr 1fr;`).

2. **Or write the inner content as pure HTML** (no Markdown at all inside the wrapper): `<h3>AI & Data</h3><ul><li>LangChain</li>...</ul>`.

Never mix: don't put `### ...` / `- ...` inside a raw `<div>`/`<td>` that lacks `markdown="1"`.

## Code path — `generar_documento_codigo`
Only if you need **pixel-perfect control**: certificates, absolute positioning, vector graphics, cover pages with full-bleed images, styled tables and embedded charts. You write Python with **reportlab**.

Contract:
- `formato`: `"pdf"`
- `codigo_python`: script that builds the PDF. You have `OUTPUT_PATH` (destination path) and the helper `guardar_documento(obj)`. With reportlab you usually write directly to `OUTPUT_PATH`.
- `nombre_archivo`: without extension.

Minimal example:
```python
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
c = canvas.Canvas(OUTPUT_PATH, pagesize=A4)
c.setFont("Helvetica-Bold", 24)
c.drawString(72, 760, "Title")
c.showPage()
c.save()
```

### Flowing document with a styled table (platypus)
```python
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle

styles = getSampleStyleSheet()
doc = SimpleDocTemplate(OUTPUT_PATH, pagesize=A4,
                        topMargin=2*cm, bottomMargin=2*cm,
                        leftMargin=2*cm, rightMargin=2*cm)
story = [Paragraph("Quarterly summary", styles["Title"]), Spacer(1, 12)]

data = [["Metric", "Q1", "Q2", "Total"],
        ["Sales", "1,000", "1,200", "2,200"],
        ["Costs", "400", "450", "850"]]
table = Table(data, colWidths=[6*cm, 3*cm, 3*cm, 3*cm])
table.setStyle(TableStyle([
    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1E293B")),
    ("TEXTCOLOR",  (0, 0), (-1, 0), colors.white),
    ("FONTNAME",   (0, 0), (-1, 0), "Helvetica-Bold"),
    ("ALIGN",      (1, 0), (-1, -1), "RIGHT"),       # numeric columns
    ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F1F5F9")]),
    ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#CBD5E1")),
]))
story += [table]
doc.build(story)
```

### Embed a chart (matplotlib image into platypus)
```python
from io import BytesIO
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from reportlab.platypus import Image
fig, ax = plt.subplots(figsize=(6, 3.2), dpi=200)
ax.bar(["Q1", "Q2", "Q3", "Q4"], [12, 18, 15, 23], color="#2563EB")
ax.set_title("Revenue up 12% QoQ"); fig.tight_layout()
buf = BytesIO(); fig.savefig(buf, format="png", bbox_inches="tight"); buf.seek(0)
plt.close(fig)
story += [Spacer(1, 12), Image(buf, width=15*cm, height=8*cm)]
```

Common mistakes:
- Remember to call `c.save()` (or `doc.build(...)` with platypus) or the file will be empty.
- reportlab coordinates have their origin at the bottom-left.
- For long styled text use `platypus` (SimpleDocTemplate + Paragraph), not `drawString`.
- Embed a chart/image only if it is **real** (generated or provided) — never a placeholder.

**Quick decision:** is it structured text? → fast path. Is it custom design, a styled
table or an embedded chart? → code path.

## Deliver complete content (no template)

Fill the document with all the real information you have. Do **not** deliver an
empty template or a skeleton with blanks, sample text or "fill here" lines unless
the user **explicitly** asked for a template or form. If extra material, an image,
an additional section or a reusable blank version could help, **suggest it in your
chat reply** — never leave gaps, placeholders or "space to add X" inside the file.
