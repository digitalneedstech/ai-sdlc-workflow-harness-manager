"""Turn raw hook envelopes into a harness-neutral event list."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

READ_TOOLS = {"Read", "read_file", "read"}
EDIT_TOOLS = {"Write", "StrReplace", "Edit", "Delete", "write", "edit"}
SEARCH_TOOLS = {"Grep", "Glob", "rg", "grep", "glob", "semantic_search"}
SHELL_TOOLS = {"Shell", "Bash", "bash", "shell"}
TASK_TOOLS = {"Task", "task", "TaskTool"}


def load_ledger(path: Path, *, offset: int = 0) -> tuple[list[dict[str, Any]], int]:
    if not path.is_file():
        return [], 0
    rows: list[dict[str, Any]] = []
    with path.open("rb") as handle:
        handle.seek(offset)
        chunk = handle.read()
        new_offset = handle.tell()
    if not chunk:
        return [], new_offset
    text = chunk.decode("utf-8", errors="replace")
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            parsed = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(parsed, dict):
            rows.append(parsed)
    return rows, new_offset


def _first_str(data: dict[str, Any], keys: tuple[str, ...]) -> str | None:
    for key in keys:
        value = data.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    return None


def _tool_input(payload: dict[str, Any]) -> dict[str, Any]:
    raw = payload.get("tool_input") or payload.get("input") or payload.get("toolArgs")
    if isinstance(raw, dict):
        return raw
    if isinstance(raw, str):
        try:
            parsed = json.loads(raw)
        except json.JSONDecodeError:
            return {"raw": raw}
        return parsed if isinstance(parsed, dict) else {"raw": raw}
    return {}


def _tool_name(payload: dict[str, Any]) -> str:
    for key in ("tool_name", "toolName", "name"):
        value = payload.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    return "unknown"


def _target_path(payload: dict[str, Any], tool_input: dict[str, Any]) -> str | None:
    for source in (payload, tool_input):
        for key in ("file_path", "path", "filePath", "target_file"):
            value = source.get(key)
            if isinstance(value, str) and value.strip():
                return value.strip()
    return None


def _command(payload: dict[str, Any], tool_input: dict[str, Any]) -> str | None:
    for source in (payload, tool_input):
        for key in ("command", "cmd"):
            value = source.get(key)
            if isinstance(value, str) and value.strip():
                return value.strip()
    return None


def _pattern(tool_input: dict[str, Any]) -> str | None:
    for key in ("pattern", "glob", "query", "search"):
        if key not in tool_input:
            continue
        value = tool_input.get(key)
        if isinstance(value, str):
            return value
    return None


def _duration(payload: dict[str, Any]) -> int | None:
    for key in ("duration", "duration_ms"):
        value = payload.get(key)
        if isinstance(value, (int, float)):
            return int(value)
    return None


def _ok(payload: dict[str, Any], event: str) -> bool:
    if event in {"postToolUseFailure", "PostToolUseFailure"}:
        return False
    result = payload.get("toolResult")
    if isinstance(result, dict) and result.get("resultType") in {"failure", "denied"}:
        return False
    return payload.get("failure_type") not in {"error", "timeout", "permission_denied"}


def tool_kind(name: str, command: str | None) -> str:
    if name in READ_TOOLS:
        return "read"
    if name in EDIT_TOOLS or name == "afterFileEdit":
        return "edit"
    if name in SEARCH_TOOLS:
        return "search"
    if name in SHELL_TOOLS:
        return "shell"
    if name in TASK_TOOLS or name.startswith("Task"):
        return "task"
    if name.startswith("MCP:") or name.lower().startswith("mcp"):
        return "mcp"
    if name in {"WebSearch", "WebFetch", "web_search"}:
        return "web"
    return "other"


def normalize_row(row: dict[str, Any]) -> dict[str, Any]:
    payload = row.get("payload") if isinstance(row.get("payload"), dict) else {}
    event = str(row.get("event") or payload.get("hook_event_name") or "unknown")
    tool_input = _tool_input(payload)
    name = _tool_name(payload)
    if event == "afterFileEdit" and name == "unknown":
        name = "Write"
    command = _command(payload, tool_input)
    tokens: dict[str, int] = {}
    for key in ("input_tokens", "output_tokens", "cache_read_tokens", "cache_write_tokens"):
        value = payload.get(key)
        if isinstance(value, (int, float)):
            tokens[key] = int(value)
    prompt = _first_str(payload, ("prompt", "text", "user_prompt", "command"))
    if event in {"postToolUse", "afterFileEdit", "afterShellExecution"} and command:
        prompt = None
    tool_output = payload.get("tool_output") or payload.get("output")
    if isinstance(tool_output, (dict, list)):
        tool_output = json.dumps(tool_output, default=str)
    elif tool_output is not None:
        tool_output = str(tool_output)
    task = payload.get("task") if isinstance(payload.get("task"), str) else None
    return {
        "ts": row.get("ts"),
        "kind": row.get("kind") or "hook",
        "harness": row.get("harness") or "cursor",
        "event": event,
        "conversation_id": payload.get("conversation_id") or payload.get("conversationId") or payload.get("session_id"),
        "generation_id": (
            (payload.get("generation_id") or payload.get("generationId") or "").strip() or None
            if isinstance(payload.get("generation_id") or payload.get("generationId"), str)
            else payload.get("generation_id") or payload.get("generationId")
        ),
        "session_id": payload.get("session_id") or payload.get("conversation_id"),
        "subagent_id": payload.get("subagent_id") or payload.get("subagentId"),
        "subagent_type": payload.get("subagent_type") or payload.get("subagentType"),
        "tool_use_id": payload.get("tool_use_id")
        or payload.get("tool_call_id")
        or payload.get("toolUseId"),
        "tool_name": name,
        "tool_kind": tool_kind(name, command),
        "target_path": _target_path(payload, tool_input),
        "command": command,
        "pattern": _pattern(tool_input),
        "tool_input": tool_input or None,
        "tool_output": tool_output,
        "prompt": prompt if event in {"beforeSubmitPrompt", "afterAgentResponse", "sessionStart"} else None,
        "text": payload.get("text") if isinstance(payload.get("text"), str) else None,
        "task": task,
        "duration_ms": _duration(payload),
        "ok": _ok(payload, event),
        "failure_type": payload.get("failure_type") or payload.get("failureType"),
        "loop_count": payload.get("loop_count"),
        "tool_call_count": payload.get("tool_call_count"),
        "status": payload.get("status"),
        "model": payload.get("model") or payload.get("model_id"),
        "model_id": payload.get("model_id") or payload.get("model"),
        "model_params": payload.get("model_params"),
        "composer_mode": payload.get("composer_mode"),
        "user_email": payload.get("user_email") or payload.get("userEmail"),
        "transcript_path": payload.get("transcript_path") or payload.get("agent_transcript_path"),
        "context_usage_percent": payload.get("context_usage_percent"),
        "context_tokens": payload.get("context_tokens"),
        "tokens": tokens,
        "step_context": row.get("step_context") if isinstance(row.get("step_context"), dict) else None,
    }


def normalize_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [normalize_row(row) for row in rows]


def dedupe_events(events: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Drop afterShellExecution when a matching postToolUse Shell exists."""
    shell_keys: set[tuple[Any, ...]] = set()
    for item in events:
        if item.get("event") == "postToolUse" and item.get("tool_kind") == "shell":
            shell_keys.add((item.get("conversation_id"), item.get("command"), item.get("generation_id")))
    out: list[dict[str, Any]] = []
    for item in events:
        if item.get("event") == "afterShellExecution":
            key = (item.get("conversation_id"), item.get("command"), item.get("generation_id"))
            if key in shell_keys:
                continue
        out.append(item)
    return out


def parse_transcript(path: str | None) -> tuple[str | None, str | None]:
    """Best-effort user prompt and last assistant text. Flush-time only."""
    if not path:
        return None, None
    file = Path(path)
    if not file.is_file():
        return None, None
    user: str | None = None
    assistant: str | None = None
    try:
        for line in file.read_text(encoding="utf-8", errors="replace").splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError:
                continue
            if not isinstance(row, dict):
                continue
            message = row.get("message") if isinstance(row.get("message"), dict) else {}
            content = message.get("content") if isinstance(message, dict) else None
            texts: list[str] = []
            if isinstance(content, str):
                texts = [content]
            elif isinstance(content, list):
                for part in content:
                    if isinstance(part, dict) and part.get("type") == "text" and isinstance(part.get("text"), str):
                        texts.append(part["text"])
            blob = "\n".join(texts)
            if "<user_query>" in blob and "</user_query>" in blob:
                user = blob.split("<user_query>", 1)[1].split("</user_query>", 1)[0].strip()
            role = row.get("role")
            if role == "assistant" and blob and not blob.startswith("{") and "<user_query>" not in blob:
                if len(blob) < 8000:
                    assistant = blob
    except OSError:
        return user, assistant
    return user, assistant
