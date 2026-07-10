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
- All private signing keys remain outside git and outside candidate-executing
  environments.
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

[signed_facts]
backend = "signed-ref-bus"
authority = "live"
events_ref = "refs/threeway/events"
cursor_namespace = "refs/threeway/cursors/"

[decision]
adr = "DECISIONS.md#signed-bus-activation"
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

## Runtime Identity Model

Introduce a typed `RuntimeIdentity` resolved from a concrete seat and validated
before authority defaults are rendered:

```text
mode
concrete_seat
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
runtime identity and a current executable side-effect token. The one parser
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
- Coordinators cannot consume the human mailbox.
- Signed-fact coordinators may use only signed-fact cursor APIs.
- Every seat/mode/role mismatch is rejected before mutation or GO authority.
- Public keys are committed and private keys are absent from git and logs.
- Shadow projection has zero unexplained divergence.
- The authority flip has one executor and one durable postcheck.
- CI emits a valid signed result for an exact integration SHA.
- The protected merge-gate performs the only authorized protected-main update.
- Focused tests, full unit tests, smoke, doctor, and independent operator
  verification all pass.
