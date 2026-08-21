---
name: four-seat-protocol
description: Use for explicit Claude role, mailbox, handoff, wave, continuation, or protocol decisions.
---

# Claude role protocol

Protocol semantics are canonical in
`.agents/skills/four-seat-protocol/SKILL.md`; read and follow that body. This
adapter adds only Claude-native mechanics.

Choose readiness bridge, assigned live role, coordinator, or parent-scoped
subagent from the explicit task. Do not infer a role. For a governed decision,
orient once:

```bash
unset GIT_INDEX_FILE
coordination/bin/pipeline-python scripts/status.py snapshot <seat>
```

Read actionable event bodies. Only an assigned receiving role consumes its
cursor; coordinators have none. Use `coordination/bin/send-event` and
`coordination/bin/consume-events`, never raw mailbox/cursor edits.

Explore, Validate, and Promote come from `docs/protocol/work-modes.md` and are
independent from review risk. Material
behavior requires non-author exact-range review. Only high-risk control also
requires a different model family and abuse-class assessment. Preserve the
complete Compact Pair binding whenever formal review is triggered.

Claude helpers and advisors return evidence to their parent. They do not own a
live role, publish role events or verdicts, consume cursors, lock, push, merge,
launch providers, or spend. Use the native worktree index; external effects
remain separately authorized.

Use Claude's native peer messages for attributed, transient findings or status
so the user does not manually relay them, including traffic crossing the named
Codex bridge. They grant no role or effect authority and are not durable
protocol state. Formal, binding, or durable speech still goes through
`coordination/bin/send-event`.

