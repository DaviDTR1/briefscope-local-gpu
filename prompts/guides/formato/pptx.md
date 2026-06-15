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

Best practices:
- Set `slide_width`/`slide_height` for 16:9 (13.333 × 7.5 in).
- Use the blank layout (`slide_layouts[6]`) and place text boxes yourself for consistent design; or use layouts with placeholders (`[0]` title, `[1]` content) for speed.
- Keep a coherent palette (define `RGBColor` constants and reuse them).
- One idea per slide; short titles; few-word bullets.

Common mistakes:
- Do not forget `guardar_documento(prs)` at the end.
- `add_slide` needs a *layout*, not a loose index: `prs.slide_layouts[i]`.
- Placeholders vary by layout; if `slide.placeholders[1]` fails, use a manual text box.
- Measurements are in EMU: always use `Inches(...)` or `Pt(...)`, never raw numbers.
