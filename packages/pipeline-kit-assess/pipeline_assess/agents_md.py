"""Proposed AGENTS.md from scan evidence. Commands come only from manifests."""

from __future__ import annotations

from pathlib import Path

START = "<!-- pipeline-kit:assessment start -->"
END = "<!-- pipeline-kit:assessment end -->"


def _section(
    signals: dict,
    model: dict,
    inventory: dict,
    items: list[dict],
    answers: dict[str, str],
) -> str:
    lines = [
        START,
        "",
        f"# {signals.get('name') or 'Project'}",
        "",
        "## Project",
        "",
        "Languages: "
        + (
            ", ".join(signals.get("languages") or [])
            or "not declared in a root manifest"
        ),
        "",
        "## Commands",
        "",
    ]
    commands = signals.get("commands") or {}
    if commands:
        for key in sorted(commands):
            lines.append(f"- {key}: `{commands[key]}`")
    else:
        lines.append(
            "- No install, build, test, or lint command was declared in a root manifest."
        )
    lines.extend(["", "## Code map", ""])
    if model.get("blocked"):
        lines.append(
            f"The graph is {model.get('blocked')}. Rebuild it before trusting this map."
        )
    elif not model.get("areas"):
        lines.append("No product areas were found in the graph.")
    else:
        for area in model.get("areas") or []:
            role = ", ".join(area.get("labels") or []) or "product code"
            tested = "tests reach it" if area.get("tested") else "no test calls found"
            lines.append(
                f"- `{area['folder']}` ({area['symbols']} symbols, {tested}): {role}"
            )
    lines.extend(["", "## Handle with care", ""])
    careful = [
        item
        for item in items
        if item.get("sensitive") or str(item.get("folder", "")).startswith("boundary-")
    ]
    if careful:
        for item in careful:
            lines.append(
                f"- `{item['folder']}`: {item['benefit']} File: `{item['path']}`."
            )
    else:
        lines.append("- No sensitive area or heavy cross-area coupling was found.")
    lines.extend(["", "## Blind spots", ""])
    blind = model.get("blind") or []
    if blind:
        lines.append(
            "Graphify does not index these folders' file types: "
            + ", ".join(f"`{name}`" for name in blind)
            + "."
        )
    else:
        lines.append(
            "No unindexed HTML, YAML, SQL, Docker, or Terraform folders were found."
        )
    lines.extend(
        [
            "",
            "## Using pipeline-kit here",
            "",
            f"Install mode: {inventory.get('mode')}.",
            "Workflows: " + (", ".join(inventory.get("workflows") or []) or "none"),
            "Start from the installed workflow that matches the task. Custom files from this scan belong under the paths in `features/assessment/proposed/`.",
            "",
            "## Using the graph",
            "",
            '- `graphify query "<area>" --budget 1500`',
            '- `graphify path "<symbol>" "<symbol>"`',
            '- `graphify affected "<symbol>"`',
            "- Refresh: `pipeline-kit knowledge extract --update`",
            "",
            "## Guardrails",
            "",
        ]
    )
    if answers.get("data") == "regulated":
        lines.append(
            "- Data is regulated. Do not put real data in fixtures. Run a security review before merge."
        )
    if answers.get("impact") == "customers":
        lines.append(
            "- A bad change reaches customers. Cover the most-connected code with tests before shipping."
        )
    if answers.get("cadence") == "continuously":
        lines.append(
            "- This repo ships continuously. Keep the graph hook installed and review CI changes."
        )
    if answers.get("teams") == "many":
        lines.append(
            "- Several teams own this repo. Keep AGENTS.md and boundary rules as the shared contract."
        )
    if not any(answers.get(key) for key in ("data", "impact", "cadence", "teams")):
        lines.append(
            "- Criticality answers were not provided. Re-run scan in a terminal to record them."
        )
    lines.extend(["", END, ""])
    return "\n".join(lines)


def write_agents(
    project: Path,
    dest: Path,
    signals: dict,
    model: dict,
    inventory: dict,
    items: list[dict],
    answers: dict[str, str],
) -> list[str]:
    body = _section(signals, model, inventory, items, answers)
    proposed = dest / "proposed"
    proposed.mkdir(parents=True, exist_ok=True)
    written = []
    full = proposed / "AGENTS.md"
    existing = project / "AGENTS.md"
    if existing.is_file():
        try:
            current = existing.read_text(encoding="utf-8")
        except OSError:
            current = ""
        full.write_text(current.rstrip() + "\n\n" + body, encoding="utf-8")
        (proposed / "AGENTS.section.md").write_text(body, encoding="utf-8")
        written.extend(["proposed/AGENTS.md", "proposed/AGENTS.section.md"])
    else:
        full.write_text("# Agent guide\n\n" + body, encoding="utf-8")
        written.append("proposed/AGENTS.md")
    if inventory.get("has_claude") and not inventory.get("has_claude_md"):
        (proposed / "CLAUDE.md").write_text("@AGENTS.md\n", encoding="utf-8")
        written.append("proposed/CLAUDE.md")
    return written


def apply_agents(project: Path, proposal: Path, *, dry_run: bool) -> str:
    if not proposal.is_file():
        raise FileNotFoundError(proposal)
    text = proposal.read_text(encoding="utf-8")
    start = text.find(START)
    end = text.find(END)
    if start < 0 or end < 0:
        raise ValueError("proposal has no assessment markers")
    section = text[start : end + len(END)] + "\n"
    target = project / "AGENTS.md"
    if not target.is_file():
        new = text if text.startswith("#") else "# Agent guide\n\n" + section
        if dry_run:
            return new
        target.write_text(new, encoding="utf-8")
        return new
    current = target.read_text(encoding="utf-8")
    if START in current and END in current:
        pre, _, rest = current.partition(START)
        _, _, post = rest.partition(END)
        merged = pre.rstrip() + "\n\n" + section + post.lstrip("\n")
    else:
        merged = current.rstrip() + "\n\n" + section
    if dry_run:
        return merged
    target.write_text(
        merged if merged.endswith("\n") else merged + "\n", encoding="utf-8"
    )
    return merged
