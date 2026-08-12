# Coordinator → All: accept Foundation Task 1 GO and open Foundation Task 2

**When:** 2026-07-19T20:56:10Z · **From:** coordinator (online)

Task-board: ledger-one-user-owner-policy-2026-07-20
Task ID: coordinator-one-user-owner-policy-foundation-task2
Status: FOUNDATION TASK 1 ACCEPTED; FOUNDATION TASK 2 OPEN; RUNTIME POLICY INACTIVE
Supersedes active route: coordination/mailbox/sent/2026-07-19T20-34-58Z-coordinator-to-all-coordination.md@386a101bf17ff736858311d08ea6582aa82c6362
Carries forward foundation route: coordination/mailbox/sent/2026-07-19T17-40-34Z-coordinator-to-all-coordination.md@972c3e95610bb597844a2a0dd3d110ce38d47c9d
Authorization source: user-task:one-user-owner-gates-and-owner-center-approved-2026-07-20
Approved design: docs/superpowers/specs/2026-07-20-one-user-owner-gates-and-owner-center-design.md@e091c436b86551efa7a9fe62b55c923818ac3eae
Foundation plan: docs/superpowers/plans/2026-07-20-one-user-owner-policy-foundation.md@e091c436b86551efa7a9fe62b55c923818ac3eae
Owner-center plan: docs/superpowers/plans/2026-07-20-owner-center-windows-pwa.md@e091c436b86551efa7a9fe62b55c923818ac3eae
Accepted Foundation Task 1 commit: 50a28cfe7f78b8cd9095bd018141f91416beb8c8
Accepted Foundation Task 1 request: coordination/mailbox/sent/2026-07-19T20-48-54Z-director-to-operator2-verify-request.md@6916291125ca68c3b2f3aceba64cf585f56ec311
Accepted Foundation Task 1 GO: coordination/mailbox/sent/2026-07-19T20-52-56Z-operator2-to-all-verification-report.md@51f5ec179b8e64f7d9438aa1baa3f4409d3dd67b
Target repository: /Users/hyungkoookkim/evidence-ledger
Target worktree: /Users/hyungkoookkim/evidence-ledger/.worktrees/codex-ppl-offer-decision-m1
Immutable target parent: 50a28cfe7f78b8cd9095bd018141f91416beb8c8
Selling-package contract SHA-256: cc4d6d552ae75afca04fd2a5e2bb2e92b26812192b0668408908af60a1cf086d
Frozen PPL contract SHA-256: 1c0f4f58632e14243f373c36abb3a78b08807cdd9dccd54eeb3cc8a16d5503a6

## Foundation Task 1 reconciliation

Operator2 on `gpt-5.6-terra` independently accepted the exact target range `5c12411d63a940508a396e4ccbd0f95e072724bf..50a28cfe7f78b8cd9095bd018141f91416beb8c8`. The range changes exactly the three routed Task 1 paths, preserves the frozen v1 two-owner operations, adds only the closed versioned quorum metadata and three private revoked helpers, and updates only the five named consumers. Focused quorum tests passed 4/4, the corrected decision-policy/cutoff/grant profile passed 44/44, target smoke passed, and both frozen contract hashes remained unchanged.

The target worktree is clean at the accepted Task 1 commit. Pipeline GO-schema validation passes with 66 committed reports and zero violations; protocol doctor passes 180 tests and project smoke. Task 1 is closed. Its commit is the immutable parent for Foundation Task 2.

## Owner and runtime contract

This private deployment has one operational user, one owner account, one persistent authenticated owner session, one laptop, and one installed Windows PWA. There is no user switcher and no second-owner matching workflow.

The owner has not supplied the five commission rates or five private risk amounts. They remain unset, private, and uninferred. Gate B and Gate C are decision-complete but runtime-inactive; Gate D remains `owner_ruling_required` until later owner-center work records an authorized ruling and capability reread. This task creates no real policy, approval, ruling, activation, booking, or spend.

## Open slice — Foundation Task 2 only

Director owns Foundation Task 2, `Correct campaign allocation and server-owned action eligibility`, from immutable parent `50a28cfe7f78b8cd9095bd018141f91416beb8c8`.

Allowed target paths are exactly:

- `supabase/migrations/20260717000500_decision_policy.sql`
- `supabase/migrations/20260717000600_offer_evaluation.sql`
- `db/tests/test_ppl_offer_evaluation.py`

Work test-first. Add the four plan-named behavioral regressions:

- `test_mixed_linear_rates_keep_campaign_action_and_only_hide_target_break_even`
- `test_unapproved_package_allocation_mode_fails_closed`
- `test_experimental_choice_false_never_selects_test`
- `test_experimental_choice_true_selects_test_before_negotiate_when_both_eligible`

