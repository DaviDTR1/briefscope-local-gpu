<!-- desc: Invoice, budget or quote with issuer/client details, line-item table, totals and taxes. -->
# Type: Invoice / quote

Commercial document with precise layout. Best in **PDF** via
`generar_documento_codigo` (reportlab) if you want a branded header and
well-aligned totals; or via `generar_documento_markdown` with your own `estilo_css`
for a quick finish. For an editable workbook use **XLSX**.

## Required elements (a professional invoice must include all of these)
- The word **"Invoice"** (or "Quote") clearly at the top.
- **Unique invoice number** — sequential is the legal/tax expectation
  (e.g. `INV-2025-001`).
- **Issue date** and **due date** (or terms like "Net 30", "Due on receipt").
- **Seller**: name/logo, full address, contact, and **tax ID** (EIN/VAT) where required.
- **Buyer**: name, address (and tax ID for VAT invoices).
- **Line items**: description, quantity, unit price, line amount.
- **Subtotal**, **tax/VAT** (rate and amount shown separately), **total amount due**.
- **Payment terms**: accepted methods, account/IBAN, deadline.
- Notes or terms at the bottom if applicable.

Tax authorities expect a unique, sequential number and the seller tax ID; PDF is
the preferred delivery format (preserves layout, not silently editable).

## Layout rules
- Header: logo + "Invoice" + number top; seller and buyer blocks side-by-side beneath.
- **Right-align every numeric column** (qty, unit price, amount) so digits line up.
- **Total due goes bottom-right**, directly under the line-item table.
- **Emphasize the total due** — largest/boldest number, in the darkest tone or an
  accent block, isolated with whitespace.
- Generous margins; thousands separator and 2 decimals; show the currency.

## Color palettes (pick one; one accent only on header + total)
- **Slate Professional:** `#1E293B` (header/total), `#475569` (labels), `#E2E8F0` (rows), `#FFFFFF` (bg), `#0EA5E9` (accent).
- **Teal Accountant:** `#0F766E` (header/total), `#134E4A` (text), `#F0FDFA` (row tint), `#FFFFFF` (bg), `#CCFBF1` (band).

## Best practices
- Compute and show taxes separately from the subtotal.
- Number and date always visible at the top.
- In XLSX, use **real formulas** for subtotal/tax/total if the user will edit it.

## Mistakes to avoid
- Forgetting the tax details or the tax breakdown.
- Misaligned amounts or no currency formatting.
- Not including a document number.
- Hex colors with `#` in openpyxl (they go without `#`).
- Computing totals in Python instead of with formulas in an editable XLSX.
