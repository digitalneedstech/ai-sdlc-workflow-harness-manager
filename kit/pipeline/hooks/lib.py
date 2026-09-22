#!/usr/bin/env python3
"""Shared stdin/stdout JSON helpers for Cursor, Claude Code, and Chorus."""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from typing import Any


def load_config() -> dict[str, Any]:
    """Project `.pipeline/config.json`, else `~/.pipeline/config.json`. Missing means defaults."""
    repo = Path(__file__).resolve().parents[2]
    candidates = (
        repo / ".pipeline" / "config.json",
        Path.home() / ".pipeline" / "config.json",
    )
    for path in candidates:
        try:
            if not path.is_file():
                continue
            with path.open(encoding="utf-8") as handle:
                data = json.load(handle)
        except (OSError, json.JSONDecodeError):
            continue
        if isinstance(data, dict):
            return data
    return {}


def load_payload() -> dict[str, Any]:
    try:
        data = json.load(sys.stdin)
    except (json.JSONDecodeError, OSError):
        return {}
    return data if isinstance(data, dict) else {}


def portal_owns_gate() -> bool:
    """Skip when an external HITL portal already owns the session."""
    if os.environ.get("PIPELINE_HOOK_SKIP") == "1":
        return True
    return bool(os.environ.get("CHORUS_TASK_ID") and os.environ.get("CHORUS_PORTAL"))


def emit_permission(allow: bool, reason: str, extra: dict[str, Any] | None = None) -> int:
    fmt = os.environ.get("PIPELINE_HOOK_FORMAT") or os.environ.get("CHORUS_HOOK_FORMAT") or "cursor"
    reason = reason or ("allow" if allow else "deny")
    extra = extra or {}
    if fmt == "claude":
        out: dict[str, Any] = {
            "hookSpecificOutput": {
                "hookEventName": extra.pop("claude_event", "PreToolUse"),
                "permissionDecision": "allow" if allow else "deny",
                "permissionDecisionReason": reason,
            }
        }
    else:
        out = {
            "permission": "allow" if allow else "deny",
            "user_message": reason,
            "agent_message": reason,
        }
        out.update(extra)
    json.dump(out, sys.stdout)
    sys.stdout.write("\n")
    return 0


def emit_followup(message: str) -> int:
    json.dump({"followup_message": message}, sys.stdout)
    sys.stdout.write("\n")
    return 0


def subagent_type(payload: dict[str, Any]) -> str:
    for key in ("subagent_type", "subagentType", "agent_type", "agentType", "type"):
        val = payload.get(key)
        if isinstance(val, str) and val.strip():
            return val.strip()
    nested = payload.get("subagent")
    if isinstance(nested, dict):
        return subagent_type(nested)
    return ""


def prompt_text(payload: dict[str, Any]) -> str:
    for key in ("prompt", "task", "description", "user_prompt"):
        val = payload.get(key)
        if isinstance(val, str):
            return val
    return ""


def emit_context(message: str) -> int:
    if not message:
        json.dump({}, sys.stdout)
        sys.stdout.write("\n")
        return 0
    json.dump({"additional_context": message}, sys.stdout)
    sys.stdout.write("\n")
    return 0


def tool_path(payload: dict[str, Any]) -> str:
    for key in ("path", "file_path", "filePath"):
        val = payload.get(key)
        if isinstance(val, str) and val.strip():
            return val.replace("\\", "/")
    for nest in ("tool_input", "input", "updated_input", "file"):
        inner = payload.get(nest)
        if isinstance(inner, dict):
            found = tool_path(inner)
            if found:
                return found
    return ""


def tool_mcp_name(payload: dict[str, Any]) -> str:
    """Best-effort MCP tool name from Cursor/Claude hook payloads."""
    for key in ("tool_name", "toolName", "tool", "name", "mcp_tool", "mcpTool"):
        val = payload.get(key)
        if isinstance(val, str) and val.strip():
            return val.strip()
    nested = payload.get("tool_input") or payload.get("input") or payload.get("mcp") or {}
    if isinstance(nested, dict):
        found = tool_mcp_name(nested)
        if found:
            return found
    return ""


def tool_mcp_server(payload: dict[str, Any]) -> str:
    for key in ("server", "server_name", "serverName", "namespace", "mcp_server"):
        val = payload.get(key)
        if isinstance(val, str) and val.strip():
            return val.strip()
    nested = payload.get("mcp") if isinstance(payload.get("mcp"), dict) else {}
    if nested:
        return tool_mcp_server(nested)
    return ""


def tool_command(payload: dict[str, Any]) -> str:
    for key in ("command", "cmd", "shell"):
        val = payload.get(key)
        if isinstance(val, str):
            return val
    nested = payload.get("tool_input") or payload.get("input") or {}
    if isinstance(nested, dict):
        return str(nested.get("command") or "")
    return ""


def tool_contents(payload: dict[str, Any]) -> str:
    for key in ("contents", "new_string", "newString", "content"):
        val = payload.get(key)
        if isinstance(val, str):
            return val
    nested = payload.get("tool_input") or payload.get("input") or {}
    if isinstance(nested, dict):
        return tool_contents(nested)
    return ""
