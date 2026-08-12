# Claude + Codex desktop guide

This repository supports only Claude Desktop Code and Codex in the ChatGPT
desktop app. Codex reads this file directly. Claude reads it through the import
in `CLAUDE.md`.

## Default loop

1. Pick one app to lead the task. Do not assign permanent roles or create a
   coordination ceremony.
2. Give every independent writer its own app-managed Git worktree and branch.
   Never let two sessions edit the same checkout or branch concurrently.
3. Keep one owner responsible for the final result. Parallel work should be
   read-only or file-disjoint and should return to that owner.
4. Inspect the exact diff and run the smallest relevant verification before
   calling work done.
5. Use the other desktop app for review when the change is broad, risky, or the
   user asks. Trivial changes do not need a cross-app handoff.

## Communication

- Use native app channels for transient same-app coordination: Claude session
  messages and side chats, or Codex task/subagent results and Handoff.
- Use a commit, branch, pull request, or issue for anything the other app must
  see. Uncommitted files in one worktree are not visible in another.
- A useful handoff states the goal, exact base and head (or PR), change summary,
  verification, open risks, and the next requested action.
- Use `cross-app-review` for a focused read-only review. The authoring app owns
  any fixes unless the user explicitly transfers implementation.
- Publish comments, push, merge, schedule work, or mutate external systems only
  when the task authorizes that effect.

## Working rules

- Follow the user's accepted scope; preserve unrelated work.
- Start behavior changes with a focused failing test when practical. Otherwise
  record what was checked and why a test was not feasible.
- Establish root cause before changing behavior after an unexpected failure.
- Prefer app-native worktrees, diffs, review panes, previews, and connectors to
  custom orchestration.
- Report evidence and uncertainty plainly. Do not invent a successful message,
  review, test, or delivery.

## Scope boundary

Keep this desktop-only. Do not add another provider, an app launcher, or a
custom coordination service. Normal build, test, Git, and debugging commands
may still run inside either desktop app's integrated terminal.
