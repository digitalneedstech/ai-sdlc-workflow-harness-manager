"""Official tt-a1i/archify Agent Skill. Never vendor or invent a renderer."""

from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
from pathlib import Path
from typing import Any, Callable

PINNED_VERSION = "v2.16.0"
SOURCE_REPO = "tt-a1i/archify"
SKILL_NAME = "archify"
PROVIDER = "archify-skill"
CONFIG_REL = ".pipeline/config.json"
CONFIG_KEY = "architecture_diagrams"
FALLBACK = "mermaid"
VISUAL_CHECK = "when-available"
NODE_MAJOR_MIN = 18
INSTALL_HINT = (
    "Install GitHub CLI 2.90+ and Node.js 18+, then:\n"
    "pipeline-kit plugins install archify --ide cursor"
)
PINNED_INSTALL = (
    f"gh skill install {SOURCE_REPO} {SKILL_NAME} "
    f"--pin {PINNED_VERSION} --agent cursor --scope project"
)

GH_AGENTS = {
    "cursor": "cursor",
    "claude-code": "claude-code",
    "github": "github-copilot",
}
SKILL_REL = {
    "cursor": Path(".agents") / "skills" / SKILL_NAME,
    "claude-code": Path(".claude") / "skills" / SKILL_NAME,
    "github": Path(".agents") / "skills" / SKILL_NAME,
}

RunFn = Callable[..., subprocess.CompletedProcess[str]]


class ArchifyError(RuntimeError):
    """Archify is missing, unpinned, or not a managed install."""

    def __init__(self, message: str, *, recovery: str = INSTALL_HINT) -> None:
        super().__init__(message)
        self.recovery = recovery


def install_command(*, ide: str, scope: str) -> list[str]:
    """Pinned ``gh skill install`` argv. Never tracks the default branch."""
    agent = GH_AGENTS.get(ide)
    if agent is None:
        raise ArchifyError(
            f"ide {ide!r} has no Archify skill mapping. Use cursor, claude-code, or github.",
            recovery=INSTALL_HINT,
        )
    if scope not in {"project", "user"}:
        raise ArchifyError("scope must be project or user", recovery=INSTALL_HINT)
    return [
        "gh",
        "skill",
        "install",
        SOURCE_REPO,
        SKILL_NAME,
        "--pin",
        PINNED_VERSION,
        "--agent",
        agent,
        "--scope",
        scope,
    ]


def skill_rel(*, ide: str) -> Path:
    rel = SKILL_REL.get(ide)
    if rel is None:
        raise ArchifyError(
            f"ide {ide!r} has no Archify skill mapping.",
            recovery=INSTALL_HINT,
        )
    return rel


def skill_dir(root: Path, *, ide: str) -> Path:
    return (root / skill_rel(ide=ide)).resolve()


def expected_skill_root(root: Path, *, ide: str) -> Path:
    return skill_dir(root, ide=ide).parent.resolve()


def gh_executable() -> str | None:
    return shutil.which("gh")


def node_executable() -> str | None:
    return shutil.which("node")


def node_major(exe: str | None = None) -> int | None:
    binary = exe or node_executable()
    if not binary:
        return None
    try:
        completed = subprocess.run(
            [binary, "--version"],
            check=False,
            capture_output=True,
            text=True,
            timeout=15,
        )
    except (OSError, subprocess.TimeoutExpired):
        return None
    text = (completed.stdout or completed.stderr or "").strip()
    match = re.match(r"v?(\d+)", text)
    return int(match.group(1)) if match else None


def gh_supports_skill(exe: str | None = None) -> bool:
    binary = exe or gh_executable()
    if not binary:
        return False
    try:
        completed = subprocess.run(
            [binary, "skill", "--help"],
            check=False,
            capture_output=True,
            text=True,
            timeout=15,
        )
    except (OSError, subprocess.TimeoutExpired):
        return False
    return completed.returncode == 0


def cli_path(directory: Path) -> Path:
    return directory / "bin" / "archify.mjs"


def _frontmatter(text: str) -> str:
    if not text.startswith("---"):
        return ""
    parts = text.split("---", 2)
    return parts[1] if len(parts) >= 3 else ""


def is_managed_archify(directory: Path, *, expected_root: Path) -> bool:
    """True only for tt-a1i/archify under the expected skill root."""
    try:
        resolved = directory.resolve()
        root = expected_root.resolve()
    except OSError:
        return False
    if resolved.name != SKILL_NAME:
        return False
    try:
        resolved.relative_to(root)
    except ValueError:
        return False
    skill_md = resolved / "SKILL.md"
    if not skill_md.is_file() or not cli_path(resolved).is_file():
        return False
    try:
        body = skill_md.read_text(encoding="utf-8")
    except OSError:
        return False
    matter = _frontmatter(body)
    haystack = f"{matter}\n{body}"
    return SOURCE_REPO in haystack or (
        "name: archify" in matter and "tt-a1i" in haystack
    )


