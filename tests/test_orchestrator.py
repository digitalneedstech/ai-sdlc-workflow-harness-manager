"""Orchestrator mode tests. Must not change kit-mode install behavior."""

from __future__ import annotations

import json
import runpy
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
INSTALL = REPO / "install.py"


def _cli(argv: list[str]) -> int:
    ns = runpy.run_path(str(INSTALL))
    return int(ns["cli_main"](argv))


def test_kit_init_still_copies_pack(tmp_path: Path):
    app = tmp_path / "app"
    app.mkdir()
    assert _cli(["init", str(app), "--ide", "none"]) == 0
    assert (app / ".pipeline" / "agents" / "developer-agent.md").is_file()
    assert (app / ".pipeline" / "loader" / "load_workflow.py").is_file()
    assert (app / ".pipeline" / "workflows" / "feature-development.json").is_file()
    marker = json.loads((app / ".pipeline" / "install.json").read_text(encoding="utf-8"))
    assert marker.get("mode", "kit") == "kit"


def test_orchestrator_init_does_not_copy_briefs(tmp_path: Path):
    app = tmp_path / "app"
    app.mkdir()
    assert _cli(["init", str(app), "--ide", "cursor", "--mode", "orchestrator"]) == 0
    assert not (app / ".pipeline" / "agents").exists()
    assert not (app / ".pipeline" / "skills").exists()
    assert not (app / ".pipeline" / "loader").exists()
    assert not (app / ".pipeline" / "workflows").exists()
    assert (app / ".pipeline" / "config.json").is_file()
    assert (app / ".pipeline" / "wiki" / "INDEX.md").is_file()
    assert (app / ".pipeline" / "hooks" / "obs" / "obs_collect.py").is_file()
    skill = app / ".cursor" / "skills" / "run-workflow" / "SKILL.md"
    assert skill.is_file()
    text = skill.read_text(encoding="utf-8")
    assert "pipeline-kit run" in text
    assert "load_workflow.py" in text
    marker = json.loads((app / ".pipeline" / "install.json").read_text(encoding="utf-8"))
    assert marker["mode"] == "orchestrator"


def test_update_preserves_orchestrator_mode(tmp_path: Path):
    app = tmp_path / "app"
    app.mkdir()
    assert _cli(["init", str(app), "--ide", "none", "--mode", "orchestrator"]) == 0
    assert _cli(["update", str(app), "--ide", "none"]) == 0
    marker = json.loads((app / ".pipeline" / "install.json").read_text(encoding="utf-8"))
    assert marker["mode"] == "orchestrator"
    assert not (app / ".pipeline" / "agents").exists()


def test_kit_workflows_list_ignores_extensions(tmp_path: Path, capsys: pytest.CaptureFixture[str]):
    app = tmp_path / "app"
    app.mkdir()
    assert _cli(["init", str(app), "--ide", "none"]) == 0
    assert _cli(["workflows", str(app), "--scaffold", "security-review"]) == 0
    assert (app / "pipeline_extensions" / "security_review.py").is_file()
    capsys.readouterr()
    assert _cli(["workflows", str(app)]) == 0
    names = capsys.readouterr().out.splitlines()
    assert "ask" in names
    assert "security-review" not in names


def test_cannot_scaffold_first_party_name(tmp_path: Path):
    app = tmp_path / "app"
    app.mkdir()
    assert _cli(["workflows", str(app), "--scaffold", "feature-development"]) == 1


def test_micro_run_with_fake_runner(tmp_path: Path):
    app = tmp_path / "app"
    app.mkdir()
    assert _cli(["init", str(app), "--ide", "none", "--mode", "orchestrator"]) == 0
    code = _cli(
        [
            "run",
            str(app),
            "--slug",
            "tiny-fix",
            "--workflow",
            "feature-development",
            "--change-class",
            "micro",
            "--runner",
            "fake",
        ]
    )
    assert code == 0
    run = json.loads(
        (app / ".pipeline" / "state" / "runs" / "tiny-fix.json").read_text(encoding="utf-8")
    )
    assert run["status"] == "completed"
    assert run["workflow_provider"] == "pipeline-kit"
    assert (app / "features" / "tiny-fix" / "state" / "developer-agent.json").is_file()
    events = (app / ".pipeline" / "state" / "obs" / "events.jsonl").read_text(encoding="utf-8")
    assert "run_start" in events
    assert "step_end" in events


def test_feature_pauses_at_signoff_then_resumes(tmp_path: Path):
    app = tmp_path / "app"
    app.mkdir()
    assert _cli(["init", str(app), "--ide", "none", "--mode", "orchestrator"]) == 0
    code = _cli(
        [
            "run",
            str(app),
            "--slug",
            "checkout-redesign",
            "--workflow",
            "feature-development",
            "--change-class",
            "feature",
            "--runner",
            "fake",
        ]
    )
    assert code == 3
    run = json.loads(
        (app / ".pipeline" / "state" / "runs" / "checkout-redesign.json").read_text(
            encoding="utf-8"
        )
    )
    assert run["status"] == "awaiting_approval"
    assert run["current_node"] == "requirements"
    assert _cli(["approve", str(app), "--slug", "checkout-redesign", "--gate", "requirements"]) == 0
    signoff = (app / "features" / "checkout-redesign" / "signoff-requirements.md").read_text(
        encoding="utf-8"
    )
    assert "SIGNOFF: approved" in signoff
    code = _cli(["resume", str(app), "--slug", "checkout-redesign", "--runner", "fake"])
    assert code == 3
    run = json.loads(
        (app / ".pipeline" / "state" / "runs" / "checkout-redesign.json").read_text(
            encoding="utf-8"
        )
    )
    assert run["current_node"] == "architect"
    assert run["steps"]["architect-agent"]["status"] == "completed"


