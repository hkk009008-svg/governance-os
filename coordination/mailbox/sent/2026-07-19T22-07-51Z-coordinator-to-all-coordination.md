# Coordinator → All: supersede foundation task 3 for explicit legacy policy isolation

**When:** 2026-07-19T22:07:51Z · **From:** coordinator (online)

Task-board: ledger-one-user-owner-policy-2026-07-20
Task ID: coordinator-one-user-owner-policy-foundation-task3-correction
Status: FOUNDATION TASK 3 DIAGNOSTIC ACCEPTED; CORRECTED TASK 3 OPEN; RUNTIME POLICY INACTIVE
Supersedes active route: coordination/mailbox/sent/2026-07-19T21-53-13Z-coordinator-to-all-coordination.md@3318016b16826555e09dc878580adbce231707cb
Carries forward foundation route: coordination/mailbox/sent/2026-07-19T17-40-34Z-coordinator-to-all-coordination.md@972c3e95610bb597844a2a0dd3d110ce38d47c9d
Authorization source: user-task:one-user-owner-gates-and-owner-center-approved-2026-07-20
Approved design: docs/superpowers/specs/2026-07-20-one-user-owner-gates-and-owner-center-design.md@e091c436b86551efa7a9fe62b55c923818ac3eae
Foundation plan: docs/superpowers/plans/2026-07-20-one-user-owner-policy-foundation.md@e091c436b86551efa7a9fe62b55c923818ac3eae
Accepted Foundation Task 1 commit: 50a28cfe7f78b8cd9095bd018141f91416beb8c8
Accepted Foundation Task 1 GO: coordination/mailbox/sent/2026-07-19T20-52-56Z-operator2-to-all-verification-report.md@51f5ec179b8e64f7d9438aa1baa3f4409d3dd67b
Accepted Foundation Task 2 commit: 2d3a76026ae0eff6413ba4270e6191f8fcba6948
Accepted Foundation Task 2 GO: coordination/mailbox/sent/2026-07-19T21-49-54Z-operator2-to-all-verification-report.md@339ba2331425c075a9ac3f56cf9b8868ba7e5a14
Target repository: /Users/hyungkoookkim/evidence-ledger
Target worktree: /Users/hyungkoookkim/evidence-ledger/.worktrees/codex-ppl-offer-decision-m1
Target branch: codex/ppl-offer-decision-m1
Immutable target parent: 2d3a76026ae0eff6413ba4270e6191f8fcba6948
Selling-package contract SHA-256: cc4d6d552ae75afca04fd2a5e2bb2e92b26812192b0668408908af60a1cf086d
Frozen PPL contract SHA-256: 1c0f4f58632e14243f373c36abb3a78b08807cdd9dccd54eeb3cc8a16d5503a6

## Diagnostic reconciliation

The initial Task 3 implementation reached valid behavioral RED and focused GREEN while remaining unstaged in the two originally routed paths. The first cumulative run then produced 14 failures and 96 passes. Every failure had one identical cause and error: a legacy synthetic package policy selected `TEST` from `calculation_available` for a generated `no_ppl` candidate; the corrected evaluator truthfully set `experimental_allowed=false`, derived `test_eligible=false`, and rejected the ineligible selected action with `PPL_POLICY_INACTIVE` and `TEST 규칙이 고정 안전 조건과 충돌합니다.`

The prior route was internally inconsistent because it simultaneously required the matching fail-closed hard guard, required the unchanged cumulative suite to pass, preserved every legacy package test fixture, and forbade the explicit fixture opt-ins needed by the affected tests. The production behavior is correct and remains frozen. This superseding route corrects only the test-fixture authority and adds the API test file needed for explicit call-site opt-ins.

The exact affected nodes are:

- `db/tests/test_selling_package_evaluation.py::test_each_current_hs_offer_gets_exactly_one_no_ppl_candidate`
- `db/tests/test_selling_package_evaluation.py::test_cross_vendor_ppl_links_generate_independent_joint_candidates`
- `db/tests/test_selling_package_evaluation.py::test_missing_package_scenario_excludes_only_that_candidate`
- `db/tests/test_selling_package_evaluation.py::test_withdrawn_expired_stale_and_out_of_window_revisions_are_excluded`
- `db/tests/test_selling_package_evaluation.py::test_hard_fail_precedes_economics_and_unknown_yields_needs_info`
- `db/tests/test_selling_package_evaluation.py::test_joint_calculation_binds_hs_and_ppl_costs_once`
- `db/tests/test_selling_package_evaluation.py::test_rank_and_winner_use_persisted_deterministic_tie_break`
- `db/tests/test_selling_package_evaluation.py::test_package_owner_decision_records_intent_without_booking_or_spend`
- `db/tests/test_selling_package_evaluation.py::test_probability_and_quantile_outputs_are_absent`
- `db/tests/test_selling_package_evaluation.py::test_future_revision_does_not_change_old_sealed_batch`
- `db/tests/test_selling_package_api.py::test_command_recovery_is_closed_lock_protected_and_actor_scoped`
- `db/tests/test_selling_package_api.py::test_product_case_and_hs_cards_have_fixed_shapes_and_bound_cursors`
- `db/tests/test_selling_package_api.py::test_requirements_recommendation_and_evidence_share_exact_identity`
- `db/tests/test_selling_package_api.py::test_revision_history_is_normalized_for_all_six_kinds`

