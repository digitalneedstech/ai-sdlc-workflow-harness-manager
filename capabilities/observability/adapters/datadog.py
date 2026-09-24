"""Datadog stub. Endpoint and auth only. Marked untested."""

from __future__ import annotations

from typing import Any

from pipeline_observability.adapters.base import AdapterConfig
from pipeline_observability.adapters.langfuse import otel_attributes
from pipeline_observability.pricing import event_usage_attrs


class DatadogAdapter:
    untested = True

    def __init__(self, config: AdapterConfig) -> None:
        self.config = config

    def endpoint(self) -> str:
        host = self.config.host.rstrip("/") or "https://trace.agent.datadoghq.com"
        return f"{host}/v0.4/traces"

    def auth_headers(self) -> dict[str, str]:
        return {"DD-API-KEY": self.config.api_key}

    def map_attributes(self, event: dict[str, Any]) -> list[dict[str, Any]]:
        attrs: dict[str, Any] = {
            "gen_ai.request.model": event.get("model_id") or event.get("model"),
        }
        attrs.update(event_usage_attrs(event, include_langfuse=False))
        return otel_attributes(attrs)

    def post_traces(self, payload: dict[str, Any]) -> tuple[bool, str]:
        return False, "datadog adapter is a stub (untested)"

    def post_scores(self, batch: list[dict[str, Any]]) -> tuple[bool, str]:
        return False, "datadog adapter is a stub (untested)"
