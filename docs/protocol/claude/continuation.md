# Claude continuation adapter

This file maps Pipeline policy to Claude Code mechanics. Canonical policy and
validation live in `pipeline/codex_protocol_model.py`; skills and agent files
contain only their local deltas.

For how the two CLIs reach each other, see `docs/protocol/peer.md`.

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

**Pipeline has no Claude launcher, registry, or session-start binding, and
does not need one.** Naming a terminal, a worktree, or a session does not
assign a role, publish a durable event, or validate a verdict.

Identity is enforced where it decides something — at publication, by
`pipeline/compact_pair_loop.py`, which binds a verdict to reviewer seat not equal
to author seat, reviewer equal to the request's assigned operator, reviewer
matching its own envelope and filename, distinct model families for
`high-risk-control`, and repository/base/head equal to the committed request.
Session-start binding never prevented a bad GO; publication-time validation
does.

## CLI start

1. Open a terminal in the exact Pipeline checkout that owns the work, or in a
   native Git worktree of it. `bin/pipeline` resolves the primary checkout's
   interpreter from a linked worktree too, so a worktree needs no venv.
2. For new independent work, create a worktree with a name that says what the
   work is. For an existing uncommitted candidate, return to the worktree that
   holds it -- a fresh one does not contain another checkout's bytes.
3. Confirm the repository root, HEAD, and scoped status, then run the compact
   snapshot below. An explicit role still has to come from the task; a
   directory name is not an assignment.

## Orientation

Use the native index of the current worktree:

```bash
coordination/bin/pipeline-python pipeline/status.py snapshot <seat>
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

At a real long-horizon boundary — ownership transfer, interruption, wrap, or
before context compaction — publish one checkpoint `findings` event (draft:
`pipeline/draft_checkpoint.py`; its `Lessons:` line routes lessons toward
learning-candidates, and `none-considered` is always valid). Resume is one
snapshot plus the newest campaign checkpoint plus the actionable bodies it
names; unread backlog is not an orientation debt. Recall from the episodic
index (`pipeline/learning_index.py query`) is optional and advisory (learning
contract I1) — committed state outranks it.

## Executable contracts

- `pipeline/codex_protocol_model.py` validates runtime identity, ownership
  lineage, work modes, risk profiles, model-family independence, and
  external-effect token shape.
- `pipeline/compact_pair_loop.py` validates formal requests, reports, and exact
  reviewed ranges.
- `pipeline/mailbox_writer.py` validates and serializes event publication.
- `pipeline/peer.py` runs the Codex CLI once as a child process and commits a
  receipt. It is not a launcher, a registry, or an authority source.
- This adapter owns Claude-native delegation and waiting behavior.

Role semantics are owned by `.agents/skills/four-seat-protocol/SKILL.md`
and its role skills. Subagents return bounded evidence to their parent and
never publish a formal verdict or live-role event.

## Claude-native deltas

These are the only places Claude differs from the shared contract, and each is
forced by the harness rather than chosen:

- Claude Code discovers skills only under `.claude/skills/` — discovery is
  scoped there, reading never was. Since ADR-067 Stage 3, five skills there
  (create-regression-pin, probe-a-claim, prove-a-control,
  isolate-a-variable, writing-skills) are
  reference stubs: frontmatter plus Claude-native deltas
  (`env -u GIT_INDEX_FILE`, `coordination/bin/pipeline-python`, Claude tool
  names, `disable-model-invocation`) pointing at the canonical body in
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
  adversarial reviewer off the authoring model, but every model it can select
  is claude-family, so it never satisfies the different-family requirement.
  Family is decided by `codex_protocol_model.models_are_independent` against
  `config/model-families.toml`, and
  `test_supported_provider_adapters_are_exactly_codex_and_claude` holds the
  supported adapters at exactly Codex and Claude — so the different-family
  counterparty for Claude-authored work is Codex, not a differently-configured
  Claude. `pipeline/ci_admission_gate.py` admits an authority-surface range only
  when a committed GO/NITS report bound to a `high-risk-control` request covers
  it, and `CLAUDE.md`, `.claude/`, and `docs/protocol/` are authority surfaces —
  so editing this adapter needs a Codex reviewer; no Claude seat or subagent can
  supply one.
- Repository lifecycle hooks are absent by design, and nothing replaced them.
  The retired PreToolUse guard bound *mutation* to `CLAUDE_SEAT` plus a per-seat
  index; it never validated review identity, so removing it took nothing away
  from the acceptance gate. Work in a worktree you are willing to commit from,
  and let `compact_pair_loop.py` decide whether a verdict binds.

### Native session and helper communication

- For transient Codex communication, run the other CLI once:
  `pipeline peer ask codex --task <id> --prompt-file <f>`. The child's exit
  code is the delivery acknowledgement -- there is no send whose delivery can
  stay unknown -- and the receipt under `coordination/peer/<task>/` records
  what actually ran, including the model the peer's own output reported.
  `--dry-run` prints the exact argv and launches nothing. Exact contract:
  `docs/protocol/peer.md`.
- Launching a peer is a provider launch and paid spend. It needs its own exact
  authority; a task id is not one.
- Use native session listing and peer messaging for transient SAME-Claude
  findings between your own terminals. That text is attributed and queued, but
  carries no conversation history or files and cannot approve permissions,
  change configuration, or execute slash commands. It is convenience, not
  protocol: it crosses no provider boundary and leaves no receipt.
- For one bounded advisor, delegate to a named project agent. A small dynamic
  workflow is appropriate only when several independent, file-disjoint
  questions justify the coordination cost; `workflowSizeGuideline: small` is
  guidance, not an authority or a hard cap.
- Cloud, scheduled tasks, computer use, PR auto-fix, and auto-merge keep their
  own launch, spend, data-access, and effect boundaries and none of them is
  part of this protocol.

Peer output and native messages are both ephemeral coordination. Formal
requests, reports, transfers, and durable decisions that the other side must
see use `coordination/bin/send-event`. Neither substitutes for the committed
Compact Pair or the fixed mailbox writer, and a receipt is evidence rather
than attestation.

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
`pipeline/target_binding.py`, then read the target repository's own
instructions. Start from Pipeline; do not infer product authority from a
bridge. For `evidence-ledger`, read `docs/protocol/claude/ledger-cli-adoption.md`.
