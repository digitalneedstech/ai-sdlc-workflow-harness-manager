"""USD cost for generation spans. Hooks still never send dollars — flush computes them.

Kit defaults are public list-price approximations (USD per million tokens). Override
per project with ``agent_observability.model_prices`` in ``.pipeline/config.json``.
Unknown and placeholder models (``auto-smart``, …) omit cost so Langfuse can still
infer from its own model catalog.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Any, Mapping

PLACEHOLDER_MODELS = frozenset(
    {"auto-smart", "auto", "default", "composer", "inherit", "unknown"}
)


def is_placeholder_model(name: Any) -> bool:
    if not isinstance(name, str):
        return True
    stripped = name.strip()
    return not stripped or stripped.lower() in PLACEHOLDER_MODELS


# USD per 1M tokens. cache_read is discounted; cache_write is often a write premium.
_DEFAULTS: dict[str, tuple[float, float, float, float]] = {
    # model: (input, output, cache_read, cache_write)
    "grok-4.6": (3.0, 15.0, 0.30, 3.75),
    "grok-4": (3.0, 15.0, 0.30, 3.75),
    "grok-3": (3.0, 15.0, 0.30, 3.75),
    "grok-code": (0.20, 1.50, 0.02, 0.25),
    "claude-opus-4": (15.0, 75.0, 1.50, 18.75),
    "claude-sonnet-4": (3.0, 15.0, 0.30, 3.75),
    "claude-haiku-4": (0.80, 4.0, 0.08, 1.00),
    "claude-3.5-sonnet": (3.0, 15.0, 0.30, 3.75),
    "claude-3.5-haiku": (0.80, 4.0, 0.08, 1.00),
    "claude-3-5-sonnet": (3.0, 15.0, 0.30, 3.75),
    "gpt-5": (1.25, 10.0, 0.125, 1.25),
    "gpt-4.1": (2.0, 8.0, 0.50, 2.0),
    "gpt-4o": (2.50, 10.0, 1.25, 2.50),
    "gpt-4o-mini": (0.15, 0.60, 0.075, 0.15),
    "o3": (2.0, 8.0, 0.50, 2.0),
    "o4-mini": (1.10, 4.40, 0.275, 1.10),
    "gemini-2.5-pro": (1.25, 10.0, 0.125, 1.25),
    "gemini-2.5-flash": (0.15, 0.60, 0.015, 0.15),
}

_ALIASES = {
    "claude-4-opus": "claude-opus-4",
    "claude-4-sonnet": "claude-sonnet-4",
    "claude-4-haiku": "claude-haiku-4",
    "claude-opus-4-1": "claude-opus-4",
    "claude-sonnet-4-5": "claude-sonnet-4",
    "claude-3.5-sonnet-latest": "claude-3.5-sonnet",
    "grok-4-6": "grok-4.6",
}

_PREFIXES = ("cursor-", "openai/", "anthropic/", "x-ai/", "xai/", "google/", "google-")


@dataclass(frozen=True)
class ModelPrice:
    input_per_million: float
    output_per_million: float
    cache_read_per_million: float
    cache_write_per_million: float


def _money(tokens: int, per_million: float) -> float:
    if tokens <= 0 or per_million <= 0:
        return 0.0
    return round(tokens * per_million / 1_000_000, 10)


def normalize_model(name: str | None) -> str | None:
    if not isinstance(name, str):
        return None
    stripped = name.strip().lower()
    if not stripped:
        return None
    for prefix in _PREFIXES:
        if stripped.startswith(prefix):
            stripped = stripped[len(prefix) :]
            break
    return stripped or None


def _parse_price(raw: Any) -> ModelPrice | None:
    if not isinstance(raw, dict):
        return None
    inp = raw.get("input_per_million", raw.get("input"))
    out = raw.get("output_per_million", raw.get("output"))
    if isinstance(inp, bool) or isinstance(out, bool):
        return None
    if not isinstance(inp, (int, float)) or not isinstance(out, (int, float)):
        return None
    cache_read = raw.get("cache_read_per_million", raw.get("cache_read", float(inp) * 0.1))
    cache_write = raw.get("cache_write_per_million", raw.get("cache_write", float(inp)))
    if isinstance(cache_read, bool) or not isinstance(cache_read, (int, float)):
        cache_read = float(inp) * 0.1
    if isinstance(cache_write, bool) or not isinstance(cache_write, (int, float)):
        cache_write = float(inp)
    return ModelPrice(
        input_per_million=float(inp),
        output_per_million=float(out),
        cache_read_per_million=float(cache_read),
        cache_write_per_million=float(cache_write),
    )


def _default_table() -> dict[str, ModelPrice]:
    return {
        key: ModelPrice(inp, out, cache_read, cache_write)
        for key, (inp, out, cache_read, cache_write) in _DEFAULTS.items()
    }


def price_table(overrides: Mapping[str, Any] | None = None) -> dict[str, ModelPrice]:
    table = _default_table()
    if not overrides:
        return table
    for key, raw in overrides.items():
        parsed = _parse_price(raw)
        norm = normalize_model(str(key))
        if parsed and norm:
            table[norm] = parsed
    return table


def lookup_price(model: str | None, overrides: Mapping[str, Any] | None = None) -> ModelPrice | None:
    norm = normalize_model(model)
    if not norm or norm in PLACEHOLDER_MODELS:
        return None
    table = price_table(overrides)
    aliased = _ALIASES.get(norm, norm)
    if aliased in table:
        return table[aliased]
    for key in sorted(table, key=len, reverse=True):
        if aliased == key or aliased.startswith(key + "-"):
            return table[key]
    return None


def compute_cost_details(
    model: str | None,
    usage: Mapping[str, int],
    *,
    prices: Mapping[str, Any] | None = None,
) -> dict[str, float] | None:
    """Langfuse cost_details keys match usage_details (USD). Cached buckets use cache rates."""
    price = lookup_price(model, prices)
    if price is None:
        return None
    input_tokens = int(usage.get("input") or 0)
    output_tokens = int(usage.get("output") or 0)
    cache_read = int(usage.get("input_cached_tokens") or 0)
    cache_write = int(usage.get("input_cache_creation") or 0)
    if input_tokens == 0 and output_tokens == 0 and cache_read == 0 and cache_write == 0:
        return None
    details: dict[str, float] = {
        "input": _money(input_tokens, price.input_per_million),
        "output": _money(output_tokens, price.output_per_million),
    }
    if cache_read:
        details["input_cached_tokens"] = _money(cache_read, price.cache_read_per_million)
    if cache_write:
        details["input_cache_creation"] = _money(cache_write, price.cache_write_per_million)
    details["total"] = round(sum(details.values()), 10)
    if details["total"] <= 0:
        return None
    return details


def observation_usage_attrs(
    *,
    model: str | None,
    input_tokens: int,
    output_tokens: int,
    cache_read: int = 0,
    cache_write: int = 0,
    prices: Mapping[str, Any] | None = None,
    include_langfuse: bool = True,
) -> dict[str, Any]:
    """OTLP attributes for a generation: exclusive usage buckets + USD cost when priced."""
    if input_tokens == 0 and output_tokens == 0 and cache_read == 0 and cache_write == 0:
        return {}
    exclusive_input = max(0, input_tokens - cache_read - cache_write)
    usage: dict[str, int] = {"input": exclusive_input, "output": output_tokens}
    if cache_read:
        usage["input_cached_tokens"] = cache_read
    if cache_write:
        usage["input_cache_creation"] = cache_write
    attrs: dict[str, Any] = {
        "gen_ai.usage.input_tokens": input_tokens or None,
        "gen_ai.usage.output_tokens": output_tokens or None,
    }
    if cache_read:
        attrs["gen_ai.usage.cache_read_tokens"] = cache_read
    if cache_write:
        attrs["gen_ai.usage.cache_write_tokens"] = cache_write
    if include_langfuse:
        attrs["langfuse.observation.usage_details"] = json.dumps(usage, separators=(",", ":"))
    cost = compute_cost_details(model, usage, prices=prices)
    if cost:
        prompt_cost = round(
            cost.get("input", 0.0)
            + cost.get("input_cached_tokens", 0.0)
            + cost.get("input_cache_creation", 0.0),
            10,
        )
        attrs["gen_ai.usage.cost"] = cost["total"]
        attrs["gen_ai.usage.input_cost"] = prompt_cost
        attrs["gen_ai.usage.output_cost"] = cost["output"]
        if include_langfuse:
            attrs["langfuse.observation.cost_details"] = json.dumps(cost, separators=(",", ":"))
    return attrs


def event_usage_attrs(
    event: dict[str, Any],
    *,
    prices: Mapping[str, Any] | None = None,
    include_langfuse: bool = True,
) -> dict[str, Any]:
    tokens = event.get("tokens") if isinstance(event.get("tokens"), dict) else {}
    model = event.get("model_id") or event.get("model")
    if not isinstance(model, str):
        model = None

    def _tok(key: str) -> int:
        value = tokens.get(key)
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            return 0
        return max(0, int(value))

    return observation_usage_attrs(
        model=model,
        input_tokens=_tok("input_tokens"),
        output_tokens=_tok("output_tokens"),
        cache_read=_tok("cache_read_tokens"),
        cache_write=_tok("cache_write_tokens"),
        prices=prices,
        include_langfuse=include_langfuse,
    )
