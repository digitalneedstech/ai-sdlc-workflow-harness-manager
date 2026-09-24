#!/usr/bin/env python3
"""postToolUseFailure: do not 'fix' failures by dropping security or tests."""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from lib import portal_owns_gate, emit_context, load_payload


MSG = (
    "The last tool failed. Retry the intended command or fix the real error. "
    "Do not disable hooks, skip authorization, swallow exceptions, or delete tests to get to SUCCESS."
)


def main() -> int:
    if portal_owns_gate():
        return emit_context("")
    load_payload()
    return emit_context(MSG)


if __name__ == "__main__":
    raise SystemExit(main())
