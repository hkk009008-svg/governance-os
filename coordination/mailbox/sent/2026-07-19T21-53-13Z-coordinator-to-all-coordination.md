# Coordinator → All: accept Foundation Task 2 GO and open Foundation Task 3

**When:** 2026-07-19T21:53:13Z · **From:** coordinator (online)

Task-board: ledger-one-user-owner-policy-2026-07-20
Task ID: coordinator-one-user-owner-policy-foundation-task3
Status: FOUNDATION TASK 2 ACCEPTED; FOUNDATION TASK 3 OPEN; RUNTIME POLICY INACTIVE
Supersedes active route: coordination/mailbox/sent/2026-07-19T21-30-35Z-coordinator-to-all-coordination.md@5aa92df21679975c9d66acd82f7d1b9338fada69
Carries forward foundation route: coordination/mailbox/sent/2026-07-19T17-40-34Z-coordinator-to-all-coordination.md@972c3e95610bb597844a2a0dd3d110ce38d47c9d
Authorization source: user-task:one-user-owner-gates-and-owner-center-approved-2026-07-20
Approved design: docs/superpowers/specs/2026-07-20-one-user-owner-gates-and-owner-center-design.md@e091c436b86551efa7a9fe62b55c923818ac3eae
Foundation plan: docs/superpowers/plans/2026-07-20-one-user-owner-policy-foundation.md@e091c436b86551efa7a9fe62b55c923818ac3eae
Accepted Foundation Task 1 commit: 50a28cfe7f78b8cd9095bd018141f91416beb8c8
Accepted Foundation Task 1 GO: coordination/mailbox/sent/2026-07-19T20-52-56Z-operator2-to-all-verification-report.md@51f5ec179b8e64f7d9438aa1baa3f4409d3dd67b
Accepted Foundation Task 2 commit: 2d3a76026ae0eff6413ba4270e6191f8fcba6948
Accepted Foundation Task 2 request: coordination/mailbox/sent/2026-07-19T21-44-31Z-director-to-operator2-verify-request.md@4de0c990d5fec225b7b1bdd88176c077cfa9a9d2
Accepted Foundation Task 2 GO: coordination/mailbox/sent/2026-07-19T21-49-54Z-operator2-to-all-verification-report.md@339ba2331425c075a9ac3f56cf9b8868ba7e5a14
Target repository: /Users/hyungkoookkim/evidence-ledger
Target worktree: /Users/hyungkoookkim/evidence-ledger/.worktrees/codex-ppl-offer-decision-m1
Target branch: codex/ppl-offer-decision-m1
Immutable target parent: 2d3a76026ae0eff6413ba4270e6191f8fcba6948
Selling-package contract SHA-256: cc4d6d552ae75afca04fd2a5e2bb2e92b26812192b0668408908af60a1cf086d
Frozen PPL contract SHA-256: 1c0f4f58632e14243f373c36abb3a78b08807cdd9dccd54eeb3cc8a16d5503a6

## Foundation Task 2 reconciliation

Operator2 on `gpt-5.6-terra` independently accepted the exact range `50a28cfe7f78b8cd9095bd018141f91416beb8c8..2d3a76026ae0eff6413ba4270e6191f8fcba6948`. The range changes exactly four routed paths, closes the hidden-default Critical finding, preserves the frozen BUY selector and legacy mixed-denominator regression, adds the exact private composite fact vocabulary and server-owned action guards, and keeps public APIs, grants, contracts, and private owner values unchanged.

Operator2 reproduced focused 4/4, eligible-BUY 3/3, cutoff 3/3, and complete profile 113/113 against ephemeral synthetic databases. Project smoke passed, both frozen contract hashes matched, and the target worktree is clean at the accepted commit. Foundation Task 2 is closed; its commit is the immutable parent for Foundation Task 3.

## Owner and runtime contract

This private deployment has one operational user, one owner account, one persistent authenticated owner session, one laptop, and one installed Windows PWA. There is no user switcher and no second-owner matching workflow.

The five commission rates and five private risk amounts remain unset, private, and uninferred. Gate B and Gate C are decision-complete but runtime-inactive. Gate D remains `owner_ruling_required` until later owner-center work records an authorized ruling and capability reread. This task creates no real policy, approval, ruling, activation, booking, or spend.

## Open slice — Foundation Task 3 only

Director owns Foundation Task 3, `Apply eligibility parity to the product-first package evaluator`, from immutable parent `2d3a76026ae0eff6413ba4270e6191f8fcba6948`.

Allowed target paths are exactly:

- `supabase/migrations/20260718000200_selling_package_evaluation.sql`
- `db/tests/test_selling_package_evaluation.py`

Work test-first. Add these two plan-named behavioral regressions:

- `test_package_test_requires_explicit_experimental_choice`
- `test_no_ppl_candidate_is_never_test_eligible`

The paired package regression must hold every synthetic fact constant except the linked PPL choice-set revision's `experimental_allowed` value. The false case must not select `TEST`; the true case must select `TEST` when TEST and NEGOTIATE are otherwise both eligible. The no-PPL regression must exercise the same private composite policy and prove a `no_ppl` candidate never selects `TEST`.

