<!-- desc: Long professional report (analysis, due diligence, executive memo) with cover, executive summary, sections and conclusions. -->
# Type: Professional report

Structured, authoritative text document. Best in **PDF** or **DOCX** via
`generar_documento_markdown`. If the client asks for strong brand identity, pass
your own `estilo_css` (PDF) or use the code path.

## Recommended structure
1. **Cover / title** — clear title, subtitle, date, author/organization.
2. **Executive summary** — see below.
3. **Table of contents** (for longer reports).
4. **Context / objective** — what was analyzed and why (purpose and scope).
5. **Findings** — one section (`##`) per topic. Subtitles, tables for figures,
   quotes for relevant source text.
6. **Analysis / implications** — what the findings mean.
7. **Recommendations** — actionable, prioritized.
8. **Conclusion** and, if applicable, **references** and **appendices** (supporting
   data, large tables, sources).

## The executive summary (write it last)
- It must work as a **standalone**: a reader who reads only this gets the full core message.
- Cover purpose, key findings and primary recommendation.
- Length ~1 page, or **5-10% of the report**. Use subheadings / a few bullets for fast scanning.

## Color palettes (pick one)
- **Corporate blue/slate:** Navy `#1B2A4A`, Steel blue `#3E5C76`, Slate `#708090`, Pale `#DCE3EA`, White `#FFFFFF`.
- **Modern teal/charcoal:** Charcoal `#2B2D31`, Teal `#1F8A8A`, Light teal `#76C4C4`, Warm gray `#E5E5E2`, White `#FFFFFF`.
- **Elegant burgundy/grey:** Burgundy `#6E1423`, Deep grey `#3A3A3A`, Mid grey `#8C8C8C`, Light grey `#ECECEC`, White `#FFFFFF`.

Use a neutral anchor (navy/charcoal) for headings and 1-2 accents for chart series.

## Layout guidance
- Margins ~1 inch (2.54 cm); body line spacing 1.0-1.15.
- Three heading levels max (H1 section / H2 subsection / H3 detail), stepped sizes
  (e.g. body 11-12pt, then 14 / 18 / 24pt).
- Place each chart/table **inline right after the paragraph that references it**,
  numbered and captioned (Figure 1 / Table 1); push large datasets to appendices.

## Best practices
- Lean on the project's data: use `buscar_en_documentos` and cite specific
  figures/dates/clauses, not generalities.
- One claim, one piece of evidence. Avoid filler.
- Tables for comparisons and numbers; prose for reasoning.
- Hierarchical Markdown headings so the document has navigation and real DOCX heading styles.
- Objective, professional tone. State uncertainty when it exists.

## Mistakes to avoid
- Inventing data not in the sources.
- Inconsistent heading levels.
- Walls of text — break into digestible sections.
