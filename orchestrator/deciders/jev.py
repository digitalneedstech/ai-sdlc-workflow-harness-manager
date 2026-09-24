"""Jev (TypeSafe System One) implementation of the model decider."""

from __future__ import annotations

import os
from typing import Protocol

from pipeline_orchestrator.deciders.base import Decision, DecisionRequest, capability_for
from pipeline_orchestrator.deciders.fixed import resolve_static
from pipeline_orchestrator.deciders.settings import KNOWN_KINDS, OrchestratorSettings

_CHOICE_LIMIT = 255
_HINTS = {
    "composer-2.5": "Fast coding model. Fit for implementation, tests, and delivery. Poor fit for planning, architecture, and review.",
    "composer-2.5-fast": "Faster coding model. Fit for implementation and tests. Poor fit for planning and review.",
    "gpt-5.4-medium": "Reasoning model. Fit for planning, architecture, and review. Heavier than a fast coding model.",
    "gpt-5.5": "Strong reasoning model. Fit for planning, architecture, and review. Prefer this over Composer for those jobs.",
    "gpt-5.6-sol": "Strong reasoning model. Fit for planning, architecture, and review. Prefer this over Composer for those jobs.",
    "claude-opus-5": "Strong reasoning model. Fit for planning, architecture, and review. Prefer this over Composer for those jobs.",
    "grok-4.5": "General model. Mid-weight. Weaker than Opus or GPT for planning and review. Fine for short writing.",
    "grok-4.6": "General model. Mid-weight. Weaker than Opus or GPT for planning and review. Fine for implementation and short writing.",
    "grok-4.7": "General model. Mid-weight. Weaker than Opus or GPT for planning and review. Fine for short writing.",
    "auto": "Let Cursor choose. Use only when no listed model matches the capability.",
}


class JevUnavailable(Exception):
    """The decision service could not answer. The caller uses the fallback model."""


class JevAnswer:
    def __init__(
        self,
        *,
        choice: str,
        confidence: float,
        probabilities: dict[str, float] | None = None,
        jev_model: str = "",
    ) -> None:
        self.choice = choice
        self.confidence = confidence
        self.probabilities = dict(probabilities or {})
        self.jev_model = jev_model


class JevClient(Protocol):
    def choose(
        self,
        *,
        state: dict,
        options: dict[str, dict],
        model: str,
    ) -> JevAnswer: ...


class TypeSafeJevClient:
    """Calls `typesafe-sdk` only when a decision is requested."""

    def choose(
        self,
        *,
        state: dict,
        options: dict[str, dict],
        model: str,
    ) -> JevAnswer:
        if not os.environ.get("TYPESAFE_API_KEY", "").strip():
            raise JevUnavailable("TYPESAFE_API_KEY is not set")
        try:
            from typesafe_sdk import Choice, TypeSafeClient
        except ImportError as exc:
            raise JevUnavailable("typesafe-sdk missing; install the orchestrator extra") from exc
        questions = {
            "model": Choice(
                instructions={
                    "question": "Which listed model should execute this agent?",
                    "rule": (
                        "Match `capability` in the state to each option. "
                        "Read that option's description, display_name, fit, and for_this_agent. "
                        "Never pick an option whose for_this_agent says Poor fit. "
                        "Planning, architecture, and review need Claude Opus or GPT. "
                        "Implementation, verification, and delivery need Composer. "
                        "Do not pick Composer for planning, architecture, or review."
                    ),
                },
                criteria=dict(options),
            )
        }
        try:
            with TypeSafeClient() as client:
                try:
                    response = client.system_one(state=state, questions=questions, model=model)
                except TypeError:
                    response = client.system_one(state=state, questions=questions)
        except JevUnavailable:
            raise
        except Exception as exc:
            raise JevUnavailable("%s: %s" % (type(exc).__name__, exc)) from exc
        answer = response.choices["model"]
        probabilities = {
            str(key): float(value) for key, value in dict(answer.probabilities).items()
        }
        return JevAnswer(
            choice=str(answer.choice),
            confidence=float(answer.confidence),
            probabilities=probabilities,
            jev_model=str(getattr(response, "model", "") or model),
        )


def _overlay(model_id: str, cards: dict[str, dict] | None) -> dict:
    raw = (cards or {}).get(model_id)
    return raw if isinstance(raw, dict) else {}


def _hint(model_id: str, cards: dict[str, dict] | None = None) -> str:
    custom = str(_overlay(model_id, cards).get("fit") or "").strip()
    if custom:
        return custom
    known = _HINTS.get(model_id)
    if known:
        return known
    lowered = model_id.lower()
    if "composer" in lowered:
        return _HINTS["composer-2.5"]
    if any(token in lowered for token in ("opus", "sonnet", "gpt", "claude", "thinking", "reason", "fable", "astra")):
        return "Reasoning model. Fit for planning, architecture, and review. Heavier than a fast coding model."
    if "grok" in lowered:
        return "General model. Mid-weight. Weaker than Opus or GPT for planning and review."
    return "Cursor model %s. Match it to the agent capability." % model_id


def _kind(model_id: str, cards: dict[str, dict] | None = None) -> str:
    custom = str(_overlay(model_id, cards).get("kind") or "").strip().lower()
    if custom in KNOWN_KINDS:
        return custom
    lowered = model_id.lower()
    if "composer" in lowered:
        return "coding"
    if any(token in lowered for token in ("opus", "sonnet", "gpt", "claude", "thinking", "reason", "fable", "astra")):
        return "reasoning"
    if "grok" in lowered:
        return "general"
    return "unknown"


