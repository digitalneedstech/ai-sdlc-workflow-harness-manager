"""Write features/pack-scan/{context,prompt}.md. Does not call a model."""

from __future__ import annotations

import sys
from pathlib import Path

from pipeline_plugins.graphify import graph_exists
from pipeline_scan.graph_context import GraphSliceError, ensure_graphifyignore, graph_slice
from pipeline_scan.inventory import InventoryError, collect_surface

_KIT_ADD = """\
Kit mode: add a workflow with a skill at `.pipeline/skills/{name}/SKILL.md`, a workflow file `.pipeline/workflows/{name}.json`, and a `workflows.{name}` entry in `.pipeline/config.json`. See the add-workflow guide. Add a sub-agent as `.pipeline/agents/{role}.md` and put it on that step's allowlist. Add a rule under `.cursor/rules/` or `.pipeline/rules/`. Add a hook only by extending `.pipeline/hooks/` the way the pack already merges hooks.
"""

_ORCH_ADD = """\
Orchestrator mode: add a workflow with `pipeline-kit workflows --scaffold {name}`. That writes `pipeline_extensions/{name}.py`. Do not reuse a first-party workflow name. Copy-ready graphs (`security-review`, `ci-audit`, `dependency-audit`, `accessibility-review`) are copied from the kit's `extensions/orchestrator/pipeline_extensions/` when the graph shows that process and the name is not already installed.
"""


def _add_steps(mode: str) -> str:
    if mode == "orchestrator":
        return _ORCH_ADD.strip()
    return _KIT_ADD.strip()


def _prompt_text(mode: str) -> str:
    template = (Path(__file__).resolve().parent / "prompt.md").read_text(encoding="utf-8")
    return template.replace("{{MODE}}", mode).replace("{{ADD_STEPS}}", _add_steps(mode))


def cmd_scan(project: Path, *, out: Path | None = None) -> int:
    project = project.expanduser().resolve()
    if not project.is_dir():
        print(f"not a directory: {project}", file=sys.stderr)
        return 64
    pack = project / ".pipeline"
    if not (pack / "install.json").is_file():
        print(
            f"no pipeline-kit install at {pack}. Run: pipeline-kit init",
            file=sys.stderr,
        )
        return 1
    if not graph_exists(project):
        from pipeline_plugins.graphify import RECOVERY

        print(
            "graphify-out/graph.json is missing. Build the knowledge graph, then retry.",
            file=sys.stderr,
        )
        print(RECOVERY, file=sys.stderr)
        return 1
    dest = out if out is not None else project / "features" / "pack-scan"
    if not dest.is_absolute():
        dest = project / dest
    wrote_ignore = ensure_graphifyignore(project)
    try:
        surface = collect_surface(project, pack)
        communities = graph_slice(project)
    except (InventoryError, GraphSliceError) as exc:
        print(str(exc), file=sys.stderr)
        recovery = getattr(exc, "recovery", "")
        if recovery:
            print(recovery, file=sys.stderr)
        return 1
    context = (
        "# Pack scan context\n\n"
        + surface.as_markdown()
        + "\n## Graph communities\n"
        + communities.rstrip()
        + "\n"
    )
    dest.mkdir(parents=True, exist_ok=True)
    context_path = dest / "context.md"
    prompt_path = dest / "prompt.md"
    context_path.write_text(context, encoding="utf-8")
    prompt_path.write_text(_prompt_text(surface.mode), encoding="utf-8")
    print(f"context: {context_path}")
    print(f"prompt: {prompt_path}")
    if wrote_ignore:
        print(f"graphifyignore: {project / '.graphifyignore'}")
        print("Next: pipeline-kit knowledge extract")
    return 0
