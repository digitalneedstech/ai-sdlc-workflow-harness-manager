"""Named pipeline capabilities. Writes existing config keys only."""

from __future__ import annotations

from pipeline_features.commands import (
    FEATURE_IDS,
    cmd_disable,
    cmd_enable,
    cmd_list,
    cmd_status,
)

__all__ = [
    "FEATURE_IDS",
    "cmd_disable",
    "cmd_enable",
    "cmd_list",
    "cmd_status",
]
