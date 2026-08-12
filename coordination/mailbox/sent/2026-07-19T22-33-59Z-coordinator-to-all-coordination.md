# Coordinator → All: accept foundation task 3 GO and open corrected foundation task 4

**When:** 2026-07-19T22:33:59Z · **From:** coordinator (online)

Task-board: ledger-one-user-owner-policy-2026-07-20
Task ID: coordinator-one-user-owner-policy-foundation-task4
Status: FOUNDATION TASK 3 ACCEPTED; FOUNDATION TASK 4 OPEN; RUNTIME POLICY INACTIVE
Supersedes active route: coordination/mailbox/sent/2026-07-19T22-14-36Z-coordinator-to-all-coordination.md@3a437a2c6ddb92f9050400f906e01f3441d0116b
Carries forward foundation route: coordination/mailbox/sent/2026-07-19T17-40-34Z-coordinator-to-all-coordination.md@972c3e95610bb597844a2a0dd3d110ce38d47c9d
Authorization source: user-task:one-user-owner-gates-and-owner-center-approved-2026-07-20
Approved design: docs/superpowers/specs/2026-07-20-one-user-owner-gates-and-owner-center-design.md@e091c436b86551efa7a9fe62b55c923818ac3eae
Foundation plan: docs/superpowers/plans/2026-07-20-one-user-owner-policy-foundation.md@e091c436b86551efa7a9fe62b55c923818ac3eae
Accepted foundation base: 5c12411d63a940508a396e4ccbd0f95e072724bf
Accepted Foundation Task 1 commit: 50a28cfe7f78b8cd9095bd018141f91416beb8c8
Accepted Foundation Task 1 GO: coordination/mailbox/sent/2026-07-19T20-52-56Z-operator2-to-all-verification-report.md@51f5ec179b8e64f7d9438aa1baa3f4409d3dd67b
Accepted Foundation Task 2 commit: 2d3a76026ae0eff6413ba4270e6191f8fcba6948
Accepted Foundation Task 2 GO: coordination/mailbox/sent/2026-07-19T21-49-54Z-operator2-to-all-verification-report.md@339ba2331425c075a9ac3f56cf9b8868ba7e5a14
Accepted Foundation Task 3 commit: 8e4e7b8a91369dedf051e73fa11204ebef5128dd
Accepted Foundation Task 3 request: coordination/mailbox/sent/2026-07-19T22-25-57Z-director-to-operator2-verify-request.md@3c7f28664439735577bf0884b136c659fab8dfc6
Accepted Foundation Task 3 GO: coordination/mailbox/sent/2026-07-19T22-30-09Z-operator2-to-all-verification-report.md@692e6cdd4223f4b1818d54eba14325ad898a8b8d
Target repository: /Users/hyungkoookkim/evidence-ledger
Target worktree: /Users/hyungkoookkim/evidence-ledger/.worktrees/codex-ppl-offer-decision-m1
Target branch: codex/ppl-offer-decision-m1
Immutable Task 4 parent: 8e4e7b8a91369dedf051e73fa11204ebef5128dd
Selling-package contract SHA-256: cc4d6d552ae75afca04fd2a5e2bb2e92b26812192b0668408908af60a1cf086d
Frozen PPL contract SHA-256: 1c0f4f58632e14243f373c36abb3a78b08807cdd9dccd54eeb3cc8a16d5503a6

## Foundation Task 3 reconciliation

Operator2 on `gpt-5.6-terra` independently accepted the exact target range `2d3a76026ae0eff6413ba4270e6191f8fcba6948..8e4e7b8a91369dedf051e73fa11204ebef5128dd`. It reproduced the corrected joint node 1/1, explicit compatibility selector 14/14, focused experimental/no-PPL selector 2/2, and cumulative profile 110/110. Target smoke passed; both frozen contract hashes and the preserved SQL-only diff hash matched. The three-path range resets candidate-local choice state, reads linked PPL `experimental_allowed`, forces no-PPL false, builds server-owned composite eligibility, preserves explicit test-policy isolation, and changes no ranking or tie-break code. Foundation Task 3 is closed.

## Plan corrections for Task 4

