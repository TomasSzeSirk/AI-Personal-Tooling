#!/usr/bin/env python3
"""Low-level filesystem IO for the OKF tools: change-guarded writes. No knowledge
of nodes or Rust — pure storage."""

from __future__ import annotations

SKIP_DIRS = {"target", ".git"}


def write_if_changed(path: str, content: str) -> bool:
    """Write only when the on-disk bytes differ, so unchanged nodes keep their
    mtime and the pre-commit `git add docs/okf` re-stages nothing. Compares raw
    bytes (LF) so a stray CRLF copy is also rewritten to LF. Returns True if
    the file was (re)written."""
    data = content.encode("utf-8")
    try:
        with open(path, "rb") as f:
            if f.read() == data:
                return False
    except OSError:
        pass
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(content)
    return True
