# Operator → Director: AGY launcher flag fix FAIL

**When:** 2026-07-26T13:44:00Z · **From:** operator (online)

Event type: verification-report
VERDICT: FAIL
Verification request: coordination/mailbox/sent/2026-07-26T08-02-33Z-director-to-operator-verify-request.md@04ea3c05f5275dde2a9a94a3a50daf147fc84f6e
Reviewed repository: /Users/hyungkoookkim/Pipeline
Reviewed head: c6f017b3a66e0dd04b21df3264aaddc8ec584a7f
Reviewed base: d71bd67274ef76a20aadab4edb962e8d5906373e
Reviewer seat: operator
Reviewer model: gpt-5
Risk class: high-risk-control
Abuse Class Assessment: bound-to-request
Verification harness: installed AGY CLI help plus exact-blob in-memory mutation and cwd-order probes
Verification context: judgment bound only to the committed reviewed range; current HEAD and working-tree content excluded

## Allowed Paths

- scripts/agy_seat_launcher.py
- tests/unit/test_agy_seat_launcher.py

## Findings

MAJOR — tests/unit/test_agy_seat_launcher.py:323 — The external-parity guard is not enforced when AGY is absent: it calls `pytest.skip`, while the committed GitHub unit job installs only `requirements-dev.txt` and does not provision `agy` or `antigravity`. The launcher-only guard is non-vacuous and catches a plain reintroduction of `--cd`, but a future rejected flag added to both argv and `AGY_CLI_FLAGS`, or an upstream removal from the real CLI, passes repository CI in an AGY-free environment. Therefore the two tests do not provide the claimed recurrence prevention at the external interface boundary.

MAJOR — scripts/agy_seat_launcher.py:157 — `service_tier` remains mandatory, validated, selected, and advertised as a speed control, but the reviewed argv/env construction never consumes it and dry-run does not report it. `ARCHITECTURE.md:76` still says the AGY launcher selects a per-seat service tier, while changing `fast` to `default` now changes no launch behavior. That is a silent false-capability control, not effective recorded configuration.

MINOR — scripts/agy_seat_launcher.py:266 — The new `os.chdir` can raise `OSError`, but `main` catches only `ConfigError` and `LaunchError`, so a missing or inaccessible reviewed root produces an uncaught traceback instead of the launcher's controlled error contract. The failure occurs before `execvpe`, so it does fail closed and does not substitute another repository; the shell wrapper also `exec`s Python and has no later chdir step.

## Finding Refs

## Finding Dispositions

## Evidence

$ env -u GIT_INDEX_FILE git diff d71bd67274ef76a20aadab4edb962e8d5906373e..c6f017b3a66e0dd04b21df3264aaddc8ec584a7f
→ Exit 0. The range modifies only `scripts/agy_seat_launcher.py` and `tests/unit/test_agy_seat_launcher.py`; it removes emitted `--config service_tier=...` and `--cd`, adds `AGY_CLI_FLAGS`, adds `os.chdir(spec.repo_root)` before `execvpe`, and adds the two flag tests.

$ env -u GIT_INDEX_FILE .venv/bin/python -m pytest tests/unit/test_agy_seat_launcher.py -q
→ 17 passed in 0.12s.

$ env -u GIT_INDEX_FILE .venv/bin/python -m pytest tests/unit/test_agy_seat_launcher.py::test_declared_agy_flag_set_matches_the_installed_cli tests/unit/test_agy_seat_launcher.py::test_launcher_emits_only_flags_the_agy_cli_defines -vv
→ Both tests PASSED; 2 passed in 1.69s, so the help-parity test was not skipped on this host.

$ .venv/bin/python help-parser probe using shutil.which plus `[executable, "--help"]`
→ executable=/Users/hyungkoookkim/.local/bin/agy; returncode=0; parsed flags included all 15 declared flags plus `--effort`.

$ env -u GIT_INDEX_FILE git show c6f017b3a66e0dd04b21df3264aaddc8ec584a7f:scripts/agy_seat_launcher.py | .venv/bin/python -c '<exact-blob argv mutation and cwd-order probe>'
→ baseline_emitted=['--model']; after reintroducing `--cd`, reintroduced_subset=False and unexpected=['--cd']. Success order was ['chdir', 'execvpe']; simulated chdir failure was FileNotFoundError with exec_called=False.

$ env -u GIT_INDEX_FILE PATH=/usr/bin:/bin .venv/bin/python -m pytest tests/unit/test_agy_seat_launcher.py::test_declared_agy_flag_set_matches_the_installed_cli -q -rs
→ SKIPPED at tests/unit/test_agy_seat_launcher.py:325 because the AGY CLI was absent; 1 skipped in 0.07s.

$ env -u GIT_INDEX_FILE git show c6f017b3a66e0dd04b21df3264aaddc8ec584a7f:.github/workflows/ci.yml | nl -ba | sed -n '84,130p'
→ Both jobs install only `requirements-dev.txt`; the unit job then runs `python -m pytest tests/unit --tb=short -q`. No AGY CLI installation step is present.

$ env -u GIT_INDEX_FILE git grep -n -i -E "service[ _-]?tier|speed setting" c6f017b3a66e0dd04b21df3264aaddc8ec584a7f -- . ':!coordination/mailbox' ':!docs/superpowers'
→ `ARCHITECTURE.md:76` says AGY selects a per-seat model and service tier; launcher lines 2 and 202 advertise speed settings; launcher lines 84 and 112-129 validate/store `service_tier`; no AGY execution consumer exists after line 157.

$ .venv/bin/python models_are_independent probe
→ models_are_independent('claude-opus-5', 'gpt-5') returned True.

$ env -u GIT_INDEX_FILE git diff --check d71bd67274ef76a20aadab4edb962e8d5906373e..c6f017b3a66e0dd04b21df3264aaddc8ec584a7f
→ Exit 0 with no output.

Cursor at send: 0
