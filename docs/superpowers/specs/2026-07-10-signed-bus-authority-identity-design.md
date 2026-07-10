# Signed-Bus Authority And Runtime Identity Design

## Purpose

Activate Pipeline's signed ref bus for signed control and promotion facts while
repairing the false-clean mailbox state and fail-open runtime identity model.
The result must preserve a human-readable coordination mailbox, separate the
two channels mechanically, and prevent any environment combination from
synthesizing mixed seat authority.

## Accepted Decisions

- The user-principal activated the signed bus on 2026-07-10.
- Signed control and promotion facts become authoritative on
  `refs/threeway/*` after the cutover gate succeeds.
- Markdown mailbox artifacts remain authoritative for human routes, briefs,
  verify-requests, verification reports, and handoffs.
- No event class is dual-written.
- Coordinators remain all-scope and unpinned for the human mailbox.
- Signed-fact cursor identities are independent from human-mailbox cursors.
- The signed-fact event ref and cursor namespace are fixed protocol constants:
  `refs/threeway/events` and `refs/threeway/cursors/`. The manifest records
  them but cannot reconfigure them.
- All private signing keys remain outside git and outside candidate-executing
  environments.
- Task 6C is the sole signed-facts `shadow` to `live` transition. Tasks 6A and
  6B provision and measure inputs while authority remains `shadow`.
- Local cutover uses verified-exact resume. While signed-fact authority remains
  `shadow`, a repeated invocation may only verify a complete managed-ref set
  that exactly matches the committed, independently scratch-derived expected-
  post OID map, perform no ref
  rewrite, and finish the durable `shadow` to `live` marker. Partial, extra,
  mismatched, changed-HEAD, or already-`live` state fails closed.

## Current Defects Addressed

1. All six human-mailbox cursor files contain scalar `0`, which selects the
   ref-bus unread path even though local signed refs are absent.
2. Missing event and cursor refs collapse to a valid-looking zero unread.
3. Runtime tools disagree on whether coordinators own consumable mailbox
   cursors.
4. `CODEX_SEAT`, `CODEX_AGENT_MODE`, and `CODEX_AGENT_ROLE` are resolved
   independently and can produce hybrid authority.
5. Mutation hooks trust unvalidated seat strings.
6. The signed-bus activation prerequisites are built but not deployed: public
   keys, private-key custody, cursor backfill, authority flip, CI signer, and
   protected merge-gate runner.

## Channel Authority Manifest

Add a committed manifest at `coordination/authority.toml` with a versioned
schema and explicit channel state:

```toml
schema_version = 1

[human_mailbox]
backend = "legacy-files"
authority = "live"
read_scope = "addressed-pairs-all-scope-coordinators"
cursor_envelope_schema = "typed-v1"

[signed_facts]
backend = "signed-ref-bus"
authority = "live"
events_ref = "refs/threeway/events"
cursor_namespace = "refs/threeway/cursors/"

[decision]
adr = "DECISIONS.md#adr-013-narrow-signed-facts-activation-to-task-6c"
activated_by = "user-principal"
```

Runtime code reads this manifest. Cursor content and ref presence are evidence
checked against the declared state; neither chooses the state.

### Fail-Closed Rules

- `human_mailbox.authority=live` requires a readable mailbox directory and
  valid pair-seat cursors or explicit uninitialized cursor state.
- `signed_facts.authority=live` requires the event ref, required signer public
  keys, and valid signed-fact cursor refs.
- A missing required signed ref is `authority unavailable`, not zero unread.
- Unknown manifest values or versions fail startup and mutation commands.
- `signed_facts.events_ref` must equal `refs/threeway/events` and
  `signed_facts.cursor_namespace` must equal `refs/threeway/cursors/`; a
  syntactically valid alternative is still invalid configuration.
- Status output names the channel and authority state beside every count.

## Human Mailbox Policy

Define separate concepts in `scripts/protocol_mailbox.py`:

```text
addressable identities
human-mailbox cursor owners
human-mailbox receipt-tracked identities
all-scope readers
signed-fact identities
```

Pair seats are addressed readers, cursor owners, and receipt-tracked.
Coordinators are addressable senders/targets and all-scope readers, but are not
human-mailbox cursor owners or receipt-tracked identities. `all` is a target,
not an identity.

Pair-seat cursors use an explicit legacy-mailbox cursor representation. Signed
bus sequence numbers never appear in human-mailbox cursor files. If the current
scalar-zero state cannot be mapped to a proven legacy timestamp, the migration
sets the pair cursor to an explicit uninitialized value and surfaces all
addressed historical mail for intentional reconciliation.

