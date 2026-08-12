# Coordinator -> All: record merged bridge and route a fresh existing-session Opus acceptance

**When:** 2026-07-14T12:32:12Z · **From:** coordinator (online)

Event type: coordination
Disposition: `PIPELINE_LEVEL5_OPUS_EXISTING_SESSION_ROUTE_ACTIVE`
Task-board: `pipeline-level5-opus-existing-session-2026-07-14`
Protocol wave: `2`
Route base before commit: `a2603359801a10bccda8a3e07a930af93650b7f4`
Coordinator mailbox at preflight: `0 unread / all-scope; no consume`

## User Authority And Decision

The user-principal directed the coordinator in this turn to record the merge,
supersede or park the old packets, and, if Opus transport remained required,
issue a new separately authorized route through the repaired existing-session
bridge. The user expressly prohibited retrying the denied attempt.

The transport criterion remains required. The old coordinator join requires
one real provider pass, while the binding Director2 artifact at
`coordination/mailbox/sent/2026-07-14T05-12-10Z-director2-to-coordinator-coordination.md`
proves that the outer runtime denied the command before process creation and
that no provider request, spend, receipt, retry, fallback, or workaround
occurred. No newer durable event waives that criterion.

This event therefore creates a distinct cycle, authorization identity, and
side-effect ID. It never resumes, replays, or reuses
`pipeline-level5-wave0-opus-attempt-2026-07-14`.

## Merge Record

- Current `main` is exact merge head
  `a2603359801a10bccda8a3e07a930af93650b7f4`.
- ChatGPT repair head `8f8af2febdee82fb42dec29cc56d4dee258b22f0`
  and Opus repair head `bdbefaf8a833503e9c5ba30f301e5c2ab6bb1444`
  are both ancestors of `main`.
- The merged Opus executable is pinned by blob identity:
  `scripts/opus_review_bridge.py` =
  `5e37f668a9e0c401ea8583cd0e07cebfffa9ba67` and
  `scripts/opus_review_receipts.py` =
  `a67da9672d5c94fc2916ad6c17d4d10841f7d122`.
- Fresh merged-head acceptance passed:
  `769 passed, 18 skipped`; `scripts/ci_smoke.py` ended `OK`.
- The immutable review worktree remains clean at
  `97c270f8f0e630fdaaded672e0da37ed32335de5`; the `claude` executable is
  present; none of the bridge-forbidden credential, endpoint, token, or proxy
  override names was present at coordinator preflight. These are readiness
  facts, not proof of a provider pass.
- The ChatGPT implementation is merged, but no live ChatGPT acceptance is
  claimed or cleared by this Opus-only route.

## Old Cycle Parked Without Reinterpretation

All five `pipeline-level5-wave0-2026-07-14` packets are now `excepted` for
scheduling:

- `coord-pipeline-level5-wave0-join`
- `director-pipeline-level5-wave0-p0-containment`
- `operator-pipeline-level5-wave0-p0-containment-lanev`
- `director2-pipeline-level5-wave0-opus-finalization`
- `operator2-pipeline-level5-wave0-opus-final-lanev`

This is not GO, correctness completion, or evidence erasure. The Pair-A
cursor-writer contradiction remains binding and its isolated worktree stays
parked clean at `807669d`. The old Director2 denial remains terminal. The old
Operator and Operator2 packets never received lawful verify-requests and issued
no verdicts. No old packet, token, command, receipt identity, or dependency may
be reconstructed or resumed.

## New Existing-Session Cycle

The new five-seat cycle is deliberately narrow:

- `coord-pipeline-level5-opus-existing-session-join` remains blocked until
  transport and independent verification both complete.
- `director-pipeline-level5-opus-existing-session-standby` and
  `operator-pipeline-level5-opus-existing-session-standby` are excepted; Pair A
  receives no implementation or verification authority.
- `director2-pipeline-level5-opus-existing-session-transport` is active and is
  the only provider executor packet.
