# Capability-First Compact Kernel Implementation Guide

**Goal:** maximize executable model capacity while retaining only controls that
prevent a named authority, correctness, concurrency, privacy, spend, or
external-effect failure.

## Invariants

- Evolve current route, lineage, verification, capability, and provider
  primitives behind one reducer; do not create a second operation store.
- Direct work without coordination, independent-verification, or effect triggers
  creates no protocol artifact. Controls are risk-triggered, never seat-triggered.
- Models may choose in-scope tools, subagents, worktrees, read-only web
  research, ChatGPT, or Claude from runtime- and user-authorized options;
  unused capacity creates no record.
- Web research and provider output are advisory and grant no verdict,
  protocol-state, or side-effect authority.
- Retain a public helper only when it has a non-test caller or documented CLI.
- Version 1 stays authoritative until the user-approved Phase-4 activation;
  shadow state cannot grant GO, terminality, or effects.
- Commit, push, mailbox/cursor mutation, spend, and activation retain their
  separate user/runtime gates.

## 1. Verified starting point

The migration must begin from current repository truth, not from the desired
architecture:

- `scripts/route_manifest.py` explicitly keeps Markdown mailbox routes as live
  authority; typed route objects are a compatibility layer.
- `scripts/route_lineage.py` has useful lineage and CAS validation, but the live
  route set has no generations and the CAS check is not a transactional writer.
- `write_route_pair()` writes JSON and Markdown sequentially, so it is not an
  atomic authority publication mechanism.
- `scripts/protocol_capacity.py` reduces capacity packets and Markdown rules,
  including standby, Pair-B, join, and next-trigger ceremony that this migration
  intends to remove.
- `scripts/route_capability.py` atomically records evidence after an effect; it
  does not reserve and execute the effect before it happens.
- `scripts/chatgpt_pro_consult.py` and `scripts/opus_review_receipts.py` already
  demonstrate pre-attempt reservation, idempotency, and uncertainty handling.
- The signed three-way reducer/ref store contains reusable primitives but is a
  separate dormant merge-gate substrate. This plan does not silently activate it.

Therefore, "evolve the existing kernel" means reuse proven primitives and
replace the live reducer through adapters. It does not mean that one typed live
kernel already exists.

## 2. Minimal execution model

The reducer tracks three independent triggers internally:

- `coordination`: two or more writers, transferred unfinished ownership, shared
  mutable state, overlapping scopes, or managed convergence.
- `verification`: an authority/security/parser boundary, destructive or
  irreversible change, external-effect mechanism, material uncertainty, or an
  explicit user/repository requirement for independent review.
- `effects[]`: exact external actions that require a user, spend, target, and
  single-executor grant.

The executing model uses the smallest profile that satisfies the triggers:

| Triggered profile | Execution form | Persistent protocol state |
|---|---|---|
| None | One writer works, validates, and reports directly. | None. |
| Verification only | One writer plus one independent verifier for the exact scope. | Verification record only. No route. |
| Coordination only | Owned mutable units plus one serialized transition duty. | Route/unit transitions only. |
| Effect only | One writer plus one pre-attempt reservation and executor. | Effect reservation and outcome only. No route. |
| Combined | Compose only the triggered records above. | No synthetic all-in-one operation object. |

All trigger combinations receive reducer tests, but operators do not perform an
eight-row classification ritual. A provisional decision is recomputed from the
actual diff and requested effects before `REVIEW`, `DONE`, or execution.

### Seat and tool use

Keep one writer per coherent mutable scope. Add producers only for disjoint,
independently testable work, a verifier only when triggered, and a serialized
writer duty only for coordinated state. Duties may share productive seats; do
not create standby, observer, Pair-B, utilization, join, receipt-only, or
terminal-next-trigger artifacts.

