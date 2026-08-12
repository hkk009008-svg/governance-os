# Director2 -> Coordinator: Ledger Phase 2 Task 2.4 next-slice planning preflight

**When:** 2026-07-08T18:09:21Z · **From:** director2 (online)

Event type: coordination
Task-board: `ledger-phase2-task24-2026-07-08`
Packet: `director2-ledger-phase2-task24-planning-preflight`
Active route: `coordination/mailbox/sent/2026-07-08T17-08-35Z-coordinator-to-all-coordination.md`
Route worktree: `/Users/hyungkoookkim/Pipeline/.worktrees/evidence-ledger-phase2-task23-2026-07-08`
Route base: `bdc7f6b8aef74eddeb35993f18d7bef48fd2a58f`

## Director2 Boundary

Director2 executed the bounded planning/preflight packet only. No
evidence-ledger product-code edit, evidence-ledger docs edit, Pipeline protocol
source edit, cursor consume, coordinator-mail consume, push, force-push, merge,
lock action, paid API spend, pod spend, production generation, normal
evidence-ledger checkout refresh, or evidence-ledger `main` refresh occurred in
this director2 turn.

Subagent utilization decision: direct/no-op. This was a narrow route-state and
plan-splitting read, with director2 retaining the authority-sensitive synthesis.

## Current Task 2.4 State

Task 2.4 implementation and Lane V are already durable, but route closeout is
not clean because operator2 reported preflight blockers while this director2
packet was being drafted:

- Director verify-request:
  `coordination/mailbox/sent/2026-07-08T17-12-21Z-director-to-operator-verify-request.md`.
- Operator GO:
  `coordination/mailbox/sent/2026-07-08T17-19-32Z-operator-to-all-verification-report.md`.
- Operator2 route/preflight FAIL:
  `coordination/mailbox/sent/2026-07-08T18-08-38Z-operator2-to-all-verification-report.md`.
- Implementation range:
  `bdc7f6b8aef74eddeb35993f18d7bef48fd2a58f..9deb0f4`.
- Implementation commit:
  `9deb0f4 feat(ios): slot entry form (계획) — RPC write, mirrored validation, live preview`.

Director2 did not duplicate Task 2.4 implementation or operator Lane V.

## Split Decision For The Next Phase 2 Slice

Verdict: splittable only as disjoint pre-integration chunks with an explicit
coordinator-owned join point; not safe as two fully integrated parallel feature
edits because both Task 2.5 and Task 2.6 naturally converge on
`ios/EvidenceLedger/Sources/Features/Broadcasts/BroadcastDetailView.swift`.

Recommended next coordinator route:

1. Pair A owns Task 2.5A, result entry / settle / correction write path.
   Allowed write set should be limited to new result-entry UI/service/test
   surfaces plus the existing entry service/validation tests:
   `ios/EvidenceLedger/Sources/Features/Entry/ResultEntryView.swift`,
   `ios/EvidenceLedger/Sources/Services/EntryAPI.swift`,
   `ios/EvidenceLedger/Sources/Features/Entry/EntryValidation.swift`,
   `ios/EvidenceLedger/Tests/EntryAPITests.swift`,
   `ios/EvidenceLedger/Tests/EntryValidationTests.swift`, and
   `db/tests/test_rpcs.py`. Avoid `BroadcastDetailView.swift` in this chunk.
2. Pair B owns Task 2.6A, audit-history read component.
   Allowed write set should be limited to a result-history model/service,
   standalone history section/view, and focused decoding/service tests, for
   example `ios/EvidenceLedger/Sources/Models/ResultHistoryRow.swift`,
   `ios/EvidenceLedger/Sources/Services/ResultHistoryAPI.swift`,
   `ios/EvidenceLedger/Sources/Features/Broadcasts/ResultHistorySection.swift`,
   and matching tests. Avoid `BroadcastDetailView.swift` in this chunk.
3. Coordinator owns convergence after both chunks have GO/NITS/FAIL. The join
   route should integrate both already-reviewed surfaces into
   `BroadcastDetailView.swift`, then run the focused iOS build/test evidence and
   continue to Task 2.7 acceptance.

If the coordinator wants the next slice to be one fully user-visible feature
without a later join route, keep it single-pair: Task 2.5 result entry / settle /
correction first, while Pair B remains in bounded planning/preflight for Task
2.6.

## Smallest Next Brief

Smallest implementation brief if using the single-pair fast path:

`Task 2.5: iOS result entry, settle, and correction flows`

Scope:

- Add `EntryAPI.recordResult(_:)` through `biz.record_result`.
- Add `EntryValidation.correctionValid(reason:)`.
- Add `ResultEntryView` with three modes: root result, settled result, and
  correction/supersede of current head.
- Add the db-side RPC supersede/head movement pin from the Phase 2 plan.
- Integrate entry actions from `BroadcastDetailView` only if this is routed as
  the sole active implementation chunk.

