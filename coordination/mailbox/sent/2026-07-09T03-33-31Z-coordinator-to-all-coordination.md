# Coordinator -> All: Ledger Phase 2 Detail Integration Route

**When:** 2026-07-09T03:33:31Z - **From:** coordinator (online)

Event type: coordination
Task-board: `ledger-phase2-detail-integration-2026-07-09`
Prior closeout: `coordination/mailbox/sent/2026-07-09T03-24-52Z-coordinator-to-all-coordination.md`
Route base: `0ffcffacf36f566bc9f36074d444e6f0161b2281`
Route worktree: `/Users/hyungkoookkim/Pipeline/.worktrees/evidence-ledger-phase2-task23-2026-07-08`

## Outcome

This route opens the separate integration join reserved by the Task 2.5A /
2.6A closeout. The pre-integration entry and history components are already
verified; this cycle wires them into `BroadcastDetailView.swift` and flips the
owner-facing `docs/MANUAL.md` status only after that screen truth is present.

No user-gated side effects are granted by this route. Coordinator remains
limited to Pipeline routing, capacity state, and later closeout evidence; it
does not edit evidence-ledger product files.

## Capacity Split Default

- single-pair fast path remains the default for narrow or shared-file work.
- If no: keep one pair implementing while Pair B performs bounded planning or
  preflight instead of idle standby.
- coordinator owns convergence: capacity packets, one consolidated route, join
  condition, conflict handling, and final closeout evidence.

Capacity split decision: this integration route is not cleanly divisible into
two implementation chunks because the detail screen is the shared convergence
surface for both result entry and audit history. Director owns the single
implementation lane; Operator owns Lane V. Pair B performs bounded read-only
preflight only and reports contradiction, missing evidence, changed safety
boundary, or readiness. This is the bounded planning or preflight branch of the
capacity split default.

## Capacity Packet Coverage

Capacity packet coverage list:
- `coord-execution-strength-broader-join`
- `coord-governance-hardening-bridge-join`
- `coord-ledger-phase2-detail-integration-join`
- `coord-ledger-phase2-task21-join`
- `coord-ledger-phase2-task21-route`
- `coord-ledger-phase2-task22-join`
- `coord-ledger-phase2-task23-join`
- `coord-ledger-phase2-task24-join`
- `coord-ledger-phase2-task25-26-join`
- `coord-ledger-runway-stage0-join`
- `coord-ledger-runway-stage0-route`
- `coord-ledger-t14-align-join`
- `coord-ledger-t14-align-route`
- `coord-unit-coherence-side-effect-token-join`
- `director-execution-strength-broader-impl`
- `director-governance-hardening-bridge-impl`
- `director-ledger-phase2-detail-integration`
- `director-ledger-phase2-task21-write-path`
- `director-ledger-phase2-task22-validations`
- `director-ledger-phase2-task23-result-history`
- `director-ledger-phase2-task24-ios-slot-entry`
- `director-ledger-phase2-task25a-result-entry`
- `director-ledger-publication-decision`
- `director-ledger-runway-stage0-owner-gates`
- `director-unit-coherence-side-effect-token-impl`
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
- `director2-ledger-runway-plan-reconcile`
- `director2-unit-coherence-observer-standby`
- `operator-execution-strength-broader-verification`
- `operator-governance-hardening-bridge-lanev`
- `operator-ledger-phase2-detail-integration-lanev`
- `operator-ledger-phase2-task21-lanev`
- `operator-ledger-phase2-task22-lanev`
- `operator-ledger-phase2-task23-lanev`
- `operator-ledger-phase2-task24-lanev`
- `operator-ledger-phase2-task25a-lanev`
- `operator-ledger-runway-stage0-verify`
- `operator-pipeline-tooling-verify`
- `operator-unit-coherence-side-effect-token-verification`
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
- `operator2-ledger-runway-worktree-verify`
- `operator2-unit-coherence-observer-standby`

Coordinator join packet: `coord-ledger-phase2-detail-integration-join`.
Director implementation packet: `director-ledger-phase2-detail-integration`.
Operator verification packet: `operator-ledger-phase2-detail-integration-lanev`.
Director2 preflight packet:
`director2-ledger-phase2-detail-integration-preflight`.
Operator2 preflight packet:
`operator2-ledger-phase2-detail-integration-preflight`.

## Seat Assignments

Director owns `director-ledger-phase2-detail-integration`: start from Pipeline,
run `ledger_start_guard.py --seat director --wave 2`, read this route, use the
route worktree at `0ffcffa`, then implement only the detail-screen/manual
integration. The expected product write set is:

- `/Users/hyungkoookkim/Pipeline/.worktrees/evidence-ledger-phase2-task23-2026-07-08/ios/EvidenceLedger/Sources/Features/Broadcasts/BroadcastDetailView.swift`
- `/Users/hyungkoookkim/Pipeline/.worktrees/evidence-ledger-phase2-task23-2026-07-08/docs/MANUAL.md`

