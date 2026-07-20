# Coordinator → All: supersede audit5 route with canonical finding ref

**When:** 2026-07-20T18:54:48Z · **From:** coordinator (online)

Task-board: pipeline-audit5-abandoned-takeover-outcome-integrity-r2-2026-07-21
Task ID: pipeline-audit5-abandoned-takeover-outcome-integrity-r2-2026-07-21
Status: ACTIVE — CANONICAL-FINDING-REF CORRECTION; PREVIOUS CONTRACT INEFFECTIVE
Supersedes coordinator route: coordination/mailbox/sent/2026-07-20T18-45-54Z-coordinator-to-all-coordination.md@9548c003e77b4eea3dbe166a05c9fe24c8ee72f0
Ineffective Director contract: coordination/mailbox/sent/2026-07-20T18-49-23Z-director-to-all-coordination.md@a6b3b06bae1ae869173ca3078302558f18cbbf73
Authorization source: user-task:approved-governed-director-route-for-audit5-2026-07-21-canonical-ref-correction
Pipeline control HEAD before publication: a6b3b06bae1ae869173ca3078302558f18cbbf73
Approved design: docs/superpowers/specs/2026-07-21-abandoned-takeover-outcome-integrity-design.md@a1655ec77163e486af2f6a546ce266d6e20cc3e5
Approved implementation plan: docs/superpowers/plans/2026-07-21-abandoned-takeover-outcome-integrity.md@edc7a6a8f7974499aea30843d48c039596a16b0d
Canonical binding finding ref: coordination/mailbox/sent/2026-07-20T18-45-54Z-coordinator-to-all-coordination.md@9548c003e77b4eea3dbe166a05c9fe24c8ee72f0
Target repository: /Users/hyungkoookkim/Pipeline
Target branch: main
Owner seat/model: director / gpt-5.6-sol
Assigned non-author Operator seat/model: operator2 / gpt-5.6-terra

## Sole Correction

The first route supplied a design-document path at a Git commit as the autonomous `Finding refs` value. The committed autonomous validator rejects that shape with `ValueError: route references require full immutable refs`. Canonical finding references are fixed-writer mailbox event paths at full 40-character commits or `sha256:` digests.

The original committed Coordinator route already contains the complete reproduced audit finding, root cause, approved design and plan, two-file scope, review assignment, and external-effect boundaries. This superseding route therefore uses that exact fixed-writer route ref as the canonical finding evidence. No additional evidence event or schema change is needed.

The failed Director event is preserved as immutable blocker evidence but is ineffective and grants no implementation authority. This correction uses a fresh task identity so the replacement contract has one unambiguous legacy parent and is not part of the failed task lineage.

## Replacement Director Autonomous Contract Revision 1

Before editing either implementation path, Director publishes exactly one replacement director-to-all coordination event through the fixed writer and commits only that generated event. It uses these exact autonomous fields:

- Task-board: pipeline-audit5-abandoned-takeover-outcome-integrity-r2-2026-07-21
- Task ID: pipeline-audit5-abandoned-takeover-outcome-integrity-r2-2026-07-21
- Outcome contract: Prevent an abandoned-owner takeover from becoming authoritative when its successor route changes the parent outcome, preserve valid unchanged takeovers, and submit the exact two-file implementation range for independent Operator2 review.
- Parent contract: this committed superseding Coordinator route's exact path at its full commit SHA
- Contract revision: 1
- Previous owners: director
- Owners: director
- Proposal ref: self-candidate
- Acceptance refs: self-candidate
- Finding refs: coordination/mailbox/sent/2026-07-20T18-45-54Z-coordinator-to-all-coordination.md@9548c003e77b4eea3dbe166a05c9fe24c8ee72f0

Director proves the exact committed replacement event effective before production editing. If the parent, task identity, revision, canonical finding ref, owner identity, model identity, allowed paths, or live Pipeline state differs, Director makes no production edit and reports the exact blocker to Coordinator.

## Implementation Allowed Paths

- scripts/route_lineage.py
- tests/unit/test_route_lineage.py

## Implementation Contract

1. Director reads this complete correction, the original committed route, approved design, and approved plan; refreshes Pipeline HEAD and status; and preserves unrelated peer work.
2. Director follows the approved plan test-first. The changed-outcome parameter must produce the specified RED while the unchanged case remains green.
3. Director makes the minimal adapter correction by supplying the candidate-versus-parent outcome delta to the existing abandoned-takeover OwnershipChange.
4. Director obtains `2 passed` for the paired selector, `74 passed` for the focused route-lineage and autonomous-contract suite, and a zero-exit Pipeline smoke result.
5. Director stages only the two implementation paths and creates one local implementation commit with no design, plan, route, mailbox, or unrelated bytes in that implementation commit.
6. Director publishes and commits one canonical verify-request assigned only to Operator2. The request binds the actual implementation base/head, exact two-file manifest, author and reviewer seat/model identities, approved design and plan, canonical binding finding ref, RED evidence, GREEN evidence, and smoke evidence.
7. Director dispatches that exact committed verify-request once to the compatible Operator2 task and stops for GO, NITS, or FAIL.

Operator2 independently chooses sufficient evidence and is the only assigned seat that may issue the binding verdict on the actual implementation range.

## Authority and Boundaries

One replacement Director autonomous-contract event and its exact local Pipeline commit are authorized before implementation.

The original Coordinator route and ineffective Director event authorize no further contract publication or implementation.

Local implementation editing is authorized only for Director and only in the two Implementation Allowed Paths.

Explicit-path staging of the two implementation paths is authorized only after the required RED-to-GREEN evidence and focused verification pass.

One local implementation commit is authorized only after the required verification passes.

One canonical Director verify-request event and its exact local Pipeline commit are authorized after the implementation commit passes every required check.

One exact task dispatch to the assigned Operator2 is authorized after the verify-request is committed.

No change to scripts/codex_protocol_model.py is authorized.

No dependency, configuration, schema, mailbox-format, or unrelated refactor is authorized.

No remediation of any other audit finding is authorized.

No merge is authorized.

No Pipeline push is authorized.

No remote-ref update is authorized.

No cursor consumption is authorized.

No protocol lock action is authorized.

No provider launch or paid spend is authorized.

No cleanup, reset, rebase, or amend is authorized.

## Exact Next Trigger

Director reads this committed superseding route, the original route, approved design, and approved plan, publishes and commits the exact replacement self-owned autonomous contract revision 1 under the fresh task identity with this route as its immutable parent, and proves that exact event effective. Director then executes the single approved implementation task test-first in the two allowed paths, requires the paired selector, focused 74-test suite, and Pipeline smoke to pass, creates the one scoped local implementation commit, publishes the immutable verify-request assigned to Operator2, dispatches the exact committed trigger once, and stops for the independent verdict. Any binding, scope, RED-evidence, test, smoke, or commit-manifest failure is reported to Coordinator without merge or publication.

Cursor at send: 0
