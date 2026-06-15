<!-- desc: Invoice, budget or quote with issuer/client details, line-item table, totals and taxes. -->
# Type: Invoice / quote

Commercial document with precise layout. Best in **PDF** via `generar_documento_codigo` (reportlab) if you want a branded header and well-aligned totals; or via `generar_documento_markdown` with your own `estilo_css` for a quick finish. For an editable workbook use **XLSX**.

## Essential elements
- **Header**: issuer name/logo, tax details (tax ID), address, contact.
- **Invoice/quote number** and **date** (and due or validity date).
- **Client details**: name, tax ID, address.
- **Line-item table**: description, quantity, unit price, amount.
- **Totals**: taxable base, taxes (VAT or others with their %), **total due** highlighted.
- **Payment terms**: method, account/IBAN, deadline.
- Notes or terms at the bottom if applicable.

## Best practices
- Align amounts to the right; use a thousands separator and 2 decimals.
- Compute and show taxes separately from the subtotal.
- The final total should stand out (bold, larger size or colored background).
- Number and date always visible at the top.

## Mistakes to avoid
- Forgetting tax details or the tax breakdown.
- Misaligned amounts or no currency formatting.
- Not including a document number.
- In XLSX, computing totals in Python instead of with formulas if the user will edit them.
