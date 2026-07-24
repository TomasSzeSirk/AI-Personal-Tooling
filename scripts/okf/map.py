"""OKF mapper CLI — regenerates docs/okf from source.

Usage: python map.py [--source ...] [--output ...] [--quiet] [--no-prune]
       python map.py --self-test
       python map.py --version
"""

from __future__ import annotations

import os
import sys
import tempfile
from pathlib import Path

# Runnable directly as `python map.py` (dev) or `python scripts/okf/map.py`
# (repo/vendored layout): put the parent of okf/ on sys.path so `okf` and
# `okf.config` import the same way in both cases.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from okf import __version__  # noqa: E402
from okf import config  # noqa: E402
from okf.classify import assign_layer  # noqa: E402
from okf.config import ConfigError  # noqa: E402
from okf.graph import resolve as resolve_graph  # noqa: E402
from okf.model import Node, scan  # noqa: E402
from okf.parsers import for_ext  # noqa: E402
from okf.parsers import go as go_parser  # noqa: E402
from okf.parsers import python as python_parser  # noqa: E402
from okf.parsers import rust as rust_parser  # noqa: E402
from okf.parsers import typescript as ts_parser  # noqa: E402
from okf.policy import compile_policy  # noqa: E402
from okf.prune import prune_orphans  # noqa: E402
from okf.render import build_domain_index, build_index, write_domain_index, write_node  # noqa: E402
from okf.storage import write_if_changed  # noqa: E402
from okf import tests_overlay  # noqa: E402


def generate(
    roots: list[str],
    output: str,
    prune: bool = True,
    layer_rule: "list[dict] | None" = None,
    policy_cfg: "dict | None" = None,
) -> dict:
    os.makedirs(output, exist_ok=True)

    nodes, skipped_unknown, errors = scan(roots)
    resolve_graph(nodes)

    for n in nodes:
        n.layer = assign_layer(n.rel, layer_rule)

    policy = compile_policy(policy_cfg)
    if policy is not None:
        nodes_by_rel = {n.rel: n for n in nodes}
        for n in nodes:
            n.violations = policy.check(n, nodes_by_rel)

    tests_overlay.compute(nodes, roots)

    nodes_written = sum(write_node(n, output) for n in nodes)

    by_domain: dict[str, list] = {}
    for n in nodes:
        by_domain.setdefault(n.domain, []).append(n)
    domain_indexes_written = sum(
        write_domain_index(d, dnodes, output) for d, dnodes in by_domain.items()
    )

    index_md = build_index(nodes, roots)
    index_changed = write_if_changed(os.path.join(output, "index.md"), index_md)

    if prune:
        pruned_nodes, pruned_indexes = prune_orphans(nodes, set(by_domain), output)
    else:
        pruned_nodes, pruned_indexes = [], []

    return {
        "status": "ok",
        "nodes_created": len(nodes),
        "nodes_written": nodes_written,
        "domain_indexes_written": domain_indexes_written,
        "index_changed": index_changed,
        "edges": sum(len(n.depends_on) for n in nodes),
        "skipped_unknown": skipped_unknown,
        "errors": errors,
        "violations": sum(1 for n in nodes if n.violations),
        "pruned_nodes": pruned_nodes,
        "pruned_indexes": pruned_indexes,
        "index_path": os.path.join(output, "index.md"),
        "index_md": index_md,
    }


