"""Allowlist gate for pipeline pack Reads. Import-safe for pytest."""

from __future__ import annotations

import os
import re
from pathlib import Path
from typing import Any

SECRET_PATH = re.compile(
    r"(?:^|/)\.env(?:\.|$)|credentials\.json|\.pem$|\.p12$|id_rsa$|id_ed25519$|\.netrc$",
    re.I,
)

GATED_PREFIXES = (
    ".pipeline/skills/",
    ".pipeline/agents/",
    ".pipeline/wiki/",
    ".pipeline/rules/",
    ".cursor/wiki/",
    ".cursor/agents/",
    ".cursor/skills/",
)

ALWAYS_ALLOW_PREFIXES = (
    "features/",
    ".pipeline/loader/",
    ".pipeline/workflows/",
    ".pipeline/state/",
    ".pipeline/hooks/",
    ".pipeline/config.json",
    ".pipeline/README.md",
    ".cursor/hooks/",
    ".cursor/skills/run-workflow/",
)


def _norm(path: str) -> str:
    rel = path.replace("\\", "/")
    while rel.startswith("./"):
        rel = rel[2:]
    return rel


def rel_to_repo(path: str, repo: Path) -> str:
    raw = _norm(path)
    try:
        resolved = Path(raw)
        if resolved.is_absolute():
            return _norm(str(resolved.resolve().relative_to(repo.resolve())))
    except (OSError, ValueError):
        pass
    return raw


def is_secret(rel: str) -> bool:
    return bool(SECRET_PATH.search(rel))


def is_always_allow(rel: str) -> bool:
    if rel in {".pipeline/config.json", ".cursor/pipeline.config.json"}:
        return True
    return any(rel == p.rstrip("/") or rel.startswith(p) for p in ALWAYS_ALLOW_PREFIXES)


def is_gated(rel: str) -> bool:
    if is_always_allow(rel):
        return False
    return any(rel == p.rstrip("/") or rel.startswith(p) for p in GATED_PREFIXES)


def allowed_reads(pack: dict[str, Any] | None) -> set[str]:
    if not pack:
        return set()
    raw = pack.get("allowed_reads")
    if not isinstance(raw, list):
        return set()
    return {_norm(item) for item in raw if isinstance(item, str)}


def decide_read(
    path: str,
    repo: Path,
    *,
    portal_owns: bool,
    pack: dict[str, Any] | None,
) -> tuple[bool, str]:
    if portal_owns:
        return True, "external portal owns this session"
    rel = rel_to_repo(path, repo)
    if not rel:
        return True, "allow"
    if is_secret(rel):
        return False, (
            f"Blocked read of secret file ({rel}). "
            "Do not ingest credentials into the model."
        )
    if is_always_allow(rel) or not is_gated(rel):
        return True, "allow"
    if pack is None:
        return True, "allow"
    reads = allowed_reads(pack)
    if rel in reads:
        return True, "allow"
    return False, f"Blocked pack read ({rel}); not on the active workflow allowlist."


def portal_owns_from_env(env: dict[str, str] | None = None) -> bool:
    source = env if env is not None else os.environ
    return bool(source.get("CHORUS_TASK_ID") and source.get("CHORUS_PORTAL"))
