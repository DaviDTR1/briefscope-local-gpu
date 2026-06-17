"""
Single tool registry for the multi-agent system.

One definition per tool, expressed as a LangChain StructuredTool. Because the
whole stack runs on LangChain, there is no second (OpenAI/Ollama) schema to keep
in sync — `bind_tools` accepts these directly for every provider.

Tools fall into two groups:

  * "executable" tools whose Python func runs server-side and returns a string
    (consultar_guia_formato, consultar_guia_tipo, buscar_en_documentos,
    guardar_investigacion, leer_investigacion, leer_documento).

  * "intercepted" tools whose schema is bound so the model can call them, but
    whose *effect* is handled by the runtime:
      - generar_documento_markdown -> rapid Markdown engine + __file_ready__
      - generar_documento_codigo   -> code (Python) engine + __file_ready__
      - invocar_creador_documentos -> runtime spawns the creator sub-agent
    Their func is a stub that is never executed.
"""
from __future__ import annotations

from langchain_core.tools import StructuredTool
from pydantic import BaseModel, Field

from app.agents.context import RunContext
from app.services.documents import read_format_guide, read_type_guide, read_design_guide


# --------------------------------------------------------------------------- #
# Argument schemas
# --------------------------------------------------------------------------- #
class _ConsultarGuiaFormatoInput(BaseModel):
    formato: str = Field(description="File format: pdf, docx, xlsx, pptx, html, md, txt.")


class _ConsultarGuiaDisenoInput(BaseModel):
    tema: str = Field(
        default="",
        description="Optional focus hint (e.g. 'pptx', 'paletas', 'tipografia'). "
        "The full design system is returned regardless.",
    )


class _ConsultarGuiaTipoInput(BaseModel):
    tipo: str = Field(
        description="Document type slug (e.g. reporte_profesional, presentacion, "
        "factura, carta, dashboard). See the guides catalog in your prompt."
    )


class _BuscarInput(BaseModel):
    consulta: str = Field(
        description="Natural-language query, specific and focused on the data you seek. "
        "E.g.: 'total Q1 2024 sales', 'termination clauses'."
    )


class _BuscarWebInput(BaseModel):
    consulta: str = Field(
        description="Web search query in natural language, specific and focused. "
        "E.g.: 'modern report color palette hex', 'professional slide layout best practices'."
    )


class _GuardarInvestigacionInput(BaseModel):
    nombre: str = Field(description="Descriptive name for the content, without extension.")
    contenido_md: str = Field(
        description="The full source content in Markdown that the creator will turn into a "
        "document (report, CV text, letter, summary, data...)."
    )


class _LeerInvestigacionInput(BaseModel):
    nombre: str = Field(description="Name of the research file to read.")


class _LeerDocumentoInput(BaseModel):
    nombre: str = Field(
        description="Name of the generated document file to read (with or without extension)."
    )


class _LeerDocumentoFuenteInput(BaseModel):
    nombre: str = Field(
        description="Name of the uploaded SOURCE document to read (with or without extension)."
    )
    parte: int = Field(
        default=1,
        description="Part number to read when the document is too large to return at once. "
        "Start at 1; the tool tells you how many parts there are and which to read next.",
    )


class _GenerarMarkdownInput(BaseModel):
    formato: str = Field(description="Output format: docx, pdf, html, txt or md.")
    contenido_markdown: str = Field(
        description="The document written in Markdown (headings, lists, tables, "
        "bold/italic, quotes, code blocks). It is converted to the requested format."
    )
    nombre_archivo: str = Field(description="Name without extension. Only letters, numbers and hyphens.")
    estilo_css: str | None = Field(
        default=None,
        description="Optional CSS for pdf/html (@page, body, h1, table... rules). "
        "If omitted, a default professional style is used.",
    )


class _GenerarCodigoInput(BaseModel):
    formato: str = Field(description="Output format: docx, pdf, pptx or xlsx.")
    codigo_python: str = Field(
        description="Python code that builds the document with the format's library "
        "(python-docx / reportlab / python-pptx / openpyxl). You have the variable "
        "OUTPUT_PATH and the helper guardar_documento(objeto). End by calling "
        "guardar_documento(objeto) (or save to OUTPUT_PATH yourself)."
    )
    nombre_archivo: str = Field(description="Name without extension. Only letters, numbers and hyphens.")


class _InvocarInvestigadorInput(BaseModel):
    tarea: str = Field(
        description="The investigation to carry out over the project documents: a detailed "
        "summary, study plan, report, analysis, etc. Describe clearly what to research and "
        "what the resulting report should cover."
    )


