# Codex Check-Ceremony Reduction Design

## Goal

Reduce repeated and visible safety-check ceremony in ordinary Codex work while
preserving the controls that protect live-seat authority, shared Git state,
verification integrity, and user-gated side effects.

## Scope

This slice changes the Codex-facing execution router and hook lifecycle only:

- `.codex/hooks.json`
- `.codex/hooks/session-smoke.sh`
- `.codex/hooks/update-state.sh`
- `.claude/hooks/update-state.sh` (age-only lock deletion only)
- `scripts/codex_protocol_model.py`
- `AGENTS.md`
- `docs/protocol/codex/continuation.md`
- focused unit tests for the hook and prompt contracts

It does not disable the global Superpowers plugin, alter sandbox approvals,
change live-seat authority, weaken operator GO, or execute the existing
optional-agent consolidation plan.

## Design

### 1. Risk-tier execution router

Add one canonical risk-tier contract to `scripts/codex_protocol_model.py` and
mirror it into `AGENTS.md` and the Codex continuation adapter.

The tiers are:

1. **Tier 0, conversational:** explanations, rewrites, and other self-contained
   answers. No repo orientation, implementation skills, mailbox checks, smoke,
   worktree, or verification commands.
2. **Tier 1, read-only:** repository inspection and evidence-backed reporting.
   Use the smallest scoped read commands. Do not load implementation skills or
   run live-seat checks unless the prompt explicitly names a seat, mailbox,
   route, wave, handoff, or protocol decision.
3. **Tier 2, local mutation:** ordinary code, test, config, or documentation
   edits. Use impact analysis, the task-relevant implementation discipline,
   focused tests, and one fresh completion verification pass.
4. **Tier 3, governed side effect:** live-seat decisions, shared protocol state,
   push, merge, locks, cursor consumption, spend, and external writes. Apply the
   full mailbox, capacity, independent-verification, and user-authorization
   gates relevant to the exact action.

The router is an applicability rule, not a relaxation of a triggered guard.
Moving from one tier to another requires a real scope change, not agent
preference. Deterministic artifact evidence produced against an unchanged HEAD
and unchanged relevant paths may be reused in the same task. Tier 3 still
requires fresh signed-bus, mailbox/cursor, lock, approval, and external-state
checks; reuse never relaxes a triggered guard.

### 2. Quiet no-op Codex hooks

Remove the always-visible status messages from the Codex PreToolUse and
PostToolUse registrations. The guard scripts remain installed and keep their
current fail-open/fail-closed behavior. They emit output only when they block,
repair, fail, or discover a state that needs attention.

The SessionStart hook remains visible on a real smoke failure. A successful
smoke run is silent.

### 3. Content-addressed session-smoke cache

Cache the session-smoke verdict under `.codex/hooks/` using a key derived from:

- current `HEAD`;
- the `main` and `origin/main` commit refs used by freshness checks;
- the complete staged and unstaged Git-visible diff; and
- every untracked, non-ignored file path and its content.

The cache is reused across resume, clear, and compaction only when the key is
identical and the cached verdict is a pass. Failures are never cached as a pass.
The hook remains fail-open and retains its execution timeout.

Smoke executes with `GIT_INDEX_FILE` removed, matching the environment used to
compute the key. Untracked symlinks contribute their link target rather than
the contents of an external target. This avoids false cache hits from broad
placeholder, coordination, signed-bus, mailbox, and documentation gates.
If the default index contains any skip-worktree or assume-unchanged flag, key
generation deliberately fails open into a fresh, non-cached smoke run because
Git diffs may omit working-tree bytes hidden by those flags.

### 4. Readiness-bridge fast path in state refresh

Preserve all existing live-seat behavior. For sessions with neither a concrete
seat marker nor a per-seat `GIT_INDEX_FILE`, check the current HEAD first. When
HEAD is unchanged, `STATE.md` exists, and the default-index scan marker is
fresh, exit before heartbeat, per-seat index sync, skip-worktree repair, and
full state regeneration.

For live seats, keep heartbeat and index maintenance. Throttle the expensive
skip-worktree scan with a timestamp marker scoped to the active default or
per-seat index rather than running it after every tool call. A newly observed
HEAD, a distinct index, or an expired marker runs the scan.

Remove the unconditional stale `.git/index.lock` deletion from PostToolUse.
Lock recovery belongs to the command that observes an actual lock failure;
file age alone is not proof that a lock is abandoned.

### 5. Verification deduplication

Codify one verification chain for an unchanged artifact:

- Tier 2: focused tests plus one completion verification pass.
- Tier 3 production/protocol work: implementer evidence followed by the formal
  operator Lane V verdict when required, then GO before push.
- Do not launch another generic reviewer or repeat Lane V for the same unchanged
  commit unless it asks a genuinely different, pre-stated question.

This composes with R-VERIFY-TIER and does not weaken mutation testing,
strict-xfail pins, or formal operator responsibility.

## Sibling audit

`.claude/hooks/update-state.sh` is the behavioral sibling of the Codex state
hook. Its index synchronization and heartbeat guarantees remain unchanged.
The unsafe age-only `.git/index.lock` deletion is provider-neutral, so it is
removed from both active hook twins. Other state-refresh optimizations remain
Codex-only because this slice targets Codex-visible ceremony and readiness.

Disposition:

- Git-index synchronization: preserve in both providers.
- Heartbeat behavior: preserve for concrete seats in both providers.
- Codex readiness fast path: Codex-only because readiness bridge is a Codex
  harness mode.
- Skip-worktree throttling: Codex-only; Claude keeps its existing scan behavior.
- Stale-lock removal: mirror in both providers because file age does not prove
  that a Git lock is abandoned.

## Testing

Add focused tests that prove:

- Codex hook registration has no success-path PreToolUse/PostToolUse status
  messages while retaining all three hook commands.
- session smoke runs on a new content key, stays silent and skips execution on
  an identical passing key, and reruns when a smoke-relevant dirty file changes.
- session smoke bypasses cache reuse for skip-worktree and assume-unchanged
  tracked files, and never caches a failing verdict.
- readiness bridge skips expensive maintenance when HEAD is unchanged.
- a live seat still stamps heartbeat and synchronizes a clean stale seat index.
- skip-worktree checking is throttled per index but reruns after its marker
  expires, HEAD changes, or another seat index becomes active.
- the model, `AGENTS.md`, and continuation adapter share the same four-tier
  contract and verification-deduplication language.

Run the focused tests, protocol prompt-sync tests, coordination-tooling tests,
and `scripts/ci_smoke.py` before any completion claim.

## Non-goals

- No push, merge, mailbox consume, lock action, route mutation, or external
  write.
- No global `~/.codex/config.toml` change.
- No edit to plugin cache files.
- No weakening of sandbox permissions or user-gated side effects.
- No automatic agent dispatch for this tightly coupled shared-file slice.
- No implementation of the separate Codex optional-agent consolidation plan.
