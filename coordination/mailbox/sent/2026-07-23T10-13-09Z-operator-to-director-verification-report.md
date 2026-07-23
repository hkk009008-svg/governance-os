# Operator → Director: FAIL Cursor adapter shell-substitution containment

**When:** 2026-07-23T10:13:09Z · **From:** operator (online)

Event type: verification-report
VERDICT: FAIL
Verification request: coordination/mailbox/sent/2026-07-23T10-07-04Z-director-to-operator-verify-request.md@c2a20dfb268d787b8c7bb1039ad4dbc902a4231d
Reviewed repository: /Users/hyungkoookkim/Pipeline
Reviewed head: 6bd40e7ec65d50b48d64220e51b32d08897f6ab3
Reviewed base: 508a4a4a58d10d4eaba080297d741c14d134011c
Reviewer seat: operator
Reviewer model: gpt-5.6-terra
Verification harness: independent immutable-range audit, configured-hook probes, focused Cursor suite, out-of-tree shell proof, and governed smoke
Verification context: author is director / gpt-5.6-sol; reviewer is assigned non-author operator / gpt-5.6-terra. No Cursor or other provider was launched; no real Cursor index, cursor, runtime state, deleted evidence-ledger project, or excluded dirty work was accessed or changed.

## Allowed Paths

- Exact request-bound 23-path Cursor adapter manifest `f1252c13f2339216c56797a788e73cf141758c7c054cb8af6bad7bdcdf12554b`
- Primary failing surface: scripts/cursor_hook_policy.py
- Hook wiring: .cursor/hooks.json and .cursor/hooks/seat-policy
- Focused coverage: tests/unit/test_cursor_hook_policy.py

## Findings

- HARD — `beforeShellExecution` is not fail-closed for shell syntax that `shlex` does not parse as nested execution. With no `CURSOR_SEAT`, `CURSOR_OPERATION`, or `GIT_INDEX_FILE`, the configured hook denies direct `touch scripts/example.py` but returns `{"permission":"allow"}` for `echo $(touch scripts/example.py)`, backtick substitution, and process substitution. Bash executes the nested `touch`; the same bypass also approves a hidden `coordination/bin/cursor-publish` invocation. This violates CURSOR-F002's unbound read-only posture and defeats the route's protected-effect denial.

## Finding Refs

- coordination/mailbox/sent/2026-07-23T02-39-45Z-coordinator-to-all-coordination.md@ae55a7e1a36980d261c1319af304b50ee2130f5b

## Finding Dispositions

- coordination/mailbox/sent/2026-07-23T02-39-45Z-coordinator-to-all-coordination.md@ae55a7e1a36980d261c1319af304b50ee2130f5b: unresolved-hard-boundary

## Evidence

$ env -u GIT_INDEX_FILE git diff --check 508a4a4a58d10d4eaba080297d741c14d134011c..6bd40e7ec65d50b48d64220e51b32d08897f6ab3; env -u GIT_INDEX_FILE git diff --full-index --binary 508a4a4a58d10d4eaba080297d741c14d134011c..6bd40e7ec65d50b48d64220e51b32d08897f6ab3 | shasum -a 256
→ diff check was silent; reviewed tree `049701dbc77c5fea2cfb566b71803575257724ff`, 23-path manifest `f1252c13f2339216c56797a788e73cf141758c7c054cb8af6bad7bdcdf12554b`, and full-index patch `5f2f87886529a9036ded0ada3aa0d1a3d64a5730cb5c379cddcd2733f416b3da` match the request.
$ env -u GIT_INDEX_FILE .venv/bin/python -m pytest tests/unit/test_cursor_hook_policy.py tests/unit/test_cursor_mailbox.py tests/unit/test_cursor_protocol_model.py tests/unit/test_cursor_seat_launcher.py tests/unit/test_cursor_surface_sync.py -q
→ 160 passed in 1.99s, but no focused policy case covers command, backtick, or process substitution inside an otherwise allowed read-only command.
$ env -u GIT_INDEX_FILE .venv/bin/python - <configured .cursor/hooks/seat-policy probe>
→ direct unbound `touch scripts/example.py` returned deny; `echo $(touch scripts/example.py)`, `echo \`touch scripts/example.py\``, `echo <(touch scripts/example.py)`, and `echo $(coordination/bin/cursor-publish --to operator --kind status --subject hidden)` each returned allow. `.cursor/hooks.json` wires this policy for `beforeShellExecution` with `failClosed: true`, so the allow is the operative hook decision.
$ env -u GIT_INDEX_FILE .venv/bin/python - <out-of-tree substitution proof>
→ policy allowed `echo $(touch marker)` under the unbound environment; Bash executed it in a temporary out-of-tree directory and created `marker` (return code 0). No Pipeline path was written.
$ env -u GIT_INDEX_FILE .venv/bin/python scripts/ci_smoke.py
→ runtime, ceremony, and placeholder checks passed, then GO-schema failed with the request-described 38 historical `Reviewed repository is unavailable` evidence-ledger bindings. The deleted external project was neither inspected nor restored; this baseline failure is separate from, and does not mitigate, the Cursor hard-boundary failure.

Cursor at send: 0
