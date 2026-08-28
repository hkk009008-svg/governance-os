# Pipeline repository manual

## Repository purpose

This repository provides a small desktop-app team transport, proportional
engineering governance, and reproducible local checks. Product behavior stays
in the selected target repository.

The interactive members are Codex, Claude, and AGY desktop apps. No terminal
command is a supported model-provider launch path.

## Top-level map

| Path | Purpose |
|---|---|
| `AGENTS.md` | Universal active team instructions. |
| `ARCHITECTURE.md` | Current implemented topology and trust boundaries. |
| `README.md` | Entry point for users. |
| `OPERATIONS.md` | Setup, daily operation, effects, troubleshooting. |
| `CLAUDE.md` | Thin Claude desktop adapter. |
| `RUNBOOK-DAILY.md` | Compact daily loop. |
| `DECISIONS.md` | Append-only architectural decisions. |
| `bin/pipeline` | Stable local command entry point and interpreter resolver. |
| `pipeline/` | Python implementation and checks. |
| `tests/` | Unit and integration contracts. |
| `docs/protocol/` | Current shared and app-specific protocol. |
| `.codex/config.toml` | Codex app MCP binding. |
| `.mcp.json` | Claude app MCP binding. |
| `.agents/plugins/pipeline-team/plugin.json` | AGY workspace-plugin registration. |
| `.agents/plugins/pipeline-team/mcp_config.json` | AGY workspace-plugin MCP binding. |
| `governance.toml` | Registered target repositories. |
| `coordination/` | Legacy conversation/cursors/receipts plus the fixed durable carrier reserved for formal review artifacts, real transfer checkpoints, and governed learning-candidate/disposition records. |

## Desktop team implementation

`pipeline/team.py` exposes `bin/pipeline team serve --member <configured-label>`
for the project MCP configs. Normal app use does not select a label through a
tool call; the config supplies it. The same local account can still launch a
different label, so this is routing metadata rather than identity attestation.

`pipeline/team_mcp.py` implements a minimal newline-delimited JSON-RPC/MCP
server with exactly three tools:

- `team_status` for orientation and sent-state inspection;
- `team_send` for validated queueing and replies;
- `team_wait` for replayable cursor reads, explicit acknowledgement, and bounded waiting.

`pipeline/team_messages.py` owns semantic validation: recipients, self-send
refusal, UTF-8 body limits, sender-scoped idempotency, valid reply ownership,
read limits, cursor rules, bounded waits, and the distinction between queued,
returned, and acknowledged.

`pipeline/team_store.py` resolves the exact Git worktree and common directory,
creates an owner-only `pipeline-team/messages.sqlite3` store, rejects symlinks
or permissive modes, initializes the schema, and records members, messages,
deliveries, and replies. It strips ambient `GIT_*` variables when resolving
repository identity.

The store is local shared state across linked worktrees. It is not committed,
signed, or an authority source.

## App bindings and preflight

Each binding points to `bin/pipeline team serve` with its own configured label:

| File | Function / configured label |
|---|---|
| `.codex/config.toml` | `codex` |
| `.mcp.json` | `claude` |
| `.agents/plugins/pipeline-team/plugin.json` | Registers the workspace plugin. |
| `.agents/plugins/pipeline-team/mcp_config.json` | `agy` |

Do not add model, credential, approval, sandbox, spend, or task authority to
these project bindings. Keep commands repository-relative and the member label
out of environment overrides; the configured label remains a non-attested
routing hint.

`pipeline/harness_preflight.py` checks:

1. recognized desktop app bundles and versions;
2. the three project config shapes and configured labels;
3. a real MCP initialize handshake for each adapter in a temporary Git repo;
4. Codex and Claude's native MCP configuration views;
5. exact Antigravity workspace registration;
6. the AGY team-tool permission needed for uninterrupted calls.