def read_installed_version(directory: Path) -> str | None:
    skill_md = directory / "SKILL.md"
    if not skill_md.is_file():
        return None
    try:
        matter = _frontmatter(skill_md.read_text(encoding="utf-8"))
    except OSError:
        return None
    for pattern in (
        r"(?im)^version:\s*[\"']?([^\"'\s]+)",
        r"(?im)^\s+version:\s*[\"']?([^\"'\s]+)",
        r"(?im)pin(?:ned)?(?:_version)?:\s*[\"']?([^\"'\s]+)",
    ):
        match = re.search(pattern, matter)
        if match:
            value = match.group(1).strip()
            if value and not value.startswith("{"):
                if re.fullmatch(r"\d+\.\d+", value):
                    return f"v{value}.0" if value.count(".") == 1 else f"v{value}"
                return value if value.startswith("v") else value
    if PINNED_VERSION in matter or "2.16" in matter:
        return PINNED_VERSION
    return None


def architecture_diagrams_config(project: Path) -> dict[str, Any]:
    path = project / CONFIG_REL
    if not path.is_file():
        return {}
    try:
        loaded = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    if not isinstance(loaded, dict):
        return {}
    block = loaded.get(CONFIG_KEY)
    return block if isinstance(block, dict) else {}


def architecture_diagrams_enabled(project: Path) -> bool:
    return architecture_diagrams_config(project).get("enabled") is True


def _write_config_block(project: Path, block: dict[str, Any]) -> None:
    path = project / CONFIG_REL
    if not path.is_file():
        raise ArchifyError(
            "no .pipeline/config.json — run pipeline-kit init first",
            recovery="pipeline-kit init --ide cursor",
        )
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ArchifyError("invalid .pipeline/config.json")
    data[CONFIG_KEY] = block
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")


def default_config_block(*, enabled: bool) -> dict[str, Any]:
    return {
        "_note": (
            "Opt-in. pipeline-kit plugins install archify sets enabled true. "
            "Absent or false keeps mermaid-only architecture. Do not add a "
            "diagram agent to class chains."
        ),
        "enabled": enabled,
        "provider": PROVIDER,
        "version": PINNED_VERSION,
        "fallback": FALLBACK,
        "visual_check": VISUAL_CHECK,
    }


def enable_architecture_diagrams(project: Path) -> None:
    block = architecture_diagrams_config(project)
    if not block:
        block = default_config_block(enabled=True)
    else:
        block = dict(block)
        block["enabled"] = True
        block.setdefault("provider", PROVIDER)
        block.setdefault("version", PINNED_VERSION)
        block.setdefault("fallback", FALLBACK)
        block.setdefault("visual_check", VISUAL_CHECK)
    _write_config_block(project, block)


def disable_architecture_diagrams(project: Path) -> None:
    block = architecture_diagrams_config(project)
    if not block:
        return
    block = dict(block)
    block["enabled"] = False
    _write_config_block(project, block)


def archify_status(
    project: Path,
    *,
    ide: str = "cursor",
    scope: str = "project",
    home: Path | None = None,
) -> dict[str, Any]:
    root = project if scope == "project" else (home or Path.home())
    gh = gh_executable()
    node = node_executable()
    major = node_major(node)
    directory: Path | None = None
    managed = False
    if ide != "none":
        try:
            directory = skill_dir(root, ide=ide)
            managed = is_managed_archify(
                directory,
                expected_root=expected_skill_root(root, ide=ide),
            )
        except ArchifyError:
            directory = None
    installed_version = read_installed_version(directory) if directory else None
    pin_ok = installed_version in {None, PINNED_VERSION, "2.16", "2.16.0"}
    if managed and pin_ok and major is not None and major >= NODE_MAJOR_MIN:
        state = "ready"
        recovery = None
    elif managed and not pin_ok:
        state = "unpinned"
        recovery = (
            f"Installed Archify is {installed_version}, expected {PINNED_VERSION}.\n"
            f"{PINNED_INSTALL}"
        )
    else:
        state = "missing"
        recovery = INSTALL_HINT
        if not gh or not gh_supports_skill(gh):
            recovery = (
                "GitHub CLI with `gh skill` is required (v2.90+).\n" + INSTALL_HINT
            )
        elif major is None:
            recovery = "Node.js 18+ is required.\n" + INSTALL_HINT
        elif major < NODE_MAJOR_MIN:
            recovery = f"Node.js {major} is too old; need 18+.\n" + INSTALL_HINT
    return {
        "name": "archify",
        "state": state,
        "executable": str(cli_path(directory)) if directory and managed else None,
        "version": installed_version,
        "pinned_version": PINNED_VERSION,
        "skill_dir": str(directory) if directory and directory.exists() else None,
        "managed": managed,
        "gh": gh,
        "node": node,
        "node_major": major,
        "enabled": architecture_diagrams_enabled(project),
        "fallback": FALLBACK,
        "recovery": recovery,
    }


