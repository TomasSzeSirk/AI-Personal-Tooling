import argparse
import asyncio
import sys
import tempfile
import time
from pathlib import Path

from gemini_mcp import config as config_mod
from gemini_mcp.config import ConfigError
from gemini_mcp.errors import ResponseTimeout


class _BlockPlaywrightImport:
    """sys.meta_path finder that fails any `import playwright*`.

    Stage 2's whole point is that completion detection is testable without a
    browser. Installed at the top of --self-test to prove no code path pulls
    in Playwright.
    """

    def find_spec(self, name, path, target=None):
        if name.split(".")[0] in ("playwright", "mcp"):
            raise ImportError(f"{name} must not be imported by --self-test (Stage 2)")
        return None


def _self_test_session() -> None:
    from gemini_mcp import session as session_mod

    # Streaming response: text changes over MANY polls — outliving one whole
    # 3 * stable_s window — with a brief mid-stream pause shorter than that
    # window, then stops changing for good. is_generating stays true
    # throughout, so only the stability path can resolve this.
    #
    # The LENGTH is load-bearing: if the change-clock (`last_change = now`)
    # were never reset, a stream outliving one window would truncate. A short
    # stream that finishes inside one window cannot catch that.
    _acc = ""
    chunks = []
    for _i in range(20):
        _acc += f"token{_i} "
        chunks.append(_acc)
        if _i == 9:
            chunks.append(_acc)  # brief mid-stream pause, shorter than the window
    _final_text = _acc
    chunks += [_final_text] * 12

    def make_text_source(seq):
        state = {"i": 0}

        def _get():
            i = min(state["i"], len(seq) - 1)
            state["i"] += 1
            return seq[i]

        return _get

    get_text = make_text_source(chunks)
    result = asyncio.run(
        session_mod.wait_for_completion(
            get_text=get_text,
            is_generating=lambda: True,
            timeout_s=2.0,
            stable_s=0.05,
            poll_s=0.01,
        )
    )
    assert result == _final_text, f"stability path returned {result!r}"

    # Indicator path: is_generating flips false a couple of polls in, while
    # text is still actively changing (and would not have stabilized on its
    # own for a long time). Must resolve promptly, not wait out stable_s.
    growing = ["a", "ab", "abc", "abcd", "abcde", "abcdef"]
    gen_flags = [True, True, False, False, False, False]
    step_state = {"i": 0}

    def _step_text():
        i = min(step_state["i"], len(growing) - 1)
        return growing[i]

    def _is_generating():
        # Called once per poll, after get_text() in the same iteration —
        # advance here so both callables agree on "this poll's" index.
        i = min(step_state["i"], len(gen_flags) - 1)
        step_state["i"] += 1
        return gen_flags[i]

    t0 = time.monotonic()
    result = asyncio.run(
        session_mod.wait_for_completion(
            get_text=_step_text,
            is_generating=_is_generating,
            timeout_s=5.0,
            stable_s=1.0,
            poll_s=0.01,
        )
    )
    elapsed = time.monotonic() - t0
    assert result == "abc", f"indicator path returned {result!r}"
    assert elapsed < 1.0, f"indicator path took {elapsed}s, should not wait out stable_s"

    # Never stabilizes, indicator never clears -> ResponseTimeout naming the limit.
    def _never_stable():
        _never_stable.n += 1
        return f"chunk-{_never_stable.n}"

    _never_stable.n = 0

    t_timeout = time.monotonic()
    try:
        asyncio.run(
            session_mod.wait_for_completion(
                get_text=_never_stable,
                is_generating=lambda: True,
                timeout_s=0.05,
                stable_s=1.0,
                poll_s=0.01,
            )
        )
        assert False, "expected ResponseTimeout"
    except ResponseTimeout as e:
        assert "0.05" in str(e), f"ResponseTimeout message missing the limit: {e}"
    # Pin that the deadline is actually enforced, not merely reported: a
    # disabled timeout check would still raise eventually and pass the message
    # assert above, just far too late.
    assert time.monotonic() - t_timeout < 1.0, "timeout was not enforced promptly"

    # Long pre-token thinking phase: empty text with the indicator pinned true
    # for longer than a whole 3 * stable_s window, THEN the real answer streams
    # in. Must not resolve as a successful "" while still generating — a Gem
    # can think for well over 3 * stable_s before its first token.
    think_polls = 10  # * poll_s=0.01 = 0.1s, vs a 3 * 0.02 = 0.06s window
    thinking = [""] * think_polls + ["The answer is 42."] * 12
    think_state = {"i": 0}

    def _thinking_text():
        i = min(think_state["i"], len(thinking) - 1)
        think_state["i"] += 1
        return thinking[i]

    result = asyncio.run(
        session_mod.wait_for_completion(
            get_text=_thinking_text,
            is_generating=lambda: True,
            timeout_s=5.0,
            stable_s=0.02,
            poll_s=0.01,
        )
    )
    assert result == "The answer is 42.", f"thinking phase returned {result!r}"

    # Empty response that never changes -> returns "" rather than hanging.
    # The indicator must read FALSE here: a genuinely finished empty answer has
    # the spinner cleared. Pinned true it would be indistinguishable from the
    # pre-token thinking phase, where returning "" is a wrong answer that looks
    # like success — so that combination now correctly runs to ResponseTimeout.
    t0 = time.monotonic()
    result = asyncio.run(
        session_mod.wait_for_completion(
            get_text=lambda: "",
            is_generating=lambda: False,
            timeout_s=5.0,
            stable_s=0.02,
            poll_s=0.01,
        )
    )
    elapsed = time.monotonic() - t0
    assert result == "", f"empty-response path returned {result!r}"
    assert elapsed < 1.0, f"empty response should resolve fast, took {elapsed}s"

    # Indicator reads false before generation has actually started (empty
    # text, network round-trip not finished yet) for the first two polls,
    # then the real response streams in. Must not return "" early.
    texts = ["", "", "The answer is 42.", "The answer is 42.", "The answer is 42."]
    flags = [False, False, True, False, False]
    late_state = {"i": 0}

    def _late_text():
        i = min(late_state["i"], len(texts) - 1)
        return texts[i]

    def _late_generating():
        i = min(late_state["i"], len(flags) - 1)
        late_state["i"] += 1
        return flags[i]

    result = asyncio.run(
        session_mod.wait_for_completion(
            get_text=_late_text,
            is_generating=_late_generating,
            timeout_s=2.0,
            stable_s=1.0,
            poll_s=0.01,
        )
    )
    assert result == "The answer is 42.", f"pre-start false indicator returned {result!r}"

    # Same shape as the indicator-path case above, but driven with async
    # callables (Playwright's inner_text/is_visible are coroutine functions).
    # Must resolve to the same result as the sync equivalent, not hang until
    # timeout on forever-truthy coroutine objects.
    async_growing = ["a", "ab", "abc", "abcd", "abcde", "abcdef"]
    async_flags = [True, True, False, False, False, False]
    async_state = {"i": 0}

    async def _async_text():
        i = min(async_state["i"], len(async_growing) - 1)
        return async_growing[i]

    async def _async_generating():
        i = min(async_state["i"], len(async_flags) - 1)
        async_state["i"] += 1
        return async_flags[i]

    result = asyncio.run(
        session_mod.wait_for_completion(
            get_text=_async_text,
            is_generating=_async_generating,
            timeout_s=2.0,
            stable_s=1.0,
            poll_s=0.01,
        )
    )
    assert result == "abc", f"async callables path returned {result!r}"

    # A transient exception from either callable (e.g. reading a detached
    # locator mid-re-render) must not kill the run; the last good text
    # should carry through and the run should still complete.
    flaky_chunks = ["Hel", "Hello", "Hello wor", "Hello world", "Hello world"]
    flaky_state = {"i": 0}

    def _flaky_text():
        i = min(flaky_state["i"], len(flaky_chunks) - 1)
        flaky_state["i"] += 1
        if i == 2:
            raise RuntimeError("detached node")
        return flaky_chunks[i]

    result = asyncio.run(
        session_mod.wait_for_completion(
            get_text=_flaky_text,
            is_generating=lambda: True,
            timeout_s=2.0,
            stable_s=0.05,
            poll_s=0.01,
        )
    )
    assert result == "Hello world", f"transient exception path returned {result!r}"

    # Mid-answer pause (e.g. a slow-rendering code block) longer than
    # stable_s but shorter than 3x stable_s, while is_generating() stays
    # true throughout. Must NOT be mistaken for done -- the answer should
    # keep streaming past the pause to its real, longer final text.
    pause_texts = [
        "Par",
        "Partial",
        "Partial",
        "Partial",
        "Partial done",
        "Partial done",
    ]
    pause_flags = [True, True, True, True, True, False]
    pause_state = {"i": 0}

    def _pause_text():
        i = min(pause_state["i"], len(pause_texts) - 1)
        return pause_texts[i]

    def _pause_generating():
        i = min(pause_state["i"], len(pause_flags) - 1)
        pause_state["i"] += 1
        return pause_flags[i]

    result = asyncio.run(
        session_mod.wait_for_completion(
            get_text=_pause_text,
            is_generating=_pause_generating,
            timeout_s=2.0,
            stable_s=0.02,
            poll_s=0.01,
        )
    )
    assert result == "Partial done", f"mid-answer pause path returned {result!r}"

    # is_generating() raises on the first two polls while text is still
    # streaming in underneath. Must not be mistaken for "done" (that would
    # need generating=False on error) nor kill the run (that would need the
    # try/except removed) -- the deadline/stability path should carry it
    # through to the full text.
    gen_raise_chunks = ["Hel", "Hello", "Hello wor", "Hello world", "Hello world"]
    gen_raise_state = {"i": 0, "calls": 0}

    def _gen_raise_text():
        i = min(gen_raise_state["i"], len(gen_raise_chunks) - 1)
        gen_raise_state["i"] += 1
        return gen_raise_chunks[i]

    def _gen_raise_generating():
        # Raises on the first two polls, then reports "still generating" for
        # the rest -- completion must come from the stability path, so this
        # also pins that a raise defaults to generating=True, not False.
        gen_raise_state["calls"] += 1
        if gen_raise_state["calls"] <= 2:
            raise RuntimeError("indicator node detached")
        return True

    result = asyncio.run(
        session_mod.wait_for_completion(
            get_text=_gen_raise_text,
            is_generating=_gen_raise_generating,
            timeout_s=2.0,
            stable_s=0.05,
            poll_s=0.01,
        )
    )
    assert result == "Hello world", f"is_generating-raises path returned {result!r}"

    # Real defaults (stable_s=2.0, poll_s=0.25), as Stage 5 will actually call
    # this. Pin the indicator false-after-text so it resolves via the
    # indicator path rather than waiting out the 2s stability window.
    default_texts = ["", "PONG", "PONG", "PONG"]
    default_flags = [False, False, True, True]
    default_state = {"i": 0}

    def _default_text():
        i = min(default_state["i"], len(default_texts) - 1)
        return default_texts[i]

    def _default_generating():
        i = min(default_state["i"], len(default_flags) - 1)
        default_state["i"] += 1
        return default_flags[i]

    t0 = time.monotonic()
    result = asyncio.run(
        session_mod.wait_for_completion(
            get_text=_default_text,
            is_generating=_default_generating,
            timeout_s=5.0,
        )
    )
    elapsed = time.monotonic() - t0
    assert result == "PONG", f"default-params path returned {result!r}"
    assert elapsed < 1.0, f"default-params path took {elapsed}s, should resolve via indicator"


