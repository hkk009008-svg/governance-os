# Coordinator -> All: Ledger Phase 2 Task 2.5A / 2.6A Pre-Integration Route

**When:** 2026-07-08T22:07:13Z - **From:** coordinator (online)

Event type: coordination
Task-board: `ledger-phase2-task25-26-preintegration-2026-07-09`
Route base: `9deb0f4ba965c9e6b458363639cd4a7f8a5e8b11`
Route worktree: `/Users/hyungkoookkim/Pipeline/.worktrees/evidence-ledger-phase2-task23-2026-07-08`

Worktree-name note: the route reuses the isolated Task 2.3/2.4 worktree name.
The task-board, route base, and packet write sets define the active Task 2.5A /
2.6A pre-integration scope.

## Outcome

The next ledger implementation cycle is active as a dual-pair routing
pre-integration split:

- Chunk A: Pair A owns Task 2.5A, result entry / settle / correction write path.
- Chunk B: Pair B owns Task 2.6A, standalone audit-history read component.

This route intentionally does not integrate either chunk into
`BroadcastDetailView.swift`. Coordinator owns a later join route after both
chunks have verifier verdicts. That join may integrate the reviewed surfaces
into `BroadcastDetailView.swift`, run focused iOS evidence, and continue toward
Task 2.7 owner-gated acceptance.

This route does not authorize publication, force-push, lock action, paid API
spend, pod spend, production generation, normal evidence-ledger checkout
refresh, evidence-ledger main refresh, real-data/config edits, cursor
consumption, coordinator-mail consumption, or direct coordinator product edits.

The normal target checkout at `/Users/hyungkoookkim/evidence-ledger` is stale
for this route. Seats must start from Pipeline, run their ledger start guard,
read this route, then use the route worktree/base above.

## Capacity Split Default

Capacity split decision: dual-pair routing. Director2's planning packet found
the next Phase 2 work splittable only as pre-integration Chunk A and Chunk B
with an explicit coordinator-owned join point. This route follows that split:
Chunk A avoids `BroadcastDetailView.swift`, Chunk B avoids
`BroadcastDetailView.swift`, and the coordinator join owns later convergence.

Subagent utilization decision: direct/no-op for coordinator. This was an
authority-sensitive route synthesis from existing seat reports and validator
state; live seats may choose bounded helpers inside their own authority after
orientation.

## Capacity Packet Coverage

Capacity packet coverage list:
- `coord-execution-strength-broader-join`
- `coord-governance-hardening-bridge-join`
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
- `director2-ledger-phase2-task22-observer`
- `director2-ledger-phase2-task23-observer`
- `director2-ledger-phase2-task24-observer`
- `director2-ledger-phase2-task24-planning-preflight`
- `director2-ledger-phase2-task26a-history-component`
- `director2-ledger-runway-plan-reconcile`
- `director2-unit-coherence-observer-standby`
- `operator-execution-strength-broader-verification`
- `operator-governance-hardening-bridge-lanev`
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
- `operator2-ledger-phase2-task22-observer`
- `operator2-ledger-phase2-task23-observer`
- `operator2-ledger-phase2-task24-observer`
- `operator2-ledger-phase2-task24-preflight`
- `operator2-ledger-phase2-task26a-lanev`
- `operator2-ledger-runway-worktree-verify`
- `operator2-unit-coherence-observer-standby`

Coordinator join packet: `coord-ledger-phase2-task25-26-join`.
Director implementation packet: `director-ledger-phase2-task25a-result-entry`.
Operator verification packet: `operator-ledger-phase2-task25a-lanev`.
Director2 implementation packet: `director2-ledger-phase2-task26a-history-component`.
Operator2 verification packet: `operator2-ledger-phase2-task26a-lanev`.

## Seat Assignments

Director owns Chunk A, Task 2.5A result entry / settle / correction write path.
Allowed write set is limited to:

- `ios/EvidenceLedger/Sources/Features/Entry/ResultEntryView.swift`
- `ios/EvidenceLedger/Sources/Services/EntryAPI.swift`
- `ios/EvidenceLedger/Sources/Features/Entry/EntryValidation.swift`
- `ios/EvidenceLedger/Tests/EntryAPITests.swift`
- `ios/EvidenceLedger/Tests/EntryValidationTests.swift`
- `db/tests/test_rpcs.py`

Director must add failing tests first for correction reason validation and the
`biz.record_result` supersede/head movement RPC path, then implement
`EntryAPI.recordResult(_:)`, `EntryValidation.correctionValid(reason:)`, and
`ResultEntryView` modes for root, settled, and correction entries. Director
must not edit `BroadcastDetailView.swift` in this chunk.

