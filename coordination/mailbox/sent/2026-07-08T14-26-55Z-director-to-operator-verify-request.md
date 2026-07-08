# Director → Operator: ledger phase2 task23 result_history bdc7f6b

**When:** 2026-07-08T14:26:55Z · **From:** director (online)

Event type: verify-request
Task-board: `ledger-phase2-task23-2026-07-08`
Director packet: `director-ledger-phase2-task23-result-history`
Operator packet: `operator-ledger-phase2-task23-lanev`
Coordinator route: `coordination/mailbox/sent/2026-07-08T14-11-13Z-coordinator-to-all-coordination.md`

## Implementation Target

- Target repo: `/Users/hyungkoookkim/evidence-ledger`
- Pipeline-local worktree: `/Users/hyungkoookkim/Pipeline/.worktrees/evidence-ledger-phase2-task23-2026-07-08`
- Branch: `codex/ledger-phase2-task23-pipeline-2026-07-08`
- Original base: `36f55063a2d87312810e82db624b837289a4a382`
- Implementation commit: `bdc7f6b8aef74eddeb35993f18d7bef48fd2a58f feat(db): add result_history audit view`
- Focused implementation range: `36f5506..bdc7f6b`

## Scope Implemented

Task 2.3 adds the read-only audit trail view `biz.result_history`.

Changed surfaces:

- `supabase/migrations/20260708000300_result_history_view.sql`
- `db/tests/test_result_history.py`
- `ARCHITECTURE.md`

Behavioral surface:

- `biz.result_history` walks the immutable `broadcast_results.supersedes_id` chain and returns one row per revision per slot.
- The view exposes `slot_id`, `revision_id`, `revision_no`, `stage`, `gross_orders`, `net_orders`, `gross_amount`, `net_amount`, `entered_by`, `entered_at`, `source`, `reason`, `superseded_by_id`, and `is_head`.
- `revision_no` starts at `1` for the root and increments along the supersedes chain.
- The prior revision reports `superseded_by_id`; the current head reports `is_head = true`.
- `authenticated` receives SELECT only; no table/RPC write surface was added.
- The current committed result schema has no `gross_orders` / `net_orders` storage. The view exposes those routed Phase-2 contract columns as typed NULL placeholders and records that in `ARCHITECTURE.md`.

Subagent utilization decision: direct/no-op because this was one tightly coupled db test plus migration plus truth-doc refresh. No subagent inherited mailbox, cursor, GO, route, lock, push, pod-spend, or paid-API authority.

## Director Evidence

Startup and hot-tree refresh:

- `env -u GIT_INDEX_FILE .venv/bin/python scripts/ledger_start_guard.py --seat director --wave 2` → PASS; active route `coordination/mailbox/sent/2026-07-08T14-11-13Z-coordinator-to-all-coordination.md`.
- `env -u GIT_INDEX_FILE .venv/bin/python .agents/skills/four-seat-protocol/scripts/seat_status.py director --wave 2` → Pipeline HEAD `bbd70f8`; director unread `0 / ref-bus`; Wave 2 `MET`.
- `env -u GIT_INDEX_FILE git log --oneline -5` in Pipeline → latest `bbd70f8 coord(coordinator): route ledger phase2 task23`.
- Evidence-ledger isolated worktree created from `origin/main` `36f55063a2d87312810e82db624b837289a4a382`.

Baseline and RED evidence:

- Initial worktree smoke with `.venv/bin/python scripts/ci_smoke.py` failed because linked worktree had no repo-local `.venv/`; reran with `/Users/hyungkoookkim/evidence-ledger/.venv/bin/python`.
- `env -u GIT_INDEX_FILE /Users/hyungkoookkim/evidence-ledger/.venv/bin/python scripts/ci_smoke.py` before implementation → `OK`.
- Initial sandboxed DB-suite run failed with local-connection `Operation not permitted` to `127.0.0.1:54322/54321`; reran with local DB access allowed.
- Baseline `env -u GIT_INDEX_FILE /Users/hyungkoookkim/evidence-ledger/.venv/bin/python -m pytest db/tests -v` → `78 passed in 7.00s`.
- After adding `db/tests/test_result_history.py` before the migration, `env -u GIT_INDEX_FILE /Users/hyungkoookkim/evidence-ledger/.venv/bin/python -m pytest db/tests/test_result_history.py -v` → `3 failed`; failures were `relation "biz.result_history" does not exist` and an empty information-schema column list.

Focused GREEN and final verification:

- After adding `20260708000300_result_history_view.sql`, focused `env -u GIT_INDEX_FILE /Users/hyungkoookkim/evidence-ledger/.venv/bin/python -m pytest db/tests/test_result_history.py -v` → `3 passed in 0.31s`.
- `env -u GIT_INDEX_FILE /Users/hyungkoookkim/evidence-ledger/.venv/bin/python -m pytest db/tests -v` → `81 passed in 7.81s`.
- Temporary `.venv` symlink created only to run the routed script exactly, then removed.
- `env -u GIT_INDEX_FILE scripts/db_test.sh` → `81 passed in 8.02s`.
- `env -u GIT_INDEX_FILE /Users/hyungkoookkim/evidence-ledger/.venv/bin/python scripts/ci_smoke.py` → `OK`.
- `env -u GIT_INDEX_FILE git diff --check` → clean; no output.
- `env -u GIT_INDEX_FILE git show --stat --oneline HEAD` → `bdc7f6b feat(db): add result_history audit view`; 3 files changed, 194 insertions(+), 3 deletions(-).
- `env -u GIT_INDEX_FILE git status --short --branch` in target worktree → `## codex/ledger-phase2-task23-pipeline-2026-07-08` with no dirty paths.

## Known Exclusions

- No push was performed.
- No force update was performed.
- No lock was claimed or released.
- No mailbox cursor was consumed.
- No paid API spend, pod spend, production generation, target checkout refresh, or real-data commit was performed.
- No iOS audit-trail UI was implemented; that remains Task 2.6.
- No underlying `broadcast_results` order-count storage was added; `gross_orders` / `net_orders` are typed NULL view-contract columns for this task.

## Expected Operator Verification

Please independently verify `operator-ledger-phase2-task23-lanev` for evidence-ledger focused range `36f5506..bdc7f6b`, then return one Pipeline mailbox `verification-report` with GO, NITS, or FAIL.

Suggested checks:

- Confirm `biz.result_history` orders root-to-head revisions by `revision_no`, preserves `reason`, exposes `superseded_by_id`, and marks only the current head with `is_head`.
- Confirm the authenticated role can SELECT `biz.result_history` and has no INSERT/UPDATE/DELETE privileges on the view.
- Confirm the routed column contract includes `gross_orders` / `net_orders` while the current schema caveat is explicitly documented.
- Confirm no write RPC, RLS table policy, real-data path, config path, push, lock, cursor, pod, paid API, or target-refresh side effect was introduced.

## Exact Next Trigger

Operator independently verifies evidence-ledger focused range `36f5506..bdc7f6b` for packet `operator-ledger-phase2-task23-lanev`, then returns one Pipeline mailbox `verification-report` with GO/NITS/FAIL. Director must not push or claim coordinator closeout before operator verdict.

Cursor at send: 0
