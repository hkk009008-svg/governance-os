# Cursor continuation adapter

This file maps Pipeline's governed protocol to **Cursor** mechanics. Policy
lives in the executable kernel model (`scripts/codex_protocol_model.py`); this
adapter only translates mode, startup, mailbox, Git, and guardrail consequences
into Cursor-native surfaces. It does not restate or fork the protocol, and it
does not replace the Codex/Claude continuation adapters.

The Cursor naming layer is a thin adapter over the canonical contract:
`scripts/cursor_protocol_model.py` renames `CURSOR_*` identity onto the same
mode/role/behavior semantics the kernel already validates. Cursor never emits
`CODEX_*` authority keys of its own.

## Modes

- Readiness bridge: the default for ordinary Cursor chat. Read-only
  orientation; no seat claim, no durable mutation, no mailbox consume, no push.
- Live seat: only when the Cursor seat launcher binds `director`, `director2`,
  `operator`, or `operator2` from a committed trigger.
- Coordinator: only for explicit reconciliation or facilitation; authors no
  behavior-changing production work and holds no cursor.
- Subagent: an unbound Cursor session may use parent-scoped advisors. Cursor's
  child-tool hook input does not safely identify a live seat child, so a live
  seat cannot spawn a subagent; use a separate unbound advisor session instead.

Behavior source map: `director -> director`, `director2 -> director`,
`operator -> operator2`, `operator2 -> operator2`.

Only the top-level Cursor seat launcher binds a live seat; an ordinary Cursor
window (including one whose parent is a seat) stays a readiness bridge, and a
Cursor subagent stays parent-scoped.

## Startup (non-trivial work)

```bash
cd /Users/hyungkoookkim/Pipeline
env -u GIT_INDEX_FILE .venv/bin/python scripts/ci_smoke.py
env -u GIT_INDEX_FILE git log --oneline -5
env -u GIT_INDEX_FILE git status --short --branch
```

Surface the unread count, then read relevant mailbox bodies before decisions.
Ordinary Git and pytest use `env -u GIT_INDEX_FILE`; a per-seat index
(`.git/index-cursor-<seat>`) is only for a deliberately bound live seat. When a
seat index is present, read-only Git (`status`, `log`, `show`, `diff`, ...)
stays usable bare; index mutators (`add`, `commit`, `stash`, ...) and pytest
require the `env -u GIT_INDEX_FILE` prefix, mirroring the Codex guard. Refresh
HEAD, relevant mail, and scoped status before any write or gate decision.

## Live seats (Cursor SDK)

A live Cursor seat is launched, not adopted from chat. The launcher
(`scripts/cursor_seat_launcher.py`, shim `coordination/bin/cursor-seat`) binds
the exact seat identity, seeds a per-seat Git index, records a private local
registry under `.cursor/runtime/` (never committed), and requires interactive
confirmation before any provider agent starts.

```bash
coordination/bin/cursor-seat readiness             # print the runtime contract
coordination/bin/cursor-seat --dry-run dispatch director --trigger-ref <path@sha>
coordination/bin/cursor-seat dispatch director --trigger-ref <path@sha>
coordination/bin/cursor-seat review operator --verify-request <path@sha>
```

An Operator review binds to the assigned committed verify-request and must run
a different system-visible model from the author. A seat writes its result to
`.cursor/runtime/outbox/<seat>/` for human review; the seat process itself
never publishes a mailbox event.

## Mailbox and locks

Cursor never reimplements mailbox mechanics. Publishing an event and consuming
a seat cursor are separately authorized effects that delegate to the existing
fixed writers, behind an interactive, seat-bound confirmation:

```bash
echo "body" | coordination/bin/cursor-publish --seat director --to operator --kind status --subject "..."
coordination/bin/cursor-consume --seat director
```

These wrappers call `coordination/bin/send-event` and
`coordination/bin/consume-events` and add no validation, fencing, or staging of
their own. Locks still use `coordination/bin/claim-lock` and are a distinct
push-first authority.

## Guardrails

Project hooks (`.cursor/hooks.json` -> `.cursor/hooks/seat-policy` ->
`scripts/cursor_hook_policy.py`) are a deterministic, fail-closed backstop, not
a hostile sandbox. They deny direct edits to fixed-writer and Cursor runtime
state and deny live fixed-writer / launcher / push / merge effects from an
agent tool, while keeping the documented read-only surfaces usable:
`cursor-seat readiness`/`status` and `--dry-run` previews of dispatch, publish,
and consume stay allowed. When a seat index is present, git index mutators and
pytest require `env -u GIT_INDEX_FILE`; read-only Git stays bare. Operator
review and Coordinator sessions are held to repository-tree read-only (out-of-
tree scratch such as `/tmp` and `.pytest-verify-tmp/` stays available). Cursor
sessions never launch another provider's seats (`codex-seat`, `agy-seat`, or
their launchers) — provider separation is enforced, reading those files is not
restricted. Subagents cannot inherit seat authority: child creation under a
live seat is denied, and seat impersonation tasks are rejected. The hook
describes identity; it never grants authority.

## Governed outcome

Autonomous Seat Outcome Contract: scripts/codex_protocol_model.py
Own the routed outcome and choose the method. Preserve material findings,
require non-author Operator GO for behavior-changing work with a distinct
Operator seat and different model, bind ownership to an immutable
parent/revision, and keep external effects separately user-authorized for the
exact effect/executor/target/scope. An Operator cannot verify anything it
authored.

Canonical Compact Pair Invariant: scripts/codex_protocol_model.py
A committed verify-request binds the actual base/head, outcome, author
seat/model, assigned non-author Operator, allowed paths, and immutable finding
refs. Only that Operator issues GO/NITS/FAIL through the fixed mailbox writer.

Push, merge, lock action, cursor consumption, provider launch, and paid spend
are distinct authorities. Structural identity never grants execution
permission.

## Target repos

Cursor product work targets FoulPlay via
`docs/protocol/cursor/foulplay-adoption.md`; evidence-ledger remains the ADR
registry default for Codex/Claude ledger seats. Select the target explicitly;
never stage a target-repo path from a Pipeline seat index.
