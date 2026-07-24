"""Markdown emission: per-node `.md` frontmatter, the root `index.md`, and one
sharded `<domain>/_index.md` table per domain. Generalized from bit2's
render.py — language-neutral, no hexagonal-specific fields."""

from __future__ import annotations

import os

from mapper.model import Node
from mapper.storage import write_if_changed

DOMAIN_INDEX_NAME = "_index.md"
DOMAIN_INDEX_MARKER = "---\ntype: knowledge_graph_domain_index"
NODE_MARKER = "---\ntype: okf_module"  # first line of every generated node


def _yaml_flow(items: list[str]) -> str:
    """Inline flow sequence: ` [a, b, c]`. Import ids / paths don't contain
    YAML flow indicators (`,[]{}`), so they stay plain and unquoted."""
    return " []" if not items else " [" + ", ".join(items) + "]"


def render_node(node: Node) -> str:
    lines = [
        "---",
        "type: okf_module",
        f"source: {node.rel}",
        f"lang: {node.lang}",
        f"domain: {node.domain}",
    ]
    if node.layer:
        lines.append(f"layer: {node.layer}")
    lines += [
        f"defines:{_yaml_flow(node.defines)}",
        f"depends_on:{_yaml_flow(node.depends_on)}",
        f"depended_on_by:{_yaml_flow(node.depended_on_by)}",
        f"external:{_yaml_flow(node.external)}",
        f"submodules:{_yaml_flow(node.submodules)}",
        f"tested_by:{_yaml_flow(node.tested_by)}",
    ]
    if node.violations:
        lines.append(f"violations:{_yaml_flow(node.violations)}")
    lines += ["---", ""]
    if node.violations:
        lines.append("## ⚠ Violations\n")
        lines += [f"- ⚠ {v}" for v in node.violations]
        lines.append("")
    return "\n".join(lines)


def write_node(node: Node, output_path: str) -> bool:
    path = os.path.join(output_path, node.node_file)
    os.makedirs(os.path.dirname(path) or output_path, exist_ok=True)
    return write_if_changed(path, render_node(node))


def _table_defines(n: Node) -> str:
    return ", ".join(f"`{name}`" for name in n.defines)


def _group_by_domain(nodes: list[Node]) -> dict[str, list[Node]]:
    by_domain: dict[str, list[Node]] = {}
    for n in nodes:
        by_domain.setdefault(n.domain, []).append(n)
    return by_domain


def build_domain_index(domain: str, dnodes: list[Node]) -> str:
    edges = sum(len(n.depends_on) for n in dnodes)
    violations = sum(len(n.violations) for n in dnodes)
    rows = "\n".join(
        f"| `{n.lang}` | [`{n.rel}`](../{n.node_file}) "
        f"| {_table_defines(n)} | {len(n.depends_on)} | {len(n.depended_on_by)} "
        f"| {'⚠ ' if n.violations else ''}{len(n.violations)} |"
        for n in sorted(dnodes, key=lambda x: (x.lang, x.rel))
    )
    return (
        "---\n"
        "type: knowledge_graph_domain_index\n"
        f"domain: {domain}\n"
        f"nodes: {len(dnodes)}\n"
        f"edges: {edges}\n"
        f"violations: {violations}\n"
        "---\n\n"
        f"# OKF — {domain}\n\n"
        "**Defines** = public surface; **Out** = internal deps (fan-out); "
        "**In** = fan-in (reverse edges); **Viol** = policy violations. "
        "Back to [index](../index.md).\n\n"
        "| Lang | Module | Defines | Out | In | Viol |\n"
        "|------|--------|---------|-----|----|------|\n"
        f"{rows}\n"
    )


def write_domain_index(domain: str, dnodes: list[Node], output_path: str) -> bool:
    path = os.path.join(output_path, domain, DOMAIN_INDEX_NAME)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    return write_if_changed(path, build_domain_index(domain, dnodes))


def build_index(nodes: list[Node], roots: list[str]) -> str:
    edges = sum(len(n.depends_on) for n in nodes)
    violations = sum(len(n.violations) for n in nodes)
    by_domain = _group_by_domain(nodes)

    lang_counts: dict[str, int] = {}
    for n in nodes:
        lang_counts[n.lang] = lang_counts.get(n.lang, 0) + 1
    lang_mix = ", ".join(f"{lang}: {count}" for lang, count in sorted(lang_counts.items()))

    domain_rows = "\n".join(
        f"| [`{d}`]({d}/{DOMAIN_INDEX_NAME}) | {len(by_domain[d])} "
        f"| {sum(len(n.depends_on) for n in by_domain[d])} "
        f"| {sum(len(n.violations) for n in by_domain[d])} |"
        for d in sorted(by_domain)
    )

    return (
        "---\n"
        "type: knowledge_graph_index\n"
        "title: OKF Knowledge Graph\n"
        f"nodes: {len(nodes)}\n"
        f"edges: {edges}\n"
        f"domains: {len(by_domain)}\n"
        f"violations: {violations}\n"
        "---\n\n"
        "# OKF Knowledge Graph — Index\n\n"
        f"Source: `{', '.join(roots)}` · Nodes: **{len(nodes)}** · Edges: **{edges}** "
        f"· Domains: **{len(by_domain)}** · Violations: **{violations}**\n\n"
        f"Language mix: {lang_mix}\n\n"
        "Sharded by domain — open one `<domain>/_index.md` for its file table "
        "instead of loading every domain. Each row's module links to a node "
        "`.md`; read that instead of the source to recall context cheaply.\n\n"
        "| Domain | Nodes | Edges | Violations |\n"
        "|--------|-------|-------|------------|\n"
        f"{domain_rows}\n"
    )
