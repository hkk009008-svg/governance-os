# Coordinator → All: supersede Task 2 with explicit fixture opt-ins

**When:** 2026-07-19T21:30:35Z · **From:** coordinator (online)

Task-board: ledger-one-user-owner-policy-2026-07-20
Task ID: coordinator-one-user-owner-policy-foundation-task2-explicit-optins
Status: FOUNDATION TASK 2 OPEN; CORRECTIVE TEST SCOPE AUTHORIZED; RUNTIME POLICY INACTIVE
Supersedes active route: coordination/mailbox/sent/2026-07-19T20-56-10Z-coordinator-to-all-coordination.md@4e6c9556fca8e658080592c6083fb957159da495
Carries forward foundation route: coordination/mailbox/sent/2026-07-19T17-40-34Z-coordinator-to-all-coordination.md@972c3e95610bb597844a2a0dd3d110ce38d47c9d
Authorization source: user-task:one-user-owner-gates-and-owner-center-approved-2026-07-20
Approved design: docs/superpowers/specs/2026-07-20-one-user-owner-gates-and-owner-center-design.md@e091c436b86551efa7a9fe62b55c923818ac3eae
Foundation plan: docs/superpowers/plans/2026-07-20-one-user-owner-policy-foundation.md@e091c436b86551efa7a9fe62b55c923818ac3eae
Accepted Foundation Task 1 commit: 50a28cfe7f78b8cd9095bd018141f91416beb8c8
Accepted Foundation Task 1 GO: coordination/mailbox/sent/2026-07-19T20-52-56Z-operator2-to-all-verification-report.md@51f5ec179b8e64f7d9438aa1baa3f4409d3dd67b
Target repository: /Users/hyungkoookkim/evidence-ledger
Target worktree: /Users/hyungkoookkim/evidence-ledger/.worktrees/codex-ppl-offer-decision-m1
Immutable target parent: 50a28cfe7f78b8cd9095bd018141f91416beb8c8
Selling-package contract SHA-256: cc4d6d552ae75afca04fd2a5e2bb2e92b26812192b0668408908af60a1cf086d
Frozen PPL contract SHA-256: 1c0f4f58632e14243f373c36abb3a78b08807cdd9dccd54eeb3cc8a16d5503a6

## Reconciliation and correction

The first Task 2 implementation reached focused GREEN, but a read-only review found that an unconditional allocation-mode rewrite inside `_seed_state` silently changed every ordinary v1 evaluation fixture. That finding is accepted. A later advisory reconsideration was not a formal verdict and did not review the corrected bytes; it is nonbinding and withdrawn.

Director restored the original BUY fixture and the legacy mixed-denominator regression, removed the unconditional helper rewrite, retained only explicit evaluator call-site opt-ins, and ran the binding four-file suite without committing. The resulting evidence is `4 passed, 65 deselected` for the required focused selector and `6 failed, 107 passed` for the binding suite.

The six residual failures are fully classified:

- `test_selected_output_policy_baseline_covers_every_closed_action[BUY]`
- `test_allowed_buy_creates_full_booking_decision_and_event_atomically`
- `test_full_buy_booking_rolls_back_decision_booking_event_and_receipt`

Those three owned tests retain the frozen BUY quote `1000`, which the new mandatory server-owned guard truthfully rejects against ceiling `90`. They require a separate explicitly named Task 2 eligible synthetic case; the frozen selector fixture itself must not change.

- `test_public_seal_waits_for_preexisting_writer_and_uses_post_lock_cutoff`
- `test_fixed_cutoff_reselects_t0_and_reproduces_snapshot`
- `test_comparison_and_history_staleness_are_frozen_at_cursor_snapshot`

Those three tests are unchanged callers in `db/tests/test_ppl_offer_cutoff.py`. Their first `_seed_state` call cannot explicitly select the approved allocation revision while that file remains outside the old route. This is a route-scope defect, not authority to hide a default. This superseding route adds that one test path for exactly those explicit call-site opt-ins.

## Open slice — corrected Foundation Task 2 only

Director continues Foundation Task 2 from immutable parent `50a28cfe7f78b8cd9095bd018141f91416beb8c8`, preserving the current uncommitted three-path WIP after rechecking it matches the diagnostic state.

Allowed target paths are now exactly:

- `supabase/migrations/20260717000500_decision_policy.sql`
- `supabase/migrations/20260717000600_offer_evaluation.sql`
- `db/tests/test_ppl_offer_evaluation.py`
- `db/tests/test_ppl_offer_cutoff.py`

