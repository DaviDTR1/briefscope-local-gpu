<!-- desc: Data dashboard / control panel with metrics, tables and charts built from the project's data (Excel or visual PDF). -->
# Type: Dashboard / data panel

Data view with metrics, tables and charts. Two options depending on use:

- **XLSX** via `generar_documento_codigo` (openpyxl) — if the user will filter,
  edit or keep working with the data. Allows formulas, multiple sheets and native
  Excel charts.
- **PDF** via `generar_documento_codigo` (reportlab / matplotlib) — if it is a
  read-only visual report with KPIs and positioned charts.

## Recommended structure
1. **Header** — title, data period, generation date.
2. **KPI row** — 3-5 key metrics highlighted (big figure + label + variation).
3. **Charts** — primary trend (line) and main comparison (bar).
4. **Detail tables** — broken-down data, colored header, totals.
5. **Notes / data source**.

## Layout (reading order matters)
- Users scan in an **F/Z pattern**: top-left gets most attention. Put the single
  **most important KPI top-left**, largest and boldest.
- **Grid:** top row = 3-5 big-number KPI tiles (full width); middle = trend chart
  (line) left + comparison (bar) right; bottom = breakdowns / detail table.
- **5-9 metrics max** (cognitive limit ~7); engagement drops past ~12.

## Chart type per data
- **Line** = trend over time. **Bar/column** = comparison across categories.
  **Scatter** = correlation. **Pie** only for part-to-whole with 3-5 slices — never
  for ranked comparison.
- Minimize chartjunk: no 3D, no gridline clutter. Titles should state the takeaway
  ("Revenue up 12% QoQ"), not just label the axis.

## Color palettes (one accent, neutral base; never color alone — pair with label/icon)
- **Corporate cool:** `#1F2A44` (text/headers), `#5B8DEF` (accent), `#F4F6F8` (canvas), `#FFFFFF` (tiles), `#E03E36` (negative), `#2BB673` (positive).
- **Neutral + single accent:** `#111827` (ink), `#F59E0B` (accent), `#6B7280` (secondary), `#F9FAFB` (bg).
- **Sequential (heatmap low→high, ColorBrewer Blues):** `#F7FBFF` `#DEEBF7` `#C6DBEF` `#9ECAE1` `#6BAED6` `#4292C6` `#2171B5` `#08519C`.
- **Diverging (negative↔positive, RdYlBu):** `#D73027` `#FC8D59` `#FEE090` `#FFFFBF` `#E0F3F8` `#91BFDB` `#4575B4`.

## Best practices
- Extract the real figures from the project with `buscar_en_documentos`; do not invent data.
- KPIs first, detail after (inverted pyramid).
- In XLSX: colored header fill, `freeze_panes`, number formatting (`#,##0`, `0%`),
  **real formulas** for totals, and charts via `openpyxl.chart` referencing ranges.

## Mistakes to avoid
- Dumping a giant table with no summary or KPIs.
- Hex colors with `#` in openpyxl (they go without `#`).
- Computing in Python what should be an editable formula.
- Charts with no titles or axis labels; pie charts with many slices.