def _self_test() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)

        # Absent file -> defaults.
        cfg = config.load(tmp_path / "no-such-okf.toml")
        assert cfg.source == ["src"]
        assert cfg.output == "docs/okf"
        assert cfg.ignore == []
        assert cfg.layer_rule is None
        assert cfg.policy is None
        assert cfg.warnings == []

        # Valid file, string source -> normalized to list.
        toml_file = tmp_path / "okf.toml"
        toml_file.write_text('source = "app"\noutput = "out"\n', encoding="utf-8")
        cfg = config.load(toml_file)
        assert cfg.source == ["app"]
        assert cfg.output == "out"

        # List source stays a list.
        toml_file.write_text('source = ["app", "lib"]\n', encoding="utf-8")
        cfg = config.load(toml_file)
        assert cfg.source == ["app", "lib"]

        # Malformed TOML -> ConfigError.
        toml_file.write_text("this is not [valid toml", encoding="utf-8")
        try:
            config.load(toml_file)
            assert False, "expected ConfigError for malformed TOML"
        except ConfigError:
            pass

        # Non-UTF-8 encoded file (e.g. UTF-16) -> ConfigError.
        toml_file.write_bytes('source = "x"\n'.encode("utf-16"))
        try:
            config.load(toml_file)
            assert False, "expected ConfigError for UTF-16 config"
        except ConfigError:
            pass

        # Bad type for source -> ConfigError.
        toml_file.write_text("source = 5\n", encoding="utf-8")
        try:
            config.load(toml_file)
            assert False, "expected ConfigError for bad 'source' type"
        except ConfigError:
            pass

        # Bad type for output -> ConfigError.
        toml_file.write_text("output = 5\n", encoding="utf-8")
        try:
            config.load(toml_file)
            assert False, "expected ConfigError for bad 'output' type"
        except ConfigError:
            pass

        # Unknown policy.kind -> ConfigError.
        toml_file.write_text(
            '[policy]\nkind = "sideways"\norder = ["a", "b"]\n', encoding="utf-8"
        )
        try:
            config.load(toml_file)
            assert False, "expected ConfigError for unknown policy.kind"
        except ConfigError:
            pass

        # Directional policy missing 'order' -> ConfigError.
        toml_file.write_text('[policy]\nkind = "inward"\n', encoding="utf-8")
        try:
            config.load(toml_file)
            assert False, "expected ConfigError for missing policy.order"
        except ConfigError:
            pass

        # Allowlist policy with malformed 'allow' -> ConfigError.
        toml_file.write_text(
            '[policy]\nkind = "allowlist"\nallow = ["a", "b"]\n', encoding="utf-8"
        )
        try:
            config.load(toml_file)
            assert False, "expected ConfigError for malformed policy.allow"
        except ConfigError:
            pass

        # Policy layer with a matching layer_rule -> no warning.
        toml_file.write_text(
            "[[layer_rule]]\n"
            'glob = "domain/**"\n'
            'layer = "domain"\n'
            "[[layer_rule]]\n"
            'glob = "adapter/**"\n'
            'layer = "adapter"\n'
            "[policy]\n"
            'kind = "inward"\n'
            'order = ["domain", "adapter"]\n',
            encoding="utf-8",
        )
        cfg = config.load(toml_file)
        assert cfg.warnings == []

        # Policy layer with no assigning layer_rule -> warning, not fatal.
        toml_file.write_text(
            "[[layer_rule]]\n"
            'glob = "domain/**"\n'
            'layer = "domain"\n'
            "[policy]\n"
            'kind = "inward"\n'
            'order = ["domain", "adapter"]\n',
            encoding="utf-8",
        )
        cfg = config.load(toml_file)
        assert len(cfg.warnings) == 1
        assert "adapter" in cfg.warnings[0]

    _self_test_parsers()
    _self_test_engine()
    _self_test_policy()
    _self_test_tests_overlay()
    _self_test_setup()

    print("self-test: OK")


def _mk_node(rel: str, layer: "str | None", domain: str, depends_on: list) -> Node:
    return Node(
        rel=rel,
        node_file=rel.replace("/", "__") + ".md",
        title=rel,
        lang="python",
        domain=domain,
        module_id=rel,
        defines=[],
        depends_on=depends_on,
        external=[],
        submodules=[],
        layer=layer,
    )


