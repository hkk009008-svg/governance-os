# Ledger CLI Four-Seat Adoption Design

Date: 2026-07-07
Status: Approved design direction; awaiting written-spec review

## Purpose

Adopt the repo's four-seat protocol for CLI work as one coordinated unit across
two repos:

- `/Users/hyungkoookkim/Pipeline` remains the generic governance kernel and
  Codex protocol source of truth.
- `/Users/hyungkoookkim/evidence-ledger` is the bound product repo where ledger
  work happens.

The adoption must let Codex study and mirror Claude Code's useful behavior
without copying Claude-only mechanics. The result should give Codex a clear CLI
launch and handoff path for ledger work while preserving the current authority
boundaries: readiness bridge by default, named seats only on explicit prompt,
mailbox-first protocol decisions, and user-gated side effects.

## Current Evidence

Verified via:

```text
$ env -u GIT_INDEX_FILE .venv/bin/python scripts/continuation_readiness.py
role: readiness bridge; no seat claim, cursor consumption, mailbox send, or inventory edit
core agent modules: lane-v-verifier.toml, money-gate-reviewer.toml, protocol-coordinator.toml, protocol-director.toml, protocol-operator.toml, readiness-bridge.toml
director  unread=0 cursor=0
director2 unread=0 cursor=0
operator  unread=0 cursor=0
operator2 unread=0 cursor=0
coordinator unread=0 cursor=0
coordinator2 unread=0 cursor=0
```

```text
$ env -u GIT_INDEX_FILE git log --oneline -5
582d402 docs: director-session handoff + seat-index-maintenance sharp edge
ba6af6a coordination: operator session wrap 2026-07-07 - cross-repo trace + fleet state
45477ff coordination: operator findings - sync cold-start wedge + send-event/gitignore breakage
0432a02 chore: gitignore .skip-worktree-cleared.log twins (completes c2e16d5)
c2e16d5 chore: gitignore .claude/hooks/.last-state-head (twin of .codex entry)
```

```text
$ rg --files tests | rg 'codex|protocol|artifact|smoke|continuation|threeway_mechanism'
tests/unit/test_imports_smoke.py
tests/unit/test_protocol_mailbox.py
```

The old focused selectors documented in `docs/protocol/codex/continuation.md`
include `tests/unit/test_codex_protocol_model.py`, but that path is absent in
this snapshot. The implementation plan must either create current regression
coverage for the new bridge or update stale verification guidance as part of
the same change.

## Design Summary

Use a kernel-plus-bridge model.

Pipeline keeps the four-seat rules and executable Codex model. Evidence-ledger
does not get a blind copy of Pipeline's protocol files. Instead, Pipeline gets a
small ledger CLI adoption bridge that tells Codex how to enter ledger work:

1. Start in Pipeline as readiness bridge unless the prompt names a seat or
   coordinator.
2. Read Pipeline protocol state first: readiness report, git log, mailbox
   bodies when a protocol decision is being made.
3. When working in `/Users/hyungkoookkim/evidence-ledger`, read that repo's own
   `CLAUDE.md`, run its current orientation checks, and treat its repo doctrine
   as product-local truth.
4. Apply Pipeline's Codex seat mechanics as the operating harness only:
   concrete seat identity, behavior-source mapping, mailbox-first decisions,
   bounded subagents, pair loop, coordinator limits, and user-gated side
   effects.
5. Prefix cross-repo git and pytest commands with `env -u GIT_INDEX_FILE` so a
   Pipeline seat index never leaks into the ledger repo.

This keeps the governance system centralized while making the ledger working
path explicit enough for Codex CLI sessions to use repeatedly.

## Components

### Pipeline Codex Kernel

Existing source surfaces remain authoritative:

- `scripts/codex_protocol_model.py`
- `docs/protocol/codex/continuation.md`
- `.agents/skills/four-seat-protocol/SKILL.md`
- `.codex/agents/*.toml`
- `.codex/hooks.json`
- `scripts/continuation_readiness.py`
- `.agents/skills/four-seat-protocol/scripts/seat_status.py`

These surfaces should gain the smallest necessary references to ledger CLI
adoption. They should not become evidence-ledger product documentation.

### Ledger CLI Bridge

Add a narrow Pipeline doc for evidence-ledger CLI adoption. It should answer:

- how Codex starts from Pipeline before touching ledger;
- which ledger-local files must be read before ledger edits;
- which commands are safe across repo boundaries;
- how named seats should launch or resume;
- what a handoff must record when the active work is in evidence-ledger;
- which side effects remain user-gated.

The bridge must avoid ambiguous authority. A Pipeline readiness bridge may
inspect and report; a named Pipeline live seat may operate only within the
explicit route; evidence-ledger product changes still follow evidence-ledger's
own repo rules.

### Claude Behavior Mapping

Claude Code behavior to mirror in Codex:

- `AskUserQuestion` maps to concise user-gated questions for policy choices,
  reversible-with-effort choices, and side effects.
- Background verification maps to Codex long-running command sessions, but the
  final claim still requires reading the command result.
