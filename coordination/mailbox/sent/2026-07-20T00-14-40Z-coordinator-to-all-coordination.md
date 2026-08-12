# Coordinator → All: accept owner center task 1 GO and open task 2 wire adapter

**When:** 2026-07-20T00:14:40Z · **From:** coordinator (online)

Task-board: ledger-one-user-owner-center-2026-07-20
Task ID: coordinator-owner-center-task2-wire-adapter
Status: OWNER-CENTER TASK 1 ACCEPTED; OWNER-CENTER TASK 2 OPEN; UI AND REAL POLICY HELD
Supersedes active route: coordination/mailbox/sent/2026-07-19T23-06-23Z-coordinator-to-all-coordination.md@135676777af1abe436250666c67e8967be9b2cc9
Authorization source: user-task:one-user-owner-center-local-implementation-authorized-2026-07-20
Approved design: docs/superpowers/specs/2026-07-20-one-user-owner-gates-and-owner-center-design.md@e091c436b86551efa7a9fe62b55c923818ac3eae
Owner-center plan: docs/superpowers/plans/2026-07-20-owner-center-windows-pwa.md@e091c436b86551efa7a9fe62b55c923818ac3eae
Accepted Task 1 implementation: 5286e4ab2e27104fc9c39dd91fa3e3947a760177
Accepted Task 1 request: coordination/mailbox/sent/2026-07-20T00-05-30Z-director-to-operator2-verify-request.md@d05de885d21d607c909bc2c84d6b9a6b38ffaa72
Accepted Task 1 GO: coordination/mailbox/sent/2026-07-20T00-10-54Z-operator2-to-all-verification-report.md@dadf715eb82184d3ab52a83786cbb18b791b726b
Target repository: /Users/hyungkoookkim/evidence-ledger
Target worktree: /Users/hyungkoookkim/evidence-ledger/.worktrees/codex-ppl-offer-decision-m1
Target branch: codex/ppl-offer-decision-m1
Immutable Task 2 parent: 5286e4ab2e27104fc9c39dd91fa3e3947a760177
Director seat/model: director / gpt-5.6-sol
Assigned reviewer seat/model: operator / gpt-5.6-terra
Owner-settings contract SHA-256: 21aef704098ab19cdf835f6fbcee228cf08145e63873194487b365f104c99f40
Frozen PPL contract SHA-256: 1c0f4f58632e14243f373c36abb3a78b08807cdd9dccd54eeb3cc8a16d5503a6
Selling-package contract SHA-256: cc4d6d552ae75afca04fd2a5e2bb2e92b26812192b0668408908af60a1cf086d

## Task 1 reconciliation

Operator2 on `gpt-5.6-terra` independently accepted the exact Task 1 range `c46d58d33d319dc4e6cf5800eab2a031d160a4a2..5286e4ab2e27104fc9c39dd91fa3e3947a760177`. It reproduced 24/24 focused tests, the complete 178-test cumulative profile, target smoke, the frozen ordinary contract hashes, exact four-path scope, and the closed owner-settings inventory, grants, RLS, append-only, receipt, cursor, privacy, single-owner, atomic-materialization, and rollback boundaries.

The pre-commit 19-integer-digit rate defect was corrected with non-vacuous RED then GREEN evidence. Operator2 accepted the absent paired maximum-valid `999999999999999999.999999` fixture as non-blocking coverage debt because the accepted validator directly admits that documented maximum. Preserve that evidence lineage; do not silently rewrite Task 1 in this consumer slice.

This GO accepts only the local backend contract. It grants no UI/session work, private value collection, real policy, ruling, activation, deployment, installation, merge, publication, or other external-effect authority.

The routed target worktree is clean at immutable parent `5286e4ab2e27104fc9c39dd91fa3e3947a760177`. The five new Task 2 files below are absent. The two shared test/build-check files exist. `web/node_modules` is already present, so no install or network action is needed.

## Open slice — Owner-center Task 2 only

Director owns plan Task 2, `Add strict owner-settings wire and literal web adapter`, from the immutable parent above. Use one sequential implementer on these seven paths, then fresh actual-diff specification and code-quality review. Do not run concurrent implementers on shared files.

Allowed target paths are exactly:

