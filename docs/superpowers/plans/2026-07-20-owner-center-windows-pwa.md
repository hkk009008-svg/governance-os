# Owner Center API and Windows PWA Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a protected owner-settings API and Korean status-plus-step owner center that collects the one user's missing private configuration and performs only an explicit reviewed local activation command.

**Architecture:** A new `owner-settings-api-v1` is separate from both frozen ordinary adapters. Append-only server draft revisions hold private configuration; review binds a complete draft digest; activation atomically materializes formula/risk versions, one-owner approvals, `manual_only`, and a `single_owner_v1` activation. The PWA stores only auth session state and actor-scoped recovery metadata; all owner values remain server-side or in memory.

**Tech Stack:** PostgreSQL 15/PL/pgSQL, psycopg/pytest, React 19, TypeScript 7, Vite 8, Supabase JS 2, Vitest/Testing Library/Playwright.

## Global Constraints

- Design authority is `docs/superpowers/specs/2026-07-20-one-user-owner-gates-and-owner-center-design.md@e0f4e43ce653dee37efed3cd73d90b7c5cc92779`.
- This plan starts only after the complete foundation plan `docs/superpowers/plans/2026-07-20-one-user-owner-policy-foundation.md` receives cumulative non-author GO.
- The target worktree stays `/Users/hyungkoookkim/evidence-ledger/.worktrees/codex-ppl-offer-decision-m1`.
- Use exactly one current owner account; retain nonmember/revoked/viewer states only for authorization negatives and wire compatibility.
- UI copy is natural Korean; stable operation, enum, reason, and field codes remain English.
- No invented defaults. The ten private numeric fields begin `unanswered` and may be saved as `unknown` or `value`.
- Activation requires all ten fields in `value` state, a current review digest, exactly one current active owner, and an unchanged active-policy head.
- Preserve the frozen PPL and selling-package adapter inventories byte-for-byte. The new adapter is a third, separate closed namespace.
- Command bodies, private values, DTOs, and responses never enter Local Storage, IndexedDB, Cache Storage, URLs, service-worker messages, analytics, logs, screenshots, or committed fixtures.
- `record_selling_package_owner_decision` remains intent-only; this plan adds no booking-capable product surface.
- Local implementation and synthetic activation tests grant no managed-project mutation, real policy activation, deployment, physical installation, real-data use, booking, integration, or publication.
- Each task receives a separate actual-range non-author Operator verdict before its consumer starts.

---

## Closed contract inventory

The owner-settings read RPCs are exactly:

```text
get_owner_settings_status
get_owner_settings_draft
list_owner_policy_versions
get_owner_settings_command_result
```

The owner-settings command operations are exactly:

```text
save_owner_settings_field
review_owner_settings_draft
activate_owner_settings_draft
restore_owner_settings_version
```

The private field codes are exactly:

```text
linear_rate_regular
linear_rate_half_special
linear_rate_full_special
linear_rate_direct_purchase
linear_rate_half_split
choice_set_budget_krw
monthly_budget_krw
downside_limit_krw
experimental_budget_krw
risk_reserve_krw
```

Each field state is `unanswered | unknown | value`. Rate values are canonical
positive decimal strings accepted by the existing `numeric(30,12)` boundary,
with at most six fractional digits.
KRW values are nonnegative whole-KRW strings of at most 18 digits. Only
`state=value` carries a non-null value.

## File map

- Create: `docs/domain/owner-settings-api-v1.md` — normative exact wire contract.
- Create: `supabase/migrations/20260720000100_owner_settings_api.sql` — append-only drafts, reviews, history projections, aggregate commands, RLS/grants.
- Create: `db/tests/test_owner_settings_api.py` — command/read/replay/activation behavior.
- Create: `db/tests/test_owner_settings_security.py` — membership, RLS/grant, redaction, concurrency, and persistence negatives.
- Modify: `web/src/domain/primitives.ts` — reuse only existing branded scalar validators.
- Create: `web/src/domain/owner-settings-wire.ts` — exact DTOs and operation unions.
- Create: `web/src/api/owner-settings-decoders.ts` — strict recursive decoders.
- Create: `web/src/api/owner-settings-api.ts` — literal four-read/four-command RPC adapter.
- Create: corresponding API/decoder tests and synthetic factories.
- Create: `web/src/features/auth/`, `web/src/features/recovery/`, and `web/src/app/AppController.ts` from the already approved Task-5B session/recovery slice.
- Create: `web/src/features/owner-settings/` — status, step form, review, history, restore, and tests.
- Modify: `web/src/app/App.tsx`, `web/src/api/errors.ts`, `web/scripts/check-pwa-dist.mjs`, and factual Korean/operations docs.

