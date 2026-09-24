"""Map capability folders to stable import names in a source checkout.

Installed wheels use ``pyproject.toml`` ``package-dir``. Source runs
(``python install.py``, pytest without a rebuilt editable install) use this
finder so public imports stay the same:

* ``knowledge``
* ``pipeline_plugins``
* ``pipeline_features``
* ``pipeline_observability``
* ``pipeline_eval``
* ``pipeline_orchestrator``
"""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent

SOURCE_PACKAGES = {
    "knowledge": ROOT / "capabilities" / "knowledge",
    "pipeline_plugins": ROOT / "capabilities" / "plugins",
    "pipeline_features": ROOT / "capabilities" / "feature_flags",
    "pipeline_observability": ROOT / "capabilities" / "observability",
    "pipeline_eval": ROOT / "capabilities" / "eval",
    "pipeline_orchestrator": ROOT / "orchestrator",
}


class SourcePackageFinder:
    def __init__(self, mapping: dict[str, Path]):
        self.mapping = {name: path for name, path in mapping.items() if path.is_dir()}

    def find_spec(self, fullname, path=None, target=None):  # noqa: ARG002
        top = fullname.split(".", 1)[0]
        root = self.mapping.get(top)
        if root is None:
            return None
        if fullname == top:
            init = root / "__init__.py"
            if not init.is_file():
                return None
            return importlib.util.spec_from_file_location(
                fullname,
                init,
                submodule_search_locations=[str(root)],
            )
        rel = fullname[len(top) + 1 :].replace(".", "/")
        file_py = root / f"{rel}.py"
        if file_py.is_file():
            return importlib.util.spec_from_file_location(fullname, file_py)
        package_dir = root / rel
        init = package_dir / "__init__.py"
        if init.is_file():
            return importlib.util.spec_from_file_location(
                fullname,
                init,
                submodule_search_locations=[str(package_dir)],
            )
        return None


class PipelineKitFinder:
    """Expose ``pipeline_kit.license`` from a source checkout.

    The wheel maps the ``pipeline_kit`` package onto this repo root. A source
    run has no ``pipeline_kit/`` directory, so this finder serves only the
    package init and the license module.
    """

    def find_spec(self, fullname, path=None, target=None):  # noqa: ARG002
        if fullname == "pipeline_kit":
            init = ROOT / "__init__.py"
            if not init.is_file():
                return None
            return importlib.util.spec_from_file_location(
                fullname,
                init,
                submodule_search_locations=[],
            )
        if fullname == "pipeline_kit.license":
            module = ROOT / "license.py"
            if not module.is_file():
                return None
            return importlib.util.spec_from_file_location(fullname, module)
        return None


_installed = False


def install_source_importers() -> None:
    """Register folder→import mappings when this tree is a kit checkout."""
    global _installed
    if _installed:
        return
    mapping = {name: path for name, path in SOURCE_PACKAGES.items() if path.is_dir()}
    if not mapping:
        return
    sys.meta_path.insert(0, PipelineKitFinder())
    sys.meta_path.insert(0, SourcePackageFinder(mapping))
    _installed = True
