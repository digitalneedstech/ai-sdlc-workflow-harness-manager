"""Select a model decider from project config."""

from __future__ import annotations

from pathlib import Path

from pipeline_orchestrator.deciders.base import ModelDecider
from pipeline_orchestrator.deciders.fixed import FixedDecider
from pipeline_orchestrator.deciders.settings import load_settings, require_known


def decider_name(project: Path) -> str:
    return require_known(load_settings(project))


def make_decider(project: Path) -> ModelDecider:
    settings = load_settings(project)
    name = require_known(settings)
    if name == "fixed":
        return FixedDecider(settings)
    from pipeline_orchestrator.deciders.jev import JevDecider

    return JevDecider(settings)