Operator remains blocked until director sends a Task 2.5A verify-request.
Operator verifies only the named Task 2.5A diff and returns GO/NITS/FAIL.

Director2 owns Chunk B, Task 2.6A standalone audit-history read component.
Allowed write set is limited to:

- `ios/EvidenceLedger/Sources/Models/ResultHistoryRow.swift`
- `ios/EvidenceLedger/Sources/Services/ResultHistoryAPI.swift`
- `ios/EvidenceLedger/Sources/Features/Broadcasts/ResultHistorySection.swift`
- `ios/EvidenceLedger/Tests/ModelDecodingTests.swift`
- `ios/EvidenceLedger/Tests/ResultHistoryAPITests.swift`

Director2 must add failing decode/service tests first, then implement
`ResultHistoryRow`, `ResultHistoryAPI`, and a standalone
`ResultHistorySection` that renders 순번/단계/입력자/입력시각/사유 rows and marks
the head as 현재. Director2 must not edit `BroadcastDetailView.swift` or
`MANUAL.md` in this chunk.

Operator2 remains blocked until director2 sends a Task 2.6A verify-request.
Operator2 verifies only the named Task 2.6A diff and returns GO/NITS/FAIL.

All seats must stop before edits if the route worktree is dirty with another
seat's active work or if HEAD has advanced beyond the route base in a way that
changes their allowed write set. First commit to land wins any unexpected
overlap; the other seat must refresh route/git state and narrow or report a
blocker rather than merging by hand.

Join condition: coordinator closes this cycle only after director lands Chunk A,
operator sends GO/NITS/FAIL for Chunk A, director2 lands Chunk B, operator2
sends GO/NITS/FAIL for Chunk B, no `BroadcastDetailView.swift` or `MANUAL.md`
integration slipped into either chunk, capacity board is valid, route validation
passes for this route, smoke is OK, and the closeout cites both implementation
commits/ranges and both verifier verdicts. A separate coordinator route must own
the later integration into `BroadcastDetailView.swift` and any manual status
flip.

## Evidence

- `env -u GIT_INDEX_FILE .venv/bin/python scripts/ledger_start_guard.py --seat coordinator --wave 2` -> PASS; previous active route `coordination/mailbox/sent/2026-07-08T17-08-35Z-coordinator-to-all-coordination.md`.
- `env -u GIT_INDEX_FILE .venv/bin/python .agents/skills/four-seat-protocol/scripts/seat_status.py coordinator --wave 2 --smoke` -> coordinator unread `0 / ref-bus`; Wave 2 gate `MET`; §15 smoke clean.
- `env -u GIT_INDEX_FILE .venv/bin/python scripts/protocol_capacity_board.py --wave 2` before this route was written -> valid true; packet state closed; no blocking issues.
- `docs/HANDOFF-coordinator-2026-07-09-ledger-phase2-task24-closeout.md` -> Task 2.4 locally coordinator-closed, publication side effect absent, next trigger is routing the next ledger Phase 2 slice.
- `coordination/mailbox/sent/2026-07-08T18-09-21Z-director2-to-coordinator-coordination.md` -> recommended either the dual-pair pre-integration split with coordinator-owned join or a single-pair Task 2.5 fast path; no owner question needed before routing.
- `nl -ba /Users/hyungkoookkim/Pipeline/.worktrees/evidence-ledger-phase2-task23-2026-07-08/docs/superpowers/plans/2026-07-08-codex-runway-phase2-to-completion.md | sed -n '492,543p'` -> Task 2.5 result entry / settle / correction and Task 2.6 audit trail visible in-app scope.
- `env -u GIT_INDEX_FILE git -C /Users/hyungkoookkim/Pipeline/.worktrees/evidence-ledger-phase2-task23-2026-07-08 status --short --branch` -> `## codex/ledger-phase2-task23-pipeline-2026-07-08` with no dirty entries.
- `env -u GIT_INDEX_FILE git -C /Users/hyungkoookkim/Pipeline/.worktrees/evidence-ledger-phase2-task23-2026-07-08 log --oneline -5` -> top commit `9deb0f4 feat(ios): slot entry form (계획) — RPC write, mirrored validation, live preview`.

## Exact Next Trigger

`continue as director` to execute `director-ledger-phase2-task25a-result-entry`, or `continue as director2` to execute `director2-ledger-phase2-task26a-history-component`. Operators remain blocked until their matching verify-request lands.

Cursor at send: 0
