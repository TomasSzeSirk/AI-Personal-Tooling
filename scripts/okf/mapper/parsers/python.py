"""Python parser: `import x` / `from x import y` extraction via regex. Stdlib
only. `rel` is source-root-relative (e.g. "a/b/c.py", not "src/a/b/c.py").

Internal/external split (no repo-wide knowledge available at this layer):
relative imports (leading dots) and multi-segment dotted absolute imports are
treated as internal (in-repo, submodule-style); single-segment absolute
imports are treated as external (stdlib/third-party top-level package).
Unresolved relative-import strings (e.g. ".sibling") are resolved against the
importing file's own module_id downstream, same as Rust's `super`/`self`."""

from __future__ import annotations

import re

EXTENSIONS = {".py"}
LANG = "python"

_BLOCK_STRING = re.compile(r'("""|\'\'\')(?:(?!\1).)*?\1', re.S)
_LINE_COMMENT = re.compile(r"#[^\n]*")


def _strip_comments(src: str) -> str:
    src = _BLOCK_STRING.sub("", src)
    src = _LINE_COMMENT.sub("", src)
    return src


_IMPORT = re.compile(r"(?m)^import\s+([\w.]+(?:\s*,\s*[\w.]+)*)")
_FROM = re.compile(r"(?m)^from\s+(\.+[\w.]*|[\w.]+)\s+import\s+(.+)")


def _parse_imports(src: str) -> tuple[list[str], list[str]]:
    src = _strip_comments(src)
    internal: set[str] = set()
    external: set[str] = set()
    for m in _IMPORT.finditer(src):
        for name in m.group(1).split(","):
            name = name.strip()
            if not name:
                continue
            if "." in name:
                internal.add(name)
            else:
                external.add(name)
    for m in _FROM.finditer(src):
        module = m.group(1).strip()
        if module.startswith("."):
            internal.add(module)
        elif "." in module:
            internal.add(module)
        else:
            external.add(module)
    return sorted(internal), sorted(external)


def module_id(rel: str, src: str) -> str:
    parts = rel[:-len(".py")].split("/") if rel.endswith(".py") else rel.split("/")
    if parts and parts[-1] == "__init__":
        parts = parts[:-1]
    return ".".join(parts)


def internal_imports(src: str) -> list[str]:
    internal, _ = _parse_imports(src)
    return internal


def external_deps(src: str) -> list[str]:
    _, external = _parse_imports(src)
    return external


_TOP_LEVEL_DEF = re.compile(r"(?m)^(?:class|def)\s+([A-Za-z_]\w*)")


def defines(src: str) -> list[str]:
    """Public top-level class/def names (not `_`-prefixed), source order."""
    s = _strip_comments(src)
    names = [n for n in _TOP_LEVEL_DEF.findall(s) if not n.startswith("_")]
    return list(dict.fromkeys(names))


_BARE_RELATIVE_IMPORT = re.compile(r"(?m)^\s*from\s+\.\s+import\s+(.+)")


def submodules(src: str) -> list[str]:
    """Package children: names re-exported via `from . import x, y` (the
    convention typically found in `__init__.py`)."""
    s = _strip_comments(src)
    names: set[str] = set()
    for m in _BARE_RELATIVE_IMPORT.finditer(s):
        for name in m.group(1).split(","):
            name = name.strip()
            if name:
                names.add(name)
    return sorted(names)


_TEST_FILE = re.compile(r"^(test_.*|.*_test)\.py$")
_TEST_FUNC_BODY = re.compile(
    r"(?m)^def\s+(?:test_\w*|\w*_test)\s*\([^)]*\):\n((?:[ \t]+.*\n?)*)"
)


def test_imports(rel: str, src: str) -> list[str]:
    """Internal ids referenced by test code: a whole `test_*.py`/`*_test.py`
    file's imports, or imports found inside `test_*`/`*_test` functions."""
    filename = rel.split("/")[-1]
    s = _strip_comments(src)
    if _TEST_FILE.match(filename):
        internal, _ = _parse_imports(s)
        return internal
    bodies = "\n".join(m.group(1) for m in _TEST_FUNC_BODY.finditer(s))
    dedented = re.sub(r"(?m)^[ \t]+", "", bodies)
    internal, _ = _parse_imports(dedented)
    return internal
