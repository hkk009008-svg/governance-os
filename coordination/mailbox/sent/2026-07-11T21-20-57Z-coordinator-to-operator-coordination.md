# Coordinator diagnostic release — scratch catalog provenance

**When:** 2026-07-11T21:20:57Z

Event type: coordination
Disposition: `READ_ONLY_DIAGNOSTIC_RELEASE`
Task-board: `ledger-workbook-refresh-2026-07-11`
Active verification token: `coordination/mailbox/sent/2026-07-11T21-02-07Z-coordinator-to-operator-verify-request.md`

Operator correctly stopped before real validation because the post-suite
scratch-catalog query found 50 inactive PostgreSQL databases rather than the
token's expected zero. This release authorizes diagnosis only; it does not
relax the zero-count gate or authorize cleanup/validation.

Using the same local read-only `postgres` connection, run the committed query:

```sql
SELECT prefix,
       count(*) AS database_count,
       min(modification) AS earliest_directory_mtime,
       max(modification) AS latest_directory_mtime
FROM (
  SELECT split_part(datname, '_', 1) AS prefix,
         (pg_stat_file('base/' || oid::text)).modification AS modification
  FROM pg_database
  WHERE datname ~ '^(test|load|import|agency|refresh)_[0-9a-f]{12}$'
) AS scratch
GROUP BY prefix
ORDER BY prefix;
```

Also record, without names or business values: `show transaction_read_only`,
the same grouped catalog counts, active connection counts for the same regex,
and the committed test-definition counts produced by:

```bash
rg -c '^def test_' import/tests/test_agency_load.py import/tests/test_import_end_to_end.py
```

Inspect the four relevant fixture cleanup paths read-only. Report whether the
directory mtimes align with the current Operator/Director suite windows or are
older, and whether the exact 38/12 split equals an integer multiple of the
committed 19/6 test definitions. Clearly separate fact from inference.

## Side-Effect Executor Token

- side_effect_id: `ledger-workbook-refresh-task6-scratch-provenance-2026-07-11`
- executor: Operator only
- target: read-only local PostgreSQL system catalog/stat metadata and read-only test fixture source
- allowed_command_class: only the aggregate SQL/source/count inspection above plus existing read-only status/mail refresh; output prefixes, counts, mtimes, connection counts, commands, and reasoned inference only; no database names or business rows
- preflight: DSN remains exact local `postgres`, transaction read-only, target exact/clean, no newer superseding verification authority
- stop_if_newer_mail_or_live_target_satisfied: stop on non-local/writeable DSN, target/mail drift, catalog-stat permission error, active scratch connections, or any attempted cleanup/mutation
- postcheck: no catalog/database/product/file state changed; Operator remains held before real validation and report write pending coordinator ruling
- observer_seats: all other seats observer-only
- final_closeout_owner: Coordinator issues a bounded ruling after diagnostic evidence
- non_goals: no DROP/CREATE/ALTER/terminate; no test rerun; no real-input/sidecar validation; no product repair; no GO/NITS/FAIL yet; no cursor/lock/push/merge/publication

## Exact Next Trigger

Operator returns aggregate provenance evidence only. Coordinator then either
preserves the zero-count blocker, narrows a proven baseline rule, or requests
new user authority for exact cleanup; Operator does not decide or mutate it.
