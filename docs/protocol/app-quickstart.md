# Desktop app quick start and capability map

This is the short operating guide for Claude, Codex, AGY (Antigravity), and
Cursor in Pipeline. It describes app capabilities verified from vendor sources
on 2026-08-09 and the locally installed versions observed that day. The
provider continuation adapters remain the detailed mechanics.

App capability is not Pipeline authority. A session, thread, subagent,
worktree, comment, scheduled task, selected model, or native message does not
assign a role, approve a review, publish a protocol event, or authorize an
external effect.

## The three-minute start

1. Open the exact checkout or app-owned worktree that contains the work. A new
   worktree does not inherit another checkout's uncommitted files.
2. Begin as readiness unless the task explicitly assigns Director, Operator,
   or Coordinator. Run `python3 scripts/status.py snapshot` (or add the assigned
   seat as the final argument) and inspect the current root, HEAD, scoped
   status, and actionable event bodies.
3. Use the app's native subagents, side questions, comments, and peer messages
   for transient work inside that app. Keep writers file-disjoint and use an
   isolated worktree when more than one agent may edit.
4. Use `coordination/bin/send-event` for formal requests/reports, durable
   transfers or decisions, and every message another provider must see. It
   stages only: separately commit and land the containing change, then
   synchronize the receiving checkout before expecting cross-provider
   visibility. Only an assigned receiving role consumes its cursor.
5. Push, merge, lock, consume, provider launch, paid/remote execution,
   connector mutation, and live-data changes remain separately authorized.

## Which app to use

| Side | Best native use | Same-app coordination | Isolation and review | Current caveat |
|---|---|---|---|---|
| Claude Desktop Code | Several local coding sessions, visual diffs/previews, direct peer relay | Named sessions can list and message one another; `/btw`, named advisors, and small dynamic workflows handle bounded side work | Desktop creates per-session Git worktrees | Pipeline has no Claude governance-seat registry. Standalone CLI peer relay requires 2.1.224+ |
| Codex in the desktop app | Parent-led multi-agent investigation/implementation, long-running work, broad tool and plugin use | The host can dispatch subagents, deliver follow-ups, wait, and hand work between tasks without user copy-paste | Built-in worktrees plus Local/Worktree Handoff and in-thread diff review | Worktree handoff performs Git operations; Automations, Remote, and plugins keep their own effect/data boundaries |
| Antigravity / AGY | Artifact-led planning and implementation with rich human feedback | The root agent delegates to native subagents and receives their results; saved slash workflows remove repeated prompts | Desktop Projects or IDE conversations, plan/task/diff/walkthrough artifacts, comments, undo | Native helpers are parent-scoped, not formal seats; schedules/browser/MCP/provider runs may spend or mutate |
| Cursor Desktop | IDE-native coding, code intelligence, visual/design feedback, multi-model work | Tiled Agents Window, custom subagents, `/multitask`, and durable side chats | Linked worktrees, local Agent Review, diffs, terminals, IDE diagnostics | Do not open a side chat in a reserved seat worktree: its new conversation may supersede the pinned seat binding |

The differentiators below are comparative, not exclusive marketing language:

- Claude's useful differentiator here is direct, attributed messaging between
  independently started same-machine sessions.
- Codex's is explicit task-tree coordination plus a first-class Handoff that
  moves one chat between Local and its app-managed worktree.
- Antigravity's is its commentable plan, task, diff, walkthrough, screenshot,
  and browser-recording artifact loop combined with workspace slash workflows.
- Cursor's is the deepest IDE surface: code intelligence and Tab completion,
  tiled agents, transcript search, Design mode, and multiple model families in
  the same editor.

## Claude Desktop Code

### Set up and start

1. Open **Code**, choose **Local**, select the exact Pipeline checkout, and
   start in Manual or Plan mode.
2. Create and rename a session for new independent work; let Desktop create its
   isolated worktree. Resume the owning session for an existing dirty
   candidate.
3. Run the compact status snapshot. A role in a session name is a label until
   the task explicitly assigns it.

### Use the app well

- Ask Claude to “tell `<session name>` …” for transient findings, status, or a
  bounded question. The receiving session's permissions still apply; the
  message cannot approve anything, change configuration, execute a slash
  command, or bring the sender's files/history with it.
- Use `/btw` for a disposable side question. For a bounded advisor, ask Claude
  to delegate to `readiness-bridge`, `lane-v-verifier`,
  `money-gate-reviewer`, or `amnesiac-prober`. Use a small dynamic workflow
  only when several independent, file-disjoint questions justify it.
- Use the integrated terminal/editor, visual diff, browser/preview, and PR
  monitor. Review Code helps self-review; it is not the non-author Operator.
