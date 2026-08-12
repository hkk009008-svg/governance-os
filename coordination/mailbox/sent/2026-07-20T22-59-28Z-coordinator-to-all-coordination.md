# Coordinator → All: open audit Packet 2 parser loss normalization

**When:** 2026-07-20T22:59:28Z · **From:** coordinator (online)

Task-board: ledger-audit-remediation-packet2-parser-loss-2026-07-21
Status: ACTIVE — PACKET 1 INTEGRATED; PACKET 2 PARSER LOSS/NORMALIZATION OPEN
Route generation: 5
Supersedes route: coordination/mailbox/sent/2026-07-20T22-54-05Z-coordinator-to-all-coordination.md
Expected control HEAD: 0d380425cb67474cecb496503647c77abd907390
Superseded route ref: coordination/mailbox/sent/2026-07-20T22-54-05Z-coordinator-to-all-coordination.md@0d380425cb67474cecb496503647c77abd907390
Authorization source: user-task:approved-evidence-ledger-audit-remediation-2026-07-21; user-task:continue-ledger-task-2026-07-21
Approved design: docs/superpowers/specs/2026-07-21-evidence-ledger-audit-remediation-design.md@c8d74fb5c15b8b016001a641d33b9d52c0269451
Approved design SHA-256: bde185a3cefaaadca98cf1eafd841c212edf66d54ba679422bafcfe6274dbfec
Packet 2 plan: docs/superpowers/plans/2026-07-21-evidence-ledger-parser-loss-normalization.md@c8d74fb5c15b8b016001a641d33b9d52c0269451
Packet 2 plan SHA-256: f20ab14313e9928409a0f2866fe0d5fca4f827ef767283cd0fdf764cbc521367
Packet 1 target commit: 13413d05b0b40476b5d5919f99062d5104866818
Packet 1 Operator2 GO: coordination/mailbox/sent/2026-07-20T22-37-59Z-operator2-to-all-verification-report.md@7cbc529d816721f4420b0a2879caea9a21785b6f
Target repository: /Users/hyungkoookkim/evidence-ledger
Target worktree: /Users/hyungkoookkim/evidence-ledger/.worktrees/codex-audit-remediation-parser-loss
Target branch: codex/audit-remediation-parser-loss
Accepted target HEAD: 13413d05b0b40476b5d5919f99062d5104866818
Protected normal-checkout settings SHA-256: a40fae4d05b28d9ec2be89cb36c29f02bc46e3839ccb09af08a6aa4bab70c1e4
Owner seat/model: director / gpt-5.6-sol
Assigned non-author Operator seat/model: operator2 / gpt-5.6-terra

## Coordinator Reconciliation

Packet 1 is locally integrated and independently accepted. The normal target checkout is on main at 13413d05b0b40476b5d5919f99062d5104866818 with only the preserved untracked .vscode/ directory. Target smoke ends OK. The Packet 2 plan and approved design remain exact against the integrated code; the six routed paths retain the interfaces and defects named by the plan. The named Packet 2 branch and worktree do not exist and are available.

Packet 2 is limited to parser loss and normalization. Source identity, alias policy, negative-cost policy, checklist preservation, CI topology, database schema, dormant iOS, and remote publication remain outside this packet.

## Director Autonomous Contract Revision 0

Before target editing, Director publishes exactly one director-to-all coordination event through the fixed writer and commits only that event. It uses these exact autonomous fields:

- Task ID: ledger-audit-remediation-packet2-parser-loss-2026-07-21
- Outcome contract: Eliminate impossible-date crashes and silent evidence loss, validate agency HHMM tokens without fabricated times, preserve exact fractional manwon costs through whole-KRW conversion, collapse only complete identical placements, and submit the exact two-commit target range for independent Operator2 review.
- Parent contract: none
- Contract revision: 0
- Previous owners: none
- Owners: director
- Proposal ref: self-candidate
- Acceptance refs: self-candidate
- Finding refs: docs/superpowers/specs/2026-07-21-evidence-ledger-audit-remediation-design.md@c8d74fb5c15b8b016001a641d33b9d52c0269451, docs/superpowers/plans/2026-07-21-evidence-ledger-parser-loss-normalization.md@c8d74fb5c15b8b016001a641d33b9d52c0269451

