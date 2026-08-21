# ARCHITECTURE.md - Pipeline governance kernel

> This file records current repository facts. Executable code wins when prose
> drifts, and the stale prose must be corrected in the same change.

*Last verified against base: 2026-08-21 @ 86146d1f*

## 1. Purpose

Pipeline preserves the minimum durable state needed to coordinate bounded AI
coding work: task events, ownership, exact-range review, and separately
authorized external effects.

It is **CLI-exclusive**. Exactly two participants are supported — the `claude`
CLI and the `codex` CLI — and every path is a terminal path. No desktop app,
no MCP server, no persistent agent peer, no browser. Surfaces that assumed one
of those were removed rather than deprecated.

`evidence-ledger` is the default registered target for ledger-routed work.
Product behavior remains owned by the target repository.

## 2. Control flow

One flow, shared by both CLIs. They differ in runtime mechanics, never in
policy.

```text
user or parent task
  -> optional explicit role
  -> one compact current-state snapshot          (pipeline status)
  -> Explore, Validate, or Promote work mode
  -> scoped work in a native Git worktree
  -> risk classification and focused verification (pipeline check)
  -> exact committed request/report only when formal review is required
  -> separately authorized external effect, if any
```

Read-only questions do not enter this flow. Ordinary local edits do not need a
mailbox event, role ceremony, handoff, or independent review unless their
actual risk or transfer boundary requires one.

Work mode is orthogonal to review risk and grants no authority; see
`docs/protocol/work-modes.md`.

## 3. Repository topology

| Path | Current role |
|---|---|
| `bin/pipeline` | The single entry point. Clears `GIT_INDEX_FILE`, resolves the primary checkout's interpreter (including from a linked worktree), dispatches a verb. |
| `pipeline/` | The kernel's Python. Flat modules, imported by bare name (`pythonpath = [".", "pipeline"]`); `pipeline/cli.py` maps verbs onto them. Formerly `scripts/`. |
| `pipeline/peer.py`, `pipeline/peer_backends.py` | One-shot invocation of the other CLI, with a committed receipt. |
| `coordination/mailbox/sent/` | Append-only human-readable task and review events. |
| `coordination/mailbox/seen/` | Compatibility cursors for the four concrete pair seats only. |
| `coordination/peer/` | Peer-invocation receipts, grouped by task. |
| `coordination/bin/` | Hardened shell front doors: `send-event`, `consume-events`, the lock pair, `probe-claim`, `pipeline-python`, `codex-seat`. |
| `.agents/skills/` | On-demand role procedures. Skill presence grants no authority. |
| `.codex/agents/` | Small reusable role deltas; no numbered pseudo-seat inventory. |
| `.codex/config.toml` | Declares no MCP servers and no ambient authority; `harness_preflight` fails closed if either reappears. |
| Repository lifecycle hooks | Absent. Neither side depends on a repository hook for orientation or durable state. |
| `governance.toml` | Registered product targets. Targets are selected per task, not fixed. |
| `.claude/`, `.codex/` | CLI discovery/adaptation surfaces. Each owns runtime mechanics only; policy comes from `pipeline/codex_protocol_model.py`. |

### Provider surfaces

| | Codex | Claude |
|---|---|---|
| Runtime | `codex` CLI | `claude` CLI |
| Adapter | `docs/protocol/codex/continuation.md` | `docs/protocol/claude/continuation.md` |
| Lifecycle hook | none | none |
| Launcher | `codex-seat` | none |
| Seat roles | `.codex/agents/*.toml` | `.claude/skills/seat-*` |
| Subagent advisors | `.codex/agents/*.toml` | `.claude/agents/*.md` |
| Reaching the other side | `pipeline peer ask claude` | `pipeline peer ask codex` |

Notable per-host constraints:

