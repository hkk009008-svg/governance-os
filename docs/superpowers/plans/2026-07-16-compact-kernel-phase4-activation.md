# Compact Kernel Phase 4 Activation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking. Activation itself remains a separately user-authorized governed side effect.

**Goal:** Migrate every live protocol reader and writer to the compact reducer boundary, prove dual-read and exclusive-writer behavior, and perform at most one fail-closed epoch-1 compact activation followed by a minimum ten-unit observation gate without pruning legacy evidence.

**Architecture:** Phase 4 keeps legacy v1 authoritative while readers dual-read the Phase-3 projection and every authoritative publisher is placed behind one Git-common-directory writer fence. Independent clones, hosts, queues, and automation must either be imported into that fence or have their write authority revoked before cutover. The compact event log, per-seat cursor refs, activation ref, and durable v1-recovery ref remain dormant until an activation candidate has independent GO, all v1 units are dispositioned, and the user names one executor. A GO-reviewed implementation commit is immutable input to an activation blob; a later preparation commit binds that blob and exact ref map, and a still-later authorization artifact binds the preparation commit and expected executor without creating a commit/object self-hash. The executor is authenticated by a host-supplied challenge source inside the shared fence and then performs one transactional exact-old-value update of the activation, event-tip, and cursor refs. Every later reader and writer uses one stable activation-selected view: epoch-0 legacy v1, epoch-1 compact, or higher-epoch recovered v1. Rollback is only a separately authorized higher epoch after lossless reverse projection into the durable recovery store; this plan installs epoch 2 only in a disposable rehearsal and performs no live rollback or additional legacy pruning.

**Tech Stack:** Python 3.14, frozen dataclasses, RFC-8785 canonical JSON, Git blob/commit objects and transactional `update-ref`, `fcntl.flock`, the compact reducer/v1 adapter/Phase-3 runtime seams, pytest, shell entrypoints, and the Pipeline four-seat protocol.

## Global Constraints

- The approved umbrella design is `docs/superpowers/specs/2026-07-16-pipeline-recovery-sequence-design.md` at `426744766711d4d6057a4698f5bb19d454ad621d`.
- The normative compact guide is `docs/superpowers/capability_first_compact_kernel_codex_seat_guide.md`, especially Sections 8-9.
- Do not start implementation until every earlier recovery phase has a content-addressed committed terminal handoff, binding GO, authorized local integration where required, and current-main ancestry. The fixed gate set is: `docs/HANDOFF-coordinator-2026-07-16-recovery-owner-wip-disposition.md`; `docs/HANDOFF-coordinator-2026-07-16-chatgpt-local-reprepare-disposition.md`; `docs/HANDOFF-director-2026-07-16-opus-b-d-recovery.md`; `docs/HANDOFF-target-aware-evidence-ledger-opus-bridge-2026-07-16.md`; `docs/HANDOFF-director-2026-07-16-candidate-policy-integrated.md` plus its post-candidate target-bridge compatibility GO; `docs/HANDOFF-ledger-ppl-publication-race-correction-2026-07-16.md`; `docs/HANDOFF-director-2026-07-16-targeted-web-integrated.md`; `docs/HANDOFF-coordinator-2026-07-16-capability-phase1-2-integrated.md`; and `docs/HANDOFF-coordinator-2026-07-16-compact-phase3-integrated.md`.
- Required predecessor plans are:

  - `docs/superpowers/plans/2026-07-16-recovery-owner-wip-disposition.md`
  - `docs/superpowers/plans/2026-07-16-compact-kernel-phase1-2-integration.md`
  - `docs/superpowers/plans/2026-07-16-control-plane-compact-phase3-convergence.md`
  - `docs/superpowers/plans/2026-07-16-opus-quality-correction-and-recovery-routing.md`
  - `docs/superpowers/plans/2026-07-16-target-aware-evidence-ledger-opus-bridge.md`
  - `docs/superpowers/plans/2026-07-16-ppl-publication-race-correction.md`
  - the already approved candidate-policy and targeted-web plans

- The fixed activation identity is `compact-kernel-phase4-2026-07-16`.
- The only activation authority ref is `refs/protocol/kernel-activation`. The only compact reducer event-tip ref is `refs/protocol/kernel-events`. Compact cursor refs are `refs/protocol/kernel-cursors/director`, `refs/protocol/kernel-cursors/director2`, `refs/protocol/kernel-cursors/operator`, `refs/protocol/kernel-cursors/operator2`, `refs/protocol/kernel-cursors/coordinator`, and `refs/protocol/kernel-cursors/coordinator2`.
- The only durable recovered-v1 store ref is `refs/protocol/kernel-v1-recovery`. It is absent in epoch 0 and epoch 1. An epoch-2/v1 transaction installs its prepared object and the epoch-2 activation object atomically; later recovered-v1 writes advance only this ref under the same fence.
- Each preparation attempt receives one immutable prepared-object archive ref `refs/protocol/kernel-archives/compact-kernel-phase4-2026-07-16/epoch-1/<preparation-attempt-id>` and matching tracked archive path. Its anchor commit tree contains the exact activation blob and six cursor blobs, and its parent is the prepared genesis event commit, making every pre-CAS target reachable. Archive refs are non-authoritative and never select a writer. Preparation creates the attempt ref with exact-old absent CAS under separate authority; NITS/FAIL retains it as failed-attempt evidence and a correction uses a fresh attempt ID/ref/path; activation exact-verifies only the archive selected by its preparation. No archive ref is ever moved, reused, or deleted by this plan.
- All activation, event, cursor, recovery, verification, effect, and advisory publishers in the authoritative repository use the same Git-common-directory lock file `protocol-kernel-writer.lock`. No second lock order exists. Any independently locked clone, remote worker, queue consumer, scheduled job, or recovery process with write capability blocks activation until it is stopped and its authority is revoked or it is moved behind this exact common directory.
- `governance.toml` is a derived consistency mirror only. It never selects a writer, repairs a ref, or supplies fallback authority. It remains epoch `0`/writer `v1` through preparation GO, user authorization, and activation-execution GO so the specialized non-work transition-control artifacts can be published lawfully. Preparation and authorization bind the exact intended epoch-1 mirror bytes/digest and one separately pre-authorized post-CAS metadata commit. After the activation/event/cursor ref transaction, all traffic remains fail-closed during the deliberate ref/mirror mismatch; the metadata committer immediately commits only the intended mirror plus activation evidence, then stable-view/doctor postcheck may release compact traffic. No v1 fallback is permitted.
- The advisory consultation `fe804d90-888f-476e-b83d-7af65b18f40e` assumed an already-existing epoch-0 activation object. Current live state and this approved plan use an absent activation/event/cursor/recovery ref set as canonical epoch-0 bootstrap. That assumption is explicitly inapplicable here: epoch 1 uses `predecessor_oid=None`, and the ref transaction exact-verifies absence as the old value. Creating an epoch-0 authority object would be a separate authority mutation and is not inferred from the advisory.
- Every activation record is canonical JSON stored as a Git blob. It binds the activation ID, schema, epoch, mode, the already-known GO-reviewed `implementation_commit`, predecessor activation OID, original final-v1 high-water digest, source-state digest, ordered migration-descriptor digest, optional compact source-event cutoff, durable recovery object OID and recovery-state digest, reducer version, event schema, reader compatibility floor, and acyclic event-genesis descriptor digest. It never contains its preparation commit, authorization artifact/digest, Operator report, executor principal, or its containing commit. Epoch 1 uses `predecessor_oid=None` plus null recovery fields because the activation and recovery refs are absent during valid epoch-0 bootstrap; later epochs require the exact previous activation blob OID, and epoch 2/v1 requires all recovery fields.
- Every live activation record also has one immutable attempt-specific tracked archive path whose Git blob OID equals the activation object OID; epoch 1 uses `coordination/activation/archive/compact-kernel-phase4-2026-07-16-epoch-1-<preparation-attempt-id>.json`. The preparation root and attempt archive ref make that object reachable before CAS, and later activation transitions retain every prior archive path/ref, including failed attempts. A predecessor OID embedded only as JSON text is not accepted as Git reachability. Preflight and postcheck bind `git fsck`, no-replace/no-graft, non-shallow, object-format, archive-blob equality, object-retention, and direct-ref protection inventories; privileged bypass risk remains a blocker rather than a claimed lock guarantee.
- Object preparation and authority are separate, one-way artifacts. Canonical `protocol-kernel-activation-preparation/v1` binds the implementation commit, activation record bytes/OID, exact ten-ref inventory/ref operation map, archive anchor/ref, preparation preflight digest, measurement/rehearsal digests, exact intended epoch-1 mirror bytes/digest, exact four-commit transition-control chain contract, user-chosen observation-duration/restart policy, and `status="candidate"`; its containing commit is not embedded in itself. Only after that exact preparation commit receives specialized preparation GO may canonical `protocol-kernel-activation-authorization/v1` bind the preparation commit and artifact digest, activation OID/ref map, control-tail prefix digest, action, expected activation executor principal/binding, separately authorized metadata-finalizer principal/binding, exact mirror path/bytes/digest, activation-evidence path plus schema/field/CAS-correlation constraints, a rule deriving the finalizer parent as the unique direct-child execution-GO commit for this authorization, expiry, and the user authorization decision. It cannot bind future evidence bytes/digest or a future parent OID. The authenticated activation and finalization APIs consume these exact artifacts and resolve/freeze the specialized execution-GO commit at CAS; no object infers or reconstructs missing authority.
- The compact event log is one first-parent Git-commit chain. Each commit contains one canonical `record.json` that binds the exact activation object OID and epoch, predecessor event OID, transition digest, full transition envelope, and its strict protocol payload. It is the reducer event store, not a parallel authority store.
- The activation/event cross-link is acyclic: the activation blob binds a canonical event-genesis descriptor digest, and the prepared genesis event binds the resulting activation blob OID. Neither object directly embeds the other's final OID.
- The first activation transaction updates activation ref, compact event-tip ref, and all six cursor refs in one Git ref transaction with exact old and new OIDs while exact-verifying the recovery ref remains absent and the immutable archive ref remains at its prepared anchor. This is a ten-ref inventory: eight updated authority refs plus two exact-verified refs. A partial ref cutover is never accepted. A rehearsed epoch-2 transaction atomically updates activation and recovery refs while exact-verifying that event and six cursor refs remain unchanged and all archive refs remain reachable.
- Before the activation transaction, v1 is the only writer and compact is observational. After a successful epoch-1 transaction, compact is the only writer and v1 paths are read-only compatibility inputs. No dual-write window exists.
- All writers acquire the common-dir fence, generate a fresh challenge, obtain and validate a host-supplied authenticated actor inside that fence, then reread current `HEAD`, activation ref, selected-store ref, mirror, authorization, and relevant specialized state. Cached or pre-lock values, repository data, arguments, environment, and payload identity cannot authorize a write.
- All readers use one mode-aware stable-view protocol. Epoch-0 `legacy-v1` reads the existing store only while bootstrap is valid. Epoch-1 `compact` reads `A1`, event tip and required cursors bound to `A1`, then `A2`. Higher-epoch `recovered-v1` reads `A1`, the recovery object/ref bound to `A1`, then `A2`. A view is accepted only when `A1 == A2`; cross-epoch, unstable, malformed, or selected-store-mismatched views retry within a fixed bounded loop and then fail closed. No positive epoch falls back to the epoch-0 legacy store.
- Before CAS, inventory and stop every live reader process, independent reader clone, stale cache, mirror, and replica that cannot read the authoritative Git common directory. This plan permits service only from readers restarted against that common directory after mirror finalization and an exact A1/store/A2 check; independent read-only replication requires a separate authenticated replication design. Cache keys include activation OID and selected-store OID. A stale clone or cache is unavailable, never an epoch-0 fallback.
- The final operational v1 high-water closes all workload, route, effect, advisory, retry, and data-plane admissions. After the preparation root commit, exactly three predeclared transition-control commits may follow before CAS: specialized preparation GO evidence, the user authorization artifact, and specialized activation-execution GO evidence. These artifacts live only under the fixed activation paths, contain no mailbox/capacity/work semantics, do not write the selected v1 store, and are excluded from the frozen migration domain. Their exact parent chain and aggregate digest are bound by authorization and reread at CAS; any other selected-store or HEAD write invalidates the candidate. This is a deliberate bounded refinement of the advisory's blanket “no v1 commit” phrasing, not permission for ordinary v1 publication.
- Every in-flight v1 unit receives one durable completion, cancellation, or explicit migration record before activation. No implicit carryover is allowed.
- Old-epoch events, cursors, reservations, reports, and provider/advisory claims are inert. A missing, deleted, lower, malformed, non-ancestor, or mirror-mismatched activation ref fails closed after activated observation.
- External effects already completed are never undone by rollback. A live rollback requires a new commit, a higher epoch, a fresh predecessor link, independent GO, and separate user authorization; this plan performs only a disposable-repository rehearsal.
- The fixed evidence root is `logs/capability-first/phase4-compact-activation-2026-07-16/`. Required committed files are `delayed-retry-inventory.json`, `precutover-compact-five-profile.json`, `rollback-rehearsal.json`, `preflight.json`, `activation.json`, `finalization-result.json`, `restart-evidence.json`, `postactivation-live-five-profile.json`, and `observation.json`.
- Phase 3 already deleted `scripts/packet_state.py` and `tests/unit/test_packet_state.py` after moving their meaning into compact fixtures/property tests. Phase 4 verifies those paths/imports/commands remain absent and never re-creates them. Additional legacy writer deletion, branch/worktree cleanup, route/v1 removal, capability/v1 removal, push, and publication belong to the separate retirement plan. Phase 4 retains all remaining read-only v1 decoders and golden histories.
- Coordinator may route and reconcile only; it never drains processes, revokes leases, authors production/config/object/evidence changes, commits the mirror, or executes activation. A routed Director owns implementation and preparation artifacts, the paired Operator owns GO/NITS/FAIL, a separately user-named drain/preparation executor performs the bounded host/process actions, exactly one user-named activation executor performs CAS, and a separately pre-authorized metadata committer performs the exact post-CAS mirror/evidence commit. These roles may name the same principal only when each distinct authority is explicit.
- Every ordinary Git and pytest command begins with `env -u GIT_INDEX_FILE`. Work in an isolated worktree with explicit pathspecs. Commit, merge, activation, push, and cleanup remain separate permissions.

