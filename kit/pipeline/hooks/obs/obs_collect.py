#!/usr/bin/env python3
"""Fail-open hook collector. Appends one sanitized JSONL row. No network. No SDK."""

from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

from obs_lib import (  # noqa: E402
    LEDGER_NAME,
    append_row,
    emit_empty,
    enabled,
    event_name,
    find_repo_root,
    harness_from_payload,
    load_payload,
    note_unknown_fields,
    obs_dir,
    sanitize,
    snapshot_context,
    utc_now,
)

SNAPSHOT_EVENTS = {
    "subagentStart",
    "SubagentStart",
}
FLUSH_EVENTS = {
    "subagentStop",
    "sessionEnd",
    "stop",
    "afterAgentResponse",
    "SubagentStop",
    "SessionEnd",
    "Stop",
    "AfterAgentResponse",
    "agentStop",
}


def _maybe_flush(repo: Path, event: str) -> None:
    if event not in FLUSH_EVENTS:
        return
    flush = HERE / "obs_flush.py"
    if not flush.is_file():
        return
    try:
        import subprocess

        subprocess.Popen(
            [sys.executable, str(flush), str(repo)],
            stdin=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            start_new_session=True,
            cwd=str(repo),
        )
    except (OSError, ValueError):
        pass


def main() -> int:
    try:
        payload = load_payload()
        if not payload:
            return emit_empty()
        repo = find_repo_root(payload)
        if repo is None or not enabled(repo):
            return emit_empty()
        event = event_name(payload)
        directory = obs_dir(repo)
        note_unknown_fields(directory, event, payload)
        row = {
            "ts": utc_now(),
            "kind": "hook",
            "harness": harness_from_payload(payload),
            "event": event,
            "payload": sanitize(payload),
        }
        if event in SNAPSHOT_EVENTS:
            context = snapshot_context(repo, payload)
            if context:
                row["step_context"] = context
                row["kind"] = "step_context"
        append_row(directory, LEDGER_NAME, row)
        _maybe_flush(repo, event)
    except Exception:
        pass
    return emit_empty()


if __name__ == "__main__":
    raise SystemExit(main())
