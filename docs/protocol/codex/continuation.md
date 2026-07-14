# Codex Continuation Adapter

This is the short Codex adapter for the executable harness kernel in
`scripts/codex_protocol_model.py`. The active invariant is: durable shared state beats chat memory. Read git, signed ref-bus facts, mailbox bodies, cursors, locks, logs, gate evidence, and operator reports before trusting stale prose.

The signed three-way ref-bus is the load-bearing state source for three-way
facts. The free-form mailbox remains the human coordination channel and must
still be checked before four-seat protocol decisions.

All Codex seats, including coordinator, must actively eliminate ceremony and
theater behavior. Status notes, routes, handoffs, receipts, and no-op reports
are valid only when they preserve real transfer state, change enforcement, or
cite executable evidence; green-looking prose is not protocol proof.

For folder ownership, use `docs/protocol/protocol-assembly-map.md`. For full
agent-neutral governance, use `docs/protocol/agents/`. This file only maps the
kernel onto Codex commands and runtime choices.

## Codex Risk-Tier Router

- `tier-0-conversational`: a self-contained answer. Use no repo orientation,
  implementation skills, mailbox checks, smoke, worktree, or verification
  commands.
- `tier-1-read-only`: repository inspection or an evidence-backed report. Use
  the smallest scoped read commands. Brainstorming, TDD, worktree,
  plan-writing, implementation-review, and completion-verification skills do
  not apply unless the user changes the task into design or mutation work.
  Live-seat checks require an explicit seat, mailbox, route, wave, handoff, or
  protocol-decision trigger.
- `tier-2-local-mutation`: an ordinary code, test, config, or documentation
  edit. Use impact analysis, task-relevant implementation discipline, focused
  tests, and one fresh completion verification pass.
- `tier-3-governed-side-effect`: a live-seat decision, shared protocol state,
  or external side effect. Apply the exact mailbox, capacity,
  independent-verification, and user-authorization gates for that action.

Deterministic artifact evidence may be reused against an unchanged HEAD and
unchanged relevant paths. Tier 3 requires fresh signed-bus, mailbox/cursor,
lock, approval, and external-state checks; reuse never relaxes a triggered
guard.
Do not launch another generic reviewer or repeat Lane V for the same unchanged
commit unless it asks a genuinely different, pre-stated question.

## ChatGPT Pro Advisory Consultation

This capability is always invocable in readiness, director, coordinator, and
operator modes. The default is `auto`, which permits one guarded send per
idempotency key through only the current runtime in-app Browser transport
(`iab`); `manual` is an explicit legacy compatibility mode, and `off` fails
closed. The auto transport order is `iab -> block`: there is no automatic
Chrome, manual relay, API, retry, or workaround fallback. Raw
prompts and responses stay out of Git, mailbox artifacts, normal logs,
screenshots, command arguments, and transcript files. Output is advisory only
and not the dual-chief order path; it grants no protocol or side-effect
authority; subagents may prepare a bounded question but only the parent context
may send or import a response. Follow
`.agents/skills/chatgpt-pro-consultation/SKILL.md`.

If `iab` is unavailable, signed out, challenged, or ambiguous before send,
transition the record to `failed` when safe to do so and block with zero send.
Uncertain or partial delivery also blocks without retry or fallback.

- Readiness may consult ideas or plans without upgrading into a seat.
- Director may consult design, brief, or plan tradeoffs, then verify claims
  locally.
- Coordinator is mailbox-first before consultation: refresh HEAD, mailbox
  bodies, route, wave, capacity, and locks before prepare, then refresh HEAD,
  mailbox bodies, route, wave, capacity, and locks again before send and before
  use; pre-send drift discards the prepared packet and requires re-prepare, and
  later drift marks the response stale.
- Operator consultation never replaces Lane V. Allow it only on explicit user
  request or for a distinct, pre-stated strategic question; it cannot
  contribute authority to GO, NITS, or FAIL.

## R-INDEPENDENCE

