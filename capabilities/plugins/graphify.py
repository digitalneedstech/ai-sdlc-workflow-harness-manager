"""Official Graphify CLI only. Never import graphify or invent a graph."""

from __future__ import annotations

import json
import re
import shutil
import subprocess
from pathlib import Path
from typing import Any, Callable

GRAPH_DIR = "graphify-out"
GRAPH_JSON = "graph.json"
MANIFEST = "manifest.json"
INSTALL_HINT = "uv tool install graphifyy && graphify install"
EXTRACT_HINT = "graphify extract . --code-only"
UPDATE_HINT = "graphify update ."
RECOVERY = f"{INSTALL_HINT}\n{EXTRACT_HINT}"
MIN_VERSION = (0, 9, 56)
IGNORE_MARKER = "# pipeline-kit: do not index the agent pack"
PACK_IGNORE = (
    ".pipeline/",
    ".cursor/",
    ".claude/",
    ".github/skills/",
    "pipeline_extensions/",
    "features/",
    "graphify-out/",
)
_SECRET = re.compile(
    r"(secret|password|api[_-]?key|token|credential|private[_-]?key|\.env|begin )",
    re.IGNORECASE,
)
_SHRINK = re.compile(r"refused to shrink|GRAPHIFY_FORCE|--force", re.IGNORECASE)
_VERSION = re.compile(r"(\d+)\.(\d+)\.(\d+)")

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


def parse_version(text: str | None) -> tuple[int, int, int] | None:
    if not text:
        return None
    match = _VERSION.search(text)
    if not match:
        return None
    return tuple(int(part) for part in match.groups())  # type: ignore[return-value]


def version_supported(text: str | None) -> bool:
    parsed = parse_version(text)
    return parsed is not None and parsed >= MIN_VERSION


def graphify_status() -> dict[str, Any]:
    exe = graphify_executable()
    if not exe:
        return {
            "name": "graphify",
            "state": "missing",
            "executable": None,
            "version": None,
            "supported": False,
            "recovery": INSTALL_HINT,
        }
    version = _graphify_version(exe)
    return {
        "name": "graphify",
        "state": "ready",
        "executable": exe,
        "version": version,
        "supported": version_supported(version),
        "recovery": None if version_supported(version) else f"graphify {version} is older than {'.'.join(map(str, MIN_VERSION))}",
    }


def graph_json_path(project: Path) -> Path:
    return project / GRAPH_DIR / GRAPH_JSON


def graph_exists(project: Path) -> bool:
    return graph_json_path(project).is_file()


def ensure_graphifyignore(project: Path) -> bool:
    """Add pack paths so the next Graphify extract indexes the product."""
    path = project / ".graphifyignore"
    try:
        existing = path.read_text(encoding="utf-8") if path.is_file() else ""
    except OSError:
        return False
    missing = [item for item in PACK_IGNORE if item not in existing.splitlines()]
    if IGNORE_MARKER in existing and not missing:
        return False
    lines = existing.splitlines()
    if IGNORE_MARKER not in existing:
        if lines and lines[-1].strip():
            lines.append("")
        lines.append(IGNORE_MARKER)
    lines.extend(missing)
    path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")
    return True


def redact_text(text: str) -> str:
    kept = [line for line in text.splitlines() if line.strip() and not _SECRET.search(line)]
    return "\n".join(kept).strip()


def shrink_refused(output: str) -> bool:
    return bool(_SHRINK.search(output or ""))