Every readiness bridge, director/director2, operator/operator2, and coordinator
context may choose the runtime's read-only web-search tool whenever external,
current, niche, or materially uncertain information would improve the work. A
sanitized query over public information needs no route, reservation, approval
artifact, or seat handoff. Prefer primary sources, cite the exact sources
actually relied on, cross-check a consequential ambiguous source, and state the
source date or freshness when it matters. For repository and protocol state,
current local durable artifacts still outrank web material.

The fast path ends at research. A query must not disclose private repository,
mailbox, route, credential, token, personal, or proprietary content. Search
does not authorize sign-in, credential entry, upload, form submission, paid
API use, spend, or any downstream action. Results cannot grant GO/NITS/FAIL,
directly mutate a route or authoritative/live reducer state, reserve an effect,
or satisfy an independent verification requirement. A separately accepted
transition may carry one sanitized citation as opaque `evidence_refs` input to
non-authoritative shadow reduction only. If the runtime tool is unavailable,
continue from local evidence or report the limitation. Stop and request
direction when the missing fact would materially change scope, security,
authority, cost, or an irreversible decision. Do not silently switch to an
interactive browser, provider API, credentialed transport, or paid fallback,
and do not download or execute software as part of research.

## 3. One reducer, no second authority store

Create one pure reducer interface, preferably in
`scripts/capability_reducer.py`:

```python
def apply_transition(
    state: "KernelState",
    event: "TransitionEnvelope",
    *,
    actor: "ActorContext",
    activation: "ActivationState",
) -> "KernelState": ...

def reduce_protocol_state(
    events: "Iterable[TransitionEnvelope]",
    *,
    resolve_actor: "ActorBindingResolver",
    activation: "ActivationState",
) -> "KernelReport": ...
```

The reducer consumes existing v1 artifacts through a read-only adapter and
compact typed events after activation. Verification and effect stores remain
specialized sources; the reducer references their validated outcomes instead of
copying them into a new root object.

### Transition envelope

Every authority-relevant transition carries only the fields needed to prevent
replay, stale writes, scope confusion, and authority inheritance:

```text
schema
work_id
transition_id
route_id or null
work_revision
unit_id or null
actor_binding_digest
requested_transition
expected_unit_version
precondition_digest
mutable_scope_ref
mutable_scope_digest
content_digest
dependency_digest
acceptance_digest
evidence_refs
verification_ref or null
effect_reservation_refs
activation_epoch
```

Reducer laws:

1. The same `transition_id` and payload returns the recorded result.
2. The same ID with changed content is a conflict.
3. A stale unit version, precondition, activation epoch, or actor binding fails.
4. The reducer resolves each immutable scope descriptor, canonicalizes path and
   lock domains, and verifies its digest. Disjoint scopes may merge;
   overlapping scopes serialize or fail.
5. Work/route revision orders events but does not invalidate unrelated
   verification.
6. A unit changes version only when its relevant content, dependencies,
   acceptance, or evidence changes.
7. Shadow reduction is observational only and cannot grant authority.
8. Unknown fields, unknown effect classes, ambiguous lineage, and incomplete
   legacy mappings fail closed.

### Principal binding

The host supplies `ActorContext` out of band with binding ID, repository,
principal, allowed actions, parent/user authority, issuance, expiry, and
revocation. Events record its digest; payload, prose, role labels, environment,
and free CLI arguments cannot mint or broaden it. Child contexts are strict
subsets. An `unattested` runtime may do local work but cannot publish
verification, activate the kernel, or execute governed effects. Bare CLI labels
are not cryptographic identity.

Required negative tests include payload actor spoofing, environment/argument
override, subagent inheritance, stale session binding, and cross-seat replay.

## 4. Scoped verification and complete state meaning

Independent verification binds to:

```text
work_id + unit_id + unit_version + content_digest + dependency_digest
+ acceptance_digest + evidence_digest + verifier_binding
```

An unrelated route or unit update does not invalidate GO. A relevant content,
dependency, acceptance, evidence, or verifier-binding change does.

