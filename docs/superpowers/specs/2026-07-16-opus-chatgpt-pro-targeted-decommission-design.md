# Opus and ChatGPT Pro Targeted Decommission Design

**Status:** Approved by the user-principal on 2026-07-16

**Bound repository head:** `bd71c61a4040e0cbeaffc8d79ec193716a901825`

## Goal

Remove the executable Opus review bridge and ChatGPT Pro consultation tool,
including their dedicated tests, skills, prompts, active protocol hooks, and
live routes. Preserve provider-neutral Lane V verification and retain existing
historical evidence as inert, content-addressed audit material.

## Motivation

Both provider integrations accumulated rigid state machines, provider-specific
authority contracts, receipt requirements, synchronized prompt surfaces, and
recovery routes that made ordinary use fragile. Their failure modes now consume
more coordination than the advisory value they provide. The program is moving
toward smaller, adaptable tools, so the correct short-term action is removal,
not another compatibility layer.

The decommission must not weaken generic Lane V. Independent verification,
structural trigger authority, exact reviewed ranges, atomic report publication,
and fail-closed handling of malformed new reports remain required.

## User-Principal Decision

The approved boundary is a targeted decommission:

- remove both executable provider tools;
- remove their dedicated tests, skills, prompts, and active hooks;
- retire the two live routes;
- preserve generic Lane V;
- preserve Git history, historical mailbox events, plans, specifications,
  logs, scope descriptors, completed packets, and local runtime evidence.

A full provenance purge is explicitly outside scope.

## Design Principles

1. **Delete provider behavior instead of disabling it.** No feature flag,
   dormant CLI, automatic fallback, compatibility shim, or hidden retry remains.
2. **Keep Lane V provider-neutral.** Verification authority comes from the
   reviewed range, descriptor, trigger, independent verifier, and published
   report—not a named model or receipt.
3. **Freeze historical evidence by digest.** Old provider-bearing reports remain
   readable as exact historical bytes but do not keep provider code executable.
4. **Retire routes before deleting their executors.** No live packet or newest
   handoff may lawfully instruct a seat to call a deleted tool.
5. **Preserve local evidence without inspecting or cleaning it.** Runtime files
   are not source code and are not part of this deletion.
6. **Prefer one provider-neutral path.** New Lane V reports use one schema and
   one publication transaction with no provider-specific branch.

## Architecture After Decommission

```text
director-owned candidate
  -> canonical descriptor and verify-request
  -> independent operator verification
  -> provider-neutral lane-v-report/v3
  -> structural authority validation
  -> atomic TaskPublicationStore publication
  -> coordinator closeout
```

There is no advisory provider call between operator analysis and report
publication. An unavailable external provider can no longer block Lane V,
because no external provider participates in Lane V.

## 1. Retire the Live Routes

The first implementation commit is coordinator-owned metadata only. It must:

- set the currently blocked ChatGPT Task-1 Operator packet and coordinator join
  packet to terminal `excepted` status;
- set the currently blocked Opus Stage-A Operator2 packet and coordinator join
  packet to terminal `excepted` status;
- retain existing `done` and `excepted` sibling packets unchanged;
- add `done_evidence` that cites one committed user-principal decommission event;
- publish one coordinator event naming the exact four packet transitions,
  preservation boundary, and prohibition on future provider invocation;
- create a newer owner handoff that supersedes the two live-looking owner
  handoffs without modifying or deleting those historical handoffs.

The coordinator event authorizes no production edit. The subsequent deletion
work is a separate implementation lane and separate commit range.

## 2. Delete the ChatGPT Pro Consultation Tool

Delete these active surfaces:

- `scripts/chatgpt_pro_consult.py`
- `tests/unit/test_chatgpt_pro_consult.py`
- `.agents/skills/chatgpt-pro-consultation/SKILL.md`
- `docs/protocol/codex/chatgpt-pro-consultation-acceptance.md`

Remove consultation behavior from:

- `scripts/codex_protocol_model.py`
- `tests/unit/test_protocol_prompt_sync.py`
- `AGENTS.md`
- `CLAUDE.md` when the current file contains a mirrored active rule
- `docs/protocol/codex/continuation.md`
- `.agents/skills/four-seat-protocol/SKILL.md`
- `.agents/skills/seat-director/SKILL.md`
- `.agents/skills/seat-operator/SKILL.md`
- `.agents/skills/seat-coordinator/SKILL.md`
- `.codex/agents/readiness-bridge.toml`
- `.codex/agents/protocol-director.toml`
- `.codex/agents/protocol-operator.toml`
- `.codex/agents/protocol-coordinator.toml`
- `.claude/agents/readiness-bridge.md`
- active onboarding or operating-doctrine text that instructs a seat to launch,
  prepare, send, accept, or reconcile a ChatGPT Pro consultation

Remove the ChatGPT lifecycle producer from the compact-state mapping and v1
adapter. Regenerate the affected fixtures and parity artifact in the same task
so no import or stale digest remains.

