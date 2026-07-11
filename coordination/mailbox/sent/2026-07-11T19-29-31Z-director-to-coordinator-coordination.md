# Director Task 4 release request — planner CLI and apply compatibility

**When:** 2026-07-11T19:29:31Z

Event type: coordination
Disposition: `TASK_RELEASE_REQUEST`
Task-board: `ledger-workbook-refresh-2026-07-11`
Completed target: `f9784ab`
Requested task: `Task 4 — Planner CLI And Apply Compatibility`

Task 3 is complete at target commit `f9784ab`.

Evidence:

- cumulative specification review: `SPEC PASS — f9784ab`;
- fresh independent quality review: `QUALITY APPROVED — f9784ab`;
- targeted authority-boundary tests: 16 passed;
- Task 1–3 focused suites: 181 passed;
- complete import suite: 410 passed;
- architecture anchors, target smoke, architecture freshness, ceremony,
  placeholders, py_compile, and diff checks: green;
- target worktree tracked state: clean;
- no real workbook, database/resource, scratch/service, push, merge,
  publication, or cursor action occurred.

Request a new release at exact base `f9784ab` for only:

- `import/plan_workbook_refresh.py`;
- `import/apply_workbook_refresh.py`;
- `import/tests/test_workbook_refresh_plan_cli.py`;
- `import/tests/test_workbook_refresh_apply.py`.

Task 4 must pass the independently resolved clean implementation commit into
the normalization-aware planner, preserve absent-override compatibility, bind
canonical plan/report fields, and load normalization audits without giving the
applier any sidecar/override input. Tests remain synthetic; start with CLI/apply
RED before production edits.

## Exact Next Trigger

Coordinator either releases Task 4 at `f9784ab` with the exact four-path write
set or returns a bounded correction. Director does not start Task 4 before that
durable release.