def _self_test_policy() -> None:
    """One tiny node set per policy `kind`: assert forbidden edges are
    flagged and allowed edges are not."""
    from okf.policy import compile_policy

    # --- assign_layer: first-match-wins glob, no rules/no match -> None ---
    rules = [
        {"glob": "domain/**", "layer": "domain"},
        {"glob": "adapter/**", "layer": "adapter"},
    ]
    assert assign_layer("domain/thing.py", rules) == "domain"
    assert assign_layer("adapter/thing.py", rules) == "adapter"
    assert assign_layer("infra/thing.py", rules) is None
    assert assign_layer("domain/thing.py", None) is None

    order = ["domain", "port", "service", "adapter", "infra"]

    def by_rel(nodes: list[Node]) -> dict:
        return {n.rel: n for n in nodes}

    # --- inward: outer layers may depend inward (toward index 0), never out ---
    domain_n = _mk_node("d.py", "domain", "app", [])
    adapter_n = _mk_node("a.py", "adapter", "app", ["d.py", "infra.py"])
    infra_n = _mk_node("infra.py", "infra", "app", [])
    nodes = [domain_n, adapter_n, infra_n]
    pol = compile_policy({"kind": "inward", "order": order})
    violations = pol.check(adapter_n, by_rel(nodes))
    assert any("infra" in v for v in violations)          # adapter -> infra: forbidden
    assert not any("domain" in v for v in violations)     # adapter -> domain: allowed
    assert pol.check(domain_n, by_rel(nodes)) == []

    # --- outward: reverse direction (inner may depend outward, never in) ---
    pol = compile_policy({"kind": "outward", "order": order})
    domain_out = _mk_node("d.py", "domain", "app", ["a.py"])  # domain -> adapter: allowed (outward)
    adapter_back = _mk_node("a.py", "adapter", "app", ["d.py"])  # adapter -> domain: forbidden
    nodes2 = [domain_out, adapter_back]
    assert pol.check(domain_out, by_rel(nodes2)) == []
    v2 = pol.check(adapter_back, by_rel(nodes2))
    assert any("domain" in v for v in v2)

    # --- downward: only strictly-later layers, same-layer siblings forbidden ---
    pol = compile_policy({"kind": "downward", "order": order})
    ui = _mk_node("ui.py", "domain", "app", ["svc.py", "peer.py"])
    svc = _mk_node("svc.py", "service", "app", [])
    peer = _mk_node("peer.py", "domain", "app", [])
    nodes3 = [ui, svc, peer]
    v3 = pol.check(ui, by_rel(nodes3))
    assert not any("service" in v for v in v3)  # ui -> svc (later): allowed
    assert any("domain" in v for v in v3)       # ui -> peer (same layer): forbidden

    # --- isolate: cross-domain forbidden except via a `shared` layer ---
    pol = compile_policy({"kind": "isolate", "shared": ["shared"]})
    billing = _mk_node("billing/x.py", None, "billing", ["orders/y.py", "shared/z.py"])
    orders_y = _mk_node("orders/y.py", None, "orders", [])
    shared_z = _mk_node("shared/z.py", "shared", "shared", [])
    nodes4 = [billing, orders_y, shared_z]
    v4 = pol.check(billing, by_rel(nodes4))
    assert any("orders" in v for v in v4)          # cross-domain: forbidden
    assert not any("shared" in v for v in v4)      # via `shared` layer: exempt
    # A node with no layer assigned is exempt from isolate's own check() early-out;
    # give billing a layer to exercise the rule itself.
    billing2 = _mk_node("billing/x.py", "feature", "billing", ["orders/y.py"])
    nodes5 = [billing2, _mk_node("orders/y.py", "feature", "orders", [])]
    assert any("orders" in v for v in pol.check(billing2, by_rel(nodes5)))

    # --- allowlist: explicit from->to escape hatch ---
    pol = compile_policy({"kind": "allowlist", "allow": [["adapter", "service"]]})
    adapter_ok = _mk_node("a.py", "adapter", "app", ["s.py"])
    adapter_bad = _mk_node("a.py", "adapter", "app", ["infra.py"])
    svc_n = _mk_node("s.py", "service", "app", [])
    infra_n2 = _mk_node("infra.py", "infra", "app", [])
    assert pol.check(adapter_ok, by_rel([adapter_ok, svc_n])) == []
    assert pol.check(adapter_bad, by_rel([adapter_bad, infra_n2])) != []

    # --- absent policy -> zero violations (nothing to check against) ---
    assert compile_policy(None) is None