def _need_kind(step_id: str) -> str:
    text = capability_for(step_id)
    if text.startswith(("planning", "architecture", "review")):
        return "reasoning"
    if text.startswith(("implementation", "verification", "delivery")):
        return "coding"
    if text.startswith("writing"):
        return "writing"
    return "general"


def _for_this_agent(step_id: str, model_id: str, cards: dict[str, dict] | None = None) -> str:
    need = _need_kind(step_id)
    kind = _kind(model_id, cards)
    if need == "reasoning":
        if kind == "reasoning":
            return "Good fit for this agent. Prefer this over Composer."
        if kind == "coding":
            return "Poor fit for this agent. Do not pick for planning, architecture, or review."
        return "Acceptable. Prefer Claude Opus or GPT if listed."
    if need == "coding":
        if kind == "coding":
            return "Good fit for this agent."
        if kind == "reasoning":
            return "Capable but heavier than needed. Prefer Composer for implementation and tests."
        return "Acceptable for implementation."
    if need == "writing":
        if kind == "coding":
            return "Acceptable. A smaller writing or general model is enough."
        return "Good fit for a short write-up."
    return "Match this model to the agent capability."


def _select_names(
    catalog: tuple[str, ...],
    candidates: tuple[str, ...],
    fallback: str,
) -> list[str]:
    names = [item for item in catalog if item]
    if candidates:
        wanted = [item for item in candidates if item in names]
        if fallback and fallback in names and fallback not in wanted:
            wanted.append(fallback)
        if wanted:
            names = wanted
    if len(names) > _CHOICE_LIMIT:
        trimmed = names[:_CHOICE_LIMIT]
        if fallback and fallback not in trimmed:
            trimmed = trimmed[:-1] + [fallback]
        names = trimmed
    return names


def _criteria(
    model_id: str,
    info: dict,
    step_id: str = "",
    cards: dict[str, dict] | None = None,
) -> dict:
    overlay = _overlay(model_id, cards)
    card = {"fit": _hint(model_id, cards)}
    if step_id:
        card["for_this_agent"] = _for_this_agent(step_id, model_id, cards)
    display_name = str(overlay.get("display_name") or info.get("display_name") or "").strip()
    description = str(overlay.get("description") or info.get("description") or "").strip()
    if display_name:
        card["display_name"] = display_name
    if description:
        card["description"] = description
    variants = info.get("variants") or []
    parameters = info.get("parameters") or []
    if variants:
        card["variants"] = variants
    if parameters:
        card["parameters"] = parameters
    return card


def _options(
    catalog: tuple[str, ...],
    fallback: str,
    model_info: dict[str, dict] | None = None,
    candidates: tuple[str, ...] = (),
    step_id: str = "",
    cards: dict[str, dict] | None = None,
) -> dict[str, dict]:
    names = _select_names(catalog, candidates, fallback)
    info = model_info or {}
    return {name: _criteria(name, info.get(name) or {}, step_id, cards) for name in names}


class JevDecider:
    name = "jev"

    def __init__(self, settings: OrchestratorSettings, client: JevClient | None = None) -> None:
        self.settings = settings
        self.client = client or TypeSafeJevClient()

    def decide(self, request: DecisionRequest) -> Decision:
        pinned = (request.pin or "").strip() or (self.settings.steps.get(request.step_id) or "").strip()
        if pinned:
            return resolve_static(
                request,
                self.settings,
                decider_name=self.name,
                fallback_reason="fixed",
            )
        options = _options(
            request.catalog,
            self.settings.fallback_model,
            request.model_info,
            candidates=self.settings.candidates,
            step_id=request.step_id,
            cards=self.settings.cards,
        )
        try:
            answer = self.client.choose(
                state={
                    "user_request": request.user_request,
                    "workflow": request.workflow,
                    "change_class": request.change_class,
                    "agent": request.step_id,
                    "job": request.job,
                    "capability": capability_for(request.step_id),
                    "prior_handoff_status": request.prior_status or "none",
                },
                options=options,
                model=self.settings.jev_model,
            )
        except JevUnavailable:
            decision = resolve_static(
                request,
                self.settings,
                decider_name=self.name,
                fallback_reason="jev_unavailable",
            )
            decision.evaluated = list(options)
            decision.criteria = dict(options)
            decision.capability = capability_for(request.step_id)
            return decision
        if answer.choice in request.catalog and answer.confidence >= self.settings.min_confidence:
            fallback = resolve_static(
                request,
                self.settings,
                decider_name=self.name,
                fallback_reason="fixed",
            ).fallback
            return Decision(
                model=answer.choice,
                reason="jev",
                decider=self.name,
                fallback=fallback,
                confidence=answer.confidence,
                probabilities=answer.probabilities,
                jev_model=answer.jev_model,
                jev_choice=answer.choice,
                evaluated=list(options),
                criteria=dict(options),
                capability=capability_for(request.step_id),
            )
        reason = "low_confidence" if answer.choice in request.catalog else "jev_unavailable"
        decision = resolve_static(
            request,
            self.settings,
            decider_name=self.name,
            fallback_reason=reason,
        )
        decision.confidence = answer.confidence
        decision.probabilities = dict(answer.probabilities)
        decision.jev_model = answer.jev_model
        decision.jev_choice = answer.choice
        decision.evaluated = list(options)
        decision.criteria = dict(options)
        decision.capability = capability_for(request.step_id)
        return decision
