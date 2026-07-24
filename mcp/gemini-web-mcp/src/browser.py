"""Persistent authenticated browser context, one per process.

A single launch_persistent_context keyed to the config's profile_dir holds the
Google session cookies on disk, so a restart stays signed in. All requests
share it and are serialized through LOCK — this MCP server drives one first-party
web UI serially by design (see the spec's single-lock decision).
"""

from __future__ import annotations

import asyncio
from typing import Optional

from playwright.async_api import BrowserContext, async_playwright

# Serializes every request against the single shared context. Stage 5 acquires
# this around a full ask() so two tool calls never drive the same UI at once.
LOCK = asyncio.Lock()

_playwright = None
_context: Optional[BrowserContext] = None


def _is_alive(ctx: BrowserContext) -> bool:
    # Playwright has no public "is this context still open" flag; a closed
    # context has no browser and its pages list is empty after a crash.
    browser = ctx.browser
    if browser is not None and not browser.is_connected():
        return False
    return True


async def get_context(config: dict) -> BrowserContext:
    """Return the shared context, launching it lazily on first use.

    Relaunches if a previous context was closed or crashed. Concurrent callers
    must serialize via LOCK: the lazy launch isn't self-synchronized, and two
    simultaneous launches on the same profile_dir hit Chromium's single-instance
    lock. (A one-shot CLI call — login, probe — has no concurrency and needn't
    hold it.) Don't take LOCK in here: asyncio.Lock is non-reentrant, so a
    request path that already holds it would deadlock.
    """
    global _playwright, _context

    if _context is not None and _is_alive(_context):
        return _context

    # Stale handle from a crash/close — drop it before relaunching.
    if _context is not None:
        _context = None

    if _playwright is None:
        _playwright = await async_playwright().start()

    _context = await _playwright.chromium.launch_persistent_context(
        user_data_dir=config["profile_dir"],
        headless=config["headless"],
    )
    return _context


async def shutdown() -> None:
    """Close the context and stop Playwright, flushing the profile to disk."""
    global _playwright, _context

    if _context is not None:
        try:
            await _context.close()
        finally:
            _context = None

    if _playwright is not None:
        try:
            await _playwright.stop()
        finally:
            _playwright = None
