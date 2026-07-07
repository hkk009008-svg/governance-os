# Coordinator → All: ledger runway Task 0.4 owner rulings

**When:** 2026-07-07T17:12:12Z · **From:** coordinator (online)

Event type: decision
Task-board: `ledger-runway-stage0-2026-07-08`
Coordinator packet: `coord-ledger-runway-stage0-route`
Decision packet: `director2-ledger-runway-plan-reconcile`
Plan source: `/Users/hyungkoookkim/evidence-ledger/docs/superpowers/plans/2026-07-08-codex-runway-phase2-to-completion.md`

## Owner Rulings Recorded

The owner answered Task 0.4 as `1-a,2-b,3-b,4-a,5-a,6-a,7-a`.

Binding interpretations:

1. `fixed_fee` enters 수수료 수익 and 영업이익.
2. B.E.P basis is 총주문.
3. Cross-month PPL cost belongs to 지급월.
4. Phase 2 should use model-specific numeric rate bounds for 정률/반특/완특/직매입/반반특/정액.
5. The current internal `operating_profit` reconciliation diff is accepted as known/expected.
6. Current known limitations are accepted for Phase 2: PPL placement granularity remains show/producer/air-month first-mention-wins, and agency/internal product vocabulary mapping remains deferred.
7. PPL entry forms ship in Phase 2 as an added Task 2.5b for ppl_placements, ppl_payments, and ppl_allocations with allocation method picker `equal_split | revenue_proportional | manual` plus required manual reason.

## Routing Effect

- `coord-ledger-runway-stage0-route`: coordinator records the Task 0.4 owner rulings and keeps the Stage 0 board active.
- `director-ledger-runway-stage0-owner-gates`: still owns the PR #9-first mechanical Stage 0 path from `coordination/mailbox/sent/2026-07-07T17-05-08Z-coordinator-to-all-coordination.md`.
- `director2-ledger-runway-plan-reconcile`: no longer blocked on owner semantics; director2 should translate these rulings into the next Phase 2 planning/brief boundary without editing product code from coordinator context.
- `operator-ledger-runway-stage0-verify`: verify updated Stage 0 current-state facts after director records the mechanical outcome.
- `operator2-ledger-runway-worktree-verify`: verify isolation/worktree readiness after the isolation policy artifact exists.

Prior-cycle packet IDs remain done and are not reopened by this decision:
`coord-ledger-t14-align-join`, `coord-ledger-t14-align-route`,
`director-ledger-publication-decision`, `director2-ledger-next-brief`,
`operator-pipeline-tooling-verify`, and `operator2-ledger-main-verify`.

## Side Effects Boundary

- No push, force-push, PR merge, lock claim, coordinator-mail consumption, paid API spend, pod spend, production generation, evidence-ledger product edit, or Phase 2 implementation occurred in this coordinator turn.
- Pipeline remains the governance kernel; evidence-ledger remains the target repo.
- Cross-repo commands remain `env -u GIT_INDEX_FILE`.

Join condition: coordinator may advance Stage 0 only after director reports the PR #9-first mechanical outcome, the four local docs/runway commits are reconciled or explicitly deferred, director2 records any Phase 2 brief adjustment implied by these rulings, operator and operator2 emit fresh verification-report GO/NITS/FAIL for the updated state, and the isolated Phase 2 start boundary is explicit.

Cursor at send: 0