def _self_test() -> None:
    valid_yaml = """
profile_dir: ~/somewhere/profile
headless: false
response_timeout_s: 30
tools:
  design_review:
    gem_url: https://gemini.google.com/gem/abc
    description: Architecture feedback
"""
    minimal_yaml = """
tools:
  design_review:
    gem_url: https://gemini.google.com/gem/abc
    description: Architecture feedback
"""
    empty_tools_yaml = """
tools: {}
"""
    missing_gem_url_yaml = """
tools:
  design_review:
    description: Architecture feedback
"""
    invalid_name_yaml = """
tools:
  "not a valid name":
    gem_url: https://gemini.google.com/gem/abc
    description: Architecture feedback
"""
    tools_as_list_yaml = """
tools:
  - design_review
"""
    broken_yaml = """
tools:
  design_review:
    gem_url: https://gemini.google.com/gem/abc
  description: [unterminated
"""
    top_level_list_yaml = """
- design_review
"""
    numeric_tool_name_yaml = """
tools:
  123:
    gem_url: https://gemini.google.com/gem/abc
    description: Architecture feedback
"""
    entry_not_mapping_yaml = """
tools:
  design_review: hello
"""
    bad_profile_dir_yaml = """
profile_dir: 123
tools:
  design_review:
    gem_url: https://gemini.google.com/gem/abc
    description: Architecture feedback
"""
    bad_headless_yaml = """
headless: not-a-bool
tools:
  design_review:
    gem_url: https://gemini.google.com/gem/abc
    description: Architecture feedback
"""
    bad_timeout_yaml = """
response_timeout_s: soon
tools:
  design_review:
    gem_url: https://gemini.google.com/gem/abc
    description: Architecture feedback
"""
    bad_gem_url_type_yaml = """
tools:
  design_review:
    gem_url: [https://gemini.google.com/gem/abc]
    description: Architecture feedback
"""
    bad_description_type_yaml = """
tools:
  design_review:
    gem_url: https://gemini.google.com/gem/abc
    description: 42
"""

    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)

        # Valid config parses; explicit values override defaults.
        p = tmp_path / "valid.yaml"
        p.write_text(valid_yaml)
        cfg = config_mod.load(p)
        assert cfg["headless"] is False
        assert cfg["response_timeout_s"] == 30
        assert cfg["tools"]["design_review"]["gem_url"] == "https://gemini.google.com/gem/abc"

        # Minimal config gets defaults applied.
        p = tmp_path / "minimal.yaml"
        p.write_text(minimal_yaml)
        cfg = config_mod.load(p)
        assert cfg["headless"] is True
        assert cfg["response_timeout_s"] == 120
        assert cfg["profile_dir"] == str(Path("~/.gemini_mcp/profile").expanduser())

        # Missing file raises ConfigError naming config.example.yaml.
        missing_path = tmp_path / "does_not_exist.yaml"
        try:
            config_mod.load(missing_path)
            assert False, "expected ConfigError for missing file"
        except ConfigError as e:
            assert "config.example.yaml" in str(e)

        # Empty tools raises ConfigError.
        p = tmp_path / "empty_tools.yaml"
        p.write_text(empty_tools_yaml)
        try:
            config_mod.load(p)
            assert False, "expected ConfigError for empty tools"
        except ConfigError:
            pass

        # Missing gem_url raises ConfigError.
        p = tmp_path / "missing_gem_url.yaml"
        p.write_text(missing_gem_url_yaml)
        try:
            config_mod.load(p)
            assert False, "expected ConfigError for missing gem_url"
        except ConfigError:
            pass

        # Invalid tool name raises ConfigError.
        p = tmp_path / "invalid_name.yaml"
        p.write_text(invalid_name_yaml)
        try:
            config_mod.load(p)
            assert False, "expected ConfigError for invalid tool name"
        except ConfigError:
            pass

        # tools as a list (not a mapping) raises ConfigError.
        p = tmp_path / "tools_as_list.yaml"
        p.write_text(tools_as_list_yaml)
        try:
            config_mod.load(p)
            assert False, "expected ConfigError for tools as a list"
        except ConfigError:
            pass

        # Broken YAML raises ConfigError, not a raw yaml.YAMLError.
        p = tmp_path / "broken.yaml"
        p.write_text(broken_yaml)
        try:
            config_mod.load(p)
            assert False, "expected ConfigError for broken YAML"
        except ConfigError:
            pass

        # Top-level list (not a mapping) raises ConfigError, not AttributeError.
        p = tmp_path / "top_level_list.yaml"
        p.write_text(top_level_list_yaml)
        try:
            config_mod.load(p)
            assert False, "expected ConfigError for top-level list"
        except ConfigError:
            pass

        # Non-string profile_dir raises ConfigError, not TypeError.
        p = tmp_path / "bad_profile_dir.yaml"
        p.write_text(bad_profile_dir_yaml)
        try:
            config_mod.load(p)
            assert False, "expected ConfigError for non-string profile_dir"
        except ConfigError:
            pass

        # Non-bool headless raises ConfigError.
        p = tmp_path / "bad_headless.yaml"
        p.write_text(bad_headless_yaml)
        try:
            config_mod.load(p)
            assert False, "expected ConfigError for non-bool headless"
        except ConfigError:
            pass

        # Non-int response_timeout_s raises ConfigError.
        p = tmp_path / "bad_timeout.yaml"
        p.write_text(bad_timeout_yaml)
        try:
            config_mod.load(p)
            assert False, "expected ConfigError for non-int response_timeout_s"
        except ConfigError:
            pass

        # Non-string gem_url raises ConfigError.
        p = tmp_path / "bad_gem_url_type.yaml"
        p.write_text(bad_gem_url_type_yaml)
        try:
            config_mod.load(p)
            assert False, "expected ConfigError for non-string gem_url"
        except ConfigError:
            pass

        # Non-string description raises ConfigError.
        p = tmp_path / "bad_description_type.yaml"
        p.write_text(bad_description_type_yaml)
        try:
            config_mod.load(p)
            assert False, "expected ConfigError for non-string description"
        except ConfigError:
            pass

        # A non-string tool name raises ConfigError, not AttributeError.
        p = tmp_path / "numeric_tool_name.yaml"
        p.write_text(numeric_tool_name_yaml)
        try:
            config_mod.load(p)
            assert False, "expected ConfigError for a numeric tool name"
        except ConfigError:
            pass

        # A tool entry that isn't a mapping raises ConfigError.
        p = tmp_path / "entry_not_mapping.yaml"
        p.write_text(entry_not_mapping_yaml)
        try:
            config_mod.load(p)
            assert False, "expected ConfigError for a non-mapping tool entry"
        except ConfigError:
            pass

        # A config saved as UTF-16 (what PowerShell's `>` produces on Windows)
        # raises ConfigError, not UnicodeDecodeError.
        p = tmp_path / "utf16.yaml"
        p.write_bytes(valid_yaml.encode("utf-16"))
        try:
            config_mod.load(p)
            assert False, "expected ConfigError for a UTF-16 encoded config"
        except ConfigError:
            pass

    # Install a meta_path finder that fails any `import playwright*` before
    # running the session tests, to prove completion detection genuinely
    # needs no browser.
    blocker = _BlockPlaywrightImport()
    sys.meta_path.insert(0, blocker)
    try:
        _self_test_session()
    finally:
        sys.meta_path.remove(blocker)

    print("self-test: OK")


