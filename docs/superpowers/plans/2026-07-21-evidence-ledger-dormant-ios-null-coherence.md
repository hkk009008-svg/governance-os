# Evidence-Ledger Dormant iOS NULL Coherence Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make the retained iOS reference client decode a nullable `commission_model`, render the Korean fallback `미정`, and remove iOS from active-product and recurring-verification claims.

**Architecture:** Keep the existing `SlotPnl` DTO and SwiftUI surfaces. Add one optional field plus one computed display property, use that property at both call sites, run one focused XCTest pass, then make the repository truthfully describe the entire iOS tree as dormant. Do not delete, regenerate, broaden, or revive the client.

**Tech Stack:** Swift, XCTest, SwiftUI, Xcode/xcodebuild, Markdown, Bash, existing Python governance scripts.

## Global Constraints

- Bind the route to target parent `1ad4eb2b5550af7c3941aacf08240559a9051193` unless the Coordinator publishes a superseding parent.
- Work in a dedicated evidence-ledger worktree and preserve the main checkout's untracked `.vscode/` byte-for-byte.
- Use only inline synthetic JSON. Do not inspect or import a private workbook or live business values.
- Do not change Supabase, web, Python import behavior, dependencies, generated project structure, or iOS features beyond the nullable field and its two display call sites.
- Do not delete any file under `ios/`.
- Do not start or stop services, deploy, merge, push, consume a cursor, or access a managed database.
- One focused xcodebuild run is required for this packet. After it passes, iOS is not a recurring beta or release gate.

---

## Task 1: Pin the NULL decoding and Korean display contract

**Files:**

- Modify: `ios/EvidenceLedger/Tests/ModelDecodingTests.swift`

- [ ] Add this focused regression test after `testSlotPnlDecodesPlannedRowWithNulls`:

```swift
func testSlotPnlDecodesNullCommissionModelAsUnknown() throws {
    let json = """
    {"slot_id": 4, "broadcast_date": "2026-10-01", "start_time": null,
     "channel_code": "GS", "channel_name_ko": "GS홈쇼핑", "product_name_ko": "합성상품",
     "commission_model": null, "sale_price": null, "commission_rate": null,
     "target_amount": null, "target_qty": null, "stage": null,
     "gross_amount": null, "net_amount": null, "ppl_allocated": null,
     "achievement_rate": null, "conversion_rate": null,
     "commission_revenue": null, "operating_profit": null, "bep_ratio": null}
    """.data(using: .utf8)!

    let row = try JSONDecoder.postgrest.decode(SlotPnl.self, from: json)

    XCTAssertNil(row.commissionModel)
    XCTAssertEqual(row.commissionModelDisplay, "미정")
}
```

- [ ] Run the test before changing production Swift:

```bash
env -u GIT_INDEX_FILE xcodebuild \
  -project ios/EvidenceLedger/EvidenceLedger.xcodeproj \
  -scheme EvidenceLedger \
  -destination 'platform=iOS Simulator,name=iPhone 17 Pro' \
  -only-testing:EvidenceLedgerTests/ModelDecodingTests/testSlotPnlDecodesNullCommissionModelAsUnknown \
  test
```

Expected: non-zero exit. Decoding fails because `commissionModel` is non-optional, and the compiler also reports that `commissionModelDisplay` does not exist.

## Task 2: Implement the smallest nullable model and rendering fix

**Files:**

- Modify: `ios/EvidenceLedger/Sources/Models/SlotPnl.swift`
- Modify: `ios/EvidenceLedger/Sources/Features/Broadcasts/BroadcastListView.swift`
- Modify: `ios/EvidenceLedger/Sources/Features/Broadcasts/BroadcastDetailView.swift`

- [ ] Change only the model field and add one centralized display property:

```swift
let commissionModel: String?

var commissionModelDisplay: String { commissionModel ?? "미정" }
```

Place `commissionModelDisplay` beside `id`, `monthKey`, and `formattedProfit`. Do not add a custom decoder; Swift's synthesized decoder already handles a JSON `null` for an optional property.

- [ ] Replace the list badge's `row.commissionModel` with `row.commissionModelDisplay`.

- [ ] Replace the detail view's `row.commissionModel` with `row.commissionModelDisplay`.

- [ ] Preserve the existing known-value assertions by adding this assertion to `testSlotPnlDecodesFromPostgrestJSON`:

```swift
XCTAssertEqual(row.commissionModelDisplay, "반특")
```

- [ ] Re-run all model tests:

```bash
env -u GIT_INDEX_FILE xcodebuild \
  -project ios/EvidenceLedger/EvidenceLedger.xcodeproj \
  -scheme EvidenceLedger \
  -destination 'platform=iOS Simulator,name=iPhone 17 Pro' \
  -only-testing:EvidenceLedgerTests/ModelDecodingTests \
  test
```

Expected: `Executed 8 tests, with 0 failures` and `** TEST SUCCEEDED **`.

- [ ] Commit the bounded Swift correction:

