---
name: four-seat-protocol
description: Use for explicit Claude role, mailbox, handoff, wave, continuation, or protocol decisions.
---

# Claude role protocol

Protocol semantics are canonical in
`.agents/skills/four-seat-protocol/SKILL.md`; read and follow that body. This
adapter adds only Claude-native mechanics.

A review has two positions, `author` and `reviewer`. Choose readiness bridge,
one explicitly assigned role, or parent-scoped subagent from the explicit
task. Do not infer a role. For a governed decision, orient once:

```bash
pipeline status
```

`bin/pipeline` clears the per-seat index variable and resolves the repository
interpreter itself — from a linked worktree too — so that line needs no
prefix. Two Claude-native deltas remain for everything it has no verb for:
prefix ordinary Git with `env -u GIT_INDEX_FILE`, and run a module or pytest
through `coordination/bin/pipeline-python` after its own `unset GIT_INDEX_FILE`
line, never behind an `env -u` prefix — Claude's Bash tool refuses that form as
soon as the command takes options.

Read actionable event bodies. Both roles are cursorless. `pipeline mail send`
is the only write path into the durable mailbox and refuses a retired sender,
a retired recipient, or a conversational kind; never edit a raw event or
cursor file.

Explore, Validate, and Promote come from `docs/protocol/work-modes.md` and are
independent from review risk. Material behavior requires non-author exact-range
review. Only high-risk control also requires a different model family and
abuse-class assessment — and every model this harness can select is
claude-family, so that counterparty is Codex, never a differently-configured
Claude. Preserve the complete Compact Pair binding whenever formal review is
triggered.

Claude helpers and advisors return evidence to their parent. They do not own a
live role, publish role events or verdicts, consume cursors, lock, merge,
launch providers, or spend. Use the native worktree index; external effects
remain separately authorized.

Reach Codex by running it once — the `pipeline peer ask codex` verb, contract
in `docs/protocol/peer.md`. The child's exit code is the delivery
acknowledgement and the receipt under `coordination/peer/<task>/` records what
actually ran, so no send's delivery can stay unknown. Launching a peer is a
provider launch and paid spend needing its own authority. Native Claude session
messages carry transient findings between your own terminals; they grant no
role or effect authority and are not durable protocol state. Formal, binding,
or durable speech still goes through `pipeline mail send`.
