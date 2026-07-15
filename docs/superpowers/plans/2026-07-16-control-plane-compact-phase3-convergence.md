# Control-Plane Compact Phase 3 Convergence Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Converge every still-relevant control-plane requirement into the compact kernel's inactive Phase-3 boundaries, give each dormant helper a real production caller or retire it, and leave live version-1 authority unchanged at epoch `0` / writer `v1` for a separately authorized Phase-4 activation.

**Architecture:** Start only from the independently reviewed Phase-1/2 integration candidate. Treat the July-10 control-plane branch and its FAIL/CLEAR artifacts as a criterion ledger, never as a merge source: freeze all 46 legacy criteria into a machine-checked disposition matrix, implement compact host-principal, scoped-verification, event-log, effect, and advisory boundaries behind a structurally inactive writer gate, preserve a strict read-only v1 projection, and delete the orphan packet-state derivation only after its meaning is absorbed by the compact mapping. Phase 3 creates the one compact event-log seam Phase 4 will activate, but neither selects it nor writes to it in the live repository.

**Tech Stack:** Python 3.14 frozen dataclasses and typed protocols, RFC-8785 canonical JSON, Git first-parent object chains and exact-old-value ref CAS, TOML read-only compatibility checks, JSON fixtures, pytest, Hypothesis, AST call-site inventory, Bash sender compatibility tests, and the existing Lane-V review machinery.

## Global Constraints

- The approved umbrella source is commit `426744766711d4d6057a4698f5bb19d454ad621d`, especially Phase 3B and the compatibility retirement matrix in `docs/superpowers/specs/2026-07-16-pipeline-recovery-sequence-design.md`.
- Do not start from an unmerged Phase-1/2 candidate. Require `docs/HANDOFF-coordinator-2026-07-16-capability-phase1-2-integrated.md`, validate its Operator GO, separately authorized local integration, merged-tree evidence, and exact containing main commit, and branch from a current primary-main SHA that contains it.
- Phase 3 is a convergence point, not a parallel peer of the provider/instruction lanes. Its write and test surfaces overlap Opus, the target bridge, candidate policy, PPL prompt authority, targeted web, and preserved ChatGPT local-reprepare work. Before Task 0 may route, current `main` must also contain and validate: `docs/HANDOFF-director-2026-07-16-opus-b-d-recovery.md`; `docs/HANDOFF-target-aware-evidence-ledger-opus-bridge-2026-07-16.md`; `docs/HANDOFF-director-2026-07-16-candidate-policy-integrated.md` plus its post-candidate bridge-compatibility GO; `docs/HANDOFF-ledger-ppl-publication-race-correction-2026-07-16.md` with no reserved/in-flight/unreconciled target-review attempt; `docs/HANDOFF-director-2026-07-16-targeted-web-integrated.md`; and `docs/HANDOFF-coordinator-2026-07-16-chatgpt-local-reprepare-disposition.md`. Bind their exact commits/blobs/digests and terminal reports into the Phase-3 route.
- The ChatGPT disposition must precede convergence. If the user-principal withdraws the preserved range, its owner records exact withdrawal while retaining the preservation branch. If the user-principal elects integration, a dedicated approved plan, independent Operator GO, separately named local integrator, merged-tree verification, and the fixed disposition handoff must complete first. A preservation-only or undecided state blocks Phase 3; post-activation integration would invalidate the activated-head observation.
- Use an isolated branch `codex/control-plane-compact-phase3-convergence-2026-07-16` and worktree `.worktrees/control-plane-compact-phase3-convergence-2026-07-16`.
- The old control-plane branch is evidence only: `codex/control-plane-authority-foundation-2026-07-10`, base `78b48ed493899dd126de2d1764cbdbf022111dfd`, committed head and still-unchanged ref `6983673db60bff0d21548a90ab1db2fcbbfa377a`. Do not merge, rebase, cherry-pick, copy its files wholesale, or resolve its design by choosing its implementation.
- Phase 0A relocates the nine parked working blobs into preservation branch `codex/recovery-control-plane-wip-2026-07-16` and commits `docs/HANDOFF-owner-2026-07-16-control-plane-wip.md`. Phase 3 must consume that exact content-addressed handoff, validate the preservation head and all nine blob identities, and prove the original ref remains `6983673...`. The preservation branch is criterion evidence only: never merge, cherry-pick, or copy it. Every preserved changed hunk/symbol receives a machine-checked disposition before implementation.
- Live Markdown/signed-bus version-1 behavior remains byte-for-byte authoritative throughout Phase 3. `governance.toml` remains a declarative epoch `0`, writer `v1` mirror. No environment variable, CLI flag, payload field, mutable config value, or test hook may activate compact writes.
- `refs/protocol/kernel-activation` is the future monotonic activation source. Phase 3 may parse and reject its absence but must not create or update it. `refs/protocol/kernel-events` is the future single compact reducer event log and `refs/protocol/kernel-cursors/<seat>` is the future per-reader cursor namespace; Phase 3 may exercise either only inside disposable test repositories.
- A host-installed `AuthenticatedActorSource` is the only authority entry point. It returns a challenge-bound `HostAuthenticatedActor` containing the reducer `ActorContext`; seat text, role labels, repository files, environment variables, CLI arguments, event payloads, inherited subagent identity, or provider output cannot construct the source, mint a context, or broaden authority. Phase 4 must call it only after acquiring the shared writer fence.
- Provider output remains advisory. Verification records, effect reservations, provider delivery records, and compact transition events remain separate specialized records connected by immutable references; do not introduce an all-in-one operation store.
- Keep `scripts/route_manifest.py` and `scripts/route_lineage.py` as v1 compatibility/read guards until Phase 4. Keep `scripts/route_capability.py` until the compact effect path is activated. Do not activate route generations or make `capability/v1` a live authority token.
- `scripts/packet_state.py` and `tests/unit/test_packet_state.py` are retired and deleted in Phase 3 after their complete meaning is moved into compact fixtures and reducer/property tests. Phase 4 must assert that boundary and must not defer, re-create, or import `packet_state`.
- Every retained public helper must have a non-test production caller or a documented CLI. Every new inactive branch must be structurally unreachable under epoch `0` and covered by an AST/call-site test.
- Adversarial surfaces trigger R-INDEPENDENCE: freeze abuse cases in Task 1 before implementation; use a fresh implementer per task, then specification and code-quality review. The final actual diff receives independent Lane-V review against the frozen cases.
- Use `env -u GIT_INDEX_FILE` for every Git and pytest command. Stage and commit with exact pathspecs. Do not touch mailbox cursors, locks, routes, refs, providers, keys, accounts, services, remotes, or external effects.
- Local integration to `main`, push, activation, old-branch disposition, source-branch deletion, and worktree cleanup are six separate decisions. Phase 3 stops for fresh user authority before local integration and authorizes none of the latter five.

---

## Frozen Legacy Evidence Manifest

The convergence fixture must record these exact source paths and SHA-256 values. A byte change to any source stops implementation until the coordinator approves a revised matrix.

| Source ID | Criterion count | Path | SHA-256 |
|---|---:|---|---|
| `DESIGN` | 10 | `docs/superpowers/specs/2026-07-10-signed-bus-authority-identity-design.md` | `32ad4a0f1b60ea01711f64e4775b2452526f49d6e12bbe232de9a3d7750e8e70` |
| `FAIL1` | 9 | `coordination/mailbox/sent/2026-07-10T07-23-26Z-operator-to-all-verification-report.md` | `36ff52eb45381dbcf82fa84c5b0155aabb5223524a317d481fbb76fd98c08baf` |
| `SPEC` | 6 | `coordination/mailbox/sent/2026-07-10T11-45-25Z-director-to-coordinator-coordination.md` | `7ca1246c7311ea7c04a54811aa340e143548443fbd9e35281b2264549ebbe0eb` |
| `RACE` | 2 | `coordination/mailbox/sent/2026-07-10T14-03-14Z-director-to-coordinator-coordination.md` | `a5bec2b7255a7b81f3ad48ecaaf819f79173684eeb80058625a3ff9bde195487` |
| `SCAN` | 1 | `coordination/mailbox/sent/2026-07-10T15-41-08Z-director-to-coordinator-coordination.md` | `a8a1845ecc1b90b7c9d17d0b07c77a3a98943050742ca2c2a0a052cee748243d` |
| `FAIL2` | 7 | `coordination/mailbox/sent/2026-07-10T18-33-55Z-operator-to-all-verification-report.md` | `f44e2a5f3bdcc078e7893875255125b07b7470e244afd256774a5e492da5ae5f` |
| `TASK3H` | 2 | `coordination/mailbox/sent/2026-07-10T18-19-09Z-director2-to-coordinator-coordination.md` | `7fc6fad03fcd55863f0aa08a412100abc56c799bcdad70c93b333c885dec4184` |
| `TASK3I` | 2 | `coordination/mailbox/sent/2026-07-10T23-36-33Z-director2-to-coordinator-coordination.md` | `026fdbd2250c32ecdf7c60e6328f66428df1111c28b744e06b3cc3796c1edeec` |
| `ACT-BLOCK` | 3 | `coordination/mailbox/sent/2026-07-10T01-23-27Z-operator2-to-coordinator-coordination.md` | `12737b5047941ed65fd9044754c47b80fdb3677561b4b66a116cc087337886e9` |
| `ACT-CLEAR` | 4 | `coordination/mailbox/sent/2026-07-10T04-24-26Z-operator2-to-coordinator-coordination.md` | `186b45909c4e8970fb1dcbf618320f81e76672f2b2c4aeb65cc35498270b80d7` |

