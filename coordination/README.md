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
  locally and in CI; ADVISORY warns; INFO silent.
- `mailbox/archive/` — Old events moved out of `sent/` for log hygiene (manual
  move by operator).
- `presence/<seat>-heartbeat.ts` — legacy/provider-specific liveness hint. Codex
  does not write repository heartbeats; host task/thread activity is its
  liveness source. A heartbeat never grants authority.
- `presence/director.md`, `presence/operator.md` — (Rule #19) per-seat
  **agent-owned intent**: flat `key: value` (`seat`, `status`, `current_task`,
  …). Each seat writes its own file and owns every field; nothing else stamps
  them, because there are no repository lifecycle hooks. A file only reads
  fresh if its seat refreshed it. Gitignored + per-clone.

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

Text after `--` reaches AGY unchanged, but **flags** after `--` are restricted to
an allowlist — `-p`/`--print`/`--prompt`, `-i`/`--prompt-interactive`,
`-c`/`--continue`, `--conversation`, `--print-timeout`, `--sandbox`. Anything
else is refused, including flags AGY does define:

| Refused | Why |
| --- | --- |
| `--model`, `--effort` | set from the seat config; forwarding one lets a seat run on something it does not report |
| `--agent`, `--mode`, `--project` | behaviour and session identity the seat's `AGY_*` runtime already declares |
| `--add-dir`, `--new-project`, `--log-file` | workspace and filesystem effects beyond the launched repository |
| `--dangerously-skip-permissions` | blanket tool approval; an external effect needing its own authorization |

It is an allowlist rather than a denylist because AGY resolves a repeated flag to
its *last* occurrence: a forwarded `--model` decides what actually runs while the
seat keeps advertising the configured value, and a report citing it names a model
that never ran. A denylist can only enumerate flags that exist today, so a future
short alias such as `-m` would be admitted silently. Unrecognized therefore means
refused, and adding an entry to `FORWARDABLE_FLAG_NAMES` is a deliberate act.

A second `--` is not an escape. Whether `--` terminates AGY's flags depends on
what precedes it — `--print-timeout --` eats it as the timeout value — so the
launcher scans the whole forwarded list rather than trying to model AGY's parser.

Only a *bare* flag token is refused. To mention one in a prompt, keep it inside
the prompt value, where it is a single token naming no flag:

```bash
coordination/bin/agy-seat operator -- -p "explain why --model is set from the seat config"
```

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
- **v5 addition, superseded by ADR-067:** `learning-candidate` — any pair
  seat surfaces an evidence-backed lesson (schema:
  `docs/protocol/learning/contract.md` §3) for director-side disposition
  via a `decision` event carrying `Candidate:` and `Disposition:`. Replaces
  `memory-candidate`, retired in the same change with zero committed
  instances (ADR-067 baseline). Read-side typing is
  `scripts/protocol_mailbox.py` (`parse_learning_candidate_statement`,
  `parse_learning_disposition_statement`); refusals are advisory until the
  Stage 2b writer-side branch lands (contract I4). Grants no memory write
  authority.
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

Retired. No STATE.md is generated, and nothing under `scripts/`,
`coordination/bin/`, or `.claude/` writes one.

A per-clone lifecycle hook used to regenerate it on each HEAD move and to
maintain the Rule #20 unread count. It is gone along with the rest of the
repository lifecycle hooks (see the next section).
`tests/unit/test_claude_hook_isolation.py` and
`tests/unit/test_codex_hook_lifecycle.py` assert the retired scripts stay
absent, and `.gitignore` still lists `STATE.md` and `.claude/hooks/` so
leftovers from that era stay untracked. Read state from its source, not from a
cache.

**Unread-count accuracy (Rule #20).** Count events `*-to-<role>-*` whose
filename-timestamp is strictly newer than the cursor's **content** timestamp,
not its mtime, and not counting the role's own sends — the pre-Rule-#20
`find -newer <cursor-mtime>` form got both wrong and produced the observed
`director=4`-vs-1. Use `python scripts/status.py mailbox-unread <seat>`, which
encapsulates that comparison, or `python scripts/mailbox_monitor.py --once`.
The Rule #8 awareness gate recomputes live; there is no cached field to fall
back to.

## Claude-only per-clone setup

None. Claude Code needs no per-clone registration to work in this repository.

The `PostToolUse` hook that once auto-maintained `STATE.md` is gone, and nothing
replaced it. Repository lifecycle hooks do not orient any side, mutate state,
refresh doctrine, or maintain a second index (`ARCHITECTURE.md` section 5).
`.claude/hooks/` retains only gitignored runtime leftovers from that era; they
are inert and no session reads them.

Read current state from Git, which is authoritative:

```bash
env -u GIT_INDEX_FILE git rev-parse HEAD
env -u GIT_INDEX_FILE .venv/bin/python scripts/status.py snapshot <seat>
```

## Claude-only seat launch

Pipeline has no Claude seat launcher, governance-seat registry, or session-start
seat binding. In Claude Desktop, open Code -> Local -> the exact Pipeline
checkout and let the app create an isolated worktree for new independent work;
resume the owning session/worktree for an existing uncommitted candidate.
Claude's host session registry and peer relay reduce app-to-app copying, but a
session name remains convention, not authority. Review identity is decided at
publication by `scripts/compact_pair_loop.py`, which binds a verdict to reviewer
seat not equal to author seat, reviewer equal to the request's assigned
operator, and distinct model families for `high-risk-control`.

**Never point `GIT_INDEX_FILE` at a per-seat index.** Earlier revisions of this
file told each seat to export one before launching `claude` and to seed it with
`git read-tree HEAD`. That mechanism is retired: no side binds a per-seat Git
index, every worktree uses its native index, and the per-provider seat-index
naming is gone (`ARCHITECTURE.md` section 5). Setting the variable in a shell
silently rebinds every later Git command in that session including commits, and
it follows `cd` into unrelated repositories, where it presents as index
corruption. Prefix ordinary Git and pytest with `env -u GIT_INDEX_FILE`.

Desktop creates native worktrees automatically. If using the CLI instead, work
in a native Git worktree you are willing to commit from:

```bash
PIPELINE_ROOT="$(git rev-parse --show-toplevel)"
cd "$PIPELINE_ROOT"
env -u GIT_INDEX_FILE git worktree add ../pipeline-<seat> -b <branch>
```

Pipeline is the governance kernel and the base for these worktrees; do not route
this work through the user Content checkout.

Each worktree has its own native index, which is the staging isolation the
retired mechanism was reaching for. The earlier objection that separate
worktrees make gitignored presence files peer-invisible no longer applies:
presence stamping was hook-maintained, and the hooks are gone.

**Seats** are `director`, `director2`, `operator`, `operator2` — two
director↔operator **pairs** (A = `director`+`operator`, B = `director2`+`operator2`).
Mailbox events address any seat directly, or `all` to broadcast
(`send-event <from> all <kind>`).

When seats do share one working tree, commit scope stays load-bearing: a
wholesale `git add . && git commit` sweeps a peer's in-tree changes, so always
commit with an explicit pathspec (`git commit -- <files>`). Preserve peer and
user dirt; the first landed shared-file commit wins.