### Task 1: Implement the append-only owner-settings contract and API

**Files:**
- Create: `docs/domain/owner-settings-api-v1.md`
- Create: `supabase/migrations/20260720000100_owner_settings_api.sql`
- Create: `db/tests/test_owner_settings_api.py`
- Create: `db/tests/test_owner_settings_security.py`

**Interfaces:**
- Consumes: foundation quorum helpers, formula/risk validators/digests, command receipt primitives, membership, and current activation head.
- Produces: the exact four-read/four-command contract above, immutable draft/review rows, and one atomic single-owner activation path.

- [ ] **Step 1: Write the normative contract before production SQL.**

The contract defines schema version 1, exact request/response keys, Korean
expected-error mapping, cursor binding, operation-indexed recovery, and the
following draft item shape:

```json
{
  "code": "monthly_budget_krw",
  "state": "unknown",
  "value": null,
  "required_for_activation": true
}
```

Status data contains exactly contract ID, member state, can-read/can-mutate,
active IDs, active format status, draft ID/revision/state, review digest,
`activation_ready`, and ten field items in contract order. It contains no
second-owner count or matching status.

- [ ] **Step 2: Write failing API and security tests.**

Cover exact shapes plus these named behaviors and outcomes:

- `test_new_owner_starts_with_ten_unanswered_fields`: exactly ten ordered
  items, every state `unanswered`, every value null, activation not ready.
- `test_save_unknown_persists_no_value_and_remains_incomplete`: the selected
  item becomes `unknown`, value stays null, and the old revision is unchanged.
- `test_save_value_creates_append_only_draft_revision`: one successor is
  created with the validated canonical value and prior bytes remain unchanged.
- `test_review_rejects_any_unanswered_or_unknown_field`: fixed incomplete-state
  error, no review row.
- `test_activation_materializes_exact_formula_risk_manual_only_and_single_owner_quorum`:
  exact formula/risk rows, one approval each, manual-only ruling, and one
  `single_owner_v1` activation are committed atomically.
- `test_activation_rejects_zero_or_multiple_current_owners`: no partial rows.
- `test_activation_rejects_stale_draft_review_or_active_head`: fixed stale
  error and unchanged active policy.
- `test_restore_copies_history_to_new_draft_without_changing_active_policy`:
  one new draft, no activation change.
- `test_command_replay_is_actor_scoped_and_body_is_not_recoverable`: replayed
  envelope only for the original actor/operation/request ID.
- `test_viewer_nonmember_and_revoked_cannot_read_private_draft_or_mutate` and
  `test_direct_table_access_and_mutation_are_denied`: permission failure with
  no leaked field values.

Run:

```bash
env -u GIT_INDEX_FILE .venv/bin/python -m pytest \
  db/tests/test_owner_settings_api.py \
  db/tests/test_owner_settings_security.py -q
```

Expected RED: missing migration surfaces only.

- [ ] **Step 3: Create immutable draft and review tables.**

Create `decision.owner_settings_draft_revisions` with `id`, unique nullable
`supersedes_id`, nullable `base_activation_id`, exact `fields jsonb`,
`fields_sha256`, `created_by`, and `created_at`. Create
`decision.owner_settings_reviews` with `draft_revision_id`, `fields_sha256`,
`reviewed_by`, `review_reason`, and `reviewed_at`. Both use the existing
append-only update/delete/truncate blockers, RLS enabled, no direct grants, and
private identity sequences.

The validator requires exactly the ten contract field codes once each, sorts
them into contract order before hashing, enforces the state/value invariant,
and rejects extra keys, negative zero, exponent notation, excessive digits,
and private text outside fixed reason fields.

- [ ] **Step 4: Implement literal reads and cursor binding.**

`get_owner_settings_status()` takes no argument. The other reads receive
exactly `{p_request: request}`. Draft reads require the authenticated current
owner; status may return a redacted nonmember/revoked capability shape without
draft values. History returns field-name changes and immutable IDs/timestamps,
not old/new private values. Every cursor binds actor, surface, filters,
snapshot, last timestamp, and last ID.

- [ ] **Step 5: Implement field save, review, and restore commands.**

Every command uses `app.ppl_begin_command`/`ppl_finish_command`, exact
`expected_head_id`, one UUID request ID, advisory lock on the owner-settings
draft chain, and actor-scoped replay.