- `Agent` and `Workflow` map to Codex role agents and bounded subagents. Codex
  does not import Claude's workflow engine; it mirrors the authority rules.
- Claude's git sharp edges map directly to `env -u GIT_INDEX_FILE` for ordinary
  git and pytest, especially when changing directories into evidence-ledger.
- Claude's template discipline maps to Codex parent prompts that include only
  the needed rule IDs, allowed paths, acceptance evidence, forbidden side
  effects, and git hygiene.

## Runtime Flow

### Readiness Bridge

1. Run Pipeline readiness:
   `env -u GIT_INDEX_FILE .venv/bin/python scripts/continuation_readiness.py`
2. Run:
   `env -u GIT_INDEX_FILE git log --oneline -5`
3. Report current protocol state and blockers only.
4. Do not consume cursors, send mailbox events, claim locks, push, spend, or
   author product changes.

### Named Live Seat

1. Locate the newest same-seat Pipeline handoff for the concrete role.
2. Run the Pipeline seat status command for the concrete seat.
3. Read relevant mailbox bodies before protocol decisions.
4. If ledger work is routed, enter evidence-ledger with `env -u GIT_INDEX_FILE`
   on all git and pytest commands.
5. Read evidence-ledger's own orientation files and current git state before
   editing.
6. Produce the normal seat artifact: brief, implementation, verify-request,
   verification-report, or handoff.

### Coordinator

1. Locate the newest Pipeline coordinator handoff.
2. Run coordinator status, git log, gate, and smoke from Pipeline.
3. Reconcile ledger work from durable evidence only: commits, handoffs,
   mailbox bodies, logs, and operator reports.
4. Route at most one consolidated coordinator event when routing is warranted.
5. Do not author behavior-changing product fixes in evidence-ledger.

## Data And State

Pipeline owns governance state:

- Codex runtime model
- role-agent prompts
- mailbox protocol
- handoff conventions
- coordinator and live-seat rules
- side-effect gates

Evidence-ledger owns product state:

- ledger code and tests
- product repo docs
- product handoffs if that repo requires them
- product-specific verification commands
- product-specific release or push decisions

Cross-repo handoffs must include both repo heads when work spans both repos,
because a Pipeline commit alone does not prove evidence-ledger state and an
evidence-ledger commit alone does not update the governance kernel.

## Error Handling

- If evidence-ledger is missing, inaccessible, or dirty in a way that affects
  the route, stop and report the blocker with `env -u GIT_INDEX_FILE git status
  --short` output from the ledger repo.
- If Pipeline and evidence-ledger doctrine conflict, user instructions win,
  then the product repo controls product behavior while Pipeline controls
  Codex seat mechanics.
- If a documented verification selector is stale, update the verification
  guidance or create current regression coverage in the same implementation
  slice that exposes the drift.
- If a seat-local index contaminates cross-repo git state, reset the command
  shape first: use `env -u GIT_INDEX_FILE` and re-run the status from the
  target repo before drawing conclusions.
- If a coordinator route would require production changes, hand it to the
  proper live seat instead of fixing directly.

## Testing And Verification

The implementation should include focused checks for:

- the ledger CLI bridge is present in the intended protocol doc map;
- Codex readiness output or model text advertises the ledger bridge without
  changing default readiness-bridge authority;
- role-agent prompts preserve concrete seat identity and cross-repo
  `env -u GIT_INDEX_FILE` hygiene;
- stale test-selector guidance is removed or replaced with current tests;
- smoke remains green.

Baseline verification already run for this design:

```text
$ env -u GIT_INDEX_FILE .venv/bin/python scripts/ci_smoke.py
PROJECT SMOKE - governance-OS runtime invariants ... OK
CEREMONY CHECK ... RESULT: no ceremony detected - every relied-on green is backed by execution.
PLACEHOLDER CHECK - PASS (no unallowlisted tokens).
GO-SCHEMA CHECK - PASS (0 GO report(s) validated; zero violations).
ARCH-FRESHNESS CHECK - ARCHITECTURE.md not in changeset; gate inert (exit 0).
OK
```

The smoke command also reported existing stale commit-SHA warnings. Those
warnings are not introduced by this design spec, but implementation should avoid
adding new stale claim text.

## Out Of Scope

- No direct evidence-ledger code or docs mutation in the design-spec step.
- No push to any remote.
- No mailbox cursor consumption.
- No coordinator route emission.
- No copy of the whole Pipeline protocol tree into evidence-ledger.
- No claim that a gate script substitutes for operator GO.

## Acceptance Criteria

- A reviewer can read one Pipeline spec and understand how Codex CLI should work
  on evidence-ledger as a four-seat unit.
- The design keeps Pipeline as kernel and evidence-ledger as product target.
- The design preserves named-seat authority, coordinator limits, pair-loop
  closure, and user-gated side effects.
- The design identifies the current stale verification-selector issue so the
  implementation plan can fix it deliberately.
- The next step is a written implementation plan, not immediate protocol edits.
