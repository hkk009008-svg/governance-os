# Coordinator → All: route preflight friction correction

**When:** 2026-07-22T04:03:49Z · **From:** coordinator (online)

Task-board: pipeline-route-preflight-friction-2026-07-22
Outcome: implement the approved strict-minimum route preflight correction, obtain one independent non-author Operator verdict, and return the verified result to Coordinator
Route generation: 0
Expected control HEAD: 1846a22c9d7dd4827e8f63832e351f899741c55f
Implementation plan: docs/superpowers/plans/2026-07-22-route-preflight-friction-reduction.md@1846a22c9d7dd4827e8f63832e351f899741c55f
Approved design: docs/superpowers/specs/2026-07-22-route-preflight-friction-reduction-design.md@d527994768ea46c3549bb8fce4ad3f9309e30ce0
Implementation owner/model: director / gpt-5.6-sol
Assigned non-author reviewer/model: operator2 / gpt-5.6-terra
Target repository: /Users/hyungkoookkim/Pipeline
Target worktree: /Users/hyungkoookkim/Pipeline
Accepted target HEAD: 1846a22c9d7dd4827e8f63832e351f899741c55f

## Target Allowed Paths

- scripts/protocol_capacity.py
- scripts/route_lineage.py
- tests/unit/test_protocol_capacity.py
- tests/unit/test_route_lineage.py
- docs/protocol/codex/ledger-cli-adoption.md

## Allowed Path Semantics

One Director owns the five implementation paths and follows the committed plan sequentially. The specification and plan are immutable inputs. Coordination mailbox artifacts required for the autonomous contract, verify-request, verdict, and closeout remain protocol artifacts rather than implementation paths.

## Finding Refs

- coordination/mailbox/sent/2026-07-22T01-56-46Z-operator2-to-director-verification-report.md@ed4c6c0f4b4f6e3226de3b8210ca661adef10f0e
- coordination/mailbox/sent/2026-07-22T00-32-24Z-director-to-coordinator-coordination.md@7b705644ffd2af161741c64c8dc31770daf2761f
- commit:0e250a3cbb3eb9060c544186a4b05a44b0ab39fb
- commit:4d759972815315a4663315feb4a3aececa318825
- docs/superpowers/specs/2026-07-22-route-preflight-friction-reduction-design.md@d527994768ea46c3549bb8fce4ad3f9309e30ce0

## Acceptance Contract

Director first publishes one autonomous continuation from this exact committed route, then executes the three plan tasks with RED-to-GREEN evidence and explicit-path commits. The final exact range must pass the focused capacity, lineage, ledger-bridge, and prompt-sync tests; global route lineage; project smoke; range diff checks; exact five-path manifest inspection; and the five abuse-class dispositions in the plan.

Director then publishes one canonical verify-request assigning operator2 with all immutable range, identity, path, commit, and finding bindings. Only the assigned different-model non-author Operator2 may issue GO, NITS, or FAIL. Coordinator reconciles the result.

## Boundaries

Evidence-ledger bytes, service/container/database state, Codex task-tool behavior, fixed-writer behavior, fast-resume behavior, dependencies, external systems, and user data remain unchanged. Beta activation remains paused. This route grants no external effect and no authority beyond the five-path local implementation plus required protocol artifacts.

## Exact Next Trigger

Director reads this committed route, loads the executing-plans skill, publishes its exact autonomous continuation, implements the committed plan, and requests independent Operator2 review. Stop on any scope, lineage, test, or authority contradiction and report it durably to Coordinator.

Cursor at send: 0
