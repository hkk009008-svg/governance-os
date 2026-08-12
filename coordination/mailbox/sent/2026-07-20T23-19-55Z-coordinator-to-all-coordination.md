# Coordinator → All: correct Packet 2 autonomous lineage revision

**When:** 2026-07-20T23:19:55Z · **From:** coordinator (online)

Task-board: ledger-audit-remediation-packet2-parser-loss-2026-07-21
Task ID: ledger-audit-remediation-packet2-parser-loss-2026-07-21
Status: ACTIVE — PACKET 2 LINEAGE REVISION CORRECTION; TARGET UNTOUCHED
Route generation: 7
Supersedes route: coordination/mailbox/sent/2026-07-20T23-12-01Z-coordinator-to-all-coordination.md
Expected control HEAD: a95ef28803d083a8c62e8d2c6d96693b350a76ec
Superseded route ref: coordination/mailbox/sent/2026-07-20T23-12-01Z-coordinator-to-all-coordination.md@a40649cd9c32572a291e70ad26bcf6efd8bb5e1a
Authorization source: user-task:approved-evidence-ledger-audit-remediation-2026-07-21; user-task:continue-ledger-task-2026-07-21
Accepted implementation route: coordination/mailbox/sent/2026-07-20T22-59-28Z-coordinator-to-all-coordination.md@8fda08723356538a88cf7b8dcfee22e468e8c76c
Accepted finding-binding correction: coordination/mailbox/sent/2026-07-20T23-12-01Z-coordinator-to-all-coordination.md@a40649cd9c32572a291e70ad26bcf6efd8bb5e1a
Ineffective Director contract: coordination/mailbox/sent/2026-07-20T23-14-47Z-director-to-all-coordination.md@a95ef28803d083a8c62e8d2c6d96693b350a76ec
Approved design: docs/superpowers/specs/2026-07-21-evidence-ledger-audit-remediation-design.md@c8d74fb5c15b8b016001a641d33b9d52c0269451
Approved design SHA-256: bde185a3cefaaadca98cf1eafd841c212edf66d54ba679422bafcfe6274dbfec
Packet 2 plan: docs/superpowers/plans/2026-07-21-evidence-ledger-parser-loss-normalization.md@c8d74fb5c15b8b016001a641d33b9d52c0269451
Packet 2 plan SHA-256: f20ab14313e9928409a0f2866fe0d5fca4f827ef767283cd0fdf764cbc521367
Target repository: /Users/hyungkoookkim/evidence-ledger
Target worktree: /Users/hyungkoookkim/evidence-ledger/.worktrees/codex-audit-remediation-parser-loss
Target branch: codex/audit-remediation-parser-loss
Accepted target HEAD: 13413d05b0b40476b5d5919f99062d5104866818
Protected normal-checkout settings SHA-256: a40fae4d05b28d9ec2be89cb36c29f02bc46e3839ccb09af08a6aa4bab70c1e4
Owner seat/model: director / gpt-5.6-sol
Assigned non-author Operator seat/model: operator2 / gpt-5.6-terra

## Coordinator Root-Cause Reconciliation

The finding-binding correction succeeded structurally, but its mandated Director contract revision did not match the autonomous parent. A Coordinator Task-board route is a legacy effective route whose autonomous revision equals its `Route generation`. The accepted correction is generation 6, so its child had to be revision 7; the committed revision-1 Director self-claim is ineffective and global lineage correctly fails closed.

This generation-7 route supersedes that correction. A Director self-claim parented to this route must therefore be revision 8. The finding refs remain the two canonical `sha256:` digests already proved by the prior correction. No parser/import requirement changed, no validator change is warranted, and evidence-ledger remains untouched at the accepted parent.

## Exact Ineffective-Contract Retraction

Before publishing a replacement contract or creating the target worktree, Director verifies that commit a95ef28803d083a8c62e8d2c6d96693b350a76ec added only `coordination/mailbox/sent/2026-07-20T23-14-47Z-director-to-all-coordination.md`, that the file bytes still carry parent a40649cd9c32572a291e70ad26bcf6efd8bb5e1a and revision 1, and that Pipeline has no other worktree or index change.

