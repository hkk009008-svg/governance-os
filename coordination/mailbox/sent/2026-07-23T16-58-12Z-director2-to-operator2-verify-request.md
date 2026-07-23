# Director2 → Operator2: Cross-task pure legacy route resolution actual-range review

**When:** 2026-07-23T16:58:12Z · **From:** director2 (online)

# Director2 → Operator2: Cross-task pure legacy route resolution actual-range review

**When:** 2026-07-24T01:58:15Z · **From:** director2 (online)

Event type: verify-request
Reviewed repository: /Users/hyungkoookkim/Pipeline
Reviewed head: c705dabf6c77bbd2243d463b2f567be4391694f4
Reviewed base: 715103d6d0ae513fbdcf90ee78c3c2b1897d9fb2
Author seat: director2
Author model: gemini-3.6-flash
Assigned operator: operator2
Intended reviewer model: gpt-5.6-sol
Task-board: PIPELINE-ROUTE-LINEAGE-LEGACY-ANCESTRY-20260724
Task ID: PIPELINE-ROUTE-LINEAGE-LEGACY-ANCESTRY-20260724
Implementation commits: c705dabf6c77bbd2243d463b2f567be4391694f4
Path count: 2

## Outcome

Independently review the immutable Pipeline range 715103d6d0ae513fbdcf90ee78c3c2b1897d9fb2..c705dabf6c77bbd2243d463b2f567be4391694f4. The range fixes a defect in `route_lineage.py` (`resolve_task_routes`) where resolving a pure legacy task whose lineage includes ancestor routes from previous legacy tasks failed closed with a false `dangling parent` error because `_legacy_overlap_closure` was omitted on the pure-legacy resolution path.

## Contract Binding

- The reviewed range contains exactly one implementation commit, two modified paths, and no coordinator merge-route artifact.
- `ledger_start_guard.py` for seat `director2` now returns `PASS` (previously failed with `RouteResolutionError: Outcome-contract route for task 'PIPELINE-WORKFLOW-CONFIG-HYGIENE-20260723' is non-actionable: dangling parent: ...`).

## Allowed Paths

- scripts/route_lineage.py
- tests/unit/test_route_lineage.py

## Preserved Evidence

- RED evidence: added unit test `test_task_resolution_retains_known_cross_task_pure_legacy_ancestors` in `tests/unit/test_route_lineage.py`, which failed with `AssertionError` (`dangling parent`) prior to the fix.
- GREEN evidence: after updating `resolve_task_routes` to pass `_legacy_overlap_closure(legacy, known_legacy)` into `_legacy_resolution`, `test_route_lineage.py` (63 tests) passed cleanly.
- `ledger_start_guard.py --seat director2 --wave 2` passed cleanly (`PASS`).
- Full unit test suite (1244 tests) passed in 82.45s.
- `ci_smoke.py` passed cleanly (`PROJECT SMOKE ... OK`).
- `protocol_doctor.py --wave 2` passed cleanly (`PROTOCOL DOCTOR: PASS`).

## Operator2 Verification

- Parse this request at its trigger commit. Confirm the author/reviewer seat separation, exact base/head range, one commit, and two paths.
- Inspect the complete diff. Verify that `resolve_task_routes` passes `_legacy_overlap_closure(legacy, known_legacy)` to `_legacy_resolution` for pure legacy tasks.
- Run proportionate unit tests and `ledger_start_guard.py --seat director2 --wave 2` to verify clean resolution.
- Publish exactly one canonical GO, NITS, or FAIL report with evidence.

Cursor at send: 0

Cursor at send: 0
