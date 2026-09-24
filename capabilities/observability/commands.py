"""pipeline-kit obs subcommands."""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from typing import Any

from pipeline_observability.export import flush_project, load_dotenv, load_obs_config
from pipeline_observability.hooks_merge import MergeError, install_hooks, uninstall_hooks
from pipeline_observability.scoring import score_ledger

DEFAULT_OBS = {
    "_note": "Opt-in agent-run observability. Distinct from telemetry-agent. Secrets stay in the environment.",
    "enabled": False,
    "adapter": "langfuse",
    "sample_rate": 1.0,
    "redact": [".env", "*secret*", "*credential*"],
    "max_field_chars": 8000,
    "flush_on": ["subagentStop", "sessionEnd"],
    "dataset": "pipeline-kit-agent-runs",
    "retention_days": 14,
}


def _pack(project: Path) -> Path:
    return project / ".pipeline"


def _set_enabled(project: Path, on: bool, adapter: str | None = None) -> None:
    path = _pack(project) / "config.json"
    if not path.is_file():
        raise MergeError("no .pipeline/config.json — run pipeline-kit init first")
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise MergeError("config.json must be an object")
    block = data.get("agent_observability")
    if not isinstance(block, dict):
        block = dict(DEFAULT_OBS)
    block["enabled"] = on
    if adapter:
        block["adapter"] = adapter
    data["agent_observability"] = block
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def cmd_install(project: Path, *, ide: str, adapter: str, version: str) -> int:
    pack = _pack(project)
    if not pack.is_dir():
        print("no .pipeline — run pipeline-kit init first", file=sys.stderr)
        return 64
    try:
        added = install_hooks(project, pack, ide=ide, version=version)
        _set_enabled(project, True, adapter=adapter)
    except (MergeError, OSError, json.JSONDecodeError) as exc:
        print(str(exc), file=sys.stderr)
        return 64
    print(f"obs hooks merged ({added} new entries) ide={ide} adapter={adapter}")
    print("Existing hook entries were left in place.")
    print("Keys stay in LANGFUSE_PUBLIC_KEY / LANGFUSE_SECRET_KEY / LANGFUSE_BASE_URL.")
    return 0


def cmd_uninstall(project: Path, *, ide: str) -> int:
    try:
        uninstall_hooks(project, ide)
        if (_pack(project) / "config.json").is_file():
            _set_enabled(project, False)
    except (MergeError, OSError, json.JSONDecodeError) as exc:
        print(str(exc), file=sys.stderr)
        return 64
    print("obs hooks removed; ledger left in .pipeline/state/obs/")
    return 0


def cmd_status(project: Path) -> int:
    cfg = load_obs_config(project)
    enabled = cfg.get("enabled") is True
    adapter = cfg.get("adapter") or "langfuse"
    ledger = project / ".pipeline" / "state" / "obs" / "events.jsonl"
    size = ledger.stat().st_size if ledger.is_file() else 0
    load_dotenv(project)
    keys = "yes" if os.environ.get("LANGFUSE_PUBLIC_KEY") and os.environ.get("LANGFUSE_SECRET_KEY") else "no"
    print(f"enabled\t{enabled}")
    print(f"adapter\t{adapter}")
    print(f"ledger_bytes\t{size}")
    print(f"langfuse_keys\t{keys}")
    print("cost\thooks never send dollars; flush prices generations from model + tokens")
    return 0


def cmd_flush(project: Path) -> int:
    result = flush_project(project)
    print(json.dumps(result, indent=2))
    return 0 if result.get("ok") else 1


def cmd_report(project: Path) -> int:
    ledger = project / ".pipeline" / "state" / "obs" / "events.jsonl"
    if not ledger.is_file():
        print("no ledger yet — run a pipeline with obs enabled", file=sys.stderr)
        return 1
    report = score_ledger(project, ledger)
    slim = {
        "event_count": report.get("event_count"),
        "cost_note": report.get("cost_note"),
        "steps": [
            {key: value for key, value in step.items() if key != "events"}
            for step in report.get("steps") or []
        ],
    }
    print(json.dumps(slim, indent=2))
    return 0


def obs_doctor_checks(root: Path) -> tuple[list[str], dict[str, bool]]:
    """`root` is either a project directory or a resolved pack (`.pipeline`)."""
    info: list[str] = []
    required: dict[str, bool] = {}
    pack = root if (root / "hooks" / "obs").is_dir() else root / ".pipeline"
    collect = pack / "hooks" / "obs" / "obs_collect.py"
    required["obs collector"] = collect.is_file()
    project = root if (root / ".pipeline").is_dir() else root.parent
    cfg = load_obs_config(project) if (project / ".pipeline" / "config.json").is_file() else {}
    if not cfg and (pack / "config.json").is_file():
        try:
            data = json.loads((pack / "config.json").read_text(encoding="utf-8"))
            cfg = data.get("agent_observability") if isinstance(data, dict) else {}
            cfg = cfg if isinstance(cfg, dict) else {}
        except (OSError, json.JSONDecodeError):
            cfg = {}
    if cfg.get("enabled") is True:
        info.append("agent_observability.enabled is true")
        info.append("hooks do not report dollar cost; flush prices generations from model + tokens")
        hooks = project / ".cursor" / "hooks.json"
        if hooks.is_file():
            required["obs cursor hook merge"] = "obs_collect.py" in hooks.read_text(encoding="utf-8")
    else:
        info.append("agent_observability is off (pipeline-kit obs install)")
    return info, required
