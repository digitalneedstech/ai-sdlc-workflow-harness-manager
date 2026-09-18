"""Agent-observability install, merge safety, scoring, and collector fail-open."""

from __future__ import annotations

import json
import runpy
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
INSTALL = REPO / "install.py"


def _run_cli(argv: list[str]) -> int:
    ns = runpy.run_path(str(INSTALL))
    return int(ns["cli_main"](argv))


def _init(app: Path) -> None:
    assert _run_cli(["init", str(app), "--ide", "none"]) == 0


def test_init_copies_obs_scripts_and_config(tmp_path: Path):
    app = tmp_path / "app"
    app.mkdir()
    _init(app)
    assert (app / ".pipeline" / "hooks" / "obs" / "obs_collect.py").is_file()
    cfg = json.loads((app / ".pipeline" / "config.json").read_text(encoding="utf-8"))
    assert cfg["agent_observability"]["enabled"] is False


def test_obs_install_appends_without_replacing(tmp_path: Path):
    app = tmp_path / "app"
    app.mkdir()
    _init(app)
    hooks = app / ".cursor" / "hooks.json"
    hooks.parent.mkdir(parents=True)
    hooks.write_text(
        json.dumps(
            {
                "version": 1,
                "hooks": {
                    "afterFileEdit": [{"command": "node .cursor/hooks/hook-handler.js"}],
                    "stop": [{"command": "node .cursor/hooks/hook-handler.js"}],
                },
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    assert _run_cli(["obs", "install", str(app), "--ide", "cursor"]) == 0
    data = json.loads(hooks.read_text(encoding="utf-8"))
    after = data["hooks"]["afterFileEdit"]
    assert after[0]["command"] == "node .cursor/hooks/hook-handler.js"
    assert any("obs_collect.py" in item.get("command", "") for item in after)
    cfg = json.loads((app / ".pipeline" / "config.json").read_text(encoding="utf-8"))
    assert cfg["agent_observability"]["enabled"] is True


def test_obs_uninstall_leaves_foreign_hooks(tmp_path: Path):
    app = tmp_path / "app"
    app.mkdir()
    _init(app)
    hooks = app / ".cursor" / "hooks.json"
    hooks.parent.mkdir(parents=True)
    hooks.write_text(
        json.dumps(
            {
                "version": 1,
                "hooks": {"stop": [{"command": "node .cursor/hooks/hook-handler.js"}]},
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    assert _run_cli(["obs", "install", str(app)]) == 0
    assert _run_cli(["obs", "uninstall", str(app)]) == 0
    data = json.loads(hooks.read_text(encoding="utf-8"))
    assert data["hooks"]["stop"] == [{"command": "node .cursor/hooks/hook-handler.js"}]


def test_scoring_groups(tmp_path: Path):
    sys.path.insert(0, str(REPO))
    from pipeline_observability.scoring import score_events

    app = tmp_path / "app"
    app.mkdir()
    _init(app)
    cfg_path = app / ".pipeline" / "config.json"
    cfg = json.loads(cfg_path.read_text(encoding="utf-8"))
    cfg["verify"]["rules"] = [
        {"match": "frontend/", "message": "Run npm run build", "expect": "npm run build"}
    ]
    cfg_path.write_text(json.dumps(cfg, indent=2) + "\n", encoding="utf-8")
    (app / "features" / "demo").mkdir(parents=True)
    (app / "features" / "demo" / "HANDOFF-developer.md").write_text("SUCCESS\n", encoding="utf-8")
    rows = [
        {
            "ts": "2026-09-16T10:00:00.000Z",
            "kind": "step_context",
            "event": "subagentStart",
            "harness": "cursor",
            "payload": {"subagent_id": "s1", "hook_event_name": "subagentStart"},
            "step_context": {
                "workflow": "feature-development",
                "step": "developer-agent",
                "slug": "demo",
                "allowed_reads": [".pipeline/agents/developer-agent.md"],
            },
        },
        {
            "ts": "2026-09-16T10:00:01.000Z",
            "kind": "hook",
            "event": "postToolUse",
            "harness": "cursor",
            "payload": {
                "hook_event_name": "postToolUse",
                "subagent_id": "s1",
                "tool_name": "Read",
                "tool_input": {"path": ".pipeline/agents/developer-agent.md"},
                "duration": 5,
            },
        },
        {
            "ts": "2026-09-16T10:00:02.000Z",
            "kind": "hook",
            "event": "postToolUse",
            "harness": "cursor",
            "payload": {
                "hook_event_name": "postToolUse",
                "subagent_id": "s1",
                "tool_name": "Read",
                "tool_input": {"path": ".pipeline/agents/developer-agent.md"},
                "duration": 4,
            },
        },
        {
            "ts": "2026-09-16T10:00:03.000Z",
            "kind": "hook",
            "event": "postToolUse",
            "harness": "cursor",
            "payload": {
                "hook_event_name": "postToolUse",
                "subagent_id": "s1",
                "tool_name": "Read",
                "tool_input": {"path": "/tmp/secret-notes.md"},
                "duration": 3,
            },
        },
        {
            "ts": "2026-09-16T10:00:04.000Z",
            "kind": "hook",
            "event": "postToolUse",
            "harness": "cursor",
            "payload": {
                "hook_event_name": "postToolUse",
                "subagent_id": "s1",
                "tool_name": "Shell",
                "tool_input": {"command": "cat frontend/App.tsx"},
                "duration": 8,
            },
        },
        {
            "ts": "2026-09-16T10:00:05.000Z",
            "kind": "hook",
            "event": "afterFileEdit",
            "harness": "cursor",
            "payload": {
                "hook_event_name": "afterFileEdit",
                "subagent_id": "s1",
                "file_path": str(app / "frontend" / "App.tsx"),
            },
        },
    ]
    report = score_events(app, rows)
    step = report["steps"][0]
    assert step["tool_calls_total"] == 5
    assert step["waste_ratio"] > 0
    assert step["wrong_tool_count"] >= 1
    assert step["out_of_contract_count"] >= 1
    assert step["integrity_pass"] == 0.0


def test_collector_fail_open_and_redacts(tmp_path: Path):
    app = tmp_path / "app"
    app.mkdir()
    _init(app)
    cfg_path = app / ".pipeline" / "config.json"
    cfg = json.loads(cfg_path.read_text(encoding="utf-8"))
    cfg["agent_observability"]["enabled"] = True
    cfg_path.write_text(json.dumps(cfg, indent=2) + "\n", encoding="utf-8")
    script = app / ".pipeline" / "hooks" / "obs" / "obs_collect.py"
    payload = json.dumps(
        {
            "hook_event_name": "afterAgentResponse",
            "text": "ok",
            "input_tokens": 12,
            "secret": "sk-lf-SUPERSECRETVALUE12",
        }
    )
    proc = subprocess.run(
        [sys.executable, str(script)],
        input=payload,
        text=True,
        cwd=str(app),
        capture_output=True,
        check=False,
    )
    assert proc.returncode == 0
    assert proc.stdout.strip() == "{}"
    ledger = (app / ".pipeline" / "state" / "obs" / "events.jsonl").read_text(encoding="utf-8")
    assert "sk-lf-SUPERSECRETVALUE12" not in ledger
    assert "input_tokens" in ledger
    row = json.loads(ledger.strip().splitlines()[-1])
    marker = json.loads((app / ".pipeline" / "install.json").read_text(encoding="utf-8"))
    assert row.get("kit_version") == marker["version"]


def test_retry_after_seconds_from_langfuse_body():
    sys.path.insert(0, str(REPO))
    from pipeline_observability.adapters.httputil import retry_after_seconds

    body = '{"message":"Rate limit exceeded","details":{"retryAfterSeconds":11,"limit":30}}'
    assert retry_after_seconds(429, f"HTTP 429: {body}", None) == 11.0
    assert retry_after_seconds(200, body, None) == 0.0


def test_post_json_retries_429(monkeypatch):
    sys.path.insert(0, str(REPO))
    from pipeline_observability.adapters import httputil

    sleeps: list[float] = []
    monkeypatch.setattr(httputil.time, "sleep", lambda seconds: sleeps.append(seconds))
    seq = [
        (False, 'HTTP 429: {"details":{"retryAfterSeconds":11}}', 429, None),
        (True, '{"ok":true}', 200, None),
    ]

    def fake_once(*_args, **_kwargs):
        return seq.pop(0)

    monkeypatch.setattr(httputil, "_post_once", fake_once)
    ok, _detail, status = httputil.post_json("http://example.invalid", {}, {})
    assert ok is True
    assert status == 200
    assert sleeps == [11.0]


def test_build_otlp_conversation_tree(tmp_path: Path):
    sys.path.insert(0, str(REPO))
    from pipeline_observability.adapters.base import AdapterConfig
    from pipeline_observability.adapters.langfuse import LangfuseAdapter
    from pipeline_observability.export import build_otlp, otel32
    from pipeline_observability.scoring import score_events

    app = tmp_path / "app"
    app.mkdir()
    _init(app)
    conv = "cf794227-f288-418e-897e-c17d21b91d66"
    gen = "6ce9e2c7-fcce-4252-89c3-51f762678606"
    rows = [
        {
            "ts": "2026-09-17T06:35:00.000Z",
            "kind": "hook",
            "event": "beforeSubmitPrompt",
            "harness": "cursor",
            "payload": {
                "hook_event_name": "beforeSubmitPrompt",
                "conversation_id": conv,
                "prompt": "add a comment to README",
                "user_email": "dev@example.com",
                "model": "auto-smart",
            },
        },
        {
            "ts": "2026-09-17T06:35:01.000Z",
            "kind": "hook",
            "event": "postToolUse",
            "harness": "cursor",
            "payload": {
                "hook_event_name": "postToolUse",
                "conversation_id": conv,
                "generation_id": gen,
                "model": "auto-smart",
                "user_email": "dev@example.com",
                "tool_name": "Read",
                "tool_input": {"path": "news-site/README.md"},
                "tool_output": "{\"ok\":true}",
                "tool_use_id": "call-1",
                "duration": 4,
            },
        },
        {
            "ts": "2026-09-17T06:35:02.000Z",
            "kind": "hook",
            "event": "afterAgentResponse",
            "harness": "cursor",
            "payload": {
                "hook_event_name": "afterAgentResponse",
                "conversation_id": conv,
                "generation_id": gen,
                "text": "done",
                "input_tokens": 10,
                "output_tokens": 3,
                "user_email": "dev@example.com",
            },
        },
        {
            "ts": "2026-09-17T06:35:03.000Z",
            "kind": "hook",
            "event": "stop",
            "harness": "cursor",
            "payload": {
                "hook_event_name": "stop",
                "conversation_id": conv,
                "generation_id": gen,
                "status": "completed",
                "user_email": "dev@example.com",
            },
        },
    ]
    report = score_events(app, rows)
    adapter = LangfuseAdapter(AdapterConfig(name="langfuse", host="https://cloud.langfuse.com"))
    payload, scores, datasets = build_otlp(report, adapter)
    assert otel32(conv) == "cf794227f288418e897ec17d21b91d66"
    spans = payload["resourceSpans"][0]["scopeSpans"][0]["spans"]
    types = set()
    for span in spans:
        for attr in span["attributes"]:
            if attr["key"] == "langfuse.observation.type":
                types.add(attr["value"]["stringValue"])
    assert "agent" in types
    assert "generation" in types
    assert "retriever" in types
    assert "event" in types
    root = spans[0]
    keys = {item["key"] for item in root["attributes"]}
    assert "langfuse.observation.input" in keys
    assert "langfuse.user.id" in keys
    assert "langfuse.session.id" in keys
    assert "langfuse.trace.tags" in keys
    assert datasets[0]["trace_id"] == "cf794227f288418e897ec17d21b91d66"
    assert datasets[0]["session_id"] == conv
    assert datasets[0]["prompt"] == "add a comment to README"
    assert any(item["name"] == "tool_calls_total" for item in scores)
    gen_span = next(
        span
        for span in spans
        if any(
            attr["key"] == "langfuse.observation.type" and attr["value"].get("stringValue") == "generation"
            for attr in span["attributes"]
        )
    )
    gen_attrs = {item["key"]: item["value"] for item in gen_span["attributes"]}
    details = json.loads(gen_attrs["langfuse.observation.usage_details"]["stringValue"])
    assert details == {"input": 10, "output": 3}
    assert gen_attrs["gen_ai.usage.input_tokens"]["intValue"] == "10"
    assert gen_attrs["gen_ai.usage.output_tokens"]["intValue"] == "3"
    assert "langfuse.observation.cost_details" not in gen_attrs
    assert "gen_ai.usage.cost" not in gen_attrs


def test_generation_usage_max_cache_and_last_model(tmp_path: Path):
    sys.path.insert(0, str(REPO))
    from pipeline_observability.adapters.base import AdapterConfig
    from pipeline_observability.adapters.langfuse import LangfuseAdapter
    from pipeline_observability.export import build_otlp
    from pipeline_observability.scoring import score_events

    app = tmp_path / "app"
    app.mkdir()
    _init(app)
    conv = "91922323-55ee-4968-aa83-08fb446d2138"
    gen = "ad04e551-b998-4c62-8558-ca6feb3f7962"
    rows = [
        {
            "ts": "2026-09-17T07:24:31.000Z",
            "kind": "hook",
            "event": "beforeSubmitPrompt",
            "harness": "cursor",
            "payload": {
                "hook_event_name": "beforeSubmitPrompt",
                "conversation_id": conv,
                "generation_id": gen,
                "prompt": "add weather",
                "model": "auto-smart",
                "model_id": "auto-smart",
            },
        },
        {
            "ts": "2026-09-17T07:25:00.000Z",
            "kind": "hook",
            "event": "postToolUse",
            "harness": "cursor",
            "payload": {
                "hook_event_name": "postToolUse",
                "conversation_id": conv,
                "generation_id": gen,
                "model": "auto-smart",
                "tool_name": "Read",
                "tool_input": {"path": "news-site/README.md"},
                "tool_output": "{\"ok\":true}",
                "tool_use_id": "call-u1",
                "duration": 4,
            },
        },
        {
            "ts": "2026-09-17T07:32:54.000Z",
            "kind": "hook",
            "event": "afterAgentResponse",
            "harness": "cursor",
            "payload": {
                "hook_event_name": "afterAgentResponse",
                "conversation_id": conv,
                "generation_id": gen,
                "text": "done",
                "model": "cursor-grok-4.6-xhigh-fast",
                "model_id": "grok-4.6",
                "model_params": [{"id": "effort", "value": "xhigh"}],
                "input_tokens": 100,
                "output_tokens": 8,
                "cache_read_tokens": 80,
                "cache_write_tokens": 0,
            },
        },
        {
            "ts": "2026-09-17T07:32:55.000Z",
            "kind": "hook",
            "event": "stop",
            "harness": "cursor",
            "payload": {
                "hook_event_name": "stop",
                "conversation_id": conv,
                "generation_id": gen,
                "status": "completed",
                "model": "cursor-grok-4.6-xhigh-fast",
                "model_id": "grok-4.6",
                "input_tokens": 100,
                "output_tokens": 8,
                "cache_read_tokens": 80,
                "cache_write_tokens": 0,
            },
        },
    ]
    report = score_events(app, rows)
    adapter = LangfuseAdapter(AdapterConfig(name="langfuse", host="https://cloud.langfuse.com"))
    payload, _scores, _datasets = build_otlp(report, adapter)
    spans = payload["resourceSpans"][0]["scopeSpans"][0]["spans"]
    gen_span = next(
        span
        for span in spans
        if any(
            attr["key"] == "langfuse.observation.type" and attr["value"].get("stringValue") == "generation"
            for attr in span["attributes"]
        )
    )
    gen_attrs = {item["key"]: item["value"] for item in gen_span["attributes"]}
    details = json.loads(gen_attrs["langfuse.observation.usage_details"]["stringValue"])
    assert details["input"] == 20
    assert details["output"] == 8
    assert details["input_cached_tokens"] == 80
    assert "input_cache_creation" not in details
    assert gen_attrs["gen_ai.usage.input_tokens"]["intValue"] == "100"
    assert gen_attrs["gen_ai.usage.output_tokens"]["intValue"] == "8"
    assert gen_attrs["gen_ai.usage.cache_read_tokens"]["intValue"] == "80"
    assert gen_attrs["langfuse.observation.model.name"]["stringValue"] == "grok-4.6"
    assert gen_attrs["gen_ai.request.model"]["stringValue"] == "grok-4.6"
    cost = json.loads(gen_attrs["langfuse.observation.cost_details"]["stringValue"])
    assert cost["input"] == 0.00006
    assert cost["output"] == 0.00012
    assert cost["input_cached_tokens"] == 0.000024
    assert cost["total"] == 0.000204
    assert gen_attrs["gen_ai.usage.input_cost"]["doubleValue"] == 0.000084
    assert gen_attrs["gen_ai.usage.output_cost"]["doubleValue"] == 0.00012
    assert gen_attrs["gen_ai.usage.cost"]["doubleValue"] == 0.000204


def test_pricing_cache_and_overrides():
    sys.path.insert(0, str(REPO))
    from pipeline_observability.pricing import compute_cost_details, event_usage_attrs, observation_usage_attrs

    usage = {"input": 20, "output": 8, "input_cached_tokens": 80}
    cost = compute_cost_details("cursor-grok-4.6-xhigh-fast", usage)
    assert cost == {
        "input": 0.00006,
        "output": 0.00012,
        "input_cached_tokens": 0.000024,
        "total": 0.000204,
    }
    assert compute_cost_details("auto-smart", usage) is None
    attrs = observation_usage_attrs(
        model="gpt-4o-mini",
        input_tokens=1000,
        output_tokens=100,
        cache_read=400,
        cache_write=100,
        prices={"gpt-4o-mini": {"input": 1.0, "output": 2.0, "cache_read": 0.1, "cache_write": 1.5}},
        include_langfuse=False,
    )
    assert attrs["gen_ai.usage.input_cost"] == 0.00069
    assert attrs["gen_ai.usage.output_cost"] == 0.0002
    assert attrs["gen_ai.usage.cost"] == 0.00089
    assert "langfuse.observation.cost_details" not in attrs
    mapped = event_usage_attrs(
        {
            "model_id": "grok-4.6",
            "tokens": {"input_tokens": 100, "output_tokens": 8, "cache_read_tokens": 80},
        }
    )
    assert json.loads(mapped["langfuse.observation.cost_details"])["total"] == 0.000204


def test_adapter_map_attributes_include_cost():
    sys.path.insert(0, str(REPO))
    from pipeline_observability.adapters.base import AdapterConfig
    from pipeline_observability.adapters.datadog import DatadogAdapter
    from pipeline_observability.adapters.langfuse import LangfuseAdapter
    from pipeline_observability.adapters.otlp import OtlpAdapter

    event = {
        "model_id": "grok-4.6",
        "tokens": {"input_tokens": 100, "output_tokens": 8, "cache_read_tokens": 80},
    }
    lf = {item["key"]: item["value"] for item in LangfuseAdapter(AdapterConfig("langfuse", "http://x")).map_attributes(event)}
    assert lf["gen_ai.usage.cost"]["doubleValue"] == 0.000204
    assert "langfuse.observation.cost_details" in lf
    otlp = {item["key"]: item["value"] for item in OtlpAdapter(AdapterConfig("otlp", "http://x")).map_attributes(event)}
    assert otlp["gen_ai.usage.input_cost"]["doubleValue"] == 0.000084
    assert "langfuse.observation.cost_details" not in otlp
    dd = {item["key"]: item["value"] for item in DatadogAdapter(AdapterConfig("datadog", "")).map_attributes(event)}
    assert dd["gen_ai.usage.output_cost"]["doubleValue"] == 0.00012


def test_empty_grep_is_wasted(tmp_path: Path):
    sys.path.insert(0, str(REPO))
    from pipeline_observability.scoring import score_events

    app = tmp_path / "app"
    app.mkdir()
    _init(app)
    rows = [
        {
            "ts": "2026-09-17T10:00:00.000Z",
            "kind": "step_context",
            "event": "subagentStart",
            "payload": {"subagent_id": "s1", "hook_event_name": "subagentStart"},
            "step_context": {
                "workflow": "feature-development",
                "step": "developer-agent",
                "slug": "demo",
                "allowed_reads": [".pipeline/agents/developer-agent.md"],
            },
        },
        {
            "ts": "2026-09-17T10:00:01.000Z",
            "kind": "hook",
            "event": "postToolUse",
            "payload": {
                "hook_event_name": "postToolUse",
                "subagent_id": "s1",
                "tool_name": "Grep",
                "tool_input": {"pattern": "", "glob": "**/.shipmate/**"},
            },
        },
    ]
    report = score_events(app, rows)
    assert report["steps"][0]["waste_ratio"] == 1.0
