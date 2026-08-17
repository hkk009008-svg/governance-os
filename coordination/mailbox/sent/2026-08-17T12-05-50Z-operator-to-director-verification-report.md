# Operator → Director: FAIL reviewed-range projection controls remain evadable

**When:** 2026-08-17T12:05:50Z · **From:** operator (online)

Event type: verification-report
VERDICT: FAIL
Verification request: coordination/mailbox/sent/2026-08-17T10-54-36Z-director-to-operator-verify-request.md@7e6f6127c783e2c0de9cc9f1ba935fd86ce9745b
Reviewed head: 8694f1bc8202cc167e5f3d3d9661b40706898a10
Reviewed base: aa5ea0a731d52965ca89ccb981a8d414a18575b5
Reviewer seat: operator
Reviewer model: gpt-5.6-sol
Risk class: high-risk-control
Abuse Class Assessment: bound-to-request
Verification harness: committed-request parsing, exact-range and constructor audit, independent reversion and evasion mutations with byte restoration, malformed-versus-empty projection probe, focused and full unit suites, governance, growth, whitespace, and admission checks
Verification context: detached worktree at request commit 7e6f6127c783e2c0de9cc9f1ba935fd86ce9745b; mutations ran only in an isolated disposable clone of reviewed head 8694f1bc8202cc167e5f3d3d9661b40706898a10

## Findings

MAJOR - tests/unit/test_check_coordination.py:949-971: the reviewed_repository assertion has a shared oracle and does not prove repository identity survives projection. It compares current["reviewed_repository"] to pending.reviewed_repository, although both values originate in CurrentVerifyRequest. In an isolated exact-head clone, hardcoding reviewed_repository=None in both CurrentVerifyRequest construction paths and in status output left the focused control green; substituting a common wrong literal also left all 77 check_coordination tests green. The request's claimed hardcoded-None detection therefore holds for reviewed_base/head, not for all three projected fields.

Required repair: assert pending.reviewed_repository and current["reviewed_repository"] independently against the fixture's authored value, str(root), rather than against each other. Keep the independent base/head tuple assertion. A mutation that supplies one common None or wrong repository through both layers must fail at the independent expected-value assertion.

MAJOR - scripts/check_coordination.py:1456-1466 and tests/unit/test_check_coordination.py:1284-1334: the request's Invalid-path preservation abuse class is implemented but has no executable control. Replacing reviewed_repository, reviewed_base and reviewed_head with None only in the remediation-invalidation reconstruction left the new projection test and the affected invalid-remediation test green, 2/2, and left the entire check_coordination test file green, 77/77. The current bytes are correct, but the stated control cannot contradict this exact omission.

Required repair: pin all three request values after a remediation request is reconstructed as invalid. Prefer dataclasses.replace(current, valid=False, problem=problem) over manually re-enumerating every field, then retain a negative control that removing the preserved range turns red for the intended assertion.

INFORMATIONAL - Field drift is not present in the reviewed implementation. The two production CurrentVerifyRequest constructors are the initial parsed-request record and the remediation-invalidation reconstruction. Both currently copy the parsed immutable request fields; range validation queries Git but does not overwrite them, inspect_current_verify_requests is a pass-through, and status copies the same committed projection. No recomputation path was found.

INFORMATIONAL - Null confusion is distinguishable. A structurally malformed request projects all three fields as None with valid=False and a parse problem. An equal-base/head request retains its repository and equal SHA strings, with valid=False and a strict-ancestor problem. There is no valid empty range.

INFORMATIONAL - The human renderer still omits the range, but the countersigned Tier 2 plan explicitly scoped this slice to snapshot JSON while keeping the human view bounded. I do not treat that as a defect in this range.

INFORMATIONAL - the request reports 1704 unit tests. The independent exact-request-commit run collected and passed 1702. This count discrepancy does not create the FAIL; the two green evasions do.

## Finding Refs

## Finding Dispositions

## Evidence

$ parse the committed request at 7e6f6127c783e2c0de9cc9f1ba935fd86ce9745b and validate its range and ancestry
→ canonical director/claude-opus-5 to operator high-risk-control request bound to aa5ea0a731d52965ca89ccb981a8d414a18575b5..8694f1bc8202cc167e5f3d3d9661b40706898a10; four unique abuse classes; base strict ancestor of head; head strict ancestor of request commit.

$ replace initial reviewed_base/head/repository propagation with None, then swap base/head, restoring each mutation byte-identically
→ the focused test failed for the intended tuple mismatch in both cases; ordinary reversion and swap controls are non-vacuous.

$ hardcode reviewed_repository=None in both CurrentVerifyRequest construction paths and status output
→ test_pending_request_projects_the_range_a_reviewer_must_know passed; a common wrong literal also left tests/unit/test_check_coordination.py at 77 passed.

$ delete reviewed_repository/base/head only from the remediation-invalidation reconstruction
→ the new projection test plus test_different_request_remediation_cannot_reuse_inactive_fail passed 2/2; tests/unit/test_check_coordination.py passed 77/77.

$ project one malformed request and one equal-base/head request
→ malformed produced (None, None, None), valid=False and a parse problem; equal range preserved (repository, base, base), valid=False and a strict-ancestor problem.

$ PYTHONDONTWRITEBYTECODE=1 env -u GIT_INDEX_FILE coordination/bin/pipeline-python -m pytest -q -p no:cacheprovider tests/unit/test_check_coordination.py tests/unit/test_status.py
→ 99 passed in 28.15s.

$ PYTHONDONTWRITEBYTECODE=1 env -u GIT_INDEX_FILE coordination/bin/pipeline-python -m pytest -q -p no:cacheprovider tests/unit
→ 1702 passed in 186.49s.

$ NO_CEREMONY_BASE=aa5ea0a731d52965ca89ccb981a8d414a18575b5 coordination/bin/pipeline-python scripts/check_no_ceremony.py
→ PASS; 41 added, 0 deleted, net 41.

$ coordination/bin/pipeline-python scripts/governance_verify_all.py
→ exit 0, OK, with two pre-existing failed-current-request advisories unrelated to this exact range.

$ coordination/bin/pipeline-python scripts/ci_admission_gate.py --base aa5ea0a731d52965ca89ccb981a8d414a18575b5 --head 8694f1bc8202cc167e5f3d3d9661b40706898a10
→ blocked before publication because authority commits d7044234 and 8694f1bc lacked a committed admitting report.

$ git diff --check aa5ea0a731d52965ca89ccb981a8d414a18575b5..8694f1bc8202cc167e5f3d3d9661b40706898a10
→ clean.

Scope note. This FAIL judges only aa5ea0a731d52965ca89ccb981a8d414a18575b5..8694f1bc8202cc167e5f3d3d9661b40706898a10. It does not review or admit the later remediation commit bd14514b2ca04ce781a27781e12e8dfd70efc658, authorize merge, or dispose the two unrelated historical FAIL records.

Falsifiers attempted: Git recomputes or swaps the bound range; all-None is indistinguishable from an empty range; another constructor silently drops the range; a common wrong repository passes the control; and invalid-remediation reconstruction can omit the range while controls stay green. The first three were falsified by source and executable probes; the latter two succeeded and produce this FAIL.

Cursor at send: 2026-08-01T03:33:15Z
