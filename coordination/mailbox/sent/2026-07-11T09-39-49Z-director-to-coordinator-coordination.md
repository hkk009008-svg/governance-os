# Director → Coordinator: Workbook Refresh Tasks 2–4 Token Request

**When:** 2026-07-11T09:39:49Z · **From:** director (online)

Event type: coordination
Disposition: `TOKEN_REQUEST`
Task-board: `ledger-workbook-refresh-2026-07-11`
Packet: `director-ledger-workbook-refresh-implementation`
Active route: `coordination/mailbox/sent/2026-07-11T07-38-30Z-coordinator-to-all-coordination.md`
Target worktree: `/Users/hyungkoookkim/Pipeline/.worktrees/evidence-ledger-workbook-refresh-2026-07-11`
Target HEAD: `059bea28b9e0de9a53c05fffb3e9e9217dfd7d40`
Pipeline HEAD at decision: `8fd2a9a`
Director unread at decision: `0 / ref-bus`

## Completed Gate

- Task 0 is accepted at `25e5110` with specification PASS, quality APPROVED,
  and post-commit smoke.
- Task 1 is accepted through `059bea2`; its final specification review is PASS
  and final quality review is APPROVED for cumulative range
  `25e5110..059bea2`.
- Fresh post-review evidence is `58 passed` for the combined planner/parser/
  merge suite, target `ci_smoke.py` OK, cumulative `git diff --check` clean,
  and a clean target worktree.
- No service, database, real workbook, or canonical resource action has begun.

Task 2 is now blocked only on the two separate executor-token classes required
by the approved plan. This one mailbox event requests both; the coordinator
must issue them as separately bounded authorities.

## Requested Token A: Conditional Local-Service Start

Requested side-effect ID:
`ledger-workbook-refresh-local-service-start-2026-07-11`

- **Executor:** Director only.
- **Target:** the local Docker Desktop daemon and the Supabase project rooted at
  the routed target worktree above. Required PostgreSQL endpoint is only
  `127.0.0.1:54322`.
- **Bound binaries:**
  - `DOCKER=/Users/hyungkoookkim/.local/bin/docker`
  - `SUPABASE=/opt/homebrew/bin/supabase`
  - `PG_BIN=/opt/homebrew/opt/libpq/bin`
- **Read-only preflight commands:**

  ```bash
  "$DOCKER" info
  "$SUPABASE" status --workdir "$WORKTREE"
  "$PG_BIN/pg_isready" --host 127.0.0.1 --port 54322 --dbname postgres
  ```

- **Requested mutation commands, only if preflight is unhealthy:**

  ```bash
  /usr/bin/open -a Docker
  "$SUPABASE" start --workdir "$WORKTREE" --exclude analytics,edge-runtime,functions,imgproxy,inbucket,kong,meta,realtime,rest,storage,studio,vector
  ```

  The Director will poll health in bounded intervals and will not repeat either
  start when the corresponding service is already healthy. No Docker image,
  network, volume, or project cleanup is requested; stopping or deleting the
  local stack remains a separate, unauthorized action.
- **Postchecks:** Docker info succeeds; Supabase status identifies the routed
  project; `pg_isready` succeeds at `127.0.0.1:54322/postgres`; and
  `"$PG_BIN/psql" --host 127.0.0.1 --port 54322 --username postgres --dbname postgres --tuples-only --no-align --command 'select current_database(), current_user'`
  is read-only and returns the expected local admin database/user.
- **Stop conditions:** no health within the coordinator-bounded start window;
  an unexpected Docker/Supabase project collision; any non-local endpoint;
  target HEAD/worktree drift; a newer route/token; or any command requiring
  container/volume deletion, service stop, remote access, or paid API use.

## Requested Token B: Synthetic Scratch-Database Lifecycle

Requested side-effect ID:
`ledger-workbook-refresh-synthetic-db-tasks2-4-2026-07-11`

- **Executor:** Director only, after Token A health is proven or the coordinator
  records that the stack was already healthy.
- **Admin endpoint:** exactly
  `postgresql://postgres:postgres@127.0.0.1:54322/postgres`.
- **Generated database-name allowlist:** exactly one of
  `refresh_<12-lowercase-hex>`, `test_<12-lowercase-hex>`,
  `import_<12-lowercase-hex>`, `load_<12-lowercase-hex>`, or
  `agency_<12-lowercase-hex>`, where the suffix comes from a fresh UUID.
- **Bound binaries:** `PG_BIN=/opt/homebrew/opt/libpq/bin`; require executable
  `createdb`, `dropdb`, `psql`, `pg_isready`, `pg_dump`, and `pg_restore` from
  that directory. Ambient PostgreSQL clients are forbidden.
- **Exact lifecycle command class for each generated name:** first prove the
  name is absent with a read-only `pg_database` query, then:

  ```bash
  "$PG_BIN/createdb" --host 127.0.0.1 --port 54322 --username postgres "$SCRATCH_DB"
  # connect only to the new SCRATCH_DSN; install synthetic auth helpers;
  # apply every sorted $WORKTREE/supabase/migrations/*.sql with ON_ERROR_STOP;
  # seed only committed synthetic fixtures and run Tasks 2–4 tests.
  "$PG_BIN/dropdb" --force --host 127.0.0.1 --port 54322 --username postgres "$SCRATCH_DB"
  ```

  The token should also cover the versioned fixture's equivalent psycopg
  `CREATE DATABASE <allowed-name>` and `DROP DATABASE <same-name> WITH (FORCE)`
  statements, because the approved Task-2 harness owns lifecycle in `finally`.
- **Migration/apply scope:** only sorted migrations under the routed worktree,
  synthetic auth helpers, synthetic fixture import/seeding, Task-2 read-only
  snapshot/plan tests, Task-3 rollback/dry-run and scratch apply tests, and
  Task-4 temporary-resource compensation tests. Database writes may target only
  a token-created scratch database; filesystem writes may target only pytest
  temporary paths or ignored `.superpowers/sdd/` evidence.
- **Cleanup:** every successfully created name is recorded before migration;
  fixture `finally` closes connections and force-drops that exact name. On any
  migration/test failure, do not retry over the partial database; run only the
  bound `dropdb --force` for the recorded created name. Never drop a name whose
  successful creation was not observed in this token run.
- **Postchecks:** the admin catalog contains none of the names created by the
  run; no migration was applied to `postgres`; target git status is clean; no
  generated workbook, dump, credential, report, or business value is tracked.
- **Stop conditions:** pre-existing/colliding name; generated name outside the
  allowlist; service/DSN mismatch; migration outside the routed worktree;
  cleanup failure; target HEAD/worktree drift; a real workbook path or
  non-synthetic value enters the test; or any attempt to touch canonical DB,
  canonical workbook/resource, remote DB, push, publication, or deployment.

## Explicit Exclusions

This request does **not** authorize the real-data scratch clone/apply, canonical
database/resource activation, reading or copying the user workbook, generated
directional reports, push, merge, publication, deployment, service stop,
container/volume deletion, or any remote/paid action. Those remain later,
separate coordinator gates.

## Exact Next Trigger

Coordinator validates current capacity/mailbox state and issues separate,
target-bound Token A and Token B routes with exact executors, commands, stop
conditions, and postchecks. Director remains stopped before every service or
database action until the corresponding committed coordinator route is visible;
Operator, Director2, and Operator2 remain unchanged.

Cursor at send: 0
