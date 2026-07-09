# Control-Plane Hardening Program Design

## Decision

Implement all recommendations from the 2026-07-10 control-plane audit as an
ordered hardening program. The user-principal selected signed-bus activation.
The activation applies to signed control and promotion facts; the Markdown
mailbox remains the human coordination channel.

The program uses four independently verifiable sub-projects. Each sub-project
receives its own implementation plan, director-owned implementation commit,
operator verification report, and coordinator closeout before the next
dependent sub-project begins.

## Goals

- Make mailbox, signed-fact, seat, role, and side-effect authority explicit and
  fail closed.
- Activate the signed ref bus without dual-writing or exposing private keys.
- Make capacity routes, execution identity, preflight focus, and join readiness
  cycle-aware and mechanically validated.
- Make effectiveness metrics describe current reduced state instead of
  historical event volume.
- Keep truth documents, publication state, handoff fallback, and target-domain
  reviewer routing executable and auditable.
- Preserve the four-seat model: two author/verifier pairs plus an on-demand
  coordinator. Do not add seats.

## Non-Goals

- Do not move evidence-ledger product truth into Pipeline.
- Do not let coordinator or subagent identities author behavior-changing
  production fixes.
- Do not make the Markdown mailbox a signed-bus event mirror.
- Do not permit a dual-write transition window.
- Do not commit private signing keys.
- Do not force-push, merge, rebase, refresh target checkouts, or publish an
  unverified commit.
- Do not make gate output substitute for operator GO.

## Architecture

### Two Explicit Communication Channels

Pipeline has two channels with different purposes and authority:

| Channel | Purpose | Authority | Cursor model |
|---|---|---|---|
| Markdown mailbox | Human-readable routes, briefs, verify-requests, reports, and handoffs | `coordination/mailbox/sent/*.md` | Pair-seat addressed cursor; coordinators are all-scope and unpinned |
| Signed ref bus | Signed control and promotion facts consumed by threeway reducers and gates | `refs/threeway/*` | Independent ref-backed cursor per signed-fact identity |

A committed authority manifest names both channels and their live state. No
reader may infer authority from cursor syntax, missing refs, or file presence.
Missing required refs are an unavailable/error state, never zero unread.

### Runtime Identity

Concrete seat identity determines mode, behavior source, mailbox policy,
verification authority, mutation scope, and publication eligibility.
Environment variables may confirm or narrow the resolved identity; they may
not independently widen it. Any inconsistent seat/mode/role triple is invalid.
Read-only orientation renders the invalidity explicitly. Mutation hooks and
commands exit nonzero.

### Cycle-Aware Capacity State

New active packets use schema version 2 and carry structured execution
identity: target repository, worktree, base commit, and integration target.
Routes name exactly one task-board cycle. Validators inspect that cycle plus
explicitly declared cross-cycle dependencies, not every packet in the wave.

Join readiness is computed from dependency state, preflight outcome, and
operator verdict. Manual packet status cannot override a blocking FAIL/NITS or
an active dependency.

### Reduced Effectiveness State

Effectiveness metrics reduce evidence by cycle, packet, and target commit.
Later GO and closeout artifacts supersede matching verify-requests and earlier
FAIL/NITS observations. Duplicate verification means the same target and
verification question was repeated, not that two reports share generic prose.

### Truth And Publication

Generated role/authority and channel-authority matrices are rendered from the
executable model into human-facing documentation. Publication status reports
local HEAD, local remote-tracking snapshot, and live published ref separately.
Live publication remains unknown until an explicit remote query runs.

One executor token binds a side effect to one target, one actor, one target SHA,
one allowed command class, one preflight, and one postcheck. Multiple tokens or
success actors for the same target fail closed.

## Sub-Projects And Order

### Sub-Project A: Signed-Bus Authority And Runtime Identity

Deliver the channel manifest, signed-bus cutover, key bootstrap/custody rules,
human-mailbox cursor repair, coordinator unpinned enforcement, strict runtime
identity resolver, mutation-hook validation, CI signer activation, and
protected merge-gate deployment contract.

This sub-project is first because every later route and status report depends
on trustworthy identity and communication state.

Detailed design:
`docs/superpowers/specs/2026-07-10-signed-bus-authority-identity-design.md`.

### Sub-Project B: Cycle-Aware Capacity And Join Readiness

Deliver packet schema v2, structured execution identity, active-cycle route
validation, computed join readiness, structured verification verdicts, and
partitioned Pair-B preflight checks. Closed version-1 cycles remain readable.

Execution/worktree and preflight modules may be implemented independently.
The adapter into `scripts/protocol_capacity.py` is serialized and lands after
the pure modules.

### Sub-Project C: Trustworthy Effectiveness Metrics

Deliver a cycle-aware reducer with schema-versioned output while preserving
the existing CLI's top-level compatibility fields. Recommendations remain
suppressed unless the reduced current state supports them.

This follows Sub-Project B because it consumes structured cycle, execution,
join, verdict, and preflight state.

### Sub-Project D: Truth Surfaces, Domain Routing, And Publication

Deliver executor-token cardinality and actor binding, local-versus-live
publication status, single-seat handoff fallback, the model-generated authority
matrix, a target-owned domain skill/reviewer registry, strengthened
ARCHITECTURE provenance, a corrected program-manual guide, and append-only ADR
reconciliation.

Publication is the terminal action after all prior sub-projects have operator
GO and coordinator closeout. The executor is elected in a complete token before
the remote mutation.

## Verification Strategy

Each behavior change follows RED, GREEN, and non-vacuity proof:

1. Add a focused regression that fails for the current behavior.
2. Run the exact selector and capture the expected failure.
3. Implement the smallest behavior change.
4. Re-run the selector and its sibling suite.
5. Flip one load-bearing fact and prove the regression fails again.
6. Run the model-derived protocol suite and `scripts/ci_smoke.py`.
7. Send one verify-request bound to the implementation commit/range.
8. Require an independent operator GO/NITS/FAIL report.

No sub-project is complete from capacity-board or gate output alone.

## Compatibility And Migration

- Closed packet schema version 1 remains readable and auditable.
- New active cycles require schema version 2.
- Markdown mailbox files remain durable human evidence after signed-bus
  activation.
- Signed-fact emitters write only the ref bus after the authority flip.
- No cursor is silently initialized as consumed. Missing trustworthy migration
  evidence produces an uninitialized state and surfaces all addressed mail.
- Remote bus and publication claims require live remote queries; local refs are
  labeled local snapshots.

## Failure And Rollback

Before the signed-bus authority flip, any failed preflight leaves legacy
authority unchanged. After the flip, readers fail closed on unavailable signed
refs; they do not silently fall back to unsigned facts. A rollback after the
flip requires a new user-authorized authority decision and durable ADR/mailbox
artifact.

Capacity schema migration rejects incomplete active version-2 packets without
rewriting closed history. Effectiveness output retains the prior top-level keys
so existing consumers degrade predictably while adopting schema version 2.

## Completion Criteria

- Signed refs, public-key registry, CI signer, and merge-gate deployment are
  independently verified live.
- Human mailbox unread counts no longer depend on signed-bus cursor state.
- Inconsistent runtime identity cannot reach mutation or GO authority.
- Active routes validate only their named cycle and explicit dependencies.
- Join readiness blocks on FAIL/NITS, blocked preflight, or active dependencies.
- Effectiveness recommendations match the reduced current cycle state.
- Documentation is rendered or regression-pinned against executable models.
- All implementation commits have operator GO.
- One named executor publishes the final verified HEAD and proves the live
  remote ref equals that SHA.
