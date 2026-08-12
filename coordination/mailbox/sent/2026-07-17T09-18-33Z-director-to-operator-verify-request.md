# Director → Operator: verify final compact replacement range

**When:** 2026-07-17T09:18:33Z · **From:** director (online)

Event type: verify-request
Reviewed head: a8b117261f1d231a387e83c12927aaea6cb9b0fc
Reviewed base: a546f059fc8f3e324cf102e242bdc9840de93880
Author seat: director
Author model: gpt-5.6-sol
Assigned operator: operator

## Acceptance Question

Does the full compact replacement through a8b117261f1d231a387e83c12927aaea6cb9b0fc implement the committed plan and abuse cases by removing descriptor, task-publication store, and recovery machinery plus all prescribed trigger headings, while retaining non-author Operator authority, the fixed mailbox-writer fence, every other mailbox, capacity, and side-effect guard, internal coordinator continuation, and all user-gated effects; and, only on GO, permit the coordinator to close only the final Phase 4 Task 2 review checkbox from the unchanged committed rehearsal log and prior Phase 4 Task 1 GO? The requests coordination/mailbox/sent/2026-07-17T08-48-03Z-director-to-operator-verify-request.md at b7bede04a00ffa274f93e257e7437d02625e52b7 and coordination/mailbox/sent/2026-07-17T09-09-12Z-director-to-operator-verify-request.md at 57ee03a6af5d30dac546da7558630f6f6226e676 are immutable historical evidence, are superseded, and grant no current authority.

## Allowed Paths

- .agents/skills/four-seat-protocol/SKILL.md
- .agents/skills/seat-coordinator/SKILL.md
- .agents/skills/seat-director/SKILL.md
- .agents/skills/seat-operator/SKILL.md
- .agents/skills/seat-operator/verification-report-format.md
- .claude/agents/lane-v-verifier.md
- .claude/skills/seat-coordinator/SKILL.md
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
- coordination/mailbox/sent/2026-07-17T08-48-03Z-director-to-operator-verify-request.md
- coordination/mailbox/sent/2026-07-17T09-09-12Z-director-to-operator-verify-request.md
- docs/PROGRAM-MANUAL.md
- docs/protocol/agents/director-operator.md
- docs/protocol/claude/continuation.md
- docs/protocol/claude/director-operator.md
- docs/protocol/claude/independence-first.md
- docs/protocol/codex/continuation.md
- scripts/check_coordination.py
- scripts/check_go_schema.py
- scripts/codex_protocol_model.py
- scripts/compact_pair_loop.py
- scripts/protocol_capacity.py
- scripts/route_manifest.py
- scripts/verification_report_gate.py
- tests/fixtures/compact_kernel/v1_surface_inventory.json
- tests/unit/test_check_coordination.py
- tests/unit/test_check_go_schema.py
- tests/unit/test_compact_kernel_surface_inventory.py
- tests/unit/test_compact_pair_loop.py
- tests/unit/test_coordination_tooling.py
- tests/unit/test_protocol_capacity.py
- tests/unit/test_protocol_doc_integrity.py
- tests/unit/test_protocol_prompt_sync.py
- tests/unit/test_route_render.py
- tests/unit/test_verification_report_gate.py

## Verification Commands

$ env -u GIT_INDEX_FILE /Users/hyungkoookkim/Pipeline/.venv/bin/python -m pytest tests/unit/test_compact_pair_loop.py tests/unit/test_coordination_tooling.py tests/unit/test_check_go_schema.py tests/unit/test_protocol_capacity.py tests/unit/test_protocol_prompt_sync.py tests/unit/test_protocol_doc_integrity.py tests/unit/test_compact_kernel_surface_inventory.py -q
$ env -u GIT_INDEX_FILE /Users/hyungkoookkim/Pipeline/.venv/bin/python -m pytest tests/unit/test_check_coordination.py tests/unit/test_protocol_capacity.py tests/unit/test_protocol_prompt_sync.py -q
$ env -u GIT_INDEX_FILE /Users/hyungkoookkim/Pipeline/.venv/bin/python -m pytest tests/unit/test_route_manifest.py tests/unit/test_route_render.py tests/unit/test_route_render_invariance.py tests/unit/test_route_schema_sync.py tests/unit/test_route_compat.py -q
$ env -u GIT_INDEX_FILE /Users/hyungkoookkim/Pipeline/.venv/bin/python scripts/ci_smoke.py
$ env -u GIT_INDEX_FILE /bin/bash -n coordination/bin/send-event
$ env -u GIT_INDEX_FILE git diff a546f059fc8f3e324cf102e242bdc9840de93880..a8b117261f1d231a387e83c12927aaea6cb9b0fc --check
$ wc -l scripts/compact_pair_loop.py
$ env -u GIT_INDEX_FILE git diff a546f059fc8f3e324cf102e242bdc9840de93880..a8b117261f1d231a387e83c12927aaea6cb9b0fc -- scripts/kernel_activation.py
$ rg -n "TaskPublicationStore|Lane-V-Scope|shipping trigger" scripts coordination/bin AGENTS.md ARCHITECTURE.md docs/protocol/codex .agents/skills .codex/agents
$ ! rg -n "^## Exact Next Trigger$|Exact Next Trigger" .agents .claude .codex docs/protocol docs/PROGRAM-MANUAL.md scripts -g '*.md' -g '*.toml' -g '*.py'
$ env -u GIT_INDEX_FILE git show a2f03443823acd40a1c4451386595a3fc309aa55:logs/capability-first/phase4-task2-disposable-rehearsal.json
$ env -u GIT_INDEX_FILE git show c93c7f34c372f9d80874c6d03db5e4e74b5f0a02:coordination/mailbox/sent/2026-07-17T04-59-08Z-operator-to-all-verification-report.md

Cursor at send: 0
