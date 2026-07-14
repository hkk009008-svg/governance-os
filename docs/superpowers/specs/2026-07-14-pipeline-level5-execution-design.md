# Pipeline Level-5 Harness Execution Design

Date: 2026-07-14
Status: user-approved direction, coordinator execution design
Scope: the Pipeline governance harness, including every tracked Python and
shell entry point, provider bridge, hook, schema, capacity/mailbox surface,
CI workflow, evidence artifact, and migration boundary

## 1. Decision

Pipeline will converge on a small provider-neutral hardened kernel through a
strangler migration. It will not be replaced in one rewrite, and its provider
surfaces will not continue as independently hardened islands.

The kernel will be the only place that owns:

- actor and capability authorization;
- consumer-scoped cursor ownership;
- canonical versioned events and deterministic state transitions;
- idempotency, replay, and crash-recovery rules;
- command-local side-effect authorization and receipts;
- evidence claims and independent verification bindings.

Codex, Claude/Opus, ChatGPT Pro, Antigravity, and future providers become thin
adapters. An adapter may validate and translate provider-specific input and
output, but it may not own scheduling, cursor policy, authorization, retry,
evidence promotion, or state-transition policy.

## 2. Level-5 Meaning

Level 5 is an assurance claim, not a test-count or abstraction-size claim. A
Level-5 release is independently verifiable, deterministic where declared,
policy-enforced at the mutation boundary, replayable from content-addressed
evidence, reproducible from pinned dependencies, and recoverable under the
declared failure model.

The claim is false while any of these remain true:

- a generated document can cite missing tests and still pass its checker;
- coordinator code can advance a consumer cursor despite the no-consume
  doctrine;
- provider retries, resume paths, or send authority are enforced only by
  prose;
- two state or authority implementations remain writable after cutover;
- a release gate trusts generated text without resolving and executing its
  cited evidence;
- CI depends on mutable actions or unlocked dependencies;
- a supported crash, race, or platform mode lacks a reproducible recovery
  test.

## 3. Current Containment Priorities

The first program slice contains two release-blocking contradictions and one
nearly complete reusable branch:

1. The three-way mechanism ledger can label mechanisms live while citing test
   paths that do not exist. Its checker compares generated text with generated
   text rather than validating the evidence.
2. Root doctrine says coordinators are unpinned and must not consume, while
   committed executable entry points still accept coordinator identities and
   can write cursor state.
3. The clean `codex/opus-lanev-receipt-hardening` branch contains commits
   corresponding to planned Tasks 1-11 through `97c270f`, but completion is
   unverified: its exact-head focused/full gates, independent actual-diff
   review, single receipt-backed Opus attempt, and formal operator verification
   remain incomplete.

The dirty `codex/control-plane-authority-foundation-2026-07-10` worktree is
valuable provenance and may be mined later, but it is not an integration base.
It remains untouched until a dedicated reconciliation task decides which
committed and uncommitted changes survive against current `main`.

## 4. Target Authority Model

### 4.1 Roles

- The user-principal grants program and side-effect authority.
- Coordinators schedule, route, reconcile, and observe. They never consume
  events, advance consumer cursors, issue verification verdicts, or repair
  production behavior.
- Directors own bounded implementation and one verify-request per stable
  scope.
- Operators independently issue GO, NITS, or FAIL for the named immutable
  range.
- Subagents and external models remain advisory. They inherit no mailbox,
  cursor, lock, route, verdict, push, or spend authority.

### 4.2 Events and state

Every authority-bearing transition uses a canonical versioned envelope bound
to actor role, consumer identity where applicable, schema version, causation
and correlation identifiers, idempotency key, content digest or CAS reference,
and transition result. Reducers are deterministic. Transport delivery is
at-least-once; observable effects become effectively-once through durable
idempotency, CAS, and deduplication.

Persisted authority and effect transitions require authenticated provenance.
Pure local helper calls do not need signatures merely for architectural
symmetry.

### 4.3 Cursors

Cursors are consumer-owned state. Only the matching consumer capability can
advance one. Coordinators have no cursor. Legacy coordinator cursor files may
remain temporarily as read-only compatibility artifacts, but no executable
path may advance them, and their deletion or migration must have an explicit
one-way cutover and rollback contract.

### 4.4 Side effects

Every governed side effect is mediated by a typed, expiring, single-executor
capability with preflight, idempotency, stop conditions, postcheck, and an
atomic content-free receipt. Prose and environment variables are not command-
local authority.

## 5. Target Evidence Model

The release evidence layer is content-addressed and independent of the code
that generated a claim. Each claim binds:

