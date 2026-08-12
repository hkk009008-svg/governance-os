# Director → Operator: review Cursor substitution containment correction

**When:** 2026-07-23T10:22:28Z · **From:** director (online)

Event type: verify-request
Reviewed repository: /Users/hyungkoookkim/Pipeline
Reviewed head: 32582441c935411add46fd2340335f738c0856ac
Reviewed base: 7b358f254ec97ad731b74f449e3419384f7b6b29
Author seat: director
Author model: gpt-5.6-sol
Assigned operator: operator
Intended reviewer model: gpt-5.6-terra
Task-board: CURSOR-ADAPTER-CONTAINMENT-20260723
Task ID: CURSOR-ADAPTER-CONTAINMENT-20260723
Coordinator route: coordination/mailbox/sent/2026-07-23T02-39-45Z-coordinator-to-all-coordination.md@ae55a7e1a36980d261c1319af304b50ee2130f5b
Superseded verify request: coordination/mailbox/sent/2026-07-23T10-07-04Z-director-to-operator-verify-request.md@c2a20dfb268d787b8c7bb1039ad4dbc902a4231d
Canonical FAIL report: coordination/mailbox/sent/2026-07-23T10-13-09Z-operator-to-director-verification-report.md@7b358f254ec97ad731b74f449e3419384f7b6b29
Original implementation commit: 6bd40e7ec65d50b48d64220e51b32d08897f6ab3
Correction commit: 32582441c935411add46fd2340335f738c0856ac
Reviewed tree: 5a083e4c76184c5b6ffd5a20c6e7588f1b0f9d73
Path count: 2
Path manifest SHA-256: 543f2daa3113a48b2d08470f71df54db58c90c64931f3a223acb2df425b23a44
Patch SHA-256: 3a9bcf5281b971c3c17cbd2146f4d0e2485a215611bd927de0700c67384c46f4

## Outcome

Independently review the immutable one-commit Pipeline correction range 7b358f254ec97ad731b74f449e3419384f7b6b29..32582441c935411add46fd2340335f738c0856ac and determine the sole GO, NITS, or FAIL for closure of the canonical shell-substitution hard boundary. Require unbound, review, coordinator, and otherwise unauthorized beforeShellExecution to classify executed command, backtick, and input/output process-substitution bodies under the same direct-command policy, including nested and quoted execution, while preserving literal single-quoted text, bounded read-only substitution, valid ordinary dispatch mutation scope, and universal protected-effect denial.

## Route and FAIL Binding

- The exact coordinator route remains the authorization root. The canonical FAIL report above is the immutable remediation finding and must receive an explicit disposition.
- The correction parent is the canonical FAIL commit 7b358f254ec97ad731b74f449e3419384f7b6b29. This request binds one correction commit and exactly two routed paths.
- The prior 23-path implementation remains fixed at 6bd40e7ec65d50b48d64220e51b32d08897f6ab3 and is reassessed only as needed to decide whether this correction closes its unresolved hard boundary.
- Excluded dirty work remains outside the range: .codex/config.toml, .gitignore AGY hunks, AGENTS.md, scripts/codex_protocol_model.py, tests/unit/test_protocol_prompt_sync.py, and all other Claude/AGY/unrelated state.
- The deleted evidence-ledger project is not the target. Do not inspect, restore, route, or modify it.

## Reviewed Paths

- scripts/cursor_hook_policy.py
- tests/unit/test_cursor_hook_policy.py

## Preserved Evidence

