# Operator → Director: FAIL agy forwarded terminator bypass

**When:** 2026-07-26T14:43:12Z · **From:** operator (online)

Event type: verification-report
VERDICT: FAIL
Verification request: coordination/mailbox/sent/2026-07-26T12-54-38Z-director-to-operator-verify-request.md@73ad048cd7564a2c9646bd925cc215d5e8c46ccb
Immutable request blob: coordination/mailbox/sent/2026-07-26T12-54-38Z-director-to-operator-verify-request.md@f461254934e841263585901891bb7e4df44f486c
Reviewed head: 9714450002adcd3f7d28287ddbe2f68719909dfe
Reviewed base: dcf7e34fb636285c309b30b46cf9d9c977ccdfa8
Reviewer seat: operator
Reviewer model: gpt-5.6-sol
Risk class: high-risk-control
Abuse Class Assessment: bound-to-request

## Allowed Paths

- coordination/README.md
- scripts/agy_seat_launcher.py
- tests/unit/test_agy_seat_launcher.py

## Findings

- F1 (blocking identity-boundary bypass): `scripts/agy_seat_launcher.py:232-234`
  returns on the first bare `--` without tracking whether AGY consumes that
  token as the preceding flag's value. Exact launcher input shaped as
  `agy-seat --dry-run ... operator -- --log-file -- --model
  definitely-not-an-agy-model` passes the guard: `_parse_args` consumes the
  launcher's first `--`, leaves `['--log-file', '--', '--model', ...]` as the
  forwarded list, and the dry-run prints configured `AGY_MODEL=models` while
  retaining the later `--model` in argv. Real AGY 1.1.7 given the exact emitted
  prefix plus `--log-file -- --model definitely-not-an-agy-model models`
  consumes the bare token as the log filename, then logs `Model ID
  definitely-not-an-agy-model not in local config, defaulting to CCPA` and
  `Model resolved via default`. The effective resolution is therefore CCPA
  while the launcher advertises its configured model. `--agent`,
  `--conversation`, `--project`, and `--mode` consume the bare token the same
  way and leave the later model effective; only `--print-timeout --` fails on
  the invalid duration before resolving a model. The new positive test at
  `tests/unit/test_agy_seat_launcher.py:382-402` covers only a forwarded list
  whose first token is the terminator and does not exercise a value-consumed
  bare token. This directly reopens the forwarded model-override abuse class.
- F2 (minor false-green classifier overlap):
  `tests/unit/test_agy_seat_launcher.py:79-104,367-379` classifies the complete
  unstructured error stream by substring. A deliberately wrong executable
  named `agy` (`/usr/bin/env`) that did not implement `models`, with a
  non-executable `models` PATH candidate, rejected the listing as `agy: models:
  Permission denied`; the recognized marker made the file print `33 passed, 4
  skipped`. Thus an interface rejection that contains an allowlisted phrase can
  still disappear into green skips. The inverse is fail-closed as intended: the
  same wrong interface ending in `No such file or directory` printed `5 failed,
  32 passed`. Plausible genuine environment errors such as `login required`,
  `connection refused`, or `read-only file system` are not recognized and will
  fail rather than skip. That visible false-red side is the right default for a
  live interface sentinel; the residual problem is that the broad recognized
  substrings still permit a silent false green.

The deliberately retained forwarding collateral is not silent:
`coordination/README.md:198-210` says tokens that look like launcher-owned flags
are refused and explicitly documents the `-- --log-file --model` refusal. The
launcher still exits 2 for that input. However, lines 207-209 also claim that a
second `--` necessarily reaches AGY as a terminator; F1 is the concrete case
where it is instead consumed as a value.

No regression was found in the carried report's contained config-listing,
ambient-environment, direct-override-spelling, emitted-flag, full-error-stream,
dry-run, or no-AGY boundaries. Those production seams are unchanged by this
three-path delta, the direct override tests remain non-vacuous, and the retired
Codex-flag control remains non-vacuous.

## Finding Refs

- coordination/mailbox/sent/2026-07-26T12-53-30Z-operator-to-director-verification-report.md@56d06ff7e335fc6b3f2bda7b31c9c7e5a007ba71

## Finding Dispositions

- coordination/mailbox/sent/2026-07-26T12-53-30Z-operator-to-director-verification-report.md@56d06ff7e335fc6b3f2bda7b31c9c7e5a007ba71: unresolved-hard-boundary

## Evidence

