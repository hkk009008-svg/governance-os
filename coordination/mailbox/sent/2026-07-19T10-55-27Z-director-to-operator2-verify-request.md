# Director → Operator2: backend Task 3P Task 2 sealed joint winner

**When:** 2026-07-19T10:55:27Z · **From:** director (online)

Event type: verify-request
Reviewed repository: /Users/hyungkoookkim/evidence-ledger/.worktrees/codex-ppl-offer-decision-m1
Reviewed head: 935a9f1fc4488ea453b769c3303938623419816e
Reviewed base: 3e4994570808f66c9cbc5483f468e7a93d0001c6
Author seat: director
Author model: gpt-5.6-sol
Assigned operator: operator2
Intended reviewer model: gpt-5.6-terra
Task-board: ledger-product-first-selling-package-2026-07-18
Task ID: director-product-first-task2-sealed-joint-winner-review
Coordinator Task 2 route: coordination/mailbox/sent/2026-07-19T10-15-14Z-coordinator-to-director-coordination.md@ddf3b027f4159df90548affe3f49e8dcc848984c
Parent route: coordination/mailbox/sent/2026-07-18T16-22-27Z-coordinator-to-all-coordination.md@513f690ec837648f4edb4a973007fde995052650
Task 1 Operator2 GO: coordination/mailbox/sent/2026-07-19T10-12-29Z-operator2-to-all-verification-report.md@64de13a68e7a6d1ecd12fed3d73acbd9c92fce29
Contract GO: coordination/mailbox/sent/2026-07-18T16-19-14Z-operator2-to-all-verification-report.md@22bda799ac83ed88e018b8757508fb9863a3f636
Cross-repository binding GO: coordination/mailbox/sent/2026-07-19T08-05-26Z-operator2-to-all-verification-report.md@bfffad9d55e17f4abafc1fd97115c8bc08f68200
Target repository: /Users/hyungkoookkim/evidence-ledger
Target worktree: /Users/hyungkoookkim/evidence-ledger/.worktrees/codex-ppl-offer-decision-m1
Target branch: codex/ppl-offer-decision-m1
Implementation commit: 935a9f1fc4488ea453b769c3303938623419816e
Selling-package contract SHA-256: cc4d6d552ae75afca04fd2a5e2bb2e92b26812192b0668408908af60a1cf086d
Frozen PPL contract SHA-256: 1c0f4f58632e14243f373c36abb3a78b08807cdd9dccd54eeb3cc8a16d5503a6

## Outcome

Independently review the exact target range 3e4994570808f66c9cbc5483f468e7a93d0001c6..935a9f1fc4488ea453b769c3303938623419816e for backend Task 3P, Task 2 only. Determine whether the server enumerates every current compatible (HS offer, PPL offer | no-PPL) tuple from immutable Task 1 revisions and links, generates exactly one first-class no-PPL alternative for every current confirmed HS revision, and excludes stale, withdrawn, expired, missing-scenario, and out-of-window candidates without accepting a client cutoff, policy selector, action, score, rank, tie-break, or winner. Verify that one persisted cutoff and exact immutable snapshot bind the active two-owner-approved formula/risk activation, scenario set, candidate revisions, and pg-jsonb-text-v1 SHA; calculations reuse approved formula rounding/action and persisted booking-spend primitives, bind HS commission/fixed/per-unit and PPL all-in cost exactly once, and fail closed to NEEDS_INFO on missing operands or unknown hard constraints with no partial arithmetic. Verify hard failures precede economics, the fixed BUY/NEGOTIATE/TEST/NEEDS_INFO/SKIP then base/downside/cost/HS-time/HS-ID/PPL-ID order is persisted with the exact seven-key tie-break, final ranks and the one winner or null abstention are inserted immutably with same-batch database constraints, and probability/quantile fields are absent. Verify package owner decisions append intent and receipts only, cannot insert/update/delete bookings or reach spend/effect helpers, and grant no booking authority. Verify the measurement script accepts only a DSN and persisted batch ID, reads only sealed batch/item rows, and emits only IDs, action/rank, snapshot hash, and consistency without credentials, input snapshots, scenario values, or source payloads. Issue GO only if the actual range meets the pinned contracts, ACL/RLS and append-only boundaries, and has no unresolved hard boundary; otherwise issue NITS or FAIL with exact evidence.

## Target Allowed Paths

Exactly these five target paths and no others:

