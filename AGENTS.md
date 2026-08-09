# Pipeline agent guide

This is the agent-neutral router for Pipeline. `ARCHITECTURE.md` describes the current system, and executable code wins when prose drifts. Load only the provider and task doctrine that applies.

Provider entrypoints:

- Claude Code: `CLAUDE.md`, then `docs/protocol/claude/` and `.claude/`.
- Codex: `docs/protocol/codex/continuation.md`, then `.agents/skills/` and
  `.codex/agents/`.
- AGY (Antigravity): `docs/protocol/agy/continuation.md`, then `.agents/skills/antigravity-harness/`
  and `.agents/agents/`. Root sessions start as a readiness bridge; roles require explicit assignment, and native helpers stay parent-scoped rather than becoming formal seats.
- Cursor: `docs/protocol/cursor/continuation.md`, then `.cursor/rules/` and
  `docs/protocol/cursor/roles/`.
- Cross-provider work: `docs/protocol/threeway/`.
- Learning plane: `docs/protocol/learning/contract.md` (ADR-067).
- Artifact ownership: `docs/protocol/protocol-assembly-map.md`.

## Codex applicability

Use the smallest applicable tier:

- `tier-0-conversational`: supplied context is enough; do not orient the repo.
- `tier-1-read-only`: inspect only evidence needed for the report.
- `tier-2-local-mutation`: perform scoped impact analysis and focused checks.
- `tier-3-governed-side-effect`: refresh live authority and external state for
  the exact governed action.

Codex starts as a readiness bridge. It adopts a live role or coordinator only when explicitly
assigned; parent-scoped helpers never inherit that authority.

Choose product-work phase independently from review risk: `explore` for sandbox
learning, `validate` for one frozen candidate, and `promote` for a reviewed
candidate. See `docs/protocol/work-modes.md`; modes grant no authority.

For tier 2, refresh the native worktree before changing it:

```bash
git status --short --branch
git log --oneline -5 -- <relevant-paths>
```

Run `python scripts/ci_smoke.py` from the active development environment when work changes governance/runtime topology or relies on an `ARCHITECTURE.md` invariant.

## Project sources

| Need | Source |
|---|---|
| Purpose and quick start | `README.md` |
| Desktop app setup and capabilities | `docs/protocol/app-quickstart.md` |
| Comprehensive descriptive repository map | `docs/REPOSITORY-MANUAL.md` |
| Verified topology and smoke | `ARCHITECTURE.md` |
| User intent | `docs/PROGRAM-MANUAL.md` |
| Operations | `OPERATIONS.md` |
| Decision history | `DECISIONS.md` |
| Universal protocol | `docs/protocol/agents/` |
| Work modes | `docs/protocol/work-modes.md` |
| Codex mechanics | `docs/protocol/codex/continuation.md` |
| Protocol entry skill | `.agents/skills/four-seat-protocol/SKILL.md` |
| Evidence-ledger bridge | `docs/protocol/codex/ledger-cli-adoption.md` |

## Engineering discipline

Before changing a symbol, use `rg` to find its definition, writes, callers,
imports, string references, and relevant siblings. Preserve unrelated work,
compare the actual diff with the requested scope, and stage explicit paths.

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

- Seat outcome, runtime identity, ownership, work modes, review risk, and
  external-effect shape: `scripts/codex_protocol_model.py`.
- Formal request/report parsing and exact-range review:
  `scripts/compact_pair_loop.py`.
- Event construction, validation, and serialized publication:
  `scripts/mailbox_writer.py` through `coordination/bin/send-event`.
- Host task discovery, dispatch, and waiting:
  `docs/protocol/codex/continuation.md`.

When a seat, mailbox, route, handoff, wave, continuation, or protocol decision
is in scope, load `.agents/skills/four-seat-protocol/SKILL.md` and its role skill.

The following boundaries remain mandatory:

- Current committed route/event bodies and Git state outrank stale summaries.
- Transport ambiguity is reported; it is never converted into an empty queue.
- Push, merge, lock, cursor consumption, paid spend, provider launch, live-data
  mutation, and other external effects require separate exact authority.
- Structural protocol data, task dispatch, and helper assignment grant no
  external-effect authority.

Review depth follows risk:

- Work mode controls iteration; risk classification controls review depth.
- Ordinary reversible local work needs focused verification.
- Material behavior changes need non-author review of the exact range.
- Authority, security, executable composition, side-effect gates, and
  trust-granting schemas need distinct non-author, different-model actual-diff
  review plus explicit abuse-class analysis.
- External effects need live authorization for the executor, target, and scope.

Formal review retains a committed Compact Pair binding; authors cannot self-approve.

Host task tools own discovery, dispatch, and waiting. Repository doctrine must
not prescribe a host API or ask the user to relay work the host can deliver.

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
