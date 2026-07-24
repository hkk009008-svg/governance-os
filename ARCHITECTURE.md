# ARCHITECTURE.md - Governance OS

> Truth lives here. AGENTS.md and CLAUDE.md are process layers; this file is
> the verified truth layer for the Pipeline governance kernel. When process
> prose and this file disagree about Pipeline facts, this file wins and the
> stale prose must be fixed in the same change.

*Last verified: 2026-07-24 @ 9692129c21d2b65a5fc35503969a6f3b5f237f74*

## 1. Purpose

Pipeline is the governance kernel for multi-seat AI coding work. It provides
durable mailbox routing, live seat status, route capacity packets, protocol
verification gates, and provider bridge mechanics. It is intentionally separate
from private product repositories: evidence-ledger is the bound default target,
while Pipeline owns the coordination harness around that target.

ARCHITECTURE.md records verified governance-kernel truth. Product behavior
truth belongs in each product repository's own docs and tests.

## 2. Topology

Primary control flow:

```text
user or parent prompt
  -> readiness or named-seat orientation
  -> active outcome contract + durable owner
  -> seat-chosen implementation, collaboration, or ownership exchange
  -> committed actual change + outcome-bound verify-request
  -> distinct-identity non-author Operator GO/NITS/FAIL with finding dispositions
  -> separately user-authorized exact external-effect tuple, if any
```

Key directories:

| Path | Role |
|---|---|
| `scripts/` | Executable governance tooling: smoke, doc checks, mailbox monitoring, route validation, capacity board, and provider adapters. |
| `coordination/` | Durable protocol state: mailbox events, seen cursors, presence, capacity packets, and shell mailbox tools. |
| `.agents/skills/` | Repo skills for four-seat operation and seat-specific authority. |
| `.codex/agents/` | Codex role prompts and runtime harness configuration. |
| `.cursor/` | Cursor Desktop app-seat hooks, rules, and explicit app commands. |
| `docs/protocol/` | Pull-on-demand protocol docs, provider adoption guides, and assembly maps. |
| `threeway/` | Signed-bus and merge-gate substrate used by cross-provider protocol tooling. |

## 3. Module Map

| Symbol | File:line | Role |
|---|---|---|
| `_project_smoke` | `scripts/ci_smoke.py:53` | Verifies governance-OS runtime invariants before governance gates run. |
| `main` | `scripts/ci_smoke.py:100` | Runs the full smoke gate sequence. |
| `run` | `scripts/check_coordination.py:287` | Validates mailbox event filenames, cursors, kinds, and coordination hygiene. |
| `run` | `scripts/check_placeholders.py:103` | Scans for adoption-placeholder tokens outside the allowlist. |
| `check_sha_refs` | `scripts/check_doc_claims.py:1706` | Reports stale or mismatched commit-SHA citations. |
| `classify_sha_ref_baseline` | `scripts/check_doc_claims.py:1768` | Classifies SHA-reference drift as reviewed baseline or new/changed drift. |
| `collect_monitor_state` | `scripts/mailbox_monitor.py:175` | Builds a read-only snapshot of mailbox, receipt, and heartbeat state. |
| `build_guard` | `scripts/ledger_start_guard.py:175` | Enforces Pipeline-first startup for target-routed seats; paths come from the binding registry. |
| `resolve_target` | `scripts/target_binding.py:143` | Resolves the active product-target binding from `governance.toml` (ADR-013); fail-closed on unknown targets. |
| `writer_fence` | `scripts/mailbox_writer.py:62` | Serializes fixed mailbox-event and cursor finalizers with one Git-common-dir lock. |
| `main` | `scripts/protocol_capacity_board.py:16` | Renders and validates active capacity packets for a wave. |
| `LEDGER_CLI_BRIDGE` | `scripts/codex_protocol_model.py:456` | Executable model data for Pipeline-to-evidence-ledger Codex startup. |
| `render_r_independence` | `scripts/codex_protocol_model.py:684` | Renders the standing R-INDEPENDENCE contract into Codex harness output. |
| `render_ledger_start_guard` | `scripts/codex_protocol_model.py:718` | Renders guard guidance into readiness output. |
| `chatgpt_pro_consult.reserve` | `scripts/chatgpt_pro_consult.py:195` | Reserves one parent-owned consultation key in the shared Git-common-dir record. |
| `parse_verify_request` | `scripts/compact_pair_loop.py:292` | Validates one committed Director verify-request and its exact reviewed range. |
| `validate_report` | `scripts/compact_pair_loop.py:451` | Binds one assigned non-author Operator verdict to that exact request, range, and scope. |
| `resolve_worktree_seat` | `scripts/cursor_app_binding.py` | Resolves one reserved Cursor app-seat linked worktree. |
| `register_session` | `scripts/cursor_app_binding.py` | Atomically records its active conversation and selected model ID. |
| `evaluate` | `scripts/cursor_hook_policy.py` | Enforces Cursor app-seat identity and role boundaries. |
| `next_verify_request` | `scripts/cursor_mailbox.py` | Resolves an Operator's pending request across seat branches. |
| `materialize` | `scripts/cursor_review_snapshot.py` | Exports an immutable reviewed head into bounded scratch without Git mutation. |

