# Coordinator → All: standalone Claude trigger withdrawn; PPL held for receipt-bound Opus route

**When:** 2026-07-13T11:38:14Z · **From:** coordinator (online)

Event type: coordination
Disposition: `PPL_STANDALONE_NON_CODEX_TRIGGER_WITHDRAWN_OPUS_BRIDGE_PREREQUISITE_HELD`
Task-board: `ledger-ppl-recommendation-evaluation-2026-07-12`
Supersedes active trigger in:
`coordination/mailbox/sent/2026-07-13T08-34-37Z-coordinator-to-all-coordination.md`
Binding Operator report:
`coordination/mailbox/sent/2026-07-13T08-03-23Z-operator-to-all-verification-report.md`
Target worktree:
`/Users/hyungkoookkim/Pipeline/.worktrees/evidence-ledger-workbook-refresh-2026-07-11`
Target repository identity: `hkk009008-svg/evidence-ledger`
Target branch: `codex/ledger-workbook-refresh-2026-07-11`
Target worktree Gitdir:
`/Users/hyungkoookkim/evidence-ledger/.git/worktrees/evidence-ledger-workbook-refresh-2026-07-11`
Target Git common directory: `/Users/hyungkoookkim/evidence-ledger/.git`
Target candidate: `8eaed44f803d871f09135c5d89395d38cf9e939e`
Observed Opus hardening worktree:
`/Users/hyungkoookkim/Pipeline/.worktrees/opus-lanev-receipt-hardening`
Observed hardening HEAD: `5092b4d5e1ee7dd028caa60abf3a19aa78add48d`
Cursor at send: 0

## Findings And Binding Disposition

The user's direct clarification supersedes the prior instruction to start a
standalone Claude Code `director`. The required model is that non-Codex
capability enters this workflow through the bounded Opus review bridge: Codex
keeps the authoritative seat, Opus supplies a receipt-bound cross-model check,
and the live Operator retains GO/NITS/FAIL authority. Opus must not be described
or used as a mailbox seat, controller, committer, or side-effect executor.

The active hardening branch implements that model through immutable scope
descriptors, one replay-safe provider attempt, receipt-only reconciliation,
and verification-report attestations. At the observed committed checkpoint it has
landed its latest Task 5 attestation checkpoint (`5092b4d`) while its committed
plan still leaves Task 6 live publication, Task 7 doctrine convergence, final integration
verification, and the independent actual-diff gate unfinished.

The checkpoint is not yet textually authority-safe. The bridge loads the
trusted `.claude/agents/lane-v-verifier.md` body as an appended system prompt;
that body still calls the model an `operator-seat verifier`, requests a
`GO / NITS / FAIL` report, and discusses authorizing lock release. The machine
output schema and reconciliation keep the provider non-authoritative, but the
provider instruction contradicts both the approved advisory-only design and
the user's non-seat Opus direction. The committed Task 7 plan does not list the
loaded Claude prompt or require a regression over its actual rendered content.
The hardening owner must correct the plan first, then remove this inherited
seat, verdict, and lock-authority language and pin its absence before any Opus
call.

That branch is deliberately limited to the Pipeline repository and the
`codex-lane-v` review profile. The PPL correction lives in the separate
evidence-ledger linked worktree. Therefore neither the current main bridge nor
the unfinished hardened bridge may be represented as able to author, inspect,
or verify the target correction. Launching a standalone Claude Director,
calling the Pipeline-only bridge against evidence-ledger, or allowing a Codex
target commit before a different-model design-time check would violate the
current authority and independence boundaries.

The corrected candidate remains `FAIL` and the join remains `blocked`. This is
a real hold, not a correctness claim or a replacement verdict.

## Advisory Consultation Reconciliation

- Consultation ID: `2a860e88-f5d6-4179-92de-16dd141a6682`
- Phase: `coordinator`
- Bound HEAD/route: Pipeline `70ad83ee43f552bf4fa7071e0dd83a3819fe676d`,
  Wave 2 route `2026-07-13T08-34-37Z`
- Question: preserve Codex seat authority while adding bounded Opus challenge
  coverage for an evidence-ledger correction outside the V1 Pipeline bridge.
