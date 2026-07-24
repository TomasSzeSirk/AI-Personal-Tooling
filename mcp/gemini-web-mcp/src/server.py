"""FastMCP server: one MCP tool per configured Gem.

Tools are built by looping over config["tools"] — nothing is hardcoded, so
adding a Gem to ~/.gemini_mcp/config.yaml adds a tool. Each tool is a stateless
(prompt: str) -> str call delegating to session.run. The three actionable
exceptions are returned as the tool result rather than crashing the server, so
one bad call (auth lapsed, UI changed, slow answer) never takes the stdio
transport down — the next call recovers.
"""

from __future__ import annotations

from mcp.server.fastmcp import FastMCP

from gemini_mcp import config as config_mod, session
from gemini_mcp.errors import NotAuthenticated, ResponseTimeout, SelectorError


def _make_tool(config: dict, gem_url: str):
    # A factory (not an inline closure with a default arg) so gem_url binds
    # correctly per tool AND the exposed signature is exactly (prompt: str) —
    # FastMCP would otherwise publish any extra parameter as a tool input.
    async def ask(prompt: str) -> str:
        try:
            return await session.run(config, gem_url, prompt)
        except (NotAuthenticated, ResponseTimeout, SelectorError) as e:
            return str(e)

    return ask


def build_server(config: dict | None = None) -> FastMCP:
    if config is None:
        config = config_mod.load()
    mcp = FastMCP("gemini-web")
    for name, entry in config["tools"].items():
        mcp.add_tool(_make_tool(config, entry["gem_url"]), name=name, description=entry["description"])
    return mcp
