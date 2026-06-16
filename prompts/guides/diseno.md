# Design guide: palettes, typography and visual recipes

Load this guide (`consultar_guia_diseno`) BEFORE designing any document so every
deliverable looks professional and consistent — not random. Pick ONE palette and
ONE font pairing per document and reuse them everywhere in it.

## Creative freedom (within constraints)

The palettes and recipes below are a reliable **starting point, not a cage**. You
are encouraged to be creative: design your own colour palette, try a different
layout, an unconventional cover, an editorial grid or a bolder type pairing — as
long as the result still serves the document's **tone and objective** and stays
professional. A children's workshop, a startup pitch, a legal memo and a wedding
invitation should not look the same.

When you go off-recipe, you must still satisfy these non-negotiables:

- **Fit the tone and purpose.** Palette, type and layout match the subject and
  audience (sober for finance/legal; warm for events; vivid for creative/marketing).
  Creativity serves the message, it never fights it.
- **Contrast and legibility.** Keep strong text/background contrast (aim for WCAG
  AA: ~4.5:1 for body text, ~3:1 for large headings). No mid-tone on mid-tone, no
  light grey on white. Check that any custom colours actually contrast.
- **Order and organisation.** Clear visual hierarchy, consistent alignment and
  spacing, generous whitespace. Creative ≠ cluttered or random.
- **One coherent system per document.** Whatever you invent, choose it once and
  apply the same palette + type system to every page/slide.

If a custom choice would hurt readability or coherence, fall back to the curated
palettes and pairings below.

## 1. Palettes

Each palette has five roles: `primary` (headers / main accent), `accent`
(highlight / CTA — use sparingly), `ink` (text), `muted` (secondary text,
borders), `surface` (soft background, never pure white). Rule 60/30/10: mostly
neutral, some primary, a little accent.

| Palette | primary | accent | ink | muted | surface |
|---|---|---|---|---|---|
| Corporate Navy | 0F3460 | E94560 | 1A1A2E | 5A5A6E | F2F4F8 |
| Slate Professional | 1E293B | 2563EB | 0F172A | 64748B | F8FAFC |
| Teal Modern | 0F766E | F59E0B | 134E4A | 475569 | F0FDFA |
| Executive Charcoal | 18181B | 6366F1 | 09090B | 71717A | FAFAFA |
| Warm Terracotta | 7C2D12 | 0D9488 | 292524 | 78716C | FAF7F2 |
| Forest | 14532D | CA8A04 | 1C1917 | 57534E | F7FAF7 |

Choose by tone: Navy/Slate = corporate/finance; Teal/Forest = tech/health/eco;
Charcoal = premium/editorial; Terracotta = warm/creative. Prefer a soft `surface`
over pure white and a tinted near-black over `#000000`.

## 2. Typography

Pairings (with web-safe fallbacks so WeasyPrint always has a font):

- Editorial / serious report: headings serif `'Lora', 'Liberation Serif', serif`
  + body `'Lato', 'Inter', 'DejaVu Sans', sans-serif`.
- Modern / UI: all sans `'Lato', 'Inter', 'DejaVu Sans', sans-serif`, contrast by
  weight (700 headings, 400 body).
- Data / dashboard: neutral sans + tabular numbers.

Print scale (pt): body 10.5–11, h3 13, h2 16, h1 22–24, cover 32+. Body line
height 1.5–1.6. Build hierarchy with size + weight + color, not underlines or
all-caps. Spacing scale (px): 4 / 8 / 12 / 16 / 24 / 32 / 48.

## 3. Recipe — PPTX with a palette and an embedded chart

