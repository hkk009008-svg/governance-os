# Operator → All: FAIL commit `7503311` ledger phase2 task25a

**When:** 2026-07-09T02:56:43Z · **From:** operator (online)

VERDICT: FAIL
Task-board: `ledger-phase2-task25-26-preintegration-2026-07-09`
Coordinator route: `coordination/mailbox/sent/2026-07-08T22-07-13Z-coordinator-to-all-coordination.md`
Coordinator reconciliation: `coordination/mailbox/sent/2026-07-09T02-30-42Z-coordinator-to-all-coordination.md`
Director verify-request: `coordination/mailbox/sent/2026-07-09T02-45-50Z-director-to-operator-verify-request.md`
Director packet: `director-ledger-phase2-task25a-result-entry`
Operator packet: `operator-ledger-phase2-task25a-lanev`
Evidence-ledger range: `c1b5f3e..7503311`
Route worktree: `/Users/hyungkoookkim/Pipeline/.worktrees/evidence-ledger-phase2-task23-2026-07-08`

## Findings

1. IMPORTANT — `ios/EvidenceLedger/Sources/Services/EntryAPI.swift:52` — `ResultEntryPayload` has no `CodingKeys`, while `EntryAPI.recordResult(_:)` sends it through Supabase `.rpc("record_result", params: ["p": payload])` at `EntryAPI.swift:89`. Supabase PostgREST's default encoder in this checked-out package revision does not set `.convertToSnakeCase`, so the production-shaped RPC body encodes `slotId`, `grossAmount`, `netAmount`, and `supersedesId`. The DB RPC reads `slot_id`, `gross_amount`, `net_amount`, and `supersedes_id` from JSON at `supabase/migrations/20260708000100_entry_write_path.sql:83`. Result: the new result-entry app path can send missing/null fields to `biz.record_result`; the range is not verifiable as working. — fix required before GO.

2. IMPORTANT — `ios/EvidenceLedger/Tests/EntryAPITests.swift:24` — the new payload encoding test uses `JSONEncoder.postgrest` directly, but `EntryAPI.recordResult(_:)` does not use that encoder on the actual Supabase RPC path. The test is therefore not load-bearing for the write-path contract above. — add or adjust coverage so it proves the runtime RPC parameter encoding contract, preferably alongside explicit `ResultEntryPayload.CodingKeys` or an equivalent production-path fix.

3. INFORMATIONAL — `ios/EvidenceLedger/Sources/Features/Broadcasts/BroadcastDetailView.swift` / `docs/MANUAL.md` — independent review noted `ResultEntryView` and `fetchLatestResultHead` are not wired into `BroadcastDetailView`; the verify-request explicitly excludes `BroadcastDetailView.swift` and `MANUAL.md` and reserves that integration for coordinator-owned join. This is not a FAIL basis for Task 2.5A, but the later join route still owns the reachable-screen integration check. — record only for this verdict.

## Scope Review

- Range `c1b5f3e..7503311` changes exactly the six Task 2.5A files named by the Director: `db/tests/test_rpcs.py`, `EntryValidation.swift`, `ResultEntryView.swift`, `EntryAPI.swift`, `EntryAPITests.swift`, and `EntryValidationTests.swift`.
- No `BroadcastDetailView.swift`, `MANUAL.md`, real-data/config, normal evidence-ledger checkout refresh, publication, push, lock, cursor, paid API, pod, or production-generation side effect occurred in this operator pass.
- `ResultEntryView` is standalone pre-integration as requested. The blocking defect is inside the allowed write surface, not a forbidden integration-path drift.

## Evidence

$ env -u GIT_INDEX_FILE .venv/bin/python scripts/ledger_start_guard.py --seat operator --wave 2
→ PASS; active route `coordination/mailbox/sent/2026-07-09T02-30-42Z-coordinator-to-all-coordination.md`; route worktree `/Users/hyungkoookkim/Pipeline/.worktrees/evidence-ledger-phase2-task23-2026-07-08`.

$ env -u GIT_INDEX_FILE .venv/bin/python .agents/skills/four-seat-protocol/scripts/seat_status.py operator --wave 2
→ Pipeline HEAD `8ce41c3`; operator unread `0 / ref-bus`; Wave 2 gate `MET`.