Director must wire `ResultEntryView` entry modes and `ResultHistorySection`
into the detail screen using the existing `EntryAPI.fetchLatestResultHead` and
`ResultHistoryAPI.fetch` surfaces, refresh latest-head/history state after a
save, keep existing P&L/provenance sections visible, and update the manual only
to the truth this screen now supports.

Operator owns `operator-ledger-phase2-detail-integration-lanev`: remain blocked
until Director sends one verify-request with commit/range and evidence, then
verify only that named diff and return GO/NITS/FAIL.

Director2 owns `director2-ledger-phase2-detail-integration-preflight`: perform
bounded read-only preflight on plan/manual/detail-screen scope. Report only a
contradiction, missing required evidence, changed safety boundary, or readiness
to coordinator.

Operator2 owns `operator2-ledger-phase2-detail-integration-preflight`: perform
bounded read-only preflight on route/base/worktree cleanliness, stale normal
checkout risk, expected selectors, and whether existing APIs support the detail
integration without extra write-surface edits. Do not verify Director's future
implementation before Operator receives the verify-request.

Subagent utilization decision: none. Coordinator handled this narrow protocol
artifact directly; live seats may use bounded helpers within their own
authority.

Join condition: coordinator closes this cycle only after Director lands the
detail integration, Operator sends GO/NITS/FAIL for the implementation range,
Director2 and Operator2 preflight state is accounted for, capacity board is
valid, route validation passes for this route, smoke is OK, and the closeout
cites implementation commit/range plus verifier verdict.

## Evidence

- `env -u GIT_INDEX_FILE .venv/bin/python scripts/ledger_start_guard.py --seat coordinator --wave 2`
  -> PASS; active route before this event was
  `coordination/mailbox/sent/2026-07-09T03-24-52Z-coordinator-to-all-coordination.md`.
- `env -u GIT_INDEX_FILE .venv/bin/python .agents/skills/four-seat-protocol/scripts/seat_status.py coordinator --wave 2`
  -> Pipeline HEAD `fee4714`; coordinator unread `0 / ref-bus`; Wave 2 gate
  `MET`.
- `env -u GIT_INDEX_FILE git status --short`
  -> no output before this route was written.
- `env -u GIT_INDEX_FILE .venv/bin/python scripts/protocol_capacity_board.py --wave 2`
  -> valid true; packet state closed; no blocking issues before this route was
  written.
- `env -u GIT_INDEX_FILE .venv/bin/python scripts/ci_smoke.py`
  -> `OK`; ceremony, placeholder, GO-schema, and arch-freshness checks pass.
- `env -u GIT_INDEX_FILE git -C /Users/hyungkoookkim/Pipeline/.worktrees/evidence-ledger-phase2-task23-2026-07-08 status --short --branch`
  -> `## codex/ledger-phase2-task23-pipeline-2026-07-08` with no dirty entries.
- `env -u GIT_INDEX_FILE git -C /Users/hyungkoookkim/Pipeline/.worktrees/evidence-ledger-phase2-task23-2026-07-08 log --oneline -8`
  -> top commit `0ffcffa fix(ios): encode result RPC params as snake case`.
- `env -u GIT_INDEX_FILE git -C /Users/hyungkoookkim/evidence-ledger status --short --branch`
  -> normal checkout `main...origin/main [behind 3]`; this route uses the
  routed worktree, not the stale normal checkout.
- `sed -n '492,560p' docs/superpowers/plans/2026-07-08-codex-runway-phase2-to-completion.md`
  -> Task 2.5 produces result entry/settle/correction from
  `BroadcastDetailView`; Task 2.6 requires audit history on
  `BroadcastDetailView` and a `docs/MANUAL.md` status flip.
- `sed -n '1,260p' ios/EvidenceLedger/Sources/Features/Broadcasts/BroadcastDetailView.swift`
  -> current detail screen has 편성, 결과, 손익, and provenance sections but no
  result-entry controls or `ResultHistorySection`.
- `sed -n '1,260p' ios/EvidenceLedger/Sources/Services/EntryAPI.swift`
  -> existing `fetchLatestResultHead(slotId:)` and `recordResult(_:)` surfaces
  are present.
- `sed -n '1,220p' ios/EvidenceLedger/Sources/Services/ResultHistoryAPI.swift`
  -> existing `ResultHistoryAPI.fetch(slotId:)` reads `biz.result_history`.
- `rg -n "데이터 입력 화면|질문\\(근거 있는 채팅\\)|추천 받기" docs/MANUAL.md`
  -> manual still marks 데이터 입력 화면, chat, and recommendation as
  `[예정]`; this route may update only the entry-screen truth.

## Exact Next Trigger

`continue as director` to implement `director-ledger-phase2-detail-integration`,
or `continue as director2` / `continue as operator2` for the bounded Pair B
preflight packets.

Cursor at send: 0