- `operator2-pipeline-level5-opus-existing-session-lanev` remains blocked until
  one canonical receipt-backed verify-request lands.

Director2 uses the merged main bridge executable against immutable reviewed
head `97c270f8f0e630fdaaded672e0da37ed32335de5`, range
`555041477bcdb9a432a1b238d664be0958c5c9ef..97c270f8f0e630fdaaded672e0da37ed32335de5`,
and descriptor `2a876e95-3a87-4203-a613-1a29dd957b5b`. The required transport
profile is exactly `anthropic-claude-existing-session-v1`.

Before process creation the bridge must reject API credentials, auth-token
overrides, custom endpoints, and proxy overrides; forward only its explicit
environment allowlist; enter no credentials; and use no API, Chrome, manual
relay, alternate provider, or transport fallback. Any denial, ambiguity,
timeout, unavailability, uncertain state, or receipt conflict stops the lane
without retry and returns one bounded Director2 artifact to coordinator.

If and only if the new process yields a real bridge-issued receipt, Director2
reconciles it and sends one canonical verify-request. Operator2 then verifies
the immutable range, merged bridge blob/profile, receipt, process cardinality,
forbidden-environment boundary, no-retry separation, and every provider finding
before issuing GO, NITS, or FAIL. A receipt is attempt evidence, never verdict
authority.

## Capacity Split Default

This is the single-pair fast path for Pair B's authority-sensitive external
transport. Pair A is expressly excepted rather than given ceremonial work;
the routed Director2 action is bounded planning or preflight followed by at
most one existing-session provider process, and Operator2 owns the independent
verification. Coordinator owns convergence, packet reconciliation, conflict
handling, and final evidence.

## Capacity Packet Coverage

The complete protocol Wave-2 packet set is named below. Historical packets
retain their existing statuses and evidence unless explicitly parked above.

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
- `coord-pipeline-level5-opus-existing-session-join`
- `coord-pipeline-level5-wave0-join`
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
- `director-pipeline-level5-opus-existing-session-standby`
- `director-pipeline-level5-wave0-p0-containment`
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
- `director2-pipeline-level5-opus-existing-session-transport`
- `director2-pipeline-level5-wave0-opus-finalization`
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
- `operator-pipeline-level5-opus-existing-session-standby`
- `operator-pipeline-level5-wave0-p0-containment-lanev`
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
- `operator2-pipeline-level5-opus-existing-session-lanev`
- `operator2-pipeline-level5-wave0-opus-final-lanev`
- `operator2-unit-coherence-observer-standby`

## Side-Effect Executor Token

- side_effect_id: `pipeline-level5-opus-existing-session-reroute-2026-07-14`
- executor: `coordinator`
- target: route mutation limited to the five old Level-5 packet status/evidence fields, five new existing-session packet JSON files, and this single coordinator-to-all route event
- allowed_command_class: `apply_patch` coordinator metadata mutation, JSON and route validation, exact-path local staging including force-add of this ignored event, one local coordinator commit, and read-only postchecks
- preflight: user directly assigned coordinator and required this distinct route; HEAD is a2603359801a10bccda8a3e07a930af93650b7f4; coordinator unread is zero; all relevant mailbox bodies and packet files were read; both repair heads are ancestors; merged acceptance is 769 passed and 18 skipped; smoke is OK; the old receipt root is absent; locks are empty; the immutable review worktree is clean at 97c270f; target packet paths contain no peer WIP
- stop_if_newer_mail_or_live_target_satisfied: stop before commit if HEAD moves, relevant mail lands, another route already records this merge and distinct transport action, any target path gains peer WIP, the immutable worktree or bridge blobs drift, receipt state appears, locks change, or packet, capacity, route, doctor, smoke, or diff validation fails
- postcheck: committed scope is exactly ten packet JSON files and this route event; old packets are excepted with evidence preserved; new cycle is valid; capacity board, route validation, protocol doctor, smoke, JSON parse, and diff checks pass; provider process, receipt, cursor, lock, merge, and remote refs remain unchanged
- observer_seats: `director`, `director2`, `operator`, `operator2`, `coordinator2`
- final_closeout_owner: `coordinator`
- non_goals: no production fix, no provider invocation by coordinator, no retry or replay of the denied command, no credential entry, no API or transport fallback, no cursor consume, no lock/ref/key mutation, no worktree or branch change, no merge, no push, no publication, no cleanup, no pod action, and no production generation

