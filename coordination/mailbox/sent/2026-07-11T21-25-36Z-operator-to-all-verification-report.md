# Operator → All: Task 6 cumulative Lane V FAIL — commit 276739f400c2676458f8b1936e5ac4e3200f9133

**When:** 2026-07-11T21:25:36Z · **From:** operator (online)

VERDICT: FAIL

## Findings

1. CRITICAL — `import/workbook_refresh.py:1816` — `_owner_normalized_snapshot()` rebuilds `incoming.facts` through a dictionary keyed by `fact_id`. Duplicate natural identities deliberately share a fact ID, so entering the normalization path can silently retain only one duplicate, erase the existing `duplicate-identity` blocker, and make one row executable. Preserve the fact sequence, update only targeted rows, and pin that an unrelated override cannot clear a duplicate blocker.
2. CRITICAL — `import/workbook_refresh_corrections.py:972-984` — sidecar validation parses the workbook from `path`, then reopens that path to calculate `sidecar_sha256`. The cold quality reviewer reproduced an `os.replace` race where decisions from workbook A were paired with workbook B's hash. Parse and hash one descriptor-bound byte snapshot.
3. IMPORTANT — `import/workbook_refresh_corrections.py:461-499` — `_add_validations()` constructs ranges such as `E2:E1` for a zero-row correction category. The cold quality reviewer reproduced an uncaught `openpyxl.ValueError` for a synthetic plan without conflicting-group rows. Skip empty ranges and pin every empty-category combination.

These are blocking implementation defects. No repair was attempted.

## Reviewer synthesis

- Fresh cold specification review: `PASS` at exact candidate `276739f400c2676458f8b1936e5ac4e3200f9133`. It mapped the typed inventory contract, canonical override boundary, sidecar generation/validation, blank completeness gate, automatic/manual/summary separation, and plan audit boundary to the approved design and plan.
- Fresh cold quality review: `FAIL` at the same exact candidate, with the three findings above.
- Capacity deviation: the simultaneous quality dispatch hit the four-thread cap. Pipeline commit `878bbb7af42b64b35f5fd83981acab2e5602dfa9` authorized sequential cold dispatch only. The first specification helper was interrupted as infrastructure `unable_to_verify` and excluded from evidence; a genuinely fresh replacement produced the specification PASS, followed by a distinct fresh quality reviewer.

## Scope-match

No. The landed range does not satisfy the approved fail-closed, hash-bound correction contract because duplicate blockers can be collapsed, parsed decisions can be bound to a different sidecar hash, and a valid partial inventory can crash generation.

## Evidence

$ env -u GIT_INDEX_FILE git rev-parse HEAD
→ `276739f400c2676458f8b1936e5ac4e3200f9133`

$ env -u GIT_INDEX_FILE git status --porcelain=v1 --untracked-files=all
→ no output (target clean)

$ env -u GIT_INDEX_FILE git rev-list --count d57f5384c5528d061583b5f52a99d382cf1edd97..276739f400c2676458f8b1936e5ac4e3200f9133
→ `14`

$ env -u GIT_INDEX_FILE git diff --name-only d57f5384c5528d061583b5f52a99d382cf1edd97..276739f400c2676458f8b1936e5ac4e3200f9133 | wc -l
→ `16`

$ env -u GIT_INDEX_FILE /Users/hyungkoookkim/evidence-ledger/.venv/bin/python -m pytest db/tests -q
→ `82 passed in 11.15s`

$ env -u GIT_INDEX_FILE /Users/hyungkoookkim/evidence-ledger/.venv/bin/python -m pytest import/tests -q
→ `454 passed in 23.31s`

$ env -u GIT_INDEX_FILE /Users/hyungkoookkim/evidence-ledger/.venv/bin/python -m pytest tests/unit -q
→ `85 passed in 0.61s`

$ env -u GIT_INDEX_FILE /Users/hyungkoookkim/evidence-ledger/.venv/bin/python scripts/ci_smoke.py
→ project smoke OK; ceremony, placeholder, and architecture-freshness gates PASS; final `OK`

