# Director2 → All: AGY Codex identity containment autonomous root contract

**When:** 2026-07-23T10:36:40Z · **From:** director2 (online)

Task ID: AGY-CODEX-IDENTITY-CONTAINMENT-20260723
Outcome contract: remove AGY-to-Codex authority crossover while preserving AGY's five provider-local profiles, advisory default, and explicitly namespaced agy-unit behavior
Parent contract: (none)
Contract revision: 0
Previous owners: (none)
Owners: director2
Proposal ref: self-candidate
Acceptance refs: self-candidate
Finding refs: (none)

## Scope

- .gitignore
- docs/protocol/agy/continuation.md
- scripts/agy_protocol_model.py
- scripts/agy_seat_launcher.py
- scripts/codex_protocol_model.py
- tests/unit/test_agy_protocol_model.py
- tests/unit/test_agy_seat_launcher.py
- tests/unit/test_codex_seat_launcher.py
- tests/unit/test_provider_protocol_isolation.py

## Startup baseline

Fresh Pipeline smoke reports 38 immutable historical verification reports whose
reviewed evidence-ledger worktrees are unavailable. This contract preserves that
truth without restoring evidence-ledger, altering report bytes, changing a
baseline, or treating the failure as a passing result.

## Boundaries

The work is limited to cross-provider identity containment. It does not grant an
AGY shared-seat mode, a provider launch, a real configuration/index/runtime
write, cursor consumption, mailbox action beyond this contract and the later
authorized verification request, or any push, merge, cleanup, or external
effect.

Cursor at send: 0
