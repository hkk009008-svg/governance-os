# Architecture: two desktop apps, one Git truth

*Capability research last checked: 2026-08-12.*

## Purpose

This repository contains only the shared guidance needed for Claude Desktop
Code and Codex in the ChatGPT desktop app to cooperate on Git repositories. It
is documentation and app-discovered configuration, not an orchestration
runtime.

## Minimal topology

| Surface | Consumer | Responsibility |
|---|---|---|
| `AGENTS.md` | Codex; imported by Claude | Shared working and handoff rules |
| `CLAUDE.md` | Claude Desktop Code | Claude-only desktop behavior |
| `.agents/skills/cross-app-review/` | Codex desktop | On-demand review workflow |
| `.claude/skills/cross-app-review/` | Claude Desktop Code | Equivalent on-demand review workflow |
| `.claude/settings.json` | Claude Desktop Code | Require approval before peer messages leave the machine |
| `.github/pull_request_template.md` | Both through GitHub | Small durable handoff shape |

There is no service to start and no separate executable interface. Git history
preserves the removed system's historical record.

## Operating flow

```text
user task
  -> choose one lead app for this task
  -> isolated app-managed worktree and branch
  -> focused implementation and verification
  -> commit / pull request
  -> optional exact-diff review in the other app
  -> lead resolves findings
```

The flow intentionally has no permanent role system or custom coordination
service. The desktop apps and Git already provide the useful capabilities,
while the old layers made small changes expensive.

## Current desktop capabilities

### Claude Desktop Code

The current Code tab supports parallel sessions with automatic Git worktrees,
visual diffs and inline feedback, an integrated editor and terminal, browser
previews and auto-verification, side chats, local/cloud/SSH sessions,
connectors and plugins, scheduled local tasks, and optional computer use.
Claude can list and send attributed text messages to other reachable Claude
Code sessions. That messaging carries text, not files or conversation history;
receiver permissions still apply. Cross-session messaging has platform,
provider, and version constraints, including Claude Code 2.1.224+ and no native
Windows support in the documented cross-session channel. Computer use is a
macOS/Windows research preview for Pro and Max plans and requires app and OS
permissions.

Agent teams are unavailable in Desktop, so they are deliberately absent here.
Claude Desktop's own sessions, side chats, and dynamic workflows cover the
app-first use case.

### Codex in the ChatGPT desktop app

The current app supports parallel chats, managed and permanent Git worktrees,
Local/Worktree Handoff, visual diff review with per-hunk stage/revert controls,
detached review chats, project skills, plugins and MCP tools, a built-in
browser, optional computer use, local environment setup/actions configured in
the app, and scheduled background tasks. Computer use is limited to supported
regions on macOS and Windows, requires its plugin, and keeps system and app
approvals separate. Scheduled tasks can run against Local or an isolated
worktree; worktree mode keeps their mutations separate.

Handoff moves one Codex chat and its Git state between Local and its associated
worktree. It is not a message bus between independent chats. The vendor docs
reviewed do not expose a native message primitive from a Claude session to a
Codex thread.

## Cross-app communication

Git is the interoperability layer because both apps understand branches,
commits, diffs, and pull requests:

1. The lead app writes on its own branch.
2. It commits and exposes the exact branch or pull request.
3. The other app reviews that exact diff without editing by default.
4. Findings return as a review summary or pull-request comments.
5. The lead app makes fixes and verifies the final result.

For local-only work, a commit or branch is enough if both apps can access it.
For asynchronous or cross-machine work, use a pull request or issue. Configure
the same GitHub connector/plugin in each app when convenient; credentials and
account policy remain user-managed app settings.

A custom relay is intentionally excluded. A daemon, shared transcript scraper,
GUI driver, or local MCP bridge would add credentials, lifecycle management,
and failure modes while still needing Git to exchange code. Computer use is
useful for testing otherwise inaccessible GUIs, not for making one coding app
operate the other as a communication channel.

## Isolation and scheduling constraints

- App-managed worktrees do not share uncommitted changes. Commit before a
  cross-app review and identify the exact base/head or pull request.
- Never check out the same branch in two worktrees or let two agents write the
  same checkout.
- Local scheduled tasks in both apps require the desktop app to be running and
  the machine to be awake. Use them for narrow, reviewable work, not hidden
  cross-app coordination.
- Skills and repository instructions guide behavior; they do not grant account
  permissions or authorize pushes, merges, comments, connector writes, or
  computer control.

## Deliberately removed

- Every provider surface except the two desktop apps
- Standalone launch and adoption layers
- Fixed roles, capacity packets, handoffs, and status rituals
- Custom messaging, transport, locking, and relay services
- The Python governance package, tests, admission machinery, logs, and generated
  historical artifacts
- Product-specific target routing and unrelated domain skills

The repository should stay small. Add a file only when a repeated desktop-app
failure demonstrates that the existing instructions, skill, or pull-request
handoff is insufficient.

## Primary vendor sources

OpenAI:

- [ChatGPT desktop app](https://developers.openai.com/codex/app)
- [Worktrees and Handoff](https://developers.openai.com/codex/app/worktrees)
- [Local environments](https://developers.openai.com/codex/app/local-environments)
- [Code review](https://developers.openai.com/codex/app/review)
- [Scheduled tasks](https://developers.openai.com/codex/app/automations)
- [Skills](https://developers.openai.com/codex/skills)
- [AGENTS.md](https://developers.openai.com/codex/guides/agents-md)

Anthropic:

- [Claude Desktop Code](https://docs.anthropic.com/en/docs/claude-code/desktop)
- [Cross-session messaging](https://docs.anthropic.com/en/docs/claude-code/cross-session-messaging)
- [Skills](https://docs.anthropic.com/en/docs/claude-code/skills)
- [Project memory and CLAUDE.md](https://docs.anthropic.com/en/docs/claude-code/memory)
- [Desktop scheduled tasks](https://docs.anthropic.com/en/docs/claude-code/desktop-scheduled-tasks)
