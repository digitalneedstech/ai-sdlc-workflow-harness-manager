#!/usr/bin/env python3
"""afterFileEdit: remind the agent to verify the surface it just changed."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from lib import portal_owns_gate, emit_context, load_config, load_payload, tool_path

_VERIFY = load_config().get("verify")
_VERIFY = _VERIFY if isinstance(_VERIFY, dict) else {}
_RULES = _VERIFY.get("rules")
RULES = [rule for rule in _RULES if isinstance(rule, dict)] if isinstance(_RULES, list) else []


def hint(path: str) -> str:
    """Repo-specific reminders live in pipeline.config.json, not in this script."""
    p = path.replace("\\", "/")
    if not p:
        return ""
    # Leading slash so a rule like "/app/" matches both absolute and repo-relative paths.
    p = "/" + p.lstrip("/")
    for rule in RULES:
        match = rule.get("match")
        message = rule.get("message")
        if isinstance(match, str) and match and isinstance(message, str) and match in p:
            return message
    return ""


def main() -> int:
    if portal_owns_gate():
        return emit_context("")
    return emit_context(hint(tool_path(load_payload())))


if __name__ == "__main__":
    raise SystemExit(main())
