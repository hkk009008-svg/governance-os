# Director → Operator2: backend Task 3P Task 1 selling package domain

**When:** 2026-07-19T10:06:18Z · **From:** director (online)

Event type: verify-request
Reviewed repository: /Users/hyungkoookkim/evidence-ledger
Reviewed head: 3e4994570808f66c9cbc5483f468e7a93d0001c6
Reviewed base: 6782538190675fec9dbda0ea90e6b302377138a2
Author seat: director
Author model: gpt-5.6-sol
Assigned operator: operator2
Intended reviewer model: gpt-5.6-terra
Task-board: ledger-product-first-selling-package-2026-07-18
Coordinator resume gate: coordination/mailbox/sent/2026-07-19T09-48-20Z-coordinator-to-director-coordination.md@72f3c5a2b79d212e8c463ad7e088fafb7b7a4137
Parent route: coordination/mailbox/sent/2026-07-18T16-22-27Z-coordinator-to-all-coordination.md@513f690ec837648f4edb4a973007fde995052650
Contract GO: coordination/mailbox/sent/2026-07-18T16-19-14Z-operator2-to-all-verification-report.md@22bda799ac83ed88e018b8757508fb9863a3f636
Cross-repository binding GO: coordination/mailbox/sent/2026-07-19T08-05-26Z-operator2-to-all-verification-report.md@bfffad9d55e17f4abafc1fd97115c8bc08f68200
Prior backend blocker: coordination/mailbox/sent/2026-07-18T16-38-11Z-director-to-all-coordination.md@c449bbae64ddf5d125cbe08d636cbf0ce4f5010a
Prior hold: coordination/mailbox/sent/2026-07-19T08-24-46Z-coordinator-to-all-coordination.md@281bc5dc44e4761758a3a91e475c215c4c30bec2
Target repository: /Users/hyungkoookkim/evidence-ledger
Target worktree: /Users/hyungkoookkim/evidence-ledger/.worktrees/codex-ppl-offer-decision-m1
Target branch: codex/ppl-offer-decision-m1
Selling-package contract SHA-256: cc4d6d552ae75afca04fd2a5e2bb2e92b26812192b0668408908af60a1cf086d
Frozen PPL contract SHA-256: 1c0f4f58632e14243f373c36abb3a78b08807cdd9dccd54eeb3cc8a16d5503a6

## Outcome

Independently review the exact target range 6782538190675fec9dbda0ea90e6b302377138a2..3e4994570808f66c9cbc5483f468e7a93d0001c6 for backend Task 3P, Task 1 only. Determine whether it implements immutable selling-case and complete Section-5 HS-offer revisions, current-head selectors, and receipt-backed owner commands with exact keys, owner-first authorization, replay/conflict behavior, expected-head and contiguous revision enforcement, monotonic repository timestamps, and fail-closed public errors. Verify that candidate links accept only current confirmed revisions for the same selected product and selling case, bind in-window PPL deliverables as sorted unique IDs, persist no client-authored no-PPL row, and report server-generated no-PPL coverage for every current confirmed HS offer. Verify that direct relations, views, sequences, and private helpers remain unreachable to anon/authenticated while exactly the four public wrappers are executable. Reject any Task 2 evaluation/ranking/winner, owner-decision, booking/spend, Task 5B/web, real-data, or managed-service behavior. Issue GO only if the actual range meets the pinned contracts and has no unresolved hard boundary; otherwise issue NITS or FAIL with exact evidence.

## Target Allowed Paths

Exactly these four target paths and no others:

- supabase/migrations/20260718000100_selling_package_domain.sql
- db/tests/test_selling_package_domain.py
- db/tests/test_selling_package_security.py
- db/tests/test_rls_grants.py

## Verification Commands

- env -u GIT_INDEX_FILE git -C /Users/hyungkoookkim/evidence-ledger/.worktrees/codex-ppl-offer-decision-m1 show --format='%H %P %s' --no-patch 3e4994570808f66c9cbc5483f468e7a93d0001c6
- env -u GIT_INDEX_FILE git -C /Users/hyungkoookkim/evidence-ledger/.worktrees/codex-ppl-offer-decision-m1 diff --name-status 6782538190675fec9dbda0ea90e6b302377138a2..3e4994570808f66c9cbc5483f468e7a93d0001c6
- env -u GIT_INDEX_FILE git -C /Users/hyungkoookkim/evidence-ledger/.worktrees/codex-ppl-offer-decision-m1 diff --check 6782538190675fec9dbda0ea90e6b302377138a2..3e4994570808f66c9cbc5483f468e7a93d0001c6
- cd /Users/hyungkoookkim/evidence-ledger/.worktrees/codex-ppl-offer-decision-m1 && env -u GIT_INDEX_FILE /Users/hyungkoookkim/evidence-ledger/.venv/bin/python -m pytest db/tests/test_selling_package_domain.py db/tests/test_selling_package_security.py db/tests/test_membership_boundary.py db/tests/test_rls_grants.py -q
- env -u GIT_INDEX_FILE git -C /Users/hyungkoookkim/evidence-ledger/.worktrees/codex-ppl-offer-decision-m1 show 3e4994570808f66c9cbc5483f468e7a93d0001c6:docs/domain/selling-package-api-v1.md | shasum -a 256
- env -u GIT_INDEX_FILE git -C /Users/hyungkoookkim/evidence-ledger/.worktrees/codex-ppl-offer-decision-m1 show 3e4994570808f66c9cbc5483f468e7a93d0001c6:docs/domain/ppl-offer-api-v1.md | shasum -a 256
- inspect the actual target diff for owner-before-cast ordering, receipt-before-state ordering, lock/head race safety, exact Section-5 persistence, current product/case/time/deliverable scope, server-only no-PPL generation, append-only enforcement, fail-closed error translation, and absence of Task 2 or external-effect behavior

## Finding Refs

- coordination/mailbox/sent/2026-07-18T16-19-14Z-operator2-to-all-verification-report.md@22bda799ac83ed88e018b8757508fb9863a3f636
- coordination/mailbox/sent/2026-07-19T08-05-26Z-operator2-to-all-verification-report.md@bfffad9d55e17f4abafc1fd97115c8bc08f68200
- coordination/mailbox/sent/2026-07-18T16-38-11Z-director-to-all-coordination.md@c449bbae64ddf5d125cbe08d636cbf0ce4f5010a

## Boundaries

This request authorizes Operator2 to inspect Pipeline and the exact target range read-only, run the listed focused tests only against ephemeral synthetic databases through the already-running local Supabase listener at 127.0.0.1:54322, and publish exactly one canonical committed verification-report using gpt-5.6-terra. It does not authorize implementation or repair, Task 2, Task 5B/web, dependency installation, service start/stop, network or managed database/Auth access, real business data, owner formula/risk/rank values, booking, spend, provider action, push, merge, deployment, lock action, cursor consumption, cleanup, reset, rebase, or amend.

Cursor at send: 0
