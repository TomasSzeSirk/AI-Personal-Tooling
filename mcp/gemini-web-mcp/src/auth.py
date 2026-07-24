"""Login-wall detection.

Gemini does NOT redirect a signed-out visitor away from gemini.google.com — it
serves /app in a signed-out state with the Google account bar showing a
"Sign in" link (selectors.LOGIN_WALL). When a real session is present that link
is replaced by the account avatar. Presence of the sign-in anchor is therefore
the signed-out signal; the URL is not.
"""

from __future__ import annotations

from gemini_mcp import selectors
from gemini_mcp.errors import NotAuthenticated

_NOT_AUTH_MESSAGE = "Not authenticated — run 'python -m gemini_mcp login'."


async def is_login_wall(page) -> bool:
    """True if `page` shows Gemini's signed-out sign-in link, not a live session."""
    if "accounts.google.com" in page.url:
        return True  # in case Gemini ever does redirect to the sign-in flow
    return await page.locator(selectors.LOGIN_WALL).count() > 0


async def require_authenticated(page) -> None:
    """Raise NotAuthenticated with the spec'd message if on the login wall."""
    if await is_login_wall(page):
        raise NotAuthenticated(_NOT_AUTH_MESSAGE)