The production requirements from the superseded Task 2 route carry forward unchanged: exact private composite fact vocabulary, approved allocation-mode fail-closure, non-blocking mixed-denominator evidence, server-owned BUY/TEST/NEGOTIATE eligibility, exact six-row test-only action table, frozen v1 validator boundary, no public API or grant widening, and no contract change. Do not broaden either SQL migration to resolve test compatibility.

Use this exact fixture correction:

1. Keep `_seed_state` default behavior unchanged. It may accept the optional keyword `formula_allocation_mode: str | None = None`. Only when a caller passes the keyword may it assert the exact value `campaign_level_action_no_target_break_even` and write that value into its already-copied `effective_formula_body`. There must be no unconditional assignment, non-`None` default, caller inspection, environment switch, or implicit fallback.
2. Preserve `formula_body()`, `risk_body()`, `GATE_B_CASES`, `GATE_C_CASES`, adversarial tables, `_selected_output_case`, and the restored legacy mixed-denominator test. In particular, `_selected_output_case("BUY")` retains quoted and source amounts `1000`; do not patch it globally.
3. Add one clearly named Task 2-only BUY helper or local case overlay. It must derive from `_selected_output_case("BUY")`, use a distinct synthetic name, copy rather than mutate its dictionaries, and set quoted and source amounts to the already-proven synthetic value `50`, which is within ceiling `90`. Only the three named BUY tests above may select this explicit eligible overlay. Non-BUY cases continue to use the frozen selector fixture.
4. In `db/tests/test_ppl_offer_cutoff.py`, import the approved-mode constant from `test_ppl_offer_evaluation` and pass it explicitly only to the first `_seed_state` call serving each of the three named cutoff tests above: the direct call in `test_public_seal_waits_for_preexisting_writer_and_uses_post_lock_cutoff`, the initial call in `build_cutoff_fixture`, and the direct call in `test_comparison_and_history_staleness_are_frozen_at_cursor_snapshot`. Do not alter later shared-policy calls or any other cutoff test, assertion, fixture, cursor, timestamp, lock, or snapshot behavior.
5. Retain explicit allocation-mode opt-ins in the owned evaluator tests only where the test intentionally exercises or depends on the Task 2 revision. A fresh reviewer must audit every such call against the immutable parent and reject broad or redundant fixture conversion.

No pre-existing expectation may be changed merely to make the suite green. The legacy mixed-denominator regression remains named `test_break_even_unit_rounding_disagreement_in_participating_rules_fails_closed` and continues to expect `missing_denominator` plus `NEEDS_INFO`. The new mixed-linear-rate test remains the explicit Task 2 case proving the new non-blocking behavior.

## Verification and review

Run, in order, against ephemeral synthetic databases through the already-running local listener:

1. The four plan-named focused regressions and require `4 passed`.
2. The exact three BUY node IDs named above and require PASS.
3. The exact three cutoff node IDs named above and require PASS.
4. `db/tests/test_ppl_decision_policy.py db/tests/test_ppl_offer_evaluation.py db/tests/test_ppl_offer_cutoff.py db/tests/test_rls_grants.py -q` and require the complete corrected profile to pass; expected count is `113 passed` unless pytest collection truthfully proves a different count.
5. Project `scripts/ci_smoke.py` and require PASS.
6. Recompute both frozen contract hashes and require the values bound above.
7. Inspect the actual parent-to-working-tree diff, `git diff --check`, and exact four-path scope.

Before any commit, send the actual corrected four-path diff to a fresh read-only review turn. The prior advisory reconsideration is not acceptance. The reviewer must separately assess spec compliance and code quality, confirm the hidden-default Critical finding is closed, confirm the original BUY and legacy mixed fixtures remain intact, audit every explicit opt-in, and find no Critical or Important issue.

Only after all checks and the fresh read-only re-review pass may Director commit exactly the four allowed paths. Director then publishes one canonical verify-request binding the exact range `50a28cfe7f78b8cd9095bd018141f91416beb8c8..HEAD`, this superseding route, all four paths, the initial Critical finding and its correction, and the verification evidence. Assign non-author Operator2 on `gpt-5.6-terra`. Operator2 independently reviews the actual range and returns GO, NITS, or FAIL.

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

Director reads this committed superseding route, confirms the current uncommitted WIP matches the diagnostic state at immutable parent `50a28cfe7f78b8cd9095bd018141f91416beb8c8`, applies only the explicit BUY overlay and three cutoff call-site opt-ins described above, completes verification and fresh read-only re-review, commits exactly the four allowed paths, and publishes the immutable actual-range request to Operator2.

Cursor at send: 0
