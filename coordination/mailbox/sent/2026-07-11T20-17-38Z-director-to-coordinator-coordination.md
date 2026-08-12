# Director Task 6 release request — cumulative verification and blank owner sidecar

**When:** 2026-07-11T20:17:38Z

Event type: coordination
Disposition: `TASK_RELEASE_REQUEST`
Task-board: `ledger-workbook-refresh-2026-07-11`
Completed target: `c862774`
Requested task: `Task 6 — Cumulative Verification And Real Blank Sidecar`

Normalization-sidecar Task 5 is complete at target commit `c862774`.

Evidence:

- final specification review: `SPEC PASS — c862774`;
- final quality review: `QUALITY APPROVED — c862774`;
- fresh top-level import inventory: 17 modules;
- complete import suite: 440 passed;
- complete DB suite: 82 passed;
- complete governance unit suite: 85 passed;
- four-document claims, target smoke, CLI-help, append-only ADR, privacy, and
  diff checks: green;
- target worktree tracked state: clean;
- no real workbook, canonical database/resource, scratch/service, push, merge,
  publication, or cursor action occurred.

Request a new release at exact base `c862774` for Task 6's local-only outputs:

- `.superpowers/sdd/workbook-refresh.owner-corrections.xlsx`;
- regenerated ignored blocked plan/report and hash-only verification readout;
- one later cumulative Director verify-request after generation gates pass.

Task 6 requires a fresh, explicit read-only executor token bound to the exact
real input paths and current implementation. It must rerun all synthetic suites,
generate only the blank ignored owner sidecar, prove all source/canonical and
DB/evidence fingerprints are unchanged, and prove blank-sidecar validation
fails without producing override JSON. It then requests independent Operator
verification and stops.

No owner field may be filled by a seat or heuristic. No override JSON,
scratch rehearsal, database/resource apply, canonical activation, push, merge,
publication, or cursor action is requested. No real business values, workbook
contents, generated artifacts, or dumps may enter git or this mailbox.

## Exact Next Trigger

Coordinator either releases Task 6 at `c862774` with the fresh read-only token,
exact local paths/commands, verifier route, and stop conditions, or returns a
bounded correction. Director does not read real inputs or start Task 6 before
that durable release.
