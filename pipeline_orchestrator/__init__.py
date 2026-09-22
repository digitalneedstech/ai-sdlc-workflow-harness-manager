"""Code-owned workflow engine. Optional; kit mode does not import this at install time."""

from __future__ import annotations

EXIT_OK = 0
EXIT_STARTUP = 1
EXIT_STEP = 2
EXIT_GATE = 3
EXIT_VERIFY = 4