## 4. Runtime Invariants

- Pipeline remains the four-seat governance kernel.
- evidence-ledger is the bound default product target for ledger-routed work.
- The fixed mailbox writer serializes event and cursor publication with one
  Git-common-dir lock. No activation selector or alternate writer exists.
- Durable shared state beats chat memory: git commits, mailbox bodies, capacity
  packets, cursor state, and verification reports are authoritative.
- A conflict-free autonomous seat event may supersede a legacy coordinator route
  only when it binds the exact current parent and next revision. Stale or
  dangling parents, forks, and conflicting same-task tips leave only the
  overlapping task non-actionable until a durable successor resolves them.
- Capacity tools are diagnostics, and preflight is advisory; neither grants
  route authority nor substitutes for review of the actual committed change.
- Live ledger seats start with `scripts/ledger_start_guard.py --seat <seat> --wave 2`
  from Pipeline before entering evidence-ledger.
- Ordinary shared-checkout git and pytest use `env -u GIT_INDEX_FILE`.
- Commit, push, merge, cursor consumption, lock actions, pod spend, target
  checkout refresh, production generation, paid API spend, and every other side
  effect are separate authorities. Each requires separately granted user
  authority for the exact effect, executor, target, and scope.
- Material finding references remain immutable through ownership and review,
  and every accepted report dispositions each carried reference explicitly.
- Behavior-changing acceptance requires actual-diff GO from an assigned
  non-author Operator using both a distinct Operator seat and a different
  system-visible model.
- Canonical Compact Pair Invariant: `scripts/codex_protocol_model.py`.
- `coordination/bin/send-event` permits verification reports only from Operator
  seats, then sends every mailbox kind through the fixed finalizer.
- For adversarial surfaces, the owner assesses plausible abuse classes and
  preserves material independent findings. A gate never substitutes for an
  actual-diff Operator verdict.

### Cursor Desktop app seats

- Cursor Desktop/Agents Window is Cursor's normal runtime. Five pinned
  top-level chats use linked `cursor-seat/<seat>` worktrees.
- A live app seat requires agreement among branch/root, `conversation_id`, and
  the app-visible selected model ID in the user-local registry. This is not
  provider/backend attestation.
- App worktrees use native Git indexes and reject `GIT_INDEX_FILE`.
  `cursor-agent`, SDK/API keys, relay daemons, and terminal launchers are not
  live-seat dependencies.
- Director seats may implement. Operator and Coordinator seats are
  repository-tree read-only; their only commit exception is their own exact
  fixed-writer event path. Coordinator holds no cursor.
- `/review-next` discovers committed requests across seat branch tips and
  materializes the actual head under scratch for read-only testing.
- Subagents remain parent-scoped advisors, not durable seats or verdict issuers.
- Existing local top-level chats have no documented automatic wake-up API. One
  Agents Window activation is the baseline pair handoff; remote automation is
  optional and separately authorized.

Other provider adapters retain their exact startup and index contracts.

## 5. Mailbox And Capacity State

Mailbox events live under `coordination/mailbox/sent/`; read cursors live under
`coordination/mailbox/seen/`. The receiving roster comes from
`scripts/protocol_mailbox.py:11` and `scripts/protocol_mailbox.py:17`.

Capacity boards and packets remain available as optional diagnostic evidence;
they keep capacity issues visible but do not grant route authority.

Unknown coordinator broadcast receipt is not delivery proof. It is an unproved
receipt state surfaced by `scripts/mailbox_monitor.py`.

## 6. Verification Gates

Primary shared-checkout commands:

```bash
env -u GIT_INDEX_FILE .venv/bin/python scripts/ci_smoke.py
env -u GIT_INDEX_FILE .venv/bin/python scripts/check_coordination.py
env -u GIT_INDEX_FILE .venv/bin/python scripts/protocol_capacity_board.py --wave 2
env -u GIT_INDEX_FILE .venv/bin/python scripts/check_doc_claims.py --sha-refs
```

Bound Cursor app worktrees use normal Git and pytest without `GIT_INDEX_FILE`.
Smoke proves executable invariants but never substitutes for an Operator
verdict or desktop UX acceptance.

## 7. Target-Repo Boundary

Pipeline can route, verify, and record evidence for target work, but it does not
own product truth. Read the target repo's local instructions and work only
inside the active route. No Cursor-specific product destination is configured.

## 8. Known Sharp Edges

- The normal evidence-ledger checkout can be stale relative to routed worktrees.
- A mailbox receipt split with `unknown` seats proves only that receipt is
  unproved.
- Existing historical SHA-reference debt is baselined and quiet in smoke.
- The Cursor registry is app binding evidence, not a cryptographic provider
  principal.
- Stale per-seat Cursor indexes may remain until separately authorized cleanup;
  app-seat runtime ignores them.
