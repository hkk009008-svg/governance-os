# Claude Continuation Adapter

This is the short Claude Code adapter onto Pipeline's live governance kernel —
the Claude analog of `docs/protocol/codex/continuation.md`. The active
invariant is: **durable shared state beats chat memory.** Read git, signed
ref-bus facts, mailbox bodies, cursors, locks, logs, gate evidence, and
operator reports before trusting stale prose — including the prose in
`docs/protocol/claude/` rule bodies, which predate the live kernel.

The signed three-way ref-bus is the load-bearing state source for three-way
facts. The free-form mailbox remains the human coordination channel and must
still be checked before four-seat protocol decisions. **Bus liveness oracle:**
`git for-each-ref refs/threeway/` — if it returns nothing locally, the legacy
mailbox remains authoritative for local work (verify remote with
`git ls-remote origin 'refs/threeway/*'` before claiming remote bus authority).

All Claude seats, including coordinator, must actively eliminate ceremony and
theater behavior. Status notes, routes, handoffs, receipts, and no-op reports
are valid only when they preserve real transfer state, change enforcement, or
cite executable evidence; green-looking prose is not protocol proof.

For folder ownership, use `docs/protocol/protocol-assembly-map.md`. For the
numbered rule bodies (Rules #7–#23), use
`docs/protocol/claude/director-operator.md`. This file maps the kernel onto
Claude Code commands and runtime choices; where an older Claude-tree rule body
disagrees with this adapter on live-kernel specifics (verdict vocabulary,
paths, channels), this adapter wins.

## Verdict vocabulary (supersedes emoji verdicts)

The seat-level verification verdict is **GO / NITS / FAIL**, carried by a
mailbox `verification-report`. Dispatched reviewers use the canonical enum
`pass | issues | unable_to_verify` from `docs/templates/claude/reviewer.md`
(GO = pass · NITS = issues, all minor · FAIL = issues with ≥1
critical/important). Older Claude-tree prose that renders verdicts as
emoji (✅/⚠️/❌/⛔) is a human render only — never a second machine encoding.

## Seat identity

- The seat universe is fixed: `director`, `director2`, `operator`,
  `operator2`, `coordinator`, `coordinator2` — two director↔operator pairs
  (Pair A = director+operator, Pair B = director2+operator2) plus on-demand
  coordination.
- A Claude session claims a seat ONLY via explicit assignment: `CLAUDE_SEAT`
  exported at launch (with a per-seat `GIT_INDEX_FILE`), or the user naming
  the seat directly in the prompt. Never infer a seat from context.
- Three-way Layer-1 provider map (`docs/protocol/threeway/UNIFIED-OPERATING-DOCTRINE.md`
  §I.2): **Claude occupies `director2` (Pair-B builder), `operator` (Pair-A
  primary verifier), and `coordinator` (Pair-A executing integrator)**; Codex
  occupies `director`, `operator2`, `coordinator2`. The provider that wrote a
  change is locked out of the primary verification and executing integration
  of its own work. Inside the four-seat campaign, either provider can inhabit
  a seat via its env var (`CLAUDE_SEAT` / `CODEX_SEAT`); the Layer-1 map
  governs signed-bus authority once `refs/threeway/*` is live.

## Runtime modes

- **Readiness orientation: default mode.** Report current durable state and
  blockers. Do not consume cursors, send mailbox events, claim locks, push,
  spend, edit inventory, or author production changes.
- **Live seat:** only when the user or parent prompt explicitly names
  `director`, `director2`, `operator`, or `operator2` — or the session was
  launched with `CLAUDE_SEAT` set to that seat. Load the matching seat skill
  (`seat-director` / `seat-operator`) and work inside that seat's authority.
- **Coordinator:** only when explicitly asked to reconcile, route, gate, or
  operate cross-seat state. Load `seat-coordinator`. The coordinator is
  unpinned and never consumes a coordinator cursor.
- **Subagent:** bounded by the parent prompt. Subagents never inherit
  live-seat or coordinator authority.

Never silently upgrade from orientation mode into a seat.

## Same-seat handoff first

On a fresh/transplanted instance, if the user or parent prompt names a live
seat or coordinator, locate the newest handoff from that same concrete role
before ordinary orientation: newest `docs/HANDOFF-<concrete-seat>-*.md` for a
live seat, newest `docs/HANDOFF-coordinator-*.md` for coordinator. If no
same-seat handoff exists, state that and continue with the first commands.

## First commands

Readiness orientation:

```bash
.venv/bin/python scripts/continuation_readiness.py
env -u GIT_INDEX_FILE git log --oneline -5
```

Live seat (also stated in the seat skills):

```bash
.venv/bin/python .claude/skills/four-seat-protocol/scripts/seat_status.py <seat> --wave 2
env -u GIT_INDEX_FILE git log --oneline -5
env -u GIT_INDEX_FILE git status --short
```

Coordinator:

```bash
.venv/bin/python .claude/skills/four-seat-protocol/scripts/seat_status.py coordinator --wave 2
env -u GIT_INDEX_FILE git log --oneline -5
.venv/bin/python scripts/wave_gate_check.py 2
.venv/bin/python scripts/ci_smoke.py
```

Before committing an active coordinator task-board route, render the
hard-gated capacity board and validate the draft route; for a strict read-only
validation bundle, run the protocol doctor:

```bash
env -u GIT_INDEX_FILE .venv/bin/python scripts/protocol_capacity_board.py --wave <wave>
env -u GIT_INDEX_FILE .venv/bin/python scripts/protocol_capacity_board.py --wave <wave> --validate-route coordination/mailbox/sent/<event>.md
env -u GIT_INDEX_FILE .venv/bin/python scripts/protocol_doctor.py --wave <wave>
env -u GIT_INDEX_FILE .venv/bin/python scripts/protocol_doctor.py --wave <wave> --route coordination/mailbox/sent/<event>.md
```

The doctor is evidence, not an operator-GO substitute. Optional read-only
tools: `scripts/mailbox_monitor.py --once` (or `--watch --interval 5` as an
awareness watchboard — it never consumes or claims a seat) and
`scripts/draft_handoff.py <seat> --wave 2 --smoke --output` to scaffold a
handoff — always refresh live state before finalizing one.

## Mailbox-first rule + cursor consumption

Always check mail before protocol decisions or state-asserting writes. Counts
are not enough: read the relevant `coordination/mailbox/sent/*.md` bodies and
let the newest binding event shape the decision.

Cursor consumption is a separate live-seat mutation, and the consume path
depends on the seat's cursor form:

- **Legacy ISO-timestamp cursor** → `coordination/bin/consume-events <seat>`
  (stages `coordination/mailbox/seen/<seat>.txt`; never commits).
- **Migrated scalar-seq cursor** (post-Slice-2.5; `consume-events` refuses it
  and says so) → `scripts/consume_bus.py <seat>`. Real unread for a migrated
  seat comes from the ref-bus (`scripts/bus_unread.py` — a library surfaced
  via `seat_status.py`, not a CLI), NOT from `sent/` filename counts — the
  legacy count silently reports 0.
- **Race-safe bounded consume:** when consuming an already-read window while
  peer seats may still send mail, prefer
  `coordination/bin/consume-events <seat> --to <last-read-timestamp>` (legacy
  cursors only) so a not-yet-read event never gets skipped.
- **Receipt checks are coordination evidence only** — they never prove
  assigned work is complete.

Do not consume from orientation mode. Do not consume coordinator mail — a
policy rule (the tools mechanically accept coordinator since Slice-2.5; the
prohibition is doctrinal, not tool-enforced).

## Shared guardrails (ADR-027)

(Origin scopes per AGENTS.md: R-HOT-TREE and R-WIP-POLLUTION bind every seat;
R-GATE-EVIDENCE originated coordinator-scoped and R-VERIFY-THEN-PUSH
director/coordinator-scoped — treat all four as binding whenever you commit,
cite a gate, or hold push authority.)

- **R-HOT-TREE:** the shared tree moves under you. Immediately before any
  commit or gate decision, re-run `git log --oneline -3` and re-read the
  mailbox; first commit to land wins.
- **R-WIP-POLLUTION:** peer WIP is invisible to your index. Commit with
  explicit pathspecs only (`git commit -m "..." -- <paths>`); never a bare
  `git commit` or `git add -A` on the shared tree.
- **R-GATE-EVIDENCE:** a gate script's PASS is process evidence, not
  correctness proof. Cite what was mechanically executed (pins under
  `--runxfail`, the operator GO) — never a status tally alone.
- **R-VERIFY-THEN-PUSH:** no push before the operator verification-report GO;
  push itself remains user-gated.

## Emergency Handling

- Emergency scope is exactly four categories: Production-affecting OR
  user-data-integrity issue, Security-critical, Active bleed-rate, and
  External time-pressure.
- Events outside those four categories use normal role partition and proposal
  cycles, even when they feel urgent.
- The first-noticer claims initial response with a `dispatch-claim` mailbox
  event carrying `urgency: emergency`.
- Triage discipline is stop-the-bleed first: use the smallest mitigation
  before root-cause analysis.
- Cross-seat temporary authority applies only during transplant or context
  exhaustion, and the commit body must include `acting under v5 §E temporary
  authority`.
- The coordinator no-production-code boundary remains in force during
  emergency routing and reconciliation.
- Within one session of resolution, write a post-incident note in
  `docs/INCIDENT-LOG.md` and review protocol gaps.

## Disagreement Handling

- States the disagreement explicitly in the next-cycle revision.
- Provides project-data-grounded evidence for the disputed item.
- Chooses exactly one resolution path: counter-refinement, defer to v(N+1), or
  acceptance criterion.
- silent-accept is the receiver's own acceptance, not permission inferred from
  peer silence.
- Re-REPLY is allowed for a live objection, but the 2-cycle escalation limit
  sends persistent disagreement to the user-principal.

## Blocked-Wave And Acting-Coordinator Handling

- Require wave-gate evidence before asserting blocked.
- Trigger immediate pod-off when a director gate-request is unserviced.
- Send one consolidated mailbox event naming blocker, owner, and SLA.
- If the owning coordinator is absent, escalate to user with the
  acting-coordinator path.
- Use a pre-brief skeleton only until the blocked owner or user direction
  confirms scope.
- Use no gate-relaxing or suppressive pins to make a blocked wave look green.
- A blocked-wave transition is verified only from operator GO, not route prose
  or a gate script alone.

## Reviewer Result Handling

- Use findings-first ordering by severity for review output and verification
  reports.
- When relaying reviewer or verifier output, preserve verdict, findings, and
  next steps.
- Separate uncertainty, inference, and follow-up so readers can tell evidence
  from hypothesis.
- Do not auto-fix after a review; route or request the next implementation
  action instead.
- Failed, incomplete, or unable_to_verify runs are not permission to invent
  substitute output.

## Side-Effect Gate

User-gated side effects: push, lock-claim side effects, paid API spend, and
pod spend require explicit user consent. Use `env -u GIT_INDEX_FILE` for
ordinary git and pytest commands unless deliberately maintaining a seat-local
index.

Side-Effect Executor Token:
- Required fields: `side_effect_id`, `executor`, `target`,
  `allowed_command_class`, `preflight`,
  `stop_if_newer_mail_or_live_target_satisfied`, `postcheck`,
  `observer_seats`, `final_closeout_owner`, and `non_goals`.
- Generic user approval is unit consent, not executor election.
- Shared user-gated side effects need exactly one named executor before
  mutation unless the user directly names the executing seat in the same
  prompt.
- Side effects covered: remote-ref update, force update, lock action,
  paid-service spend, pod action, production generation, target-repo checkout
  refresh, cursor consume, and route mutation.
- Observer seats default to observer mode: read live state only, do not repeat
  the side effect, and report only contradiction, missing required evidence,
  changed safety boundary, or explicit coordinator request.
- Live evidence may close an already-satisfied side effect without appointing
  a redundant executor.
- Multiple same-target side-effect success claims need a common
  side_effect_id; otherwise route validation fails.

## Pair Operating Contract

- director -> operator is the fast path inside each pair: director scopes and
  sends the smallest sufficient artifact; operator verifies only that artifact
  or landed commit.
- Every baton handoff is a mailbox artifact, not chat: brief, verify-request,
  verification-report, or handoff with commit/range, paths, tests, exclusions,
  and exact next trigger.
- Every live-seat/coordinator turn ends with an `Exact Next Trigger` section
  naming the next lawful prompt, seat event, standby condition, or blocker —
  the final user-facing section as well as the terminal mailbox/handoff
  section.
- Director sends one verify-request per implementation or brief once scope is
  stable; include commit/range, brief path, evidence commands, known excluded
  workspace state, and expected verdict.
- Operator waits for a fresh verify-request or shipping commit; no duplicate
  Lane V for docs-only, status-only, or handoff-only commits, and no
  speculative verification when phase is ambiguous.
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

## Capacity Split Default

- Single-pair fast path remains the default for narrow or shared-file work.
- Divisible or preplanned larger work defaults to dual-pair routing.
- Coordinator promotion question: can this route produce two independently
  reviewable deliverables?
- If yes: director owns Chunk A and operator verifies Chunk A; director2 owns
  Chunk B and operator2 verifies Chunk B.
- If no: keep one pair implementing while Pair B performs bounded planning or
  preflight instead of idle standby.
- The two active chunks must name disjoint write sets, explicit interfaces,
  focused tests, forbidden side effects, and separate
  verify-request/verification-report loops.
- Pair B preflight packets use `director-preflight` and `operator-preflight`
  packet types (`coordination/capacity/packets/*.json`, validated by
  `scripts/protocol_capacity.py`).
- Coordinator owns convergence: capacity packets, one consolidated route, join
  condition, conflict handling, and final closeout evidence.

## Seat Subagent Development (Claude-native)

Core rule: seats retain authority; subagents own bounded work. Live seats and
coordinator may choose bounded subagents at seat discretion; after
orientation, record a Subagent utilization decision (dispatch a bounded helper
for a named task, or direct/no-op with the reason).

- Director seats may dispatch bounded implementer subagents
  (`docs/templates/claude/implementer.md` body, including its Git-hygiene
  block); required loop: implementer -> spec review -> quality review ->
  director-seat synthesis. The director still writes the brief and
  verify-request.
- Operator seats may dispatch read-only verifier helpers — the `lane-v-verifier`
  agent for independent post-commit verification, `money-gate-reviewer` for
  cost-gate diffs, cold-context reviewers per
  `docs/templates/claude/reviewer.md`. The operator seat still issues
  GO/NITS/FAIL.
- Coordinator may dispatch read-only reconciliation helpers for inventory,
  mailbox, lock, gate, or plan-readiness checks; it still owns the
  consolidated route or no-op report.
- Subagent prompts carry only the relevant rule IDs, allowed paths, acceptance
  evidence, forbidden side effects, and `env -u GIT_INDEX_FILE` git/pytest
  hygiene — never inherited doctrine.
- Subagents do not consume cursors, send mailbox events, issue GO, route
  coordinator work, push, claim locks, start pods, or spend paid API budget.
- Do not run parallel implementation subagents on shared files or behind the
  same push-gated lock.

## Codex Function Harmonization

Core stance: adapt Codex-native protocol mechanics to Claude Code primitives;
do not transplant Codex-only mechanics.

- `CODEX_SEAT` -> `CLAUDE_SEAT`; both resolve the same six-seat universe.
- Codex `apply_patch` edits -> Claude `Edit`/`Write` tools.
- Codex exec sessions for long verification -> `Bash` with
  `run_in_background: true`; read the result before claiming status.
- Codex `sandbox_mode = "read-only"` agents -> Claude agent definitions with
  read-only tool sets (`.claude/agents/*.md`, `tools: Read, Grep, Glob, Bash`).
- Codex `.codex/agents/*.toml` role agents -> Claude seat skills
  (`.claude/skills/seat-*`) for main-session seats, plus `.claude/agents/*`
  for bounded helpers. Claude seats are interactive main sessions, not
  subagents; a Claude subagent never holds seat authority.
- Reviewer evidence rigor is shared verbatim: `pass | issues |
  unable_to_verify`, reviewed-head checks, clean-tree checks, command
  evidence (`docs/templates/claude/reviewer.md`).

## Ledger CLI Adoption Bridge

For work routed to `/Users/hyungkoookkim/evidence-ledger`, read
`docs/protocol/codex/ledger-cli-adoption.md` (the bridge doc is
provider-shared) before entering the target repo. Pipeline remains the
four-seat governance kernel; evidence-ledger owns product-local truth.
Cross-repo git and pytest commands use `env -u GIT_INDEX_FILE` so Pipeline
seat indexes do not leak into ledger work. Start from
`/Users/hyungkoookkim/Pipeline` and run
`env -u GIT_INDEX_FILE .venv/bin/python scripts/ledger_start_guard.py --seat <seat> --wave 2`
before target-repo inspection (the guard accepts the five standing seats;
`coordinator2`, being on-demand oversight, is not in its VALID_SEATS). Read
evidence-ledger `CLAUDE.md` before product edits.

## Verification Commands

Run the narrow command that proves the current claim:

```bash
env -u GIT_INDEX_FILE .venv/bin/python scripts/ci_smoke.py
.venv/bin/python scripts/wave_gate_check.py 2
env -u GIT_INDEX_FILE git status --short
env -u GIT_INDEX_FILE git diff --stat
```

## Related files

- Rule bodies (Rules #7–#23): `docs/protocol/claude/director-operator.md`
- Four-seat extension (coordinator §10, co-sign tiers):
  `docs/protocol/claude/four-seat-extension.md`
- Codex adapter (peer document): `docs/protocol/codex/continuation.md`
- Unified three-way doctrine: `docs/protocol/threeway/UNIFIED-OPERATING-DOCTRINE.md`
- Seat status: `.claude/skills/four-seat-protocol/scripts/seat_status.py`
- Daily loop: `RUNBOOK-DAILY.md` · Program intent: `docs/PROGRAM-MANUAL.md`
- Verified truth: `ARCHITECTURE.md` · Folder intent:
  `docs/protocol/protocol-assembly-map.md`
