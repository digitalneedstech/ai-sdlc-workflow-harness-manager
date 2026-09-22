# Create an associate-owned workflow that cannot shadow first-party names.

from __future__ import annotations

import re
from pathlib import Path

from pipeline_orchestrator.graph import BUILTIN
from pipeline_orchestrator.registry import EXTENSIONS_DIR

SAFE = re.compile(r"^[a-z][a-z0-9-]{1,48}$")


def scaffold_workflow(project: Path, name: str) -> int:
    slug = name.strip().lower()
    if not SAFE.match(slug):
        print("invalid workflow name: %r (use kebab-case)" % name)
        return 1
    if slug in BUILTIN:
        print("cannot scaffold first-party workflow name: %s" % slug)
        return 1
    root = project / EXTENSIONS_DIR
    dest = root / (slug.replace("-", "_") + ".py")
    if dest.is_file():
        print("already exists: %s" % dest)
        return 1
    agent = slug + "-agent"
    gate = slug.split("-")[0]
    root.mkdir(parents=True, exist_ok=True)
    init = root / "__init__.py"
    if not init.is_file():
        init.write_text("\"\"\"Project-local orchestrator extensions. Not used by kit mode.\"\"\"\n", encoding="utf-8")
    py = (
        "from pipeline_orchestrator.graph import AgentStep, SignoffGate, WorkflowSpec\n\n"
        "PROVIDER = %r\n\n" % (project.name or "local")
        + "SPEC = WorkflowSpec(\n"
        + "    name=%r,\n" % slug
        + "    provider=PROVIDER,\n"
        + "    nodes=[\n"
        + "        AgentStep(\n"
        + "            id=%r,\n" % agent
        + "            context_files=(\"briefs/%s.md\",),\n" % agent
        + "        ),\n"
        + "        SignoffGate(id=%r),\n" % gate
        + "    ],\n"
        + ")\n"
    )
    dest.write_text(py, encoding="utf-8")
    brief_dir = root / "briefs"
    brief_dir.mkdir(parents=True, exist_ok=True)
    brief = brief_dir / (agent + ".md")
    brief.write_text(
        "# %s\n\nYou are `%s` in the `%s` workflow.\n"
        "Write features/{slug}/state/%s.json and a HANDOFF with **status:** SUCCESS.\n"
        % (slug, agent, slug, agent),
        encoding="utf-8",
    )
    print("created %s" % dest.relative_to(project))
    print("created %s" % brief.relative_to(project))
    print("run with: pipeline-kit run --slug <slug> --workflow %s" % slug)
    print("kit mode will not see this workflow.")
    return 0