- Advice summary: hold the target correction; finish receipt hardening; build
  and independently verify a target-aware bridge; then use two distinct,
  non-authoritative Opus questions around a Codex-authored correction.
- Codex dispositions: `adopted` for the hold, target-aware extension, complete
  immutable binding, two distinct questions, explicit finding dispositions,
  and no automatic Opus authority; `modified` so the Codex Director owns only
  the later bounded implementation while the live Operator retains the binding
  GO/NITS/FAIL verdict; `rejected` for no item; `unresolved` until runtime
  negative tests and the trusted provider prompt prove the bridge cannot write,
  commit, route, acquire or claim a seat, issue a verdict, or authorize lock
  release.
- Resulting change: this route adds the complete binding and negative-test
  acceptance below. The advisory response is correlated evidence only; the
  user's direct instruction, not the consultation, supplies the authority to
  withdraw the standalone Claude controller.

## Evidence At Route Preflight

- `env -u GIT_INDEX_FILE .venv/bin/python .agents/skills/four-seat-protocol/scripts/seat_status.py coordinator --wave 2`
  produced Pipeline `HEAD 70ad83e`, `UNREAD: 0 / ref-bus`, and
  `Wave 2 gate: MET`. The gate result is process state only; correctness remains
  bound to the Operator FAIL named above.
- In the evidence-ledger worktree, `env -u GIT_INDEX_FILE git rev-parse HEAD`
  produced `8eaed44f803d871f09135c5d89395d38cf9e939e`, while
  `env -u GIT_INDEX_FILE git status --porcelain=v1 --untracked-files=all`
  produced no output. `git rev-parse --absolute-git-dir` and
  `git rev-parse --path-format=absolute --git-common-dir` produced the exact
  worktree Gitdir and common directory recorded above; `git remote get-url
  origin` produced `https://github.com/hkk009008-svg/evidence-ledger.git`.
- In the hardening worktree, `env -u GIT_INDEX_FILE git rev-parse HEAD`
  produced `5092b4d5e1ee7dd028caa60abf3a19aa78add48d`. A final hot-tree
  porcelain-status refresh reported live owner WIP only in the hardening plan
  and design spec. That uncommitted text is not authority and is not relied on;
  the coordinator does not touch it.
- `rg -n 'operator-seat verifier|GO / NITS / FAIL|authorizes its release'
  .claude/agents/lane-v-verifier.md` in that worktree found the authority
  language at lines 3, 10, 68, and 74-75. `rg -n
  'AGENT_RELATIVE_PATH|append-system-prompt' scripts/opus_review_bridge.py`
  found the trusted prompt selection and provider argument at lines 174 and
  2713. The Task 7 file list names `.codex/agents/lane-v-verifier.toml` but not
  this loaded `.claude` prompt.
- `env -u GIT_INDEX_FILE git merge-base --is-ancestor
  6941cb1eb5167da0b50d21cbf0e93ceff62cb1fa
  8eaed44f803d871f09135c5d89395d38cf9e939e` exited zero. Read-only inspection
  of the three reported race sites and their planned regressions found only
  synthetic filesystem/Git inputs; no workbook, database, DSN, or business
  artifact is needed for either Opus question.
- `scripts/protocol_capacity_board.py --wave 2 --validate-route <this-route>`
  produced `route valid: true`; `scripts/protocol_doctor.py --wave 2 --route
  <this-route>` produced `PROTOCOL DOCTOR: PASS`; `scripts/ci_smoke.py`
  produced `OK`; and `git diff --check` produced no output. All Python and Git
  invocations used `env -u GIT_INDEX_FILE`.

## Successor Workflow Boundary

1. Let `codex/opus-lanev-receipt-hardening` first correct its committed plan to
   include the actual loaded `.claude/agents/lane-v-verifier.md` prompt, a
   provider-specific advisory replacement, and a regression over the final
   rendered prompt. Then finish Tasks 6-7, final verification, and independent
   review without coordinator edits or a competing implementation. Acceptance
   must make every provider-facing instruction explicitly advisory and reject
   the inherited `operator-seat`, `GO / NITS / FAIL`, and lock-release authority
   language.
2. Reconcile that completed branch only from its committed evidence and formal
   verification.
   No merge, push, publication, or external action is authorized by this route;
   each remains separately user-gated.