Both `coordination/bin/consume-events` and `scripts/consume_bus.py` reject
coordinator aliases for human-mailbox consumption. Signed-fact consumption uses
the signed-fact identity policy and ref cursor namespace, not the mailbox roster.

### Historical Envelope Provenance

Task 2 replaces the failed wall-clock cutoff with immutable Git-introduction
provenance. `human_mailbox.cursor_envelope_schema = "typed-v1"` is committed in
the corrective child that deploys the typed generator. Validation identifies
the unique marker-introduction commit: the one HEAD-ancestor whose tree first
contains the exact field while none of its parents does. Zero or multiple
candidates fail closed. A committed numeric envelope is legacy only when its
own unique introducing commit is a HEAD-ancestor, the marker-introduction
commit is not an ancestor of that event-introduction commit, and current event
bytes equal both the introducing blob and the blob at the exact lexical
`HEAD:<path>`. The repo-relative Git path is derived without dereferencing
symlinks; every component below the repository root and the leaf itself must be
an unsymlinked regular path. Deletion or modification at HEAD followed by an
uncommitted byte restoration, or a leaf/parent symlink rebound, therefore
remains invalid. Numeric mail introduced after the marker,
uncommitted numeric mail while the marker is active, a backdated addition, a
renamed event, or byte-modified legacy mail fails closed. This permits lawful
numeric mail whose introducing commit does not descend from the marker-
introduction commit, including parallel pre-integration mail, without granting
a wall-clock bypass.

`scripts/protocol_mailbox.py` owns one strict event parser used by send,
consume, status, checkers, monitors, draft handoffs, and hook state rendering.
The parser validates the full filename, sender, target, registered kind,
self-addressing prohibition, H1/`When`/`From` agreement, terminal envelope, and
legacy provenance before an event can affect a cursor or count. A missing
`sent/` directory, malformed full cursor file, unknown identity/kind, or
trailing cursor content is unavailable/invalid, never zero unread.

Human cursor advance is one synchronized compare-and-replace operation. It
opens and exclusively locks the stable `coordination/mailbox/seen/` directory
descriptor for the complete operation, rereads and fully validates the cursor
under lock, selects only strictly parsed addressed events, refuses regression,
writes and fsyncs a same-directory temporary file, atomically replaces the
cursor, fsyncs the directory, and only then permits explicit-path staging.
Concurrent or interrupted consumers cannot regress or truncate the cursor.

Every derived human-unread surface calls the same policy: status, both
seat-status mirrors, `protocol_effectiveness_report.py`, both `update-state.sh`
mirrors, mailbox monitor, and draft handoff. Coordinators and coordinator2 are
all-scope aliases on every observational surface, with no cursor file.
Effectiveness accepts only canonical parsed envelopes, surfaces invalid scan
state, and carries typed `count`, `unavailable`, and `all-scope-unpinned`
observations through JSON and summary rendering without coercing either sentinel
to zero. Continuation readiness uses the human-reader roster only for human
mail and `SIGNED_FACT_CURSOR_IDENTITIES` only for signed-bus probes.
Coordinator2 automatic drafts use the canonical `HANDOFF-coordinator-*` token,
and both coordinator aliases participate symmetrically in route-to-GO samples.
`ledger_start_guard.py` and `protocol_capacity.py` remain intentionally
canonical-`coordinator` route-authority surfaces; observational alias parity
does not silently widen route ownership.

## Runtime Identity Model

Introduce a typed `RuntimeIdentity` resolved from a concrete seat and validated
before authority defaults are rendered:

```text
mode
concrete_seat
agent_role
behavior_source
capability_scope
mutation_scope
mailbox_policy
git_policy
verification_policy
routing_authority
publication_eligibility
identity_valid
validation_errors
```

### Resolution Rules

- A live-seat mode requires one concrete pair seat.
- A coordinator mode requires a coordinator alias and never gains production
  implementation or operator GO authority.
- A readiness bridge or subagent cannot carry a concrete seat.
- Subagent mode requires exactly one supported spawned `agent_role`; that role
  survives session binding and selects its frozen narrow-only defaults.
- An explicit role must agree with the seat-derived role family.
- An explicit mode must agree with the seat-derived mode.
- Unknown seats, roles, modes, or policies are invalid.
- Capability, mutation, mailbox, git, verification, and authority overrides may
  only narrow the resolved defaults.