def test_custom_workflow_is_orchestrator_only(tmp_path: Path):
    app = tmp_path / "app"
    app.mkdir()
    assert _cli(["init", str(app), "--ide", "none", "--mode", "orchestrator"]) == 0
    assert _cli(["workflows", str(app), "--scaffold", "security-review"]) == 0
    code = _cli(
        [
            "run",
            str(app),
            "--slug",
            "pci-gap",
            "--workflow",
            "security-review",
            "--runner",
            "fake",
        ]
    )
    assert code == 3
    run = json.loads(
        (app / ".pipeline" / "state" / "runs" / "pci-gap.json").read_text(encoding="utf-8")
    )
    assert run["workflow"] == "security-review"
    assert run["workflow_provider"] != "pipeline-kit"
    assert (app / "features" / "pci-gap" / "state" / "security-review-agent.json").is_file()


def test_run_persists_user_request(tmp_path: Path):
    app = tmp_path / "app"
    app.mkdir()
    assert _cli(["init", str(app), "--ide", "none", "--mode", "orchestrator"]) == 0
    ask = "add a line in AGENTS.md about orchestrator mode"
    code = _cli(
        [
            "run",
            str(app),
            "--slug",
            "agents-md-line",
            "--workflow",
            "feature-development",
            "--change-class",
            "micro",
            "--runner",
            "fake",
            "--request",
            ask,
        ]
    )
    assert code == 0
    run = json.loads(
        (app / ".pipeline" / "state" / "runs" / "agents-md-line.json").read_text(
            encoding="utf-8"
        )
    )
    assert run["user_request"] == ask
    assert (app / "features" / "agents-md-line" / "request.md").read_text(
        encoding="utf-8"
    ).strip() == ask


def test_run_loads_request_md(tmp_path: Path):
    app = tmp_path / "app"
    app.mkdir()
    assert _cli(["init", str(app), "--ide", "none", "--mode", "orchestrator"]) == 0
    dest = app / "features" / "from-file" / "request.md"
    dest.parent.mkdir(parents=True)
    dest.write_text("fix the empty cart badge\n", encoding="utf-8")
    code = _cli(
        [
            "run",
            str(app),
            "--slug",
            "from-file",
            "--workflow",
            "feature-development",
            "--change-class",
            "micro",
            "--runner",
            "fake",
        ]
    )
    assert code == 0
    run = json.loads(
        (app / ".pipeline" / "state" / "runs" / "from-file.json").read_text(encoding="utf-8")
    )
    assert run["user_request"] == "fix the empty cart badge"


def test_fake_startup_failure_is_exit_1(tmp_path: Path):
    import sys

    sys.path.insert(0, str(REPO))
    from pipeline_orchestrator.engine import advance, start_run
    from pipeline_orchestrator.graph import feature_development
    from pipeline_orchestrator.runners.fake import FakeRunner
    import asyncio

    app = tmp_path / "app"
    (app / ".pipeline").mkdir(parents=True)
    spec = feature_development()
    run = start_run(
        project=app,
        spec=spec,
        slug="boom",
        change_class="micro",
        runner_name="fake",
        kit_version="test",
    )
    runner = FakeRunner({"developer-agent": {"startup_failure": True}})
    code = asyncio.run(advance(project=app, spec=spec, run=run, runner=runner))
    assert code == 1


def test_demo_extensions_load_and_run(tmp_path: Path, capsys: pytest.CaptureFixture[str]):
    import shutil

    app = tmp_path / "app"
    app.mkdir()
    shutil.copytree(
        REPO / "extensions" / "orchestrator" / "pipeline_extensions",
        app / "pipeline_extensions",
    )
    assert _cli(["init", str(app), "--ide", "none", "--mode", "orchestrator"]) == 0
    capsys.readouterr()
    assert _cli(["workflows", str(app)]) == 0
    listed = capsys.readouterr().out
    for name in (
        "security-review",
        "ci-audit",
        "dependency-audit",
        "accessibility-review",
    ):
        assert name in listed
    assert _cli(
        [
            "run",
            str(app),
            "--slug",
            "pci-sample",
            "--workflow",
            "security-review",
            "--runner",
            "fake",
            "--request",
            "review auth on checkout",
        ]
    ) == 3
    run = json.loads(
        (app / ".pipeline" / "state" / "runs" / "pci-sample.json").read_text(encoding="utf-8")
    )
    assert run["workflow"] == "security-review"
    assert run["status"] == "awaiting_approval"
    assert run["current_node"] == "security"
    assert (app / "features" / "pci-sample" / "state" / "security-review-agent.json").is_file()
    assert _cli(
        [
            "run",
            str(app),
            "--slug",
            "deps-sample",
            "--workflow",
            "dependency-audit",
            "--runner",
            "fake",
            "--request",
            "list unpinned Python deps",
        ]
    ) == 0


def test_missing_state_fails_closed(tmp_path: Path):
    import sys
    import asyncio

    sys.path.insert(0, str(REPO))
    from pipeline_orchestrator.engine import advance, start_run
    from pipeline_orchestrator.graph import feature_development
    from pipeline_orchestrator.runners.fake import FakeRunner

    app = tmp_path / "app"
    (app / ".pipeline").mkdir(parents=True)
    spec = feature_development()
    run = start_run(
        project=app,
        spec=spec,
        slug="ghost",
        change_class="micro",
        runner_name="fake",
        kit_version="test",
    )
    runner = FakeRunner({"developer-agent": {"omit_state": True}})
    code = asyncio.run(advance(project=app, spec=spec, run=run, runner=runner))
    assert code == 2
