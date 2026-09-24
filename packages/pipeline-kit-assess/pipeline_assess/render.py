"""Deterministic assessment files. The clock lives only in assessment-run.json."""

from __future__ import annotations

import json
from pathlib import Path

PROMPT = """# Write the assessment drafts

If `report.md` has a section "Questions still open", stop. Ask each question in the chat, one at a time, and wait for the answer. Append one `id: value` line to `answers.md`. Do not invent an answer. Run `pipeline-kit scan --no-bootstrap` again. Do not write rule, skill, agent, workflow, or hook files until that section is gone.

Scan wrote this report. It did not write those file bodies. You write them in chat, from the answers and the code.

Read `report.md`, `assessment.json`, and `answers.md` in this directory. Do not open `graphify-out/graph.json`. Do not add an id that is not already in `assessment.json`.

Explain, in this order: the product map, Create these, Turn these on, Not relevant, and File types without a rule.

Then write each Create these item whose `kind` is `rule`, `skill`, `agent`, `workflow`, or `hook`. Skip `agents-md`. Write the file at `proposed/` plus the item's `path`. Before writing, read the code the item names: its `folder`, its `globs`, and the symbols in `evidence`. Use `graphify query` for that folder when you need call sites. Use `answers.md` for criticality, the persona, the workflow, the eval, and the file types the user chose.

Each file must be specific to this repo. Name the types, files, and checks you actually found. A sentence that only repeats the item id is not enough.

Copy the template. Keep its headings, frontmatter keys, and attribute table. Replace the placeholder words with this repo's answers and code. Do not add a section the template does not have.

- Rule: `.pipeline/skills/repo-assessment/assets/rule.mdc` (same shape as `.pipeline/rules/security.mdc`).
- Skill: `.pipeline/skills/repo-assessment/assets/SKILL.md` (same shape as `.pipeline/skills/ask/SKILL.md`).
- Agent: `.pipeline/skills/repo-assessment/assets/agent.md` (same shape as `.pipeline/agents/ba-agent.md`).
- Workflow: `.pipeline/skills/repo-assessment/assets/workflow.json` (same shape as `.pipeline/workflows/ask.json`). List each skill from `assessment.json` under `context.parent.files` or `context.steps`.
- Hook: same shape as `.pipeline/hooks/after-file-edit.py` — shebang, module docstring, `main`. The check names behavior you found in the folder.

Leave the repo's `.cursor/`, `.pipeline/`, and root `AGENTS.md` unchanged. Tell the user the draft path. Copying is a separate yes.
"""


def _priority(item: dict) -> tuple:
    rank = {"P0": 0, "P1": 1, "P2": 2}.get(str(item.get("priority")), 9)
    kind = 0 if item.get("list") == "create" else 1
    return (rank, kind, str(item.get("id")))


def write_outputs(
    dest: Path, payload: dict, *, previous: dict | None
) -> dict[str, str]:
    dest.mkdir(parents=True, exist_ok=True)
    assessment = dest / "assessment.json"
    text = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    assessment.write_text(text, encoding="utf-8")
    report = _report(payload, previous)
    (dest / "report.md").write_text(report, encoding="utf-8")
    (dest / "plan.md").write_text(_plan(payload), encoding="utf-8")
    (dest / "prompt.md").write_text(PROMPT, encoding="utf-8")
    return {"assessment": str(assessment), "report": str(dest / "report.md")}