def _self_test_engine() -> None:
    """Stage 3: scan + digraph resolution + render, over a two-root,
    two-language fixture tree."""
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        py_root = tmp_path / "app"
        rs_root = tmp_path / "svc"
        (py_root / "widgets").mkdir(parents=True)
        (rs_root / "committer").mkdir(parents=True)

        # Python pair: widget.py imports helper.py (same root) -> digraph edge.
        (py_root / "widgets" / "helper.py").write_text(
            "def assist():\n    pass\n", encoding="utf-8"
        )
        (py_root / "widgets" / "widget.py").write_text(
            "from .helper import assist\n\n\ndef build():\n    assist()\n",
            encoding="utf-8",
        )

        # Rust file in the second root — unrelated, just proves multi-root/
        # multi-lang scanning and no id collision with the python nodes.
        (rs_root / "committer" / "submit.rs").write_text(
            "pub fn run() {}\n", encoding="utf-8"
        )

        roots = [str(py_root), str(rs_root)]
        nodes, skipped_unknown, errors = scan(roots)
        resolve_graph(nodes)

        assert errors == []
        by_rel = {n.rel: n for n in nodes}
        widget_rel = "app/widgets/widget.py"
        helper_rel = "app/widgets/helper.py"
        rust_rel = "svc/committer/submit.rs"
        assert widget_rel in by_rel
        assert helper_rel in by_rel
        assert rust_rel in by_rel
        assert len({n.rel for n in nodes}) == len(nodes)  # no id collision

        widget = by_rel[widget_rel]
        helper = by_rel[helper_rel]
        assert widget.lang == "python"
        assert widget.domain == "widgets"
        assert rust_rel and by_rel[rust_rel].lang == "rust"

        # The digraph: widget imports helper => helper in widget.depends_on
        # AND widget in helper.depended_on_by.
        assert helper_rel in widget.depends_on
        assert widget_rel in helper.depended_on_by

        assert widget.submodules == []  # only __init__ files carry submodules

        output = tmp_path / "out"
        result = generate(roots, str(output), prune=True)
        assert result["status"] == "ok"
        assert result["nodes_created"] == 3
        assert (output / "index.md").is_file()
        assert (output / "widgets" / "_index.md").is_file()
        assert (output / "committer" / "_index.md").is_file()

        # write_if_changed no-ops on an identical rerun.
        before = {
            p: p.stat().st_mtime_ns for p in output.rglob("*.md")
        }
        result2 = generate(roots, str(output), prune=True)
        assert result2["index_changed"] is False
        assert result2["nodes_written"] == 0
        assert result2["domain_indexes_written"] == 0
        after = {p: p.stat().st_mtime_ns for p in output.rglob("*.md")}
        assert before == after


def _self_test_tests_overlay() -> None:
    """Stage 5: a test file referencing node A lands A's reference in
    `tested_by` only — absent from `depends_on`/`depended_on_by`/`violations`,
    which are computed BEFORE the overlay runs."""
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        root = tmp_path / "app" / "widgets"
        root.mkdir(parents=True)

        (root / "widget.py").write_text(
            "def build():\n    pass\n", encoding="utf-8"
        )
        (root / "test_widget.py").write_text(
            "from .widget import build\n\n\ndef test_build():\n    build()\n",
            encoding="utf-8",
        )

        roots = [str(tmp_path / "app")]
        nodes, _, errors = scan(roots)
        assert errors == []
        resolve_graph(nodes)

        by_rel = {n.rel: n for n in nodes}
        widget_rel = "app/widgets/widget.py"
        test_rel = "app/widgets/test_widget.py"
        widget = by_rel[widget_rel]
        test_node = by_rel[test_rel]

        # Before the overlay: the test file's import is a normal digraph edge.
        assert widget_rel in test_node.depends_on
        assert test_rel in widget.depended_on_by

        for n in nodes:
            n.violations = []  # no policy configured; mirrors generate()'s no-op path

        tests_overlay.compute(nodes, roots)

        # After the overlay: the reference moved to tested_by only, exactly
        # once (no duplicate "(inline)" label for a whole-file test node).
        assert widget.tested_by == [test_rel]
        assert test_rel not in widget.depended_on_by
        assert widget_rel not in test_node.depends_on
        assert widget.violations == []


