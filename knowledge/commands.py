"""User-facing knowledge commands. Thin wrappers over overlay + Graphify CLI."""

from __future__ import annotations

import sys
from pathlib import Path

from knowledge.const import INSTALL_HINT, RECOVERY
from knowledge.graphify import (
    GraphifyError,
    extract_graph,
    graphify_status,
    register_skill as register_graphify_skill,
)
from knowledge.overlay import (
    OverlayError,
    enable_test_design,
    init_overlay,
    overlay_status,
    promote_candidates,
    refresh_manifest_graph,
    validate_candidates,
)
from knowledge.render import RenderError, render_case_views


def cmd_init(project: Path, *, register_skill: bool = False, ide: str = "cursor") -> int:
    try:
        root = init_overlay(project)
        enable_test_design(project)
    except OverlayError as exc:
        print(str(exc), file=sys.stderr)
        return 64
    print(f"QA overlay: {root}")
    print("test_design.enabled: true")
    status = graphify_status()
    print(f"graphify: {status['state']}")
    if register_skill:
        registered = register_graphify_skill(project, ide=ide)
        if registered:
            print(f"registered Graphify skill: {registered}")
        else:
            print(
                "Graphify skill not registered. Install Graphify, then retry "
                f"with --register-skill.\n{INSTALL_HINT}",
                file=sys.stderr,
            )
    print("Next: pipeline-kit knowledge extract")
    return 0


def cmd_extract(project: Path, *, force: bool = False) -> int:
    try:
        path = extract_graph(project, force=force)
    except GraphifyError as exc:
        print(str(exc), file=sys.stderr)
        print(exc.recovery, file=sys.stderr)
        return 1
    if (project / "test-knowledge" / "manifest.json").is_file():
        refresh_manifest_graph(project)
    print(f"graph: {path}")
    return 0


def cmd_status(project: Path) -> int:
    cli = graphify_status()
    overlay = overlay_status(project)
    print(f"graphify: {cli['state']}")
    if cli["executable"]:
        print(f"executable: {cli['executable']}")
    if cli["version"]:
        print(f"version: {cli['version']}")
    print(f"graphify-out/graph.json: {'present' if overlay['graph_present'] else 'absent'}")
    print(f"overlay: {'present' if overlay['present'] else 'absent'}")
    print(f"test_design.enabled: {str(overlay['test_design_enabled']).lower()}")
    if cli["state"] == "missing":
        print(RECOVERY)
    return 0


def cmd_validate(project: Path, *, run_id: str) -> int:
    try:
        errors = validate_candidates(project, run_id)
    except OverlayError as exc:
        print(str(exc), file=sys.stderr)
        return 1
    if errors:
        print("validation failed:", file=sys.stderr)
        for error in errors:
            print(error, file=sys.stderr)
        return 1
    print(f"candidates ok: {run_id}")
    return 0


def cmd_promote(project: Path, *, run_id: str) -> int:
    try:
        promoted = promote_candidates(project, run_id)
    except OverlayError as exc:
        print(str(exc), file=sys.stderr)
        return 1
    print(f"promoted {len(promoted)} file(s) from {run_id}")
    for name in promoted:
        print(name)
    return 0


def cmd_render(project: Path, *, slug: str) -> int:
    try:
        written = render_case_views(project, slug)
    except RenderError as exc:
        print(str(exc), file=sys.stderr)
        return 1
    for path in written:
        print(path.relative_to(project))
    return 0
