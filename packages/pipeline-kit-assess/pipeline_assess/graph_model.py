"""Product areas, coupling, and health built from Graphify's files. No Graphify import."""

from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from pipeline_plugins.graphify import (
    MIN_VERSION,
    PACK_IGNORE,
    graph_freshness,
    graph_json_path,
    redact_text,
    version_supported,
)

INLINE_GRAPH_BYTES = 32_000_000
_FIELD = re.compile(
    r'^"(id|label|source_file|file_type|source|target|relation)"\s*:\s*(.+?)\s*,?\s*$'
)
SENSITIVE = ("auth", "payment", "billing", "pii", "crypto", "tenant", "password")
SERVICE_PARTS = {"api", "routes", "controllers", "handlers", "services"}
SKIP_WALK = {
    ".git",
    "node_modules",
    "graphify-out",
    ".pipeline",
    "dist",
    "build",
    ".venv",
    "venv",
}
BLIND_SUFFIXES = {".html", ".css", ".yml", ".yaml", ".sql", ".tf", ".tpl"}
BLIND_NAMES = {
    "dockerfile",
    "docker-compose.yml",
    "docker-compose.yaml",
    "compose.yml",
    "compose.yaml",
}


class GraphModelError(RuntimeError):
    def __init__(self, message: str, *, recovery: str = "") -> None:
        super().__init__(message)
        self.recovery = recovery


def _pack(source: str) -> bool:
    norm = source.replace("\\", "/").removeprefix("./")
    return any(
        norm == item.rstrip("/") or norm.startswith(item) for item in PACK_IGNORE
    )


def _secret(text: str) -> bool:
    return (
        "secret" in text.lower()
        or "password" in text.lower()
        or "api_key" in text.lower()
        or "api-key" in text.lower()
    )


def _json_value(raw: str) -> str:
    text = raw.strip().rstrip(",")
    if text == "null":
        return ""
    try:
        value = json.loads(text)
    except json.JSONDecodeError:
        return text.strip('"')
    return value if isinstance(value, str) else ""


def stream_graph(path: Path) -> dict[str, Any]:
    """Read a pretty-printed Graphify graph without loading the whole file."""
    nodes: list[dict[str, str]] = []
    links: list[dict[str, str]] = []
    section = ""
    current: dict[str, str] = {}
    try:
        handle = path.open(encoding="utf-8")
    except OSError as exc:
        raise GraphModelError(f"could not read {path.name}: {exc}") from exc
    with handle:
        for line in handle:
            stripped = line.strip()
            if stripped in {'"nodes": [', '"links": [', '"edges": ['}:
                section = stripped.split('"')[1]
                current = {}
                continue
            if not section:
                continue
            if stripped.startswith("}"):
                if section == "nodes" and current.get("source_file"):
                    nodes.append(current)
                elif (
                    section in {"links", "edges"}
                    and current.get("source")
                    and current.get("target")
                ):
                    links.append(current)
                current = {}
                continue
            match = _FIELD.match(stripped)
            if not match:
                continue
            key, raw = match.group(1), match.group(2)
            value = _json_value(raw)
            if key == "label":
                value = value[:120]
            if value:
                current[key] = value
    if not nodes:
        raise GraphModelError(
            "graphify-out/graph.json has no readable nodes.",
            recovery="pipeline-kit knowledge extract",
        )
    return {"nodes": nodes, "links": links}


def load_graph(project: Path) -> dict[str, Any]:
    path = graph_json_path(project)
    if not path.is_file():
        raise GraphModelError(
            "graphify-out/graph.json is missing.",
            recovery="pipeline-kit knowledge extract",
        )
    if path.stat().st_size > INLINE_GRAPH_BYTES:
        return stream_graph(path)
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise GraphModelError(
            f"graphify-out/graph.json is not valid JSON: {exc}"
        ) from exc
    if not isinstance(data, dict):
        raise GraphModelError("graphify-out/graph.json is not an object.")
    return data


def _links(data: dict[str, Any]) -> list[dict[str, Any]]:
    raw = data.get("links")
    if not isinstance(raw, list):
        raw = data.get("edges")
    if not isinstance(raw, list):
        return []
    return [item for item in raw if isinstance(item, dict)]


