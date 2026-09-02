# Pipeline operations

This runbook operates the Codex, Claude, and AGY desktop-app team. It does not
contain a provider launch path.

## Readiness

Open the same repository in any or all three apps. Their checked-in MCP
bindings supply distinct member labels; do not copy one member's binding over
another.

On Antigravity's first open, use Open Folder for this exact repository, then
refresh and approve the workspace `pipeline-team` server. To let AGY
communicate without pausing at every tool call, explicitly allow
`mcp(pipeline-team/*)`. This is a global, name-based user permission: avoid the
same server name in untrusted workspaces. Pipeline checks it but never writes
permission policy.

Run the local preflight when setup changed or communication fails:

```bash
bin/pipeline preflight
```

It checks app installation, config shape, configured labels, a real MCP
initialize handshake, Codex and Claude's native config views, Antigravity's
exact workspace registration, and AGY's team-tool permission. These are
configuration proxies; after Antigravity first registers the folder, confirm
`pipeline-team` is connected in Installed MCP Servers. No row proves that a
desktop window or model session remains live.

## Begin or resume work

1. Read the current user task.
2. Inspect `git status --short --branch`, the relevant diff, and recent task
   history.
3. Call `team_status` once.
4. Read addressed messages with `team_wait` after the last cursor you handled.
5. Start the scoped work. Do not reconstruct a role board or process an entire
   legacy mailbox.

Git, tests, and desktop task history are normal state. A checkpoint is needed
only when another member must take over after transfer, interruption,
compaction, or wrap.

## Communicate

Use `team_send` for a bounded request, result, challenge, coordination note, or
reply. Address one member when ownership is clear; use `all` only when every
member needs the same information.

Include enough context to act: objective, relevant paths or commit, what was
observed, and the requested response. Do not paste hidden chain-of-thought or a
large transcript. Link a reply with `reply_to` so status can show the exchange.

State interpretation:

| Observation | Meaning |
|---|---|
| `team_send` returns `queued` | Stored successfully; no acknowledgement claim. |
| Recipient appears in `acknowledged_by` | Its adapter advanced `after_id` through the message. |
| A reply id appears | A response was queued; inspect its content. |
| `last_seen` changed | Recent tool activity, not proof the app is open. |

If an answer is required, wait at a natural boundary with `team_wait` or
continue independent work and check later. Never convert a timeout into assent,
acknowledgement, a globally empty queue, or authority.

## Implement

Keep ordinary work direct. Parallelize read-only investigation and
nonoverlapping paths when useful. Give one member ownership of integration and
serialize shared-file or shared-resource writes.

Use a failing behavior test when feasible, focused checks while iterating, and
one final proportionate pass. Investigate unexpected failures before changing
behavior. Preserve unrelated work and inspect the exact diff before handoff or
commit.

Useful local commands:

```bash
bin/pipeline --help
bin/pipeline status
bin/pipeline doctor
bin/pipeline check --fast
bin/pipeline check
bin/pipeline check docs
bin/pipeline check arch
```

These commands operate on the repository. None is a provider-launch command.
The default doctor and coordination check report current desktop-team state.
Use their `--history` option only for retired cursor, pre-cutover review, and
route-lineage diagnostics.

## Review

Ordinary local work has no formal role. For `material-behavior` or
`high-risk-control`, temporarily assign the candidate owner as `author` and a
non-author Codex or Claude member as `reviewer`. Bind review to the exact
committed base and head. High-risk review also needs a different model family
and explicit abuse-class assessment.

AGY may map, test, challenge, review evidence, and propose fixes. Material AGY
findings must be dispositioned on their merits, but AGY cannot publish the sole
formal GO/NITS/FAIL result or grant authority. End the responsibilities when
the range is resolved.

## Effects

Before push, merge, release, paid spend, live-data mutation, or a destructive
operation, resolve exact authority for:

- executor;
- target;
- effect;
- scope.

If any element is missing, stop before the effect and ask the user. A team
message, old approval, role label, review, or test cannot fill a blank.

## Transfer and close

For a real transfer, leave one concise checkpoint containing objective, scope,
owner, base/head, evidence, verification status, blockers, and next executable
action. Prefer the desktop task history. When the record must outlive that task,
use `bin/pipeline checkpoint` to draft it and the fixed `bin/pipeline mail send`
writer to persist it. That writer is also available for a risk-required exact-
range formal review artifact or governed learning-candidate/disposition record,
never routine chat or standing-seat workflow.

At ordinary completion, report changed files, tests actually run, remaining
limitations, and any effects not performed.

## Troubleshooting

- Missing tool: verify the app opened this repository, approve or reload its
  workspace MCP server, and run `preflight`.
- AGY permission failure: approve the exact `mcp(pipeline-team/*)` scope in
  Antigravity only if interruption-free use is desired and same-named servers
  in other workspaces are trusted. Do not use broad `mcp(*)` merely to make the
  check green.
- Wrong label: repair the app's project config. Labels come from args but are
  local coordination hints, not attestation.
- Queued but unacknowledged: the recipient has not advanced its cursor through it.
- Acknowledged without useful reply: send a precise follow-up or continue without
  claiming agreement.
- Store permission or symlink refusal: inspect the repository Git common
  directory's `pipeline-team` entry; keep it owner-only and do not bypass the
  check.
- Legacy mailbox conversation or receipt conflict: treat it as historical
  evidence and use current Git/task state plus MCP for routine work. Preserve
  only a required formal artifact, real transfer, or governed learning record
  through the fixed writer.
