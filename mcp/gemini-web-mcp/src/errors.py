"""Exceptions shared across gemini_mcp stages."""


class ResponseTimeout(Exception):
    """Raised when Gemini's response never stabilizes and never finishes."""


class SelectorError(Exception):
    """Raised when a Playwright selector fails to match the expected DOM."""


class NotAuthenticated(Exception):
    """Raised when Gemini shows a login wall — the profile has no live session."""
