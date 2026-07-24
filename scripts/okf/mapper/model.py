"""The OKF graph model: the Node dataclass and the source scan that builds one
node per parseable file, language-dispatched via the parser registry."""

from __future__ import annotations

import fnmatch
import os
from dataclasses import dataclass, field

from mapper.classify import domain as classify_domain
from mapper.parsers import for_ext
from mapper.storage import SKIP_DIRS


@dataclass
class Node:
    """One OKF graph node: a single source file and its resolved metadata."""

    rel: str                       # repo-relative path incl. root (node id)
    node_file: str                 # node .md path, flattened
    title: str                     # file stem
    lang: str
    domain: str
    module_id: str                 # parser-native id, resolved against root-relative path
    defines: list[str]
    depends_on: list[str]
    external: list[str]
    submodules: list[str]
    layer: "str | None" = None
    depended_on_by: list[str] = field(default_factory=list)   # reverse edges (rels)
    tested_by: list[str] = field(default_factory=list)        # test refs (Stage 5)
    test_imports: list[str] = field(default_factory=list)     # internal; not rendered (Stage 5)
    violations: list[str] = field(default_factory=list)       # policy flags (Stage 4)


def _root_relative(rel: str, root_name: str) -> str:
    """`rel` (repo-relative, incl. root) with the root prefix stripped, for
    the parser's `rel` argument — parsers were written expecting a source-
    root-relative path (e.g. "okf/map.py" under root "scripts"). `rel` always
    starts with the root's own basename (see `scan`), so stripping is done
    against that basename, not the raw (possibly absolute) root string."""
    prefix = root_name + "/"
    return rel[len(prefix):] if rel.startswith(prefix) else rel


def _node_file(rel: str) -> str:
    """Node `.md` path: the repo-relative tree flattened into one filename
    (no subdirectories) so multi-root/multi-language trees never collide and
    Windows separators never leak into the cache key."""
    return rel.replace("/", "__") + ".md"


def scan(
    roots: list[str], ignore: "list[str] | None" = None
) -> tuple[list[Node], int, list[str]]:
    """Walk each root, building one Node per file whose extension a parser
    registers. Returns (nodes, skipped_unknown_count, errors). A single bad
    file is recorded in `errors` (and skipped) without aborting the run."""
    ignore = ignore or []
    nodes: list[Node] = []
    skipped_unknown = 0
    errors: list[str] = []

    for root in roots:
        root_name = os.path.basename(root.rstrip(os.sep).replace("\\", "/"))
        if not os.path.isdir(root):
            continue
        for dirpath, dirs, files in os.walk(root):
            dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
            for name in files:
                abs_path = os.path.join(dirpath, name)
                rel = os.path.relpath(abs_path, os.path.dirname(root.rstrip(os.sep)) or ".")
                rel = rel.replace(os.sep, "/")

                if any(fnmatch.fnmatch(rel, pat) for pat in ignore):
                    continue

                ext = os.path.splitext(name)[1]
                parser = for_ext(ext)
                if parser is None:
                    skipped_unknown += 1
                    continue

                try:
                    with open(abs_path, "rb") as f:
                        raw = f.read()
                    src = raw.decode("utf-8", errors="ignore")
                    root_rel = _root_relative(rel, root_name)
                    node = Node(
                        rel=rel,
                        node_file=_node_file(rel),
                        title=os.path.splitext(name)[0],
                        lang=parser.LANG,
                        domain=classify_domain(rel, roots),
                        module_id=parser.module_id(root_rel, src),
                        defines=parser.defines(src),
                        depends_on=parser.internal_imports(src),
                        external=parser.external_deps(src),
                        submodules=parser.submodules(src),
                        test_imports=parser.test_imports(root_rel, src),
                    )
                except Exception as e:  # noqa: BLE001 - one bad file must not abort the run
                    errors.append(f"{rel}: {e}")
                    continue
                nodes.append(node)

    nodes.sort(key=lambda n: n.rel)
    return nodes, skipped_unknown, errors
