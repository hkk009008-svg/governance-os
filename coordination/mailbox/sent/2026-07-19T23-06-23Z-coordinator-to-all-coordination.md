# Coordinator → All: accept foundation GO and open owner-center task 1

**When:** 2026-07-19T23:06:23Z · **From:** coordinator (online)

Task-board: ledger-one-user-owner-center-2026-07-20
Task ID: coordinator-owner-center-task1-backend
Status: FOUNDATION CUMULATIVE GO ACCEPTED; OWNER-CENTER TASK 1 OPEN; REAL POLICY INACTIVE
Supersedes active route: coordination/mailbox/sent/2026-07-19T22-33-59Z-coordinator-to-all-coordination.md@73ba5838fc3136a6256ed029b9e16035de859a5b
Authorization source: user-task:one-user-owner-center-local-implementation-authorized-2026-07-20
Approved design: docs/superpowers/specs/2026-07-20-one-user-owner-gates-and-owner-center-design.md@e091c436b86551efa7a9fe62b55c923818ac3eae
Owner-center plan: docs/superpowers/plans/2026-07-20-owner-center-windows-pwa.md@e091c436b86551efa7a9fe62b55c923818ac3eae
Accepted foundation cumulative request: coordination/mailbox/sent/2026-07-19T22-51-20Z-director-to-operator-verify-request.md@41c31beb1fcf0c5ccdfb9ec26ff7554c3a85b54a
Accepted foundation cumulative GO: coordination/mailbox/sent/2026-07-19T23-03-15Z-operator-to-all-verification-report.md@52391738ea69fd3b4cab1a50bd2c0c9c979bf52d
Target repository: /Users/hyungkoookkim/evidence-ledger
Target worktree: /Users/hyungkoookkim/evidence-ledger/.worktrees/codex-ppl-offer-decision-m1
Target branch: codex/ppl-offer-decision-m1
Immutable Task 1 parent: c46d58d33d319dc4e6cf5800eab2a031d160a4a2
Director seat/model: director / gpt-5.6-sol
Assigned reviewer seat/model: operator2 / gpt-5.6-terra
Selling-package contract SHA-256: cc4d6d552ae75afca04fd2a5e2bb2e92b26812192b0668408908af60a1cf086d
Frozen PPL contract SHA-256: 1c0f4f58632e14243f373c36abb3a78b08807cdd9dccd54eeb3cc8a16d5503a6

## Foundation reconciliation

Operator on `gpt-5.6-terra` independently accepted the exact cumulative foundation range `5c12411d63a940508a396e4ccbd0f95e072724bf..c46d58d33d319dc4e6cf5800eab2a031d160a4a2` with no findings. It reproduced the exact eleven-path scope, the two intentional legacy public-v1 two-owner matches, 154/154 synthetic database tests, target smoke, frozen contract hashes, append-only ADR state, private helper revocation, server-owned eligibility, and the no-activation boundary. The foundation prerequisite in the owner-center plan is met.

This GO accepts only the local foundation. It supplies no private values, real policy, ruling, activation, deployment, installation, merge, publication, or other external-effect authority.

The routed target worktree is clean at immutable parent `c46d58d33d319dc4e6cf5800eab2a031d160a4a2`. All four Task 1 paths below are absent at that parent. The normal evidence-ledger checkout has unrelated untracked `.vscode/`; do not touch or absorb it.

## Open slice — Owner-center Task 1 only

Director owns plan Task 1, `Implement the append-only owner-settings contract and API`, from the immutable parent above. Use the target repository's orchestration and trust-fence discipline: one sequential implementer on these paths, then fresh actual-diff spec and code-quality review. Do not run concurrent implementers on shared files.

Allowed target paths are exactly these four new files:

- `docs/domain/owner-settings-api-v1.md`
- `supabase/migrations/20260720000100_owner_settings_api.sql`
- `db/tests/test_owner_settings_api.py`
- `db/tests/test_owner_settings_security.py`

Do not edit any existing target file. In particular, do not edit either frozen ordinary adapter contract, any existing migration or test, web, iOS, import, config, generated artifacts, architecture/operations/decision docs, or real-data path.

### Closed owner-settings contract

Author the normative contract first. The read RPC inventory is exactly:

- `get_owner_settings_status`
- `get_owner_settings_draft`
- `list_owner_policy_versions`
- `get_owner_settings_command_result`

The command operation inventory is exactly:

- `save_owner_settings_field`
- `review_owner_settings_draft`
- `activate_owner_settings_draft`
- `restore_owner_settings_version`

The ten ordered private field codes are exactly:

- `linear_rate_regular`
- `linear_rate_half_special`
- `linear_rate_full_special`
- `linear_rate_direct_purchase`
- `linear_rate_half_split`
- `choice_set_budget_krw`
- `monthly_budget_krw`
- `downside_limit_krw`
- `experimental_budget_krw`
- `risk_reserve_krw`

Every new owner starts with all ten fields in `unanswered` state with null values. A field may become `unknown` with a null value or `value` with one validated canonical value. Do not invent, infer, prefill, log, cache, or persist a default. Rate values are positive canonical decimal strings within the existing `numeric(30,12)` boundary and at most six fractional digits. KRW values are nonnegative whole-KRW strings of at most 18 digits. Reject extra or duplicate field codes, missing codes, negative zero, exponent notation, excessive digits, and invalid state/value combinations.

### Append-only server behavior

Write failing focused API/security tests before production SQL; the initial RED must be missing Task 1 surfaces, not an unrelated failure. Then implement only the migration needed to make those tests pass.