- repository identity and exact HEAD;
- relevant source/config/schema hashes;
- exact pytest node IDs or other executable selectors;
- command, toolchain, platform, locale, timezone, seed, and dependency lock;
- normalized result and artifact digests;
- independent verifier identity and verdict.

The verifier resolves every cited source and selector and executes it in a
clean environment. Negative controls must prove that deleting or renaming a
cited test, changing a claim, corrupting an artifact, bypassing a critical
guard, or injecting a failing mutant makes the evidence gate fail.

Parser/schema tests, golden-text synchronization, historical evidence, and
runtime behavior are separately labeled. Only executed behavior evidence can
satisfy a behavior claim.

## 6. Provider Contract

Provider adapters share one semantic contract and may expose namespaced,
versioned extensions. Deliberate provider differences require an owner,
rationale, conformance waiver, and expiry. Hidden adapter policy is a defect.

Provider prompts are rendered from canonical policy inputs or verified against
the exact loaded bytes. Every provider-facing instruction is advisory-only:
no provider is called a seat, controller, committer, verdict issuer, or lock
authority. Raw prompts and responses stay out of Git, mailbox artifacts,
normal logs, screenshots, command arguments, and ordinary transcripts.

ChatGPT Pro and Opus use the same kernel principles even when their transports
differ: one authoritative reservation, no automatic retry, explicit ambiguous-
delivery handling, content-free receipts, bounded output, current state
binding, and operator-owned reconciliation.

## 7. Migration Strategy

The migration is reversible until legacy deletion:

1. Characterize current behavior and stop false assurance.
2. Put a compatibility facade in front of legacy callers.
3. Extract proven primitives behind that facade.
4. Migrate one vertical slice and one provider at a time.
5. Shadow against isolated or side-effect-free sinks and compare normalized
   state transitions, not raw nondeterministic text.
6. Cut over one authority writer at a time and reconcile state.
7. Run a bounded read-only compatibility period.
8. Delete legacy writable paths and duplicated policy.

No migration stage may leave two writable authority models as a permanent
compatibility feature.

## 8. Containment Gate And Seven Migration Waves

### Wave 0 - Pre-wave containment and executable inventory

- Make the mechanism ledger fail on nonexistent or non-collectable evidence.
- Remove coordinator cursor mutation authority from executable entry points.
- Create a machine-readable manifest of every Python, shell, hook, CI, schema,
  state-mutator, provider, and external-side-effect surface.
- Reconcile active branches/worktrees without discarding user-owned WIP.

Exit: no known false-green P0 remains; no executable coordinator-consume path
remains; every executable surface has an owner and assurance classification.

### Wave 1 - Finish consultation bridges

- Complete and independently verify the existing Opus receipt-hardening
  branch, including one actual receipt-backed Opus challenge on an unchanged
  head.
- Harden ChatGPT consultation resume, idempotency, hard-link, coordinator
  binding, activation, stdout/privacy, provenance, crash, and resource bounds.
- Record supported host/sandbox capability classes explicitly.

Exit: both bridges satisfy the common semantic contract and their distinct
transport limits are explicit, tested, and non-authoritative.

### Wave 2 - Trustworthy acceptance and evidence

- Replace self-referential ledgers and prose cells with machine-readable claim
  manifests and an independent executing verifier.
- Add negative controls, mutation gates, deterministic concurrency, crash
  injection, and public-CLI end-to-end tests.

Exit: every promoted claim resolves and executes; corrupted or missing evidence
turns the gate red.

### Wave 3 - Shared hardened kernel

- Extract canonical events, schemas, roles, cursor ownership, CAS,
  idempotency, deterministic transitions, and capability checks behind a
  narrow facade.
- Add static dependency rules and runtime assertions against bypass.

Exit: new code cannot bypass the kernel; one representative vertical slice
passes legacy/kernel differential tests.

### Wave 4 - State and authority cutover

- Migrate consumer cursors and transition ownership with one writer at a time.
- Add durable inbox/outbox, deduplication, dead-letter quarantine, replay, key
  rotation/revocation, and tested rollback.

Exit: zero coordinator cursor advances, zero dual writers, and deterministic
reconciliation at the declared recovery point.

### Wave 5 - Provider and doctrine convergence

- Move all providers and bridges onto generated conformance suites.
- Generate or mechanically verify provider prompts/docs from canonical model
  data; make extensions explicit.

Exit: adapters contain translation only; provider drift is either eliminated
or covered by a current waiver.

### Wave 6 - CI, platform, and supply-chain assurance