Work and verdict mapping is total before reader migration:

| Legacy/result value | Compact meaning | Terminal for this review/unit? | Retry or next action | Effect eligible? |
|---|---|---:|---|---:|
| `ready`, `active` | `RUN` | No | Continue current unit. | No |
| `blocked`, no completion evidence | `WAIT` with blocker owner and wake condition | No | Resume when the named condition changes. | No |
| `blocked`, completion evidence present | Derive completed work: `REVIEW` if verification is required, otherwise `DONE` | Depends on derived state | Verify or close without reopening the work. | Only through a separate current grant |
| implementation `done`, verification required | `REVIEW` | No | Obtain one review-of-record. | No |
| `done`, all triggered gates met | `DONE` | Yes | None for this version. | Only with a current effect grant |
| `excepted` | `DONE` with an exception reference | Yes | New unit/version to reopen. | No unless separately granted |
| `GO` | Verification accepted for the exact key | Yes | Continue integration/effect gates. | Yes, if all other gates pass |
| `NITS` | Minor issues block current GO | Yes | Fix and create a new scoped version. | No |
| `FAIL` | Verification failed | Yes | Remediate under a new scoped version. | No |
| `unable_to_verify` | Local review did not conclude; not a defect verdict | No | Re-dispatch within policy or escalate. | No |
| Provider `pass`, `issues`, `unavailable` | Advisory evidence only | No effect on unit terminality | Local verifier reconciles or continues without it. | Never by itself |
| `cancelled` | Work intentionally terminated | Yes | New work ID to restart. | No |
| `failed` | Execution attempt failed conclusively | Yes for the attempt | New transition only if policy permits. | No |
| `superseded` | Historical version replaced | Yes | Follow the named successor. | No |
| `outcome_unknown` | External attempt may have occurred | No | Reconcile only; never retry. | No new attempt |

Specialized lifecycle adapters are also total and remain distinct:

| Existing store | Existing states | Compact interpretation |
|---|---|---|
| Capability | `issued`, `activated` | Grant available; no attempt or success implied. |
| Capability | `consumed` | Inspect the bound receipt outcome; never infer success from the state alone. |
| Capability | `revoked`, `expired`, `failed` | Terminal and unavailable for a new attempt. |
| ChatGPT | `prepared`, `sending`, `sent`, `received`, `reconciled` | Reserved, attempting, awaiting/received response, then locally reconciled; always advisory. |
| ChatGPT | `failed`, `stale` | Preserve failure class and map ambiguous delivery to `outcome_unknown`; only an explicitly authorized, non-ambiguous manual-origin failure may resume the same manual consultation, while all other failures and `stale` remain terminal/unusable. |
| Opus | `reserved`, `reviewed`, `reconciled`, `publishing`, `published` | Preserve the provider attempt, local disposition, and publication phase; none grants local verdict authority. |

## 5. External effects

Register only effect classes with an implemented executor and threat model.
Do not create a generic shell-command authority taxonomy.

Every governed effect follows:

```text
RESERVED -> CANCELLED | ATTEMPTING
ATTEMPTING -> SUCCEEDED | FAILED | OUTCOME_UNKNOWN
OUTCOME_UNKNOWN -> RECONCILED_SUCCEEDED | RECONCILED_FAILED
```

Before the attempt, reservation immutably binds work/unit version, epoch,
user/standing grant, one executor, exact target/class, provider idempotency key
when available, pre/postchecks, expiry, and reconciliation.

No transport, provider, executor, target, or request change is allowed after
reservation. An ambiguous or partial outcome blocks retry until reconciliation.
Rollback of protocol state never claims to undo a real external effect.

The executor durably records `ATTEMPTING` before crossing the boundary. An
abandoned `RESERVED` may resume the same reservation after preflight, or cancel
only when that marker is absent; expiry also cancels before attempt. Abandoned
`ATTEMPTING` becomes `OUTCOME_UNKNOWN` and can only reconcile. Conclusive
`FAILED` needs a fresh grant and reservation.

