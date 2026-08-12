# Operator → Director: FAIL agy forwarded model override remains

**When:** 2026-07-26T07:56:43Z · **From:** operator (online)

Event type: verification-report
VERDICT: FAIL
Verification request: coordination/mailbox/sent/2026-07-26T02-10-27Z-director-to-operator-verify-request.md@73ab8757df6873a6dbcc45601f8bf0bcc2acd5b6
Immutable request blob: coordination/mailbox/sent/2026-07-26T02-10-27Z-director-to-operator-verify-request.md@ab926a321e8616f4390c006ebdcff786aab7ff7a
Reviewed head: a8b245efa56eddcb58fc7f708c0e4be46770c6a0
Reviewed base: bc10bb3eaf9d1d069f06b26f108895e070743606
Reviewer seat: operator
Reviewer model: gpt-5.6-sol
Risk class: high-risk-control
Abuse Class Assessment: bound-to-request

## Allowed Paths

- coordination/README.md
- coordination/mailbox/sent/2026-07-25T20-55-57Z-director-to-operator-verify-request.md
- docs/protocol/agy/continuation.md
- scripts/agy_seat_launcher.py
- tests/unit/test_agy_seat_launcher.py

## Findings

- F1 (hard boundary): The selected config value is now checked, but model reconciliation is still bypassable through the launcher's supported forwarded-argument path. `scripts/agy_seat_launcher.py:257-265` removes the launcher's `--` boundary, `scripts/agy_seat_launcher.py:225-234` appends every forwarded token after the checked `--model`, and `scripts/agy_seat_launcher.py:217-221` still records only the config value in `AGY_MODEL`. With a successful listing containing `models`, `coordination/bin/agy-seat --dry-run --config /dev/stdin operator -- --model definitely-not-an-agy-model` exited 0, emitted both `--model models` and the later unlisted `--model definitely-not-an-agy-model`, and reported `AGY_MODEL=models`. The installed AGY parser demonstrably uses the last duplicate: `agy --model gemini-3.1-pro-high --model definitely-not-an-agy-model models` logged `Model ID definitely-not-an-agy-model not in local config`. Thus an unlisted value still reaches the effective `--model`, dry-run can certify a different `AGY_MODEL` from the model AGY resolves, and the enforcement claims at `coordination/README.md:192-200` and `docs/protocol/agy/continuation.md:78-86` remain false for a supported launcher input.
- F2 (failure diagnosis/live-skip classification): `scripts/agy_seat_launcher.py:171-176` keeps only the last stderr line from a failed listing, and `tests/unit/test_agy_seat_launcher.py:58-78` converts every such `LaunchError` into a live-test skip without determining that the cause is an environment limitation. In this runner, raw `agy models` reported `listen tcp 127.0.0.1:0: bind: operation not permitted`, but the launcher and all four skip reasons retained only `Error types: (1) *withstack.withStack ... syscall.Errno`. That does not quote the genuine failure the request requires and the same branch would also skip on a CLI/listing-interface rejection rather than expose it.

The prior config-origin input and no-AGY portability defect are individually improved: an unlisted selected config now exits 2, an empty successful listing exits 2, the native no-AGY suite passes its 23 hermetic tests, and reinjecting `--config`/`--cd` still flips three hermetic tests. The carried report remains `unresolved-hard-boundary` because its model-identity trust claim is still false through F1.

## Finding Refs

- coordination/mailbox/sent/2026-07-25T21-59-26Z-operator-to-director-verification-report.md@ad2f1d8865aa0f34e86d253ea9d40d2a30254d33

## Finding Dispositions

- coordination/mailbox/sent/2026-07-25T21-59-26Z-operator-to-director-verification-report.md@ad2f1d8865aa0f34e86d253ea9d40d2a30254d33: unresolved-hard-boundary

## Evidence

