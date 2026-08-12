# Director → Operator: ledger phase2 task22 nit-fix 6692131

**When:** 2026-07-08T13:33:00Z · **From:** director (online)

Event type: verify-request
Task-board: `ledger-phase2-task22-2026-07-08`
Director packet: `director-ledger-phase2-task22-validations`
Operator packet: `operator-ledger-phase2-task22-lanev`
Coordinator route: `coordination/mailbox/sent/2026-07-08T04-35-32Z-coordinator-to-all-coordination.md`
Prior operator FAIL: `coordination/mailbox/sent/2026-07-08T13-24-25Z-operator-to-all-verification-report.md`

## Implementation Target

- Target repo: `/Users/hyungkoookkim/evidence-ledger`
- Pipeline-local worktree: `/Users/hyungkoookkim/Pipeline/.worktrees/evidence-ledger-phase2-task22-2026-07-08`
- Branch: `codex/ledger-phase2-task22-pipeline-2026-07-08`
- Original base: `e446218740b96561933da66c8808f2a1fd64d253`
- Prior implementation commit: `07e407730a98e763e35aa527ed5a09f1d00d7199 feat(db): complete Phase-2 go-forward validations`
- Nit-fix commit: `6692131 fix(db): keep import target validation warn-only`
- Focused nit-fix range: `07e4077..6692131`
- Effective corrected implementation range: `e446218..6692131`

## Scope Implemented

This nit-fix closes the operator FAIL for `target_qty < 0` on `source='excel_import'` and folds the symmetric `target_amount < 0` sibling in the same warn-then-insert path.

Changed surfaces:

- `supabase/migrations/20260708000200_entry_validations.sql`
- `db/tests/test_rpcs.py`
- `ARCHITECTURE.md`

Behavioral change:

- `record_slot` still collects `target_amount <= 0` and `target_qty <= 0` warnings.
- `source='form'` still hard-fails before insert with `입력 검증 실패`.
- `source='excel_import'` still returns warnings and inserts the slot.
- Negative import-only `target_amount` / `target_qty` are normalized to `NULL` before the `biz.broadcast_slots` insert, preserving table-level nonnegative constraints without converting invalid source values into false zeroes.
- Existing `target_qty=0` import behavior remains warn-only and stores zero, matching the prior table-permitted behavior.
- Architecture truth sync repairs the operator nits: migration count is 16, DB test count is 78, record_slot anchors are refreshed, and the stamps no longer point at base `e446218`.

Subagent utilization decision: direct/no-op because this was a small, tightly coupled operator FAIL nit-fix in one SQL RPC plus its tests/docs. No subagent inherited mailbox, cursor, lock, push, pod-spend, or paid-API authority.

## Director Evidence

Startup and route refresh:

- `env -u GIT_INDEX_FILE .venv/bin/python scripts/ledger_start_guard.py --seat director --wave 2` -> PASS; active route `coordination/mailbox/sent/2026-07-08T04-35-32Z-coordinator-to-all-coordination.md`.
- `env -u GIT_INDEX_FILE .venv/bin/python .agents/skills/four-seat-protocol/scripts/seat_status.py director --wave 2` -> Pipeline HEAD `655d8e4`, director unread `0 / ref-bus`, Wave 2 `MET`.
- Latest Pipeline mailbox before fix/send remained `2026-07-08T13-24-25Z-operator-to-all-verification-report.md`.

TDD RED evidence before SQL change:

- Initial sandboxed run of `env -u GIT_INDEX_FILE /Users/hyungkoookkim/evidence-ledger/.venv/bin/python -m pytest db/tests/test_rpcs.py -q` failed with `Operation not permitted` connecting to `127.0.0.1:54322`; reran with local DB access allowed.
- After adding the negative target regression and sibling pin, same focused command -> `2 failed, 22 passed in 1.95s`; failures were `broadcast_slots_target_qty_check` for `target_qty=-1` and `broadcast_slots_target_amount_check` for `target_amount=-1`.

Focused GREEN evidence:

- `env -u GIT_INDEX_FILE /Users/hyungkoookkim/evidence-ledger/.venv/bin/python -m pytest db/tests/test_rpcs.py -q` -> `24 passed in 1.71s`.

Final director-side verification:

- `env -u GIT_INDEX_FILE /Users/hyungkoookkim/evidence-ledger/.venv/bin/python -m pytest db/tests -q` -> `78 passed in 5.95s`.
- `env -u GIT_INDEX_FILE /Users/hyungkoookkim/evidence-ledger/.venv/bin/python -m pytest import/tests -q` -> `124 passed in 5.98s`.
- `env -u GIT_INDEX_FILE /Users/hyungkoookkim/evidence-ledger/.venv/bin/python -m pytest tests/unit -q` -> `49 passed in 0.24s`.
- `env -u GIT_INDEX_FILE /Users/hyungkoookkim/evidence-ledger/.venv/bin/python scripts/check_doc_claims.py ARCHITECTURE.md` -> `All anchors checked — no drift.`
- `env -u GIT_INDEX_FILE /Users/hyungkoookkim/evidence-ledger/.venv/bin/python scripts/ci_smoke.py` -> `OK`.
- `env -u GIT_INDEX_FILE git diff --check` -> clean, no output.
- `env -u GIT_INDEX_FILE git diff --name-only -- data '*.xlsx' ios/EvidenceLedger/Sources/Config.plist` -> no output.
- `env -u GIT_INDEX_FILE git show --stat --oneline --no-renames HEAD` -> `6692131`, 3 files changed, 47 insertions, 12 deletions.
- `env -u GIT_INDEX_FILE git status --short --branch` in target worktree -> `## codex/ledger-phase2-task22-pipeline-2026-07-08` with no dirty paths.

## Known Exclusions

- No push was performed.
- No force update was performed.
- No lock was claimed or released.
- No mailbox cursor was consumed.
- No paid API spend, pod spend, production generation, target checkout refresh, or real-data commit was performed.

## Expected Operator Verification

Please independently re-verify `operator-ledger-phase2-task22-lanev` for evidence-ledger focused range `07e4077..6692131` and corrected full range `e446218..6692131`, then return one Pipeline mailbox `verification-report` with GO, NITS, or FAIL.

Suggested checks:

- Confirm `source='excel_import'` with `target_qty=-1` now returns an id plus `target_qty` warning and does not store a negative target quantity.
- Confirm `source='excel_import'` with `target_amount=-1` now returns an id plus `target_amount` warning and does not store a negative target amount.
- Confirm `source='form'` still hard-fails nonpositive target values before insert.
- Confirm model-specific commission-rate bounds, near-duplicate warnings, auth-stamped RPC posture, and import scratch-DB auth shim behavior remain unchanged from the original Task 2.2 implementation.
- Confirm ARCHITECTURE.md truth sync and no real-data/config path changes.

## Exact Next Trigger

Operator independently verifies evidence-ledger focused range `07e4077..6692131` and corrected full range `e446218..6692131` for packet `operator-ledger-phase2-task22-lanev`, then returns one Pipeline mailbox `verification-report` with GO/NITS/FAIL. Director must not push or claim coordinator closeout before operator verdict.

Cursor at send: 0
