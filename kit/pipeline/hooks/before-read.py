#!/usr/bin/env python3
"""beforeReadFile: secrets, then workflow pack allowlist. portal skip first."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from lib import portal_owns_gate, emit_permission, load_payload, tool_path
from pack_gate import decide_read


def _loader_dir() -> Path | None:
    repo = Path(__file__).resolve().parents[2]
    local = repo / ".pipeline" / "loader"
    if local.is_dir():
        return local
    user = Path.home() / ".pipeline" / "loader"
    if user.is_dir():
        return user
    return None


def _active_pack():
    loader = _loader_dir()
    if loader is None:
        return None
    sys.path.insert(0, str(loader))
    try:
        from context_pack import load_active_pack, pack_root_from, project_root_from
    except Exception:
        return None
    try:
        project = project_root_from()
        return load_active_pack(pack_root_from(project))
    except Exception:
        return None


def main() -> int:
    extra = {"claude_event": "PreToolUse"}
    if portal_owns_gate():
        return emit_permission(True, "external portal owns this session", extra)
    payload = load_payload()
    path = tool_path(payload)
    try:
        allow, reason = decide_read(
            path,
            Path(__file__).resolve().parents[2],
            portal_owns=False,
            pack=_active_pack(),
        )
    except Exception:
        return emit_permission(True, "allow", extra)
    return emit_permission(allow, reason, extra)


if __name__ == "__main__":
    raise SystemExit(main())