## Frozen 46-Criterion Disposition Ledger

Allowed dispositions are exactly `carried-forward`, `already-satisfied`, and `superseded-with-equivalent-coverage`. `already-satisfied` requires an executable test on the Phase-3 base; prose or a green inventory string is insufficient. A `superseded-with-equivalent-coverage` row must name the compact test or the exact Phase-4 gate that prevents loss of the original safety property.

| ID | Legacy criterion | Required disposition | Exact equivalent coverage |
|---|---|---|---|
| `DESIGN-01` | User activation decision for the signed-fact channel | `already-satisfied` | `tests/unit/test_control_plane_convergence.py::test_current_signed_bus_activation_is_preserved`; no July-10 code import |
| `DESIGN-02` | Signed control/promotion facts use fixed refs after their cutover | `carried-forward` | fixed `KERNEL_EVENTS_REF` / `KERNEL_CURSOR_PREFIX` and `tests/unit/test_compact_event_store.py::test_compact_ref_names_have_no_override` |
| `DESIGN-03` | Human routes, briefs, verify requests/reports, and handoffs remain Markdown authority in v1 | `already-satisfied` | `tests/unit/test_control_plane_convergence.py::test_current_markdown_route_is_live_authority` |
| `DESIGN-04` | No event class is dual-written | `carried-forward` | `tests/unit/test_compact_event_store.py::test_sender_has_exactly_one_writer_for_each_epoch` |
| `DESIGN-05` | Coordinators are all-scope and unpinned for human mail | `superseded-with-equivalent-coverage` | compact coordinator aliases remain all-scope in `test_coordinator_cursors_are_all_scope`; Phase-4 gate `P4-CURSOR-INIT` atomically replaces the unpinned sentinel with six explicit cursors |
| `DESIGN-06` | Signed-fact cursors are independent of human-mailbox cursors | `already-satisfied` | `tests/unit/test_control_plane_convergence.py::test_current_human_and_signed_cursors_are_independent` |
| `DESIGN-07` | Event/cursor namespaces are fixed constants | `carried-forward` | `test_compact_ref_names_have_no_override` |
| `DESIGN-08` | Private signing material stays outside Git and candidate runtimes | `already-satisfied` | `tests/unit/test_control_plane_convergence.py::test_current_private_keys_are_excluded` |
| `DESIGN-09` | Only the separately gated final activation task changes authority | `superseded-with-equivalent-coverage` | Phase-4 gate `P4-ACTIVATION-ONLY`: exact-old CAS on `refs/protocol/kernel-activation` after GO and explicit executor authorization |
| `DESIGN-10` | Repeat activation is exact verified resume, never a rewrite | `superseded-with-equivalent-coverage` | Phase-4 gate `P4-MONOTONIC-EPOCH`: exact-current activation/event refs and newer-epoch rollback only |
| `FAIL1-01` | Numeric pre-marker history stays auditable without accepting new numeric envelopes | `superseded-with-equivalent-coverage` | `tests/unit/test_capability_v1_adapter.py::test_reader_projection_rejects_ambiguous_legacy_normalization`; Phase 4 imports only normalized source digests |
| `FAIL1-02` | Durable wording assigns activation only to the final cutover | `superseded-with-equivalent-coverage` | `P4-ACTIVATION-ONLY` and Phase-3 inactive-writer static tests |
| `FAIL1-03` | Effectiveness/readers use the same authority source as consumption | `carried-forward` | `tests/unit/test_capability_v1_adapter.py::test_reader_projection_has_one_normalized_source_per_observation` |
| `FAIL1-04` | Hook/status mirrors cannot turn unavailable/uninitialized mail into zero | `carried-forward` | `tests/unit/test_compact_runtime.py::test_reader_projection_preserves_unavailable_state` |
| `FAIL1-05` | Cursor/event publication is monotonic and atomic | `carried-forward` | `tests/unit/test_compact_event_store.py::test_append_uses_locked_exact_old_event_ref_cas` and `::test_advance_cursor_uses_same_fence_and_exact_old_cas` |
| `FAIL1-06` | Mutation accepts only canonically validated events | `carried-forward` | `tests/unit/test_compact_event_store.py::test_decode_rejects_unknown_or_noncanonical_record_before_ref_write` |
| `FAIL1-07` | Reader and consumer cannot split across configurable ref namespaces | `superseded-with-equivalent-coverage` | fixed `KERNEL_EVENTS_REF`; `test_event_ref_has_no_configuration_override` |
| `FAIL1-08` | Mirrors fully validate state and fail visibly when the store is missing | `carried-forward` | `test_reader_projection_rejects_missing_or_invalid_source`, `test_event_chain_missing_tip_is_unavailable_after_activation`, and `test_cursor_missing_after_activation_is_unavailable` |
| `FAIL1-09` | Coordinator aliases are observationally symmetric | `carried-forward` | `tests/unit/test_compact_event_store.py::test_coordinator_aliases_are_all_scope_and_symmetric` |
| `SPEC-01` | Legacy provenance binds exact bytes to the pinned repository version | `carried-forward` | `test_reader_projection_binds_source_digest_and_rejects_changed_duplicate_source_id` |
| `SPEC-02` | Effectiveness/classification consumes canonical envelopes only | `carried-forward` | `test_reader_projection_uses_only_frozen_legacy_observation` |
| `SPEC-03` | Unavailable and all-scope states are typed, never integer zero | `carried-forward` | `test_reader_projection_preserves_unavailable_state` |
| `SPEC-04` | Human-reader and signed-fact identity rosters do not alias | `superseded-with-equivalent-coverage` | compact cursors use the frozen `COMPACT_CURSOR_SEATS` roster and never infer identity from human v1 cursor syntax |
| `SPEC-05` | Coordinator2 handoff naming remains discoverable | `superseded-with-equivalent-coverage` | compact handoffs are typed mailbox events rendered by `unread_mailbox_messages()`; no filename token exists to become undiscoverable |
| `SPEC-06` | Coordinator2 route-to-GO observation is symmetric | `carried-forward` | `tests/unit/test_compact_event_store.py::test_coordinator_aliases_are_all_scope_and_symmetric` plus reader-projection route metadata |
| `RACE-01` | One immutable body snapshot drives parse, classification, and metrics | `carried-forward` | frozen `LegacySemanticObservation`; `test_reader_projection_does_not_reopen_source_path` |
| `RACE-02` | Leaf/parent substitution cannot change accepted bytes | `superseded-with-equivalent-coverage` | host-normalized adapter accepts no path; Phase-4 gate `P4-V1-SNAPSHOT` requires the v1 decoder to bind descriptor bytes before producing an observation |
| `SCAN-01` | A global scan failure is unavailable, not a false-clean zero | `carried-forward` | `test_reader_projection_global_source_failure_is_unavailable` |
| `FAIL2-01` | Missing required signed cursor/event refs are unavailable, not zero | `carried-forward` | `tests/unit/test_compact_event_store.py::test_cursor_or_event_ref_missing_after_activation_is_unavailable` |
| `FAIL2-02` | Mutation remains bound to the descriptor/ref that was locked | `carried-forward` | Git-common-dir lock plus ref CAS in `test_append_ref_rebound_fails_without_write` |
| `FAIL2-03` | Ambiguous history cannot be hidden by simplified traversal | `carried-forward` | first-parent compact event chain with unique parent and `test_read_chain_rejects_graft_or_multiple_parent_commit` |
| `FAIL2-04` | Git/object-read failure never becomes vacuous positive evidence | `carried-forward` | `test_read_chain_object_failure_is_unavailable` |
| `FAIL2-05` | Legacy status does not bypass universal envelope validation | `carried-forward` | `test_reader_projection_rejects_unknown_fields_for_every_legacy_value` |
| `FAIL2-06` | Unknown read policies fail closed | `superseded-with-equivalent-coverage` | no compact read-scope configuration; `test_reader_projection_has_no_policy_override` |
| `FAIL2-07` | One pinned repository/activation view binds all provenance reads | `carried-forward` | activation OID in every compact event record plus `test_append_rejects_activation_change_inside_fence` |
| `TASK3H-01` | Privileged proof negative has causal GREEN/RED/cleanup/GREEN choreography | `superseded-with-equivalent-coverage` | old service proof is retired; `test_actor_spoof_flip_is_causal_and_context_immutable` plus independent adversarial review |
| `TASK3H-02` | Runtime principal proof is real on supported hosts, never mocked/skipped | `superseded-with-equivalent-coverage` | host installs the only `AuthenticatedActorSource`; challenge-bound `HostAuthenticatedActor` is validated and no in-repo credential/context inference exists |
| `TASK3I-01` | Privileged cleanup remains unconditional after every failure mode | `superseded-with-equivalent-coverage` | no privileged helper/service is deployed; effect outcomes use explicit `OUTCOME_UNKNOWN` and reconciliation |
| `TASK3I-02` | Cross-platform peer identity has fail-closed kernel proof | `superseded-with-equivalent-coverage` | identity is a host-source contract, not a repository service; replayed challenge, cross-repository, expired, revoked, child-broadening, and unattested proofs/contexts are rejected |
| `ACT-BLOCK-01` | Trust-root provisioning and activation are separate actions | `superseded-with-equivalent-coverage` | Phase 3 performs neither; Phase-4 `P4-ACTIVATION-ONLY` cannot generate keys or alter provider trust roots |
| `ACT-BLOCK-02` | Activation has exact manifest/token input and verified resume | `superseded-with-equivalent-coverage` | activation record schema and exact-old ref CAS under `P4-MONOTONIC-EPOCH` |
| `ACT-BLOCK-03` | Key bootstrap has canonical roster, off-repo custody, and complete-state refusal | `superseded-with-equivalent-coverage` | compact activation has no key bootstrap or signer roster; `P4-ACTIVATION-ONLY` rejects any activation path that writes keys |
| `ACT-CLEAR-01` | Activation resume accepts only an exact complete expected ref map | `superseded-with-equivalent-coverage` | exact predecessor/activation/event OIDs in Phase-4 activation record and CAS tests |
| `ACT-CLEAR-02` | Importer/marker boundary is deterministic and fail closed | `superseded-with-equivalent-coverage` | Phase-4 `P4-V1-SNAPSHOT` imports frozen `LegacySemanticObservation` records and records their aggregate digest |
| `ACT-CLEAR-03` | Production key state is complete or refuses before writes | `superseded-with-equivalent-coverage` | no compact key writer; `P4-ACTIVATION-ONLY` statically excludes trust-root/key paths from the activation write set |
| `ACT-CLEAR-04` | Provision, measure, and activate have independent authority gates | `superseded-with-equivalent-coverage` | Phase-3 evidence commit, independent GO, and explicit Phase-4 activation executor remain separate |