`save_owner_settings_field` copies the current ten-item array, replaces exactly
one item, validates and hashes the complete result, and appends one revision.
`review_owner_settings_draft` rejects any state other than `value`, records the
exact draft hash, and returns a review ID/digest. `restore_owner_settings_version`
copies a selected historical formula/risk pair into a new draft and leaves the
active activation unchanged.

- [ ] **Step 6: Implement atomic single-owner activation.**

`activate_owner_settings_draft` locks the draft, review, current membership,
and current policy head. It revalidates the review digest and exactly one active
owner, then materializes:

```text
formula metadata:
  target_metric_code=incremental_campaign_contribution_krw
  scenario_input_net_of_returns=true
  package_allocation_mode=campaign_level_action_no_target_break_even
  timing_basis=target_slot_with_booked_at_budget_commitment
  scenario_mode=target_lines
  counterfactual_method=owner_manual_without_ppl
  scenario_input_scale=6

each of five formula rules:
  formula_kind=linear_rate
  metric_code=incremental_settled_sales
  unit_code=krw
  scale=6
  rounding_mode=half_up
  rounding_point=final_only
  final_money_scale=0
  threshold_basis=post_round
  break_even_unit_rounding=not_applicable

risk metadata:
  manual_buy_allowed=true
  pilot_booking_allowed=true
  business_timezone=Asia/Seoul
  monthly_budget_basis=booked_at_calendar_month
  action_truth_table=the approved six-row composite table

format:
  format_status=manual_only
  approval_quorum=single_owner_v1
```

It inserts one formula approval, one risk approval, one `manual_only` ruling,
and one activation event labeled `single_owner_v1`, all bound to server-derived
digests and the authenticated actor. Any failure rolls back the complete
transaction. Success does not make a booking or deployment.

- [ ] **Step 7: Register recovery and enforce the closed operation inventory.**

Extend the command receipt constraint with exactly the four owner-settings
operations. `get_owner_settings_command_result` accepts only those four names.
Source and DB tests reject raw formula/risk/activation operations from the
owner-settings client contract.

- [ ] **Step 8: Run the complete backend gate.**

```bash
env -u GIT_INDEX_FILE .venv/bin/python -m pytest \
  db/tests/test_owner_settings_api.py \
  db/tests/test_owner_settings_security.py \
  db/tests/test_ppl_decision_policy.py \
  db/tests/test_ppl_offer_evaluation.py \
  db/tests/test_selling_package_evaluation.py \
  db/tests/test_selling_package_api.py \
  db/tests/test_selling_package_security.py -q
env -u GIT_INDEX_FILE .venv/bin/python scripts/ci_smoke.py
```

- [ ] **Step 9: Commit and request independent review.**

```bash
env -u GIT_INDEX_FILE git add -- \
  docs/domain/owner-settings-api-v1.md \
  supabase/migrations/20260720000100_owner_settings_api.sql \
  db/tests/test_owner_settings_api.py \
  db/tests/test_owner_settings_security.py
env -u GIT_INDEX_FILE git commit -m "feat(policy): add one-user owner settings API"
```

### Task 2: Add strict owner-settings wire and literal web adapter

**Files:**
- Create: `web/src/domain/owner-settings-wire.ts`
- Create: `web/src/api/owner-settings-decoders.ts`
- Create: `web/src/api/owner-settings-api.ts`
- Create: `web/src/api/owner-settings-decoders.test.ts`
- Create: `web/src/api/owner-settings-api.test.ts`
- Modify: `web/src/test/synthetic-wire.ts`
- Modify: `web/scripts/check-pwa-dist.mjs`

**Interfaces:**
- Consumes: `owner-settings-api-v1` and existing strict scalar/RPC invoker helpers.
- Produces: `OwnerSettingsApi`, exact read/command unions, DTOs, and strict decoders for session/UI tasks.

- [ ] **Step 1: Write failing exact-shape and literal-call tests.**

Tests reject missing/extra keys, unsafe IDs, malformed canonical decimals,
state/value mismatches, duplicate/missing field codes, unordered server items,
unexpected operations, dynamic RPC names, raw operations-only PPL names, and
non-redacted errors. Adapter tests assert capabilities use no args and every
other call uses exactly `p_request` or `p_command`.

- [ ] **Step 2: Run focused web RED.**

```bash
cd web
npm test -- src/api/owner-settings-decoders.test.ts \
  src/api/owner-settings-api.test.ts
```

- [ ] **Step 3: Implement exact types and recursive decoders.**

Use discriminated item types:

```ts
type OwnerSettingField =
  | { code: OwnerSettingFieldCode; state: "unanswered" | "unknown"; value: null; required_for_activation: true }
  | { code: OwnerSettingFieldCode; state: "value"; value: CanonicalDecimal; required_for_activation: true };
```

