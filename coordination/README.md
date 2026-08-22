# Coordination Directory

Inter-session coordination scaffold for the two CLI participants, `claude` and
`codex`. A review has exactly **two live roles**, `author` and `reviewer`. The
six retired seat names (`director`, `director2`, `operator`, `operator2`,
`coordinator`, `coordinator2`) still *parse*, so committed history stays
readable, but no new event may be written from or to them
(`pipeline/mailbox_writer.py`, `NEW_WRITE_SENDERS` / `NEW_WRITE_RECIPIENTS`).
Roles are cursorless.

The collaboration boundary and the surviving Rules #7–#23 table live in
[docs/protocol/agents/director-operator.md](../docs/protocol/agents/director-operator.md).
[AGENTS.md](../AGENTS.md) is the binding contract; [CLAUDE.md](../CLAUDE.md)
adds Claude-only mechanics. To reach the other CLI, see
[docs/protocol/peer.md](../docs/protocol/peer.md) — not a seat launcher.

## Layout

- `mailbox/sent/` — Authoritative inter-session events. Each event is a markdown
  file; the v6.0 envelope is an H1 (`# <From> → <To>: <subject>`) followed by a
  `**When:** <ISO-UTC> · **From:** <seat>` line whose timestamp must match the
  filename (linted). Pre-v6.0 events used YAML frontmatter (`from`, `to`,
  `kind`, …) and are grandfathered. New events must go through
  `bin/send-event`; raw event writes bypass publication validation and are not
  supported.
- `mailbox/seen/<seat>.txt` — Compatibility read state for the four retired
  pair seats. `coordinator.txt` / `coordinator2.txt` are tracked but inert:
  those identities are cursorless and the snapshot reports them as such, and so
  are the two live roles. Historical ISO timestamps and migrated scalar
  sequences are accepted; malformed state is unavailable or fatal, never
  silently zero unread.
- `bin/send-event <from> <to> <kind> <subject…>` (body on stdin), reachable as
  `pipeline mail send` — constructs one canonical candidate, validates its
  envelope and kind-specific structure, finalizes it under the shared writer
  fence, and stages only its explicit path. It never commits. A validation or
  staging failure is reported rather than bypassed with a direct write. New
  writes are restricted to sender/recipient in {`author`, `reviewer`} (`all`
  may receive) and to eight kinds: `decision`, `dispatch-claim`, `findings`,
  `learning-candidate`, `measurement-report`, `verification-report`,
  `verify-addendum`, `verify-request`.