Two stale plan literals are superseded for executable truth:

1. The cumulative foundation range begins at accepted parent `5c12411d63a940508a396e4ccbd0f95e072724bf`, not the plan's earlier `41d9f1d846d6e0928b520573094ae59846114df5`. Task 1 was lawfully rebased by its committed route onto `5c12411`; all three accepted foundation commits descend from it.
2. `db/tests/test_ppl_offer_security.py` does not exist at the accepted parent or Task 3 head. The real grant/security coverage for the PPL policy surface is `db/tests/test_rls_grants.py`. Use that file in the cumulative gate. Do not invent or substitute a nonexistent test.

The source-boundary preflight at Task 3 head is already exact: `rg -n "<>2|\)=2|두 명"` across the two policy/evaluator migrations returns only `20260717000500_decision_policy.sql:895` and `:898`, the intentionally preserved public v1 two-owner activation wrapper.

## Owner and runtime contract

The selected private deployment has one operational user, one owner account, one persistent authenticated owner session, one laptop, and one installed Windows PWA after the later owner-center/PWA work. There is no user switcher and no second-owner matching workflow in that selected deployment.

The current public `ppl-offer-api-v1` commands and local historical fixtures remain backward-compatible with `two_owner_v1`. This foundation adds private recognition of `single_owner_v1`; it does not yet expose the later owner-center command that creates a real single-owner policy, ruling, or activation. Existing two-account local seed instructions therefore remain factual legacy-development instructions, not the selected production operating model.

The five commission rates and five private risk amounts remain unset, private, and uninferred. Gate B and Gate C are decision-complete but runtime-inactive. Gate D remains `owner_ruling_required` until later owner-center work records the authorized `manual_only` ruling and rereads capability. This task creates no real policy, approval, ruling, activation, booking, or spend.

## Open slice — Foundation Task 4 only

Director owns Foundation Task 4, `Reconcile factual documentation and run the foundation gate`, from immutable parent `8e4e7b8a91369dedf051e73fa11204ebef5128dd`.

Allowed target paths are exactly:

- `ARCHITECTURE.md`
- `DECISIONS.md`
- `OPERATIONS.md`

Work from command-backed source inventory. Do not edit SQL, tests, contracts, code, config, web, iOS, import, or generated artifacts.

### DECISIONS.md

Append one new ADR after ADR-011; do not edit prior ADR text. Record these facts and boundaries:

- `single_owner_v1` is an additive, versioned quorum revision; it does not rewrite historical `two_owner_v1` activation or ruling rows.
- Existing public v1 activation and initial-format commands remain explicit `two_owner_v1` compatibility paths. Private quorum consumers accept `single_owner_v1` only when exactly one current active owner exists and one digest-bound matching approval or ruling exists.
- The approved single-owner risk action order is fixed: `needs_info_required → NEEDS_INFO`, `hard_skip_required → SKIP`, `buy_eligible → BUY`, `test_eligible → TEST`, `negotiate_eligible → NEGOTIATE`, then `always → SKIP`.
- Both PPL-offer and product-first package evaluators calculate the composite eligibility on the server and fail closed if policy selection produces an ineligible BUY, TEST, or NEGOTIATE.
- No real single-owner policy row, private amount, format ruling, approval, or activation is created by Foundation Tasks 1–4. The exact six-row table exists as a closed synthetic test policy in this foundation and becomes a real server-materialized policy only in separately routed owner-center work.

### ARCHITECTURE.md

Update only factual topology and invariants proven by the accepted commits and source inventory:

- Reconcile the selected one-operational-user deployment with retained two-owner v1 compatibility and synthetic two-owner fixtures; do not falsely claim the owner-center or one-owner runtime is already usable.
- Document `approval_quorum` on policy activation and initial-format ruling history, accepted values `two_owner_v1` and `single_owner_v1`, and the private quorum helpers/consumers added by Task 1.
- Document the Task 2 composite fact vocabulary and approved allocation-mode boundary, including mixed-denominator break-even-only behavior and server hard guards.
- Document Task 3 product-first parity: linked choice-set `experimental_allowed` for PPL, false for no-PPL, candidate-local state reset, and unchanged server ranking/tie-break code consuming corrected actions.
- Refresh the verification stamp and source references only where command-backed truth changed. Preserve all unrelated counts and historical statements unless the current source proves them stale.

