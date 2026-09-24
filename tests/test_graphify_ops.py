"""Graphify wrappers stay on the official CLI."""

from __future__ import annotations

from pathlib import Path

from pipeline_plugins.graphify import (
    graph_freshness,
    shrink_refused,
    update_graph,
)


class _Done:
    def __init__(self) -> None:
        self.returncode = 0
        self.stdout = ""
        self.stderr = ""


def test_update_uses_official_argv(tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setattr("pipeline_plugins.graphify.graphify_executable", lambda: "graphify")
    seen: dict[str, list[str]] = {}

    def runner(cmd, **_kwargs):
        seen["cmd"] = list(cmd)
        out = tmp_path / "graphify-out"
        out.mkdir()
        (out / "graph.json").write_text("{}\n", encoding="utf-8")
        return _Done()

    update_graph(tmp_path, runner=runner)
    assert seen["cmd"] == ["graphify", "update", "."]


def test_shrink_message_is_detected() -> None:
    assert shrink_refused("ERROR: refused to shrink graphify-out/graph.json")
    assert not shrink_refused("graph: 10 nodes")


def test_freshness_flags_a_moved_repo(tmp_path: Path) -> None:
    dest = tmp_path / "graphify-out"
    dest.mkdir()
    (dest / "manifest.json").write_text(
        '{"src/a.py": {"mtime": 1}, "src/b.py": {"mtime": 1}, "src/c.py": {"mtime": 1}, "src/d.py": {"mtime": 1}}',
        encoding="utf-8",
    )
    fresh = graph_freshness(tmp_path)
    assert fresh["state"] == "stale"
    assert fresh["missing"] == 4