- Read-only orientation may render an invalid contract with errors.
- Every mutation hook, mailbox mutation command, signed emitter, and verdict
  command exits nonzero for an invalid identity.

Behavior-source reuse remains supported: `director2` uses director behavior and
both operators use operator behavior. Behavior-source reuse never changes the
concrete seat's durable identity.

Runtime-operation eligibility is necessary but never sufficient for a
user-gated side effect. `ROUTE_MUTATE`, `LOCK_MUTATE`,
`HUMAN_CURSOR_CONSUME`, and `SIGNED_CURSOR_CONSUME` require both a valid
runtime identity and a current executable side-effect token. Signed-fact emit
also always requires a token; an emitter configured with a remote additionally
requires remote-publication authorization before any local or remote ref
change. The one parser
and verifier is `scripts/protocol_executor_token.py`; route validation, the
PreToolUse guard, interactive commands, and cutover all consume that module
instead of maintaining parallel Markdown parsers.

Before stdin is read into an artifact, a temporary file is created, or any
file, index, lock, cursor, or ref is changed, the caller supplies a committed
token source path and exact side-effect ID. The verifier binds the concrete
executor, normalized target, command class, expected HEAD, current appointment,
preflight results, stop predicates, and already-satisfied target state. An
absent, duplicate, uncommitted, stale, superseded, wrong-target, wrong-executor,
wrong-command, wrong-HEAD, failed-preflight, triggered-stop, or already-
satisfied token fails closed with no mutation.

The lock scripts are remote operations, not local lock-file helpers:
`claim-lock` fetches/merges, commits, and pushes, while `release-lock` commits
and pushes. Their frozen command bundles therefore require both `LOCK_MUTATE`
and `REMOTE_PUBLISH`. A separate `lock-mutation-local` class covers an
explicitly local lock-file mutation. Missing either remote-lock operation, a
wrong command class, or an ineligible actor fails before fetch, merge, file,
index, commit, reset, or push.

One cumulative runtime entry point resolves identity, verifies actor-operation
and command-context eligibility, and, for token-required or token-appointed
operations, verifies the exact executor token before returning authorization.
Token-required mutation callers may not call a bare eligibility predicate.
`REMOTE_PUBLISH`, `TRUST_ROOT_BOOTSTRAP`, and `AUTHORITY_CUTOVER` have no
default actor. Remote appointability is frozen by command class: remote lock
claim/release admit only director-family or coordinator identities, and remote
signed-fact publication may additionally admit an operator only for a fact
signed by that same concrete operator and bound to a committed GO from the
other operator. The binding records fact kind, signer, candidate, independent
verifier, and verification-report path in the committed executor token and the
returned authorization. A readiness bridge, subagent, or mechanical principal
is never appointable. Signed cursor advancement is local-only even when events
are read from a remote authority, so no remote-cursor publisher is appointable.

The cumulative entry point binds frozen command bundles. Local signed-fact emit
requires `signed-fact-emit`; remote emit requires both `signed-fact-emit` and
`remote-publish`. Local signed-cursor advance requires
`signed-cursor-consume`; reading events from a remote authority still advances
only the local cursor and never requests `remote-publish`. Remote signed-fact
use is explicit and target-bound, never a CLI default.
Authorization completes before event construction, key access, Git-object
creation, fetch, append, push, or cursor mutation.

Publication policy has one exact runtime wire format. The environment variable
is `CODEX_PUBLICATION_POLICY`; its only serialized tokens are lowercase
`true` and `false`, while the resolved identity stores a Boolean. Absent means
the actor default, `false` may narrow a `true` default, and `true` may never
widen a `false` default. Empty, whitespace/case variants, unknown, duplicate,
or conflicting values fail closed in deterministic order. Effective `false`
rejects a remote-publication request before token, key, ref, or mutation
callbacks even when a route otherwise appoints the actor.

Supported spawned roles retain separate frozen narrow-only defaults.
`protocol-director` may mutate only parent-named paths; `protocol-operator`,
`protocol-coordinator`, `lane-v-verifier`, and `money-gate-reviewer` are
read-only advisory helpers. None may send or consume mail, route, issue GO,
publish, or inherit the parent seat. Every capability, mutation, mailbox, git,
verification, routing, and publication policy has a literal token vocabulary;
unknown, empty, widening, or conflicting overrides fail closed.