For Git push, describe enforcement accurately:

- `credential-mediated` only when a broker/sandbox with scoped credentials
  actually prevents raw push;
- otherwise `user-gated audited executor`, with exact refspec, expected remote
  OID, fixed argument vector, and postcheck. Do not claim structural prevention.

## 6. Flexible research, ChatGPT, and Claude use

### Read-only web research

Web search is a runtime research tool, not an advisory-provider dispatch and
not an external-effect executor. A seat chooses it directly under Section 2's
public/sanitized/read-only boundary. No consultation reservation is created
for an ordinary query, and no result is imported as authority.

When research contributes to durable work, record the minimum useful
provenance: a direct source reference, publication or retrieval date when
freshness matters, and the local conclusion it supports. Raw search result
pages and copied private context do not belong in route or protocol state. The
compact reducer may receive a sanitized durable citation identifier through
`evidence_refs`; it treats that identifier as opaque evidence, never fetches
it, judges its truth, or derives eligibility from it. Any action suggested by
research passes through its ordinary authority and side-effect gates.

Required abuse coverage for the live seat harness is: private query leakage;
credential, sign-in, form, and upload attempts; paid or credentialed fallback;
stale or uncited reliance; result-as-verdict or result-as-route confusion; and
tool unavailability. The hermetic capability-baseline collector may disable
web access to preserve benchmark comparability; that benchmark setting is not
a general seat restriction.

### Advisory model transports

No advisory transport or provider adapter is implemented by this guide. The
former Phase 3 promises for `scripts/advisory_dispatch.py`, effect adapters, and
provider adapters are retired. Any future provider tool requires separate user
authorization and a new design.

## 7. Function and ceremony pruning rule

Classify every changed public helper using import/AST search, CLI registration,
skill/config references, and focused coverage:

| Classification | Keep condition |
|---|---|
| Runtime core | At least one current non-test caller and an enforced behavior. |
| CLI entrypoint | Documented command, exercised canary, and maintained contract. |
| Historical adapter | Called by the active reducer for v1 history and covered by golden fixtures. |
| Telemetry | Invoked by smoke/doctor/reporting and never treated as authority. |
| Duplicate, test-only, or orphan | Inline or delete. Tests alone do not justify production code. |

Prune after cutover:

- all-seat coverage and forced Pair-B work;
- standby/idle/observer/utilization artifacts;
- mandatory coordinator joins and terminal next-trigger prose;
- route-by-filename and generation-height authority selection;
- live Markdown authority parsing and legacy writers;
- duplicate route views, packet enumeration, and phrase-copy sync tests;
- unused provider/capability classifiers and helpers without real callers.

## 8. Implementation phases

### Phase 1: Baseline and executable contracts

**Surfaces:** `governance.toml`, the capacity/effectiveness/packet-state tools,
existing route/verification/capability tests, and new golden replay fixtures.

- [x] Inventory every live authority source, reader, writer, effect executor,
  provider adapter, and public helper; classify helpers under Section 7.
- [x] Encode both Section-4 tables as total parameterized mappings and commit
  replay vectors for forged principals, duplicate IDs, stale versions, and
  dependency, acceptance, and evidence changes. Phase 2 checks their current
  shadow parity; external effects and providers carry no corpus promise.
