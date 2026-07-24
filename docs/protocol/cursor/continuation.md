# Cursor continuation adapter

This adapter maps Pipeline's provider-neutral governance contract onto Cursor Desktop/Agents Window.
Canonical policy remains in
`scripts/codex_protocol_model.py`; `scripts/cursor_protocol_model.py` only
renames the runtime vocabulary.

Cursor app seats do not require `cursor-agent`, the Cursor SDK, API keys,
terminal launchers, relay daemons, or shared-checkout per-seat indexes.

## Policy model

The project hook is write-governed. Reads are free: any inspection command —
Git reads, `rg`, `pytest`, diagnostics — runs without ceremony in every
posture. Authority applies only to writes and effects:

- **Director worktree chats** mutate their own worktree freely.
- **Every other top-level posture** (operator, coordinator, readiness) gets one
  in-app approval per repository mutation instead of a hard deny. Scratch
  writes under `.pytest-verify-tmp/` are always free.
- **Separately authorized effects** — mailbox publish/consume, `git push`,
  `pull`, `fetch`, `merge`, `rebase`, `cherry-pick` — always surface one
  in-app approval naming the acting seat. The approval is the exact-effect
  user authority; structural identity alone never grants it.
- **Hard denies** are reserved for direct writes to mailbox/lock/runtime
  state, direct fixed-writer calls, foreign provider launchers, mutations
  targeting another checkout, and subagent seat impersonation or inherited
  authority.

Because approvals replace denials, the main checkout can bootstrap changes to
the policy itself without disabling hooks.

## Runtime topology

- **Readiness bridge:** any chat in the main checkout or on an ordinary branch.
  It inspects freely, writes scratch freely, and needs one in-app approval per
  governed mutation or effect.
- **Director seats:** pinned top-level chats in linked worktrees on
  `cursor-seat/director` (and `cursor-seat/director2` on demand). They
  implement and commit in their worktree.
- **Operator seats:** pinned top-level chats in linked worktrees on
  `cursor-seat/operator2` (and `cursor-seat/operator` on demand). They review
  and publish binding verdicts.
- **Coordinator:** an on-demand top-level chat on `cursor-seat/coordinator`.
  It routes and reconciles but holds no cursor and authors no production
  changes.
- **Subagents:** optional parent-scoped advisors/capacity workers. They are not
  durable seats and cannot publish verdicts or inherit seat authority.

The standing pair is `director` plus `operator2`; the other seats are capacity
lanes created on demand, not mandatory ceremony. Behavior source map:
`director -> director`, `director2 -> director`, `operator -> operator2`,
`operator2 -> operator2`.

## App setup

In Cursor Agents Window:

1. Create a linked worktree per active seat with its reserved
   `cursor-seat/<seat>` branch (two standing: director, operator2).
2. Open and pin one top-level chat in each worktree.
3. Select the intended model for each chat; the Operator's selected model ID
   must differ from the Director's.
4. The `sessionStart` hook registers the newest conversation and app-visible
   selected model metadata for that worktree in the user-local
   `~/.cursor/pipeline-app-seats.json`. No initialization message is required.

The newest chat in a seat's worktree becomes active. An older duplicate loses
authority because its conversation id no longer matches. A live worktree at a
different path is not silently replaced. Any additional seat becomes live the
same way: add its worktree, open a chat, done.

Do not switch branches from inside a seat chat on a dirty tree: the app may
auto-commit a checkpoint of every dirty file onto the current branch. Seats
stay on their reserved branch; branch surgery happens in a terminal with
explicit user authority.

`coordination/bin/cursor-seat readiness|status` remains a read-only diagnostic;
it never launches or binds a seat.

## Binding and Git isolation

Identity is one fact checked one way: the linked worktree's reserved
`cursor-seat/<seat>` branch plus the user-local registry record written at
`sessionStart` (absolute root, active `conversation_id`, selected `model_id`).
`scripts/cursor_app_binding.py` owns this resolution and the atomic registry.

Wrappers and hooks resolve that identity at point of use with
`resolve_registered_session`; nothing depends on injected environment values.
`sessionStart` still exports identity variables as context, and when they are
present they must agree with the registry, but they never establish identity.
Model changes require a new session registration.

The reserved branch is a Pipeline convention verified with Git, not a
Cursor-issued worktree identity. Unknown, detached, multi-root, and ordinary
branches remain readiness posture.

Each worktree owns a normal Git working tree and index. Cursor app seats reject
`GIT_INDEX_FILE`; the obsolete `.git/index-cursor-*` files are never consulted.
Use parallel writers only for non-overlapping work and reconcile through normal
Git history.

## Individual, pair, and unit operation

### Individual

Open the pinned seat chat and work in its dedicated worktree. No terminal
launch or copied bootstrap prompt is needed.

### Compact pair

