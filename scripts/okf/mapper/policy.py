"""Architecture policy: compile a validated `okf.toml` [policy] table into a
checker that flags dependency edges crossing declared architecture layers.

All five kinds ultimately answer one question per dependency edge: is the
source layer allowed to depend on the target layer? `inward`/`outward`/
`downward` are directional shortcuts over an `order` list; `isolate` is a
peer rule keyed on `node.domain` (not layer) with a `shared` escape layer;
`allowlist` is the explicit from->to escape hatch the others could always
fall back to.
"""

from __future__ import annotations

_DIRECTIONAL_KINDS = {"inward", "outward", "downward"}


class Policy:
    """Compiled policy. `check(node, nodes_by_rel)` returns human-readable
    violation strings for `node`'s dependency out-edges that the policy
    forbids. Edges to an unclassified (layer=None) target are never
    violations."""

    def __init__(self, policy_cfg: dict):
        self.kind = policy_cfg["kind"]
        if self.kind in _DIRECTIONAL_KINDS:
            self.order = list(policy_cfg["order"])
        elif self.kind == "isolate":
            self.shared = set(policy_cfg.get("shared", []))
        elif self.kind == "allowlist":
            self.allow: dict[str, set[str]] = {}
            for frm, to in policy_cfg["allow"]:
                self.allow.setdefault(frm, set()).add(to)
        else:
            raise ValueError(f"unknown policy kind: {self.kind!r}")

    def _directional_allowed(self, src_layer: str, tgt_layer: str) -> bool:
        if src_layer not in self.order or tgt_layer not in self.order:
            # A layer outside the declared `order` isn't governed by this
            # policy — nothing to flag.
            return True
        si = self.order.index(src_layer)
        ti = self.order.index(tgt_layer)
        if self.kind == "inward":
            return ti <= si          # only same-or-toward index 0 (domain)
        if self.kind == "outward":
            return ti >= si          # only same-or-toward the last layer
        return ti > si               # downward: strictly later layers only

    def check(self, node, nodes_by_rel: dict) -> list[str]:
        violations: list[str] = []

        # `isolate` is a peer rule keyed on domain, not layer — nodes need no
        # `layer_rule` match at all to participate (only the `shared` escape
        # layer does), so it skips the layer-gated path below entirely.
        if self.kind == "isolate":
            for target_rel in node.depends_on:
                target = nodes_by_rel.get(target_rel)
                if target is None:
                    continue
                if (
                    node.domain != target.domain
                    and node.layer not in self.shared
                    and target.layer not in self.shared
                ):
                    violations.append(
                        f"{node.domain} imports {target.domain} (cross-domain leak)"
                    )
            return violations

        if node.layer is None:
            return violations

        for target_rel in node.depends_on:
            target = nodes_by_rel.get(target_rel)
            if target is None or target.layer is None:
                continue

            if self.kind in _DIRECTIONAL_KINDS:
                if not self._directional_allowed(node.layer, target.layer):
                    violations.append(
                        f"{node.layer} imports {target.layer} (cross-layer leak)"
                    )
            elif self.kind == "allowlist":
                if target.layer not in self.allow.get(node.layer, set()):
                    violations.append(
                        f"{node.layer} imports {target.layer} (cross-layer leak)"
                    )

        return violations


def compile_policy(policy_cfg: "dict | None") -> "Policy | None":
    """Compile a validated policy dict (as produced by `config.load`) into a
    `Policy`. `None` in -> `None` out (no policy configured)."""
    if policy_cfg is None:
        return None
    return Policy(policy_cfg)