The human-relayed concept of seeking future external advice is not replaced in
this change. Active instructions must describe no currently available ChatGPT
Pro tool. A future implementation requires a new design and new code.

## 3. Delete the Opus Review Bridge

Delete these active surfaces:

- `scripts/opus_review_bridge.py`
- `scripts/opus_review_receipts.py`
- `tests/unit/test_opus_review_bridge.py`
- `tests/unit/test_opus_review_receipts.py`
- `scripts/prompts/opus_lane_v_advisory.md`
- `scripts/prompts/opus_lane_v_advisory.authority.583cdcb5b5129b629ae4ada21627a4fc5bab1b9c.json`

Remove provider invocation, standing paid-call authority, receipt reservation,
model checks, provider statuses, degradation reasons, and Opus attestation
fields from all operative surfaces.

The following shared files remain and are simplified rather than deleted:

- `scripts/verification_report_gate.py`
- `scripts/check_go_schema.py`
- `coordination/bin/send-event`
- `scripts/codex_protocol_model.py`
- `.agents/skills/seat-operator/SKILL.md`
- `.agents/skills/seat-operator/verification-report-format.md`
- `.claude/skills/seat-operator/verification-report-format.md`
- `.codex/agents/lane-v-verifier.toml`
- `.codex/agents/protocol-operator.toml`
- `.claude/agents/lane-v-verifier.md`
- their provider-neutral unit tests

`coordination/bin/send-event` continues to use the trusted report publisher, but
its trusted source set no longer includes either deleted Opus module.

## 4. Provider-Neutral Lane V Report Contract

All new reports use `lane-v-report/v3`. The exact ordered attestation fields are:

1. `Verification schema: lane-v-report/v3`
2. `Verification mode: independent-lane-v`
3. `Verification harness: lane-v:independent-verifier`
4. `Verification task ID: <canonical UUID>`
5. `Scope authority: <descriptor path>@sha256:<digest>`
6. `Trigger identity: <canonical shipping-commit or verify-request identity>`
7. `Reviewed head: <lowercase full Git SHA>`
8. `Reviewed base: <lowercase full Git SHA or none>`
9. `Review profile: independent-lane-v`
10. `Reviewer identity: <normalized seat or reviewer identifier>`

The existing H1, envelope, single `VERDICT: GO|NITS|FAIL`, canonical filename,
descriptor binding, trigger binding, reviewed-range checks, and report body
digest remain enforced.

The v3 parser has no provider field, receipt field, model field, cross-model
status, degradation reason, reconciliation guard, or finding-disposition JSON.
Findings and evidence stay ordinary report sections. The verifier's seat and
capacity separation provide independence; a model brand does not.

`TaskPublicationStore` remains the sole live publication state machine. New
reports publish through its existing no-replace, staged-index, recovery-aware
transaction. The Opus receipt store and its launch/reservation lifecycle are
deleted.

Minimal generic JSON canonicalization, path normalization, scope-reference
parsing, and trigger-identity validation move into
`scripts/verification_report_gate.py`. `scripts/check_go_schema.py` imports the
public parser from that module instead of importing a provider receipt module.
No new generic framework module is introduced.

## 5. Historical Report Preservation

All verification reports committed before the decommission cutover remain
unchanged. They are moved under one frozen historical baseline contract:

- create a committed manifest containing each historical report's canonical
  path and SHA-256 digest at the cutover commit;
- accept historical `lane-v-report/v1` and `lane-v-report/v2` bytes only when
  both path and digest exactly match that manifest;
- reject any new, modified, copied, renamed, or unlisted v1/v2 report;
- parse and structurally validate only new v3 reports with live code.

This preserves audit evidence without retaining executable Opus schemas or
receipt logic. `scripts/baselines/lane_v_report_v1.json` remains historical; the
new complete cutover manifest may replace its live role but must not rewrite its
recorded entries.

## 6. Compact-State and Capability Surfaces

Remove the following producer domains from the active compact mapping:

- `chatgpt`
- `opus_receipt`
- `provider_result`

Retain provider-neutral `local_verdict` and work-result semantics. Recompute the
mapping fixture, v1 adapter rules, replay corpus, misuse vectors, surface
inventory, and committed phase-2 parity artifact from the reduced producer set.

The implementation must update these surfaces atomically:

- `scripts/compact_state_mapping.py`
- `scripts/capability_v1_adapter.py`
- `tests/fixtures/compact_state_mapping/v1.json`
- `tests/fixtures/compact_kernel/v1_misuse_vectors.json`
- `tests/fixtures/compact_kernel/v1_surface_inventory.json`
- `tests/fixtures/compact_kernel/v1_to_v2_replay.json`
- `logs/capability-first/phase2b-shadow-parity.json`
- `tests/unit/test_compact_state_mapping.py`
- `tests/unit/test_capability_v1_adapter.py`
- `tests/unit/test_compact_kernel_surface_inventory.py`