- [x] Benchmark the five Section-2 profiles five times on one host and persist
  cohort, raw runs, medians, and immutable review identities under `logs/`.
  Measure with a monotonic clock from accepted input to first executable tool
  callback and from accepted route event to published GO; missing endpoints
  invalidate a run.
  Use `scripts/capability_baseline_runtime.py`: its fixed committed contract and
  collector identity come from the pinned source tree, its Codex identity comes
  from a contract-approved executable path/version/digest, and its opaque host
  identity is runtime-derived. Fresh collection rejects prior state; resumed
  self-authenticating state can never issue operational provenance. Canary state
  is separate from the 25-run cohort. The child retains flexible local tool
  choice inside one writable fixture directory. Each disposable workspace has
  a fresh local `.git` directory and one exact-path, session-only trust entry
  only so Codex loads the parent-installed project hooks while user config is
  ignored; that metadata is parent-owned, read-only, and has no live remote,
  branch authority, or shared history. The child uses `workspace-write` with
  its CWD narrowed to the fixture and both implicit temp write roots disabled,
  leaving the parent instrumentation outside the writable root.
  Network/browser/app/plugin/multi-agent features remain disabled. The ten local
  marker effects require `--authorize-local-markers`; no provider, mailbox,
  branch, push, or live protocol effect is authorized. The committed-byte
  preflight must pass before canary or collection.
- [x] Make the reporter declare protocol roots, accepted-result denominators,
  and artifact classes. A standby artifact records only waiting, observing,
  utilization, or no-op readiness; duplicate reviews share exact
  `(base, head, scope digest, question digest)` identity, not reason text.
- [x] Add `[protocol.kernel]` epoch `0`/writer `v1` to `governance.toml` only as
  a declarative mirror, never the activation high-water mark.

**Phase-1 evidence (2026-07-15):** `REQUIRED_SURFACE_OWNERS` is the independent
ownership oracle; the committed compact-state fixture validates
49 mappings across 7 domains; the 25-run cohort and report are committed at
`8149df28b45bd2b0b159b243923d0ab439c3d815` and integrated by merge `d07fc4d`;
the reporter's `VerifiedBaselineProvenance` contract binds the committed
contract/observation digests, cohort, collector, source, Codex identity, and
exactly 25 run-record digests before `operational_complete`; and the declarative
kernel mirror remains epoch `0`/writer `v1`. No compact path was activated.
Task 1 closed with the exact changed-surface command and result:

```sh
env -u GIT_INDEX_FILE /Users/hyungkoookkim/Pipeline/.venv/bin/python \
  -m pytest -q \
  tests/unit/test_compact_kernel_surface_inventory.py \
  tests/unit/test_protocol_mailbox.py \
  tests/unit/test_governance_hardening.py \
  tests/unit/test_codex_ledger_bridge.py \
  tests/unit/test_protocol_prompt_sync.py \
  tests/unit/test_protocol_capacity.py \
  tests/unit/test_route_lineage.py \
  tests/unit/test_seat_status_all.py \
  tests/unit/test_status.py \
  tests/unit/test_compact_state_mapping.py \
  tests/unit/test_codex_seat_launcher.py \
  tests/unit/test_threeway_activation_scripts.py \
  tests/unit/test_threeway_constants.py
```

```text
267 passed in 6.68s
```

**Gate status:** reclosed by Task-3 commit
`09d2e7f768a0324ace1a6de61afc483ce222dd52`. The focused RED was
`34 failed, 59 passed`; the non-vacuous override mutation was
`1 failed, 92 deselected` after temporarily removing
`scripts.mailbox_monitor.main` and was restored before GREEN; the final focused
suite was `93 passed`; and the exact 13-file changed-surface regression suite
was `303 passed`. Project smoke was `OK`. A fresh read-only Codex subagent
independently reviewed
`1c3e5fdae3f072743155e2345e40cfe7b8b7df9d..09d2e7f768a0324ace1a6de61afc483ce222dd52`
and returned `RESOLVED`, with no Critical or Important issue and
`Ready to reclose: Yes`.

The finite owner/import closure and independently pinned required overrides are
now enforced. The original 49-mapping, committed 25-run cohort, reporter
contract, and epoch `0`/writer `v1` declarative-mirror evidence above remains
valid. Current v1 remains authoritative; no compact path is authoritative or
activated.

### Phase 2: Compact reducer and non-authoritative shadow