def _nodes(data: dict[str, Any]) -> list[dict[str, Any]]:
    raw = data.get("nodes")
    if not isinstance(raw, list):
        return []
    return [
        item
        for item in raw
        if isinstance(item, dict) and isinstance(item.get("source_file"), str)
    ]


def _analysis(project: Path) -> dict[str, Any]:
    path = project / "graphify-out" / ".graphify_analysis.json"
    if not path.is_file():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return data if isinstance(data, dict) else {}


def _is_test(source: str) -> bool:
    parts = source.replace("\\", "/").lower().split("/")
    name = parts[-1] if parts else ""
    if any(
        part in {"test", "tests", "__tests__", "spec", "specs"} for part in parts[:-1]
    ):
        return True
    return (
        name.startswith("test_")
        or name.endswith("_test.py")
        or ".spec." in name
        or ".test." in name
    )


def _folder(source: str, depth: int) -> str:
    parts = [part for part in source.replace("\\", "/").split("/") if part]
    if len(parts) <= 1:
        return parts[0] if parts else source
    return "/".join(parts[: min(depth, len(parts) - 1)])


def _choose_depth(sources: list[str]) -> int:
    best = 2
    best_gap = 999
    for depth in (1, 2, 3):
        count = len({_folder(source, depth) for source in sources})
        if 5 <= count <= 25:
            return depth
        gap = abs(count - 12)
        if gap < best_gap:
            best = depth
            best_gap = gap
    return best


def _tags(text: str) -> list[str]:
    lowered = text.lower()
    return [word for word in SENSITIVE if word in lowered and not _secret(text)]


