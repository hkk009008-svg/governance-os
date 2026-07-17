# Director → Operator: verify terminal live-caller cleanup

**When:** 2026-07-17T10:53:03Z · **From:** director (online)

Event type: verify-request
Reviewed head: 411c2af73cd73812ef42a55bf8e52e40c261c271
Reviewed base: d434a0d5fed0baea5df1516d68d3dbd76b424c21
Author seat: director
Author model: gpt-5.6-sol
Assigned operator: operator

## Acceptance Question

Does implementation commit 411c2af73cd73812ef42a55bf8e52e40c261c271 faithfully execute the committed terminal-cleanup plan at docs/superpowers/plans/2026-07-17-live-caller-only-terminal-cleanup.md by retaining only the compact pair and one fixed mailbox writer, deleting unused capability/selector/provider/recovery surfaces, and preserving the real reader parsing, validation, target binding, exit-code behavior, Operator-only verdict authority, shared common-dir lock, no-follow/no-clobber publication, fsync, rollback, and exact-path staging? Independently test every committed abuse case: docs/tests alone cannot preserve a dead subsystem; no real production caller was hidden; removal cannot split writers, follow a symlink, overwrite an event, skip fsync, or stage an unintended path; reader-guard removal cannot weaken target, mailbox, capacity, or report validation; stale/same-author actors cannot publish an authoritative report; historical reports remain evidence-only; and operative prose cannot advertise retired selector, receipt, descriptor, or publication machinery. Expected verdict is GO only if the exact diff and all cases pass; otherwise issue NITS or FAIL findings-first.

## Allowed Paths

## Verification Commands

$ env -u GIT_INDEX_FILE .venv/bin/python -m pytest -q
$ env -u GIT_INDEX_FILE .venv/bin/python -m pytest tests/unit/test_mailbox_writer.py tests/unit/test_coordination_tooling.py tests/unit/test_target_binding.py tests/unit/test_target_binding_properties.py tests/unit/test_protocol_capacity.py tests/unit/test_route_lineage.py tests/unit/test_seat_status_all.py tests/unit/test_status.py tests/unit/test_compact_pair_loop.py -q
$ env -u GIT_INDEX_FILE .venv/bin/python scripts/ci_smoke.py
$ env -u GIT_INDEX_FILE .venv/bin/python scripts/protocol_doctor.py --wave 2
$ env -u GIT_INDEX_FILE /bin/bash -n coordination/bin/send-event coordination/bin/consume-events
$ env -u GIT_INDEX_FILE git diff d434a0d5fed0baea5df1516d68d3dbd76b424c21..411c2af73cd73812ef42a55bf8e52e40c261c271 --check
$ wc -l scripts/compact_pair_loop.py scripts/mailbox_writer.py
$ ! rg -n 'capability_baseline_runtime|protocol_effectiveness_report|route_capability|compact_state_mapping|capability_reducer|capability_v1_adapter|route-v2|kernel_activation|refs/protocol/kernel-activation|TaskPublicationStore|Lane-V-Scope' scripts coordination/bin AGENTS.md ARCHITECTURE.md coordination/README.md docs/protocol .agents/skills .codex/agents .claude/agents

Cursor at send: 0
