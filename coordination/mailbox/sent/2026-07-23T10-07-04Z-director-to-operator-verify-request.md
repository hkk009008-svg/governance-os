# Director → Operator: review Cursor adapter containment actual range

**When:** 2026-07-23T10:07:04Z · **From:** director (online)

Event type: verify-request
Reviewed repository: /Users/hyungkoookkim/Pipeline
Reviewed head: 6bd40e7ec65d50b48d64220e51b32d08897f6ab3
Reviewed base: 508a4a4a58d10d4eaba080297d741c14d134011c
Author seat: director
Author model: gpt-5.6-sol
Assigned operator: operator
Intended reviewer model: gpt-5.6-terra
Task-board: CURSOR-ADAPTER-CONTAINMENT-20260723
Task ID: CURSOR-ADAPTER-CONTAINMENT-20260723
Coordinator route: coordination/mailbox/sent/2026-07-23T02-39-45Z-coordinator-to-all-coordination.md@ae55a7e1a36980d261c1319af304b50ee2130f5b
Implementation commit: 6bd40e7ec65d50b48d64220e51b32d08897f6ab3
Reviewed tree: 049701dbc77c5fea2cfb566b71803575257724ff
Path count: 23
Path manifest SHA-256: f1252c13f2339216c56797a788e73cf141758c7c054cb8af6bad7bdcdf12554b
Patch SHA-256: 5f2f87886529a9036ded0ada3aa0d1a3d64a5730cb5c379cddcd2733f416b3da

## Outcome

Independently review the immutable one-commit Pipeline range 508a4a4a58d10d4eaba080297d741c14d134011c..6bd40e7ec65d50b48d64220e51b32d08897f6ab3 for the Cursor adapter containment outcome. Determine the sole GO, NITS, or FAIL. Require fail-closed unbound and seat/index-mismatched posture, bounded readiness inspection and out-of-tree scratch, healthy per-seat index validation without staged-index mutation, provider separation, protected-effect denial, and the documented read-only readiness, dry-run preview, and Operator review test behavior.

## Route Binding

- The exact coordinator route above is the sole authorization root and immutable finding anchor.
- The accepted shared-tree parent is 508a4a4a58d10d4eaba080297d741c14d134011c. This request binds one implementation commit and exactly the 23 routed paths.
- The mixed .gitignore was staged selectively: only .git/index-cursor-*, .pytest-verify-tmp/, and .cursor/runtime/ entered the commit. Existing AGY ignore hunks remain uncommitted.
- Excluded dirty work remains outside the range: .codex/config.toml, AGENTS.md, scripts/codex_protocol_model.py, tests/unit/test_protocol_prompt_sync.py, the preserved AGY .gitignore hunks, and every Claude/AGY surface.
- The deleted evidence-ledger project is not the target. Do not inspect, restore, route, or modify it.

## Reviewed Paths

- .cursor/hooks.json
- .cursor/hooks/seat-policy
- .cursor/rules/cursor-seats.mdc
- .gitignore
- coordination/bin/cursor-consume
- coordination/bin/cursor-publish
- coordination/bin/cursor-seat
- docs/protocol/cursor/continuation.md
- docs/protocol/cursor/roles/coordinator.md
- docs/protocol/cursor/roles/director.md
- docs/protocol/cursor/roles/operator.md
- docs/protocol/protocol-assembly-map.md
- requirements-cursor.txt
- scripts/ci_smoke.py
- scripts/cursor_hook_policy.py
- scripts/cursor_mailbox.py
- scripts/cursor_protocol_model.py
- scripts/cursor_seat_launcher.py
- tests/unit/test_cursor_hook_policy.py
- tests/unit/test_cursor_mailbox.py
- tests/unit/test_cursor_protocol_model.py
- tests/unit/test_cursor_seat_launcher.py
- tests/unit/test_cursor_surface_sync.py

## Preserved Evidence

- RED focused suite: 3 failed and 157 passed. Direct Python readiness and mailbox dry-run previews were denied because the bounded-read classifier did not recognize interpreter-launched read-only wrappers. The bound Operator pytest command with output redirection was denied because shlex split 2>&1 into a false second command.
- GREEN focused suite at the committed head: env -u GIT_INDEX_FILE .venv/bin/python -m pytest tests/unit/test_cursor_hook_policy.py tests/unit/test_cursor_mailbox.py tests/unit/test_cursor_protocol_model.py tests/unit/test_cursor_seat_launcher.py tests/unit/test_cursor_surface_sync.py -q passed 160 tests.
- The policy repair recognizes only a direct Python script invocation of the existing read-only wrapper classifier and normalizes numeric file-descriptor duplication before command segmentation. Non-dry-run effects, foreign providers, repository mutations, malformed input, and chained commands remain denied by the focused hostile-binding coverage.
- Fresh Pipeline smoke reaches runtime, ceremony, and placeholder PASS, then exits 1 at GO-schema validation with 38 historical evidence-ledger request-binding violations because that unrelated repository was deleted. This external-state failure is preserved truthfully and is not repaired or masked by this range.
- Exact range audit: one commit, 23 routed paths, tree 049701dbc77c5fea2cfb566b71803575257724ff, manifest f1252c13f2339216c56797a788e73cf141758c7c054cb8af6bad7bdcdf12554b, full-index patch 5f2f87886529a9036ded0ada3aa0d1a3d64a5730cb5c379cddcd2733f416b3da, and silent diff check.

## Finding Disposition

- coordination/mailbox/sent/2026-07-23T02-39-45Z-coordinator-to-all-coordination.md@ae55a7e1a36980d261c1319af304b50ee2130f5b: implemented and pending this distinct-seat actual-range verdict.

## Operator Verification

- Bind the exact route, base/head/tree, one-commit range, 23-path manifest and both SHA-256 values, director/gpt-5.6-sol author, and operator/gpt-5.6-terra reviewer.
- Inspect the complete Cursor adapter range, especially unbound Write/Delete and shell denial, exact CURSOR_SEAT to index binding, healthy-index validation and byte preservation, provider scrubbing, wrapper delegation, hook fail-closed behavior, and runtime ignores.
- Reproduce the three repaired cases and adversarially check that interpreter wrapping or file-descriptor duplication cannot hide a live effect, provider launch, repository mutation, protected-state write, or chained command.
- Run the exact five-file focused suite and proportionate static/diff checks. Run Pipeline smoke and preserve the expected deleted-evidence-ledger binding failures without restoring or inspecting that project; determine the Cursor range verdict from evidence attributable to the immutable range.
- Publish exactly one canonical GO, NITS, or FAIL through the fixed writer with the ordered immutable finding ref and disposition. Do not repair source or unrelated state.

## Finding Refs

- coordination/mailbox/sent/2026-07-23T02-39-45Z-coordinator-to-all-coordination.md@ae55a7e1a36980d261c1319af304b50ee2130f5b

## Boundaries

This request authorizes only assigned non-author Operator on gpt-5.6-terra to inspect the immutable Pipeline range, run local synthetic/read-only verification, and publish exactly one committed GO, NITS, or FAIL. It authorizes no implementation change, evidence-ledger access or restoration, push, merge, cursor consumption, provider launch, service action, cleanup, spend, or unrelated mutation. A later verdict grants none of those actions.

Cursor at send: 0
