"""Config loading and validation for gemini_mcp.

Config lives at ~/.gemini_mcp/config.yaml (not inside the package) since it
holds semi-private Gem URLs. See config.example.yaml in the repo for the
shape to copy.
"""

from __future__ import annotations

from pathlib import Path

import yaml

DEFAULT_CONFIG_PATH = Path("~/.gemini_mcp/config.yaml").expanduser()
EXAMPLE_CONFIG_NAME = "config.example.yaml"

DEFAULTS = {
    "headless": True,
    "response_timeout_s": 120,
    "profile_dir": "~/.gemini_mcp/profile",
}


class ConfigError(Exception):
    """Raised when the config file is missing or invalid."""


def load(path: str | Path | None = None) -> dict:
    """Load and validate the config file.

    Defaults to ~/.gemini_mcp/config.yaml. Raises ConfigError naming the
    file for any missing/invalid state.
    """
    config_path = Path(path).expanduser() if path is not None else DEFAULT_CONFIG_PATH

    if not config_path.is_file():
        raise ConfigError(
            f"Config file not found: {config_path}. "
            f"Copy {EXAMPLE_CONFIG_NAME} to {config_path} and fill in your Gem URLs."
        )

    # open() must be inside the try: a config saved as UTF-16 or cp1252 (what
    # PowerShell 5.1's `>` and Out-File produce) raises UnicodeDecodeError, and
    # an unreadable file raises OSError. Both would otherwise escape ConfigError
    # and kill the stdio MCP server with a traceback.
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            raw = yaml.safe_load(f) or {}
    except (yaml.YAMLError, UnicodeDecodeError, OSError) as e:
        raise ConfigError(f"{config_path}: could not read config: {e}") from e

    if not isinstance(raw, dict):
        raise ConfigError(
            f"{config_path}: top level must be a mapping, not {type(raw).__name__}."
        )

    tools = raw.get("tools")
    if not tools:
        raise ConfigError(f"{config_path}: 'tools' is missing or empty.")
    if not isinstance(tools, dict):
        raise ConfigError(
            f"{config_path}: 'tools' must be a mapping of name -> {{gem_url, description}}."
        )

    for name, entry in tools.items():
        if not isinstance(name, str) or not name.isidentifier():
            raise ConfigError(
                f"{config_path}: tool name '{name}' is not a valid Python identifier."
            )
        if not isinstance(entry, dict):
            raise ConfigError(
                f"{config_path}: tool '{name}' must be a mapping with 'gem_url' and 'description'."
            )
        gem_url = entry.get("gem_url")
        if not isinstance(gem_url, str) or not gem_url.strip():
            raise ConfigError(f"{config_path}: tool '{name}' is missing 'gem_url'.")
        description = entry.get("description")
        if not isinstance(description, str) or not description.strip():
            raise ConfigError(f"{config_path}: tool '{name}' is missing 'description'.")

    config = dict(DEFAULTS)
    config.update(raw)

    if not isinstance(config.get("headless"), bool):
        raise ConfigError(f"{config_path}: 'headless' must be true or false.")

    timeout = config.get("response_timeout_s")
    if not isinstance(timeout, int) or isinstance(timeout, bool):
        raise ConfigError(f"{config_path}: 'response_timeout_s' must be an integer (seconds).")

    profile_dir = config.get("profile_dir")
    if not isinstance(profile_dir, str) or not profile_dir.strip():
        raise ConfigError(f"{config_path}: 'profile_dir' must be a non-empty string.")
    config["profile_dir"] = str(Path(profile_dir).expanduser())

    config["tools"] = tools

    return config
