# Coordinator → All: correct pre-existing selling-package writer lock before Foundation Task 1

**When:** 2026-07-19T20:02:36Z · **From:** coordinator (online)

# Coordinator → All: correct pre-existing selling-package writer lock before Foundation Task 1

Event type: coordination
Task-board: ledger-one-user-owner-policy-2026-07-20
Task ID: coordinator-selling-package-writer-lock-prerequisite
Status: BASELINE SECURITY DEFECT CONFIRMED; ONE-PATH CORRECTION OPEN; FOUNDATION TASK 1 HELD
Supersedes active route: coordination/mailbox/sent/2026-07-19T19-53-49Z-coordinator-to-all-coordination.md@859961fe22342ece0b8bd7908580a070af651663
Authorization source: user-task:continue-owner-gate-foundation-2026-07-20
Target repository: /Users/hyungkoookkim/evidence-ledger
Target worktree: /Users/hyungkoookkim/evidence-ledger/.worktrees/codex-ppl-offer-decision-m1
Immutable target parent: 41d9f1d846d6e0928b520573094ae59846114df5
Finding ref: director-task:019f7363-57c8-7ca1-9ee4-05651fdea24a/turn:019f7bf1-fa40-75f0-841b-c2c71661aa9b
Origin commit: 935a9f1f

## Confirmed prerequisite defect

The local database prerequisite is now healthy and port 54322 is listening. The exact 40-test Foundation baseline executes through migrations and RPC setup but reports 39 passed and one failed.

The failing test is `db/tests/test_ppl_offer_cutoff.py::test_every_participating_writer_is_discovered_and_lock_ordered`. A focused rerun with local variables proved the failing catalog signature is `decision._record_selling_package_manual_scenarios(jsonb,bigint,uuid)`. The function was introduced in `supabase/migrations/20260718000200_selling_package_evaluation.sql` by `935a9f1f`; it directly inserts into participating timestamped selling-package scenario relations without first calling `app.ppl_reference_snapshot_lock()`. The test raises `KeyError: 'global_lock'` at the private-direct-writer branch. Sibling private writers, including `decision._record_ppl_manual_scenarios`, take the global lock immediately on entry.

This is a pre-existing global snapshot-ordering defect outside Foundation Task 1. Foundation Task 1 remains held until this correction receives committed non-author GO. After GO, coordinator will rebind the Foundation Task 1 immutable parent to the accepted correction commit.

## Open correction slice

Director owns one test-first correction from immutable parent `41d9f1d846d6e0928b520573094ae59846114df5`.

The only allowed target path is:

- `supabase/migrations/20260718000200_selling_package_evaluation.sql`

Use the existing failing lock-order test as the executable RED. Add the repository global snapshot lock as the first stateful operation in `decision._record_selling_package_manual_scenarios(jsonb,bigint,uuid)`, before participant reads, domain locks, or inserts. Do not change payload, quorum, calculation, recommendation, timestamp, or public API semantics.

Verify in this order:

1. Reproduce the exact focused RED at the immutable parent.
2. Run the focused failing test and prove it passes after the correction.
3. Run `db/tests/test_selling_package_security.py`.
4. Run the exact 40-test selector: `db/tests/test_ppl_decision_policy.py db/tests/test_rls_grants.py db/tests/test_ppl_offer_cutoff.py -q`.
5. Inspect the actual diff and commit only the one allowed path.

Director then submits the immutable parent-to-head range and finding ref to non-author Operator2 on a different model. Operator2 independently checks the actual diff, lock-before-read/write ordering, focused regression, selling-package security, and exact 40-test selector, then returns GO, NITS, or FAIL.

No Foundation Task 1 file may change in this correction.

No new test suppression, xfail, skip, parser weakening, or fixture workaround is authorized.

No private owner value collection is authorized.

No policy creation, approval, format ruling, or activation is authorized.

No service lifecycle or container mutation is authorized.

No managed database, real-data, deployment, booking, provider, or spend action is authorized.

No evidence-ledger merge is authorized.

No evidence-ledger push is authorized.

No Pipeline push is authorized.

No cursor consumption, lock action, cleanup, reset, rebase, or amend is authorized.

## Exact next trigger

Director reads this complete committed route, reproduces the focused RED, implements only the one-path global-lock correction, verifies the exact scopes above, commits the actual correction, and sends the immutable range to Operator2 for independent review.

Cursor at send: 0
