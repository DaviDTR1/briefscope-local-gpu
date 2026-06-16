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
from pptx.enum.text import PP_ALIGN

prs = Presentation()
prs.slide_width = Inches(13.333)   # 16:9
prs.slide_height = Inches(7.5)

# Cover (blank layout for full control)
blank = prs.slide_layouts[6]
s = prs.slides.add_slide(blank)
# background color
from pptx.oxml.ns import qn
fill = s.background.fill
fill.solid()
fill.fore_color.rgb = RGBColor(0x0F, 0x34, 0x60)

tb = s.shapes.add_textbox(Inches(0.8), Inches(2.8), Inches(11.7), Inches(2))
p = tb.text_frame.paragraphs[0]
p.text = "Presentation title"
p.font.size = Pt(44); p.font.bold = True
p.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)

guardar_documento(prs)
```

Charts (embed a matplotlib figure from memory, no temp files):
```python
from io import BytesIO
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
fig, ax = plt.subplots(figsize=(8, 4.2), dpi=200)
ax.bar(["Q1", "Q2", "Q3", "Q4"], [12, 18, 15, 23], color="#2563EB")
ax.set_title("Revenue (M$)"); fig.tight_layout()
buf = BytesIO(); fig.savefig(buf, format="png", bbox_inches="tight"); buf.seek(0)
plt.close(fig)
slide.shapes.add_picture(buf, Inches(1.2), Inches(1.3), width=Inches(10.9))
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
- Do not fill slides with placeholder/fake content (fake image captions,
  placeholder QR/links, reader tips). If it is not real, leave it out and mention
  it in chat.

## Deliver complete content (no template)

Fill the document with all the real information you have. Do **not** deliver an
empty template or a skeleton with blanks, sample text or "fill here" lines unless
the user **explicitly** asked for a template or form. If extra material, an image,
an additional section or a reusable blank version could help, **suggest it in your
chat reply** — never leave gaps, placeholders or "space to add X" inside the file.
