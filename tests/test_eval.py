"""Eval harness: eval-ready spans, Starter 7 run-level scores, judge sync, stub-adapter skip."""

from __future__ import annotations

import json
import runpy
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
INSTALL = REPO / "install.py"


def _run_cli(argv: list[str]) -> int:
    ns = runpy.run_path(str(INSTALL))
    return int(ns["cli_main"](argv))


def _init(app: Path) -> None:
    assert _run_cli(["init", str(app), "--ide", "none"]) == 0


CONV = "cf794227-f288-418e-897e-c17d21b91d66"


def _rows() -> list[dict]:
    return [
        {
            "ts": "2026-09-18T10:00:00.000Z",
            "kind": "hook",
            "event": "beforeSubmitPrompt",
            "harness": "cursor",
            "payload": {
                "hook_event_name": "beforeSubmitPrompt",
                "conversation_id": CONV,
                "prompt": "add a badge to the header",
                "user_email": "dev@example.com",
            },
        },
        {
            "ts": "2026-09-18T10:00:01.000Z",
            "kind": "step_context",
            "event": "subagentStart",
            "harness": "cursor",
            "payload": {
                "hook_event_name": "subagentStart",
                "conversation_id": CONV,
                "subagent_id": "s1",
                "task": "implement the badge per patch.md",
            },
            "step_context": {
                "workflow": "feature-development",
                "step": "developer-agent",
                "slug": "demo",
                "allowed_reads": [
                    ".pipeline/agents/developer-agent.md",
                    ".pipeline/skills/secure-implementation/SKILL.md",
                ],
            },
        },
        {
            "ts": "2026-09-18T10:00:02.000Z",
            "kind": "hook",
            "event": "postToolUse",
            "harness": "cursor",
            "payload": {
                "hook_event_name": "postToolUse",
                "conversation_id": CONV,
                "subagent_id": "s1",
                "tool_name": "Read",
                "tool_input": {"path": ".pipeline/agents/developer-agent.md"},
                "duration": 4,
            },
        },
        {
            "ts": "2026-09-18T10:00:03.000Z",
            "kind": "hook",
            "event": "stop",
            "harness": "cursor",
            "payload": {
                "hook_event_name": "stop",
                "conversation_id": CONV,
                "subagent_id": "s1",
                "status": "completed",
            },
        },
    ]


def _write_artifacts(app: Path) -> None:
    root = app / "features" / "demo"
    root.mkdir(parents=True)
    (root / "route.md").write_text("change_class: micro\n", encoding="utf-8")
    for step in ("developer", "tester", "devops", "retro"):
        (root / f"HANDOFF-{step}.md").write_text(
            f"# HANDOFF {step}\nSUCCESS\nDid the {step} work.\n", encoding="utf-8"
        )
    (root / "deploy-result.env").write_text("OVERALL=passed\n", encoding="utf-8")
    (root / "notes.md").write_text("leaked sk-lf-SUPERSECRETVALUE12 oops\n", encoding="utf-8")


def _build(app: Path, rows: list[dict]):
    sys.path.insert(0, str(REPO))
    from pipeline_observability.adapters.base import AdapterConfig
    from pipeline_observability.adapters.langfuse import LangfuseAdapter
    from pipeline_observability.export import build_otlp
    from pipeline_observability.scoring import score_events

    report = score_events(app, rows)
    adapter = LangfuseAdapter(AdapterConfig(name="langfuse", host="https://cloud.langfuse.com"))
    return build_otlp(report, adapter)


def _attrs(span: dict) -> dict:
    return {item["key"]: item["value"] for item in span["attributes"]}


def test_eval_ready_spans_and_starter7_scores(tmp_path: Path):
    app = tmp_path / "app"
    app.mkdir()
    _init(app)
    _write_artifacts(app)
    payload, scores, datasets = _build(app, _rows())
    spans = payload["resourceSpans"][0]["scopeSpans"][0]["spans"]

    root = spans[0]
    root_attrs = _attrs(root)
    assert root_attrs["langfuse.session.id"]["stringValue"] == "feature-development:demo"
    tags = [v["stringValue"] for v in root_attrs["langfuse.trace.tags"]["arrayValue"]["values"]]
    assert "pack_id=pipeline-kit" in tags
    assert "developer-agent" in tags
    marker = json.loads((app / ".pipeline" / "install.json").read_text(encoding="utf-8"))
    installed = str(marker["version"])
    assert f"kit_version={installed}" in tags
    assert root_attrs["pipeline.kit_version"]["stringValue"] == installed
    assert root_attrs["langfuse.trace.metadata.kit_version"]["stringValue"] == installed
    resource = payload["resourceSpans"][0]["resource"]["attributes"]
    resource_by_key = {item["key"]: item["value"] for item in resource}
    assert resource_by_key["service.version"]["stringValue"] == installed
    assert resource_by_key["pipeline.kit_version"]["stringValue"] == installed
    assert payload["resourceSpans"][0]["scopeSpans"][0]["scope"]["version"] == installed
    expected = [
        v["stringValue"]
        for v in root_attrs["langfuse.trace.metadata.steps_expected"]["arrayValue"]["values"]
    ]
    assert expected == ["developer-agent", "tester-agent", "devops-agent", "retro-agent"]

    step_span = next(s for s in spans if s["name"] == "pipeline.step developer-agent")
    step_attrs = _attrs(step_span)
    output = json.loads(step_attrs["langfuse.observation.output"]["stringValue"])
    assert "SUCCESS" in (output["handoff"] or "")
    assert output["status"] == "completed"
    skills = [
        v["stringValue"]
        for v in step_attrs["langfuse.observation.metadata.pipeline.skills"]["arrayValue"]["values"]
    ]
    assert "secure-implementation" in skills
    assert step_attrs["langfuse.observation.metadata.subagent_name"]["stringValue"] == "developer-agent"
    assert step_attrs["pipeline.kit_version"]["stringValue"] == installed

    by_name = {item["name"]: item for item in scores}
    assert by_name["tool_calls_total"]["value"] >= 1  # existing Layer C intact
    assert by_name["step_success"]["value"] == 1.0
    assert by_name["step_success"]["observationId"] == step_span["spanId"]
    assert by_name["task_complete"]["value"] == 1.0
    assert by_name["task_complete"]["dataType"] == "BOOLEAN"
    assert by_name["task_complete"]["observationId"] == root["spanId"]
    assert by_name["hitl_count"]["value"] == 0.0
    assert by_name["critic_retry_count"]["value"] == 0.0
    assert by_name["secret_leak_count"]["value"] == 1.0
    assert datasets[0]["session_id"] == "feature-development:demo"
    assert datasets[0]["kit_version"] == installed

    # Deterministic ids: a second build (double flush) yields identical score ids.
    _payload2, scores2, _d2 = _build(app, _rows())
    assert sorted(item["id"] for item in scores) == sorted(item["id"] for item in scores2)