class _InvocarCreadorInput(BaseModel):
    nombre_informe: str = Field(
        description="Name of the saved source content to use as the base."
    )
    instruccion: str = Field(
        description="What document to generate, with what changes and style. Be explicit if it is "
        "replicate/modify (e.g. 'replicate this CV changing the role to X') and in what format."
    )
    formato: str | None = Field(
        default=None,
        description="Desired format (pdf, docx, xlsx, pptx, html, md, txt) or empty to let the creator choose.",
    )


# --------------------------------------------------------------------------- #
# Executable tool funcs
# --------------------------------------------------------------------------- #
def _build_executable(name: str, ctx: RunContext) -> StructuredTool:
    if name == "consultar_guia_formato":
        return StructuredTool(
            name="consultar_guia_formato",
            description=(
                "Returns the technical guide for a format (which tool to use, the exact "
                "input contract and the common mistakes to avoid). Call it BEFORE generating "
                "to produce the file without errors. Formats: pdf, docx, xlsx, pptx, html, md, txt."
            ),
            func=read_format_guide,
            args_schema=_ConsultarGuiaFormatoInput,
        )

    if name == "consultar_guia_diseno":
        return StructuredTool(
            name="consultar_guia_diseno",
            description=(
                "Returns the DESIGN system: curated color palettes (with hex), font "
                "pairings, spacing scale and ready-to-use visual recipes (PPTX with an "
                "embedded chart, branded PDF/HTML CSS, XLSX conditional formatting + "
                "chart, DOCX styles). Call it BEFORE designing so the document looks "
                "professional and consistent. Pick one palette and one font pairing and "
                "reuse them across the whole document."
            ),
            func=read_design_guide,
            args_schema=_ConsultarGuiaDisenoInput,
        )

    if name == "consultar_guia_tipo":
        return StructuredTool(
            name="consultar_guia_tipo",
            description=(
                "Returns a best-practices guide for a TYPE of document (professional report, "
                "presentation, invoice, letter, dashboard...). Use it when the request matches "
                "a type in the catalog, to structure it with quality. The catalog with "
                "descriptions is in your prompt."
            ),
            func=read_type_guide,
            args_schema=_ConsultarGuiaTipoInput,
        )

    if name == "buscar_en_documentos":
        from app.services.rag import retrieve, format_rag_context

        def _search(consulta: str) -> str:
            chunks = retrieve(ctx.project_id, consulta)
            if not chunks:
                return (
                    "No relevant fragments were found for: "
                    f"'{consulta}'. Try more specific terms."
                )
            return format_rag_context(chunks)

        return StructuredTool(
            name="buscar_en_documentos",
            description=(
                "Searches for specific information inside the project's documents (RAG). "
                "Use it ONLY when you need data you do not already have in front of you: figures, "
                "dates, names, clauses or tables that are in documents not included in the context. "
                "If the relevant document already appears in full in your context, use it directly "
                "instead of searching. You do not have to call it on every request."
            ),
            func=_search,
            args_schema=_BuscarInput,
        )

    if name == "buscar_en_web":
        from app.services.web_search import search_web

        def _search_web(consulta: str) -> str:
            return search_web(consulta)

        return StructuredTool(
            name="buscar_en_web",
            description=(
                "Searches the public web (DuckDuckGo) for external references that are "
                "NOT in the project's documents. The creator uses it to look up document "
                "design references: color palettes, font pairings, layouts, presentation "
                "and typography best practices. Returns a list of results with title, URL "
                "and snippet. Use it to complement — not replace — the project documents; "
                "for data that lives in the uploaded files use buscar_en_documentos instead."
            ),
            func=_search_web,
            args_schema=_BuscarWebInput,
        )

    if name == "guardar_investigacion":
        from app.services.research_store import save_research

        def _save(nombre: str, contenido_md: str) -> str:
            filename = save_research(nombre, contenido_md)
            ctx.saved_research.append(filename)
            return (
                f"Content saved as '{filename}'. "
                "Pass this exact name to invocar_creador_documentos."
            )

        return StructuredTool(
            name="guardar_investigacion",
            description=(
                "Saves in Markdown the SOURCE CONTENT that the creator will turn into a document "
                "(a report, the text of a CV, a letter, a summary, data...) and returns its "
                "filename. It is the bridge to invocar_creador_documentos. It does not have to "
                "be 'research': use it whenever you are going to generate a document, with the "
                "material already gathered."
            ),
            func=_save,
            args_schema=_GuardarInvestigacionInput,
        )

    if name == "leer_investigacion":
        from app.services.research_store import read_research

        def _read(nombre: str) -> str:
            return read_research(nombre)

        return StructuredTool(
            name="leer_investigacion",
            description=(
                "Reads the saved source content (report, CV text, letter, data...), "
                "by its filename."
            ),
            func=_read,
            args_schema=_LeerInvestigacionInput,
        )

    if name == "leer_documento":
        from app.services.documents import read_generated

        def _read_doc(nombre: str) -> str:
            return read_generated(ctx.project_id, nombre)

        return StructuredTool(
            name="leer_documento",
            description=(
                "Reads the text content of an ALREADY GENERATED document (the downloadable file: "
                "pdf, docx, xlsx, pptx, html, md, txt), by its name. Use it when you need "
                "to review or modify a document delivered earlier."
            ),
            func=_read_doc,
            args_schema=_LeerDocumentoInput,
        )

    if name == "leer_documento_fuente":
        from app.services.documents import read_source_document

        def _read_source(nombre: str, parte: int = 1) -> str:
            return read_source_document(ctx.project_id, nombre, parte)

        return StructuredTool(
            name="leer_documento_fuente",
            description=(
                "Reads the full text of a SOURCE document the user uploaded (the original "
                "PDF/DOCX/TXT...), by its name. Use it when you need to read a whole document "
                "to analyze it in depth or quote it verbatim — not just search fragments. If "
                "the document is too large for one read, it is returned in sequential parts: "
                "call again with the next 'parte' to keep reading until the end. For a targeted "
                "lookup of a specific datum, prefer buscar_en_documentos."
            ),
            func=_read_source,
            args_schema=_LeerDocumentoFuenteInput,
        )

    raise KeyError(name)


