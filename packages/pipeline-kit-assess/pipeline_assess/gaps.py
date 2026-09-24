"""Custom files this repo still needs. Ids come from folders, not community numbers."""

from __future__ import annotations

import re

from pipeline_assess.catalog import DENY
from pipeline_assess.inventory import covers

MAX_ITEMS = 12
TESTING_SKILLS = {
    "testing-unit",
    "testing-e2e",
    "testing-ui-playwright",
    "testing-api",
    "test-design",
}


def _slug(text: str) -> str:
    cleaned = re.sub(r"[^a-z0-9]+", "-", text.lower()).strip("-")
    return cleaned or "area"


def _item(
    kind: str,
    folder: str,
    *,
    evidence: str,
    benefit: str,
    sensitive: bool = False,
    globs: list[str] | None = None,
    when: str = "",
    action: str = "",
) -> dict:
    ident = f"{kind}-{_slug(folder)}"
    if kind == "workflow":
        path = f".pipeline/workflows/{_slug(folder)}.json"
    elif kind == "skill":
        path = f".pipeline/skills/{_slug(folder)}/SKILL.md"
    elif kind == "hook":
        path = f".pipeline/hooks/{_slug(folder)}.py"
    elif kind == "agent":
        path = f".pipeline/agents/{_slug(folder)}.md"
    else:
        path = f".cursor/rules/{_slug(folder)}.mdc"
    return {
        "id": ident,
        "kind": kind,
        "list": "create",
        "path": path,
        "folder": folder,
        "evidence": evidence,
        "benefit": benefit,
        "covered_by": "none",
        "sensitive": sensitive,
        "priority": "P1",
        "globs": [f"{folder}/**"] if globs is None else globs,
        "when": when,
        "action": action,
    }


def _covered(folder: str, inventory: dict) -> str | None:
    for artifact in inventory.get("artifacts") or []:
        if covers(artifact, folder):
            return str(artifact.get("name"))
    return None


