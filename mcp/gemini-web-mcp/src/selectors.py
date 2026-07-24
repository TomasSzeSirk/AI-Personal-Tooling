"""Every Gemini DOM selector lives here. UI change = fix this file only.

Discovered against the live, signed-in gemini.google.com/app page (2026-07-24,
Spanish-locale account). Prefer LOCALE-INDEPENDENT, stable handles: the aria
labels are translated ("Enviar mensaje", "Detener respuesta") and must NOT be
selected on. Material icon `fonticon` names (arrow_upward, stop) and Quill/
Angular structural classes (.ql-editor, .model-response-text) are language- and
build-stable; the mat-mdc-*/ng-tns-* hash classes are not — never select those.
"""

from __future__ import annotations

# Prompt box: a contenteditable Quill editor. Locale-independent.
PROMPT_EDITOR = ".ql-editor[contenteditable='true']"

# Send button: mounts only once the editor is non-empty, and is swapped for the
# stop button (GENERATING_INDICATOR) while a response streams. Keyed on its
# Material icon, not the translated aria-label.
SUBMIT_BUTTON = "button:has(mat-icon[fonticon='arrow_upward'])"

# The latest model turn's text. One .model-response-text per turn; read the
# LAST match to get the newest response (Stage 5 uses one tab per call, so
# there is exactly one, but last-of stays correct if that ever changes). Note:
# the enclosing <model-response> also carries a screen-reader "Gemini ha dicho"
# prefix — .model-response-text is the clean text node without it.
RESPONSE_CONTAINER = ".model-response-text"

# Present ONLY while Gemini is streaming: the send button becomes a stop button
# (Material icon "stop"). Verified present during generation and absent once the
# answer completes — the signal Stage 2's completion heuristic polls.
GENERATING_INDICATOR = "button:has(mat-icon[fonticon='stop'])"

# Signed-out Gemini serves /app (no redirect) with the Google account bar's
# sign-in link. Present = not authenticated; replaced by the avatar when a
# session exists.
LOGIN_WALL = "a[href*='accounts.google.com/ServiceLogin']"
