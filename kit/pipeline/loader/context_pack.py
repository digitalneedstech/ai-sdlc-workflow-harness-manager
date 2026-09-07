"""Load a workflow step allowlist. No third-party deps.

Project root is where `features/` is written. Pack root is the `.pipeline`
directory that holds workflows and config: the project's `.pipeline` if
present, otherwise `~/.pipeline`.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

PACK_DIRNAME = ".pipeline"
USER_PACK_DIRNAME = ".pipeline"


def _is_pack_dir(path: Path) -> bool:
    return (path / "config.json").is_file() or (path / "workflows").is_dir()


def project_root_from(start: Path | None = None) -> Path:
    here = (start or Path.cwd()).resolve()
    if here.is_file():
        here = here.parent
    for cur in (here, *here.parents):
        if _is_pack_dir(cur / PACK_DIRNAME):
            return cur
        if (cur / ".git").exists():
            return cur
    return Path.cwd().resolve()


def repo_root_from(start: Path | None = None) -> Path:
    """Alias for project_root_from (hooks and older callers)."""
    return project_root_from(start)


def user_pack_dir(home: Path | None = None) -> Path:
    return (home or Path.home()) / USER_PACK_DIRNAME


def pack_root_from(
    project: Path,
    *,
    pack_root: Path | None = None,
    home: Path | None = None,
) -> Path:
    if pack_root is not None:
        resolved = pack_root.resolve()
        if not _is_pack_dir(resolved):
            raise ValueError(f"not a pipeline pack: {resolved}")
        return resolved
    local = project.resolve() / PACK_DIRNAME
    if _is_pack_dir(local):
        return local
    user = user_pack_dir(home)
    if _is_pack_dir(user):
        return user
    raise ValueError("no pipeline pack found (project .pipeline or ~/.pipeline)")


def normalize_rel(path: str) -> str:
    rel = path.replace("\\", "/")
    while rel.startswith("./"):
        rel = rel[2:]
    return rel


def load_workflow_doc(pack: Path, workflow: str) -> dict[str, Any]:
    name = workflow.strip().lower()
    path = pack / "workflows" / f"{name}.json"
    if not path.is_file():
        raise ValueError(f"unknown workflow: {workflow} (missing {path})")
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"invalid workflow pack: {path}")
    return data


def files_for_step(doc: dict[str, Any], step: str) -> list[str]:
    context = doc.get("context")
    if not isinstance(context, dict):
        raise ValueError("workflow pack missing context")
    key = step.strip()
    if key == "parent":
        block = context.get("parent")
    else:
        steps = context.get("steps")
        if not isinstance(steps, dict):
            raise ValueError("workflow pack missing context.steps")
        block = steps.get(key)
    if not isinstance(block, dict):
        raise ValueError(f"unknown step: {step}")
    files = block.get("files")
    if not isinstance(files, list) or not all(isinstance(item, str) for item in files):
        raise ValueError(f"step {step} files must be a list of strings")
    return [normalize_rel(item) for item in files]


def build_pack(workflow: str, step: str, slug: str, files: list[str]) -> dict[str, Any]:
    return {
        "workflow": workflow.strip().lower(),
        "step": step.strip(),
        "slug": slug.strip(),
        "allowed_reads": files,
    }


def write_pack(
    project: Path, pack: Path, slug: str, data: dict[str, Any]
) -> tuple[Path, Path]:
    safe = slug.strip().strip("/")
    if not safe or ".." in safe.split("/"):
        raise ValueError("invalid slug")
    artifact = project / "features" / safe / "context-pack.json"
    artifact.parent.mkdir(parents=True, exist_ok=True)
    state = pack / "state" / "active-context.json"
    state.parent.mkdir(parents=True, exist_ok=True)
    text = json.dumps(data, indent=2) + "\n"
    artifact.write_text(text, encoding="utf-8")
    state.write_text(text, encoding="utf-8")
    return artifact, state


def load_active_pack(pack: Path) -> dict[str, Any] | None:
    path = pack / "state" / "active-context.json"
    if not path.is_file():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    if not isinstance(data, dict):
        return None
    reads = data.get("allowed_reads")
    if not isinstance(reads, list):
        return None
    data["allowed_reads"] = [normalize_rel(item) for item in reads if isinstance(item, str)]
    return data


def activate(
    project: Path,
    workflow: str,
    step: str,
    slug: str,
    *,
    pack: Path | None = None,
    home: Path | None = None,
) -> dict[str, Any]:
    pack_dir = pack if pack is not None else pack_root_from(project, home=home)
    doc = load_workflow_doc(pack_dir, workflow)
    files = files_for_step(doc, step)
    data = build_pack(workflow, step, slug, files)
    write_pack(project, pack_dir, slug, data)
    return data


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Activate a workflow step allowlist.")
    parser.add_argument("--workflow", required=True)
    parser.add_argument("--step", required=True)
    parser.add_argument("--slug", required=True)
    parser.add_argument("--repo-root", default="", help="Project root (features/ live here).")
    parser.add_argument("--pack-root", default="", help="Override .pipeline pack directory.")
    args = parser.parse_args(argv)
    project = Path(args.repo_root).resolve() if args.repo_root else project_root_from()
    pack_override = Path(args.pack_root).resolve() if args.pack_root else None
    try:
        pack_dir = pack_root_from(project, pack_root=pack_override)
        data = activate(project, args.workflow, args.step, args.slug, pack=pack_dir)
    except ValueError as exc:
        sys.stderr.write(f"{exc}\n")
        return 1
    json.dump(data, sys.stdout, indent=2)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
