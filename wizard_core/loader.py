"""Module loader + runtime registry (Blueprint §11.4).

Scans a modules directory, validates each ``manifest.yaml`` against
:class:`ModuleManifest`, checks base-API compatibility, loads the referenced
content (lessons / tools / troubleshooters / glossary) and registers it. Adding
content is adding data — no UI/code changes. Bad manifests/content fail loudly.

The troubleshooter router (T00) is realised here as an aggregated symptom index
built across every loaded troubleshooter module (deterministic, offline).
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable

import yaml

from . import BASE_API_VERSION
from .glossary import Glossary
from .models import (
    GlossaryTerm,
    LessonSpec,
    ModuleManifest,
    ToolSpec,
    TroubleshooterSpec,
)


class ModuleError(RuntimeError):
    """Raised for any invalid manifest/content (fail loudly)."""


# --------------------------------------------------------------------------- #
#  base_api compatibility
# --------------------------------------------------------------------------- #

_REQ_RE = re.compile(r"^\s*(>=|==|>)?\s*(\d+)\.(\d+)\s*$")


def _ver_tuple(v: str) -> tuple[int, int]:
    major, _, minor = v.partition(".")
    return int(major), int(minor or 0)


def api_satisfied(requirement: str, current: str = BASE_API_VERSION) -> bool:
    """Check a simple ``>=X.Y`` / ``>X.Y`` / ``==X.Y`` requirement against current API."""
    m = _REQ_RE.match(requirement or ">=1.0")
    if not m:
        raise ModuleError(f"Unparseable base_api requirement: {requirement!r}")
    op, maj, minr = m.group(1) or ">=", int(m.group(2)), int(m.group(3))
    cur = _ver_tuple(current)
    req = (maj, minr)
    if op == ">=":
        return cur >= req
    if op == ">":
        return cur > req
    return cur == req  # "=="


# --------------------------------------------------------------------------- #
#  Registry
# --------------------------------------------------------------------------- #


@dataclass
class SymptomMatch:
    troubleshooter_id: str
    symptom_id: str
    label: str
    score: int


@dataclass
class Registry:
    modules: dict[str, ModuleManifest] = field(default_factory=dict)
    lessons: dict[str, LessonSpec] = field(default_factory=dict)
    tools: dict[str, ToolSpec] = field(default_factory=dict)
    troubleshooters: dict[str, TroubleshooterSpec] = field(default_factory=dict)
    glossary: Glossary = field(default_factory=Glossary)

    # -- troubleshooter router (T00) -------------------------------------- #
    def search_symptoms(self, query: str) -> list[SymptomMatch]:
        """Deterministic keyword match across all troubleshooter symptoms/aliases."""
        terms = [t for t in re.split(r"\W+", query.lower()) if t]
        matches: list[SymptomMatch] = []
        for ts in self.troubleshooters.values():
            for sym in ts.symptoms:
                haystack = " ".join([sym.label, *sym.aliases]).lower()
                score = sum(1 for t in terms if t in haystack)
                if score:
                    matches.append(
                        SymptomMatch(ts.troubleshooter_id, sym.symptom_id, sym.label, score)
                    )
        matches.sort(key=lambda m: (-m.score, m.label))
        return matches

    def all_symptoms(self) -> list[SymptomMatch]:
        out: list[SymptomMatch] = []
        for ts in self.troubleshooters.values():
            for sym in ts.symptoms:
                out.append(SymptomMatch(ts.troubleshooter_id, sym.symptom_id, sym.label, 0))
        return out

    def categories(self) -> dict[str, list[str]]:
        """Category tag -> tool_ids, for the UI category tabs."""
        cats: dict[str, list[str]] = {}
        for tool in self.tools.values():
            for c in tool.categories:
                cats.setdefault(c, []).append(tool.tool_id)
        return cats


# --------------------------------------------------------------------------- #
#  Loader
# --------------------------------------------------------------------------- #


def _read_yaml(path: Path) -> dict:
    if not path.exists():
        raise ModuleError(f"Content file not found: {path}")
    with path.open("r", encoding="utf-8") as fh:
        data = yaml.safe_load(fh)
    if data is None:
        raise ModuleError(f"Empty content file: {path}")
    return data


def _resolve(module_dir: Path, ref: str) -> list[Path]:
    """Resolve a manifest content ref (relative path or glob) to concrete files."""
    if any(ch in ref for ch in "*?[]"):
        hits = sorted(module_dir.glob(ref))
        if not hits:
            raise ModuleError(f"No files match content glob {ref!r} in {module_dir}")
        return hits
    return [module_dir / ref]


class ModuleLoader:
    """Loads modules from one or more directories into a :class:`Registry`."""

    def __init__(self, registry: Registry | None = None) -> None:
        self.registry = registry or Registry()

    def load_dir(self, modules_root: str | Path) -> Registry:
        root = Path(modules_root)
        if not root.is_dir():
            raise ModuleError(f"Modules root is not a directory: {root}")
        manifests = sorted(root.glob("*/manifest.yaml"))
        if not manifests:
            raise ModuleError(f"No module manifests found under {root}")
        # Load non-router modules first so the router can aggregate them.
        deferred: list[Path] = []
        for mpath in manifests:
            manifest = self._parse_manifest(mpath)
            if manifest.type == "troubleshooter_router":
                deferred.append(mpath)
            else:
                self._load_module(mpath, manifest)
        for mpath in deferred:
            self._load_module(mpath, self._parse_manifest(mpath))
        return self.registry

    # -- internals --------------------------------------------------------- #
    def _parse_manifest(self, mpath: Path) -> ModuleManifest:
        data = _read_yaml(mpath)
        try:
            manifest = ModuleManifest.model_validate(data)
        except Exception as exc:  # pydantic ValidationError -> loud
            raise ModuleError(f"Invalid manifest {mpath}: {exc}") from exc
        if not api_satisfied(manifest.requires.base_api):
            raise ModuleError(
                f"Module {manifest.module_id} requires base_api {manifest.requires.base_api}, "
                f"engine provides {BASE_API_VERSION}."
            )
        return manifest

    def _load_module(self, mpath: Path, manifest: ModuleManifest) -> None:
        module_dir = mpath.parent
        if manifest.module_id in self.registry.modules:
            raise ModuleError(f"Duplicate module_id: {manifest.module_id}")

        # Dependency check (other modules must already be present).
        for dep in manifest.requires.modules:
            if dep not in self.registry.modules:
                raise ModuleError(
                    f"Module {manifest.module_id} requires missing module {dep!r}."
                )

        content = manifest.content

        if manifest.type == "lesson":
            for f in _resolve(module_dir, content["lesson"]):
                lesson = LessonSpec.model_validate(_read_yaml(f))
                self.registry.lessons[lesson.lesson_id] = lesson
        elif manifest.type == "tool":
            for f in _resolve(module_dir, content["tool"]):
                tool = ToolSpec.model_validate(_read_yaml(f))
                self.registry.tools[tool.tool_id] = tool
        elif manifest.type == "troubleshooter":
            for f in _resolve(module_dir, content["troubleshooter"]):
                ts = TroubleshooterSpec.model_validate(_read_yaml(f))
                self.registry.troubleshooters[ts.troubleshooter_id] = ts
        elif manifest.type == "troubleshooter_router":
            # Router owns no content of its own; it aggregates the registry.
            missing = [r for r in manifest.routes_to if r not in self.registry.modules]
            if missing:
                raise ModuleError(
                    f"Router {manifest.module_id} routes to modules not loaded: {missing}"
                )
        elif manifest.type in ("knowledge", "theme"):
            pass  # not exercised in Milestone 1
        else:  # pragma: no cover - guarded by Literal
            raise ModuleError(f"Unknown module type: {manifest.type}")

        # Merge any glossary the module ships.
        if "glossary" in content:
            for f in _resolve(module_dir, content["glossary"]):
                self._load_glossary(f)

        self.registry.modules[manifest.module_id] = manifest

    def _load_glossary(self, path: Path) -> None:
        data = _read_yaml(path)
        terms: Iterable[dict] = data["terms"] if isinstance(data, dict) and "terms" in data else data
        for item in terms:
            term = GlossaryTerm.model_validate(item)
            self.registry.glossary.add(term.term, term.definition)


def load_modules(modules_root: str | Path) -> Registry:
    """Convenience: load every module under ``modules_root`` into a fresh registry."""
    return ModuleLoader().load_dir(modules_root)
