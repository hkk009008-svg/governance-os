# Operator → All: GO commit `0ffcffa` ledger phase2 task25a fix

**When:** 2026-07-09T03:22:34Z · **From:** operator (online)

VERDICT: GO
Task-board: `ledger-phase2-task25-26-preintegration-2026-07-09`
Coordinator route: `coordination/mailbox/sent/2026-07-08T22-07-13Z-coordinator-to-all-coordination.md`
Coordinator reconciliation: `coordination/mailbox/sent/2026-07-09T02-30-42Z-coordinator-to-all-coordination.md`
Director verify-request: `coordination/mailbox/sent/2026-07-09T03-14-44Z-director-to-operator-verify-request.md`
Prior Operator FAIL: `coordination/mailbox/sent/2026-07-09T02-56-43Z-operator-to-all-verification-report.md`
Director packet: `director-ledger-phase2-task25a-result-entry`
Operator packet: `operator-ledger-phase2-task25a-lanev`
Evidence-ledger fix commit: `0ffcffacf36f566bc9f36074d444e6f0161b2281`
Evidence-ledger fix range: `7503311..0ffcffa`
Route worktree: `/Users/hyungkoookkim/Pipeline/.worktrees/evidence-ledger-phase2-task23-2026-07-08`

## Findings

1. INFORMATIONAL — `ios/EvidenceLedger/Sources/Services/EntryAPI.swift:60` — `ResultEntryPayload` now has explicit snake_case `CodingKeys`, while `EntryAPI.recordResult(_:)` still sends `.rpc("record_result", params: ["p": payload])` at `EntryAPI.swift:101`. This fixes the prior blocking mismatch between Swift default encoding and the SQL RPC's snake_case JSON reads. — verified fixed.

2. INFORMATIONAL — `ios/EvidenceLedger/Tests/EntryAPITests.swift:35` — the added regression encodes `["p": payload]` with `JSONEncoder()`, matching the Supabase RPC default encoder path for nested params rather than the app-only `JSONEncoder.postgrest` helper. It asserts required snake_case keys are present and camelCase keys are absent at `EntryAPITests.swift:49-58`. — load-bearing for the prior FAIL.

3. INFORMATIONAL — focused XCTest execution did not reach the test body because CoreSimulator refused app launch with `Busy ("Application failed preflight checks")`. This is an execution-environment boundary, not a product assertion failure; the project test build succeeded and the non-vacuous Swift encoding probe directly proves the runtime contract. — record only.

## Scope Review

- Fix range `7503311..0ffcffa` changes only `ios/EvidenceLedger/Sources/Services/EntryAPI.swift` and `ios/EvidenceLedger/Tests/EntryAPITests.swift`.
- Forbidden path check for `BroadcastDetailView.swift`, `docs/MANUAL.md`, SQL migrations, DB tests, and `ios/EvidenceLedger/Sources/Config.plist` showed no diff.
- No real-data/config, normal evidence-ledger checkout refresh, publication, push, lock, cursor, paid API, pod, production generation, or integration-screen work occurred in this operator pass.
- No lock release is relevant to this lane.

## Evidence

$ env -u GIT_INDEX_FILE .venv/bin/python scripts/ledger_start_guard.py --seat operator --wave 2
→ PASS; active route `coordination/mailbox/sent/2026-07-09T02-30-42Z-coordinator-to-all-coordination.md`; route worktree `/Users/hyungkoookkim/Pipeline/.worktrees/evidence-ledger-phase2-task23-2026-07-08`.

$ env -u GIT_INDEX_FILE .venv/bin/python .agents/skills/four-seat-protocol/scripts/seat_status.py operator --wave 2
→ Pipeline HEAD `6305b19`; operator unread `0 / ref-bus`; Wave 2 gate `MET`.

$ env -u GIT_INDEX_FILE .venv/bin/python scripts/ci_smoke.py
→ PROJECT SMOKE OK; ceremony check PASS; placeholder check PASS; GO-SCHEMA CHECK PASS; ARCH-FRESHNESS CHECK PASS; final `OK`.

$ env -u GIT_INDEX_FILE git -C /Users/hyungkoookkim/Pipeline/.worktrees/evidence-ledger-phase2-task23-2026-07-08 rev-parse HEAD
→ `0ffcffacf36f566bc9f36074d444e6f0161b2281`.

$ env -u GIT_INDEX_FILE git -C /Users/hyungkoookkim/Pipeline/.worktrees/evidence-ledger-phase2-task23-2026-07-08 diff --name-status 7503311..0ffcffa
→ `M ios/EvidenceLedger/Sources/Services/EntryAPI.swift`; `M ios/EvidenceLedger/Tests/EntryAPITests.swift`.

$ env -u GIT_INDEX_FILE git -C /Users/hyungkoookkim/Pipeline/.worktrees/evidence-ledger-phase2-task23-2026-07-08 diff --check 7503311..0ffcffa
→ no output.

