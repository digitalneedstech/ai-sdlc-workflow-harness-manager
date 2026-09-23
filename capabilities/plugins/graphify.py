"""Official Graphify CLI only. Never import graphify or invent a graph."""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path
from typing import Any, Callable

GRAPH_DIR = "graphify-out"
GRAPH_JSON = "graph.json"
INSTALL_HINT = "uv tool install graphifyy && graphify install"
EXTRACT_HINT = "graphify extract . --code-only"
RECOVERY = f"{INSTALL_HINT}\n{EXTRACT_HINT}"

RunFn = Callable[..., subprocess.CompletedProcess[str]]

_IDE_UNINSTALL = {
    "cursor": ("cursor", "uninstall"),
    "claude-code": ("claude", "uninstall"),
    "github": ("copilot", "uninstall"),
}


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
            "name": "graphify",
            "state": "missing",
            "executable": None,
            "version": None,
            "recovery": INSTALL_HINT,
        }
    version = _graphify_version(exe)
    return {
        "name": "graphify",
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
    from pipeline_scan.graph_context import ensure_graphifyignore

    ensure_graphifyignore(project)
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


def register_command(*, ide: str) -> list[str] | None:
    """Official Graphify skill install argv. Missing IDE mapping returns None."""
    if ide == "none":
        return None
    if ide == "cursor":
        return ["graphify", "cursor", "install"]
    return ["graphify", "install", "--project"]


def uninstall_command(*, ide: str) -> list[str] | None:
    extra = _IDE_UNINSTALL.get(ide)
    if extra is None:
        return None
    return ["graphify", *extra]


def register_skill(
    project: Path,
    *,
    ide: str,
    runner: RunFn = subprocess.run,
) -> str | None:
    """Register Graphify's own skill. Missing CLI is a skip, not a fake install."""
    exe = graphify_executable()
    argv = register_command(ide=ide)
    if not exe or not argv:
        return None
    command = [exe, *argv[1:]]
    try:
        completed = runner(
            command,
            cwd=project,
            check=False,
            capture_output=True,
            text=True,
            timeout=120,
        )
    except (OSError, subprocess.TimeoutExpired, TypeError):
        return None
    if completed.returncode != 0:
        return None
    return " ".join(command)


def uninstall_skill(
    project: Path,
    *,
    ide: str,
    purge: bool = False,
    runner: RunFn = subprocess.run,
) -> dict[str, Any]:
    """Remove Graphify's IDE skill. ``graphify-out/`` stays unless ``purge``."""
    exe = graphify_executable()
    argv = uninstall_command(ide=ide)
    command: list[str] | None = None
    uninstalled = False
    if exe and argv:
        command = [exe, *argv[1:]]
        try:
            completed = runner(
                command,
                cwd=project,
                check=False,
                capture_output=True,
                text=True,
                timeout=120,
            )
            uninstalled = completed.returncode == 0
        except (OSError, subprocess.TimeoutExpired, TypeError):
            uninstalled = False
    purged = False
    graph_dir = project / GRAPH_DIR
    if purge and graph_dir.exists():
        shutil.rmtree(graph_dir)
        purged = True
    return {
        "uninstalled": uninstalled,
        "command": " ".join(command) if command else None,
        "purged": purged,
        "graph_dir": str(graph_dir),
    }


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
