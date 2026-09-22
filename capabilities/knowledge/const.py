"""Shared constants for the official Graphify + QA overlay path."""

from __future__ import annotations

GRAPH_DIR = "graphify-out"
GRAPH_JSON = "graph.json"
GRAPH_PROVIDER = "graphify-cli"
KNOWLEDGE_DIR = "test-knowledge"
CANDIDATES_DIR = "_candidates"
AREAS_DIR = "areas"
CONFIG_REL = ".pipeline/config.json"

INSTALL_HINT = "uv tool install graphifyy && graphify install"
EXTRACT_HINT = "graphify extract . --code-only"
RECOVERY = f"{INSTALL_HINT}\n{EXTRACT_HINT}"

EVIDENCE_STATES = frozenset(
    {"observed", "inferred", "planned", "verified", "stale"}
)
CATALOG_FILES = (
    "application.json",
    "actions.json",
    "fixtures.json",
    "oracles.json",
    "coverage.json",
)
ITEM_CATALOGS = frozenset({"actions.json", "fixtures.json", "oracles.json"})
ID_PATTERN = r"^[A-Z]{2,8}-[A-Za-z0-9._-]+$"
SECRET_PATTERNS = (
    r"(?i)(api[_-]?key|secret|passwd|password|token|bearer)\s*[:=]\s*\S+",
    r"-----BEGIN [A-Z ]*PRIVATE KEY-----",
    r"(?i)\b(ssn|social.?security)\b.+\d{3}",
)