def register_skill(
    project: Path,
    *,
    ide: str,
    scope: str = "project",
    home: Path | None = None,
    runner: RunFn = subprocess.run,
) -> str:
    """Install the pinned Archify skill via GitHub CLI. Never tracks main."""
    if ide == "none":
        raise ArchifyError(
            "cannot register Archify with --ide none",
            recovery=INSTALL_HINT,
        )
    gh = gh_executable()
    if not gh:
        raise ArchifyError(
            "gh is not on PATH. Install GitHub CLI v2.90+, then retry.",
            recovery=INSTALL_HINT,
        )
    if not gh_supports_skill(gh):
        raise ArchifyError(
            "this GitHub CLI build has no `gh skill` command. Upgrade to v2.90+.",
            recovery=INSTALL_HINT,
        )
    major = node_major()
    if major is None:
        raise ArchifyError(
            "node is not on PATH. Install Node.js 18+, then retry.",
            recovery=INSTALL_HINT,
        )
    if major < NODE_MAJOR_MIN:
        raise ArchifyError(
            f"Node.js {major} is too old. Archify needs Node.js 18+.",
            recovery=INSTALL_HINT,
        )
    command = install_command(ide=ide, scope=scope)
    command[0] = gh
    cwd = project if scope == "project" else (home or Path.home())
    env = os.environ.copy()
    env.setdefault("ARCHIFY_UPDATE_CHECK_DISABLED", "1")
    try:
        completed = runner(
            command,
            cwd=cwd,
            check=False,
            capture_output=True,
            text=True,
            timeout=180,
            env=env,
        )
    except OSError as exc:
        raise ArchifyError(
            f"could not run gh skill install: {exc}",
            recovery=PINNED_INSTALL,
        ) from exc
    except subprocess.TimeoutExpired as exc:
        raise ArchifyError(
            "gh skill install timed out. Run the pinned command locally.",
            recovery=PINNED_INSTALL,
        ) from exc
    except TypeError:
        # Test doubles may omit env=.
        completed = runner(
            command,
            cwd=cwd,
            check=False,
            capture_output=True,
            text=True,
            timeout=180,
        )
    if completed.returncode != 0:
        detail = (completed.stderr or completed.stdout or "").strip()
        suffix = f"\n{detail}" if detail else ""
        raise ArchifyError(
            f"gh skill install failed (exit {completed.returncode}).{suffix}",
            recovery=PINNED_INSTALL,
        )
    root = project if scope == "project" else (home or Path.home())
    directory = skill_dir(root, ide=ide)
    if not is_managed_archify(directory, expected_root=expected_skill_root(root, ide=ide)):
        raise ArchifyError(
            "gh skill install exited 0 but the pinned Archify skill is missing.",
            recovery=PINNED_INSTALL,
        )
    return " ".join(command)


def uninstall_skill(
    project: Path,
    *,
    ide: str,
    scope: str = "project",
    home: Path | None = None,
) -> Path:
    """Remove only the managed Archify skill directory. Keep diagram artifacts."""
    if ide == "none":
        raise ArchifyError("cannot uninstall Archify with --ide none")
    root = project if scope == "project" else (home or Path.home())
    directory = skill_dir(root, ide=ide)
    expected = expected_skill_root(root, ide=ide)
    if not directory.exists():
        return directory
    if not is_managed_archify(directory, expected_root=expected):
        raise ArchifyError(
            f"refusing to delete {directory}: it is not a managed {SOURCE_REPO} skill.",
            recovery="Inspect the path, then delete only .agents/skills/archify if it is yours.",
        )
    shutil.rmtree(directory)
    return directory


def archify_doctor_checks(target: Path) -> tuple[list[str], dict[str, bool]]:
    status = archify_status(target)
    info = [
        f"archify: {status['state']}",
        f"architecture_diagrams.enabled: {str(status['enabled']).lower()}",
    ]
    if status["skill_dir"] and status["managed"]:
        info.append(f"archify skill: {status['skill_dir']}")
    if status["state"] != "ready" and status["recovery"]:
        info.append(f"archify recovery: {status['recovery'].splitlines()[0]}")
    # Mermaid remains valid; never fail doctor when Archify is absent.
    return info, {}
