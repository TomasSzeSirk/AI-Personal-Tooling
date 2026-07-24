"""okf.toml loading and validation. No parsing of source files — pure config."""

from __future__ import annotations

import pathlib
import tomllib
from dataclasses import dataclass, field

_ALLOWED_POLICY_KINDS = {"inward", "outward", "downward", "isolate", "allowlist"}
_DIRECTIONAL_KINDS = {"inward", "outward", "downward"}


class ConfigError(Exception):
    pass


@dataclass
class Config:
    source: list[str]
    output: str
    ignore: list[str]
    layer_rule: list[dict] | None
    policy: dict | None
    warnings: list[str] = field(default_factory=list)


def _default_okf_toml_path() -> pathlib.Path:
    # This file lives at <repo-root>/scripts/okf/config.py in the vendored
    # layout, so the repo root is two levels up (same pattern as adapt.py).
    return pathlib.Path(__file__).resolve().parents[2] / "okf.toml"


def _require_str_list(value: object, name: str, file: str) -> list[str]:
    if isinstance(value, str):
        return [value]
    if isinstance(value, list) and all(isinstance(v, str) for v in value):
        return list(value)
    raise ConfigError(f"{file}: '{name}' must be a string or list of strings")


def _validate_layer_rule(raw: object, file: str) -> list[dict]:
    if not isinstance(raw, list):
        raise ConfigError(f"{file}: 'layer_rule' must be a list of tables")
    rules = []
    for i, entry in enumerate(raw):
        if not isinstance(entry, dict):
            raise ConfigError(f"{file}: 'layer_rule[{i}]' must be a table")
        glob = entry.get("glob")
        layer = entry.get("layer")
        if not isinstance(glob, str) or not isinstance(layer, str):
            raise ConfigError(
                f"{file}: 'layer_rule[{i}]' must have string 'glob' and 'layer'"
            )
        rules.append({"glob": glob, "layer": layer})
    return rules


def _validate_policy(raw: object, file: str) -> tuple[dict, list[str]]:
    if not isinstance(raw, dict):
        raise ConfigError(f"{file}: 'policy' must be a table")
    kind = raw.get("kind")
    if kind not in _ALLOWED_POLICY_KINDS:
        raise ConfigError(
            f"{file}: 'policy.kind' must be one of {sorted(_ALLOWED_POLICY_KINDS)}, got {kind!r}"
        )

    policy: dict = {"kind": kind}
    referenced_layers: list[str] = []

    if kind in _DIRECTIONAL_KINDS:
        order = raw.get("order")
        if not isinstance(order, list) or not order or not all(isinstance(v, str) for v in order):
            raise ConfigError(f"{file}: 'policy.order' must be a non-empty list of strings")
        policy["order"] = list(order)
        referenced_layers.extend(order)
    elif kind == "isolate":
        shared = raw.get("shared", [])
        if not isinstance(shared, list) or not all(isinstance(v, str) for v in shared):
            raise ConfigError(f"{file}: 'policy.shared' must be a list of strings")
        policy["shared"] = list(shared)
    elif kind == "allowlist":
        allow = raw.get("allow")
        if not isinstance(allow, list) or not all(
            isinstance(pair, list) and len(pair) == 2 and all(isinstance(v, str) for v in pair)
            for pair in allow
        ):
            raise ConfigError(
                f"{file}: 'policy.allow' must be a list of [from, to] string pairs"
            )
        policy["allow"] = [list(pair) for pair in allow]
        for pair in allow:
            referenced_layers.extend(pair)

    return policy, referenced_layers


def load(path: str | pathlib.Path | None = None) -> Config:
    toml_path = pathlib.Path(path) if path is not None else _default_okf_toml_path()
    file_label = str(toml_path)

    try:
        with open(toml_path, "rb") as f:
            data = tomllib.load(f)
    except FileNotFoundError:
        return Config(source=["src"], output="docs/okf", ignore=[], layer_rule=None, policy=None)
    except OSError as e:
        raise ConfigError(f"{file_label}: cannot read config file: {e}") from e
    except (tomllib.TOMLDecodeError, UnicodeDecodeError) as e:
        raise ConfigError(f"{file_label}: malformed TOML: {e}") from e

    source = _require_str_list(data.get("source", ["src"]), "source", file_label)

    output = data.get("output", "docs/okf")
    if not isinstance(output, str):
        raise ConfigError(f"{file_label}: 'output' must be a string")

    ignore = _require_str_list(data.get("ignore", []), "ignore", file_label)

    layer_rule = None
    if "layer_rule" in data:
        layer_rule = _validate_layer_rule(data["layer_rule"], file_label)

    policy = None
    warnings: list[str] = []
    if "policy" in data:
        policy, referenced_layers = _validate_policy(data["policy"], file_label)
        assigned_layers = {rule["layer"] for rule in layer_rule} if layer_rule else set()
        for layer in referenced_layers:
            if layer not in assigned_layers:
                warnings.append(
                    f"{file_label}: policy references layer {layer!r} that no layer_rule assigns"
                )

    return Config(
        source=source,
        output=output,
        ignore=ignore,
        layer_rule=layer_rule,
        policy=policy,
        warnings=warnings,
    )
