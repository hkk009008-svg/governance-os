# Operator → All: Lane V FAIL commit 48ca2a8 side-effect executor token

**When:** 2026-07-08T02:24:17Z · **From:** operator (online)

VERDICT: FAIL

Packet: `operator-unit-coherence-side-effect-token-verification`
Target commit: `48ca2a8 feat(protocol): require side-effect executor token`
Commit range verified: `02efcef..48ca2a8`
Verify request: `coordination/mailbox/sent/2026-07-08T02-13-31Z-director-to-operator-verify-request.md`
Route event: `coordination/mailbox/sent/2026-07-08T01-58-03Z-coordinator-to-all-coordination.md`

Subagent utilization decision: dispatched two read-only `lane-v-verifier` helpers for independent spec/scope and code-quality validation. Both reported side-effect-token false negatives; the operator seat reproduced the blocking behavior with disposable route probes before issuing this verdict.

## Evidence

$ env -u GIT_INDEX_FILE .venv/bin/python .agents/skills/four-seat-protocol/scripts/seat_status.py operator --wave 2
-> HEAD `0e418a7`; operator unread `0 / ref-bus`; Wave 2 gate `MET`.

$ env -u GIT_INDEX_FILE git diff --name-status 02efcef..48ca2a8
-> 12 changed files: `scripts/protocol_capacity.py`, `scripts/codex_protocol_model.py`, Codex continuation docs, live-seat skills, Codex role prompts, and focused unit tests.

$ env -u GIT_INDEX_FILE .venv/bin/python -m pytest tests/unit/test_protocol_capacity.py::test_route_validation_rejects_shared_side_effect_without_executor_token tests/unit/test_protocol_capacity.py::test_route_validation_allows_complete_side_effect_executor_token tests/unit/test_protocol_capacity.py::test_route_validation_rejects_duplicate_side_effect_success_claims_without_common_token tests/unit/test_protocol_capacity.py::test_route_validation_rejects_delegated_subagent_side_effect_directives tests/unit/test_protocol_prompt_sync.py::test_side_effect_executor_token_contract_is_model_backed_and_documented -q
-> `7 passed in 0.06s`.

$ env -u GIT_INDEX_FILE .venv/bin/python -m pytest tests/unit/test_protocol_capacity.py tests/unit/test_protocol_prompt_sync.py -q
-> `20 passed, 6 xfailed in 0.14s` after strict xfail pins were added for the deferred defects.

$ env -u GIT_INDEX_FILE .venv/bin/python -m pytest tests/unit/test_protocol_capacity.py::test_route_validation_requires_token_for_modal_side_effect_language tests/unit/test_protocol_capacity.py::test_route_validation_rejects_multi_executor_token tests/unit/test_protocol_capacity.py::test_route_validation_rejects_token_for_different_side_effect_target tests/unit/test_protocol_prompt_sync.py::test_side_effect_executor_token_detailed_contract_is_surface_synced --runxfail -q
-> RED as required for non-vacuous pins: `6 failed in 0.04s`; failures show route issues are empty for `Director may push`, `Director pushes`, `Director claims lock`, multi-executor token, wrong-target token, and missing detailed contract text on compact surfaces.

$ env -u GIT_INDEX_FILE .venv/bin/python -m pytest tests/unit/test_imports_smoke.py tests/unit/test_protocol_mailbox.py tests/unit/test_status.py tests/unit/test_coordination_tooling.py tests/unit/test_ceremony_gates.py tests/unit/test_protocol_capacity.py tests/unit/test_protocol_prompt_sync.py tests/unit/test_codex_ledger_bridge.py -q
-> `75 passed, 6 xfailed in 1.91s`.

$ env -u GIT_INDEX_FILE .venv/bin/python scripts/protocol_capacity_board.py --wave 2 --validate-route coordination/mailbox/sent/2026-07-08T01-58-03Z-coordinator-to-all-coordination.md
-> `route valid: true`; `BLOCKING ISSUES - none`.

$ env -u GIT_INDEX_FILE .venv/bin/python scripts/ci_smoke.py
-> final `OK`; existing warning remains `215 stale commit-SHA ref(s) in docs`.

$ env -u GIT_INDEX_FILE git diff --check
-> no output.

## Findings

1. CRITICAL — `scripts/protocol_capacity.py:1051` / `scripts/protocol_capacity.py:115` — shared side-effect detection only checks side-effect patterns after `SIDE_EFFECT_DIRECTIVE_RE` matches; the directive regex omits common route wording such as `may push`, `pushes`, and `claims lock`. Disposable validation reproduced empty `route_issues` for all three forms even though the route contract requires a side-effect executor token before shared mutation. — FAIL.

2. CRITICAL — `scripts/protocol_capacity.py:1003` — token sufficiency checks only that some complete token exists, not that it names exactly one executor or matches the routed side-effect target/command class. Disposable validation reproduced empty `route_issues` for `executor: director, operator` and for a lock-claim token satisfying a route that authorizes a push to `origin/main`. This conflicts with `scripts/codex_protocol_model.py:319` and the route's single-executor contract. — FAIL.

3. IMPORTANT — `tests/unit/test_protocol_capacity.py:245` / `tests/unit/test_protocol_capacity.py:281` / `tests/unit/test_protocol_capacity.py:319` — strict xfail pins now record the unfixed route-validator false negatives and go RED under `--runxfail`, so CI re-verifies the deferred defect instead of relying on this report. — pinned.

4. IMPORTANT — `tests/unit/test_protocol_prompt_sync.py:197` — strict xfail pin now records that compact role/docs surfaces do not carry the detailed model contract for exact executor selection, covered side effects, duplicate success claims, and observer contradiction-only reporting. It goes RED under `--runxfail`. — pinned.

## Scope-Match

The landed diff is in the coordinator-routed scope, but it does not satisfy the route's required implementation behavior for missing executor tokens and same-target side-effect control. No push, cursor consume, lock action, paid API spend, pod spend, evidence-ledger product edit, or production generation was performed.

## Exact Next Trigger

`continue as director` to fix the side-effect executor token validator and prompt/model sync defects, then send a fresh verify-request to operator for re-verification of the nit-fix/new commit.

Cursor at send: 0
