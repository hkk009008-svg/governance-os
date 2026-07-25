# AGY Protocol Modernization — Context Summary

## Project Overview
The AGY Protocol Modernization project updates Pipeline's AGY (Antigravity) provider integration:
1. **R1: Direct Autonomous Operation**: Remove `--mode single-model-autonomous` or `--dry-run` restrictions from `scripts/agy_protocol_model.py`, `scripts/agy_seat_launcher.py`, and `coordination/bin/agy-seat`. Support direct autonomous operation by default.
2. **R2: Subagent & Artifact Mesh Architecture**: Update `docs/protocol/agy/continuation.md` and `.agents/skills/antigravity-harness/SKILL.md` to establish subagent (`define_subagent`/`invoke_subagent`) and artifact (`implementation_plan.md`, `walkthrough.md`) usage over legacy disk mailbox polling.
3. **R3: Test Alignment & Verification**: Update unit tests in `tests/unit/test_agy_*.py`, run pytest and `scripts/ci_smoke.py`, ensuring zero regression for Codex, Claude, Cursor.

## Agent Working Directories
- Orchestrator: `/Users/hyungkoookkim/Pipeline/.agents/orchestrator/`
- Subagents will be spawned into dedicated `.agents/<type>_<milestone>_[N]/` directories.
