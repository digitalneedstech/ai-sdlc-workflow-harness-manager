"""Deterministic runner for tests."""

from __future__ import annotations

from pipeline_orchestrator.runners.base import StepRequest, StepResult
from pipeline_orchestrator.state import agent_state_path, utc_now, write_json


class FakeRunner:
    name = "fake"

    def __init__(self, results: dict[str, dict] | None = None, catalog: list[str] | None = None) -> None:
        self.results = results or {}
        self.calls: list[str] = []
        self.catalog = list(catalog) if catalog is not None else ["composer-2.5", "gpt-5.4-medium", "auto"]

    def is_available(self) -> bool:
        return True

    def list_models(self) -> list[str]:
        return list(self.catalog)

    def model_info(self) -> dict[str, dict]:
        return {}

    async def run(self, request: StepRequest) -> StepResult:
        self.calls.append(request.step_id)
        planned = dict(self.results.get(request.step_id) or {})
        status = str(planned.get("status") or "SUCCESS")
        if planned.get("reject_model") and request.model == planned.get("reject_model"):
            return StepResult(ok=False, status="error", error="invalid model %s" % request.model)
        if request.project is not None and not planned.get("omit_state"):
            write_json(
                agent_state_path(request.project, request.slug, request.step_id),
                {
                    "version": 1,
                    "agent": request.step_id,
                    "slug": request.slug,
                    "status": status,
                    "updated_at": utc_now(),
                    "context": {"next_agent": "stop", "next_must_read": []},
                },
            )
        if planned.get("startup_failure"):
            return StepResult(ok=False, status="error", startup_failure=True, error=str(planned.get("error") or "startup"))
        if planned.get("run_failure"):
            return StepResult(ok=False, status="error", error=str(planned.get("error") or "run"))
        return StepResult(ok=True, status="finished", agent_id=str(planned.get("agent_id") or "fake-agent"), run_id=str(planned.get("run_id") or "fake-run"), model=request.model, tokens={"input": 1, "output": 1})