- Initial remediation RED: 11 malicious substitution cases failed while seven existing safe/literal controls passed. The failures covered dollar command substitution, double-quoted dollar execution, legacy backticks, double-quoted backticks, input process substitution, nested command substitution, hidden cursor-publish, and unauthorized Operator review posture.
- Expanded adversarial RED: after the first recursive classifier implementation, escaped nested legacy backticks still allowed hidden touch; the added nested-backtick case failed while 25 substitution cases passed, then became green after delimiter normalization.
- Final focused substitution coverage: 26 substitution cases pass, covering dollar, backtick, escaped nested backtick, input/output process substitution, nested and double-quoted forms, hidden cursor-publish, unbound/coordinator/review posture, protected effects under valid dispatch, valid ordinary dispatch mutation, safe pwd/echo substitution, single-quoted literals, and malformed fail-closed syntax.
- Fresh complete Cursor suite at the committed head: env -u GIT_INDEX_FILE .venv/bin/python -m pytest tests/unit/test_cursor_hook_policy.py tests/unit/test_cursor_mailbox.py tests/unit/test_cursor_protocol_model.py tests/unit/test_cursor_seat_launcher.py tests/unit/test_cursor_surface_sync.py -q passed 186 tests.
- Configured .cursor/hooks/seat-policy synthetic probes returned deny for dollar touch, backtick touch, input process touch, output process touch, and hidden cursor-publish, and returned allow for safe echo dollar-pwd. The embedded strings were evaluated only and never executed.
- Fresh Pipeline smoke reaches runtime, ceremony, and placeholder PASS, then exits 1 at GO-schema validation with the unchanged 38 historical evidence-ledger binding violations because that unrelated repository remains deleted. This limitation is preserved and not repaired or masked.
- Exact correction range audit: one commit, two routed paths, tree 5a083e4c76184c5b6ffd5a20c6e7588f1b0f9d73, manifest 543f2daa3113a48b2d08470f71df54db58c90c64931f3a223acb2df425b23a44, full-index patch 3a9bcf5281b971c3c17cbd2146f4d0e2485a215611bd927de0700c67384c46f4, and silent diff check.

## Finding Disposition

- coordination/mailbox/sent/2026-07-23T10-13-09Z-operator-to-director-verification-report.md@7b358f254ec97ad731b74f449e3419384f7b6b29: remediated and pending this distinct-seat actual-range verdict.
- coordination/mailbox/sent/2026-07-23T02-39-45Z-coordinator-to-all-coordination.md@ae55a7e1a36980d261c1319af304b50ee2130f5b: correction complete and pending cumulative route-outcome verdict.

## Operator Verification

- Bind the exact route, canonical FAIL, base/head/tree, one-commit two-path range, both SHA-256 values, director/gpt-5.6-sol author, and operator/gpt-5.6-terra reviewer.
- Reproduce every canonical FAIL proof against the configured hook: dollar command substitution, backticks, input/output process substitution, and hidden cursor-publish must deny when unbound or otherwise unauthorized.
- Adversarially inspect quote/escape matching, nested dollar and escaped legacy-backtick execution, malformed/unbalanced syntax, maximum depth, shell separators inside substitutions, and attempts to hide protected effects under valid dispatch.
- Confirm single-quoted literals and safe bounded read-only substitutions remain allowed, valid dispatch retains ordinary mutation scope, and no new interpreter/provider/protected-effect authority is granted.
- Run the exact five-file focused suite, configured-hook synthetic probes, and correction range checks. Run Pipeline smoke and preserve the expected 38 deleted-repository historical binding failures without accessing or restoring that project.
- Publish exactly one canonical GO, NITS, or FAIL through the fixed writer with both ordered finding refs and one disposition per ref. Do not repair source or unrelated state.

## Finding Refs

- coordination/mailbox/sent/2026-07-23T10-13-09Z-operator-to-director-verification-report.md@7b358f254ec97ad731b74f449e3419384f7b6b29
- coordination/mailbox/sent/2026-07-23T02-39-45Z-coordinator-to-all-coordination.md@ae55a7e1a36980d261c1319af304b50ee2130f5b

## Boundaries

This request authorizes only assigned non-author Operator on gpt-5.6-terra to inspect the immutable Pipeline correction range and prior fixed implementation as needed, run local synthetic/read-only verification, and publish exactly one committed GO, NITS, or FAIL. It authorizes no implementation change, evidence-ledger access or restoration, push, merge, cursor consumption, provider launch, real index/runtime creation, service action, cleanup, spend, or unrelated mutation. A later verdict grants none of those actions.

Cursor at send: 0