1. A Director implements, tests, commits the actual range, and drafts a
   canonical verify-request body under `.pytest-verify-tmp/`.
2. The Director invokes `coordination/bin/cursor-publish` with `--body-file`.
   The hook shows an in-app approval and the wrapper delegates to the fixed
   `send-event` writer. The Director commits only the returned staged event
   path on its seat branch.
3. The user activates the pinned assigned Operator chat and invokes
   `/review-next`.
4. The skill resolves the newest pending committed verify-request addressed to
   that Operator, validates its selected model ID differs from the author, and
   uses `scripts/cursor_review_snapshot.py` to materialize the exact reviewed
   head under scratch without changing the Operator branch.
5. The Operator drafts and publishes one canonical GO/NITS/FAIL report through
   the same approved wrapper, then commits only the returned staged report
   path.

No prompt body or `path@sha` is relayed by the user. Cursor currently exposes
no documented API to wake and submit into another existing local top-level
chat, so activating that pinned chat is the one baseline manual app handoff.
Cloud Agents/Automations may automate it later, but are optional, remote,
potentially paid, and separately authorized.

### Unit

Keep the standing pair pinned in Agents Window and add capacity seats only
when parallel lanes earn their cost. Worktrees isolate file/index state;
committed mailbox events and cursors hold durable coordination state.
Coordinator facilitates only when reconciliation is useful.

## Mailbox

Cursor never reimplements mailbox finalization:

- `coordination/bin/cursor-publish` delegates to `send-event`;
- `coordination/bin/cursor-consume` delegates to `consume-events`;
- direct writes to `coordination/mailbox/`, locks, or `.cursor/runtime/` are
  denied.

Publication requires a regular non-symlink body file under
`.pytest-verify-tmp/` and one in-app approval. The wrapper resolves the bound
seat itself from the worktree and app registry, uses `subprocess.run`, and
delegates the body on stdin. Direct fixed-writer calls from agent tools stay
denied.

`next-review` is read-only: it finds the newest pending committed request for
the bound Operator across all `refs/heads/cursor-seat/*` tips, skips requests
already referenced by a committed report, and refuses same-model review. Seats
do not merge mailbox-only commits merely to discover them. Focused tests may
use the immutable scratch snapshot; repository-level gates
(`scripts/ci_smoke.py`, `scripts/cursor_land_gate.py`) must run only after
`scripts/cursor_review_snapshot.py --require-exact-head` succeeds against
`reviewed_head`, or inside a detached worktree checked out at that exact
commit. Never green those gates from a seat HEAD that is not `reviewed_head`.

Mailbox publication, cursor consume, push, pull, fetch, merge, rebase,
cherry-pick, lock, and spend are separate effects. Each surfaces one in-app
approval naming the acting posture; a subagent or foreign `-C` target is
denied outright. Local seat synchronization is the same flow: run
`git merge --ff-only <commit>` in the bound seat's own worktree and approve
the request.

## Hook policy

`.cursor/hooks.json` routes `sessionStart`, sensitive file tools, shell
execution, and subagent creation through `.cursor/hooks/seat-policy` and
`scripts/cursor_hook_policy.py`. Shell commands are evaluated exactly once, by
`beforeShellExecution`.

The policy:

- fails closed on malformed input and unclassifiable identity;
- Reads are free for classified inspection forms and scratch writes;
- unknown top-level shell commands ask; unknown subagent shell commands deny;
- sensitive hooks compare payload `conversation_id` / `model_id` to the
  registry whenever those fields are supplied and fail closed on mismatch;
- permits unattended production mutation only in Director worktree chats, and
  the Operator's own staged fixed-writer event commit;
- converts every other governed mutation or separately authorized effect into
  one in-app approval;
- hard-denies direct mailbox/runtime writes, direct fixed-writer calls,
  foreign provider launchers, and subagent seat impersonation or inherited
  authority.

When Cursor's optional third-party configuration support also loads
`.claude/settings.json`, the Claude guard does not unconditionally defer. It
maps the compatibility payload into this same app-seat policy; because that
host has no in-app approval surface, approval-gated decisions fail closed
there.

Hooks are accidental-misuse guardrails, not an authenticated provider
principal. Cursor has no first-class immutable seat principal; Pipeline records
and checks the strongest app-visible worktree, conversation, and
selected-model evidence available. `model_id` is not provider/backend
attestation; reports record the exact selected IDs and make no stronger claim.

## Startup and verification

At the start of non-trivial work, refresh smoke, recent Git history, scoped
status, and relevant mailbox bodies. In app worktrees use normal Git and
pytest; do not set or unset a per-seat index variable.

Unit tests and `scripts/ci_smoke.py` verify executable invariants but do not
substitute for a different-model Operator verdict or desktop acceptance.

## Target repositories

No Cursor-specific product destination is configured. Future destinations use
the provider-neutral `governance.toml` registry and an explicit route.