## Fixed Interfaces

### Activation record and fence

Create `scripts/kernel_activation.py` with these public contracts:

```python
ACTIVATION_REF = "refs/protocol/kernel-activation"
EVENTS_REF = "refs/protocol/kernel-events"
CURSOR_REF_PREFIX = "refs/protocol/kernel-cursors/"
V1_RECOVERY_REF = "refs/protocol/kernel-v1-recovery"
ARCHIVE_REF_PREFIX = (
    "refs/protocol/kernel-archives/"
    "compact-kernel-phase4-2026-07-16/epoch-1/"
)
ACTIVATION_SCHEMA = "protocol-kernel-activation/v1"

class KernelActivationError(ValueError):
    code: str

@dataclass(frozen=True)
class ActivationRecord:
    schema: Literal["protocol-kernel-activation/v1"]
    activation_id: str
    epoch: int
    mode: Literal["v1", "compact"]
    implementation_commit: str
    predecessor_oid: str | None
    final_v1_high_water_digest: str
    source_state_digest: str
    migration_chain_digest: str
    source_event_cutoff_oid: str | None
    recovery_object_oid: str | None
    recovery_state_digest: str | None
    reducer_version: str
    event_schema: Literal["compact-event/v1"]
    reader_compatibility_floor: str
    genesis_descriptor_digest: str

@dataclass(frozen=True)
class ActivationSnapshot:
    record: ActivationRecord
    object_oid: str | None
    head: str
    common_dir: Path

@dataclass(frozen=True)
class StableView:
    activation: ActivationSnapshot
    event_oid: str | None
    cursor_oids: tuple[tuple[str, str | None], ...]
    recovery_oid: str | None
    writer_selection: Literal["legacy-v1", "compact", "recovered-v1"]

@dataclass(frozen=True)
class WriterFence:
    view: StableView
    actor: capability_reducer.ActorContext
    actor_attestation_digest: str
    fence_challenge_digest: str

@dataclass(frozen=True)
class ActivationAttemptResult:
    activation_oid: str
    event_oid: str
    cursor_oids: tuple[tuple[str, str], ...]
    archive_oid: str
    execution_go_commit: str
    evidence_digest: str

@dataclass(frozen=True)
class MetadataFinalizationResult:
    metadata_commit: str
    finalizer_attestation_digest: str
    finalizer_challenge_digest: str
    already_installed: bool
```

Public call signatures are exact:

- `load_activation(root: Path, *, allow_bootstrap: bool) -> ActivationSnapshot`
- `load_stable_view(root: Path, *, required_cursors: tuple[str, ...], max_attempts: int = 3) -> StableView`
- `writer_selection(root: Path) -> Literal["legacy-v1", "compact", "recovered-v1"]`
- `writer_fence(root: Path, *, actor_source: compact_runtime.AuthenticatedActorSource, required_action: str, expected_selection: str, expected_activation_oid: str | None) -> ContextManager[WriterFence]`
- `validate_observation(root: Path, path: Path) -> dict[str, object]`
- `activate(root: Path, *, preparation_path: Path, authorization_path: Path, execution_report_path: Path, actor_source: compact_runtime.AuthenticatedActorSource, evidence_path: Path) -> ActivationAttemptResult`
- `finalize_activation_metadata(root: Path, *, preparation_path: Path, authorization_path: Path, execution_report_path: Path, actor_source: compact_runtime.AuthenticatedActorSource, evidence_path: Path) -> MetadataFinalizationResult`

The implementation also exposes `inspect` and `validate-observation` as direct read-only CLI commands. The `activate` and `finalize_activation_metadata` APIs are callable only through authenticated host launchers that supply `AuthenticatedActorSource` as an in-process capability; direct invocation without that source fails before lock/ref or worktree access. Only `activate` mutates protocol-authority refs. Before CAS, `activate` atomically writes and fsyncs canonical activation-evidence intent at the prebound path. That intent binds the exact expected old/new ref map and a deterministic metadata-commit recipe: parent derivation, exact two path modes/bytes, canonical tree construction, fixed author and committer names/emails, one fixed author/committer timestamp and offset, and a fixed commit message. It does not claim that CAS succeeded, does not contain the resulting metadata commit OID, and binds only the authorized expected metadata-finalizer principal/binding/action—not a future finalizer attestation. `finalize_activation_metadata` accepts only the already-installed exact target ref map, the execution-GO commit resolved and frozen at CAS as the required primary parent, the exact evidence-intent bytes, prebound mirror bytes, metadata-finalizer identity, and two-path allowlist. While holding the same common-dir fence it deterministically reconstructs the tree and commit, then either exact-old-CAS advances only `refs/heads/main` from that parent to the computed commit or, when `main` already equals that computed commit and every byte/ref/identity check passes, returns the installed result without mutation. Any other `main` value fails. Its typed return includes the actual authenticated finalizer attestation/challenge digests and whether it recognized an installed result. Exact replay after a crash is therefore idempotent; it never reruns, rewinds, or falls back from activation CAS.

Preparation and execution verdicts after the operational cutoff use canonical `protocol-kernel-transition-verification/v1` JSON at fixed paths under `coordination/activation/reports/`. They bind activation ID, stage `preparation|execution`, verdict `GO|NITS|FAIL`, reviewed commit/object/ref/archive/control-tail identities, frozen operational high-water and source-state digests, Operator principal/binding/attestation digest, exact command/result digest, finite findings, issue/expiry timestamps, and previous transition-control commit. A routed Operator commits each artifact as the sole path in its exact parent commit under the common-dir fence. These are specialized transition-control evidence, not mailbox events, capacity events, work units, or selected-v1-store writes.

### Phase-3 seams retained and activated

Phase 4 consumes these Phase-3 APIs without creating substitutes:

- `capability_v1_adapter.project_v1_history(records, *, resolve_actor, resolve_scope) -> tuple[LegacySemanticObservation, ...]`
- `compact_runtime.project_reader_state(records, *, resolve_actor, resolve_scope) -> CompactReaderProjection`
- `compact_runtime.authenticate_host_actor(source, *, repository, required_action, challenge, now) -> ActorContext`
- `compact_runtime.writer_selection(root: Path) -> Literal["legacy-v1", "compact", "recovered-v1"]`
- `compact_runtime.require_actor_context(actor, *, repository, required_action) -> ActorContext`
- `compact_runtime.make_verification_key(unit, *, verifier_binding_digest) -> VerificationKey`
- `compact_runtime.verification_is_current(recorded, *, unit, verifier_binding_digest) -> bool`
- `compact_event_store.read_event_chain(repo, *, tip_oid) -> tuple[CompactEventRecord, ...]`
- `compact_event_store.read_mailbox_message(repo, *, event_oid, record) -> CompactMailboxMessage | None`
- `compact_event_store.cursor_ref(seat) -> str`, `read_cursor(repo, *, seat, activation)`, `unread_mailbox_messages(repo, *, seat, activation)`, and `advance_cursor(repo, *, seat, expected_cursor_oid, through_event_oid, actor, activation)`
- `compact_event_store.append_transition(repo, *, event, actor, expected_event_oid, activation, mailbox=None) -> CompactAppendResult`
- `compact_effects.reserve_effect(*, reservation_id, work_id, unit_id, activation_epoch, grant_digest, executor_binding_digest, effect_class, target_digest, request_digest, precheck_digest, postcheck_digest, expires_at) -> EffectReservation` and `transition_effect(reservation, *, requested_state, actor, activation) -> EffectReservation`
- `advisory_dispatch.eligible_transports(runtime, *, purpose) -> tuple[str, ...]` and `reserve_intent(state_path, *, purpose, question_digest, repository, state_digest, scope_digest, request_hash, selected_transport, executor_binding_digest, grant_digest) -> AdvisoryIntentClaim`

Phase 4 extends the projection's mode/writer literals, but it does not change the persisted Phase-3 event, mailbox, or cursor schemas. `COMPACT_CURSOR_SEATS`, `COMPACT_RECIPIENTS`, `COMPACT_KINDS`, and `schemas/compact-mailbox-v1.schema.json` remain frozen and sync-tested; compact runtime paths never consult mutable `coordination/mailbox/kinds.txt`. All live callers continue through these modules.

For rollback readiness, extend `scripts/capability_v1_adapter.py` with a frozen `V1RecoverySnapshot` and the exact call `materialize_v1_recovery(events, *, through_event_oid, activation, resolve_actor, resolve_scope) -> V1RecoverySnapshot`. The snapshot binds the epoch-1 activation OID, exact compact event-head cutoff/sequence, recovered v1 state bytes/digest, accepted-unit IDs, effect references, and unresolved-unit IDs. It is valid only when every accepted compact event through the cutoff is represented exactly once and unresolved units are empty.

Create `scripts/v1_recovery_store.py` with an append-only Git object chain at `V1_RECOVERY_REF`. Each commit tree contains exactly canonical `recovery.json` and `state.json`; `recovery.json` has schema `protocol-kernel-v1-recovery/v1`, source epoch-1 activation OID, exact event cutoff/sequence, previous recovery OID, state blob OID/digest, accepted-unit IDs, immutable effect references, and empty unresolved-unit IDs. Public calls are exact:

- `prepare_recovery(repo: Path, snapshot: V1RecoverySnapshot, *, expected_previous_oid: str | None) -> PreparedV1Recovery`
- `read_recovery(repo: Path, *, tip_oid: str, activation: ActivationSnapshot) -> V1RecoverySnapshot`
- `append_recovered_v1(repo: Path, *, update: object, actor_source: AuthenticatedActorSource, expected_recovery_oid: str, activation: ActivationSnapshot) -> V1RecoveryWriteResult`

