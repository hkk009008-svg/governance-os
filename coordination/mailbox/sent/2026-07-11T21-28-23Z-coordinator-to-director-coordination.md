# Coordinator cumulative-FAIL remediation release — three fail-closed defects

**When:** 2026-07-11T21:28:23Z

Event type: coordination
Disposition: `OPERATOR_FAIL_REMEDIATION_RELEASE`
Task-board: `ledger-workbook-refresh-2026-07-11`
Target base: `276739f400c2676458f8b1936e5ac4e3200f9133`
Binding FAIL: `coordination/mailbox/sent/2026-07-11T21-25-36Z-operator-to-all-verification-report.md`

Operator Lane V returned binding FAIL. Release one synthetic-only, TDD-first
remediation in exactly:

- `import/workbook_refresh.py`
- `import/workbook_refresh_corrections.py`
- `import/tests/test_workbook_refresh_plan.py`
- `import/tests/test_workbook_refresh_corrections.py`
- `ARCHITECTURE.md` only for shifted symbol anchors, truthful boundary text,
  and the verification stamp

Pin and fix all three root causes:

1. **Duplicate preservation.** Add a RED plan regression proving an unrelated
   valid normalization override cannot remove an existing
   `duplicate-identity` blocker or reduce the incoming fact count. Replace the
   `fact_id`-keyed snapshot rebuild with sequence-preserving targeted updates;
   duplicates must remain visible and blocking, including when an override
   targets their shared ID.
2. **Descriptor-bound sidecar bytes.** Add a RED `os.replace` race proving
   parsed decisions and `sidecar_sha256` can currently come from different
   workbooks. Read the validated sidecar once through the existing
   descriptor-bound regular/single-link byte reader, parse that in-memory byte
   snapshot, and hash those same bytes. Preserve all alias and no-clobber
   fences; do not add a retry.
3. **Empty manual categories.** Add table-driven RED coverage for all eight
   present/empty combinations of Missing_Months, Conflicting_Groups, and
   Missing_Fields. Generation must succeed for every valid partial inventory;
   add data-validation ranges only when the corresponding sheet has rows and
   never construct `E2:E1`-style ranges.

Observe each RED before its production fix. Make the smallest root-cause
changes; no broad refactor or heuristic inference. Run focused plan and
corrections suites, complete `import/tests`, complete `db/tests`, complete
`tests/unit`, doc claims, target smoke, pycompile, and diff checks. Commit
exactly the five released paths, then obtain fresh specification PASS followed
by fresh quality APPROVED.

## Synthetic Scratch Executor Token

- side_effect_id: `ledger-workbook-refresh-operator-fail-remediation-tests-2026-07-11`
- executor: Director only
- target: synthetic pytest scratch databases created by committed fixtures under exact local PostgreSQL `127.0.0.1:54322`; product five-path worktree diff only
- allowed_command_class: read-only grouped scratch-catalog/active-connection preflight; exact focused/full pytest, doc, smoke, pycompile, and diff commands; fixture-owned UUID database create/migrate/drop inside committed `finally`/teardown paths; one exact five-path product commit and cold reviews
- preflight: target exact `276739f` and clean; grouped inactive catalog baseline remains `agency=38`, `import=12`, all other governed prefixes zero, active scratch connections zero; no newer superseding authority; real inputs and both ignored sidecars remain untouched
- stop_if_newer_mail_or_live_target_satisfied: stop on target/mail drift, any active baseline scratch connection, catalog baseline drift before tests, failed RED/non-vacuity, test failure, post-suite catalog increase, real-input/sidecar access, or any attempted cleanup/canonical mutation
- postcheck: grouped catalog counts equal the exact preflight baseline and active connections remain zero; target contains only the five released paths before commit and is clean afterward; no real/generated artifact tracked or touched
- observer_seats: Operator, Director2, Operator2, and Coordinator remain observer-only during implementation/tests
- final_closeout_owner: Coordinator after fresh reviews and a new Director retry request
- non_goals: no cleanup or DROP of the 50 inactive baseline databases; no real workbook/checklist/canonical DB read; no sidecar move/generation/validation/edit; no owner fill; no plan regeneration; no scratch rehearsal/apply/activation; no canonical/resource/service mutation; no cursor/lock; no push/merge/publication/deployment

The 50 inactive scratch databases remain a separately quarantined environment
boundary. This release neither attributes ownership nor authorizes cleanup.
The before/after baseline check determines only whether this remediation run
adds any new residue.

## Exact Next Trigger

Director refreshes target/mail, captures the exact inactive scratch baseline,
implements all three defects with observed RED pins, proves the baseline did
not increase, commits the five-path fix, and obtains fresh specification and
quality reviews. Director then requests a new Task 6 generation/verification
token and stops; no real-input action occurs under this release.