Scope: both.
Trigger: before designing or implementing, classify whether the change touches an adversarial-surface: input rendered or composed into a parseable or executable context; authority or security-boundary enforcement; side-effect gating; or schema validation whose acceptance grants trust.
Action: triggered work requires an independent design-time enumeration of abuse cases, edge cases, and coverage targets before implementation. A different model or harness is preferred; a same-model independent reviewer is weaker and must be identified. Fold the result into enforced-and-tested acceptance criteria in a committed plan or equivalent durable artifact. Before completion, an independent reviewer must verify the actual diff against those cases. For Codex-authored adversarial work, Lane V plus verdict-blind Opus supplies the per-task cross-model pair.
Deduplication: R-VERIFY-TIER still prohibits redundant same-question passes. Non-adversarial, read-only, and hermetic work uses the smallest sufficient profile.
Evidence: the committed design-time enumeration artifact and the independent verification report naming the reviewer and harness.
Details: `docs/protocol/claude/independence-first.md` (ADR-019).

## Claude Function Harmonization:

- core stance: adapt Claude functions to Codex-native primitives; do not transplant Claude-only mechanics.
- AskUserQuestion discipline: ask only for cross-cutting, policy, or
  hard-to-reverse choices; use repo convention and durable state for ordinary
  file, naming, and routing choices.
- background work discipline: let long verification run in an exec session
  while independent read-only context gathering continues, then read the result
  before claiming status.
- dispatch-template minimalism: give subagents only the relevant rule IDs,
  allowed paths, evidence checks, side-effect limits, and env-u git hygiene
  instead of inherited doctrine.
- reviewer evidence rigor: reviewers use `pass | issues | unable_to_verify`,
  U1-U5 unverifiable reasons, reviewed-head checks, clean-tree checks, and
  command evidence.
- adversarial verification: verification agents actively try to make the gate
  or proof fail with non-vacuous RED, `--runxfail`, sibling, and
  touched-script/hook checks.

## Emergency Handling

- Emergency scope is exactly four categories: Production-affecting OR user-data-integrity issue, Security-critical, Active bleed-rate, and External time-pressure.
- Events outside those four categories use normal role partition and proposal cycles, even when they feel urgent.
- The first-noticer claims initial response with a `dispatch-claim` mailbox event carrying `urgency: emergency`.
- Triage discipline is stop-the-bleed first: use the smallest mitigation before root-cause analysis.
- Cross-seat temporary authority applies only during transplant or context exhaustion, and the commit body must include `acting under v5 §E temporary authority`.
- The coordinator no-production-code boundary remains in force during emergency routing and reconciliation.
- Within one session of resolution, write a post-incident note in `docs/INCIDENT-LOG.md` and review protocol gaps.

## Disagreement Handling

- States the disagreement explicitly in the next-cycle revision.
- Provides project-data-grounded evidence for the disputed item.
- Chooses exactly one resolution path: counter-refinement, defer to v(N+1), or acceptance criterion.
- silent-accept is the receiver's own acceptance, not permission inferred from peer silence.
- Re-REPLY is allowed for a live objection, but the 2-cycle escalation limit sends persistent disagreement to the user-principal.

## Blocked-Wave And Acting-Coordinator Handling

- Require wave-gate evidence before asserting blocked.
- Trigger immediate pod-off when a director gate-request is unserviced.
- Send one consolidated mailbox event naming blocker, owner, and SLA.
- If the owning coordinator is absent, escalate to user with the acting-coordinator path.
- Use a pre-brief skeleton only until the blocked owner or user direction confirms scope.
- Use no gate-relaxing or suppressive pins to make a blocked wave look green.
- A blocked-wave transition is verified only from operator GO, not route prose or a gate script alone.

## Reviewer Result Handling

- Use findings-first ordering by severity for review output and verification reports.
- When relaying reviewer or verifier output, preserve verdict, findings, and next steps.
- separate uncertainty, inference, and follow-up so readers can tell evidence from hypothesis.
- do not auto-fix after a review; route or request the next implementation action instead.
- failed, incomplete, or unable_to_verify runs are not permission to invent substitute output.

