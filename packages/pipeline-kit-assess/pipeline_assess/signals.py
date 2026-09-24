"""Stack facts from allowlisted manifests and well-known paths. No source reads."""

from __future__ import annotations

import json
import re
from pathlib import Path

MAX_BYTES = 200_000
LLM = ("openai", "anthropic", "langchain", "llama-index", "llama_index")
FRONTEND = ("react", "vue", "angular", "svelte", "next")
TEST_LIBS = ("pytest", "jest", "vitest", "playwright", "junit", "mocha")


def _read(path: Path) -> str:
    if not path.is_file() or path.stat().st_size > MAX_BYTES:
        return ""
    try:
        return path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return ""


def _has_named(project: Path, names: set[str]) -> bool:
    for name in names:
        if (project / name).is_file():
            return True
        if any(project.glob(name)):
            return True
    return False


def collect_signals(project: Path) -> dict:
    package = _read(project / "package.json")
    pyproject = _read(project / "pyproject.toml")
    requirements = "\n".join(
        _read(path) for path in sorted(project.glob("requirements*.txt"))[:5]
    )
    pom = _read(project / "pom.xml")
    gradle = _read(project / "build.gradle") or _read(project / "build.gradle.kts")
    gomod = _read(project / "go.mod")
    blob = "\n".join([package, pyproject, requirements, pom, gradle, gomod]).lower()
    scripts: dict[str, str] = {}
    name = project.name
    if package:
        try:
            data = json.loads(package)
        except json.JSONDecodeError:
            data = {}
        if isinstance(data, dict):
            if isinstance(data.get("name"), str):
                name = data["name"]
            raw = data.get("scripts")
            if isinstance(raw, dict):
                scripts = {
                    str(key): str(value)
                    for key, value in raw.items()
                    if isinstance(value, str)
                }
    commands: dict[str, str] = {}
    for key in ("install", "build", "test", "lint", "start", "dev"):
        if key in scripts:
            commands[key] = scripts[key]
        elif key == "test" and "pytest" in pyproject:
            commands["test"] = "pytest"
    makefile = _read(project / "Makefile")
    for target in ("test", "lint", "build"):
        if target not in commands and re.search(rf"^{target}:", makefile, re.MULTILINE):
            commands[target] = f"make {target}"
    languages = []
    if package:
        languages.append("javascript")
    if pyproject or requirements or (project / "setup.py").is_file():
        languages.append("python")
    if pom or gradle:
        languages.append("java")
    if gomod:
        languages.append("go")
    ci = (project / ".github" / "workflows").is_dir() or (
        project / "Jenkinsfile"
    ).is_file()
    docker = _has_named(
        project,
        {
            "Dockerfile",
            "docker-compose.yml",
            "docker-compose.yaml",
            "compose.yml",
            "compose.yaml",
        },
    )
    iac = (
        any(project.glob("*.tf"))
        or (project / "charts").is_dir()
        or (project / "helm").is_dir()
    )
    e2e = (
        (project / "e2e").is_dir()
        or (project / "automation-tests").is_dir()
        or "playwright" in blob
    )
    return {
        "name": name,
        "languages": languages,
        "frontend": any(token in blob for token in FRONTEND),
        "tests": any(token in blob for token in TEST_LIBS)
        or (project / "tests").is_dir(),
        "llm": any(token in blob for token in LLM),
        "ci": ci,
        "docker": docker,
        "iac": iac,
        "e2e": e2e,
        "commands": commands,
        "jira": "unknown",
    }
