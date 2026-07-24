"""One stateless Gemini exchange, plus the browser-free completion detector.

wait_for_completion is a pure async function: it takes get_text/is_generating
callables so it can be tested without importing Playwright at all. run() wires
those against the real page selectors. All Playwright/browser imports stay
INSIDE run() — session is imported by the Stage-2 self-test, which blocks any
playwright import to prove completion detection needs no browser.
"""

from __future__ import annotations

import asyncio
import inspect
import time
from pathlib import Path
from typing import Any, Callable

from gemini_mcp.errors import ResponseTimeout, SelectorError

# Where run() drops a screenshot when a selector never shows — the first thing
# to look at when Gemini's UI has shifted under the selectors.
LAST_ERROR_PNG = Path("~/.gemini_mcp/last_error.png").expanduser()
# Shown to callers unexpanded — the absolute form would leak the OS username.
LAST_ERROR_DISPLAY = "~/.gemini_mcp/last_error.png"

# How long to wait for a selector (editor, submit button) to appear. Generous:
# a Gem URL cold-load was observed to take >6s.
SELECTOR_TIMEOUT_MS = 30000


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


async def _screenshot_and_raise(page, what: str, cause: Exception) -> None:
    try:
        await page.screenshot(path=str(LAST_ERROR_PNG))
    except Exception:
        pass  # a screenshot failure must not mask the real selector error
    raise SelectorError(
        f"Failed on {what} — Gemini's page or DOM may have changed "
        f"(fix selectors.py). Screenshot: {LAST_ERROR_DISPLAY}"
    ) from cause


async def run(config: dict, gem_url: str, prompt: str) -> str:
    """Ask one Gem one prompt, statelessly, and return its answer text.

    One invocation = one fresh tab, discarded at the end. No page or conversation
    is ever reused, so answers can't cross-contaminate. Serialized against every
    other call by browser.LOCK.
    """
    from playwright.async_api import Error as PWError

    from gemini_mcp import auth, browser, selectors

    async with browser.LOCK:
        ctx = await browser.get_context(config)
        page = await ctx.new_page()
        try:
            # Every Playwright failure below (nav timeout, dead host, detached
            # locator, click intercepted) becomes a SelectorError with a
            # screenshot — never a raw traceback leaking gem_url to the caller.
            # NotAuthenticated and ResponseTimeout deliberately stay outside
            # these catches so they surface with their own actionable message.
            try:
                await page.goto(gem_url, wait_until="load", timeout=60000)
            except PWError as e:
                await _screenshot_and_raise(page, "loading the Gem page", e)

            await auth.require_authenticated(page)  # raises NotAuthenticated

            editor = page.locator(selectors.PROMPT_EDITOR)
            try:
                await editor.wait_for(state="visible", timeout=SELECTOR_TIMEOUT_MS)
                await editor.fill(prompt)
            except PWError as e:
                await _screenshot_and_raise(page, "the prompt editor", e)

            submit = page.locator(selectors.SUBMIT_BUTTON)
            try:
                await submit.wait_for(state="visible", timeout=SELECTOR_TIMEOUT_MS)
                await submit.click()
            except PWError as e:
                await _screenshot_and_raise(page, "the submit button", e)

            async def get_text() -> str:
                loc = page.locator(selectors.RESPONSE_CONTAINER)
                if await loc.count() == 0:
                    return ""  # response node not mounted yet (pre-token phase)
                return await loc.last.inner_text()

            async def is_generating() -> bool:
                return await page.locator(selectors.GENERATING_INDICATOR).count() > 0

            text = await wait_for_completion(
                get_text, is_generating, timeout_s=config["response_timeout_s"]
            )
            return text.strip()
        finally:
            # Always discard the tab — on success, timeout, or any error — so no
            # orphan page or half-finished conversation survives the call.
            await page.close()
