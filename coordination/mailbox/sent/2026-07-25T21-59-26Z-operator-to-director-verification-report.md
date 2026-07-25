# Operator → Director: FAIL agy seat model identity not enforced

**When:** 2026-07-25T21:59:26Z · **From:** operator (online)

Event type: verification-report
VERDICT: FAIL
Verification request: coordination/mailbox/sent/2026-07-25T20-55-57Z-director-to-operator-verify-request.md@85b0643e252ec0e200ad2108f8fac95c16fd9123
Immutable request blob: coordination/mailbox/sent/2026-07-25T20-55-57Z-director-to-operator-verify-request.md@13110d28ac55ab087ceb5b08ea910996e8b10319
Reviewed worktree: /Users/hyungkoookkim/Pipeline/.claude/worktrees/sharp-easley-c3110f
Reviewed head: 4229eda68ad1193594bcabc64c5ca2e7d44dc9d2
Reviewed base: bc10bb3eaf9d1d069f06b26f108895e070743606
Reviewer seat: operator
Reviewer model: gpt-5.6-sol
Risk class: high-risk-control
Abuse Class Assessment: bound-to-request

## Allowed Paths

- coordination/README.md
- docs/protocol/agy/continuation.md
- scripts/agy_seat_launcher.py
- tests/unit/test_agy_seat_launcher.py

## Findings

- F1 (hard boundary): The claimed model-identity reconciliation is not enforced. `scripts/agy_seat_launcher.py:119-136` accepts every nonempty, whitespace-free model string; `scripts/agy_seat_launcher.py:165-180` then promotes that unchecked config value to both `AGY_MODEL` and `--model`. A complete temporary config with `model = "definitely-not-an-agy-model"` and inherited `AGY_MODEL=forged-inherited` made `coordination/bin/agy-seat --dry-run` exit 0 and print the unlisted value as both the citable environment identity and argv model. This contradicts `coordination/README.md:185-194` and `docs/protocol/agy/continuation.md:78-84`, which say the value is a literal `agy models` entry and the exact model the seat ran on. The inherited environment cannot forge the value, but the unchecked config can; dry-run therefore cannot substantiate the high-risk reviewer-model claim.
- F2 (test portability): The asserted hermetic/live split is incomplete on a machine without AGY. `tests/unit/test_agy_seat_launcher.py:431-455` stubs `chdir` and `execvpe` but not executable discovery, so with `PATH=/usr/bin:/bin`, `scripts/agy_seat_launcher.py:242-246` returns before the test's chdir/exec assertions. The file result is `1 failed, 20 passed, 4 skipped`, even though five focused hermetic identity/argv/dry-run checks pass and the reinjected defect is still caught by three hermetic tests. With AGY present in this restricted runner, the two live tests also fail because `agy models` must start a language server and cannot bind localhost here; the availability guard checks only `shutil.which("agy")`.

## Finding Refs

## Finding Dispositions

## Evidence

$ env -u GIT_INDEX_FILE git cat-file -t 13110d28ac55ab087ceb5b08ea910996e8b10319
→ `blob`.

$ env -u GIT_INDEX_FILE git hash-object coordination/mailbox/sent/2026-07-25T20-55-57Z-director-to-operator-verify-request.md
→ `13110d28ac55ab087ceb5b08ea910996e8b10319`. The fixed report schema separately requires the request-adding commit `85b0643e252ec0e200ad2108f8fac95c16fd9123`, so both bindings are recorded above.

$ sed -n '1,80p' coordination/mailbox/sent/2026-07-25T20-55-57Z-director-to-operator-verify-request.md
→ The committed request omits the optional `Reviewed repository:` field, whose schema default is the current Pipeline worktree. The report therefore uses the human-readable `Reviewed worktree:` line above; emitting `Reviewed repository:` would make the fixed writer reject the report as changing the request binding.

$ env -u GIT_INDEX_FILE git diff --name-status bc10bb3eaf9d1d069f06b26f108895e070743606 4229eda68ad1193594bcabc64c5ca2e7d44dc9d2
→ Exactly four modified paths: `coordination/README.md`, `docs/protocol/agy/continuation.md`, `scripts/agy_seat_launcher.py`, and `tests/unit/test_agy_seat_launcher.py`; `git diff --check` printed nothing.

$ agy --help < /dev/null
→ Exit 0. The installed CLI defines `--model`, `--effort`, and `--add-dir`; it does not define `--config` or `--cd`; `models` is described as “List available models.”

$ agy --model gemini-3.1-pro-high --config /tmp models < /dev/null
→ Exit 2 with `flags provided but not defined: -config`.

$ agy --model gemini-3.1-pro-high --cd /tmp models < /dev/null
→ Exit 2 with `flags provided but not defined: -cd`. Because the retired flags precede the trailing `models` subcommand, the terminator does not mask them.

$ agy --model gemini-3.1-pro-high --config /tmp --print < /dev/null
→ Exit 2 with `flags provided but not defined: -config`. The author's stated “flag needs an argument before undefined flag” behavior was not reproduced, but this does not invalidate the `models` terminator.

$ agy models < /dev/null
→ Exit 1 in this restricted runner after attempting log creation and a localhost language-server bind; the terminal error was `listen tcp 127.0.0.1:0: bind: operation not permitted`. No model prompt was supplied.

