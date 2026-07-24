"""The `tested_by` overlay: attribute test code to the nodes it exercises, as
output kept fully separate from `depends_on`/`depended_on_by`/`violations`.
Generalized from bit2-timestamp-server's `compute_test_edges`. Reuses
`graph.py`'s module_id index + longest-prefix resolver (`build_index`/
`resolve_dep`) for every resolution step, rather than reimplementing it.

Two kinds of test source:
  - inline (`Node.test_imports`, already produced by the Stage 2 parsers) —
    raw import strings resolved in the containing node's own namespace via
    `graph.resolve_dep`, attributed with an "(inline)" label.
  - whole-file test sources (a file that *is* test code, per a per-language
    naming convention) — for Python/TypeScript/Go these are already ordinary
    graph nodes (scanned like any other file), so their `depends_on`/
    `depended_on_by` edges (already resolved by `graph.resolve`) are moved
    from the digraph into `tested_by`. Rust's convention is the sibling
    `tests/` integration dir, which sits *outside* the source root entirely
    and is never scanned into a node — its files are walked here directly.
"""

from __future__ import annotations

import os
import re
from dataclasses import dataclass

from okf.graph import build_index, resolve_dep
from okf.model import Node
from okf.storage import SKIP_DIRS

_PY_TEST_FILE = re.compile(r"^(test_.*|.*_test)\.py$")
_TS_TEST_FILE = re.compile(r"\.(test|spec)\.tsx?$")
_GO_TEST_FILE = re.compile(r"_test\.go$")
_CARGO_NAME = re.compile(r'(?m)^\s*name\s*=\s*"([^"]+)"')


def _is_whole_test_file(rel: str, lang: str) -> bool:
    """A file that *is* test code by a per-language naming convention (whole-
    file test source, as opposed to inline test code inside a normal file)."""
    name = rel.split("/")[-1]
    if lang == "python":
        return bool(_PY_TEST_FILE.match(name)) or "tests" in rel.split("/")[:-1]
    if lang == "typescript":
        return bool(_TS_TEST_FILE.search(name))
    if lang == "go":
        return bool(_GO_TEST_FILE.search(name))
    return False


@dataclass
class _VirtualOrigin:
    """A stand-in for `Node` used to resolve imports in test source that isn't
    itself a graph node (Rust's sibling `tests/` integration files) — carries
    just enough for `graph.resolve_dep`."""

    module_id: str
    lang: str


def _crate_name(root: str) -> "str | None":
    """The crate's import identifier (Cargo.toml `name`, `-` -> `_`), read
    from the Cargo.toml next to `root`. Integration tests import via this
    name, not `crate::`."""
    cargo = os.path.join(os.path.dirname(os.path.abspath(root.rstrip("/\\"))), "Cargo.toml")
    try:
        text = open(cargo, encoding="utf-8").read()
    except OSError:
        return None
    m = _CARGO_NAME.search(text)
    return m.group(1).replace("-", "_") if m else None


def _rust_integration_tests(root: str, by_module: dict, tested: "dict[str, set[str]]") -> None:
    """Sibling `tests/` dir next to `root`: the whole file is test code. It
    imports the crate by package name, so rewrite that to `crate::` before
    resolving (bit2's approach)."""
    from okf.parsers import rust

    tests_dir = os.path.join(os.path.dirname(os.path.abspath(root.rstrip("/\\"))), "tests")
    if not os.path.isdir(tests_dir):
        return
    crate = _crate_name(root)
    origin = _VirtualOrigin(module_id="", lang="rust")

    for dirpath, dirs, files in os.walk(tests_dir):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        for name in files:
            if not name.endswith(".rs"):
                continue
            try:
                with open(os.path.join(dirpath, name), encoding="utf-8", errors="ignore") as f:
                    src = f.read()
            except OSError:
                continue
            if crate:
                src = src.replace(f"{crate}::", "crate::")
            label = "tests/" + os.path.relpath(
                os.path.join(dirpath, name), tests_dir
            ).replace(os.sep, "/")
            for dep in rust.internal_imports(src):
                if not dep.startswith("crate::"):
                    continue  # self/super are unresolvable outside a module context
                target = resolve_dep(dep, origin, by_module)
                if target is not None:
                    tested[target.rel].add(label)


def compute(nodes: list[Node], roots: list[str]) -> None:
    """Populate each node's `tested_by` in place, and strip whole-file test
    nodes' edges out of `depends_on`/`depended_on_by` (they never represent
    architecture dependencies). Must run after `graph.resolve` (needs
    resolved edges) and after policy (violations are computed from the
    pre-overlay digraph, per the plan)."""
    by_module = build_index(nodes)
    by_rel = {n.rel: n for n in nodes}
    tested: dict[str, set[str]] = {n.rel: set() for n in nodes}

    # Inline test code: raw import strings resolved in the containing node's
    # own namespace, same resolver as the production digraph.
    for n in nodes:
        if _is_whole_test_file(n.rel, n.lang):
            continue
        for dep in n.test_imports:
            target = resolve_dep(dep, n, by_module)
            if target is not None:
                tested[target.rel].add(f"{n.rel} (inline)")

    # Whole-file test nodes (Python/TypeScript/Go conventions): their already-
    # resolved depends_on/depended_on_by edges are test refs, not dependency
    # edges — move them into tested_by and remove them from the digraph.
    for n in nodes:
        if not _is_whole_test_file(n.rel, n.lang):
            continue
        for target_rel in list(n.depends_on):
            target = by_rel.get(target_rel)
            if target is None:
                continue
            tested[target_rel].add(n.rel)
            target.depended_on_by = [r for r in target.depended_on_by if r != n.rel]
        n.depends_on = []

    # Rust's sibling tests/ integration dir sits outside the source root and
    # is never scanned into a node — walked directly, per root.
    for root in roots:
        _rust_integration_tests(root, by_module, tested)

    for n in nodes:
        n.tested_by = sorted(tested[n.rel])
