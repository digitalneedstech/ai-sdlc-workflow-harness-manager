"""Official Graphify CLI only. Never import graphify or invent a graph."""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path
from typing import Any

from knowledge.const import EXTRACT_HINT, GRAPH_DIR, GRAPH_JSON, INSTALL_HINT, RECOVERY


class GraphifyError(RuntimeError):
    """Graphify is missing or extract failed. Recovery is official CLI only."""

    def __init__(self, message: str, *, recovery: str = RECOVERY) -> None:
        super().__init__(message)
        self.recovery = recovery


def graphify_executable() -> str | None:
    return shutil.which("graphify")


def graphify_status() -> dict[str, Any]:
    exe = graphify_executable()
    if not exe:
        return {
            "state": "missing",
            "executable": None,
            "version": None,
            "recovery": INSTALL_HINT,
        }
    version = _graphify_version(exe)
    return {
        "state": "ready",
        "executable": exe,
        "version": version,
        "recovery": None,
    }


def graph_json_path(project: Path) -> Path:
    return project / GRAPH_DIR / GRAPH_JSON


def graph_exists(project: Path) -> bool:
    return graph_json_path(project).is_file()


def extract_graph(project: Path, *, force: bool = False) -> Path:
    """Run ``graphify extract . --code-only``. Do not write a substitute graph."""
    exe = graphify_executable()
    if not exe:
        raise GraphifyError(
            "graphify is not on PATH. Install Graphify officially, then retry.",
            recovery=RECOVERY,
        )
    command = [exe, "extract", ".", "--code-only"]
    if force:
        command.append("--force")
    try:
        completed = subprocess.run(
            command,
            cwd=project,
            check=False,
            capture_output=True,
            text=True,
            timeout=900,
        )
    except OSError as exc:
        raise GraphifyError(
            f"could not run graphify: {exc}",
            recovery=RECOVERY,
        ) from exc
    except subprocess.TimeoutExpired as exc:
        raise GraphifyError(
            "graphify extract timed out. Run the official command locally.",
            recovery=EXTRACT_HINT,
        ) from exc
    if completed.returncode != 0:
        detail = (completed.stderr or completed.stdout or "").strip()
        suffix = f"\n{detail}" if detail else ""
        raise GraphifyError(
            f"graphify extract failed (exit {completed.returncode}).{suffix}",
            recovery=RECOVERY,
        )
    path = graph_json_path(project)
    if not path.is_file():
        raise GraphifyError(
            "graphify extract exited 0 but graphify-out/graph.json is missing.",
            recovery=EXTRACT_HINT,
        )
    return path


def register_skill(project: Path, *, ide: str) -> str | None:
    """Register Graphify's own skill. Missing CLI is a skip, not a fake install."""
    exe = graphify_executable()
    if not exe:
        return None
    command = [exe, "cursor", "install"] if ide == "cursor" else [exe, "install", "--project"]
    try:
        completed = subprocess.run(
            command,
            cwd=project,
            check=False,
            capture_output=True,
            text=True,
            timeout=120,
        )
    except (OSError, subprocess.TimeoutExpired):
        return None
    if completed.returncode != 0:
        return None
    return " ".join(command)


def _graphify_version(exe: str) -> str | None:
    try:
        completed = subprocess.run(
            [exe, "--version"],
            check=False,
            capture_output=True,
            text=True,
            timeout=15,
        )
    except (OSError, subprocess.TimeoutExpired):
        return None
    text = (completed.stdout or completed.stderr or "").strip()
    return text.splitlines()[0] if text else None
