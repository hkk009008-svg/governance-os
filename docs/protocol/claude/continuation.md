# Claude continuation adapter

This file maps Pipeline policy to Claude Code mechanics. Canonical policy and
validation live in `scripts/codex_protocol_model.py`; skills and agent files
contain only their local deltas.

For the four-app setup and capability comparison, see
`docs/protocol/app-quickstart.md`.

## Modes

- Readiness bridge: read-only orientation; no role claim or durable mutation.
- Live role: only when a concrete Director or Operator role is assigned.
- Coordinator: only for explicit observation, reconciliation, or mediation.
- Subagent: bounded by its parent and never inherits live-role authority.

These runtime identities are separate from product-work modes. Select Explore,
Validate, or Promote through `docs/protocol/work-modes.md`. Explore is the
default for reversible sandbox iteration and does not create seat ceremony;
Validate freezes one candidate; Promote carries the reviewed candidate toward
a separately authorized canonical or external effect.

**Pipeline has no Claude governance-seat launcher, registry, or session-start
binding, and does not need one.** Claude Desktop does have a host session
registry, automatic worktrees, and native peer messaging. Those are useful
convenience surfaces, not Pipeline identity: naming or messaging a session
does not assign a role, publish a durable event, or validate a verdict.

Identity is enforced where it decides something — at publication, by
`scripts/compact_pair_loop.py`, which binds a verdict to reviewer seat not equal
to author seat, reviewer equal to the request's assigned operator, reviewer
matching its own envelope and filename, distinct model families for
`high-risk-control`, and repository/base/head equal to the committed request.
Session-start binding never prevented a bad GO; publication-time validation
does.

## Desktop-first start

1. Open Claude Desktop's Code tab, choose **Local**, and select the exact
   Pipeline checkout that owns the work. Start in Manual or Plan mode.
2. For new independent work, create and rename a session; Desktop gives each
   Git session an isolated worktree. For an existing uncommitted candidate,
   resume its owning session/worktree instead — a fresh automatic worktree does
   not contain another checkout's uncommitted bytes.
3. Confirm the repository root, HEAD, and scoped status, then run the compact
   snapshot below. An explicit role still has to come from the task; a session
   title is not an assignment.
4. Use the visual diff, terminal, editor, and preview panes in the same session.
   Review Code is self-review assistance, not an independent Operator verdict.

The standalone `claude` CLI installed during the 2026-08-09 audit was 2.1.220.
Native cross-session messaging in the CLI requires 2.1.224 or later, so update
the CLI separately before expecting terminal sessions to appear in
Claude's native `ListAgents` result. Do not infer the Desktop embedded-engine version from the
standalone binary.

## Orientation

Use the native index of the current worktree:

```bash
python scripts/status.py snapshot <seat>
```

Read actionable event bodies before a decision. Only the assigned live role
consumes its cursor, and coordinator has no cursor.

Use the fixed interfaces, never raw event or cursor edits:

```bash
coordination/bin/send-event <sender> <recipient> <kind> <subject...>  # body on stdin
coordination/bin/consume-events <seat> [--to <timestamp>]
```

Refresh HEAD, relevant events, and scoped status before a write or gate. One
fresh snapshot is the orientation path; there is no separate fast-resume
classification or second doctrine dump.

## Executable contracts

- `scripts/codex_protocol_model.py` validates runtime identity, ownership
  lineage, work modes, risk profiles, model-family independence, and
  external-effect token shape.
- `scripts/compact_pair_loop.py` validates formal requests, reports, and exact
  reviewed ranges.
- `scripts/mailbox_writer.py` validates and serializes event publication.
- This adapter owns Claude-native delegation and waiting behavior.

Role deltas:

- Director owns an accepted outcome and submits its actual committed range.
- Operator may implement, but when reviewing stays non-author and issues the
  evidence-backed GO/NITS/FAIL for the assigned range.
- Coordinator observes, reconciles, and mediates; it is not an approval gate
  and does not author behavior-changing production work.
- Readiness bridge reports current evidence without claiming work.
- Subagents return bounded evidence to their parent and never publish a formal
  verdict or live-role event.

