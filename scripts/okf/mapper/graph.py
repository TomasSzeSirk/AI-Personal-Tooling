"""Digraph resolution: turn each node's parser-native `depends_on` strings
into edges between nodes, by longest-prefix match against a `module_id`
index, then invert to fill `depended_on_by`. Generalized from bit2's
`compute_reverse_edges` (Rust-only) to all four parser languages.

Each language's import strings use a different separator and relative-import
convention, so `module_id`s are only ever matched within their own language
(cross-language imports aren't literal import statements anyway, and would
never share a namespace). Unresolved imports (no matching node) are ignored,
not errors — resolution is best-effort per the plan."""

from __future__ import annotations

import posixpath

from mapper.model import Node

_SPLIT = {
    "rust": "::",
    "python": ".",
    "typescript": "/",
    "go": "/",
}


def _module_parts(module_id: str, lang: str) -> tuple[str, ...]:
    if not module_id:
        return ()
    return tuple(module_id.split(_SPLIT.get(lang, "/")))


def _resolve_path(dep: str, origin: Node) -> "tuple[str, ...] | None":
    """The target module-path (as a tuple of segments in the origin's own
    language namespace) for one raw import string, or None if the syntax
    isn't a recognized internal-import form for that language."""
    own = _module_parts(origin.module_id, origin.lang)

    if origin.lang == "rust":
        segs = dep.split("::")
        head = segs[0]
        if head == "crate":
            return tuple(segs[1:])
        if head == "self":
            return own + tuple(segs[1:])
        if head == "super":
            return own[:-1] + tuple(segs[1:])
        return None

    if origin.lang == "python":
        if dep.startswith("."):
            dots = len(dep) - len(dep.lstrip("."))
            rest = dep[dots:]
            # Relative imports resolve against the *package* containing the
            # module. `__init__.py`'s module_id already *is* its package (the
            # trailing `__init__` segment is stripped in python.module_id);
            # any other module's package is its own module_id minus the file
            # segment. One leading dot = that package itself.
            is_package = origin.rel.split("/")[-1] == "__init__.py"
            base = own if is_package else own[:-1]
            levels = dots - 1
            if levels:
                base = base[:-levels] if levels <= len(base) else ()
            tail = tuple(p for p in rest.split(".") if p)
            return base + tail
        return tuple(dep.split("."))

    if origin.lang == "typescript":
        if dep.startswith("./") or dep.startswith("../"):
            own_dir = posixpath.dirname(origin.module_id)
            resolved = posixpath.normpath(posixpath.join(own_dir, dep))
            return tuple(p for p in resolved.split("/") if p and p != ".")
        return tuple(dep.split("/"))

    if origin.lang == "go":
        return tuple(dep.split("/"))

    return None


ModuleIndex = "dict[str, dict[tuple[str, ...], Node]]"


def build_index(nodes: list[Node]) -> ModuleIndex:
    """`{lang -> {module_path -> Node}}`, the per-language `module_id` index
    used by the longest-prefix resolver below. Shared by digraph resolution
    (this module) and the `tested_by` overlay (`tests_overlay.py`) so both
    resolve raw import strings to nodes the same way."""
    by_module: ModuleIndex = {}
    for n in nodes:
        by_module.setdefault(n.lang, {})[_module_parts(n.module_id, n.lang)] = n
    return by_module


def resolve_dep(dep: str, origin: Node, by_module: ModuleIndex) -> "Node | None":
    """The node one raw import string (`dep`, in `origin`'s language) resolves
    to via longest module-path-prefix match, or None if unresolved. `origin`
    only needs `.lang` and `.module_id` (a lightweight stand-in works, e.g. for
    test source that isn't itself a graph node)."""
    path = _resolve_path(dep, origin)
    if not path:
        return None
    index = by_module.get(origin.lang, {})
    for length in range(len(path), 0, -1):  # longest prefix wins
        hit = index.get(path[:length])
        if hit is not None:
            return hit
    return None


def resolve(nodes: list[Node]) -> None:
    """Populate `depends_on` (resolved target `rel`s) and `depended_on_by`
    (its inversion) in place. Self-edges are dropped."""
    by_module = build_index(nodes)

    resolved_out: dict[str, set[str]] = {n.rel: set() for n in nodes}
    reverse: dict[str, set[str]] = {n.rel: set() for n in nodes}

    for n in nodes:
        for dep in n.depends_on:
            target = resolve_dep(dep, n, by_module)
            if target is None or target.rel == n.rel:
                continue
            resolved_out[n.rel].add(target.rel)
            reverse[target.rel].add(n.rel)

    for n in nodes:
        n.depends_on = sorted(resolved_out[n.rel])
        n.depended_on_by = sorted(reverse[n.rel])
