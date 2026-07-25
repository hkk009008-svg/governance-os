# AGY Protocol Modernization — Plan

## Architecture & Goals
Modernize AGY (Antigravity) protocol integration in Pipeline by:
1. Eliminating legacy advisory posture restrictions (`--mode single-model-autonomous`, `--dry-run` launch blockers).
2. Transitioning from disk-bound Markdown mailbox file polling to AGY native subagent & artifact mesh architecture (`define_subagent` / `invoke_subagent`, `implementation_plan.md`, `walkthrough.md`).
3. Updating unit test suite (`tests/unit/test_agy_*.py`) and verifying full CI suite without regressions for Codex, Claude, or Cursor.

## Milestones

| # | Milestone | Target Scope | Dependencies | Status |
|---|-----------|--------------|--------------|--------|
| M1 | Exploration & Analysis | Codebase analysis of AGY models, launcher, docs, skills, tests | None | DONE |
| M2 | Protocol Model & Launcher Refactoring (R1) | `scripts/agy_protocol_model.py`, `scripts/agy_seat_launcher.py`, `coordination/bin/agy-seat` | M1 | DONE |
| M3 | Documentation & Harness Skill Update (R2) | `docs/protocol/agy/continuation.md`, `.agents/skills/antigravity-harness/SKILL.md` | M1 | DONE |
| M4 | Test Suite Alignment & CI Verification (R3) | `tests/unit/test_agy_*.py`, `pytest tests/unit/`, `scripts/ci_smoke.py` | M2, M3 | DONE |

## Interface Contracts & Layout
- Key AGY scripts: `scripts/agy_protocol_model.py`, `scripts/agy_seat_launcher.py`, `coordination/bin/agy-seat`
- Key AGY docs & skills: `docs/protocol/agy/continuation.md`, `.agents/skills/antigravity-harness/SKILL.md`
- Key unit tests: `tests/unit/test_agy_*.py`
- Non-AGY providers (Codex, Claude, Cursor) remain 100% unaffected.
