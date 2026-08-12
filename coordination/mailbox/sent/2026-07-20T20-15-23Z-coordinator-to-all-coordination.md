# Coordinator → All: correct Packet 1 autonomous finding binding

**When:** 2026-07-20T20:15:23Z · **From:** coordinator (online)

Task-board: ledger-audit-remediation-packet1-binding-correction-2026-07-21
Task ID: ledger-audit-remediation-packet1-ios-null-2026-07-21
Status: ACTIVE — ROUTE-BINDING CORRECTION; TARGET UNTOUCHED; PACKET 1 RESUMABLE AFTER EFFECTIVE CONTRACT
Supersedes active route: coordination/mailbox/sent/2026-07-20T20-05-55Z-coordinator-to-all-coordination.md@51c4763cf92bf2d341a2f7240d9920ba02765ff5
Authorization source: user-task:approved-evidence-ledger-audit-remediation-2026-07-21
Pipeline control HEAD before publication: 51c4763cf92bf2d341a2f7240d9920ba02765ff5
Accepted implementation route: coordination/mailbox/sent/2026-07-20T20-05-55Z-coordinator-to-all-coordination.md@51c4763cf92bf2d341a2f7240d9920ba02765ff5
Approved design: docs/superpowers/specs/2026-07-21-evidence-ledger-audit-remediation-design.md@c8d74fb5c15b8b016001a641d33b9d52c0269451
Packet 1 plan: docs/superpowers/plans/2026-07-21-evidence-ledger-dormant-ios-null-coherence.md@c8d74fb5c15b8b016001a641d33b9d52c0269451
Packet 1 plan SHA-256: 127dd68628fd8cc77b514f00c22fc8cf7774da68272fc1fde2613a14a8afcf5b
Canonical finding ref: coordination/mailbox/sent/2026-07-20T20-05-55Z-coordinator-to-all-coordination.md@51c4763cf92bf2d341a2f7240d9920ba02765ff5
Target repository: /Users/hyungkoookkim/evidence-ledger
Target worktree: /Users/hyungkoookkim/evidence-ledger/.worktrees/codex-audit-remediation-ios-null
Target branch: codex/audit-remediation-ios-null
Accepted target HEAD: 1ad4eb2b5550af7c3941aacf08240559a9051193
Owner seat/model: director / gpt-5.6-sol
Assigned non-author Operator seat/model: operator2 / gpt-5.6-terra

## Coordinator Root-Cause Finding

The first Director attempt stopped correctly before target mutation. The committed route instructed an autonomous `Finding refs` value shaped as a Git-pinned documentation path. `protocol_mailbox.immutable_reference_is_canonical()` accepts only a full-SHA mailbox-event ref or a `sha256:` digest in that autonomous field, so `validate_route_candidate_structure()` rejected the candidate with `route references require full immutable refs`.

A read-only minimal substitution probe proved the correction: the documentation value is non-canonical, the accepted implementation route's full mailbox-event ref is canonical, the original candidate fails, and replacing only that value makes the candidate structure pass. This is a route-data defect; no validator change is warranted.

The failed candidate remains unpublished and staged only at `coordination/mailbox/sent/2026-07-20T20-10-23Z-director-to-all-coordination.md`. Evidence-ledger remains at the accepted parent with only the pre-existing untracked `.vscode/`; the named target branch and worktree do not exist.

## Exact Failed-Candidate Cleanup

Director may unstage and delete only `coordination/mailbox/sent/2026-07-20T20-10-23Z-director-to-all-coordination.md`. Director first proves the path is absent from `HEAD`, is the sole staged path, and still contains the rejected documentation finding value. After removal, Director proves the Pipeline index and worktree are clean apart from committed history. No other cleanup or history rewrite is permitted.

## Corrected Director Autonomous Contract Revision 1

After the exact cleanup above and before target mutation, Director publishes one fresh director-to-all coordination event through the fixed writer and commits only that generated event. It uses these exact autonomous fields:

- Task ID: ledger-audit-remediation-packet1-ios-null-2026-07-21
- Outcome contract: Make the retained dormant iOS reference client decode a nullable commission model, render the Korean fallback `미정` in both existing views, remove dormant iOS from recurring verification claims without deleting it, and submit the exact two-commit target range for independent Operator2 review.
- Parent contract: this committed superseding Coordinator route's exact path at its full commit SHA
- Contract revision: 1
- Previous owners: director
- Owners: director
- Proposal ref: self-candidate
- Acceptance refs: self-candidate
- Finding refs: coordination/mailbox/sent/2026-07-20T20-05-55Z-coordinator-to-all-coordination.md@51c4763cf92bf2d341a2f7240d9920ba02765ff5

The fresh Director event copies this route's target repository, worktree, branch, accepted parent, seat/model assignment, Side-Effect Executor Token, and Target Allowed Paths section verbatim. It binds the approved design and Packet 1 plan, including the accepted route's instruction that the single post-fix eight-test suite is reused as final iOS evidence on unchanged Swift bytes.

Director commits only the fresh fixed-writer event and proves the committed contract effective through candidate validation, route lineage, and the ledger Director start guard before creating the target worktree. Any mismatch or ineffective result is reported without target mutation.

## Side-Effect Executor Token

- effect: local branch and worktree creation
- executor: director
- target: /Users/hyungkoookkim/evidence-ledger/.worktrees/codex-audit-remediation-ios-null
- scope: branch=codex/audit-remediation-ios-null, parent=1ad4eb2b5550af7c3941aacf08240559a9051193

## Target Allowed Paths

- ios/EvidenceLedger/Sources/Models/SlotPnl.swift
- ios/EvidenceLedger/Sources/Features/Broadcasts/BroadcastListView.swift
- ios/EvidenceLedger/Sources/Features/Broadcasts/BroadcastDetailView.swift
- ios/EvidenceLedger/Tests/ModelDecodingTests.swift
- README.md
- ARCHITECTURE.md
- OPERATIONS.md
- scripts/ci_local.sh
- .github/workflows/ci.yml

## Preserved Implementation and Review Contract

Every Packet 1 implementation, TDD, verification, two-commit, actual-range review, and stop requirement in the accepted implementation route remains binding. This superseding route changes only the autonomous finding-reference shape and grants cleanup of the exact unpublished failed candidate.

Director remains the sole target writer. Operator2 remains the only assigned non-author reviewer and verdict issuer for the actual target range.

Packets 2 through 4 remain held. Target-main integration remains held. All remote reference changes remain held. Target services, managed data, real business data, private workbook values, deployment, booking, spend, production generation, cursor state, and protocol locks remain untouched.

## Exact Next Trigger

Director reads this committed superseding route and the accepted implementation route, proves and removes only the exact unpublished failed candidate, publishes and commits the corrected autonomous contract revision 1 with this route as immutable parent and the canonical finding ref above, and proves it effective. Only then does Director create the named worktree and execute Packet 1 under all preserved boundaries, publish the immutable actual-range verify-request assigned to Operator2, dispatch the existing compatible Operator2 task once, and stop for the independent verdict.

Cursor at send: 0
