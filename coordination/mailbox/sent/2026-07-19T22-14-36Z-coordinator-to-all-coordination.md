# Coordinator → All: supersede task 3 for corrected joint winner expectation

**When:** 2026-07-19T22:14:36Z · **From:** coordinator (online)

Task-board: ledger-one-user-owner-policy-2026-07-20
Task ID: coordinator-one-user-owner-policy-foundation-task3-ranking-correction
Status: FOUNDATION TASK 3 SECOND DIAGNOSTIC ACCEPTED; CORRECTED TASK 3 OPEN; RUNTIME POLICY INACTIVE
Supersedes active route: coordination/mailbox/sent/2026-07-19T22-07-51Z-coordinator-to-all-coordination.md@10cb1d681fd38b6af17ed63a6875dc40c1164b84
Carries forward initial Task 3 route: coordination/mailbox/sent/2026-07-19T21-53-13Z-coordinator-to-all-coordination.md@3318016b16826555e09dc878580adbce231707cb
Authorization source: user-task:one-user-owner-gates-and-owner-center-approved-2026-07-20
Approved design: docs/superpowers/specs/2026-07-20-one-user-owner-gates-and-owner-center-design.md@e091c436b86551efa7a9fe62b55c923818ac3eae
Foundation plan: docs/superpowers/plans/2026-07-20-one-user-owner-policy-foundation.md@e091c436b86551efa7a9fe62b55c923818ac3eae
Accepted Foundation Task 2 commit and immutable target parent: 2d3a76026ae0eff6413ba4270e6191f8fcba6948
Accepted Foundation Task 2 GO: coordination/mailbox/sent/2026-07-19T21-49-54Z-operator2-to-all-verification-report.md@339ba2331425c075a9ac3f56cf9b8868ba7e5a14
Target repository: /Users/hyungkoookkim/evidence-ledger
Target worktree: /Users/hyungkoookkim/evidence-ledger/.worktrees/codex-ppl-offer-decision-m1
Target branch: codex/ppl-offer-decision-m1
Preserved Task 3 production SQL diff SHA-256: 90dd8145373984da56da9741b8d30f31ed76c09e75adfc4c81680d1a21b2cdfc
Selling-package contract SHA-256: cc4d6d552ae75afca04fd2a5e2bb2e92b26812192b0668408908af60a1cf086d
Frozen PPL contract SHA-256: 1c0f4f58632e14243f373c36abb3a78b08807cdd9dccd54eeb3cc8a16d5503a6

## Second diagnostic reconciliation

The first corrective route was applied without changing production SQL: all 14 named legacy nodes now explicitly select the approved private composite policy, the API helper requires its policy argument, and immutable-parent helper defaults remain unchanged. The exact 14-node selector produced 13 passes and one truthful assertion failure:

- `db/tests/test_selling_package_evaluation.py::test_joint_calculation_binds_hs_and_ppl_costs_once`
- stale assertion: `assert ppl["winner"] is True`
- actual: the PPL candidate is `TEST` and is not the winner; the no-PPL candidate is `NEGOTIATE` and is the winner
- reason: the unchanged server ranking precedence places `NEGOTIATE` before `TEST`

This is not a production failure and is not a reason to change policy facts, eligibility, action selection, ranking, or tie-break behavior. The test's primary economic assertions pass. Its old winner assertion depended on the superseded primitive policy and became stale only when the route-required private policy made the corrected action values visible.

The previous correction route authorized only policy opt-ins and froze all assertions, so it cannot truthfully complete. This route supersedes that narrow contradiction and authorizes one exact expectation correction.

## Corrected open slice — Foundation Task 3 only

Director resumes from the preserved unstaged three-path state. Allowed target paths remain exactly:

- `supabase/migrations/20260718000200_selling_package_evaluation.sql`
- `db/tests/test_selling_package_evaluation.py`
- `db/tests/test_selling_package_api.py`

All implementation and explicit policy-isolation requirements from the superseded corrective route remain binding. The only newly authorized edit is inside `test_joint_calculation_binds_hs_and_ppl_costs_once`:

1. Store the existing `_evaluations(...)` result once as `rows` and select the PPL row from it.
2. Preserve the exact economic-value tuple assertion unchanged.
3. Replace only the stale `assert ppl["winner"] is True` expectation with assertions that the PPL row is `TEST` and is not the winner, and that the single winner from `rows` has `ppl_mode == "no_ppl"` and `manual_policy_action == "NEGOTIATE"`.

This expectation pins the already-observed corrected action and existing precedence. Do not change the synthetic values, private action table, action precedence, winner filter, rank expression, tie-break payload, production SQL, or any other assertion.

The production SQL diff must remain byte-identical to SHA-256 `90dd8145373984da56da9741b8d30f31ed76c09e75adfc4c81680d1a21b2cdfc` throughout this correction. The 14 explicit policy opt-ins and required API helper argument remain as routed. `_seed_package` must retain `policy=None` and `experimental_allowed=True`; only the two new Task 3 regressions may override `experimental_allowed`.

## Verification and review

Use only the already-running local listener at `127.0.0.1:54322` and ephemeral synthetic databases. Do not change service state.

After the single expectation correction:

1. Run `db/tests/test_selling_package_evaluation.py::test_joint_calculation_binds_hs_and_ppl_costs_once` and require one pass.
2. Run all 14 exact compatibility nodes from the superseded corrective route and require 14 passes.
3. Run `db/tests/test_selling_package_evaluation.py -k 'test_requires_explicit_experimental or no_ppl_candidate_is_never' -q` and require two passes.
4. Run `db/tests/test_selling_package_domain.py db/tests/test_selling_package_evaluation.py db/tests/test_selling_package_api.py db/tests/test_selling_package_security.py db/tests/test_ppl_offer_evaluation.py -q` and require the complete cumulative suite to pass.
5. Run project `scripts/ci_smoke.py` and require PASS.
6. Recompute both frozen contract hashes and the production SQL diff hash; require all three values bound above.
7. Run `git diff --check` and prove the exact three-path scope. Audit that the second correction changed only the named test expectation and no production or other test bytes.

Before commit, obtain a fresh read-only review of the complete actual three-path diff. It must audit the original Task 3 behavior, all 14 explicit-only policy opt-ins, the corrected one-node action/winner expectation, hidden-default absence, no-PPL fail-closed behavior, and ranking/tie-break non-interference. Do not commit with a Critical or Important finding.

Only after every gate passes may Director commit exactly the three allowed paths. Director then publishes one canonical verify-request binding `2d3a76026ae0eff6413ba4270e6191f8fcba6948..HEAD`, this route, the foundation plan, all three paths, preserved behavioral RED, focused and 14-node results, cumulative suite, hashes, smoke, and fresh review. Assign non-author Operator2 on `gpt-5.6-terra`.

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

Director reads this complete committed superseding route, changes only the stale winner expectation in the named joint-calculation test as specified, completes the full corrected Task 3 verification and fresh review, commits exactly the three routed paths, and publishes the canonical immutable Operator2 request.

Cursor at send: 0
