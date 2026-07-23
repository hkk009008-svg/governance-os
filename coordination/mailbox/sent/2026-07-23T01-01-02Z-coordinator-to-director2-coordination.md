# Coordinator → Director2: Route AGY provider-isolation containment

**When:** 2026-07-23T01:01:02Z · **From:** coordinator (online)

Event type: coordination
Route ref: AGY-PROVIDER-ISOLATION-20260723
Immutable parent: de9e7ab42b681f52c07d858395728f2a6698624aa
Owner: director2
Author provider/model: Codex/gpt-5.6-terra
Assigned reviewer: operator2
Reviewer provider/model: Codex/gpt-5.6-sol
Outcome: make the AGY launcher and continuation adapter provider-pure and cross-provider-safe without launching AGY or claiming a live shared seat.

Confirmed findings:
- AGY-F001: scripts/agy_seat_launcher.py emits CODEX_SEAT, CODEX_AGENT_MODE, CODEX_AGENT_ROLE, and CODEX_BEHAVIOR_SOURCE alongside AGY identity.
- AGY-F002: build_launch_spec preserves ambient CLAUDE_*, CURSOR_*, CODEX_*, ANTIGRAVITY_*, and GIT_* authority, including a foreign GIT_DIR.
- AGY-F003: docs/protocol/agy/continuation.md describes AGY-only propagation but advertises live shared seats by default and shows the fixed writer with an obsolete body-file argument. Cross-provider doctrine permits AGY only as advisory/read-only unless an explicit independent single-model AGY unit is selected.

Required behavior:
1. Write failing tests first for AGY-F001..F003 where executable.
2. The launcher exports only AGY-owned seat/mode/role/behavior identity plus the resolved AGY seat index; it must not expose CODEX_* compatibility identity.
3. Strip foreign provider contract variables and inherited GIT_* authority before constructing the child environment. Preserve only normal environment and narrowly justified credentials.
4. Default cross-provider posture is readiness/advisory and cannot claim a shared live seat. If live AGY single-model mode is retained, require an explicit, documented mode selection that cannot be confused with Codex/Claude/Cursor seat occupancy.
5. Correct the fixed-writer example to send the body on stdin.
6. Preserve current unrelated dirty/untracked work; do not absorb Cursor, Claude, Superpowers, or ambient root changes.

Allowed implementation paths:
- scripts/agy_seat_launcher.py
- tests/unit/test_agy_seat_launcher.py
- docs/protocol/agy/continuation.md
- coordination/bin/agy-seat
- a new AGY-specific protocol adapter and its focused test only if needed

Explicitly excluded:
- scripts/codex_protocol_model.py
- AGENTS.md
- scripts/ci_smoke.py
- tests/unit/test_protocol_prompt_sync.py
- all .cursor and .claude paths
- provider launch, local config creation, runtime lock/lease changes, cursor consumption, merge, push, or cleanup

Acceptance:
- focused AGY tests and any directly affected prompt/surface sync test pass;
- fresh ci_smoke.py and git diff --check pass;
- publish one committed verify-request for the actual base..head range, binding this route and AGY-F001..F003;
- operator2 alone issues GO/NITS/FAIL on that exact range.

Cursor at send: 0