The adapter exports only the four reads and four commands. It is not imported
by `selling-package-api.ts` or `ppl-api.ts`.

- [ ] **Step 4: Add built-source negative checks.**

`check-pwa-dist.mjs` verifies ordinary feature bundles contain no raw
operations-only PPL names, the owner-settings namespace contains only its eight
literal names, and no new persistence/network library appears.

- [ ] **Step 5: Run and commit.**

```bash
cd web
npm test -- src/api/owner-settings-decoders.test.ts \
  src/api/owner-settings-api.test.ts src/api/ppl-api.test.ts \
  src/api/selling-package-api.test.ts
npm run typecheck
npm run build:ci
cd ..
env -u GIT_INDEX_FILE git add -- web
env -u GIT_INDEX_FILE git commit -m "feat(web): add strict owner settings adapter"
```

### Task 3: Complete session, capability, and separated recovery foundations

**Files:**
- Create/modify exactly the Task-5B auth, recovery, and controller files listed in `docs/superpowers/plans/2026-07-17-ppl-offer-task5-windows-pwa.md` under `Task 5B`.
- Modify: `web/src/features/recovery/pending-journal.ts`
- Modify: `web/src/features/recovery/command-runner.ts`
- Test: corresponding Task-5B tests plus owner-settings recovery cases.

**Interfaces:**
- Consumes: all three literal adapters and Supabase auth.
- Produces: one persistent owner session, capability-before-mutation rendering, and disjoint recovery namespaces for selling workflow and owner settings.

The pending metadata type becomes exactly:

```ts
export type PendingNamespace = "selling_workflow" | "owner_settings";

export interface PendingMetadata {
  readonly namespace: PendingNamespace;
  readonly operation: SellingWorkflowCommandOperation | OwnerSettingsCommandOperation;
  readonly request_id: CanonicalUuid;
  readonly created_at: UtcTimestamp;
}
```

- [ ] **Step 1: Execute the existing Task-5B failing-test step unchanged.**

Use its exact file list and commands. Add cases proving no signup or user
switcher, owner-settings status loads after auth, and mutation controls remain
hidden until all applicable capabilities decode.

- [ ] **Step 2: Keep recovery namespaces disjoint.**

Persist only `{namespace, operation, request_id, created_at}` where namespace
is `selling_workflow | owner_settings`. The exact actor UUID remains in the
storage key, not the value. Command bodies stay memory-only. An unresolved
owner-settings entry blocks owner-settings mutation but not read-only status;
it never admits an ordinary operation and vice versa.

- [ ] **Step 3: Implement transition clearing and one-user shell.**

Logout, signed-out/refresh failure, actor change, `pageshow`, offline, and
transport loss synchronously clear all business/draft DTOs before rendering a
new route. Keep the one authenticated owner session; add no profile chooser,
second-owner state, or app PIN.

Capability gating is deliberately split to avoid a setup deadlock. An active
owner with `owner-settings can_mutate=true` may edit the owner-center draft
while PPL/selling-package policy is inactive. Policy inactivity continues to
block selling-decision mutations and calculated recommendations. A viewer,
nonmember, revoked member, offline session, or unresolved owner-settings journal
cannot mutate the owner center.

- [ ] **Step 4: Run Task-5B and owner recovery tests.**

```bash
cd web
npm test -- src/features/auth/session.test.ts \
  src/features/recovery/pending-journal.test.ts \
  src/features/recovery/command-runner.test.ts \
  src/app/AppController.test.ts
npm run typecheck
```

- [ ] **Step 5: Commit and request independent review.**

```bash
env -u GIT_INDEX_FILE git add -- web/src/app web/src/features/auth \
  web/src/features/recovery
env -u GIT_INDEX_FILE git commit -m "feat(web): add one-user session and recovery"
```

### Task 4: Build the Korean status-plus-step owner center

**Files:**
- Create: `web/src/features/owner-settings/OwnerSettingsPage.tsx`
- Create: `web/src/features/owner-settings/OwnerSettingsStatus.tsx`
- Create: `web/src/features/owner-settings/OwnerSettingStep.tsx`
- Create: `web/src/features/owner-settings/OwnerSettingsReview.tsx`
- Create: `web/src/features/owner-settings/OwnerSettingsHistory.tsx`
- Create: `web/src/features/owner-settings/copy.ts`
- Create: matching component/integration tests.
- Modify: `web/src/app/App.tsx`

**Interfaces:**
- Consumes: session/controller, `OwnerSettingsApi`, command runner, and exact server status/draft/history DTOs.
- Produces: the selected Korean owner-center experience; no local calculations or policy authority.

