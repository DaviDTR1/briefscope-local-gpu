"""
Unified agent runtime (LangChain, provider-agnostic).

A single agentic loop drives every agent — Anthropic, OpenAI, Google or Ollama —
because each is a LangChain chat model. There is no separate cloud/local loop.

Streaming protocol (raw strings, consumed unchanged by routers/chat.py):
  - plain text fragments                          -> SSE "token"
  - '{"__thinking__": "..."}'                     -> SSE "thinking"
  - '{"__file_ready__": true, "filename": ...}'   -> SSE "file_ready"

The orchestrator searches the project documents itself and answers the user.
When a downloadable deliverable is wanted it saves its findings as a research
report and delegates only the document creation to the creator sub-agent.

Visible text is only streamed from the TOP-LEVEL agent (the orchestrator).
The creator sub-agent runs with stream_text=False: its reasoning is captured as
the tool result handed back to the orchestrator; only its thinking/file_ready
markers bubble up so the UI keeps showing progress.

Risk mitigations (plan §6) enforced here:
  - agent_max_rounds: tool rounds per agent.
  - agent_max_depth:  orchestrator -> sub-agent nesting cap.
  - max_delegations:  global sub-agent invocations per turn.
  - pipeline mode:    sequential search -> creator fallback for models that
                      handle nested tool-calling poorly.
"""
from __future__ import annotations

import json
from typing import AsyncGenerator

from langchain_core.messages import SystemMessage, HumanMessage, AIMessage, ToolMessage

from app import config
from app.logging_config import logger
from app.agents.context import RunContext
from app.agents.definitions import AgentDef, ORCHESTRATOR, RESEARCHER, CREATOR, RESEARCH_TOOLS
from app.agents.registry import build_tools
from app.services.llm.provider import build_llm

_TOOL_LABEL = {
    "buscar_en_documentos":        "Searching information in documents",
    "consultar_guia_formato":      "Consulting format guide",
    "consultar_guia_tipo":         "Consulting type guide",
    "guardar_investigacion":       "Saving research",
    "leer_investigacion":          "Reading research",
    "leer_documento":              "Reading document",
    "generar_documento_markdown":  "Generating document (Markdown)",
    "generar_documento_codigo":    "Generating document (code)",
    "invocar_investigador":        "Researching the documents",
    "invocar_creador_documentos":  "Creating document",
}


# Tool arguments that may carry large payloads (full document bodies/code).
# They are summarized as a size, never logged verbatim.
_BIG_ARG_KEYS = ("contenido_markdown", "codigo_python", "estilo_css", "contenido_md")


def _args_summary(args: dict) -> str:
    """Compact, log-friendly view of tool args (large payloads shown as a size)."""
    parts = []
    for key, value in (args or {}).items():
        if key in _BIG_ARG_KEYS:
            parts.append(f"{key}=<{len(str(value))} chars>")
        else:
            text = str(value)
            parts.append(f"{key}={text[:77] + '…' if len(text) > 80 else text}")
    return ", ".join(parts) if parts else "(no args)"


def _thinking(msg: str) -> str:
    return json.dumps({"__thinking__": msg})


def _is_marker(s: str) -> bool:
    return s.startswith('{"__thinking__"') or s.startswith('{"__file_ready__"')


def _to_lc_messages(messages: list[dict]) -> list:
    lc = []
    for m in messages:
        role = m.get("role")
        content = m.get("content", "")
        if role == "user":
            lc.append(HumanMessage(content=content))
        elif role == "system":
            lc.append(SystemMessage(content=content))
        else:
            lc.append(AIMessage(content=content))
    return lc


def _extract_text(chunk) -> str:
    c = chunk.content
    if isinstance(c, str):
        return c
    if isinstance(c, list):
        return "".join(
            b.get("text", "") if isinstance(b, dict) and b.get("type") == "text" else ""
            for b in c
        )
    return ""


def _format_doc_list(names: list[str]) -> str:
    """Render the orchestrator-visible list of document filenames (names only)."""
    if not names:
        return "No documents have been loaded into the project yet."
    items = "\n".join(f"- {n}" for n in names)
    return (
        "Names of the documents loaded into the project (names only, "
        "never their content):\n" + items
    )