Mechanical principals use operation-specific maps rather than one token
boolean. The principal resolver binds an exact signer identity and an exact set
of allowed operations; a separate set names which of those operations requires
an executor token. Execution context is a closed enum: overseer and chief
principals run only in `control-plane`, CI only in `ci-runner`, and merge-gate
only in `protected-runner`; `candidate` and every unknown context are invalid.
Candidate environments cannot sign or mutate.

Merge-gate evaluation owns event acquisition; no public function accepts or
returns an `EventSnapshot`, event bytes, proof path/ref, or caller-provided
acquisition capability. `evaluate_gate_read_only()` accepts the trusted event
store, while the real runner's `poll_once()` enters the same private lexical
acquisition context once so candidate discovery and every evaluation consume
one captured tip. Both local and remote acquisition resolve the canonical event
ref and copy only that ref into an isolated temporary bare proof repository
retained for the evaluation lifetime. The proof path/ref never appears on a
returned object. Before every proof command, the context rechecks the private
repository's no-follow path/device/inode identity and rejects a rebound.
The private acquired state retains only immutable ordered JSON bytes and their
binding; candidate discovery discards its freshly parsed events, and each
reduction reparses from those bytes so mutable `Event.payload` objects are never
shared across the two phases.

Every proof-object command uses a dedicated runner with explicit
`git --no-replace-objects --no-lazy-fetch --literal-pathspecs
--git-dir=<private-proof-repository>` arguments and an environment that inherits
no ambient `GIT_*` values, then sets only the fixed proof settings named in the
plan. The protected runner supplies an absolute Git executable before candidate
input; its no-follow path/device/inode identity is rechecked for every command,
and subprocess execution names that exact path rather than resolving it through
ambient `PATH`. The same runner binds Git's absolute exec-path plus an exact
ordered set of absolute, non-group/world-writable helper directories; each
directory identity is rechecked, `--exec-path` is explicit, and child `PATH` is
replaced with only that set. Remote transport/helpers therefore cannot resolve
from caller-controlled `PATH`. Replacement refs, graft/shallow metadata, and
untrusted alternates in the proof repository fail closed. Validation
independently resolves the retained
proof ref and re-reads its actual tip, tree, and ordered event bytes before
reduction. A digest over caller-chosen bytes is not provenance: validation
traverses the real Git object graph at the claimed tip with replacement objects
disabled and compares the actual tree and ordered bytes. Adding one same-tip
replacement ref or redirecting the ambient repository/object database cannot
change which graph is trusted.
Merge computation writes only to a quarantine object directory backed by the
input repository as a read-only alternate. Evaluation records the no-follow
Git-common-directory identity, co-located target/event authority, candidate,
tip/digest, deterministic materialization, expected old SHA, and proposed merge
SHA in one frozen result and leaves durable state unchanged.

Every merge authorization records that same binding and exact effect target.
Application accepts no free candidate, target, or snapshot arguments. It
recomputes repository/authority identity, freshly revalidates both executor
tokens and appointment freshness, and verifies the complete quarantine result
before any durable object import. Plain Git cannot atomically couple refs in
different repositories, so cross-repository apply fails closed before private-
key load, object import, or ref mutation. Co-located local refs publish through
one prepared `update-ref --stdin` transaction: both expected-old updates reach `prepare`
while verified quarantines are visible as alternates, then the exact combined
closure is imported, then the already-prepared transaction commits. A stale ref
therefore leaves the durable input object set unchanged. Remote authority binds
exactly one normalized effective push endpoint for both refs; acquisition and
publication address that endpoint directly rather than a possibly different
fetch URL or multi-push remote alias. The verified merge commit and signed
`merge_completed` event commit publish in one atomic two-ref update with exact
expected-old leases on both refs. Zero/multiple or mismatched push endpoints
fail closed. A concurrent revocation/event append or target change rejects the
whole transaction; neither ref advances. Missing atomic capability, mismatched
material, stale authority, or unsupported topology leaves durable objects and
refs unchanged. Every
target-ref update and completion-fact emission retains exact merge-gate signer
and token requirements; `refs/heads/main` additionally requires an opaque
protected-runner credential attestation. The current merge-gate path mutates
refs and emits `merge_completed`, so it is not the token-free evaluator.

## Signed-Bus Activation Sequence

Activation is one ordered, gated sequence.

### 1. Regression Baseline

Add failing tests for:

- absent live refs reporting unavailable rather than zero;
- scalar signed-bus cursors never selecting human-mailbox unread behavior;
- coordinator human-mailbox consume rejection;
- channel-manifest schema and required-state validation;
- inconsistent seat/mode/role matrices;
- widening environment overrides;
- invalid identities blocked by mutation hooks;
- no dual-write from each emitter class.

