# ARCHITECTURE.md - Pipeline governance kernel

> This file records current repository facts. Executable code wins when prose
> drifts, and the stale prose must be corrected in the same change.

*Last verified: 2026-07-25 @ 61786501e26f7e1bac92efbdcd4ff0ea468a7bbb*

## 1. Purpose

Pipeline preserves the minimum durable state needed to coordinate bounded AI
coding work: task events, ownership, exact-range review, and separately
authorized external effects. It is not a product repository, a general-purpose
scheduler, or a substitute for the host task runtime.

`evidence-ledger` is the default registered target for ledger-routed work.
Product behavior remains owned by the target repository.

## 2. Codex control flow

```text
user or parent task
  -> optional explicit role
  -> one compact current-state snapshot
  -> scoped work in a native Git worktree
  -> risk classification and focused verification
  -> exact committed request/report only when formal review is required
  -> separately authorized external effect, if any
```

Read-only questions do not enter this flow. Ordinary local edits do not need a
mailbox event, role ceremony, capacity packet, handoff, or independent review
unless their actual risk or transfer boundary requires one.

## 3. Repository topology

| Path | Current role |
|---|---|
| `scripts/` | Runtime validators, compact status, target guard, and provider adapters. |
| `coordination/mailbox/sent/` | Append-only human-readable task and review events. |
| `coordination/mailbox/seen/` | Compatibility cursors for the four concrete pair seats only. |
| `.agents/skills/` | On-demand role procedures. Skill presence grants no authority. |
| `.codex/agents/` | Small reusable role deltas; no numbered pseudo-seat inventory. |
| Project Codex hooks | Absent by design. Codex has no repository lifecycle hook dependency. |
| `threeway/` | Signed ref-bus substrate used only when its event and matching cursor refs prove it live. |
| `governance.toml` | Registered product targets. |
| `.claude/`, `.agy/`, `.cursor/` | Provider-specific adapters with their own runtime contracts. |

## 4. Executable seams

The table names stable symbols instead of volatile line numbers.

| Symbol | Source | Responsibility |
|---|---|---|
| `collect_orientation_snapshot`, `render_orientation_snapshot` | `scripts/status.py` | Produce the bounded current-state view. |
| `resolve_unread` | `scripts/bus_unread.py` | Select one proven unread authority and expose ambiguity. |
| `inspect_current_verify_requests` | `scripts/check_coordination.py` | Find and validate current committed review requests. |
| `validate_event_candidate`, `writer_fence` | `scripts/mailbox_writer.py` | Validate and serialize event/cursor publication. |
| `parse_verify_request`, `validate_report` | `scripts/compact_pair_loop.py` | Bind formal review to one committed request and exact range. |
| `RuntimeIdentity`, `review_profile_for` | `scripts/codex_protocol_model.py` | Close runtime identity and select a finite review policy. |
| `build_launch_spec` | `scripts/codex_seat_launcher.py` | Launch a named role in the caller-selected native worktree. |
| `build_guard` | `scripts/ledger_start_guard.py` | Validate one ordinary Pipeline-first target start. |
| `resolve_target` | `scripts/target_binding.py` | Resolve the selected product binding. |

## 5. Runtime invariants

- Codex begins without a live role. A user or parent must explicitly assign a
  concrete role.
- Runtime identity is closed: mode, role, seat, behavior source, and model must
  agree. Ambient policy variables cannot widen it.
- A launched Codex process inherits the selected checkout but not
  `GIT_INDEX_FILE` or ambient Codex policy variables. Each worktree uses its
  native index.
- Repository hooks do not orient Codex, mutate state, refresh doctrine, or
  maintain a second index.
- One compact snapshot is the normal orientation path. There is no fast-resume
  classifier or mandatory handoff-first pass.
- Current Git state and committed event bodies outrank summaries, packets, and
  historical prose.
- Coordinators are cursorless observers. Only `director`, `director2`,
  `operator`, and `operator2` own consumable compatibility cursors.
- Capacity boards, handoffs, and protocol doctors are optional diagnostics.
  They never grant task, review, or effect authority.
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
| `high-risk-control` | Distinct non-author Operator, different model, exact range, and abuse-class assessment. |
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
python -m pytest tests/unit -q
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