def create_items(
    model: dict, inventory: dict, signals: dict, answers: dict | None = None
) -> tuple[list[dict], list[dict]]:
    unknown = [
        {
            "folder": folder,
            "reason": "Graphify does not index this folder's file types.",
        }
        for folder in model.get("blind") or []
    ]
    answers = answers or {}
    if model.get("blocked"):
        return kickoff_items(answers, uncovered_file_types(model, inventory)), unknown
    skills = set(inventory.get("skills") or [])
    testing_shipped = bool(skills & TESTING_SKILLS) or inventory.get("flags", {}).get(
        "test-design"
    )
    items: list[dict] = []
    seen: set[str] = set()

    def push(item: dict) -> None:
        if item["id"] in seen or item["id"] in DENY:
            return
        seen.add(item["id"])
        items.append(item)

    for area in model.get("areas") or []:
        folder = str(area["folder"])
        if folder in (model.get("blind") or []):
            continue
        owner = _covered(folder, inventory)
        if owner:
            continue
        evidence = f"{folder} ({area['symbols']} code symbols)"
        if area.get("labels"):
            evidence += ": " + ", ".join(area["labels"][:3])
        sensitive = bool(area.get("sensitive"))
        if sensitive:
            check = (
                f"Before editing `{folder}`, name the auth, crypto, billing, or tenant behavior the change touches "
                "and the test that covers it. Do not copy production credentials or customer data into the change."
            )
            push(
                _item(
                    "rule",
                    folder,
                    evidence=evidence,
                    benefit="Agents change this area only with a stated check.",
                    sensitive=True,
                    when=f"Any edit under `{folder}/`.",
                    action=check,
                )
            )
            push(
                _item(
                    "hook",
                    folder,
                    evidence=evidence,
                    benefit="Edits in this area are checked before they land.",
                    sensitive=True,
                    when="After a file edit, once this hook is registered on afterFileEdit.",
                    action=check,
                )
            )
            continue
        if area.get("service") and area.get("god"):
            push(
                _item(
                    "rule",
                    folder,
                    evidence=evidence,
                    benefit="The most-connected code in this service keeps a written boundary.",
                )
            )
            push(
                _item(
                    "workflow",
                    folder,
                    evidence=evidence,
                    benefit="Changes here follow a workflow instead of a one-off prompt.",
                )
            )
            continue
        if signals.get("frontend") and folder.split("/")[0] in {
            "web",
            "frontend",
            "ui",
            "app",
            "src",
        }:
            push(
                _item(
                    "rule",
                    folder,
                    evidence=evidence,
                    benefit="UI changes stay inside the folders this rule names.",
                )
            )
            continue
        if not area.get("tested") and not testing_shipped:
            push(
                _item(
                    "skill",
                    folder + "-tests",
                    evidence=evidence + "; no test calls this area",
                    benefit="Tests for this area are designed before the code change.",
                )
            )
            continue
        push(
            _item(
                "rule",
                folder,
                evidence=evidence,
                benefit="Agents have a written scope for this product area.",
            )
        )

    for pair in model.get("coupling") or []:
        folder = f"{pair['left']}-{pair['right']}"
        push(
            _item(
                "rule",
                "boundary-" + folder,
                evidence=f"{pair['count']} calls or imports between {pair['left']} and {pair['right']}",
                benefit="Cross-area changes name both sides.",
                globs=[f"{pair['left']}/**", f"{pair['right']}/**"],
                when=f"An edit touches both `{pair['left']}` and `{pair['right']}`.",
                action=(
                    f"The graph shows {pair['count']} calls or imports between these folders. "
                    "Say which side owns the change and which side is only called."
                ),
            )
        )
    if signals.get("docker"):
        push(
            _item(
                "rule",
                "docker",
                evidence="Dockerfile or Compose file is present.",
                benefit="Image and compose edits keep a stated check.",
            )
        )
        push(
            _item(
                "hook",
                "docker",
                evidence="Dockerfile or Compose file is present.",
                benefit="Container file edits are checked before they land.",
            )
        )
    if signals.get("iac"):
        push(
            _item(
                "rule",
                "infra",
                evidence="Terraform or Helm files are present.",
                benefit="Infrastructure edits stay in a named rule.",
            )
        )
    if signals.get("ci") and inventory.get("mode") != "orchestrator":
        push(
            _item(
                "rule",
                "ci",
                evidence="CI workflow files are present.",
                benefit="Pipeline edits keep a verify rule.",
                globs=[".github/workflows/**", "Jenkinsfile"],
                when="An edit changes a workflow, Jenkinsfile, or pipeline YAML.",
                action="Keep secrets out of the workflow file. Name the command the new step runs and how a failure is visible.",
            )
        )
    if signals.get("llm"):
        push(
            _item(
                "skill",
                "product-eval",
                evidence="An LLM SDK is declared in a manifest.",
                benefit="The product's own model behavior gets an eval set, separate from agent-run scores.",
            )
        )
    sensitive_ids = [item for item in items if item.get("sensitive")]
    stack_ids = [
        item
        for item in items
        if item["folder"] in {"docker", "infra", "ci", "product-eval"}
        or item["folder"].startswith("boundary-")
    ]
    rest = [
        item for item in items if item not in sensitive_ids and item not in stack_ids
    ]
    rest.sort(key=lambda item: item["id"])
    kept = sensitive_ids + stack_ids
    for item in rest:
        if len(kept) >= MAX_ITEMS:
            break
        kept.append(item)
    kept.extend(kickoff_items(answers, uncovered_file_types(model, inventory)))
    return kept, unknown


WORKFLOWS = {
    "ui-creation": {
        "summary": "Create a new UI surface.",
        "steps": (
            ("choose-ui-surface", "Name the screen or component this UI adds."),
            (
                "build-ui",
                "Build the surface with the components this repo already uses.",
            ),
            ("check-ui", "Check the new surface in the browser before finishing."),
        ),
    },
    "ui-design": {
        "summary": "Produce a UI design before code.",
        "steps": (
            ("read-ui-brief", "Read the brief and name the screens in scope."),
            ("draft-ui-design", "Draft the layout, states, and content."),
            (
                "review-ui-design",
                "Review the design against the brief before code starts.",
            ),
        ),
    },
    "design-to-code": {
        "summary": "Turn a design into a code change.",
        "steps": (
            (
                "read-design",
                "Read the design and list the screens and states it contains.",
            ),
            (
                "plan-code-changes",
                "Plan which files change and which existing components to reuse.",
            ),
            (
                "implement-from-design",
                "Implement the planned change so it matches the design.",
            ),
        ),
    },
}
_WORKFLOW_ALIASES = {
    "ui creation": "ui-creation",
    "ui-creation": "ui-creation",
    "ui design": "ui-design",
    "ui-design": "ui-design",
    "design to code": "design-to-code",
    "design-to-code": "design-to-code",
}
_EVAL_ALIASES = {
    "agent-runs": "agent-runs",
    "agent runs": "agent-runs",
    "product-behavior": "product-behavior",
    "product behavior": "product-behavior",
    "ui": "ui",
    "ui-eval": "ui",
}
_EVAL_SKILLS = {
    "product-behavior": (
        "product-behavior-eval",
        "Name the product behavior, the cases, and what a pass looks like.",
    ),
    "ui": (
        "ui-eval",
        "Compare the screen to the design or brief and record pass or fail.",
    ),
}
_NONE = {"", "none", "no", "n"}
_YES = {"yes", "y"}
FILE_TYPE_CAP = 12