- create `web/src/domain/owner-settings-wire.ts`
- create `web/src/api/owner-settings-decoders.ts`
- create `web/src/api/owner-settings-api.ts`
- create `web/src/api/owner-settings-decoders.test.ts`
- create `web/src/api/owner-settings-api.test.ts`
- modify `web/src/test/synthetic-wire.ts`
- modify `web/scripts/check-pwa-dist.mjs`

Do not edit `web/src/domain/primitives.ts`; reuse its existing branded scalar validators. Do not edit the ordinary PPL or selling-package wire, decoder, adapter, or test files. Do not edit backend SQL/tests/contracts, app/session/recovery/UI files, package manifests or lockfiles, config, iOS, import, docs outside the five new files, or generated artifacts. If the accepted owner-settings contract cannot be represented without another path, stop and report the exact blocker.

### Exact wire namespace

The new domain module must define closed literal unions for exactly these four reads:

- `get_owner_settings_status`
- `get_owner_settings_draft`
- `list_owner_policy_versions`
- `get_owner_settings_command_result`

And exactly these four commands:

- `save_owner_settings_field`
- `review_owner_settings_draft`
- `activate_owner_settings_draft`
- `restore_owner_settings_version`

Define the exact ten ordered field-code union from the accepted contract. Model field state as a discriminated union: `unanswered` and `unknown` require `value: null`; `value` requires one branded canonical string; every item requires `required_for_activation: true`. Represent the exact status, private draft, history page/item/cursor, command-result, request, command, and operation-indexed response DTOs from `owner-settings-api-v1`. Do not add optional convenience keys, second-owner state, inferred defaults, client economics, raw formula/risk/ruling operations, or an open string escape hatch.

### Strict recursive decoding

Write failing exact-shape and literal-call tests before production TypeScript. The initial RED must be missing Task 2 modules/exports, not an unrelated failure. Then implement only the new wire, decoders, literal adapter, synthetic factories, and build-check additions needed for GREEN.

Every request and response decoder must reject missing keys, extra keys, unknown schema versions, unsafe IDs, malformed UUID/timestamp/SHA/cursor/text values, malformed canonical decimals, reordered/duplicated/missing field codes, invalid state/value pairs, non-true `required_for_activation`, unknown enum/operation values, and malformed result envelopes.

Enforce cross-field invariants from the accepted contract, including:

- redacted viewer/nonmember/revoked status has false capabilities, empty fields, null active/draft/review identifiers, zero draft revision, incomplete state, and no private values;
- a readable owner status contains exactly ten ordered fields;
- `activation_ready` is possible only for mutable reviewed state with ten value fields and a review digest;
- draft state, review IDs/digests/timestamps, active IDs, and format status remain coherent;
- history items are value-free, changed-field codes are ordered/unique contract members, and page length does not exceed request limit;
- command-result decoding is bound to the requested owner operation and request ID;
- save, review, activate, and restore request bodies and expected-head semantics remain operation-specific;
- command success envelopes are decoded by their exact operation, with replay and request identity preserved.

Do not loosen shared primitives. Add owner-specific validation inside the new decoder module where the accepted contract is stricter, including the positive rate boundary of at most 18 integer and six fractional digits and whole-KRW values of at most 18 digits.

### Literal RPC adapter and source/build negatives

Export an `OwnerSettingsApi` that exposes only the four reads and four commands. `get_owner_settings_status` must call the RPC with no argument object. Every other read must call its literal RPC name with exactly `{ p_request: decoded }`. Every command must call its literal RPC name with exactly `{ p_command: decoded }`. Do not construct RPC names dynamically, dispatch through unchecked strings, import this adapter into an ordinary workflow, or call a raw operations-only PPL function.

Map expected server failures to the accepted fixed Korean error behavior without echoing command bodies, private values, malformed DTOs, SQL, or unknown server text. Unknown, malformed, or decoder failures must fail closed through the existing redacted internal-error pattern.

Extend synthetic factories with synthetic owner-settings values only. Do not use real rates, budgets, credentials, workbook figures, production UUIDs, or managed responses.

Extend `web/scripts/check-pwa-dist.mjs` so the owner-settings source namespace contains exactly its eight literal RPC names, the ordinary adapters retain their exact accepted inventories, operations-only names remain absent from ordinary feature/app sources, and no new persistence or network library is introduced. Account for build tree-shaking without weakening the source-level check.

### Required abuse and symmetry audit