def graph_freshness(project: Path) -> dict[str, Any]:
    """Compare graphify-out/manifest.json with files on disk. No Graphify import."""
    path = project / GRAPH_DIR / MANIFEST
    if not path.is_file():
        return {"state": "unknown", "indexed": 0, "missing": 0, "changed": 0}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {"state": "unknown", "indexed": 0, "missing": 0, "changed": 0}
    if not isinstance(data, dict) or not data:
        return {"state": "unknown", "indexed": 0, "missing": 0, "changed": 0}
    missing = 0
    changed = 0
    for rel, meta in data.items():
        if not isinstance(rel, str) or not rel.strip():
            continue
        target = project / rel
        if not target.is_file():
            missing += 1
            continue
        recorded = meta.get("mtime") if isinstance(meta, dict) else None
        if isinstance(recorded, (int, float)) and target.stat().st_mtime > float(recorded) + 1:
            changed += 1
    indexed = len(data)
    drifted = missing + changed
    stale = drifted > max(2, indexed // 5)
    return {
        "state": "stale" if stale else "fresh",
        "indexed": indexed,
        "missing": missing,
        "changed": changed,
    }


def _run_graphify(
    project: Path,
    args: list[str],
    *,
    runner: RunFn = subprocess.run,
    timeout: int = 900,
) -> subprocess.CompletedProcess[str]:
    exe = graphify_executable()
    if not exe:
        raise GraphifyError(
            "graphify is not on PATH. Install Graphify officially, then retry.",
            recovery=RECOVERY,
        )
    try:
        return runner(
            [exe, *args],
            cwd=project,
            check=False,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise GraphifyError(f"could not run graphify: {exc}", recovery=RECOVERY) from exc


def update_graph(project: Path, *, force: bool = False, runner: RunFn = subprocess.run) -> Path:
    """Run ``graphify update .``. Incremental, and it does not call a model."""
    command = ["update", "."]
    if force:
        command.append("--force")
    completed = _run_graphify(project, command, runner=runner)
    detail = (completed.stderr or completed.stdout or "").strip()
    if completed.returncode != 0:
        recovery = UPDATE_HINT + (" --force" if shrink_refused(detail) else "")
        raise GraphifyError(
            f"graphify update failed (exit {completed.returncode}). {detail}".strip(),
            recovery=recovery,
        )
    path = graph_json_path(project)
    if not path.is_file():
        raise GraphifyError("graphify update exited 0 but graphify-out/graph.json is missing.", recovery=UPDATE_HINT)
    return path


def merge_graphs(project: Path, inputs: list[Path], *, runner: RunFn = subprocess.run) -> Path:
    """Run ``graphify merge-graphs`` into graphify-out/graph.json."""
    if len(inputs) < 2:
        raise GraphifyError("merge-graphs needs at least two graph.json files.", recovery="graphify merge-graphs <g1> <g2>")
    out = graph_json_path(project)
    out.parent.mkdir(parents=True, exist_ok=True)
    completed = _run_graphify(
        project,
        ["merge-graphs", *[str(path) for path in inputs], "--out", str(out)],
        runner=runner,
        timeout=300,
    )
    if completed.returncode != 0:
        detail = (completed.stderr or completed.stdout or "").strip()
        raise GraphifyError(
            f"graphify merge-graphs failed (exit {completed.returncode}). {detail}".strip(),
            recovery="graphify merge-graphs <g1> <g2> --out graphify-out/graph.json",
        )
    if not out.is_file():
        raise GraphifyError("graphify merge-graphs exited 0 but wrote no graph.", recovery=EXTRACT_HINT)
    return out


def god_nodes(project: Path, *, top: int = 10, runner: RunFn = subprocess.run) -> list[dict[str, Any]]:
    completed = _run_graphify(project, ["god-nodes", "--json", "--top", str(top)], runner=runner, timeout=60)
    if completed.returncode != 0:
        return []
    try:
        data = json.loads(completed.stdout or "[]")
    except json.JSONDecodeError:
        return []
    if isinstance(data, dict):
        data = data.get("gods") or data.get("nodes") or []
    if not isinstance(data, list):
        return []
    return [item for item in data if isinstance(item, dict)]


def affected(project: Path, label: str, *, depth: int = 2, runner: RunFn = subprocess.run) -> str:
    completed = _run_graphify(
        project,
        ["affected", label, "--depth", str(depth)],
        runner=runner,
        timeout=60,
    )
    if completed.returncode != 0:
        return ""
    return redact_text(completed.stdout or "")


def hook_status(project: Path, *, runner: RunFn = subprocess.run) -> str:
    try:
        completed = _run_graphify(project, ["hook", "status"], runner=runner, timeout=30)
    except GraphifyError:
        return "unknown"
    text = ((completed.stdout or "") + (completed.stderr or "")).strip()
    return "installed" if completed.returncode == 0 and "not" not in text.lower() else "absent"


def install_hook(project: Path, *, runner: RunFn = subprocess.run) -> bool:
    completed = _run_graphify(project, ["hook", "install"], runner=runner, timeout=60)
    return completed.returncode == 0


def uninstall_hook(project: Path, *, runner: RunFn = subprocess.run) -> bool:
    completed = _run_graphify(project, ["hook", "uninstall"], runner=runner, timeout=60)
    return completed.returncode == 0


def graphify_owned_files(project: Path) -> list[str]:
    """Files Graphify's IDE install writes. They do not cover product areas."""
    found: list[str] = []
    rule = project / ".cursor" / "rules" / "graphify.mdc"
    if rule.is_file():
        found.append(str(rule.relative_to(project)))
    for name in ("CLAUDE.md", "AGENTS.md"):
        path = project / name
        if not path.is_file():
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except OSError:
            continue
        if "graphify-out/graph.json" in text or "/graphify" in text:
            found.append(name)
    return found


def extract_graph(project: Path, *, force: bool = False) -> Path:
    """Run ``graphify extract . --code-only``. Do not write a substitute graph."""
    exe = graphify_executable()
    if not exe:
        raise GraphifyError(
            "graphify is not on PATH. Install Graphify officially, then retry.",
            recovery=RECOVERY,
        )
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
        recovery = EXTRACT_HINT + " --force" if shrink_refused(detail) else RECOVERY
        raise GraphifyError(
            f"graphify extract failed (exit {completed.returncode}).{suffix}",
            recovery=recovery,
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
