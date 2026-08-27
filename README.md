# Pipeline

Pipeline is a small engineering harness for the Codex, Claude, and AGY
(Antigravity) desktop apps. The three apps share one repository-scoped MCP
conversation, direct work together, and use the strengths of each app without
creating permanent seats or a coordination bureaucracy.

Pipeline is the governance kernel; evidence-ledger is the bound product target
by default, while `bin/pipeline target` can select another registered target.

All three members may reason, direct, implement, test, and challenge. Codex is
well suited to workspace integration and sustained orchestration; Claude to
large-context reasoning and independent review; AGY to fast mapping, debugging,
browser/artifact work, and premise or evasion challenges. These are routing
hints, not job restrictions.

## What is supported

- Interactive work happens in the three desktop apps only.
- App-to-app communication uses `team_status`, `team_send`, and `team_wait`.
- Repository implementation uses normal Git worktrees, local tools, and tests.
- Formal author/reviewer responsibilities exist only for a risk-triggered exact
  range.
- Legacy mailbox conversation, cursors, seats, and peer receipts remain
  compatibility evidence; the fixed mailbox writer is reserved for three
  narrowly governed uses: a required formal review artifact, a real
  transfer/checkpoint `findings` event, or the governed
  learning-candidate/disposition lifecycle.

Pipeline does not launch a model provider from the terminal or run another app
as a headless child. A terminal remains useful for deterministic builds, tests,
Git, and harness preflight.

## Start

Open the repository in the desktop app you want to use. The checked-in project
configuration supplies that app's normal team label:

| App | Project binding | Member |
|---|---|---|
| Codex | `.codex/config.toml` | `codex` |
| Claude | `.mcp.json` | `claude` |
| AGY | `.agents/plugins/pipeline-team/plugin.json` + `.agents/plugins/pipeline-team/mcp_config.json` | `agy` |

Antigravity loads the repository-scoped server from that workspace plugin's
manifest and MCP config. The first time it opens this repository, refresh and
approve the workspace `pipeline-team` server if prompted. To meet the
interruption-free team goal, the user must allow `mcp(pipeline-team/*)` in
Antigravity. That rule is global and name-based, so use the same server name
only in trusted workspaces. Pipeline reports the state but never edits user
permissions.

In the app, call `team_status`, then use `team_wait` to read pending messages.
Use `team_send` directly when another member can help or needs an update. Queue
success is not acknowledgement, acknowledgement is not understanding, and a reply is not
necessarily substantive. Concurrent instances of one member may receive the
same row before either receipt commits; deduplicate by message id. Labels are
not app/model attestation, and no team message grants permission or authority.

For local readiness and repository checks:

```bash
bin/pipeline preflight
bin/pipeline status
bin/pipeline check --fast
bin/pipeline check
```

`preflight` checks installed app bundles, all three app bindings (including
AGY's workspace plugin manifest and MCP config), a real adapter handshake,
Codex and Claude's native config views, Antigravity's exact workspace
registration, and its team-tool permission. These are configuration proxies,
not proof that a desktop window, AGY's Installed MCP Servers panel, or a model
session is live. The check does not launch a model, send, or spend.

## Work loop

1. Read the accepted task and inspect fresh Git state.
2. Choose the simplest sufficient implementation.
3. Split only genuinely independent or file-disjoint work.
4. Use focused tests while iterating; inspect the exact diff.
5. At the risk boundary, temporarily name an author and a non-author Codex or
   Claude reviewer. AGY findings remain first-class evidence but cannot be the
   sole formal verdict.
6. Run one proportionate final verification pass.

Push, merge, release, paid spend, live-data mutation, and destructive
operations need exact current task/user authority. Transport state, a green
test, or an old approval cannot grant it.

Git, tests, and desktop task history are the normal continuation record. Create
one concise checkpoint only for a real transfer, interruption, compaction, or
wrap where another member must resume.

## Documentation

- `AGENTS.md` — active team contract
- `ARCHITECTURE.md` — implemented system and trust boundaries
- `OPERATIONS.md` — operating procedures and troubleshooting
- `docs/GUIDEBOOK.md` — practical collaboration patterns
- `docs/PROGRAM-MANUAL.md` — governance model
- `docs/REPOSITORY-MANUAL.md` — code and repository map
- `docs/protocol/peer.md` — desktop-team message contract
- `docs/protocol/agents/risk-classes.md` — review and effect boundaries

Executable code and current repository state outrank prose when they disagree.
