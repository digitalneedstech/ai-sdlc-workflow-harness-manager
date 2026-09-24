"""pipeline-kit scan. No model call. Same repo, graph, and answers produce the same assessment.json."""

from __future__ import annotations

import json
import sys
from datetime import UTC, datetime
from pathlib import Path

from pipeline_plugins.graphify import graphify_status

from pipeline_assess import COMPATIBLE_KIT
from pipeline_assess.agents_md import write_agents
from pipeline_assess.apply import ApplyError, apply_ids
from pipeline_assess.bootstrap import prepare
from pipeline_assess.catalog import match_catalog
from pipeline_assess.gaps import create_items, uncovered_file_types
from pipeline_assess.graph_model import GraphModelError, analyze
from pipeline_assess.inventory import collect_inventory
from pipeline_assess.render import order_items, write_outputs
from pipeline_assess.rules import (
    apply_priority,
    collect_answers,
    coverage_scores,
    kit_fit,
    read_answers,
    write_answers,
)
from pipeline_assess.signals import collect_signals


def _kit_version() -> str:
    try:
        from pipeline_kit import __version__ as version
    except ImportError:
        version = ""
    if not version:
        path = Path(__file__).resolve().parents[3] / "VERSION"
        if path.is_file():
            version = path.read_text(encoding="utf-8").strip()
    return version


def cmd_scan(
    project: Path,
    *,
    out: Path | None = None,
    yes: bool = False,
    no_bootstrap: bool = False,
    as_json: bool = False,
    apply: str = "",
    dry_run: bool = False,
    tty: bool | None = None,
    input_fn=None,
    installer=None,
) -> int:
    project = project.expanduser().resolve()
    if not project.is_dir():
        print(f"not a directory: {project}", file=sys.stderr)
        return 64
    version = _kit_version()
    if version and not version.startswith(COMPATIBLE_KIT):
        print(
            f"pipeline-kit {version} does not match pipeline-kit-assess {COMPATIBLE_KIT}. "
            'Run: uv tool install -e ".[assess]"',
            file=sys.stderr,
        )
        return 1
    dest = out if out is not None else project / "features" / "assessment"
    if not dest.is_absolute():
        dest = project / dest
    if apply.strip():
        try:
            notes = apply_ids(
                project,
                dest,
                [part.strip() for part in apply.split(",") if part.strip()],
                dry_run=dry_run,
            )
        except (
            ApplyError,
            OSError,
            json.JSONDecodeError,
            FileNotFoundError,
            ValueError,
        ) as exc:
            print(str(exc), file=sys.stderr)
            return 1
        for note in notes:
            print(note)
        _append_history(dest, apply, dry_run)
        return 0
    is_tty = sys.stdin.isatty() if tty is None else tty
    reader = input_fn or input
    code = prepare(
        project,
        yes=yes,
        no_bootstrap=no_bootstrap,
        tty=is_tty,
        input_fn=reader,
        installer=installer,
    )
    if code != 0:
        return code
    try:
        model = analyze(project, graphify_version=graphify_status().get("version"))
    except GraphModelError as exc:
        print(str(exc), file=sys.stderr)
        if exc.recovery:
            print(exc.recovery, file=sys.stderr)
        return 1
    inventory = collect_inventory(project)
    signals = collect_signals(project)
    answers_path = dest / "answers.md"
    file_type_gap = uncovered_file_types(model, inventory)
    answers, open_questions = collect_answers(
        read_answers(answers_path),
        file_types=file_type_gap,
        tty=is_tty,
        input_fn=reader,
    )
    if answers:
        write_answers(answers_path, answers)
    items, unknown = create_items(model, inventory, signals, answers)
    catalog = match_catalog(inventory, signals, answers)
    apply_priority(items, catalog, answers)
    items = order_items(items)
    scores = coverage_scores(model, items, inventory)
    scores["kit_fit"] = kit_fit(catalog, inventory, model)
    previous = _previous(dest / "assessment.json")
    payload = _payload(
        answers=answers,
        catalog=catalog,
        model=model,
        file_type_gap=file_type_gap,
        open_questions=open_questions,
        items=items,
        scores=scores,
        unknown=unknown,
    )
    write_outputs(dest, payload, previous=previous)
    write_agents(project, dest, signals, model, inventory, items, answers)
    agents = {
        "id": "agents-md",
        "list": "create",
        "priority": "P0",
        "path": "AGENTS.md",
        "folder": ".",
        "evidence": "Every coding agent reads AGENTS.md first.",
        "benefit": "Later sessions start from this repo's map, commands, and guardrails.",
        "covered_by": "installed" if inventory.get("has_agents_md") else "none",
        "sensitive": False,
    }
    payload["items"] = [agents, *items]
    write_outputs(dest, payload, previous=previous)
    print(f"coverage: {scores['coverage']}%")
    print(f"projected: {scores['projected']}%")
    print(f"kit fit: {scores['kit_fit']}%")
    for item in payload["items"][:5]:
        print(f"{item['priority']} {item['id']} {item['path']}")
    print(f"report: {dest / 'report.md'}")
    if as_json:
        print((dest / "assessment.json").read_text(encoding="utf-8"), end="")
    return 0


_CATALOG_FIELDS = (
    "benefit",
    "enable",
    "id",
    "license_area",
    "priority",
    "reason",
    "status",
    "summary",
)


def _payload(
    *,
    answers: dict,
    catalog: list[dict],
    model: dict,
    file_type_gap: list,
    open_questions: list,
    items: list[dict],
    scores: dict,
    unknown: list,
) -> dict:
    public_catalog = []
    for row in catalog:
        public = {field: row.get(field) for field in _CATALOG_FIELDS}
        public["license_area"] = row.get("license_area") or ""
        public["priority"] = row.get("priority", "")
        public["reason"] = row.get("reason") or ""
        public_catalog.append(public)
    return {
        "answers": answers,
        "catalog": public_catalog,
        "graph": {
            "areas": model.get("areas") or [],
            "blind": model.get("blind") or [],
            "blocked": model.get("blocked"),
            "coupling": model.get("coupling") or [],
            "freshness": model.get("freshness"),
            "gods": model.get("gods") or [],
            "pack_nodes": model.get("pack_nodes"),
            "product_nodes": model.get("product_nodes"),
        },
        "file_type_gap": file_type_gap,
        "open_questions": open_questions,
        "items": items,
        "scores": scores,
        "unknown": unknown,
        "version": 1,
    }


def _previous(path: Path) -> dict | None:
    if not path.is_file():
        return None
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    return data if isinstance(data, dict) else None


def _append_history(dest: Path, apply: str, dry_run: bool) -> None:
    path = dest / "assessment-run.json"
    try:
        data = json.loads(path.read_text(encoding="utf-8")) if path.is_file() else {}
    except (OSError, json.JSONDecodeError):
        data = {}
    if not isinstance(data, dict):
        data = {}
    history = data.get("apply") if isinstance(data.get("apply"), list) else []
    history.append(
        {
            "ids": apply,
            "dry_run": dry_run,
            "at": datetime.now(UTC).strftime("%Y-%m-%dT%H:%M:%SZ"),
        }
    )
    data["apply"] = history
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")