No failure had a different classification. The target remains at the immutable parent with exactly the two original Task 3 paths modified and unstaged. Nothing is committed.

## Corrected open slice — Foundation Task 3 only

Director resumes Foundation Task 3 from the preserved uncommitted diagnostic state. Allowed target paths are now exactly:

- `supabase/migrations/20260718000200_selling_package_evaluation.sql`
- `db/tests/test_selling_package_evaluation.py`
- `db/tests/test_selling_package_api.py`

Preserve the current production SQL behavior and the two new plan-named regressions. Do not weaken, bypass, remove, or special-case the product-first composite facts or the BUY, TEST, and NEGOTIATE hard guards. `ppl` candidates must continue to read `experimental_allowed` only from their linked choice-set revision. `no_ppl` candidates must continue to force `experimental_allowed=false` and `test_eligible=false`.

The only newly authorized correction is explicit synthetic private-policy isolation for the 14 named legacy test nodes:

1. In each of the ten named evaluation tests, create the already-approved Task 2 private composite policy inside that test and pass it explicitly as `policy=` to that test's `_seed_package` call.
2. In `db/tests/test_selling_package_api.py`, import the private-policy helper from its defining Task 2 test module. Make `_sealed_fixture` require a `policy` argument with no default and pass it explicitly to `_seed_package`. Each of the four named API tests creates the approved private composite policy inside the test and passes it explicitly to `_sealed_fixture`.
3. Keep `_seed_package(policy=None, experimental_allowed=True)` at its immutable-parent-compatible defaults. Do not make the private policy a helper default. Do not make `_seed_state`, `_seed_package`, `_sealed_fixture`, a fixture, a marker, or an environment variable silently choose the private policy.
4. Only the two new Task 3 regressions may override `experimental_allowed`. The 14 compatibility opt-ins select only the private composite policy and approved allocation revision; they do not override the choice flag or unrelated synthetic values.
5. Do not change `GATE_B_CASES`, `GATE_C_CASES`, generic engine tables, the private action table, frozen BUY overlays, cutoff fixtures, adversarial tables, or any non-named test.

The explicit opt-ins repair test-policy fidelity; they are not an exception to production eligibility. Do not translate a rejected legacy `TEST` into another action in production, skip no-PPL evaluation, add a compatibility branch keyed by policy shape, or relax fail-closed behavior.

All other Task 3 behavior and exclusions from the superseded route remain binding. Do not alter candidate generation, missing-scenario exclusion, no-PPL generation, formula math, costs, timestamps, evidence, stable reads, public APIs, grants, operation inventory, owner-decision behavior, action labels, winner eligibility, ranking order, tie-break fields, or tie-break precedence except through the corrected server-owned action already consumed by existing ranking logic. Do not alter either frozen contract.

## Corrected verification and review

Use only the already-running local listener at `127.0.0.1:54322` and ephemeral synthetic databases. Do not change service state.

Preserve the recorded valid Task 3 behavioral RED and focused GREEN. After only the explicit test correction above:

1. Run the 14 exact nodes listed in this route and require 14 passes.
2. Run `db/tests/test_selling_package_evaluation.py -k 'test_requires_explicit_experimental or no_ppl_candidate_is_never' -q` and require two passes.
3. Run `db/tests/test_selling_package_domain.py db/tests/test_selling_package_evaluation.py db/tests/test_selling_package_api.py db/tests/test_selling_package_security.py db/tests/test_ppl_offer_evaluation.py -q` and require the complete cumulative suite to pass.
4. Run project `scripts/ci_smoke.py` and require PASS.
5. Recompute both frozen contract hashes and require the values bound above.
6. Inspect the actual parent-to-working-tree diff, run `git diff --check`, and prove the exact three-path scope. Confirm the production SQL differs from the initial Task 3 WIP only by any formatting already present before this correction; the newly authorized compatibility correction is test-only.

Before commit, obtain a fresh read-only review of the complete three-path actual diff for spec compliance, code quality, and plausible abuse classes. The review must audit all original Task 3 requirements plus explicit-only policy selection, absence of hidden defaults, the exact 14-node footprint, API helper requiredness, no-PPL fail-closed behavior, and ranking/tie-break non-interference. Do not commit with a Critical or Important finding.

Only after all corrected verification and review gates pass may Director commit exactly the three allowed paths. Director then publishes one canonical verify-request binding the exact range `2d3a76026ae0eff6413ba4270e6191f8fcba6948..HEAD`, this superseding route, the plan, all three paths, preserved TDD evidence, the 14-node correction selector, cumulative suite, contract hashes, smoke, and actual-diff review. Assign non-author Operator2 on `gpt-5.6-terra`.

Foundation Task 4 remains held until Task 3 receives committed Operator2 GO. The owner-center plan remains held until the complete foundation range receives cumulative GO.

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

Director reads this complete committed superseding route, resumes from the preserved unstaged Task 3 diagnostic state at immutable parent `2d3a76026ae0eff6413ba4270e6191f8fcba6948`, applies only the explicit 14-node test-policy correction across the three allowed paths, and completes the corrected verification, review, commit, and canonical Operator2 request.

Cursor at send: 0
