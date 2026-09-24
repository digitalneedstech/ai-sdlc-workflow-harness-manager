"""Locate the bundled kit pack (wheel or source checkout)."""

from __future__ import annotations

from pathlib import Path


def kit_pack_root() -> Path:
    here = Path(__file__).resolve()
    candidates = [
        here.parent.parent / "kit" / "pipeline",
        here.parent / "kit" / "pipeline",
    ]
    try:
        import pipeline_kit

        pkg = Path(pipeline_kit.__file__).resolve().parent
        candidates.append(pkg / "kit" / "pipeline")
        candidates.append(pkg.parent / "kit" / "pipeline")
    except Exception:
        pass
    try:
        import install as install_mod

        candidates.append(Path(install_mod.__file__).resolve().parent / "kit" / "pipeline")
    except Exception:
        pass
    for candidate in candidates:
        if (candidate / "agents").is_dir() and (candidate / "workflows").is_dir():
            return candidate
    raise FileNotFoundError("bundled kit/pipeline pack not found")


def normalize_pack_rel(path: str) -> str:
    rel = path.replace("\\", "/")
    while rel.startswith("./"):
        rel = rel[2:]
    prefix = ".pipeline/"
    if rel.startswith(prefix):
        rel = rel[len(prefix):]
    return rel