The table is normative. The JSON fixture repeats the rows verbatim in machine-readable form; a reviewer may tighten a disposition only through a separately approved plan correction, never by dropping a row.

## Exact Phase-3 Interfaces

### Host principal, scoped verification, and reader projection

Create `scripts/compact_runtime.py`:

```python
class CompactRuntimeError(ValueError):
    code: str


@dataclass(frozen=True)
class HostAuthenticatedActor:
    actor: capability_reducer.ActorContext
    repository: str
    required_action: str
    challenge_digest: str
    attestation_digest: str
    issued_at: str
    expires_at: str


class AuthenticatedActorSource(Protocol):
    def authenticate_actor(
        self,
        *,
        repository: str,
        required_action: str,
        challenge: bytes,
    ) -> HostAuthenticatedActor: ...


@dataclass(frozen=True)
class VerificationKey:
    work_id: str
    unit_id: str | None
    unit_version: int
    content_digest: str
    dependency_digest: str
    acceptance_digest: str
    evidence_digest: str
    verifier_binding_digest: str


@dataclass(frozen=True)
class ReaderUnitProjection:
    work_id: str
    route_id: str | None
    work_revision: int
    unit_id: str | None
    unit_version: int
    precondition_digest: str
    compact_state: str
    terminal_scope: str
    next_action: str
    effect_eligibility: str
    advisory_only: bool
    verification_ref: str | None
    source_ids: tuple[str, ...]


@dataclass(frozen=True)
class CompactReaderProjection:
    mode: Literal["shadow"]
    epoch: int
    writer: Literal["v1"]
    state_digest: str
    units: tuple[ReaderUnitProjection, ...]


def require_actor_context(
    actor: object,
    *,
    repository: str,
    required_action: str,
) -> capability_reducer.ActorContext: ...


def authenticate_host_actor(
    source: AuthenticatedActorSource,
    *,
    repository: str,
    required_action: str,
    challenge: bytes,
    now: str,
) -> capability_reducer.ActorContext: ...


def make_verification_key(
    unit: capability_reducer.UnitSnapshot,
    *,
    verifier_binding_digest: str,
) -> VerificationKey: ...


def verification_is_current(
    recorded: object,
    *,
    unit: capability_reducer.UnitSnapshot,
    verifier_binding_digest: str,
) -> bool: ...


def inactive_activation(root: Path) -> capability_reducer.ActivationState: ...


def compact_writer_active(root: Path) -> bool: ...


def project_reader_state(
    records: Iterable[object],
    *,
    resolve_actor: capability_reducer.ActorBindingResolver,
    resolve_scope: capability_reducer.ScopeResolver,
) -> CompactReaderProjection: ...
```

`AuthenticatedActorSource` is an in-process capability installed by the authenticated host launcher. There is no default implementation, registry lookup, import-by-name, file loader, environment loader, CLI selector, payload decoder, or repository fallback. `authenticate_host_actor()` accepts only the exact protocol result, verifies canonical timestamps and digests, exact repository/action/challenge binding, attestation freshness, and the existing reducer actor laws, then returns the embedded immutable `ActorContext`. Phase-3 production branches remain inactive; tests may inject a fake source only into this function's direct unit boundary. Phase 4 obtains a fresh random challenge and calls this function inside `writer_fence`, after the common-directory lock is held and before any authority-bearing state is reread or mutated.

`compact_writer_active()` is structurally `False` in Phase 3. It accepts no optional mode, callback, environment, CLI, config, or test override. `inactive_activation()` accepts only the declarative epoch-0/writer-v1 mirror and returns the reducer's shadow activation. Phase 4 replaces the gate with a trusted-primary-checkout reader of `refs/protocol/kernel-activation`; no Phase-3 caller may anticipate that result from `governance.toml`.

Extend `scripts/capability_v1_adapter.py`:

```python
@dataclass(frozen=True)
class LegacySemanticObservation:
    source_id: str
    work_id: str
    route_id: str | None
    work_revision: int
    unit_id: str | None
    domain: str
    value: str
    compact_state: str
    terminal_scope: str
    next_action: str
    effect_eligibility: str
    advisory_only: bool
    verification_ref: str | None
    route_event_transition_id: str | None


def project_v1_history(
    records: Iterable[object],
    *,
    resolve_actor: capability_reducer.ActorBindingResolver,
    resolve_scope: capability_reducer.ScopeResolver,
) -> tuple[LegacySemanticObservation, ...]: ...
```

Specialized verification/effect/provider lifecycle observations have `route_event_transition_id=None`; they are referenced but never copied into the route event stream.

### Single compact event log, typed mailbox payload, inactive publisher, and cursor seam

Create `scripts/compact_event_store.py`:

```python
KERNEL_EVENTS_REF = "refs/protocol/kernel-events"
KERNEL_CURSOR_PREFIX = "refs/protocol/kernel-cursors/"
COMPACT_CURSOR_SEATS = (
    "director", "director2", "operator", "operator2",
    "coordinator", "coordinator2",
)
COMPACT_RECIPIENTS = (*COMPACT_CURSOR_SEATS, "all")
COMPACT_KINDS = (
    "acknowledgement", "convergence", "coordination", "decision",
    "dispatch-claim", "discussion", "doc-sync-notice", "findings",
    "fold-notice", "fyi", "measurement-report", "memory-candidate",
    "proposal", "proposal-reply", "query", "reply", "scout-report",
    "scout-request", "status", "verification-report", "verify-addendum",
    "verify-readiness", "verify-readiness-converged", "verify-request", "wrap",
)


class CompactEventStoreError(ValueError):
    code: str


@dataclass(frozen=True)
class CompactEventRecord:
    schema: Literal["compact-event/v1"]
    sequence: int
    activation_epoch: int
    activation_ref_oid: str
    previous_event_oid: str | None
    transition_digest: str
    transition: capability_reducer.TransitionEnvelope
    mailbox_blob_oid: str | None
    mailbox_digest: str | None


@dataclass(frozen=True)
class CompactMailboxPayload:
    schema: Literal["compact-mailbox-payload/v1"]
    sender_principal: str
    sender_binding_digest: str
    recipient: str
    kind: str
    subject: str
    body: str


@dataclass(frozen=True)
class CompactMailboxMessage:
    event_oid: str
    sequence: int
    transition_id: str
    sender_principal: str
    sender_binding_digest: str
    recipient: str
    kind: str
    subject: str
    body: str


@dataclass(frozen=True)
class CompactCursorRecord:
    schema: Literal["compact-cursor/v1"]
    seat: str
    activation_epoch: int
    through_event_oid: str | None
    through_sequence: int


@dataclass(frozen=True)
class CompactCursorResult:
    cursor_ref: str
    cursor_oid: str
    previous_cursor_oid: str | None
    through_event_oid: str | None
    through_sequence: int
    idempotent: bool


@dataclass(frozen=True)
class CompactAppendResult:
    event_oid: str
    previous_event_oid: str | None
    transition_id: str
    idempotent: bool


def encode_event_record(record: CompactEventRecord) -> bytes: ...


def decode_event_record(raw: bytes) -> CompactEventRecord: ...


def encode_mailbox_payload(payload: CompactMailboxPayload) -> bytes: ...


def decode_mailbox_payload(raw: bytes) -> CompactMailboxPayload: ...


def read_event_chain(
    repo: Path,
    *,
    tip_oid: str | None,
) -> tuple[CompactEventRecord, ...]: ...


def read_mailbox_message(
    repo: Path,
    *,
    event_oid: str,
    record: CompactEventRecord,
) -> CompactMailboxMessage | None: ...


def cursor_ref(seat: str) -> str: ...


def read_cursor(
    repo: Path,
    *,
    seat: str,
    activation: capability_reducer.ActivationState,
) -> tuple[str, CompactCursorRecord] | None: ...


def unread_mailbox_messages(
    repo: Path,
    *,
    seat: str,
    activation: capability_reducer.ActivationState,
) -> tuple[CompactMailboxMessage, ...]: ...


def append_transition(
    repo: Path,
    *,
    event: capability_reducer.TransitionEnvelope,
    actor: capability_reducer.ActorContext,
    expected_event_oid: str | None,
    activation: capability_reducer.ActivationState,
    mailbox: CompactMailboxPayload | None = None,
) -> CompactAppendResult: ...


def advance_cursor(
    repo: Path,
    *,
    seat: str,
    expected_cursor_oid: str | None,
    through_event_oid: str | None,
    actor: capability_reducer.ActorContext,
    activation: capability_reducer.ActivationState,
) -> CompactCursorResult: ...
```

