# Pipeline agent guide

This is the always-loaded, agent-agnostic router for AI tools in this repo. It
keeps only rules needed before the task is known. Load task-specific doctrine
from the linked source when its trigger fires.

`ARCHITECTURE.md` is factual truth; this file is process guidance. Current code
wins when either document drifts. Fix a stale claim in the same scoped change
that exposes it.

Provider mechanics live in their own surfaces:

- Claude Code: `CLAUDE.md`, then `docs/protocol/claude/` and `.claude/`.
- Codex: `docs/protocol/codex/continuation.md`, then the triggered skill under
  `.agents/skills/` and role module under `.codex/agents/`.
- Antigravity and cross-provider work: `docs/protocol/threeway/`.
- Artifact ownership: `docs/protocol/protocol-assembly-map.md`.

For Claude Code, explicit user instructions outrank `CLAUDE.md`, which outranks
this universal guide. Other tools translate these principles into their native
mechanics without copying provider-specific ceremony.

## Codex mode and risk tier

Codex starts as a readiness bridge. It becomes `director`, `director2`,
`operator`, `operator2`, or coordinator only when the user or parent prompt
names that role or explicitly requests a protocol decision. A skill's presence
alone is not a trigger.

Choose the smallest applicable tier before loading tools or skills:

- `tier-0-conversational`: answer from the supplied context. No repo startup,
  mailbox, smoke, worktree, planning, or verification commands.
- `tier-1-read-only`: inspect only the evidence needed for the report. Do not
  invoke implementation workflow or live-seat checks without an explicit seat,
  mailbox, route, wave, handoff, or protocol-decision trigger.
- `tier-2-local-mutation`: make the ordinary code, test, config, or Markdown
  change with impact analysis, focused checks, and one fresh completion pass.
- `tier-3-governed-side-effect`: for live-seat decisions, shared protocol
  state, or external effects, apply the exact mailbox, capacity, independent
  verification, and user-authorization gates for that action.

Deterministic artifact evidence may be reused only when HEAD and relevant paths
are unchanged. Tier 3 always refreshes live bus/mailbox, cursor, lock, approval,
and external state. Tier 3 requires fresh signed-bus, mailbox/cursor, lock,
approval, and external-state checks; reuse never relaxes a triggered guard. Do
not launch another generic reviewer or repeat Lane V for the same unchanged
commit unless it asks a genuinely different, pre-stated question.

## Start only what the task requires

For tier 2 work, inspect scoped status/history and run the focused check that
matches the change:

```bash
env -u GIT_INDEX_FILE git status --short --branch
env -u GIT_INDEX_FILE git log --oneline -5 -- <relevant-paths>
```

Run `scripts/ci_smoke.py` and re-check `ARCHITECTURE.md` section 2 when the task
touches governance/runtime topology, depends on a documented invariant, or the
task's completion profile requires the project smoke. Tier 3 loads the
four-seat skill and follows its triggered startup. Tier 0 and ordinary tier 1
work pay none of this startup cost.

Read linked docs on demand, not as a session-start bundle. In particular,
`docs/PROGRAM-MANUAL.md` is pull-on-demand through
`docs/protocol/program-manual-guide.md`.

## Project sources

| Need | Source |
|---|---|
| Purpose and quick start | `README.md` |
| Verified topology and smoke | `ARCHITECTURE.md` |
| User intent and capability goals | `docs/PROGRAM-MANUAL.md` |
| Run, configure, troubleshoot | `OPERATIONS.md` |
| Decision history | `DECISIONS.md` |
| Universal protocol doctrine | `docs/protocol/agents/` |
| Codex continuation | `docs/protocol/codex/continuation.md` |
| Codex four-seat entrypoint | `.agents/skills/four-seat-protocol/SKILL.md` |
| Evidence-ledger bridge | `docs/protocol/codex/ledger-cli-adoption.md` |
| Daily pair loop | `RUNBOOK-DAILY.md` |
| Prompt templates | `docs/templates/agents/` |
| Rule provenance | `docs/PROTOCOL-RULES-LOG.md` |

Keep subsystem facts in `ARCHITECTURE.md`. Append decisions with rationale to
`DECISIONS.md`; never rewrite earlier decision entries.

## Universal implementation discipline

### Impact

Before changing a symbol, use `rg` to find its definition, writes, callers,
imports, string references, and relevant siblings. Read those sites before
editing. High-fanout changes require a stated caller and risk summary. For a
rename, re-run the search after editing and confirm no obsolete site remains.

Before handoff, compare the actual diff and changed paths with the requested
scope. Preserve unrelated user or peer work.

### Evidence and measurement

- **R-EVIDENCE:** A factual inventory claim must cite the command and result
  that proves that exact scope. Otherwise label it unverified.
- **R-MEASURE:** A number that controls a gate or recorded verdict comes from a
  committed instrument and a citable `logs/` artifact. Label ad-hoc runtime
  observations as estimates or runtime-unreproducible.
- Tests and gate scripts prove only what they execute. A wave gate is not a
  correctness verdict; cite the regression evidence or formal operator GO.

### Verification tiering