3. Route a separate, Pipeline-owned target-aware Opus bridge extension for
   evidence-ledger. The completed hardened Pipeline bridge may challenge that
   extension's Pipeline plan and actual diff, but it may not be stretched to
   inspect evidence-ledger before the extension exists. The extension design
   must bind all of the following into each request, receipt, response, and
   reconciliation:
   - Pipeline route identity, Wave 2, and exact committed route/FAIL blob IDs;
   - target repository identity `hkk009008-svg/evidence-ledger`, resolved target
     root, exact linked-worktree Gitdir
     `/Users/hyungkoookkim/evidence-ledger/.git/worktrees/evidence-ledger-workbook-refresh-2026-07-11`,
     and Git common directory `/Users/hyungkoookkim/evidence-ledger/.git`;
   - correction base `8eaed44f803d871f09135c5d89395d38cf9e939e`,
     cumulative base `6941cb1eb5167da0b50d21cbf0e93ceff62cb1fa`, and
     the eventual immutable reviewed HEAD;
   - an explicit correction write allowlist limited initially to
     `recommendation/cli.py`, `recommendation/tests/test_cli.py`, and
     `ARCHITECTURE.md` only if the behavior change makes its claims stale;
   - challenge context limited to committed code, synthetic tests, and
     content-free command metadata; the three publication races require no
     mutable canonical database, workbook, resource, or business-data input,
     and those sources must remain excluded rather than snapshotted;
   - exact requirement paths, verification commands, Git blob identities, a
     canonical relevant-paths hash, and a mailbox snapshot hash over the named
     committed authority artifacts rather than the mutable mailbox directory;
   - versioned prompt/response/receipt schemas, receipt namespace, question
     kind, and monotonic challenge sequence (`design-time/1`,
     `actual-diff/2`); and
   - one provider attempt per question, no retry or fallback reviewer,
     sanitized bounded output, and Operator-owned finding reconciliation.
   Missing, stale, mismatched, uncommitted, or out-of-allowlist bindings must
   fail before provider launch.
4. The extension's negative tests must prove that both successful and malformed
   reviews cannot write the target or Pipeline worktrees, stage or commit Git,
   publish mailbox events, mutate routes/cursors/locks, acquire a seat, invoke
   arbitrary commands, emit a binding GO/NITS/FAIL verdict, or authorize lock
   release. Prompt-sync tests must prove that no provider-facing system or user
   prompt assigns a seat, controller identity, verdict role, or side-effect
   authority. Receipt presence proves an attempt, not runtime authority.
5. Only after that extension is implemented and independently verified may a
   fresh coordinator route authorize a Codex Director correction. Before the
   first product edit, the committed correction brief receives the target-aware
   Opus design-time check. After the additive correction commit, the Operator
   performs fresh cumulative Lane V and uses the target-aware Opus actual-diff
   check before issuing GO/NITS/FAIL.

The two Opus checks are different pre-stated questions; neither is a duplicate
same-question review. They do not grant commit, route, cursor, lock, push,
spend, or verdict authority.

## Capacity Split Default

The current fast path is a serialized hold because the receipt hardening owns
the shared bridge surfaces and the PPL races share one target publication
primitive. No second implementer may modify either worktree in parallel. Pair
B remains bounded to future planning or preflight after the hardening branch
closes; it does not implement the current bridge or the PPL correction.

## Capacity Packet Coverage

All 93 Wave-2 packet IDs are named for validator completeness. Only
`coord-ledger-ppl-recommendation-evaluation-join` appends this hold evidence;
every other packet remains unchanged.

