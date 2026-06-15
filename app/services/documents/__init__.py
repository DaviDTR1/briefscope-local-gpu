"""
Document generation & retrieval for BriefScope.

Two complementary generation engines give the agent full design freedom:

  rapid_generator  — Markdown in, document out. Fast path for simple/standard
                     documents. Markdown -> DOCX (pandoc), PDF (WeasyPrint),
                     HTML (markdown lib) or TXT (plain strip).

  code_generator   — Python code in, document out. The agent writes the code
                     (python-docx / reportlab / python-pptx / openpyxl) and it
                     runs in an isolated subprocess. Total control over layout,
                     colours, fonts and charts. DOCX / PDF / PPTX / XLSX.

  store            — locate, read and persist generated files (+ source sidecar
                     so a deliverable can be re-read and modified faithfully).

  guides           — read the format/type knowledge guides and list the type
                     guides with their short descriptions.
"""
from __future__ import annotations

from app.services.documents.rapid_generator import generate_markdown
from app.services.documents.code_generator import generate_code
from app.services.documents.store import (
    read_generated,
    save_source_sidecar,
    save_metadata,
    read_metadata,
    list_generated,
    project_dir,
    safe_generated_path,
    delete_generated,
)
from app.services.documents.guides import (
    read_format_guide,
    read_type_guide,
    list_type_guides,
    type_guides_catalog,
)

__all__ = [
    "generate_markdown",
    "generate_code",
    "read_generated",
    "save_source_sidecar",
    "save_metadata",
    "read_metadata",
    "list_generated",
    "project_dir",
    "safe_generated_path",
    "delete_generated",
    "read_format_guide",
    "read_type_guide",
    "list_type_guides",
    "type_guides_catalog",
]
