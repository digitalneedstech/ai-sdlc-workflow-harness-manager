"""User-facing optional plugin commands. Thin wrappers over Graphify and Archify."""

from __future__ import annotations

import sys
from pathlib import Path

from pipeline_plugins.archify import (
    INSTALL_HINT as ARCHIFY_HINT,
    PINNED_INSTALL,
    PINNED_VERSION,
    ArchifyError,
    architecture_diagrams_enabled,
    archify_status,
    disable_architecture_diagrams,
    enable_architecture_diagrams,
    register_skill as register_archify_skill,
    uninstall_skill as uninstall_archify_skill,
)
from pipeline_plugins.graphify import (
    INSTALL_HINT as GRAPHIFY_HINT,
    graph_freshness,
    graphify_status,
    hook_status,
    install_hook,
    register_skill as register_graphify_skill,
    uninstall_skill as uninstall_graphify_skill,
)

PLUGIN_NAMES = ("graphify", "archify")


def cmd_list() -> int:
    print("graphify\toptional\tQA knowledge graph (official CLI). Used by scan and test design")
    print(
        f"archify\toptional\tArchitect diagrams (Agent Skill, pinned {PINNED_VERSION})"
    )
    print("Both stay off until you install them. Mermaid architecture still works.")
    return 0


def cmd_install(
    project: Path,
    name: str,
    *,
    ide: str = "cursor",
    scope: str = "project",
    home: Path | None = None,
    hook: bool = False,
) -> int:
    if name == "graphify":
        status = graphify_status()
        print(f"graphify: {status['state']}")
        registered = register_graphify_skill(project, ide=ide)
        if registered:
            print(f"registered Graphify skill: {registered}")
            if hook:
                if install_hook(project):
                    print("graphify hook: installed")
                else:
                    print("graphify hook: not installed. Run: graphify hook install", file=sys.stderr)
            return 0
        print(
            "Graphify skill not registered. Install Graphify, then retry.\n"
            f"{GRAPHIFY_HINT}",
            file=sys.stderr,
        )
        return 1 if status["state"] == "missing" else 1
    if name == "archify":
        try:
            enable_architecture_diagrams(project)
        except ArchifyError as exc:
            print(str(exc), file=sys.stderr)
            return 64
        print("architecture_diagrams.enabled: true")
        print("architecture_diagrams.fallback: mermaid")
        if ide == "none":
            print(
                "Archify skill not registered (--ide none). "
                "Mermaid remains the architecture baseline.",
                file=sys.stderr,
            )
            print(ARCHIFY_HINT, file=sys.stderr)
            return 0
        try:
            registered = register_archify_skill(
                project,
                ide=ide,
                scope=scope,
                home=home,
            )
        except ArchifyError as exc:
            print(str(exc), file=sys.stderr)
            print(exc.recovery, file=sys.stderr)
            print(
                "Config is enabled; Architect will use mermaid-fallback until Archify is ready."
            )
            return 1
        print(f"registered Archify skill: {registered}")
        print(f"pinned: {PINNED_VERSION}")
        return 0
    print(f"unknown plugin: {name}", file=sys.stderr)
    return 64


def cmd_status(
    project: Path,
    name: str | None,
    *,
    ide: str = "cursor",
    scope: str = "project",
    home: Path | None = None,
) -> int:
    names = PLUGIN_NAMES if name is None else (name,)
    for plugin in names:
        if plugin == "graphify":
            status = graphify_status()
            print(f"graphify: {status['state']}")
            if status["executable"]:
                print(f"executable: {status['executable']}")
            if status["version"]:
                print(f"version: {status['version']}")
                print(f"supported: {str(bool(status.get('supported'))).lower()}")
            fresh = graph_freshness(project)
            print(f"freshness: {fresh['state']}")
            if fresh["state"] == "stale":
                print(f"stale: {fresh['missing']} missing, {fresh['changed']} changed")
            print(f"hook: {hook_status(project)}")
            if status["recovery"]:
                print(status["recovery"])
            continue
        if plugin == "archify":
            status = archify_status(project, ide=ide, scope=scope, home=home)
            print(f"archify: {status['state']}")
            print(f"pinned: {status['pinned_version']}")
            print(f"architecture_diagrams.enabled: {str(status['enabled']).lower()}")
            print(f"fallback: {status['fallback']}")
            if status["skill_dir"]:
                print(f"skill_dir: {status['skill_dir']}")
            if status["executable"]:
                print(f"cli: {status['executable']}")
            if status["version"]:
                print(f"installed_version: {status['version']}")
            if status["recovery"] and status["state"] != "ready":
                print(status["recovery"])
            continue
        print(f"unknown plugin: {plugin}", file=sys.stderr)
        return 64
    return 0


def cmd_uninstall(
    project: Path,
    name: str,
    *,
    ide: str = "cursor",
    scope: str = "project",
    purge: bool = False,
    home: Path | None = None,
) -> int:
    if name == "graphify":
        result = uninstall_graphify_skill(project, ide=ide, purge=purge)
        if result["command"] and result["uninstalled"]:
            print(f"uninstalled Graphify skill: {result['command']}")
        elif result["command"]:
            print(
                "Graphify skill uninstall did not complete. "
                f"Try: {result['command']}",
                file=sys.stderr,
            )
        elif ide == "none":
            print("no IDE Graphify skill to uninstall (--ide none)")
        else:
            print(
                "Graphify CLI is missing; nothing to uninstall from the IDE.\n"
                f"{GRAPHIFY_HINT}",
                file=sys.stderr,
            )
        if result["purged"]:
            print(f"purged {result['graph_dir']}")
        else:
            print("left graphify-out/ in place (pass --purge to delete it)")
        return 0 if result["uninstalled"] or result["purged"] or not result["command"] else 1
    if name == "archify":
        if purge:
            print(
                "--purge does not delete architecture diagrams. "
                "features/*/diagrams/ is left in place.",
                file=sys.stderr,
            )
        try:
            path = uninstall_archify_skill(
                project,
                ide=ide,
                scope=scope,
                home=home,
            )
        except ArchifyError as exc:
            print(str(exc), file=sys.stderr)
            print(exc.recovery, file=sys.stderr)
            return 1
        if architecture_diagrams_enabled(project):
            disable_architecture_diagrams(project)
            print("architecture_diagrams.enabled: false")
        print(f"removed Archify skill: {path}")
        print("left features/*/diagrams/ in place")
        print(f"reinstall pinned: {PINNED_INSTALL}")
        return 0
    print(f"unknown plugin: {name}", file=sys.stderr)
    return 64
