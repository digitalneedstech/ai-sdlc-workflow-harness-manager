"""Runner protocol."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Protocol


@dataclass
class StepRequest:
    prompt: str
    step_id: str
    slug: str
    project: Path | None = None
    model: str = "composer-2.5"
    mcp: tuple[str, ...] = ()
    extra: dict[str, str] = field(default_factory=dict)


@dataclass
class StepResult:
    ok: bool
    status: str = "finished"
    agent_id: str = ""
    run_id: str = ""
    model: str = ""
    tokens: dict[str, int] = field(default_factory=dict)
    error: str = ""
    startup_failure: bool = False
    payload: dict[str, Any] = field(default_factory=dict)


class AgentRunner(Protocol):
    name: str

    def is_available(self) -> bool: ...

    async def run(self, request: StepRequest) -> StepResult: ...