Preparation writes objects but not refs. Epoch-2 installation updates `ACTIVATION_REF` and `V1_RECOVERY_REF` in one exact-old transaction, while verifying `EVENTS_REF` and all six cursor refs remain at their epoch-1 values. From that stable view, readers select only recovered `state.json` and writers advance only `V1_RECOVERY_REF`; the epoch-0 Markdown/filesystem store is historical and cannot receive a positive-epoch write.

### Observation schema

`logs/capability-first/phase4-compact-activation-2026-07-16/observation.json` has exactly these fields:

```text
schema
status
activation_id
activated_head
activation_epoch
activation_ref
activation_object_oid
writer_mode
observed_unit_ids
observed_unit_profiles
profile_counts
authority_divergence_count
effect_eligibility_divergence_count
duplicate_dispatch_count
unresolved_effect_count
rollback_rehearsal_epoch
observation_policy_decision_path
observation_policy_decision_digest
observation_started_at
observation_ended_at
observation_duration_seconds
minimum_observation_duration_seconds
required_restart_count
observed_restart_count
restart_evidence_digest
restart_evidence_path
max_delayed_retry_horizon_seconds
post_restart_observation_seconds
delayed_retry_inventory_digest
delayed_retry_inventory_path
precutover_measurement_path
precutover_measurement_digest
postactivation_measurement_path
postactivation_measurement_digest
measurement_host_binding_digest
measurement_baseline_digest
measurement_input_digest
measurement_instrumentation_digest
reporter_commit
report_digest
```

Its schema is `protocol-kernel-observation/v1`. Before post-activation review, `status` is exactly `pending_operator_go` and remains immutable after commit. It requires ten unique observed unit IDs, at least three profiles with positive counts, all four failure counts equal to zero, writer mode `compact`, activation epoch `1`, rollback rehearsal epoch `2`, full commit SHAs, and agreement with the live activation ref/object. `reporter_commit` is the already-known activation-evidence/current-code commit, never the future commit containing `observation.json`.

The user-principal must make a separate pre-activation design decision that binds an exact positive `minimum_observation_duration_seconds` and exact `required_restart_count`; the manual advisory recommends at least one live restart but supplies no lawful numeric duration, so this plan does not invent either value. The measured delayed/retry inventory supplies `max_delayed_retry_horizon_seconds` and an exact committed path/digest; zero is valid only when that artifact proves no nonzero queue, lease, replica-lag, or delayed retry horizon. Restart evidence likewise resolves by committed path/digest. Validation requires ordered timestamps, duration at least the chosen minimum, observed restarts at least the chosen count, restart evidence bound to the live activation, all governed readers restarted/checked, and post-restart observation lasting at least the measured maximum horizon.

`profile_counts` has exactly the canonical keys `direct`, `verification-only`, `coordination-only`, `effect-only`, and `combined`; arbitrary labels fail. `observed_unit_profiles` maps every observed unit ID exactly once to one of those profiles, has no extra key, and recomputes exactly to `profile_counts`; at least three canonical counts are positive. Both measurement paths/digests must resolve to committed canonical artifacts with the same exact host binding, Phase-1 baseline digest, five profiles, five runs per profile, cohort/input digest, and instrumentation digest; the post-activation artifact must bind the live activation OID. Duration/restart/horizon, ten-unit/three-profile observation, and five-profile measurement are independent gates and none substitutes for another.

## R-INDEPENDENCE Abuse and Race Matrix

The implementation plan and final independent review must cover all of these pre-stated cases:

1. Missing, malformed, symbolic, peeled, non-blob, unknown-schema, wrong-field, duplicate-key, noncanonical, or unsupported-hash activation objects fail closed.
2. Activation epoch must increase exactly from the expected predecessor; stale, equal, lower, skipped, or predecessor-mismatched records cannot activate.
3. `governance.toml` cannot select compact behavior by itself. Ref absent plus epoch-1 mirror fails closed; epoch-1 ref plus epoch-0 mirror also fails closed.
4. The common-dir lock is shared across linked worktrees. Two worktrees cannot activate or append concurrently under different lock paths.
5. An independently locked clone, host, automation process, delayed queue, stale credential, or recovery writer blocks activation; a local common-dir lock is never claimed to serialize those external writers.
6. `HEAD`, activation ref, selected-store ref, event/cursor refs when compact, recovery ref when recovered-v1, mirror, in-flight digest, preparation, authorization, and host actor are all reread or freshly authenticated under the fence. Actor substitution, expiry/revocation after preflight, child broadening, binding/principal mismatch, or changing any bound value aborts before mutation.
7. The activation/event/cursor ref transaction is all-or-nothing. Injected failure at transaction start, prepare, or commit leaves every ref at its old OID.
8. The activation blob and genesis event have an acyclic binding: a canonical genesis descriptor digest is frozen first, the activation blob binds it, and the genesis event binds the resulting activation OID. The blob binds only the already-known implementation commit; the later preparation artifact binds its OID, and the later authorization artifact binds the preparation commit. No object embeds its containing or future commit.
9. Event records bind the exact activation object OID, not just epoch. An event prepared for another object with the same epoch is rejected.
10. Exact duplicate transition ID and payload are idempotent; changed payload, actor, scope, epoch, predecessor, or transition digest conflicts.
11. Event chain merge commits, multiple parents, missing parents, cycles, noncanonical trees, missing `record.json`, extra tree entries, and content-digest mismatch fail closed.
12. `mailbox.json` is exactly `compact-mailbox-payload/v1` with `schema`, `sender_principal`, `sender_binding_digest`, `recipient`, `kind`, `subject`, and `body`; authority values remain in the typed transition and immutable references rather than renderable text.
13. Per-seat cursor CAS rejects wrong seat, off-chain event OID, backward movement, skipped visibility rule, stale expected OID, foreign activation epoch, and cross-worktree races.
14. A reader accepts only a stable `A1 -> event/cursor view -> A2` snapshot with `A1 == A2` and every object bound to that activation. Cache keys include the activation OID; unstable reads, stale caches, and cross-epoch replicas fail closed.
15. During v1 mode every migrated reader returns the unchanged v1 result and compares a non-authoritative compact projection; any authority/effect divergence blocks activation.
16. During compact mode every migrated reader selects the event-chain projection and treats v1 artifacts as historical metadata only. A reader that silently falls back to v1 is a failure.
17. Every v1 publisher is fenced at its final commit point. After compact activation, direct invocation of a stale v1 shell/Python path produces no Markdown route, packet, cursor, receipt, report, ref, or effect state. Actor context from manifest, argv, environment, payload, role text, or repository file is rejected even when its visible fields match.
18. Verification keys invalidate on unit version, content, dependency, acceptance, evidence, or verifier binding changes; unrelated formatting does not invalidate.
19. Effects reserve before attempt. Crash before attempt cancels or remains safe; crash during attempt becomes outcome unknown; outcome unknown never retries or switches provider/executor.
20. Advisory dispatch has exactly the guarded ChatGPT and Opus callers. Duplicate intent, unavailable transport, ambiguous send, stale activation, and grant mismatch produce no second attempt.
21. Activation cannot proceed with an undispositioned v1 unit, live old writer process, unimported governed clone, dirty activation path, stale Operator report, non-GO preparation, expired/mismatched authorization, unnamed executor, or missing host-authenticated actor matching the authorization principal and binding digest.
22. Missing/deleted/lower activation ref after observation fails closed using the current mirror, event ref, and common-dir high-water record; it never bootstraps v1.
23. Rollback rehearsal writes epoch `2`/mode `v1` with predecessor equal to the epoch-1 activation object and binds an exact compact event-head cutoff plus the durable recovery object OID/digest. One transaction installs activation and recovery refs while event/cursors remain exact-unchanged. Stable readers and writers then select only `recovered-v1`; completed effects remain immutable, epoch-1 events are historical, and no ref is lowered or deleted.
24. Observation evidence cannot self-certify: duplicate unit IDs, fewer than three profiles, duration below the user-bound minimum, insufficient restart count, post-restart coverage shorter than the measured delayed/retry horizon, stale/inconsistent readers, a nonzero divergence/dispatch/unresolved count, stale reporter commit, live-ref/archive mismatch, event discontinuity, missing/mismatched same-host five-by-five pre/post measurement, or failed activated-head gate fails validation. A binding compact post-activation Operator GO is still required before docs-only completion.
25. Direct force-update, archive/ref deletion or movement, replace/graft injection, object-pruning risk, shallow/incomplete object availability, or an unreviewed alternate ref writer blocks activation. Attempt-specific archive refs plus tracked/archive-anchor reachability are verified before and after CAS. The protocol detects and stops; it does not claim a local lock can prevent privileged out-of-band mutation.
26. Provider, push, merge, cleanup, branch deletion, and live rollback remain impossible without their own distinct authority even when activation tests are green.
27. `scripts/packet_state.py`, its dedicated test, imports, and commands remain absent. Phase 4 consumes Phase-3 equivalence evidence and cannot defer or reverse that retirement.
28. The activation-only transition-control channel accepts only the pre-cutoff trigger and exact `preparation root -> preparation GO -> authorization -> execution GO` chain. Any mailbox/capacity/work field, extra tail commit, selected-v1-store mutation, wrong parent/path/identity, or use outside the drained attempt fails closed and cannot grant GO.
29. A failed/NITS preparation archive is never moved, deleted, or reused. A corrected attempt receives a fresh attempt ID, tracked path, archive ref, anchor, preparation root, and review chain; activation exact-verifies exactly one selected archive while retaining all failed-attempt objects.
30. CAS success followed by a crash before or during mirror/evidence finalization leaves all traffic stopped. Resume recomputes the commit from the frozen parent, exact two path modes/bytes, canonical tree, fixed identities/timestamp/offset/message, and prewritten evidence intent; it may exact-old-CAS `main` once or recognize the already-installed exact result, and never embeds the result OID, reruns, rewinds, or falls back from activation CAS.
31. Every live reader, replica, clone, and cache is inventoried before cutover. Readers that cannot restart against the authoritative common directory stay stopped; each serving reader invalidates epoch-0 cache state and proves an A1/selected-store/A2 epoch-1 view before serving. Stale or lagging readers fail unavailable, never v1 fallback.

---

### Task 1: Bind the exact predecessor state and create an isolated Phase-4 worktree

**Files:**

- Read: all predecessor handoffs and Operator reports named in Global Constraints
- Read: `tests/fixtures/compact_kernel/v1_surface_inventory.json`
- No production mutation before the route and worktree gates pass

**Interfaces:**

- Consumes: the nine fixed predecessor handoffs in Global Constraints, their exact report/join/integrated-head descendants, exact current `main`, clean ownership state, and current mailbox/capacity/lock/receipt state.
- Produces: one route-bound clean Phase-4 worktree; no ref mutation.

- [ ] **Step 1: Prove all predecessor gates**

Run coordinator seat status, capacity board, doctor, current Git log/status, receipt-state inventory, and exact head tests. For every fixed handoff, resolve its committed path, introduction/finalization commit, Git blob OID, and SHA-256 digest; read exact bytes from that commit; follow only the report, join, authorization, and integrated-head references inside it; and require every referenced commit plus integrated code SHA to be an ancestor of current `main`. Require canonical GO, terminal `done_evidence`, no post-GO production edit, merged-tree evidence, and no active PPL receipt. The ChatGPT disposition must be `withdrawn-preserved` or `integrated-reviewed`. A branch-only candidate or generic plan checkbox is not accepted.

