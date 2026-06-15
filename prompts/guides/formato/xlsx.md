# Format guide: XLSX (Excel)

A single path: **`generar_documento_codigo`** with `formato: "xlsx"`. (There is no Markdown path for spreadsheets.)

You write Python with **openpyxl**. You have `OUTPUT_PATH` and the helper `guardar_documento(obj)` (accepts the workbook and calls `.save()`).

Contract:
- `formato`: `"xlsx"`
- `codigo_python`: build the `Workbook()` and end with `guardar_documento(wb)`.
- `nombre_archivo`: without extension.

Recommended skeleton:
```python
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter

wb = Workbook()
ws = wb.active
ws.title = "Summary"

headers = ["Item", "Q1", "Q2", "Total"]
ws.append(headers)
head_fill = PatternFill("solid", fgColor="0F3460")
for c in ws[1]:
    c.font = Font(bold=True, color="FFFFFF")
    c.fill = head_fill
    c.alignment = Alignment(horizontal="center")

ws.append(["Sales", 1000, 1200, "=B2+C2"])

# column width
for i, _ in enumerate(headers, 1):
    ws.column_dimensions[get_column_letter(i)].width = 18

ws.freeze_panes = "A2"
guardar_documento(wb)
```

Conditional formatting & charts (make the data read itself):
```python
from openpyxl.formatting.rule import ColorScaleRule, DataBarRule
from openpyxl.chart import BarChart, Reference
# green->red scale over a range
ws.conditional_formatting.add("B2:C4",
    ColorScaleRule(start_type="min", start_color="F8696B",
                   end_type="max", end_color="63BE7B"))
# data bars
ws.conditional_formatting.add("D2:D4", DataBarRule(start_type="min", end_type="max", color="2563EB"))
# native chart anchored to a cell
chart = BarChart(); chart.title = "By region"
data = Reference(ws, min_col=2, max_col=3, min_row=1, max_row=4)
chart.add_data(data, titles_from_data=True)
chart.set_categories(Reference(ws, min_col=1, min_row=2, max_row=4))
ws.add_chart(chart, "F2")
```

Best practices:
- **Call `consultar_guia_diseno()` first** for the palette hex (header fill, bars).
- Bold headers with a colored fill and `freeze_panes` to lock the title row.
- Use **real formulas** (`"=SUM(B2:B10)"`) instead of computing in Python when the user will want to edit them.
- Add `ColorScaleRule`/`DataBarRule`/`IconSetRule` and native charts for tables of numbers.
- Adjust `column_dimensions[...].width` so the content is readable.
- Apply number formatting with `cell.number_format = "#,##0.00"` or `"0%"`.
- For several sections use several sheets (`wb.create_sheet("Detail")`).

Common mistakes:
- Do not forget `guardar_documento(wb)` at the end.
- Colors go in hex **without** `#` (`"0F3460"`, not `"#0F3460"`).
- Formulas are written as a string starting with `=`.
- `wb.active` is the first already-created sheet; do not duplicate it with `create_sheet`.
