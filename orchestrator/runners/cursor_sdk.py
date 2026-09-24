"""Cursor SDK runner. Enable with the orchestrator extra."""

from __future__ import annotations

import os
from pathlib import Path

from pipeline_orchestrator.runners.base import StepRequest, StepResult


def _text(value: object) -> str:
    return str(value or "").strip()


def model_cards(models: object) -> dict[str, dict]:
    """Serializable Cursor catalog fields Jev can read for each model id."""
    items = models
    if hasattr(models, "models"):
        items = getattr(models, "models")
    elif isinstance(models, dict):
        items = models.get("models") or models.get("data") or models.get("items") or []
    if not isinstance(items, (list, tuple)):
        return {}
    cards: dict[str, dict] = {}
    for item in items:
        if isinstance(item, str):
            model_id = item.strip()
            card: dict = {}
        elif isinstance(item, dict):
            model_id = _text(item.get("id") or item.get("name"))
            card = _card_from_mapping(item)
        else:
            model_id = _text(getattr(item, "id", None) or getattr(item, "name", None))
            card = _card_from_object(item)
        if model_id and model_id not in cards:
            cards[model_id] = card
    return cards


def _card_from_mapping(item: dict) -> dict:
    variants = []
    for variant in item.get("variants") or []:
        if not isinstance(variant, dict):
            continue
        variants.append(
            {
                "display_name": _text(variant.get("display_name") or variant.get("displayName")),
                "description": _text(variant.get("description")),
                "is_default": bool(variant.get("is_default") or variant.get("isDefault")),
            }
        )
    parameters = []
    for param in item.get("parameters") or []:
        if not isinstance(param, dict):
            continue
        values = []
        for value in param.get("values") or []:
            if isinstance(value, dict):
                values.append(
                    {
                        "value": _text(value.get("value")),
                        "display_name": _text(value.get("display_name") or value.get("displayName")),
                    }
                )
        parameters.append(
            {
                "id": _text(param.get("id")),
                "display_name": _text(param.get("display_name") or param.get("displayName")),
                "values": values,
            }
        )
    return {
        "display_name": _text(item.get("display_name") or item.get("displayName")),
        "description": _text(item.get("description")),
        "parameters": parameters,
        "variants": variants,
    }


def _card_from_object(item: object) -> dict:
    variants = []
    for variant in getattr(item, "variants", ()) or []:
        variants.append(
            {
                "display_name": _text(getattr(variant, "display_name", "")),
                "description": _text(getattr(variant, "description", "")),
                "is_default": bool(getattr(variant, "is_default", False)),
            }
        )
    parameters = []
    for param in getattr(item, "parameters", ()) or []:
        values = []
        for value in getattr(param, "values", ()) or []:
            values.append(
                {
                    "value": _text(getattr(value, "value", "")),
                    "display_name": _text(getattr(value, "display_name", "")),
                }
            )
        parameters.append(
            {
                "id": _text(getattr(param, "id", "")),
                "display_name": _text(getattr(param, "display_name", "")),
                "values": values,
            }
        )
    return {
        "display_name": _text(getattr(item, "display_name", "")),
        "description": _text(getattr(item, "description", "")),
        "parameters": parameters,
        "variants": variants,
    }


def catalog_ids(payload: object) -> list[str]:
    """Normalize Cursor.models.list() into model id strings."""
    items: object = payload
    if hasattr(payload, "models"):
        items = getattr(payload, "models")
    elif isinstance(payload, dict):
        items = payload.get("models") or payload.get("data") or payload.get("items") or []
    if not isinstance(items, (list, tuple)):
        return []
    ids: list[str] = []
    for item in items:
        if isinstance(item, str):
            name = item.strip()
        elif isinstance(item, dict):
            name = str(item.get("id") or item.get("name") or "").strip()
        else:
            name = str(getattr(item, "id", None) or getattr(item, "name", "") or "").strip()
        if name and name not in ids:
            ids.append(name)
    return ids


class CursorSdkRunner:
    name = "cursor"

    def __init__(self, api_key: str | None = None) -> None:
        self.api_key = api_key or os.environ.get("CURSOR_API_KEY", "").strip()
        self._models: list[object] | None = None

    def _load_models(self) -> list[object]:
        if self._models is None:
            if not self.api_key:
                raise RuntimeError("CURSOR_API_KEY is not set")
            try:
                from cursor_sdk import Cursor
            except ImportError as exc:
                raise RuntimeError("cursor-sdk missing; install the orchestrator extra") from exc
            self._models = list(Cursor.models.list())
        return self._models

    def is_available(self) -> bool:
        try:
            import cursor_sdk  # noqa: F401
        except ImportError:
            return False
        return bool(self.api_key)

    def list_models(self) -> list[str]:
        return catalog_ids(self._load_models())

    def model_info(self) -> dict[str, dict]:
        return model_cards(self._load_models())

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
