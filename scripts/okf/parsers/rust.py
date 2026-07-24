"""Rust parser: comment/test stripping and `use`/`mod` extraction via regex.
Ported from bit2-timestamp-server's scripts/okf/parsing.py + model.py's
`_module_path`. Stdlib only. `rel` is source-root-relative (e.g.
"committer/service/submit.rs", not "src/committer/service/submit.rs")."""

from __future__ import annotations

import re

EXTENSIONS = {".rs"}
LANG = "rust"

# ---------------------------------------------------------------------------
# Comment / test-module stripping (avoid false-positive imports)
# ---------------------------------------------------------------------------

_BLOCK_COMMENT = re.compile(r"/\*.*?\*/", re.S)
_LINE_COMMENT = re.compile(r"//[^\n]*")


def _strip_comments(src: str) -> str:
    src = _BLOCK_COMMENT.sub("", src)
    src = _LINE_COMMENT.sub("", src)
    return src


_TEST_MOD = re.compile(r"(?:#\[cfg\(test\)\]\s*)?(?:pub\s+)?mod\s+tests\s*\{")


def _strip_test_modules(src: str) -> str:
    """Excise `mod tests { ... }` blocks — test-only imports are not
    architecture dependencies."""
    out, i = [], 0
    while True:
        m = _TEST_MOD.search(src, i)
        if not m:
            out.append(src[i:])
            break
        out.append(src[i:m.start()])
        depth, j = 1, m.end()  # walk to matching closing brace
        while j < len(src) and depth:
            c = src[j]
            if c == "{":
                depth += 1
            elif c == "}":
                depth -= 1
            j += 1
        i = j
    return "".join(out)


def _extract_test_modules(src: str) -> str:
    """Inverse of _strip_test_modules: contents of `mod tests` blocks only."""
    out, i = [], 0
    while True:
        m = _TEST_MOD.search(src, i)
        if not m:
            break
        depth, j = 1, m.end()
        while j < len(src) and depth:
            c = src[j]
            if c == "{":
                depth += 1
            elif c == "}":
                depth -= 1
            j += 1
        out.append(src[m.end():j - 1])  # inside the braces
        i = j
    return "\n".join(out)


# ---------------------------------------------------------------------------
# Import parsing
# ---------------------------------------------------------------------------

_USE = re.compile(r"\buse\s+(.+?);", re.S)
_MOD = re.compile(r"^\s*(?:pub\s+)?mod\s+(\w+)\s*;", re.M)

_INTERNAL_ROOTS = {"crate", "super", "self"}


def _expand_braces(path: str) -> list[str]:
    """Expand one `prefix::{a, b::c, d}` group into full paths. Single level."""
    path = re.sub(r"\s+", "", path)
    if "{" not in path:
        return [path]
    head, _, rest = path.partition("{")
    inner = rest.rsplit("}", 1)[0]
    head = head.rstrip(":")
    items, depth, buf = [], 0, ""
    for ch in inner:  # split top-level commas only
        if ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
        if ch == "," and depth == 0:
            items.append(buf)
            buf = ""
        else:
            buf += ch
    if buf:
        items.append(buf)
    out = []
    for it in items:
        if not it or it == "self":
            out.append(head)
        else:
            for sub in _expand_braces(it):
                out.append(f"{head}::{sub}" if head else sub)
    return out


def _internal_imports_from_chunk(chunk: str) -> list[str]:
    """Internal (crate/super/self) imports from a raw source chunk, 3-seg
    truncated. Used both for production code and for the contents of `mod
    tests` blocks."""
    internal: set[str] = set()
    for m in _USE.finditer(chunk):
        for full in _expand_braces(m.group(1)):
            segs = full.split("::")
            if segs[0] in _INTERNAL_ROOTS:
                internal.add("::".join(segs[:3]))
    return sorted(internal)


def _parse_imports(src: str) -> tuple[list[str], list[str]]:
    """(internal_deps, external_crates), excluding test-only imports."""
    src = _strip_test_modules(_strip_comments(src))
    internal: set[str] = set()
    external: set[str] = set()
    for m in _USE.finditer(src):
        for full in _expand_braces(m.group(1)):
            segs = full.split("::")
            root = segs[0]
            if root in _INTERNAL_ROOTS:
                internal.add("::".join(segs[:3]))
            elif root and root != "std":
                external.add(root)
    return sorted(internal), sorted(external)


# ---------------------------------------------------------------------------
# Public parser interface
# ---------------------------------------------------------------------------

def _module_parts(rel: str) -> tuple[str, ...]:
    """Module path for a node, source-root-relative: committer/service/
    submit.rs -> ('committer','service','submit'); committer/mod.rs ->
    ('committer',) — a mod.rs *is* its directory's module."""
    if not rel.endswith(".rs"):
        return (rel,)
    parts = rel[:-len(".rs")].split("/")
    if parts and parts[-1] == "mod":
        parts = parts[:-1]
    return tuple(parts) if parts else ("",)


def module_id(rel: str, src: str) -> str:
    return "::".join(_module_parts(rel))


def internal_imports(src: str) -> list[str]:
    internal, _ = _parse_imports(src)
    return internal


def external_deps(src: str) -> list[str]:
    _, external = _parse_imports(src)
    return external


_PUB_TYPE = re.compile(r"(?m)^\s*pub(?:\([^)]*\))?\s+(?:struct|trait|enum)\s+(\w+)")
_PUB_FN = re.compile(
    r"(?m)^\s*pub(?:\([^)]*\))?\s+(?:async\s+)?(?:unsafe\s+)?(?:extern\s+\"[^\"]*\"\s+)?fn\s+(\w+)"
)


def defines(src: str) -> list[str]:
    """Public type surface: `pub struct/trait/enum` names, in source order
    (order-preserving dedup). Falls back to `pub fn` names only when the file
    declares no public types. Test-only defs excluded."""
    s = _strip_test_modules(_strip_comments(src))
    types = list(dict.fromkeys(_PUB_TYPE.findall(s)))
    if types:
        return types
    return list(dict.fromkeys(_PUB_FN.findall(s)))


def submodules(src: str) -> list[str]:
    return sorted({m.group(1) for m in _MOD.finditer(_strip_comments(src))})


def test_imports(rel: str, src: str) -> list[str]:
    """Internal imports found inside `mod tests` blocks."""
    return _internal_imports_from_chunk(_strip_comments(_extract_test_modules(src)))


_VIS = r"(?:pub\s+)?(?:pub\([^)]*\)\s+)?"  # optional visibility: pub / pub(crate)
_MOD_DECL = re.compile(rf"(?m)^\s*{_VIS}mod\s+\w+\s*;")
_USE_STMT = re.compile(rf"(?ms)^[ \t]*{_VIS}use\s+.+?;")  # incl. multi-line braces
_ATTR = re.compile(r"#!?\[[^\]]*\]")


def is_trivial_mod(src: str) -> bool:
    """True for a `mod.rs` that is a pure aggregator — only `mod`/`use`
    re-exports (any visibility) and attributes, no real code."""
    s = _strip_comments(src)
    s = _ATTR.sub("", s)
    s = _USE_STMT.sub("", s)
    s = _MOD_DECL.sub("", s)
    return s.strip() == ""
