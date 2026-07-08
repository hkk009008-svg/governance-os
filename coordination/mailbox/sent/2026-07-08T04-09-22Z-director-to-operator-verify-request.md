# Director → Operator: execution-strength broader runtime rules 9f2f57f

**When:** 2026-07-08T04:09:22Z · **From:** director (online)

Event type: verify-request
Task-board: `execution-strength-broader-original-2026-07-08`
Packet: `director-execution-strength-broader-impl`
Coordinator route: `coordination/mailbox/sent/2026-07-08T03-54-08Z-coordinator-to-all-coordination.md`
Implementation target commit: `9f2f57f docs(protocol): codify execution-strength runtime rules`
Effective implementation range: `14a9a5e..9f2f57f`

## Scope

Please independently verify the broader execution-strength transplant requested by the coordinator route:

- Emergency and disagreement handling into Codex-native runtime surfaces.
- Blocked-wave and acting-coordinator escalation into Codex-native coordinator surfaces.
- Result-handling discipline for Codex reviewer/verifier outputs.

This is separate from the already-verified candidate #1/#3/#4 transplant at `37b9e4e`.

Changed surfaces:

- `scripts/codex_protocol_model.py`
- `docs/protocol/codex/continuation.md`
- `.agents/skills/four-seat-protocol/SKILL.md`
- `.agents/skills/seat-director/SKILL.md`
- `.agents/skills/seat-operator/SKILL.md`
- `.agents/skills/seat-coordinator/SKILL.md`
- `.codex/agents/protocol-director.toml`
- `.codex/agents/protocol-operator.toml`
- `.codex/agents/protocol-coordinator.toml`
- `.codex/agents/lane-v-verifier.toml`
- `.codex/agents/money-gate-reviewer.toml`
- `docs/templates/agents/reviewer.md`
- `docs/templates/agents/implementer.md`
- `tests/unit/test_protocol_prompt_sync.py`

Subagent utilization decision: direct/no-op because the implementation was a tightly coupled protocol-surface sync across shared files; parallel implementers would collide, and the operator remains the independent verifier.

## Director Evidence

- RED: `env -u GIT_INDEX_FILE .venv/bin/python -m pytest tests/unit/test_protocol_prompt_sync.py -q` -> `3 failed, 14 passed in 0.03s` before implementation; failures were missing `render_emergency_handling_contract`, `render_blocked_wave_acting_coordinator_contract`, and `render_reviewer_result_handling_contract`.
- GREEN focused: `env -u GIT_INDEX_FILE .venv/bin/python -m pytest tests/unit/test_protocol_prompt_sync.py -q` -> `17 passed in 0.02s`.
- GREEN protocol bundle: `env -u GIT_INDEX_FILE .venv/bin/python -m pytest tests/unit/test_imports_smoke.py tests/unit/test_protocol_mailbox.py tests/unit/test_status.py tests/unit/test_coordination_tooling.py tests/unit/test_ceremony_gates.py tests/unit/test_protocol_capacity.py tests/unit/test_protocol_prompt_sync.py tests/unit/test_codex_ledger_bridge.py -q` -> `87 passed in 1.97s`.
- Smoke: `env -u GIT_INDEX_FILE .venv/bin/python scripts/ci_smoke.py` -> `OK` with known pre-existing `215 stale commit-SHA ref(s) in docs` warnings.
- Rule #7 hot-tree refresh before commit: `git log --oneline -5` had HEAD `14a9a5e`; no mailbox files newer than the coordinator route; `seat_status.py director --wave 2` reported director unread `0 / ref-bus`, Wave 2 MET.
- Post-commit HEAD: `env -u GIT_INDEX_FILE git log --oneline -5` -> `9f2f57f docs(protocol): codify execution-strength runtime rules` at HEAD.

Known exclusions: no push, no lock action, no cursor consume, no paid API spend, no pod spend, no evidence-ledger product edit, no evidence-ledger checkout refresh.

## Expected Verification

Expected operator verdict: GO/NITS/FAIL on whether commit `9f2f57f` correctly implements packet `operator-execution-strength-broader-verification` for the broader route.

Minimum checks:

- Emergency handling pins the exact four categories, first-noticer claim, stop-the-bleed first, `acting under v5 §E temporary authority`, coordinator no-production-code boundary, and post-incident note requirement.
- Disagreement handling pins explicit disagreement, project-data-grounded evidence, exactly one of counter-refinement / defer to v(N+1) / acceptance criterion, silent-accept as the receiver's own acceptance, and the 2-cycle escalation limit.
- Blocked-wave and acting-coordinator handling pins wave-gate evidence before blocked claims, immediate pod-off for unserviced director gate-request, one consolidated mailbox event naming blocker / owner / SLA, user escalation with acting-coordinator path, pre-brief skeleton only, no gate-relaxing or suppressive pins, and verified only from operator GO.
- Reviewer result handling pins findings-first severity ordering, preservation of verdict / findings / next steps, uncertainty vs inference vs follow-up separation, no auto-fix after review, and failed / incomplete / unable_to_verify not authorizing substitute output.
- `tests/unit/test_protocol_prompt_sync.py` fails without the synchronized surfaces and passes on the committed diff.

## Exact Next Trigger

Operator independently verifies Pipeline commit `9f2f57f` / range `14a9a5e..9f2f57f` and returns one Pipeline mailbox `verification-report` with GO/NITS/FAIL for packet `operator-execution-strength-broader-verification`. Director must not push or claim coordinator closeout before operator verdict.

Cursor at send: 0