- `bin/consume-events <seat> [--to <ts>]`, reachable as `pipeline mail consume`
  — advances `seen/<seat>.txt` to the newest event addressed to that seat (or
  the explicit target), refusing regressions and nonexistent targets, and
  STAGES the cursor file. It accepts only the four retired pair seats
  (`director`, `director2`, `operator`, `operator2`); the live roles have no
  cursor to advance. The wrapper supplies `--repo-root` itself. **Cursor
  folding (v6.0):** the staged advance rides the seat's next substantive
  commit; standalone cursor-only commits are deprecated (idle-consume exempt).
  A commit whose **entire** changeset is `seen/*.txt` (no `sent/` event, no
  code/doc) is a standalone cursor-only commit; `pipeline check coordination`
  (i.e. `check_coordination.py --git-root <repo>`) ADVISORY-flags these (lever #5, capacity audit `wf_6be2ee18-f4b`). Intentional
  idle-consume advances are exempt — prefix the subject `coord(cursor):` to signal it.
  **ACKs:** an `acknowledgement` event that carries substantive body (role
  resolution, retraction, findings) stays a `sent/` event file; a bare "received"
  ACK that adds nothing beyond the cursor should be a cursor advance only.
- `mailbox/kinds.txt` — canonical mailbox kind vocabulary, one kind per line,
  above a comment header the loader skips. `bin/send-event` and
  `pipeline/check_coordination.py` load this registry through
  `pipeline/protocol_mailbox.py`. `wc -l` counts the comment lines too, so ask
  the loader instead:

  ```bash
  coordination/bin/pipeline-python -c \
    "import pathlib,sys; sys.path.insert(0,'pipeline'); import protocol_mailbox as m; \
     print(len(m.load_known_kinds(pathlib.Path('.'))))"   # → 25
  ```

  These 25 are what may be *read*; only the eight listed under `bin/send-event`
  above may be *written*.
- `pipeline/check_coordination.py` (`pipeline check coordination`) — lints all
  of the above (cursor parseable/non-future/non-orphan, filename convention,
  envelope, registered kind, unread report). Wired into `pipeline check`
  (`pipeline/governance_verify_all.py`): FATAL hard-fails locally and in CI;
  ADVISORY warns; INFO silent.
- `mailbox/archive/` — Old events moved out of `sent/` for log hygiene (manual
  move; no tool does it).
- `presence/<seat>-heartbeat.ts` — legacy/provider-specific liveness hint. Codex
  does not write repository heartbeats; host task/thread activity is its
  liveness source. A heartbeat never grants authority.
- `presence/<name>.md` — per-session **agent-owned intent**: flat `key: value`
  (`seat`, `status`, `current_task`, …), from `SEAT.md.template`. Each session
  writes its own file and owns every field; nothing else stamps them, because
  there are no repository lifecycle hooks. A file only reads fresh if its owner
  refreshed it. Gitignored + per-clone, so none is present in a fresh checkout.

## Orientation

Run one compact non-role snapshot:

```bash
bin/pipeline status snapshot
```

Run it from the repository root; `pipeline` is not installed on `PATH`. It
reports current Git, the retired-seat unread counts, the current request or
blocker, and the lawful next action without claiming a role or mutating state.
`pipeline status` (no subcommand) prints the longer report, including the
per-identity cursor block. There is no separate mailbox monitor: the
`mailbox_monitor.py` watch loop was deleted, and the snapshot carries the same
unread block.

For an explicitly assigned role, add it: `pipeline status snapshot author` or
`pipeline status snapshot reviewer`, then read the actionable event bodies.
Cursor consumption is a separate action and applies only to the four retired
pair seats; run `pipeline mail consume <seat>` only when that is authorized.
Coordinator was always unpinned: read relevant coordinator and all-scope
bodies, but never try to consume a coordinator cursor — the writer rejects it.

## Codex transplant

**To reach Codex from Claude (or Claude from Codex), you do not launch a seat.**
You run the other CLI once as a child process and keep its receipt:
`pipeline peer ask <claude|codex|agy>`, documented in
[docs/protocol/peer.md](../docs/protocol/peer.md). That is the current
mechanism. The launcher below is a separate thing: it starts a local, human-
driven Codex session in this checkout, not a peer call.

Codex-native continuation details live in
`docs/protocol/codex/continuation.md`. The repo also provides:

- `.agents/skills/four-seat-protocol/SKILL.md` — reusable Codex workflow for
  orientation and explicit role continuation.
- `.codex/agents/*.toml` — explicit-use Codex custom agents for
  `readiness-bridge`, `protocol-director`, `protocol-operator`,
  `protocol-coordinator`, `lane-v-verifier`, `money-gate-reviewer`, and
  `amnesiac-prober`.
- No project Codex hook registry — Codex has no repository lifecycle hook or
  persistent-index dependency.

**Local seat launcher.** `coordination/bin/codex-seat` starts a local Codex
session bound to one of the two launchable seats, which are exactly the two
live roles (`pipeline/protocol_mailbox.py`: `LAUNCHABLE_SEATS = ROLES`). A
retired seat name is refused, because a process that can publish nothing has no
lawful action available to it. The config must define **exactly** those two
tables — a leftover five-seat file fails with
`codex-seat: config must define exactly: author, reviewer`:

```toml
# ~/.codex/pipeline-seat-launcher.toml
[seats.author]
model = "gpt-5.6-sol"
service_tier = "default"

[seats.reviewer]
model = "gpt-5.6-terra"
service_tier = "fast"
```

Then launch only the selected seat:

```bash
coordination/bin/codex-seat author
coordination/bin/codex-seat reviewer
```

Each table is independent. Changing one table does not change the other.
`service_tier` accepts `fast` or `default`. Arguments after `--`, including a
start prompt, pass to Codex unchanged; `--dry-run` prints the resolved argv and
environment and launches nothing:

```bash
coordination/bin/codex-seat reviewer -- "continue as reviewer"
coordination/bin/codex-seat --dry-run reviewer
```

Codex has no repository-mutating lifecycle hooks and does not use persistent
per-seat indexes. Launch mutating work from a task-specific native Git worktree;
the checkout's ordinary index is the only index. A shared-root Codex session is
read-only except for narrowly authorized coordination writes with explicit
pathspecs.

Mailbox read state is user-interface state, not execution authority. Only a
retired pair seat has a cursor to advance, and only through the canonical
front door. Never hand-edit or stage a cursor as a substitute for a successful
consume operation.

## Authority (Rule #8)

A sent mailbox event communicates durable task state. It can bind work only
within authority already granted by the user, an accepted route, or an
executable capability. It cannot grant merge, spend, peer invocation,
live-data mutation, or any other external effect merely by saying so.
(`AGENTS.md` item 6 records why push is deliberately absent from that list.)

**User instructions and executable capabilities define authority. Mailbox
events preserve coordination and evidence inside that boundary.**

### Session-bootstrap awareness gate (Rule #8 sub-clause)

On session start, use the compact status/orientation snapshot. Surface a
mailbox item only when it changes the lawful next action, introduces a blocker,
or requires user authority. Do not manufacture a startup announcement for an
empty or unchanged queue.

## Polling cadence (consuming session)

1. **Session start** — Read one compact status/orientation snapshot.
2. **Before any shared-task action** — Rule #7: refresh current Git and the
   relevant events before a state-asserting write. A mailbox event between
   your pre-write check and your commit can invalidate the assertion.
3. **Before protocol finalization** — refresh the relevant task/event refs once.
4. **On receipt of a user instruction** that may interact with
   pending events. For an assigned role, read pending mail before acting on
   the instruction unless the user explicitly asks for read-only behavior.

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
# Reviewer → Author: <subject>

**When:** 2026-08-21T22:12:09Z · **From:** reviewer (online)

<structured authority body for verify-request; kind-specific body otherwise>

Cursor at send: cursorless
```

The trailing `Cursor at send:` line still appears; because roles are cursorless
it reads literally `cursorless`. Live example:
`coordination/mailbox/sent/2026-08-21T22-12-09Z-reviewer-to-author-verification-report.md`.

The `**When:**` timestamp must match the filename timestamp (linted by
`pipeline/check_coordination.py`). The filename carries the registered kind;
an authority-bearing verify-request also carries the exact in-body event type
and fields below. The current accepted vocabulary is
`coordination/mailbox/kinds.txt`.

For compact-pair verification, the filename kind alone is not authority.
Canonical Compact Pair Invariant: `pipeline/codex_protocol_model.py`. This
surface intentionally does not restate its lifecycle grammar. The fixed mailbox
writer publishes the event only after `coordination/bin/send-event` validates
the committed request/report binding and reviewer-only verdict authority.

**Kind registry (current):**

- **v2 (original):** `dispatch-claim` | `findings` | `decision` | `query` |
  `status` | `fold-notice`
- **v4 additions:** `verify-request` | `verification-report` |
  `doc-sync-notice` (Lanes V + D active) | `scout-request` |
  `scout-report` (Lane S scaffolded in v4, **active in v5**)
- **v5 addition, superseded by ADR-067:** `learning-candidate` — a producer
  surfaces an evidence-backed lesson (schema:
  `docs/protocol/learning/contract.md` §3) for non-producer disposition
  via a `decision` event carrying `Candidate:` and `Disposition:`. Replaces
  `memory-candidate`, retired in the same change with zero committed
  instances (ADR-067 baseline). Read-side typing is
  `pipeline/protocol_mailbox.py` (`parse_learning_candidate_statement`,
  `parse_learning_disposition_statement`); the Stage 2b writer-side branch
  landed, so the contract I4 refusals bind at publication
  (`pipeline/mailbox_writer.py`, `tests/unit/test_learning_promotion.py`).
  Grants no memory write authority.
- **Observed-in-practice additions:** `acknowledgement` | `convergence` |
  `coordination` | `discussion` | `fyi` | `measurement-report` | `proposal` |
  `proposal-reply` | `reply` | `verify-addendum` | `verify-readiness` |
  `verify-readiness-converged` | `wrap`

**Filename convention:** `<UTC-ISO-timestamp>-<from>-to-<to>-<kind>.md`.
Timestamp ensures lexicographic ordering matches chronological. Example:
`2026-08-21T21-48-14Z-author-to-reviewer-verify-request.md`.

## Stale-event cleanup

Manual: periodically move events older than ~N sessions from `sent/` to
`archive/`. No tool does this, and no automation is planned until it hurts.

## Claude-only STATE.md model

Retired. No STATE.md is generated, and nothing under `pipeline/`,
`coordination/bin/`, or `.claude/` writes one.

A per-clone lifecycle hook used to regenerate it on each HEAD move and to
maintain the unread count. It is gone along with the rest of the
repository lifecycle hooks (see the next section).
`tests/unit/test_claude_hook_isolation.py` and
`tests/unit/test_codex_hook_lifecycle.py` assert the retired scripts stay
absent, and `.gitignore` still lists `STATE.md` and `.claude/hooks/` so any
leftover from that era stays untracked. Read state from its source, not from a
cache.

**Unread-count accuracy.** Count events `*-to-<seat>-*` whose
filename-timestamp is strictly newer than the cursor's **content** timestamp,
not its mtime, and not counting that seat's own sends — the earlier
`find -newer <cursor-mtime>` form got both wrong and produced the observed
`director=4`-vs-1. Use `pipeline status mailbox-unread <seat>`, which
encapsulates that comparison (the seat argument is one of the four retired pair
seats). The awareness gate recomputes live; there is no cached field to fall
back to.

## Claude-only per-clone setup

None. Claude Code needs no per-clone registration to work in this repository.

The `PostToolUse` hook that once auto-maintained `STATE.md` is gone, and nothing
replaced it. Repository lifecycle hooks do not orient any side, mutate state,
refresh doctrine, or maintain a second index (`ARCHITECTURE.md` section 5).
`.claude/hooks/` no longer exists in this checkout at all; the `.gitignore`
entry is the only trace left.

Read current state from Git, which is authoritative:

```bash
env -u GIT_INDEX_FILE git rev-parse HEAD
bin/pipeline status snapshot
```

`bin/pipeline` clears `GIT_INDEX_FILE` and resolves the repository interpreter
itself, from a linked worktree too, so it needs no `env -u` prefix and no
per-worktree `.venv`.

## Claude-only start

Pipeline has no Claude seat launcher, governance-seat registry, or session-start
seat binding, and no desktop app is involved — the participants are the `claude`
and `codex` CLIs. Per
[docs/protocol/claude/continuation.md](../docs/protocol/claude/continuation.md):

1. Open a terminal in the exact Pipeline checkout that owns the work, or in a
   native Git worktree of it.
2. For new independent work, create a worktree named for what the work is. For
   an existing uncommitted candidate, return to the worktree that holds it — a
   fresh one does not contain another checkout's bytes.
3. Confirm repository root, HEAD, and scoped status, then run
   `bin/pipeline status snapshot`. A directory name is not a role assignment;
   an explicit role still has to come from the task.

Review identity is decided at publication by `pipeline/compact_pair_loop.py`,
which binds a verdict to reviewer not equal to author, reviewer equal to the
request's assigned reviewer, and distinct model families for
`high-risk-control`.

**Never point `GIT_INDEX_FILE` at a per-seat index.** Earlier revisions of this
file told each seat to export one before launching `claude` and to seed it with
`git read-tree HEAD`. That mechanism is retired: no side binds a per-seat Git
index, every worktree uses its native index, and the per-provider seat-index
naming is gone (`ARCHITECTURE.md` section 5). Setting the variable in a shell
silently rebinds every later Git command in that session including commits, and
it follows `cd` into unrelated repositories, where it presents as index
corruption. Prefix ordinary Git with `env -u GIT_INDEX_FILE`; run Python and
pytest through `coordination/bin/pipeline-python`, and everything else through
`bin/pipeline`, both of which clear the variable themselves.

Work in a native Git worktree you are willing to commit from:

```bash
PIPELINE_ROOT="$(env -u GIT_INDEX_FILE git rev-parse --show-toplevel)"
env -u GIT_INDEX_FILE git -C "$PIPELINE_ROOT" worktree add ../pipeline-<slug> -b <branch>
```

Pipeline is the governance kernel and the base for these worktrees; do not route
this work through the user Content checkout.

Each worktree has its own native index, which is the staging isolation the
retired mechanism was reaching for, and carries no `.venv` of its own. The
earlier objection that separate worktrees make gitignored presence files
peer-invisible no longer applies: presence stamping was hook-maintained, and
the hooks are gone.

**Identities.** New events carry one of two roles, `author` or `reviewer`, and
may be addressed to either or to `all` for a broadcast
(`pipeline mail send author all findings <subject>`). The six retired seat
names remain readable in committed history and unwritable going forward.

When two sessions share one working tree, commit scope stays load-bearing: a
wholesale `git add . && git commit` sweeps a peer's in-tree changes, so always
commit with an explicit pathspec (`git commit -- <files>`). Preserve peer and
user dirt; the first landed shared-file commit wins.
