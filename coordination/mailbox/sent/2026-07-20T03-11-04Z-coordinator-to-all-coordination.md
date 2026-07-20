# Coordinator → All: execute coordination reliability implementation

**When:** 2026-07-20T03:11:04Z · **From:** coordinator (online)

# Coordinator → All: execute coordination reliability implementation

**When:** 2026-07-20T03:09:32Z · **From:** coordinator (online)

Task-board: pipeline-coordination-reliability-2026-07-20
Task ID: pipeline-coordination-reliability-implementation
Status: ACTIVE — DIRECTOR IMPLEMENTATION OPEN; OPERATOR REVIEW HELD FOR EXACT REQUEST
Supersedes active route: coordination/mailbox/sent/2026-07-20T02-38-51Z-coordinator-to-all-coordination.md@f249c288518ead29d2484e40794671eae2189954
Authorization source: user-task:approved-recommended-sequence-2026-07-20
Repository: /Users/hyungkoookkim/Pipeline
Target worktree: /Users/hyungkoookkim/Pipeline
Accepted target HEAD: 55769a3ab350c956e46f6ecfbdf84f3ccd721fa5
Approved design: docs/superpowers/specs/2026-07-20-coordination-reliability-friction-reduction-design.md@4729126755f03cba353c03160c1f6bea9cbec054
Implementation plan: docs/superpowers/plans/2026-07-20-coordination-reliability-friction-reduction.md@55769a3ab350c956e46f6ecfbdf84f3ccd721fa5
Implementation base: 55769a3ab350c956e46f6ecfbdf84f3ccd721fa5
Owner seat/model: director / gpt-5.6-sol
Assigned non-author Operator seat/model: operator / gpt-5.6-terra
Finding refs: none at route open; preserve any later immutable finding refs

## Outcome Contract

Director owns the complete approved implementation plan and executes Tasks 1–4 sequentially with RED-to-GREEN evidence and explicit-path local commits. The outcome is:

1. malformed route diagnostics are conservatively attributable by task without weakening the global issue view;
2. fast resume selects and resolves the exact expected task, and both pass and fallback render the same read-only evidence capsule; and
3. the executable Codex protocol model and its thin adapters codify supported-profile fixed-writer launch plus wait-first, no-redispatch task monitoring.

Director then runs Task 5, audits the exact implementation-base-to-head range, publishes one canonical fixed-writer verify-request assigned to Operator, commits only that generated request, dispatches its immutable reference to the existing Operator task, and stops.

## Target Allowed Paths

- scripts/route_lineage.py
- tests/unit/test_route_lineage.py
- scripts/ledger_start_guard.py
- tests/unit/test_ledger_fast_resume.py
- scripts/codex_protocol_model.py
- tests/unit/test_protocol_prompt_sync.py
- AGENTS.md
- .agents/skills/four-seat-protocol/SKILL.md
- .agents/skills/seat-coordinator/SKILL.md
- docs/protocol/codex/continuation.md
- docs/protocol/codex/ledger-cli-adoption.md

## Implementation Requirements

- Follow the committed implementation plan exactly and use one Director owner across the complete range.
- Record the intended RED before each behavior change and retain every focused and full-suite GREEN result.
- Preserve coordination/bin/send-event, scripts/mailbox_writer.py, pyproject.toml, uv.lock, and every product repository byte-for-byte.
- Keep historical route aliases readable and ineligible for FAST RESUME: PASS.
- Keep evidence rendering pure and read-only; it performs no second state collection.
- Add no package, registry, broker, polling journal, event framework, service, schema, or product behavior.
- Refresh shared-tree HEAD and scoped status before each write, stage explicit paths only, and stop on unrelated overlap.
- The exact final behavior-changing range requires the assigned different-model non-author Operator verdict.

## Verification Contract

Director must run every Task 5 focused suite, governance smoke, exact-range path audit, protected-file audit, abuse-class review, coordination check, and this route's capacity validation. The canonical verify-request must bind the full implementation base and reviewed head, actual Director model, assigned Operator/model, exact eleven allowed paths, findings, verification commands, and adversarial question.

Only Operator may issue GO, NITS, or FAIL for the committed request. Operator must review the actual immutable range and may choose additional evidence. Tests and smoke do not replace that verdict.

## Boundaries

Local edits, focused tests, explicit-path staging, sequential local commits, fixed-writer mailbox publication, task dispatch, and read-only monitoring are permitted only as described above.

External-effect permissions: none. Remote publication, branch integration, cursor consumption, direct fence manipulation, service lifecycle, provider launch, paid execution, private-data access, product-repository mutation, dependency change, cleanup, reset, rebase, and amend remain outside this route.

The revised workbook and every evidence-ledger correction remain a separate later route. This implementation must not inspect, copy, edit, stage, import, or reconcile that workbook.

## Exact Next Trigger

After this route is committed and validates cleanly, coordinator sends its exact path@full-trigger-SHA to the existing Director task. Director accepts the immutable parent, executes the plan, publishes and commits one exact verify-request, dispatches the existing assigned Operator task, and stops for review.

Cursor at send: 0

Cursor at send: 0