## Ledger CLI Adoption Bridge

For work routed to `/Users/hyungkoookkim/evidence-ledger`, use
`docs/protocol/codex/ledger-cli-adoption.md` before entering the target repo.
Pipeline remains the Codex four-seat governance kernel; evidence-ledger owns
product-local truth. Cross-repo git and pytest commands use
`env -u GIT_INDEX_FILE` so Pipeline seat indexes do not leak into ledger work.
Do not start ledger work from `/Users/hyungkoookkim/Content`. Start from
`/Users/hyungkoookkim/Pipeline` and run
`env -u GIT_INDEX_FILE .venv/bin/python scripts/ledger_start_guard.py --seat <seat> --wave 2`
before target-repo inspection.

## Runtime modes

- Readiness bridge: default mode. Report current durable state and blockers.
  Do not consume cursors, send mailbox, claim locks, push, spend, edit
  inventory, or author production changes.
- Live seat: only when the user or parent prompt explicitly names `director`,
  `director2`, `operator`, or `operator2`. Work inside that seat's authority.
- Coordinator: only when explicitly asked to reconcile, route, gate, or operate
  cross-seat state. The coordinator is unpinned and never consumes a
  coordinator cursor.
- Subagent: bounded by the parent prompt. Subagents never inherit live-seat or
  coordinator authority. The parent seat may assign bounded work, but the seat
  keeps mailbox, cursor, GO/NITS/FAIL, route, lock, push, and spend authority.

## Live-Seat Behavior Sources

Concrete live-seat identity and canonical behavior source are separate.
Behavior source map: `director -> director`, `director2 -> director`, `operator -> operator2`, `operator2 -> operator2`.

Mailbox, cursor, heartbeat, event-addressing, and git-index operations use the concrete seat, not the behavior source.
For example, `CODEX_SEAT=operator` uses operator mailbox/cursor/index paths
while following the `operator2` behavior source.

## Same-Seat Handoff First

On a fresh/transplanted instance, if the user or parent prompt names a live
seat or coordinator, locate the newest handoff from that same concrete role
before ordinary orientation:

- Live seat: newest `docs/HANDOFF-<concrete-seat>-*.md`.
- Coordinator: newest `docs/HANDOFF-coordinator-*.md`.

Use the concrete seat, not the behavior source. For example, `director` reads
`HANDOFF-director-*`, not `HANDOFF-director2-*`. If no same-seat handoff exists,
state that and continue with the first commands below.

## First Commands

Readiness bridge:

```bash
.venv/bin/python scripts/continuation_readiness.py
env -u GIT_INDEX_FILE git log --oneline -5
```

Live seat:

```bash
.venv/bin/python .agents/skills/four-seat-protocol/scripts/seat_status.py <seat> --wave 2
env -u GIT_INDEX_FILE git log --oneline -5
```

Coordinator:

```bash
.venv/bin/python .agents/skills/four-seat-protocol/scripts/seat_status.py coordinator --wave 2
env -u GIT_INDEX_FILE git log --oneline -5
.venv/bin/python scripts/wave_gate_check.py 2
.venv/bin/python scripts/ci_smoke.py
```

Before committing an active coordinator task-board route, render the hard-gated
capacity board and validate the draft route:

```bash
env -u GIT_INDEX_FILE .venv/bin/python scripts/protocol_capacity_board.py --wave <wave>
env -u GIT_INDEX_FILE .venv/bin/python scripts/protocol_capacity_board.py --wave <wave> --validate-route coordination/mailbox/sent/<event>.md
```

For a strict read-only protocol validation bundle, run the protocol doctor:

```bash
env -u GIT_INDEX_FILE .venv/bin/python scripts/protocol_doctor.py --wave <wave>
env -u GIT_INDEX_FILE .venv/bin/python scripts/protocol_doctor.py --wave <wave> --route coordination/mailbox/sent/<event>.md
```

