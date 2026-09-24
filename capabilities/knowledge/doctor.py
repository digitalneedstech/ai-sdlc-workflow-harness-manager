"""Doctor lines for Graphify. Informational unless test design is enabled."""

from __future__ import annotations

from pathlib import Path

from knowledge.graphify import graph_exists, graph_freshness, graphify_status
from knowledge.overlay import test_design_enabled


def graphify_doctor_checks(target: Path) -> tuple[list[str], dict[str, bool]]:
    status = graphify_status()
    graph_ok = graph_exists(target)
    fresh = graph_freshness(target) if graph_ok else {"state": "absent", "missing": 0, "changed": 0}
    info = [
        f"graphify: {status['state']}",
        f"graphify version: {status.get('version') or 'unknown'}",
        f"graphify supported: {str(bool(status.get('supported'))).lower()}",
        f"graphify-out/graph.json: {'present' if graph_ok else 'absent'}",
        f"graph freshness: {fresh['state']}",
    ]
    if fresh["state"] == "stale":
        info.append(
            "graph is stale. Run: pipeline-kit knowledge extract --update"
            + (f" ({fresh['missing']} missing, {fresh['changed']} changed)" if fresh.get("missing") or fresh.get("changed") else "")
        )
    assessed = (target / "features" / "assessment" / "assessment.json").is_file()
    required: dict[str, bool] = {}
    if test_design_enabled(target):
        required["graphify CLI (test_design.enabled)"] = status["state"] == "ready"
        required["graphify-out/graph.json (test_design.enabled)"] = graph_ok
    if assessed and status.get("version") and not status.get("supported"):
        info.append(
            "graphify is older than 0.9.56. Upgrade: uv tool install --upgrade graphifyy"
        )
    return info, required