- [ ] **Step 1: Write failing UI and accessibility tests.**

Test `설정 필요` badge/banner, three groups (`재무 공식`, `위험·행동 정책`,
`입력 방식`), next required field, `저장하고 다음`, `나중에`, `아직 모름`,
field help, KRW labels, loading/error/offline/recovery states, review summary,
explicit `정책 활성화` confirmation, active-vs-draft display, history, and
copy-to-draft restore. Assert native labels, keyboard order, focus placement,
and no second-owner language.

- [ ] **Step 2: Implement status and step navigation from server order.**

The UI never computes completeness. It renders the server's ordered field
items and `activation_ready`. Saving sends only the selected code/state/value
plus the expected draft head; success replaces the whole local draft with the
validated server response.

- [ ] **Step 3: Implement unknown/help behavior without defaults.**

`아직 모름` saves `state=unknown,value=null`. Help copy explains the source of
each amount/rate but contains no example business amount and never pre-fills an
input. `나중에` performs no mutation.

- [ ] **Step 4: Implement review, explicit activation, and history.**

Review is unavailable until the server reports ready. Activation requires a
Korean confirmation dialog displaying formula/risk/format digests and active
head identity, not private values in general activity copy. Restore only calls
copy-to-draft and routes to review; it never changes the active policy directly.

- [ ] **Step 5: Run focused UI tests and commit.**

```bash
cd web
npm test -- src/features/owner-settings src/app/AppController.test.ts
npm run typecheck
npm run build:ci
cd ..
env -u GIT_INDEX_FILE git add -- web/src/features/owner-settings \
  web/src/app/App.tsx
env -u GIT_INDEX_FILE git commit -m "feat(web): add Korean owner settings center"
```

### Task 5: Reconcile docs, persistence negatives, and cumulative local GO

**Files:**
- Modify: `README.md`
- Modify: `ARCHITECTURE.md`
- Modify: `OPERATIONS.md`
- Modify: `DECISIONS.md`
- Modify: `docs/MANUAL.md`
- Create: `web/e2e/owner-settings.spec.ts`
- Modify: `web/playwright.config.ts`
- Modify: `web/e2e/security.spec.ts`
- Modify: `web/e2e/workflow.spec.ts`

**Interfaces:**
- Consumes: independently accepted Tasks 1-4.
- Produces: factual Korean operator guidance and complete local verification evidence.

- [ ] **Step 1: Update owner-facing and operational documentation.**

Document one account/session, the `필요 정보` page, `아직 모름`, drafts,
explicit activation, current-active preservation, history/restore, offline
fail-closed behavior, and `manual_only`. Remove product-facing two-user quorum
instructions without deleting historical ADR text.

- [ ] **Step 2: Run persistence and operation-inventory negatives.**

```bash
cd web
rg -n 'localStorage|indexedDB|caches\.|sessionStorage' src --glob '!**/*.test.*'
rg -n 'create_ppl_formula_version|approve_ppl_formula_version|create_ppl_risk_policy|approve_ppl_risk_policy|activate_ppl_policy_pair|record_ppl_initial_format_ruling' src/features src/app
npm run test
npm run typecheck
npm run build:ci
```

Expected: only the reviewed metadata journal and auth adapter use browser
storage; raw operations-only PPL names are absent from features/app; all web
checks pass.

- [ ] **Step 3: Run the cumulative database and repo gate.**

```bash
env -u GIT_INDEX_FILE .venv/bin/python -m pytest \
  db/tests/test_owner_settings_api.py \
  db/tests/test_owner_settings_security.py \
  db/tests/test_ppl_decision_policy.py \
  db/tests/test_ppl_offer_evaluation.py \
  db/tests/test_selling_package_evaluation.py \
  db/tests/test_selling_package_api.py \
  db/tests/test_selling_package_security.py -q
env -u GIT_INDEX_FILE .venv/bin/python scripts/ci_smoke.py
env -u GIT_INDEX_FILE git diff --check
```

- [ ] **Step 4: Commit docs and request cumulative review.**

```bash
env -u GIT_INDEX_FILE git add -- README.md ARCHITECTURE.md OPERATIONS.md \
  DECISIONS.md docs/MANUAL.md web
env -u GIT_INDEX_FILE git commit -m "docs(owner): document one-user settings workflow"
```

Submit the exact foundation-GO..HEAD range to a non-author Operator on a
different model. Cumulative GO is local implementation only. A separate owner
effect packet is required before managed deployment, real private-value entry,
runtime Gate-D recording, policy activation, Windows installation, or booking.
