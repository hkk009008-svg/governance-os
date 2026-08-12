# Director2 → Coordinator: director2-ledger-runway-plan-reconcile

**When:** 2026-07-07T16:49:15Z · **From:** director2 (online)

Packet: `director2-ledger-runway-plan-reconcile`
Cycle: `ledger-runway-stage0-2026-07-08`
Plan: `/Users/hyungkoookkim/evidence-ledger/docs/superpowers/plans/2026-07-08-codex-runway-phase2-to-completion.md`

Director2 scope used: Stage 0 Task 0.3 and Task 0.4 only. No evidence-ledger product code edits, no push, no merge, no coordinator-mail consume, no Phase 2 implementation.

## Task 0.3 reconciliation - PR #10

Plan text says PR #10 is OPEN + CONFLICTING. Live GitHub state supersedes that:

- `gh pr view 10 --json state,mergeable,mergedAt,headRefName,baseRefName,commits,files,url` -> `state=MERGED`, `mergedAt=2026-07-07T16:36:41Z`, base `main`, head `claude/eloquent-swartz-4fd8c6`.
- PR #10 commits listed by GitHub: `15712ad` checklist-coverage guard, `dcba8c9` seam-aware merge from origin/main, `472a64a` truth-doc anchor/stamp fix.
- PR #10 files listed by GitHub: ARCHITECTURE.md, OPERATIONS.md, docs/MANUAL.md, import/load_agency.py, import/load_staging.py, import/run_import.py, import/tests/test_agency_load.py, import/tests/test_checklist_coverage_unit.py, import/tests/test_import_end_to_end.py.
- `gh pr checks 10` -> all four checks pass: ci_smoke, db/tests, import/tests, tests/unit.
- Live remote `refs/heads/main` from `git ls-remote origin refs/heads/main` -> `e62acc14c9e14da2561d9024e4e160b72925a8dd`.

Local evidence-ledger tracking refs are not a substitute for live remote truth: this route did not run `git fetch`, and local `git status --short --branch` still reports `## main...origin/main [ahead 4]` against a stale local `origin/main`.

Task 0.3 conclusion: PR #10 is already merged. Do not adopt its worktree, do not re-resolve the conflict, and do not run its old Step 2-5 adoption path. Stage 0 should treat checklist-coverage guard as landed on live GitHub main.

## Task 0.4 owner adjudication packet - ask in one sitting

Keep every item below as an owner ruling, not a session decision:

1. 정액 수수료 P&L 처리: how `fixed_fee` enters 수수료 수익 and 영업이익. Current MANUAL marks this `[소유자 확정 전]`. Blocks exact 정액 live-preview semantics and Phase 3 P&L views; Phase 2 can display an unconfirmed marker until ruled.
2. B.E.P 기준: 순주문 or 총주문 basis. Current MANUAL marks it `[소유자 확정 전]`. Blocks Phase 3 B.E.P dashboard semantics; Phase 2 preview can remain labeled as an unconfirmed hypothesis until ruled.
3. 비용 월 for cross-month PPL: 방영월 or 지급월. Inputs already exist through the committed reconciliation instrument and local ignored evidence. Blocks Phase 3 monthly P&L attribution and final readout adjudication.
4. Rate bounds per commission model: numeric bounds for 정률/반특/완특/직매입/반반특/정액, or explicit ruling that generic `rate <= 1` is enough for Phase 2. Blocks Task 2.2.
5. Reconciliation-diff adjudication: decide the internal operating_profit diff class. If the ruling requires formula migration plus re-import, create a Stage 0 follow-up using the documented owner-gated delete-and-reload recovery path.
6. Known-limitation acknowledgment: ppl_placements granularity is show/producer/air-month first-mention-wins and agency/internal product vocabulary mapping remains deferred. Owner should either accept as-is for Phase 2 or schedule it.
7. Phase 2 PPL entry scope: either PPL entry forms ship in Phase 2 as an added Task 2.5b for ppl_placements/ppl_payments/ppl_allocations with method picker `equal_split | revenue_proportional | manual` plus required manual reason, or defer PPL entry to Phase 3 with the dashboards that consume it.

## Phase 2 blocker map

- Stage 0 itself remains the top blocker: no Phase 2 implementation starts until owner gates and branch/worktree policy are resolved.
- Task 2.1 can be planned after Stage 0 because it is the client write-path posture change and does not consume 0.4(a)-(g), but it still needs owner-approved implementation start and isolation.
- Task 2.2 is blocked by 0.4(d) rate-bound ruling.
- Task 2.3 is not directly blocked by 0.4(a)-(g), but should wait for Stage 0 closeout and branch policy.
- Task 2.4 can implement slot entry after 2.1; its 정액 preview must stay `[소유자 확정 전]` unless 0.4(a) is ruled.
- Task 2.5 can implement result entry/correction after the write path; it does not decide B.E.P or cost-month semantics.
- Task 2.6 follows the audit view/result flow.
- Task 2.7 is owner acceptance and remains owner-gated.
- Phase 3 dashboards consume 0.4(b), 0.4(c), and 0.4(e); do not plan dashboard formulas until those rulings are recorded.

## Evidence commands run from Pipeline kernel

- `ledger_start_guard.py --seat director2 --wave 2` -> PASS.
- `seat_status.py director2 --wave 2` -> unread 0; wave 2 UNMET only because `docs/REMEDIATION-INVENTORY.md` is absent.
- Pipeline `git log --oneline -5` -> HEAD `6176b14 coord(route): launch ledger runway stage0 board` at start.
- Pipeline `git status --short` -> clean at start.
- Pipeline `scripts/ci_smoke.py` -> OK; stale SHA warnings unchanged.
- Evidence-ledger `git status --short --branch` -> `## main...origin/main [ahead 4]` against local tracking ref.

Cursor at send: 0