def uncovered_file_types(model: dict, inventory: dict) -> list[dict]:
    covered = {ext.lower() for ext in inventory.get("rule_extensions") or []}
    found = []
    for item in model.get("file_types") or []:
        ext = str(item.get("ext") or "").lower()
        if ext and ext not in covered:
            found.append({"ext": ext, "files": int(item.get("files") or 0)})
    return found


def selected_evals(value: str) -> list[str]:
    chosen: list[str] = []
    for part in re.split(r"[,;/]|\band\b", value.lower()):
        token = _EVAL_ALIASES.get(part.strip())
        if token and token not in chosen:
            chosen.append(token)
    return chosen


def _selected_workflows(value: str) -> list[str]:
    chosen: list[str] = []
    for part in re.split(r"[,;/]|\band\b", value.lower()):
        token = _WORKFLOW_ALIASES.get(part.strip())
        if token and token not in chosen:
            chosen.append(token)
    return chosen


def _selected_extensions(value: str, uncovered: list[dict]) -> list[str]:
    raw = value.strip().lower()
    if raw in _NONE:
        return []
    if raw in _YES or raw == "all":
        return [item["ext"] for item in uncovered[:FILE_TYPE_CAP]]
    chosen: list[str] = []
    for part in re.split(r"[,;\s]+", raw):
        ext = part.strip().lstrip(".")
        if ext.isalnum() and ext not in chosen:
            chosen.append(ext)
    return chosen[:FILE_TYPE_CAP]


def _persona(answers: dict) -> str:
    flag = answers.get("extra-persona", "").strip().lower()
    if flag in _NONE:
        return ""
    if flag in _YES:
        persona = answers.get("persona", "").strip()
        if persona.lower() in _NONE or persona.lower() in _YES:
            return ""
        return persona
    return flag


def kickoff_items(answers: dict, uncovered: list[dict]) -> list[dict]:
    items: list[dict] = []
    seen: set[str] = set()

    def push(item: dict) -> None:
        if item["id"] in seen or item["id"] in DENY:
            return
        seen.add(item["id"])
        items.append(item)

    for name in _selected_workflows(answers.get("workflows", "")):
        spec = WORKFLOWS[name]
        steps = [
            {"id": step, "skill": f".pipeline/skills/{step}/SKILL.md", "does": action}
            for step, action in spec["steps"]
        ]
        workflow = _item(
            "workflow",
            name,
            evidence="Named in the scan answers.",
            benefit=spec["summary"],
            globs=[],
            when=f"The customer asked for the {name} workflow.",
            action=spec["summary"],
        )
        workflow["steps"] = steps
        push(workflow)
        for step, action in spec["steps"]:
            push(
                _item(
                    "skill",
                    step,
                    evidence=f"Step of the {name} workflow.",
                    benefit=action,
                    globs=[],
                    when=f"During the {name} workflow, at the {step} step.",
                    action=action,
                )
            )
    persona = _persona(answers)
    if persona:
        title = persona.split(",")[0].strip()
        push(
            _item(
                "agent",
                title,
                evidence=persona,
                benefit="A persona the shipped agents do not cover.",
                globs=[],
                when="Work that belongs to this persona.",
                action=persona,
            )
        )
    for name in selected_evals(answers.get("evals", "")):
        skill = _EVAL_SKILLS.get(name)
        if not skill:
            continue
        step, action = skill
        push(
            _item(
                "skill",
                step,
                evidence="Named in the scan answers.",
                benefit=action,
                globs=[],
                when=f"When checking {name.replace('-', ' ')}.",
                action=action,
            )
        )
    named = _selected_extensions(answers.get("rule-types", ""), uncovered)
    counts = {item["ext"]: item["files"] for item in uncovered}
    for ext in named:
        count = counts.get(ext)
        evidence = (
            f"{count} .{ext} files have no installed rule for this type."
            if count
            else f"The scan answers asked for a .{ext} rule."
        )
        push(
            _item(
                "rule",
                f"type-{ext}",
                evidence=evidence,
                benefit=f"Edits to .{ext} files have a written check.",
                globs=[f"**/*.{ext}"],
                when=f"An edit touches a .{ext} file.",
                action=f"Before editing a .{ext} file, state the check that belongs to this file type.",
            )
        )
    return items
