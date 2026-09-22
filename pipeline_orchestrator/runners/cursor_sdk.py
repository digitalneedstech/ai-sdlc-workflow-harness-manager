"""Cursor SDK runner. Enable with the orchestrator extra."""

from __future__ import annotations

import os
from pathlib import Path

from pipeline_orchestrator.runners.base import StepRequest, StepResult


class CursorSdkRunner:
    name = "cursor"

    def __init__(self, api_key: str | None = None) -> None:
        self.api_key = api_key or os.environ.get("CURSOR_API_KEY", "").strip()

    def is_available(self) -> bool:
        try:
            import cursor_sdk  # noqa: F401
        except ImportError:
            return False
        return bool(self.api_key)

    async def run(self, request: StepRequest) -> StepResult:
        if not self.api_key:
            return StepResult(ok=False, startup_failure=True, error="CURSOR_API_KEY is not set")
        try:
            from cursor_sdk import Agent, AgentOptions, LocalAgentOptions
        except ImportError:
            return StepResult(
                ok=False,
                startup_failure=True,
                error="cursor-sdk missing; install the orchestrator extra",
            )
        cwd = str((request.project or Path.cwd()).resolve())
        try:
            with Agent.create(model=request.model, api_key=self.api_key, local=LocalAgentOptions(cwd=cwd)) as agent:
                run = agent.send(request.prompt)
                agent_id = getattr(agent, "agent_id", "") or ""
                run_id = getattr(run, "id", "") or ""
                result = run.wait()
                status = getattr(result, "status", "") or ""
                if str(status).lower() == "error":
                    return StepResult(ok=False, status="error", agent_id=str(agent_id), run_id=str(run_id), model=request.model, error="cursor run status=error")
                return StepResult(ok=True, status=str(status or "finished"), agent_id=str(agent_id), run_id=str(run_id), model=request.model)
        except Exception as exc:
            name = type(exc).__name__
            startup = name == "CursorAgentError" or "api key" in str(exc).lower()
            return StepResult(ok=False, startup_failure=startup, error=f"{name}: {exc}", status="error")