Tests must explicitly opt into the Task 2 private composite policy and approved allocation revision. Reuse the existing Task 2 test-only private-policy helper or an equivalently closed direct synthetic helper; do not send private condition codes through the frozen v1 risk-policy command. Any new helper parameter must default to the immutable-parent behavior, and only the two new tests may override `experimental_allowed` for this slice. Do not globally rewrite `_seed_package`, `_seed_state`, `GATE_B_CASES`, existing package fixtures, or adversarial tables.

In the package evaluator, set `experimental_allowed` from the linked `biz.ppl_choice_set_revisions` row for a `ppl` candidate and set it to `false` for a `no_ppl` candidate. Do not infer it from offer, deliverable, policy, browser, or client data.

Build the same Task 2 composite facts after all primitive calculation, constraint, budget, downside, quote, and candidate-mode facts exist:

```text
needs_info_required = not calculation_available
  or hard_constraint_unknown or missing_critical_term
  or invalid_vat or invalid_scenario or unsupported_objective

hard_skip_required = hard_constraint_failed
  or offer_expired or offer_withdrawn
  or choice_budget_exceeded or monthly_budget_exceeded
  or downside_cap_exceeded

buy_eligible = not needs_info_required and not hard_skip_required
  and manual_buy_allowed
  and quoted_base_amount is within the positive-or-zero scenario quote ceiling

test_eligible = not needs_info_required and not hard_skip_required
  and pilot_booking_allowed and experimental_allowed
  and experimental budget exists and is not exceeded

negotiate_eligible = not needs_info_required and not hard_skip_required
  and a positive scenario quote ceiling exists
  and buy_eligible is false
```

Preserve the already-computed primitive fact keys for compatibility and add exactly `needs_info_required`, `hard_skip_required`, `buy_eligible`, `test_eligible`, `negotiate_eligible`, `experimental_allowed`, and `always=true` before calling `decision._ppl_select_action`. Require the matching composite eligibility boolean in the post-selection hard guards for `BUY`, `TEST`, and `NEGOTIATE`; a policy rule that selects an ineligible action must continue to fail closed with the existing error boundary.

For `no_ppl`, `experimental_allowed=false` must make `test_eligible=false` regardless of pilot permission or experimental budget. Do not otherwise prohibit a no-PPL candidate from a lawful BUY, NEGOTIATE, NEEDS_INFO, or SKIP result.

Do not calculate action in the web client. Do not change candidate generation, missing-scenario exclusion, no-PPL generation, formula math, costs, timestamps, evidence, stable reads, public APIs, grants, operation inventory, owner-decision behavior, action labels, winner eligibility, ranking order, tie-break fields, or tie-break precedence except through the corrected server-owned action value already consumed by the existing ranking logic. Do not alter either frozen contract.

## Verification and review

Use only the already-running local listener at `127.0.0.1:54322` and ephemeral synthetic test databases. If the listener is unavailable, stop and report the exact boundary; do not change service state.

Verify in this order:

1. Before production SQL changes, run `db/tests/test_selling_package_evaluation.py -k 'test_requires_explicit_experimental or no_ppl_candidate_is_never' -q` and capture executable behavioral RED, not a fixture, collection, connection, or setup failure.
2. Run the same focused selector after implementation and require both tests to pass.
3. Run `db/tests/test_selling_package_domain.py db/tests/test_selling_package_evaluation.py db/tests/test_selling_package_api.py db/tests/test_selling_package_security.py db/tests/test_ppl_offer_evaluation.py -q` and require PASS.
4. Run project `scripts/ci_smoke.py` and require PASS.
5. Recompute both frozen contract hashes and require the values bound above.
6. Inspect the actual parent-to-working-tree diff, `git diff --check`, and exact two-path scope. Confirm excluded missing scenarios, no-PPL generation, rank/winner behavior, evidence, stable reads, frozen fixtures, and Task 2 behavior remain unchanged.

Before commit, obtain a fresh read-only review of the actual two-path diff for spec compliance and code quality. It must audit candidate-mode handling, the linked choice-set source of `experimental_allowed`, all composite definitions and hard guards, private-policy test isolation, no-PPL behavior, ranking/tie-break non-interference, and plausible abuse classes. Do not commit with a Critical or Important finding.

Only after verification and clean read-only review may Director commit exactly the two allowed paths. Director then publishes one canonical verify-request binding the exact range `2d3a76026ae0eff6413ba4270e6191f8fcba6948..HEAD`, this route, the plan, both paths, TDD evidence, full suite, contract hashes, smoke, and actual-diff review. Assign non-author Operator2 on `gpt-5.6-terra`. Operator2 independently reviews the actual range and returns GO, NITS, or FAIL.

Foundation Task 4 remains held until Task 3 receives committed GO. The owner-center plan remains held until the complete foundation range receives cumulative GO.

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

Director reads this complete committed route, confirms the clean target at immutable parent `2d3a76026ae0eff6413ba4270e6191f8fcba6948`, executes only Foundation Task 3 across the two allowed paths, and publishes the immutable actual-range request to Operator2.

Cursor at send: 0
