"""TypeScript parser: `import ... from '...'` / `require('...')` extraction
via regex. Stdlib only. `rel` is source-root-relative (e.g. "src/foo/bar.ts").

Relative specifiers (`./x`, `../x`) are returned as-is (unresolved) — resolved
against the importing file's own `rel` downstream, same as Rust's
`super`/`self` and Python's leading-dot imports."""

from __future__ import annotations

import re

EXTENSIONS = {".ts"}
LANG = "typescript"

_BLOCK_COMMENT = re.compile(r"/\*.*?\*/", re.S)
_LINE_COMMENT = re.compile(r"//[^\n]*")


def _strip_comments(src: str) -> str:
    src = _BLOCK_COMMENT.sub("", src)
    src = _LINE_COMMENT.sub("", src)
    return src


_IMPORT_FROM = re.compile(r"""import\s+(?:[^'"]+?\s+from\s+)?['"]([^'"]+)['"]""")
_REQUIRE = re.compile(r"""require\(\s*['"]([^'"]+)['"]\s*\)""")
_EXPORT_FROM = re.compile(r"""export\s+(?:\*|\{[^}]*\})\s+from\s+['"]([^'"]+)['"]""")


def _strip_extension(spec: str) -> str:
    for ext in (".ts", ".tsx", ".js"):
        if spec.endswith(ext):
            return spec[: -len(ext)]
    return spec


def _specifiers(src: str) -> list[str]:
    s = _strip_comments(src)
    specs = [m.group(1) for m in _IMPORT_FROM.finditer(s)]
    specs += [m.group(1) for m in _REQUIRE.finditer(s)]
    return specs


def module_id(rel: str, src: str) -> str:
    return _strip_extension(rel)


def internal_imports(src: str) -> list[str]:
    internal = {
        _strip_extension(spec) for spec in _specifiers(src)
        if spec.startswith("./") or spec.startswith("../")
    }
    return sorted(internal)


def external_deps(src: str) -> list[str]:
    external = {
        spec for spec in _specifiers(src)
        if not (spec.startswith("./") or spec.startswith("../") or spec.startswith("/"))
    }
    return sorted(external)


_EXPORT_NAMED = re.compile(
    r"(?m)^export\s+(?:default\s+)?(?:async\s+)?"
    r"(?:function|class|interface|type|const|let|var)\s+([A-Za-z_$][\w$]*)"
)
_EXPORT_BRACE = re.compile(r"export\s*\{([^}]+)\}(?!\s*from)")


def defines(src: str) -> list[str]:
    """Exported names: `export function/class/interface/type/const foo` plus
    `export { a, b }` lists (not re-exports — see submodules)."""
    s = _strip_comments(src)
    names = list(dict.fromkeys(_EXPORT_NAMED.findall(s)))
    for m in _EXPORT_BRACE.finditer(s):
        for item in m.group(1).split(","):
            item = item.strip()
            if not item:
                continue
            name = item.split(" as ")[-1].strip()
            if name and name not in names:
                names.append(name)
    return names


def submodules(src: str) -> list[str]:
    """Re-exported child modules: `export ... from './x'`."""
    s = _strip_comments(src)
    return sorted({_strip_extension(m.group(1)) for m in _EXPORT_FROM.finditer(s)})


_TEST_FILE = re.compile(r"\.(test|spec)\.tsx?$")


def test_imports(rel: str, src: str) -> list[str]:
    """Internal ids referenced by `*.test.ts`/`*.spec.ts` files."""
    filename = rel.split("/")[-1]
    if not _TEST_FILE.search(filename):
        return []
    return internal_imports(src)
