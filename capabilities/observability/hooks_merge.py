"""Non-destructive merge of observability hooks into existing harness configs."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

OWNED_COMMAND_NEEDLE = ".pipeline/hooks/obs/obs_collect.py"
MANIFEST_REL = Path(".pipeline") / "state" / "obs" / "install.json"

CURSOR_EVENTS = (
    "beforeSubmitPrompt",
    "postToolUse",
    "postToolUseFailure",
    "afterShellExecution",
    "afterMCPExecution",
    "afterFileEdit",
    "afterAgentResponse",
    "subagentStart",
    "subagentStop",
    "stop",
    "sessionStart",
    "sessionEnd",
    "preCompact",
)


class MergeError(ValueError):
    """Hook config cannot be merged safely."""


def owned_command(project: Path) -> str:
    return f"python3 {OWNED_COMMAND_NEEDLE}"


def manifest_path(project: Path) -> Path:
    return project / MANIFEST_REL


def load_fragment(pack: Path, ide: str) -> dict[str, Any]:
    names = {
        "cursor": "cursor.hooks.json",
        "claude-code": "claude.settings.json",
        "github": "copilot.hooks.json",
    }
    name = names.get(ide)
    if not name:
        raise MergeError(f"no hook fragment for ide={ide}")
    path = pack / "hooks" / "obs" / name
    if not path.is_file():
        raise MergeError(f"missing fragment {path}")
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise MergeError("fragment must be an object")
    return data


def _entry_owns(entry: Any, needle: str) -> bool:
    if not isinstance(entry, dict):
        return False
    for key in ("command", "bash", "powershell"):
        value = entry.get(key)
        if isinstance(value, str) and needle in value:
            return True
    nested = entry.get("hooks")
    if isinstance(nested, list):
        return any(_entry_owns(item, needle) for item in nested)
    return False


def _append_unique(bucket: list[Any], entries: list[Any], needle: str) -> int:
    added = 0
    for entry in entries:
        if _entry_owns(entry, needle) and any(_entry_owns(item, needle) for item in bucket):
            continue
        bucket.append(entry)
        added += 1
    return added


def merge_cursor(dest: Path, fragment: dict[str, Any], command: str) -> int:
    existing: dict[str, Any] = {"version": 1, "hooks": {}}
    if dest.is_file():
        loaded = json.loads(dest.read_text(encoding="utf-8"))
        if isinstance(loaded, dict):
            existing = loaded
            existing.setdefault("hooks", {})
            existing.setdefault("version", 1)
    hooks = existing.setdefault("hooks", {})
    if not isinstance(hooks, dict):
        raise MergeError("hooks.json hooks must be an object")
    added = 0
    incoming = fragment.get("hooks") if isinstance(fragment.get("hooks"), dict) else {}
    for event, entries in incoming.items():
        if not isinstance(entries, list):
            continue
        bucket = hooks.setdefault(event, [])
        if not isinstance(bucket, list):
            raise MergeError(f"hooks.{event} must be an array")
        added += _append_unique(bucket, entries, OWNED_COMMAND_NEEDLE)
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(json.dumps(existing, indent=2) + "\n", encoding="utf-8")
    return added


def merge_claude(dest: Path, fragment: dict[str, Any]) -> int:
    existing: dict[str, Any] = {}
    if dest.is_file():
        loaded = json.loads(dest.read_text(encoding="utf-8"))
        if isinstance(loaded, dict):
            existing = loaded
    hooks = existing.setdefault("hooks", {})
    if not isinstance(hooks, dict):
        raise MergeError(".claude/settings.json hooks must be an object")
    added = 0
    incoming = fragment.get("hooks") if isinstance(fragment.get("hooks"), dict) else {}
    for event, entries in incoming.items():
        if not isinstance(entries, list):
            continue
        bucket = hooks.setdefault(event, [])
        if not isinstance(bucket, list):
            raise MergeError(f"hooks.{event} must be an array")
        added += _append_unique(bucket, entries, OWNED_COMMAND_NEEDLE)
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(json.dumps(existing, indent=2) + "\n", encoding="utf-8")
    return added


def merge_copilot(dest: Path, fragment: dict[str, Any]) -> int:
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(json.dumps(fragment, indent=2) + "\n", encoding="utf-8")
    return 1


def strip_owned(data: dict[str, Any]) -> dict[str, Any]:
    hooks = data.get("hooks")
    if not isinstance(hooks, dict):
        return data
    for event, entries in list(hooks.items()):
        if not isinstance(entries, list):
            continue
        kept = [item for item in entries if not _entry_owns(item, OWNED_COMMAND_NEEDLE)]
        if kept:
            hooks[event] = kept
        else:
            del hooks[event]
    return data


def uninstall_hooks(project: Path, ide: str) -> None:
    if ide == "cursor":
        path = project / ".cursor" / "hooks.json"
        if path.is_file():
            data = json.loads(path.read_text(encoding="utf-8"))
            if isinstance(data, dict):
                path.write_text(json.dumps(strip_owned(data), indent=2) + "\n", encoding="utf-8")
    elif ide == "claude-code":
        path = project / ".claude" / "settings.json"
        if path.is_file():
            data = json.loads(path.read_text(encoding="utf-8"))
            if isinstance(data, dict):
                path.write_text(json.dumps(strip_owned(data), indent=2) + "\n", encoding="utf-8")
    elif ide == "github":
        path = project / ".github" / "hooks" / "pipeline-obs.json"
        if path.is_file():
            path.unlink()


def write_manifest(project: Path, *, ide: str, version: str, files: list[str]) -> None:
    path = manifest_path(project)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(
            {
                "name": "pipeline-kit-obs",
                "version": version,
                "ide": ide,
                "files": files,
                "hook_commands": [owned_command(project)],
                "command_needle": OWNED_COMMAND_NEEDLE,
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )


def install_hooks(project: Path, pack: Path, *, ide: str, version: str) -> int:
    fragment = load_fragment(pack, ide)
    added = 0
    files: list[str] = [str(MANIFEST_REL)]
    if ide == "cursor":
        dest = project / ".cursor" / "hooks.json"
        added = merge_cursor(dest, fragment, owned_command(project))
        files.append(".cursor/hooks.json")
    elif ide == "claude-code":
        dest = project / ".claude" / "settings.json"
        added = merge_claude(dest, fragment)
        files.append(".claude/settings.json")
    elif ide == "github":
        dest = project / ".github" / "hooks" / "pipeline-obs.json"
        added = merge_copilot(dest, fragment)
        files.append(".github/hooks/pipeline-obs.json")
    else:
        raise MergeError("ide=none does not install hooks; use cursor, claude-code, or github")
    write_manifest(project, ide=ide, version=version, files=files)
    return added