Persist exactly one RFC-8785 canonical `record.json` blob, mode `100644`, in each first-parent Git commit on `refs/protocol/kernel-events`. The commit parent equals `previous_event_oid`; `sequence` is exactly the parent sequence plus one; the record binds the exact activation-ref OID and epoch, canonical transition digest, and complete transition envelope. A coordination event adds exactly one RFC-8785 `mailbox.json` blob, mode `100644`, in the same commit tree. Those are the only permitted tree entries. `record.json.mailbox_blob_oid` names that blob and `record.json.mailbox_digest` must equal both the `sha256:<64-lowercase-hex>` digest of its canonical bytes and `transition.content_digest`. A non-mailbox transition has both mailbox fields `null` and no `mailbox.json` tree entry.

`mailbox.json` has exactly the seven `CompactMailboxPayload` fields above. `sender_principal` is copied from the already validated host `ActorContext.principal`; `sender_binding_digest` must equal both the actor and transition binding digest. `recipient` is exactly one member of frozen `COMPACT_RECIPIENTS` and `kind` is exactly one member of frozen `COMPACT_KINDS`. `schemas/compact-mailbox-v1.schema.json` repeats those enums and exact field/size constraints; a sync test proves module/schema identity and proves the initial compact kind list equals the v1 registry at the migration boundary. Runtime compact reads never consult mutable `coordination/mailbox/kinds.txt`; any later vocabulary change requires a new schema version and activation review. UTF-8 `subject` is one line, contains no NUL/CR/LF, and encodes to 1 through 512 bytes. UTF-8 `body` contains no NUL and encodes to 0 through 1,048,576 bytes. They are rendering content, not a second authority parser: authority-bearing work, revision, unit, scope, verification, effect, and activation values live only in the typed transition and its immutable references. No Markdown is generated or reparsed after compact activation. `read_mailbox_message()` verifies the object OID, canonical bytes, digest, actor binding, closed recipient/kind vocabularies, sizes, and record/transition relationship before returning renderable sender, recipient, kind, subject, and body.

No timestamps, raw provider content, mutable paths, or unbound identity metadata enter `record.json`. The decoder rejects unknown fields, merge commits, sequence/parent mismatch, missing or extra tree entries, duplicate transition IDs with changed payloads, noncanonical bytes, and object failures. Exact duplicate IDs/payloads return the prior result idempotently.

`append_transition()` loads code from the trusted primary checkout, takes the Git-common-dir writer lock, rereads activation and event refs inside the fence, requires exact expected event OID, validates host actor binding and optional mailbox payload, creates the objects, and changes the event ref with exact-old-value CAS. In Phase 3 it rejects with `compact_writer_inactive` before any object/ref mutation. A private write core may be exercised only in disposable repositories to prove the future fence; it is not a public bypass and has no live caller.

Each identity in frozen `COMPACT_CURSOR_SEATS` has exactly one fixed ref `refs/protocol/kernel-cursors/<seat>`; `all` is never a cursor identity. A cursor ref points to one RFC-8785 canonical Git blob encoding exactly `CompactCursorRecord`. `read_cursor()` validates the closed seat roster, exact ref name, canonical blob, activation epoch, sequence/OID agreement with the pinned current event chain, and non-regression. Before activation, all compact cursor refs must be absent. After activation, a missing/invalid cursor or event ref is `compact_store_unavailable`, never sequence zero.

Phase-4 gate `P4-CURSOR-INIT` must bind the exact six-seat roster and six initial cursor blob OIDs in the activation record, then create the activation ref, event ref, and all cursor refs in one `git update-ref --stdin` transaction under the common-dir fence. Every initial cursor points to the frozen v1-import boundary: `through_event_oid=None` / `through_sequence=0` when the compact log is empty, or the exact imported compact boundary event. Partial, extra, missing, wrong-roster, or mixed-epoch cursor sets fail activation and exact resume.

`advance_cursor()` uses the same trusted-primary code and Git-common-dir fence as event append. Inside that one fence it rereads activation, event, and selected cursor refs; requires exact `expected_cursor_oid`; proves `through_event_oid` is `None`/sequence zero or an ancestor on the pinned current first-parent event chain; rejects regression, skipped unknown history, wrong seat/actor, stale epoch, and ref rebound; writes one canonical cursor blob; then updates only the exact cursor ref with exact-old-value CAS. An exact same target is idempotent. `unread_mailbox_messages()` begins strictly after the cursor sequence and validates every record/payload. Pair seats receive only `recipient in {seat, "all"}`; `coordinator` and `coordinator2` are symmetric all-scope readers and receive every valid mailbox message. The function returns ordered `CompactMailboxMessage` objects. Phase 3 exercises this only in disposable repositories and never creates a live cursor ref.

The event sender gets one explicit selection seam: under epoch 0 it follows its existing v1 path without changed output; if the compact writer ever becomes active, the legacy sender must refuse rather than fall back to v1 unless invoked through the host-bound `append_transition(..., mailbox=CompactMailboxPayload(...))` path. Phase 4 therefore changes only the activation reader and host-bound sender entrypoint, not the persisted event, mailbox, or cursor schemas. `read_event_chain()` plus `project_reader_state()` reconstructs authority metadata after v1 writes stop; `unread_mailbox_messages()` supplies renderable sender/recipient/kind/subject/body and the exact per-seat unread boundary.

### Effect reservation and recovery

Create `scripts/compact_effects.py`:

```python
class CompactEffectError(ValueError):
    code: str


@dataclass(frozen=True)
class EffectReservation:
    schema: Literal["compact-effect/v1"]
    reservation_id: str
    work_id: str
    unit_id: str | None
    activation_epoch: int
    grant_digest: str
    executor_binding_digest: str
    effect_class: str
    target_digest: str
    request_digest: str
    precheck_digest: str
    postcheck_digest: str
    expires_at: str
    state: str


def reserve_effect(
    *,
    reservation_id: str,
    work_id: str,
    unit_id: str | None,
    activation_epoch: int,
    grant_digest: str,
    executor_binding_digest: str,
    effect_class: str,
    target_digest: str,
    request_digest: str,
    precheck_digest: str,
    postcheck_digest: str,
    expires_at: str,
) -> EffectReservation: ...


def transition_effect(
    reservation: object,
    *,
    requested_state: str,
    actor: capability_reducer.ActorContext,
    activation: capability_reducer.ActivationState,
) -> EffectReservation: ...
```

The closed lifecycle is `RESERVED -> CANCELLED | ATTEMPTING`, `ATTEMPTING -> SUCCEEDED | FAILED | OUTCOME_UNKNOWN`, and `OUTCOME_UNKNOWN -> RECONCILED_SUCCEEDED | RECONCILED_FAILED`. `ATTEMPTING` must be durably recorded before the attempt. `OUTCOME_UNKNOWN` cannot retry, switch executor/provider, or become success/failure without an explicit reconciliation record. Phase 3 computes and tests records but executes no effect.

### Atomic advisory dispatcher

Create `scripts/advisory_dispatch.py`:

```python
class AdvisoryDispatchError(ValueError):
    code: str


@dataclass(frozen=True)
class DispatchEligibility:
    purpose: str
    eligible_transports: tuple[str, ...]
    selected_transport: str | None
    state_digest: str


@dataclass(frozen=True)
class AdvisoryIntentClaim:
    schema: Literal["advisory-intent/v1"]
    purpose: str
    question_digest: str
    repository: str
    state_digest: str
    scope_digest: str
    request_hash: str
    selected_transport: str
    executor_binding_digest: str
    grant_digest: str
    state: Literal["reserved"]


def eligible_transports(
    runtime: Mapping[str, object],
    *,
    purpose: str,
) -> tuple[str, ...]: ...


def reserve_intent(
    state_path: Path,
    *,
    purpose: str,
    question_digest: str,
    repository: str,
    state_digest: str,
    scope_digest: str,
    request_hash: str,
    selected_transport: str,
    executor_binding_digest: str,
    grant_digest: str,
) -> AdvisoryIntentClaim: ...
```

Exactly two production modules call this API: `scripts/chatgpt_pro_consult.py` and `scripts/opus_review_bridge.py`. Eligibility order is deterministic; selection is immutable once reserved; claim creation is atomic/no-follow and one-time; crash/resume may inspect or continue only the same provider; unavailable/ambiguous delivery blocks without retry, provider switch, manual/API fallback, or raw prompt/response in the claim.

---

### Task 0: Bind all converged predecessors and create the isolated worktree

**Files:**
- Read: every fixed upstream handoff named in Global Constraints
- Read: `docs/HANDOFF-coordinator-2026-07-16-recovery-owner-wip-disposition.md`
- Read: `docs/HANDOFF-owner-2026-07-16-control-plane-wip.md`
- Create through a later coordinator action: one capacity-valid Phase-3 implementation route
- Create: worktree `.worktrees/control-plane-compact-phase3-convergence-2026-07-16`

**Interfaces:**
- Consumes content-addressed predecessor handoffs/reports, terminal joins, current primary `main`, the still-frozen July-10 ref, and the preservation-only nine-blob branch.
- Produces one route commit and one clean isolated worktree at that exact commit. It creates no provider attempt, receipt mutation, compact ref, mailbox consume, merge, push, activation, or external effect.

