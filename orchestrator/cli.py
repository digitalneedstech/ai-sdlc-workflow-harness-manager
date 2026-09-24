"""CLI helpers for orchestrator mode. Wired from install.cli_main."""

from __future__ import annotations

import asyncio
import json
import os
from pathlib import Path

from pipeline_orchestrator import EXIT_STARTUP
from pipeline_orchestrator.deciders.base import DecisionError, DecisionRequest, job_for
from pipeline_orchestrator.deciders.factory import decider_name, make_decider
from pipeline_orchestrator.engine import advance, start_run
from pipeline_orchestrator.graph import AgentStep, LayerFan, WaveFan
from pipeline_orchestrator.gates import approve
from pipeline_orchestrator.registry import list_specs, resolve_spec
from pipeline_orchestrator.runners.cursor_sdk import CursorSdkRunner
from pipeline_orchestrator.runners.fake import FakeRunner
from pipeline_orchestrator.state import load_run, request_path
from pipeline_orchestrator.verify import cmd_verify, read_install_mode


def resolve_user_request(
    project: Path,
    slug: str,
    request: str = "",
    request_file: str = "",
) -> str:
    text = (request or "").strip()
    if text:
        return text
    if request_file:
        path = Path(request_file)
        if not path.is_absolute():
            path = project / path
        if not path.is_file():
            raise FileNotFoundError("request file not found: %s" % path)
        return path.read_text(encoding="utf-8").strip()
    auto = request_path(project, slug)
    if auto.is_file():
        return auto.read_text(encoding="utf-8").strip()
    return ""


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


def _dry_run_steps(chain: list) -> list[AgentStep]:
    steps: list[AgentStep] = []
    for node in chain:
        if isinstance(node, AgentStep):
            steps.append(node)
        elif isinstance(node, WaveFan):
            steps.extend(AgentStep(id=step_id, context_from=step_id) for step_id in node.child_chain)
        elif isinstance(node, LayerFan):
            steps.extend(
                AgentStep(id="tester-agent-%s" % layer, context_from="tester-agent")
                for layer in node.layers
            )
    return steps


def _print_dry_run(project: Path, *, spec, change_class: str, runner: str, user_request: str) -> int:
    try:
        name = decider_name(project)
    except ValueError as exc:
        print(str(exc))
        return EXIT_STARTUP
    try:
        chain = spec.chain_for(change_class)
    except ValueError as exc:
        print(str(exc))
        return EXIT_STARTUP
    print("workflow=%s provider=%s class=%s decider=%s" % (spec.name, spec.provider, change_class, name))
    catalog: list[str] = []
    model_info: dict[str, dict] = {}
    decider = None
    catalog_note = ""
    try:
        impl = _runner(runner)
        if runner in {"cursor", "cursor-sdk"} and not os.environ.get("CURSOR_API_KEY", "").strip():
            catalog_note = "catalog_unavailable"
        elif runner in {"cursor", "cursor-sdk"} and not impl.is_available():
            catalog_note = "catalog_unavailable"
        else:
            catalog = [item for item in impl.list_models() if item]
            loaded = getattr(impl, "model_info", None)
            if callable(loaded):
                raw = loaded()
                if isinstance(raw, dict):
                    model_info = {str(key): value for key, value in raw.items() if isinstance(value, dict)}
            decider = make_decider(project)
    except Exception as exc:
        if runner in {"cursor", "cursor-sdk"} and not os.environ.get("CURSOR_API_KEY", "").strip():
            catalog_note = "catalog_unavailable"
        else:
            print(str(exc))
            return EXIT_STARTUP
    if decider is not None and not catalog:
        catalog_note = "catalog_unavailable"
        decider = None
    rows: list[str] = []
    for step in _dry_run_steps(chain):
        if decider is None:
            print("model step=%s chosen=? reason=%s decider=%s" % (step.id, catalog_note or "catalog_unavailable", name))
            rows.append("  %s  chosen=?  reason=%s" % (step.id, catalog_note or "catalog_unavailable"))
            continue
        try:
            decision = decider.decide(
                DecisionRequest(
                    step_id=step.id,
                    job=job_for(step.id),
                    user_request=user_request,
                    workflow=spec.name,
                    change_class=change_class,
                    prior_status="",
                    catalog=tuple(catalog),
                    pin=step.model,
                    model_info=model_info,
                )
            )
        except DecisionError as exc:
            print("model step=%s chosen=? reason=error decider=%s error=%s" % (step.id, name, exc))
            rows.append("  %s  chosen=?  reason=error" % step.id)
            continue
        print(decision.format(step.id))
        rows.append(decision.summary_line(step.id))
    if rows:
        print("summary")
        for row in rows:
            print(row)
    return 0


def cmd_run(
    project: Path,
    *,
    slug: str,
    workflow: str,
    change_class: str,
    runner: str,
    dry_run: bool,
    request: str = "",
    request_file: str = "",
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
        try:
            user_request = resolve_user_request(project, slug, request, request_file)
        except FileNotFoundError:
            user_request = ""
        return _print_dry_run(
            project,
            spec=spec,
            change_class=cls,
            runner=runner,
            user_request=user_request,
        )
    if runner in {"cursor", "cursor-sdk"} and not os.environ.get("CURSOR_API_KEY", "").strip():
        print("CURSOR_API_KEY is not set")
        return EXIT_STARTUP
    try:
        impl = _runner(runner)
    except ValueError as exc:
        print(str(exc))
        return EXIT_STARTUP
    if runner in {"cursor", "cursor-sdk"} and not impl.is_available():
        print("cursor-sdk missing; install with: uv tool install -e \".[orchestrator]\"")
        return EXIT_STARTUP
    try:
        user_request = resolve_user_request(project, slug, request, request_file)
    except FileNotFoundError as exc:
        print(str(exc))
        return EXIT_STARTUP
    if not user_request:
        print(
            "warning: no user request; pass --request or write features/%s/request.md"
            % slug
        )
    else:
        print("USER_REQUEST: %s" % user_request.splitlines()[0][:200])
    run = start_run(
        project=project,
        spec=spec,
        slug=slug,
        change_class=cls,
        runner_name=runner,
        kit_version=version(),
        user_request=user_request,
    )
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