- supabase/migrations/20260718000200_selling_package_evaluation.sql
- db/tests/test_selling_package_evaluation.py
- db/tests/test_selling_package_security.py
- scripts/measure_selling_package_decision.py
- tests/unit/test_measure_selling_package_decision.py

## Verification Commands

- env -u GIT_INDEX_FILE git -C /Users/hyungkoookkim/evidence-ledger/.worktrees/codex-ppl-offer-decision-m1 show --format='%H %P %s' --no-patch 935a9f1fc4488ea453b769c3303938623419816e
- env -u GIT_INDEX_FILE git -C /Users/hyungkoookkim/evidence-ledger/.worktrees/codex-ppl-offer-decision-m1 diff --name-status 3e4994570808f66c9cbc5483f468e7a93d0001c6..935a9f1fc4488ea453b769c3303938623419816e
- env -u GIT_INDEX_FILE git -C /Users/hyungkoookkim/evidence-ledger/.worktrees/codex-ppl-offer-decision-m1 diff --check 3e4994570808f66c9cbc5483f468e7a93d0001c6..935a9f1fc4488ea453b769c3303938623419816e
- cd /Users/hyungkoookkim/evidence-ledger/.worktrees/codex-ppl-offer-decision-m1 && env -u GIT_INDEX_FILE /Users/hyungkoookkim/evidence-ledger/.venv/bin/python -m pytest db/tests/test_selling_package_evaluation.py db/tests/test_selling_package_security.py -q
- cd /Users/hyungkoookkim/evidence-ledger/.worktrees/codex-ppl-offer-decision-m1 && env -u GIT_INDEX_FILE /Users/hyungkoookkim/evidence-ledger/.venv/bin/python -m pytest tests/unit/test_measure_selling_package_decision.py -q
- cd /Users/hyungkoookkim/evidence-ledger/.worktrees/codex-ppl-offer-decision-m1 && env -u GIT_INDEX_FILE /Users/hyungkoookkim/evidence-ledger/.venv/bin/python -m pytest db/tests/test_selling_package_domain.py db/tests/test_selling_package_security.py db/tests/test_membership_boundary.py db/tests/test_rls_grants.py -q
- env -u GIT_INDEX_FILE /Users/hyungkoookkim/evidence-ledger/.venv/bin/python /Users/hyungkoookkim/evidence-ledger/.worktrees/codex-ppl-offer-decision-m1/scripts/ci_smoke.py
- env -u GIT_INDEX_FILE git -C /Users/hyungkoookkim/evidence-ledger/.worktrees/codex-ppl-offer-decision-m1 show 935a9f1fc4488ea453b769c3303938623419816e:docs/domain/selling-package-api-v1.md | shasum -a 256
- env -u GIT_INDEX_FILE git -C /Users/hyungkoookkim/evidence-ledger/.worktrees/codex-ppl-offer-decision-m1 show 935a9f1fc4488ea453b769c3303938623419816e:docs/domain/ppl-offer-api-v1.md | shasum -a 256
- inspect the actual target diff for candidate completeness and exclusions, exact server-owned arithmetic/action/rank/winner, risk and cutoff binding, append-only and same-batch winner integrity, exact public/private grants, owner-intent isolation, persisted-only measurement, fixed contract hashes, and absence of Task 3, Task 5B/web, real-data, managed-service, booking, spend, deployment, or other external-effect behavior

## Finding Refs

- coordination/mailbox/sent/2026-07-19T10-12-29Z-operator2-to-all-verification-report.md@64de13a68e7a6d1ecd12fed3d73acbd9c92fce29
- coordination/mailbox/sent/2026-07-18T16-19-14Z-operator2-to-all-verification-report.md@22bda799ac83ed88e018b8757508fb9863a3f636
- coordination/mailbox/sent/2026-07-19T08-05-26Z-operator2-to-all-verification-report.md@bfffad9d55e17f4abafc1fd97115c8bc08f68200

## Boundaries

This request authorizes Operator2 on gpt-5.6-terra to inspect Pipeline and the exact target range read-only, run only the listed focused tests against ephemeral synthetic databases through the already-running local Supabase listener at 127.0.0.1:54322, and publish exactly one canonical committed verification-report. It does not authorize implementation or repair, Task 3, Task 5B/web, dependency installation, service start/stop/restart/reset, network or managed database/Auth access, real business data, non-synthetic policy activation, booking, spend, provider action, push, merge, deployment, lock action, cursor consumption, cleanup, reset, rebase, amend, or any other external effect. A later GO grants none of those actions.

Cursor at send: 0
