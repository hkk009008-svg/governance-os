# Coordinator execution release — normalization sidecar Task 5

**When:** 2026-07-11T19:58:03Z

Event type: coordination
Disposition: `IMPLEMENTATION_RELEASE`
Task-board: `ledger-workbook-refresh-2026-07-11`
Target base: `cb9c278`
Governing plan: `657a1ba`

Task 4 is complete at `cb9c278` with fresh specification PASS and quality
APPROVED. Release Task 5 only in exactly:

- `DECISIONS.md`
- `ARCHITECTURE.md`
- `OPERATIONS.md`
- `docs/MANUAL.md`

Collect fresh tracked facts before editing by running the plan's import-module
inventory plus complete `import/tests`, `db/tests`, and `tests/unit` suites.
Record only those freshly executed outputs and no real business values.

Append ADR-009 without editing prior ADR text. Synchronize product truth to the
reviewed Tasks 1–4, including the two normalization modules, 12 automatic /
68 owner-input / 3 dependent-summary authority partition, canonical JSON
boundary, audit bindings, ignored local artifacts, read-only DB binding, and
the applier's no-Excel boundary. Document exact sidecar generation,
validation, and planner commands. Add the Korean owner procedure, editable
columns, complete-partition rule, validation failure meanings, and a mandatory
stop while any of the 68 owner fields remains blank. An incomplete sidecar
cannot authorize scratch or canonical apply.

Run doc claims over all four documents, target smoke, and `git diff --check`;
commit exactly the four paths, then obtain fresh specification PASS and fresh
quality APPROVED. No real workbook, database/resource, scratch/service, push,
merge, publication, or cursor action is released. Absolute real paths may
appear only in clearly labeled local-only command examples; real values,
hashes, dumps, sidecars, plans, and reports remain out of git and mailbox
bodies.

## Exact Next Trigger

Director refreshes target/mail, executes the four fresh fact commands, updates
only the released four documents, runs all Task 5 gates, commits, and enters
fresh specification and quality reviews.
