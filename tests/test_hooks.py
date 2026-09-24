"""Policy guardrails ship with the pack and merge on IDE init."""

from __future__ import annotations

import json
import runpy
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
INSTALL = REPO / "install.py"


def _run(argv: list[str]) -> int:
    ns = runpy.run_path(str(INSTALL))
    return int(ns["main"](argv))


def _run_cli(argv: list[str]) -> int:
    ns = runpy.run_path(str(INSTALL))
    return int(ns["cli_main"](argv))


def test_init_copies_guardrails_beside_obs(tmp_path: Path):
    app = tmp_path / "app"
    app.mkdir()
    assert _run(["--project", str(app), "--ide", "none"]) == 0
    hooks = app / ".pipeline" / "hooks"
    assert (hooks / "before-shell.py").is_file()
    assert (hooks / "before-mcp.py").is_file()
    assert (hooks / "before-read.py").is_file()
    assert (hooks / "after-file-edit.py").is_file()
    assert (hooks / "pre-write.py").is_file()
    assert (hooks / "subagent-start.py").is_file()
    assert (hooks / "lib.py").is_file()
    assert (hooks / "pack_gate.py").is_file()
    assert (hooks / "obs" / "obs_collect.py").is_file()
    assert not (hooks / "obs" / "before-shell.py").exists()


def test_cursor_init_merges_guardrails_not_obs(tmp_path: Path):
    app = tmp_path / "app"
    app.mkdir()
    assert _run(["--project", str(app), "--ide", "cursor"]) == 0
    data = json.loads((app / ".cursor" / "hooks.json").read_text(encoding="utf-8"))
    hooks = data["hooks"]
    assert any("before-shell.py" in item["command"] for item in hooks["beforeShellExecution"])
    assert any("before-mcp.py" in item["command"] for item in hooks["beforeMCPExecution"])
    assert any("after-file-edit.py" in item["command"] for item in hooks["afterFileEdit"])
    flat = [item.get("command", "") for entries in hooks.values() for item in entries]
    assert not any("obs_collect.py" in cmd for cmd in flat)


def test_cursor_merge_keeps_existing_and_survives_obs(tmp_path: Path):
    app = tmp_path / "app"
    app.mkdir()
    hooks = app / ".cursor" / "hooks.json"
    hooks.parent.mkdir(parents=True)
    hooks.write_text(
        json.dumps(
            {
                "version": 1,
                "hooks": {"afterFileEdit": [{"command": "node .cursor/hooks/hook-handler.js"}]},
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    assert _run(["--project", str(app), "--ide", "cursor"]) == 0
    assert _run_cli(["obs", "install", str(app), "--ide", "cursor"]) == 0
    data = json.loads(hooks.read_text(encoding="utf-8"))
    after = data["hooks"]["afterFileEdit"]
    cmds = [item.get("command", "") for item in after]
    assert cmds[0] == "node .cursor/hooks/hook-handler.js"
    assert any("after-file-edit.py" in cmd for cmd in cmds)
    assert any("obs_collect.py" in cmd for cmd in cmds)


def test_uninstall_strips_guardrails_keeps_foreign(tmp_path: Path):
    app = tmp_path / "app"
    app.mkdir()
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
    assert _run(["--project", str(app), "--ide", "cursor"]) == 0
    assert _run(["--uninstall", "--project", str(app)]) == 0
    data = json.loads(hooks.read_text(encoding="utf-8"))
    assert data["hooks"]["stop"] == [{"command": "node .cursor/hooks/hook-handler.js"}]
    assert "beforeShellExecution" not in data["hooks"]


def test_before_shell_denies_publish():
    script = REPO / "kit" / "pipeline" / "hooks" / "before-shell.py"
    verb = "com" + "mit"
    proc = subprocess.run(
        [sys.executable, str(script)],
        input=json.dumps({"command": "git %s -am x" % verb}),
        capture_output=True,
        text=True,
        check=False,
    )
    assert proc.returncode == 0
    out = json.loads(proc.stdout)
    assert out["permission"] == "deny"


def test_before_mcp_allows_read_denies_write():
    script = REPO / "kit" / "pipeline" / "hooks" / "before-mcp.py"
    read = subprocess.run(
        [sys.executable, str(script)],
        input=json.dumps({"tool_name": "getJiraIssue"}),
        capture_output=True,
        text=True,
        check=False,
    )
    write = subprocess.run(
        [sys.executable, str(script)],
        input=json.dumps({"tool_name": "createJiraIssue"}),
        capture_output=True,
        text=True,
        check=False,
    )
    assert json.loads(read.stdout)["permission"] == "allow"
    assert json.loads(write.stdout)["permission"] == "deny"
