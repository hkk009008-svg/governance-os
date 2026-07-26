# Coordination Directory

Inter-session coordination scaffold for the director-operator four-seat agent
protocol. See [CLAUDE.md](../CLAUDE.md) / [AGENTS.md](../AGENTS.md) `# Director-Operator Concurrent Operation`
for the full discipline (Rules #7–#23).

## Layout

- `mailbox/sent/` — Authoritative inter-session events. Each event is a markdown
  file; the v6.0 envelope is an H1 (`# <From> → <To>: <subject>`) followed by a
  `**When:** <ISO-UTC> · **From:** <seat>` line whose timestamp must match the
  filename (linted). Pre-v6.0 events used YAML frontmatter (`from`, `to`,
  `kind`, …) and are grandfathered. New events must go through
  `bin/send-event`; raw event writes bypass publication validation and are not
  supported.
- `mailbox/seen/<seat>.txt` — Compatibility read state for the four concrete
  pair seats. Coordinators are cursorless. Historical ISO timestamps and
  migrated scalar sequences are accepted; malformed state is unavailable or
  fatal, never silently zero unread.
- `bin/send-event <from> <to> <kind> <subject…>` (body on stdin) — constructs
  one canonical candidate, validates its envelope and kind-specific structure,
  finalizes it under the shared writer fence, and stages only its explicit
  path. It never commits. A validation or staging failure is reported rather
  than bypassed with a direct write.
- `bin/consume-events <role> [--to <ts>]` — advances `seen/<role>.txt` to the
  newest event addressed to the role (or the explicit target), refusing
  regressions and nonexistent targets, and STAGES the cursor file. **Cursor
  folding (v6.0):** the staged advance rides the seat's next substantive
  commit; standalone cursor-only commits are deprecated (idle-consume exempt).
  A commit whose **entire** changeset is `seen/*.txt` (no `sent/` event, no
  code/doc) is a standalone cursor-only commit; `check_coordination.py --git-root <repo>`
  ADVISORY-flags these (lever #5, capacity audit `wf_6be2ee18-f4b`). Intentional
  idle-consume advances are exempt — prefix the subject `coord(cursor):` to signal it.
  **ACKs:** an `acknowledgement` event that carries substantive body (role
  resolution, retraction, findings) stays a `sent/` event file; a bare "received"
  ACK that adds nothing beyond the cursor should be a cursor advance only.
- `mailbox/kinds.txt` — canonical mailbox kind vocabulary, one kind per line.
  `bin/send-event` and `scripts/check_coordination.py` load this registry through
  `scripts/protocol_mailbox.py` (`wc -l coordination/mailbox/kinds.txt` → 25,
  2026-06-18).
- `scripts/check_coordination.py` (repo root) — lints all of the above (cursor
  parseable/non-future/non-orphan, filename convention, envelope, registered
  kind, unread report). Wired into `scripts/ci_smoke.py`: FATAL hard-fails
  locally, warns in CI; ADVISORY warns; INFO silent.
- `mailbox/archive/` — Old events moved out of `sent/` for log hygiene (manual
  move by operator).
- `presence/<seat>-heartbeat.ts` — legacy/provider-specific liveness hint. Codex
  does not write repository heartbeats; host task/thread activity is its
  liveness source. A heartbeat never grants authority.
- `presence/director.md`, `presence/operator.md` — (v5.7 Rule #19, narrowed by
  v6.0 Tier 2) per-seat **agent-owned intent**: flat `key: value` (`seat`,
  `status`, `current_task`, …). The hook NEVER touches these anymore (the
  pre-split hook sed livelocked the seat's own Write-tool edits and let
  hook-stamped `updated:` mask stale prose). Gitignored + per-clone.
  Transition: a session predating the split has no heartbeat file — fall back
  to its .md `updated:` until the first heartbeat appears.

## Readiness bridge

Use `python scripts/status.py snapshot` for one compact non-seat orientation.
`scripts/continuation_readiness.py` is a compatibility wrapper around that same
snapshot. It reports current Git, authoritative unread transport, the current
request or blocker, and the lawful next action without claiming a role or
mutating state.

Use `python scripts/mailbox_monitor.py --once` for an active communication
snapshot, or `python scripts/mailbox_monitor.py --watch --interval 5` while a
bridge/coordinator needs to notice mailbox or heartbeat changes. The monitor is
read-only: it reports unread counts, latest unread events, coordinator broadcast
receipt splits, and heartbeat freshness, but it never consumes cursors, sends
mailbox events, claims live-seat authority, or proves assigned work complete.

For an explicitly assigned Codex pair role, use
`python scripts/status.py snapshot <seat>` and read the actionable event bodies.
Cursor consumption is a separate action; run
`coordination/bin/consume-events <seat>` only when that role is authorized to
advance its own read state. Coordinator is unpinned: read relevant coordinator
and all-scope bodies, but never run `consume-events coordinator`.

## Codex transplant

Codex-native continuation details live in
`docs/protocol/codex/continuation.md`. The repo also provides:

- `.agents/skills/four-seat-protocol/SKILL.md` — reusable Codex workflow for
  readiness bridge and explicit seat continuation.
- `.codex/agents/*.toml` — explicit-use Codex custom agents for
  `readiness-bridge`, `protocol-director`, `protocol-operator`,
  `protocol-coordinator`, `lane-v-verifier`, and `money-gate-reviewer`.
- No project Codex hook registry — Codex has no repository lifecycle hook or
  persistent-index dependency.

For a local Codex seat launch, give each seat its own model and speed in
`~/.codex/pipeline-seat-launcher.toml`:

```toml
[seats.director]
model = "gpt-5.6-sol"
service_tier = "default"

[seats.director2]
model = "gpt-5.6-sol"
service_tier = "fast"

[seats.operator]
model = "gpt-5.6-sol"
service_tier = "default"

[seats.operator2]
model = "gpt-5.6-sol"
service_tier = "default"

[seats.coordinator]
model = "gpt-5.6-sol"
service_tier = "default"
```

Then launch only the selected seat:

```bash
coordination/bin/codex-seat director
coordination/bin/codex-seat director2
```

Each table is independent. Changing one table does not change another seat.
`service_tier` accepts `fast` or `default`. Arguments after `--`, including a
start prompt, pass to Codex unchanged:

```bash
coordination/bin/codex-seat operator -- "continue as operator"
coordination/bin/codex-seat --dry-run operator
```

Codex has no repository-mutating lifecycle hooks and does not use persistent
per-seat indexes. Launch mutating work from a task-specific native Git worktree;
the checkout's ordinary index is the only index. A shared-root Codex session is
read-only except for narrowly authorized coordination writes with explicit
pathspecs.

Mailbox read state is user-interface state, not execution authority. Only a
concrete consuming role advances its own cursor through the canonical event
store; coordinator has no cursor. Never hand-edit or stage a cursor as a
substitute for a successful consume operation.

## AGY transplant

AGY-native continuation details live in `docs/protocol/agy/continuation.md`.
Give each seat its own model and reasoning effort in
`~/.agy/pipeline-seat-launcher.toml`:

```toml
[seats.director]
model = "gemini-3.1-pro-high"
effort = "high"

[seats.director2]
model = "gemini-3.1-pro-high"
effort = "high"

[seats.operator]
model = "gemini-3.1-pro-high"
effort = "high"

[seats.operator2]
model = "gemini-3.1-pro-high"
effort = "high"

[seats.coordinator]
model = "gemini-3.6-flash-low"
effort = "low"
```

Then launch only the selected seat, exactly as with Codex:

```bash
coordination/bin/agy-seat operator -- "continue as operator"
coordination/bin/agy-seat --dry-run operator
```

The schema is deliberately *not* the Codex one. AGY has no service tier and no
working-directory flag; it expresses speed as reasoning effort, and the seat
starts in the repository because the launcher chdirs there before exec.
`effort` accepts `low`, `medium`, or `high`.

`model` must be a literal entry from the model listing — that listing is the
only authority for the name, and it is what `--model` accepts:

```bash
agy models
```

The launcher enforces this rather than trusting the file: it runs that listing
on every launch *and* on `--dry-run`, and refuses a model the listing does not
offer. If the listing cannot be produced at all — a sandbox that blocks AGY's
local language-server socket, a missing login — the launch fails rather than
proceeding with a model it could not check.

Arguments after `--` reach AGY unchanged, with one exception: they may not
restate `--model`, `--effort`, or `--add-dir`, in any spelling. AGY resolves a
repeated flag to its *last* occurrence, so a forwarded `--model` would decide
what actually runs while the seat kept advertising the configured value, and a
report citing it would name a model that never ran. The seat config is the only
place seat identity is set; prompts and every other AGY flag forward normally.

Report the same string back. `Author model:` and `Reviewer model:` in a
verification report must be the exact listed ID the seat ran on, which
`coordination/bin/agy-seat --dry-run <seat>` prints as `AGY_MODEL`. Do not
decorate it with a harness prefix such as `antigravity-`:
`codex_protocol_model.model_family` strips those before comparing families, so
a prefix buys no independence and only makes the cited string impossible to
check against `agy models`.

Model family still governs independence, and AGY does not automatically supply
it: two AGY seats both on `gemini-*` are one family, so they cannot be the
author/Operator pair for `high-risk-control`, the profile whose
`requires_different_model` is set. The listing also offers non-Gemini models, so
an independent AGY Operator is possible — but it is a configuration choice,
never an assumption.

## Authority (Rule #8)

A sent mailbox event communicates durable task state. It can bind work only
within authority already granted by the user, an accepted route, or an
executable capability. It cannot grant push, merge, spend, provider launch,
live-data mutation, or any other external effect merely by saying so.

**User instructions and executable capabilities define authority. Mailbox
events preserve coordination and evidence inside that boundary.**

### Session-bootstrap awareness gate (Rule #8 sub-clause)

On session start, use the compact status/orientation snapshot. Surface a
mailbox item only when it changes the lawful next action, introduces a blocker,
or requires user authority. Do not manufacture a startup announcement for an
empty or unchanged queue.

## Polling cadence (consuming session)

1. **Session start** — Read one compact status/orientation snapshot.
2. **Before any shared-task action** — Pairs with Rule #4 (pre-Write check)
   and Rule #7 (pre-commit check). A mailbox event between your pre-Write
   check and your commit can invalidate the assertion.
3. **Before protocol finalization** — refresh the relevant task/event refs once.
4. **On receipt of a user instruction** that may interact with
   pending events. For live seats, read/consume pending mail before acting on
   the instruction unless the user explicitly asks for read-only/no-consume
   behavior.

## Event format

```markdown
---
from: operator
to: director
kind: dispatch-claim | findings | decision | query | status | fold-notice |
      verify-request | verification-report | doc-sync-notice |
      scout-request | scout-report
related-commits: <sha>, <sha>
related-rules: <rule numbers, if any>
---

<structured authority body for verify-request; kind-specific body otherwise>
```

**v6.0 envelope (current — write THIS on new events; the YAML form above is
the grandfathered pre-v6.0 format).** Generated by `bin/send-event`:

```markdown
# Operator → Director: <subject>

**When:** 2026-06-11T10:00:00Z · **From:** operator (online)

<structured authority body for verify-request; kind-specific body otherwise>

Cursor at send: 2026-06-11T09:00:00Z
```

The `**When:**` timestamp must match the filename timestamp (linted by
`scripts/check_coordination.py`). The filename carries the registered kind;
an authority-bearing verify-request also carries the exact in-body event type
and fields below. The current accepted vocabulary is
`coordination/mailbox/kinds.txt`.

For compact-pair verification, the filename kind alone is not authority.
Canonical Compact Pair Invariant: `scripts/codex_protocol_model.py`. This
surface intentionally does not restate its lifecycle grammar. The fixed mailbox
writer publishes the event only after `coordination/bin/send-event` validates
the committed request/report binding and Operator-only verdict authority.

**Kind registry (current):**

- **v2 (original):** `dispatch-claim` | `findings` | `decision` | `query` |
  `status` | `fold-notice`
- **v4 additions:** `verify-request` | `verification-report` |
  `doc-sync-notice` (Lanes V + D active) | `scout-request` |
  `scout-report` (Lane S scaffolded in v4, **active in v5**)
- **v5 addition:** `memory-candidate` — operator-seat surfaces
  memory-worthy observations (recurring failure modes, tool quirks,
  project-specific gotchas) for director-seat to write or decline
  via `decision`. Closes the latency on operator-observed memory
  candidates without changing memory write authority.
- **Observed-in-practice additions:** `acknowledgement` | `convergence` |
  `coordination` | `discussion` | `fyi` | `measurement-report` | `proposal` |
  `proposal-reply` | `reply` | `verify-addendum` | `verify-readiness` |
  `verify-readiness-converged` | `wrap`

**Filename convention:** `<UTC-ISO-timestamp>-<from>-to-<to>-<kind>.md`.
Timestamp ensures lexicographic ordering matches chronological. Example:
`2026-05-24T13-42-00Z-operator-to-director-status.md`.

## Stale-event cleanup

Manual for v1. Operator-only task: periodically move events older than ~N
sessions from `sent/` to `archive/`. Stale-event surfacing automation
deferred to v2 if it becomes painful.

## Claude-only STATE.md model

STATE.md is **gitignored, per-clone, regenerated on disk** by
`.claude/hooks/update-state.sh` on each HEAD move. B-003 Option E (cycle 8)
retired the prior `git commit --amend` STATE.md-fold model — the hook **never
touches git history**. STATE.md is an informational cache, NOT a coordination
channel (it is not shared between seats).

**Unread-count accuracy (Rule #20, v5.7).** The hook counts events
`*-to-<role>-*` whose filename-timestamp is newer than the cursor's **content**
timestamp — replacing the pre-v5.7 `find -newer <cursor-mtime>` that counted
both directions AND compared file mtime (the source of the observed
`director=4`-vs-1). The Rule #8 awareness gate **recomputes unread live**
regardless; STATE.md's field is a convenience cache. For exact current HEAD,
`git rev-parse HEAD` (git > STATE.md per the authority precedence).

## Claude-only per-clone setup

The hook that auto-maintains `STATE.md` (and thus the `unread mailbox` field)
lives at `.claude/hooks/update-state.sh` (committed). Hook **registration**
lives in `.claude/settings.local.json` (per-clone, gitignored). Each
developer/role must add the following to their own `.claude/settings.local.json`
under the top-level `hooks` key:

```json
"hooks": {
  "PostToolUse": [
    {
      "matcher": "Bash|Write|Edit",
      "hooks": [
        {
          "type": "command",
          "command": "bash /absolute/path/to/Pipeline/.claude/hooks/update-state.sh"
        }
      ]
    }
  ]
}
```

Without registration, `STATE.md` becomes stale after each commit (the cold-
start checklist will still work but the read will be out-of-date). The matcher
is `Bash|Write|Edit` (v5.7): presence freshness (Rule #19) must update through
long edit stretches with no Bash call, not just on commits.

## Claude-only shared-tree seat launch

The two seats run as concurrent Claude Code sessions in **one shared working
tree** (shared object store, shared HEAD on `main`). Per Q4 (user-adjudicated
**D-a**), each seat isolates only its **git index** so one seat's `git add` can
no longer sweep the other's staged WIP (the `2c5ca05` /
`feedback_shared_index_sweep_use_pathspec` class). Launch each session with its
own `GIT_INDEX_FILE` + role marker:

```bash
# director session (run in the shared tree, BEFORE launching `claude`)
cd /Users/hyungkoookkim/Pipeline
export CLAUDE_SEAT=director
export GIT_INDEX_FILE="$(git rev-parse --absolute-git-dir)/index-director"
[ -f "$GIT_INDEX_FILE" ] || git read-tree HEAD   # seed a fresh per-seat index from HEAD
claude

# operator session (separate terminal, same tree)
cd /Users/hyungkoookkim/Pipeline
export CLAUDE_SEAT=operator
export GIT_INDEX_FILE="$(git rev-parse --absolute-git-dir)/index-operator"
[ -f "$GIT_INDEX_FILE" ] || git read-tree HEAD
claude

# --- Pair B (4-seat protocol; see docs/protocol/claude/four-seat-extension.md) ---
# director2 session (separate terminal, SAME tree)
cd /Users/hyungkoookkim/Pipeline
export CLAUDE_SEAT=director2
export GIT_INDEX_FILE="$(git rev-parse --absolute-git-dir)/index-director2"
[ -f "$GIT_INDEX_FILE" ] || git read-tree HEAD
claude

# operator2 session (separate terminal, SAME tree)
cd /Users/hyungkoookkim/Pipeline
export CLAUDE_SEAT=operator2
export GIT_INDEX_FILE="$(git rev-parse --absolute-git-dir)/index-operator2"
[ -f "$GIT_INDEX_FILE" ] || git read-tree HEAD
claude
```

**Seats** are `director`, `director2`, `operator`, `operator2` — two
director↔operator **pairs** (A = `director`+`operator`, B = `director2`+`operator2`).
The heartbeat hook (`.claude/hooks/update-state.sh`) is seat-generic, so presence /
heartbeat / per-seat index isolation work for all four with no hook change. Mailbox
events address any seat directly, or `all` to broadcast (`send-event <from> all <kind>`).

The `git read-tree HEAD` seed is **required**: a fresh `GIT_INDEX_FILE` is an
empty index, so without it `git status` reports every tracked file as a phantom
deletion (verified: 555 phantoms vs 0 after seeding). It writes only the new
per-seat index — the working tree and the shared index are untouched. On
relaunch the index already exists, so the seed is skipped.

`CLAUDE_SEAT` (Rule #19) tells the hook which presence file to stamp and lets a
session self-identify its role. `GIT_INDEX_FILE` gives per-seat staging on the
**shared** tree, so presence / STATE.md / `coordination/` stay peer-visible
(gitignored files in the same working dir) — which separate **worktrees** would
break (they force separate branches + separate working dirs → gitignored
presence becomes peer-invisible; rejected per operator REPLY `ab9925d`). With
this live, the `git commit -- <pathspec>` discipline remains **load-bearing
for commit SCOPE**: a wholesale `git add . && git commit` can still sweep the
peer's in-tree changes, so always commit via pathspec (`git commit -- <files>`).

**Index freshness is now hook-maintained (v5.8).** `update-state.sh`
auto-fast-forwards a seat's stale `GIT_INDEX_FILE` index to HEAD on
peer-commit staleness — and only then; staged work is never touched (decision
table in the hook; the manual `git read-tree HEAD` workaround is retired for
this case). The one case left manual is **mixed** state (you have staged work
AND the peer moved HEAD): the hook deliberately abstains, so resolve it with
`git read-tree -m`. The launch seed above (`[ -f … ] || git read-tree HEAD`)
still stands — the hook needs an existing index to maintain.

**Skip-worktree pollution is also hook-cleared (v5.9).** Harness child
processes (Workflow/subagent runs) have twice left skip-worktree bits in the
active index (N=4; N=767/844 on 2026-06-10), which hides the seat's own edits
from `git status` and breaks add/rm with phantom "sparse-checkout" errors.
`update-state.sh` now clears any flagged entry per-path
(`git update-index --no-skip-worktree` — flag-only, staged work untouched)
on every hook fire, and appends one line per event to the gitignored
`.claude/hooks/.skip-worktree-cleared.log` (the evidence trail toward the
still-unidentified trigger op). The manual per-path / `read-tree HEAD`
workarounds are retired for this case.
