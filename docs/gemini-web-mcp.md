# Gemini Web MCP

A Playwright-driven MCP server that fronts **Gemini Web Gems** as MCP tools.
Each Gem you configure becomes one `(prompt: str) -> str` tool callable from
Claude Code or Codex — a second, differently-grounded model available inside
your agent loop. There is no official Gemini Gems API; this drives the web UI
under a dedicated Google account, so every DOM selector is centralized in one
file and a UI change is a one-file fix.

Lives at `mcp/gemini-web-mcp/` — the repo's first MCP server, so `mcp/` is the
by-type home for future ones.

## The Gems it fronts

Tools are **not hardcoded** — the server registers one per entry in your
`~/.gemini_mcp/config.yaml`. The Gems this was built around:

| Tool | Gem role |
|------|----------|
| `adversarial_review` | Red-team a plan/design/code — ranked failure modes, no cortesía. |
| `second_opinion` | Independent critique of another model's answer or decision — breaks single-model echo. |
| `deep_research` | In-depth, source-cited research answers (Gemini's web grounding). |

Add or remove a tool by editing the config — no code change.

## How it works

One tool call = one fresh browser tab, one prompt, discarded. No page or
conversation is reused, so answers never cross-contaminate. All calls are
serialized through a single process-wide lock (the server drives one web UI
serially by design). The persistent Chromium profile at `~/.gemini_mcp/profile`
holds the Google session cookies on disk, so it stays signed in across restarts.
Completion is detected by watching Gemini's streaming DOM (the "stop" control
plus response-text stability) — see `src/session.py`.

## Install

From `mcp/gemini-web-mcp/`:

```
python -m venv .venv
.venv\Scripts\python.exe -m pip install -e .      # Windows
# .venv/bin/python -m pip install -e .            # macOS/Linux
.venv\Scripts\python.exe -m playwright install chromium
```

> On Windows, run the package as `.venv\Scripts\python.exe -m gemini_mcp`.
> `python3` is the broken Windows Store alias — don't use it.

## Configure

Config lives **outside the repo** at `~/.gemini_mcp/config.yaml` (Gem URLs are
semi-private). Copy the shipped example and fill in real Gem URLs:

```
copy config.example.yaml %USERPROFILE%\.gemini_mcp\config.yaml   # Windows
```

```yaml
tools:
  deep_research:
    gem_url: https://gemini.google.com/gem/<id>
    description: In-depth researched answers with cited sources, via Gemini
# headless: true            # default
# response_timeout_s: 120   # default
# profile_dir: ~/.gemini_mcp/profile
```

Find a Gem's URL by opening it in Gemini Web and copying `.../gem/<id>` from the
address bar. A tool name must be a valid Python identifier — it becomes the MCP
tool name.

## Sign in (one time, human)

Cannot be automated — a person signs into the dedicated Google account:

```
.venv\Scripts\python.exe -m gemini_mcp login
```

A visible Chromium opens on `gemini.google.com`. Sign in, confirm you land on
the chat app (not the "Meet Gemini" landing), then **close the window** — the
profile flushes to disk. A later headless run stays signed in.

## Register

**Claude Code** (user scope makes the Gems available in any session):

```
claude mcp add gemini-web -s user -- <abs-path>\.venv\Scripts\python.exe -m gemini_mcp serve
claude mcp list        # gemini-web should show ✔ Connected
```

**Codex** — add to `~/.codex/config.toml` *(shape per Codex docs; not verified
against an installed codex on this machine — confirm against your version)*:

```toml
[mcp_servers.gemini-web]
command = "<abs-path>/.venv/Scripts/python.exe"
args = ["-m", "gemini_mcp", "serve"]
```

## Smoke test without a client

```
.venv\Scripts\python.exe -m gemini_mcp ask deep_research "Reply with exactly: PONG"
```

Sends one prompt to a configured Gem and prints the answer. Handy for debugging
after any UI or config change.

## Troubleshooting

**A UI change breaks everything → fix `src/selectors.py` only.** Every
Gemini DOM selector lives in that one file; nothing else selects on the DOM.

- **Diagnose with `probe`:** `... -m gemini_mcp probe <gem_url>` opens the page
  (headed by default) and prints, every 1.5s, how many nodes each selector
  matches. Type a prompt in the window and submit to watch `GENERATING_INDICATOR`
  flip 1→0. Close the window to stop. If `PROMPT_EDITOR`, `SUBMIT_BUTTON`,
  `RESPONSE_CONTAINER`, or `GENERATING_INDICATOR` reports 0 where it should be 1,
  that constant needs updating.
- **First thing to look at on a `SelectorError`:** the screenshot at
  `~/.gemini_mcp/last_error.png` — `run()` writes it whenever a selector never
  appears, so you can see what the page actually looked like.
- **`Not authenticated`:** the session lapsed — rerun `login`. A tool returns
  this as its result string rather than crashing the server.
- **Selectors are locale-independent on purpose:** they key on stable handles
  (Material `fonticon` names, `role`, `contenteditable`, `href`), never on
  translated aria-label text. Keep it that way when fixing them.
