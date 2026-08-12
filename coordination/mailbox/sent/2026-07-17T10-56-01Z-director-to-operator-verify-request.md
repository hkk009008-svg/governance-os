# Director → Operator: supersede invalid terminal cleanup request

**When:** 2026-07-17T10:56:01Z · **From:** director (online)

Event type: verify-request
Reviewed head: 411c2af11abca0413c6e41f8980dcd2a1a009763
Reviewed base: d434a0d3ed5c47deb6855571d740a3b05ba9c257
Author seat: director
Author model: gpt-5.6-sol
Assigned operator: operator
Intended reviewer model: gpt-5.6-terra

## Acceptance Question

Does implementation commit 411c2af11abca0413c6e41f8980dcd2a1a009763 faithfully execute the committed terminal-cleanup plan at docs/superpowers/plans/2026-07-17-live-caller-only-terminal-cleanup.md by retaining only the compact pair and one fixed mailbox writer, deleting unused capability, selector, provider, and recovery surfaces, and preserving the real reader parsing, validation, target binding, exit-code behavior, Operator-only verdict authority, shared common-dir lock, no-follow and no-clobber publication, fsync, rollback, and exact-path staging? Independently test every committed abuse case: docs and tests alone cannot preserve a dead subsystem; no real production caller was hidden; removal cannot split writers, follow a symlink, overwrite an event, skip fsync, or stage an unintended path; reader-guard removal cannot weaken target, mailbox, capacity, or report validation; stale or same-author actors cannot publish an authoritative report; historical reports remain evidence-only; and operative prose cannot advertise retired selector, receipt, descriptor, or publication machinery. The prior event `coordination/mailbox/sent/2026-07-17T10-53-03Z-director-to-operator-verify-request.md` is immutable invalid historical evidence, is superseded, and grants no authority because it names nonexistent reviewed SHAs and has an empty Allowed Paths section. Expected verdict is GO only if this exact request, diff, and all cases pass; otherwise issue NITS or FAIL findings-first.

## Allowed Paths