def _self_test_parsers() -> None:
    # --- registry ---
    assert for_ext(".rs") is rust_parser
    assert for_ext("rs") is rust_parser
    assert for_ext(".py") is python_parser
    assert for_ext(".ts") is ts_parser
    assert for_ext(".go") is go_parser
    assert for_ext(".md") is None

    # --- rust ---
    rel = "committer/service/submit.rs"
    src = (
        "use crate::committer::service::Submitter;\n"
        "use super::helper::Thing;\n"
        "use std::collections::HashMap;\n"
        "use serde::Deserialize;\n"
        "\n"
        "mod helper;\n"
        "mod internal_impl;\n"
        "\n"
        "pub struct Submitter {\n"
        "    inner: HashMap<String, i32>,\n"
        "}\n"
        "\n"
        "pub fn run() -> Submitter {\n"
        "    Submitter { inner: HashMap::new() }\n"
        "}\n"
        "\n"
        "#[cfg(test)]\n"
        "mod tests {\n"
        "    use crate::committer::service::helper::Thing;\n"
        "\n"
        "    #[test]\n"
        "    fn it_works() {}\n"
        "}\n"
    )
    assert rust_parser.module_id(rel, src) == "committer::service::submit"
    assert rust_parser.internal_imports(src) == [
        "crate::committer::service", "super::helper::Thing",
    ]
    assert rust_parser.external_deps(src) == ["serde"]
    assert rust_parser.defines(src) == ["Submitter"]
    assert rust_parser.submodules(src) == ["helper", "internal_impl"]
    assert rust_parser.test_imports(rel, src) == ["crate::committer::service"]
    assert rust_parser.module_id("committer/mod.rs", "") == "committer"

    # --- python ---
    py_rel = "okf/widgets/widget.py"
    py_src = (
        '"""Module docstring."""\n'
        "import os\n"
        "import okf.parsers.rust\n"
        "from . import helper\n"
        "from .sibling import Thing\n"
        "from okf.config import Config\n"
        "import requests\n"
        "\n"
        "\n"
        "class Widget:\n"
        "    pass\n"
        "\n"
        "\n"
        "def build():\n"
        "    pass\n"
        "\n"
        "\n"
        "def _private():\n"
        "    pass\n"
        "\n"
        "\n"
        "def test_build():\n"
        "    import okf.parsers.python\n"
        "    build()\n"
    )
    assert python_parser.module_id(py_rel, py_src) == "okf.widgets.widget"
    assert python_parser.module_id("okf/parsers/__init__.py", "") == "okf.parsers"
    assert python_parser.internal_imports(py_src) == [
        ".", ".sibling", "okf.config", "okf.parsers.rust",
    ]
    assert python_parser.external_deps(py_src) == ["os", "requests"]
    assert python_parser.defines(py_src) == ["Widget", "build", "test_build"]
    assert python_parser.submodules(py_src) == ["helper"]
    assert python_parser.test_imports(py_rel, py_src) == ["okf.parsers.python"]

    # --- typescript ---
    ts_rel = "src/widgets/widget.ts"
    ts_src = (
        "import { Foo } from './foo';\n"
        "import Bar from '../shared/bar';\n"
        "import * as fs from 'fs';\n"
        "import { baz } from 'left-pad';\n"
        "const dyn = require('./dynamic');\n"
        "\n"
        "export * from './reexport';\n"
        "export { Thing } from './other';\n"
        "\n"
        "export function build() {}\n"
        "export class Widget {}\n"
        "export const VALUE = 1;\n"
        "export { helper };\n"
    )
    assert ts_parser.module_id(ts_rel, ts_src) == "src/widgets/widget"
    assert ts_parser.internal_imports(ts_src) == [
        "../shared/bar", "./dynamic", "./foo",
    ]
    assert ts_parser.external_deps(ts_src) == ["fs", "left-pad"]
    assert ts_parser.defines(ts_src) == ["build", "Widget", "VALUE", "helper"]
    assert ts_parser.submodules(ts_src) == ["./other", "./reexport"]
    assert ts_parser.test_imports(ts_rel, ts_src) == []
    ts_test_src = "import { Widget } from './widget';\n"
    assert ts_parser.test_imports("widget.test.ts", ts_test_src) == ["./widget"]

    # --- go ---
    go_rel = "widgets/widget.go"
    go_src = (
        "package widgets\n"
        "\n"
        "import (\n"
        '\t"fmt"\n'
        '\t"github.com/pkg/errors"\n'
        '\t"myrepo/internal/helper"\n'
        ")\n"
        "\n"
        'import "encoding/json"\n'
        "\n"
        "type Widget struct {\n"
        "\tName string\n"
        "}\n"
        "\n"
        "func Build() *Widget {\n"
        "\tfmt.Println(json.Marshal, errors.New, helper.Do)\n"
        "\treturn &Widget{}\n"
        "}\n"
        "\n"
        "func helperFunc() {}\n"
    )
    assert go_parser.module_id(go_rel, go_src) == "widgets"
    assert go_parser.module_id("main.go", "") == "."
    assert go_parser.internal_imports(go_src) == ["myrepo/internal/helper"]
    assert go_parser.external_deps(go_src) == [
        "encoding/json", "fmt", "github.com/pkg/errors",
    ]
    assert go_parser.defines(go_src) == ["Widget", "Build"]
    assert go_parser.submodules(go_src) == []
    assert go_parser.test_imports(go_rel, go_src) == []
    go_test_src = 'import "myrepo/internal/helper"\n'
    assert go_parser.test_imports("widget_test.go", go_test_src) == [
        "myrepo/internal/helper"
    ]


