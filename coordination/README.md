# Coordination state

Routine Codex, Claude, and AGY messages use the local `pipeline-team` SQLite
transport, not Git. The database lives under the repository's Git common
directory so linked worktrees share it.

This tracked directory has one active purpose:

- `mailbox/kinds.txt` lists the two formal artifact kinds.
- `mailbox/sent/` retains published `verify-request` and
  `verification-report` files written by `bin/pipeline mail send`.

The author publishes a request for one exact committed range. A non-author
Codex or Claude reviewer publishes one bound GO, NITS, or FAIL report. High-risk
requests carry abuse-class bullets and reports bind that assessment. Published
artifacts are append-only; retire verdicts with valid `Supersedes` reports and
retain the originals. Local mailbox health and exact-range integration admission
are separate checks; neither reconstructs discarded branch history.

Do not put routine chat, plans, handoffs, cursors, presence files, capacity
packets, or role assignments here.
