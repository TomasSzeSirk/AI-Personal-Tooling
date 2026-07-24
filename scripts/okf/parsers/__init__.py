"""Parser registry: extension -> parser module, looked up via for_ext()."""

from __future__ import annotations

from okf.parsers import go, python, rust, typescript

_PARSERS = (rust, python, typescript, go)

_BY_EXT = {ext: mod for mod in _PARSERS for ext in mod.EXTENSIONS}


def for_ext(ext: str):
    """Return the parser module registered for `ext` (e.g. '.py' or 'py'), or
    None if no parser handles it."""
    if not ext.startswith("."):
        ext = "." + ext
    return _BY_EXT.get(ext)
