"""
Declarative agent definitions for the BriefScope multi-agent system.

Three roles, each with a system-prompt file and an allow-list of tools:

  ORCHESTRATOR  — talks to the user and handles simple tasks itself (a quick RAG
                  lookup, reading a document or a saved report, answering within
                  its capacity). It delegates detailed investigation to the
                  researcher and document creation to the creator.
                  Tools: RAG search + save/read research + invoke researcher +
                  invoke the creator.
  RESEARCHER    — runs detailed investigations, summaries, study plans, reports…
                  over the project documents, saves the full report in Markdown
                  and returns a brief description plus the saved report name.
                  Tools: RAG search + read documents/research + save research.
  CREATOR       — turns a research report into a downloadable document.
                  Tools: read research + format guide + generate document.

This module is provider-agnostic: nothing here knows about Anthropic, OpenAI,
Google or Ollama. The same definitions drive every plugin variant.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from app import config

_AGENT_PROMPTS_DIR = Path(__file__).resolve().parent.parent.parent / "prompts" / "agents"


@dataclass(frozen=True)
class AgentDef:
    name: str
    prompt_file: str
    tools: tuple[str, ...]

    @property
    def max_rounds(self) -> int:
        return int(config.get("agent_max_rounds", 8))

    def render_system(
        self,
        *,
        instructions: str = "",
        doc_context: str = "",
        doc_list: str = "",
        guias_tipo: str = "",
    ) -> str:
        """Load the role prompt and inject instructions / document context.

        Uses str.replace (not str.format) so literal braces in the prompt or in
        the injected content never raise KeyError.
        """
        path = _AGENT_PROMPTS_DIR / self.prompt_file
        try:
            template = path.read_text(encoding="utf-8")
        except OSError:
            template = f"You are the {self.name} agent of BriefScope.\n{{instructions}}\n{{doc_context}}"
        return (
            template
            .replace("{instructions}", instructions or "")
            .replace("{doc_context}", doc_context or "")
            .replace("{documentos_disponibles}", doc_list or "")
            .replace("{guias_tipo}", guias_tipo or "")
            .strip()
        )


# Tool names handled specially by the runtime (they spawn sub-agents).
AGENT_INVOCATION_TOOLS = ("invocar_investigador", "invocar_creador_documentos")

# Search/research tools the orchestrator uses to gather information itself.
RESEARCH_TOOLS = (
    "buscar_en_documentos",
    "leer_documento_fuente",
    "guardar_investigacion",
    "leer_investigacion",
    "leer_documento",
)

# Tools the researcher uses to investigate the project documents and save its
# report. No invocation tools — the researcher never spawns further sub-agents.
RESEARCHER_TOOLS = (
    "buscar_en_documentos",
    "leer_documento_fuente",
    "leer_documento",
    "leer_investigacion",
    "guardar_investigacion",
)

ORCHESTRATOR = AgentDef(
    name="orquestador",
    prompt_file="orquestador.md",
    tools=RESEARCH_TOOLS + ("invocar_investigador", "invocar_creador_documentos"),
)

RESEARCHER = AgentDef(
    name="investigador",
    prompt_file="investigador.md",
    tools=RESEARCHER_TOOLS,
)

CREATOR = AgentDef(
    name="creador",
    prompt_file="creador.md",
    tools=(
        "consultar_guia_formato",
        "consultar_guia_diseno",
        "consultar_guia_tipo",
        "leer_investigacion",
        "leer_documento",
        "generar_documento_markdown",
        "generar_documento_codigo",
    ),
)

BY_NAME = {a.name: a for a in (ORCHESTRATOR, RESEARCHER, CREATOR)}
