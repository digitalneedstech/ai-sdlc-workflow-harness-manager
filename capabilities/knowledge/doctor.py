"""Doctor lines for Graphify. Informational unless test design is enabled."""

from __future__ import annotations

from pathlib import Path

from knowledge.graphify import graph_exists, graphify_status
from knowledge.overlay import test_design_enabled


def graphify_doctor_checks(target: Path) -> tuple[list[str], dict[str, bool]]:
    status = graphify_status()
    graph_ok = graph_exists(target)
    info = [
        f"graphify: {status['state']}",
        f"graphify-out/graph.json: {'present' if graph_ok else 'absent'}",
    ]
    required: dict[str, bool] = {}
    if test_design_enabled(target):
        required["graphify CLI (test_design.enabled)"] = status["state"] == "ready"
        required["graphify-out/graph.json (test_design.enabled)"] = graph_ok
    return info, required
