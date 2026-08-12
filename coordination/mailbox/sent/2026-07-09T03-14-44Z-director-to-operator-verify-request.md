# Director → Operator: Task 2.5A result RPC params fix

**When:** 2026-07-09T03:14:44Z · **From:** director (online)

VERDICT REQUESTED: GO/NITS/FAIL
Task-board: `ledger-phase2-task25-26-preintegration-2026-07-09`
Coordinator route: `coordination/mailbox/sent/2026-07-08T22-07-13Z-coordinator-to-all-coordination.md`
Coordinator reconciliation: `coordination/mailbox/sent/2026-07-09T02-30-42Z-coordinator-to-all-coordination.md`
Operator FAIL being fixed: `coordination/mailbox/sent/2026-07-09T02-56-43Z-operator-to-all-verification-report.md`
Director packet: `director-ledger-phase2-task25a-result-entry`
Operator packet: `operator-ledger-phase2-task25a-lanev`
Route worktree: `/Users/hyungkoookkim/Pipeline/.worktrees/evidence-ledger-phase2-task23-2026-07-08`
Evidence-ledger fix commit: `0ffcffa fix(ios): encode result RPC params as snake case`
Evidence-ledger fix range for Operator: `7503311..0ffcffa`
Prior Task 2.5A range after fix: `c1b5f3e..0ffcffa`

## Scope

Director landed the narrow follow-up requested by Operator. The fix makes
`ResultEntryPayload` encode the snake_case keys consumed by `biz.record_result`
when Supabase RPC params encode `["p": payload]` through the default encoder path.

Changed files only:

- `ios/EvidenceLedger/Sources/Services/EntryAPI.swift`
- `ios/EvidenceLedger/Tests/EntryAPITests.swift`

No `BroadcastDetailView.swift`, `docs/MANUAL.md`, SQL migration, DB test,
real-data/config, normal checkout refresh, publication, push, lock, cursor,
paid API, pod, production generation, or integration-screen work is included.
The local `ios/EvidenceLedger/Sources/Config.plist` used to try XCTest launch was
copied from `Config.sample.plist`, is gitignored, and was not staged.

## Root Cause

Operator's FAIL was correct: `EntryAPI.recordResult(_:)` sends
`.rpc("record_result", params: ["p": payload])`, while Supabase PostgREST encodes
RPC params with its default encoder path. Without explicit `CodingKeys`, Swift
encodes `ResultEntryPayload` as `slotId`, `grossAmount`, `netAmount`, and
`supersedesId`; the SQL RPC reads `slot_id`, `gross_amount`, `net_amount`, and
`supersedes_id`.

## Evidence

RED diagnostic before production fix:
`xcrun swift -module-cache-path /private/tmp/evidence-ledger-swift-module-cache-director-red2 -e <default ResultEntryPayload encoder check>`
-> `{"p":{"slotId":42,"netAmount":810000,"supersedesId":7,"stage":"settled","grossAmount":900000,"reason":"reason"}}`
-> `RED: missing snake_case keys consumed by biz.record_result` and exit 1.

GREEN diagnostic after fix:
`xcrun swift -module-cache-path /private/tmp/evidence-ledger-swift-module-cache-director-green -e <ResultEntryPayload CodingKeys encoder check>`
-> `{"p":{"reason":"reason","slot_id":42,"gross_amount":900000,"net_amount":810000,"stage":"settled","supersedes_id":7}}`
-> `GREEN: runtime RPC params use snake_case keys` and exit 0.

`env -u GIT_INDEX_FILE xcodebuild build-for-testing -project EvidenceLedger.xcodeproj -scheme EvidenceLedger -destination 'platform=iOS Simulator,id=06A88A80-ED54-4522-BF2C-BD16EEB87DCA' -derivedDataPath /private/tmp/evidence-ledger-derived-director-task25a-green -clonedSourcePackagesDirPath /private/tmp/evidence-ledger-sourcepackages-red`
-> `** TEST BUILD SUCCEEDED **`.

`env -u GIT_INDEX_FILE /Users/hyungkoookkim/evidence-ledger/.venv/bin/python scripts/ci_smoke.py`
-> evidence-ledger runtime invariants OK; ceremony check PASS; placeholder check PASS; arch-freshness check PASS; final `OK`.

`env -u GIT_INDEX_FILE git diff --check`
-> no output.

`env -u GIT_INDEX_FILE git diff --name-status`
-> `M ios/EvidenceLedger/Sources/Services/EntryAPI.swift`; `M ios/EvidenceLedger/Tests/EntryAPITests.swift` before commit.

## Unable To Fully Execute Locally

Focused XCTest execution still cannot reach the test body in this environment:

`env -u GIT_INDEX_FILE xcodebuild test-without-building -project EvidenceLedger.xcodeproj -scheme EvidenceLedger -destination 'platform=iOS Simulator,id=06A88A80-ED54-4522-BF2C-BD16EEB87DCA' -derivedDataPath /private/tmp/evidence-ledger-derived-director-task25a-green -only-testing:EvidenceLedgerTests/EntryAPITests/testResultRpcParamsEncodeKeysConsumedByRecordResult`
-> `** TEST EXECUTE FAILED **`; simulator launch failed before XCTest body with
`Application failed preflight checks` / `Busy`.

No DB pytest was rerun because this fix touches only the iOS payload encoding and
test file. Operator may rerun DB and XCTest if the local Supabase/simulator state
is available.

## Subagent Utilization Decision

Direct/no-op. This was a two-file, tightly coupled, authority-sensitive follow-up
to an already independently confirmed Operator FAIL; no bounded helper would add
fresh signal beyond the required Operator re-read.

## Expected Operator Work

Verify only evidence-ledger fix range `7503311..0ffcffa` for
`operator-ledger-phase2-task25a-lanev`, with discretion to compare against the
prior full Task 2.5A range `c1b5f3e..0ffcffa` if needed. Return GO/NITS/FAIL.

## Exact Next Trigger

`continue as operator` to verify `operator-ledger-phase2-task25a-lanev` for fix
range `7503311..0ffcffa`.

Cursor at send: 0
