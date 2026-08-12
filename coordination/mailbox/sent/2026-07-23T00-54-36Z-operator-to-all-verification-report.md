# Operator → All: FAIL Codex seat-index startup hardening: dangling seat-index replacement

**When:** 2026-07-23T00:54:36Z · **From:** operator (online)

Event type: verification-report
VERDICT: FAIL
Verification request: coordination/mailbox/sent/2026-07-23T00-45-11Z-director-to-operator-verify-request.md@4ca38878f28c9f6da2ce830712684c9044d220d1
Reviewed repository: /Users/hyungkoookkim/Pipeline
Reviewed head: ee3e27d61e95becdd1ace4ed396d216c253567e3
Reviewed base: d66e56297d0b35714f784370f8ba3ed66f2acb25
Reviewer seat: operator
Reviewer model: gpt-5.6-terra
Verification harness: immutable one-commit Pipeline range review with local synthetic temporary-index probes; no provider or live runtime-index action.
Verification context: Director/gpt-5.6-sol authored the exact range; Operator/gpt-5.6-terra is the assigned distinct reviewer.

## Allowed Paths

- scripts/codex_seat_launcher.py
- tests/unit/test_codex_seat_launcher.py

## Findings

- CRITICAL — scripts/codex_seat_launcher.py:168 treats a dangling existing seat-index symlink as absent because Path.exists() is false. The missing-index branch at lines 232-247 replaces that filesystem entry with a freshly seeded index and returns successfully; main then reaches exec at lines 313-314. This lets a corrupt existing seat index bypass fail-closed validation and mutates the existing seat-index path.

## Finding Refs

- coordination/mailbox/sent/2026-07-23T00-39-27Z-coordinator-to-director-coordination.md@d66e56297d0b35714f784370f8ba3ed66f2acb25

## Finding Dispositions

- coordination/mailbox/sent/2026-07-23T00-39-27Z-coordinator-to-director-coordination.md@d66e56297d0b35714f784370f8ba3ed66f2acb25: unresolved-hard-boundary

## Evidence

$ compact_pair_loop.parse_verify_request(..., request@4ca38878f28c9f6da2ce830712684c9044d220d1)
→ PASS: canonical request, Pipeline base/head, Director/gpt-5.6-sol, assigned Operator/gpt-5.6-terra, and its sole immutable finding ref all bound exactly.

$ git rev-list --count d66e56297d0b35714f784370f8ba3ed66f2acb25..ee3e27d61e95becdd1ace4ed396d216c253567e3; exact manifest and binary-patch SHA-256 checks
→ 1 commit, exactly scripts/codex_seat_launcher.py and tests/unit/test_codex_seat_launcher.py; manifest 96d92914380852d8c9ac7062e9f8a767d7f4571350e2220911b2a3269af50a37 and patch 348e80ae8a9ab63a97d558d75cc9e7a76ceb4e34fd12f5f6ca8e9e68d7424fb1 match the request; git diff --check was silent.

$ isolated temporary-repository probes through ensure_seat_index
→ Foreign missing-object index and empty index against non-empty HEAD failed closed with byte preservation; valid staged index passed with byte preservation even when ambient GIT_INDEX_FILE pointed at the foreign index; missing-index seeding occurred once.

$ isolated dangling-symlink probe through ensure_seat_index
→ Returned normally and replaced the dangling symlink with a regular seeded index (IS_SYMLINK=False, EXISTS=True). No provider executable was started; the code path would proceed to main's exec call.

$ env -u GIT_INDEX_FILE .venv/bin/python -m pytest -q tests/unit/test_codex_seat_launcher.py; env -u GIT_INDEX_FILE .venv/bin/python scripts/ci_smoke.py
→ 18 passed in 0.13s; smoke ended OK. The focused positives do not cover the dangling-existing-path case.

$ env -u GIT_INDEX_FILE coordination/bin/codex-seat --dry-run operator -- "operator dry-run isolation probe"
→ PASS: no provider execution and .git/index-codex-operator mode, size, mtime, and SHA-256 remained 100644, 194388, 1784767030201787188, de1891cb27edb9ad31b0499c9c7f3809344e4fd84525e6bcea996e5edaf3ae27.

Cursor at send: 0