Closed-cycle coordinator-join packets are also hard-gated: standby, idle,
closeout, transfer, or transplant evidence must cite a durable
`docs/HANDOFF-*.md` artifact instead of ending on a chat-only or generic
`Exact Next Trigger`.

Use `<wave>` when the active wave is not 2:

```bash
.venv/bin/python scripts/wave_gate_check.py <wave>
```

## Mailbox-First Rule

mailbox-first decisions: always check mail before protocol decisions or
state-asserting writes. Counts are not enough: read the relevant
`coordination/mailbox/sent/*.md` bodies and let the newest binding event shape
the decision. Cursor consumption is a separate live-seat mutation:

```bash
coordination/bin/consume-events <seat>
```

Do not run that command from readiness bridge mode. Do not consume coordinator
mail.

## Side-Effect Gate

The kernel names `user-gated side effects`: push, lock-claim side effects, paid
API spend, and pod spend require explicit user consent. Use
`env -u GIT_INDEX_FILE` for ordinary git and pytest commands unless you are
deliberately maintaining a seat-local or scoped temporary index.

Side-Effect Executor Token:
- Required fields: `side_effect_id`, `executor`, `target`,
  `allowed_command_class`, `preflight`,
  `stop_if_newer_mail_or_live_target_satisfied`, `postcheck`,
  `observer_seats`, `final_closeout_owner`, and `non_goals`.
- generic user approval is unit consent, not executor election.
- shared user-gated side effects need exactly one named executor before mutation unless the user directly names the executing seat in the same prompt.
- side effects covered: remote-ref update, force update, lock action, paid-service spend, pod action, production generation, target-repo checkout refresh, cursor consume, and route mutation.
- observer seats default to observer mode: read live state only, do not repeat
  the side effect, and report only contradiction, missing required evidence,
  changed safety boundary, or explicit coordinator request.
- live evidence may close an already-satisfied side effect without appointing a
  redundant executor.
- multiple same-target side-effect success claims need a common side_effect_id; otherwise route validation fails.
- report only contradiction, missing required evidence, changed safety boundary, or explicit coordinator request.

The coordinator may route and reconcile but does not author behavior-changing
production fixes. A verified inventory transition still needs an operator
`verification-report` GO plus executed evidence; a gate script is process
evidence, not row-correctness proof.

## Pair Operating Contract

- director -> operator is the fast path inside each pair: director scopes and
  sends the smallest sufficient artifact; operator starts Lane V only from
  lawful trigger authority.
- Every baton handoff is a mailbox artifact, not chat: brief, verify-request,
  verification-report, or handoff with commit/range, paths, tests, exclusions,
  and exact next trigger.
- Every live-seat/coordinator turn ends with an `Exact Next Trigger` section
  naming the next lawful prompt, seat event, standby condition, or blocker; make
  it the final user-facing section as well as the terminal mailbox/handoff
  section.
- Director sends one canonical committed verify-request per implementation or
  brief once structural scope authority is stable; include paths, tests,
  evidence commands, known exclusions, and expected verdict without
  substituting them for authority.
- Operator waits for a lawful authority-bearing trigger; no duplicate Lane V for
  docs-only, status-only, or handoff-only commits, and no speculative
  verification when phase is ambiguous.
- No receipt/status churn: send mail only when it changes ownership, preserves
  evidence, requests verification, returns GO/NITS/FAIL, or blocks on
  user-gated side effects.
- When both seats are active, do not edit the same files or rerun the same
  task; first commit to land wins and the other seat narrows or stands down
  after git/mailbox refresh.
- At boundaries, stop with exact next trigger and durable handoff only when
  context is transferring; avoid broad recaps when mailbox/gate state already
  proves standby.
- Effectiveness means a closed loop: director artifact -> operator
  verification-report GO/NITS/FAIL -> director consumes the report or
  coordinator closes; gate scripts never substitute for operator
  verification-report GO.

