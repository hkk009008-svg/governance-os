# Coordinator → All: accept writer-lock GO and reopen one-user foundation Task 1

**When:** 2026-07-19T20:30:21Z · **From:** coordinator (online)

Task-board: ledger-one-user-owner-policy-2026-07-20
Task ID: coordinator-one-user-owner-policy-foundation-task1-rebound
Status: WRITER-LOCK PREREQUISITE GO ACCEPTED; FOUNDATION TASK 1 OPEN; RUNTIME POLICY INACTIVE
Supersedes active route: coordination/mailbox/sent/2026-07-19T20-13-31Z-coordinator-to-all-coordination.md@8e41423ffb0416f0655b06b4e558a3586c584f11
Carries forward foundation route: coordination/mailbox/sent/2026-07-19T17-40-34Z-coordinator-to-all-coordination.md@972c3e95610bb597844a2a0dd3d110ce38d47c9d
Authorization source: user-task:one-user-owner-gates-and-owner-center-approved-2026-07-20
Approved design: docs/superpowers/specs/2026-07-20-one-user-owner-gates-and-owner-center-design.md@e091c436b86551efa7a9fe62b55c923818ac3eae
Foundation plan: docs/superpowers/plans/2026-07-20-one-user-owner-policy-foundation.md@e091c436b86551efa7a9fe62b55c923818ac3eae
Owner-center plan: docs/superpowers/plans/2026-07-20-owner-center-windows-pwa.md@e091c436b86551efa7a9fe62b55c923818ac3eae
Accepted prerequisite commit: 5c12411d63a940508a396e4ccbd0f95e072724bf
Accepted prerequisite request: coordination/mailbox/sent/2026-07-19T20-22-41Z-director-to-operator2-verify-request.md@670f5d413dd8e4e414eef6e6a7088c470f096a47
Accepted prerequisite GO: coordination/mailbox/sent/2026-07-19T20-26-59Z-operator2-to-all-verification-report.md@e6507fae13d3cf2cddb7eb5cafd44ac502773010
Target repository: /Users/hyungkoookkim/evidence-ledger
Target worktree: /Users/hyungkoookkim/evidence-ledger/.worktrees/codex-ppl-offer-decision-m1
Immutable target parent: 5c12411d63a940508a396e4ccbd0f95e072724bf
Selling-package contract SHA-256: cc4d6d552ae75afca04fd2a5e2bb2e92b26812192b0668408908af60a1cf086d
Frozen PPL contract SHA-256: 1c0f4f58632e14243f373c36abb3a78b08807cdd9dccd54eeb3cc8a16d5503a6

## Prerequisite reconciliation

Operator2 on `gpt-5.6-terra` independently accepted the exact prerequisite range `41d9f1d846d6e0928b520573094ae59846114df5..5c12411d63a940508a396e4ccbd0f95e072724bf`. The range changes only the two selling-package migrations, adds exactly six entry-lock calls, and passed the catalog-wide lock test, all four selling-package suites, the exact 40-test policy/grant/cutoff selector, and project smoke. Pipeline GO-schema validation passes with 65 committed reports and zero violations.

The target worktree is clean at the accepted prerequisite commit. That commit is now the immutable parent for Foundation Task 1. No prerequisite path is open for further change.

## Superseding owner contract

This private deployment has one operational user, one owner account, one persistent authenticated owner session, one laptop, and one installed Windows PWA. There is no user switcher and no second-owner matching workflow.

Legacy policy and format history remains immutable under `two_owner_v1`. New owner-center activation will use additive `single_owner_v1`: exactly one current active owner in the deployment and exactly one matching digest-bound approval from that owner. The frozen ordinary PPL and selling-package operation inventories remain unchanged.

The owner has not supplied the five commission rates or five private risk amounts. They remain unset, private, and uninferred. Gate B and Gate C are decision-complete but runtime-inactive; Gate D remains `owner_ruling_required` until the later owner-center work records an authorized ruling and capability reread. This task creates no real policy or owner ruling.

## Open slice — Foundation Task 1 only

