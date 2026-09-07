"""Installer tests. Writes only under tmp_path."""

from __future__ import annotations

import json
import runpy
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
INSTALL = REPO / "install.py"


def _run(argv: list[str]) -> int:
    ns = runpy.run_path(str(INSTALL))
    return int(ns["main"](argv))


def test_source_pack_is_bundled_kit():
    ns = runpy.run_path(str(INSTALL))
    pack = ns["source_pack"]()
    assert pack == ns["bundled_pack"]()
    assert (pack / "workflows" / "ask.json").is_file()


def test_default_args_create_project_pipeline(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    monkeypatch.chdir(tmp_path)
    assert _run(["--ide", "none"]) == 0
    assert (tmp_path / ".pipeline" / "workflows" / "ask.json").is_file()
    assert (tmp_path / ".pipeline" / "install.json").is_file()


def test_project_install_and_uninstall(tmp_path: Path):
    app = tmp_path / "app"
    app.mkdir()
    assert _run(["--project", str(app), "--ide", "none"]) == 0
    assert (app / ".pipeline" / "loader" / "load_workflow.py").is_file()
    assert (app / ".pipeline" / "workflows" / "ask.json").is_file()
    assert (app / ".pipeline" / "agents" / "developer-agent.md").is_file()
    assert (app / ".pipeline" / "config.json").is_file()
    assert (app / ".pipeline" / "install.json").is_file()
    assert (app / ".pipeline" / "docs" / "CUSTOMER-GUIDE.md").is_file()
    guide = (app / ".pipeline" / "docs" / "CUSTOMER-GUIDE.md").read_text(encoding="utf-8")
    assert "customer guide" in guide.lower()
    assert "chorus" not in guide.lower()
    assert not (app / ".cursor").exists()
    cfg = json.loads((app / ".pipeline" / "config.json").read_text(encoding="utf-8"))
    assert cfg["verify"]["rules"] == []
    assert "ask" in cfg["workflows"]
    assert _run(["--uninstall", "--project", str(app)]) == 0
    assert not (app / ".pipeline" / "install.json").exists()
    assert not (app / ".pipeline" / "loader" / "load_workflow.py").exists()


def test_project_ide_claude_code(tmp_path: Path):
    app = tmp_path / "app"
    app.mkdir()
    assert _run(["--project", str(app), "--ide", "claude-code"]) == 0
    skill = app / ".claude" / "skills" / "run-workflow" / "SKILL.md"
    assert skill.is_file()
    assert not (app / ".cloud").exists()


def test_project_ide_cursor_and_agent_stubs(tmp_path: Path):
    app = tmp_path / "app"
    app.mkdir()
    assert _run(["--project", str(app), "--ide", "cursor", "--agent-stubs"]) == 0
    skill = app / ".cursor" / "skills" / "run-workflow" / "SKILL.md"
    stub = app / ".cursor" / "agents" / "developer-agent.md"
    assert skill.is_file()
    assert stub.is_file()
    text = stub.read_text(encoding="utf-8")
    assert ".pipeline/agents/developer-agent.md" in text
    assert "Thin Cursor stub" in text


def test_merge_config_does_not_clobber(tmp_path: Path):
    app = tmp_path / "app"
    (app / ".pipeline").mkdir(parents=True)
    existing = {
        "version": 1,
        "workflows": {"custom": {"chain": []}},
        "verify": {"rules": [{"match": "/src/", "message": "keep me"}]},
    }
    (app / ".pipeline" / "config.json").write_text(
        json.dumps(existing, indent=2) + "\n", encoding="utf-8"
    )
    assert _run(["--project", str(app), "--ide", "none"]) == 0
    cfg = json.loads((app / ".pipeline" / "config.json").read_text(encoding="utf-8"))
    assert cfg["workflows"]["custom"] == {"chain": []}
    assert "ask" in cfg["workflows"]
    assert cfg["verify"]["rules"] == [{"match": "/src/", "message": "keep me"}]


def test_user_install(tmp_path: Path):
    home = tmp_path / "home"
    home.mkdir()
    assert _run(["--user", "--ide", "cursor", "--home", str(home)]) == 0
    assert (home / ".pipeline" / "workflows" / "ask.json").is_file()
    assert (home / ".pipeline" / "config.json").is_file()
    assert (home / ".cursor" / "skills" / "run-workflow" / "SKILL.md").is_file()
    marker = json.loads((home / ".pipeline" / "install.json").read_text(encoding="utf-8"))
    assert marker["scope"] == "user"
    assert any(name.endswith("ask.json") for name in marker["files"])
    assert _run(["--uninstall", "--user", "--home", str(home)]) == 0
    assert not (home / ".pipeline" / "install.json").exists()
    assert not (home / ".cursor" / "skills" / "run-workflow" / "SKILL.md").exists()


def test_dry_run_writes_nothing(tmp_path: Path):
    app = tmp_path / "app"
    app.mkdir()
    assert _run(["--project", str(app), "--ide", "none", "--dry-run"]) == 0
    assert not (app / ".pipeline").exists()