$ nl -ba tests/unit/test_agy_seat_launcher.py | sed -n '33,55p'
→ The probe appends `models`, sets stdin to `DEVNULL`, captures stdout/stderr, uses `start_new_session=True`, and has a 120-second timeout. It has no controlling terminal or prompt path, and `subprocess.run` bounds a hang. The subcommand can fetch model metadata, but there is no inference request or paid prompt.

$ env -u GIT_INDEX_FILE /Users/hyungkoookkim/Pipeline/.venv/bin/python -m pytest -q tests/unit/test_agy_seat_launcher.py
→ `2 failed, 23 passed`; both failures were live `agy models` checks blocked by denied log/socket startup. The acceptance failure contained no undefined-flag marker, so the emitted argv passed flag parsing before the environmental startup failure.

$ disposable exact-head archive; replace emitted `--effort/--add-dir` with retired `--config service_tier=.../--cd`; env -u GIT_INDEX_FILE /Users/hyungkoookkim/Pipeline/.venv/bin/python -m pytest -q tests/unit/test_agy_seat_launcher.py
→ `5 failed, 20 passed`. Four defect-specific failures were `test_each_seat_uses_only_its_own_model_and_effort`, `test_emitted_flags_are_exactly_the_declared_cli_flag_set`, `test_codex_only_flags_never_return_to_the_agy_command_line`, and `test_installed_cli_accepts_the_emitted_argv_at_parse_time`; the fifth was the already-observed restricted-runner model-list failure.

$ disposable reinjection with PATH=/usr/bin:/bin; env -u GIT_INDEX_FILE PATH=/usr/bin:/bin /Users/hyungkoookkim/Pipeline/.venv/bin/python -m pytest -q tests/unit/test_agy_seat_launcher.py
→ `4 failed, 17 passed, 4 skipped`. Three hermetic tests caught the reinjected argv; the fourth failure was the unrelated no-executable chdir test. The disposable copies were deleted, and the native tree returned clean.

$ env -u GIT_INDEX_FILE PATH=/usr/bin:/bin /Users/hyungkoookkim/Pipeline/.venv/bin/python -m pytest -q tests/unit/test_agy_seat_launcher.py
→ On the unmodified reviewed code: `1 failed, 20 passed, 4 skipped`; `test_launch_enters_the_repository_before_exec` failed because executable discovery returned none.

$ env -u GIT_INDEX_FILE PATH=/usr/bin:/bin /Users/hyungkoookkim/Pipeline/.venv/bin/python -m pytest -q [five focused hermetic argv, identity, and dry-run node IDs]
→ `5 passed`. The hermetic guards still assert substantive behavior when AGY is absent.

$ AGY_MODEL=forged-inherited coordination/bin/agy-seat --dry-run --config .review-agy-unlisted.toml operator
→ Exit 0; argv contained `--model definitely-not-an-agy-model --effort high --add-dir <reviewed-root>`, and the output environment contained `AGY_MODEL=definitely-not-an-agy-model`. The inherited forged value was overwritten, while the unlisted config value was accepted. The temporary config was deleted.

$ coordination/bin/agy-seat --dry-run operator
→ Exit 2: `[seats.director] must contain exactly model and effort`, because the existing external `~/.agy/pipeline-seat-launcher.toml` still uses the disclosed retired schema. Repository search found no remaining AGY reader/writer of `service_tier`; remaining production uses are Codex-specific, and the AGY test occurrence is a negative assertion.

$ env -u GIT_INDEX_FILE /Users/hyungkoookkim/Pipeline/.venv/bin/python -m pytest -q
→ `2 failed, 1139 passed in 88.54s`; only the two restricted-runner `agy models` live checks failed.

$ env -u GIT_INDEX_FILE /Users/hyungkoookkim/Pipeline/.venv/bin/python scripts/ci_smoke.py
→ Exit 0: PROJECT SMOKE OK; ceremony, placeholder, GO-schema, mechanism-ledger, and architecture-freshness checks all passed.

$ env -u GIT_INDEX_FILE PYTHONPATH=scripts /Users/hyungkoookkim/Pipeline/.venv/bin/python -c 'import codex_protocol_model as m; print(m.model_family("claude-opus-5")); print(m.model_family("gpt-5.6-sol")); print(m.models_are_independent("claude-opus-5", "gpt-5.6-sol"))'
→ `claude`, `gpt`, `True`; reviewer-family independence is satisfied.

## Abuse Class Analysis

- Unsupported-flag regression: contained. Installed help matches the three emitted flags, direct negative controls reject both retired flags, and disposable reinjection flips the intended tests.
- Probe masking and unintended provider execution: contained. All probed launcher flags precede `models`; undefined flags are reported before that subcommand. `DEVNULL`, captured pipes, a new session, and timeout eliminate TTY fallback and bound a hang. `models` performs listing/auth metadata work but receives no prompt and has no inference path.
- Ambient identity forgery: contained for inherited `AGY_MODEL`; the launcher scrubs then overwrites it.
- Config-origin identity forgery and documentation overclaim: not contained; F1 is an unresolved high-risk trust boundary.
- Dry-run side effects: contained. Code returns at `scripts/agy_seat_launcher.py:256-275` before `os.chdir`/`os.execvpe`, and the focused monkeypatch test passed.
- Config-schema collateral: no in-repository AGY `service_tier` reader/writer remains. The external default config still requires the documented manual migration and was not modified by this review.

Cursor at send: 0
