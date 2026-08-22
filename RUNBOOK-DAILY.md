# Daily Runbook

Use only the branch of this loop that the task needs.

1. Understand the requested outcome and hard boundaries.
2. For local change, refresh the native worktree and affected-path history.
3. Inspect definitions, writes, callers, and sibling paths before changing
   behavior.
4. Add a failing behavior test when feasible, implement the narrow fix, and run
   focused verification.
5. Classify the actual diff:
   - ordinary local work stops after focused verification;
   - material behavior gets non-author exact-range review;
   - high-risk control additionally gets different-model-family review and
     abuse-class analysis;
   - external effects wait for exact live authorization.
6. Compare the final diff with the requested scope and report remaining
   unknowns truthfully.

Run `bin/pipeline status snapshot` only when current protocol state matters;
add a role argument (`bin/pipeline status snapshot <role>`) only after explicit
assignment. Mailbox events, full smoke, and coordination checks are triggered
tools, not daily rituals. Historical capacity packets are not a live scheduler.

`GO` accepts its bound range; it never authorizes an external effect.
Classify documentation and tests by actual behavior/risk, not filename.

`bin/pipeline` is the single entry point: it clears `GIT_INDEX_FILE` and
resolves the repository interpreter, from a linked worktree too. The policy
kernel is `pipeline/codex_protocol_model.py`; formal exact-range review is
`pipeline review validate` (`pipeline/compact_pair_loop.py`); validated
serialized event and cursor writes go through `pipeline mail send` and
`pipeline mail consume`, the fixed front doors over
`pipeline/mailbox_writer.py`.