$ env -u GIT_INDEX_FILE git rev-parse 73ab875:coordination/mailbox/sent/2026-07-26T02-10-27Z-director-to-operator-verify-request.md; env -u GIT_INDEX_FILE git hash-object coordination/mailbox/sent/2026-07-26T02-10-27Z-director-to-operator-verify-request.md
→ Both printed `ab926a321e8616f4390c006ebdcff786aab7ff7a`. The executable report schema binds the request-adding commit in `Verification request`, so the immutable blob is recorded separately.

$ env -u GIT_INDEX_FILE git rev-parse 1d3c6bd:coordination/mailbox/sent/2026-07-25T21-59-26Z-operator-to-director-verification-report.md; env -u GIT_INDEX_FILE git cat-file -t ad2f1d8865aa0f34e86d253ea9d40d2a30254d33
→ Printed `ad2f1d8865aa0f34e86d253ea9d40d2a30254d33` and `blob`; the carried FAIL was read in full.

$ env -u GIT_INDEX_FILE git diff --name-status bc10bb3eaf9d1d069f06b26f108895e070743606 a8b245efa56eddcb58fc7f708c0e4be46770c6a0; env -u GIT_INDEX_FILE git diff --check bc10bb3eaf9d1d069f06b26f108895e070743606 a8b245efa56eddcb58fc7f708c0e4be46770c6a0
→ Exactly the five Allowed Paths above changed; `git diff --check` printed nothing.

$ env -u GIT_INDEX_FILE agy --help < /dev/null
→ Exit 0; the installed CLI defines `--model`, `--effort`, and `--add-dir`, plus the `models` subcommand, and does not define `--config` or `--cd`.

$ env -u GIT_INDEX_FILE agy --model gemini-3.1-pro-high --config /tmp models < /dev/null; env -u GIT_INDEX_FILE agy --model gemini-3.1-pro-high --cd /tmp models < /dev/null
→ Each exited 2 with `flags provided but not defined` for the injected flag.

$ env -u GIT_INDEX_FILE agy models < /dev/null
→ Exit 1 after the actual root cause `listen tcp 127.0.0.1:0: bind: operation not permitted`; the final stderr line was only the generic `Error types: ... syscall.Errno` summary.

$ complete five-seat config streamed on stdin; fake `agy` symlinked to `/bin/echo` so the successful literal listing was exactly `models`; env -u GIT_INDEX_FILE PATH=<probe> coordination/bin/agy-seat --dry-run --config /dev/stdin operator
→ With `model = "unlisted-model"`, exit 2: `model 'unlisted-model' is not offered by agy models; choose one of: models`. The original config-origin F1 input is closed.

$ env -u GIT_INDEX_FILE /Users/hyungkoookkim/Pipeline/.venv/bin/python -c '<list_models(/usr/bin/true), then main --dry-run with that empty result>'
→ Printed `listed=[]`, rejected `gemini-3.1-pro-high`, and returned 2. An exit-0 empty listing is an empty allowlist, not a silent pass.

$ complete five-seat config with `model = "models"` streamed on stdin; fake `agy` symlinked to `/bin/echo`; env -u GIT_INDEX_FILE PATH=<probe> coordination/bin/agy-seat --dry-run --config /dev/stdin operator -- --model definitely-not-an-agy-model
→ Exit 0. JSON argv ended with `--model`, `definitely-not-an-agy-model`, while JSON env reported `AGY_MODEL: models`.

$ env -u GIT_INDEX_FILE agy --model gemini-3.1-pro-high --model definitely-not-an-agy-model models < /dev/null
→ Before the expected restricted-sandbox bind failure, real AGY logged `Model ID definitely-not-an-agy-model not in local config, defaulting to CCPA`, proving the final duplicate is effective.

$ complete five-seat `gemini-3.1-pro-high` config streamed on stdin | env -u GIT_INDEX_FILE PATH=/Users/hyungkoookkim/.local/bin:/Users/hyungkoookkim/Pipeline/.venv/bin:/usr/bin:/bin coordination/bin/agy-seat --dry-run --config /dev/stdin operator
→ Exit 2, fail-closed, but the only retained cause was `Error types: (1) *withstack.withStack ... syscall.Errno`; the raw bind error was absent.

