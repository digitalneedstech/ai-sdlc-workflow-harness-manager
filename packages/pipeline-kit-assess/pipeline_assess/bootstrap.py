"""Setup checks. Network installs run only in a terminal, and only after consent."""

from __future__ import annotations

import sys
from pathlib import Path

from pipeline_plugins.graphify import (
    EXTRACT_HINT,
    INSTALL_HINT,
    graph_exists,
    graph_freshness,
    graphify_status,
)


def _ask(prompt: str, *, yes: bool, no_bootstrap: bool, tty: bool, input_fn) -> bool:
    if no_bootstrap or not tty:
        print(prompt, file=sys.stderr)
        return False
    if yes:
        return True
    answer = input_fn(prompt + " [y/N] ")
    return answer.strip().lower() in {"y", "yes"}


def prepare(
    project: Path,
    *,
    yes: bool,
    no_bootstrap: bool,
    tty: bool,
    input_fn,
    installer=None,
) -> int:
    """Return 0 when the pack and a graph are present. Otherwise print the next step."""
    pack = project / ".pipeline" / "install.json"
    if not pack.is_file():
        print(
            "No pipeline-kit install. This writes .pipeline/ and IDE files.",
            file=sys.stderr,
        )
        if not _ask(
            "Run pipeline-kit init in this folder?",
            yes=yes,
            no_bootstrap=no_bootstrap,
            tty=tty,
            input_fn=input_fn,
        ):
            print("Next: pipeline-kit init", file=sys.stderr)
            return 1
        ide = _ide(project, tty=tty, input_fn=input_fn)
        mode = _mode(tty=tty, input_fn=input_fn)
        if not ide or not mode:
            print(
                "Init needs an IDE and a mode (kit or orchestrator).", file=sys.stderr
            )
            return 1
        if installer is None:
            print(f"Next: pipeline-kit init --mode {mode} --ide {ide}", file=sys.stderr)
            return 1
        code = int(installer(project, mode, ide))
        if code != 0:
            return code
    status = graphify_status()
    if status["state"] != "ready" and not graph_exists(project):
        print(INSTALL_HINT, file=sys.stderr)
        print(
            "Graphify install changes the user environment and uses the network.",
            file=sys.stderr,
        )
        if not tty:
            print("Refusing to install Graphify without a terminal.", file=sys.stderr)
            return 1
        if not _ask(
            "Install Graphify now?",
            yes=False,
            no_bootstrap=no_bootstrap,
            tty=tty,
            input_fn=input_fn,
        ):
            return 1
        print("Run the install command above, then rerun scan.", file=sys.stderr)
        return 1
    if not status.get("supported") and status.get("version"):
        print(status.get("recovery") or "Upgrade Graphify.", file=sys.stderr)
        return 1
    if not graph_exists(project):
        print("Knowledge graph is missing.", file=sys.stderr)
        print(EXTRACT_HINT, file=sys.stderr)
        print("Next: pipeline-kit knowledge extract", file=sys.stderr)
        return 1
    fresh = graph_freshness(project)
    if fresh["state"] == "stale":
        print(
            f"Knowledge graph is stale ({fresh['missing']} missing, {fresh['changed']} changed). "
            "Create these is withheld until you run: pipeline-kit knowledge extract --update",
            file=sys.stderr,
        )
    return 0


def _ide(project: Path, *, tty: bool, input_fn) -> str:
    cursor = (project / ".cursor").is_dir()
    claude = (project / ".claude").is_dir()
    if cursor and not claude:
        return "cursor"
    if claude and not cursor:
        return "claude-code"
    if not tty:
        return ""
    raw = input_fn("IDE? cursor, claude-code, github, or none: ").strip()
    return raw if raw in {"cursor", "claude-code", "github", "none"} else ""


def _mode(*, tty: bool, input_fn) -> str:
    if not tty:
        return ""
    raw = input_fn("Mode? kit or orchestrator: ").strip()
    return raw if raw in {"kit", "orchestrator"} else ""
