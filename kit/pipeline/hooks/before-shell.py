#!/usr/bin/env python3
"""beforeShellExecution: block high-risk autonomous actions (VCS, exfil, deps, destroy)."""

from __future__ import annotations

import os
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from lib import portal_owns_gate, emit_permission, load_payload, tool_command

PIPE_SHELL = re.compile(r"(curl|wget|fetch)\b[^|&;\n]*\|\s*(ba)?sh\b", re.I)
DESTROY = re.compile(
    r"(rm\s+-rf\s+(/|~|\$HOME)\b)|(\bmkfs\.)|(\bdd\s+if=)",
    re.I,
)
VCS = re.compile(
    r"\b(git\s+commit|git\s+push|git\s+push\s+--force|npm\s+publish|twine\s+upload)\b",
    re.I,
)
DEPS = re.compile(
    r"\b(npm\s+i(nstall)?|pnpm\s+add|yarn\s+add|pip(\d)?\s+install|uv\s+add)\b",
    re.I,
)
REMOTE = re.compile(r"\b(ssh\s+|scp\s+|rsync\s+.*:)", re.I)
NET = re.compile(r"\b(curl|wget|nc|ncat|npx\s+--yes)\b", re.I)
LOCAL_NET = re.compile(r"(127\.0\.0\.1|localhost|\[::1\])", re.I)


def main() -> int:
    extra = {"claude_event": "PreToolUse"}
    if portal_owns_gate() or os.environ.get("PIPELINE_ALLOW_ALL") == "1":
        return emit_permission(True, "allow", extra)

    cmd = tool_command(load_payload())
    if not cmd.strip():
        return emit_permission(True, "allow", extra)

    if DESTROY.search(cmd) or PIPE_SHELL.search(cmd):
        return emit_permission(
            False,
            "Blocked destructive or curl|sh command. Autonomous agents must not wipe disks or pipe remote scripts to a shell.",
            extra,
        )
    if os.environ.get("PIPELINE_ALLOW_GIT") != "1" and VCS.search(cmd):
        return emit_permission(
            False,
            "Blocked commit/push/publish. Set PIPELINE_ALLOW_GIT=1 only when the user asked to ship.",
            extra,
        )
    if os.environ.get("PIPELINE_ALLOW_DEPS") != "1" and DEPS.search(cmd):
        return emit_permission(
            False,
            "Blocked new dependency install. Reuse existing libraries or set PIPELINE_ALLOW_DEPS=1 after a spec/security note.",
            extra,
        )
    if REMOTE.search(cmd):
        return emit_permission(
            False,
            "Blocked ssh/scp/rsync to a remote host from the agent session.",
            extra,
        )
    if os.environ.get("PIPELINE_ALLOW_NET") != "1" and NET.search(cmd) and not LOCAL_NET.search(cmd):
        return emit_permission(
            False,
            "Blocked non-localhost network command (possible exfil). Use 127.0.0.1 or set PIPELINE_ALLOW_NET=1.",
            extra,
        )
    return emit_permission(True, "allow", extra)


if __name__ == "__main__":
    raise SystemExit(main())
