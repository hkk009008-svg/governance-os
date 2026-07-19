# Pipeline agent guide

This is the agent-neutral router for Pipeline. `ARCHITECTURE.md` is factual
truth and current code wins when prose drifts. Load task-specific doctrine only
when its trigger fires.

Provider mechanics live in their adapters:

- Claude Code: `CLAUDE.md`, then `docs/protocol/claude/` and `.claude/`.
- Codex: `docs/protocol/codex/continuation.md`, then `.agents/skills/` and
  `.codex/agents/`.
- Cross-provider work: `docs/protocol/threeway/`.
- Artifact ownership: `docs/protocol/protocol-assembly-map.md`.

## Codex applicability

Use the smallest applicable tier:

- `tier-0-conversational`: supplied context is enough; do not orient the repo.
- `tier-1-read-only`: inspect only evidence needed for the report.
- `tier-2-local-mutation`: perform scoped impact analysis and focused checks.
- `tier-3-governed-side-effect`: refresh live authority, mailbox, locks, and
  external state for the exact governed action.

Codex starts as a readiness bridge. It becomes `director`, `director2`,
`operator`, `operator2`, or coordinator only when the user or parent explicitly
names the role or requests a protocol decision.

For tier 2 work:

```bash
env -u GIT_INDEX_FILE git status --short --branch
env -u GIT_INDEX_FILE git log --oneline -5 -- <relevant-paths>
```

Run `env -u GIT_INDEX_FILE .venv/bin/python scripts/ci_smoke.py` when the task
touches governance/runtime topology or relies on an `ARCHITECTURE.md`
invariant.

## Project sources

| Need | Source |
|---|---|
| Purpose and quick start | `README.md` |
| Verified topology and smoke | `ARCHITECTURE.md` |
| User intent | `docs/PROGRAM-MANUAL.md` |
| Operations | `OPERATIONS.md` |
| Decision history | `DECISIONS.md` |
| Universal protocol | `docs/protocol/agents/` |
| Codex continuation | `docs/protocol/codex/continuation.md` |
| Four-seat entrypoint | `.agents/skills/four-seat-protocol/SKILL.md` |
| Evidence-ledger bridge | `docs/protocol/codex/ledger-cli-adoption.md` |

## Implementation discipline

Before changing a symbol, use `rg` to find its definition, writes, callers,
imports, string references, and relevant siblings. Read those sites before
editing. Compare the actual diff and changed paths with the requested scope;
preserve unrelated user or peer work.

Factual inventory claims cite the command and result that proves the exact
scope. Gate-controlling numbers come from a committed instrument and citable
`logs/` evidence. Tests prove only what they execute, and a gate script never
substitutes for an Operator verdict.

Use the smallest sufficient verification profile. Do not repeat the same review
question over an unchanged commit. A confirmed defect intentionally deferred
needs a strict xfail pin or a `test-infeasible` reason.

## Proportional independence

For parseable/executable composition, authority or security enforcement,
side-effect gating, or trust-granting schema validation, the owner explicitly
assesses plausible abuse classes and preserves material independent findings.
The owner and actual-diff Operator choose proportional review depth. Early
independent review is encouraged when it adds signal; it is advisory and is not
a universal pre-implementation CLEAR gate. Behavior-changing acceptance still
requires distinct-seat, different-model, non-author Operator review of the
actual commit or range.

## Autonomous governed work

Autonomous Seat Outcome Contract: scripts/codex_protocol_model.py
Own the routed outcome and choose the method. Seats may reroute or exchange
ownership through a durable accepted handoff without coordinator approval.
Preflight is advisory. Preserve material findings, require non-author Operator
GO for behavior-changing work with a distinct Operator seat and different
model, bind autonomous ownership to an immutable parent/revision, preserve
immutable finding refs, and keep external effects separately user-authorized
for the exact effect/executor/target/scope. An Operator cannot verify anything
it authored. Use the fixed mailbox writer for durable ownership and review
events.

Delegation is an owner-chosen capacity tool, not a task-count or line-count
mandate. Use it when it adds independent signal or useful capacity. Never run
concurrent implementers on shared files.

## Four-seat trigger and mechanics

When a seat, mailbox, route, wave, handoff, continuation, or protocol decision
is explicitly in scope, load `.agents/skills/four-seat-protocol/SKILL.md` and
the concrete seat skill. Read relevant mailbox bodies before decisions; live
seat cursors are per-seat state and coordinator has no cursor. Only the
concrete seat consumes its cursor. Ordinary Git and pytest use
`env -u GIT_INDEX_FILE`.

Canonical Compact Pair Invariant: scripts/codex_protocol_model.py

The fixed writers under `coordination/bin/` own mailbox publication. A
committed verify-request binds the actual reviewed range, author identity,
assigned non-author Operator, and finding refs; only the assigned Operator may
issue GO/NITS/FAIL. Coordinator observes and facilitates but does not author
behavior-changing production fixes.

Push, merge, lock action, cursor consumption, paid spend, provider launch, and
other external effects are distinct actions requiring their own explicit
authority. Structural protocol data never grants that authority.

For evidence-ledger work, start in Pipeline, read
`docs/protocol/codex/ledger-cli-adoption.md`, run
`scripts/ledger_start_guard.py --seat <seat> --wave 2`, and then read the target
repo instructions. Pipeline remains the governance kernel; evidence-ledger owns
product-local truth.

Fast resume is optional only for a named seat or coordinator continuing an
unchanged already-routed local implementation or review by passing its exact
current route ref. Fresh, transplanted, ambiguous, or external-effect work uses
ordinary fresh orientation. The classifications are `FAST RESUME: PASS`,
`FULL ORIENTATION REQUIRED`, and `START GUARD: FAIL`; full orientation is an
advisory fallback to ordinary startup, not `BLOCKED`, and fast resume grants no
external-effect authority.

## Hot shared tree

- Refresh `env -u GIT_INDEX_FILE git log --oneline -3` and scoped status before
  every write or gate decision.
- Preserve unrelated dirty files and stage explicit pathspecs only.
- First landed commit wins on shared work; refresh and narrow instead of
  recreating it.
- Local edit, stage, commit, push, merge, mailbox consume, lock, and spend are
  separate authorities.

Optional ChatGPT Pro consultation is parent-only and advisory: follow .agents/skills/chatgpt-pro-consultation/SKILL.md; it grants no protocol or side-effect authority.