# --------------------------------------------------------------------------- #
# Intercepted tool stubs (schema only — runtime handles the effect)
# --------------------------------------------------------------------------- #
def _stub(**_: object) -> str:  # pragma: no cover - never executed
    return ""


def _build_intercepted(name: str) -> StructuredTool:
    if name == "generar_documento_markdown":
        return StructuredTool(
            name="generar_documento_markdown",
            description=(
                "FAST PATH: generates a downloadable document from Markdown that you write. "
                "Formats: docx, pdf, html, txt, md. It is the default path for structured text: "
                "reports, letters, CVs, memos, documentation, summaries. Call "
                "consultar_guia_formato first."
            ),
            func=_stub,
            args_schema=_GenerarMarkdownInput,
        )
    if name == "generar_documento_codigo":
        return StructuredTool(
            name="generar_documento_codigo",
            description=(
                "ONLY for generating a document by running Python code that you write "
                "(python-docx / reportlab / python-pptx / openpyxl). Formats: docx, pdf, pptx, "
                "xlsx. Use it when you need custom design that Markdown does not allow: colors, "
                "fonts, charts, dashboards, certificates, exact positioning; and ALWAYS "
                "for pptx and xlsx. For normal structured text use the fast path (markdown). "
                "Call consultar_guia_formato first."
            ),
            func=_stub,
            args_schema=_GenerarCodigoInput,
        )
    if name == "invocar_investigador":
        return StructuredTool(
            name="invocar_investigador",
            description=(
                "Launches the researcher agent for detailed investigation over the project "
                "documents: in-depth summaries, study plans, reports, analyses. The researcher "
                "searches the RAG, reads documents, writes the full report in Markdown, saves it, "
                "and returns a brief description plus the saved report name. Use it when the task "
                "needs real investigation — not for a simple lookup you can answer yourself."
            ),
            func=_stub,
            args_schema=_InvocarInvestigadorInput,
        )
    if name == "invocar_creador_documentos":
        return StructuredTool(
            name="invocar_creador_documentos",
            description=(
                "Launches the creator agent to generate a downloadable file (create, replicate or "
                "modify a document) from the source content you saved. Use it whenever "
                "the user wants a document, not only for research reports."
            ),
            func=_stub,
            args_schema=_InvocarCreadorInput,
        )
    raise KeyError(name)


_INTERCEPTED = {
    "generar_documento_markdown",
    "generar_documento_codigo",
    "invocar_investigador",
    "invocar_creador_documentos",
}


def build_tools(tool_names: tuple[str, ...], ctx: RunContext) -> tuple[list, dict]:
    """Return (tools_for_bind_tools, executables_by_name) for an agent.

    `tools_for_bind_tools` includes intercepted tools (schema only) so the model
    can call them. `executables_by_name` maps only the runnable tools, which the
    runtime invokes directly.
    """
    bound: list = []
    executables: dict = {}
    for name in tool_names:
        if name in _INTERCEPTED:
            bound.append(_build_intercepted(name))
        else:
            tool = _build_executable(name, ctx)
            bound.append(tool)
            executables[name] = tool
    return bound, executables
