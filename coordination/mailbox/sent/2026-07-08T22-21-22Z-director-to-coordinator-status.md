# Director → Coordinator: Task 2.5A blocked by route worktree dirty with Chunk B WIP

**When:** 2026-07-08T22:21:22Z · **From:** director (online)

Packet: `director-ledger-phase2-task25a-result-entry`
Route: `coordination/mailbox/sent/2026-07-08T22-07-13Z-coordinator-to-all-coordination.md`

Director started from Pipeline, ran the ledger start guard and director seat status, read the active route, and prepared to execute Chunk A test-first. The route stop condition then triggered before any Chunk A edits: the shared route worktree is dirty with files outside director's allowed write set, matching Director2/Chunk B surfaces.

Evidence:

- `env -u GIT_INDEX_FILE .venv/bin/python scripts/ledger_start_guard.py --seat director --wave 2` -> PASS; active route `coordination/mailbox/sent/2026-07-08T22-07-13Z-coordinator-to-all-coordination.md`; route base `9deb0f4ba965c9e6b458363639cd4a7f8a5e8b11`; route worktree `/Users/hyungkoookkim/Pipeline/.worktrees/evidence-ledger-phase2-task23-2026-07-08`.
- `env -u GIT_INDEX_FILE .venv/bin/python .agents/skills/four-seat-protocol/scripts/seat_status.py director --wave 2` -> director unread `0 / ref-bus`; Wave 2 gate `MET`; Pipeline HEAD `2c0278c`; peers online.
- `env -u GIT_INDEX_FILE git -C /Users/hyungkoookkim/Pipeline/.worktrees/evidence-ledger-phase2-task23-2026-07-08 status --short --branch` -> `## codex/ledger-phase2-task23-pipeline-2026-07-08`; dirty entries: `M ios/EvidenceLedger/Tests/ModelDecodingTests.swift`; `?? ios/EvidenceLedger/Sources/Features/Broadcasts/ResultHistorySection.swift`; `?? ios/EvidenceLedger/Sources/Models/ResultHistoryRow.swift`; `?? ios/EvidenceLedger/Sources/Services/ResultHistoryAPI.swift`; `?? ios/EvidenceLedger/Tests/ResultHistoryAPITests.swift`.
- `env -u GIT_INDEX_FILE git -C /Users/hyungkoookkim/Pipeline/.worktrees/evidence-ledger-phase2-task23-2026-07-08 diff --name-status` -> `M ios/EvidenceLedger/Tests/ModelDecodingTests.swift`.
- Pipeline smoke: `env -u GIT_INDEX_FILE .venv/bin/python scripts/ci_smoke.py` -> OK.
- Evidence-ledger smoke attempt: `env -u GIT_INDEX_FILE .venv/bin/python scripts/ci_smoke.py` in the route worktree -> failed before running because `.venv/bin/python` is absent.

Subagent utilization decision:

Director dispatched one bounded worker for Task 2.5A, then interrupted it after the out-of-scope dirty worktree appeared. Worker reported no Chunk A edits and no commit. Director did not write tests, production code, verify-request, cursor update, lock, push, spend, or publication side effect.

Disposition:

Director is blocked on the route stop condition until the coordinator or owning seat resolves/commits/clears the Chunk B WIP in the shared route worktree, or issues a revised route allowing director to proceed despite the disjoint dirty state.

Exact Next Trigger:

`continue as coordinator` to reconcile the Task 2.5A/2.6A shared-worktree stop condition, or `continue as director2` to finish/commit/stand down the Chunk B WIP. After the shared route worktree is clean or the route is revised, `continue as director` can resume Task 2.5A.

Cursor at send: 0
