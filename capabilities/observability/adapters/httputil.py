"""Shared stdlib HTTP helpers. Never log secrets."""

from __future__ import annotations

import base64
import json
import time
import urllib.error
import urllib.request
from typing import Any


def basic_auth(user: str, password: str) -> str:
    token = base64.b64encode(f"{user}:{password}".encode("utf-8")).decode("ascii")
    return f"Basic {token}"


def _json_object(text: str) -> dict[str, Any]:
    raw = text.strip()
    if raw.startswith("HTTP ") and ": " in raw:
        raw = raw.split(": ", 1)[1]
    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError:
        return {}
    return parsed if isinstance(parsed, dict) else {}


def retry_after_seconds(status: int, body: str, headers: Any | None) -> float:
    if status != 429:
        return 0.0
    details = _json_object(body).get("details")
    if isinstance(details, dict) and details.get("retryAfterSeconds") is not None:
        try:
            return max(float(details["retryAfterSeconds"]), 1.0)
        except (TypeError, ValueError):
            pass
    raw = None
    if headers is not None:
        try:
            raw = headers.get("Retry-After")
        except (AttributeError, TypeError):
            raw = None
    if raw:
        try:
            return max(float(raw), 1.0)
        except ValueError:
            return 15.0
    return 15.0


def _post_once(
    url: str,
    payload: dict[str, Any],
    headers: dict[str, str],
    *,
    timeout: float,
) -> tuple[bool, str, int, Any]:
    body = json.dumps(payload).encode("utf-8")
    request = urllib.request.Request(
        url,
        data=body,
        method="POST",
        headers={"Content-Type": "application/json", **headers},
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            text = response.read().decode("utf-8", errors="replace")[:500]
            return True, text, int(response.status), response.headers
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")[:300]
        return False, f"HTTP {exc.code}: {detail}", int(exc.code), exc.headers
    except (urllib.error.URLError, TimeoutError, OSError) as exc:
        return False, str(exc), 0, None


def post_json(
    url: str,
    payload: dict[str, Any],
    headers: dict[str, str],
    *,
    timeout: float = 12.0,
    retries: int = 6,
) -> tuple[bool, str, int]:
    last = (False, "no attempt", 0)
    attempts = max(int(retries), 1)
    for attempt in range(attempts):
        ok, detail, status, hdrs = _post_once(url, payload, headers, timeout=timeout)
        last = (ok, detail, status)
        if ok:
            return last
        if status == 429 and attempt < attempts - 1:
            time.sleep(min(retry_after_seconds(status, detail, hdrs), 60.0))
            continue
        if status in {502, 503, 504} and attempt < attempts - 1:
            time.sleep(min(2**attempt, 16))
            continue
        return last
    return last
