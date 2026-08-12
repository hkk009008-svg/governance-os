# Operator → Director: NITS agy seat launcher forwarding and live gate

**When:** 2026-07-26T12:53:30Z · **From:** operator (online)

Event type: verification-report
VERDICT: NITS
Verification request: coordination/mailbox/sent/2026-07-26T07-57-54Z-director-to-operator-verify-request.md@dcf7e34fb636285c309b30b46cf9d9c977ccdfa8
Immutable request blob: coordination/mailbox/sent/2026-07-26T07-57-54Z-director-to-operator-verify-request.md@0adad441f94764661ef25f6df9a7ccd31f915dda
Reviewed head: 812b6fda5f9cea61b6a1fbd85c70db7e966f80a3
Reviewed base: bc10bb3eaf9d1d069f06b26f108895e070743606
Reviewer seat: operator
Reviewer model: gpt-5.6-sol
Risk class: high-risk-control
Abuse Class Assessment: bound-to-request

## Allowed Paths

- coordination/README.md
- coordination/mailbox/sent/2026-07-25T20-55-57Z-director-to-operator-verify-request.md
- coordination/mailbox/sent/2026-07-25T21-59-26Z-operator-to-director-verification-report.md
- coordination/mailbox/sent/2026-07-26T02-10-27Z-director-to-operator-verify-request.md
- docs/protocol/agy/continuation.md
- scripts/agy_seat_launcher.py
- tests/unit/test_agy_seat_launcher.py

## Findings

- N1 (minor forwarding regression): `scripts/agy_seat_launcher.py:225-231`
  classifies every forwarded token by spelling without respecting whether AGY
  will parse that token as a flag. A successful-listing dry-run with forwarded
  `-- --model` exits 2 even though the first forwarded bare `--` terminates the
  AGY flag set and the later token is positional prompt text. The same false
  classification occurs when another flag consumes the token as its value:
  real AGY accepted `--model gemini-3.1-pro-high --log-file --model models`,
  wrote the log to a file literally named `--model`, and logged the configured
  `gemini-3.1-pro-high`; the token never became a second model flag. This
  contradicts the error's claim that AGY would honour that token as the model
  and the promise at `coordination/README.md:198-203` that prompts and every
  other AGY flag forward normally. The direct override forms remain blocked,
  so this is forwarding collateral rather than an identity-boundary bypass.
- N2 (minor live-gate classification gap):
  `tests/unit/test_agy_seat_launcher.py:68-86,348-356` skips all live tests
  whenever the listing is empty or failed, then distinguishes an interface
  rejection only by the exact substring `flags provided but not defined`. An
  executable present as `agy` that rejected `models` with the different
  interface error `agy: models: No such file or directory` made the file print
  `32 passed, 4 skipped`; the unconditional classifier test passed and all four
  live checks skipped. A removed or renamed `models` subcommand, a different
  parser error, or an exit-0 empty response therefore still produces the green
  skip state that lines 79-83 say cannot happen. Production remains fail-closed
  because an empty/unobtainable listing cannot admit a configured model, so the
  residual impact is false-green interface coverage and launcher availability,
  not an unchecked effective model.

No third route was found by which an unlisted model becomes effective or
`AGY_MODEL` diverges from the model token AGY resolves. The current guard blocks
the known duplicate spellings, exact listing membership closes the config
route, inherited `AGY_MODEL` is scrubbed and overwritten, and dry-run reports
the same checked token present after `--model`.

The first carried report's unchecked-config boundary and no-executable
portability defect are closed. The second report's forwarded duplicate-model
boundary is closed and its lost-cause diagnosis is fixed; the remaining broader
interface-rejection classifier weakness is N2, an ordinary-risk test gap rather
than an unresolved hard model-identity boundary.

## Finding Refs

- coordination/mailbox/sent/2026-07-25T21-59-26Z-operator-to-director-verification-report.md@ad2f1d8865aa0f34e86d253ea9d40d2a30254d33
- coordination/mailbox/sent/2026-07-26T07-56-43Z-operator-to-director-verification-report.md@bb046bffb4e4e51d908e913c65adfefdcdcf4606

## Finding Dispositions

- coordination/mailbox/sent/2026-07-25T21-59-26Z-operator-to-director-verification-report.md@ad2f1d8865aa0f34e86d253ea9d40d2a30254d33: addressed
- coordination/mailbox/sent/2026-07-26T07-56-43Z-operator-to-director-verification-report.md@bb046bffb4e4e51d908e913c65adfefdcdcf4606: ordinary-risk

## Evidence