def _cmd_login(args: argparse.Namespace) -> None:
    raise NotImplementedError("login is implemented in a later stage")


def _cmd_serve(args: argparse.Namespace) -> None:
    config_mod.load()
    raise NotImplementedError("serve is implemented in a later stage")


def main() -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    parser = argparse.ArgumentParser(prog="gemini_mcp")
    parser.add_argument("--self-test", action="store_true", help="run the self-test suite and exit")
    subparsers = parser.add_subparsers(dest="command")
    subparsers.add_parser("login", help="interactively sign in and save the browser profile")
    subparsers.add_parser("serve", help="start the MCP server over stdio")

    args = parser.parse_args()

    if args.self_test:
        _self_test()
        return 0

    if args.command == "login":
        try:
            _cmd_login(args)
        except NotImplementedError as e:
            print(f"login: not implemented yet ({e})", file=sys.stderr)
            return 1
        return 0

    if args.command == "serve":
        try:
            _cmd_serve(args)
        except ConfigError as e:
            print(f"serve: {e}", file=sys.stderr)
            return 1
        except NotImplementedError as e:
            print(f"serve: not implemented yet ({e})", file=sys.stderr)
            return 1
        return 0

    parser.print_help()
    return 1


if __name__ == "__main__":
    sys.exit(main())