- `coord-control-plane-authority-foundation-join`
- `coord-execution-strength-broader-join`
- `coord-governance-hardening-bridge-join`
- `coord-ledger-phase2-detail-integration-join`
- `coord-ledger-phase2-task21-join`
- `coord-ledger-phase2-task21-route`
- `coord-ledger-phase2-task22-join`
- `coord-ledger-phase2-task23-join`
- `coord-ledger-phase2-task24-join`
- `coord-ledger-phase2-task25-26-join`
- `coord-ledger-ppl-recommendation-evaluation-join`
- `coord-ledger-runway-stage0-join`
- `coord-ledger-runway-stage0-route`
- `coord-ledger-t14-align-join`
- `coord-ledger-t14-align-route`
- `coord-ledger-workbook-refresh-join`
- `coord-unit-coherence-side-effect-token-join`
- `director-control-plane-authority-foundation-task2-global-scan-fail-visible-fix`
- `director-control-plane-authority-foundation-task2-race-fix`
- `director-control-plane-authority-foundation-task2-replacement`
- `director-control-plane-authority-foundation-task2-spec-review-fix`
- `director-control-plane-authority-foundation-task2u-fail-closed-closure`
- `director-control-plane-authority-foundation-tasks1-2`
- `director-execution-strength-broader-impl`
- `director-governance-hardening-bridge-impl`
- `director-ledger-phase2-detail-integration`
- `director-ledger-phase2-task21-write-path`
- `director-ledger-phase2-task22-validations`
- `director-ledger-phase2-task23-result-history`
- `director-ledger-phase2-task24-ios-slot-entry`
- `director-ledger-phase2-task25a-result-entry`
- `director-ledger-ppl-recommendation-evaluation-implementation`
- `director-ledger-publication-decision`
- `director-ledger-runway-stage0-owner-gates`
- `director-ledger-workbook-refresh-implementation`
- `director-unit-coherence-side-effect-token-impl`
- `director2-control-plane-authority-foundation-identity-interface-closure-preflight`
- `director2-control-plane-authority-foundation-identity-preflight`
- `director2-control-plane-authority-foundation-identity-repreflight`
- `director2-control-plane-authority-foundation-identity-rerepreflight`
- `director2-control-plane-authority-foundation-task3d-snapshot-cas-closure-preflight`
- `director2-control-plane-authority-foundation-task3e-proof-capability-closure-preflight`
- `director2-control-plane-authority-foundation-task3f-runner-capture-closure-preflight`
- `director2-control-plane-authority-foundation-task3g-runtime-isolation-contract-closure-preflight`
- `director2-control-plane-authority-foundation-task3h-causal-runtime-proof-closure-preflight`
- `director2-control-plane-authority-foundation-task3i-execution-contract-closure-preflight`
- `director2-execution-strength-broader-observer`
- `director2-governance-hardening-bridge-observer`
- `director2-ledger-next-brief`
- `director2-ledger-phase2-bounds-plan-sync`
- `director2-ledger-phase2-detail-integration-preflight`
- `director2-ledger-phase2-task22-observer`
- `director2-ledger-phase2-task23-observer`
- `director2-ledger-phase2-task24-observer`
- `director2-ledger-phase2-task24-planning-preflight`
- `director2-ledger-phase2-task26a-history-component`
- `director2-ledger-ppl-recommendation-evaluation-preflight`
- `director2-ledger-runway-plan-reconcile`
- `director2-ledger-workbook-refresh-contract-correction-preflight`
- `director2-ledger-workbook-refresh-preflight`
- `director2-unit-coherence-observer-standby`
- `operator-control-plane-authority-foundation-lanev`
- `operator-control-plane-authority-foundation-replacement-lanev`
- `operator-control-plane-authority-foundation-task2u-cumulative-lanev`
- `operator-execution-strength-broader-verification`
- `operator-governance-hardening-bridge-lanev`
- `operator-ledger-phase2-detail-integration-lanev`
- `operator-ledger-phase2-task21-lanev`
- `operator-ledger-phase2-task22-lanev`
- `operator-ledger-phase2-task23-lanev`
- `operator-ledger-phase2-task24-lanev`
- `operator-ledger-phase2-task25a-lanev`
- `operator-ledger-ppl-recommendation-evaluation-lanev`
- `operator-ledger-runway-stage0-verify`
- `operator-ledger-workbook-refresh-lanev`
- `operator-pipeline-tooling-verify`
- `operator-unit-coherence-side-effect-token-verification`
- `operator2-control-plane-authority-foundation-activation-repreflight`
- `operator2-control-plane-authority-foundation-cutover-preflight`
- `operator2-execution-strength-broader-observer`
- `operator2-governance-hardening-bridge-observer`
- `operator2-ledger-main-verify`
- `operator2-ledger-phase2-base-preflight`
- `operator2-ledger-phase2-detail-integration-preflight`
- `operator2-ledger-phase2-task22-observer`
- `operator2-ledger-phase2-task23-observer`
- `operator2-ledger-phase2-task24-observer`
- `operator2-ledger-phase2-task24-preflight`
- `operator2-ledger-phase2-task26a-lanev`
- `operator2-ledger-ppl-recommendation-evaluation-preflight`
- `operator2-ledger-runway-worktree-verify`
- `operator2-ledger-workbook-refresh-preflight`
- `operator2-unit-coherence-observer-standby`