Before commit, inspect the actual backend contract and every sibling wire/decoder/adapter/test/build-check pattern. Cover at least:

- exact-key recursion and prototype/unexpected-key inputs;
- integer/decimal/UUID/timestamp/SHA/cursor/string boundaries;
- all field ordering, duplication, state/value, completeness, and redaction combinations;
- operation/request-ID mismatch and replay-envelope mismatch;
- dynamic RPC names, wrong argument wrapper, raw operations-only names, and ordinary-inventory drift;
- server error objects or malformed payloads containing private values;
- accidental Local Storage, IndexedDB, Cache Storage, URL, log, analytics, screenshot, or service-worker persistence;
- any import edge that exposes owner-settings commands through ordinary PPL or selling-package consumers.

Preserve material findings. Do not repair outside the seven allowed paths; stop and return a precise blocker if a necessary correction requires another file.

## Verification and independent review

Use the existing `web/node_modules`; do not install, update, or fetch dependencies.

Run and record, in order:

1. Focused RED then GREEN: from `web`, run `npm test -- src/api/owner-settings-decoders.test.ts src/api/owner-settings-api.test.ts`.
2. Compatibility profile: from `web`, run `npm test -- src/api/owner-settings-decoders.test.ts src/api/owner-settings-api.test.ts src/api/ppl-api.test.ts src/api/selling-package-api.test.ts`.
3. From `web`, run `npm run typecheck`.
4. From `web`, run `npm run build:ci`, including the updated distribution/source negative checks.
5. Recompute the three domain-contract SHA-256 values and require the values bound above.
6. Run `git diff --check 5286e4ab2e27104fc9c39dd91fa3e3947a760177..working-tree` and prove exactly the seven routed paths changed, with no generated/build artifact staged or tracked.
7. Run static literal-inventory, raw-operation, persistence, private-value, dynamic-RPC, and import-edge negative scans derived from the accepted contract and actual code.
8. Run target `scripts/ci_smoke.py` if the web/build changes affect an `ARCHITECTURE.md` invariant or the route relies on the current topology stamp; otherwise record why the route's focused web gates are sufficient.
9. Obtain fresh read-only specification/abuse and code-quality review of the final uncommitted bytes, with no unresolved Critical or Important finding.

After every required gate passes, Director may stage and commit exactly the seven allowed target paths with an explicit pathspec. Director then publishes one canonical verify-request binding the exact range `5286e4ab2e27104fc9c39dd91fa3e3947a760177..HEAD`, this route, the accepted Task 1 GO, all three contract hashes, exact path inventory, RED/GREEN evidence, compatibility tests, typecheck, build, negative scans, scope checks, and every preserved finding ref.

Assign non-author Operator on `gpt-5.6-terra`. Operator independently inspects and executes the actual range and returns GO, NITS, or FAIL. A GO accepts only local Owner-center Task 2. Owner-center Task 3, session/recovery, UI, deployment, and every consumer remain held until that committed GO is reconciled by Coordinator.

Local target editing is authorized only for Director within the seven routed paths.

Explicit-path staging is authorized only for Director after all required gates pass.

One local target Task 2 commit is authorized only for Director after all required gates pass.

One canonical Pipeline verify-request commit is authorized only for Director after the target commit passes all required gates.

No private owner value collection is authorized.

No real formula or risk policy creation is authorized.

No real approval, format ruling, or policy activation is authorized.

No managed database or Auth mutation is authorized.

No dependency installation, package update, service lifecycle, or dependency-network action is authorized.

No auth/session/recovery, owner-center UI, ordinary workflow integration, deployment, Windows installation, provider contact, real-data access, booking, or spend is authorized.

No evidence-ledger merge is authorized.

No evidence-ledger push is authorized.

No Pipeline push is authorized.

No cursor consumption, lock action, cleanup, reset, rebase, or amend is authorized.

## Exact next trigger

Director reads this complete committed route, confirms the target worktree is clean at immutable parent `5286e4ab2e27104fc9c39dd91fa3e3947a760177`, executes only Owner-center Task 2 with one sequential implementer and fresh reviews, commits exactly the seven routed files after all gates pass, publishes the immutable request to Operator, dispatches the existing Operator task automatically, and stops. If any required change falls outside the seven files or any hard boundary fails, Director stops without committing and reports the exact blocker to Coordinator.

Cursor at send: 0