- Agent teams remain a CLI-only experimental mechanism and are unnecessary for
  this path. Dispatch, cloud sessions, scheduled tasks, connectors, computer
  use, auto-fix, and auto-merge are optional effects, not implied defaults.

For durable or cross-app communication, publish through `send-event`; do not
ask the user to copy a Claude peer message into another app.

## Codex desktop

### Set up and start

1. Open the Pipeline project and start a Local chat when it must own the current
   checkout. Choose Worktree for independent background work.
2. Keep one parent responsible for the requested outcome. Give subagents
   concrete, bounded, non-overlapping ownership and let the host deliver their
   results and follow-up instructions.
3. Use Handoff to move that same chat between Local and its worktree only when
   moving the Git state is intended. Inspect the resulting diff before landing.

### Use the app well

- Use native task discovery, dispatch, follow-up, waiting, interruption, and
  handoff instead of asking the user to relay text between Codex tasks.
- Use app worktrees for independent writers; use parent-scoped subagents in one
  task for read-only mapping, adversarial review, or file-disjoint production.
  The parent reconciles the result.
- Use diff comments, integrated terminal output, files/images, skills, approved
  plugins, browser research, and remote mobile steering as context surfaces.
- Use Scheduled/Automations first for read-only recurring triage or monitoring.
  A scheduled mutation, network effect, or paid service still needs exact
  authority and a narrow sandbox.

Codex task delivery is transient host coordination. Formal review state and
all Claude/AGY/Cursor-visible messages still use `send-event`.

## Antigravity / AGY

### Set up and start

1. Open the exact Pipeline folder as an Antigravity Desktop Project or in the
   IDE, then choose the project security, artifact-review, terminal, and MCP
   permissions appropriate to the task.
2. Invoke `/pipeline-start`, the workspace workflow in
   `.agents/workflows/pipeline-start.md`. It uses the already-open AGY
   conversation for read-only orientation and returns the next lawful action
   without launching another provider process, consuming a cursor, or
   publishing an event.
3. Use the implementation plan, task list, diff, and walkthrough artifacts as
   the feedback loop. Submit inline comments; an unsubmitted comment does not
   reach the agent.

### Use the app well

- Delegate independent research or file-disjoint checks to native subagents and
  let the root agent relay results. Helpers remain parent-scoped advisors, not
  Director/Operator/Coordinator seats.
- Save repeated prompts as workspace workflows under `.agents/workflows/` and
  reusable domain procedure as a skill under `.agents/skills/`. Keep standing
  policy in the existing router instead of cloning it into every workflow.
- Use **Send to Agent** from Problems or selected terminal output, commentable
  artifacts, browser verification, and walkthrough screenshots/recordings to
  reduce manual context transcription.
- `/goal`, `/schedule`, browser subagents, MCP tools, headless AGY, and live
  model/provider launch are optional capabilities. They do not waive spend,
  credential, data-access, or external-effect boundaries.

Subagent reports and artifact comments stay inside AGY. Anything formal,
durable, or addressed to another provider goes through `send-event`.

## Cursor Desktop

### Set up and start

1. Open **Agents Window**. Keep only the standing `director` and `operator`
   chats pinned in their reserved linked worktrees; create capacity seats only
   when parallel load earns them.
2. Select an explicit model for each governed seat. Auto is useful for ordinary
   work, but its routed model can be hidden; high-risk author/reviewer work uses
   explicit recognized different-family model IDs.
3. Let `sessionStart` bind the top-level conversation, run the compact snapshot,
   and use `/review-next` in the pinned Operator chat for the normal review
   handoff.

### Use the app well

- Tile agents and the editor/diff/terminal; use diagnostics, Problems,
  transcript search, Design mode, and local Agent Review to keep evidence in
  view.
- Use custom read-only subagents for bounded work inside a bound seat. Use
  `/multitask` only for independent work, and do not assume it prevents agents
  from editing the same file.
- Side chats (`/side` or `/btw`) are useful in readiness/unreserved workspaces.
  Do not create one inside a reserved seat worktree: every new conversation can
  run `sessionStart`, and Pipeline's newest-conversation binding may deactivate
  the pinned top-level seat. Use a custom subagent there instead.
- Project shell and MCP hooks enforce their documented boundary. Native file
  edits outside a bound Director are denied because Cursor does not currently
  enforce `preToolUse`'s `ask` result; use a separately approved shell mutation
  or move the work to a bound Director. Every well-formed MCP call surfaces an
  approval because Cursor does not document a child discriminator on that hook.
  The card is invocation consent, not external-effect authority; the task must
  separately authorize the exact target and scope.
- Cloud agents, mobile/remote work, Automations, Slack/Teams, and background
  agents are remote and potentially paid. They require explicit setup and are
  not part of the standing pair.

