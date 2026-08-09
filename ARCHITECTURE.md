# ARCHITECTURE.md - Pipeline governance kernel

> This file records current repository facts. Executable code wins when prose
> drifts, and the stale prose must be corrected in the same change.

*Last verified against base: 2026-08-09 @ 89b212b*

## 1. Purpose

Pipeline preserves the minimum durable state needed to coordinate bounded AI
coding work: task events, ownership, exact-range review, and separately
authorized external effects. It is not a product repository, a general-purpose
scheduler, or a substitute for the host task runtime.

`evidence-ledger` is the default registered target for ledger-routed work.
Product behavior remains owned by the target repository.

## 2. Control flow

One flow, shared by every provider side. Codex, Cursor, Claude, and AGY differ
in runtime mechanics, never in policy.

```text
user or parent task
  -> optional explicit role
  -> one compact current-state snapshot
  -> Explore, Validate, or Promote work mode
  -> scoped work in a native Git worktree
  -> risk classification and focused verification
  -> exact committed request/report only when formal review is required
  -> separately authorized external effect, if any
```

Read-only questions do not enter this flow. Ordinary local edits do not need a
mailbox event, role ceremony, capacity packet, handoff, or independent review
unless their actual risk or transfer boundary requires one.

Work mode is orthogonal to review risk. Explore permits recorded iteration only
inside a declared non-canonical scope. Validate freezes one candidate and
requires its non-author review. Promote adds rollback and separately authorized
canonical or external-effect scope. The mode itself grants no authority; see
`docs/protocol/work-modes.md`.

## 3. Repository topology

| Path | Current role |
|---|---|
| `scripts/` | Runtime validators, compact status, target guard, and provider adapters. |
| `coordination/mailbox/sent/` | Append-only human-readable task and review events. |
| `coordination/mailbox/seen/` | Compatibility cursors for the four concrete pair seats only. |
| `.agents/skills/` | On-demand role procedures. Skill presence grants no authority. |
| `.codex/agents/` | Small reusable role deltas; no numbered pseudo-seat inventory. |
| Repository lifecycle hooks | Absent on every side except `.cursor/hooks/seat-policy`, which gates enforceable shell/MCP approvals and denies unsupported file-tool asks. No side depends on a hook for orientation or durable state. |
| `threeway/` | Signed ref-bus substrate used only when its event and matching cursor refs prove it live. Dormant here; still load-bearing, because proving the bus absent is what makes the mailbox fallback correct. |
| `governance.toml` | Registered product targets. Targets are selected per task, not fixed. |
| `.claude/`, `.codex/`, `.cursor/`, `.agents/agents/`, `.agents/workflows/` | Provider discovery/adaptation surfaces. Each owns runtime mechanics only; policy comes from `scripts/codex_protocol_model.py`. |

### Provider surfaces

Each side maps the same policy onto its host. The differences below are forced
by the host, not chosen, and each adapter states its own.

| | Codex | Cursor | Claude | AGY |
|---|---|---|---|---|
| Runtime | host task tools | Agents Window chats | desktop app | native subagent mesh |
| Adapter | `docs/protocol/codex/continuation.md` | `docs/protocol/cursor/continuation.md` | `docs/protocol/claude/continuation.md` | `docs/protocol/agy/continuation.md` |
| Lifecycle hook | none | `seat-policy` | none | none |
| Launcher | `codex-seat` | `cursor-seat` | none | `agy-seat` |
| Seat roles | `.codex/agents/*.toml` | `/review-next` skill | `.claude/skills/seat-*` | explicit assignment + `.agents/skills/seat-*` |
| Subagent advisors | `.codex/agents/*.toml` | `.cursor/agents/*.md` | `.claude/agents/*.md` | `.agents/agents/*.md` |

Notable per-host constraints:

- Cursor is the only side with a repository lifecycle hook. Shell and MCP
  approval hooks are enforceable; `preToolUse` asks are not, so non-Director
  native file edits deny instead of receiving a false approval.
- Pipeline has no Claude launcher or governance-seat registry. Claude Desktop's
  host session registry, automatic worktrees, and peer relay are conveniences;
  they do not turn a session title or message into role authority.
- Claude Code discovers skills only under `.claude/skills/`. Since ADR-067
  Stage 3, four `.claude` skills (create-regression-pin, probe-a-claim,
  prove-a-control, chatgpt-pro-consultation) are reference stubs over their
  canonical `.agents/skills/` bodies plus Claude-native deltas; the five
  seat-family pairs are declared provider-native adaptations (O2 ruling
  2026-07-31) whose protocol semantics resolve toward `.agents`. Only
  `seat-operator/verification-report-format.md` is asserted byte-identical,
  and no test asserts `SKILL.md` parity. Review, not a gate, catches
  divergence.
- Codex carries the spawnable seat roles because host task tools dispatch them.
  Other sides carry only the read-only advisors.
- AGY keeps a launcher because it selects a per-seat model. It carried a
  per-seat service tier until 2026-07-26; the installed CLI exposes no such
  option, so the setting selected nothing and was removed rather than left as
  a control that appeared to work.

## 4. Executable seams

The table names stable symbols instead of volatile line numbers.