### OPERATIONS.md

Add a concise foundation verification and safety section:

- State the selected one-user deployment model and the current legacy-development limitation: public v1 seed/activation procedures remain two-owner compatibility paths until owner-center work lands.
- State that local tests use ephemeral synthetic policies and approvals; their activation is not a real or managed runtime activation.
- Record the source-boundary, corrected cumulative test, smoke, contract-hash, and exact-range commands from this route.
- State that private values must be entered only through the future owner-center flow; they are not inferred from workbooks, history, source, defaults, or chat.
- State the no-activation boundary and the later capability reread required after Gate D and policy activation.

Do not add private values, guessed defaults, credentials, UUIDs, workbook figures, managed-project data, or claims that the Windows PWA, owner-center, Gate D ruling, single-owner policy, deployment, or activation already exists.

## Verification and cumulative review

Use only the already-running listener at `127.0.0.1:54322` and ephemeral synthetic databases. If it is unavailable, stop and report; do not change service state.

Verify in this order:

1. Run `rg -n "<>2|\)=2|두 명" supabase/migrations/20260717000500_decision_policy.sql supabase/migrations/20260717000600_offer_evaluation.sql`. Require exactly the two intentionally preserved public-v1 matches at lines 895 and 898, allowing line-number movement only if the source bytes themselves changed before this route; this docs-only task may not change them.
2. Run the corrected complete foundation suite:
   `db/tests/test_ppl_decision_policy.py db/tests/test_ppl_offer_evaluation.py db/tests/test_ppl_offer_cutoff.py db/tests/test_rls_grants.py db/tests/test_selling_package_domain.py db/tests/test_selling_package_evaluation.py db/tests/test_selling_package_api.py db/tests/test_selling_package_security.py -q`.
3. Run project `scripts/ci_smoke.py` and require PASS, including architecture freshness.
4. Recompute both frozen contract hashes and require the values bound above.
5. Run `git diff --check 5c12411d63a940508a396e4ccbd0f95e072724bf..HEAD` and require no output.
6. Inspect `8e4e7b8a91369dedf051e73fa11204ebef5128dd..working-tree` and prove only the three routed documentation paths changed. Inspect `5c12411d63a940508a396e4ccbd0f95e072724bf..working-tree` and prove the cumulative foundation path set is exactly the accepted implementation/test paths plus these three docs, with no contract, API, grant, config, client, import, or generated-file drift.
7. Audit every new factual claim against a current command or exact source site. Confirm `DECISIONS.md` is append-only and no earlier ADR bytes changed.

After all gates pass, Director may commit exactly the three documentation paths with no adjacent changes. Director then publishes one canonical cumulative verify-request binding the exact target range `5c12411d63a940508a396e4ccbd0f95e072724bf..HEAD`, this route, the design and foundation plan, the three accepted task commits/GO reports, exact cumulative path inventory, source-boundary result, complete suite, smoke, hashes, diff checks, and documentation claim audit.

Assign non-author Operator on `gpt-5.6-terra`. Operator independently reviews the actual cumulative range and returns GO, NITS, or FAIL. The review must cover versioned quorum and digest binding, legacy v1 preservation, source-boundary exactness, fixed action precedence, mixed-denominator/allocation behavior, PPL and product-first eligibility, explicit test isolation, documentation truth, contract/grant/API non-expansion, plausible abuse classes, and all no-activation/private-data boundaries.

A cumulative GO accepts only the local Foundation Tasks 1–4 implementation. It does not authorize owner-center implementation, private input, Gate D recording, real policy creation or activation, integration, deployment, or any external effect.

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

Director reads this complete committed route, confirms the target is clean at immutable parent `8e4e7b8a91369dedf051e73fa11204ebef5128dd`, executes only the three-path documentation reconciliation and corrected cumulative foundation gate, commits the docs, and publishes the immutable cumulative request to non-author Operator.

Cursor at send: 0
