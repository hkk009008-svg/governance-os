# Pipeline agent guide

This is the agent-neutral router for Pipeline. `ARCHITECTURE.md` describes the
current system, and executable code wins when prose drifts. Load only the
provider and task doctrine that applies.

Provider entrypoints:

- Claude Code: `CLAUDE.md`, then `docs/protocol/claude/` and `.claude/`.
- Codex: `docs/protocol/codex/continuation.md`, then `.agents/skills/` and
  `.codex/agents/`.
- AGY (Antigravity): `docs/protocol/agy/continuation.md`, then
  `.agents/skills/antigravity-harness/` and `.agy/agents/`.
- Cursor: `docs/protocol/cursor/continuation.md`, then `.cursor/rules/` and
  `docs/protocol/cursor/roles/`.
- Cross-provider work: `docs/protocol/threeway/`.
- Artifact ownership: `docs/protocol/protocol-assembly-map.md`.

## Codex applicability

Use the smallest applicable tier:

- `tier-0-conversational`: supplied context is enough; do not orient the repo.
- `tier-1-read-only`: inspect only evidence needed for the report.
- `tier-2-local-mutation`: perform scoped impact analysis and focused checks.
- `tier-3-governed-side-effect`: refresh live authority and external state for
  the exact governed action.

Codex starts as a readiness bridge. It adopts a live role or coordinator role
only when the user or parent explicitly assigns it. Parent-scoped helpers never
inherit that authority.

For tier 2, refresh the native worktree before changing it:

```bash
git status --short --branch
git log --oneline -5 -- <relevant-paths>
```

Run `python scripts/ci_smoke.py` from the active development environment when work changes governance/runtime
topology or relies on an `ARCHITECTURE.md` invariant.

## Project sources

| Need | Source |
|---|---|
| Purpose and quick start | `README.md` |
| Verified topology and smoke | `ARCHITECTURE.md` |
| User intent | `docs/PROGRAM-MANUAL.md` |
| Operations | `OPERATIONS.md` |
| Decision history | `DECISIONS.md` |
| Universal protocol | `docs/protocol/agents/` |
| Codex mechanics | `docs/protocol/codex/continuation.md` |
| Protocol entry skill | `.agents/skills/four-seat-protocol/SKILL.md` |
| Evidence-ledger bridge | `docs/protocol/codex/ledger-cli-adoption.md` |

## Engineering discipline

Before changing a symbol, use `rg` to find its definition, writes, callers,
imports, string references, and relevant siblings. Read those sites before
editing. Preserve unrelated user and peer work, compare the actual diff with
the requested scope, and stage explicit paths only.

Factual inventory claims cite the command and result that proves the scope.
Gate-controlling numbers come from a committed instrument and citable evidence.
Tests prove only what they execute; a green gate does not grant authority.

- Execute an accepted exact task without adding a brainstorming or planning
  cycle unless behavior is materially ambiguous.
- For a behavior change or bug fix, start with a failing behavior test when
  feasible; otherwise preserve characterization evidence or `test-infeasible`.
- Establish root cause before changing behavior after an unexpected failure.
- Run fresh, smallest-sufficient verification before claiming completion.
- A confirmed defect deferred from the current scope needs a strict xfail pin
  or a `test-infeasible` reason.
- Delegation is optional and owner-chosen. Never run concurrent implementers on
  shared files.

Pipeline does not depend on the Superpowers plugin. Historical
`docs/superpowers/` artifacts are inputs, not instructions, and skill presence
alone is not a trigger.

## Governed protocol

Use the executable seam that owns the claim:

- Autonomous Seat Outcome Contract: `scripts/codex_protocol_model.py`.
- Runtime identity, ownership lineage, risk profiles, and structural
  external-effect shape: `scripts/codex_protocol_model.py`.
- Formal request/report parsing and exact-range review:
  `scripts/compact_pair_loop.py`.
- Event construction, validation, and serialized publication:
  `scripts/mailbox_writer.py` through `coordination/bin/send-event`.
- Host task discovery, dispatch, and waiting:
  `docs/protocol/codex/continuation.md`.

When a seat, mailbox, route, handoff, wave, continuation, or protocol decision
is explicitly in scope, load `.agents/skills/four-seat-protocol/SKILL.md` and
the concrete role skill.

The following boundaries remain mandatory:

- Current committed route/event bodies and Git state outrank stale summaries.
- Transport ambiguity is reported; it is never converted into an empty queue.
- Push, merge, lock, cursor consumption, paid spend, provider launch, live-data
  mutation, and other external effects require separate exact authority.
- Structural protocol data, task dispatch, and helper assignment grant no
  external-effect authority.

Review depth follows risk:

- Ordinary reversible local work needs focused verification.
- Material behavior changes need non-author review of the exact range.
- Authority, security, executable composition, side-effect gates, and
  trust-granting schemas need distinct non-author, different-model actual-diff
  review plus explicit abuse-class analysis.
- External effects need live authorization for the executor, target, and scope.

When formal review is triggered, its committed request retains the complete
Compact Pair binding. An author cannot approve its own work.

Host task tools own discovery, dispatch, and waiting mechanics. Repository
doctrine must not prescribe a particular host API or ask the user to relay a
task that the active host can deliver.

## Target repositories

For evidence-ledger work, start in Pipeline and read
`docs/protocol/codex/ledger-cli-adoption.md` before entering the target repo.
Pipeline owns governance; the target repo owns product-local truth.

## Worktree hygiene

- Use the worktree's native Git index; do not create or share per-seat indexes.
- Refresh HEAD and scoped status before each write or gate decision.
- First landed work wins in a shared tree; refresh and narrow, do not recreate.
- Editing, staging, committing, pushing, merging, consuming events, locking,
  and spending are separate actions.

Optional ChatGPT Pro consultation is parent-only and advisory: follow .agents/skills/chatgpt-pro-consultation/SKILL.md; it grants no protocol or side-effect authority.