def _system_for(agent: AgentDef, ctx: RunContext) -> str:
    is_orch = agent.name == "orquestador"
    instructions = ctx.instructions if is_orch else ""
    doc_context = ctx.doc_context if is_orch else ""
    doc_list = _format_doc_list(ctx.doc_names) if is_orch else ""
    # The creator browses the type-guide catalog to pick the right playbook.
    guias_tipo = ""
    if not is_orch:
        from app.services.documents import type_guides_catalog
        guias_tipo = type_guides_catalog()
    return agent.render_system(
        instructions=instructions,
        doc_context=doc_context,
        doc_list=doc_list,
        guias_tipo=guias_tipo,
    )


# --------------------------------------------------------------------------- #
# Core single-agent loop
# --------------------------------------------------------------------------- #
async def run_agent(
    agent: AgentDef,
    messages: list[dict],
    ctx: RunContext,
    *,
    depth: int,
    stream_text: bool,
    result_sink: list[str],
    tools: tuple[str, ...] | None = None,
) -> AsyncGenerator[str, None]:
    """Run one agent's tool loop. Yields markers (always) and visible text (only
    when stream_text). Appends the agent's final text to result_sink.

    `tools` overrides the agent's default tool allow-list (used by the pipeline
    fallback to run the orchestrator with search-only, no-nesting tools)."""
    try:
        base_llm = build_llm()
    except ValueError as exc:
        if stream_text:
            yield str(exc)
        result_sink.append(str(exc))
        return

    bound, executables = build_tools(tools if tools is not None else agent.tools, ctx)
    llm = base_llm.bind_tools(bound) if bound else base_llm

    logger.info(
        "[agent:%s] start (depth=%d, max_rounds=%d, stream_text=%s, project=%s)",
        agent.name, depth, agent.max_rounds, stream_text, ctx.project_id,
    )

    lc_messages = [SystemMessage(content=_system_for(agent, ctx))] + _to_lc_messages(messages)
    final_text = ""

    for _round in range(agent.max_rounds):
        chunks = []
        text_started = False
        try:
            async for chunk in llm.astream(lc_messages):
                text = _extract_text(chunk)
                if text:
                    if stream_text:
                        if not text_started:
                            yield _thinking("")
                            text_started = True
                        yield text
                    final_text += text
                chunks.append(chunk)
        except Exception as exc:
            logger.exception("Error en astream (%s): %s", agent.name, exc)
            msg = f"\n[Error LLM: {exc}]"
            if stream_text:
                yield msg
            final_text += msg
            break

        if not chunks:
            break

        full = chunks[0]
        for c in chunks[1:]:
            full = full + c

        tool_calls = getattr(full, "tool_calls", None) or []
        if not tool_calls:
            break

        ai_msg = AIMessage(
            content=full.content if isinstance(full.content, str) else "",
            tool_calls=tool_calls,
        )
        new_msgs: list = [ai_msg]

        for tc in tool_calls:
            name = tc.get("name", "")
            args = tc.get("args", {}) or {}
            call_id = tc.get("id", f"call_{_round}")

            logger.info(
                "[agent:%s] tool → %s(%s)", agent.name, name, _args_summary(args),
            )
            yield _thinking(_TOOL_LABEL.get(name, name))

            if name in ("invocar_investigador", "invocar_creador_documentos"):
                async for ev, result in _delegate(name, args, ctx, depth):
                    if ev is not None:
                        yield ev
                    if result is not None:
                        new_msgs.append(ToolMessage(content=result, tool_call_id=call_id))

            elif name in ("generar_documento_markdown", "generar_documento_codigo"):
                formato = (args.get("formato") or "txt").lower().strip()
                nombre = args.get("nombre_archivo", "documento")
                yield _thinking(f"Generating {formato.upper()}")
                result = ""
                try:
                    if name == "generar_documento_markdown":
                        from app.services.documents import (
                            generate_markdown, save_source_sidecar, save_metadata,
                        )
                        contenido = args.get("contenido_markdown", "")
                        filename = generate_markdown(
                            ctx.project_id, contenido, formato, nombre,
                            estilo_css=args.get("estilo_css"),
                        )
                        save_source_sidecar(ctx.project_id, filename, contenido)
                    else:
                        from app.services.documents import (
                            generate_code, save_source_sidecar, save_metadata,
                        )
                        codigo = args.get("codigo_python", "")
                        gen = generate_code(ctx.project_id, codigo, formato, nombre)
                        if not gen["success"]:
                            raise RuntimeError(
                                "The code did not generate the document. Fix it and retry.\n"
                                f"stderr:\n{gen['stderr']}"
                            )
                        filename = gen["filename"]
                        save_source_sidecar(ctx.project_id, filename, codigo)

                    save_metadata(ctx.project_id, filename, title=nombre, formato=formato)
                    ctx.generated_files.append(filename)
                    yield json.dumps({"__file_ready__": True, "filename": filename, "formato": formato})
                    result = (
                        f"File '{filename}' generated successfully. "
                        "You can generate more documents if the user needs them."
                    )
                except Exception as exc:
                    logger.exception("Error %s: %s", name, exc)
                    result = f"Error generating file: {exc}"
                new_msgs.append(ToolMessage(content=result, tool_call_id=call_id))

            else:
                tool = executables.get(name)
                if tool is None:
                    result = f"Unknown tool: {name}"
                else:
                    try:
                        result = tool.invoke(args)
                        logger.info(
                            "[agent:%s] tool ✓ %s (%d chars)",
                            agent.name, name, len(str(result)),
                        )
                    except Exception as exc:
                        logger.exception("Error tool %s: %s", name, exc)
                        result = f"Error in {name}: {exc}"
                new_msgs.append(ToolMessage(content=str(result), tool_call_id=call_id))

        lc_messages = lc_messages + new_msgs

    logger.info("[agent:%s] done (%d chars)", agent.name, len(final_text.strip()))
    result_sink.append(final_text.strip())


