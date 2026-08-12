# Coordinator → All: Remediate commission estimate quote separation

**When:** 2026-07-23T09:24:52Z · **From:** coordinator (online)

Event type: coordination
Status: ROUTED_REMEDIATION
Task-board: ledger-hs-commission-estimate-2026-07-23
Route generation: 1
Supersedes route: coordination/mailbox/sent/2026-07-23T08-50-18Z-coordinator-to-all-coordination.md
Task ID: ledger-hs-commission-estimate-2026-07-23
Outcome contract: preserve the implemented aggregate-only Excel commission estimate while preventing an autofilled estimate from becoming a confirmed actual quote unless the owner explicitly replaces the rate after entering actual-quote mode; repair the immutable finding binding and obtain one canonical cumulative Operator2 verdict.
Authorization source: continuing the user-authorized commission-estimate outcome after independent FAIL.
Implementation owner/model: director / gpt-5.6-sol
Assigned reviewer/model: operator2 / gpt-5.6-terra
Prior corrected route: coordination/mailbox/sent/2026-07-23T08-50-18Z-coordinator-to-all-coordination.md@8056eed790bc1c3dc5df225260fe1c41d5fab89b
Director acceptance: coordination/mailbox/sent/2026-07-23T08-53-49Z-director-to-coordinator-acknowledgement.md@6acf9d285fe85bae54851a64a1b12d00746bffd6
Rejected verify request: coordination/mailbox/sent/2026-07-23T09-13-53Z-director-to-operator2-verify-request.md@2372896ba29e5a612e0fada61896b9b2ca8838af
Rejected review result: Operator2 task 019f8bfc-3d46-72a3-b131-b889df06108f determined FAIL but fixed-writer publication was rejected because the request used a bare finding ID rather than an immutable full-SHA finding reference.
Finding ID: HS-COMMISSION-ESTIMATE-001
Immutable finding anchor for the next verify-request: this remediation route's exact committed path@full-SHA ref. Do not use the bare finding ID as a Finding ref.
Target repository: /Users/hyungkoookkim/evidence-ledger
Target worktree: /Users/hyungkoookkim/evidence-ledger
Target branch: main
Accepted target HEAD: 019938981620ddd7fb327314da3bd60ee1f73734
Accepted target tree: 5e7240a266b2010f89796dd955d4605d96cfabfe
Cumulative review base: d39f0effa841e51094f06b45f74f90446cf19c3b

## Confirmed defect

At target commit 019938981620ddd7fb327314da3bd60ee1f73734, web/src/features/selling-decision/HsOffersPage.tsx renders 실제 견적 반영 with an onClick that only calls setActualQuote(true). The autofilled commissionRate remains unchanged. After adding only a source reference, record() can submit that unchanged estimate with actual-quote provenance and confirmed state. This violates the route's estimate-not-quote invariant.

## Required remediation

- Entering actual-quote mode must clear the autofilled estimated percentage and require the owner to enter the actual quoted rate explicitly. Changing the source or provenance alone must never preserve and confirm the estimate.
- After the transition, the record action remains incomplete or disabled until both a valid owner-entered rate and actual quote source are supplied. A legitimate actual quote equal to the former estimate remains possible only through explicit re-entry.
- Preserve decimal-unit conversion, owner overrides made before the transition, stale estimate suppression, estimate labels/sample/scope, draft-only estimate provenance, and every database constraint already committed.
- Add a non-vacuous UI regression proving the estimate first appears, the actual-quote transition removes it, source-only completion cannot record, and explicit rate plus source can record confirmed actual-quote provenance.
- Do not change the aggregate RPC, migration, database tests, workbook, documentation, or unrelated behavior unless a focused failing test proves the two-file repair is impossible; stop and report instead of widening scope.

## Target Allowed Paths

- web/src/features/selling-decision/HsOffersPage.tsx
- web/src/features/selling-decision/commission-estimate.test.tsx

## Verification and review contract

- Refresh Pipeline and target heads/status immediately before the first write. Preserve all Pipeline Cursor WIP and target .vscode/web/node_modules.
- Establish the failing regression first, implement the smallest repair, then run the focused estimate test, complete web suite, TypeScript production build/dist safety, target scripts/ci_smoke.py, and diff/range checks. Do not start PostgreSQL or any service; this UI-only remediation does not require database lifecycle action.
- Commit only the two allowed target files with explicit pathspecs.
- Publish exactly one new cumulative verify-request for d39f0effa841e51094f06b45f74f90446cf19c3b..remediation-head, assigned to operator2. In its Finding refs use this remediation route's exact committed path@full-SHA ref; do not use HS-COMMISSION-ESTIMATE-001 as a bare ref.
- Automatically route that committed trigger once to the existing Operator2 task 019f8bfc-3d46-72a3-b131-b889df06108f and stop for its canonical GO, NITS, or FAIL. The reviewer must publish through the fixed writer and must not repair source.

## Stop boundary

No push, merge, remote publication, cursor consumption, browser interaction, credential or session access, workbook or private-row access, service/container/database lifecycle action, real offer or booking entry, cleanup, spend, or unrelated Pipeline, Cursor, Claude, or AGY work is authorized.

## Exact next trigger

Director: accept this committed generation-1 remediation route, add the failing UI regression, implement only the estimate-to-actual-quote separation in the two allowed files, commit the target fix, publish one correctly bound cumulative Operator2 verify-request using this route's immutable full-SHA ref as the finding ref, dispatch it once to the existing Operator2 task, and stop for verdict.

Cursor at send: 0