- [x] Add `schemas/route-v2.schema.json`, `scripts/capability_reducer.py`, the
  Section-3 types/laws, and focused deterministic replay/merge tests.
- [x] Adapt v1 history read-only; never rewrite it. Shadow-reduce the same
  accepted inputs and structurally prohibit shadow GO, DONE, and effects.

**Gate:** zero authority/effect-eligibility divergence across the full replay
corpus; deliberately injected divergence blocks the gate.

**Phase-2 evidence (2026-07-16):** The exact implementation range is
`f17d14c684e1e1a6378e52ab8f151070fb710e07..efa8731eae2e9d9fa020d95045e5b08ab6331ba3`.
The committed corpus artifact
`logs/capability-first/phase2b-shadow-parity.json` is byte-identical to fresh
output from `env -u GIT_INDEX_FILE /Users/hyungkoookkim/Pipeline/.venv/bin/python scripts/capability_v1_adapter.py --check-corpus tests/fixtures/compact_kernel/v1_to_v2_replay.json`
and reports 46 cases and 31 executed replay permutations with every blocking,
non-authority-only, and specialized-event list empty. The focused command
`env -u GIT_INDEX_FILE /Users/hyungkoookkim/Pipeline/.venv/bin/python -m pytest -q tests/unit/test_capability_v1_adapter.py tests/unit/test_capability_reducer.py tests/unit/test_capability_reducer_replay.py tests/unit/test_route_v2_schema_sync.py tests/unit/test_compact_state_mapping.py tests/unit/test_compact_kernel_surface_inventory.py tests/unit/test_route_manifest.py tests/unit/test_route_schema_sync.py tests/unit/test_target_binding.py`
reported `552 passed`; independent Review 11 of the exact range returned
`APPROVED` with no Critical, Important, or Minor finding; and
`scripts/target_binding.py --check` reports epoch `0`, writer `v1`, declarative
only. Version 1 remains the sole authority; Phase 3 is retired, and Phase 4
remains inactive and separately user-gated.

### Phase 3: Retired

No executable task remains. The speculative corpus/report bookkeeping and the
effect/provider implementation promises were removed because no authoritative
live caller justified them. Historical evidence remains in Git history.

### Phase 4: Reader migration, activation, and pruning

- [ ] Move capacity, mailbox, ledger-start, continuation, seat-status, doctor,
  and operative-doc readers to the reducer while retaining dual-read,
  single-v1-write behavior.
- [ ] Add `tests/integration/test_protocol_e2e.py`, mixed-version tests, and one
  canary per profile, including guarded advisory and disposable ambiguous-effect
  reconciliation. Make `protocol_doctor.py --current` report, not decide,
  reducer/epoch/writer state and mixed-writer violations.
- [ ] Fence writers; reread HEAD and activation inside the fence; reject cached,
  stale, lower, or mismatched epochs. Complete, cancel, or explicitly migrate
  every in-flight v1 unit.
- [ ] After independent GO and explicit user authorization naming exactly one
  activation executor, commit one monotonic compact-writer epoch; allow dual
  read but only compact write. Rehearse rollback as a newer epoch, never an
  in-place downgrade.
- [ ] After Section-9 observation, delete legacy writers and ceremony while
  retaining the read-only v1 decoder and golden histories.

**Gate:** all cutover evidence in Section 9 passes on the activated head and the
doctor reports exactly one writer mode.

Activation uses a Git-common-dir lock plus exact-old-value CAS on
`refs/protocol/kernel-activation`, whose value binds epoch, mode, activation
commit, and predecessor; `governance.toml` is only a mirror. Every publisher
loads this guard from the trusted primary checkout under lock and records the
epoch. After any activated observation, a missing/deleted/lower ref fails
closed; old-epoch artifacts are inert. Drain old processes and import the same
ref into every governed writer clone before activation.

## 9. Cutover and capacity evidence

Activation is allowed only when all of the following are true:

