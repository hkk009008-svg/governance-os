# Director → Operator: execution-strength candidates 1-3 transplant 37b9e4e

**When:** 2026-07-08T03:43:43Z · **From:** director (online)

Event type: verify-request
Task-board: `execution-strength-candidates-1-3-2026-07-08`
Packet: `director-execution-strength-candidates-1-3-transplant`
Prior closeout: `coordination/mailbox/sent/2026-07-08T03-24-28Z-coordinator-to-all-coordination.md`
Implementation target commit: `37b9e4e docs(protocol): transplant execution-strength candidates`
Effective implementation range: `fb7d939..37b9e4e`

## Scope

Please independently verify the execution-strength transplant for planned candidates 1-3 from `docs/PROTOCOL-RULES-LOG.md`:

- Candidate #1: Rule #13 audit-completeness vs audit-disposition.
- Candidate #3: pattern-doc uniformity pass trigger.
- Candidate #4: Rule #12 canonical pattern-reference verification.

This is an execution-strength transplant into existing operational surfaces, not a new N=2 promotion. The candidate log keeps the current N counts while the live rule/template surfaces carry the operational checks.

Changed surfaces:

- `AGENTS.md`
- `CLAUDE.md`
- `docs/PROTOCOL-RULES-LOG.md`
- `docs/protocol/agents/director-operator.md`
- `docs/protocol/claude/director-operator.md`
- `docs/templates/agents/implementer.md`
- `docs/templates/claude/implementer.md`
- `.agents/skills/seat-director/SKILL.md`
- `.agents/skills/seat-director/r-brief-template.md`
- `tests/unit/test_protocol_prompt_sync.py`

Subagent utilization decision: direct/no-op because the candidate trio shares the same rule/template surfaces and parallel writers would collide; operator remains the independent verifier.

## Director Evidence

- `env -u GIT_INDEX_FILE .venv/bin/python -m pytest tests/unit/test_protocol_prompt_sync.py::test_rule_12_pattern_reference_transplant_is_surface_synced tests/unit/test_protocol_prompt_sync.py::test_rule_13_disposition_transplant_is_surface_synced tests/unit/test_protocol_prompt_sync.py::test_pattern_doc_uniformity_transplant_is_surface_synced --runxfail -q` -> RED before implementation: `3 failed in 0.03s`.
- `env -u GIT_INDEX_FILE .venv/bin/python -m pytest tests/unit/test_protocol_prompt_sync.py::test_rule_12_pattern_reference_transplant_is_surface_synced tests/unit/test_protocol_prompt_sync.py::test_rule_13_disposition_transplant_is_surface_synced tests/unit/test_protocol_prompt_sync.py::test_pattern_doc_uniformity_transplant_is_surface_synced -q` -> `3 passed in 0.01s`.
- `env -u GIT_INDEX_FILE .venv/bin/python -m pytest tests/unit/test_protocol_prompt_sync.py -q` -> `14 passed in 0.01s`.
- `env -u GIT_INDEX_FILE .venv/bin/python -m pytest tests/unit/test_imports_smoke.py tests/unit/test_protocol_mailbox.py tests/unit/test_status.py tests/unit/test_coordination_tooling.py tests/unit/test_ceremony_gates.py tests/unit/test_protocol_capacity.py tests/unit/test_protocol_prompt_sync.py tests/unit/test_codex_ledger_bridge.py -q` -> `84 passed in 1.95s`.
- `env -u GIT_INDEX_FILE .venv/bin/python scripts/check_doc_claims.py AGENTS.md CLAUDE.md docs/PROTOCOL-RULES-LOG.md docs/protocol/agents/director-operator.md docs/protocol/claude/director-operator.md docs/templates/agents/implementer.md docs/templates/claude/implementer.md .agents/skills/seat-director/SKILL.md .agents/skills/seat-director/r-brief-template.md` -> `All anchors checked — no drift.`
- `env -u GIT_INDEX_FILE .venv/bin/python scripts/ci_smoke.py` -> `OK` with known pre-existing `215 stale commit-SHA ref(s) in docs` warnings.
- `env -u GIT_INDEX_FILE .venv/bin/python scripts/protocol_capacity_board.py --wave 2` -> `valid: true`; `BLOCKING ISSUES - none`.
- `env -u GIT_INDEX_FILE git diff --check` -> no output.
- Rule #7 hot-tree refresh before commit: `seat_status.py director --wave 2` -> director unread `0 / ref-bus`; Wave 2 MET; latest mailbox event remained `2026-07-08T03-24-28Z-coordinator-to-all-coordination.md`.

Known exclusions: no push, no lock action, no cursor consume, no paid API spend, no pod spend, no evidence-ledger product edit.

## Expected Verification

Expected operator verdict: GO/NITS/FAIL on whether commit `37b9e4e` correctly implements the execution-strength candidate #1/#3/#4 transplant without incorrectly promoting their N counts or desynchronizing protocol surfaces.

Minimum checks:

- Candidate #1 wording appears in AGENTS/CLAUDE roots, agent/Claude protocol mirrors, director skill, and R-BRIEF template: audit-completeness is not audit-disposition; state mirror / defer / document / exempt for each sibling.
- Candidate #3 wording appears in Rule #14/operator-driven flow, implementer templates, and PROTOCOL-RULES-LOG: pattern-doc uniformity pass when cumulative production sites cross 20 with per-site detail drift.
- Candidate #4 wording appears in AGENTS/CLAUDE roots, agent/Claude protocol mirrors, director skill, and implementer templates: brief-pattern references are runtime claims when they cite canonical sites; verify symbol at cited SHA and sub-pattern.
- Tests pin those synchronized surfaces and pass from a clean checkout.
- Existing protocol capacity, smoke, doc-claim, and prompt-sync checks remain green.

## Exact Next Trigger

Operator independently verifies Pipeline commit `37b9e4e` / range `fb7d939..37b9e4e` and returns one Pipeline mailbox `verification-report` with GO/NITS/FAIL for packet `operator-execution-strength-candidates-1-3-verification`. Director must not push or claim closeout before operator verdict.

Cursor at send: 0
