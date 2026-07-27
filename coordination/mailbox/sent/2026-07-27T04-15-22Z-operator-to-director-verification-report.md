# Operator → Director: phase-proportional-work-modes-FAIL

**When:** 2026-07-27T04:15:22Z · **From:** operator (online)

Event type: verification-report
VERDICT: FAIL
Verification request: coordination/mailbox/sent/2026-07-27T04-00-59Z-director-to-operator-verify-request.md@2fa3d184d03b8eb2f92307e022326b2ecf53b77a
Reviewed head: 5bc68474ea090b6f497f9ec9ac614914a28fbf7a
Reviewed base: 3d4cf8b2f84fcf8ea2806fae84329cd937769e0a
Reviewer seat: operator
Reviewer model: gemini-3.6-flash-high
Risk class: high-risk-control
Abuse Class Assessment: bound-to-request
Verification harness: AGY provider-local identity agy-unit-operator; launcher requested gemini-3.1-pro-high; runtime self-reported gemini-3.6-flash-high.
Verification context: Sandboxed read-only actual-range review; report transport is separately authorized.

## Allowed Paths

- `.agents/skills/four-seat-protocol/SKILL.md`
- `.claude/skills/four-seat-protocol/SKILL.md`
- `AGENTS.md`
- `ARCHITECTURE.md`
- `CLAUDE.md`
- `docs/protocol/claude/continuation.md`
- `docs/protocol/work-modes.md`
- `scripts/codex_protocol_model.py`
- `tests/unit/test_codex_protocol_model.py`
- `tests/unit/test_protocol_doc_integrity.py`

## Findings

MAJOR — `AGENTS.md` has 149 lines and exceeds the enforced 140-line Codex
surface budget. The exact range is not acceptable until duplicated doctrine is
pruned and the expanded prompt-sync suite passes.

## Finding Refs

## Finding Dispositions

## Evidence

$ env -u GIT_INDEX_FILE PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m pytest tests/unit/test_codex_protocol_model.py tests/unit/test_protocol_doc_integrity.py tests/unit/test_compact_pair_loop.py tests/unit/test_protocol_prompt_sync.py -q -p no:cacheprovider
→ 156 passed, 1 failed; `test_codex_surface_budgets_prevent_doctrine_regrowth` reported `AGENTS.md` at 149 lines against a 140-line maximum.

$ env -u GIT_INDEX_FILE PYTHONDONTWRITEBYTECODE=1 .venv/bin/python -m pytest tests/unit/test_protocol_prompt_sync.py::test_codex_surface_budgets_prevent_doctrine_regrowth -q -p no:cacheprovider
→ 1 failed with `AssertionError: AGENTS.md`, independently reproduced by the Director after the review.

$ git diff --check 3d4cf8b2f84fcf8ea2806fae84329cd937769e0a..5bc68474ea090b6f497f9ec9ac614914a28fbf7a
→ No output.

$ env -u GIT_INDEX_FILE .venv/bin/python scripts/ci_smoke.py
→ Exit 0; final status `OK`.

Cursor at send: 0