- [ ] **Step 1: Resolve every fixed predecessor from committed objects**

From primary `main`, resolve each required handoff's unique introduction or fixed finalization commit, Git blob OID, and SHA-256 digest. Follow only the report/join/integrated-head references inside those exact committed bytes. Require all of these conditions at once:

1. Phase-1/2, Opus B-D, target bridge, candidate policy, and targeted web each have canonical Operator GO plus their required separately authorized local integration and merged-tree evidence.
2. The candidate handoff binds the distinct post-candidate target-bridge compatibility GO.
3. The PPL handoff binds the cumulative target GO; its target-review family has no `reserved`, `in_flight`, or unreconciled receipt, and no target/provider operation is active.
4. The ChatGPT disposition is terminal `withdrawn-preserved` or `integrated-reviewed`; `preserved-pending` is not accepted.
5. Every integrated code SHA and containing handoff commit is an ancestor of current primary `main`, and no relevant path changed after its last required compatibility/merged-tree gate without a newer bound verdict.

Read all current mailbox bodies that can supersede those artifacts. A missing/duplicate path, non-GO report, nonterminal join, stale ancestry, later overlapping edit, active receipt, or ambiguous disposition blocks before route creation.

- [ ] **Step 2: Validate the control-plane preservation chain**

Resolve `docs/HANDOFF-owner-2026-07-16-control-plane-wip.md` only through the exact content-addressed reference in the aggregate owner handoff. Require the original ref `codex/control-plane-authority-foundation-2026-07-10` still equals `6983673db60bff0d21548a90ab1db2fcbbfa377a`; require preservation branch `codex/recovery-control-plane-wip-2026-07-16` at the handoff's exact full head; prove its preservation commit is a child of the frozen old head; and validate the nine exact path/blob IDs plus disposition `commit-and-handoff for salvage only`. Compare committed objects, not working-tree paths. A moved old ref, a tenth path, a changed blob, or any GO/merge claim blocks.

- [ ] **Step 3: Commit one exact Phase-3 route**

Refresh coordinator mail, capacity, locks, `main`, worktrees, and remote divergence. The coordinator commits one consolidated route that binds every predecessor handoff/report/join by path/commit/blob/digest, the PPL no-in-flight receipt manifest digest, the control-plane owner handoff and preservation head, exact current main parent, Phase-3 branch/worktree, complete write allowlist, tests, stop conditions, Director owner, Operator verifier, and zero provider/ref/activation authority. Validate it with `protocol_capacity_board.py --wave 2 --validate-route`. The route commit must be a one-parent child of the captured main head.

- [ ] **Step 4: Create the worktree from the exact route commit**

```bash
set -euo pipefail
PIPELINE_ROOT=/Users/hyungkoookkim/Pipeline
cd "$PIPELINE_ROOT"
PHASE3_ROUTE_COMMIT="$(env -u GIT_INDEX_FILE git rev-parse 'HEAD^{commit}')"
env -u GIT_INDEX_FILE git worktree add \
  -b codex/control-plane-compact-phase3-convergence-2026-07-16 \
  .worktrees/control-plane-compact-phase3-convergence-2026-07-16 \
  "$PHASE3_ROUTE_COMMIT"
test "$(env -u GIT_INDEX_FILE git -C \
  .worktrees/control-plane-compact-phase3-convergence-2026-07-16 \
  rev-parse 'HEAD^{commit}')" = "$PHASE3_ROUTE_COMMIT"
test -z "$(env -u GIT_INDEX_FILE git -C \
  .worktrees/control-plane-compact-phase3-convergence-2026-07-16 \
  status --porcelain=v1 --untracked-files=all)"
```

Record the route path/commit/blob/digest and `PHASE3_ROUTE_COMMIT` in the fixture, candidate evidence, verification request, and both later handoffs. Never redefine the base from moving `main`.

### Task 1: Freeze the 46-row matrix, preservation-diff ledger, and abuse-case contract

**Files:**
- Create: `tests/fixtures/compact_kernel/control_plane_convergence.json`
- Create: `tests/unit/test_control_plane_convergence.py`

**Interfaces:**
- Fixture schema `compact-kernel-control-plane-convergence/v1` with exact top-level keys `schema`, `umbrella_commit`, `legacy_branch`, `sources`, `criteria`, `wip_salvage`, and `phase4_gates`.
- Every criterion object has exact keys `id`, `source_id`, `source_ordinal`, `summary`, `disposition`, `equivalent_coverage`, and `phase`.
- The matrix contains exactly 46 unique IDs and the ten source hashes above only when the preservation-diff ledger proves no new criterion. `wip_salvage` binds the control-plane handoff/preservation objects and gives every changed hunk/symbol a reviewed disposition without creating a merge, cherry-pick, copy, or July-10 branch dependency.

- [ ] **Step 1: Write the failing matrix validator**

Add tests that assert the exact source/count map `{DESIGN: 10, FAIL1: 9, SPEC: 6, RACE: 2, SCAN: 1, FAIL2: 7, TASK3H: 2, TASK3I: 2, ACT-BLOCK: 3, ACT-CLEAR: 4}`, exact SHA-256 values, exact 46 IDs, unique source ordinals, allowed dispositions, nonempty equivalent coverage, and required Phase-4 gate IDs `P4-ACTIVATION-ONLY`, `P4-MONOTONIC-EPOCH`, `P4-V1-SNAPSHOT`, and `P4-CURSOR-INIT`. Add the four executable current-state selectors named by `already-satisfied` rows: `test_current_signed_bus_activation_is_preserved`, `test_current_markdown_route_is_live_authority`, `test_current_human_and_signed_cursors_are_independent`, and `test_current_private_keys_are_excluded`. Each reads current code/Git state and fails if the claimed coverage is merely prose.

The same validator resolves the frozen old-head and preservation-head blobs through the Task-0 handoff, computes canonical zero-context diffs for all nine paths, hashes every hunk, inventories changed Python symbols, and requires exact one-to-one `wip_salvage` entries. Each entry has one of: `existing-criterion` with nonempty 46-row criterion IDs; `superseded-with-equivalent-coverage` with an executable compact selector or Phase-4 gate; or `new-reviewed-criterion` with a newly reviewed source/ordinal. Unmapped, duplicate, overlapping, or stale hunk/symbol identities fail.

Run:

```bash
env -u GIT_INDEX_FILE .venv/bin/python -m pytest \
  tests/unit/test_control_plane_convergence.py -q
```

Expected: collection succeeds and fails because the fixture is absent.

- [ ] **Step 2: Create the exact matrix and preservation-diff ledger**

Transcribe the normative table above without paraphrase drift. For every `already-satisfied` target, verify the named selector exists and runs on the Phase-3 base. For every carried or superseded target, make the test validate that the named future file/selector or Phase-4 gate exists in the fixture. Populate `wip_salvage` with the owner-handoff reference, frozen original ref/head, preservation branch/head/commit, nine original and preserved blob pairs, aggregate diff digest, per-hunk/symbol hashes, and reviewed dispositions. This ledger is analysis evidence only; never apply a preserved patch or treat a preserved implementation as the chosen design.

If any preserved hunk/symbol expresses a useful invariant not already covered by the 46 rows or an equivalent compact gate, stop. The coordinator must approve a plan correction with a revised criterion count/source hash and a fresh independent design review before Task 2. Never retain the string `46 criteria across 10 immutable sources` while silently adding or dropping a requirement.

Run the validator again. Expected: all matrix tests pass and report `46 criteria across 10 immutable sources`.

- [ ] **Step 3: Run independent design-time abuse enumeration**

Dispatch one fresh reviewer with only this plan's exact interfaces, the fixture, and these pre-stated questions: actor spoof/inheritance; stale verification; changed duplicate event; ref/activation race; ambiguous effect; duplicate provider delivery/spend; missing/invalid v1 source; writer-mode override; raw-content leakage; and post-v1 reader reconstruction. Fold every accepted case into named fixture coverage before implementation. Do not add a second reviewer for the same question.

- [ ] **Step 4: Commit only the matrix and validator**

```bash
env -u GIT_INDEX_FILE git add -- \
  tests/fixtures/compact_kernel/control_plane_convergence.json \
  tests/unit/test_control_plane_convergence.py
env -u GIT_INDEX_FILE git diff --cached --name-only
env -u GIT_INDEX_FILE git commit -m "test(protocol): freeze compact control-plane convergence"
```

Expected staged paths: exactly the two paths above.

### Task 2: Add host-bound runtime, scoped verification, and the Phase-4 reader seam

**Files:**
- Create: `scripts/compact_runtime.py`
- Create: `tests/unit/test_compact_runtime.py`
- Modify: `scripts/capability_v1_adapter.py`
- Modify: `tests/unit/test_capability_v1_adapter.py`
- Modify: `scripts/codex_protocol_model.py`
- Modify: `tests/unit/test_codex_ledger_bridge.py`
- Modify: `scripts/consume_reviewer_result.py`
- Create: `tests/unit/test_consume_reviewer_result.py`

**Interfaces:** exact runtime, verification, legacy observation, and reader projection APIs above. `codex_protocol_model.py` receives an inactive host-principal branch; `consume_reviewer_result.py` receives an inactive scoped-verification branch. Existing v1 outputs remain golden-identical.

- [ ] **Step 1: Write RED principal and verification tests**

