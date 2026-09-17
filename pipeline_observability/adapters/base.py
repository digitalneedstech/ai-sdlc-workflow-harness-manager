"""Adapter contract for shipping scored runs."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Protocol


@dataclass
class AdapterConfig:
    name: str
    host: str
    public_key: str = ""
    secret_key: str = ""
    api_key: str = ""


class Adapter(Protocol):
    def endpoint(self) -> str: ...

    def auth_headers(self) -> dict[str, str]: ...

    def map_attributes(self, event: dict[str, Any]) -> list[dict[str, Any]]: ...

    def post_scores(self, batch: list[dict[str, Any]]) -> tuple[bool, str]: ...

    def post_traces(self, payload: dict[str, Any]) -> tuple[bool, str]: ...
