<!-- desc: Slide presentation (pitch, visual executive summary, meeting report) in PowerPoint. -->
# Type: Presentation

Slides. Always **PPTX** via `generar_documento_codigo` (see the `pptx` format guide). The goal is to communicate visually, not to dump text.

## Recommended structure
1. **Cover** — strong title, subtitle, date/author. Brand-colored background.
2. **Agenda / context** (optional) — what will be covered.
3. **One idea per slide** — affirmative title (the conclusion, not the topic) + visual support.
4. **Data** — one big highlighted figure or one simple table/chart per slide.
5. **Closing** — conclusions and next steps / call to action.

## Best practices
- 16:9 (`Inches(13.333) × Inches(7.5)`).
- Coherent palette: define 2-3 `RGBColor` (primary, accent, text) and reuse them across all slides.
- Few-word titles; bullets of at most one line; 3-5 bullets per slide.
- Large, legible text (title ≥ 32pt, body ≥ 18pt).
- Use contrast: light text on a dark background or vice versa.
- If there are key numbers, show them huge instead of in a sentence.

## Mistakes to avoid
- Whole paragraphs on a slide (it is a presentation, not a document).
- More than ~6 lines of text per slide.
- Inconsistent colors across slides.
- Forgetting `guardar_documento(prs)`.
