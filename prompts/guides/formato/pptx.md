# Format guide: PPTX (PowerPoint)

A single path: **`generar_documento_codigo`** with `formato: "pptx"`. (There is no Markdown path for presentations.)

You write Python with **python-pptx**. You have the variable `OUTPUT_PATH` and the helper `guardar_documento(obj)` (accepts the presentation and calls `.save()` for you).

Contract:
- `formato`: `"pptx"`
- `codigo_python`: build the `Presentation()` and end with `guardar_documento(prs)`.
- `nombre_archivo`: without extension.

Recommended skeleton:
```python
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR

prs = Presentation()
prs.slide_width = Inches(13.333)   # 16:9
prs.slide_height = Inches(7.5)

# Cover (blank layout for full control)
blank = prs.slide_layouts[6]
s = prs.slides.add_slide(blank)
# background color
fill = s.background.fill
fill.solid()
fill.fore_color.rgb = RGBColor(0x0F, 0x34, 0x60)

tb = s.shapes.add_textbox(Inches(0.8), Inches(2.8), Inches(11.7), Inches(2))
p = tb.text_frame.paragraphs[0]
p.text = "Real presentation title"   # the actual subject, NOT a description
p.font.size = Pt(44); p.font.bold = True
p.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)

guardar_documento(prs)
```

## Titles are real content, never meta-descriptions

The cover title and subtitle are the **actual subject**, not a description of the
file or its format. Write `"La fierecilla domada"` with a subtitle like
`"Comedia de William Shakespeare"` — **never** `"Resumen extenso (en bullets)"`,
`"Summary in bullets"`, `"Presentation about the play"`, `"Detailed overview"` or
anything that narrates what the document is. The same rule applies to every slide
headline: state the point (assertion), not the activity. If you feel the urge to
describe the format ("resumen en viñetas", "key points below"), delete it — the
reader can see the format.

## Never let text overflow the slide

The most common defect is body text spilling off the bottom of the slide. It
happens when a text box keeps the default `SHAPE_TO_FIT_TEXT` autofit, which makes
the **box grow** to fit the text instead of keeping the text inside the box. Fix it
with a **content budget + a fixed box + word wrap**, and split dense slides:

- **Budget per slide:** at most ~6 bullets of ~1 line each (the 6×6 ceiling). If
  you have more, **split into two slides** (`"Personajes (1/2)"`, `"(2/2)"`), don't
  cram.
- **Fixed box inside the safe area:** top band ends ~0.9 in; keep the body box
  within `top=1.4` and `height≤5.4` so its bottom (≤6.8 in) never reaches the
  7.5 in edge. Leave side margins (`left≈0.9`, `width≈11.5`).
- **Turn off growth, turn on wrap:** `tf.word_wrap = True` and
  `tf.auto_size = None` (i.e. `MSO_AUTO_SIZE.NONE`) — the box stays put and text
  wraps inside it.
- **Pick a readable size that fits the budget:** body ≥18 pt (headline 30–40 pt).
  With 6 short bullets at 18–20 pt this fits comfortably in a 5.4 in box.

```python
from pptx.enum.text import MSO_AUTO_SIZE, MSO_ANCHOR

body = s.shapes.add_textbox(Inches(0.9), Inches(1.4), Inches(11.5), Inches(5.4))
tf = body.text_frame
tf.word_wrap = True
tf.auto_size = MSO_AUTO_SIZE.NONE        # do NOT grow the box (prevents overflow)
tf.vertical_anchor = MSO_ANCHOR.TOP

bullets = ["First point — one line", "Second point", "Third point"]  # ≤6 items
for i, line in enumerate(bullets):
    p = tf.paragraphs[0] if i == 0 else tf.add_paragraph()
    p.text = line
    p.font.size = Pt(20)
    p.space_after = Pt(6)
```

Optional: if you must keep more text in a fixed box, call
`tf.fit_text(font_family="DejaVu Sans", max_size=20)` **after** setting the box
size and text — it sets `auto_size=NONE`, turns on word wrap and shrinks the font
to the largest size that fits. (It needs a font file present; `DejaVu Sans` is
installed. Prefer splitting slides over shrinking below ~16 pt.)

## Native table (graphic-frame)

```python
rows, cols = 4, 3
tbl_shape = s.shapes.add_table(rows, cols, Inches(0.9), Inches(1.5),
                               Inches(11.5), Inches(4.0))
table = tbl_shape.table
headers = ["Character", "Role", "Function"]
for c, text in enumerate(headers):
    cell = table.cell(0, c)
    cell.text = text
    cell.text_frame.paragraphs[0].font.bold = True
    cell.text_frame.paragraphs[0].font.size = Pt(16)
    cell.fill.solid(); cell.fill.fore_color.rgb = RGBColor(0x0F, 0x34, 0x60)
    cell.text_frame.paragraphs[0].font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
data = [["Catalina", "Eldest daughter", "Initial obstacle"],
        ["Bianca", "Youngest", "Object of rivalry"],
        ["Petruchio", "Suitor", "Drives the main plot"]]
for r, row in enumerate(data, start=1):
    for c, val in enumerate(row):
        table.cell(r, c).text = val
        table.cell(r, c).text_frame.paragraphs[0].font.size = Pt(13)
```