Confirm the Phase-3 integrated handoff binds `compact_runtime.py`, `compact_event_store.py`, `compact_effects.py`, and `advisory_dispatch.py`, target-bridge compatibility, provider/receipt mutation counts `0`, writer v1/epoch 0, compact selector false, and its exact merged main SHA. Also require its retired-surface and preservation-diff evidence, then prove `scripts/packet_state.py`, `tests/unit/test_packet_state.py`, production imports, and executable commands remain absent while compact mapping/property tests still cover every retired meaning. Bind the complete content-addressed predecessor set and current-main SHA into the Phase-4 route; any newer conflicting handoff or overlapping edit blocks.

- [ ] **Step 2: Prove exact target paths are owner-clean**

Run:

```bash
env -u GIT_INDEX_FILE git status --short -- \
  governance.toml ARCHITECTURE.md OPERATIONS.md AGENTS.md CLAUDE.md \
  scripts/kernel_activation.py scripts/capability_reducer.py \
  scripts/capability_v1_adapter.py scripts/v1_recovery_store.py \
  scripts/compact_runtime.py \
  scripts/compact_event_store.py scripts/compact_effects.py \
  scripts/advisory_dispatch.py scripts/protocol_capacity.py \
  scripts/protocol_capacity_board.py scripts/protocol_mailbox.py \
  scripts/status.py scripts/bus_unread.py scripts/ledger_start_guard.py \
  scripts/continuation_readiness.py scripts/protocol_doctor.py \
  scripts/codex_protocol_model.py scripts/route_manifest.py \
  scripts/route_capability.py scripts/verification_report_gate.py \
  scripts/consume_reviewer_result.py scripts/chatgpt_pro_consult.py \
  scripts/opus_review_bridge.py scripts/opus_review_receipts.py \
  coordination/bin/send-event coordination/bin/consume-events \
  .agents/skills/four-seat-protocol/scripts/seat_status.py \
  tests/unit tests/integration docs/protocol
```

Expected: no output for implementation-owned paths. A dirty path requires a new exact owner handoff; do not stash, reset, copy, or absorb it.

- [ ] **Step 3: Create the route-bound worktree**

After one capacity-valid coordinator route commits, run:

```bash
ROUTE_BASE="$(env -u GIT_INDEX_FILE git rev-parse 'HEAD^{commit}')"
env -u GIT_INDEX_FILE git worktree add \
  .worktrees/compact-kernel-phase4-activation \
  -b codex/compact-kernel-phase4-activation \
  "$ROUTE_BASE"
```

Expected: one clean worktree at the routed full SHA. All remaining commands run inside it unless explicitly marked primary-checkout or disposable-repository.

### Task 2: Implement strict activation records, high-water safety, and the shared writer fence

**Files:**

- Create: `scripts/kernel_activation.py`
- Create: `scripts/kernel_transition_verification.py`
- Create: `tests/unit/test_kernel_activation.py`
- Create: `tests/unit/test_kernel_transition_verification.py`
- Modify: `scripts/target_binding.py`
- Modify: `tests/unit/test_target_binding.py`

**Interfaces:**

- Produces the activation record/snapshot/fence APIs in Fixed Interfaces.
- Produces the new, activation-only transition-control trigger/report parser and publisher law described above. It accepts exactly the pre-cutoff route-bound preparation attempt, fixed root/GO/authorization/execution parent chain, finite questions/commands, host-authenticated Operator identity, and `GO|NITS|FAIL`; it cannot publish mailbox/capacity/work semantics or operate outside a drained activation transition.
- Keeps `target_binding.load_kernel_mirror()` declarative and non-selecting.

- [ ] **Step 1: Write RED parser and ref-object tests**

Cover every fixed activation field, canonical JSON bytes, Git SHA-1 and SHA-256 object IDs, duplicate/unknown keys, bool-as-int epoch, invalid mode, invalid implementation commit, wrong object type, symbolic ref, missing object, predecessor mismatch, malformed genesis descriptor, illegal/missing recovery fields by epoch/mode, and Git replace/graft isolation. Explicitly reject old or invented `activation_commit`, `preparation_commit`, `authorization_digest`, `authorization_expires_at`, `executor_principal`, and report fields so no future/self commit can enter the blob. Assert only finite `KernelActivationError.code` values escape.

In the transition-verification tests, reject any trigger created after cutoff; any path, parent, attempt ID, stage, reviewed commit, command, Operator identity, result, archive, high-water/source digest, or previous-tail mismatch; any mailbox/capacity/work field; any fourth pre-CAS tail commit; and any unauthenticated or expired report. Prove the pre-cutoff trigger plus preparation-root derivation permits exactly one preparation report and, after the exact authorization direct child, one execution report. This activation-only schema/publisher/validator and its protocol-law exception must be implemented, documented, prompt-synchronized, and covered by the Phase-4 implementation Lane V before it can replace the ordinary mailbox GO path during a drain.

- [ ] **Step 2: Write RED bootstrap/high-water tests**

Bootstrap is accepted only when activation/event/cursor/recovery refs are all absent, mirror is exactly epoch 0/writer v1, and the common-dir high-water file is absent. After observing epoch 1, deleting or lowering activation ref fails even from a linked worktree or old checkout. The high-water file is a monotonic safety cache, not a selector, and is written only after a valid ref observation.

- [ ] **Step 3: Write RED shared-lock and in-fence-reread tests**

Use two linked worktrees sharing one common directory. Pause writer A after preflight, advance HEAD or a ref through writer B, then release A. Assert A aborts before mutation. Assert both worktrees resolve exactly the same lock inode/path and no code accepts a per-worktree lock. Under the acquired fence, issue the fresh host challenge and cover actor replacement, replayed challenge, expiry/revocation after preflight, parent/child broadening, repository/action mismatch, principal/binding mismatch with authorization, and actor spoofing through manifest/argv/environment/payload. No mutation occurs before the actor is authenticated and matched.

- [ ] **Step 4: Write RED stable-view tests**

Move activation, event, cursor, and recovery refs between the first activation read and its reread. In compact selection, accept only a view whose two activation OIDs match and whose event/cursor objects all bind that OID. In recovered-v1 selection, accept only a view whose two activation OIDs match and whose recovery object/digest binds that activation. Exhausting the three-attempt read bound raises `unstable_activation_view`; no branch consults `governance.toml` or legacy v1 as fallback after a positive epoch.

- [ ] **Step 5: Implement the minimum activation module**

Use trusted `/usr/bin/git --no-replace-objects --literal-pathspecs`, strict environment removal of inherited `GIT_*`, `fcntl.flock`, canonical JSON, and descriptor-relative common-dir discovery. `load_activation` verifies mirror consistency but selects behavior only from the ref. `writer_selection` returns exactly `legacy-v1`, `compact`, or `recovered-v1`; `load_stable_view` implements the matching bounded activation/selected-store/activation protocol. `writer_fence` acquires the shared lock first, creates a fresh challenge, calls the host-installed `AuthenticatedActorSource` inside the fence, validates it through `authenticate_host_actor`, rereads `HEAD`/refs/authorization, requires the expected selection and activation OID, and yields immutable actor plus observed OIDs. No repository, CLI, environment, or payload fallback exists.

- [ ] **Step 6: Run focused GREEN**

```bash
env -u GIT_INDEX_FILE .venv/bin/python -m pytest \
  tests/unit/test_kernel_activation.py \
  tests/unit/test_kernel_transition_verification.py \
  tests/unit/test_target_binding.py -q
```

Expected: all tests pass; no ref in the real repository changes.

### Task 3: Activate reducer modes and complete the event/payload/cursor store

**Files:**

- Modify: `scripts/capability_reducer.py`
- Modify: `scripts/capability_v1_adapter.py`
- Modify: `scripts/compact_runtime.py`
- Modify: `scripts/compact_event_store.py`
- Create: `scripts/v1_recovery_store.py`
- Modify: `tests/unit/test_capability_reducer.py`
- Modify: `tests/unit/test_capability_reducer_replay.py`
- Modify: `tests/unit/test_capability_v1_adapter.py`
- Modify: Phase-3 runtime/event-store tests
- Create: `tests/unit/test_v1_recovery_store.py`

**Interfaces:**

- Extends `ActivationState.mode` from shadow-only to `Literal["shadow", "active", "recovered"]`; shadow requires epoch `0`, compact active requires epoch `1` or higher with mode compact, and recovered requires epoch `2` or higher with mode v1 plus a bound recovery object.
- Extends `CompactReaderProjection` to report mode `shadow|active|recovered`, writer selection `legacy-v1|compact|recovered-v1`, exact activation object OID, selected-store OID, and the same reader-unit tuple.
- Retains the exact Phase-3 `compact-event/v1`, `compact-mailbox-payload/v1`, and `compact-cursor/v1` schemas and activates their six cursor-ref read/CAS operations without inventing a second payload.
- Adds the exact `materialize_v1_recovery` rollback-readiness seam and durable recovery-store contracts defined above.

- [ ] **Step 1: Write RED active-mode reducer tests**

Assert epoch 0/active, epoch 0/recovered, positive-epoch/shadow, compact/recovered mismatch, v1/active mismatch, stale epoch, and activation-object mismatch fail. Assert epoch-1 active transition application preserves duplicate, scope, principal, precondition, and unit-version laws. Assert epoch-2 recovered projection reads the durable recovery state without applying compact events as new authority. Mutating either selected branch back to shadow or legacy v1 must flip a test.

- [ ] **Step 2: Write RED payload and chain-shape tests**

The optional canonical `mailbox.json` contains exactly `schema`, `sender_principal`, `sender_binding_digest`, `recipient`, `kind`, `subject`, and `body`. The event record binds its blob OID and SHA-256, and that digest must equal the transition `content_digest`. Authority-bearing event class, work/revision/unit/scope, verification, effect, and activation values stay in the typed transition and immutable references. Cover missing/extra tree entries, payload mismatch, merge commits, wrong parent, wrong activation object, event cycles, changed duplicate, and linked-worktree races.

- [ ] **Step 3: Write RED cursor tests**

Create one cursor test per receiving seat plus invalid-seat, off-chain, backward, stale-CAS, cross-epoch, and two-worktree races. A cursor ref update and event append both require the shared activation fence and exact expected OID.

- [ ] **Step 4: Write RED reverse-projection tests**

Build compact histories containing coordination, verification, effect, advisory, duplicate, and terminal units. Materialize v1 recovery through an exact event OID, prepare canonical `recovery.json`/`state.json` objects without moving refs, and prove every accepted unit appears exactly once, completed effects remain immutable references, and any missing event, unresolved unit, nondeterministic value, changed cutoff, foreign activation OID, wrong recovery predecessor, or object/digest mismatch fails. Replaying the same cutoff produces byte-identical state, tree, object OID, and digest. In a disposable repository, atomically install epoch 2 plus the recovery ref, prove stable readers select recovered state, and prove the next recovered-v1 writer advances only the recovery ref.

- [ ] **Step 5: Replace the structurally false selector**

Replace the Boolean `compact_writer_active` seam with `compact_runtime.writer_selection(root)`. It returns `legacy-v1` only for valid epoch-0 bootstrap, `compact` only for a valid compact record whose `implementation_commit` is GO-reviewed and an ancestor of current HEAD, and `recovered-v1` only for a higher-epoch v1 record with a stable matching recovery ref/object/digest. It raises `CompactRuntimeError` on invalid or ambiguous state; it never collapses recovered v1 into the legacy store or falls back after an observed activation error.

- [ ] **Step 6: Run reducer/store GREEN**

```bash
env -u GIT_INDEX_FILE .venv/bin/python -m pytest \
  tests/unit/test_capability_reducer.py \
  tests/unit/test_capability_reducer_replay.py \
  tests/unit/test_capability_v1_adapter.py \
  tests/unit/test_compact_runtime.py \
  tests/unit/test_compact_event_store.py \
  tests/unit/test_v1_recovery_store.py -q
```

Expected: all pass in temporary repositories; the live activation/event/cursor/recovery refs remain absent.

### Task 4: Migrate all required readers under dual-read semantics

**Files:**