def test_kit_version_resolution(tmp_path: Path, monkeypatch):
    sys.path.insert(0, str(REPO))
    from pipeline_observability.export import kit_version

    monkeypatch.delenv("PIPELINE_KIT_VERSION", raising=False)
    assert kit_version(tmp_path) == "unknown"
    (tmp_path / ".pipeline").mkdir()
    (tmp_path / ".pipeline" / "install.json").write_text(
        json.dumps({"name": "pipeline-kit", "version": "9.9.9"}),
        encoding="utf-8",
    )
    assert kit_version(tmp_path) == "9.9.9"
    monkeypatch.setenv("PIPELINE_KIT_VERSION", "env-override")
    assert kit_version(tmp_path) == "env-override"


def test_missing_handoff_fails_open(tmp_path: Path):
    app = tmp_path / "app"
    app.mkdir()
    _init(app)
    # No features/demo artifacts at all.
    payload, scores, _datasets = _build(app, _rows())
    spans = payload["resourceSpans"][0]["scopeSpans"][0]["spans"]
    step_span = next(s for s in spans if s["name"] == "pipeline.step developer-agent")
    # Output stays the plain status (previous behavior) when no artifacts exist.
    assert _attrs(step_span)["langfuse.observation.output"]["stringValue"] == "completed"
    by_name = {item["name"]: item for item in scores}
    assert by_name["step_success"]["value"] == 0.0
    assert by_name["task_complete"]["value"] == 0.0
    assert "secret_leak_count" not in by_name  # N/A stays N/A, never 0


def test_flush_stub_adapter_skips_and_keeps_offset(tmp_path: Path):
    sys.path.insert(0, str(REPO))
    from pipeline_observability.export import flush_project, read_offset

    app = tmp_path / "app"
    app.mkdir()
    _init(app)
    cfg_path = app / ".pipeline" / "config.json"
    cfg = json.loads(cfg_path.read_text(encoding="utf-8"))
    cfg["agent_observability"] = {"enabled": True, "adapter": "otlp"}
    cfg_path.write_text(json.dumps(cfg, indent=2) + "\n", encoding="utf-8")
    ledger = app / ".pipeline" / "state" / "obs" / "events.jsonl"
    ledger.parent.mkdir(parents=True)
    ledger.write_text(json.dumps(_rows()[0]) + "\n", encoding="utf-8")
    result = flush_project(app)
    assert result["ok"] is True
    assert "otlp" in result["skipped"]
    assert read_offset(app) == 0  # re-flush after switching adapters ships the same rows


def test_eval_judges_sync_posts_score_configs(tmp_path: Path, monkeypatch):
    sys.path.insert(0, str(REPO))
    from pipeline_observability.adapters import langfuse as lf
    from pipeline_eval.judges import sync_judges

    app = tmp_path / "app"
    app.mkdir()
    _init(app)
    monkeypatch.setenv("LANGFUSE_PUBLIC_KEY", "pk-lf-test")
    monkeypatch.setenv("LANGFUSE_SECRET_KEY", "sk-lf-test")
    posted: list[dict] = []

    def fake_post(url, payload, headers, retries=3):
        posted.append({"url": url, "payload": payload})
        return True, "ok", 200

    monkeypatch.setattr(lf, "post_json", fake_post)
    result = sync_judges(app)
    assert result["ok"] is True
    names = {item["payload"]["name"] for item in posted}
    assert {"spec_completeness", "safety_hygiene", "task_complete", "tool_calls_total"} <= names
    assert all("/api/public/score-configs" in item["url"] for item in posted)
    assert Path(result["judges_dir"]).is_dir()


def test_init_copies_judge_prompts(tmp_path: Path):
    app = tmp_path / "app"
    app.mkdir()
    _init(app)
    judges = app / ".pipeline" / "eval" / "judges"
    assert (judges / "spec_completeness.md").is_file()
    assert (judges / "safety_hygiene.md").is_file()
