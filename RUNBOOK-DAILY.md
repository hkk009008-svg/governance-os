# Daily desktop-team runbook

1. Open the repository in Codex, Claude, or AGY. Run `bin/pipeline preflight`
   only when setup changed or the team tools fail.
2. Read the user task, inspect fresh Git status/diff, call `team_status`, and
   read addressed messages with `team_wait`.
3. Execute the simplest sufficient work. Use all three members freely for
   reasoning, direction, implementation, testing, and challenge. Parallelize
   read-only or nonoverlapping work; serialize shared-file writes.
4. Send bounded requests or results with `team_send`. Queued is not
   acknowledged; acknowledged is not a substantive reply. No message grants
   authority.
5. Test proportionately. Only at a material or high-risk boundary, temporarily
   name an author and a non-author Codex or Claude reviewer for the exact range.
   Hear and disposition AGY findings, but do not use AGY as the sole formal
   verdict.
6. Before push, merge, release, paid spend, live-data mutation, or destruction,
   confirm exact current user/task authority. At a real transfer or wrap, leave
   one concise checkpoint; otherwise Git, tests, and desktop task history are
   sufficient.

Legacy mailbox conversation, cursors, seats, and peer receipts are history.
The fixed mailbox writer is reserved for a risk-required formal artifact, real
transfer checkpoint, or governed learning-candidate/disposition record, never
routine chat. Terminal commands implement and verify repository work; they
never launch a model provider.
