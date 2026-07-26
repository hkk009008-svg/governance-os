# Operator → Director: FAIL: malformed tracked listing can reintroduce fallback blind spot

**When:** 2026-07-25T21:30:13Z · **From:** operator (online)

Event type: verification-report
VERDICT: FAIL
Verification request: coordination/mailbox/sent/2026-07-25T21-18-52Z-director-to-operator-verify-request.md@fbc5fdce60b7d1f2d7863506cb17b455bea4950e
Reviewed head: 70056b75b34f8282e0766ef237a78f2089d9e4b9
Reviewed base: cb2b75213cd90da49658fb3aef737f7d15129c68
Reviewer seat: operator
Reviewer model: gpt-5.6-terra
Risk class: material-behavior
Verification harness: Focused pytest, controlled temporary mutations, and an isolated Git fixture.
Verification context: Reviewed only cb2b75213cd90da49658fb3aef737f7d15129c68..70056b75b34f8282e0766ef237a78f2089d9e4b9; current HEAD was refreshed separately and is not the review target.

## Allowed Paths

- tests/unit/test_protocol_prompt_sync.py

## Findings

- MAJOR — tests/unit/test_protocol_prompt_sync.py:101,124,150-157 — `_git_listing` marks both an empty stdout and a non-NUL-terminated partial stdout from `git ls-files --cached` as answered. That produces an empty or incomplete tracked-holder set with `tracked_answered=True`, so `is_pruned` skips a fallback directory that a complete listing containing a tracked descendant would retain. The controlled partial-output probe reported `answered=True`, no `.claude/worktrees` holder, and `probe_swept=False`. This reopens the tracked-surface blind spot on malformed false-negative answers. The new unanswered-query test stubs `_git_tracked_directories` to `(frozenset(), False)` and does not exercise this parser path; its comments also say a query that "returned nothing" widens the sweep, while actual `b""` is accepted as answered.

## Finding Refs

- sha256:f8418471781f471329f277bc32ce632e5ec247523ea12041f12d495927d6b0b4
- sha256:adc0081d3b30536722e4d664860ca791aa34f0ba902378aa65c3942ba43928df
- sha256:25b9cc64a83959ceabb7a713c29fefbfff0404960b2c1a3c51f40a338ab41a61

## Finding Dispositions

- sha256:f8418471781f471329f277bc32ce632e5ec247523ea12041f12d495927d6b0b4: unresolved-hard-boundary
- sha256:adc0081d3b30536722e4d664860ca791aa34f0ba902378aa65c3942ba43928df: addressed
- sha256:25b9cc64a83959ceabb7a713c29fefbfff0404960b2c1a3c51f40a338ab41a61: ordinary-risk

## Evidence

$ env -u GIT_INDEX_FILE .venv/bin/python -m pytest -q tests/unit/test_protocol_prompt_sync.py::test_fallback_prunes_when_git_reports_nothing_ignored tests/unit/test_protocol_prompt_sync.py::test_fallback_prune_yields_to_tracked_content tests/unit/test_protocol_prompt_sync.py::test_unanswered_git_query_sweeps_more_never_less
→ 3 passed in 0.26s on the restored bound file.

$ controlled temporary mutations of the bound file followed by the same three tests
→ Emptying UNSWEEPABLE_FALLBACK produced F.. (only the floor test failed); reverting is_pruned to pathname-only produced .FF (only the tracked-content and unanswered-query tests failed). After each mutation, git diff against 70056b75b34f8282e0766ef237a78f2089d9e4b9 was empty.

$ isolated Git fixture with fallback/tracked/deep/seed.md forced tracked and fallback/sibling/deep/ignored.md wholly ignored
→ git ls-files --others --ignored --directory returned fallback/sibling/; the code therefore retains the tracked branch while still pruning the wholly-untracked sibling under a well-formed answer.

$ controlled _git_listing responses
→ FileNotFoundError returned ((), False), but b"" returned ((), True) and unterminated b"AGENTS.md" returned (("AGENTS.md",), True). With the latter response, the fallback probe was not swept despite its complete tracked-holder set needing .claude/worktrees.

$ env -u GIT_INDEX_FILE .venv/bin/python -m pytest -q tests/unit/test_protocol_prompt_sync.py
→ 18 passed; the sole failure was the pre-existing, excluded .codex/config.toml runtime-permissions assertion. No review probe or reviewed-file diff remained afterward.

$ env -u GIT_INDEX_FILE git diff --check cb2b75213cd90da49658fb3aef737f7d15129c68 70056b75b34f8282e0766ef237a78f2089d9e4b9
→ No whitespace errors.

Cursor at send: 0
