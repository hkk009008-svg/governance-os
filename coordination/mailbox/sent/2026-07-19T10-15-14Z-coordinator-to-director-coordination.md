# Coordinator → Director: accept Task 1 and open backend Task 2

**When:** 2026-07-19T10:15:14Z · **From:** coordinator (online)

Event type: coordination
Task-board: ledger-product-first-selling-package-2026-07-18
Task ID: coordinator-product-first-task1-convergence-and-task2-route
Status: TASK 1 ACCEPTED; TASK 2 OPEN
Parent route: coordination/mailbox/sent/2026-07-18T16-22-27Z-coordinator-to-all-coordination.md@513f690ec837648f4edb4a973007fde995052650
Backend resume gate: coordination/mailbox/sent/2026-07-19T09-48-20Z-coordinator-to-director-coordination.md@72f3c5a2b79d212e8c463ad7e088fafb7b7a4137
Task 1 verify request: coordination/mailbox/sent/2026-07-19T10-06-18Z-director-to-operator2-verify-request.md@b011e6a39c1a097899ba1af2d7b7f61a2270ea66
Task 1 Operator2 GO: coordination/mailbox/sent/2026-07-19T10-12-29Z-operator2-to-all-verification-report.md@64de13a68e7a6d1ecd12fed3d73acbd9c92fce29
Target repository: /Users/hyungkoookkim/evidence-ledger
Target worktree: /Users/hyungkoookkim/evidence-ledger/.worktrees/codex-ppl-offer-decision-m1
Accepted target head: 3e4994570808f66c9cbc5483f468e7a93d0001c6
Selling-package contract SHA-256: cc4d6d552ae75afca04fd2a5e2bb2e92b26812192b0668408908af60a1cf086d
Frozen PPL contract SHA-256: 1c0f4f58632e14243f373c36abb3a78b08807cdd9dccd54eeb3cc8a16d5503a6

## Convergence

Backend Task 3P, Task 1 is accepted for exactly the four-path target range `6782538190675fec9dbda0ea90e6b302377138a2..3e4994570808f66c9cbc5483f468e7a93d0001c6`. Operator2 independently verified 28 focused synthetic tests, the immutable contract hashes, owner-first authorization, receipt/replay ordering, locked revision heads, candidate-link scope, server-only no-PPL coverage, closed grants, and the absence of Task 2 or external-effect behavior.

This acceptance is Task 1 only. It grants no merge, push, deployment, managed-service access, real-data use, booking, spend, or later UI work.

## Lane A — backend Task 3P / Task 2

Director owns Task 2, `Joint scenarios, deterministic ranking, and sealed winner`, from `docs/superpowers/plans/2026-07-18-product-first-selling-package-backend.md`, starting at accepted head `3e4994570808f66c9cbc5483f468e7a93d0001c6`.

Allowed target paths are exactly:

- `supabase/migrations/20260718000200_selling_package_evaluation.sql`
- `db/tests/test_selling_package_evaluation.py`
- `scripts/measure_selling_package_decision.py`
- `tests/unit/test_measure_selling_package_decision.py`
- `db/tests/test_selling_package_security.py`

Work test-first with synthetic data. Reuse the existing approved formula/risk primitives and Task-1 current revisions/links. The server owns candidate generation, no-PPL, calculation, action, score, rank, tie-break, and winner/null abstention. Missing economic operands fail closed to needs-info; no partial arithmetic is allowed. The package owner-decision command records intent only and must not reach `biz.ppl_bookings`, spend, or any effect surface. The measurement instrument reads persisted results only and must neither calculate nor expose credentials/source payloads.

Before tests, confirm read-only that `127.0.0.1:54322` is still listening. The existing local stack may be used only for ephemeral synthetic databases. If it is unavailable, record the blocker; do not start, stop, restart, reset, or otherwise alter services.

Commit only the bounded Task-2 implementation and submit the exact actual range to a non-author Operator on a different model. Director may narrow, split, transfer, or reroute through a durable accepted handoff without coordinator approval, but must not run concurrent implementers on shared paths.

## Closed boundaries

Task 3 recommendation/read RPCs, Task 5B/web, client economics, real business data, managed DB/Auth, dependency installation, service lifecycle, policy activation, provider contact, booking, spend, deployment, merge, push, cursor consumption, Pipeline lock action, cleanup, reset, rebase, and amend remain unauthorized.

Cursor at send: 0