Lane V trigger authority: a verify-request trigger is a canonical committed
sent-mailbox event strictly after the reviewed HEAD with exactly one
`Event type: verify-request`, one `Reviewed head: <40-lowercase-hex>`, one
`Reviewed base: <40-lowercase-hex>`, and one
`Lane-V-Scope: coordination/verification/scopes/<uuid>.json@sha256:<64-lowercase-hex>`
whose values agree with the committed descriptor and canonical
filename/envelope. A shipping trigger commit equals the reviewed HEAD, its
subject begins `feat`, `fix`, or `refactor`, and exactly one identical descriptor
reference in the terminal Git trailer block supplies its `Lane-V-Scope`.
Missing, duplicated, abbreviated, uppercase, misplaced, uncommitted, stale, or
mismatched authority is not a trigger: stop with a blocker, do not reconstruct
missing fields, and do not fall back to the other trigger kind. The descriptor
and trigger grammar is Pipeline-only; cross-repository or evidence-ledger review
must return to the coordinator for a separate evidence-ledger-aware bridge route
and never fabricate Pipeline descriptor authority.

## Capacity Split Default:

- single-pair fast path remains the default for narrow or shared-file work.
- divisible or preplanned larger work defaults to dual-pair routing.
- Coordinator promotion question: can this route produce two independently reviewable deliverables?
- If yes: director owns Chunk A and operator verifies Chunk A; director2 owns Chunk B and operator2 verifies Chunk B.
- If no: keep one pair implementing while Pair B performs bounded planning or preflight instead of idle standby.
- The two active chunks must name disjoint write sets, explicit interfaces, focused tests, forbidden side effects, and separate verify-request/verification-report loops.
- Pair B preflight packets use `director-preflight` and `operator-preflight` packet types.
- coordinator owns convergence: capacity packets, one consolidated route, join condition, conflict handling, and final closeout evidence.

## Optional Tools

- `scripts/mailbox_monitor.py --once` or `--watch --interval 5`: read-only
  mailbox awareness without claiming a seat.
- `scripts/draft_handoff.py <seat> --wave 2 --smoke --output`: draft a
  handoff evidence scaffold; refresh live state before finalizing it.
- `scripts/protocol_effectiveness_report.py`: read-only diagnostics. It does
  not route work, consume mail, or decide inventory state.
- `scripts/protocol_capacity_board.py --wave <wave>`: read-only hard-gated
  capacity board; use `--validate-route coordination/mailbox/sent/<event>.md`
  before active coordinator task-board route commits.
- `scripts/protocol_doctor.py --wave <wave>`: strict read-only protocol bundle;
  use `--route coordination/mailbox/sent/<event>.md` when validating an active
  coordinator task-board route. It is evidence, not an operator GO substitute.
- `.codex/agents/agentNN.toml`: optional guardrail extensions. They do not
  replace seat authority, mailbox cursor rules, or user-gated push.

## Subagents

Use project role agents only when the parent prompt asks for that role:
`protocol-director`, `protocol-operator`, `protocol-coordinator`,
`lane-v-verifier`, or `money-gate-reviewer`. A live seat or coordinator may
create that parent prompt at seat discretion when bounded subagent work would
add signal; this does not require a separate user request for delegation. Keep
the parent responsible for final synthesis and for any user-gated action.

## Seat Subagent Development

Core rule: seats retain authority; subagents own bounded work.
Live seats and coordinator may choose bounded subagents at seat discretion; this does not require a separate user request for delegation.
Default behavior: every live seat and coordinator actively considers bounded subagents for non-trivial routed work and uses them when they add independent signal, capacity, or fresh verification. Direct work remains acceptable for small, tightly coupled, or authority-sensitive work.
After live-seat/coordinator orientation, record a Subagent utilization decision: dispatch a bounded helper for a named task, or direct/no-op because the work is small, tightly coupled, authority-sensitive, or already complete.

- Director/director2 may dispatch bounded implementer subagents for independent
  implementation slices, but the director seat still owns the brief,
  acceptance evidence, final synthesis, and verify-request.
