"""Per-turn execution context shared across agents in a single chat turn."""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class RunContext:
    project_id: int
    doc_context: str = ""        # source-document context (used by the researcher)
    instructions: str = ""       # project-level instructions
    doc_names: list[str] = field(default_factory=list)  # filenames visible to the orchestrator
    saved_research: list[str] = field(default_factory=list)  # report names saved this turn
    generated_files: list[str] = field(default_factory=list)  # downloadable files this turn
    delegations: int = 0         # global sub-agent invocation counter (cap in §6)
