# Director → Operator: Task 2.5A result entry correction flow

**When:** 2026-07-09T02:45:50Z · **From:** director (online)

VERDICT REQUESTED: GO/NITS/FAIL
Task-board: `ledger-phase2-task25-26-preintegration-2026-07-09`
Coordinator route: `coordination/mailbox/sent/2026-07-08T22-07-13Z-coordinator-to-all-coordination.md`
Coordinator reconciliation: `coordination/mailbox/sent/2026-07-09T02-30-42Z-coordinator-to-all-coordination.md`
Operator2 GO now landed: `coordination/mailbox/sent/2026-07-09T02-36-24Z-operator2-to-all-verification-report.md`
Director packet: `director-ledger-phase2-task25a-result-entry`
Operator packet: `operator-ledger-phase2-task25a-lanev`
Route worktree: `/Users/hyungkoookkim/Pipeline/.worktrees/evidence-ledger-phase2-task23-2026-07-08`
Evidence-ledger commit: `7503311 feat(ios+db): add result entry correction flow`
Evidence-ledger range for Operator: `c1b5f3e..7503311`

## Scope

Director implemented Task 2.5A result entry / settle / correction pre-integration
surface only. The range adds:

- `EntryAPI.recordResult(_:)` plus `ResultEntryPayload`, `ResultEntryHead`, and
  `fetchLatestResultHead(slotId:)` for the `biz.record_result` /
  `biz.latest_results` write/read path.
- `EntryValidation.correctionValid(reason:)` for the client-side correction
  reason mirror.
- Standalone `ResultEntryView` modes for root (`provisional`), settle
  (`settled`, supersedes current head, default reason `정산 확정`), and correction
  (supersedes current head, prefilled values, reason required).
- Regression coverage for payload encoding, head decoding, correction reason
  validation, and RPC supersede/head movement.

No `BroadcastDetailView.swift` or `MANUAL.md` integration is included; the
coordinator-owned join route still owns that later convergence.

## Diff Scope

`env -u GIT_INDEX_FILE git -C /Users/hyungkoookkim/Pipeline/.worktrees/evidence-ledger-phase2-task23-2026-07-08 diff --name-status c1b5f3e..7503311`
→ exactly six Task 2.5A files:

- `M db/tests/test_rpcs.py`
- `M ios/EvidenceLedger/Sources/Features/Entry/EntryValidation.swift`
- `A ios/EvidenceLedger/Sources/Features/Entry/ResultEntryView.swift`
- `M ios/EvidenceLedger/Sources/Services/EntryAPI.swift`
- `M ios/EvidenceLedger/Tests/EntryAPITests.swift`
- `M ios/EvidenceLedger/Tests/EntryValidationTests.swift`

## Evidence

`env -u GIT_INDEX_FILE .venv/bin/python .agents/skills/four-seat-protocol/scripts/seat_status.py director --wave 2`
→ director unread `0 / ref-bus`; Wave 2 gate `MET`; Pipeline HEAD `7a1e6b2` with Operator2 Chunk B GO already landed.

`env -u GIT_INDEX_FILE git -C /Users/hyungkoookkim/Pipeline/.worktrees/evidence-ledger-phase2-task23-2026-07-08 status --short --branch`
→ `## codex/ledger-phase2-task23-pipeline-2026-07-08` with no dirty entries after commit.

RED: focused iOS test before implementation:
`env -u GIT_INDEX_FILE xcodebuild test -project EvidenceLedger.xcodeproj -scheme EvidenceLedger -destination 'platform=iOS Simulator,id=06A88A80-ED54-4522-BF2C-BD16EEB87DCA' -derivedDataPath /private/tmp/evidence-ledger-derived-red -clonedSourcePackagesDirPath /private/tmp/evidence-ledger-sourcepackages-red -only-testing:EvidenceLedgerTests/EntryValidationTests/testCorrectionPayloadRequiresReason -only-testing:EvidenceLedgerTests/EntryAPITests/testResultPayloadEncodesSupersedeAndReason -only-testing:EvidenceLedgerTests/EntryAPITests/testLatestResultHeadDecodesCurrentRevision`
→ failed for expected missing symbols: `EntryValidation.correctionValid`, `ResultEntryPayload`, `ResultEntryHead`, and `JSONEncoder.postgrest`.

GREEN compile:
`env -u GIT_INDEX_FILE xcodebuild build-for-testing -project EvidenceLedger.xcodeproj -scheme EvidenceLedger -destination 'platform=iOS Simulator,id=06A88A80-ED54-4522-BF2C-BD16EEB87DCA' -derivedDataPath /private/tmp/evidence-ledger-derived-build2 -clonedSourcePackagesDirPath /private/tmp/evidence-ledger-sourcepackages-red`
→ `** TEST BUILD SUCCEEDED **`.

Target smoke:
`env -u GIT_INDEX_FILE /Users/hyungkoookkim/evidence-ledger/.venv/bin/python scripts/ci_smoke.py`
→ evidence-ledger runtime invariants OK; ceremony check PASS; placeholder check PASS; arch-freshness check PASS; final `OK`.

Python syntax check:
`env -u GIT_INDEX_FILE /Users/hyungkoookkim/evidence-ledger/.venv/bin/python -m py_compile db/tests/test_rpcs.py`
→ exit 0.

Whitespace check:
`env -u GIT_INDEX_FILE git diff --check`
→ no output.

## Unable To Fully Execute Locally

- Focused DB pytest:
  `env -u GIT_INDEX_FILE /Users/hyungkoookkim/evidence-ledger/.venv/bin/python -m pytest db/tests/test_rpcs.py::test_record_result_supersede_via_rpc_moves_head -q`
  → setup failed because local Postgres at `127.0.0.1:54322` refused connection.
- Supabase status:
  `supabase status`
  → `Cannot connect to the Docker daemon at unix:///Users/hyungkoookkim/.docker/run/docker.sock. Is the docker daemon running?`
- Focused XCTest execution after compile:
  two concrete simulators (`iPhone 17`, `iPhone 17 Pro`, iOS 26.5) both failed
  before assertions with `Application failed preflight checks` / `Busy`.

These are environment boundaries, not claimed product GO evidence. Operator
should rerun DB pytest if Docker/Supabase is available and may use
`build-for-testing` plus read-only source review if the simulator launch state
remains blocked, matching the Operator2 Task 2.6A boundary.

## Boundaries

No publication, force-push, lock action, cursor consumption, coordinator-mail
consumption, paid API spend, pod spend, production generation, normal
evidence-ledger checkout refresh, evidence-ledger main refresh, real-data/config
edit, `BroadcastDetailView.swift` integration, or `MANUAL.md` update was taken.

Subagent utilization decision: direct/no-op. The implementation was a small,
tightly coupled, authority-sensitive slice inside the routed Entry write set.

## Expected Operator Work

Verify only evidence-ledger range `c1b5f3e..7503311` for
`operator-ledger-phase2-task25a-lanev`. Return GO/NITS/FAIL and cite any
environment-limited checks separately from executable proof.

## Exact Next Trigger

`continue as operator` to verify `operator-ledger-phase2-task25a-lanev` for
range `c1b5f3e..7503311`.

Cursor at send: 0