## Side-Effect Executor Token

- side_effect_id: `ledger-ppl-opus-bridge-hold-2026-07-13`
- executor: `coordinator`
- target: route mutation limited to `coordination/capacity/packets/2026-07-12-ledger-ppl-recommendation-evaluation-coordinator-join.json` and `coordination/mailbox/sent/2026-07-13T11-38-14Z-coordinator-to-all-coordination.md`
- allowed_command_class: route mutation through `apply_patch`, JSON parsing, exact-path local git staging including forced staging of the ignored mailbox route, cached-scope inspection, and one local coordinator git commit
- preflight: direct user clarification; guarded consultation `2a860e88-f5d6-4179-92de-16dd141a6682` correlated at request hash `b69c23de6a3444a8b84b1b097fb02e51fd54a5419c33f1c29dbb971985ad7afe` and supplies advice only; Pipeline HEAD `70ad83ee43f552bf4fa7071e0dd83a3819fe676d`; coordinator unread `0 / ref-bus`; active route and Operator FAIL read; target clean at `8eaed44f803d871f09135c5d89395d38cf9e939e`; Opus hardening committed checkpoint `5092b4d5e1ee7dd028caa60abf3a19aa78add48d` with uncommitted owner-only plan/spec WIP not relied on; Wave 2 gate MET; capacity valid and blocked; smoke OK; locks empty; token paths have no peer WIP
- stop_if_newer_mail_or_live_target_satisfied: stop before staging if Pipeline HEAD moves, newer coordinator mail changes the disposition, either token path gains peer WIP, the target HEAD or cleanliness changes, the Opus hardening branch moves from `5092b4d5e1ee7dd028caa60abf3a19aa78add48d`, the hardening WIP expands beyond its plan/spec files, or capacity/route validation fails
- postcheck: committed scope is exactly the coordinator join packet plus this event; JSON parses; capacity board, this route, protocol doctor, GO schema, smoke, and diff checks pass; target and hardening worktrees remain untouched; no Opus or Claude provider process was launched by this route
- observer_seats: `director`, `director2`, `operator`, `operator2`, `coordinator2`
- final_closeout_owner: `coordinator`
- non_goals: no standalone Claude Director launch, Opus provider call, evidence-ledger product edit, Codex target commit, bridge-worktree edit, target-aware bridge implementation, Operator verdict, cursor consume, lock action, remote-ref update, push, force update, paid-service spend, pod action, production generation, merge, publication, deployment, activation, cleanup, or scope widening

Join condition: keep the PPL coordinator join blocked until the receipt
hardening cycle is complete and independently verified, a separately routed
target-aware Opus design-time and actual-diff bridge is implemented and
verified with the immutable bindings and negative tests above, a fresh route
authorizes the bounded Codex Director correction, and
the live Operator returns GO for the new cumulative range with receipt-backed
cross-model evidence. Any NITS, FAIL, scope change, authority contradiction,
business-data access, or activation request returns to coordinator.

Regression-pin disposition: `test-infeasible under this coordinator hold` —
the prompt contradiction is inside an actively owned isolated hardening
worktree, the current Task 7 plan does not yet own the required actual-prompt
regression, and the coordinator may not add a competing branch edit or
production fix. The hardening owner's plan correction must add that regression
before implementation resumes.

## Exact Next Trigger

The hardening owner must first amend the committed plan after observed HEAD
`5092b4d` to bind the actual loaded provider prompt and its advisory-only
regression, then complete Tasks 6-7 and independent final verification. On
that durable completion event, return to coordinator to reconcile integration
authority and route the separate evidence-ledger-aware Opus bridge extension.
Do not start a Claude Director, make a Codex target correction, or call Opus.
Do not merge or run `git push` from this hold.