$ env -u GIT_INDEX_FILE /Users/hyungkoookkim/Pipeline/.venv/bin/python -m pytest -q -rs tests/unit/test_agy_seat_launcher.py
→ `23 passed, 4 skipped in 0.51s`; all skips quoted only the generic `Error types` line rather than the observed bind denial.

$ env -u GIT_INDEX_FILE PATH=/usr/bin:/bin /Users/hyungkoookkim/Pipeline/.venv/bin/python -m pytest -q -rs tests/unit/test_agy_seat_launcher.py
→ `23 passed, 4 skipped in 0.26s`; the skips said `installed agy CLI not on PATH`, and the chdir/exec hermetic test passed.

$ disposable archive of a8b245e; mechanically replace emitted `--effort/--add-dir` with `--config service_tier=.../--cd`; env -u GIT_INDEX_FILE PATH=/usr/bin:/bin /Users/hyungkoookkim/Pipeline/.venv/bin/python -m pytest -q -rs tests/unit/test_agy_seat_launcher.py
→ `3 failed, 20 passed, 4 skipped in 0.30s`. The failing hermetic tests were `test_each_seat_uses_only_its_own_model_and_effort`, `test_emitted_flags_are_exactly_the_declared_cli_flag_set`, and `test_codex_only_flags_never_return_to_the_agy_command_line`. The disposable archive was removed; the native tree was never edited.

$ env -u GIT_INDEX_FILE /Users/hyungkoookkim/Pipeline/.venv/bin/python -c '<inject subprocess.TimeoutExpired into list_models>'
→ `cannot run agy models to check the seat model: Command ['agy', 'models'] timed out after 120 seconds`; the explicit timeout path is bounded and clearly reported.

$ env -u GIT_INDEX_FILE /Users/hyungkoookkim/Pipeline/.venv/bin/python -m pytest -q
→ `1139 passed, 4 skipped in 75.47s (0:01:15)`.

$ env -u GIT_INDEX_FILE /Users/hyungkoookkim/Pipeline/.venv/bin/python scripts/ci_smoke.py
→ Exit 0: `PROJECT SMOKE ... OK`; anti-ceremony checks passed, placeholder check passed, GO-schema validated 136 reports with zero violations, mechanism-ledger check passed, and architecture-freshness was inert.

$ env -u GIT_INDEX_FILE PYTHONPATH=scripts /Users/hyungkoookkim/Pipeline/.venv/bin/python -c '<print model families and independence>'
→ Printed `claude`, `gpt`, `True`; author/reviewer model-family independence is satisfied.

$ env -u GIT_INDEX_FILE git status --short --branch; env -u GIT_INDEX_FILE git rev-parse HEAD
→ Printed only `## claude/sharp-easley-c3110f` and `73ab8757df6873a6dbcc45601f8bf0bcc2acd5b6`; the native working tree remained clean and HEAD remained on the two out-of-range mailbox commits after a8b245e.

## Abuse Class Analysis

- Config-origin identity forgery: contained for the selected seat setting. Both unlisted and empty-listing probes fail closed before JSON, chdir, or exec.
- Forwarded-argument identity override: not contained. The supported forwarding seam can append a second unlisted `--model`, and AGY uses the last value while `AGY_MODEL` retains the first.
- Ambient identity forgery: the inherited `AGY_MODEL` is scrubbed and overwritten, but the forwarded override still makes the resulting report surface disagree with the effective CLI model.
- Unsupported-flag regression: contained for the retired `--config`/`--cd` defect. Installed help and negative controls agree, and the hermetic reinjection flips three tests with AGY absent.
- Probe masking and liveness: partially contained. `DEVNULL`, captured pipes, a new session, and the 120-second timeout bound the intended listing, but failed-listing diagnostics discard the real cause and the live-test gate skips every listing failure without classification.
- Dry-run process effects: contained for chdir/exec; the hermetic tests passed. The separately intended `agy models` subprocess still runs and fails closed.
- Documentation: not contained because the docs claim every model is checked and `AGY_MODEL` is the exact effective model, which F1 disproves.

Cursor at send: 0
