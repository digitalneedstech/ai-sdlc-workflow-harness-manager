"""Bounded slice of graphify-out/graph.json. Never inlines the whole graph."""

from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path

from pipeline_plugins.graphify import (
    EXTRACT_HINT,
    RECOVERY,
    graph_json_path,
    graphify_executable,
)

MAX_GRAPH_BYTES = 1_500_000
MAX_LABELS = 40
MIN_PRODUCT_NODES = 5
QUERY = "What are the major product areas in this codebase, ignoring the pipeline pack? List folder names only."
IGNORE_MARKER = "# pipeline-kit: do not index the agent pack"
PACK_IGNORE = (
    ".pipeline/",
    ".cursor/",
    ".claude/",
    ".github/skills/",
    "pipeline_extensions/",
    "features/",
    "graphify-out/",
)
_SECRET = re.compile(
    r"(secret|password|api[_-]?key|token|credential|private[_-]?key|\.env|begin )",
    re.IGNORECASE,
)


class GraphSliceError(RuntimeError):
    """The graph cannot be reduced to a short context."""

    def __init__(self, message: str, *, recovery: str = RECOVERY) -> None:
        super().__init__(message)
        self.recovery = recovery


def _secret(text: str) -> bool:
    return bool(_SECRET.search(text))


def _label(value: object) -> str:
    if isinstance(value, str):
        return value.strip()
    if isinstance(value, dict):
        for key in ("label", "name", "title", "community_label", "communityLabel"):
            raw = value.get(key)
            if isinstance(raw, str) and raw.strip():
                return raw.strip()
    return ""


def _add(found: list[str], text: str) -> None:
    cleaned = text.strip()
    if not cleaned or _secret(cleaned) or cleaned in found:
        return
    if len(found) >= MAX_LABELS:
        return
    found.append(cleaned)


def _is_pack_path(source: str) -> bool:
    norm = source.replace("\\", "/").removeprefix("./")
    return any(norm == item.rstrip("/") or norm.startswith(item) for item in PACK_IGNORE)


def ensure_graphifyignore(project: Path) -> bool:
    """Add pack paths so the next Graphify extract indexes the product."""
    path = project / ".graphifyignore"
    try:
        existing = path.read_text(encoding="utf-8") if path.is_file() else ""
    except OSError:
        return False
    missing = [item for item in PACK_IGNORE if item not in existing.splitlines()]
    if IGNORE_MARKER in existing and not missing:
        return False
    lines = existing.splitlines()
    if IGNORE_MARKER not in existing:
        if lines and lines[-1].strip():
            lines.append("")
        lines.append(IGNORE_MARKER)
    lines.extend(missing)
    path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")
    return True


def _product_slice(nodes: list[object]) -> str | None:
    product: list[dict] = []
    pack = 0
    for node in nodes:
        if not isinstance(node, dict):
            continue
        source = node.get("source_file")
        if not isinstance(source, str) or not source.strip():
            continue
        if _is_pack_path(source):
            pack += 1
            continue
        product.append(node)
    if not product:
        if pack == 0:
            return None
        return _missing_product(pack, 0)
    if len(product) < MIN_PRODUCT_NODES and pack > len(product) * 3:
        return _missing_product(pack, len(product))
    grouped: dict[object, list[dict]] = {}
    for node in product:
        grouped.setdefault(node.get("community"), []).append(node)
    lines: list[str] = []
    ordered = sorted(grouped.items(), key=lambda item: -len(item[1]))
    for _community, members in ordered[:12]:
        folders: dict[str, int] = {}
        labels: list[str] = []
        for node in members:
            source = str(node.get("source_file") or "")
            parts = source.replace("\\", "/").split("/")
            folder = "/".join(parts[:2]) if len(parts) > 1 else parts[0]
            folders[folder] = folders.get(folder, 0) + 1
            label = _label(node)
            if label and not _secret(label) and label not in labels:
                labels.append(label)
        folder = max(folders, key=folders.get) if folders else "product"
        shown = ", ".join(labels[:4])
        detail = f": {shown}" if shown else ""
        lines.append(f"- {folder} ({len(members)} code symbols){detail}")
    return "\n".join(lines)


