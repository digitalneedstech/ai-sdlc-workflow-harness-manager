#!/usr/bin/env python3
"""Detached flush. Prefer the Python package so a stale PATH CLI cannot swallow obs."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


def main() -> int:
    repo = Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else Path.cwd()
    try:
        import pipeline_observability.export  # noqa: F401

        subprocess.Popen(
            [
                sys.executable,
                "-c",
                "from pathlib import Path; from pipeline_observability.export import flush_project; "
                "flush_project(Path.cwd())",
            ],
            stdin=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            start_new_session=True,
            cwd=str(repo),
        )
        return 0
    except ImportError:
        pass
    try:
        subprocess.Popen(
            ["pipeline-kit", "obs", "flush", str(repo)],
            stdin=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            start_new_session=True,
            cwd=str(repo),
        )
        return 0
    except (OSError, ValueError):
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