## Charts — two options

**A) Native editable chart** (PowerPoint can recolor/edit it):
```python
from pptx.chart.data import CategoryChartData
from pptx.enum.chart import XL_CHART_TYPE, XL_LEGEND_POSITION

cd = CategoryChartData()
cd.categories = ["Q1", "Q2", "Q3", "Q4"]
cd.add_series("Revenue", (12, 18, 15, 23))
gframe = s.shapes.add_chart(XL_CHART_TYPE.COLUMN_CLUSTERED,
                            Inches(1.2), Inches(1.4), Inches(10.9), Inches(5.2), cd)
chart = gframe.chart
chart.has_legend = True
chart.legend.position = XL_LEGEND_POSITION.BOTTOM
chart.legend.include_in_layout = False
```

**B) Matplotlib figure embedded as an image** (full styling control, from memory, no temp files):
```python
from io import BytesIO
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
fig, ax = plt.subplots(figsize=(8, 4.2), dpi=200)
ax.bar(["Q1", "Q2", "Q3", "Q4"], [12, 18, 15, 23], color="#2563EB")
ax.set_title("Revenue up 12% QoQ"); fig.tight_layout()
buf = BytesIO(); fig.savefig(buf, format="png", bbox_inches="tight"); buf.seek(0)
plt.close(fig)
s.shapes.add_picture(buf, Inches(1.2), Inches(1.4), width=Inches(10.9))
```
Use the native chart when the user may edit it in PowerPoint; use matplotlib when
you need a specific look the native engine can't produce.

## Big-number layout (one oversized stat)

```python
big = s.shapes.add_textbox(Inches(0), Inches(2.4), Inches(13.333), Inches(2.0))
bp = big.text_frame.paragraphs[0]; bp.alignment = PP_ALIGN.CENTER
bp.text = "37%"; bp.font.size = Pt(96); bp.font.bold = True
bp.font.color.rgb = RGBColor(0xF9, 0x73, 0x16)   # accent only on the number
cap = s.shapes.add_textbox(Inches(0), Inches(4.5), Inches(13.333), Inches(0.8))
cp = cap.text_frame.paragraphs[0]; cp.alignment = PP_ALIGN.CENTER
cp.text = "year-over-year growth"; cp.font.size = Pt(24)
```

Best practices:
- **Call `consultar_guia_diseno()` first**: pick one palette (its hex) and one
  font pairing and reuse them on every slide.
- Set `slide_width`/`slide_height` for 16:9 (13.333 × 7.5 in).
- Use the blank layout (`slide_layouts[6]`) and place text boxes yourself for consistent design; or use layouts with placeholders (`[0]` title, `[1]` content) for speed.
- Define `RGBColor` constants from the chosen palette and reuse them.
- One idea per slide; short titles; few-word bullets; charts/big numbers over prose.
- **Only real assets.** Add a picture only when you actually have a real image
  (provided, in the source, or genuinely generated). Never type a fake caption
  like "[Imagen sin copyright] ...", a placeholder QR/link/store button, or a
  reader tip ("Sugerencia: ...") onto a slide. If a visual or link would help,
  suggest it in your chat reply instead of inserting a placeholder.

Common mistakes:
- Do not forget `guardar_documento(prs)` at the end.
- `add_slide` needs a *layout*, not a loose index: `prs.slide_layouts[i]`.
- Placeholders vary by layout; if `slide.placeholders[1]` fails, use a manual text box.
- Measurements are in EMU: always use `Inches(...)` or `Pt(...)`, never raw numbers.
- **Text overflow:** leaving the default autofit so the box grows past the slide
  edge — set `auto_size = MSO_AUTO_SIZE.NONE` + `word_wrap = True` and split dense
  slides instead.
- **Meta-description titles** ("Resumen en bullets", "Overview"): use the real
  subject as the title.
- Do not fill slides with placeholder/fake content (fake image captions,
  placeholder QR/links, reader tips). If it is not real, leave it out and mention
  it in chat.

## Deliver complete content (no template)

Fill the document with all the real information you have. Do **not** deliver an
empty template or a skeleton with blanks, sample text or "fill here" lines unless
the user **explicitly** asked for a template or form. If extra material, an image,
an additional section or a reusable blank version could help, **suggest it in your
chat reply** — never leave gaps, placeholders or "space to add X" inside the file.
