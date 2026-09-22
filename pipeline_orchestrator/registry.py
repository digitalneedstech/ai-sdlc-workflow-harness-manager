"""Resolve first-party and associate-owned workflows. Kit mode never imports this."""

from __future__ import annotations

import importlib
import importlib.metadata
import importlib.util
import sys
from pathlib import Path

from pipeline_orchestrator.graph import BUILTIN, WorkflowSpec

ENTRY_GROUP = "pipeline_kit.workflows"
EXTENSIONS_DIR = "pipeline_extensions"
BUILTIN_PROVIDER = "pipeline-kit"


class WorkflowConflict(ValueError):
    """An associate workflow reused a first-party name."""


def _as_spec(obj: object, *, provider: str, version: str = "") -> WorkflowSpec:
    if isinstance(obj, WorkflowSpec):
        if not obj.version:
            obj.version = version
        if obj.provider == BUILTIN_PROVIDER and provider != BUILTIN_PROVIDER:
            obj.provider = provider
        return obj
    raise TypeError(f"workflow object is not a WorkflowSpec: {type(obj)!r}")


def load_entry_point_specs() -> dict[str, WorkflowSpec]:
    found: dict[str, WorkflowSpec] = {}
    try:
        eps = importlib.metadata.entry_points()
        group = eps.select(group=ENTRY_GROUP) if hasattr(eps, "select") else eps.get(ENTRY_GROUP, [])
    except Exception:
        return found
    for ep in group:
        loaded = ep.load()
        spec = _as_spec(loaded, provider=ep.dist.name if ep.dist else ep.name, version=ep.dist.version if ep.dist else "")
        if spec.name in BUILTIN:
            raise WorkflowConflict(
                f"custom workflow {spec.name!r} cannot replace the first-party workflow"
            )
        found[spec.name] = spec
    return found


def load_project_specs(project: Path) -> dict[str, WorkflowSpec]:
    found: dict[str, WorkflowSpec] = {}
    root = project / EXTENSIONS_DIR
    if not root.is_dir():
        return found
    for path in sorted(root.glob("*.py")):
        if path.name.startswith("_"):
            continue
        mod_name = f"_pipeline_ext_{path.stem}"
        spec_loader = importlib.util.spec_from_file_location(mod_name, path)
        if spec_loader is None or spec_loader.loader is None:
            continue
        module = importlib.util.module_from_spec(spec_loader)
        sys.modules[mod_name] = module
        spec_loader.loader.exec_module(module)
        raw = getattr(module, "SPEC", None)
        if raw is None:
            continue
        spec = _as_spec(raw, provider=getattr(module, "PROVIDER", project.name or "local"))
        if spec.name in BUILTIN:
            raise WorkflowConflict(
                f"{path.name}: custom workflow {spec.name!r} cannot replace a first-party workflow"
            )
        found[spec.name] = spec
    return found


def resolve_spec(name: str, project: Path | None = None) -> WorkflowSpec:
    key = name.strip().lower()
    if key in BUILTIN:
        return BUILTIN[key]
    extras: dict[str, WorkflowSpec] = {}
    extras.update(load_entry_point_specs())
    if project is not None:
        extras.update(load_project_specs(project))
    if key not in extras:
        known = ", ".join([*BUILTIN, *extras]) or "(none)"
        raise ValueError(f"unknown workflow: {name} (known: {known})")
    return extras[key]


def list_specs(project: Path | None = None) -> list[WorkflowSpec]:
    specs = [BUILTIN[name] for name in BUILTIN]
    extras: dict[str, WorkflowSpec] = {}
    extras.update(load_entry_point_specs())
    if project is not None:
        extras.update(load_project_specs(project))
    for name in sorted(extras):
        specs.append(extras[name])
    return specs