`pipeline/native_app_readiness.py` owns those native-view, workspace, and
permission checks. `agy mcp list` is deliberately not used because it reports
user-global servers rather than the workspace `pipeline-team` plugin. The
preflight launches only local configuration/adapter checks. It does not open a
desktop app, launch a model provider, send a team message, spend, or establish
liveness. Pipeline never edits the user's Antigravity permission policy.

## Governance implementation

`pipeline/codex_protocol_model.py` owns the closed risk profiles, model-family
mapping, work-mode descriptions, and external-effect token shape. Unknown
model families cannot satisfy different-family review.

`pipeline/compact_pair_loop.py` owns formal exact-range request/report parsing
and validation. New work uses temporary `author` and `reviewer`
responsibilities only at the material/high-risk boundary. Historical seat
names remain accepted only where required to read committed evidence.

AGY can direct, implement, test, and review evidence but cannot be the sole
independent formal verdict or authority source. Codex or Claude supplies the
non-author formal reviewer; high-risk review also requires a different model
family and abuse-class analysis.

Push, merge, release, paid spend, live-data mutation, and destructive
operations are separately authorized effects. Transport, review, tests, and
configuration do not grant them.

## Local command surface

Discover the current verbs rather than copying stale argument lists:

```bash
bin/pipeline --help
bin/pipeline <verb> --help
```

Common checks:

```bash
bin/pipeline status
bin/pipeline preflight
bin/pipeline check --fast
bin/pipeline check docs
bin/pipeline check arch
bin/pipeline check
```

The shell entry point clears `GIT_INDEX_FILE` and resolves the primary
checkout's interpreter, including from a linked worktree. Each worktree uses
its native Git index.

## Making a change

1. Read current instructions and inspect fresh Git status/diff.
2. Identify whether another member already owns overlapping paths.
3. Write a failing behavior test when feasible for behavior changes.
4. Make the smallest coherent implementation.
5. Run focused tests and inspect the exact diff.
6. Classify risk by behavior, not line count.
7. Obtain temporary exact-range review only when required.
8. Run one proportionate final pass and report exact results.

Parallelize read-only or nonoverlapping work; serialize shared-file edits. Do
not add a mode, event, packet, role board, or handoff to ordinary work.

## Testing

Use the repository interpreter through `bin/pipeline` or
`coordination/bin/pipeline-python` where an individual test command requires
Python. Focused desktop-team tests include the team store, message layer, MCP
adapter, app config integration, and preflight. The aggregate remains
`bin/pipeline check`.

Run `git diff --check` on edited paths. Search active docs for removed CLI
launcher, standing-seat, mailbox-as-current-transport, and peer-receipt claims.
Do not describe a passing local adapter handshake as proof that all apps are
open or that end-to-end substantive communication occurred.

## Documentation placement

- Universal behavior belongs in `AGENTS.md` or `docs/protocol/agents/`.
- Current component facts belong in `ARCHITECTURE.md`.
- App mechanics belong in their continuation adapter and project config.
- Transport semantics belong in `pipeline/team_*` and
  `docs/protocol/peer.md`.
- Risk/effect rules belong in `pipeline/codex_protocol_model.py` and the risk
  doc.
- Product facts belong in the target repository.
- A durable architectural choice appends one ADR to `DECISIONS.md`.

Avoid copying the same rule into more files than users need. When code and
prose disagree, establish current behavior and correct the stale active doc.

## Legacy boundary

Mailbox conversation, cursor files, capacity packets, old four-seat prompts,
peer-launch receipts, historical handoffs, plans, and logs remain for audit and
compatibility. Do not rewrite historical evidence. The fixed mailbox writer is
used only for a risk-required exact-range formal artifact, a real transfer
checkpoint, or the governed learning-candidate/disposition lifecycle, never
routine team communication, standing roles, or authority.

Normal continuation is the desktop task plus Git and tests. One concise
checkpoint is reserved for a real ownership transfer, interruption, compaction,
or wrap where another member must resume.

## Targets

Resolve target repositories with:

```bash
bin/pipeline target
```

Then read the target's own instructions. Pipeline governs collaboration; it
does not infer product ownership or external-effect authority from a target
binding.