Every test includes a one-fact non-vacuity flip.

### 2. Key Bootstrap And Custody

Run the existing idempotent cutover bootstrap once. If public keys already
exist, do not regenerate them. Generate the complete signing roster in one
invocation.

- Commit only `coordination/threeway/keys/*.pub`.
- Keep `<identity>.ed25519` files in seat-local keystores outside the repo.
- Give each interactive seat only its own private key.
- Keep the CI key only in the protected CI secret store.
- Keep the merge-gate key and protected-main credential only on the dedicated
  merge-gate runner.
- Candidate-executing environments hold neither the merge-gate key nor its
  protected-main credential.

Key generation, public-key commit, CI secret upload, and runner deployment are
separate executor-token actions with explicit postchecks.

### 3. Shadow Projection And Divergence Gate

Project legacy structured facts into a shadow signed-bus view without changing
authority. Validate signatures, sequence continuity, event IDs, recipient
mapping, and cursor backfill. Compare the projected/reduced state with current
durable outcomes.

Any divergence, malformed legacy fact, missing required signer, or ambiguous
cursor mapping blocks cutover. Human prose that has no signed-fact equivalent
remains only in the Markdown mailbox and is not a divergence.

### 4. Single Authority Flip

Execute the existing cutover command with its explicit confirmation only after
the shadow gate, focused tests, full signed-bus suites, and operator GO.
The flip creates or verifies the authoritative refs and records the manifest's
live signed-fact state. There is no dual-write window.

The cutover is bound to a committed, secret-free activation manifest under
`coordination/threeway/activation/<activation_id>.toml`. The manifest pins the
trusted code and trust-root commits, structured-source
and projection digests, nonzero projected head, signing and signed-cursor
rosters, Git object format, ordered managed-ref table, exact pre-run ref map,
independently measured expected post-cutover OID for every managed ref, and
rollback boundary. Both
preflight and mutation require the same activation-manifest path, coordinator
executor-token artifact, and side-effect ID. The executor token pins the exact
HEAD containing the manifest plus its digest; the manifest never contains a
self-referential commit or tree hash.

Legacy carrier signatures use one explicitly non-authoritative importer:
`migration-importer:legacy:v1`. Its Ed25519 seed is derived from the public,
domain-separated context
`Pipeline/threeway/legacy-import/v1/pipeline-local-authority-2026-07-10`.
The exact derivation is
`SHA256(UTF8("threeway/non-authoritative-legacy-importer/v1") || 0x00 ||
UTF8(key_context))`, whose 32 output bytes are passed to
`Ed25519PrivateKey.from_private_bytes()`.
The manifest records the derivation profile, context, and derived public key.
This importer is outside the trusted 11-principal signing roster and cannot
authorize any load-bearing fact.

The committed R-MEASURE builder creates the projected events ref and six cursor
refs only in fresh scratch Git repositories with the manifest's object format,
fixed Git identity/timestamps, deterministic importer, and exact structured
source. It records the seven resulting OIDs in the manifest and proves the live
`refs/threeway/*` snapshot is unchanged. Two fresh processes must produce the
same map. The live cutover derives the same importer key; it never generates an
ephemeral importer.

Verified-exact resume exists only for the crash window after the complete
managed-ref set is durable but before the committed authority marker is
`live`. A resume compares the complete live seven-ref map against the committed
scratch-derived expected-post map without writing refs, then permits only the
remaining authority-marker step. Any partial, extra, substituted, or mismatched
ref state is a hard refusal. Once the authority marker is `live`, recovery
requires a new user-authorized action.

Immediately before the marker transition, the driver revalidates every mutable
input: clean tracked tree and index, token-bound HEAD/current appointment,
activation-manifest bytes and digest, exact `shadow` authority preimage and all
non-marker bytes, public-registry digest and pair correspondence, trusted-code
and trust-root commits, structured source and projection, importer binding,
both rosters, all seven expected ref OIDs, GO artifacts, and every stop
predicate. The marker writer uses a no-follow sibling lock, compares the exact
preimage while locked, changes only `shadow` to `live`, fsyncs a same-directory
temporary file, atomically replaces the file, and fsyncs the directory. All
sanctioned authority-marker writers use this cooperative compare-and-swap path.

After the flip:

- signed control and promotion emitters write only the signed ref bus;
- Markdown mailbox senders continue writing human coordination artifacts;
- signed-fact readers fail closed if the live bus is unavailable;
- human-mailbox readers remain independent from ref-bus health.

