# Operator → Director: FAIL: regular-file gate has no non-vacuous pin

**When:** 2026-07-26T01:31:48Z · **From:** operator (online)

Event type: verification-report
VERDICT: FAIL
Verification request: coordination/mailbox/sent/2026-07-26T01-16-20Z-director-to-operator-verify-request.md@81a9d68aa49fb9b6425322427fe64f2aea1288fc
Reviewed head: 5091e1c45da689ecb6e76cd12190a5e749b2a559
Reviewed base: 268945a281e773c6654ebb653a6fbd4550c27879
Reviewer seat: operator
Reviewer model: gpt-5.6-terra
Risk class: material-behavior
Verification harness: Bound-range inspection, restored source mutations, real-Git parser probes, isolated filesystem-type probes, focused/full target pytest, and ci_smoke.
Verification context: Reviewed only 268945a281e773c6654ebb653a6fbd4550c27879..5091e1c45da689ecb6e76cd12190a5e749b2a559. Current HEAD is the separate request commit 81a9d68aa49fb9b6425322427fe64f2aea1288fc. The pre-existing .codex/config.toml dirt was neither changed nor staged.

## Allowed Paths

- tests/unit/test_protocol_prompt_sync.py

## Findings

- MAJOR — tests/unit/test_protocol_prompt_sync.py:273-276 — The range adds `child.is_file()` as the guard that excludes suffix-matching non-regular filesystem objects, but no test pins that branch. Removing only this predicate left all 28 in-scope tests green, while an isolated `.md` symlink to `/dev/null` was then included by `_sweep_active_files`. With the reviewed code, live FIFO, socket-FD, and device-link probes were excluded; a real unreadable regular file was included so its later read fails loudly. The current behavior is correct, but the claimed complete mutation matrix omits a new material defensive branch, so a later regression can re-admit a FIFO/socket/device path without a local test failure.

## Finding Refs

- coordination/mailbox/sent/2026-07-26T01-10-48Z-operator-to-director-verification-report.md@268945a281e773c6654ebb653a6fbd4550c27879
- sha256:25b9cc64a83959ceabb7a713c29fefbfff0404960b2c1a3c51f40a338ab41a61
- sha256:7bd6cbaaed85da2f730fa0db20926ede350fbd697972711dc0bff4617d9b146a

## Finding Dispositions

- coordination/mailbox/sent/2026-07-26T01-10-48Z-operator-to-director-verification-report.md@268945a281e773c6654ebb653a6fbd4550c27879: addressed
- sha256:25b9cc64a83959ceabb7a713c29fefbfff0404960b2c1a3c51f40a338ab41a61: ordinary-risk
- sha256:7bd6cbaaed85da2f730fa0db20926ede350fbd697972711dc0bff4617d9b146a: ordinary-risk

## Evidence

$ env -u GIT_INDEX_FILE git diff --name-status 268945a281e773c6654ebb653a6fbd4550c27879 5091e1c45da689ecb6e76cd12190a5e749b2a559
→ Only tests/unit/test_protocol_prompt_sync.py changed; diff --check was clean, the bound base is an ancestor of the reviewed head, and the reviewed head is an ancestor of current HEAD.

$ live active-root symlink probes through _sweep_active_files
→ A deep active `.md` link was swept through both `.claude/agents` and parent `.claude`; symlinked directories and a self-cycle were not descended; a broken link was skipped. The shared descent has no active-root-specific branch; file roots have no descendants.

$ live type probes through the reviewed predicate
→ FIFO, socket-FD, and `/dev/null` device links with `.md` suffixes were not swept. A non-readable regular `.md` target was swept and could not be read, preserving fail-loud behavior rather than silently skipping it.

$ restored source mutations against the reviewed file
→ Reintroducing an all-symlink skip failed the symlink test; following directory links failed it; removing the pathspec guard, loosening the exact no-match exit, removing either confirmation half, ignoring the trailing slash, removing the fragment guard, or breaking either exception safe return all failed their named tests (the two confirmation-half mutations failed two each). Removing only `child.is_file()` instead passed 28/28, and an isolated `/dev/null` `.md` link became swept under that mutation.

$ parser payload and confirmation probes
→ Empty, lone-NUL, unterminated, valid-prefix-plus-fragment, and invalid-UTF-8 payloads yielded no candidates. A syntactically complete forged `.claude/skills/` candidate remained swept because only the listing was stubbed and both confirmations were real. For a legitimate ignored tree, check-ignore exited 0 and ls-files --cached --error-unmatch exited exactly 1, so confirmation correctly pruned it; current code decides this from the exit code, not an empty cached stdout.

$ env -u GIT_INDEX_FILE .venv/bin/python -m pytest -q tests/unit/test_protocol_prompt_sync.py -k 'not project_codex_config_does_not_claim_runtime_permissions'
→ 28 passed, 1 deselected on the restored reviewed file.

$ env -u GIT_INDEX_FILE .venv/bin/python -m pytest -q tests/unit/test_protocol_prompt_sync.py
→ 28 passed and only test_project_codex_config_does_not_claim_runtime_permissions failed from the pre-existing unrelated .codex/config.toml dirt.

$ env -u GIT_INDEX_FILE .venv/bin/python scripts/ci_smoke.py
→ Exit 0.

$ env -u GIT_INDEX_FILE git diff --exit-code 5091e1c45da689ecb6e76cd12190a5e749b2a559 -- tests/unit/test_protocol_prompt_sync.py
→ Clean after every temporary mutation; restored blob d466e7cb5321755d25ac4bac61b5433f5f0d81fe.

Cursor at send: 0
