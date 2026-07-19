# Coordinator → All: complete selling-package writer lock prerequisite

**When:** 2026-07-19T20:13:31Z · **From:** coordinator (online)

Task-board: ledger-one-user-owner-policy-2026-07-20
Task ID: coordinator-selling-package-writer-lock-complete-prerequisite
Status: CASCADED SECURITY DEFECTS CONFIRMED; TWO-PATH CORRECTION OPEN; FOUNDATION TASK 1 HELD
Supersedes active route: coordination/mailbox/sent/2026-07-19T20-02-36Z-coordinator-to-all-coordination.md@bf0d0ffc3a64b77647f15bd35d4a47d81d0695b9
Authorization source: user-task:continue-owner-gate-foundation-2026-07-20
Target repository: /Users/hyungkoookkim/evidence-ledger
Target worktree: /Users/hyungkoookkim/evidence-ledger/.worktrees/codex-ppl-offer-decision-m1
Immutable target parent: 41d9f1d846d6e0928b520573094ae59846114df5
Finding refs: director-task:019f7363-57c8-7ca1-9ee4-05651fdea24a/turn:019f7bf1-fa40-75f0-841b-c2c71661aa9b, director-task:019f7363-57c8-7ca1-9ee4-05651fdea24a/turn:019f7bfa-009d-7823-9a7a-149243fd4993
Origin commits: 935a9f1f, 02447ea

## Confirmed cascade and preserved WIP

The prior one-path correction added `app.ppl_reference_snapshot_lock()` as the first stateful operation in `decision._record_selling_package_manual_scenarios(jsonb,bigint,uuid)`. The catalog-wide lock-order test then advanced past that writer and exposed other pre-existing unlocked private direct writers. Exact `--showlocals` evidence named `biz._record_selling_case_revision(jsonb,bigint,uuid,boolean)` and `decision._record_selling_package_owner_decision(jsonb,bigint,uuid)` on separate runs. The failure order is set-order dependent, so serially routing only the next displayed signature would be incomplete.

Read-only source inventory of the two selling-package migrations identifies six private functions that directly insert participating state. None had the required entry lock at immutable parent `41d9f1d846d6e0928b520573094ae59846114df5`. The catalog-wide test remains the executable exhaustiveness check.

The sole current target WIP is the prior authorized one-line correction in `supabase/migrations/20260718000200_selling_package_evaluation.sql`. Director must inspect and preserve that exact WIP before widening within this superseding route. Foundation Task 1 remains held until the complete correction receives committed non-author GO. After GO, coordinator will rebind the Foundation Task 1 immutable parent to the accepted correction commit.

## Open complete correction slice

Director owns one test-first correction from immutable parent `41d9f1d846d6e0928b520573094ae59846114df5` across exactly these two target paths:

- `supabase/migrations/20260718000100_selling_package_domain.sql`
- `supabase/migrations/20260718000200_selling_package_evaluation.sql`

The exact private direct writers in scope are:

- `biz._record_selling_case_revision(jsonb,bigint,uuid,boolean)`
- `biz._record_hs_offer_revision(jsonb,bigint,uuid)`
- `biz._record_selling_package_candidate_links(jsonb,bigint,uuid)`
- `decision._record_selling_package_manual_scenarios(jsonb,bigint,uuid)`
- `decision._seal_selling_package_evaluation(jsonb,bigint,uuid)`
- `decision._record_selling_package_owner_decision(jsonb,bigint,uuid)`

For each function, make `perform app.ppl_reference_snapshot_lock();` the first stateful operation immediately after `begin`, before payload reads, participant reads, row or table locks, temporary-table work, or inserts. The already-routed manual-scenario line counts toward this exact set. Do not alter any other statement or function.

Preserve payload, validation, replay, quorum, calculation, recommendation, timestamp, grant, public API, and error semantics. Reentrant acquisition inside the public command transaction is expected and must not move or weaken the existing `app.ppl_begin_command` boundary.

Verify in this order:

1. Preserve the executable RED evidence and the two named post-first-fix signatures.
2. Inspect the actual diff and prove it consists only of six identical entry-lock calls across the two allowed paths.
3. Run `db/tests/test_ppl_offer_cutoff.py::test_every_participating_writer_is_discovered_and_lock_ordered` and require PASS.
4. Run all four selling-package suites: `db/tests/test_selling_package_domain.py`, `db/tests/test_selling_package_api.py`, `db/tests/test_selling_package_evaluation.py`, and `db/tests/test_selling_package_security.py`.
5. Run the exact 40-test selector: `db/tests/test_ppl_decision_policy.py db/tests/test_rls_grants.py db/tests/test_ppl_offer_cutoff.py -q`.
6. Commit only the two allowed paths.

Director then submits the immutable parent-to-head range and both finding refs to non-author Operator2 on a different model. Operator2 independently checks the exact diff, six lock-before-stateful-operation placements, catalog-wide focused regression, four selling-package suites, and exact 40-test selector, then returns GO, NITS, or FAIL.

No Foundation Task 1 file may change in this correction.

No test file change, suppression, xfail, skip, parser weakening, or fixture workaround is authorized.

No private owner value collection is authorized.

No policy creation, approval, format ruling, or activation is authorized.

No service lifecycle or container mutation is authorized.

No managed database, real-data, deployment, booking, provider, or spend action is authorized.

No evidence-ledger merge is authorized.

No evidence-ledger push is authorized.

No Pipeline push is authorized.

No cursor consumption, lock action, cleanup, reset, rebase, or amend is authorized.

## Exact next trigger

Director reads this complete committed route, confirms the preserved one-line WIP, adds only the remaining five entry-lock calls across the two allowed migrations, verifies the exact scopes above, commits the complete correction, and sends the immutable range to Operator2 for independent review.

Cursor at send: 0