No placeholder lifecycle or compatibility value replaces a deleted producer.

## 7. Operative Documentation and Decision Record

Update operative truth and role surfaces so a fresh seat cannot discover a
lawful instruction to use either provider tool:

- `AGENTS.md`
- `ARCHITECTURE.md`
- current continuation and adoption docs
- current seat skills
- Codex and Claude role prompts
- verification-report format mirrors
- protocol model renderers and synchronization tests

Append a new decision to `DECISIONS.md` that supersedes the active effect of the
Opus and ChatGPT Pro decisions. Prior decision entries remain immutable.

Historical mailbox events, plans, specifications, handoffs, logs, scope
descriptors, and completed capacity packets are not rewritten to remove provider
names. The new coordinator event and newest owner handoff make them inert.

## 8. Local Runtime Evidence

Do not inspect, delete, rewrite, stage, or commit:

- `.codex/runtime/chatgpt-pro-consultations.json`
- `.codex/runtime/chatgpt-pro-consultations.json.lock`
- `.codex/runtime/opus-review-receipts/`
- any provider approval or execution residue outside tracked source

Existing ignore rules for those exact evidence paths may remain with a comment
that they protect decommissioned local audit residue. They grant no executable
authority and are excluded from active-reference absence checks.

## 9. Error Handling and Fail-Closed Behavior

- A new v1 or v2 report that is not in the cutover manifest fails.
- A changed historical report digest fails.
- A v3 report containing provider or receipt attestation fields fails as an
  unknown-field violation.
- An active instruction, skill, prompt, agent, or script that imports or invokes
  either deleted tool fails the operative-surface absence test.
- A live capacity route that names either provider fails the decommission gate.
- There is no retry, fallback provider, manual relay, receipt fabrication,
  degraded-provider path, or compatibility environment variable.

## 10. Implementation Authority and Sequencing

The work is large and cross-cutting, so it follows separate reviewable tasks:

1. coordinator retires the two live routes and publishes the decommission handoff;
2. implementation owner removes ChatGPT Pro and compact-mapping dependencies;
3. implementation owner introduces provider-neutral report v3 and removes Opus;
4. implementation owner removes operative documentation and prompt hooks;
5. independent spec reviewer checks the complete deletion range;
6. independent code-quality reviewer checks the complete deletion range;
7. Operator verifies the reviewed head through provider-neutral Lane V;
8. coordinator closes the decommission only after Operator GO.

No task invokes either provider. No push, remote publication, branch cleanup,
runtime cleanup, or historical-evidence cleanup is authorized by this design.

## 11. Verification Strategy

Focused tests must prove:

- `lane-v-report/v3` accepts a canonical provider-neutral GO, NITS, and FAIL;
- malformed field order, duplicate fields, stale triggers, wrong reviewed heads,
  and mismatched descriptors fail;
- provider and receipt fields are rejected from v3;
- historical reports pass only by exact cutover path and digest;
- altered or new v1/v2 reports fail;
- publication remains atomic, no-replace, and recoverable;
- compact mapping contains no deleted producer domains;
- prompt synchronization contains no active provider invocation contract;
- the two retired cycles are terminal and capacity-valid;
- no tracked executable or operative surface imports, invokes, or routes either
  deleted tool.

Completion requires fresh successful output from:

```bash
env -u GIT_INDEX_FILE .venv/bin/python -m pytest tests/unit -q
env -u GIT_INDEX_FILE .venv/bin/python scripts/check_coordination.py
env -u GIT_INDEX_FILE .venv/bin/python scripts/protocol_capacity_board.py --wave 2
env -u GIT_INDEX_FILE .venv/bin/python scripts/protocol_doctor.py --wave 2
env -u GIT_INDEX_FILE .venv/bin/python scripts/check_doc_claims.py --sha-refs
env -u GIT_INDEX_FILE .venv/bin/python scripts/ci_smoke.py
env -u GIT_INDEX_FILE git diff --check
```

The final review must also run a tracked-file search over executable and
operative paths. Historical evidence directories and the exact local-runtime
ignore entries are the only allowed provider-name residue.

## Acceptance Criteria

The decommission is complete only when:

1. both executable provider tools and dedicated tests are absent;
2. the ChatGPT Pro skill and provider prompts are absent;
3. no active role, skill, protocol model, continuation guide, or command can
   invoke either provider;
4. the two live cycles are terminally retired;
5. generic Lane V publishes and validates v3 reports without provider state;
6. historical reports remain byte-identical and verifiable by frozen manifest;
7. compact-state fixtures and parity evidence match the reduced producer set;
8. local runtime evidence remains untouched;
9. independent spec and code-quality reviews report no blocking finding;
10. Operator returns GO for the exact deletion range;
11. the complete verification command set passes;
12. no push or external side effect occurs without separate authorization.