### 5. Remote CI Signer

Enable `THREEWAY_BUS_LIVE=true` only after the authoritative remote refs and
public-key registry are verified. Install the CI private key as
`THREEWAY_CI_KEY` without printing or persisting it in logs. Trigger the trusted
workflow against an explicit integration ref and SHA. Require the signed
`ci_result` to bind the exact integration SHA and policy digest.

### 6. Protected Merge Gate

Deploy a dedicated runner that owns the merge-gate private key and the only
protected-main credential. It recomputes the deterministic merge, validates the
signed fact set, and updates protected main only when the gate returns GO. A
textual conflict, SHA mismatch, missing signature, stale approval, or failed CI
fact produces ABORT/REWORK and no main mutation.

## Side-Effect Executors

The coordinator creates complete executor tokens before each shared mutation.
`scripts/protocol_executor_token.py` is the single typed loader and executable
verifier. Runtime identity, user consent, executor election, token validation,
and operation-specific safety checks are cumulative gates; no one gate implies
another. Interactive route, lock, and cursor commands require explicit
`--executor-token`/`--side-effect-id` inputs, while direct tool route writes
receive the same committed path/ID through the bound session environment.

At minimum, activation needs distinct target-bound tokens for:

1. public-key trust-root commit;
2. authoritative ref creation/cutover;
3. GitHub repository variable update;
4. GitHub Actions secret update;
5. merge-gate runner deployment;
6. final protected-main publication.

Each token names one executor, target, allowed command class, preflight,
stop-if condition, postcheck, observer seats, closeout owner, and non-goals.
Generic unit authorization does not permit two executors to race the same
target.

The local trust-root bootstrap/public-key commit and the local authoritative
ref cutover are always separate actions. The trust-root token cannot create or
change refs or the authority marker. The cutover token treats the verified
public registry and off-repo private keystore as read-only inputs and cannot
generate keys.

## Verification

Focused suites cover keys, refstore, cutover, cursor backfill, legacy
projection, divergence, emitters, runtime identity, mailbox policy, hooks, and
CI activation guards. Global acceptance runs:

```text
model-derived protocol pytest suite
full unit pytest suite
scripts/threeway_mechanism_ledger.py --check
scripts/ci_smoke.py
scripts/protocol_doctor.py --wave 2
```

Operator verification must inspect the actual implementation diff, rerun the
focused RED/GREEN/non-vacuity selectors, verify no private-key paths are staged,
and confirm the authority manifest matches live local and remote state.

## Documentation And ADRs

Append a signed-bus activation ADR that records the user-principal trigger,
the two-channel authority split, the no-dual-write rule, key custody, and the
protected merge-gate requirement. Update executable-model mirrors,
ARCHITECTURE, operations/adoption docs, seat skills, hooks, and agent prompts in
the same verified cycle.

Do not rewrite prior ADR entries. Mark the new decision's exact relationship to
ADR-010: the bus deferral is ended by the user-principal; the pre-push-hook and
Antigravity decisions remain independently unchanged.

## Acceptance Criteria

- The manifest declares both channels and signed-fact authority as live.
- Missing live signed refs are visible failures.
- Human mailbox unread is correct with signed refs present or absent.
- Legacy numeric envelopes are accepted only when the unique `typed-v1`
  marker-introduction commit is not an ancestor of the event-introduction
  commit and the event bytes remain unchanged; a
  post-marker, backdated, uncommitted, renamed, or modified numeric event is
  rejected.
- Coordinators cannot consume the human mailbox.
- Signed-fact coordinators may use only signed-fact cursor APIs.
- Non-canonical signed event/cursor refs are rejected at manifest load.
- Concurrent human cursor consumers cannot regress or truncate a cursor.
- Both state hooks, both seat-status mirrors, effectiveness reporting, monitor,
  and draft handoff agree with canonical pair/all-scope unread semantics.
- Every seat/mode/role mismatch is rejected before mutation or GO authority.
- Every signed-fact or remote publication mutation passes the cumulative
  runtime-and-token gate, and every supported subagent role remains narrow.
- Public keys are committed and private keys are absent from git and logs.
- Shadow projection has zero unexplained divergence.
- The authority flip has one executor and one durable postcheck.
- CI emits a valid signed result for an exact integration SHA.
- The protected merge-gate performs the only authorized protected-main update.
- Focused tests, full unit tests, smoke, doctor, and independent operator
  verification all pass.