- Use the smallest sufficient verification profile.
- Do not launch a third same-question pass after two independent confirmations
  unless the new question is stated first.
- A confirmed defect deferred from the current session needs a strict xfail
  regression pin or a `test-infeasible` reason in the handoff.
- Never push production code before the required operator GO.

### Independence first

**R-INDEPENDENCE:** Before implementation, classify whether the change touches
an adversarial-surface: parseable/executable composition, authority or security
enforcement, side-effect gating, or trust-granting schema validation. If
triggered, capture an independent design-time enumeration of abuse cases, edge
cases, and coverage targets as enforced-and-tested acceptance criteria, then
have an independent reviewer verify the actual diff. This classification occurs
before implementation. R-VERIFY-TIER still
prevents redundant review. Non-adversarial, read-only, and hermetic work uses
the smallest sufficient profile. Full doctrine:
`docs/protocol/claude/independence-first.md`.

### Orchestration

Orchestrate when a plan has at least five independent tasks or at least 800
lines of expected change. A user-referenced plan requires plan-driven execution
and checkpoints, but does not force delegation when its work is tightly
coupled. Use fresh bounded implementers only for independently testable slices;
never run concurrent implementers on shared files. Keep a single tightly
coupled change in the main context. Details:
`docs/protocol/agents/orchestration.md`.

Use a subagent only when it adds independent signal or genuinely parallel
capacity. Give it the relevant rules, allowed paths, acceptance evidence,
forbidden effects, and `env -u GIT_INDEX_FILE` hygiene. Direct work needs no
recorded non-use decision.

**Capacity Split Default:** the single-pair fast path remains the default for
narrow or shared-file work; divisible or preplanned larger work defaults to
dual-pair routing only when it yields two independently reviewable deliverables.
If split, director owns Chunk A and operator verifies Chunk A; director2 owns
Chunk B and operator2 verifies Chunk B. Otherwise Pair B performs bounded
planning or preflight instead of idle standby. Pair B preflight packets use
`director-preflight` and `operator-preflight` packet types; coordinator owns
convergence.

### Repeated safety checks

- **R-BRIEF:** brief-pattern references are runtime claims when they cite
  canonical sites: verify the named symbol exists at the cited SHA and verify
  the cited SHA exhibits the named sub-pattern, including its full signature,
  scope, error handling, and guards.
- **R-PID:** A project-scoped HTTP resource takes `<pid>` explicitly; never
  recover it by scanning a global list. Check all sibling endpoints.
- **R-SKILL:** Load the matching project skill before authoring, reviewing, or
  debugging domain graph/pipeline code or a major external-API client.
- **Rule 12, grep the writes:** A declaration is not runtime evidence. Find and
  cite the production mutator/write site for each targeted field or key.
- **Rule 13, symmetric endpoints:** audit-completeness is not audit-disposition.
  Enumerate every sibling sharing the fence, flag, or state; use
  `mirror / defer / document / exempt` and state the disposition for each sibling.

## Four-seat protocol trigger

Do not run four-seat startup for ordinary feature or documentation work. When
a seat, mailbox, route, wave, handoff, continuation, or protocol decision is
explicitly in scope, load `.agents/skills/four-seat-protocol/SKILL.md` and the
concrete seat skill. For evidence-ledger work, start in Pipeline and load
`docs/protocol/codex/ledger-cli-adoption.md` before entering the target repo.

Canonical Compact Pair Invariant: scripts/codex_protocol_model.py

Mailbox decisions remain body-first: read relevant mailbox bodies before acting;
live seat cursors are intentional per-seat state, and the coordinator has no cursor.
The verifying operator must be a non-author and alone issues GO/NITS/FAIL from repository evidence.
The coordinator may route and reconcile but not author behavior-changing production fixes.
Push, merge, paid spend, and every other side effect are separately gated and require explicit authority.

The live authority block and Codex commands are owned by
`docs/protocol/codex/continuation.md`; the umbrella and concrete seat skills add
only their local consequences. The executable model owns lifecycle, capacity,
emergency, disagreement, blocked-wave, review-result, and shared
side-effect-executor details. Do not copy those bodies into this router.

## Hot shared tree

- Refresh `git log --oneline -3` and scoped status immediately before every
  write or gate decision; a peer may have moved HEAD.
- If an unrelated file is dirty, preserve it. Never run broad auto-fix or broad
  staging over peer WIP. Use `env -u GIT_INDEX_FILE` and explicit pathspecs.
- First landed commit wins on shared work. After a refresh, narrow or stand
  down instead of recreating the same change.
- Local edit, stage, commit, push, merge, mailbox consume, lock, and spend are
  distinct actions. Do not infer authority for one from authority for another.

## Provider coordination

`CLAUDE.md` may add Claude-only mechanics but must not replace the universal
authority boundaries here. Codex adapts those functions to native tools through
`docs/protocol/codex/continuation.md`; it does not transplant Claude-only tool
syntax. Cross-provider ownership and synchronization rules live in
`docs/protocol/protocol-assembly-map.md`.

Optional ChatGPT Pro consultation is parent-only and advisory: follow .agents/skills/chatgpt-pro-consultation/SKILL.md; it grants no protocol or side-effect authority.
