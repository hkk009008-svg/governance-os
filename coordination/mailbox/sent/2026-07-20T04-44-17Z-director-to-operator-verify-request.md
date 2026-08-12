# Director → Operator: coordination reliability verification

**When:** 2026-07-20T04:44:17Z · **From:** director (online)

Event type: verify-request
Reviewed repository: /Users/hyungkoookkim/Pipeline
Reviewed head: 6fe3afc3e07df3e688e2bdd93a10a16645d96bd2
Reviewed base: 8e27847b8f05bb4425df3d7b1f2903590f7949a3
Author seat: director
Author model: gpt-5.6-sol
Assigned operator: operator
Intended reviewer model: gpt-5.6-terra
Task-board: pipeline-coordination-reliability-2026-07-20
Task ID: pipeline-coordination-reliability-implementation-review
Coordinator route: coordination/mailbox/sent/2026-07-20T03-19-29Z-coordinator-to-all-coordination.md@8e27847b8f05bb4425df3d7b1f2903590f7949a3
Implementation commits: 9ba9817811fd4c9d6509a736f91c44a3190e9bca, ed518f60fc4fc7941bc2d67064827ac44fa2025c, 4e23974ea901a3a8fc5744c7bf9bed4c325794e2, 898bc639c6d71bd70bf3f00bce0bceeee56bd0ee, 6fe3afc3e07df3e688e2bdd93a10a16645d96bd2

## Outcome

Independently inspect the exact actual range 8e27847b8f05bb4425df3d7b1f2903590f7949a3..6fe3afc3e07df3e688e2bdd93a10a16645d96bd2 and issue GO only if all three coordination-reliability corrections are acceptable with no unresolved hard boundary:

1. Malformed route diagnostics remain globally visible but resume decisions include same-task and unattributable issues while excluding only issues unambiguously attributed to another task; exact fast resume resolves the expected task and no historical, forked, ineffective, changed, or malformed same-task route can become authoritative.
2. FAST PASS and evidence-backed FULL fallback render the same complete authority-free evidence capsule; fallback reuses collected guidance for ordinary actions without a second route/state collection or mutation, while fresh startup retains validated route reading and legacy aliases remain readable.
3. The executable model and thin adapters require prior exact authority for known-context scoped fixed-writer launch, forbid generic escalation/direct edits/alternate writers/TMPDIR or fence weakening, and require wait-first per-target-cursor monitoring whose handler-unavailable fallback cannot redispatch, replace a task, change seats, or ask the user to relay a trigger.

Confirm the actual range changes exactly the eleven paths below; adds no registry, broker, polling journal, dependency, schema, service, product behavior, or external-effect authority; and leaves coordination/bin/send-event, scripts/mailbox_writer.py, pyproject.toml, uv.lock, ARCHITECTURE.md, and every product repository unchanged. The Director's final advisory actual-diff re-review found no remaining Critical or Important issue after correction commit 6fe3afc3e07df3e688e2bdd93a10a16645d96bd2. Formal acceptance belongs only to the assigned Operator.

## Target Allowed Paths

- scripts/route_lineage.py
- tests/unit/test_route_lineage.py
- scripts/ledger_start_guard.py
- tests/unit/test_ledger_fast_resume.py
- scripts/codex_protocol_model.py
- tests/unit/test_protocol_prompt_sync.py
- AGENTS.md
- .agents/skills/four-seat-protocol/SKILL.md
- .agents/skills/seat-coordinator/SKILL.md
- docs/protocol/codex/continuation.md
- docs/protocol/codex/ledger-cli-adoption.md

## Verification Commands

- env -u GIT_INDEX_FILE .venv/bin/python -m pytest tests/unit/test_route_lineage.py -q
- env -u GIT_INDEX_FILE .venv/bin/python -m pytest tests/unit/test_ledger_fast_resume.py -q
- env -u GIT_INDEX_FILE .venv/bin/python -m pytest tests/unit/test_protocol_prompt_sync.py -q
- env -u GIT_INDEX_FILE .venv/bin/python -m pytest tests/unit/test_codex_ledger_bridge.py tests/unit/test_protocol_doc_integrity.py -q
- env -u GIT_INDEX_FILE .venv/bin/python -m pytest tests/unit/test_coordination_tooling.py tests/unit/test_mailbox_writer.py -q
- env -u GIT_INDEX_FILE .venv/bin/python scripts/ci_smoke.py

Fresh Director results at reviewed head: 40 passed; 42 passed; 41 passed; 31 passed; 15 passed; governance smoke OK. Also inspect git diff --check, the exact changed-path set, all five commits, protected-file preservation, canonical/legacy route grammar, pure evidence/action rendering, architecture anchors 456/684/718, and the actual model assignment order.

## Adversarial Question

Can unrelated malformed history, same-task or unattributable malformed history, writer-escalation wording, evidence fallback, or monitoring failure bypass task scoping, fail-closed authority, single-collection truth, or dispatch deduplication? Issue NITS or FAIL with exact evidence if any such bypass or other material boundary exists.

## Boundaries

This request authorizes Operator on gpt-5.6-terra to perform independent read-only actual-range inspection, run only the listed local tests and smoke with their normal synthetic scratch state, and publish exactly one canonical committed verification-report. It does not authorize implementation or repair, direct mailbox edits, alternate writers, dependency installation, service/provider launch, product-repository access or mutation, private data, push, merge, branch integration, deployment, lock or fence action, cursor consumption, spend, cleanup, reset, rebase, amend, or any other external effect. A later GO grants none of those actions.

## Finding Refs

Cursor at send: 0