1. Every work/verdict state and every specialized lifecycle state in Section 4
   has tested terminality, retryability, and effect eligibility.
2. Replay and shadow canaries have zero authority or effect-eligibility
   divergence. Non-authority formatting differences do not block.
3. Exact duplicate transitions are idempotent; changed duplicates, stale unit
   versions, and stale epochs fail.
4. Verification invalidates only for relevant unit content, dependency,
   acceptance, evidence, or verifier changes.
5. Principal spoofing and subagent authority inheritance fail.
6. Each governed effect reserves before attempt; ambiguous delivery produces no
   retry or provider switch and can be reconciled.
7. Mixed-version tests prove dual-read/single-write behavior and the exclusive
   writer fence.
8. Every in-flight v1 unit has a durable completion, cancellation, or migration
   disposition.
9. A newer-epoch rollback rehearsal succeeds without claiming to undo completed
   external effects.
10. Function inventory has no unclassified or test-only production helper.

Capacity thresholds are relational to the committed Phase-1 baseline:

- direct-path protocol artifacts, standby artifacts, duplicate same-scope
  reviews, unauthorized effects, and duplicate effect attempts are exactly zero;
- time to first executable work and median route-to-GO latency do not regress;
- artifacts per accepted boundary-bearing result do not increase;
- at least one of time-to-work, route-to-GO latency, or artifact count improves;
- committed regression/canary failures, unresolved effect outcomes, stale-GO
  acceptances, and rollback failures are exactly zero.

The benchmark uses the same five scenarios, five runs, host, inputs, and
instrumentation before and after. Median latency may increase by at most the
larger of 5% or 50 ms to absorb local timing noise; artifact and safety counts
have zero tolerance. Before legacy pruning, observe ten consecutive activated
boundary-bearing units spanning at least three triggered profiles. Disposable
canaries must cover any missing effect or advisory profile. Any authority/effect
divergence, duplicate dispatch, or unresolved effect outcome resets the
observation window after remediation.

Measurements must come from the committed effectiveness reporter and a `logs/`
artifact. A green smoke test alone is not capacity evidence.

Recommended verification commands:

```sh
env -u GIT_INDEX_FILE .venv/bin/python -m pytest tests/unit -q
env -u GIT_INDEX_FILE .venv/bin/python -m pytest tests/integration/test_protocol_e2e.py -q
env -u GIT_INDEX_FILE .venv/bin/python scripts/ci_smoke.py
env -u GIT_INDEX_FILE .venv/bin/python scripts/protocol_doctor.py --current
env -u GIT_INDEX_FILE git diff --check
```

## 10. ChatGPT Pro consultation reconciliation

- **ID/phase:** `2540c043-c177-4017-aa1b-0c3d3453ffa9`; post-plan adversarial
  simplification.
- **Binding:** HEAD `ee2c71cd50714c137cc502102fa415fa5f2c7634`; no live route.
- **Question:** smallest safe kernel, migration, provider selection, and cutover
  evidence that preserve model capability.
- **Advice:** reuse typed primitives behind shadow adapters; scope verification,
  reserve effects, choose runtime-eligible transports, and activate by epoch.
- **Disposition:** adopted those controls plus idempotency, total compatibility,
  a thin cross-provider intent claim, and writer fencing; corrected the assumed
  live typed kernel; rejected a second store, global invalidation, universal
  review, fixed seats, mandatory joins, and generic command/provider authority.
- **Result:** a four-phase in-place migration with v1 authoritative until
  explicit activation and every retained control tied to a named failure mode.

## 11. Implementation kickoff

Implement the next incomplete phase from current evidence. Keep v1 authoritative
until the Phase-4 gate; select only useful writers, tools, and triggered controls;
finish that phase's tests and gate; then remove dead code and ceremony. Advisory
models remain tools, not authority. Activation, commit, push, spend, and
mailbox/cursor mutation each require their own authorization.
