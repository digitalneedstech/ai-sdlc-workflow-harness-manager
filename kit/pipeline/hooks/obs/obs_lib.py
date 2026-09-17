#!/usr/bin/env python3
"""Stdlib helpers for the agent-observability collector. Fail-open. No network."""

from __future__ import annotations

import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

SECRET_RE = re.compile(
    r"(?i)((?:sk-lf-|sk-|pk-lf-|ghp_|github_pat_|xox[baprs]-|AKIA)"
    r"[A-Za-z0-9_\-]{8,}|Bearer\s+[A-Za-z0-9._\-]{8,})"
)
MAX_FIELD_CHARS = 8000
LEDGER_NAME = "events.jsonl"
UNKNOWN_NAME = "unknown-fields.jsonl"
STATE_DIR = Path(".pipeline") / "state" / "obs"

COMMON_FIELDS = (
    "conversation_id",
    "generation_id",
    "model",
    "model_id",
    "model_params",
    "cursor_version",
    "session_id",
    "hook_event_name",
    "workspace_roots",
    "user_email",
    "transcript_path",
    "input_tokens",
    "output_tokens",
    "cache_read_tokens",
    "cache_write_tokens",
)


def utc_now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"


def emit_empty() -> int:
    try:
        sys.stdout.write("{}\n")
        sys.stdout.flush()
    except OSError:
        pass
    return 0


def load_payload() -> dict[str, Any]:
    try:
        data = json.load(sys.stdin)
    except (json.JSONDecodeError, OSError):
        return {}
    return data if isinstance(data, dict) else {}


def find_repo_root(payload: dict[str, Any] | None = None) -> Path | None:
    payload = payload or {}
    candidates: list[Path] = []
    roots = payload.get("workspace_roots")
    if isinstance(roots, list):
        for item in roots:
            if isinstance(item, str) and item.strip():
                candidates.append(Path(item).expanduser())
    cwd = Path.cwd()
    candidates.append(cwd)
    candidates.extend(cwd.parents)
    seen: set[Path] = set()
    for path in candidates:
        try:
            resolved = path.resolve()
        except OSError:
            continue
        if resolved in seen:
            continue
        seen.add(resolved)
        if (resolved / ".pipeline" / "config.json").is_file() or (
            resolved / ".pipeline" / "hooks" / "obs"
        ).is_dir():
            return resolved
    return None


def obs_dir(repo: Path) -> Path:
    return repo / STATE_DIR


def enabled(repo: Path) -> bool:
    path = repo / ".pipeline" / "config.json"
    if not path.is_file():
        return False
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return False
    block = data.get("agent_observability") if isinstance(data, dict) else None
    if not isinstance(block, dict):
        return False
    return block.get("enabled") is True


def redact_text(value: str) -> str:
    return SECRET_RE.sub("[redacted]", value)


def truncate(value: Any, limit: int = MAX_FIELD_CHARS) -> Any:
    if isinstance(value, str) and len(value) > limit:
        return value[:limit] + f"...[truncated {len(value) - limit} chars]"
    if isinstance(value, dict):
        return {str(key): truncate(item, limit) for key, item in list(value.items())[:80]}
    if isinstance(value, list):
        return [truncate(item, limit) for item in value[:40]]
    return value


def sanitize(value: Any) -> Any:
    if isinstance(value, str):
        return truncate(redact_text(value))
    if isinstance(value, dict):
        return {str(key): sanitize(item) for key, item in list(value.items())[:80]}
    if isinstance(value, list):
        return [sanitize(item) for item in value[:40]]
    return value


def append_row(directory: Path, filename: str, row: dict[str, Any]) -> None:
    directory.mkdir(parents=True, exist_ok=True)
    path = directory / filename
    line = json.dumps(row, separators=(",", ":"), default=str) + "\n"
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_APPEND, 0o600)
    try:
        os.write(fd, line.encode("utf-8"))
    finally:
        os.close(fd)


def load_active_context(repo: Path) -> dict[str, Any] | None:
    path = repo / ".pipeline" / "state" / "active-context.json"
    if not path.is_file():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    return data if isinstance(data, dict) else None


def snapshot_context(repo: Path, payload: dict[str, Any]) -> dict[str, Any] | None:
    pack = load_active_context(repo)
    if not pack:
        return None
    slug = pack.get("slug")
    if not slug:
        for key in ("task", "prompt", "description", "user_prompt"):
            value = payload.get(key)
            if isinstance(value, str) and "FEATURE_SLUG:" in value:
                tail = value.split("FEATURE_SLUG:", 1)[1].strip().split()
                if tail:
                    slug = tail[0].strip("`\"'")
                    break
    reads = pack.get("allowed_reads")
    return {
        "workflow": pack.get("workflow"),
        "step": pack.get("step"),
        "slug": slug,
        "allowed_reads": reads if isinstance(reads, list) else [],
    }


def note_unknown_fields(directory: Path, event: str, payload: dict[str, Any]) -> None:
    allowed = set(COMMON_FIELDS) | {
        "tool_name",
        "tool_input",
        "tool_output",
        "tool_use_id",
        "toolName",
        "toolArgs",
        "toolResult",
        "command",
        "output",
        "duration",
        "duration_ms",
        "cwd",
        "file_path",
        "path",
        "edits",
        "text",
        "prompt",
        "status",
        "loop_count",
        "subagent_id",
        "subagent_type",
        "parent_conversation_id",
        "tool_call_id",
        "tool_call_count",
        "message_count",
        "modified_files",
        "agent_transcript_path",
        "context_usage_percent",
        "context_tokens",
        "context_window_size",
        "composer_mode",
        "is_background_agent",
        "sandbox",
        "error_message",
        "is_interrupt",
        "is_parallel_worker",
        "subagent_model",
        "description",
        "task",
    }
    unknown = sorted(key for key in payload if key not in allowed)
    if not unknown:
        return
    seen_path = directory / "seen-unknown.json"
    seen: list[str] = []
    if seen_path.is_file():
        try:
            loaded = json.loads(seen_path.read_text(encoding="utf-8"))
            if isinstance(loaded, list):
                seen = [str(item) for item in loaded]
        except (OSError, json.JSONDecodeError):
            seen = []
    fresh = [key for key in unknown if f"{event}:{key}" not in seen]
    if not fresh:
        return
    append_row(
        directory,
        UNKNOWN_NAME,
        {"ts": utc_now(), "event": event, "fields": fresh},
    )
    seen.extend(f"{event}:{key}" for key in fresh)
    try:
        seen_path.write_text(json.dumps(seen, indent=2) + "\n", encoding="utf-8")
        os.chmod(seen_path, 0o600)
    except OSError:
        pass


def event_name(payload: dict[str, Any]) -> str:
    for key in ("hook_event_name", "hookEventName", "event"):
        value = payload.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
    return "unknown"


def harness_from_payload(payload: dict[str, Any]) -> str:
    if "toolName" in payload or "toolArgs" in payload:
        return "copilot"
    if payload.get("hook_event_name"):
        return "cursor"
    event = event_name(payload)
    if event[:1].isupper() or event in {"PostToolUse", "Stop", "SessionStart"}:
        return "claude-code"
    return "cursor"