Director owns Foundation Task 1, `Version the policy quorum without changing the frozen v1 operations`, from immutable parent `5c12411d63a940508a396e4ccbd0f95e072724bf`.

Allowed target paths are exactly:

- `supabase/migrations/20260717000500_decision_policy.sql`
- `supabase/migrations/20260717000600_offer_evaluation.sql`
- `db/tests/test_ppl_decision_policy.py`

Work test-first. Add the four plan-named focused behavioral regressions for single-owner activation, zero-or-multiple-owner rejection, legacy two-owner history, and single-owner `manual_only` digest matching. Preserve the existing tests proving the v1 `activate_ppl_policy_pair` and `record_ppl_initial_format_ruling` operations still reject one approval.

Add immutable `approval_quorum` metadata with closed values `two_owner_v1` and `single_owner_v1`, retaining `two_owner_v1` as the legacy default. Existing v1 operations must explicitly write `two_owner_v1`; no existing row may be updated, deleted, or reinterpreted.

Add only the plan-specified private shared predicates:

- `decision._ppl_required_owner_count(text)`
- `decision._ppl_activation_is_approved(bigint)`
- `decision._ppl_effective_format_status()`

Revoke public, anonymous, and authenticated execution of those helpers. `single_owner_v1` qualifies only with exactly one current active owner and one current matching formula approval plus one current matching risk approval. `two_owner_v1` continues to require two distinct current matching owner approvals. Format status uses the same versioned owner-count rule and newest qualifying digest-bound ruling.

Replace downstream hard-coded approval counts only in the plan-listed consumers: active policy lookup, manual-scenario revalidation, as-of activation lookup, seal revalidation, and capability format resolution. Preserve the explicit two-owner rules inside the existing operations-only v1 activation and initial-format wrappers.

Do not change any ordinary PPL or selling-package operation inventory, public API, receipt/replay boundary, grant surface, calculation, recommendation, lock prerequisite, owner-center API, web surface, real value, policy body, approval, ruling, or activation.

Verify in this order:

1. Run the focused Task 1 selector before implementation and capture executable RED for the missing quorum metadata/helpers, not a fixture or connection failure.
2. Run the focused selector after implementation and require PASS: `db/tests/test_ppl_decision_policy.py -k 'single_owner_quorum or two_owner_v1_history or single_owner_manual_only' -q`.
3. Run `db/tests/test_ppl_decision_policy.py db/tests/test_ppl_offer_security.py db/tests/test_ppl_offer_cutoff.py db/tests/test_rls_grants.py -q`.
4. Run project `scripts/ci_smoke.py`.
5. Inspect the actual diff and commit only the three allowed paths.

Use only the already-running local listener and ephemeral synthetic test databases. If the listener is unavailable, stop and report the exact boundary; do not change service state.

Director then publishes one canonical verify-request binding the exact range `5c12411d63a940508a396e4ccbd0f95e072724bf..HEAD`, the three allowed paths, this route, and the plan. Assign non-author Operator2 on `gpt-5.6-terra`. Operator2 independently reviews the actual diff, legacy compatibility, exact-one-owner fail-closed rules, digest matching, private helper grants, focused tests, full listed suite, and smoke before returning GO, NITS, or FAIL.

Foundation Tasks 2 through 4 remain held until Task 1 receives committed GO. The owner-center plan remains held until the complete foundation range receives cumulative GO.

No private owner value collection is authorized.

No real policy creation is authorized.

No approval, format ruling, or policy activation is authorized.

No managed database or Auth mutation is authorized.

No service lifecycle or dependency-network action is authorized.

No real-data access, provider contact, booking, deployment, or spend is authorized.

No evidence-ledger merge is authorized.

No evidence-ledger push is authorized.

No Pipeline push is authorized.

No cursor consumption, lock action, cleanup, reset, rebase, or amend is authorized.

## Exact next trigger

Director reads this complete committed route, confirms the clean target at immutable parent `5c12411d63a940508a396e4ccbd0f95e072724bf`, executes only Foundation Task 1 across the three allowed paths, and publishes the immutable actual-range request to Operator2.

Cursor at send: 0