- .agents/skills/four-seat-protocol/scripts/seat_status.py
- .claude/agents/readiness-bridge.md
- ARCHITECTURE.md
- coordination/README.md
- coordination/bin/consume-events
- coordination/bin/send-event
- docs/protocol/capabilities.md
- docs/protocol/claude/continuation.md
- docs/protocol/codex/continuation.md
- docs/protocol/threeway/ANTIGRAVITY-ADOPTION.md
- docs/protocol/threeway/ARCHITECTURE-DIAGRAM.md
- docs/protocol/threeway/ONBOARDING.md
- docs/protocol/threeway/UNIFIED-OPERATING-DOCTRINE.md
- docs/superpowers/capability_first_compact_kernel_codex_seat_guide.md
- docs/superpowers/plans/2026-07-15-capability-compact-reducer-phase2.md
- docs/superpowers/plans/2026-07-15-capability-phase1-surface-inventory-closure.md
- docs/superpowers/plans/2026-07-16-capability-v1-shadow-adapter-phase2b.md
- docs/superpowers/plans/2026-07-16-chatgpt-local-reprepare-approval-and-integration.md
- docs/superpowers/plans/2026-07-16-chatgpt-local-reprepare-task1-lanev-correction.md
- docs/superpowers/plans/2026-07-16-compact-kernel-phase1-2-integration.md
- docs/superpowers/plans/2026-07-16-compact-kernel-phase4-activation.md
- docs/superpowers/plans/2026-07-16-control-plane-compact-phase3-convergence.md
- docs/superpowers/plans/2026-07-16-opus-quality-correction-and-recovery-routing.md
- docs/superpowers/plans/2026-07-16-ppl-publication-race-correction.md
- docs/superpowers/plans/2026-07-16-provider-tools-targeted-decommission.md
- docs/superpowers/plans/2026-07-16-recovery-owner-wip-disposition.md
- docs/superpowers/plans/2026-07-16-recovery-retirement-publication-reconciliation.md
- docs/superpowers/plans/2026-07-16-target-aware-evidence-ledger-opus-bridge.md
- docs/superpowers/plans/2026-07-17-compact-pair-loop-replacement.md
- docs/superpowers/specs/2026-07-16-chatgpt-local-reprepare-design.md
- docs/superpowers/specs/2026-07-16-chatgpt-local-reprepare-task1-lanev-correction-design.md
- docs/superpowers/specs/2026-07-16-operative-doc-surface-compaction-proposal.md
- docs/superpowers/specs/2026-07-16-opus-chatgpt-pro-targeted-decommission-design.md
- docs/superpowers/specs/2026-07-16-pipeline-recovery-sequence-design.md
- docs/superpowers/specs/2026-07-16-simple-cross-model-gptpro-invariants.md
- governance.toml
- schemas/capability-receipt-v1.schema.json
- schemas/capability-v1.schema.json
- schemas/route-v2.schema.json
- scripts/baselines/capability_first_five_profile_v1.json
- scripts/capability_baseline_runtime.py
- scripts/capability_reducer.py
- scripts/capability_v1_adapter.py
- scripts/compact_state_mapping.py
- scripts/continuation_readiness.py
- scripts/ledger_start_guard.py
- scripts/mailbox_monitor.py
- scripts/mailbox_writer.py
- scripts/protocol_capacity_board.py
- scripts/protocol_doctor.py
- scripts/protocol_effectiveness_report.py
- scripts/route_capability.py
- scripts/route_lineage.py
- scripts/status.py
- scripts/target_binding.py
- tests/fixtures/compact_kernel/v1_misuse_vectors.json
- tests/fixtures/compact_kernel/v1_surface_inventory.json
- tests/fixtures/compact_kernel/v1_to_v2_replay.json
- tests/fixtures/compact_kernel/v2_replay_vectors.json
- tests/fixtures/compact_state_mapping/v1.json
- tests/unit/test_capability_baseline_runtime.py
- tests/unit/test_capability_reducer.py
- tests/unit/test_capability_reducer_replay.py
- tests/unit/test_capability_security.py
- tests/unit/test_capability_stateful.py
- tests/unit/test_capability_v1_adapter.py
- tests/unit/test_compact_kernel_surface_inventory.py
- tests/unit/test_compact_state_mapping.py
- tests/unit/test_coordination_tooling.py
- tests/unit/test_kernel_activation.py
- tests/unit/test_kernel_properties.py
- tests/unit/test_lineage_capability_stateful.py
- tests/unit/test_mailbox_writer.py
- tests/unit/test_protocol_effectiveness_report.py
- tests/unit/test_protocol_prompt_sync.py
- tests/unit/test_route_capability.py
- tests/unit/test_route_lineage.py
- tests/unit/test_route_v2_schema_sync.py
- tests/unit/test_target_binding.py

## Verification Commands

$ env -u GIT_INDEX_FILE .venv/bin/python -m pytest -q
$ env -u GIT_INDEX_FILE .venv/bin/python -m pytest tests/unit/test_mailbox_writer.py tests/unit/test_coordination_tooling.py tests/unit/test_target_binding.py tests/unit/test_target_binding_properties.py tests/unit/test_protocol_capacity.py tests/unit/test_route_lineage.py tests/unit/test_seat_status_all.py tests/unit/test_status.py tests/unit/test_compact_pair_loop.py -q
$ env -u GIT_INDEX_FILE .venv/bin/python scripts/ci_smoke.py
$ env -u GIT_INDEX_FILE .venv/bin/python scripts/protocol_doctor.py --wave 2
$ env -u GIT_INDEX_FILE /bin/bash -n coordination/bin/send-event coordination/bin/consume-events
$ env -u GIT_INDEX_FILE git diff d434a0d3ed5c47deb6855571d740a3b05ba9c257..411c2af11abca0413c6e41f8980dcd2a1a009763 --check
$ wc -l scripts/compact_pair_loop.py scripts/mailbox_writer.py
$ ! rg -n 'capability_baseline_runtime|protocol_effectiveness_report|route_capability|compact_state_mapping|capability_reducer|capability_v1_adapter|route-v2|kernel_activation|refs/protocol/kernel-activation|TaskPublicationStore|Lane-V-Scope' scripts coordination/bin AGENTS.md ARCHITECTURE.md coordination/README.md docs/protocol .agents/skills .codex/agents .claude/agents

Cursor at send: 0
