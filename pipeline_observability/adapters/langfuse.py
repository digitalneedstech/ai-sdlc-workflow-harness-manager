"""Langfuse OTLP traces + scores API. Does not use the Langfuse SDK."""

from __future__ import annotations

from typing import Any

from pipeline_observability.adapters.base import AdapterConfig
from pipeline_observability.adapters.httputil import basic_auth, post_json


def _attr(key: str, value: Any) -> dict[str, Any] | None:
    if value is None:
        return None
    if isinstance(value, list):
        return {
            "key": key,
            "value": {"arrayValue": {"values": [{"stringValue": str(item)} for item in value if item is not None]}},
        }
    if isinstance(value, bool):
        return {"key": key, "value": {"boolValue": value}}
    if isinstance(value, int) and not isinstance(value, bool):
        return {"key": key, "value": {"intValue": str(value)}}
    if isinstance(value, float):
        return {"key": key, "value": {"doubleValue": value}}
    return {"key": key, "value": {"stringValue": str(value)}}


def otel_attributes(pairs: dict[str, Any]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for key, value in pairs.items():
        item = _attr(key, value)
        if item:
            out.append(item)
    return out


class LangfuseAdapter:
    def __init__(self, config: AdapterConfig) -> None:
        self.config = config

    def endpoint(self) -> str:
        return f"{self.config.host.rstrip('/')}/api/public/otel/v1/traces"

    def scores_url(self) -> str:
        return f"{self.config.host.rstrip('/')}/api/public/scores"

    def _root(self) -> str:
        return self.config.host.rstrip("/")

    def auth_headers(self) -> dict[str, str]:
        return {
            "Authorization": basic_auth(self.config.public_key, self.config.secret_key),
            "x-langfuse-ingestion-version": "4",
        }

    def _json_headers(self) -> dict[str, str]:
        return {"Authorization": basic_auth(self.config.public_key, self.config.secret_key)}

    def map_attributes(self, event: dict[str, Any]) -> list[dict[str, Any]]:
        return otel_attributes(
            {
                "pipeline.step": event.get("step"),
                "pipeline.slug": event.get("slug"),
                "pipeline.workflow": event.get("workflow"),
                "tool.name": event.get("tool_name"),
                "tool.kind": event.get("tool_kind"),
                "tool.verdict": event.get("verdict"),
                "tool.confidence": event.get("confidence"),
                "tool.path": event.get("target_path"),
                "gen_ai.request.model": event.get("model"),
                "gen_ai.usage.input_tokens": (event.get("tokens") or {}).get("input_tokens"),
                "gen_ai.usage.output_tokens": (event.get("tokens") or {}).get("output_tokens"),
            }
        )

    def post_traces(self, payload: dict[str, Any]) -> tuple[bool, str]:
        ok, detail, _status = post_json(self.endpoint(), payload, self.auth_headers())
        return ok, detail

    def post_scores(self, batch: list[dict[str, Any]]) -> tuple[bool, str]:
        headers = self._json_headers()
        errors: list[str] = []
        for item in batch:
            ok, detail, _status = post_json(self.scores_url(), item, headers, retries=8)
            if not ok:
                errors.append(detail)
        if errors:
            return False, "; ".join(errors[:3])
        return True, f"posted {len(batch)} scores"

    def create_score_config(self, payload: dict[str, Any]) -> tuple[bool, str]:
        """Idempotent-ish: Langfuse rejects duplicate names with 400/409 — treat as exists."""
        ok, detail, status = post_json(
            f"{self._root()}/api/public/score-configs",
            payload,
            self._json_headers(),
            retries=3,
        )
        if ok or status in (400, 409):
            return True, str(payload.get("name") or "")
        return False, detail

    def ensure_dataset(self, name: str) -> tuple[bool, str]:
        ok, detail, status = post_json(
            f"{self._root()}/api/public/datasets",
            {"name": name, "description": "pipeline-kit agent runs (deterministic scores)"},
            self._json_headers(),
            retries=3,
        )
        if ok or status == 409:
            return True, name
        return False, detail

    def upsert_dataset_item(self, payload: dict[str, Any]) -> tuple[bool, str]:
        ok, detail, status = post_json(
            f"{self._root()}/api/public/dataset-items",
            payload,
            self._json_headers(),
            retries=3,
        )
        if ok or status == 409:
            return True, str(payload.get("id") or "")
        return False, detail

    def create_dataset_run_item(self, payload: dict[str, Any]) -> tuple[bool, str]:
        ok, detail, _status = post_json(
            f"{self._root()}/api/public/dataset-run-items",
            payload,
            self._json_headers(),
            retries=3,
        )
        return ok, detail