async def _delegate(name: str, args: dict, ctx: RunContext, depth: int):
    """Spawn a sub-agent. Yields (marker_or_None, result_or_None) pairs:
    markers stream out as they arrive; a single final (None, result) carries the
    tool result for the caller."""
    max_depth = int(config.get("agent_max_depth", 2))
    max_delegations = int(config.get("max_delegations", 4))

    if depth + 1 > max_depth or ctx.delegations >= max_delegations:
        logger.warning(
            "[delegate] limit reached (depth=%d/%d, delegations=%d/%d) — not delegating",
            depth + 1, max_depth, ctx.delegations, max_delegations,
        )
        yield None, (
            "Delegation limit reached. Answer the user with the "
            "information already available without delegating further."
        )
        return

    ctx.delegations += 1

    # invocar_investigador → researcher sub-agent. It investigates the documents,
    # saves the full report in Markdown and returns a brief description + the
    # saved report name, which the orchestrator can hand to the creator later.
    if name == "invocar_investigador":
        logger.info(
            "[delegate] → researcher sub-agent (depth=%d, delegation #%d)",
            depth + 1, ctx.delegations,
        )
        tarea = args.get("tarea", "")
        before = len(ctx.saved_research)
        sink: list[str] = []
        user_text = f"Investigation task:\n{tarea}"
        async for ev in run_agent(
            RESEARCHER, [{"role": "user", "content": user_text}], ctx,
            depth=depth + 1, stream_text=False, result_sink=sink,
        ):
            yield ev, None
        sub_text = sink[0] if sink else ""
        saved = ctx.saved_research[-1] if len(ctx.saved_research) > before else "(none)"
        yield None, f"{sub_text}\n\n[SAVED_RESEARCH: {saved}]"
        return

    # invocar_creador_documentos → creator sub-agent.
    logger.info(
        "[delegate] → creator sub-agent (depth=%d, delegation #%d)",
        depth + 1, ctx.delegations,
    )
    nombre_informe = args.get("nombre_informe", "")
    instruccion = args.get("instruccion", "")
    formato = args.get("formato") or "the most appropriate one"
    sink = []
    user_text = (
        f"Source content: {nombre_informe}\n"
        f"Instruction: {instruccion}\n"
        f"Desired format: {formato}"
    )
    async for ev in run_agent(
        CREATOR, [{"role": "user", "content": user_text}], ctx,
        depth=depth + 1, stream_text=False, result_sink=sink,
    ):
        yield ev, None
    sub_text = sink[0] if sink else ""
    files = ", ".join(ctx.generated_files) if ctx.generated_files else "(none)"
    yield None, f"{sub_text}\n\n[GENERATED_FILES: {files}]"
    return