Create immutable append-only draft revisions and review rows using the existing update/delete/truncate blockers. Bind every fields digest to the canonical ten-item order. Enforce RLS, no direct table access, private sequences, authenticated current-owner reads, redacted nonmember capability state, and denial for viewer, nonmember, revoked, zero-owner, and multiple-owner mutation paths.

Use the existing command receipt primitives, one UUID request ID, exact expected-head binding, actor-scoped replay, and a draft-chain advisory lock. Recovery may expose only the fixed result envelope for the original actor, operation, and request ID; it must never make a command body or private field value recoverable.

`save_owner_settings_field` appends one successor revision. `review_owner_settings_draft` requires all ten fields in `value` state and binds the exact current draft digest. `restore_owner_settings_version` copies one historical formula/risk version into a new draft without changing the active policy. History returns IDs, timestamps, and changed field names, not old or new private values.

`activate_owner_settings_draft` must be one atomic server transaction. It locks and revalidates the draft, review digest, unchanged active-policy head, and exactly one current active owner, then materializes the already-approved formula metadata, five linear-rate rules, risk metadata and exact six-row action truth table, one formula approval, one risk approval, one `manual_only` ruling, and one `single_owner_v1` activation. All IDs, digests, membership facts, and activation bindings are server-derived. Any failure rolls back every row. A successful synthetic test activation makes no booking, managed mutation, deployment, or real runtime activation.

Extend the receipt operation constraint with exactly the four owner-settings command names. The owner-settings facade must not expose or invoke raw formula, risk, ruling, or activation commands. Preserve both ordinary PPL and selling-package contract bytes and operation inventories exactly.

### Required abuse and symmetry audit

Before commit, inspect definitions, writes, callers, grants, sibling append-only tables, command receipt constraints, recovery filters, membership checks, formula/risk validators, digest producers, active-head locks, activation consumers, and rollback behavior. Cover at least:

- zero, one, and multiple current active owners;
- viewer, nonmember, revoked, stale actor, and actor-swapped replay;
- incomplete, unknown, malformed, reordered, duplicated, and extra fields;
- stale draft, stale review digest, stale expected head, and concurrent mutation;
- direct table access, direct RPC misuse, grant leakage, and helper exposure;
- request-ID reuse across actor or operation;
- partial materialization or activation on every failure path;
- history/restore leaking values or changing the active policy;
- any widening of the frozen ordinary adapter or product API inventories.

Preserve material findings. Do not repair outside the four allowed paths; stop and return a precise blocker if a necessary correction requires another file.

## Verification and review

Use only the already-running listener at `127.0.0.1:54322` and test-created ephemeral synthetic databases. If the listener is unavailable, stop and report; do not change service state.

Run and record, in order:

1. Focused RED and then GREEN for `db/tests/test_owner_settings_api.py db/tests/test_owner_settings_security.py`.
2. The complete cumulative database profile: the two new owner-settings tests plus `db/tests/test_ppl_decision_policy.py db/tests/test_ppl_offer_evaluation.py db/tests/test_ppl_offer_cutoff.py db/tests/test_rls_grants.py db/tests/test_selling_package_domain.py db/tests/test_selling_package_evaluation.py db/tests/test_selling_package_api.py db/tests/test_selling_package_security.py`.
3. Target `scripts/ci_smoke.py`.
4. Both frozen domain-contract SHA-256 checks and require the values bound above.
5. `git diff --check c46d58d33d319dc4e6cf5800eab2a031d160a4a2..working-tree` and exact path inventory; require exactly the four routed paths and no existing-file drift.
6. Static closed-inventory, grant/revoke, persistence, private-value, and raw-operation negative scans derived from the normative contract and actual migration.
7. Fresh actual-diff spec and code-quality review after GREEN, with no unresolved Critical or Important finding.

After every gate passes, Director may stage and commit exactly the four allowed target paths with an explicit pathspec. Director then publishes one canonical verify-request binding the exact range `c46d58d33d319dc4e6cf5800eab2a031d160a4a2..HEAD`, this route, the accepted foundation GO, the design and owner-center plan, exact path inventory, RED/GREEN evidence, cumulative suite, smoke, hashes, static audits, and all preserved finding refs.

Assign non-author Operator2 on `gpt-5.6-terra`. Operator2 independently inspects and executes the actual range and returns GO, NITS, or FAIL. A GO accepts only local Owner-center Task 1. Owner-center Task 2 and every consumer remain held until that committed GO is reconciled by Coordinator.

Local target editing is authorized only for Director within the four routed paths.

Explicit-path staging is authorized only for Director after all required gates pass.

One local target Task 1 commit is authorized only for Director after all required gates pass.

One canonical Pipeline verify-request commit is authorized only for Director after the target commit passes all required gates.

No private owner value collection is authorized.

No real formula or risk policy creation is authorized.

No real approval, format ruling, or policy activation is authorized.

No managed database or Auth mutation is authorized.

No service lifecycle or dependency-network action is authorized.

No web, PWA, deployment, Windows installation, provider contact, real-data access, booking, or spend is authorized.

No evidence-ledger merge is authorized.

No evidence-ledger push is authorized.

No Pipeline push is authorized.

No cursor consumption, lock action outside the transaction-local advisory lock, cleanup, reset, rebase, or amend is authorized.

## Exact next trigger

Director reads this complete committed route, confirms the target worktree is clean at immutable parent `c46d58d33d319dc4e6cf5800eab2a031d160a4a2`, executes only Owner-center Task 1 with one sequential implementer and fresh reviews, commits exactly the four routed files after all gates pass, publishes the immutable request to Operator2, dispatches the existing Operator2 task automatically, and stops. If any required change falls outside the four files or any hard boundary fails, Director stops without committing and reports the exact blocker to Coordinator.

Cursor at send: 0