The official Cursor surfaces reviewed on 2026-08-09 did not document a way to
wake and submit into another existing local top-level seat chat. Activate the
pinned Operator and run `/review-next`; do not build a relay daemon for one
click.

## Cross-app communication without another messaging layer

| Side | Same-app low-friction path | Different-model use | Cross-app path |
|---|---|---|---|
| Claude | Ask one named session to message another; use `/btw` or a bounded advisor for side work | Select the needed model per independent session, then use the native peer message | `send-event` → commit/land → receiver sync |
| Codex | Parent task dispatch, follow-up, wait, and handoff; subagents report to the parent | Choose an explicit model for a bounded task when the host exposes that choice; keep formal independence evidence separate | `send-event` → commit/land → receiver sync |
| AGY | `send_message` to a known conversation ID; parent/child results auto-wake and return natively | Use the plan-available model selector or `inherit`/`flash`/`pro` helper tier; a tier label is not model-family proof | `send-event` → commit/land → receiver sync |
| Cursor | Custom subagent or readiness side chat; activate an existing pinned seat manually | Pin explicit model families in separate top-level chats for high-risk author/reviewer work | `send-event` → commit/land → receiver sync |

`send-event` above means the validated
`coordination/bin/send-event` front door, not a raw mailbox write. `send-event`
stages but does not commit or land. Same-app messages are convenient and
transient; an event becomes durable when committed and becomes cross-provider
visible only after its containing commit is landed and the receiving checkout
is synchronized to a ref containing it.

| Need | Use |
|---|---|
| Disposable question to the same parent | Side question or parent-scoped subagent |
| Status/finding for another session in the same app | Native session/task message or follow-up |
| Formal verify request/report or durable decision | `send-event`, then separately commit and land/sync as required |
| Message another provider must see | `send-event`, then land the commit and synchronize the receiver |
| Read current cross-provider state | `python3 scripts/status.py snapshot [seat]`, then read named event bodies |
| Advance a role cursor | Only the assigned receiver, through `coordination/bin/consume-events` with separate authority |

Do not add a generic relay daemon, shared chat transcript scraper, GUI driver,
or second mailbox. Native channels solve ephemeral same-app friction; the fixed
writer already solves durable cross-app communication.

## Local installation snapshot

Observed read-only on 2026-08-09; this is an inventory record, not a promise
that every account/feature flag exposes every capability.

| Side | Desktop bundle | CLI |
|---|---|---|
| Claude | `com.anthropic.claudefordesktop` 1.26832.0 | Claude Code 2.1.220 |
| Codex | `com.openai.codex` 26.803.41515 | `codex-cli` 0.146.0 |
| AGY | Desktop `com.google.antigravity` 2.5.0; IDE 2.1.1 | `agy` 1.1.11 |
| Cursor | `com.todesktop.230313mzl4w4u92` 3.15.6 | `cursor` 3.15.6 |

Claude Desktop is above the documented 1.2581.0 floor for the current Code-tab
layout. The standalone Claude Code CLI is below the 2.1.224 peer-messaging
floor; upgrade is a separate provider/network action and was not performed by
this change. The Codex bundle is installed at `/Applications/ChatGPT.app`
despite its `com.openai.codex` identifier. Antigravity Desktop 2.6.0 is the
current vendor release while the installed bundle is 2.5.0; update separately
before relying heavily on its multi-agent mesh. No application was updated by
this work.

## Primary vendor sources

- Anthropic: [Desktop](https://code.claude.com/docs/en/desktop),
  [cross-session messaging](https://code.claude.com/docs/en/cross-session-messaging),
  [settings](https://code.claude.com/docs/en/settings), and
  [agent teams](https://code.claude.com/docs/en/agent-teams).
- OpenAI: [Codex app introduction](https://openai.com/index/introducing-the-codex-app/),
  [worktrees and Handoff](https://learn.chatgpt.com/docs/environments/git-worktrees),
  [scheduled tasks](https://learn.chatgpt.com/docs/automations), and
  [mobile Remote](https://help.openai.com/en/articles/6825453-chatgpt-release-notes).
- Google: [Antigravity overview](https://antigravity.google/docs/overview),
  [Projects](https://antigravity.google/docs/projects),
  [subagents](https://antigravity.google/docs/subagents),
  [workflows](https://antigravity.google/docs/ide/workflows), and
  [hooks/native tools](https://antigravity.google/docs/hooks), plus the
  [release changelog](https://antigravity.google/changelog?app=antigravity).
- Cursor: [Agents Window](https://cursor.com/changelog/3-0),
  [side chats and search](https://cursor.com/changelog/side-chat),
  [Cursor Router](https://cursor.com/changelog/router), and
  [hooks](https://cursor.com/docs/hooks).