Cover exact valid host context, absent/non-protocol source, wrong repository, missing required action, challenge mismatch/replay, malformed attestation digest, future issue time, expired proof, unattested/expired/revoked embedded actor, payload/env/argument actor spoof, stale session binding, parentless child claim, child action broadening, and cross-repository replay. Prove there is no production constructor or loader for the source and that a fake source is accepted only at the direct unit boundary. Cover verification invalidation on each of content, dependency, acceptance, evidence, unit version, and verifier binding; an unrelated route/work revision or unrelated unit change must not invalidate.

Run:

```bash
env -u GIT_INDEX_FILE .venv/bin/python -m pytest \
  tests/unit/test_compact_runtime.py \
  tests/unit/test_capability_v1_adapter.py -q
```

Expected: fail on missing `compact_runtime` and projection APIs.

- [ ] **Step 2: Implement the minimal host-bound checks and verification key**

Validate `AuthenticatedActorSource` by capability use and validate exact `HostAuthenticatedActor`/actor dataclass identity and every field; never coerce mappings or strings into a source, proof, or actor. Require exact challenge digest, repository and required action, fresh proof timestamps, canonical attestation digest, action membership, `attested=True`, `expired=False`, `revoked=False`, and a strict child subset when a parent exists. Errors expose only stable codes. The host source performs host authentication; repository code only verifies and consumes the challenge-bound result. Compute verification equality over exactly the eight `VerificationKey` fields.

Run the RED selectors. Expected: all principal and scoped-verification cases pass.

- [ ] **Step 3: Add RED reader projection tests**

Cover all 49 Phase-2 mappings; stable source ordering; one source ID with changed bytes; missing, duplicate, ambiguous, and unknown observations; specialized states with no route-event transition; typed unavailable state; global source failure; no source-path reopen; and reconstruction containing route/work revision, unit version, precondition, scope meaning, verification reference, and source IDs.

Implement `project_v1_history()` and `project_reader_state()` as pure transformations over frozen host-normalized records. They must not open a mailbox path or create a compact event.

Run:

```bash
env -u GIT_INDEX_FILE .venv/bin/python -m pytest \
  tests/unit/test_capability_v1_adapter.py \
  tests/unit/test_compact_runtime.py -q
```

Expected: zero failures; specialized lifecycle records have `route_event_transition_id is None`.

- [ ] **Step 4: Wire real inactive callers and prove v1 stability**

Add narrow branches in `codex_protocol_model.py` and `consume_reviewer_result.py` that call the compact APIs only after `compact_writer_active(root)`. Because that predicate is structurally false, current output and mutation behavior cannot change. Add AST tests proving the calls exist and negative tests proving env/CLI/config/payload values cannot reach them.

Run:

```bash
env -u GIT_INDEX_FILE .venv/bin/python -m pytest \
  tests/unit/test_codex_ledger_bridge.py \
  tests/unit/test_consume_reviewer_result.py \
  tests/unit/test_compact_runtime.py \
  tests/unit/test_capability_v1_adapter.py -q
```

Expected: all pass; existing v1 golden output is unchanged; no filesystem protocol artifact is created by direct work.

- [ ] **Step 5: Commit the runtime/reader slice**

Stage the eight exact paths above, inspect `git diff --cached --stat`, and commit:

```bash
env -u GIT_INDEX_FILE git commit -m "feat(protocol): add inactive compact runtime boundary"
```

### Task 3: Add the single compact event log and fence the legacy sender

**Files:**
- Create: `scripts/compact_event_store.py`
- Create: `tests/unit/test_compact_event_store.py`
- Create: `schemas/compact-mailbox-v1.schema.json`
- Create: `tests/unit/test_compact_mailbox_schema_sync.py`
- Modify: `coordination/bin/send-event`
- Modify: `tests/unit/test_coordination_tooling.py`
- Modify: `scripts/compact_runtime.py`
- Modify: `tests/unit/test_compact_runtime.py`
- Modify: `scripts/status.py`
- Modify: `tests/unit/test_status.py`
- Modify: `scripts/consume_bus.py`
- Create: `tests/unit/test_consume_bus.py`

**Interfaces:** exact event, mailbox-payload, append, cursor, unread, codec, and reader APIs above. One future event ref, one fixed cursor namespace, one first-parent event chain, no Markdown authority and no second operation store.

The exact inactive production caller map is:

```text
coordination/bin/send-event -> append_transition(mailbox=...)
scripts/status.py -> unread_mailbox_messages()
scripts/consume_bus.py -> read_cursor() + advance_cursor()
```

Every branch is selected only by the structural writer gate. Epoch 0 executes the existing v1 path.

- [ ] **Step 1: Write RED codec and history tests**

In disposable Git repositories, cover canonical event/mailbox/cursor round trips; module/schema recipient, kind, and size identity; initial compact-kind equality with the v1 registry; unknown/missing fields; noncanonical bytes; transition or mailbox digest mismatch; mailbox blob OID mismatch; extra/missing tree entry; sender/actor mismatch; unknown recipient/kind; invalid UTF-8/size; parent or sequence mismatch; merge commit; missing object; wrong object type; multiple introductions; exact duplicate ID/payload; changed duplicate ID; ordered reader reconstruction; and no raw provider prompt/response or prose authority fields. Assert subject/body round-trip exactly for rendering while never being reparsed for authority.

Run:

```bash
env -u GIT_INDEX_FILE .venv/bin/python -m pytest \
  tests/unit/test_compact_event_store.py \
  tests/unit/test_compact_mailbox_schema_sync.py -q
```

Expected: fail because the module is absent.

- [ ] **Step 2: Implement canonical record/read primitives**

Use RFC-8785 canonical bytes and literal Git object IDs. Walk one pinned first-parent tip, reject a second parent, verify each record's sequence/`previous_event_oid`, and return oldest-to-newest records. Resolve `mailbox.json` only through its bound blob OID and verify that its byte digest equals both record and transition content digests. Do not read floating HEAD or mutable worktree files while validating the chain.

Run the codec/history selectors. Expected: all pass.

- [ ] **Step 3: Write RED fence and CAS tests**

Cover structural Phase-3 refusal before object/ref mutation; no environment/CLI/config/test override; exact-old event-ref mismatch; activation-ref change after precheck; event-ref replacement after lock; wrong common-dir/primary checkout; stale epoch; wrong actor; exact duplicate idempotence; changed duplicate conflict; subprocess failure; and interrupted write leaving the old ref authoritative. Add all six `RECEIVING_SEATS` cursor refs, reject `all`/unknown seat, prove missing post-activation cursor/event is unavailable, exact-old cursor CAS, event/cursor ref rebound, monotonic sequence, ancestor membership, non-regression, idempotent same-target advance, and ordered addressed/broadcast unread filtering. Exercise private write cores only in disposable repositories; `append_transition()` and `advance_cursor()` themselves must remain inactive.

Implement the common-dir lock, fresh activation/event reread, object creation, and exact-old CAS. Capture before/after `for-each-ref` and object reachability in tests.

- [ ] **Step 4: Add the inactive sender selection seam**

Before any legacy mailbox write, have `coordination/bin/send-event` consult trusted-primary code for writer mode. Epoch 0 must select the exact existing v1 code path and preserve stdout, exit code, bytes, stage behavior, and recoverability. A simulated compact-active result must refuse the legacy path and require the host-bound publisher; it may not fall back or accept actor fields from argv/env/body.

Run:

```bash
env -u GIT_INDEX_FILE .venv/bin/python -m pytest \
  tests/unit/test_compact_event_store.py \
  tests/unit/test_coordination_tooling.py \
  tests/unit/test_compact_runtime.py -q
bash -n coordination/bin/send-event
```

Expected: all tests pass; shell syntax exits `0`; the existing v1 sender golden cases remain unchanged.

- [ ] **Step 5: Add inactive status and consume cursor callers**

Add compact branches in `scripts/status.py` and `scripts/consume_bus.py`. Status renders the exact `CompactMailboxMessage` fields and unavailable sentinel; consume resolves the host actor, reads the exact cursor OID, and advances through the pinned event tip. Under epoch 0 both execute their current v1 code paths with byte-identical stdout/stderr/exit behavior. No CLI/env argument can force the compact branch or supply actor authority.

Run:

```bash
env -u GIT_INDEX_FILE .venv/bin/python -m pytest \
  tests/unit/test_status.py \
  tests/unit/test_consume_bus.py \
  tests/unit/test_compact_event_store.py -q
```

Expected: all pass; AST inventory finds exactly the three production caller edges above.

- [ ] **Step 6: Prove reader reconstruction after v1 stops**

Create a disposable v1-prefix plus compact-event-suffix history. Feed the frozen v1 projection and `read_event_chain()` result to the reader. Assert exact route ID, work revision, unit version, scope/precondition, verification reference, source IDs, activation epoch, and writer provenance after the last v1 record. Remove any one field and require a stable failure.

- [ ] **Step 7: Commit the event-log slice**

Stage exactly the twelve paths above and commit:

```bash
env -u GIT_INDEX_FILE git commit -m "feat(protocol): add inactive compact event publisher"
```

### Task 4: Add compact effect reservation and recovery with a real adapter caller

**Files:**
- Create: `scripts/compact_effects.py`
- Create: `tests/unit/test_compact_effects.py`
- Modify: `scripts/route_capability.py`
- Modify: `tests/unit/test_route_capability.py`

**Interfaces:** exact `EffectReservation`, `reserve_effect()`, and `transition_effect()` API and closed lifecycle above. `route_capability.py` is the only Phase-3 production adapter caller and remains on v1 behavior while inactive.

