"""Compose step prompts from the wheel (kit briefs) or an associate package."""

from __future__ import annotations

import json
from pathlib import Path

from pipeline_orchestrator.graph import AgentStep
from pipeline_orchestrator.pack import kit_pack_root, normalize_pack_rel

PROMPT_BUDGET = 400_000
ISOLATION = Path(__file__).resolve().parent / "prompts" / "isolation.txt"


def files_for_kit_step(workflow: str, step: str) -> list[str]:
    path = kit_pack_root() / "workflows" / f"{workflow}.json"
    if not path.is_file():
        path = kit_pack_root() / "workflows" / "feature-development.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    steps = (data.get("context") or {}).get("steps") or {}
    block = steps.get(step) or {}
    files = block.get("files") or []
    return [normalize_pack_rel(item) for item in files if isinstance(item, str)]


def _read_rel(rel: str, *, project: Path, spec_dir: Path | None) -> tuple[str, str]:
    if rel.startswith("kit:"):
        rel = files_for_kit_step("feature-development", rel[4:])[0] if ":" in rel else rel
    if rel.startswith("kit:"):
        rels = files_for_kit_step("feature-development", rel.split(":", 1)[1])
        chunks = []
        for item in rels:
            text = (kit_pack_root() / item).read_text(encoding="utf-8")
            chunks.append(f"## {item}\n\n{text}")
        return rel, "\n\n".join(chunks)
    kit = kit_pack_root() / rel
    if kit.is_file():
        return rel, kit.read_text(encoding="utf-8")
    if spec_dir is not None:
        local = spec_dir / rel
        if local.is_file():
            return rel, local.read_text(encoding="utf-8")
        brief = spec_dir / "briefs" / Path(rel).name
        if brief.is_file():
            return str(brief.relative_to(spec_dir)), brief.read_text(encoding="utf-8")
    project_rel = project / rel
    if project_rel.is_file():
        return rel, project_rel.read_text(encoding="utf-8")
    raise FileNotFoundError(f"context file not found: {rel}")


def resolve_context_files(step: AgentStep, workflow: str) -> list[str]:
    if step.context_files:
        out: list[str] = []
        for item in step.context_files:
            if item.startswith("kit:"):
                out.extend(files_for_kit_step("feature-development", item.split(":", 1)[1]))
            else:
                out.append(item)
        return out
    source = step.context_from or step.id
    try:
        return files_for_kit_step(workflow, source)
    except Exception:
        return files_for_kit_step("feature-development", source)


def compose_prompt(
    *,
    step: AgentStep,
    workflow: str,
    change_class: str,
    slug: str,
    project: Path,
    extra: dict[str, str] | None = None,
    spec_dir: Path | None = None,
) -> tuple[str, str]:
    import hashlib

    isolation = ISOLATION.read_text(encoding="utf-8") if ISOLATION.is_file() else ""
    files = resolve_context_files(step, workflow)
    parts = [isolation.strip(), ""]
    fields = {
        "WORKFLOW": workflow,
        "CHANGE_CLASS": change_class,
        "REPO_ROOT": str(project.resolve()),
        "FEATURE_SLUG": slug,
        "PIPELINE_STATE_PATH": f"features/{slug}/pipeline-state.json",
        "PRIOR_STATE_PATH": (
            f"features/{slug}/state/{step.prior_agent}.json" if step.prior_agent else "none"
        ),
        "STEP": step.id,
    }
    if extra:
        fields.update(extra)
    parts.append("## Run fields\n")
    for key, value in fields.items():
        parts.append(f"{key}: {value}")
    parts.append("")
    parts.append(
        f"You are {step.id}. Follow the inlined brief and skills below. "
        "Do not read `.pipeline/agents` or `.pipeline/skills` from disk — they are not installed in orchestrator mode. "
        "Write artifacts under features/{slug}/ only. "
        f"Write features/{slug}/state/{step.id}.json when done. "
        "Return a short HANDOFF with **status:** SUCCESS | BLOCKED | ASSUMPTIONS_USED | changes-required."
    )
    parts.append("")
    for rel in files:
        name, text = _read_rel(rel, project=project, spec_dir=spec_dir)
        parts.append(f"\n----- BEGIN {name} -----\n{text}\n----- END {name} -----\n")
    prompt = "\n".join(parts)
    if len(prompt) > PROMPT_BUDGET:
        raise ValueError(
            f"composed prompt for {step.id} is {len(prompt)} chars (budget {PROMPT_BUDGET})"
        )
    digest = hashlib.sha256(prompt.encode("utf-8")).hexdigest()
    return prompt, digest
