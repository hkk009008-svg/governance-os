# Coordinator -> All: ledger Phase 2 Task 2.1 route

**When:** 2026-07-08T00:10:29Z · **From:** coordinator (online)

Event type: coordination
Task-board: `ledger-phase2-task21-2026-07-08`
Coordinator packet: `coord-ledger-phase2-task21-route`

## Outcome

Phase 2 routing starts now. PR #11 is merged, and the lawful Phase 2 base is
evidence-ledger `origin/main` at
`d3e87e64d3e1e4b1f4441e8bac0f69947df64e89`, not the previously divergent normal
evidence-ledger `main` checkout.

The first implementation packet is Task 2.1: client write path for entry forms
and revisions/audit foundations. The independent planning packet prepares the
Task 2.2 numeric-bound unblocker and preserves the Task 2.5b PPL entry-form
requirement from the owner rulings.

## Packet Ledger

Current Phase 2 packets:

- `coord-ledger-phase2-task21-route` -> coordinator active; tracks this cycle and eventual join/closeout.
- `director-ledger-phase2-task21-write-path` -> director active; implement Task 2.1 from `origin/main` `d3e87e64d3e1e4b1f4441e8bac0f69947df64e89`.
- `director2-ledger-phase2-bounds-plan-sync` -> director2 active; prepare the numeric-bound owner gate or cite why no owner input is needed; preserve Task 2.5b.
- `operator-ledger-phase2-task21-lanev` -> operator blocked until director sends the Task 2.1 outcome and verify-request.
- `operator2-ledger-phase2-base-preflight` -> operator2 active; read-only base/isolation verification before implementation proceeds too far.

Prior closed packet ids remain closed and are not reopened by this route:

- `coord-ledger-t14-align-join`
- `coord-ledger-t14-align-route`
- `director-ledger-publication-decision`
- `director2-ledger-next-brief`
- `operator-pipeline-tooling-verify`
- `operator2-ledger-main-verify`
- `coord-ledger-runway-stage0-route`
- `director-ledger-runway-stage0-owner-gates`
- `director2-ledger-runway-plan-reconcile`
- `operator-ledger-runway-stage0-verify`
- `operator2-ledger-runway-worktree-verify`
- `coord-ledger-runway-stage0-join`

## Seat Routes

Director:

- Work in evidence-ledger from a clean isolated Phase 2 branch/worktree based on `origin/main` `d3e87e64d3e1e4b1f4441e8bac0f69947df64e89`.
- Implement Task 2.1 only: ADR-007 entry RPC grants, SECURITY DEFINER boundary, auth stamping, and corrections-as-revisions semantics.
- Include focused DB tests and truth-doc updates required by changed behavior.
- Send a Pipeline mailbox outcome with commit/range, verification evidence, and operator verify-request.
- No push before operator GO.

Director2:

- Read the Phase 2 plan and Task 0.4 owner rulings.
- Prepare the smallest owner-gate or director brief needed for Task 2.2 numeric commission-rate bounds.
- Preserve the owner ruling that PPL entry forms ship during Phase 2 as Task 2.5b.
- Do not edit evidence-ledger product code in this packet.

Operator:

- Stand by for director's Task 2.1 outcome and verify-request.
- Then issue one Pipeline mailbox verification-report with GO, NITS, or FAIL for the named Task 2.1 diff.

Operator2:

- Run read-only Phase 2 base/isolation preflight against evidence-ledger.
- Verify `origin/main` at `d3e87e64d3e1e4b1f4441e8bac0f69947df64e89`, PR #11 merge state, normal-main divergence boundary, and absence of active presence/lock contradiction.
- Issue one Pipeline mailbox verification-report scoped only to base/isolation readiness.

## Evidence Commands

- `env -u GIT_INDEX_FILE .venv/bin/python scripts/ledger_start_guard.py --seat coordinator --wave 2` -> PASS; active route before this event was `coordination/mailbox/sent/2026-07-08T00-00-22Z-coordinator-to-all-coordination.md`.
- `env -u GIT_INDEX_FILE .venv/bin/python .agents/skills/four-seat-protocol/scripts/seat_status.py coordinator --wave 2 --smoke` -> Pipeline HEAD `7c168b8`; coordinator unread `0 / ref-bus`; smoke OK; Wave 2 inventory gate remains UNMET because `docs/REMEDIATION-INVENTORY.md` is absent.
- `env -u GIT_INDEX_FILE gh pr view 11 --repo hkk009008-svg/evidence-ledger --json number,state,mergeCommit,headRefOid,baseRefOid,url,mergedAt` -> PR #11 `MERGED` at `2026-07-08T00:06:51Z`; merge commit `d3e87e64d3e1e4b1f4441e8bac0f69947df64e89`.
- `env -u GIT_INDEX_FILE git -C /Users/hyungkoookkim/evidence-ledger fetch origin main codex/ledger-stage0-reconcile-2026-07-08` -> origin/main advanced `30f9ca4..d3e87e6`.
- `env -u GIT_INDEX_FILE git -C /Users/hyungkoookkim/evidence-ledger rev-parse origin/main` -> `d3e87e64d3e1e4b1f4441e8bac0f69947df64e89`.
- `env -u GIT_INDEX_FILE git -C /Users/hyungkoookkim/evidence-ledger log --oneline -3 origin/main` -> top commit `d3e87e6 Merge pull request #11 from hkk009008-svg/codex/ledger-stage0-reconcile-2026-07-08`.

## Side Effects Boundary

- No evidence-ledger product edit happened in this coordinator route.
- No force-push, lock claim, lock release, coordinator-mail consumption, paid API spend, pod spend, or production generation happened in this coordinator route.
- Pipeline remains the governance kernel; evidence-ledger remains the target repo.

Join condition: Phase 2 Task 2.1 can join only after director sends the implementation outcome, operator returns GO/NITS/FAIL for that Task 2.1 diff, director2 closes or defers the Task 2.2 numeric-bound unblocker with evidence, operator2 returns GO/NITS/FAIL for base/isolation readiness, and the coordinator records a fresh capacity-board-valid closeout.

Cursor at send: 0

## Exact Next Trigger

Director runs Task 2.1 from evidence-ledger `origin/main` `d3e87e64d3e1e4b1f4441e8bac0f69947df64e89`; director2 prepares the Task 2.2 numeric-bound unblocker; operator2 runs the read-only base/isolation preflight; operator waits for director's Task 2.1 verify-request.
