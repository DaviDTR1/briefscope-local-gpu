<!-- desc: Data dashboard / control panel with metrics, tables and charts built from the project's data (Excel or visual PDF). -->
# Type: Dashboard / data panel

Data view with metrics, tables and charts. Two options depending on use:

- **XLSX** via `generar_documento_codigo` (openpyxl) — if the user will want to filter, edit or keep working with the data. Allows formulas, multiple sheets and native Excel charts.
- **PDF** via `generar_documento_codigo` (reportlab) — if it is a read-only visual report with KPIs and positioned charts.

## Recommended structure
1. **Header** — title, data period, generation date.
2. **Main KPIs** — 3-6 key metrics highlighted (big figure + label + variation).
3. **Detail tables** — broken-down data, with a colored header and totals.
4. **Charts** — trends or comparisons (bar, line, pie) as appropriate.
5. **Notes / data source**.

## Best practices
- Extract the real figures from the project with `buscar_en_documentos`; do not invent data.
- KPIs first, detail after (inverted pyramid).
- In XLSX: headers with colored fill, `freeze_panes`, number formatting (`#,##0`, `0%`) and **real formulas** for totals.
- In XLSX you can add charts with `openpyxl.chart` (BarChart, LineChart) referencing ranges.
- Coherent palette, consistent with the brand if known.

## Mistakes to avoid
- Dumping a giant table with no summary or KPIs.
- Hex colors with `#` in openpyxl (they go without `#`).
- Computing in Python what should be an editable formula.
- Charts with no titles or axis labels.
