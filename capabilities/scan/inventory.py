"""Directory listing of the agent surface already installed. Does not walk app source."""

from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from pathlib import Path

_NAME = re.compile(r"^name:\s*[\"']?([^\"'\n]+)", re.MULTILINE)


def _read_mode(pack: Path) -> str:
    marker = pack / "install.json"
    if not marker.is_file():
        return "kit"
    try:
        data = json.loads(marker.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return "kit"
    if isinstance(data, dict):
        return str(data.get("mode") or "kit")
    return "kit"


class InventoryError(RuntimeError):
    """The installed pack could not be listed."""


@dataclass
class Surface:
    mode: str
    workflows: list[str] = field(default_factory=list)
    skills: list[str] = field(default_factory=list)
    subagents: list[str] = field(default_factory=list)
    rules: list[str] = field(default_factory=list)
    hooks: list[str] = field(default_factory=list)
    flags: list[str] = field(default_factory=list)

    def as_markdown(self) -> str:
        return "\n".join(
            [
                f"Install mode: {self.mode}",
                "",
                _section("Workflows", self.workflows),
                _section("Skills", self.skills),
                _section("Sub-agents", self.subagents),
                _section("Rules", self.rules),
                _section("Hooks", self.hooks),
                _section("Flags", self.flags),
            ]
        ).rstrip() + "\n"


def _section(title: str, items: list[str]) -> str:
    body = "\n".join(f"- {item}" for item in items) if items else "- (none)"
    return f"## {title}\n{body}\n"


def _skill_name(path: Path) -> str:
    try:
        head = path.read_text(encoding="utf-8")[:4000]
    except OSError:
        return path.parent.name
    match = _NAME.search(head)
    if match:
        return match.group(1).strip()
    return path.parent.name


def _names_under(root: Path, pattern: str) -> list[str]:
    if not root.is_dir():
        return []
    found: list[str] = []
    for path in sorted(root.glob(pattern)):
        if path.is_file() and path.name != ".gitkeep":
            found.append(path.name)
    return found


def _workflow_names(project: Path, pack: Path, mode: str) -> list[str]:
    if mode == "orchestrator":
        from pipeline_orchestrator.registry import list_specs

        try:
            return [spec.name for spec in list_specs(project)]
        except Exception as exc:
            raise InventoryError(f"could not list orchestrator workflows: {exc}") from exc
    names: list[str] = []
    workflows = pack / "workflows"
    if not workflows.is_dir():
        return names
    for path in sorted(workflows.glob("*.json")):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            names.append(path.stem)
            continue
        if isinstance(data, dict) and isinstance(data.get("name"), str) and data["name"].strip():
            names.append(data["name"].strip())
        else:
            names.append(path.stem)
    return names


def _flag_lines(pack: Path) -> list[str]:
    path = pack / "config.json"
    if not path.is_file():
        return []
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return []
    if not isinstance(data, dict):
        return []
    design = data.get("test_design") if isinstance(data.get("test_design"), dict) else {}
    diagrams = data.get("architecture_diagrams") if isinstance(data.get("architecture_diagrams"), dict) else {}
    obs = data.get("agent_observability") if isinstance(data.get("agent_observability"), dict) else {}
    intake = data.get("intake") if isinstance(data.get("intake"), dict) else {}
    jira = intake.get("jira") if isinstance(intake.get("jira"), dict) else {}
    rows = (
        ("test-design", bool(design.get("enabled"))),
        ("playwright", bool(design.get("playwright"))),
        ("archify", bool(diagrams.get("enabled"))),
        ("agent-observability", bool(obs.get("enabled"))),
        ("jira-intake", bool(jira.get("enabled"))),
    )
    return [f"{name}: {'on' if on else 'off'}" for name, on in rows]


def collect_surface(project: Path, pack: Path) -> Surface:
    mode = _read_mode(pack)
    skills: list[str] = []
    skill_root = pack / "skills"
    if skill_root.is_dir():
        for path in sorted(skill_root.glob("*/SKILL.md")):
            skills.append(_skill_name(path))
    agents_dir = pack / "agents"
    agents = [path.stem for path in sorted(agents_dir.glob("*.md"))] if agents_dir.is_dir() else []
    rules: list[str] = []
    for folder in (
        project / ".cursor" / "rules",
        project / ".claude" / "rules",
        pack / "rules",
    ):
        rules.extend(_names_under(folder, "*"))
    hooks = _names_under(pack / "hooks", "*")
    for ide_hooks in (
        project / ".cursor" / "hooks.json",
        project / ".claude" / "settings.json",
    ):
        if ide_hooks.is_file():
            hooks.append(str(ide_hooks.relative_to(project)))
    return Surface(
        mode=mode,
        workflows=_workflow_names(project, pack, mode),
        skills=skills,
        subagents=agents,
        rules=rules,
        hooks=hooks,
        flags=_flag_lines(pack),
    )