## Side-Effect Executor Token

- side_effect_id: `pipeline-level5-opus-existing-session-attempt-2026-07-14`
- executor: `director2`
- target: exactly one existing-session Claude Opus provider process for descriptor 2a876e95-3a87-4203-a613-1a29dd957b5b and immutable reviewed head 97c270f8f0e630fdaaded672e0da37ed32335de5, launched only by merged bridge blob 5e37f668a9e0c401ea8583cd0e07cebfffa9ba67 with transport profile anthropic-claude-existing-session-v1 and authorization source user-task:pipeline-level5-opus-existing-session-2026-07-14
- allowed_command_class: one paid-service spend through `scripts/opus_review_bridge.py review` using the exact repo root, head, base, shipping commit, codex-lane-v profile, existing-session transport profile, and new authorization source named above; receipt status/reconciliation and read-only postchecks only
- preflight: the committed new route and Director2 packet are fresh; the old side-effect ID remains terminally excepted with no receipt; main retains the pinned bridge and receipt blobs; the target worktree is clean at exact 97c270f and descriptor/prompt authority match; the receipt store has no existing or uncertain record for the new authorization; all merged bridge tests, target deterministic gates, route, capacity, locks, mail, executable availability, and forbidden-environment-name checks pass; no newer verified report satisfies the task
- stop_if_newer_mail_or_live_target_satisfied: stop before provider entry if route, mailbox, capacity, lock, target, descriptor, prompt, bridge blob, transport profile, environment, executable, or receipt state drifts; stop permanently without retry after any outer-runtime denial, process entry, ambiguity, timeout, unavailability, uncertain state, or result
- postcheck: at most one process entry occurs under the new authorization; any resulting bridge receipt is content-free, correlated, and preserved; raw prompt/response bytes stay out of tracked, mailbox, log, argument, and screenshot surfaces; bridge and target heads remain unchanged; Director2 emits exactly one verify-request on a real receipt or one bounded blocker without retry
- observer_seats: `director`, `operator`, `operator2`, `coordinator`, `coordinator2`
- final_closeout_owner: `coordinator`
- non_goals: no reuse or retry of pipeline-level5-wave0-opus-attempt-2026-07-14, no second provider process, no fallback reviewer, no API substitution, no credential entry, no custom endpoint or proxy override, no raw-content persistence, no code/worktree edit, no verdict authority for Opus, no cursor/lock/route/ref mutation by Director2, no merge, no push, no publication, and no downstream PPL action

Join condition: one real provider pass and one Operator2 verification-report GO
under `pipeline-level5-opus-existing-session-2026-07-14`; the five old Level-5
packets remain excepted with denial and Pair-A contradiction evidence intact;
ChatGPT live acceptance remains a separate hold; fresh mailbox, capacity,
route, doctor, smoke, lock, receipt, bridge-blob, environment, and target-head
checks pass; and no denied command, token, receipt, or attempt is retried or
reused.

Cursor at send: all-scope-unpinned

## Exact Next Trigger

Run `continue as director2` from Pipeline. Director2 must read this route and
the terminal denial, refresh every named preflight, and execute at most one new
existing-session bridge process under
`pipeline-level5-opus-existing-session-attempt-2026-07-14`. Run
`continue as operator2` only after a canonical receipt-backed verify-request lands. Any
denial, ambiguity, unavailable result, uncertain receipt, drift, or missing
precondition returns one blocker to coordinator with zero retry.
