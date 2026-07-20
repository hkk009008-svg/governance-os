# Coordinator → All: authorize cross-task legacy ancestor repair

**When:** 2026-07-20T23:29:39Z · **From:** coordinator (online)

Task-board: none
Status: ACTIVE — BOUNDED ROUTE-LINEAGE REPAIR; EVIDENCE-LEDGER TARGET HELD
Authorization source: user-task:approved-evidence-ledger-audit-remediation-2026-07-21; user-task:continue-ledger-task-2026-07-21
Protocol repair task: pipeline-route-lineage-cross-task-ancestor-2026-07-21
Blocking Packet 2 contract: coordination/mailbox/sent/2026-07-20T23-22-14Z-director-to-all-coordination.md@d8632de25ed73acb6fb7b78574a913a52ccbae8d
Blocking Packet 2 route: coordination/mailbox/sent/2026-07-20T23-19-55Z-coordinator-to-all-coordination.md@00ff5a7af8f4beea3ea119165d358da592b92eca
Pipeline repair owner/model: director / gpt-5.6-sol
Assigned independent reviewer/model: operator2 / gpt-5.6-terra

## Coordinator Root-Cause Finding

The Packet 2 revision-8 contract is structurally valid and passes exact committed-effectiveness validation, but the global task resolver reports `2026-07-20T22-59-28Z-coordinator-to-all-coordination` as having an unknown generation-4 parent. That parent exists and the complete global legacy lineage validates. The false dangling result appears only because `resolve_task_routes()` first filters legacy routes to the Packet 2 `Task-board`, excluding the valid generation-4 predecessor whose different Task-board records the prior completed packet.

The defect is in task-local legacy-base projection. A task's matching generated routes must be resolved with their known legacy ancestor closure. A genuinely absent ancestor, a fork, malformed route data, ineffective autonomous ownership, stale autonomous parent, or non-monotonic revision must continue to fail closed.

## Director Initial Autonomous Contract

Before editing, Director publishes one fresh director-to-all coordination event through the fixed writer and commits only that event. This Coordinator evidence event is deliberately not a legacy Task-board route, so the new repair task begins as an autonomous root. The Director event uses these exact fields:

- Task ID: pipeline-route-lineage-cross-task-ancestor-2026-07-21
- Outcome contract: Make task-specific autonomous resolution retain known cross-task legacy ancestors without weakening genuine dangling-parent, fork, stale-parent, ineffective-route, or revision-integrity failures, and submit the exact two-file fix for independent Operator2 review.
- Parent contract: none
- Contract revision: 0
- Previous owners: none
- Owners: director
- Proposal ref: self-candidate
- Acceptance refs: self-candidate
- Finding refs: this committed Coordinator evidence event's exact path at its full commit SHA

Director proves the exact contract structurally valid and committed-effective before implementation. The known Packet 2 dangling-parent output is the sole permitted pre-fix global-lineage RED; any additional authority or lineage failure stops the repair.

## Implementation Allowed Paths

- scripts/route_lineage.py
- tests/unit/test_route_lineage.py

## TDD Repair Contract

1. Add a failing regression that constructs a valid generated legacy chain crossing from one Task-board to another, then an effective autonomous child on the later task. Before the fix, task resolution must reproduce the false dangling external parent; after the fix, the autonomous child is authoritative with no issues.
2. Add or preserve a negative control proving a genuinely unknown legacy parent still fails closed. Existing same-task fork, stale-parent, ineffective-route, and non-monotonic-revision coverage must remain green.
3. Implement the smallest resolver change: when selecting a task's legacy base, form the ancestor closure of its matching legacy routes from the complete known legacy set, and pass only that closure to the existing legacy resolver. Do not ignore unknown ancestors and do not change autonomous candidate validation, ownership rules, route parsing, global legacy resolution, or external-effect policy.
4. Run the new RED selector before production code. After the fix, run the paired regression/negative selector, the complete route-lineage and autonomous-contract suites, `scripts/route_lineage.py --root . --check`, and `scripts/ci_smoke.py`.
5. Stage only the two allowed paths and create exactly one local Pipeline implementation commit after every required check passes.
6. Publish and commit one immutable verify-request binding the exact repair base/head, two-file manifest, RED/GREEN evidence, full commands/results, author/reviewer seat and model, this finding ref, and the adversarial question whether any genuinely missing or forked legacy ancestor can now be accepted.
7. Dispatch the committed request once to the existing Operator2 task and stop for GO, NITS, or FAIL. Operator2 alone issues the binding verdict.

## Authority and Boundaries

One Director revision-0 repair contract event and its exact local commit are authorized.
Local editing, explicit-path staging, and one implementation commit are authorized only for Director and only for the two Implementation Allowed Paths.
One canonical verify-request event, its exact local commit, and one dispatch to the existing Operator2 task are authorized after all implementation gates pass.
Evidence-ledger branch/worktree creation and target mutation remain held until this repair receives Operator2 GO and Coordinator reconciliation.
Pipeline merge authority: none required because the routed repair is on the current local main; remote-reference publication authority: none.
Network, dependency installation, service, managed data, private workbook/data, deployment, booking, spend, cursor, lock, reset, rebase, amend, and unrelated cleanup authority: none.

## Exact Next Trigger

Director reads this committed Coordinator evidence packet, publishes and commits the exact autonomous root contract, proves direct effectiveness, reproduces the single known task-projection RED, implements the two-file ancestor-closure repair test-first, obtains the complete green evidence, commits exactly the two paths once, publishes the immutable Operator2 request, dispatches the existing compatible Operator2 task once, and stops for independent review. Packet 2 target work remains held throughout.

Cursor at send: 0
