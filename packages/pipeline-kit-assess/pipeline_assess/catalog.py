"""Shipped kit features. New plugins are new entries, not scanner changes."""

from __future__ import annotations

import json
from pathlib import Path

CATALOG_PATH = Path(__file__).resolve().parent / "catalog.json"
DENY = frozenset(
    {
        "feature-development",
        "playwright",
        "test-design",
        "secure-implementation",
        "security-review",
        "ci-audit",
        "dependency-audit",
        "accessibility-review",
    }
)


def load_catalog() -> list[dict]:
    data = json.loads(CATALOG_PATH.read_text(encoding="utf-8"))
    items = data.get("items") if isinstance(data, dict) else None
    if not isinstance(items, list):
        return []
    return [item for item in items if isinstance(item, dict) and item.get("id")]


def _relevant(item: dict, signals: dict, answers: dict) -> str:
    cond = str(item.get("relevant_when") or "always")
    if cond == "always":
        return "yes"
    if cond == "jira":
        value = answers.get("jira", signals.get("jira", "unknown"))
        if value == "yes":
            return "yes"
        if value == "no":
            return "no"
        return "unknown"
    return "yes" if signals.get(cond) else "no"


def _enabled(item: dict, inventory: dict) -> bool:
    check = str(item.get("enabled_when") or "")
    if check == "always":
        return True
    kind, _, name = check.partition(":")
    if kind == "workflow":
        return name in inventory.get("workflows", [])
    if kind == "flag":
        return bool(inventory.get("flags", {}).get(name))
    if kind == "extension":
        return name in inventory.get("extensions", [])
    if kind == "config" and name == "verify":
        return int(inventory.get("verify_rules") or 0) > 0
    if kind == "config" and name == "deploy":
        return not inventory.get("deploy_auto", True)
    return False


def match_catalog(inventory: dict, signals: dict, answers: dict) -> list[dict]:
    mode = inventory.get("mode") or "kit"
    rows = []
    for item in load_catalog():
        modes = item.get("modes") or ["kit", "orchestrator"]
        if mode not in modes:
            rows.append(
                {**item, "status": "not_relevant", "reason": f"install mode is {mode}"}
            )
            continue
        relevant = _relevant(item, signals, answers)
        if relevant == "no":
            rows.append(
                {
                    **item,
                    "status": "not_relevant",
                    "reason": f"{item.get('relevant_when')} is not present",
                }
            )
            continue
        if relevant == "unknown":
            rows.append(
                {**item, "status": "unknown", "reason": "jira use is not confirmed"}
            )
            continue
        if _enabled(item, inventory):
            rows.append({**item, "status": "in_use", "reason": ""})
            continue
        rows.append({**item, "status": "recommended", "reason": ""})
    return rows


def shipped_ids() -> set[str]:
    return {str(item["id"]) for item in load_catalog()}