- Modify: `scripts/protocol_capacity.py`
- Modify: `scripts/protocol_capacity_board.py`
- Modify: `scripts/status.py`
- Modify: `scripts/bus_unread.py`
- Modify: `scripts/consume_bus.py`
- Modify: `scripts/ledger_start_guard.py`
- Modify: `scripts/continuation_readiness.py`
- Modify: `.agents/skills/four-seat-protocol/scripts/seat_status.py`
- Modify: `scripts/protocol_doctor.py`
- Modify: `scripts/codex_protocol_model.py`
- Modify: the matching unit tests for every reader
- Modify: `tests/unit/test_consume_bus.py`

**Interfaces:**

- Every reader calls one `compact_runtime.project_reader_state` path and takes its inputs from `kernel_activation.load_stable_view`: legacy artifacts only for epoch 0, event/cursors for compact, or the durable recovery object for recovered-v1.
- In v1 mode, each reader returns its existing result and compares the compact projection.
- In compact mode, each reader returns the compact projection and may use legacy v1 only as immutable historical metadata. In recovered-v1 mode, it returns the durable recovery projection and may use neither compact events nor legacy Markdown as current authority.

- [ ] **Step 1: Extract v1 readers without changing behavior**

Rename existing internal implementations to explicit `_v1` helpers while keeping public signatures stable. Record current golden CLI/stdout/JSON fixtures before selection logic. Do not change output wording merely to ease migration.

- [ ] **Step 2: Add shared projection adapters**

Map capacity packets/routes, mailbox events, cursor visibility, ledger route selection, continuation summaries, seat status, and doctor fields into the Phase-3 `LegacySemanticObservation` and `ReaderUnitProjection` contracts. Every selected read starts with a stable activation/selected-store snapshot and caches only by activation object OID plus event tip or recovery OID. Specialized effect/advisory states remain referenced evidence, not parallel route authority.

- [ ] **Step 3: Prove v1-selected dual-read**

For every reader, feed identical v1 and compact meanings and assert byte-identical existing output. Inject both more-permissive and more-restrictive divergence and assert a finite blocking result rather than v1 fallback. Keep live mode epoch 0/v1 throughout these tests.

- [ ] **Step 4: Prove compact-selected reads**

In disposable repositories, activate epoch 1, append compact events, omit or stale the equivalent legacy-v1 event, and assert capacity, unread, route selection, continuation, seat status, and doctor select compact. Then atomically install epoch 2/recovered-v1 and assert the same readers select the durable recovery ref while event/cursors remain historical. Delete/corrupt either selected store and assert failure, never fallback to the other store or epoch-0 artifacts.

- [ ] **Step 5: Run reader GREEN**

```bash
env -u GIT_INDEX_FILE .venv/bin/python -m pytest \
  tests/unit/test_protocol_capacity.py \
  tests/unit/test_status.py \
  tests/unit/test_protocol_mailbox.py \
  tests/unit/test_codex_ledger_bridge.py \
  tests/unit/test_seat_status_all.py \
  tests/unit/test_protocol_doc_integrity.py \
  tests/unit/test_protocol_prompt_sync.py -q
```

Expected: all pass, including unchanged v1 golden output and fail-closed compact selection.

### Task 5: Fence every governed writer and enforce one selected writer

**Files:**

- Modify: `scripts/route_manifest.py`
- Modify: `scripts/route_capability.py`
- Modify: `scripts/verification_report_gate.py`
- Modify: `scripts/consume_reviewer_result.py`
- Modify: `scripts/chatgpt_pro_consult.py`
- Modify: `scripts/opus_review_bridge.py`
- Modify: `scripts/opus_review_receipts.py`
- Modify: `coordination/bin/send-event`
- Modify: `coordination/bin/consume-events`
- Modify: matching unit tests and `tests/fixtures/compact_kernel/v1_surface_inventory.json`

**Interfaces:**

- Epoch-0 `legacy-v1` executes one existing v1 write and zero compact/recovery writes.
- Epoch-1 `compact` executes one compact event/cursor/reservation transition and zero legacy/recovery authority writes.
- Higher-epoch `recovered-v1` executes one durable recovery-store write and zero legacy/compact writes.
- All paths use `kernel_activation.writer_fence`, the host-supplied authenticated actor obtained inside it, and the exact activation/selected-store snapshot observed there.

- [ ] **Step 1: Refresh the production write inventory**

Start from the exhaustive 14-class Phase-2 producer ledger. Grep every write to mailbox, capacity packet, verification report, capability receipt, provider receipt, consultation state, event ref, cursor ref, recovery ref, and effect/advisory reservation. Give every existing and newly discovered writer class one explicit `legacy-v1` / `compact` / `recovered-v1` disposition before editing; the committed test proves every nonempty `writer_paths` component and every writer path appears exactly once. A writer cannot be exempted solely because it is a shell script or manual CLI. Assert `packet_state` remains retired and contributes no producer/import/command.

- [ ] **Step 2: Add RED exclusive-writer tests**

For each producer, assert legacy-v1 changes only its old store, compact changes only the event/specialized compact store, and recovered-v1 changes only the recovery store. Pause a legacy-v1 producer immediately before its old-store commit, activate compact, then release it and assert the final in-fence activation/actor reread prevents the write. Inject activation drift, actor replacement, actor expiry/revocation, child broadening, authorization drift, and selected-store drift after command parsing and before every mutation; assert in-fence refusal. Manifest/argv/environment/payload actor spoofing must never reach a write.

- [ ] **Step 3: Route coordination and cursor writes**

In compact mode `send-event` validates the frozen Phase-3 recipient/kind vocabulary, builds one strict compact payload and transition, and appends it to the compact event ref without creating or staging a Markdown authority file. `consume-events` and `scripts/consume_bus.py` converge on one host-bound cursor path that advances only the authenticated caller's compact cursor ref by exact CAS. Epoch-0 legacy-v1 remains byte-for-byte compatible; recovered-v1 routes the equivalent v1-semantic update only to `V1_RECOVERY_REF`.

- [ ] **Step 4: Route verification/effect/advisory writes**

Verification publication stores the signed report as specialized evidence and appends one compact verification transition; it creates no v1 verification-authority event in compact mode. Effects reserve through `compact_effects` before attempt and append each state transition. ChatGPT and Opus retain their terminal specialized stores but dispatch only through the Phase-3 advisory intent claim and append advisory lifecycle transitions. Provider output remains advisory.

- [ ] **Step 5: Prove crash and ambiguity recovery**

Inject crashes between reservation/event append, event append/attempt, attempt/outcome write, report evidence/event append, and cursor/event reads. Each state must be safely recoverable, terminal, or outcome unknown; no path retries, double-spends, double-publishes, or silently treats missing evidence as GO.

- [ ] **Step 6: Run writer GREEN**

```bash
env -u GIT_INDEX_FILE .venv/bin/python -m pytest \
  tests/unit/test_route_manifest.py \
  tests/unit/test_route_capability.py \
  tests/unit/test_verification_report_gate.py \
  tests/unit/test_chatgpt_pro_consult.py \
  tests/unit/test_opus_review_bridge.py \
  tests/unit/test_opus_review_receipts.py \
  tests/unit/test_opus_target_review_bridge.py \
  tests/unit/test_protocol_prompt_sync.py \
  tests/unit/test_coordination_tooling.py \
  tests/unit/test_consume_bus.py \
  tests/unit/test_compact_kernel_surface_inventory.py -q
```

Expected: all pass with real provider attempts, receipt-store mutations, and live ref changes equal to zero. The target-aware bridge suite proves Phase-4 changes to generic Opus/receipt writers retain sealed target closure, prompt authority, route/consent/token binding, CAS identity, and unavailable semantics.

### Task 6: Add end-to-end, mixed-version, measurement, and doctor gates

**Files:**

- Create: `tests/integration/test_protocol_e2e.py`
- Modify: `scripts/protocol_effectiveness_report.py`
- Modify: `scripts/protocol_doctor.py`
- Modify: `tests/unit/test_protocol_effectiveness_report.py`
- Modify: `tests/unit/test_protocol_doc_integrity.py`
- Modify: `ARCHITECTURE.md`, `OPERATIONS.md`, `AGENTS.md`, `CLAUDE.md`
- Modify: operative Codex/Claude protocol and skill mirrors

**Interfaces:**

- `protocol_doctor.py --current` reports activation object, epoch, writer selection, event tip/cursors or recovery tip as selected, divergence, and mixed-writer violations; it never activates.
- The effectiveness reporter runs exactly `direct`, `verification-only`, `coordination-only`, `effect-only`, and `combined`, exactly five runs per profile, and compares current results with the committed Phase-1 five-profile baseline. It emits canonical artifacts binding host, baseline, cohort/input, and instrumentation digests.

- [ ] **Step 1: Build the disposable end-to-end matrix**

Cover the exact five profiles across bootstrap legacy-v1, dual-read legacy-v1, epoch-1 compact, stale v1 process, duplicate event, ambiguous effect, advisory unavailable, cursor consume, linked worktree, independently locked clone refusal, stable-read ref churn, and epoch-2 recovered-v1 installation/selection. No real provider or remote is used; effect/advisory profiles stop at their durable local lifecycle boundaries unless separately authorized.

- [ ] **Step 2: Add transactional activation fault injection**

Exercise Git ref transaction start/prepare/commit failures and process termination at every boundary. Compare the complete ten-ref inventory (activation, events, six cursors, recovery, selected attempt archive) before and after. For epoch 1, activation/event/six cursor refs change, recovery remains absent, and archive is exact-verified unchanged; for epoch 2, only activation/recovery change and event/six cursor/archive values are exact-verified unchanged. Also inject crashes before evidence-intent persistence, after intent fsync/before CAS, after CAS/before finalization, after metadata object creation/before `main` CAS, and after `main` CAS/before return. Assert the evidence contains no result/self OID; perturb parent, either file byte/mode, tree membership, author/committer name/email/timestamp/offset, or message and require failure; prove exact replay recomputes one OID and recognizes an already-installed result without a second CAS. The pre-CAS cases preserve epoch-0 mirror under drain, while post-CAS cases permit only exact idempotent finalization. Any partial authority update, unintended primary commit, or fallback fails the test.

- [ ] **Step 3: Add `--current` doctor output**

The doctor reports facts from the activation/event/cursor/recovery refs and current HEAD/mirror. It emits a blocking failure for missing/lower/mismatched activation, split writer modes, stale cursors, event activation mismatch, recovery object/digest mismatch, wrong selected store, unstable cross-ref reads, unauthorized alternate ref writers, incomplete object availability, high-water regression, or unresolved divergence. It never decides a route, verdict, or activation.

- [ ] **Step 4: Implement and trial the exact five-by-five measurement**

Extend the committed collector with a disposable compact-candidate mode and a live-selected-store mode that share one immutable input/cohort/instrumentation descriptor. Run a disposable trial here to prove schema and thresholds, but do not claim it as the activation preflight measurement. The activation-host run in Task 8 must produce `precutover-compact-five-profile.json`; the live selected-store run in Task 11 must produce `postactivation-live-five-profile.json`. Each canonical artifact contains exactly five named profiles, five runs per profile, host-binding digest, Phase-1 baseline path/digest, candidate or activation OID, cohort/input digest, instrumentation digest, per-run results, aggregate metrics, and safety counts. Require zero safety-count regressions, no latency regression beyond the larger of 5 percent or 50 ms, no artifact-per-result increase, and improvement in at least one latency or artifact metric. Any profile/run omission or measurement failure blocks activation or observation respectively.

- [ ] **Step 5: Synchronize operative truth**

Document the exact refs, archive reachability, lock, bootstrap rule, reader selection, writer selection, drain, finite transition-control trigger/report exception, CAS-to-metadata-finalization seam, observation, rollback, and exclusions. The protocol model and active Director/Operator/coordinator mirrors must state that specialized transition GO is lawful only for the exact pre-cutoff trigger and drained activation attempt; ordinary Lane-V/mailbox GO remains unchanged elsewhere. Update `ARCHITECTURE.md` file/line claims after implementation. Prompt-sync and doc-integrity tests must compare canonical model fragments rather than copied free text.