def _degree(links: list[dict[str, Any]]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for link in links:
        for key in ("source", "target"):
            ident = link.get(key)
            if isinstance(ident, str):
                counts[ident] = counts.get(ident, 0) + 1
    return counts


def _blind_folders(project: Path, indexed: set[str]) -> list[str]:
    found: dict[str, int] = {}
    seen = 0
    for path in project.rglob("*"):
        seen += 1
        if seen > 2000:
            break
        if not path.is_file():
            continue
        if any(part in SKIP_WALK for part in path.parts):
            continue
        rel = path.relative_to(project).as_posix()
        if _pack(rel) or rel in indexed:
            continue
        name = path.name.lower()
        if name in BLIND_NAMES or path.suffix.lower() in BLIND_SUFFIXES:
            folder = rel.split("/")[0]
            found[folder] = found.get(folder, 0) + 1
    return sorted(found)


def _file_types(sources: list[str]) -> list[dict[str, Any]]:
    files: dict[str, set[str]] = {}
    for source in sources:
        suffix = Path(source).suffix.lower().lstrip(".")
        if not suffix.isascii() or not suffix.isalnum() or not 1 <= len(suffix) <= 8:
            continue
        files.setdefault(suffix, set()).add(source)
    ranked = sorted(files.items(), key=lambda item: (-len(item[1]), item[0]))
    return [{"ext": ext, "files": len(paths)} for ext, paths in ranked[:20]]


def analyze(project: Path, *, graphify_version: str | None = None) -> dict[str, Any]:
    fresh = graph_freshness(project)
    if graphify_version and not version_supported(graphify_version):
        raise GraphModelError(
            f"graphify {graphify_version} is older than {'.'.join(map(str, MIN_VERSION))}.",
            recovery="uv tool install --upgrade graphifyy",
        )
    data = load_graph(project)
    nodes = _nodes(data)
    links = _links(data)
    product = [node for node in nodes if not _pack(str(node.get("source_file")))]
    pack_count = len(nodes) - len(product)
    indexed = {str(node.get("source_file")) for node in nodes}
    if not product:
        return {
            "blocked": "pack-only" if pack_count else "empty",
            "freshness": fresh,
            "product_nodes": 0,
            "pack_nodes": pack_count,
            "areas": [],
            "coupling": [],
            "blind": _blind_folders(project, indexed),
            "gods": [],
            "file_types": [],
        }
    if fresh["state"] == "stale":
        return {
            "blocked": "stale",
            "freshness": fresh,
            "product_nodes": len(product),
            "pack_nodes": pack_count,
            "areas": [],
            "coupling": [],
            "blind": [],
            "gods": [],
            "file_types": [],
        }
    sources = [
        str(node["source_file"])
        for node in product
        if node.get("file_type", "code") == "code"
    ]
    depth = _choose_depth(sources or [str(node["source_file"]) for node in product])
    degrees = _degree(links)
    analysis = _analysis(project)
    god_ids = set()
    gods_out: list[dict[str, Any]] = []
    for item in analysis.get("gods") or []:
        if isinstance(item, dict) and isinstance(item.get("id"), str):
            god_ids.add(item["id"])
            label = redact_text(str(item.get("label") or ""))
            if label:
                gods_out.append(
                    {
                        "id": item["id"],
                        "label": label,
                        "degree": int(item.get("degree") or 0),
                    }
                )
    by_id = {str(node.get("id")): node for node in product if node.get("id")}
    areas: dict[str, dict[str, Any]] = {}
    for node in product:
        source = str(node["source_file"])
        folder = _folder(source, depth)
        area = areas.setdefault(
            folder,
            {
                "folder": folder,
                "symbols": 0,
                "god": False,
                "tested": False,
                "sensitive": [],
                "labels": [],
                "test_nodes": [],
                "node_ids": [],
            },
        )
        if node.get("file_type", "code") == "code":
            area["symbols"] += 1
        ident = str(node.get("id") or "")
        if ident:
            area["node_ids"].append(ident)
        label = str(node.get("label") or "")
        if (
            label
            and not _secret(label)
            and label not in area["labels"]
            and len(area["labels"]) < 4
        ):
            area["labels"].append(redact_text(label) or label)
        if ident in god_ids or degrees.get(ident, 0) >= 8:
            area["god"] = True
        blob = f"{folder} {label} {node.get('source_file')}"
        for tag in _tags(blob):
            if tag not in area["sensitive"]:
                area["sensitive"].append(tag)
        if _is_test(source):
            area["test_nodes"].append(ident)
    id_area = {}
    for folder, area in areas.items():
        for ident in area["node_ids"]:
            id_area[ident] = folder
    for link in links:
        source = link.get("source")
        target = link.get("target")
        if not isinstance(source, str) or not isinstance(target, str):
            continue
        source_area = id_area.get(source)
        target_area = id_area.get(target)
        if (
            source in by_id
            and _is_test(str(by_id[source].get("source_file")))
            and target_area
        ):
            areas[target_area]["tested"] = True
        if (
            target in by_id
            and _is_test(str(by_id[target].get("source_file")))
            and source_area
        ):
            areas[source_area]["tested"] = True
    coupling: dict[tuple[str, str], int] = {}
    for link in links:
        relation = str(link.get("relation") or "")
        if relation not in {"calls", "imports", "imports_from"}:
            continue
        left = id_area.get(str(link.get("source")))
        right = id_area.get(str(link.get("target")))
        if not left or not right or left == right:
            continue
        pair = tuple(sorted((left, right)))
        coupling[pair] = coupling.get(pair, 0) + 1
    couples = [
        {"left": pair[0], "right": pair[1], "count": count}
        for pair, count in sorted(
            coupling.items(), key=lambda item: (-item[1], item[0])
        )
        if count >= 3
    ][:8]
    listed = []
    for folder, area in sorted(
        areas.items(), key=lambda item: (-item[1]["symbols"], item[0])
    ):
        listed.append(
            {
                "folder": folder,
                "symbols": area["symbols"],
                "god": area["god"],
                "tested": area["tested"] or bool(area["test_nodes"]),
                "sensitive": area["sensitive"],
                "labels": [label for label in area["labels"] if label],
                "service": any(part in SERVICE_PARTS for part in folder.split("/")),
            }
        )
    return {
        "blocked": None,
        "freshness": fresh,
        "product_nodes": sum(area["symbols"] for area in listed),
        "pack_nodes": pack_count,
        "areas": listed,
        "coupling": couples,
        "blind": _blind_folders(project, indexed),
        "gods": gods_out[:8],
        "depth": depth,
        "file_types": _file_types(sources),
    }