```python
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from io import BytesIO
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

# Palette (Slate Professional)
PRIMARY = RGBColor(0x1E, 0x29, 0x3B)
ACCENT  = RGBColor(0x25, 0x63, 0xEB)
INK     = RGBColor(0x0F, 0x17, 0x2A)
WHITE   = RGBColor(0xFF, 0xFF, 0xFF)

prs = Presentation(); prs.slide_width = Inches(13.333); prs.slide_height = Inches(7.5)
blank = prs.slide_layouts[6]

# Cover: full-bleed primary background
s = prs.slides.add_slide(blank)
s.background.fill.solid(); s.background.fill.fore_color.rgb = PRIMARY
tb = s.shapes.add_textbox(Inches(0.9), Inches(2.6), Inches(11.5), Inches(2))
p = tb.text_frame.paragraphs[0]; p.text = "Quarterly Review"
p.font.size = Pt(44); p.font.bold = True; p.font.color.rgb = WHITE

# Data slide with a matplotlib chart embedded from memory
s2 = prs.slides.add_slide(blank)
fig, ax = plt.subplots(figsize=(8, 4.2), dpi=200)
ax.bar(["Q1", "Q2", "Q3", "Q4"], [12, 18, 15, 23], color="#2563EB")
ax.set_title("Revenue (M$)"); fig.tight_layout()
buf = BytesIO(); fig.savefig(buf, format="png", bbox_inches="tight"); buf.seek(0)
plt.close(fig)
s2.shapes.add_picture(buf, Inches(1.2), Inches(1.3), width=Inches(10.9))

guardar_documento(prs)
```

## 4. Recipe — PDF/HTML branded CSS (fast path `estilo_css`)

```css
@page { size: A4; margin: 22mm; }
body { font-family: 'Lato','Inter','DejaVu Sans',sans-serif; color:#0F172A;
       line-height:1.55; font-size:11pt; background:#FFFFFF; }
h1 { font-family:'Lora','Liberation Serif',serif; color:#1E293B; font-size:23pt;
     border-bottom:3px solid #2563EB; padding-bottom:5px; }
h2 { color:#1E293B; font-size:16pt; margin-top:22px; }
.callout { background:#F8FAFC; border-left:4px solid #2563EB; padding:10px 16px; }
table { border-collapse:collapse; width:100%; }
th { background:#1E293B; color:#fff; padding:7px 10px; }
td { border:1px solid #CBD5E1; padding:6px 10px; }
tr:nth-child(even) td { background:#F8FAFC; }
```

## 5. Recipe — XLSX header, conditional formatting and chart

```python
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment
from openpyxl.formatting.rule import ColorScaleRule, DataBarRule
from openpyxl.chart import BarChart, Reference

wb = Workbook(); ws = wb.active; ws.title = "Summary"
ws.append(["Region", "Q1", "Q2"])
for c in ws[1]:
    c.font = Font(bold=True, color="FFFFFF"); c.fill = PatternFill("solid", fgColor="1E293B")
    c.alignment = Alignment(horizontal="center")
for row in [["North", 120, 150], ["South", 90, 130], ["East", 200, 180]]:
    ws.append(row)
ws.freeze_panes = "A2"
# green->red color scale on the data
ws.conditional_formatting.add("B2:C4",
    ColorScaleRule(start_type="min", start_color="F8696B",
                   end_type="max", end_color="63BE7B"))
# native chart
chart = BarChart(); chart.title = "Quarterly by region"
data = Reference(ws, min_col=2, max_col=3, min_row=1, max_row=4)
cats = Reference(ws, min_col=1, min_row=2, max_row=4)
chart.add_data(data, titles_from_data=True); chart.set_categories(cats)
ws.add_chart(chart, "E2")
guardar_documento(wb)
```

## 6. Recipe — DOCX styles (don't format paragraph by paragraph)

```python
from docx import Document
from docx.shared import Pt, RGBColor
doc = Document()
n = doc.styles["Normal"]; n.font.name = "Lato"; n.font.size = Pt(11)
h1 = doc.styles["Heading 1"]; h1.font.color.rgb = RGBColor(0x1E, 0x29, 0x3B); h1.font.size = Pt(20)
doc.add_heading("Executive summary", level=1)
doc.add_paragraph("Body text uses the Normal style.")
t = doc.add_table(rows=1, cols=2); t.style = "Light Grid Accent 1"
guardar_documento(doc)
```

Reminder: matplotlib and Pillow are available in code mode for charts/images.
Always finish with `guardar_documento(objeto)`.