- [ ] **Step 6: Run the full pre-activation code gate**

```bash
env -u GIT_INDEX_FILE .venv/bin/python -m pytest tests/unit -q
env -u GIT_INDEX_FILE .venv/bin/python -m pytest \
  tests/integration/test_protocol_e2e.py -q
env -u GIT_INDEX_FILE .venv/bin/python scripts/ci_smoke.py
env -u GIT_INDEX_FILE .venv/bin/python scripts/protocol_doctor.py --current --wave 2
env -u GIT_INDEX_FILE git diff --check
```

Expected: tests/smoke pass, doctor reports epoch 0/writer v1 with compact inactive and zero divergence, and diff check is silent.

### Task 7: Freeze the implementation candidate and obtain pre-activation GO

**Files:**

- Create: one Lane-V descriptor for the exact implementation range
- Create: one canonical verify-request
- Create after GO: `docs/HANDOFF-director-2026-07-16-compact-kernel-phase4-ready.md`
- Create after separately authorized integration: `docs/HANDOFF-coordinator-2026-07-16-compact-kernel-phase4-implementation-integrated.md`

**Interfaces:**

- Produces a `candidate` / `pending_operator_go` implementation with mirror still epoch 0/v1, then a docs-only readiness handoff after GO.
- Produces no activation object, event ref, cursor ref, provider attempt, merge, or push.

- [ ] **Step 1: Commit task-sized implementation changes**

Use one commit per Tasks 2-6 with strict pathspecs and fresh tests. Mark any implementation status artifact `candidate` / `pending_operator_go`. No task commit changes the live mirror from epoch 0/v1. Reviewer fixes are append-only and require renewed review of the final range.

- [ ] **Step 2: Obtain independent spec and quality review**

The spec reviewer maps every abuse/race case to code/tests. The quality reviewer inspects the actual range for lock identity, in-fence host actor authentication, Git environment isolation, both multi-ref transaction shapes, canonical object parsing, archive reachability, commit/object acyclicity, three-way writer selection, legacy/recovery fallback, writer omissions, crash recovery, the narrowly scoped activation transition-control authority exception, target-aware bridge compatibility, and provider/effect authority leaks. Any blocking finding stops before Lane V.

- [ ] **Step 3: Obtain binding Operator GO**

Create the lawful descriptor/request for the exact final implementation range. Operator reruns Task 6 plus the complete target-aware bridge provider-free suite, mutates the three-way selector, in-fence actor validation, epoch-1/epoch-2 ref transactions, recovery selection, writer guards, transition-control trigger/report parent law, and CAS-to-finalizer crash states; verifies the exhaustive surface inventory, archive-object reachability, provider attempts/receipt-store mutation counts `0`; and returns GO/NITS/FAIL. This consumer-compatibility question is folded into the existing implementation pass, not launched as a redundant reviewer. GO authorizes only an activation-ready candidate; it does not authorize merge or activation.

- [ ] **Step 4: Commit only the GO readiness handoff**

After GO, create `docs/HANDOFF-director-2026-07-16-compact-kernel-phase4-ready.md` with exact implementation base/head/range, Operator report path/verdict, test evidence, exhaustive producer inventory digest, and explicit epoch-0 legacy-v1 state. Commit only that handoff; do not rewrite candidate evidence, code, tests, config, or schemas. The handoff grants no merge or activation authority and does not trigger duplicate Lane V for unchanged production.

- [ ] **Step 5: Merge only under separate authorization**

After user authorizes local integration for the exact reviewed base/head, the named integrator merges the GO-reviewed candidate and reruns the full merged-tree gate, including the target-aware bridge suite and provider/receipt before/after manifest equality. A conflict or post-GO edit stops for renewed review. Push remains unauthorized. The merged head continues to run epoch 0/v1.

The coordinator then commits only `docs/HANDOFF-coordinator-2026-07-16-compact-kernel-phase4-implementation-integrated.md`, binding the user authority, named integrator, readiness handoff/report, exact reviewed and integrated main SHAs, merged-tree results, epoch `0`, writer `v1`, and push/activation status `not-authorized`. Capture its commit/blob/digest and require it changes only that path. Task 8 consumes this fixed artifact; branch state or chat alone is insufficient.

### Task 8: Drain v1, prepare immutable activation objects, and obtain preparation GO

**Files:**

- Read only during preparation: `governance.toml` at epoch `0`, writer `v1`
- Create: `coordination/activation/archive/compact-kernel-phase4-2026-07-16-epoch-1-<preparation-attempt-id>.json`
- Create: `coordination/activation/compact-kernel-phase4-2026-07-16-<preparation-attempt-id>-preparation.json`
- Create: `coordination/activation/compact-kernel-phase4-2026-07-16-observation-policy.json`
- Create: `logs/capability-first/phase4-compact-activation-2026-07-16/delayed-retry-inventory.json`
- Create: `logs/capability-first/phase4-compact-activation-2026-07-16/precutover-compact-five-profile.json`
- Create: `logs/capability-first/phase4-compact-activation-2026-07-16/preflight.json`
- Create: `logs/capability-first/phase4-compact-activation-2026-07-16/rollback-rehearsal.json`
- Create: fixed specialized preparation-GO evidence under `coordination/activation/reports/`

**Interfaces:**

- Consumes: the fixed Phase-4 implementation-integrated handoff, merged activation-ready code, implementation GO, a capacity-valid preparation route committed before cutoff, a fresh explicit user authorization naming the drain/preparation executor and routed Director preparation owner, exact host/repository/common directory/action allowlist/expiry, and the user's exact observation-duration/restart design decision.
- Produces on the clean primary `main` checkout one exact preparation-root commit plus prepared ten-ref inventory/map with `status=candidate` / `gate=pending_preparation_go`; activation/event/cursor/recovery refs and the mirror remain unchanged, while the non-authoritative immutable archive ref is created at its exact prepared anchor. No activation executor is authorized yet.

- [ ] **Step 0: Obtain bounded drain/preparation and observation-policy authority**

Before stopping anything, the user-principal separately names one drain/preparation executor, one routed Director preparation owner, the exact activation host/repository/Git common directory, an expiry, and an allowlist limited to admission stop, queue freeze, lease/credential revocation, governed process/reader stop, object materialization, one exact archive-ref creation, and the exact preparation-root paths. It explicitly forbids activation/event/cursor/recovery ref mutation, mirror mutation, provider/remote effects, push, cleanup, and executor substitution. The coordinator only commits the route before cutoff and reconciles results.

The same pre-cutoff decision records exact positive `minimum_observation_duration_seconds` and exact `required_restart_count` in `coordination/activation/compact-kernel-phase4-2026-07-16-observation-policy.json`. If the user has not decided these advisory-derived values, preparation blocks; the plan does not infer them.

- [ ] **Step 1: The named executor drains and freezes the operational v1 domain**

Only the named drain/preparation executor performs these host/process effects. Stop new workload/route/effect/advisory admissions; freeze delayed and retry queues; revoke or expire old writer leases, credentials, and scheduled automation; stop old writer processes and every reader/cache/clone that cannot restart against the authoritative common directory; enumerate every active/blocked/incomplete v1 unit; and record one completion, cancellation, or migration disposition. Write canonical `delayed-retry-inventory.json` with sanitized queue/lease/automation/replica classes, exact counts, latest eligible-at or expiry boundary per nonempty class, measurement time, computed nonnegative `max_delayed_retry_horizon_seconds`, repository/common-directory binding, and source-command digest. Zero is valid only when every enumerated class is empty or already expired. Leave only the primary common directory write-capable.

All preparation route, role assignment, exact path/parent contracts, and Operator transition-control authority must already be committed before this cutoff. Capture the final operational v1 high-water and source-state digest only after the drain. From that point through CAS, no selected-v1-store, mailbox, capacity, route, work, effect, advisory, retry, or data-plane write is allowed. The preparation-root commit may then be followed by exactly the three specialized transition-control commits defined above. Any other live writer, independently locked clone, undispositioned unit, queued retry, reader replica, selected-store mutation, or unexpected HEAD commit invalidates preparation.

- [ ] **Step 2: Build the migration chain without moving refs**

Deterministically adapt the frozen operational v1 history into canonical transition/mailbox descriptors that do not contain the activation OID. Freeze their ordered migration-chain digest, final operational v1 high-water digest, source-state digest, and acyclic event-genesis descriptor digest. Build the epoch-1 activation bytes from those values plus the already-known GO-reviewed `implementation_commit`, write those identical bytes to the route-bound attempt-specific archive path, and compute the Git blob OID. The blob contains no preparation/authorization/report/executor or future commit. Only then materialize the genesis event commit and exact six cursor blobs bound to that activation OID.

Create one canonical archive anchor commit whose tree contains the exact activation blob and six cursor blobs and whose parent is the prepared genesis event commit. Under the separately authorized preparation action and common-dir lock, exact-old-CAS the previously absent attempt-specific immutable archive ref to that anchor. Validate the tracked activation path's blob OID, anchor tree/blob OIDs, genesis parent, `git fsck`, object format, non-shallow repository, absent replace/graft state, protected-ref/direct-update inventory, and object availability. `git for-each-ref` must still show activation/event/cursor/recovery refs absent while that attempt archive ref equals only its prepared anchor. The preparation artifact binds the complete descriptor/object/archive mapping; failure never deletes or moves the archive ref, and any corrected candidate uses a fresh attempt ID/ref/path.

- [ ] **Step 3: Rehearse epoch-2 rollback in a disposable clone**

Activate epoch 1/compact, append events, freeze an exact compact event-head cutoff, and run `materialize_v1_recovery` through that cutoff. Prepare canonical recovery objects at `V1_RECOVERY_REF`, then transactionally install epoch 2/v1 plus the recovery ref with predecessor equal to the epoch-1 object and the recovery object OID/digest bound into the epoch-2 record. Exact-verify event and all six cursor refs remain unchanged. Prove every accepted compact event is represented exactly once, completed effects remain recorded, unresolved units are empty, stable readers select recovered state, the next v1-semantic writer advances only the recovery ref, epoch-1 events become historical, and no ref is deleted/lowered. Persist sanitized object/ref maps and selection results to `rollback-rehearsal.json`.

- [ ] **Step 4: Run the same-host disposable compact five-by-five measurement**

On the exact intended activation host, run the disposable compact candidate for exactly `direct`, `verification-only`, `coordination-only`, `effect-only`, and `combined`, five runs each, with the Phase-1 cohort/input/instrumentation contract. Commit canonical `precutover-compact-five-profile.json` binding the host, baseline, candidate implementation, activation OID, cohort/input, instrumentation, all 25 runs, aggregates, and threshold result. No real provider, remote, or external effect is used. Any missing run, host ambiguity, safety regression, or threshold failure blocks preparation.

- [ ] **Step 5: Write the one-way preparation artifact and preflight**

`preflight.json` binds the implementation commit/GO report, epoch-1 record OID and attempt-specific tracked archive path/blob, exact ten-ref inventory/ref operation map for activation/event/six cursors/recovery/archive, final operational v1 high-water, source-state, migration-chain, genesis and in-flight disposition digests, governed writer/reader/clone/cache dispositions, the exact committed delayed/retry inventory path/digest and recomputed horizon, the exact observation-policy decision, intended future epoch-1 `governance.toml` bytes/digest, the pre-cutoff transition-control trigger and exact three-commit tail grammar, archive/ref/object reachability and GC/replace/shallow/protected-ref evidence, the exact pre-cutover measurement path/digest/host/baseline/input/instrumentation values, rollback-rehearsal digest, executed gates, and `status="candidate"` / `gate="pending_preparation_go"`. It does not bind the preparation artifact or its containing commit.

