---
description: Orient Pipeline read-only and return the next lawful local action
---

# Pipeline start

Use this saved workflow to orient the current Pipeline checkout without
creating protocol or external state.

1. Read `AGENTS.md`, then `docs/protocol/agy/continuation.md`. Load only the
   skill that matches the requested work.
2. Confirm the current repository root and HEAD. Run:

   ```bash
   python3 scripts/status.py snapshot
   ```

   If the task explicitly assigns a receiving seat, rerun the snapshot with
   that exact seat as the final argument and read the actionable event bodies
   it names. Do not infer or claim a seat.
3. Report the current posture, root, HEAD, scoped dirty paths, actionable
   request or blocker, and the single next lawful action.
4. For several independent questions, use Antigravity native subagents and
   return their findings to the root conversation. They are parent-scoped
   helpers, not formal seats; keep writers file-disjoint.

This workflow is read-only. Do not publish or consume an event, launch a
provider, push, merge, lock, spend, schedule work, or mutate live data. Those
actions require their own exact authority after orientation.
