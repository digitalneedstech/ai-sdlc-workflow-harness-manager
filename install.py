#!/usr/bin/env python3
"""Install the portable pipeline pack into a project or ~/.pipeline.

    python3 install.py                          # creates ./.pipeline
    python3 install.py --project /path/to/app   # creates <app>/.pipeline
    python3 install.py --user                   # creates ~/.pipeline
    python3 install.py --sync-kit               # refresh the bundled pack from this repo
    python3 install.py --uninstall --project
    python3 install.py --uninstall --user
"""

from __future__ import annotations

import argparse
import json
import shutil
import stat
import sys
from pathlib import Path
from typing import Any


HERE = Path(__file__).resolve().parent
MARKER_NAME = "install.json"
PACK_DIRS = (
    "loader",
    "skills",
    "agents",
    "rules",
    "workflows",
    "wiki",
    "commands",
    "adapters",
    "docs",
)
PACK_FILES = ("README.md",)
SKIP_NAMES = {"state", "config.json", "install.json"}
IDE_SKILL_REL = {
    "cursor": Path(".cursor") / "skills" / "run-workflow" / "SKILL.md",
    "claude-code": Path(".claude") / "skills" / "run-workflow" / "SKILL.md",
    "github": Path(".github") / "skills" / "run-workflow" / "SKILL.md",
}


def version() -> str:
    return (HERE / "VERSION").read_text(encoding="utf-8").strip()


def bundled_pack() -> Path:
    return HERE / "kit" / "pipeline"


def live_pack() -> Path:
    """Optional working copy for maintainers (`./.pipeline`). Defaults to the bundle."""
    return HERE / ".pipeline"


def _is_pack_dir(path: Path) -> bool:
    return (path / "workflows").is_dir() and (path / "loader").is_dir()


def source_pack() -> Path:
    """Bundled kit first so install works even if this repo has no .pipeline."""
    bundled = bundled_pack()
    if _is_pack_dir(bundled):
        return bundled
    live = live_pack()
    if _is_pack_dir(live):
        return live
    raise FileNotFoundError(
        "pipeline pack source is missing. Run: python3 install.py --sync-kit"
    )


def _chmod_script(path: Path) -> None:
    if path.suffix in {".py", ".sh"}:
        path.chmod(path.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)


def _copy_file(src: Path, dest: Path, root: Path, copied: list[str]) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dest)
    _chmod_script(dest)
    copied.append(str(dest.relative_to(root)))


def _copy_tree(src: Path, dest: Path, root: Path, copied: list[str]) -> None:
    if not src.is_dir():
        return
    for item in sorted(src.rglob("*")):
        if item.is_dir():
            continue
        rel = item.relative_to(src)
        if any(part in SKIP_NAMES or part == "__pycache__" for part in rel.parts):
            continue
        _copy_file(item, dest / rel, root, copied)


def generic_config(source: dict[str, Any]) -> dict[str, Any]:
    data = json.loads(json.dumps(source))
    data["_readme"] = (
        "Project-specific pipeline config. Add verify.rules and deploy.targets "
        "for this repo. Do not put secrets, hosts, or tracker site URLs in other pack files."
    )
    verify = data.get("verify")
    if isinstance(verify, dict):
        verify["rules"] = []
        verify["_note"] = "Add path-substring reminders for this repo after install."
    deploy = data.get("deploy")
    if isinstance(deploy, dict):
        deploy["target"] = "auto"
        deploy["targets"] = ["auto"]
        deploy["_note"] = "Set targets this repo's deploy runbook understands."
    return data


def load_source_config(pack: Path) -> dict[str, Any]:
    path = pack / "config.json"
    if path.is_file():
        loaded = json.loads(path.read_text(encoding="utf-8"))
        if isinstance(loaded, dict):
            return loaded
    template = HERE / "kit" / "config.template.json"
    if template.is_file():
        loaded = json.loads(template.read_text(encoding="utf-8"))
        if isinstance(loaded, dict):
            return loaded
    return {"version": 1, "workflows": {}}