## Claude-native deltas

These are the only places Claude differs from the shared contract, and each is
forced by the harness rather than chosen:

- Claude Code discovers skills only under `.claude/skills/` — discovery is
  scoped there, reading never was. Since ADR-067 Stage 3, four skills there
  (create-regression-pin, probe-a-claim, prove-a-control,
  chatgpt-pro-consultation) are reference stubs: frontmatter plus
  Claude-native deltas (`env -u GIT_INDEX_FILE`, `.venv/bin/python`, Claude
  tool names, `disable-model-invocation`) pointing at the canonical body in
  `.agents/skills/`, which the session reads and follows. The five
  seat-family pairs are declared provider-native adaptations (O2 ruling
  2026-07-31, ADR-067 addendum): protocol semantics are canonical in
  `.agents`, and semantic divergence resolves toward `.agents` in the same
  change — divergence beyond the declared deltas is still drift, and review
  still catches it. Only `seat-operator/verification-report-format.md` is
  asserted byte-identical, by
  `test_verification_report_templates_remain_identical`; stub targets are
  asserted to exist by `test_claude_stub_targets_exist`.
- Agent definitions are Markdown with a `tools:` list, not TOML with
  `sandbox_mode`. Withholding Write and Edit from `tools:` is how a read-only
  advisor is expressed.
- `model:` in agent frontmatter is the only in-harness lever that forces an
  adversarial reviewer off the authoring model. Model-family independence is
  validated by `codex_protocol_model.models_are_independent`.
- Repository lifecycle hooks are absent by design, and nothing replaced them.
  The retired PreToolUse guard bound *mutation* to `CLAUDE_SEAT` plus a per-seat
  index; it never validated review identity, so removing it took nothing away
  from the acceptance gate. Work in a worktree you are willing to commit from,
  and let `compact_pair_loop.py` decide whether a verdict binds.

### Native session and helper communication

- Use native session listing and peer messaging for transient same-Claude
  findings, status, or a bounded question. Ask Claude to tell the named session;
  the host discovers and delivers it, so the user does not copy-paste between
  sessions. Peer text is attributed and queued, but carries no conversation
  history or files and cannot approve permissions, change configuration, or
  execute slash commands.
- The checked-in `isolatePeerMachines: true` setting preserves low-friction
  same-machine delivery while requiring approval before a message leaves the
  machine. Pipeline deliberately does not force `crossSessionInbound: accept`;
  the receiving session's native permission-class checks remain in force.
- Use `/btw` for a disposable side question. For one bounded advisor, ask
  Claude to delegate to the named project agent. A small dynamic workflow is
  appropriate only when several
  independent, file-disjoint questions justify the coordination cost;
  `workflowSizeGuideline: small` is guidance, not an authority or hard cap.
- Agent teams are CLI-only and experimental. Do not enable them for the normal
  Desktop path. Cloud, Dispatch, scheduled tasks, connectors, computer use, PR
  auto-fix, and auto-merge keep their own launch, spend, data-access, and effect
  boundaries.

Native messages are ephemeral coordination. Formal requests, reports,
transfers, decisions that another provider must see, and every cross-provider
message use `coordination/bin/send-event`. A peer message never substitutes for
the committed Compact Pair or the fixed mailbox writer.

## Review and external effects

Review depth is risk-based as defined by `AGENTS.md` and the executable model.
Ordinary local edits do not need a mailbox event, role ceremony, capacity
packet, handoff, or independent review.

When formal review is triggered, preserve the complete committed Compact Pair
binding; do not weaken it because a lower-risk task would not have required it.
An author cannot approve authored work, a subagent verdict is advisory, and a
green script cannot substitute for the assigned review.

External effects remain separate from structural validation. Push, merge,
locking, event consumption, paid spend, provider launch, and live-data mutation
need exact authority for the executor, target, and scope.

## Target bridge

Targets are selected per task, not fixed. Resolve the active binding through
`scripts/target_binding.py`, then read the target repository's own
instructions. Start from Pipeline; do not infer product authority from a
bridge. For `evidence-ledger`, read `docs/protocol/claude/ledger-cli-adoption.md`.
