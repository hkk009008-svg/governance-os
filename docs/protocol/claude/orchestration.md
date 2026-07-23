# Orchestration - Claude Code

> Claude Code detail document loaded on the `R-ORCH` trigger, not at session
> start. The agent-neutral authority and delegation contract lives in
> `docs/protocol/agents/orchestration.md`; this file maps it to Claude-native
> mechanics without adding authority.

## Native mechanics, not plugin coupling

Use the Claude-native TaskCreate, TaskUpdate, and Agent helpers when delegation
adds fresh context, independent signal, or genuinely useful capacity. Pipeline
does not require a workflow plugin, and a named or installed skill is not an
automatic trigger.

Plugin availability does not grant seat authority, write scope, review
authority, worktree creation, merge, push, cleanup, spend, or any other
external effect. A plan under docs/superpowers/ is an ordinary durable input;
read it when the current route or user names it, but do not infer a plugin
invocation or a mandatory workflow from its location.

Delegation is an owner-chosen capacity tool, not a task-count or line-count
mandate. Stay direct for small, tightly coupled, or authority-sensitive work.
Delegate when a bounded helper can add useful capacity or independent signal.
Never run concurrent implementers on shared files or behind the same
collision-prone lock.

## Claude-native task loop

When the owner chooses delegation:

1. Record the bounded unit with TaskCreate, including the exact outcome,
   allowed paths, immutable finding refs, evidence bar, and forbidden effects.
2. Mark it in progress with TaskUpdate.
3. Dispatch one bounded Agent helper with the relevant repository instructions
   and current route. Use a general-purpose helper unless a routed specialist
   is required.
4. Read the helper's evidence and inspect the actual diff. Treat its report as
   advisory; it does not inherit the owner's seat or mailbox authority.
5. Resolve material concerns before accepting the work. A fresh Agent may
   perform a read-only spec or quality check when that adds signal.
6. Mark the unit complete only after the owning seat has reconciled the actual
   result.

Keep overlapping implementation sequential. Independent read-only
investigations may run concurrently when they ask distinct questions. Helpers
use `env -u GIT_INDEX_FILE` for ordinary Git and pytest and preserve unrelated
peer or user edits.

## Plans and source truth

A written plan is an input, not live authority. Compare it with the current
route, repository instructions, source, tests, and Git state. Where a plan has
drifted, follow current executable truth and record the material divergence.
Do not start a redundant brainstorming, specification, or planning cycle when
an accepted exact task already defines the behavior.

Unexpected failures require root-cause evidence before behavior changes.
Behavior changes and bug fixes get a failing behavior test first when feasible;
otherwise preserve characterization evidence or a concrete
`test-infeasible` reason. Run the fresh smallest sufficient verification before
completion claims.

## Review and finish boundary

Helper review is advisory. Binding acceptance comes only from the assigned
non-author Operator reviewing the actual commit or range with a distinct seat
and different model. The owning Director commits only the routed paths, then
publishes one exact verify-request through the fixed mailbox writer. Only the
assigned Operator publishes GO, NITS, or FAIL.

Finishing a task therefore means:

1. Refresh shared-tree HEAD and scoped status.
2. Run the routed focused checks, Doctor or smoke gates, and exact diff checks.
3. Commit only explicit allowed pathspecs.
4. Publish the immutable actual-range verify-request.
5. Route it once to the compatible Operator task, wait, and reconcile the
   committed verdict.

No native helper or optional plugin substitutes for that Operator boundary.
Push, merge, cursor consumption, provider launch, permission changes, plugin
installation or removal, and other external effects remain separately
authorized actions.

## Context and recovery

Keep helper prompts self-contained and results compact. Durable Git and mailbox
artifacts outrank chat recollection after compaction. If a helper reports
blocked or needs context, the owner reconciles the concrete evidence rather
than treating silence, narration, or task completion state as success.
