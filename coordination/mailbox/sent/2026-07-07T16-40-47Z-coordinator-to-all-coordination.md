# Coordinator → All: ledger runway Stage 0 task-board

**When:** 2026-07-07T16:40:47Z · **From:** coordinator (online)

Task-board: `ledger-runway-stage0-2026-07-08`

Plan source: `/Users/hyungkoookkim/evidence-ledger/docs/superpowers/plans/2026-07-08-codex-runway-phase2-to-completion.md`

This route is Stage 0 reconciliation and owner-gate preparation only. Do not start Phase 2 implementation yet.

Coordinator basis from fresh commands:
- Pipeline guard: `scripts/ledger_start_guard.py --seat coordinator --wave 2` PASS from `/Users/hyungkoookkim/Pipeline`.
- Pipeline coordinator status: `main` at `121a67b fix(codex): enforce ledger seat start guard`, `9 ahead / 0 behind`; wave 2 gate UNMET only because `docs/REMEDIATION-INVENTORY.md` is absent.
- Pipeline smoke: `scripts/ci_smoke.py` OK; stale-SHA warnings unchanged.
- Evidence-ledger smoke: `scripts/ci_smoke.py` OK.
- Evidence-ledger git: `main...origin/main` is `4 0`; `origin/main..main` is `987ce61`, `5dedf86`, `b84dba9`, `8fbbd38`.
- Evidence-ledger Stage 0 plan mismatch: Task 0.1 expects exactly `987ce61`, so the live four-commit ahead state must be reconciled before any push/publication action.
- PR #9: OPEN, docs-only two files, checks pass, mergeable UNKNOWN.
- PR #10: MERGED; the plan's OPEN+CONFLICTING text is stale.
- Evidence-ledger isolation: normal `main` checkout, not a linked worktree; `.worktrees` is not ignored. Implementation must not start on `main` without owner-approved isolation.
- Evidence-ledger presence/locks: only a tombstone presence file was found; no lock files were found.

Required startup for every seat:

```bash
cd /Users/hyungkoookkim/Pipeline
env -u GIT_INDEX_FILE .venv/bin/python scripts/ledger_start_guard.py --seat <seat> --wave 2
env -u GIT_INDEX_FILE .venv/bin/python .agents/skills/four-seat-protocol/scripts/seat_status.py <seat> --wave 2
```

Seat assignments:
- coordinator owns packet `coord-ledger-runway-stage0-route`. Maintain this board, reconcile reports, and do not edit evidence-ledger product files.
- director owns packet `director-ledger-runway-stage0-owner-gates`. Reconcile Task 0.1 and Task 0.2 against live state and prepare the owner-facing publication/PR #9 gate. No push or merge.
- director2 owns packet `director2-ledger-runway-plan-reconcile`. Reconcile Task 0.3 against live PR #10 MERGED state and prepare the batched Task 0.4 owner adjudication question set. Do not decide business semantics.
- operator owns packet `operator-ledger-runway-stage0-verify`. Independently verify current Stage 0 readiness and report GO/NITS/FAIL to Pipeline mailbox.
- operator2 owns packet `operator2-ledger-runway-worktree-verify`. Independently verify isolation/worktree readiness and report GO/NITS/FAIL to Pipeline mailbox.

Prior-cycle packet closeout IDs: `coord-ledger-t14-align-join`, `coord-ledger-t14-align-route`, `director-ledger-publication-decision`, `director2-ledger-next-brief`, `operator-pipeline-tooling-verify`, `operator2-ledger-main-verify`.

Side effects boundary:
- No push, force-push, PR merge, lock claim, paid API spend, pod spend, or production generation is authorized by this route.
- Do not consume coordinator mail.
- All cross-repo git, pytest, and verification commands must use `env -u GIT_INDEX_FILE`.
- No Phase 2 implementation starts until owner gates are answered and the worktree/branch policy is resolved.

Join condition: coordinator may advance past Stage 0 only after director records the owner gate packet, director2 records the plan-reconciliation/adjudication packet, operator and operator2 emit verification-report GO/NITS/FAIL, and the owner resolves the required gates or explicitly narrows the route.

Cursor at send: 0