Known brief hazard to include, but not mark as a confirmed defect in this
packet: Task 2.4 introduced `미정` / NULL commission-model entry semantics, while
`SlotPnl.commissionModel` currently decodes as non-optional. The next
implementation brief should either pin and fix that decode boundary or state why
the routed flow cannot surface a NULL `commission_model` through `slot_pnl`.

No owner-question packet is needed before Task 2.5/2.6 routing. Task 2.7 remains
the next owner gate for full Phase 2 acceptance.

## Live Blocker Observed Before Commit

Operator2's newer FAIL means coordinator should not close
`ledger-phase2-task24-2026-07-08` from the operator GO plus this planning packet
alone. The operator2 report names two closeout blockers:

1. Capacity board / route validation fails G1 because superseded director2 and
   operator2 observer packets are still counted as current/done alongside the
   new planning/preflight packets.
2. The operator2 preflight packet names `.superpowers/sdd/progress.md` and
   `coordination/locks/`, but the routed worktree lacks those paths, so the
   packet's presence/lock preflight contract cannot be cleanly satisfied as
   written.

Director2's next-slice split decision above remains valid as planning guidance,
but coordinator must reconcile the route/packet blockers before closeout or a
new implementation route.

## Evidence Commands

- `env -u GIT_INDEX_FILE .venv/bin/python scripts/ledger_start_guard.py --seat director2 --wave 2`
  -> PASS; active route
  `coordination/mailbox/sent/2026-07-08T17-08-35Z-coordinator-to-all-coordination.md`.
- `env -u GIT_INDEX_FILE .venv/bin/python .agents/skills/four-seat-protocol/scripts/seat_status.py director2 --wave 2`
  -> HEAD `919924a`; director2 unread `0 / ref-bus`; Wave 2 `MET`.
- `env -u GIT_INDEX_FILE git log --oneline -5`
  -> `919924a operator(verify): GO ledger phase2 task24`; `633230e feat(protocol): enforce capacity split routing`; `75c161d feat(protocol): default divisible work to dual pairs`; `d589a29 coord(coordinator): route ledger phase2 task24`; `aa5f9b2 coord(coordinator): close governance bridge cycle`.
- `env -u GIT_INDEX_FILE git status --short`
  -> existing unrelated dirty files observed and preserved:
  `.github/pull_request_template.md`, `AGENTS.md`, `CLAUDE.md`,
  `TRANSFER-MANIFEST.md`, `docs/protocol/codex/continuation.md`,
  `scripts/protocol_capacity.py`, `tests/unit/test_protocol_capacity.py`, and
  untracked `tests/unit/test_protocol_doc_integrity.py`.
- `env -u GIT_INDEX_FILE git -C /Users/hyungkoookkim/Pipeline/.worktrees/evidence-ledger-phase2-task23-2026-07-08 status --short --branch`
  -> `## codex/ledger-phase2-task23-pipeline-2026-07-08` with no dirty entries.
- `env -u GIT_INDEX_FILE git -C /Users/hyungkoookkim/Pipeline/.worktrees/evidence-ledger-phase2-task23-2026-07-08 log --oneline -8`
  -> `9deb0f4 feat(ios): slot entry form (계획) — RPC write, mirrored validation, live preview`; `bdc7f6b feat(db): add result_history audit view`; `36f5506 docs: sync task22 architecture verification facts`; `6692131 fix(db): keep import target validation warn-only`; `07e4077 feat(db): complete Phase-2 go-forward validations`; `e446218 docs: fix Task 2.1 truth stamps`; `35dc478 feat(db): ADR-007 Phase-2 client write path`; `d3e87e6 Merge pull request #11 from hkk009008-svg/codex/ledger-stage0-reconcile-2026-07-08`.
- `nl -ba /Users/hyungkoookkim/Pipeline/.worktrees/evidence-ledger-phase2-task23-2026-07-08/docs/superpowers/plans/2026-07-08-codex-runway-phase2-to-completion.md | sed -n '492,720p'`
  -> Task 2.5 is result entry / settle / correction, Task 2.6 is audit trail
  visible in app, Task 2.7 is the owner-gated Phase 2 acceptance run.
- `sed -n '1,140p' coordination/mailbox/sent/2026-07-08T17-19-32Z-operator-to-all-verification-report.md`
  -> operator verdict `GO` for Task 2.4 range `bdc7f6b..9deb0f4`.
- `sed -n '1,180p' coordination/mailbox/sent/2026-07-08T18-08-38Z-operator2-to-all-verification-report.md`
  -> operator2 verdict `FAIL` for `operator2-ledger-phase2-task24-preflight`
  because capacity board/route validation fails G1 on duplicate current/done
  Pair B packets, and the packet names absent routed-worktree paths.

## Exact Next Trigger

Coordinator can treat `director2-ledger-phase2-task24-planning-preflight` as
reported, but must first reconcile the operator2 FAIL on capacity packet state
and missing preflight paths. After a coordinator route or packet-state
correction, operator2 can rerun preflight; the next implementation route should
then choose either the dual-pair pre-integration split above or the single-pair
Task 2.5 fast path above.

Cursor at send: 0
