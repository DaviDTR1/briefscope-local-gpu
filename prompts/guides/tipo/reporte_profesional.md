<!-- desc: Long professional report (analysis, due diligence, executive memo) with cover, executive summary, sections and conclusions. -->
# Type: Professional report

Structured, authoritative text document. Best in **PDF** or **DOCX** via `generar_documento_markdown`. If the client asks for strong brand identity, pass your own `estilo_css` (PDF) or use the code path.

## Recommended structure
1. **Cover / title** — clear title, subtitle, date, author/organization.
2. **Executive summary** — 3-6 sentences with the findings and the main recommendation. Everything should be understandable by reading this alone.
3. **Context / objective** — what was analyzed and why.
4. **Findings** — one section (`##`) per topic. Use subtitles, tables for figures and quotes for relevant source text.
5. **Analysis / implications** — what the findings mean.
6. **Recommendations** — actionable, prioritized.
7. **Conclusion** and, if applicable, **appendices** (supporting data, sources).

## Best practices
- Lean on the project's data: use `buscar_en_documentos` and cite specific figures/dates/clauses, not generalities.
- One claim, one piece of evidence. Avoid filler.
- Use tables for comparisons and numbers; prose for reasoning.
- Hierarchical Markdown headings (`#`, `##`, `###`) so the document has navigation and, in DOCX, real heading styles.
- Objective, professional tone. If there is uncertainty, state it.

## Mistakes to avoid
- Do not invent data that is not in the sources.
- Do not mix heading levels inconsistently.
- Avoid walls of text: break into digestible sections.