- Pin CI actions by commit SHA and dependencies by hashes.
- Test the supported Python/platform/sandbox matrix.
- Add strict lint/type, critical-branch coverage, mutation, fuzz, vulnerability,
  secret, license, SBOM, provenance, and reproducibility gates.

Exit: all supported environments pass and no unwaived critical/high finding or
critical first-order mutant survives.

### Wave 7 - Shadow cutover and deletion

- Run isolated shadow/replay and a predeclared soak window.
- Exercise rollback from every migration stage.
- Delete legacy writable authority, duplicated provider hooks, circular
  evidence checks, and bypass routes.

Exit: observability attributes every transition to actor, cause, schema, and
code version; legacy writable paths are deleted, not merely disabled.

## 9. First Dual-Pair Dispatch

### Pair A - P0 containment

Pair A implements two sequential, independently reviewable commits on a new
isolated worktree based on the coordinator route commit:

1. reject `coordinator` and `coordinator2` at every routed human/signed consume
   entry point in the authorized slice, with real-entrypoint regressions and a
   no-live-state-change assertion;
2. make the mechanism ledger validate evidence existence/collection and render
   unsupported claims as unverified rather than fabricating green coverage.

The slice may not reuse or modify the dirty authority-foundation worktree. If
the write audit finds another coordinator cursor mutator outside the authorized
paths, Pair A stops with a bounded route contradiction instead of widening.

### Pair B - Opus finalization

Pair B receives the clean existing Opus worktree at exact head `97c270f`. It
does not modify code during the first pass. It runs the plan's complete focused,
full, repository, and exact-range gates; performs a fresh independent
actual-diff challenge of Section 9 in
`docs/superpowers/specs/2026-07-13-opus-lanev-receipt-hardening-design.md`;
and only after a local PASS executes the one user-consented, executor-routed
receipt-backed Opus attempt. It then hands the immutable range and receipt to
Operator2.

A local failure stops before provider spend. A provider unavailable result is
recorded once with no retry or substitute, but it does not satisfy this
program's Opus-complete exit criterion. Any newly confirmed code defect returns
to coordinator for a new bounded correction packet.

The two pair write sets are disjoint. Pair A never enters the Opus worktree;
Pair B never enters Pair A's new worktree or the dirty authority worktree.

## 10. Adversarial Acceptance Set

Every triggered implementation must cover, where applicable:

- alternate state files/worktrees creating duplicate idempotency namespaces;
- ambiguous delivery, crash-before/after-send, malformed post-send responses,
  and forbidden resume/retry;
- symlink, hard-link, pathname replacement, parent relocation, temp-file swap,
  and cleanup substitution;
- stale HEAD, route, mailbox, capacity, lock, schema, prompt, or dependency
  binding;
- duplicate/abbreviated/noncanonical authority fields and body/trailer
  ambiguity;
- concurrent reservations with a deterministic contender-ready barrier;
- lost acknowledgement, CAS contention, partial writes, process kill, restart,
  replay, duplicate delivery, and cancellation;
- raw secret/payload leakage through stdout, stderr, logs, traces, screenshots,
  arguments, state, or Git;
- provider output attempting to claim a seat, verdict, commit, route, cursor,
  lock, push, or spend authority;
- deletion/rename of cited evidence and guard-bypass mutations.

Tests must contain an independent oracle and a demonstrated non-vacuous RED for
each critical guard. A label generated and checked by the same test is not an
oracle.

## 11. Compatibility, Rollback, and Deletion

Every task names its compatibility behavior, rollback point, and deletion
condition. Shadow and replay sinks must be isolated or idempotent so parity
testing cannot duplicate external effects. Nondeterministic fields require a
canonical normalization rule before comparison.

The compatibility facade is time-bounded technical debt. Each legacy path has
an owner, telemetry, expiry, and deletion gate. A release cannot claim Level 5
while a legacy bypass remains writable.

## 12. Owner Decisions Deferred to Their Gate

These decisions remain explicit and do not block the first dispatch:

- contractual OS, Python, container, sandbox, and socket support matrix;
- exact recovery objective and rollback point after cutover;
- signature-key ownership, rotation, revocation, and emergency process;
- provider extension roster and waiver owners;
- sensitive data classes and mandatory redaction/encryption rules.

They must be resolved before Waves 4-6 claim their respective exit gates.

## 13. Non-Goals of the First Dispatch

No evidence-ledger product edit, target-aware bridge implementation, merge,
push, lock action, cursor consume, authority flip, key/ref mutation, production
generation, pod action, deployment, publication, or cleanup is authorized.
The prior Wave-2 FAIL, CONTRADICTION, and PPL HOLD evidence remains binding and
is parked rather than reinterpreted.
