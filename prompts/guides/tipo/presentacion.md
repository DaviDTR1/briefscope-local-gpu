<!-- desc: Slide presentation (pitch, visual executive summary, meeting report) in PowerPoint. -->
# Type: Presentation

Slides. Always **PPTX** via `generar_documento_codigo` (see the `pptx` format guide). The goal is to communicate visually, not to dump text.

## Recommended structure
1. **Cover** — strong title, subtitle, date/author. Brand-colored background. The
   title and subtitle are the **real subject** (e.g. "La fierecilla domada" /
   "Comedia de William Shakespeare"), never a description of the file or its format
   ("Resumen extenso (en bullets)", "Summary in bullets", "Overview").
2. **Agenda / context** (optional) — what will be covered.
3. **One idea per slide** — affirmative title (the conclusion, not the topic) + visual support.
4. **Data** — one big highlighted figure or one simple table/chart per slide.
5. **Closing** — conclusions and next steps / call to action.

## Evidence-based rules
- **One idea per slide.** Control flow by limiting each slide to a single clear point.
- **Assertion-evidence:** the headline is a **complete-sentence takeaway** (the
  assertion); the body is a supporting chart/image/diagram (the evidence) — not a
  topic label over bullets.
- **10/20/30 guideline** (Kawasaki, echoed by Microsoft): ~10 slides, ~20 minutes,
  **≥30pt** font. **6×6** as a ceiling: at most ~6 bullets of ~6 words.
- **Type sizes:** title/headline 30-40pt+, body ≥18pt. High contrast (dark on light
  or light on dark); avoid mid-tone on mid-tone.
- **One chart / one data point per slide.** Big numbers shown huge, not in a sentence.
- **Content budget so nothing overflows.** Keep the body inside a fixed box
  (`top≈1.4`, `height≤5.4` in) with `word_wrap=True` and `auto_size=MSO_AUTO_SIZE.NONE`;
  if a list needs more than ~6 lines, split it across two slides ("(1/2)", "(2/2)")
  rather than letting text run off the slide edge.

## Color palettes (pick one; 2-3 colors, reuse across the deck)
- **Dark + accent:** bg `#111827`, text `#F3F4F6`, accent cyan `#22D3EE`, secondary `#94A3B8`.
- **Light + accent:** bg `#FAFAFA`, text `#1A1A1A`, accent orange `#F97316`, secondary `#64748B`.
- **Corporate dark + teal:** bg `#0F2540`, text `#FFFFFF`, accent teal `#2DD4BF`, secondary `#93A3B8`.

Define them as `RGBColor` constants and reuse on every slide.

## Layout patterns
1. **Title + visual:** assertion headline full-width on top; one large chart/image/
   diagram filling the body below.
2. **Big-number:** one oversized stat centered (~80-120pt), a short caption beneath;
   lots of whitespace, the accent color only on the number.

## Best practices
- 16:9 (`Inches(13.333) × Inches(7.5)`).
- Few-word titles; bullets of at most one line; 3-5 bullets per slide.
- Use contrast: light text on a dark background or vice versa.

## Mistakes to avoid
- Whole paragraphs on a slide (it is a presentation, not a document).
- More than ~6 lines of text per slide.
- **Text overflowing the slide edge** — caused by leaving the default autofit so the
  box grows. Fix with `auto_size=MSO_AUTO_SIZE.NONE` + `word_wrap=True`, a fixed box
  inside the safe area, and splitting dense slides.
- **Meta-description titles** ("Resumen en bullets", "Detailed overview") — use the
  real subject as the title/subtitle.
- Inconsistent colors across slides.
- **Placeholders and fake assets.** Never add fake image captions ("[Imagen sin
  copyright] ...", "image here"), placeholder QR codes, or placeholder
  links/store/library buttons. Only include an image or a QR/link if it is real
  (provided, present in the source, or genuinely generated). If a visual would
  help, suggest it in the chat reply instead of putting a placeholder on a slide.
- **Reader tips / meta-commentary on a slide** (e.g. "Suggestion: try reading a
  scene aloud"). Put those in the chat reply, not in the deck.
- Forgetting `guardar_documento(prs)`.