def merge_config(dest: Path, incoming: dict[str, Any]) -> str:
    dest.parent.mkdir(parents=True, exist_ok=True)
    if dest.is_file():
        loaded = json.loads(dest.read_text(encoding="utf-8"))
        if isinstance(loaded, dict):
            for key, value in incoming.items():
                if key not in loaded:
                    loaded[key] = value
            src_wf = incoming.get("workflows")
            dest_wf = loaded.setdefault("workflows", {})
            if isinstance(src_wf, dict) and isinstance(dest_wf, dict):
                for name, cfg in src_wf.items():
                    dest_wf.setdefault(name, cfg)
            dest.write_text(json.dumps(loaded, indent=2) + "\n", encoding="utf-8")
            return "merged"
    dest.write_text(json.dumps(incoming, indent=2) + "\n", encoding="utf-8")
    return "wrote"


def adapter_skill(pack: Path, ide: str) -> Path | None:
    candidate = pack / "adapters" / ide / "skills" / "run-workflow" / "SKILL.md"
    if candidate.is_file():
        return candidate
    fallback = pack / "adapters" / "cursor" / "skills" / "run-workflow" / "SKILL.md"
    return fallback if fallback.is_file() else None


def write_agent_stubs(agents_src: Path, dest_dir: Path, root: Path, copied: list[str]) -> None:
    if not agents_src.is_dir():
        return
    dest_dir.mkdir(parents=True, exist_ok=True)
    for src in sorted(agents_src.glob("*.md")):
        name = src.stem
        dest = dest_dir / src.name
        dest.write_text(
            (
                f"---\nname: {name}\n"
                f"description: Thin Cursor stub. Read .pipeline/agents/{src.name}.\n"
                "---\n\n"
                f"# {name}\n\n"
                f"Read and follow `.pipeline/agents/{src.name}`. "
                "This file exists only so Cursor can register the Task type.\n"
            ),
            encoding="utf-8",
        )
        copied.append(str(dest.relative_to(root)))


def _copy_tree_plain(src: Path, dest: Path) -> None:
    if not src.is_dir():
        return
    dest.mkdir(parents=True, exist_ok=True)
    for item in sorted(src.rglob("*")):
        if not item.is_file():
            continue
        rel = item.relative_to(src)
        if any(part in SKIP_NAMES or part == "__pycache__" for part in rel.parts):
            continue
        out = dest / rel
        out.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(item, out)
        _chmod_script(out)


def sync_kit() -> int:
    """Copy this repo's live .pipeline into the bundled kit (generic config)."""
    live = live_pack()
    if not _is_pack_dir(live):
        print(f"no live pack at {live}", file=sys.stderr)
        return 1
    dest = bundled_pack()
    if dest.exists():
        shutil.rmtree(dest)
    dest.mkdir(parents=True)
    for name in PACK_DIRS:
        _copy_tree_plain(live / name, dest / name)
    for name in PACK_FILES:
        src = live / name
        if src.is_file():
            shutil.copy2(src, dest / name)
    cfg = generic_config(load_source_config(live))
    (dest / "config.json").write_text(json.dumps(cfg, indent=2) + "\n", encoding="utf-8")
    guide = HERE / "CUSTOMER-GUIDE.md"
    if guide.is_file():
        docs = dest / "docs"
        docs.mkdir(parents=True, exist_ok=True)
        shutil.copy2(guide, docs / "CUSTOMER-GUIDE.md")
    print(f"synced kit ← {live}", file=sys.stderr)
    print(f"wrote {dest}", file=sys.stderr)
    return 0


