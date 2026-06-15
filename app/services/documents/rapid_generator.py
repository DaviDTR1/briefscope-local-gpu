"""
Rapid document generation from Markdown.

The agent writes natural Markdown; this engine converts it to the requested
format. Fast path for simple/standard documents that don't need bespoke layout.

  DOCX  -> pandoc            (rich Word, editable)
  PDF   -> WeasyPrint        (Markdown -> HTML -> PDF, full Unicode + CSS)
  HTML  -> markdown library  (standalone styled page)
  TXT   -> Markdown stripped to plain text

For total layout control (charts, certificates, precise coordinates) use the
code generator instead.
"""
from __future__ import annotations

import os
import re
import subprocess
import tempfile
from pathlib import Path

from app.logging_config import logger
from app.services.documents.store import build_dest

_VALID = ("docx", "pdf", "html", "txt", "md")

# Clean, neutral-professional stylesheet used for PDF/HTML when the agent does
# not supply its own CSS.
_DEFAULT_CSS = """
/* Slate Professional palette: primary #1E293B, accent #2563EB, ink #0F172A,
   muted #64748B, surface #F8FAFC. Serif headings + sans body, with web-safe
   fallbacks so WeasyPrint always has a font. */
@page {
    size: A4; margin: 22mm;
    @bottom-center { content: counter(page) " / " counter(pages);
                     font-family: 'Lato','Inter','DejaVu Sans',sans-serif;
                     font-size: 8pt; color: #94A3B8; }
}
body {
    font-family: 'Lato', 'Inter', 'DejaVu Sans', 'Segoe UI', Arial, sans-serif;
    color: #0F172A; line-height: 1.58; font-size: 11pt;
}
h1 { font-family: 'Lora','Liberation Serif',Georgia,serif; color: #1E293B;
     font-size: 23pt; border-bottom: 3px solid #2563EB; padding-bottom: 5px;
     margin: 0 0 16px; line-height: 1.2; }
h2 { color: #1E293B; font-size: 16pt; margin: 24px 0 8px; font-weight: 700; }
h3 { color: #334155; font-size: 12.5pt; margin: 18px 0 6px; font-weight: 700; }
p  { margin: 0 0 10px; }
a  { color: #2563EB; text-decoration: none; }
ul, ol { margin: 0 0 11px 22px; }
li { margin: 0 0 4px; }
strong { color: #1E293B; }
hr { border: none; border-top: 1px solid #E2E8F0; margin: 20px 0; }
table { border-collapse: collapse; width: 100%; margin: 16px 0; font-size: 10pt; }
th, td { border: 1px solid #E2E8F0; padding: 7px 10px; text-align: left; vertical-align: top; }
th { background: #1E293B; color: #ffffff; font-weight: 700; }
tr:nth-child(even) td { background: #F8FAFC; }
code { background: #F1F5F9; padding: 1px 5px; border-radius: 3px; color: #334155;
       font-family: 'DejaVu Sans Mono', monospace; font-size: 9.5pt; }
pre { background: #F1F5F9; padding: 12px 14px; border-radius: 6px; overflow-x: auto;
      border: 1px solid #E2E8F0; }
blockquote { border-left: 4px solid #2563EB; margin: 16px 0; padding: 4px 18px;
             color: #475569; background: #F8FAFC; border-radius: 0 4px 4px 0; }
"""


def generate_markdown(
    project_id: int,
    markdown_content: str,
    formato: str,
    nombre: str,
    *,
    estilo_css: str | None = None,
) -> str:
    """Generate a document from Markdown. Returns the generated filename."""
    fmt = formato.lower().strip()
    if fmt not in _VALID:
        raise ValueError(
            f"Format '{formato}' is not supported in Markdown mode. "
            f"Use one of {_VALID} or switch to the code tool (pptx/xlsx)."
        )

    dest = build_dest(project_id, fmt, nombre)
    titulo = (nombre or "Document").strip() or "Document"

    if fmt == "docx":
        _md_to_docx(markdown_content, dest, titulo)
    elif fmt == "pdf":
        _md_to_pdf(markdown_content, dest, estilo_css, titulo)
    elif fmt == "html":
        _md_to_html(markdown_content, dest, estilo_css, titulo)
    elif fmt == "md":
        dest.write_text(markdown_content, encoding="utf-8")
    else:  # txt
        dest.write_text(_strip_markdown(markdown_content), encoding="utf-8")

    logger.info("Document (markdown) generated: %s (%d bytes)", dest.name, dest.stat().st_size)
    return dest.name


# --------------------------------------------------------------------------- #
# Converters
# --------------------------------------------------------------------------- #
def _md_to_docx(content: str, dest: Path, titulo: str = "Document") -> None:
    with tempfile.NamedTemporaryFile("w", suffix=".md", delete=False, encoding="utf-8") as tmp:
        tmp.write(content)
        tmp_path = tmp.name
    try:
        subprocess.run(
            ["pandoc", tmp_path, "-o", str(dest), "--from", "gfm", "--to", "docx",
             "--metadata", f"title={titulo}"],
            check=True, capture_output=True, text=True, timeout=60,
        )
    except FileNotFoundError as exc:
        raise RuntimeError("pandoc is not installed in the container.") from exc
    except subprocess.CalledProcessError as exc:
        raise RuntimeError(f"pandoc failed to generate DOCX: {exc.stderr}") from exc
    finally:
        os.unlink(tmp_path)


def _md_to_pdf(content: str, dest: Path, estilo_css: str | None, titulo: str = "Document") -> None:
    from weasyprint import HTML

    html = _md_to_html_string(content, estilo_css, titulo)
    HTML(string=html).write_pdf(str(dest))


def _md_to_html(content: str, dest: Path, estilo_css: str | None, titulo: str = "Document") -> None:
    dest.write_text(_md_to_html_string(content, estilo_css, titulo), encoding="utf-8")


def _md_to_html_string(content: str, estilo_css: str | None, titulo: str = "Document") -> str:
    import html as _html
    import markdown

    # `md_in_html` lets Markdown written *inside* raw HTML wrappers (e.g. a
    # two-column <div markdown="1">...</div> used for layout) be parsed instead
    # of leaking through as literal text. `attr_list` allows {: ...} attributes.
    body = markdown.markdown(
        content,
        extensions=["tables", "fenced_code", "sane_lists", "nl2br", "md_in_html", "attr_list"],
    )
    css = estilo_css if estilo_css else _DEFAULT_CSS
    safe_title = _html.escape(titulo)
    return (
        "<!DOCTYPE html>\n<html lang=\"en\">\n<head>\n<meta charset=\"utf-8\">\n"
        f"<title>{safe_title}</title>\n<style>{css}</style>\n</head>\n<body>\n"
        f"{body}\n</body>\n</html>"
    )


def _strip_markdown(content: str) -> str:
    text = content
    text = re.sub(r"```.*?```", "", text, flags=re.DOTALL)   # code blocks
    text = re.sub(r"`(.+?)`", r"\1", text)                    # inline code
    text = re.sub(r"^#{1,6}\s+", "", text, flags=re.MULTILINE)  # headers
    text = re.sub(r"\*\*\*(.+?)\*\*\*", r"\1", text)          # bold+italic
    text = re.sub(r"\*\*(.+?)\*\*", r"\1", text)              # bold
    text = re.sub(r"(?<!\*)\*(?!\*)(.+?)(?<!\*)\*(?!\*)", r"\1", text)  # italic
    text = re.sub(r"!\[.*?\]\(.+?\)", "", text)               # images
    text = re.sub(r"\[(.+?)\]\(.+?\)", r"\1", text)           # links
    return text.strip() + "\n"
