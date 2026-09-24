"""Generic OTLP/HTTP stub. Endpoint and auth only. Marked untested."""

from __future__ import annotations

from typing import Any

from pipeline_observability.adapters.base import AdapterConfig
from pipeline_observability.adapters.langfuse import otel_attributes
from pipeline_observability.pricing import event_usage_attrs


class OtlpAdapter:
    untested = True

    def __init__(self, config: AdapterConfig) -> None:
        self.config = config

    def endpoint(self) -> str:
        host = self.config.host.rstrip("/")
        return f"{host}/v1/traces"

    def auth_headers(self) -> dict[str, str]:
        if self.config.api_key:
            return {"Authorization": f"Bearer {self.config.api_key}"}
        return {}

    def map_attributes(self, event: dict[str, Any]) -> list[dict[str, Any]]:
        attrs: dict[str, Any] = {
            "gen_ai.request.model": event.get("model_id") or event.get("model"),
        }
        attrs.update(event_usage_attrs(event, include_langfuse=False))
        return otel_attributes(attrs)

    def post_traces(self, payload: dict[str, Any]) -> tuple[bool, str]:
        return False, "generic otlp adapter is a stub (untested)"

    def post_scores(self, batch: list[dict[str, Any]]) -> tuple[bool, str]:
        return True, "otlp has no score primitive; scores stay as span attributes"
