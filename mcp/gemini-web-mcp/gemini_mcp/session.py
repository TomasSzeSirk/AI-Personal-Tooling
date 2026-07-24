"""Completion detection for a Gemini response, browser-free.

wait_for_completion is a pure async function: it takes get_text/is_generating
callables so it can be tested without importing Playwright at all. Wiring
these against real page selectors happens in a later stage.
"""

from __future__ import annotations

import asyncio
import inspect
import time
from typing import Any, Callable

from gemini_mcp.errors import ResponseTimeout


async def wait_for_completion(
    get_text: Callable[[], Any],
    is_generating: Callable[[], Any],
    timeout_s: float,
    stable_s: float = 2.0,
    poll_s: float = 0.25,
) -> str:
    """Poll get_text/is_generating until the response looks finished.

    get_text/is_generating may be plain callables or return awaitables (the
    real Playwright locator methods are coroutine functions).

    Resolves when is_generating() is false, or when get_text() has been
    unchanged for stable_s seconds. Raises ResponseTimeout after timeout_s.
    """
    start = time.monotonic()
    last_text: str = ""
    last_change = start

    while True:
        now = time.monotonic()
        if now - start > timeout_s:
            raise ResponseTimeout(f"No completion detected after {timeout_s}s")

        try:
            text = get_text()
            if inspect.isawaitable(text):
                text = await text
        except Exception:
            # A transient read (e.g. Gemini re-rendering the response node
            # mid-stream) shouldn't kill the whole wait; keep the last good
            # text and let the deadline above remain the backstop.
            text = last_text

        if text != last_text:
            last_text = text
            last_change = now

        try:
            generating = is_generating()
            if inspect.isawaitable(generating):
                generating = await generating
        except Exception:
            generating = True  # don't mistake a transient read failure for "done"

        if not generating:
            # There's a network round-trip between submit and the first
            # rendered token, so the indicator can read false for a moment
            # before generation has actually started. Don't trust "not
            # generating" until we've seen real text.
            if last_text:
                return last_text

        # Never resolve as "done" with no text at all while the indicator still
        # reads generating — that is the pre-token thinking phase, and a Gem
        # can think for well over 3 * stable_s. Returning "" there is a wrong
        # answer that looks like success; let timeout_s be the backstop instead.
        #
        # ponytail: stability is a naive ceiling — a mid-answer pause (thinking,
        # rendering a code block, a tool call) longer than 3 * stable_s still
        # truncates the answer even while is_generating() is true. Tripling the
        # window while the indicator reads "generating" covers normal pauses;
        # a stuck-true indicator would need a smarter signal than stability.
        if (last_text or not generating) and now - last_change >= (
            stable_s * 3 if generating else stable_s
        ):
            return last_text

        await asyncio.sleep(poll_s)