- Claude Code discovers skills only under `.claude/skills/`. Five `.claude`
  skills (create-regression-pin, probe-a-claim, prove-a-control,
  isolate-a-variable, writing-skills) are reference stubs over their canonical
  `.agents/skills/` bodies plus Claude-native deltas; the seat-family pairs are
  declared provider-native adaptations (O2 ruling 2026-07-31) whose protocol
  semantics resolve toward `.agents`. Only
  `seat-operator/verification-report-format.md` is asserted byte-identical, and
  no test asserts `SKILL.md` parity. Review, not a gate, catches divergence.
  Frozen selection and stub-routing cases live under `tests/skill_packs/`
  (ADR-068).
- Every model the Claude harness can select is claude-family, so a Claude
  session cannot supply its own different-family reviewer. That counterparty is
  Codex.
- Codex carries the spawnable seat roles because host task tools dispatch them.

## 4. Executable seams

| Symbol | Source | Responsibility |
|---|---|---|
| `main`, `_resolve` | `pipeline/cli.py` | Map one verb (longest prefix wins) onto an existing module's entrypoint with `sys.argv` rewritten. |
| `collect_orientation_snapshot`, `render_orientation_snapshot` | `pipeline/status.py` | Produce the bounded current-state view. |
| `inspect_current_verify_requests` | `pipeline/check_coordination.py` | Find and validate current committed review requests. |
| `_committed_mailbox_projection`, `_normalize_archive_name` | `pipeline/check_coordination.py` | Project immutable committed mailbox bytes, resolving pre-rename manifest paths without tolerating a missing manifest. |
| `CommitGraphProjection` | `pipeline/git_commit_projection.py` | Pin one repository identity and HEAD and answer committed-range ancestry from one bounded in-memory graph. |
| `validate_event_candidate`, `writer_fence` | `pipeline/mailbox_writer.py` | Validate and serialize event/cursor publication. |
| `parse_verify_request`, `validate_report` | `pipeline/compact_pair_loop.py` | Bind formal review to one committed request and exact range. |
| `RuntimeIdentity`, `work_profile_for`, `review_profile_for` | `pipeline/codex_protocol_model.py` | Close runtime identity and select finite work-mode and review policies. |
| `model_family`, `models_are_independent` | `pipeline/codex_protocol_model.py` | Decide reviewer independence by model family, so a harness prefix or version suffix cannot buy it. |
| `build`, `reported_result` | `pipeline/peer_backends.py` | Build one peer's argv; read the model and result from that peer's own output, recording absence rather than inferring it. |
| `run`, `write_receipt` | `pipeline/peer.py` | Run one peer once under a timeout and commit a receipt of what actually ran. |
| `check_peers`, `check_codex` | `pipeline/harness_preflight.py` | Report whether both CLI peers could run, and refuse ambient authority or any declared MCP server. |
| `build_launch_spec` | `pipeline/codex_seat_launcher.py` | Launch a named Codex role in the caller-selected native worktree without binding an index. |
| `resolve_unread` | `pipeline/bus_unread.py` | Answer unread from the canonical mailbox order, so a legacy scalar cursor can never render `0 unread`. |
| `build_guard` | `pipeline/ledger_start_guard.py` | Validate one ordinary Pipeline-first target start. |
| `resolve_target` | `pipeline/target_binding.py` | Resolve the selected product binding. |
| `build_index`, `query_index` | `pipeline/learning_index.py` | Build and query the derived episodic index; unavailable is `None`, never a silent zero. |
| `parse_learning_candidate_statement`, `committed_learning_candidate_ids` | `pipeline/protocol_mailbox.py` | Type learning candidates and dispositions from committed events. |
| `draft_candidate` | `pipeline/learning_extract.py` | Draft one evidence-triggered candidate into scratch; never publishes. |
| `parse_checkpoint_statement`, `checkpoint_intent` | `pipeline/protocol_mailbox.py` | Type a continuity checkpoint from a findings body. |
| `draft_checkpoint` | `pipeline/draft_checkpoint.py` | Draft one checkpoint findings event into scratch; never publishes. |
| `_python_growth_violations`, `_RENAME_THRESHOLD` | `pipeline/check_no_ceremony.py` | Bound Python growth, asking Git one question about file identity in both halves of the rule. |