Then write canonical `protocol-kernel-activation-preparation/v1`, which binds the same implementation commit, activation record bytes/OID and archive anchor/ref/path, exact ten-ref inventory/operations, `preflight.json` digest, measurement/rollback/observation-policy/horizon/control-trigger digests, intended mirror bytes/digest, command digest, and pending status. It contains no preparation commit, authorization, executor, expiry, or future GO. This one-way ordering is acyclic.

- [ ] **Step 6: Commit the preparation head**

Task 8 runs only in the clean primary checkout on branch `main` after Task 7's separately authorized integration and merged-tree gate. Under the Step-0 user authority, the routed Director preparation owner commits the preparation root directly on primary `main`; there is no implicit merge or coordinator commit. The root changes only the attempt-specific tracked activation archive, preparation artifact, observation-policy artifact, delayed/retry inventory, preflight, pre-cutover measurement, and rollback rehearsal. It does not change truth docs, `governance.toml`, or activation/event/cursor/recovery refs; the separately created attempt archive ref already equals the bound anchor. Require strict pathspecs, exact captured parent, and one-parent topology. Record the root SHA only in later artifacts; never amend it into a contained object.

This root closes the preparation phase and starts the exact transition-control tail. The selected v1 store remains frozen. The only lawful chain is `preparation root -> preparation GO -> authorization -> execution GO`, with each commit the sole direct child of the preceding commit. Any other commit invalidates the attempt. A different preparation after NITS/FAIL uses a fresh attempt ID/archive ref/path and new root; failed archives remain immutable.

- [ ] **Step 7: Obtain fresh preparation GO**

Using only the already committed pre-cutoff transition trigger, the routed Operator verifies the exact preparation root, absence of a self/future commit field, implementation ancestry/GO, preparation/preflight/object/archive bytes, migration chain, complete ten-ref inventory/operations, cursor mapping, operational cutoff, reader/writer/clone dispositions, intended mirror bytes, observation policy, committed delayed/retry inventory path/digest and recomputed horizon, same-host 25-run measurement, durable epoch-2 recovery installation/selection rehearsal, and full gates. It then commits exactly one fixed-path `protocol-kernel-transition-verification/v1` preparation report as the root's sole direct child. GO permits the authorization step; NITS/FAIL stops and preserves the failed attempt/archive. No mailbox, descriptor, verify-request, capacity event, or selected-v1-store write occurs after cutoff, and the coordinator cannot repair production.

### Task 9: Commit separate user authorization and obtain activation-execution GO

**Files:**

- Create: `coordination/activation/compact-kernel-phase4-2026-07-16-<preparation-attempt-id>-authorization.json`
- Create: fixed specialized activation-execution GO evidence under `coordination/activation/reports/`

**Interfaces:**

- Consumes: the exact immutable preparation root and specialized preparation GO, then fresh explicit user instructions separately authorizing one route-bound authorization recorder, one activation executor, and one exact post-CAS metadata finalizer for that preparation.
- Produces: the second and third commits in the fixed transition-control tail: authorization direct-child of preparation GO, then specialized activation-execution GO direct-child of authorization. No selected-v1-store, prepared object, mirror, or authority-ref change occurs.

- [ ] **Step 1: Obtain exact user-principal authorization**

After preparation GO, ask the user to authorize exactly one recorder to commit the authorization artifact as the preparation-GO commit's sole direct child at its one attempt-specific path. Ask separately for the exact preparation root/artifact/preparation-GO digests, activation record OID, selected attempt archive ref/anchor, complete ten-ref inventory/operations, action `activate-compact-epoch-1`, activation executor principal/binding and expiry. Separately ask for post-CAS metadata-finalization authority binding the metadata-finalizer principal/binding, exact intended `governance.toml` bytes/digest, exact `activation.json` path and schema/field/CAS-correlation constraints, two-path commit allowlist, direct-parent derivation rule, action `finalize-compact-epoch-1-metadata`, expiry, and no other commit/ref authority. One principal may hold multiple roles only if each distinct grant is explicit. Authorization for the umbrella design, implementation, merge, preparation, or a differently named recorder/executor/finalizer does not satisfy these gates.

- [ ] **Step 2: Write and commit the authorization artifact**

The named authorization recorder writes canonical `protocol-kernel-activation-authorization/v1` with `status="candidate"` / `gate="pending_activation_execution_go"`, authenticated user-decision correlation/digest, recorder principal/binding and exact commit authority, preparation root/artifact/preparation-GO identities, activation record OID, selected archive ref/anchor, exact ten-ref inventory/operations, current control-tail prefix digest, activation action/executor principal/binding/expiry, metadata-finalizer action/principal/binding/expiry, intended mirror path/bytes/digest, evidence path/schema/field/CAS-correlation constraints, exact two-path allowlist, direct-parent derivation rule, issued/expiry timestamps, and command digests. It contains no mutable actor object, future evidence digest, future execution-GO commit OID, or future finalizer-parent OID. Commit only this artifact as the sole direct child of preparation GO and second tail commit. The coordinator does not write it; recorder authority grants no CAS/finalizer power. The preparation root/artifact, activation blob, preflight, measurement, rehearsal, mirror, selected v1 store, and refs remain unchanged.

- [ ] **Step 3: Obtain binding activation-execution GO**

Using the pre-cutoff trigger, the routed Operator verifies preparation GO, exact authorization bytes/freshness, preparation root/digest, archive/object/ten-ref map, both distinct authorities, intended mirror bytes, finalizer constraints, host actor-source availability, operational drain, selected-v1-store immutability, exact two-commit tail prefix, and every execution gate against current primary history. It commits exactly one fixed-path specialized execution report as the authorization commit's sole direct child and third/final pre-CAS tail commit. GO binds this authorization candidate; NITS/FAIL stops. Any changed code, mirror, schema, preparation, object, ref target, measurement, authorization, executor/finalizer, selected-v1 store, or extra HEAD commit starts a fresh attempt; do not rewrite pending artifacts.

### Task 10: Execute one atomic epoch-1 activation

**Files:**

- Mutate governed refs only through the authenticated `kernel_activation.activate(...)` API
- Modify after successful CAS only: `governance.toml` to the exact prebound epoch `1`, writer `compact` bytes
- Create: `logs/capability-first/phase4-compact-activation-2026-07-16/activation.json`
- Create after finalization: `logs/capability-first/phase4-compact-activation-2026-07-16/finalization-result.json`

**Interfaces:**

- Consumes: implementation GO, specialized preparation GO, specialized activation-execution GO, exact three-commit control tail/current primary HEAD, immutable preparation/authorization/archive objects, user-named activation executor, and separately authorized metadata finalizer authenticated by host sources.
- Produces in fixed order: one atomic ref transaction; while all traffic remains stopped, one exact mirror/evidence metadata commit; then stable postcheck and reader restart. No provider, push, or cleanup.

- [ ] **Step 1: Refresh immediately before the side effect**

The named activation executor reruns exact current HEAD and proves it is the unique direct-child specialized execution-GO commit over authorization over preparation-GO over the preparation root; recomputes the complete control-tail digest; verifies worktree cleanliness, frozen operational high-water/source state, selected-v1-store immutability, process/queue/lease/reader drain, governed clone and credential inventory, preparation/authorization/report digests and expiries, archive/object reachability, host actor-source availability, mirror still exact epoch `0`/writer `v1`, and all ten expected ref values. Any extra HEAD/store write or drift aborts before lock/ref mutation. Resolving an opaque host source does not authenticate the actor yet; authentication occurs only after fence acquisition.

- [ ] **Step 2: Execute the exact preparation and authorization through the host launcher**

From the primary checkout, the authenticated host launcher calls this exact API shape with an in-process source capability:

```python
kernel_activation.activate(
    root=Path("."),
    preparation_path=Path(
        "coordination/activation/"
        f"compact-kernel-phase4-2026-07-16-"
        f"{preparation_attempt_id}-preparation.json"
    ),
    authorization_path=Path(
        "coordination/activation/"
        f"compact-kernel-phase4-2026-07-16-"
        f"{preparation_attempt_id}-authorization.json"
    ),
    execution_report_path=Path(
        "coordination/activation/reports/"
        f"compact-kernel-phase4-2026-07-16-"
        f"{preparation_attempt_id}-execution.json"
    ),
    actor_source=host_authenticated_actor_source,
    evidence_path=Path(
        "logs/capability-first/phase4-compact-activation-2026-07-16/"
        "activation.json"
    ),
)
```

There is no direct mutating CLI path and no `--actor`, `--principal`, `--binding`, `--yes`, force, alternate ref/epoch, environment override, or retry flag. Under one common-dir lock, `activate` creates a fresh challenge, calls and validates the host source, matches repository/action/principal/binding/attestation/freshness/revocation/parent narrowing to the authorization, rereads the exact control tail/high-water/objects/ten-ref inventory, and constructs canonical activation-evidence intent. Before touching a ref it writes that intent by temporary-file plus fsync plus atomic rename and fsyncs the containing directory. The intent contains the exact expected old/new ref map and deterministic metadata recipe but no claimed transaction outcome or containing-commit/result OID. `activate` then performs one `git update-ref --stdin` transaction for activation, event, and six cursor refs while exact-verifying recovery remains absent and the selected attempt archive ref remains at its anchor. It does not release traffic or treat the epoch-0 mirror as fallback.

- [ ] **Step 3: Finalize mirror and evidence before any normal read or writer release**

After successful CAS, all readers and writers remain stopped because normal stable-view law rejects the deliberate epoch-1-ref/epoch-0-mirror mismatch. The separately authorized metadata finalizer invokes `finalize_activation_metadata` through its host launcher. Under the same common-dir fence, that API authenticates the finalizer, resolves the execution-GO commit as the unique authorization direct child and exact current parent frozen by CAS, proves refs equal the prepared targets, and validates the prewritten evidence-intent schema/fields/CAS correlation. It reconstructs the metadata commit from exactly the execution-GO parent tree with only `governance.toml` and `activation.json` replaced at their fixed modes and bytes, using the recipe's fixed author/committer names, emails, timestamp/offset, and message. It computes the resulting commit OID without embedding that OID in either file. If `refs/heads/main` equals the execution-GO parent, it creates that exact object if needed and exact-old-CAS advances only `refs/heads/main` from the parent to the computed commit. If `main` already equals the recomputed commit and its parent/tree/files are exact, it returns the installed result without mutation. Every other `main` value or byte/identity mismatch stops. It changes no protocol-authority ref.

Before any reader restart, the authenticated host launcher writes canonical `finalization-result.json` by temporary-file plus fsync plus atomic rename and directory fsync. It binds the metadata commit SHA, activation/ref-map digest, evidence-intent digest, expected and actual finalizer principal/binding, actual finalizer attestation/challenge digests, `already_installed`, completion timestamp, and host-launcher audit correlation without raw proof material. If the API completed but the launcher crashed before this receipt was durable, service remains stopped; exact finalizer replay may recognize the installed commit, authenticate a fresh authorized finalizer, and produce one receipt for that recognition. A mismatched existing receipt is terminal. Task 11 commits this receipt unchanged, and its compact Operator GO evidence/transition plus observed handoff durably bind the receipt digest and metadata SHA.

Crash semantics are strict: a crash before the ref transaction leaves mirror epoch 0/v1 and the operational drain in place; the evidence intent is not success evidence and the activation attempt is not retried. After an uncertain transaction return, inspect the complete ten-ref inventory under the fence: all-old is a preserved failed attempt, all-new permits only exact metadata finalization, and any mixed or unexpected state is terminal escalation. A crash after CAS and before/during finalization leaves all service unavailable. Resume may only recompute or recognize the exact deterministic metadata commit after proving CAS targets, control tail, parent, identities, recipe, and bytes; it never reruns, retries, rolls back, or falls back from activation CAS. A different commit, file, actor, evidence byte, or ref state is terminal escalation.

- [ ] **Step 4: Postcheck, restart readers, then release compact traffic**