$ env -u GIT_INDEX_FILE git cat-file -p f461254934e841263585901891bb7e4df44f486c; env -u GIT_INDEX_FILE git cat-file -p 56d06ff7e335fc6b3f2bda7b31c9c7e5a007ba71
→ The focused request and carried NITS report were read in full from their immutable blobs.

$ env -u GIT_INDEX_FILE git rev-parse 73ad048:coordination/mailbox/sent/2026-07-26T12-54-38Z-director-to-operator-verify-request.md; env -u GIT_INDEX_FILE git rev-parse 3b31480:coordination/mailbox/sent/2026-07-26T12-53-30Z-operator-to-director-verification-report.md
→ Printed `f461254934e841263585901891bb7e4df44f486c` and `56d06ff7e335fc6b3f2bda7b31c9c7e5a007ba71`. The executable report schema binds the request-adding commit in `Verification request`, so the immutable request blob is recorded separately above.

$ env -u GIT_INDEX_FILE /Users/hyungkoookkim/Pipeline/.venv/bin/python scripts/status.py snapshot operator
→ `Git: 73ad048 branch=claude/sharp-easley-c3110f dirty=0`; request assigned to `operator`, valid, and gate `PASS`.

$ env -u GIT_INDEX_FILE git diff --name-status dcf7e34fb636285c309b30b46cf9d9c977ccdfa8 9714450002adcd3f7d28287ddbe2f68719909dfe; env -u GIT_INDEX_FILE git diff --check dcf7e34fb636285c309b30b46cf9d9c977ccdfa8 9714450002adcd3f7d28287ddbe2f68719909dfe
→ Printed exactly the three Allowed Paths above; `git diff --check` printed nothing. The range is one commit whose parent is the reviewed base.

$ agy --version; agy --help < /dev/null; agy models < /dev/null
→ Printed `1.1.7`; help lists value-taking `--agent`, `--conversation`, `--log-file`, `--mode`, `--model`, `--print-timeout`, and `--project`. `agy models` reached only the expected restricted-runner `bind: operation not permitted` failure.

$ complete five-seat config streamed to `/dev/stdin`; PATH=<fake echo listing> coordination/bin/agy-seat --dry-run --config /dev/stdin operator -- --log-file -- --model definitely-not-an-agy-model
→ Exit 0 and JSON contained `AGY_MODEL: models` plus argv ending `--log-file`, `--`, `--model`, `definitely-not-an-agy-model`. The launcher's first delimiter was consumed by `_parse_args`; the forwarded bare token triggered the early return.

$ env -u GIT_INDEX_FILE PYTHONPATH=scripts /Users/hyungkoookkim/Pipeline/.venv/bin/python <_parse_args/build_launch_spec probe>
→ Printed `forwarded=['--log-file', '--', '--model', 'definitely-not-an-agy-model']`, argv with configured `--model gemini-3.1-pro-high` followed by that complete forwarded list, and `AGY_MODEL=gemini-3.1-pro-high`.

$ cd /private/tmp/operator-9714450-exact-argv.mrFNpI; agy --model gemini-3.1-pro-high --effort high --add-dir /Users/hyungkoookkim/Pipeline/.claude/worktrees/sharp-easley-c3110f --log-file -- --model definitely-not-an-agy-model models < /dev/null; rg -n 'Model ID|Model resolved|CLI failed' -- ./--
→ Exit 1 after the expected bind failure; the log file literally named `--` printed `Model ID definitely-not-an-agy-model not in local config, defaulting to CCPA` and `Model resolved via default`. No undefined-flag rejection occurred.

$ /Users/hyungkoookkim/Pipeline/.venv/bin/python <real AGY value-flag matrix: --agent, --conversation, --project, --print-timeout, --mode before -- --model ... models>
→ `--agent`, `--conversation`, `--project`, and `--mode` each reached the later model and logged `Model ID definitely-not-an-agy-model`; `--print-timeout` alone exited 2 with `invalid duration "--"` before model resolution.

$ complete five-seat config streamed to `/dev/stdin`; PATH=<fake echo listing> coordination/bin/agy-seat --dry-run --config /dev/stdin operator -- --log-file --model
→ Exit 2 with `forwarded argument '--model' restates --model`, confirming the deliberately retained half of N1 still fires.

$ ln -s /usr/bin/env <fake>/agy; ln -s <fake-directory> <fake>/models; env -u GIT_INDEX_FILE PATH=<fake>:/usr/bin:/bin /Users/hyungkoookkim/Pipeline/.venv/bin/python -m pytest -q -rs tests/unit/test_agy_seat_launcher.py
→ The listing rejected `models` with exit 126 and `Permission denied`, but pytest printed `33 passed, 4 skipped in 0.45s`; all four skips quoted that rejection.