# --------------------------------------------------------------------------- #
# Entry points
# --------------------------------------------------------------------------- #
async def run_orchestrated(messages: list[dict], ctx: RunContext) -> AsyncGenerator[str, None]:
    """Default 'agentic' mode: the orchestrator reasons with sub-agents as tools."""
    yield _thinking("Analyzing request")
    sink: list[str] = []
    async for ev in run_agent(
        ORCHESTRATOR, messages, ctx, depth=0, stream_text=True, result_sink=sink,
    ):
        yield ev


# --------------------------------------------------------------------------- #
# Pipeline fallback (risk mitigation §6)
# --------------------------------------------------------------------------- #
_DOC_KEYWORDS = (
    # Spanish
    "genera", "generar", "documento", "descargable", "archivo", "informe en",
    "presentacion", "presentación", "diapositiv", "hoja de calculo", "hoja de cálculo",
    # English
    "generate", "create", "make", "document", "downloadable", "file", "report in",
    "presentation", "slide", "spreadsheet", "letter", "invoice",
    # Format names (both languages)
    "pdf", "word", "docx", "excel", "xlsx", "powerpoint", "pptx",
)
_FORMAT_KEYWORDS = {
    "pdf": "pdf", "word": "docx", "docx": "docx", "excel": "xlsx", "xlsx": "xlsx",
    "powerpoint": "pptx", "pptx": "pptx", "presentaci": "pptx", "presentation": "pptx",
    "diapositiv": "pptx", "slide": "pptx", "spreadsheet": "xlsx", "markdown": "md",
}


def _wants_document(text: str) -> bool:
    low = text.lower()
    return any(k in low for k in _DOC_KEYWORDS)


def _detect_format(text: str) -> str | None:
    low = text.lower()
    for k, fmt in _FORMAT_KEYWORDS.items():
        if k in low:
            return fmt
    return None


async def run_pipeline(messages: list[dict], ctx: RunContext) -> AsyncGenerator[str, None]:
    """Sequential fallback for weak models: the SAME main agent gathers the
    information, but with flat (no-nesting) search tools; then—if the user wants
    a document—the creator is invoked deterministically. No nested tool-calling,
    so it works with models that handle it poorly."""
    user_message = ""
    for m in reversed(messages):
        if m.get("role") == "user":
            user_message = m.get("content", "")
            break

    wants_doc = _wants_document(user_message)

    # Main agent searches the documents directly, with flat tools only.
    yield _thinking("Gathering information from the documents")
    sink: list[str] = []
    async for ev in run_agent(
        ORCHESTRATOR, messages, ctx,
        depth=1, stream_text=not wants_doc, result_sink=sink,
        tools=RESEARCH_TOOLS,
    ):
        yield ev

    research_text = sink[0] if sink else ""

    if not wants_doc:
        # The plain-text answer was already streamed by the agent above.
        if not research_text:
            yield _thinking("")
            yield "The query could not be completed."
        return

    # Document requested: persist the findings and hand them to the creator.
    report = ctx.saved_research[-1] if ctx.saved_research else None
    if report is None:
        from app.services.research_store import save_research
        report = save_research("research", research_text or "No relevant information.")
        ctx.saved_research.append(report)

    fmt = _detect_format(user_message) or "the most appropriate one"
    async for ev, _ in _delegate(
        "invocar_creador_documentos",
        {"nombre_informe": report, "instruccion": user_message, "formato": fmt},
        ctx, depth=0,
    ):
        if ev is not None:
            yield ev
    yield _thinking("")
    yield "I have generated the requested document from the information in your documents."