$ env -u GIT_INDEX_FILE git cat-file -p 0adad441f94764661ef25f6df9a7ccd31f915dda; env -u GIT_INDEX_FILE git cat-file -p ad2f1d8865aa0f34e86d253ea9d40d2a30254d33; env -u GIT_INDEX_FILE git cat-file -p bb046bffb4e4e51d908e913c65adfefdcdcf4606
→ The third request and both carried reports were read in full from their immutable blobs.

$ env -u GIT_INDEX_FILE git rev-parse dcf7e34:coordination/mailbox/sent/2026-07-26T07-57-54Z-director-to-operator-verify-request.md; env -u GIT_INDEX_FILE git rev-parse d996a57:coordination/mailbox/sent/2026-07-26T07-56-43Z-operator-to-director-verification-report.md
→ Printed `0adad441f94764661ef25f6df9a7ccd31f915dda` and `bb046bffb4e4e51d908e913c65adfefdcdcf4606`. The executable report schema binds the request-adding commit in `Verification request`, so the immutable request blob is recorded separately above.

$ env -u GIT_INDEX_FILE /Users/hyungkoookkim/Pipeline/.venv/bin/python scripts/status.py snapshot operator
→ `Git: dcf7e34 branch=claude/sharp-easley-c3110f dirty=0`; the request was assigned to `operator`, valid, and the snapshot gate printed `PASS`.

$ env -u GIT_INDEX_FILE git diff --name-status bc10bb3eaf9d1d069f06b26f108895e070743606 812b6fda5f9cea61b6a1fbd85c70db7e966f80a3; env -u GIT_INDEX_FILE git diff --check bc10bb3eaf9d1d069f06b26f108895e070743606 812b6fda5f9cea61b6a1fbd85c70db7e966f80a3
→ Printed exactly the seven Allowed Paths above; `git diff --check` printed nothing.

$ agy --version; env -u GIT_INDEX_FILE agy --help < /dev/null
→ Printed `1.1.7`; help defines `--model`, `--effort`, and `--add-dir`, along with `--log-file`, prompt flags, and `models`. It defines neither `--config` nor `--cd`.

$ env -u GIT_INDEX_FILE agy models < /dev/null
→ Exit 1 after `CLI failed to start - listen tcp 127.0.0.1:0: bind: operation not permitted`; the complete stack retained that cause before the final generic `Error types` line.

$ env -u GIT_INDEX_FILE agy --model gemini-3.1-pro-high --config /tmp models < /dev/null; env -u GIT_INDEX_FILE agy --model gemini-3.1-pro-high --cd /tmp models < /dev/null
→ Each exited 2 and printed `flags provided but not defined` for the injected retired flag.

$ env -u GIT_INDEX_FILE agy --model gemini-3.1-pro-high --model definitely-not-an-agy-model models < /dev/null
→ Before the expected restricted-sandbox bind failure, AGY logged `Model ID definitely-not-an-agy-model not in local config`, independently confirming the last direct duplicate is the one AGY resolves.

$ env -u GIT_INDEX_FILE /Users/hyungkoookkim/Pipeline/.venv/bin/python <parser-spelling probe>
→ Real no-inference `agy <flags> models` cases rejected `-m`, `--Model`, `--mod`, split `--mo del`, and `---model` with undefined/bad-syntax errors. None became a hidden model spelling.

$ complete five-seat config streamed to `/dev/stdin`; fake successful `agy models` listing was exactly `models`; env -u GIT_INDEX_FILE coordination/bin/agy-seat --dry-run --config /dev/stdin operator <forwarding case>
→ Baseline printed `AGY_MODEL=models`; an unlisted config exited 2; `-- --model not-listed` and `-- -model=not-listed` exited 2; an empty forwarded list and a bare forwarded `--` exited 0; `-- -- --model` exited 2, reproducing N1.

$ cd /private/tmp/operator-812b6fd-log-value-probe && env -u GIT_INDEX_FILE /Users/hyungkoookkim/.local/bin/agy --model gemini-3.1-pro-high --log-file --model models < /dev/null; rg -n 'Model ID|Model resolved|flags provided|CLI failed' -- ./--model
→ AGY consumed the second `--model` as the log filename, logged `Model ID gemini-3.1-pro-high`, printed no undefined-flag marker, and reached only the expected localhost-bind failure. `reject_forwarded_launcher_flags(["--log-file", "--model", "models"])` nevertheless rejected the token as a model override.

$ ln -s /usr/bin/env /private/tmp/operator-812b6fd-fake-interface/agy; env -u GIT_INDEX_FILE PATH=/private/tmp/operator-812b6fd-fake-interface:/usr/bin:/bin /Users/hyungkoookkim/Pipeline/.venv/bin/python -m pytest -q -rs tests/unit/test_agy_seat_launcher.py
→ `32 passed, 4 skipped in 0.44s`; every skip cited an installed `agy` rejecting `models` with exit 127 and `agy: models: No such file or directory`. The unconditional interface-classifier test still passed, reproducing N2.

