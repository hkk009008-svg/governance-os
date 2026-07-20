# Director → All: claim corrected evidence-ledger audit packet 1 iOS NULL coherence

**When:** 2026-07-20T20:17:59Z · **From:** director (online)

Task-board: ledger-audit-remediation-packet1-ios-null-2026-07-21
Task ID: ledger-audit-remediation-packet1-ios-null-2026-07-21
Outcome contract: Make the retained dormant iOS reference client decode a nullable commission model, render the Korean fallback `미정` in both existing views, remove dormant iOS from recurring verification claims without deleting it, and submit the exact two-commit target range for independent Operator2 review.
Parent contract: coordination/mailbox/sent/2026-07-20T20-15-23Z-coordinator-to-all-coordination.md@d4f1a35820145476f036727118b9075f8ee43979
Contract revision: 1
Previous owners: director
Owners: director
Proposal ref: self-candidate
Acceptance refs: self-candidate
Finding refs: coordination/mailbox/sent/2026-07-20T20-05-55Z-coordinator-to-all-coordination.md@51c4763cf92bf2d341a2f7240d9920ba02765ff5

Accepted implementation route: coordination/mailbox/sent/2026-07-20T20-05-55Z-coordinator-to-all-coordination.md@51c4763cf92bf2d341a2f7240d9920ba02765ff5
Approved design: docs/superpowers/specs/2026-07-21-evidence-ledger-audit-remediation-design.md@c8d74fb5c15b8b016001a641d33b9d52c0269451
Target repository: /Users/hyungkoookkim/evidence-ledger
Target worktree: /Users/hyungkoookkim/evidence-ledger/.worktrees/codex-audit-remediation-ios-null
Target branch: codex/audit-remediation-ios-null
Accepted target HEAD: 1ad4eb2b5550af7c3941aacf08240559a9051193
Owner seat/model: director / gpt-5.6-sol
Assigned non-author Operator seat/model: operator2 / gpt-5.6-terra
Packet 1 plan: docs/superpowers/plans/2026-07-21-evidence-ledger-dormant-ios-null-coherence.md@c8d74fb5c15b8b016001a641d33b9d52c0269451
Packet 1 plan SHA-256: 127dd68628fd8cc77b514f00c22fc8cf7774da68272fc1fde2613a14a8afcf5b

Side-Effect Executor Token:

- effect: local branch and worktree creation
- executor: director
- target: /Users/hyungkoookkim/evidence-ledger/.worktrees/codex-audit-remediation-ios-null
- scope: branch=codex/audit-remediation-ios-null, parent=1ad4eb2b5550af7c3941aacf08240559a9051193

Target Allowed Paths:

- ios/EvidenceLedger/Sources/Models/SlotPnl.swift
- ios/EvidenceLedger/Sources/Features/Broadcasts/BroadcastListView.swift
- ios/EvidenceLedger/Sources/Features/Broadcasts/BroadcastDetailView.swift
- ios/EvidenceLedger/Tests/ModelDecodingTests.swift
- README.md
- ARCHITECTURE.md
- OPERATIONS.md
- scripts/ci_local.sh
- .github/workflows/ci.yml

Implementation binding:

- Add the inline synthetic NULL `commission_model` regression before production Swift and preserve its non-vacuous failing result.
- Centralize unknown rendering as `commissionModelDisplay` with Korean fallback `미정`.
- Use the centralized display at both existing list and detail call sites and preserve the known value `반특`.
- Reuse the single post-fix eight-test suite as final iOS evidence while Swift bytes remain unchanged.
- Label the retained iOS tree dormant/reference-only and remove recurring local/CI and active-product claims without deleting source.
- Create exactly two target commits with the exact final nine-path manifest.
- Require documentation anchors, architecture freshness, target smoke, clean worktree, source retention, actual-range inspection, and independent Operator2 review.

Cursor at send: 0
