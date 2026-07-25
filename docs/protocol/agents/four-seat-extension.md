# Four-seat coordination — protocol extension

Seat identity, lane ownership, broadcast addressing, and coordinator policy are
provider-neutral. Each provider adapter maps them to its own runtime; none of
them are Claude-, Codex-, Cursor-, or AGY-specific.

Status: **ACCEPTED.** The operative lane record for this deployment is
`DECISIONS.md` ADR-009: Pair A = coordination layer, Pair B = verification and
signing layer.

## 1. Seat model

Canonical seat IDs are a 4-set — **`director`, `director2`, `operator`,
`operator2`** — plus a `coordinator` cross-pair role. They form two pairs:

| Pair | Director | Operator | Lane (adopter slot — operative record: ADR-009) |
|------|----------|----------|------|
| **A** | `director`  | `operator`  | **<domain-lane-A>** — <!-- TODO(<PROJECT>): list the Pair-A domain modules, subsystems, and data-integrity concerns for this project. --> |
| **B** | `director2` | `operator2` | **<domain-lane-B>** — <!-- TODO(<PROJECT>): list the Pair-B domain modules, subsystems, external-API clients, and main orchestrator paths for this project. --> |

The angle-bracket lane slots stay unbound by ADR-009's explicit instruction
(adopter fill-ins, ADR-002).

Four seat names are a mailbox and review compatibility vocabulary, not a
staffing requirement. A task needs the seats its risk class actually calls for;
one director and one non-author operator is the normal working pair, and the
second pair is cold capacity.

**Shared seams** (modules touching both lanes): the owner is whoever's change
lane the edit falls in, with an `all` heads-up first per Rule #23.

The director/operator relationship is unchanged within each pair. The user is
principal, and Git remains the tiebreaker — first commit to land wins.

## 2. Mailbox addressing — point-to-point plus a broadcast target

Any seat may address any other seat directly (`<from>-to-<to>-<kind>.md`). The
pseudo-target **`all`** lets a seat announce to everyone without sending N
copies. `all` is a valid `to` only — never a `from`, and never a real cursor or
`seen/` file, so there is no `seen/all.txt`.

The live seat and kind registry is `scripts/protocol_mailbox.py`
(`SEATS` / `RECEIVING_SEATS` / `KNOWN_KINDS`). Read it rather than duplicating
the vocabulary into prose.

## 3. Work partitioning — Rule #23, lane ownership

- **Pair lanes.** Each pair's director owns its lane; its operator independently
  verifies. Disjoint by construction; shared seams handled below.
- **Tiebreaker.** Refresh scoped Git state before acting on a shared task; the
  first commit to land wins. Each seat works in its own linked worktree with a
  native index, so staging is isolated and commits serialize on Git's ref lock.
- **Lane discipline.** A seat does substantive work only in its lane.
  Cross-lane edits need an `all` heads-up first, or a direct dispatch-claim to
  the owning pair. Pathspec-scoped commits remain load-bearing.
- **Architectural decisions.** A lane-local ADR is owned by that lane's
  director. A cross-cutting ADR needs both directors' sign-off, or escalation to
  the user. This prevents two directors landing conflicting architecture.
- **Co-sign tiers.** The cross-director co-sign is tiered so an awareness
  heads-up does not serialize behind a full session. Classifier: *would the
  co-signer's own verification change which files or sites the implementation
  touches?*
  - **Tier A — implementation-scope-determining** (yes): the co-signing director
    runs an independent verification and lands a mailbox `verification-report`
    before dispatch. Fulfillable asynchronously; it just has to precede dispatch.
  - **Tier B — awareness-only** (no): a broadcast or direct heads-up with a
    48h proceed-if-no-objection default.

  When unsure which tier applies, treat it as Tier A.

## 4. Coordinator — on-demand policy

The `coordinator` is a cross-pair oversight role, **not a standing concurrent
seat**. Standing operation consumes the working seats' attention and duplicates
findings already queued; the value is the cross-pair view, not constant
presence.

- **Trigger.** Spawn on demand at a multi-pair-wrap boundary, when the user or a
  director wants a cross-pair audit.
- **Posture.** Read-only by default. Holds no mailbox cursor and owns no lane,
  so Rule #23 does not apply to it.
- **Output.** Land findings as a single findings commit or one mailbox event —
  not a stream of per-finding events.
- **Authority.** It is not a route-approval or convergence gate and does not
  author behavior-changing production work. Commits only under explicit user
  direction; push stays user-gated.
