# Supported desktop apps

Pipeline supports Claude Desktop Code and the Codex desktop app. App
capability is not Pipeline authority: a session, task, subagent, worktree,
message, selected model, or scheduled run does not assign a role, approve a
review, publish an event, or authorize an external effect.

## The three-minute start

1. Open the exact checkout or app-owned worktree containing the work.
2. Begin as readiness unless the task explicitly assigns Director, Operator,
   or Coordinator. Run `python3 scripts/status.py snapshot` and add the exact
   seat only when assigned.
3. Use native subagents, side questions, and peer messages for transient work.
   Keep writers file-disjoint and isolate concurrent writers in worktrees.
4. Use `coordination/bin/send-event` for formal requests, reports, transfers,
   and cross-provider decisions. It stages but does not commit or land. A
   receiving checkout sees the event only after the containing commit lands
   and that checkout synchronizes to it.
5. Push, merge, lock, cursor consumption, provider launch, paid execution, and
   live-data changes remain separately authorized.

## Which app to use

| Side | Best native use | Same-app coordination | Isolation |
|---|---|---|---|
| Claude Desktop Code | Several local coding sessions, visual diffs, and direct peer relay | Named sessions can message one another; `/btw` and bounded advisors handle side work | Desktop creates per-session Git worktrees |
| Codex desktop | Parent-led investigation and implementation with broad local tools | Task discovery, follow-up, waiting, interruption, and handoff keep work inside the task tree | Built-in Local and Worktree execution plus diff review |

Claude's differentiator here is direct, attributed messaging between
independently started same-machine sessions. Codex's is task-tree coordination
plus a first-class handoff between Local and an app-managed worktree.

## Claude Desktop Code

1. Open Code, choose Local, select the exact checkout, and start in Manual or
   Plan mode.
2. Create a new session for independent work; resume the owning session for an
   existing dirty candidate.
3. Run the compact status snapshot. A role in a session name remains a label
   until the task explicitly assigns it.

Use named peer messages for transient findings and status. Use `/btw` for a
disposable question and a bounded advisor for focused read-only analysis. The
receiving session's permissions still apply, and transient messages carry
neither files nor role/effect authority. For durable or cross-app
communication, use `send-event`.

## Codex desktop

1. Start a Local task when it must own the current checkout; choose Worktree
   for independent background work.
2. Keep one parent responsible for the outcome and give helpers concrete,
   bounded, non-overlapping ownership.
3. Use Handoff only when moving that task's Git state is intended, then inspect
   the resulting diff before landing.

Use task discovery, follow-up, waiting, interruption, and handoff instead of
asking the user to relay text between Codex tasks. Automations, remote work,
plugins, browser actions, and connector mutations keep their own data, spend,
and effect boundaries. Formal review state still goes through `send-event`.

## Cross-app communication

| Need | Use |
|---|---|
| Disposable question to the same parent | Side question or parent-scoped subagent |
| Status for another session in the same app | Native session/task message |
| Formal request, report, or durable decision | `send-event`, then separately commit and land/synchronize |
| Read current shared state | `python3 scripts/status.py snapshot [seat]`, then read named event bodies |
| Advance a role cursor | The assigned receiver through `coordination/bin/consume-events`, with separate authority |

Do not add a relay daemon, chat scraper, GUI driver, or second mailbox. Native
channels solve transient same-app coordination; the fixed writer owns durable
cross-app state.

## Local installation snapshot

Observed read-only on 2026-08-09; versions may drift.

| Side | Desktop bundle | CLI |
|---|---|---|
| Claude | `com.anthropic.claudefordesktop` 1.26832.0 | Claude Code 2.1.220 |
| Codex | `com.openai.codex` 26.803.41515 | `codex-cli` 0.146.0 |

Claude Desktop was above the documented 1.2581.0 floor for the Code-tab
layout. The standalone Claude Code CLI was below the 2.1.224 peer-messaging
floor; any upgrade is a separate provider/network action. No application was
updated by this record.

## Primary vendor sources

- Anthropic: [Desktop](https://code.claude.com/docs/en/desktop),
  [cross-session messaging](https://code.claude.com/docs/en/cross-session-messaging),
  [settings](https://code.claude.com/docs/en/settings), and
  [agent teams](https://code.claude.com/docs/en/agent-teams).
- OpenAI: [Codex app introduction](https://openai.com/index/introducing-the-codex-app/),
  [worktrees and Handoff](https://learn.chatgpt.com/docs/environments/git-worktrees),
  [scheduled tasks](https://learn.chatgpt.com/docs/automations), and
  [mobile Remote](https://help.openai.com/en/articles/6825453-chatgpt-release-notes).