$ shasum -a 256 .superpowers/sdd/workbook-refresh.plan.json /Users/hyungkoookkim/evidence-ledger/data/홈쇼핑분석.xlsx /Users/hyungkoookkim/Downloads/260710.xlsx /Users/hyungkoookkim/evidence-ledger/data/merges.csv .superpowers/sdd/workbook-refresh.owner-corrections.c862774.blocked.xlsx .superpowers/sdd/workbook-refresh.owner-corrections.xlsx
→ plan `8f2acb186c7b2fedafc450f8f22863a1d35fc4b7247d3da26fbcb83f6da9cac1`; previous source `50d762fd789427ce172542fabeca1584b33d6c133a3f24dfbb006a3a532a21f8`; incoming source `8184252a702d79c0f995be76e96630dd9f8f58e2d444c2532e068a09c7ebfb79`; checklist `14914f7293aee8bbe1e8cbb331c35cc54dd258b52ac601e44cb2142252f5afe5`; archived sidecar `a29a596f801599990c78b7b26fe7c81fac861f761da320444b12c93a66e37493`; remediated sidecar `e9a1d8d15d29035507f2beb4ae462de4df54a120dcec67e40d968bff46484f79`. Final rehashes were unchanged.

$ stat -f '%N|mode=%HT|links=%l|dev=%d|inode=%i|size=%z' <plan/source/checklist/sidecar paths>
→ all six inputs are distinct regular files with one hard link each.

$ env -u GIT_INDEX_FILE /Users/hyungkoookkim/evidence-ledger/.venv/bin/python - <value-suppressing structural script from the binding token>
→ `{"audit_only_cases": 12, "bindings_state": "veryHidden", "conflicting_group_decisions": 14, "conflicting_member_rows": 87, "dependent_summary_gates": 3, "missing_field_decisions": 4, "missing_month_decisions": 50, "owner_decisions": 68, "owner_inputs_all_blank": true, "sheets": ["Instructions", "Missing_Months", "Conflicting_Groups", "Missing_Fields", "Auto_Resolved", "Summary_Gates", "_Bindings"]}`

$ test ! -e .superpowers/sdd/workbook-refresh.owner-corrections.json
→ JSON absent before and after the stopped verification.

$ env -u GIT_INDEX_FILE git check-ignore -q <plan/report/archived-sidecar/remediated-sidecar/JSON paths>
→ all generated paths ignored; none tracked.

$ env -u GIT_INDEX_FILE PYTHONPATH=import /Users/hyungkoookkim/evidence-ledger/.venv/bin/python - <read-only fingerprint/evidence script>
→ `transaction_read_only=on`; database fingerprint `bc54318a5216e1cb39c1ace35cd204d12a0fab23d7496e849d7a2b4084006b96`; evidence head `8419f129c5302f05a03e134958fcf7a664499d5439e0b8a5af9513de3c135a7c`.

## Environment/token discrepancy

The token required scratch database count zero. The post-suite read-only catalog query counted PostgreSQL databases, not schemas or business rows:

$ SELECT split_part(datname, '_', 1), count(*) FROM pg_database WHERE datname ~ '^(test|load|import|agency|refresh)_[0-9a-f]{12}$' GROUP BY 1 ORDER BY 1;
→ `agency=38`, `import=12`, all other listed prefixes zero; `pg_stat_activity` showed zero active scratch connections.

$ rg -c '^def test_' import/tests/test_agency_load.py import/tests/test_import_end_to_end.py
→ agency test definitions `19`; import test definitions `6`. The observed catalog split is exactly two times those definition counts, but causality is inference, not proof.

Pipeline commit `acc61beaa4abb137ec1f397e66e616182bb1b9b5` authorized one aggregate provenance diagnostic. Its exact `pg_stat_file` query stopped with `psycopg.errors.InsufficientPrivilege: permission denied for function pg_stat_file`, so directory mtimes and current-vs-older provenance remain unverified. No cleanup was authorized or attempted. This discrepancy is separate from the three product findings and independently prevents satisfying the token postcheck.

## Exclusions and stop evidence

- The one exact real negative validation was NOT RUN. The quality-review FAIL and scratch-count discrepancy triggered the token's stop conditions before that one-shot command.
- No JSON was created; no owner field was filled or inferred.
- No generation, move, sidecar/plan/source edit, repair, scratch/dry-run/apply/activation, canonical/resource/service mutation, cursor consume, lock action, push, merge, publication, or deployment occurred.
- Regression-pin-infeasible in this verification commit: the executor token authorizes exactly one mailbox artifact and explicitly forbids product/test edits. The remediation lane must land non-vacuous regression pins with the fixes.
- There is no task lock to release.

## Exact Next Trigger

Coordinator issues a bounded remediation release for the three findings, including non-vacuous regression pins, and separately rules on the inactive scratch-database baseline. After fixes land at a new exact candidate, Coordinator sends one fresh cumulative Operator verify-request; no real-input validation proceeds before that event.

Cursor at send: 0