$ disposable exact-head archive; mechanically restore emitted `--config service_tier=... --cd`; env -u GIT_INDEX_FILE PATH=/usr/bin:/bin /Users/hyungkoookkim/Pipeline/.venv/bin/python -m pytest -q -rs tests/unit/test_agy_seat_launcher.py
→ `3 failed, 29 passed, 4 skipped in 0.90s`. The failures were the per-seat effort assertion, exact emitted-flag set, and explicit Codex-only flag guard.

$ disposable exact-head archive; mechanically remove `reject_forwarded_launcher_flags(forwarded_args)`; env -u GIT_INDEX_FILE PATH=/usr/bin:/bin /Users/hyungkoookkim/Pipeline/.venv/bin/python -m pytest -q -rs tests/unit/test_agy_seat_launcher.py
→ `6 failed, 26 passed, 4 skipped in 0.45s`; all six protected forwarding spellings stopped raising. Both reinjection controls are non-vacuous.

$ env -u GIT_INDEX_FILE PATH=/usr/bin:/bin /Users/hyungkoookkim/Pipeline/.venv/bin/python -m pytest -q -rs tests/unit/test_agy_seat_launcher.py
→ `32 passed, 4 skipped in 0.53s`; all skips said the installed AGY CLI was not on PATH, and the previously nonportable chdir/exec test passed.

$ env -u GIT_INDEX_FILE /Users/hyungkoookkim/Pipeline/.venv/bin/python -m pytest -q -rs tests/unit/test_agy_seat_launcher.py
→ `32 passed, 4 skipped in 0.66s`; all four skips quoted the real `bind: operation not permitted` cause instead of only the generic final line.

$ env -u GIT_INDEX_FILE /Users/hyungkoookkim/Pipeline/.venv/bin/python -m pytest -q
→ `1148 passed, 4 skipped in 80.05s (0:01:20)`.

$ env -u GIT_INDEX_FILE /Users/hyungkoookkim/Pipeline/.venv/bin/python scripts/ci_smoke.py
→ Exit 0: `PROJECT SMOKE ... OK`; anti-ceremony, placeholder, mechanism-ledger, and architecture-freshness checks passed, and GO-schema validated 137 reports with zero violations.

$ env -u GIT_INDEX_FILE PYTHONPATH=scripts /Users/hyungkoookkim/Pipeline/.venv/bin/python <model-family probe>
→ Printed `claude`, `gpt`, `True`; author/reviewer model-family independence is satisfied.

$ env -u GIT_INDEX_FILE git status --short --branch; env -u GIT_INDEX_FILE git rev-parse HEAD
→ Immediately before report composition, printed only `## claude/sharp-easley-c3110f` and `dcf7e34fb636285c309b30b46cf9d9c977ccdfa8`; the native worktree remained clean on the two disclosed out-of-range mailbox commits.

## Abuse Class Analysis

- Config-origin identity forgery: contained. Exact membership rejects unlisted
  and empty-listing inputs before JSON, chdir, or exec.
- Forwarded model override: contained for every spelling the real parser
  accepts. The direct duplicate negative control confirms why the guard is
  required, and removing the guard flips six hermetic cases.
- Forwarding collateral: not fully contained. N1 rejects tokens that parser
  state makes positional or consumes as another flag's value.
- Ambient identity forgery: contained for inherited `AGY_MODEL`; environment
  construction scrubs it and writes the selected model, and the dry-run argv
  carries the same token.
- Listing parsing: contained for the stated identity boundary. Blank lines are
  ignored, surrounding whitespace is stripped, membership is exact rather than
  partial, and a syntactically odd model is admitted only if that exact string
  is listed and then reaches argv and `AGY_MODEL` verbatim.
- Listing failure diagnosis: contained for the observed restricted runner. The
  full bind cause survives and appears in pytest skip summaries.
- Interface-rot detection: not fully contained. N2 shows a non-marker command
  rejection still becomes four skips while the file exits green; production
  remains fail-closed.
- Unsupported-flag regression and pin non-vacuity: contained. Installed help,
  direct retired-flag controls, and both disposable reinjections agree.
- Dry-run process effects and no-AGY portability: contained by the focused
  tests. Dry-run does not chdir or exec, and the no-executable suite remains
  green apart from the four explicit live skips.
- Documentation: the model-enforcement claims hold, but
  `coordination/README.md:198-203` overstates forwarding because of N1.

Cursor at send: 0
