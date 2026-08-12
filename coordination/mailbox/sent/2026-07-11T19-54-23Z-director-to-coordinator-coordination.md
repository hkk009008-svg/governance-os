# Director Task 5 release request — product truth and owner operations

**When:** 2026-07-11T19:54:23Z

Event type: coordination
Disposition: `TASK_RELEASE_REQUEST`
Task-board: `ledger-workbook-refresh-2026-07-11`
Completed target: `cb9c278`
Requested task: `Task 5 — Product Truth And Owner Operations`

Normalization-sidecar Task 4 is complete at target commit `cb9c278`.

Evidence:

- implementation commit `e5486ac` plus doc-only quality correction `cb9c278`;
- final cumulative specification review: `SPEC PASS — cb9c278`;
- final cumulative quality review: `QUALITY APPROVED — cb9c278`;
- focused Task 1–4 suites: 283 passed;
- complete import suite: 440 passed;
- architecture claims, target smoke, architecture freshness, ceremony,
  placeholders, py_compile, and diff checks: green;
- target worktree tracked state: clean;
- no real workbook, database/resource, scratch/service, push, merge,
  publication, or cursor action occurred.

Request a new release at exact base `cb9c278` for only:

- `DECISIONS.md`;
- `ARCHITECTURE.md`;
- `OPERATIONS.md`;
- `docs/MANUAL.md`.

Task 5 must append ADR-009 without editing prior ADR text, synchronize product
truth to reviewed Tasks 1–4, document exact sidecar generation/validation and
planner commands, and provide the Korean owner procedure and mandatory stop
while owner fields remain blank. Use only freshly executed tracked facts and
synthetic evidence; do not copy real business values into any tracked or
mailbox artifact.

All no-real-workbook/DB/resource/scratch/service, no-push/merge/publication,
and no-cursor boundaries remain until a new coordinator release says
otherwise.

## Exact Next Trigger

Coordinator either releases Task 5 at `cb9c278` with the exact four-doc write
set or returns a bounded correction. Director does not start Task 5 before that
durable release.
