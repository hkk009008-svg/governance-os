# Director → Operator: ledger phase2 task22 validations 07e4077

**When:** 2026-07-08T13:15:02Z · **From:** director (online)

Event type: verify-request
Task-board: `ledger-phase2-task22-2026-07-08`
Director packet: `director-ledger-phase2-task22-validations`
Operator packet: `operator-ledger-phase2-task22-lanev`
Coordinator route: `coordination/mailbox/sent/2026-07-08T04-35-32Z-coordinator-to-all-coordination.md`

## Implementation Target

- Target repo: `/Users/hyungkoookkim/evidence-ledger`
- Pipeline-local worktree: `/Users/hyungkoookkim/Pipeline/.worktrees/evidence-ledger-phase2-task22-2026-07-08`
- Branch: `codex/ledger-phase2-task22-pipeline-2026-07-08`
- Required base: `e446218740b96561933da66c8808f2a1fd64d253`
- Implementation commit: `07e407730a98e763e35aa527ed5a09f1d00d7199 feat(db): complete Phase-2 go-forward validations`
- Effective implementation range: `e446218..07e4077`

## Scope Implemented

Task 2.2 implements go-forward validation behavior around `biz.record_slot(jsonb)`:

- `supabase/migrations/20260708000200_entry_validations.sql` recreates `biz.record_slot(jsonb)` while preserving the Task 2.1 auth-stamped/source-forced insert shape.
- Adds `target_qty <= 0` as a hard form validation and an excel-import warning.
- Adds model-specific commission-rate upper bounds:
  - `정률 <= 0.48`
  - `반특 <= 0.45`
  - `완특 <= 0.25`
  - `직매입 <= 0.49`
  - `반반특 <= 0.30`
  - `정액 <= 0.15` when present
- Preserves generic `commission_rate > 1` warning for unbounded or unknown model cases.
- Keeps `target_amount <= 0` validation behavior.
- Keeps `source='form'` as the hard-fail path with `입력 검증 실패` and `source='excel_import'` as warn-only.
- Adds a near-duplicate notice for same `channel_id` + `broadcast_date`; the notice is returned in `warnings` but is excluded from hard-fail warnings and never blocks insert.
- Adds import test scratch-DB auth shim support so import-suite migration replay includes the Task 2.1 auth helper surface.
- Syncs `ARCHITECTURE.md` anchors/counts and marks Task 2.2 implementation/test steps complete in the runway plan. Independent verification remains unchecked by design.

## Changed Surfaces

- `supabase/migrations/20260708000200_entry_validations.sql`
- `db/tests/test_rpcs.py`
- `import/tests/db_setup.py`
- `import/tests/test_agency_load.py`
- `import/tests/test_import_end_to_end.py`
- `import/tests/test_load_staging.py`
- `ARCHITECTURE.md`
- `docs/superpowers/plans/2026-07-08-codex-runway-phase2-to-completion.md`

## Subagent Decision

Direct implementation only. The SQL/test/doc slice was tightly coupled, and seat-authority-sensitive handoff remained with director. No subagent inherited mailbox, cursor, lock, push, pod-spend, or paid-API authority.

## Director Evidence

Pre-change baseline after local Supabase stack was available:

- `env -u GIT_INDEX_FILE bash scripts/db_test.sh` -> `60 passed in 4.87s`
- `env -u GIT_INDEX_FILE bash scripts/import_test.sh` -> `124 passed in 6.01s` after adding the import scratch-DB auth shim required by the existing Task 2.1 auth-stamped migration replay.

TDD red evidence before production SQL:

- `env -u GIT_INDEX_FILE .venv/bin/python -m pytest db/tests/test_rpcs.py -q` -> `10 failed, 12 passed in 1.44s`; failures matched the new Task 2.2 expectations for `target_qty`, near-duplicate warnings, and model-specific commission-rate bounds.

Focused green evidence:

- `env -u GIT_INDEX_FILE .venv/bin/python -m pytest db/tests/test_rpcs.py -q` -> `22 passed in 1.43s`

Final director-side verification:

- `env -u GIT_INDEX_FILE bash scripts/db_test.sh` -> `76 passed in 7.42s`
- `env -u GIT_INDEX_FILE bash scripts/import_test.sh` -> `124 passed in 8.09s`
- `env -u GIT_INDEX_FILE .venv/bin/python -m pytest tests/unit -q` -> `49 passed in 0.27s`
- `env -u GIT_INDEX_FILE .venv/bin/python scripts/ci_smoke.py` -> `OK`
- `env -u GIT_INDEX_FILE git diff --check` -> clean, no output
- `find supabase/migrations -maxdepth 1 -name '*.sql' -print | wc -l` -> `16`
- `env -u GIT_INDEX_FILE git show --stat --oneline HEAD` -> `07e4077`, 8 files changed, 246 insertions, 10 deletions
- `env -u GIT_INDEX_FILE git status --short --branch` in target worktree -> `## codex/ledger-phase2-task22-pipeline-2026-07-08` with no dirty paths

Pipeline refresh immediately before this verify-request:

- `env -u GIT_INDEX_FILE .venv/bin/python .agents/skills/four-seat-protocol/scripts/seat_status.py director --wave 2` -> unread `0 / ref-bus`, Wave 2 `MET`, HEAD `13cde0e`
- `ls -1t coordination/mailbox/sent | head -12` -> newest mailbox entry remained `2026-07-08T04-35-32Z-coordinator-to-all-coordination.md`
- Target worktree HEAD -> `07e4077 feat(db): complete Phase-2 go-forward validations`

## Known Exclusions

- No push was performed.
- No force update was performed.
- No lock was claimed.
- No mailbox cursor was consumed.
- No paid API spend, pod spend, production generation, or real-data commit was performed.
- Docker/Supabase local stack was used only to run local DB/import verification.

## Expected Operator Verification

Please independently verify `operator-ledger-phase2-task22-lanev` for evidence-ledger commit `07e4077` / range `e446218..07e4077` and return one Pipeline mailbox `verification-report` with GO, NITS, or FAIL.

Suggested checks:

- Confirm `source='form'` hard-fails `target_qty <= 0`.
- Confirm `source='form'` hard-fails the listed model-specific commission-rate upper bounds, while exact limits and `commission_rate is null` remain accepted where schema permits.
- Confirm `source='excel_import'` returns warnings only for invalid `target_qty` and commission-rate bounds.
- Confirm near-duplicate detection returns a warning/notice and still inserts the row.
- Confirm the import scratch-DB auth shim is test-only and does not relax production grants or `record_slot` auth stamping.
- Confirm `ARCHITECTURE.md` and the runway plan truth sync match the landed diff.
- Confirm no real-data output, paid API, pod spend, push, or force update occurred.

## Exact Next Trigger

Operator independently verifies evidence-ledger commit `07e4077` / range `e446218..07e4077` for packet `operator-ledger-phase2-task22-lanev` and returns one Pipeline mailbox `verification-report` with GO/NITS/FAIL. Director must not push or claim coordinator closeout before operator verdict.

Cursor at send: 0