From the returned metadata commit and durable `finalization-result.json`, read the complete ten-ref inventory through normal stable-view protocol, decode activation/event/cursor/archive objects, prove recovery absent, compare exact targets, run archive/GC protections, doctor `--current`, and one compact read-only canary. Restart each inventoried reader against the authoritative common directory, invalidate old activation/cache keys, and require an exact A1/store/A2 compact view before it serves. Independent clones/replicas remain stopped. Only complete agreement and an exact receipt release compact writers/readers.

`activation.json` uses schema `protocol-kernel-activation-evidence/v1` with `status="pending_postactivation_go"` and binds activation ID, authenticated activation-executor principal/binding/attestation digest, authorized expected metadata-finalizer principal/binding/action, preparation root/digest, authorization artifact and execution-GO identities, implementation commit, activation OID/archive anchor, complete expected old/new ten-ref inventory, transition-control digest, mirror digest, exact metadata parent/tree-input/identity/timestamp/message recipe, evidence-intent persistence method, and postcheck requirements. It contains no future metadata-finalizer attestation, claimed CAS outcome, metadata commit result, or self-containing commit OID. The finalizer validates actual CAS success from the live refs; `finalization-result.json`, the later observation compact Operator GO evidence/transition, and the observed handoff bind the actual finalizer attestation digest and resulting metadata commit SHA. The activation ref remains sole authority; the mirror/evidence commit records but never selects it. Uncertain or partial state keeps all traffic stopped and escalates without retry/fallback.

### Task 11: Measure live activation, observe ten units, obtain GO, and hand off

**Files:**

- Read: `logs/capability-first/phase4-compact-activation-2026-07-16/delayed-retry-inventory.json`
- Read and commit unchanged: `logs/capability-first/phase4-compact-activation-2026-07-16/finalization-result.json`
- Create: `logs/capability-first/phase4-compact-activation-2026-07-16/restart-evidence.json`
- Create: `logs/capability-first/phase4-compact-activation-2026-07-16/postactivation-live-five-profile.json`
- Create: `logs/capability-first/phase4-compact-activation-2026-07-16/observation.json`
- Create after GO: `docs/HANDOFF-coordinator-2026-07-16-compact-kernel-phase4-observed.md`
- No legacy deletion

**Interfaces:**

- Consumes: stable epoch-1 compact activation and live boundary-bearing units.
- Produces: pending live measurement/observation evidence, a binding post-activation Operator GO, then a docs-only retirement prerequisite; no pruning or push.

- [ ] **Step 1: Run the exact same-host live five-by-five measurement**

On the same host bound in `precutover-compact-five-profile.json`, run exactly `direct`, `verification-only`, `coordination-only`, `effect-only`, and `combined`, five runs each, against the live stable activation OID. Use the identical Phase-1 baseline, cohort/input digest, and instrumentation digest. Commit no provider/remote/external effect without its own authorization; local effect/advisory lifecycle boundaries are sufficient. Canonical `postactivation-live-five-profile.json` binds all 25 runs, live activation/ref/OID, host/baseline/input/instrumentation digests, aggregates, safety counts, and comparisons against both Phase-1 baseline and the disposable pre-cutover compact artifact. Any mismatch, omitted run, safety regression, or threshold failure blocks observation completion.

- [ ] **Step 2: Observe the required duration, restart, horizon, and unit window**

Start the clock only after metadata finalization and every governed reader restart/stable-view check. Observe at least the user-bound `minimum_observation_duration_seconds`, at least ten consecutive unique boundary-bearing units across at least three triggered profiles, and the user-bound number of controlled live process restarts. After the last required restart, continue for at least the `max_delayed_retry_horizon_seconds` recomputed from committed `delayed-retry-inventory.json`; if it is zero, that artifact must prove no nonzero queue, retry, lease, replica-lag, or delayed-work horizon. Each restarted process must reload the exact activation OID and selected store, invalidate stale caches, and complete A1/store/A2 before service.

Write canonical `restart-evidence.json` with the activation OID, metadata commit SHA, governed-reader inventory digest, one ordered row per restart containing process/reader binding digest, stop/start timestamps, executable/config digest, cache-invalidation result, A1/store/A2 values, first-service time, and post-restart health result, plus the exact observed restart count and last-restart timestamp. It contains no credentials or raw host proofs. Its committed path/digest must agree with `observation.json`; missing, duplicate, stale-activation, or failed rows do not count.

Use disposable canaries for missing profiles; an effect or provider canary needs its own user authorization and one-shot guard. For every unit, prove contiguous event-chain inclusion and stable agreement across every serving reader, then record authority/effect divergence, duplicate dispatch, unresolved effect outcomes, replica/cache lag, and restart recovery. The same-host five-profile measurement and activated-head gate remain mandatory; duration, restart/horizon, ten-unit sample, and 25 measurement runs are independent. Any nonzero count or stale reader fails the window; a correction requires fresh review and a new complete window rather than hiding prior failure.

- [ ] **Step 3: Build and validate pending observation evidence**

Generate the exact schema in Fixed Interfaces. Resolve and recompute both `restart_evidence_path`/`restart_evidence_digest` and `delayed_retry_inventory_path`/`delayed_retry_inventory_digest`, derive the restart count, last-restart timestamp, maximum horizon, and post-restart duration from those exact committed bytes, then run:

```bash
env -u GIT_INDEX_FILE .venv/bin/python scripts/kernel_activation.py \
  validate-observation \
  --path logs/capability-first/phase4-compact-activation-2026-07-16/observation.json \
  --root .
```

Expected: pass only for `status=pending_operator_go`, epoch 1/compact, stable live ref/object/archive agreement, exact user observation-policy and measured-horizon digests, elapsed duration at least the chosen minimum, observed restarts at least the chosen count, post-restart duration at least the maximum horizon, all serving readers consistent, at least ten unique units found on one contiguous event chain, three positive profiles, zero four failure counts, exact same-host/digest-bound pre/post five-by-five measurement artifacts, a green activated-head gate, and epoch-2 rollback rehearsal with durable lossless recovery installation/selection.

- [ ] **Step 4: Run activated-head verification**

```bash
env -u GIT_INDEX_FILE .venv/bin/python -m pytest tests/unit -q
env -u GIT_INDEX_FILE .venv/bin/python -m pytest \
  tests/integration/test_protocol_e2e.py -q
env -u GIT_INDEX_FILE .venv/bin/python scripts/ci_smoke.py
env -u GIT_INDEX_FILE .venv/bin/python scripts/protocol_doctor.py --current --wave 2
env -u GIT_INDEX_FILE git diff --check
```

Expected: all pass; doctor reports exactly one compact writer and no mixed-writer or stale-ref issue.

- [ ] **Step 5: Commit only the pending evidence candidate**

Commit only the already-fsynced unchanged `finalization-result.json`, `restart-evidence.json`, `postactivation-live-five-profile.json`, `observation.json`, and any content-free activated test report required by the established evidence schema. These evidence artifacts remain pending and immutable. Recompute the finalization receipt digest and require its metadata SHA/actual finalizer attestation to match the live finalized state. Do not create the final handoff, check completion boxes, or rewrite activation/preparation evidence in this commit.

- [ ] **Step 6: Obtain binding post-activation observation GO**

Create one lawful compact-mode descriptor/request transition for the exact activated/evidence range beginning at the preparation base and ending at the pending observation commit. The compact verification publisher stores specialized report evidence and appends the verification transition; it creates no legacy Markdown authority event. Operator independently verifies the live ten-ref inventory, archive reachability, activation intent, finalization-result receipt and actual finalizer attestation/metadata SHA, observation-policy decision, duration/restart/horizon and reader-consistency evidence, all 25 pre-cutover and 25 live runs with equal host/baseline/input/instrumentation bindings, thresholds, ten-unit contiguous window, three-profile coverage, zero failure counts, recovery rehearsal installation/selection, complete tests, and absence of additional deletion. Its report evidence explicitly content-addresses `finalization-result.json`. NITS/FAIL or any evidence correction starts a new pending candidate and review; do not patch the handoff around it.

- [ ] **Step 7: Commit the final handoff as docs only**

Only after GO, a compact coordinator route authorizes one docs-only handoff commit. Create `docs/HANDOFF-coordinator-2026-07-16-compact-kernel-phase4-observed.md`. It binds activated head, implementation/preparation/authorization/observation Operator evidence paths/commits/event OIDs, activation object/epoch/archive, activation intent, finalization-result path/digest with actual finalizer attestation digest and metadata SHA, both measurement artifacts, duration/restart/horizon policy and results, reader consistency, observation report, rollback rehearsal, tests, all retained v1 decoders/histories, Phase-3 packet-state retirement evidence, and explicit exclusions. Commit only the handoff and this plan/guide completion markers if maintained; do not change code, tests, config, schemas, refs, or evidence. Append one compact completion transition that content-addresses the committed handoff; its event OID is the terminal evidence. The next trigger is retirement/publication reconciliation, with no delete, cleanup, push, or live rollback authority.

## Completion Gate

Phase 4 is complete only when:

1. every required reader and writer is routed through the compact runtime/fence;
2. independent implementation GO, preparation GO, activation-execution GO, and post-activation observation GO each bind their exact immutable candidate/range;
3. one user-named executor was authenticated by the host source inside the fence and performed one exact epoch-1 ref transaction;
4. activation/event/six cursor refs equal the committed preparation targets, recovery remains absent, and the selected attempt archive ref/objects remain exact and reachable;
5. doctor reports exactly one compact writer;
6. the user-bound minimum duration/restart policy and measured delayed/retry horizon are satisfied, every serving reader is restart-validated and consistent, and at least ten consecutive units across at least three profiles have contiguous event-chain inclusion with zero authority/effect divergence, duplicate dispatch, and unresolved effect outcome;
7. same-host disposable pre-cutover and live post-activation five-profile/five-run artifacts are digest-bound and green, the exact CAS-to-finalizer metadata commit and crash/resume law validate, observation validation and activated-head tests pass, and the lossless epoch-2 rehearsal atomically installs/selects durable recovered v1; and
8. Phase-3 packet-state retirement remains intact, and no additional legacy writer, decoder, branch, worktree, evidence, or ref has been pruned or pushed by this plan.

## Stop Conditions

- Any predecessor handoff/head/GO is absent, stale, dirty, or contradictory.
- A required reader projection or compact payload/cursor seam is missing from Phase 3.
- Any writer bypasses the common-dir fence, accepts actor identity from repository/manifest/argv/environment/payload, authenticates before rather than inside the fence, or can write the nonselected store.
- Any independent clone, host, queue, credential, automation, or recovery process remains capable of authoritative writes outside the primary common-dir fence.
- Epoch-1 activation/event/cursor refs cannot update in one exact-old transactional operation, or the epoch-2 rehearsal cannot atomically install activation/recovery while exact-preserving event/cursors.
- Readers cannot obtain the bounded mode-selected activation/event-cursor or activation/recovery view, a Boolean selector collapses recovered v1 into legacy v1, or any positive-epoch reader can fall back to epoch-0 artifacts.
- Migration cannot reconstruct sender/recipient/kind/body, cursor visibility, or unit semantics without treating v1 Markdown as new authority.
- The acyclic genesis descriptor, known implementation-commit binding, one-way preparation/authorization chain, final v1 high-water, source-state digest, or durable lossless v1 recovery objects cannot be reproduced byte-for-byte.
- Any authority/effect divergence, stale GO, duplicate dispatch, retry, provider switch, unresolved effect, or unclassified helper remains.
- The mirror or ref changes before the named activation window, or a writer remains live.
- The user has not explicitly named exactly one activation executor for the exact preparation commit/object/ref map, or the host-authenticated principal/binding does not match.
- Any required Operator verdict is absent/NITS/FAIL, a pending candidate is prematurely marked complete, ref postcheck is uncertain, or evidence validation fails.
- A live rollback, provider call, merge, push, cleanup, pruning, or deletion is proposed without its separate authority.
