# Coordination state

Routine messages and working notes use the local `pipeline-team` SQLite
transport, not Git. This tracked directory holds only formal artifacts:

- `mailbox/kinds.txt` lists the two artifact kinds.
- `mailbox/sent/` retains every published `verify-request` and
  `verification-report`, append-only. Retire a verdict with a valid
  `Supersedes` report and keep the original.

No chat, plans, handoffs, cursors, presence files, or role assignments here.