```bash
env -u GIT_INDEX_FILE git add \
  ios/EvidenceLedger/Sources/Models/SlotPnl.swift \
  ios/EvidenceLedger/Sources/Features/Broadcasts/BroadcastListView.swift \
  ios/EvidenceLedger/Sources/Features/Broadcasts/BroadcastDetailView.swift \
  ios/EvidenceLedger/Tests/ModelDecodingTests.swift
env -u GIT_INDEX_FILE git commit -m "fix(ios): decode unknown commission model"
```

Expected: one commit containing exactly the four listed paths.

## Task 3: Remove iOS from active and recurring verification claims

**Files:**

- Modify: `README.md`
- Modify: `ARCHITECTURE.md`
- Modify: `OPERATIONS.md`
- Modify: `scripts/ci_local.sh`
- Modify: `.github/workflows/ci.yml` (comments only in this packet)

- [ ] In `README.md`, replace active-client wording with this product boundary:

```markdown
The retained read-only iOS client is dormant reference code. It is not the
active product, a beta surface, or a recurring release target; current product
work is the Windows PWA.
```

Remove iOS setup and `ios tests` from the default quickstart. Keep a link to the dormant source; do not imply deletion or active support.

- [ ] In `scripts/ci_local.sh`, leave only `scripts/db_test.sh` and `scripts/import_test.sh`. Remove the conditional xcodebuild block so a normal local verification does not revive the dormant lane.

- [ ] In `.github/workflows/ci.yml`, update only the scope comments: iOS is omitted because it is dormant, not because a paid runner is pending. Delete the commented future macOS job stub if it promises later activation; do not add or remove a CI job.

- [ ] In `ARCHITECTURE.md`, preserve the factual source inventory but label §1 and the iOS subsection as dormant/reference-only. State all four points explicitly:

  1. the source remains in the repository;
  2. the packet's one focused NULL test is recorded evidence;
  3. iOS is not the active product or beta surface; and
  4. iOS is excluded from recurring local and CI release verification.

Change both `*Last verified:*` lines to `2026-07-21 @ 1ad4eb2` (or the exact superseding packet parent named by the route). Update nearby test-count and `ci_local.sh` claims from seven to eight and from recurring to one-time recorded evidence.

- [ ] In `OPERATIONS.md`, move iOS installation/testing under a clearly labeled dormant-reference subsection. Remove it from prerequisites, numbered default installation, full local verification, CI lane promises, and troubleshooting that implies recurring support. Preserve the one direct xcodebuild command as the manual revival/reference check and record its expected `8/8` result only after Task 2 produced that output.

- [ ] Repair and verify documentation anchors:

```bash
env -u GIT_INDEX_FILE /Users/hyungkoookkim/evidence-ledger/.venv/bin/python \
  scripts/check_doc_claims.py --fix
env -u GIT_INDEX_FILE /Users/hyungkoookkim/evidence-ledger/.venv/bin/python \
  scripts/check_doc_claims.py OPERATIONS.md
env -u GIT_INDEX_FILE /Users/hyungkoookkim/evidence-ledger/.venv/bin/python \
  scripts/check_arch_freshness.py --base 1ad4eb2b5550af7c3941aacf08240559a9051193
```

Expected: both doc-claim commands exit 0; architecture freshness reports no violation.

- [ ] Commit the dormant-boundary correction:

```bash
env -u GIT_INDEX_FILE git add \
  README.md ARCHITECTURE.md OPERATIONS.md scripts/ci_local.sh .github/workflows/ci.yml
env -u GIT_INDEX_FILE git commit -m "docs: mark retained iOS client dormant"
```

Expected: one documentation/harness commit containing exactly the five listed paths.

## Task 4: Verify the packet and prepare immutable review evidence

**Files:**

- Verify only; no new product files.

- [ ] Run the focused iOS suite once more against the final packet tree:

```bash
env -u GIT_INDEX_FILE xcodebuild \
  -project ios/EvidenceLedger/EvidenceLedger.xcodeproj \
  -scheme EvidenceLedger \
  -destination 'platform=iOS Simulator,name=iPhone 17 Pro' \
  -only-testing:EvidenceLedgerTests/ModelDecodingTests \
  test
```

Expected: 8 tests, 0 failures, `** TEST SUCCEEDED **`.

- [ ] Run the governance checks that the documentation changes activate:

```bash
env -u GIT_INDEX_FILE /Users/hyungkoookkim/evidence-ledger/.venv/bin/python scripts/ci_smoke.py
env -u GIT_INDEX_FILE git diff --check 1ad4eb2b5550af7c3941aacf08240559a9051193..HEAD
env -u GIT_INDEX_FILE git diff --name-only 1ad4eb2b5550af7c3941aacf08240559a9051193..HEAD
env -u GIT_INDEX_FILE git status --short --branch
```

Expected: smoke ends in `OK`; diff check is silent; changed paths are exactly the nine paths named in Tasks 1-3; the worktree is clean.

- [ ] Publish a verify-request bound to the exact two-commit range, assigning non-author Operator2. Include the NULL fixture result, known-value preservation, both view call sites, dormant status, and the absence of deletion as separate finding references.

- [ ] Stop. Do not merge or push. A non-author Operator2 GO makes the range eligible for separately authorized local integration; it does not itself authorize integration or publication.