def write_marker(pack_dest: Path, scope: str, files: list[str]) -> None:
    unique: list[str] = []
    for name in files:
        if name not in unique:
            unique.append(name)
    (pack_dest / MARKER_NAME).write_text(
        json.dumps(
            {"name": "pipeline-kit", "version": version(), "scope": scope, "files": unique},
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )


def install(
    *,
    scope: str,
    target: Path,
    ide: str,
    agent_stubs: bool,
    dry_run: bool,
    home: Path | None = None,
) -> int:
    pack_src = source_pack()
    home_dir = home or Path.home()
    if scope == "user":
        pack_dest = home_dir / ".pipeline"
        ide_root = home_dir
        marker_root = home_dir
    else:
        pack_dest = target / ".pipeline"
        ide_root = target
        marker_root = target
    print(f"kit:     {HERE} (v{version()})", file=sys.stderr)
    print(f"source:  {pack_src}", file=sys.stderr)
    print(f"target:  {pack_dest} ({scope})", file=sys.stderr)
    if dry_run:
        print("[dry run] would copy pack, merge config.json, write install.json", file=sys.stderr)
        return 0

    pack_dest.mkdir(parents=True, exist_ok=True)
    copied: list[str] = []
    for name in PACK_DIRS:
        _copy_tree(pack_src / name, pack_dest / name, marker_root, copied)
    for name in PACK_FILES:
        src = pack_src / name
        if src.is_file():
            dest_file = pack_dest / name
            dest_file.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dest_file)
            copied.append(str(dest_file.relative_to(marker_root)))

    guide = HERE / "CUSTOMER-GUIDE.md"
    if guide.is_file():
        dest_guide = pack_dest / "docs" / "CUSTOMER-GUIDE.md"
        dest_guide.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(guide, dest_guide)
        copied.append(str(dest_guide.relative_to(marker_root)))

    status = merge_config(pack_dest / "config.json", generic_config(load_source_config(pack_src)))
    print(f"config.json: {status}", file=sys.stderr)
    if ".pipeline/config.json" not in copied:
        copied.append(".pipeline/config.json")

    if ide != "none":
        skill_src = adapter_skill(pack_src, ide) or adapter_skill(pack_dest, ide)
        skill_rel = IDE_SKILL_REL.get(ide)
        if skill_src and skill_rel:
            if scope == "user" and ide in {"cursor", "claude-code"}:
                skill_dest = home_dir / skill_rel
                _copy_file(skill_src, skill_dest, home_dir, copied)
            elif scope == "project":
                _copy_file(skill_src, ide_root / skill_rel, target, copied)
            else:
                print(f"note: --user --ide {ide} writes no IDE adapter (use cursor, claude-code, or --project)", file=sys.stderr)

    if agent_stubs:
        stubs_dir = (
            (home_dir / ".cursor" / "agents")
            if scope == "user"
            else (target / ".cursor" / "agents")
        )
        stubs_root = home_dir if scope == "user" else target
        write_agent_stubs(pack_src / "agents", stubs_dir, stubs_root, copied)

    marker_pack = pack_dest
    write_marker(marker_pack, scope, copied)
    copied.append(".pipeline/install.json" if scope == "project" else MARKER_NAME)
    print(f"installed {version()}: {len(copied)} files", file=sys.stderr)
    print(f"Done. Loader: python3 {pack_dest / 'loader' / 'load_workflow.py'}", file=sys.stderr)
    return 0


def uninstall(*, scope: str, target: Path, home: Path | None = None) -> int:
    home_dir = home or Path.home()
    pack = (home_dir / ".pipeline") if scope == "user" else (target / ".pipeline")
    marker = pack / MARKER_NAME
    if not marker.is_file():
        print(f"no pipeline-kit install at {pack} ({MARKER_NAME} missing)", file=sys.stderr)
        return 1
    meta = json.loads(marker.read_text(encoding="utf-8"))
    root = home_dir if scope == "user" else target
    removed = 0
    for rel in meta.get("files") or []:
        path = root / rel
        if path.is_file():
            path.unlink()
            removed += 1
    if marker.is_file():
        marker.unlink()
        removed += 1
    print(f"removed {removed} kit files; features/ and local config edits were left.", file=sys.stderr)
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Create a .pipeline folder in a project or in your home directory."
    )
    scope = parser.add_mutually_exclusive_group(required=False)
    scope.add_argument(
        "--project",
        nargs="?",
        const=".",
        default=None,
        help="create <path>/.pipeline (default: current directory)",
    )
    scope.add_argument("--user", action="store_true", help="create ~/.pipeline")
    parser.add_argument("--ide", choices=("cursor", "claude-code", "github", "none"), default="cursor")
    parser.add_argument("--agent-stubs", action="store_true")
    parser.add_argument("--uninstall", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument(
        "--sync-kit",
        action="store_true",
        help="refresh kit/pipeline from this repo's .pipeline (maintainers)",
    )
    parser.add_argument("--home", default="", help=argparse.SUPPRESS)
    args = parser.parse_args(argv)
    if args.sync_kit:
        return sync_kit()
    home = Path(args.home).expanduser().resolve() if args.home else None
    if args.user:
        target = home or Path.home()
        scope_name = "user"
    else:
        target = Path(args.project or ".").expanduser().resolve()
        scope_name = "project"
        if not target.is_dir():
            print(f"not a directory: {target}", file=sys.stderr)
            return 64
    if args.uninstall:
        return uninstall(scope=scope_name, target=target, home=home)
    return install(
        scope=scope_name,
        target=target,
        ide=args.ide,
        agent_stubs=args.agent_stubs,
        dry_run=args.dry_run,
        home=home,
    )


if __name__ == "__main__":
    raise SystemExit(main())