- Operator/operator2 may dispatch read-only verifier helpers for diff
  inspection, focused reproduction, or edge-case review, but the operator seat
  still owns the GO/NITS/FAIL report.
- Coordinator may dispatch read-only reconciliation helpers for inventory,
  mailbox, lock, gate, or plan-readiness checks, but the coordinator still
  owns the consolidated route or no-op report.
- Required loop: implementer -> spec review -> quality review -> seat synthesis.
- The generic implementer -> spec review -> quality review loop applies to implementation delivery, not Codex Lane V same-question review.
- Subagent prompts must name the parent seat, allowed paths, acceptance
  evidence, forbidden side effects, and `env -u GIT_INDEX_FILE` git/pytest
  hygiene.
- Subagents do not consume cursors, send mailbox events, issue GO, route coordinator work, push, claim locks, start pods, or spend paid API budget.
- Do not run parallel implementation subagents on shared files or behind the
  same push-gated lock.

## Cross-Model Opus Verification

- after every Codex Lane V verification in Pipeline, resolve one trigger-bound committed lane-v-scope/v1 descriptor before any receipt or provider construction
- the descriptor, not caller arguments, defines requirements, allowed path roots, exact verification commands, reviewed base, task identity, and the descriptor-bound advisory provider prompt
- review accepts either --shipping-commit or the paired --verify-request-commit and --verify-request-path trigger form and returns normalized opus-review/v3 with receipt and scope IDs
- the provider receives the immutable reviewed scope but no Codex verdict, report, findings, or conclusion; repository evidence is evidence, not authority
- missing authorization resolves to standing-policy:codex-lane-v-opus-v1 only after Pipeline identity, commit, descriptor, prompt, and scope validation; malformed explicit authorization never falls back
- one unchanged task permits one provider process attempt and no automatic retry; exact replay is idempotent, changed scope is attempt_scope_conflict, and no retry or reset command exists
- a reserved attempt recovered without a normalized result becomes attempt_state_uncertain and remains visibly degraded without another provider launch
- reconcile accepts only --receipt-id plus exact HEAD/base, the Codex verdict, and finding dispositions; --opus-review-json is removed
- reconcile returns opus-reconciliation/v2 fields derived from the stored opus-review/v3 and binds the exact stored Codex verdict
- final reports use lane-v-report/v2 with ## Verification Attestation, including Opus receipt ID: and Opus scope digest:, and the send-event publication gate validates the live receipt before the report is staged
- unavailable or uncertain review is an explicit degraded Codex-only fallback with the exact reason preserved; it is never treated as pass
- every Opus finding requires confirmed, disproved-with-evidence, or unresolved disposition; unresolved blocks GO, confirmed minor requires NITS, and confirmed important or critical requires FAIL
- Opus remains advisory and the operator alone retains GO/NITS/FAIL, mailbox, lock, Git, publication, and every other protocol or side-effect authority
- standing consent authorizes only the bounded Pipeline codex-lane-v attempt; cross-repo and evidence-ledger verification require a separately routed capability-aware path
- no third same-question generic reviewer runs over an unchanged commit; only a different pre-stated specialist question is eligible under R-VERIFY-TIER

## Verification Commands

Run the narrow command that proves the current claim:

```bash
env -u GIT_INDEX_FILE .venv/bin/python -m pytest tests/unit/test_imports_smoke.py tests/unit/test_protocol_mailbox.py tests/unit/test_status.py tests/unit/test_coordination_tooling.py tests/unit/test_ceremony_gates.py tests/unit/test_protocol_capacity.py tests/unit/test_protocol_doc_integrity.py tests/unit/test_protocol_prompt_sync.py tests/unit/test_codex_ledger_bridge.py -q
env -u GIT_INDEX_FILE .venv/bin/python scripts/ci_smoke.py
.venv/bin/python scripts/wave_gate_check.py 2
```

For a commit or handoff, also inspect scope:

```bash
env -u GIT_INDEX_FILE git status --short
env -u GIT_INDEX_FILE git diff --stat
```
