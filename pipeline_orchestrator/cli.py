"""CLI helpers for orchestrator mode. Wired from install.cli_main."""

from __future__ import annotations

import asyncio
import json
import os
from pathlib import Path

from pipeline_orchestrator import EXIT_STARTUP
from pipeline_orchestrator.engine import advance, start_run
from pipeline_orchestrator.gates import approve
from pipeline_orchestrator.registry import list_specs, resolve_spec
from pipeline_orchestrator.runners.cursor_sdk import CursorSdkRunner
from pipeline_orchestrator.runners.fake import FakeRunner
from pipeline_orchestrator.state import load_run
from pipeline_orchestrator.verify import cmd_verify, read_install_mode


def _runner(name: str, fake_results: dict | None = None):
    key = (name or "cursor").strip().lower()
    if key == "fake":
        return FakeRunner(fake_results)
    if key in {"cursor", "cursor-sdk"}:
        return CursorSdkRunner()
    raise ValueError("unknown runner: %s" % name)


def cmd_list_orchestrator(project: Path) -> int:
    print("name\tprovider\tsource")
    for spec in list_specs(project):
        source = "built-in" if spec.provider == "pipeline-kit" else "extension"
        print("%s\t%s\t%s" % (spec.name, spec.provider, source))
    return 0


def cmd_run(
    project: Path,
    *,
    slug: str,
    workflow: str,
    change_class: str,
    runner: str,
    dry_run: bool,
) -> int:
    from install import version

    try:
        spec = resolve_spec(workflow, project)
    except ValueError as exc:
        print(str(exc))
        return EXIT_STARTUP
    spec_dir = None
    ext = project / "pipeline_extensions"
    if spec.provider != "pipeline-kit" and ext.is_dir():
        spec_dir = ext
    cls = change_class or spec.default_change_class
    if dry_run:
        chain = spec.chain_for(cls)
        print("workflow=%s provider=%s class=%s" % (spec.name, spec.provider, cls))
        for node in chain:
            print("  - %s (%s)" % (node.id, type(node).__name__))
        return 0
    if runner in {"cursor", "cursor-sdk"} and not os.environ.get("CURSOR_API_KEY", "").strip():
        print("CURSOR_API_KEY is not set")
        return EXIT_STARTUP
    run = start_run(
        project=project,
        spec=spec,
        slug=slug,
        change_class=cls,
        runner_name=runner,
        kit_version=version(),
    )
    try:
        impl = _runner(runner)
    except ValueError as exc:
        print(str(exc))
        return EXIT_STARTUP
    return asyncio.run(advance(project=project, spec=spec, run=run, runner=impl, spec_dir=spec_dir))


def cmd_resume(project: Path, *, slug: str, runner: str = "cursor") -> int:
    run = load_run(project, slug)
    spec = resolve_spec(str(run["workflow"]), project)
    spec_dir = project / "pipeline_extensions" if spec.provider != "pipeline-kit" else None
    impl = _runner(runner or str(run.get("runner") or "cursor"))
    return asyncio.run(advance(project=project, spec=spec, run=run, runner=impl, spec_dir=spec_dir))


def cmd_approve(project: Path, *, slug: str, gate: str, note: str) -> int:
    return approve(project=project, slug=slug, gate=gate, note=note)


def cmd_status(project: Path, *, slug: str) -> int:
    run = load_run(project, slug)
    print(json.dumps(run, indent=2))
    return 0


def cmd_export_briefs(project: Path) -> int:
    import shutil
    from pipeline_orchestrator.pack import kit_pack_root

    dest = project / ".pipeline" / "_reference"
    src = kit_pack_root()
    dest.mkdir(parents=True, exist_ok=True)
    (dest / "README.md").write_text(
        "# Reference copy only\n\nThese files are not executed in orchestrator mode.\n",
        encoding="utf-8",
    )
    for name in ("agents", "skills"):
        if (src / name).is_dir():
            target = dest / name
            if target.exists():
                shutil.rmtree(target)
            shutil.copytree(src / name, target)
    print("wrote %s (non-executing reference)" % dest)
    return 0