## 5. Runtime invariants

- Every side begins without a live role. A user or parent must explicitly assign
  a concrete role.
- Runtime identity is closed: mode, role, seat, behavior source, and model must
  agree. Ambient policy variables cannot widen it.
- No side binds a per-seat Git index. A launched process inherits the selected
  checkout but not `GIT_INDEX_FILE` or ambient provider policy variables.
- Session start grants nothing. Review identity is decided at publication by
  `pipeline/compact_pair_loop.py`.
- Peer traffic is transient routing only. A peer's output can carry a finding
  or an opinion; it cannot assign a role, validate a reviewer, grant an effect,
  or replace the fixed mailbox. A peer receipt is evidence, not attestation.
- Repository hooks do not orient any side, mutate state, refresh doctrine, or
  maintain a second index.
- One compact snapshot is the normal orientation path.
- Current Git state and committed event bodies outrank summaries and
  historical prose.
- Coordinators are cursorless observers. Only `director`, `director2`,
  `operator`, and `operator2` own consumable compatibility cursors.
- Protocol doctors and metrics are optional diagnostics. They never grant task,
  review, or effect authority.
- Editing, staging, committing, publishing an event, consuming a cursor,
  pushing, merging, locking, invoking a peer, spending, and mutating live data
  are distinct actions.

## 6. Queue and publication authority

The mailbox is the only coordination transport. The signed ref-bus that this
kernel once hedged against is gone: it was dormant on two independent axes
(`governance.toml` declared `transport = "mailbox"`, and `refs/threeway/*`
held zero refs while `refs/heads` held 110), so every probe of it was already
short-circuited. With one transport there is no authority to prove and no
"unconsulted bus mistaken for an empty one" failure mode to defend against.
A legacy scalar cursor still resolves against the canonical ordered mailbox
projection; an invalid cursor resolves to unavailable, never to zero.

All new events pass through `coordination/bin/send-event` and the fixed writer,
which rejects malformed envelopes, invalid sender/kind combinations, and
invalid review-request structure before publication. Historical event files
remain immutable evidence; a grandfathered malformed artifact is reported as
invalid and grants no authority.

## 7. Review and external effects

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
schema, token, review result, or peer receipt.

Because the supported adapters are exactly Claude and Codex, and every model a
Claude harness selects is claude-family, the different-family counterparty for
Claude-authored work is Codex — reached with `pipeline peer ask codex`, whose
receipt records the model that side's own output reported.

## 8. Verification

```bash
pipeline check                                  # the completion-gate aggregate
coordination/bin/pipeline-python -m pytest tests -q
pipeline check coordination
```

`ci.yml` sets `NO_CEREMONY_BASE` to the pull-request base, so the growth
budget is measured across the whole range rather than one commit. Reproduce
that locally with
`NO_CEREMONY_BASE=$(git merge-base main HEAD) pipeline check ceremony`.

Smoke and tests prove only the behavior they execute; they do not commit,
publish, consume, push, merge, invoke a peer, or issue a formal verdict.

## 9. Compatibility boundaries

- The four concrete seat names remain mailbox/review compatibility identities;
  they are not a requirement to allocate four agents to every task.
- Historical events, capacity packets, and SHA citations remain evidence and may
  contain superseded process language, including paths under the pre-rename
  `scripts/` prefix. The committed-mailbox projection normalizes those
  references rather than rewriting frozen provenance.
- A configured model name is runtime evidence, not cryptographic provider
  attestation. A peer receipt narrows the gap without closing it.
- A normal target checkout may be stale relative to an explicitly routed
  target worktree; the route's exact target and base win.