The mixed-linear-rate regression must retain a campaign action in `BUY`, `TEST`, or `NEGOTIATE`; keep required campaign contribution available; leave sales and units break-even null; include `mixed_denominators`; and add no missing field. An unsupported `package_allocation_mode` must fail closed to `NEEDS_INFO`, reuse `missing_critical_term`, and identify `/formula/package_allocation_mode`. `experimental_allowed=false` must never select `TEST`; when true and both TEST and NEGOTIATE are eligible, TEST wins by precedence.

Add exactly these private evaluator facts and no other new condition vocabulary:

- `needs_info_required`
- `hard_skip_required`
- `buy_eligible`
- `test_eligible`
- `negotiate_eligible`
- `experimental_allowed`
- `always`

Do not add those private facts to the frozen v1 `_validate_risk_body` allowlist. Tests may insert only the approved synthetic risk rows directly through a test helper and must independently derive the digest. Preserve all existing v1 fixtures and adversarial tables unless a test explicitly selects the new synthetic one-user policy revision.

The only approved allocation mode is `campaign_level_action_no_target_break_even`. In `_ppl_calculate_offer`, any other mode is unsupported: append existing reason `missing_critical_term`, add the missing item at `/formula/package_allocation_mode`, and set the needs-information fact. Do not add a wire reason code. When more than one denominator exists, retain `mixed_denominators` as evidence but do not append a missing field and do not remove calculation availability. Sales and units break-even remain null while required campaign contribution remains `all_in`.

Compute the composite facts only after all primitive flags exist, using the plan's exact definitions:

```text
needs_info_required = not calculation_available
  or hard_unknown or unsupported_allocation_mode
  or invalid_vat or invalid_scenario or missing_critical_term
  or unsupported_objective

hard_skip_required = hard_failed or offer_expired or offer_withdrawn
  or choice_exceeded or month_exceeded or downside_exceeded

buy_eligible = not needs_info_required and not hard_skip_required
  and manual_buy_allowed and quoted_base_amount is within the quote ceiling

test_eligible = not needs_info_required and not hard_skip_required
  and pilot_booking_allowed and experimental_allowed
  and experimental budget exists and is not exceeded

negotiate_eligible = not needs_info_required and not hard_skip_required
  and a positive quote ceiling exists and buy_eligible is false
```

Add those booleans, `experimental_allowed`, and `always=true` to the private facts object. Post-selection guards must require the matching eligibility boolean for `BUY`, `TEST`, and `NEGOTIATE`.

Pin this exact six-row action table in a test-only policy helper, in order:

1. `needs_info_required / is_true / NEEDS_INFO`
2. `hard_skip_required / is_true / SKIP`
3. `buy_eligible / is_true / BUY`
4. `test_eligible / is_true / TEST`
5. `negotiate_eligible / is_true / NEGOTIATE`
6. `always / is_true / SKIP`

Each row has the listed one-based precedence and a null threshold source. Do not send the new private condition codes through the frozen v1 risk-policy command. Do not widen any public API, operation inventory, grant surface, receipt/replay boundary, or frozen contract.

Verify in this order:

1. Run `db/tests/test_ppl_offer_evaluation.py -k 'mixed_linear_rates_keep or unapproved_package_allocation or experimental_choice' -q` before implementation and capture executable behavioral RED, not a fixture or connection failure.
2. Run the same focused selector after implementation and require PASS.
3. Run `db/tests/test_ppl_decision_policy.py db/tests/test_ppl_offer_evaluation.py db/tests/test_ppl_offer_cutoff.py db/tests/test_rls_grants.py -q`.
4. Run project `scripts/ci_smoke.py`.
5. Inspect the actual diff, confirm both frozen contract hashes, and commit only the three allowed paths.

The foundation plan's inherited `db/tests/test_ppl_offer_security.py` entry is stale and is not part of this route because that path does not exist at the immutable parent. `db/tests/test_rls_grants.py` is the real repository-wide grant/security profile for this slice.

Use only the already-running local listener and ephemeral synthetic test databases. If the listener is unavailable, stop and report the exact boundary; do not change service state.

Director then publishes one canonical verify-request binding the exact range `50a28cfe7f78b8cd9095bd018141f91416beb8c8..HEAD`, the three allowed paths, this route, and the plan. Assign non-author Operator2 on `gpt-5.6-terra`. Operator2 independently reviews the actual diff, mixed-denominator evidence semantics, unsupported allocation fail-closure, server-owned eligibility and precedence, frozen v1 boundary, focused tests, full corrected suite, contract hashes, and smoke before returning GO, NITS, or FAIL.

Foundation Tasks 3 and 4 remain held until Task 2 receives committed GO. The owner-center plan remains held until the complete foundation range receives cumulative GO.

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

Director reads this complete committed route, confirms the clean target at immutable parent `50a28cfe7f78b8cd9095bd018141f91416beb8c8`, executes only Foundation Task 2 across the three allowed paths, and publishes the immutable actual-range request to Operator2.

Cursor at send: 0
