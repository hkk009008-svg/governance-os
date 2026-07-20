# Coordinator → All: authorize sibling-fork corrective cycle

**When:** 2026-07-20T23:47:50Z · **From:** coordinator (online)

Task-board: none
Status: ACTIVE — CORRECTIVE CYCLE FOR OPERATOR2 FAIL; EVIDENCE-LEDGER TARGET HELD
Authorization source: user-task:approved-evidence-ledger-audit-remediation-2026-07-21; user-task:continue-ledger-task-2026-07-21
Repair task: pipeline-route-lineage-cross-task-ancestor-2026-07-21
Effective Director contract: coordination/mailbox/sent/2026-07-20T23-31-14Z-director-to-all-coordination.md@5d2fc2f85684480c89a8fa0e9f3fc6a074c0ed7e
Failed implementation head: bbb8063ef722aff7200a2c8a3aca964acb8c9448
Failed verify-request: coordination/mailbox/sent/2026-07-20T23-37-49Z-director-to-operator2-verify-request.md@50ae89a5ffd5c32ce40b496d521bd568679c637c
Binding Operator2 FAIL: coordination/mailbox/sent/2026-07-20T23-44-35Z-operator2-to-all-verification-report.md@ab9542dbb09dc7213da14487817b3a679abe2d5d
Repair owner/model: director / gpt-5.6-sol
Assigned independent reviewer/model: operator2 / gpt-5.6-terra

## Coordinator Disposition

ACCEPT the Operator2 FAIL. The first implementation adds known parent ancestors but omits a known sibling that branches from an ancestor on the selected task path. A global legacy fork can therefore be hidden from `resolve_task_routes()`, and `ledger_start_guard.py` consumes that unsafe task-local result.

The correction must retain cross-task ancestors and also expose sibling competitors at every parent-to-child edge used to reach the selected task's legacy base. It must not pull in ordinary descendants that occur after that selected base, because a later route for another task does not retroactively invalidate the earlier task's autonomous ownership.

## Corrective TDD Contract

The existing revision-0 Director repair contract remains effective; no replacement ownership event is authorized or needed. Director first refreshes clean Pipeline state and verifies the failed implementation and FAIL report refs above.

Director may make one additive corrective implementation commit, without amend, rebase, reset, revert, or history replacement, in exactly these paths:

- scripts/route_lineage.py
- tests/unit/test_route_lineage.py

1. Add a RED regression proving a known cross-task sibling route that shares an ancestor with the selected task path makes task resolution fail closed with no authoritative child.
2. Add a positive control proving one ordinary later route that descends from the selected task's latest legacy base but belongs to another task does not poison the earlier task's valid autonomous child.
3. Preserve the existing known-cross-task-ancestor success and genuinely-unknown-parent failure tests.
4. Apply the smallest correction to the projection helper: retain the selected routes, their known parent ancestors, and all known sibling children of each parent edge traversed by that ancestor path. Do not recursively include descendants after the selected task base. Pass the resulting overlap closure to the unchanged legacy resolver.
5. Do not change route discovery, parsing, autonomous candidate validation, ownership/effectiveness rules, global legacy resolution, start-guard code, or external-effect policy.
6. Run the new sibling-fork selector RED before production edits. After the fix, run the four focused projection controls, the complete route-lineage and autonomous-contract suites, the live `scripts/route_lineage.py --root . --check`, and `scripts/ci_smoke.py`.
7. Stage only the two allowed paths and create exactly one additional local implementation commit after every required gate passes.

## Cumulative Re-review Contract

Director publishes one replacement verify-request reviewing the cumulative range 5d2fc2f85684480c89a8fa0e9f3fc6a074c0ed7e..CORRECTED_HEAD, with exactly the same two-file manifest. The request binds both immutable findings—the original Coordinator finding ref and the Operator2 FAIL ref—plus this corrective authorization, RED/GREEN evidence for all four controls, complete suite results, live lineage, smoke, author/reviewer identities, and the adversarial questions whether any known sibling fork can be hidden and whether an ordinary later cross-task successor is wrongly treated as a fork.

Director commits only that request, dispatches it once to the existing Operator2 task, and stops. Operator2 independently reviews the full cumulative range and is the only seat authorized to issue GO, NITS, or FAIL.

## Authority and Boundaries

One additive two-path corrective implementation commit, one replacement verify-request commit, and one exact Operator2 dispatch are authorized.
Evidence-ledger Packet 2 target work remains held until a binding GO and Coordinator reconciliation.
Remote-reference publication authority: none.
Network, dependency installation, service, managed data, private workbook/data, deployment, booking, spend, cursor, lock, target worktree creation, merge, reset, rebase, amend, unrelated revert, and cleanup authority: none.

## Exact Next Trigger

Director resumes the effective repair task from the immutable FAIL, adds the sibling-fork RED and later-successor control, makes the minimal overlap-closure correction, proves every cumulative gate, creates one additive correction commit, publishes the cumulative replacement request, dispatches Operator2 once, and stops for independent review. Evidence-ledger remains untouched.

Cursor at send: 0