| Symbol | Source | Responsibility |
|---|---|---|
| `collect_orientation_snapshot`, `render_orientation_snapshot` | `scripts/status.py` | Produce the bounded current-state view. |
| `inspect_current_verify_requests` | `scripts/check_coordination.py` | Find and validate current committed review requests. |
| `CommitGraphProjection` | `scripts/git_commit_projection.py` | Pin one repository identity and HEAD, batch-check candidate object types, and answer committed-range ancestry from one bounded in-memory graph. |
| `validate_event_candidate`, `writer_fence` | `scripts/mailbox_writer.py` | Validate and serialize event/cursor publication. |
| `parse_verify_request`, `validate_report` | `scripts/compact_pair_loop.py` | Bind formal review to one committed request and exact range. |
| `RuntimeIdentity`, `work_profile_for`, `review_profile_for` | `scripts/codex_protocol_model.py` | Close runtime identity and select finite work-mode and review policies. |
| `model_family`, `models_are_independent` | `scripts/codex_protocol_model.py` | Decide reviewer independence by model family, so a harness prefix or version suffix cannot buy it. |
| `build_launch_spec` | `scripts/codex_seat_launcher.py`, `scripts/agy_seat_launcher.py` | Launch a named role in the caller-selected native worktree. Neither binds an index. |
| `resolve_unread` | `scripts/bus_unread.py` | Answer unread from the proven authority, falling back to the canonical mailbox order so an absent bus never renders `0 unread`. |
| `build_guard` | `scripts/ledger_start_guard.py` | Validate one ordinary Pipeline-first target start. |
| `resolve_target` | `scripts/target_binding.py` | Resolve the selected product binding. |
| `build_index`, `query_index` | `scripts/learning_index.py` | Build and query the derived episodic index from the committed tree; unavailable is `None`, never a silent zero. |
| `parse_learning_candidate_statement`, `committed_learning_candidate_ids` | `scripts/protocol_mailbox.py` | Type learning candidates and dispositions from committed events; content-hash identity and pinned-commit dedup. |
| `draft_candidate` | `scripts/learning_extract.py` | Draft one evidence-triggered candidate into scratch; never publishes, never mutates git. |
| `collect_metrics` | `scripts/learning_metrics.py` | Read-only learning-lifecycle metrics with advisory promotion-linkage WARNs. |

## 5. Runtime invariants

- Every side begins without a live role. A user or parent must explicitly assign
  a concrete role.
- Runtime identity is closed: mode, role, seat, behavior source, and model must
  agree. Ambient policy variables cannot widen it.
- No side binds a per-seat Git index. A launched process inherits the selected
  checkout but not `GIT_INDEX_FILE` or ambient provider policy variables; every
  worktree uses its native index. `index-<provider>-<seat>` is retired.
- Session start grants nothing. Pipeline has no Claude governance-seat launcher
  or registry, even though Claude Desktop has a host session registry and relay;
  Cursor's registry exists to gate in-app effects, not to validate a verdict.
  Review identity is decided at publication by `scripts/compact_pair_loop.py`.
- Repository hooks do not orient any side, mutate state, refresh doctrine, or
  maintain a second index.
- One compact snapshot is the normal orientation path. There is no fast-resume
  classifier or mandatory handoff-first pass.
- Current Git state and committed event bodies outrank summaries, packets, and
  historical prose.
- Coordinators are cursorless observers. Only `director`, `director2`,
  `operator`, and `operator2` own consumable compatibility cursors.
- Capacity boards, handoffs, and protocol doctors are optional diagnostics.
  They never grant task, review, or effect authority.
- Explore does not allocate seats or create formal review artifacts unless a
  real transfer or phase change requires them.
- Editing, staging, committing, publishing an event, consuming a cursor,
  pushing, merging, locking, launching a provider, spending, and mutating live
  data are distinct actions.

## 6. Queue and publication authority

The mailbox is authoritative until both the signed event ref and the addressed
seat's signed cursor ref exist and form a coherent sequence. An absent or
partial bus is never interpreted as an empty queue. Legacy scalar cursors are
resolved against the canonical ordered mailbox projection while the bus is not
proven live. Malformed state produces an unavailable/failing result, not zero
unread.

All new events pass through `coordination/bin/send-event` and the fixed writer.
The writer rejects malformed envelopes, invalid sender/kind combinations, and
invalid review-request structure before publication. Historical event files
remain immutable evidence; a grandfathered malformed artifact is reported as
invalid and grants no authority.

## 7. Review and external effects

Review depth is selected from four closed profiles:

| Profile | Required evidence |
|---|---|
| `ordinary-local` | Focused verification. |
| `material-behavior` | Non-author review of the exact committed range. |
| `high-risk-control` | Distinct non-author Operator, different model **family**, exact range, and abuse-class assessment. |
| `external-effect` | Live authorization for the exact executor, target, effect, and scope. |

Once formal review is required, the committed Compact Pair binding remains
strict. An author cannot approve authored work, a generic subagent verdict is
advisory, and a green script cannot substitute for the assigned review.
External-effect authorization is never inferred from a route, task dispatch,
schema, token, or review result.

## 8. Verification

Activate a development environment containing
`requirements-dev.txt`, then run the smallest relevant tests and one completion
gate:

```bash
python -m pytest tests -q
python scripts/ci_smoke.py
python scripts/check_coordination.py
```

These commands use the worktree's normal Git environment. Smoke and tests prove
only the behavior they execute; they do not commit, publish, consume, push,
merge, or issue a formal verdict.

## 9. Compatibility boundaries

- The four concrete seat names remain mailbox/review compatibility identities;
  they are not a requirement to allocate four agents to every task.
- Historical capacity packets, handoffs, events, and SHA citations remain
  evidence and may contain superseded process language.
- The signed bus is optional until its complete local authority pair is live.
- A configured model name is runtime evidence, not cryptographic provider
  attestation.
- A normal target checkout may be stale relative to an explicitly routed
  target worktree; the route's exact target and base win.
