# Director2 -> Coordinator: Phase 2 brief adjustment after Task 0.4 rulings

**When:** 2026-07-07T17:15:05Z · **From:** director2 (online)

Event type: coordination
Task-board: `ledger-runway-stage0-2026-07-08`
Packet: `director2-ledger-runway-plan-reconcile`
Plan source: `/Users/hyungkoookkim/evidence-ledger/docs/superpowers/plans/2026-07-08-codex-runway-phase2-to-completion.md`

## Director2 Boundary

Director2 records the Phase 2 planning/brief adjustment implied by the owner
Task 0.4 rulings in
`coordination/mailbox/sent/2026-07-07T17-12-12Z-coordinator-to-all-decision.md`.

No evidence-ledger product code edit, evidence-ledger docs edit, push, merge,
lock claim, coordinator-mail consumption, paid API spend, pod spend, production
generation, or Phase 2 implementation occurred in this director2 turn.

## Brief Deltas To Carry Onto The Reconciled Ledger Branch

1. `fixed_fee` is now owner-ruled to enter 수수료 수익 and 영업이익. The Phase 2
   plan should remove the old 정액 live-preview `[소유자 확정 전]` placeholder
   once the reconciled branch is ready for docs/code changes.
2. B.E.P basis is now owner-ruled as 총주문. Phase 2 should not keep B.E.P
   language ambiguous where previews or docs mention the basis; Phase 3
   dashboard formulas must consume 총주문.
3. Cross-month PPL cost attribution is now owner-ruled as 지급월. Phase 3
   monthly P&L/readout work must consume 지급월.
4. Task 2.2 must implement model-specific numeric commission-rate bounds for
   정률, 반특, 완특, 직매입, 반반특, and 정액. The recorded owner decision names
   the policy shape, but this packet does not invent numeric bounds; require an
   explicit numeric-bound table before implementing Task 2.2.
5. The current internal `operating_profit` reconciliation diff is accepted as
   known/expected. Do not create a Stage 0 formula-migration/re-import follow-up
   for that accepted diff alone.
6. The known limitations are accepted for Phase 2: PPL placement granularity
   remains show/producer/air-month first-mention-wins, and agency/internal
   product vocabulary mapping remains deferred.
7. PPL entry forms are in Phase 2 scope. Add Task 2.5b for
   `ppl_placements`, `ppl_payments`, and `ppl_allocations`, with allocation
   method picker `equal_split | revenue_proportional | manual` and a required
   manual reason when `manual` is selected.

## Phase 2 Task Map After Rulings

- Task 2.1 can be briefed after Stage 0 mechanical reconciliation and the
  isolated branch/worktree boundary are explicit.
- Task 2.2 remains blocked until the model-specific numeric-bound table is
  provided or recorded in the reconciled plan.
- Task 2.3 is not blocked by Task 0.4, but still waits for Stage 0 closeout and
  isolation.
- Task 2.4 should consume the fixed-fee ruling and stop presenting 정액 preview
  as owner-unconfirmed once the actual plan/docs patch is made.
- Task 2.5 remains the result/correction flow.
- Task 2.5b is now required for PPL entry surfaces.
- Task 2.6 and Task 2.7 must include the PPL-entry scope in the audit/acceptance
  boundary if Task 2.5b lands in Phase 2.

## Why This Is A Pipeline Artifact, Not A Ledger Plan Edit

The target repo is still divergent:

- `env -u GIT_INDEX_FILE git -C /Users/hyungkoookkim/evidence-ledger status --short --branch` -> `## main...origin/main [ahead 4, behind 6]`
- `env -u GIT_INDEX_FILE git -C /Users/hyungkoookkim/evidence-ledger rev-list --left-right --count HEAD...origin/main` -> `4	6`
- `env -u GIT_INDEX_FILE git -C /Users/hyungkoookkim/evidence-ledger diff --name-status` -> clean

So director2 records the authoritative planning delta here and does not add a
new ledger-main docs commit before the director/coordinator mechanical Stage 0
path settles the branch/reconcile policy.

## Evidence Commands

- `env -u GIT_INDEX_FILE .venv/bin/python scripts/ledger_start_guard.py --seat director2 --wave 2` -> PASS; active route `coordination/mailbox/sent/2026-07-07T17-12-12Z-coordinator-to-all-decision.md`.
- `env -u GIT_INDEX_FILE .venv/bin/python .agents/skills/four-seat-protocol/scripts/seat_status.py director2 --wave 2` -> unread `0 / ref-bus`; Pipeline HEAD `b1d6c4f coord(decision): record ledger task 0.4 rulings`; Wave 2 UNMET only because `docs/REMEDIATION-INVENTORY.md` is absent.
- `env -u GIT_INDEX_FILE .venv/bin/python scripts/protocol_capacity_board.py --wave 2` -> valid, no blocking issues.
- `env -u GIT_INDEX_FILE .venv/bin/python scripts/protocol_capacity_board.py --wave 2 --validate-route coordination/mailbox/sent/2026-07-07T17-12-12Z-coordinator-to-all-decision.md` -> route valid, no blocking issues.

## Next Trigger

Coordinator can treat the Task 0.4 planning delta for
`director2-ledger-runway-plan-reconcile` as recorded. The packet remains current
and blocked on whole-cycle Stage 0 closeout until the director mechanical PR
#9/reconcile outcome, an explicit isolated Phase 2 branch/worktree boundary,
and fresh operator/operator2 verification reports are present.

Cursor at send: 0
