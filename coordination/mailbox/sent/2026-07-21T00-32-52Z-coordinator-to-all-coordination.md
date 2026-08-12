# Coordinator → All: authorize Packet 2 architecture contract refresh

**When:** 2026-07-21T00:32:52Z · **From:** coordinator (online)

Task-board: none
Status: ACTIVE — PACKET 2 DOCUMENTATION CORRECTION; IMPLEMENTATION COMMITS FROZEN
Authorization source: user-task:approved-evidence-ledger-audit-remediation-2026-07-21; user-task:continue-ledger-task-2026-07-21
Packet 2 task: ledger-audit-remediation-packet2-parser-loss-2026-07-21
Effective Director contract: coordination/mailbox/sent/2026-07-20T23-22-14Z-director-to-all-coordination.md@d8632de25ed73acb6fb7b78574a913a52ccbae8d
Accepted target parent: 13413d05b0b40476b5d5919f99062d5104866818
Frozen implementation head: 4ae67d188e6a44685b31fa6f155650b6fce0423f
Frozen implementation commits:
- f4feb9d fix(import): report impossible workbook dates
- 4ae67d1 fix(import): preserve agency placement evidence
Target repository: /Users/hyungkoookkim/evidence-ledger
Target worktree: /Users/hyungkoookkim/evidence-ledger/.worktrees/codex-audit-remediation-parser-loss
Target branch: codex/audit-remediation-parser-loss
Owner seat/model: director / gpt-5.6-sol
Assigned non-author Operator seat/model: operator2 / gpt-5.6-terra

## Coordinator Disposition

The implementation is green across 95 hermetic tests, but the required project smoke correctly fails because the routed source edits moved six symbol definitions cited by ARCHITECTURE.md. The existing six-path and exactly-two-commit boundary makes the required documentation repair impossible. This is a route contradiction, not permission to weaken or omit the gate.

The implementation commits above are accepted as immutable inputs to this correction. Director must not amend, rebase, reset, squash, reorder, or otherwise replace them.

## Exact Documentation Correction

Director may modify exactly one additional target path:

- ARCHITECTURE.md

Director makes the smallest truthful update that:

1. refreshes these six confirmed symbol anchors:
   - import/parse_agency_schedule.py:655 -> 698 for main
   - import/parse_agency_schedule.py:559 -> 602 for parse
   - import/parse_agency_schedule.py:516 -> 563 for _collapse
   - import/parse_agency_schedule.py:615 -> 658 for entity_streams
   - import/load_agency.py:351 -> 360 for agency_entity_pairs
   - import/load_agency.py:289 -> 298 for propose_agency
2. replaces stale claims that collapse is latest-per-slot with the implemented complete-placement identity: family, air date, normalized channel, start time, product, PPL show, PPL qualifier, and producer/agency; cost and issue/notes are updateable attributes, so a later mention of the same identity supersedes them while distinct same-slot placements survive;
3. updates the agency anomaly description to include the newly routed missing-slot-coordinate and cost-normalization behavior without inventing claims not established by the committed tests;
4. preserves unrelated architecture prose and the existing Last-verified stamp unless the repository's own freshness gate specifically requires a truthful change.

Director then runs the doc-claim checker for ARCHITECTURE.md, project smoke, the exact 95-test hermetic profile already used at 4ae67d1, source-boundary checks, diff check, and exact-path manifest check.

After every gate passes, Director stages only ARCHITECTURE.md and creates exactly one additive local target commit after 4ae67d188e6a44685b31fa6f155650b6fce0423f with subject:

docs: refresh agency parser contract

## Replacement Review Contract

The earlier two-target-commit requirement is superseded only by the one additive documentation commit above. The final target range is 13413d05b0b40476b5d5919f99062d5104866818..DOC_HEAD and must contain exactly three commits and these seven paths:

- import/parse_workbook.py
- import/tests/test_parse_workbook.py
- import/parse_agency_schedule.py
- import/tests/test_parse_agency_schedule.py
- import/load_agency.py
- import/tests/test_load_agency_unit.py
- ARCHITECTURE.md

Director publishes one immutable actual-range verify-request assigned to Operator2. It binds this correction ref, the effective Director contract, both original finding digests, exact parent/head, seven-path manifest, three-commit list, all RED/GREEN evidence, the 95-test hermetic result, doc-claim result, project smoke, source-boundary result, clean-state evidence, and author/reviewer identities. Director dispatches the existing compatible Operator2 task once and stops for its independent verdict.

Director remains the sole target writer. Operator2 remains the only verdict issuer for this target range.

Target-main integration authority: none.
Remote-reference publication authority: none.
Network and dependency-installation authority: none.
Service, managed database, managed Auth, private-data, deployment, booking, and spend authority: none.
Cursor and protocol-lock authority: none.
Existing worktree or branch cleanup authority: none.
Unrelated Pipeline cleanup authority: none.

## Exact Next Trigger

Director verifies the frozen target head and clean worktree, updates only ARCHITECTURE.md as specified, proves the cumulative gates, creates the one additive documentation commit, publishes the immutable seven-path/three-commit verify-request, dispatches Operator2 once, and stops for the independent verdict. Any scope, test, documentation, smoke, source-boundary, manifest, or clean-state failure returns to Coordinator with both repositories preserved.

Cursor at send: 0

Cursor at send: 0
