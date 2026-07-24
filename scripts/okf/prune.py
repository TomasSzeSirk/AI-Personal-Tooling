"""Pruning of derived output: node `.md` files and domain indexes whose
source no longer exists. Keeps the corpus purely derived without deleting
hand-added files. Ported from bit2's prune.py — language-neutral."""

from __future__ import annotations

import os

from okf.model import Node
from okf.render import DOMAIN_INDEX_MARKER, DOMAIN_INDEX_NAME, NODE_MARKER
from okf.storage import SKIP_DIRS


def _prune_empty_dirs(output_path: str) -> None:
    for d, _dirs, _files in os.walk(output_path, topdown=False):
        if os.path.abspath(d) == os.path.abspath(output_path):
            continue
        try:
            os.rmdir(d)
        except OSError:
            pass


def _has_marker(path: str, marker: str) -> bool:
    try:
        return open(path, encoding="utf-8").read(len(marker)) == marker
    except OSError:
        return False


def prune_orphans(
    nodes: list[Node], live_domains: set[str], output_path: str
) -> tuple[list[str], list[str]]:
    """Single walk of the derived output tree, deleting both kinds of orphan:
    node `.md` files whose source no longer exists, and `<domain>/_index.md`
    shards whose domain no longer has any node. Only files carrying the
    matching generated marker are removed. Returns (removed_nodes,
    removed_indexes)."""
    keep = {n.node_file for n in nodes}
    removed_nodes: list[str] = []
    removed_indexes: list[str] = []
    for root, dirs, files in os.walk(output_path):
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        for name in files:
            if not name.endswith(".md"):
                continue
            path = os.path.join(root, name)
            relnode = os.path.relpath(path, output_path).replace(os.sep, "/")
            if relnode == "index.md":
                continue
            if name == DOMAIN_INDEX_NAME:
                domain = os.path.relpath(root, output_path).replace(os.sep, "/")
                if domain not in live_domains and _has_marker(path, DOMAIN_INDEX_MARKER):
                    os.remove(path)
                    removed_indexes.append(relnode)
                continue
            if relnode not in keep and _has_marker(path, NODE_MARKER):
                os.remove(path)
                removed_nodes.append(relnode)
    _prune_empty_dirs(output_path)
    return sorted(removed_nodes), sorted(removed_indexes)
