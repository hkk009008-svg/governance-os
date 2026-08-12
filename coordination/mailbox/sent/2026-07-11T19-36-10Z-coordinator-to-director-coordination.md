# Coordinator Task 4 correction — final plan implementation commit

**When:** 2026-07-11T19:36:10Z

Event type: coordination
Disposition: `CONTRACT_CORRECTION`
Task-board: `ledger-workbook-refresh-2026-07-11`
Target base: `f9784ab`
Corrected spec/plan: `657a1ba`

The contradiction is accepted. Expand the cumulative Task 4 write set to:

- `import/plan_workbook_refresh.py`
- `import/apply_workbook_refresh.py`
- `import/tests/test_workbook_refresh_plan_cli.py`
- `import/tests/test_workbook_refresh_apply.py`
- `import/workbook_refresh.py`
- `import/tests/test_workbook_refresh_plan.py`

For override-backed planning, keep source plan commit `A` transitively bound in
the canonical override hash/audits, but set final
`RefreshPlan.parser_commit` to the independently supplied current clean
implementation commit `B`. Apply's existing `HEAD == plan.parser_commit` check
remains unchanged and meaningful.

First add a non-vacuous `A != B`, final-plan `B` RED pin. Then implement only
this correction plus the already-red CLI/apply integration. Run Task 1–4
focused tests, all import tests, doc claims/smoke/diff, commit, and obtain fresh
specification and quality reviews.

All inputs remain synthetic; no real workbook, DB/resource/scratch/service,
push, merge, publication, or cursor action is authorized.

## Exact Next Trigger

Director reads corrected contract `657a1ba`, proves the final-plan commit RED,
implements the six-path correction, and resumes Task 4 review gates.
