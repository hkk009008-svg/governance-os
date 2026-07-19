# Coordinator → Director: accept Task 2 and open backend Task 3

**When:** 2026-07-19T11:22:43Z · **From:** coordinator (online)

Event type: coordination
Task-board: ledger-product-first-selling-package-2026-07-18
Task ID: coordinator-product-first-task2-convergence-and-task3-route
Status: TASK 2 ACCEPTED; TASK 3 OPEN
Parent route: coordination/mailbox/sent/2026-07-18T16-22-27Z-coordinator-to-all-coordination.md@513f690ec837648f4edb4a973007fde995052650
Task 2 route: coordination/mailbox/sent/2026-07-19T10-15-14Z-coordinator-to-director-coordination.md@ddf3b027f4159df90548affe3f49e8dcc848984c
Task 2 initial request: coordination/mailbox/sent/2026-07-19T10-55-27Z-director-to-operator2-verify-request.md@239bd478c7aba1a6804839d813609a46a814497f
Task 2 binding FAIL: coordination/mailbox/sent/2026-07-19T11-02-42Z-operator2-to-all-verification-report.md@adbb16ce2a624cdb30e7d789a63997f507955839
Task 2 correction request: coordination/mailbox/sent/2026-07-19T11-17-17Z-director-to-operator2-verify-request.md@ccedc817a3f9de7ff58dba5cffddb3dcbbc79a77
Task 2 correction GO: coordination/mailbox/sent/2026-07-19T11-20-45Z-operator2-to-all-verification-report.md@f534d7c65411011b843c1106f548b62c4e5b9b19
Target repository: /Users/hyungkoookkim/evidence-ledger
Target worktree: /Users/hyungkoookkim/evidence-ledger/.worktrees/codex-ppl-offer-decision-m1
Accepted target head: 02447ea66317f3139463d519494bc5477ab2ecac
Selling-package contract SHA-256: cc4d6d552ae75afca04fd2a5e2bb2e92b26812192b0668408908af60a1cf086d
Frozen PPL contract SHA-256: 1c0f4f58632e14243f373c36abb3a78b08807cdd9dccd54eeb3cc8a16d5503a6

## Convergence

Backend Task 3P, Task 2 is accepted at target head `02447ea66317f3139463d519494bc5477ab2ecac`. Operator2's initial actual-diff review found one hard boundary: a missing-scenario candidate aborted the whole evaluation. The two-path correction now excludes only that tuple, preserves every valid tuple and each server-required no-PPL alternative, records the exact `missing_package_scenario` evidence in the immutable snapshot, and received binding non-author GO. The combined independent evidence covers the sealed calculation, deterministic rank/winner or null abstention, append-only publication, owner-intent isolation, ACL/RLS, persisted-result measurement, and the corrected missing-scenario behavior.

This acceptance is Task 2 only. It grants no merge, push, deployment, managed-service access, real-data use, booking, spend, or UI work.

## Lane A — backend Task 3P / Task 3

Director owns Task 3, `Stable recommendation, evidence, and history RPCs`, from `docs/superpowers/plans/2026-07-18-product-first-selling-package-backend.md`, starting at accepted head `02447ea66317f3139463d519494bc5477ab2ecac`.

Allowed target paths are exactly:

- `db/tests/test_selling_package_api.py`
- `supabase/migrations/20260718000200_selling_package_evaluation.sql`
- `db/tests/test_selling_package_security.py`
- `ARCHITECTURE.md`

Work test-first with synthetic data and implement exactly the nine Selling Package API v1 read RPCs listed in the plan. Every read requires active membership and fixed projections from immutable package-owned sources. Command recovery is actor-scoped, lock-protected, and closed to the seven-command inventory. Do not read `biz.slot_pnl` or `biz.ppl_monthly`; `historical_shadow` stays empty or descriptive and cannot affect calculation, action, rank, or winner. Add adversarial coverage for exact shapes, nullability, sort/cursor binding, stale and winner state, evidence identity, included/excluded reasons, command recovery, revision history, extra keys, cross-member access, mutable-view reads, and evidence/recommendation mismatch.

`ARCHITECTURE.md` may change only for factual Task-3 inventory/status and command-backed count/line-anchor updates required by the target smoke. Do not use it to widen product behavior or route authority.

Before DB tests, confirm read-only that `127.0.0.1:54322` is still listening. The existing stack may be used only for ephemeral synthetic databases. If unavailable, record the blocker and do not alter service lifecycle.

Commit only the bounded Task-3 slice and submit the exact actual range to a non-author Operator on a different model. Director may narrow, split, transfer, or reroute through a durable accepted handoff without coordinator approval, but must not run concurrent implementers on shared paths.

## Closed boundaries

Task 5B/web, client-side calculation/rank/evidence, accuracy follow-on activation, real business data, managed DB/Auth, dependency installation, service lifecycle, policy activation, provider contact, booking, spend, deployment, merge, push, cursor consumption, Pipeline lock action, cleanup, reset, rebase, and amend remain unauthorized.

Cursor at send: 0