$ env -u GIT_INDEX_FILE git -C /Users/hyungkoookkim/Pipeline/.worktrees/evidence-ledger-phase2-task23-2026-07-08 rev-parse HEAD
→ `750331108cbdd437370cd2044e89db9667307f8e`.

$ env -u GIT_INDEX_FILE git -C /Users/hyungkoookkim/Pipeline/.worktrees/evidence-ledger-phase2-task23-2026-07-08 diff --name-status c1b5f3e..7503311
→ exactly six files: `M db/tests/test_rpcs.py`; `M ios/EvidenceLedger/Sources/Features/Entry/EntryValidation.swift`; `A ios/EvidenceLedger/Sources/Features/Entry/ResultEntryView.swift`; `M ios/EvidenceLedger/Sources/Services/EntryAPI.swift`; `M ios/EvidenceLedger/Tests/EntryAPITests.swift`; `M ios/EvidenceLedger/Tests/EntryValidationTests.swift`.

$ env -u GIT_INDEX_FILE git -C /Users/hyungkoookkim/Pipeline/.worktrees/evidence-ledger-phase2-task23-2026-07-08 diff --check c1b5f3e..7503311
→ no output.

$ env -u GIT_INDEX_FILE /Users/hyungkoookkim/evidence-ledger/.venv/bin/python scripts/ci_smoke.py
→ evidence-ledger runtime invariants OK; ceremony check PASS; placeholder check PASS; arch-freshness check PASS; final `OK`.

$ env -u GIT_INDEX_FILE /Users/hyungkoookkim/evidence-ledger/.venv/bin/python -m py_compile db/tests/test_rpcs.py
→ exit 0.

$ env -u GIT_INDEX_FILE /Users/hyungkoookkim/evidence-ledger/.venv/bin/python -m pytest db/tests/test_rpcs.py::test_record_result_supersede_via_rpc_moves_head -q
→ sandbox run failed with local TCP `Operation not permitted`; rerun outside sandbox reached `127.0.0.1:54322` and failed `Connection refused`. `supabase status` outside sandbox also reported Docker daemon unavailable. Treat DB pytest as U2 environment-limited, not product GO evidence.

$ env -u GIT_INDEX_FILE xcodebuild build-for-testing -project EvidenceLedger.xcodeproj -scheme EvidenceLedger -destination 'platform=iOS Simulator,id=06A88A80-ED54-4522-BF2C-BD16EEB87DCA' -derivedDataPath /private/tmp/evidence-ledger-derived-operator-task25a-build2 -clonedSourcePackagesDirPath /private/tmp/evidence-ledger-sourcepackages-red
→ `** TEST BUILD SUCCEEDED **`.

$ env -u GIT_INDEX_FILE xcodebuild test-without-building -project EvidenceLedger.xcodeproj -scheme EvidenceLedger -destination 'platform=iOS Simulator,id=06A88A80-ED54-4522-BF2C-BD16EEB87DCA' -derivedDataPath /private/tmp/evidence-ledger-derived-operator-task25a-build2 -only-testing:EvidenceLedgerTests/EntryValidationTests/testCorrectionPayloadRequiresReason -only-testing:EvidenceLedgerTests/EntryAPITests/testResultPayloadEncodesSupersedeAndReason -only-testing:EvidenceLedgerTests/EntryAPITests/testLatestResultHeadDecodesCurrentRevision
→ `** TEST EXECUTE FAILED **`; app crashed before XCTest connection on missing gitignored `Config.plist` at `AppConfig.swift:9`. Treat as environment/config boundary, not product GO evidence.

$ rg -n "keyEncodingStrategy|convertToSnakeCase|JSONEncoder\.supabase|PostgrestClient\.Configuration\.jsonEncoder" /private/tmp/evidence-ledger-sourcepackages-red/checkouts/supabase-swift/Sources/PostgREST /private/tmp/evidence-ledger-sourcepackages-red/checkouts/supabase-swift/Sources/Helpers /private/tmp/evidence-ledger-sourcepackages-red/checkouts/supabase-swift/Sources/Supabase
→ PostgREST default encoder resolves to `JSONEncoder.supabase()`; grep found no `keyEncodingStrategy` or `convertToSnakeCase` in the PostgREST/Supabase helper encoder path used by RPC params.

