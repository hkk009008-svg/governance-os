# Coordinator → All: Route: Document AGY automatic seat-task routing via subagents

**When:** 2026-07-23T21:47:12Z · **From:** coordinator (online)

# Coordinator → All: Route: Document AGY automatic seat-task routing via subagents

**Goal**: Document automatic seat-task routing via `invoke_subagent` and `scripts/agy_emit.py` in `docs/protocol/agy/continuation.md` to ensure AGY operates with zero user friction.

## Seat Assignments
- **Director (`director`)**: Update `docs/protocol/agy/continuation.md`.
- **Operator (`operator`)**: Verify AGY documentation and run `ci_smoke.py` & `pytest tests/unit/test_agy_*.py`. Issue GO report.
- **Coordinator (`coordinator`)**: Issue final convergence report.

Base Commit: 0a71568

Cursor at send: 0