Director then creates one history-preserving revert of exactly a95ef28803d083a8c62e8d2c6d96693b350a76ec. The revert must delete only that ineffective event. No reset, rebase, amend, manual mailbox edit, or unrelated cleanup is permitted. Director proves the event absent from `HEAD`, the accepted routes retained, global route lineage valid, Pipeline smoke `OK`, and the tree clean before continuing.

## Corrected Director Autonomous Contract Revision 8

After the exact retraction above and before target mutation, Director publishes exactly one fresh director-to-all coordination event through the fixed writer and commits only that generated event. It uses these exact autonomous fields:

- Task ID: ledger-audit-remediation-packet2-parser-loss-2026-07-21
- Outcome contract: Eliminate impossible-date crashes and silent evidence loss, validate agency HHMM tokens without fabricated times, preserve exact fractional manwon costs through whole-KRW conversion, collapse only complete identical placements, and submit the exact two-commit target range for independent Operator2 review.
- Parent contract: this committed superseding Coordinator route's exact path at its full commit SHA
- Contract revision: 8
- Previous owners: director
- Owners: director
- Proposal ref: self-candidate
- Acceptance refs: self-candidate
- Finding refs: sha256:bde185a3cefaaadca98cf1eafd841c212edf66d54ba679422bafcfe6274dbfec, sha256:f20ab14313e9928409a0f2866fe0d5fca4f827ef767283cd0fdf764cbc521367

Director copies this route's target repository, worktree, branch, accepted parent, seat/model assignment, Side-Effect Executor Token, Target Allowed Paths, synthetic-data boundary, two-commit requirement, exact final manifest, and Operator2 review contract. Director validates and commits the fresh event, proves committed effectiveness and global lineage, then reruns the ledger Director start guard against that exact committed event before target mutation.

## Side-Effect Executor Token

- effect: local branch and worktree creation
- executor: director
- target: /Users/hyungkoookkim/evidence-ledger/.worktrees/codex-audit-remediation-parser-loss
- scope: branch=codex/audit-remediation-parser-loss, parent=13413d05b0b40476b5d5919f99062d5104866818

## Target Allowed Paths

- import/parse_workbook.py
- import/tests/test_parse_workbook.py
- import/parse_agency_schedule.py
- import/tests/test_parse_agency_schedule.py
- import/load_agency.py
- import/tests/test_load_agency_unit.py

## Preserved Implementation and Review Contract

Every implementation, TDD, verification, exact-path, synthetic-data, two-target-commit, actual-range review, and stop requirement in the accepted implementation route remains binding. The finding-binding correction remains controlling for the two canonical digest refs. This route changes only the lineage revision and grants the exact ineffective-contract retraction above. Director uses the approved `superpowers:executing-plans` workflow directly; a child implementer remains outside scope.

Director remains the sole target writer. Operator2 remains the only assigned non-author reviewer and verdict issuer for the actual target range. Packet 3 remains held until Packet 2 receives independent review, Coordinator reconciliation, and separately authorized local integration.

Target-main integration authority: none.
Remote-reference publication authority: none.
Network and dependency-installation authority: none.
Service, managed database, managed Auth, private-data, deployment, booking, and spend authority: none.
Cursor and protocol-lock authority: none.
Existing target worktree/branch cleanup authority: none.
Unrelated Pipeline cleanup authority: none.

## Exact Next Trigger

Director reads this committed generation-7 route plus its two accepted predecessors, performs and proves only the exact ineffective-contract retraction, publishes and commits the exact revision-8 autonomous contract above with this route as immutable parent, and proves it effective. Only then does Director create the one authorized target worktree and execute the approved Packet 2 plan test-first. Director creates exactly the two verified target commits, publishes the immutable actual-range verify-request assigned to Operator2, dispatches the existing compatible Operator2 task once, and stops for the independent verdict. Any lineage, RED-evidence, test, scope, smoke, manifest, source-boundary, or clean-state failure is reported to Coordinator with both repositories preserved.

Cursor at send: 0
