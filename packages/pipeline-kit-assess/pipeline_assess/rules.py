"""Criticality answers change priority. Kickstarter answers choose workflows, skills, agents, and file-type rules."""

from __future__ import annotations

from pathlib import Path

from pipeline_assess.gaps import selected_evals
from pipeline_assess.inventory import covers

QUESTIONS = (
    ("data", "Data handled? public, internal, or regulated"),
    ("impact", "If a bad change ships, who is hurt? team or customers"),
    ("cadence", "How does this repo ship? seldom or continuously"),
    ("teams", "Who owns it? one team or many"),
    ("workflows", "Custom workflows? ui-creation, ui-design, design-to-code, or none"),
    ("extra-persona", "Any persona besides the agents in .pipeline/agents? yes or no"),
    ("evals", "What should an eval check? agent-runs, product-behavior, ui, or none"),
)
WEIGHTS = {
    "workflow": 15,
    "testing": 15,
    "quality": 10,
    "delivery": 10,
    "observability": 5,
    "integrations": 5,
}
AGENT_CONTEXT = 20
GRAPH = 20
PERSONA_QUESTION = ("persona", "Name that persona and what they do")
_YES = frozenset({"yes", "y"})
_CRITICAL = frozenset(
    {"security-review", "agent-observability", "eval", "verify-rules"}
)
_AGENT_EVAL = frozenset({"eval", "agent-observability"})


def read_answers(path: Path) -> dict[str, str]:
    if not path.is_file():
        return {}
    found: dict[str, str] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        if ":" not in line or line.startswith("#"):
            continue
        key, _, value = line.partition(":")
        key = key.strip()
        value = value.strip()
        if key and value:
            found[key] = value
    return found


def write_answers(path: Path, answers: dict[str, str]) -> None:
    lines = [f"{key}: {answers[key]}" for key in sorted(answers)]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + ("\n" if lines else ""), encoding="utf-8")


def missing_questions(
    answers: dict[str, str],
    *,
    jira_unknown: bool,
    file_types: list[dict] | None = None,
) -> list[tuple[str, str]]:
    pending = [item for item in QUESTIONS if item[0] not in answers]
    if jira_unknown and "jira" not in answers:
        pending.append(("jira", "Is Jira in use? yes or no"))
    if "rule-types" not in answers:
        shown = ", ".join(
            str(item.get("ext")) for item in (file_types or [])[:12] if item.get("ext")
        )
        if shown:
            prompt = f"File types with no rule: {shown}. Create rules for which? all, none, or a comma list"
        else:
            prompt = "File types that should get a rule? none, or a comma list such as java,xml"
        pending.append(("rule-types", prompt))
    return pending


def ask(pending: list[tuple[str, str]], *, tty: bool, input_fn) -> dict[str, str]:
    if not tty or not pending:
        return {}
    print(
        f"{len(pending)} assessment question{'s' if len(pending) != 1 else ''}.",
        flush=True,
    )
    found = {}
    for key, prompt in pending:
        raw = input_fn(prompt + ": ").strip().lower()
        if raw:
            found[key] = raw
    return found


def _needs_persona(answers: dict[str, str]) -> bool:
    return (
        answers.get("extra-persona", "").strip().lower() in _YES
        and "persona" not in answers
    )


def collect_answers(
    answers: dict[str, str],
    *,
    file_types: list[dict],
    tty: bool,
    input_fn,
) -> tuple[dict[str, str], list[dict[str, str]]]:
    """Ask only what is still blank. Return the answers and the questions still open."""
    pending = missing_questions(answers, jira_unknown=True, file_types=file_types)
    answers.update(ask(pending, tty=tty, input_fn=input_fn))
    if _needs_persona(answers):
        answers.update(ask([PERSONA_QUESTION], tty=tty, input_fn=input_fn))
    still_open = [
        {"id": key, "prompt": prompt}
        for key, prompt in missing_questions(
            answers, jira_unknown=True, file_types=file_types
        )
    ]
    if _needs_persona(answers):
        still_open.append({"id": PERSONA_QUESTION[0], "prompt": PERSONA_QUESTION[1]})
    return answers, still_open


def apply_priority(
    items: list[dict], catalog_rows: list[dict], answers: dict[str, str]
) -> None:
    raised = answers.get("data") == "regulated" or answers.get("impact") == "customers"
    asked_evals = set(selected_evals(answers.get("evals", "")))
    for item in items:
        if item.get("sensitive") and raised:
            item["priority"] = "P0"
            item["benefit"] = (
                item["benefit"]
                + " Raised because the criticality answers mark this as customer or regulated impact."
            )
        elif item.get("sensitive"):
            item["priority"] = "P1"
    for row in catalog_rows:
        if row.get("status") != "recommended":
            continue
        reasons = []
        if raised and row["id"] in _CRITICAL:
            reasons.append(
                "Raised because data is regulated or customers are affected."
            )
        if "agent-runs" in asked_evals and row["id"] in _AGENT_EVAL:
            reasons.append("The scan answers asked for agent-run evaluation.")
        if reasons:
            row["priority"] = "P0"
            row["benefit"] = str(row.get("benefit") or "") + " " + " ".join(reasons)
        else:
            row["priority"] = "P1"


def coverage_scores(model: dict, items: list[dict], inventory: dict) -> dict[str, int]:
    areas = model.get("areas") or []
    total = sum(int(area.get("symbols") or 0) for area in areas) or 0
    if model.get("blocked") or total == 0:
        return {"coverage": 0, "projected": 0, "symbols": total}
    covered_folders = set()
    for area in areas:
        folder = str(area["folder"])
        if any(
            covers(artifact, folder) for artifact in inventory.get("artifacts") or []
        ):
            covered_folders.add(folder)
    covered = sum(
        int(area["symbols"]) for area in areas if area["folder"] in covered_folders
    )
    recommended = {str(item.get("folder")) for item in items}
    projected_folders = covered_folders | recommended
    projected = sum(
        int(area["symbols"]) for area in areas if area["folder"] in projected_folders
    )
    return {
        "coverage": round(100 * covered / total),
        "projected": round(100 * projected / total),
        "symbols": total,
    }


def kit_fit(catalog_rows: list[dict], inventory: dict, model: dict) -> int:
    score = 0
    if inventory.get("has_agents_md"):
        score += AGENT_CONTEXT
    if model.get("freshness", {}).get("state") == "fresh" and not model.get("blocked"):
        score += GRAPH
    elif model.get("product_nodes"):
        score += GRAPH // 2
    for dimension, weight in WEIGHTS.items():
        rows = [
            row
            for row in catalog_rows
            if row.get("dimension") == dimension and row.get("status") != "unknown"
        ]
        if not rows:
            score += weight
            continue
        done = sum(1 for row in rows if row.get("status") in {"in_use", "not_relevant"})
        score += round(weight * done / len(rows))
    return min(100, score)
