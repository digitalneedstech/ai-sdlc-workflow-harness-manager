"""pipeline-kit eval subcommands."""

from __future__ import annotations

import json
from pathlib import Path

from pipeline_eval.judges import JUDGES, sync_judges


def cmd_judges_sync(project: Path) -> int:
    result = sync_judges(project)
    print(json.dumps({key: value for key, value in result.items() if key != "judges_dir"}, indent=2))
    if not result.get("ok"):
        return 1
    print()
    print("Score configs synced. LLM-as-judge evaluators need an LLM connection that")
    print("only you can add — finish in the Langfuse UI (observation-level, not trace):")
    print("  1. Project Settings -> LLM Connections: add a key and pin one judge model.")
    print(f"  2. Evaluators -> New: paste a prompt from {result.get('judges_dir')}")
    print("     mapping {{input}} / {{output}} to the observation input/output.")
    print("  3. Rule target = observation NAME filter, e.g.:")
    for judge in JUDGES:
        print(f"       {judge['name']:28s} -> {judge['target']}")
    print("  4. Sampling: 100% on golden runs, ~10% on live traffic.")
    return 0
