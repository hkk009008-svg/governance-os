# Coordinator execution release — normalization sidecar Task 1

**When:** 2026-07-11T17:31:40Z

Event type: coordination
Disposition: `IMPLEMENTATION_RELEASE`
Task-board: `ledger-workbook-refresh-2026-07-11`
Target: `/Users/hyungkoookkim/Pipeline/.worktrees/evidence-ledger-workbook-refresh-2026-07-11`
Target base: `d57f538`
Approved spec: `docs/superpowers/specs/2026-07-12-ledger-workbook-normalization-sidecar-design.md` through `b7ce3a9`
Approved plan: `docs/superpowers/plans/2026-07-12-ledger-workbook-normalization-sidecar.md` at `e109814`

The user-principal selected subagent-driven execution. Release Task 1 only:
the pure normalization contract in exactly
`import/workbook_refresh_normalization.py` and
`import/tests/test_workbook_refresh_normalization.py`.

Use a fresh implementer, strict tests-only RED before production, then a clean
commit, fresh specification review, and fresh quality review. Record completion
in the ignored `.superpowers/sdd/progress.md` ledger. Do not begin Task 2 until
both Task 1 reviews approve the immutable commit.

Global boundaries remain: synthetic values only; no real workbook read; no
source/canonical workbook, database, resource, scratch, or service mutation;
no push, merge, publication, or cursor consume. Coordinator authors no product
code. Existing unrelated Pipeline WIP remains untouched.

## Exact Next Trigger

Director refreshes durable state, verifies the routed worktree is clean at
`d57f538`, extracts Task 1 from plan `e109814`, dispatches a fresh tests-only
implementer, observes the intended RED, and then authorizes production code.
