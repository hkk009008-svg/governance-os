# Director → Operator: verify compact pair replacement and Phase 4 closeout evidence

**When:** 2026-07-17T08:48:03Z · **From:** director (online)

Event type: verify-request
Reviewed head: 37c6a7fa546201c4d5f91e6a318a3f19f3768b57
Reviewed base: a546f059fc8f3e324cf102e242bdc9840de93880
Author seat: director
Author model: gpt-5.6-sol
Assigned operator: operator

## Acceptance Question

Does the exact three-commit compact replacement implement the committed plan and abuse cases, preserve scripts/kernel_activation.py and all user-gated effect boundaries, and—only on GO—is the unchanged committed Phase 4 Task 2 rehearsal evidence at a2f03443823acd40a1c4451386595a3fc309aa55 plus the prior Phase 4 Task 1 GO sufficient for the coordinator to close only the final Task 2 review checkbox without rerunning the failed publication campaign?

## Allowed Paths

- .agents/skills/four-seat-protocol/SKILL.md
- .agents/skills/seat-coordinator/SKILL.md
- .agents/skills/seat-director/SKILL.md
- .agents/skills/seat-operator/SKILL.md
- .agents/skills/seat-operator/verification-report-format.md
- .claude/agents/lane-v-verifier.md
- .claude/skills/seat-director/SKILL.md
- .claude/skills/seat-operator/SKILL.md
- .claude/skills/seat-operator/verification-report-format.md
- .codex/agents/lane-v-verifier.toml
- .codex/agents/protocol-coordinator.toml
- .codex/agents/protocol-director.toml
- .codex/agents/protocol-operator.toml
- .codex/agents/readiness-bridge.toml
- AGENTS.md
- ARCHITECTURE.md
- RUNBOOK-DAILY.md
- coordination/bin/send-event
- docs/PROGRAM-MANUAL.md
- docs/protocol/agents/director-operator.md
- docs/protocol/claude/continuation.md
- docs/protocol/claude/director-operator.md
- docs/protocol/claude/independence-first.md
- docs/protocol/codex/continuation.md
- scripts/check_go_schema.py
- scripts/codex_protocol_model.py
- scripts/compact_pair_loop.py
- scripts/protocol_capacity.py
- scripts/verification_report_gate.py
- tests/fixtures/compact_kernel/v1_surface_inventory.json
- tests/unit/test_check_go_schema.py
- tests/unit/test_compact_kernel_surface_inventory.py
- tests/unit/test_compact_pair_loop.py
- tests/unit/test_coordination_tooling.py
- tests/unit/test_protocol_capacity.py
- tests/unit/test_protocol_doc_integrity.py
- tests/unit/test_protocol_prompt_sync.py
- tests/unit/test_verification_report_gate.py

## Verification Commands

$ env -u GIT_INDEX_FILE /Users/hyungkoookkim/Pipeline/.venv/bin/python -m pytest tests/unit/test_compact_pair_loop.py tests/unit/test_coordination_tooling.py tests/unit/test_check_go_schema.py tests/unit/test_protocol_capacity.py tests/unit/test_protocol_prompt_sync.py tests/unit/test_protocol_doc_integrity.py tests/unit/test_compact_kernel_surface_inventory.py -q
$ env -u GIT_INDEX_FILE /Users/hyungkoookkim/Pipeline/.venv/bin/python scripts/ci_smoke.py
$ env -u GIT_INDEX_FILE /bin/bash -n coordination/bin/send-event
$ env -u GIT_INDEX_FILE git diff a546f059fc8f3e324cf102e242bdc9840de93880..37c6a7fa546201c4d5f91e6a318a3f19f3768b57 --check
$ wc -l scripts/compact_pair_loop.py
$ env -u GIT_INDEX_FILE git diff a546f059fc8f3e324cf102e242bdc9840de93880..37c6a7fa546201c4d5f91e6a318a3f19f3768b57 -- scripts/kernel_activation.py
$ rg -n "TaskPublicationStore|Lane-V-Scope|shipping trigger" scripts coordination/bin AGENTS.md ARCHITECTURE.md docs/protocol/codex .agents/skills .codex/agents
$ env -u GIT_INDEX_FILE git show a2f03443823acd40a1c4451386595a3fc309aa55:logs/capability-first/phase4-task2-disposable-rehearsal.json
$ env -u GIT_INDEX_FILE git show c93c7f3e4c8c069e4e29bbd7df28bf84759446bc:coordination/mailbox/sent/2026-07-17T04-59-08Z-operator-to-all-verification-report.md

Cursor at send: 0