- [ ] **Step 1: Write the RED state-machine suite**

Cover every allowed edge and every forbidden edge; exact duplicate reservation; same ID changed field; wrong work/unit/epoch/executor/grant/target/request; expired grant; precheck/postcheck mismatch; stale/revoked/unattested actor; unknown effect class; and unknown field. Assert `ATTEMPTING` must exist before any attempt and `OUTCOME_UNKNOWN` permits only reconciliation.

Run:

```bash
env -u GIT_INDEX_FILE .venv/bin/python -m pytest \
  tests/unit/test_compact_effects.py -q
```

Expected: fail because the module is absent.

- [ ] **Step 2: Implement the pure reservation/recovery state machine**

Keep effect taxonomy closed and specific; do not introduce a generic shell-command effect. Require host actor and current activation arguments at every transition. Store digests only, never secrets, raw commands, or provider output.

- [ ] **Step 3: Add the inactive `route_capability.py` caller**

When compact writing is inactive, preserve the current `capability/v1` evidence-after-effect semantics exactly. Add an unreachable compact branch that creates/resolves `EffectReservation` records but never attempts the effect in Phase 3. AST tests must find the production call; mutation tests must prove no env/config/CLI activation.

Run:

```bash
env -u GIT_INDEX_FILE .venv/bin/python -m pytest \
  tests/unit/test_compact_effects.py \
  tests/unit/test_route_capability.py -q
```

Expected: all pass and no external command, ref, lock, or network call occurs.

- [ ] **Step 4: Commit the effect slice**

Stage exactly the four paths above and commit:

```bash
env -u GIT_INDEX_FILE git commit -m "feat(protocol): add inactive compact effect lifecycle"
```

### Task 5: Add atomic advisory dispatch with exactly two real callers

**Files:**
- Create: `scripts/advisory_dispatch.py`
- Create: `tests/unit/test_advisory_dispatch.py`
- Modify: `scripts/chatgpt_pro_consult.py`
- Modify: `tests/unit/test_chatgpt_pro_consult.py`
- Modify: `scripts/opus_review_bridge.py`
- Modify: `tests/unit/test_opus_review_bridge.py`

**Interfaces:** exact eligibility and reservation APIs above. Exactly two production callers, no others.

- [ ] **Step 1: Write RED eligibility and atomic-claim tests**

Cover deterministic runtime-aware transport order; no eligible transport; selected transport absent from eligibility; same claim idempotence; changed same intent conflict; symlink/parent replacement; concurrent creators; crash before/after atomic replace; truncated/unknown claim; executor/grant mismatch; and claim content allowlist. Assert the claim contains no raw question, response, path disclosure, credential, screenshot, or transcript.

- [ ] **Step 2: Write RED delivery/recovery abuse tests**

Cover unavailable provider, ambiguous/partial delivery, lost stdout, provider challenge/sign-out, executor death, and changed runtime after reservation. Every case blocks without retry, provider switch, manual/API fallback, or second spend. Resume can only inspect or continue the same reserved provider under its existing provider-specific law.

Run:

```bash
env -u GIT_INDEX_FILE .venv/bin/python -m pytest \
  tests/unit/test_advisory_dispatch.py -q
```

Expected: fail because the module is absent.

- [ ] **Step 3: Implement the atomic claim and migrate the two callers**

Use descriptor-bound/no-follow creation and atomic replace under the existing provider record lock. Keep provider-specific delivery/result stores unchanged. The shared claim binds only purpose and digests; it grants no verdict, protocol, effect, or spend authority.

- [ ] **Step 4: Enforce the exact caller inventory**

Add an AST test that scans production Python and resolves exactly:

```text
scripts/chatgpt_pro_consult.py -> advisory_dispatch
scripts/opus_review_bridge.py -> advisory_dispatch
```

Any third caller or a test-only public helper fails. Run:

```bash
env -u GIT_INDEX_FILE .venv/bin/python -m pytest \
  tests/unit/test_advisory_dispatch.py \
  tests/unit/test_chatgpt_pro_consult.py \
  tests/unit/test_opus_review_bridge.py -q
```

Expected: all pass; existing provider golden behavior remains advisory-only and no live provider is contacted.

- [ ] **Step 5: Commit the advisory slice**

Stage exactly the six paths above and commit:

```bash
env -u GIT_INDEX_FILE git commit -m "refactor(protocol): share atomic advisory dispatch"
```

### Task 6: Absorb packet-state meaning and retire only the orphan module

**Files:**
- Modify: `tests/fixtures/compact_state_mapping/v1.json`
- Modify: `tests/fixtures/compact_kernel/v1_surface_inventory.json`
- Modify: `scripts/compact_state_mapping.py`
- Modify: `tests/unit/test_compact_state_mapping.py`
- Modify: `tests/unit/test_compact_kernel_surface_inventory.py`
- Modify: `tests/unit/test_kernel_properties.py`
- Delete: `scripts/packet_state.py`
- Delete: `tests/unit/test_packet_state.py`
- Modify: `docs/protocol/packet-state.md`
- Modify: `docs/protocol/claude/continuation.md`

**Interfaces:** all `packet_state` work/verification meanings and allowed transition laws become explicit compact mapping fixtures/property tests. No live capacity gate is changed. `route_manifest.py`, `route_lineage.py`, and `route_capability.py` remain.

- [ ] **Step 1: Write RED equivalence tests before deleting anything**

Parameterize every current `packet_state` work mapping, verification mapping, and allowed/forbidden work transition against `compact_state_mapping.meaning_for()` plus the reducer transition laws. Include ready, active, blocked with/without evidence, done with/without verification, excepted, unknown/queued, GO, FAIL, NITS, unable-to-verify, and no-review packet types.

Run the exact equivalence selectors while `packet_state.py` still exists. Expected: RED where the compact fixture lacks an explicit old law.

- [ ] **Step 2: Extend only the compact fixtures/mapping until equivalence is complete**

Do not add an adapter that imports `packet_state`. The new expected values live in JSON fixtures; production meaning remains one compact mapping/reducer. Rerun Phase-2 parity and require zero authority/effect-eligibility divergence.

- [ ] **Step 3: Delete the standalone module and migrate property tests**

Remove `scripts/packet_state.py` and its dedicated test. Rewrite the `tests/unit/test_kernel_properties.py` packet-state section to target the compact mapping/reducer. Update surface inventory to classify the old module as retired with equivalent coverage.

Run:

```bash
env -u GIT_INDEX_FILE rg -n "(^|[^a-z_])packet_state([^a-z_]|$)" \
  --glob '*.py' --glob '*.md' --glob '*.toml' .
env -u GIT_INDEX_FILE .venv/bin/python -m pytest \
  tests/unit/test_compact_state_mapping.py \
  tests/unit/test_capability_v1_adapter.py \
  tests/unit/test_compact_kernel_surface_inventory.py \
  tests/unit/test_kernel_properties.py -q
```

Expected: code/tests have no `packet_state` import or command. Historical ADR/plan references may remain; active docs state retirement and point to compact equivalents. All tests pass with zero parity divergence.

- [ ] **Step 4: Update active compatibility docs truthfully**

Turn `docs/protocol/packet-state.md` into a short retirement/equivalent-coverage record. Remove the live command from `docs/protocol/claude/continuation.md`. Do not rewrite historical `DECISIONS.md` or prior plan files.

- [ ] **Step 5: Commit the retirement slice**

Stage exactly the ten paths above, including both deletions, and commit:

```bash
env -u GIT_INDEX_FILE git commit -m "refactor(protocol): retire orphan packet state derivation"
```

### Task 7: Prove convergence, record evidence, and hand off without activation

**Files:**
- Create: `logs/capability-first/phase3-control-plane-convergence.json`
- Modify: `docs/superpowers/capability_first_compact_kernel_codex_seat_guide.md`
- Modify: `ARCHITECTURE.md`
- Create: `docs/HANDOFF-director-2026-07-16-compact-phase3-convergence.md`
- Create only after separately authorized integration: `docs/HANDOFF-coordinator-2026-07-16-compact-phase3-integrated.md`
- Modify only if required by the established doctor manifest: `scripts/codex_protocol_model.py`

**Interfaces:** content-free canonical evidence record, truthful Phase-3 guide status, architecture topology, exact final range and stop boundary.

The executable/evidence commit remains `candidate` with Phase 3 `pending_operator_go`. Only a later docs-only finalization commit may mark Phase 3 complete after binding GO; it never rewrites the candidate evidence.

- [ ] **Step 1: Run the full focused adversarial gate from a clean worktree**

```bash
env -u GIT_INDEX_FILE .venv/bin/python -m pytest \
  tests/unit/test_control_plane_convergence.py \
  tests/unit/test_compact_runtime.py \
  tests/unit/test_compact_event_store.py \
  tests/unit/test_compact_mailbox_schema_sync.py \
  tests/unit/test_compact_effects.py \
  tests/unit/test_advisory_dispatch.py \
  tests/unit/test_capability_v1_adapter.py \
  tests/unit/test_status.py \
  tests/unit/test_consume_bus.py \
  tests/unit/test_compact_state_mapping.py \
  tests/unit/test_compact_kernel_surface_inventory.py \
  tests/unit/test_kernel_properties.py \
  tests/unit/test_codex_ledger_bridge.py \
  tests/unit/test_consume_reviewer_result.py \
  tests/unit/test_route_capability.py \
  tests/unit/test_chatgpt_pro_consult.py \
  tests/unit/test_opus_review_bridge.py \
  tests/unit/test_opus_review_receipts.py \
  tests/unit/test_opus_target_review_bridge.py \
  tests/unit/test_protocol_prompt_sync.py \
  tests/unit/test_coordination_tooling.py -q
```

