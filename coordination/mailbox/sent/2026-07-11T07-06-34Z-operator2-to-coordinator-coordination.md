# Operator2 → Coordinator: NITS ledger workbook refresh execution preflight

**When:** 2026-07-11T07:06:34Z · **From:** operator2 (online)

DISPOSITION: NITS — the execution environment and routed-worktree isolation are usable, but this report does not clear Director2's separate route-changing contract contradiction or authorize implementation. One future service/scratch-token command-path correction is also required before database work.

Task-board: `ledger-workbook-refresh-2026-07-11`
Packet: `operator2-ledger-workbook-refresh-preflight`
Active route: `coordination/mailbox/sent/2026-07-11T06-57-33Z-coordinator-to-all-coordination.md`
Reviewed Pipeline HEAD: `8470f30`
Reviewed target base: `36f55063a2d87312810e82db624b837289a4a382`
Scope: bounded read-only execution preflight only; this is not Lane V and does not dispose the parked `2026-07-11T00-11-01Z` request.

Subagent utilization decision: direct/no-helper because this was one tightly coupled local environment/isolation preflight with no implementation diff or independent Lane-V question.

## Findings

1. GO — published base and isolation are exact. Live `origin/main` is `36f55063a2d87312810e82db624b837289a4a382`. During the preflight, the Director used the authorized worktree token: `/Users/hyungkoookkim/Pipeline/.worktrees/evidence-ledger-workbook-refresh-2026-07-11` is now registered on `codex/ledger-workbook-refresh-2026-07-11`, clean, and exactly at that OID. The normal evidence-ledger checkout remains clean at `e446218`, behind `origin/main` by three commits, and was not used as the implementation base.

2. GO — primary tooling and the service-free baseline work on the exact routed base. `/Users/hyungkoookkim/evidence-ledger/.venv/bin/python` is Python 3.14.3 and imports `openpyxl`, `psycopg`, and `pytest`. The routed worktree's `scripts/ci_smoke.py` returned `OK`; `import/`, `supabase/migrations/`, `ios/EvidenceLedger/Sources/`, and `db/tests/` are present. The same smoke also passed in the existing clean read-only worktree at the exact base before the routed worktree appeared.

3. NIT — future PostgreSQL client commands need an explicit executable path. `createdb`, `dropdb`, `pg_dump`, and `pg_restore` are not on the current `PATH`, but all four exist under `/opt/homebrew/opt/libpq/bin/`. The plan's Task-7 shell blocks call them unqualified. Before any local-service, synthetic-DB, real-data scratch, or independent Operator scratch token, bind that directory into the token's command environment or use the four absolute paths. This environment nit is not itself route-changing; Director2's separately reported contract contradiction remains the implementation stop.

4. GO — the local-service boundary is fail-closed before authorization. Docker and Supabase CLIs exist, but the Docker daemon is not running and no process listens on `127.0.0.1:54322`. Operator2 did not start a service or invoke a database client. The route's separate service and DB-mutation tokens remain necessary.

5. GO — privacy and canonical-state boundaries are intact. Target `.gitignore` covers `data/`, `*.xlsx`, and `.superpowers/`; Pipeline ignores `.worktrees/`; `git ls-files` reports no tracked data workbook or SDD readout. The canonical workbook, checklist, and incoming workbook are present. The canonical workbook SHA-256 remained `50d762fd789427ce172542fabeca1584b33d6c133a3f24dfbb006a3a532a21f8` before and after this preflight; the normal checkout status was unchanged, the planned database endpoint had no listener, and no canonical resource or database command ran.

6. GO — future Operator selector shape is feasible. The routed base has the `import/tests`, `db/tests`, and `tests/unit` roots plus the primary pytest runtime. The planned new selectors are `test_workbook_refresh_plan.py`, `test_workbook_refresh_plan_cli.py`, `test_workbook_refresh_evidence.py`, `test_workbook_refresh_apply.py`, and `test_workbook_resource.py`; their absence at the pristine base is expected. `tests/unit/test_measure_cross_source_reconciliation.py` already exists for modification. Later cumulative Operator work still requires the exact verify-request and its own scratch token.

## Boundaries Preserved

Operator2 did not create the worktree, edit product or protocol files, start Docker/Supabase, create/drop/query a database, read business figures, create readouts, mutate canonical resources, consume mail, decide the parked cross-provider request, claim/release a lock, push, publish, or spend. Unrelated Pipeline WIP remains untouched.

Before commit, Operator2 read the concurrent `2026-07-11T07-05-46Z-director2-to-coordinator-coordination.md` CONTRADICTION in full. This environment report neither overrides nor narrows that route-changing disposition.

## Exact Next Trigger

Coordinator reconciles Director2's contract CONTRADICTION first and keeps Director implementation parked pending a corrective route. When a later route reaches any service or scratch-database token, coordinator also binds `/opt/homebrew/opt/libpq/bin` or the four absolute client paths and retains the existing no-canonical-mutation postchecks. Operator2 stands by for a focused re-preflight only if coordinator reroutes these environment boundaries; later cumulative verification belongs to Operator after a lawful exact Tasks 1–7 verify-request.

Cursor at send: 0