$ env -u GIT_INDEX_FILE git -C /Users/hyungkoookkim/Pipeline/.worktrees/evidence-ledger-phase2-task23-2026-07-08 diff --exit-code 7503311..0ffcffa -- ios/EvidenceLedger/Sources/Features/Broadcasts/BroadcastDetailView.swift docs/MANUAL.md supabase/migrations db/tests ios/EvidenceLedger/Sources/Config.plist
→ no output.

$ env -u GIT_INDEX_FILE git -C /Users/hyungkoookkim/Pipeline/.worktrees/evidence-ledger-phase2-task23-2026-07-08 grep -n "p->>'slot_id'\|p->>'gross_amount'\|p->>'net_amount'\|p->>'supersedes_id'" 0ffcffa -- supabase/migrations/20260708000100_entry_write_path.sql supabase/migrations/20260702000700_biz_rpcs.sql
→ SQL reads the snake_case result payload keys at `20260708000100_entry_write_path.sql:83-85` and `20260702000700_biz_rpcs.sql:87-89`.

$ rg -n "configuration\.encoder\.encode\(params\)|func rpc|JSONEncoder\.supabase|keyEncodingStrategy|convertToSnakeCase" /private/tmp/evidence-ledger-sourcepackages-red/checkouts/supabase-swift/Sources/PostgREST /private/tmp/evidence-ledger-sourcepackages-red/checkouts/supabase-swift/Sources/Helpers /private/tmp/evidence-ledger-sourcepackages-red/checkouts/supabase-swift/Sources/Supabase
→ `.rpc(... params:)` encodes params via `configuration.encoder.encode(params)` at `PostgrestClient.swift:283`; default PostgREST encoder is `JSONEncoder.supabase()` at `Defaults.swift:27`; no `keyEncodingStrategy` / `convertToSnakeCase` hit in the default encoder path.

$ xcrun swift -module-cache-path /private/tmp/evidence-ledger-swift-module-cache-operator-fix-check -e '<ResultEntryPayload with current CodingKeys; encode ["p": payload] using JSONEncoder()>'
→ `{"p":{"net_amount":810000,"stage":"settled","supersedes_id":7,"slot_id":42,"reason":"reason","gross_amount":900000}}`; `GREEN: runtime RPC params use snake_case keys`.

$ env -u GIT_INDEX_FILE /Users/hyungkoookkim/evidence-ledger/.venv/bin/python scripts/ci_smoke.py
→ evidence-ledger runtime invariants OK; ceremony check PASS; placeholder check PASS; arch-freshness check PASS; final `OK`.

$ env -u GIT_INDEX_FILE xcodebuild build-for-testing -project EvidenceLedger.xcodeproj -scheme EvidenceLedger -destination 'platform=iOS Simulator,id=06A88A80-ED54-4522-BF2C-BD16EEB87DCA' -derivedDataPath /private/tmp/evidence-ledger-derived-operator-task25a-fix -clonedSourcePackagesDirPath /private/tmp/evidence-ledger-sourcepackages-red
→ `** TEST BUILD SUCCEEDED **`.

$ env -u GIT_INDEX_FILE xcodebuild test-without-building -project EvidenceLedger.xcodeproj -scheme EvidenceLedger -destination 'platform=iOS Simulator,id=06A88A80-ED54-4522-BF2C-BD16EEB87DCA' -derivedDataPath /private/tmp/evidence-ledger-derived-operator-task25a-fix -only-testing:EvidenceLedgerTests/EntryAPITests/testResultRpcParamsEncodeKeysConsumedByRecordResult
→ `** TEST EXECUTE FAILED **`; CoreSimulator failed before XCTest body with `Busy ("Application failed preflight checks")`.

$ lane-v-verifier Kierkegaard read-only spec review
→ `pass`; no blocking findings; confirmed `EntryAPI.swift:60` fixes the snake_case payload contract and `EntryAPITests.swift:35` is load-bearing for `["p": payload]` default-encoder params.

$ lane-v-verifier Arendt read-only code-quality/scope review
→ `unable_to_verify` for unsandboxed Xcode execution under subagent authority; source-level review found no scope/code-quality issues, no forbidden path changes, and no missed sibling encoding cases.

## Boundaries

- Focused XCTest execution remains environment-limited by simulator launch preflight; it did not fail inside the test assertion.
- DB RPC pytest was not rerun because this fix touches only the iOS payload encoding and test file, and the verify-request excluded SQL/DB-test scope.
- This GO covers the Task 2.5A fix range `7503311..0ffcffa`; it does not verify the later coordinator-owned integration-screen/reachability join scope.

## Exact Next Trigger

Coordinator may reconcile `operator-ledger-phase2-task25a-lanev` as GO for fix commit `0ffcffa`, then perform the join closeout/reroute only after current capacity-board and route checks remain valid and both Task 2.5A and Task 2.6A verifier verdicts are accounted for.

Cursor at send: 0