def _report(payload: dict, previous: dict | None) -> str:
    scores = payload["scores"]
    lines = [
        "# Assessment",
        "",
        f"Coverage of product code by an installed agent file: {scores['coverage']}%.",
        f"Projected coverage after Create these: {scores['projected']}%.",
        f"Kit fit (checklist, not a grade of the codebase): {scores['kit_fit']}%.",
        "",
        "## Questions still open",
        "",
    ]
    open_questions = payload.get("open_questions") or []
    if not open_questions:
        lines.append("- None. The kickstarter answers are on file.")
    else:
        lines.append(
            "Answer these before any rule, skill, agent, workflow, or hook is written."
        )
        for item in open_questions:
            lines.append(f"- `{item['id']}`: {item['prompt']}")
    lines.extend(["", "## Product map", ""])
    blocked = payload.get("graph", {}).get("blocked")
    if blocked:
        lines.append(
            f"Graph status: {blocked}. Create these is withheld until the graph is rebuilt."
        )
    for area in payload.get("graph", {}).get("areas") or []:
        flags = []
        if area.get("sensitive"):
            flags.append("sensitive: " + ",".join(area["sensitive"]))
        if area.get("god"):
            flags.append("has a highly connected symbol")
        if not area.get("tested"):
            flags.append("no test calls")
        extra = f" ({'; '.join(flags)})" if flags else ""
        lines.append(f"- `{area['folder']}` — {area['symbols']} symbols{extra}")
    if not payload.get("graph", {}).get("areas") and not blocked:
        lines.append("- No product areas.")
    lines.extend(
        [
            "",
            "## Create these",
            "",
            "Scan lists these files. It does not write their bodies. Follow `prompt.md` in chat to write each rule, skill, agent, workflow, and hook under `proposed/`.",
            "",
        ]
    )
    creates = [item for item in payload["items"] if item.get("list") == "create"]
    if not creates:
        lines.append("- Nothing to add beyond the kit for the areas the graph can see.")
    for item in creates:
        lines.append(f"- `{item['id']}` ({item['priority']}) `{item['path']}`")
        lines.append(f"  - Evidence: {item['evidence']}")
        lines.append(f"  - Why the kit does not cover it: {item['covered_by']}")
        lines.append(f"  - Benefit: {item['benefit']}")
    lines.extend(["", "## Turn these on", ""])
    turns = [row for row in payload["catalog"] if row.get("status") == "recommended"]
    if not turns:
        lines.append("- No shipped feature is waiting to be turned on.")
    for row in turns:
        license_note = (
            f" Needs license: {row['license_area']}." if row.get("license_area") else ""
        )
        lines.append(f"- `{row['id']}` ({row.get('priority', 'P1')}) {row['summary']}")
        lines.append(f"  - Command: {row['enable']}")
        lines.append(f"  - Benefit: {row.get('benefit')}{license_note}")
    lines.extend(["", "## Not relevant", ""])
    skipped = [row for row in payload["catalog"] if row.get("status") == "not_relevant"]
    if not skipped:
        lines.append("- None.")
    for row in skipped:
        lines.append(f"- `{row['id']}`: {row.get('reason')}")
    gap = payload.get("file_type_gap") or []
    lines.extend(["", "## File types without a rule", ""])
    if not gap:
        lines.append("- No product file type is waiting on a rule.")
    else:
        for item in gap:
            lines.append(f"- `.{item['ext']}` — {item['files']} files")
        lines.append(
            "- Answer `rule-types` with all, none, or a comma list to draft rules for these types."
        )
    unknown = payload.get("unknown") or []
    if unknown:
        lines.extend(["", "## Unknown to the graph", ""])
        for item in unknown:
            lines.append(f"- `{item['folder']}`: {item['reason']}")
    lines.extend(["", "## Since last assessment", ""])
    if not previous:
        lines.append("- This is the first assessment.")
    else:
        old_ids = {item["id"] for item in previous.get("items") or []}
        new_ids = {item["id"] for item in payload["items"]}
        lines.append(
            f"- Coverage {previous.get('scores', {}).get('coverage')}% -> {scores['coverage']}%."
        )
        gone = sorted(old_ids - new_ids)
        added = sorted(new_ids - old_ids)
        lines.append("- Resolved: " + (", ".join(gone) or "none"))
        lines.append("- New: " + (", ".join(added) or "none"))
    lines.append("")
    return "\n".join(lines)


def _plan(payload: dict) -> str:
    lines = [
        "# Plan",
        "",
        "## Phase 0",
        "",
        "- Graph: `pipeline-kit knowledge extract` or `pipeline-kit knowledge extract --update`",
        "- Copy `proposed/AGENTS.md` to the repo root, or run `pipeline-kit scan --apply agents-md`.",
        "",
        "## Phase 1",
        "",
    ]
    creates = [item for item in payload["items"] if item.get("list") == "create"]
    if not creates:
        lines.append("- No custom files.")
    for item in creates:
        lines.append(
            f"- Write `{item['path']}` ({item['id']}) from `prompt.md`, using the answers and the code that item names."
        )
    lines.extend(["", "## Phase 2", ""])
    for row in payload["catalog"]:
        if row.get("status") == "recommended":
            lines.append(f"- {row['enable']} ({row['id']})")
    if not any(row.get("status") == "recommended" for row in payload["catalog"]):
        lines.append("- No kit features to turn on.")
    lines.append("")
    return "\n".join(lines)


def order_items(items: list[dict]) -> list[dict]:
    return sorted(items, key=_priority)