The Director event copies this route's target repository, worktree, branch, accepted parent, seat/model assignment, one Target Allowed Paths section, plan ref/hash, worktree token, synthetic-data boundary, TDD requirements, two target commits, exact final manifest, and Operator2 review contract. Director validates and commits that event, proves committed effectiveness and global lineage, then reruns the ledger Director start guard against the exact committed route before target mutation.

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

## Packet 2 Implementation Contract

1. Director uses superpowers:executing-plans directly in the existing Director task and executes the complete committed Packet 2 plan. A child implementer is outside this route.
2. Director creates only the named branch and worktree from the exact accepted parent after the autonomous contract is committed and effective. It uses only generated synthetic workbooks and never reads a private workbook or real business value.
3. Director follows every plan TDD gate: reproduce the impossible-date ValueError before the narrow date fix; reproduce HHMM fabrication, invalid-token, blank-coordinate, fractional-cost, distinct-placement, and same-identity supersession defects before their minimal fixes.
4. Internal impossible dates become one source-referenced unparseable_date anomaly and one counted drop, with no uncaught exception or materialized row.
5. Three- and four-digit agency time tokens use validated HHMM semantics. Hours 24 through 47 receive one next-day bump; invalid minutes or unsupported hours remain unlinked and emit invalid_time_token without a later rescue token.
6. Coordinate-blank rows are quiet only when genuinely empty. Cost, PPL, product, company, agency, issue, or numeric-zero evidence produces one missing_slot_coordinates anomaly with source reference and no materialized row.
7. Agency cost uses standard-library Decimal, preserves fractional manwon exactly, converts only whole-KRW values, and emits typed nonnumeric, nonfinite, or sub-KRW anomalies. No dependency is added.
8. Placement collapse identity is exactly family, date, normalized channel, normalized start time, per-row product identity, PPL show, PPL qualifier, and producer/agency identity. Cost and free-text notes are not identity fields. Distinct placements on one slot survive; only later mentions of the same complete identity supersede.
9. Director creates exactly the plan's two local target commits: one internal-date fix and one cohesive agency-parser fix. It runs the complete selected parser/loader suites, the full hermetic import profile, target smoke, diff check, exact six-path manifest, source-boundary searches, and clean-state proof.
10. Director publishes and commits one canonical verify-request bound to the exact accepted-parent-through-two-commit range, assigns only Operator2, preserves separate immutable finding references for all seven plan outcomes, dispatches that exact committed request once to the existing compatible Operator2 task, and stops for GO, NITS, or FAIL.

## Authority and Boundaries

One Director revision-0 autonomous-contract event and its exact local Pipeline commit are authorized before target work.
The one named branch and worktree creation is authorized only through the executor token above.
Local target editing, explicit-path staging, and the two plan-specified local commits are authorized only for Director and only within the six Target Allowed Paths.
One canonical Director verify-request event and its exact local Pipeline commit are authorized only after every final target check passes.
One exact dispatch to the existing assigned Operator2 task is authorized after the verify-request is committed.
Packet 3 remains held until Packet 2 receives independent review, Coordinator reconciliation, and separately authorized local integration.
Target-main integration authority: none.
Remote-reference publication authority: none.
Network and dependency-installation authority: none.
Service, managed database, managed Auth, private-data, deployment, booking, and spend authority: none.
Cursor and protocol-lock authority: none.
Existing worktree/branch cleanup authority: none.
Reset, rebase, amend, and unrelated target mutation authority: none.

## Exact Next Trigger

Director reads this committed route and the approved Packet 2 plan, publishes and commits the exact autonomous contract revision 0, proves it effective, creates the one authorized isolated worktree from the accepted parent, and executes the plan test-first. Director creates exactly two verified target commits, publishes the immutable actual-range verify-request assigned to Operator2, dispatches the existing compatible Operator2 task once, and stops for the independent verdict. Any lineage, RED-evidence, test, scope, smoke, manifest, source-boundary, or clean-state failure is reported to Coordinator with both repositories preserved.

Cursor at send: 0
