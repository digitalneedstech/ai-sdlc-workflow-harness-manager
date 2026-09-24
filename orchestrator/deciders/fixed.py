"""No-network decider. Pins win, then the configured fallback model."""

from __future__ import annotations

from pipeline_orchestrator.deciders.base import Decision, DecisionError, DecisionRequest
from pipeline_orchestrator.deciders.settings import OrchestratorSettings


def fallback_id(settings: OrchestratorSettings, catalog: tuple[str, ...]) -> str:
    if settings.fallback_model in catalog:
        return settings.fallback_model
    return catalog[0]


def resolve_static(
    request: DecisionRequest,
    settings: OrchestratorSettings,
    *,
    decider_name: str,
    fallback_reason: str,
) -> Decision:
    catalog = request.catalog
    if not catalog:
        raise DecisionError("model catalog is empty")
    fallback = fallback_id(settings, catalog)
    pin = (request.pin or "").strip()
    if pin:
        if pin not in catalog:
            raise DecisionError("pinned model %r is not in the catalog" % pin)
        return Decision(model=pin, reason="pin", decider=decider_name, fallback=fallback)
    step_model = (settings.steps.get(request.step_id) or "").strip()
    if step_model:
        if step_model not in catalog:
            raise DecisionError("configured model %r for %s is not in the catalog" % (step_model, request.step_id))
        return Decision(model=step_model, reason="config", decider=decider_name, fallback=fallback)
    return Decision(model=fallback, reason=fallback_reason, decider=decider_name, fallback=fallback)


class FixedDecider:
    name = "fixed"

    def __init__(self, settings: OrchestratorSettings) -> None:
        self.settings = settings

    def decide(self, request: DecisionRequest) -> Decision:
        return resolve_static(
            request,
            self.settings,
            decider_name=self.name,
            fallback_reason="fixed",
        )