Expected: exit `0`; no xfail/skip may stand in for an adversarial selector. The target-aware bridge suite proves the installed target policy, sealed closure, prompt authority, route/consent/token binding, and receipt-CAS behavior remain compatible after the generic Opus/advisory changes. Provider attempts and receipt-store mutations remain `0`.

- [ ] **Step 2: Run broad compatibility and invariant gates**

```bash
env -u GIT_INDEX_FILE .venv/bin/python -m pytest tests/unit -q
env -u GIT_INDEX_FILE .venv/bin/python scripts/capability_v1_adapter.py \
  --check-corpus tests/fixtures/compact_kernel/v1_to_v2_replay.json
env -u GIT_INDEX_FILE .venv/bin/python scripts/target_binding.py --check
env -u GIT_INDEX_FILE .venv/bin/python scripts/ci_smoke.py
env -u GIT_INDEX_FILE git diff --check HEAD~1..HEAD
```

Expected: all unit tests pass; parity has empty blocking divergence arrays; target binding reports epoch `0`, writer `v1`, declarative-only; smoke passes; diff check is silent.

- [ ] **Step 3: Prove inactive structure and live-v1 equivalence**

Run a committed inventory test that asserts:

```text
compact_writer_active == structurally false
refs/protocol/kernel-activation == absent and unchanged
refs/protocol/kernel-events == absent and unchanged
refs/protocol/kernel-cursors/* == absent and unchanged
live writer == v1
compact production event writes == 0
compact production effect attempts == 0
advisory production sends during tests == 0
legacy/compact authority divergence == 0
legacy/compact effect-eligibility divergence == 0
unclassified production helpers == 0
```

Capture before/after ref sets and working-tree status. A newly created ref or live behavior difference is FAIL, not cleanup work.

- [ ] **Step 4: Write the canonical evidence artifact**

Create `logs/capability-first/phase3-control-plane-convergence.json` with schema `compact-kernel-phase3-convergence/v1`, `status="candidate"`, `phase3_gate="pending_operator_go"`, exact implementation base and known pre-evidence code head/range, 46-row matrix digest, source hashes, preservation-handoff reference, preservation-diff-ledger digest and disposition counts, test commands and outcomes, production caller inventory, event/mailbox/cursor schema IDs and refs, writer epoch/mode, zero-divergence arrays, zero-side-effect counts, target-bridge compatibility result, provider-attempt/receipt-mutation counts `0`, retained compatibility modules, retired modules, and Phase-4 gate IDs. Do not put the future containing evidence-commit SHA or future Operator verdict in this artifact; the candidate commit, Lane-V descriptor, report, and final handoff bind those facts without a self-hash. Include digests and selectors, never raw prompts, provider responses, credentials, or mailbox bodies. This candidate artifact is immutable after commit; the later Operator report carries the GO fact.

Validate RFC-8785 canonical bytes and rerun the evidence test. Expected: byte-stable reserialization.

- [ ] **Step 5: Update the guide and architecture as a pending candidate**

Leave every Phase-3 completion box unchecked. Record exact implemented topology in `ARCHITECTURE.md`, but label guide status explicitly:

```text
Phase 3 candidate: inactive boundaries and real callers implemented; Operator GO pending.
Activation epoch: 0.
Writer: v1.
Compact event log: schema frozen, no live ref.
Compact mailbox payload: schema frozen, no live publication.
Compact per-seat cursors: schema/ref namespace frozen, no live refs.
Phase 4: not started; reader migration, writer fence activation, and pruning remain gated.
```

Update `ARCHITECTURE.md` with exact file:line anchors for the runtime, reader projection, event log, effect lifecycle, advisory dispatcher, and packet-state retirement. Do not claim compact authority.

- [ ] **Step 6: Commit the pending candidate evidence and truth docs**

Stage only the immutable candidate evidence, pending guide status, architecture, and an already-established doctor-manifest update if the current model requires the new selectors. Do not create or finalize the handoff yet. Commit:

```bash
env -u GIT_INDEX_FILE git commit -m "docs(protocol): prepare compact phase 3 candidate"
```

- [ ] **Step 7: Request independent verification of the actual range**

Use `superpowers:requesting-code-review`, then a lawful Lane-V verify request. The reviewer must answer these distinct questions against the exact base/head range: all 46 rows present or a separately approved revised count; every preserved WIP hunk/symbol dispositioned with no old-branch code imported wholesale; no live-v1 semantic change; host identity unforgeable from repo inputs; scoped GO invalidates exactly; event log canonical/CAS/fenced; effects ambiguous-safe; advisory no-retry/no-fallback; exactly two advisory callers; target-aware bridge provider-free compatibility retained with zero provider/receipt mutation; packet-state meaning preserved; Phase 4 still inactive.

GO requires the focused adversarial command, full unit suite, parity CLI, target binding, smoke, ref before/after evidence, and matrix validator. NITS or FAIL stops the handoff; do not push or activate.

- [ ] **Step 8: Finalize status and the exact handoff in a docs-only commit**

Only after GO, check the Phase-3 guide boxes, mark this plan complete if maintained, and create `docs/HANDOFF-director-2026-07-16-compact-phase3-convergence.md`. It names exact base/head, commit list, reviewed range, Operator report path and verdict, immutable candidate-evidence digest, retained compatibility surfaces, retired packet-state surface, epoch `0`, writer `v1`, and absent activation/event/cursor refs, plus the exact next trigger:

```text
Next trigger: obtain separate user authority for local Phase-3 integration and merged-tree verification; Phase 4 remains blocked until the fixed integrated handoff commits.
Not authorized: merge, push, activation, compact publication, ref mutation,
legacy writer deletion, old-branch cleanup, provider send, or external effect.
```

Commit only the guide, this plan if its checkboxes are maintained, and the handoff with subject `docs(protocol): finalize compact phase 3 after GO`. Do not change production, tests, fixtures, architecture claims, or the candidate log after the reviewed head. This docs-only finalization does not trigger duplicate Lane V for unchanged production.

- [ ] **Step 9: Integrate under fresh authority and commit the fixed Phase-3 integrated handoff**

After GO and docs-only finalization, stop for a fresh explicit user-principal authorization naming one local integrator and binding the exact Phase-3 route base, reviewed production head, finalization head, and current target `main` head. The authorization is local-integration-only and grants no push, activation, protocol-ref mutation, cleanup, or conflict resolution. The coordinator records but does not execute it.

The named integrator refreshes main/mail/capacity/locks/worktrees/remote state, validates all upstream content-addressed handoffs again, and integrates locally. Any conflict or overlapping post-review edit stops for a revised range and renewed Operator review. On the merged tree rerun the complete focused adversarial suite, full unit suite, parity/target-binding/smoke gates, preservation-ledger validator, inactive-ref checks, target-aware bridge suite, provider-attempt/receipt-store before/after manifest equality, and exact ancestry/path checks. Capture the exact integrated code SHA.

Only after those gates pass, the coordinator creates and commits only `docs/HANDOFF-coordinator-2026-07-16-compact-phase3-integrated.md`. It binds the user authority correlation, named integrator, Phase-3 base/reviewed/finalization heads, Operator GO report, exact integrated code SHA, containing primary-main ancestry, merged-tree commands/results, upstream handoff set, preservation-ledger digest, epoch `0`, writer `v1`, absent activation/event/cursor refs, and push/activation/cleanup `not-authorized`. Capture its commit/blob/digest and prove the commit changes only that path. Phase 4 must start from this exact containing handoff commit, never the pre-merge candidate branch.

## Stop Conditions

Stop immediately and return a bounded blocker if any of these occurs:

- The Phase-1/2 handoff lacks an exact GO-reviewed source SHA, or its SHA changes.
- Any required upstream integration/disposition handoff is absent, nonterminal, stale, or not an ancestor of the captured Phase-3 base; any PPL advisory receipt remains active.
- Any legacy source hash or criterion count differs from the frozen manifest.
- The July-10 worktree owner WIP changes in a way that would be overwritten or mistaken for source.
- A proposed implementation requires merging/cherry-picking the old branch or deploying its privileged service/key/cutover stack.
- A compact path can be activated through env, CLI, payload, config, governance mirror, test hook, or caller injection.
- A host actor can be forged, broadened by a child, replayed across repository, or accepted while unattested/expired/revoked.
- Verification remains current after a relevant digest/binding change or becomes stale from an unrelated route/unit change.
- The event publisher can write without a fresh activation/event ref inside the common-dir fence, the cursor can advance without fresh activation/event/cursor refs in the same fence, mailbox rendering fields are not digest-bound to the transition, or reader reconstruction loses metadata after v1 stops.
- An ambiguous effect/provider outcome can retry, switch provider/executor, or claim success without reconciliation.
- Advisory dispatch has other than the two named production callers or records raw content.
- Packet-state deletion loses any mapping/transition property or changes a live capacity gate.
- Parity shows any authority/effect-eligibility divergence, target binding differs from epoch `0`/writer `v1`, a compact ref appears, or live v1 output changes.
- The user has not separately authorized the exact local integration, the named integrator differs, or the merged-tree gate fails.
- Independent review is NITS/FAIL or lacks the exact reviewed range.

At any stop, preserve the isolated worktree and exact evidence. Do not repair by widening authority, weakening tests, activating a fallback, or importing the rejected branch.