$ nl -ba /private/tmp/evidence-ledger-sourcepackages-red/checkouts/supabase-swift/Sources/Helpers/Codable.swift | sed -n '32,49p'
→ `JSONEncoder.supabase()` sets date encoding and testing output formatting only; no snake_case key strategy.

$ nl -ba /private/tmp/evidence-ledger-sourcepackages-red/checkouts/supabase-swift/Sources/PostgREST/PostgrestClient.swift | sed -n '274,309p'
→ `.rpc(... params:)` encodes params via `configuration.encoder.encode(params)` and POSTs that body.

$ xcrun swift -module-cache-path /private/tmp/evidence-ledger-swift-module-cache-task25a -e 'import Foundation; struct ResultEntryPayload: Encodable { let slotId: Int64; let stage: String; let grossAmount: Double; let netAmount: Double; let supersedesId: Int64?; let reason: String? }; let payload = ResultEntryPayload(slotId: 42, stage: "settled", grossAmount: 900000, netAmount: 810000, supersedesId: 7, reason: "reason"); let data = try JSONEncoder().encode(["p": payload]); print(String(data: data, encoding: .utf8)!)'
→ `{"p":{"supersedesId":7,"stage":"settled","slotId":42,"reason":"reason","netAmount":810000,"grossAmount":900000}}`.

$ env -u GIT_INDEX_FILE git -C /Users/hyungkoookkim/Pipeline/.worktrees/evidence-ledger-phase2-task23-2026-07-08 grep -n "p->>'slot_id'\|p->>'gross_amount'\|p->>'net_amount'\|p->>'supersedes_id'" 7503311 -- supabase/migrations/20260708000100_entry_write_path.sql supabase/migrations/20260702000700_biz_rpcs.sql
→ SQL reads snake_case result payload keys at both current and earlier RPC definitions, including `20260708000100_entry_write_path.sql:83-85`.

$ lane-v-verifier Bernoulli read-only scope review
→ `issues`; scope matches the six expected files and forbidden integration paths are untouched; advisory issue that runtime `record_result` payload encoding may not match the DB RPC snake_case contract.

$ lane-v-verifier Heisenberg read-only code-quality review
→ `issues`; independently flagged the same production RPC payload encoding bug and non-load-bearing encoder test. Also noted missing `BroadcastDetailView` reachability, which this operator treats as later join-route scope because the Director verify-request explicitly excluded that integration.

## R-VERIFY-TIER Disposition

No xfail pin was authored in this operator pass. This is a blocking FAIL, not an accepted/deferred defect, and operator-authored target tests would contaminate the non-author verification boundary for `c1b5f3e..7503311`. The fix owner should add a production-path regression in the nit-fix/fix commit proving the RPC payload uses the snake_case keys consumed by `biz.record_result`.

## Boundaries

- Full DB pytest could not execute because local Supabase/Postgres/Docker was unavailable.
- Focused XCTest assertions could not execute because the app trapped on missing gitignored `Config.plist` before the test runner connected.
- The strongest executable proof obtained here is Pipeline smoke OK, evidence-ledger smoke OK, Python syntax OK, diff/whitespace checks clean, iOS `build-for-testing` success, source-level PostgREST encoder audit, and two independent read-only Lane V reviews.
- No lock release is relevant to this FAIL. No side effects were taken: no push, force-push, lock action, cursor consume, coordinator-mail consume, paid API spend, pod spend, publication, normal evidence-ledger checkout refresh, evidence-ledger main refresh, production generation, or product edit.

## Exact Next Trigger

Director fixes `operator-ledger-phase2-task25a-lanev` by landing a narrow follow-up on the route worktree, at minimum making `ResultEntryPayload` encode the snake_case keys consumed by `biz.record_result` and adding load-bearing regression coverage for the actual RPC parameter encoding path. Then Director sends a fresh verify-request naming the nit-fix/fix range for Operator re-read.

Cursor at send: 0
