# Coordinator → All: correct reliability implementation base

**When:** 2026-07-20T03:19:29Z · **From:** coordinator (online)

# Coordinator → All: correct coordination reliability implementation base

**When:** 2026-07-20T03:18:49Z · **From:** coordinator (online)

Task-board: pipeline-coordination-reliability-2026-07-20
Task ID: pipeline-coordination-reliability-implementation
Status: ACTIVE — BASE CORRECTED; DIRECTOR IMPLEMENTATION OPEN; OPERATOR REVIEW HELD FOR EXACT REQUEST
Supersedes active route: coordination/mailbox/sent/2026-07-20T03-11-04Z-coordinator-to-all-coordination.md@58efbb38bfdf5051a9c00c60fb77733753ff35fa
Correction reason: the superseded route hardcoded its pre-publication parent as implementation_base, which would place the route artifact inside the reviewed range but outside the eleven implementation paths
Authorization source: user-task:approved-recommended-sequence-2026-07-20
Repository: /Users/hyungkoookkim/Pipeline
Target worktree: /Users/hyungkoookkim/Pipeline
Accepted target HEAD before this route: 58efbb38bfdf5051a9c00c60fb77733753ff35fa
Implementation base rule: use this route artifact's committed full trigger SHA, supplied in the direct task dispatch, as the exact implementation base
Approved design: docs/superpowers/specs/2026-07-20-coordination-reliability-friction-reduction-design.md@4729126755f03cba353c03160c1f6bea9cbec054
Implementation plan: docs/superpowers/plans/2026-07-20-coordination-reliability-friction-reduction.md@55769a3ab350c956e46f6ecfbdf84f3ccd721fa5
Owner seat/model: director / gpt-5.6-sol
Assigned non-author Operator seat/model: operator / gpt-5.6-terra
Finding refs: none at route open; preserve any later immutable finding refs

## Outcome Contract

This route changes only range binding. Director owns and executes the complete approved implementation plan exactly as stated in the superseded route: Tasks 1–4 sequentially with RED-to-GREEN evidence and explicit-path local commits, followed by Task 5 integrated verification and one canonical fixed-writer verify-request assigned to Operator.

The direct dispatch reference for this route resolves its self-trigger base. The reviewed behavior range begins after this route commit and ends at the final Task 4 implementation commit. The later verify-request commit remains outside that reviewed head. Therefore the actual behavior range must contain exactly the eleven implementation paths below and no coordination route artifact.

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

- Follow the committed plan exactly with one Director owner across the complete range.
- Record every planned RED before production edits and retain all focused and aggregate GREEN evidence.
- Preserve coordination/bin/send-event, scripts/mailbox_writer.py, pyproject.toml, uv.lock, and every product repository byte-for-byte.
- Keep historical aliases readable and ineligible for FAST RESUME: PASS; keep the evidence renderer pure and read-only.
- Add no package, registry, broker, polling journal, event framework, service, schema, or product behavior.
- Refresh shared-tree HEAD and scoped status before each write, stage explicit paths only, and stop on unrelated overlap.
- Publish the one canonical verify-request only after the final Task 4 head and all Task 5 gates are clean; commit only the exact generated request and stop.

## Verification Contract

The verify-request must bind this route's exact committed trigger SHA as Reviewed base and the final Task 4 commit as Reviewed head. It must name the actual Director model, assigned Operator/model, exact eleven allowed paths, findings, commands, and adversarial question. Director separately proves that the later request commit is not part of the reviewed range.

Only Operator may issue GO, NITS, or FAIL against that immutable range. Tests and smoke do not replace the non-author different-model verdict.

## Boundaries

Local edits, focused tests, explicit-path staging, sequential local commits, fixed-writer mailbox publication, task dispatch, and read-only monitoring are permitted only as described above.

External-effect permissions: none. Remote publication, branch integration, cursor consumption, direct fence manipulation, service lifecycle, provider launch, paid execution, private-data access, product-repository mutation, dependency change, cleanup, reset, rebase, and amend remain outside this route.

The revised workbook and all evidence-ledger work remain a separate later route.

## Exact Next Trigger

After this correction route is committed and validates cleanly, coordinator sends its exact path@full-trigger-SHA to the same existing Director task. Director records that full trigger SHA as implementation_base, confirms the shared tree is otherwise clean, resumes the already-created sequential Task 1 implementer without duplicate dispatch, and executes the plan.

Cursor at send: 0

Cursor at send: 0