def _missing_product(pack: int, product: int) -> str:
    ignored = "\n".join(PACK_IGNORE)
    return (
        "Product code is missing from this graph. "
        f"{pack} nodes are the pipeline pack (`.pipeline`, `.cursor`, `pipeline_extensions`). "
        f"{product} node{'s are' if product != 1 else ' is'} application code. "
        "Do not recommend skills, workflows, rules, or hooks from the pack.\n\n"
        "Add the pack paths to `.graphifyignore` (scan writes them when they are absent), "
        "then run `pipeline-kit knowledge extract` again. "
        "Until that graph exists, the only answer is to re-extract.\n\n"
        f"{ignored}"
    )


def extract_labels(data: object) -> list[str]:
    """Community and god-node names only. Node source is ignored."""
    if not isinstance(data, dict):
        return []
    found: list[str] = []
    for key in ("community_labels", "communityLabels"):
        labels = data.get(key)
        if isinstance(labels, dict):
            for value in labels.values():
                _add(found, _label(value))
    communities = data.get("communities")
    if isinstance(communities, dict):
        for value in communities.values():
            _add(found, _label(value))
    elif isinstance(communities, list):
        for item in communities:
            _add(found, _label(item))
    for key in ("gods", "god_nodes", "godNodes"):
        gods = data.get(key)
        if isinstance(gods, list):
            for item in gods:
                _add(found, _label(item))
    nodes = data.get("nodes")
    if isinstance(nodes, list):
        for node in nodes:
            if not isinstance(node, dict):
                continue
            if node.get("god") or node.get("is_god") or node.get("god_node"):
                _add(found, _label(node))
            for key in ("community_label", "communityLabel"):
                raw = node.get(key)
                if isinstance(raw, str):
                    _add(found, raw)
    return found


def redact_text(text: str) -> str:
    kept = [line for line in text.splitlines() if line.strip() and not _secret(line)]
    return "\n".join(kept).strip()


def _query(project: Path) -> str:
    exe = graphify_executable()
    if not exe:
        raise GraphSliceError(
            "graphify-out/graph.json is too large to inline, and graphify is not on PATH.",
            recovery=RECOVERY,
        )
    try:
        completed = subprocess.run(
            [exe, "query", QUERY, "--budget", "1500"],
            cwd=project,
            check=False,
            capture_output=True,
            text=True,
            timeout=120,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise GraphSliceError(
            f"graphify query failed: {exc}",
            recovery=EXTRACT_HINT,
        ) from exc
    if completed.returncode != 0:
        detail = (completed.stderr or completed.stdout or "").strip()
        raise GraphSliceError(
            f"graphify query failed (exit {completed.returncode}). {detail}".strip(),
            recovery=EXTRACT_HINT,
        )
    redacted = redact_text(completed.stdout or "")
    if not redacted:
        raise GraphSliceError(
            "graphify query returned no usable community text.",
            recovery=EXTRACT_HINT,
        )
    return redacted


def graph_slice(project: Path, *, max_bytes: int = MAX_GRAPH_BYTES, query_fn=None) -> str:
    path = graph_json_path(project)
    if not path.is_file():
        raise GraphSliceError(
            "graphify-out/graph.json is missing. Build the knowledge graph, then retry.",
            recovery=RECOVERY,
        )
    if path.stat().st_size > max_bytes:
        text = query_fn(project) if query_fn is not None else _query(project)
        redacted = redact_text(text)
        if not redacted:
            raise GraphSliceError(
                "graph query returned no usable community text.",
                recovery=EXTRACT_HINT,
            )
        return redacted
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise GraphSliceError(
            f"graphify-out/graph.json is not valid JSON: {exc}",
            recovery=EXTRACT_HINT,
        ) from exc
    nodes = data.get("nodes") if isinstance(data, dict) else None
    if isinstance(nodes, list) and any(isinstance(node, dict) and node.get("source_file") for node in nodes):
        product = _product_slice(nodes)
        if product:
            return product
    labels = extract_labels(data)
    if not labels:
        return "(no community labels in graph.json)"
    return "\n".join(f"- {label}" for label in labels)