def _self_test_setup() -> None:
    """Stage 6: setup.py vendors OKF into a target repo, idempotently."""
    from okf import setup

    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        target = tmp_path / "target-repo"
        target.mkdir()
        (target / "src").mkdir()
        (target / "src" / "a.py").write_text("def f():\n    pass\n", encoding="utf-8")

        # --dry-run writes nothing.
        before = sorted(target.rglob("*"))
        result = setup.setup_target(target, ["src"], "docs/okf", with_hook=False, dry_run=True)
        after = sorted(target.rglob("*"))
        assert before == after
        assert result["status"] == "dry-run"
        assert any("vendor" in a for a in result["actions"])

        # A real run vendors the mapper, writes okf.toml, injects AGENTS.md,
        # and generates the map.
        result = setup.setup_target(target, ["src"], "docs/okf", with_hook=False, dry_run=False)
        assert result["status"] == "ok"
        assert (target / "scripts" / "okf" / "map.py").is_file()
        assert (target / "scripts" / "okf" / "parsers" / "python.py").is_file()
        assert not (target / "scripts" / "okf" / "setup.py").exists()
        assert not (target / "scripts" / "okf" / "AGENTS-okf.md").exists()
        assert (target / "okf.toml").is_file()
        agents_text = (target / "AGENTS.md").read_text(encoding="utf-8")
        assert agents_text.count(setup.MARKER_START) == 1
        assert (target / "docs" / "okf" / "index.md").is_file()

        # A second real run: exactly one AGENTS section, existing okf.toml
        # untouched.
        cfg_before = (target / "okf.toml").read_text(encoding="utf-8")
        setup.setup_target(target, ["src"], "docs/okf", with_hook=False, dry_run=False)
        agents_text2 = (target / "AGENTS.md").read_text(encoding="utf-8")
        assert agents_text2.count(setup.MARKER_START) == 1
        assert agents_text2 == agents_text, "AGENTS.md must be byte-identical across re-runs"
        assert (target / "okf.toml").read_text(encoding="utf-8") == cfg_before

        # Injecting into an existing marker-less AGENTS.md appends once and
        # preserves the original content.
        target2 = tmp_path / "target-repo-2"
        target2.mkdir()
        (target2 / "AGENTS.md").write_text(
            "# My repo\n\nSome existing notes.\n", encoding="utf-8"
        )
        setup.inject_agents_md(target2, ["src"], "docs/okf", dry_run=False)
        text2 = (target2 / "AGENTS.md").read_text(encoding="utf-8")
        assert "Some existing notes." in text2
        assert text2.count(setup.MARKER_START) == 1
        setup.inject_agents_md(target2, ["src"], "docs/okf", dry_run=False)
        text2b = (target2 / "AGENTS.md").read_text(encoding="utf-8")
        assert text2b.count(setup.MARKER_START) == 1
        assert text2b == text2, "AGENTS.md must be byte-identical across re-runs (append-then-noop)"

        # A partial marker pair fails loud rather than double-injecting.
        target3 = tmp_path / "target-repo-3"
        target3.mkdir()
        (target3 / "AGENTS.md").write_text(
            setup.MARKER_START + "\nno end marker\n", encoding="utf-8"
        )
        try:
            setup.inject_agents_md(target3, ["src"], "docs/okf", dry_run=False)
            assert False, "expected SetupError for mismatched markers"
        except setup.SetupError:
            pass

        # Vendoring into a target whose scripts/okf IS this source tree
        # (dogfooding this repo on itself) is a self-copy no-op, not a crash.
        self_target = Path(__file__).resolve().parent.parent.parent
        actions = setup.vendor(self_target, dry_run=False)
        assert any("map.py" in a for a in actions)


def main() -> int:
    import argparse
    import json

    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    parser = argparse.ArgumentParser(description="OKF codebase mapper.")
    parser.add_argument("--source", action="append", help="source root (repeatable)")
    parser.add_argument("--output", help="output directory for the generated map")
    parser.add_argument("--quiet", action="store_true", help="suppress summary output")
    parser.add_argument("--no-prune", action="store_true", help="skip pruning orphan node files")
    parser.add_argument("--self-test", action="store_true", help="run the in-script test suite")
    parser.add_argument("--version", action="store_true", help="print the okf version")
    args = parser.parse_args()

    if args.version:
        print(__version__)
        return 0

    if args.self_test:
        _self_test()
        return 0

    cfg = config.load()
    roots = args.source or cfg.source
    output = args.output or cfg.output

    result = generate(
        roots, output, prune=not args.no_prune,
        layer_rule=cfg.layer_rule, policy_cfg=cfg.policy,
    )

    summary = {k: v for k, v in result.items() if k != "index_md"}
    print(json.dumps(summary, indent=2))
    if not args.quiet:
        print("\n===== index.md =====\n")
        print(result["index_md"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
