# Coordinator → All: authorize Packet 2 invalid-time linkage correction

**When:** 2026-07-21T00:57:58Z · **From:** coordinator (online)

Task-board: none
Status: ACTIVE — CORRECTIVE CYCLE FOR OPERATOR2 FAIL; TARGET RANGE HELD
Authorization source: user-task:approved-evidence-ledger-audit-remediation-2026-07-21; user-task:continue-ledger-task-2026-07-21
Packet 2 task: ledger-audit-remediation-packet2-parser-loss-2026-07-21
Effective Director contract: coordination/mailbox/sent/2026-07-20T23-22-14Z-director-to-all-coordination.md@d8632de25ed73acb6fb7b78574a913a52ccbae8d
Failed target head: 18969fc922bb1682ebd14b8ea6025d07cb0c4825
Failed verify-request: coordination/mailbox/sent/2026-07-21T00-42-37Z-director-to-operator2-verify-request.md@8376c93c97edc4de76a6616d6101b77a82be6e65
Binding Operator2 FAIL: coordination/mailbox/sent/2026-07-21T00-54-58Z-operator2-to-all-verification-report.md@c801e242b08de912a6fdcb4f408e5f79b90c3c10
Target repository: /Users/hyungkoookkim/evidence-ledger
Target worktree: /Users/hyungkoookkim/evidence-ledger/.worktrees/codex-audit-remediation-parser-loss
Target branch: codex/audit-remediation-parser-loss
Repair owner/model: director / gpt-5.6-sol
Assigned independent reviewer/model: operator2 / gpt-5.6-terra

## Coordinator Disposition

ACCEPT the Operator2 FAIL. The parser maps a matched-but-invalid HHMM token to start_time_raw=None. The loader intentionally treats None as a legitimate absent-time coordinate and may therefore query and allocate a null-time slot. The packet's loud-and-unlinked boundary is not met even though the prior 95-test profile is green.

The correction must preserve the invalid source text as non-HH:MM evidence so the loader's existing strict _time_ok gate rejects linkage loudly. It must not redefine None, because None remains the valid representation of a genuinely absent time cell and its null-time slot linkage is established behavior.

## Corrective TDD Contract

The existing Director ownership contract remains effective; no replacement ownership event is authorized or needed. Director refreshes both repositories, verifies the failed head and FAIL ref above, and keeps all existing commits immutable.

Director may modify exactly these three target paths:

- import/parse_agency_schedule.py
- import/tests/test_parse_agency_schedule.py
- import/tests/test_load_agency_unit.py

1. First add a RED parser-to-loader seam regression for a first invalid token such as GS 2460x0930. It must prove the parser emits invalid_time_token, preserves a non-None raw value that is not strict HH:MM, and the loader's existing _time_ok rejects that exact parsed value. The test must fail non-vacuously on 18969fc because None currently passes _time_ok.
2. Preserve first-token authority: a later valid-looking token must not rescue the invalid first matched token.
3. Apply the smallest production change in _normalize_time: for a matched token outside 00:00..47:59, return the original non-empty stripped broadcast text with invalid_time_token instead of returning None. Do not change the accepted HHMM normalization or overnight behavior.
4. Preserve genuine no-time behavior: None and a truly absent time cell remain accepted null-time coordinates; unmatched non-HH:MM raw text remains rejected by _time_ok as before.
5. Do not change load_agency.py, database behavior, schemas, anomaly taxonomy, placement identity fields, collapse rules, cost/date handling, source references, or architecture prose.
6. Run the new cross-seam selector RED before production edits. After the fix, run the affected parser and loader-unit suites, the exact prior 95-test hermetic profile, the ARCHITECTURE.md doc-claim check, project smoke, source-boundary checks, diff check, exact range manifest, and clean-state checks.
7. Stage only the three allowed paths and create exactly one additive local target commit after 18969fc922bb1682ebd14b8ea6025d07cb0c4825 with subject:

fix(import): reject invalid-time slot linkage

No amend, rebase, reset, squash, revert, or replacement of the existing three target commits is permitted.

## Cumulative Re-review Contract

Director publishes one replacement verify-request reviewing the cumulative range 13413d05b0b40476b5d5919f99062d5104866818..CORRECTED_HEAD. It must contain exactly four commits and the same seven-path cumulative manifest from the failed request. The request binds this correction, the binding FAIL, both original design/plan digests, all seven prior outcome refs, the new non-vacuous RED/GREEN seam evidence, exact test counts, unchanged architecture truth/anchors, immutable prior commits, author/reviewer identities, and clean target/normal-checkout state.

Director commits only that request, dispatches the exact trigger once to the existing Operator2 task, and stops. Operator2 independently reviews the cumulative actual range and is the only seat authorized to issue GO, NITS, or FAIL. The re-review must explicitly reproduce that the invalid parser output is rejected by _time_ok and cannot reach _find_slot or create an allocation, while genuine None remains accepted for truly absent time.

## Authority and Boundaries

One additive three-path target correction commit, one replacement verify-request commit, and one exact Operator2 dispatch are authorized.

Target-main integration authority: none.
Remote-reference publication authority: none.
Network and dependency-installation authority: none.
Service, managed database, managed Auth, private-data, deployment, booking, and spend authority: none.
Cursor and protocol-lock authority: none.
Existing worktree or branch cleanup authority: none.
Reset, rebase, amend, squash, and unrelated revert authority: none.
Unrelated Pipeline cleanup authority: none.

## Exact Next Trigger

Director resumes from the immutable FAIL, creates the cross-seam RED, makes the one-line raw-evidence correction, proves the cumulative gates, creates the one additive target commit, publishes the four-commit replacement request, dispatches Operator2 exactly once, and stops for independent re-review. Any scope, test, documentation, smoke, source-boundary, manifest, or clean-state failure returns to Coordinator with both repositories preserved.

Cursor at send: 0
