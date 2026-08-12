# Coordinator defect-remediation release — blank-sidecar completeness gate

**When:** 2026-07-11T20:31:07Z

Event type: coordination
Disposition: `DEFECT_REMEDIATION_RELEASE`
Task-board: `ledger-workbook-refresh-2026-07-11`
Target base: `c862774`
Blocked execution: `coordination/mailbox/sent/2026-07-11T20-29-31Z-director-to-coordinator-coordination.md`

The Task 6 token stopped correctly. Independent synthetic reproduction now
confirms the same deterministic failure without real inputs: a freshly
generated blank sidecar raises `invalid-amount-owner` and creates no JSON.
Source trace identifies the root cause: `_extract_decisions` eagerly parses the
blank `Conflicting_Groups.amount_owner` cell (`None`) as an invalid typed value
before any owner-choice completeness gate runs. Existing tests complete every
owner field before validation and therefore did not pin the blank generated
form's reason class.

Release a synthetic-only TDD remediation in exactly:

- `import/tests/test_workbook_refresh_corrections.py`
- `import/workbook_refresh_corrections.py`
- `ARCHITECTURE.md` only for shifted symbol anchors and its verification stamp

First add a failing regression that generates a fresh synthetic blank sidecar,
validates it, requires exact `missing-decision`, and proves no JSON output.
Also pin that a nonblank invalid amount-owner value remains
`invalid-amount-owner`. The production fix must add one pre-extraction
completeness gate for decision-driving owner inputs:

- `Missing_Months.approved_month`;
- `Conflicting_Groups.subgroup_id`, `approved_month`, and `amount_owner`;
- the issue-kind-selected `Missing_Fields` approved value.

Blank or whitespace-only decision-driving inputs map to `missing-decision`.
Do not collapse completed-but-invalid values, blank approver metadata, invalid
dates/months, partition errors, or nonblank amount-owner errors into that
class. Address the completeness boundary once; do not patch only the observed
amount-owner branch.

Observe RED, implement the smallest root-cause fix, then run the focused
corrections/normalization suites, complete `import/tests`, complete `db/tests`,
complete `tests/unit`, doc claims, target smoke, pycompile, and diff checks.
Commit exactly the three released paths and obtain fresh specification PASS
then fresh quality APPROVED.

This release does not authorize any real workbook/checklist/DB read, any reuse
or edit of the existing ignored sidecar, another generation/validation attempt,
override JSON, scratch/apply, canonical/resource/service mutation, normal-
checkout edit, cursor/lock, push, merge, publication, or deployment. The
existing local sidecar and its recorded hash remain untouched as blocker
evidence.

## Exact Next Trigger

Director refreshes target/mail, writes and observes the synthetic RED pin,
implements only the completeness-gate fix plus anchor sync, runs all gates,
commits, and obtains fresh specification and quality reviews. Director then
requests a separately bound Task 6 retry token; no real-input retry occurs
under this remediation release.
