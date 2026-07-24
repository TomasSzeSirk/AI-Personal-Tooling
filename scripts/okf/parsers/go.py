"""Go parser: `import ( ... )` / `import "..."` extraction via regex. Stdlib
only. `rel` is source-root-relative (e.g. "pkg/foo/bar.go"); Go packages are
per-directory, so module_id is the directory portion of rel.

Internal/external split is best-effort (no go.mod parsing here): import paths
containing a dot in their first segment (domain-qualified, e.g.
"github.com/...") are external, as are a small set of well-known stdlib
paths; everything else is treated as module-local/internal.
# ponytail: without go.mod's module path this can't be exact — misclassifies
# any dotless stdlib package not in _STDLIB as internal. Upgrade by reading
# go.mod's `module` line if this proves noisy in practice.
"""

from __future__ import annotations

import re

EXTENSIONS = {".go"}
LANG = "go"

_STDLIB = {
    "fmt", "os", "strings", "strconv", "context", "errors", "time", "sync",
    "io", "bytes", "sort", "testing", "reflect", "regexp", "math", "unicode",
    "encoding/json", "net/http", "path/filepath", "sync/atomic", "os/exec",
}

_BLOCK_COMMENT = re.compile(r"/\*.*?\*/", re.S)
_LINE_COMMENT = re.compile(r"//[^\n]*")


def _strip_comments(src: str) -> str:
    src = _BLOCK_COMMENT.sub("", src)
    src = _LINE_COMMENT.sub("", src)
    return src


_IMPORT_BLOCK = re.compile(r"import\s*\(([^)]*)\)", re.S)
_IMPORT_SINGLE = re.compile(r'(?m)^import\s+(?:\w+\s+)?"([^"]+)"')
_PATH_IN_BLOCK = re.compile(r'(?:\w+\s+)?"([^"]+)"')


def _import_paths(src: str) -> list[str]:
    s = _strip_comments(src)
    paths = []
    for m in _IMPORT_BLOCK.finditer(s):
        paths += _PATH_IN_BLOCK.findall(m.group(1))
    paths += _IMPORT_SINGLE.findall(s)
    return paths


def _is_external(path: str) -> bool:
    if path in _STDLIB:
        return True
    head = path.split("/", 1)[0]
    return "." in head


def module_id(rel: str, src: str) -> str:
    if "/" not in rel:
        return "."
    return rel.rsplit("/", 1)[0]


def internal_imports(src: str) -> list[str]:
    return sorted({p for p in _import_paths(src) if not _is_external(p)})


def external_deps(src: str) -> list[str]:
    return sorted({p for p in _import_paths(src) if _is_external(p)})


_TOP_FUNC = re.compile(r"(?m)^func\s+([A-Z]\w*)\s*\(")
_TOP_TYPE = re.compile(r"(?m)^type\s+([A-Z]\w*)\s+")


def defines(src: str) -> list[str]:
    """Exported (CamelCase) top-level type/func names, in source order."""
    s = _strip_comments(src)
    names = []
    ordered = sorted(
        [(m.start(), m.group(1)) for m in _TOP_FUNC.finditer(s)]
        + [(m.start(), m.group(1)) for m in _TOP_TYPE.finditer(s)]
    )
    for _, name in ordered:
        if name not in names:
            names.append(name)
    return names


def submodules(src: str) -> list[str]:
    """Go has no nested modules within a package."""
    return []


_TEST_FILE = re.compile(r"_test\.go$")


def test_imports(rel: str, src: str) -> list[str]:
    """Internal ids referenced by `*_test.go` files."""
    filename = rel.split("/")[-1]
    if not _TEST_FILE.search(filename):
        return []
    return internal_imports(src)
