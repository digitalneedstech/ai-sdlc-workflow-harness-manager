"""pipeline-kit scan writes a prompt from a Graphify graph. It does not call a model."""

from __future__ import annotations

import json
import runpy
from pathlib import Path

from pipeline_plugins.graphify import EXTRACT_HINT
from pipeline_scan.graph_context import graph_slice

REPO = Path(__file__).resolve().parents[1]
INSTALL = REPO / "install.py"


def _run_cli(argv: list[str]) -> int:
    ns = runpy.run_path(str(INSTALL))
    return int(ns["cli_main"](argv))


def _pack(root: Path, *, mode: str = "kit") -> None:
    pipeline = root / ".pipeline"
    (pipeline / "workflows").mkdir(parents=True)
    (pipeline / "skills" / "orchestration").mkdir(parents=True)
    (pipeline / "agents").mkdir()
    (pipeline / "hooks").mkdir()
    (pipeline / "rules").mkdir()
    (pipeline / "install.json").write_text(json.dumps({"mode": mode}) + "\n", encoding="utf-8")
    (pipeline / "workflows" / "ask.json").write_text(
        json.dumps({"name": "ask"}) + "\n",
        encoding="utf-8",
    )
    (pipeline / "skills" / "orchestration" / "SKILL.md").write_text(
        "---\nname: orchestration\n---\n# Orchestration\n",
        encoding="utf-8",
    )
    (pipeline / "agents" / "developer-agent.md").write_text("# Developer\n", encoding="utf-8")
    (pipeline / "hooks" / "before-read.py").write_text("# hook\n", encoding="utf-8")
    (pipeline / "rules" / "pack-rule.md").write_text("# rule\n", encoding="utf-8")
    rules = root / ".cursor" / "rules"
    rules.mkdir(parents=True)
    (rules / "local.mdc").write_text("# local\n", encoding="utf-8")


def _graph(root: Path, payload: dict) -> None:
    dest = root / "graphify-out"
    dest.mkdir()
    (dest / "graph.json").write_text(json.dumps(payload), encoding="utf-8")


def test_scan_missing_graph_exits_without_prompt(tmp_path: Path, capsys) -> None:
    _pack(tmp_path)
    code = _run_cli(["scan", str(tmp_path)])
    captured = capsys.readouterr()
    assert code == 1
    assert EXTRACT_HINT in captured.err
    assert not (tmp_path / "features" / "pack-scan" / "prompt.md").exists()


def test_scan_writes_communities_and_installed_surface(tmp_path: Path, capsys) -> None:
    _pack(tmp_path)
    _graph(
        tmp_path,
        {
            "community_labels": {"0": "Billing", "1": "api_key_live"},
            "nodes": [
                {"label": "Invoice", "god": True, "source": "SECRET_SHOULD_NOT_COPY = True"},
                {"label": "IgnoredNode", "community": 0},
            ],
        },
    )
    code = _run_cli(["scan", str(tmp_path)])
    captured = capsys.readouterr()
    assert code == 0, captured.err
    out = tmp_path / "features" / "pack-scan"
    context = (out / "context.md").read_text(encoding="utf-8")
    prompt = (out / "prompt.md").read_text(encoding="utf-8")
    assert "Billing" in context
    assert "Invoice" in context
    assert "api_key_live" not in context
    assert "SECRET_SHOULD_NOT_COPY" not in context
    assert "ask" in context
    assert "orchestration" in context
    assert "developer-agent" in context
    assert "before-read.py" in context
    assert "local.mdc" in context
    assert "pack-rule.md" in context
    assert "Install mode: kit" in context
    for heading in ("## workflows", "## skills", "## sub-agents", "## rules", "## hooks"):
        assert heading in prompt
    assert not (tmp_path / "test-knowledge").exists()


def test_scan_orchestrator_lists_builtin_workflows(tmp_path: Path, capsys) -> None:
    _pack(tmp_path, mode="orchestrator")
    _graph(tmp_path, {"communities": [{"label": "Checkout"}]})
    code = _run_cli(["scan", str(tmp_path)])
    captured = capsys.readouterr()
    assert code == 0, captured.err
    context = (tmp_path / "features" / "pack-scan" / "context.md").read_text(encoding="utf-8")
    prompt = (tmp_path / "features" / "pack-scan" / "prompt.md").read_text(encoding="utf-8")
    assert "Install mode: orchestrator" in context
    assert "feature-development" in context
    assert "Checkout" in context
    assert "workflows --scaffold" in prompt


def test_large_graph_uses_query_and_drops_secret_lines(tmp_path: Path) -> None:
    _graph(
        tmp_path,
        {
            "community_labels": {"0": "ShouldNotParse"},
            "nodes": [{"source": "x" * 50}],
        },
    )

    def query(_project: Path) -> str:
        return "Billing community\napi_key in vault\nAuth community\n"

    text = graph_slice(tmp_path, max_bytes=10, query_fn=query)
    assert "Billing community" in text
    assert "Auth community" in text
    assert "api_key" not in text
    assert "ShouldNotParse" not in text


def test_scan_ignores_pack_nodes_and_names_product_folders(tmp_path: Path, capsys) -> None:
    _pack(tmp_path)
    nodes = [
        {"label": "hint()", "community": 0, "source_file": ".pipeline/hooks/after-file-edit.py"},
        {"label": "api_key_live", "community": 1, "source_file": "news-site/auth.py"},
    ]
    for index in range(6):
        nodes.append(
            {
                "label": f"Article{index}",
                "community": 2,
                "source_file": "news-site/pages/home.py",
            }
        )
    _graph(tmp_path, {"nodes": nodes, "links": []})
    code = _run_cli(["scan", str(tmp_path)])
    captured = capsys.readouterr()
    assert code == 0, captured.err
    context = (tmp_path / "features" / "pack-scan" / "context.md").read_text(encoding="utf-8")
    prompt = (tmp_path / "features" / "pack-scan" / "prompt.md").read_text(encoding="utf-8")
    assert "news-site/pages" in context
    assert "Article0" in context
    assert "after-file-edit.py" not in context
    assert "api_key_live" not in context
    assert "Product code is missing" not in context
    assert "Product code is missing" in prompt
    assert ".pipeline/" in (tmp_path / ".graphifyignore").read_text(encoding="utf-8")


def test_scan_says_when_the_graph_is_only_the_pack(tmp_path: Path, capsys) -> None:
    _pack(tmp_path)
    nodes = [
        {"label": "hint()", "community": index, "source_file": ".pipeline/hooks/lib.py"}
        for index in range(8)
    ]
    nodes.append({"label": "Home", "community": 9, "source_file": "news-site/pages/home.py"})
    _graph(tmp_path, {"nodes": nodes})
    assert _run_cli(["scan", str(tmp_path)]) == 0
    context = (tmp_path / "features" / "pack-scan" / "context.md").read_text(encoding="utf-8")
    assert "Product code is missing" in context
    assert "hint()" not in context


def test_scan_missing_pack(tmp_path: Path, capsys) -> None:
    code = _run_cli(["scan", str(tmp_path)])
    captured = capsys.readouterr()
    assert code == 1
    assert "pipeline-kit init" in captured.err
    assert not (tmp_path / "features" / "pack-scan" / "prompt.md").exists()
