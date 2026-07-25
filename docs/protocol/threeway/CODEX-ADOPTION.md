# Codex — Three-Way Protocol Adapter

This is the Codex adapter for the cross-provider three-way protocol. Current
code, `AGENTS.md`, and `scripts/codex_protocol_model.py` win over this document.
Read the shared doctrine only for shared rules; this file records Codex-specific
mechanics and the current deployment boundary.

## Current status

The signed-bus package, reducer, ref store, migration substrate, tiered
emitters, and merge-gate tooling are built and test-covered. That is not a
claim that the signed bus or strategic loop is deployed.

Check the local authority state before relying on it:

```bash
git for-each-ref refs/threeway/
```

Until a local signed event ref **and** the addressed seat's matching cursor ref
resolve with a coherent sequence relationship, the legacy mailbox remains
authoritative for local work. A missing, partial, corrupt, or mismatched pair is
an explicit transport problem, not an empty live bus. Do not infer remote
authority from local code: if it matters, inspect the remote refs directly.

The migration is a one-way, single-writer cutover. Shadow projection and cursor
backfill exist to support it, but a session must not perform or claim the
cutover without evidence from the target environment. There is no dual write:
never write the same coordination fact to the mailbox and signed bus.

The free-form mailbox remains the channel for human coordination, handoffs, and
verify requests. The signed bus carries signed three-way promotion facts only
after its authority proof is complete.

## Codex identity and worktree

Codex begins as a readiness bridge. It has no three-way seat merely because a
prompt, environment value, branch, or prior task names one. A live identity is
closed and explicit: the assigned Codex role is one of `director`, `operator2`,
or `coordinator2`, with the matching harness role and task authority. All other
sessions remain a readiness bridge, coordinator, or parent-bounded subagent as
assigned by the Codex adapter.

`director` owns an accepted outcome; `operator2` independently verifies a
foreign authored range; `coordinator2` observes and reconciles. A coordinator
does not become a signed-bus integrator merely by using the name `coordinator2`.
Integration against protected `main` is unavailable until the protected runner,
credential isolation, branch protection, and ref-ACL deployment are proved.

Use Codex native task worktrees and their native index. Do not create or share
per-seat index machinery or add index-cleanup ceremony. Preserve unrelated work
and use explicit paths for scoped changes.

## Compact orientation

For an assigned role, take one compact status snapshot, read the actionable
event bodies, then refresh the relevant HEAD and scoped working-tree state
before a write or gate decision:

```bash
python scripts/status.py snapshot <assigned-seat>
```

There is no handoff-first prerequisite and no legacy seat-status startup. A
handoff is evidence to inspect when relevant, not a substitute for current
mailbox, cursor, ref, and Git state.

Only the assigned live role consumes its own cursor; a coordinator has no
cursor. Use the fixed mailbox interfaces for mailbox mutations and cursor
consumption. Never edit event files, signed refs, or cursor files directly.
Transport ambiguity must remain visible and fails closed for authority claims.

## Signed-bus deployment facts

- `RefEventStore` is the signed event substrate. A coherent local event ref and
  addressed-seat cursor ref are the minimum local liveness proof; a scalar
  mailbox cursor is not enough.
- The local mechanisms are exercised against `refs/threeway/test-main`.
  Protected `refs/heads/main` remains fail-closed without deployed protection
  and the dedicated merge-gate runner.
- The CI signer is intentionally gated: the `threeway-ci-result` workflow job
  runs only from trusted `main`, after its required checks, and only when the
  live-bus deployment setting is enabled. Its presence in the repository is not
  deployment proof.
- A merge gate recomputes the exact merge and requires the signed evidence for
  the requested tier. It is a protected-runner action, never an ordinary Codex
  session action. Textual integration conflicts are abort-and-rework, not
  authorization for semantic edits.
- Emitters sign only facts owned by their named principal. Test or fixture loop
  helpers are not a production event authority.

## Key and merge boundaries

Public keys form the committed trust registry; private keys stay outside the
repository and are held only by the single environment for their assigned seat.
Candidate-executing environments must not hold the protected merge-gate key.
The CI key belongs only to its unprivileged runner, while the merge-gate key and
the ability to update protected `main` belong only to the protected runner.

No signed event, local green test, role label, or structural validation grants
push, merge, cursor consumption, lock action, provider launch, paid spend, or
live-data mutation authority. Each remains an explicitly authorized external
effect with a named executor, target, and scope.

## Review and evidence

Choose review depth proportionally to the behavior, trust, and side-effect risk.
For behavior-changing work, the assigned non-author Operator reviews the actual
committed range and preserves its evidence-backed GO, NITS, or FAIL. An Operator
never reviews work it authored. Higher-risk changes also require the abuse-case
analysis and evidence expected by the shared doctrine.

Do not duplicate the kernel's rules here. The canonical Codex contracts are:

- `scripts/codex_protocol_model.py` — runtime identity and adapter invariants.
- `AGENTS.md` — task authority, evidence, review, and side-effect policy.
- `docs/protocol/codex/continuation.md` — Codex continuation mechanics.
- `docs/protocol/threeway/UNIFIED-OPERATING-DOCTRINE.md` — shared three-way
  topology and protocol semantics.

When these sources and this adapter disagree, use the executable/current source
and correct the stale documentation in its proper scope.
