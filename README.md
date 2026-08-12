# Claude + Codex Desktop

This repository is a small cooperation layer for exactly two coding surfaces:

- Claude Desktop, **Code** tab
- Codex in the ChatGPT desktop app

It has no provider launcher, custom coordination service, executable
runtime, or dependency stack. The desktop apps may still run normal project
commands in their integrated terminals.

## Fast path

1. Open the same Git repository in both desktop apps.
2. Choose one app as the lead for the task. Use an app-managed worktree for
   every independent writing session.
3. Let the lead commit to its own branch and open a pull request.
4. Open that branch or pull request in the other app and invoke
   `cross-app-review` (`/cross-app-review` in Claude or `$cross-app-review` in
   Codex).
5. Return findings through pull-request comments or the review summary. The
   lead owns fixes and final verification.

For a tiny, low-risk change, use one app and skip the handoff.

## Communication

| Need | Path |
|---|---|
| Question inside one Claude session | Side chat |
| Message between Claude Desktop sessions | Claude's native attributed session messaging |
| Work inside one Codex task | Codex's native thread/subagent flow |
| Move one Codex chat between foreground and isolation | Local/Worktree Handoff |
| Claude-to-Codex handoff | Branch or pull request with an exact diff |
| Durable discussion | Pull-request or issue comments |

There is no documented native Claude-session-to-Codex-thread message channel.
Git and GitHub are therefore the shared source of truth. Do not automate one
app's GUI from the other or add another messaging service just to relay text.

## Use each app where its desktop surface helps

- Claude Desktop is useful for parallel Code sessions, same-app messaging,
  visual previews, side chats, connectors, and pane-based diff review.
- Codex desktop is useful for parallel worktrees, Local/Worktree Handoff,
  detached code review, granular staging/reverting, plugins, and scheduled
  tasks.

Choose by the task and available app feature, not by fixed roles. For broad or
risky changes, having the other app review the exact diff is the simplest way
to combine their perspectives.

## Repository map

- [`AGENTS.md`](AGENTS.md): concise shared instructions read by Codex and
  imported by Claude.
- [`CLAUDE.md`](CLAUDE.md): Claude Desktop-specific additions.
- [`.agents/skills/cross-app-review/`](.agents/skills/cross-app-review/):
  Codex project skill.
- [`.claude/skills/cross-app-review/`](.claude/skills/cross-app-review/):
  equivalent Claude project skill.
- [`ARCHITECTURE.md`](ARCHITECTURE.md): capability research, limitations, and
  the reason for the minimal design.

Capability information and vendor sources were checked on 2026-08-12.

## License

Proprietary. All rights reserved.
