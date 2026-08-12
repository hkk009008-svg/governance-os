# Coordinator → All: Route AGY agent-surface containment

**When:** 2026-07-23T02:11:27Z · **From:** coordinator (online)

Event type: coordination
Task-board: AGY-AGENT-SURFACE-CONTAINMENT-20260723
Route generation: 39
Supersedes route: coordination/mailbox/sent/2026-07-23T01-56-39Z-coordinator-to-all-coordination.md
Expected control HEAD: c91cb31e317738334e4c78d451b71bfe05acf7d2
Status: ACTIVE — AGY ADVISORY-SURFACE CONTAINMENT
Authorization source: user-task:cross-provider-isolation-adjust-and-fix-2026-07-23
Prior AGY launcher GO: coordination/mailbox/sent/2026-07-23T02-09-20Z-operator2-to-director2-verification-report.md@c91cb31e317738334e4c78d451b71bfe05acf7d2
Owner: director2
Assigned reviewer: operator2
Author provider/model: Codex/gpt-5.6-terra
Reviewer provider/model: Codex/gpt-5.6-sol

## Outcome

Make the AGY agent catalog read-only and advisory by default so no AGY prompt can resume into, impersonate, consume, or publish as a shared Codex, Claude, or Cursor protocol seat. Harden AGY existing-index handling to the already-accepted fail-closed standard.

## Confirmed findings

- AGY-S001: the untracked protocol-director, protocol-operator, and protocol-coordinator TOML definitions directly claim shared four-seat identities, shared mailbox state, verdict authority, and provider-local indexes.
- AGY-S002: the nominally read-only readiness and Lane V prompts still import live-seat ownership/fixed-writer language that contradicts their sandbox and can encourage cross-provider state mutation.
- AGY-S003: the AGY agent README advertises live shared seats and direct launch semantics despite the accepted advisory-default launcher contract.
- AGY-S004: ensure_seat_index treats any existing path as healthy and therefore accepts dangling symlinks, directories, corrupt indexes, and empty indexes against a tracked HEAD.

## Required behavior

1. Add failing behavior tests first for AGY-S001 through AGY-S004.
2. Remove the three untracked live-seat profile files from the working tree. They must not enter the committed AGY catalog.
3. Commit only a small advisory catalog: readiness-bridge, lane-v-verifier, money-gate-reviewer, and a README. Every profile remains read-only, emits findings to its parent/local caller only, and cannot claim a shared seat, use the fixed mailbox writer, consume shared state, or issue a binding GO, NITS, or FAIL.
4. Add a catalog test that fails if a forbidden live-seat profile reappears or a committed AGY prompt grants shared-seat, writer, or shared-state authority.
5. Existing AGY indexes must be regular files and independently parseable by Git. Reject symlinks, directories, unreadable/corrupt indexes, and an empty index when HEAD tracks files. Preserve a healthy existing index byte-for-byte, including staged work. Missing-index seeding remains unchanged and uses a Git-authority-clean environment.
6. Keep advisory default and explicit agy-unit namespacing unchanged. This route does not enable a provider process or a shared AGY seat.

## Allowed paths

- .agy/agents/README.md
- .agy/agents/readiness-bridge.toml
- .agy/agents/lane-v-verifier.toml
- .agy/agents/money-gate-reviewer.toml
- .agy/agents/protocol-director.toml for local removal only
- .agy/agents/protocol-operator.toml for local removal only
- .agy/agents/protocol-coordinator.toml for local removal only
- scripts/agy_seat_launcher.py
- tests/unit/test_agy_seat_launcher.py
- tests/unit/test_agy_agent_surfaces.py

## Exclusions and review

Preserve every unrelated dirty or untracked file, including all Cursor, Claude, Codex, root-governance, and protocol-sync work. No other AGY path is in scope. No provider configuration, runtime registry, real seat index, shared mailbox state, target repository, or external service may be changed.

After a focused green suite, fresh Pipeline smoke, and a clean exact diff check, Director2 commits the scoped implementation and publishes one actual-range verification request. Operator2 alone reviews the immutable range and issues the binding verdict.

## Exact Next Trigger

Continue in the existing Director2 task, implement this route, and use the existing Operator2 task for the one actual-range review. Do not create replacement tasks.

Cursor at send: 0

Cursor at send: 0