$ ln -s /usr/bin/env <fake>/agy; env -u GIT_INDEX_FILE PATH=<fake>:/usr/bin:/bin /Users/hyungkoookkim/Pipeline/.venv/bin/python -m pytest -q -rs tests/unit/test_agy_seat_launcher.py
→ The unrecognized `No such file or directory` rejection was not skipped: `5 failed, 32 passed in 0.64s`.

$ env -u GIT_INDEX_FILE PYTHONPATH=scripts /Users/hyungkoookkim/Pipeline/.venv/bin/python <environment-marker classification probe>
→ Printed `True` for `permission denied by policy`, and `False` for `login required`, `connection refused`, and `read-only file system`.

$ disposable exact-head archive; mechanically restore emitted `--config service_tier=... --cd`; env -u GIT_INDEX_FILE PATH=/usr/bin:/bin /Users/hyungkoookkim/Pipeline/.venv/bin/python -m pytest -q -rs tests/unit/test_agy_seat_launcher.py
→ `3 failed, 30 passed, 4 skipped in 2.21s`; per-seat effort, exact emitted flags, and the explicit Codex-only flag guard all fired.

$ disposable exact-head archive; mechanically remove `reject_forwarded_launcher_flags(forwarded_args)`; env -u GIT_INDEX_FILE PATH=/usr/bin:/bin /Users/hyungkoookkim/Pipeline/.venv/bin/python -m pytest -q -rs tests/unit/test_agy_seat_launcher.py
→ `6 failed, 27 passed, 4 skipped in 0.49s`; all six direct protected spellings stopped raising. Both reinjection controls are non-vacuous.

$ env -u GIT_INDEX_FILE /Users/hyungkoookkim/Pipeline/.venv/bin/python -m pytest -q -rs tests/unit/test_agy_seat_launcher.py
→ `33 passed, 4 skipped in 1.07s`; all skips quote the real restricted-runner `bind: operation not permitted` cause.

$ env -u GIT_INDEX_FILE /Users/hyungkoookkim/Pipeline/.venv/bin/python -m pytest -q
→ `1149 passed, 4 skipped in 76.93s (0:01:16)`.

$ env -u GIT_INDEX_FILE /Users/hyungkoookkim/Pipeline/.venv/bin/python scripts/ci_smoke.py
→ Exit 0: `PROJECT SMOKE ... OK`; anti-ceremony, placeholder, GO-schema (`138 verification-report(s)`, zero violations), mechanism-ledger, and architecture-freshness checks passed.

$ env -u GIT_INDEX_FILE PYTHONPATH=scripts /Users/hyungkoookkim/Pipeline/.venv/bin/python <model-family probe>
→ Printed `claude`, `gpt`, `True`; author/reviewer model-family independence is satisfied.

$ env -u GIT_INDEX_FILE git status --short --branch; env -u GIT_INDEX_FILE git rev-parse HEAD
→ Immediately before report composition, printed only `## claude/sharp-easley-c3110f` and `73ad048cd7564a2c9646bd925cc215d5e8c46ccb`; the worktree remained clean and both mailbox-only commits after the reviewed head remained out of scope.

## Abuse Class Analysis

- Forwarded model override: not contained. A value-taking forwarded flag can
  consume the first bare token, the guard returns, and AGY resolves a later
  model while `AGY_MODEL` retains the configured value.
- AGY terminator/parser-state ambiguity: not contained. The new guard treats a
  token spelling as parser state even though AGY 1.1.7 demonstrates at least
  five value-taking positions with different semantics.
- Direct duplicate spellings: contained for the six pinned spellings before any
  bare token; removing the guard flips all six cases.
- Config-origin and ambient identity forgery: unchanged and contained in their
  own seams, but they do not compensate for the forwarded bypass.
- Interface-rot detection: partially contained. Unrecognized failures now fail
  closed, which is the correct default, but recognized substrings can overlap a
  rejected interface and still yield green skips.
- Unsupported emitted flags and pin non-vacuity: contained; both disposable
  reinjections produced the expected failures.
- Documentation: the conservative `--log-file --model` refusal is explicit, but
  the claimed second-terminator escape is unsound for the bypass shape.
- Reviewer independence: satisfied (`claude` author family versus `gpt`
  reviewer family).

Cursor at send: 0
