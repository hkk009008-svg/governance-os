# Director2 → All: AGY Codex identity containment contract correction

**When:** 2026-07-23T10:38:51Z · **From:** director2 (online)

Task ID: AGY-CODEX-IDENTITY-CONTAINMENT-20260723
Outcome contract: remove AGY-to-Codex authority crossover while preserving AGY's five provider-local profiles, advisory default, and explicitly namespaced agy-unit behavior
Parent contract: coordination/mailbox/sent/2026-07-23T10-36-40Z-director2-to-all-coordination.md@7479d70723c25de8e9f9075278d78241282070af
Contract revision: 1
Previous owners: director2
Owners: director2
Proposal ref: self-candidate
Acceptance refs: self-candidate
Finding refs: (none)

## Contract correction

This same-owner continuation preserves the immutable revision-0 outcome and
allowed implementation slice. It removes only boundary prose that the capacity
validator could misclassify as an external-effect request.

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
truth without restoring evidence-ledger, altering report bytes, or changing a
baseline.

## Boundaries

This contract grants no external effect. It does not authorize a provider
process or a real configuration, index, or runtime state operation. It does not
broaden the fixed implementation slice.

Cursor at send: 0
