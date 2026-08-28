---
name: four-seat-protocol
description: Reserved for explicit formal review of an exact committed range, temporary Claude author or reviewer responsibility, durable transfer or continuation, or inspection of a legacy mailbox handoff.
---

# Claude desktop formal-review adapter

Protocol semantics are canonical in
`.agents/skills/four-seat-protocol/SKILL.md`; read and follow that complete
body. This file adds only Claude Desktop mechanics.

Orient with `team_status` and the task's Git state. Communicate with Codex and
AGY through `team_send`/`team_wait`; never mistake a queued or merely returned
message for acknowledgement. Claude's Desktop sessions,
side chats, visual diff, previews, computer use, and worktrees may all support
the accepted task, but none grants an effect or verdict authority.

Use `bin/pipeline` for reproducible checks. When Claude is the temporary
reviewer, stay read-only for that range and publish a formal result only if the
risk policy requires it. Claude may review high-risk work only when its model
family differs from the author; another Claude session and AGY advice do not
satisfy the accepting-reviewer boundary.
