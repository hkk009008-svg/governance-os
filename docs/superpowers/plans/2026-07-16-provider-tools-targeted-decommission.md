# Provider Tools Targeted Decommission Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking. Live coordinator, director, and operator authority remains with the routed seats; advisory subagents inherit no mailbox, commit, push, receipt, or verdict authority.

**Goal:** Delete the executable ChatGPT Pro consultation and Opus review subsystems, retire their provider-dependent routes, and leave one provider-neutral, fail-closed Lane V report and publication path while preserving historical audit evidence.

**Architecture:** The coordinator first terminally retires the provider-dependent cycles and routes one sequential two-owner decommission. Director removes provider lifecycle producers and ChatGPT Pro; Director2 then replaces Lane V v2 with provider-neutral v3, freezes all pre-v3 reports by path and digest, removes Opus, and converges operative surfaces. Two independent reviews precede one formal Operator Lane V pass, after which the coordinator closes the cycle without pushing or touching local runtime evidence.

**Tech Stack:** Python 3.11/3.13/3.14-compatible standard library, pytest, Bash, JSON capacity packets and scope descriptors, Markdown mailbox events, Git content addressing, and the existing `TaskPublicationStore` atomic publisher.

## Global Constraints

- The approved design is `docs/superpowers/specs/2026-07-16-opus-chatgpt-pro-targeted-decommission-design.md` at commit `66c73f07c2cedb998a6709db9b5a2ff4ce47812e`.
- The two removals stay in one plan because they share `scripts/compact_state_mapping.py`, `scripts/capability_v1_adapter.py`, `scripts/codex_protocol_model.py`, `scripts/verification_report_gate.py`, `scripts/check_go_schema.py`, and synchronized role/report surfaces. Tasks are sequential at every shared path.
- R-ORCH applies. Each implementation task receives a fresh implementer plus a fresh spec reviewer and code-quality reviewer before the next task begins. Task 6 asks two different full-range questions and is not a repeat of those per-task reviews.
- Do not invoke ChatGPT Pro, Claude, Opus, an in-app browser, a provider CLI, a paid API, a receipt reservation, or a provider retry at any point in this plan.
- Do not inspect, delete, rewrite, stage, or commit `.codex/runtime/chatgpt-pro-consultations.json`, `.codex/runtime/chatgpt-pro-consultations.json.lock`, `.codex/runtime/opus-review-receipts/`, or any provider approval/execution residue outside tracked source.
- Preserve Git history and all existing mailbox events, plans, specifications, logs, scope descriptors, completed packets, and historical handoffs byte-for-byte. Only the four explicitly blocked provider-cycle packets are transitioned in Task 1.
- Preserve `scripts/baselines/lane_v_report_v1.json` byte-for-byte as historical evidence. Create `scripts/baselines/lane_v_reports_pre_v3.json` as the complete live cutover manifest.
- All new verification reports use exactly `lane-v-report/v3`, `independent-lane-v`, and `lane-v:independent-verifier`; no provider, receipt, model, cross-model, degradation, authorization, reconciliation, or finding-disposition attestation field remains.
- `TaskPublicationStore` remains the sole live publication state machine. Do not add a replacement compatibility module, disabled provider flag, fallback transport, manual relay, retry path, or generic framework.
- All ordinary Git and test commands begin with `env -u GIT_INDEX_FILE`. Use explicit pathspecs for commits and `git add -f` for ignored sent-mailbox artifacts.
- Coordinator commits contain metadata only. Director/Director2 commits contain implementation and operative documentation. Operator/Operator2 never repair the reviewed diff.
- Commit, push, merge, provider launch, runtime cleanup, and external publication remain separate authorities. This plan authorizes commits only; it authorizes no push, merge, provider call, or cleanup.
- Before every state-asserting write or verdict, refresh `git log --oneline -3`, seat mail, packet state, and the capacity board. Stop on peer WIP in an overlapping path.
- `scripts/check_doc_claims.py --sha-refs` currently has a known repository-wide historical baseline. The decommission must add zero new drift; it does not authorize unrelated cleanup.

## File Structure and Ownership

### Coordinator metadata

- Modify the four blocked packets named in Task 1.
- Create five `2026-07-16-provider-tools-decommission-*.json` packets for the new cycle.
- Create one coordinator route event and `docs/HANDOFF-owner-2026-07-16-provider-tool-decommission.md`.
- At closeout, modify only the five new packets and create one closeout event/handoff.

### Compact-state contraction

- Modify `scripts/compact_state_mapping.py` and `scripts/capability_v1_adapter.py` to retain only `capacity`, `capability`, `local_verdict`, and `work_result` producer domains.
- Regenerate the five committed fixture/parity artifacts listed in Task 2.
- Modify the three compact/capability unit-test modules listed in Task 2.

### ChatGPT Pro deletion

- Delete the executable, dedicated test, skill, and acceptance document listed in Task 3.
- Remove consultation state, renderers, validation, triggers, paths, and instructions from the exact active role/skill/doc surfaces listed in Task 3.

### Provider-neutral Lane V and Opus deletion

- Keep `scripts/verification_report_gate.py`, `scripts/check_go_schema.py`, `coordination/bin/send-event`, and their provider-neutral tests.
- Move the minimal generic descriptor/path/JSON/publication helpers from `scripts/opus_review_receipts.py` into `scripts/verification_report_gate.py`, then delete both Opus modules, dedicated tests, and prompt assets.
- Keep the existing H1/envelope/verdict/filename/descriptor/trigger/range/body-digest rules and the `TaskPublicationStore` transaction.

### Operative convergence

- Update `AGENTS.md`, `ARCHITECTURE.md`, `DECISIONS.md`, current continuation/adoption/doctrine docs, seat skills, agent prompts, and verification-report mirrors.
- Add a regression test that checks explicit executable/operative roots and launchable capacity packets while excluding historical evidence and local runtime residue.

---

### Task 1: Retire Provider Routes and Open the Decommission Cycle

**Owner:** Coordinator

**Files:**

- Modify: `coordination/capacity/packets/2026-07-16-chatgpt-local-reprepare-task1-operator-lanev.json`
- Modify: `coordination/capacity/packets/2026-07-16-chatgpt-local-reprepare-task1-coordinator-join.json`
- Modify: `coordination/capacity/packets/2026-07-15-pipeline-opus-transport-first-recovery-stage-a-operator2-lanev.json`
- Modify: `coordination/capacity/packets/2026-07-15-pipeline-opus-transport-first-recovery-stage-a-coordinator-join.json`
- Create: `coordination/capacity/packets/2026-07-16-provider-tools-decommission-director-implementation.json`
- Create: `coordination/capacity/packets/2026-07-16-provider-tools-decommission-director2-implementation.json`
- Create: `coordination/capacity/packets/2026-07-16-provider-tools-decommission-operator2-quality-preflight.json`
- Create: `coordination/capacity/packets/2026-07-16-provider-tools-decommission-operator-lanev.json`
- Create: `coordination/capacity/packets/2026-07-16-provider-tools-decommission-coordinator-join.json`
- Create: `docs/HANDOFF-owner-2026-07-16-provider-tool-decommission.md`
- Create: the one canonical sent-mailbox path returned in `ROUTE_EVENT`

**Interfaces:**

- Consumes: user-principal deletion approval, approved design commit `66c73f07c2cedb998a6709db9b5a2ff4ce47812e`, the four exact blocked packets, and current capacity/mailbox state.
- Produces: one terminal retirement event, five capacity-valid sequential packets, a newest owner handoff, and a metadata-only commit whose SHA becomes `DECOMMISSION_BASE` for Task 7.

- [ ] **Step 1: Refresh coordinator truth before editing**

Run:

```bash
env -u GIT_INDEX_FILE git log --oneline -3
env -u GIT_INDEX_FILE .venv/bin/python \
  .agents/skills/four-seat-protocol/scripts/seat_status.py coordinator --wave 2
env -u GIT_INDEX_FILE .venv/bin/python scripts/protocol_capacity_board.py --wave 2
env -u GIT_INDEX_FILE git status --short
```

Expected: the four named packets are still `blocked`; no newer event has already retired either cycle; no uncommitted peer edit overlaps the eleven exact metadata/handoff paths. Read every surfaced coordinator mailbox body without consuming it.

- [ ] **Step 2: Generate the one decommission route event path**

Run once:

```bash
SEND_OUTPUT="$(coordination/bin/send-event coordinator all coordination \
  "retire provider routes and route targeted decommission" <<'EOF'
User-principal decision: permanently retire the executable ChatGPT Pro consultation and Opus review subsystems while preserving generic Lane V and historical audit evidence.

Packet transitions:
- operator-chatgpt-local-reprepare-task1-lanev: blocked -> excepted
- coord-chatgpt-local-reprepare-task1-join: blocked -> excepted
- operator2-pipeline-opus-transport-first-recovery-stage-a-lanev: blocked -> excepted
- coord-pipeline-opus-transport-first-recovery-stage-a-join: blocked -> excepted

Preservation boundary: keep Git history, historical mailbox events, plans, specifications, logs, scope descriptors, completed packets, historical handoffs, and ignored local runtime evidence unchanged.

Execution boundary: no future task may invoke ChatGPT Pro, Claude, Opus, a provider CLI, an in-app browser, a paid API, a provider retry, or an Opus receipt lifecycle. Director owns compact-state contraction and ChatGPT deletion. Director2 starts only after Director finishes and owns provider-neutral Lane V v3, Opus deletion, and operative convergence. Operator2 asks the bounded quality-preflight question. Operator performs the final provider-neutral Lane V pass. Coordinator closes only after GO.

Exact Next Trigger: coordinator completes the four packet transitions, creates the five decommission packets and newest owner handoff, validates this route, and commits metadata only; then Director starts Task 2 from that exact commit.
EOF
)"
ROUTE_EVENT="${SEND_OUTPUT#created }"
ROUTE_EVENT="${ROUTE_EVENT%% *}"
test -f "$ROUTE_EVENT"
printf '%s\n' "$ROUTE_EVENT"
```

Expected: one canonical coordinator-to-all event path is printed and the event contains exactly one terminal `Exact Next Trigger` section.

- [ ] **Step 3: Apply the four exact terminal transitions**

In each of the four existing packets, preserve every field except:

```json
{
  "status": "excepted",
  "done_evidence": [
    "${ROUTE_EVENT} at the metadata-only retirement commit; user-principal decommission supersedes this provider-dependent cycle"
  ]
}
```

Do not change their IDs, cycle names, acceptance history, reviewed SHAs, descriptor paths, sibling packet states, or historical handoffs. The route-event path is runtime-generated, not guessed.

- [ ] **Step 4: Create the five exact decommission packets**

Use cycle `provider-tools-targeted-decommission-2026-07-16`, wave `2`, no row IDs, and no lock keys. The packet matrix is:

| Packet ID | Owner/type | Initial status | Dependencies | Terminal deliverable |
|---|---|---|---|---|
| `director-provider-tools-decommission-implementation` | `director` / `director-implementation` | `ready` | none | Tasks 2-3 committed and reviewed |
| `director2-provider-tools-decommission-implementation` | `director2` / `director-implementation` | `blocked` | Director packet | Tasks 4-5 committed and reviewed |
| `operator2-provider-tools-decommission-quality-preflight` | `operator2` / `operator-preflight` | `blocked` | Director2 packet | Task 6 quality finding event |
| `operator-provider-tools-decommission-lanev` | `operator` / `operator-verification` | `blocked` | Operator2 packet | Task 7 v3 GO/NITS/FAIL |
| `coord-provider-tools-decommission-join` | `coordinator` / `coordinator-join` | `blocked` | Operator packet | Task 8 closeout |

Every packet must contain these exact common acceptance statements:

```text
No ChatGPT Pro, Claude, Opus, provider CLI, in-app browser, paid API, provider retry, or provider receipt action is authorized.
Historical evidence and ignored local runtime evidence are read-only and outside the write set.
Commit, push, merge, provider launch, runtime cleanup, and external publication are separate authorities; this packet authorizes no push, merge, provider call, or cleanup.
```

Set `allowed_paths` and `scope_files` to the exact task file lists in this plan. Director2's packet depends on Director because the owners share compact/report model surfaces. Operator's packet remains blocked until the fixed descriptor `coordination/verification/scopes/11249ae3-1a0f-45c0-aa90-7d558537b001.json` and one canonical verify-request are committed.

- [ ] **Step 5: Create the newest owner handoff**

Write `docs/HANDOFF-owner-2026-07-16-provider-tool-decommission.md` with these exact sections:

```markdown
# Owner Handoff: Provider Tool Targeted Decommission

## Supersedes

- `docs/HANDOFF-owner-2026-07-16-opus-stage-a.md`
- the newest ChatGPT Task-1 owner handoff resolved by `git log --all -- docs/HANDOFF-owner-*chatgpt*.md`

## Active Ownership

- Coordinator: route retirement, capacity, activation, and closeout metadata only.
- Director: Tasks 2-3.
- Director2: Tasks 4-5 after Director completes.
- Operator2: Task 6 bounded quality preflight; no repair.
- Operator: Task 7 provider-neutral Lane V; no repair.

## Preservation Boundary

Historical Git, mailbox, plan, specification, log, descriptor, packet, handoff, and ignored local runtime evidence remains unchanged.

## Prohibited Actions

No provider invocation, browser send, paid API, retry, fallback, receipt mutation, runtime cleanup, push, or merge.

## Exact Next Trigger

Director starts Task 2 only after the coordinator route commit passes the wave-2 capacity validator.
```

Resolve and insert the exact ChatGPT handoff path; if none exists, state `No dedicated ChatGPT owner handoff exists; the terminal coordinator event supersedes its live packets.`

- [ ] **Step 6: Validate and commit metadata only**

Run:

```bash
env -u GIT_INDEX_FILE .venv/bin/python scripts/protocol_capacity_board.py --wave 2
env -u GIT_INDEX_FILE .venv/bin/python scripts/protocol_capacity_board.py \
  --wave 2 --validate-route "$ROUTE_EVENT"
env -u GIT_INDEX_FILE .venv/bin/python scripts/check_coordination.py
env -u GIT_INDEX_FILE git diff --check
```

Expected: all commands pass and the staged set contains exactly four modified legacy packets, five new decommission packets, one handoff, and one route event.

Commit with explicit pathspecs and subject:

```text
coord(coordinator): retire provider routes and open decommission
```

Record the resulting full SHA as `DECOMMISSION_BASE`. Do not stage ambient untracked files.

### Task 2: Remove Provider Lifecycle Producers from Compact State

**Owner:** Director

**Files:**

- Modify: `scripts/compact_state_mapping.py`
- Modify: `scripts/capability_v1_adapter.py`
- Modify: `tests/fixtures/compact_state_mapping/v1.json`
- Modify: `tests/fixtures/compact_kernel/v1_misuse_vectors.json`
- Modify: `tests/fixtures/compact_kernel/v1_surface_inventory.json`
- Modify: `tests/fixtures/compact_kernel/v1_to_v2_replay.json`
- Modify: `logs/capability-first/phase2b-shadow-parity.json`
- Modify: `tests/unit/test_compact_state_mapping.py`
- Modify: `tests/unit/test_capability_v1_adapter.py`
- Modify: `tests/unit/test_compact_kernel_surface_inventory.py`

**Interfaces:**

- Consumes: the Task 1 route commit and current producer constants.
- Produces: compact/capability fixtures with exactly four producer domains—`capacity`, `capability`, `local_verdict`, `work_result`—and no import of either provider module. Tasks 3-4 may then delete provider modules without breaking compact imports.

- [ ] **Step 1: Write failing producer-contraction tests**

Replace provider-backed imports and expectations in `tests/unit/test_compact_state_mapping.py` with:

```python
EXPECTED_SOURCE_DOMAINS = {
    "capacity",
    "capability",
    "local_verdict",
    "work_result",
}
REMOVED_SOURCE_DOMAINS = {"chatgpt", "opus_receipt", "provider_result"}


def test_fixture_contains_only_live_provider_neutral_domains() -> None:
    fixture = _load(FIXTURE_PATH)
    assert set(fixture["source_values"]) == EXPECTED_SOURCE_DOMAINS
    assert {row["domain"] for row in fixture["rows"]} == EXPECTED_SOURCE_DOMAINS


@pytest.mark.parametrize("domain", sorted(REMOVED_SOURCE_DOMAINS))
def test_removed_provider_domain_fails_closed(domain: str) -> None:
    with pytest.raises(compact_state_mapping.StateMappingError, match="unknown domain"):
        compact_state_mapping.meaning_for(domain, "removed", context={})
```

In `tests/unit/test_capability_v1_adapter.py`, assert no replay case or parity case ID starts with `mapping:chatgpt-`, `mapping:opus-`, or `mapping:provider-`. In `tests/unit/test_compact_kernel_surface_inventory.py`, remove the two provider component IDs and assert neither deleted script is a production module, dependency, or orphan.

- [ ] **Step 2: Run the contraction tests and observe failure**

Run:

```bash
env -u GIT_INDEX_FILE .venv/bin/python -m pytest \
  tests/unit/test_compact_state_mapping.py \
  tests/unit/test_capability_v1_adapter.py \
  tests/unit/test_compact_kernel_surface_inventory.py -q
```

Expected: FAIL because the current source/fixtures still expose `chatgpt`, `opus_receipt`, and `provider_result`.

- [ ] **Step 3: Contract the production mapping and adapter**

In `scripts/compact_state_mapping.py`:

- delete imports of `chatgpt_pro_consult`, `opus_review_bridge`, and `opus_review_receipts`;
- remove those three entries from `_producer_values()`;
- delete `_chatgpt_meaning`, `_opus_receipt_meaning`, and `_provider_result_meaning`;
- delete their branches from `_accepted_context_keys()` and `meaning_for()`;
- replace the Opus-derived verdict union with the provider-neutral closed set `_LOCAL_VERDICTS = frozenset({"GO", "NITS", "FAIL", "unable_to_verify"})` and retain the existing mapping semantics for all four values.

The final dispatch must be exactly:

```python
def meaning_for(
    domain: str,
    value: str,
    *,
    context: Mapping[str, object] | None = None,
) -> StateMeaning:
    normalized_context = _context(context)
    if domain == "capacity":
        return _capacity_meaning(value, normalized_context)
    if domain == "capability":
        return _capability_meaning(value, normalized_context)
    if domain == "local_verdict":
        return _local_verdict_meaning(value, normalized_context)
    if domain == "work_result":
        return _work_result_meaning(value, normalized_context)
    raise StateMappingError("unknown domain")
```

In `scripts/capability_v1_adapter.py`, delete `_chatgpt_failure_rules()` and every legacy mapping rule whose key domain is one of the three removed domains. Retain all capacity, capability, local-verdict, work-result, history, misuse, resolver, and replay validation logic.

- [ ] **Step 4: Regenerate the committed fixtures mechanically**

Apply one deterministic transformation, then inspect every resulting diff:

```python
from hashlib import sha256
import json
from pathlib import Path

removed_domains = {"chatgpt", "opus_receipt", "provider_result"}
removed_prefixes = ("mapping:chatgpt-", "mapping:opus-", "mapping:provider-")

mapping_path = Path("tests/fixtures/compact_state_mapping/v1.json")
mapping = json.loads(mapping_path.read_text(encoding="utf-8"))
mapping["source_values"] = {
    key: value for key, value in mapping["source_values"].items()
    if key not in removed_domains
}
mapping["rows"] = [
    row for row in mapping["rows"] if row["domain"] not in removed_domains
]
mapping_path.write_text(json.dumps(mapping, indent=2) + "\n", encoding="utf-8")

misuse_path = Path("tests/fixtures/compact_kernel/v1_misuse_vectors.json")
misuse = json.loads(misuse_path.read_text(encoding="utf-8"))
misuse["vectors"] = [
    vector for vector in misuse["vectors"]
    if vector["id"] not in {"duplicate_advisory_dispatch", "fallback_advisory_dispatch"}
]
misuse_path.write_text(json.dumps(misuse, indent=2) + "\n", encoding="utf-8")

replay_path = Path("tests/fixtures/compact_kernel/v1_to_v2_replay.json")
replay = json.loads(replay_path.read_text(encoding="utf-8"))
replay["case_manifest"] = [
    case_id for case_id in replay["case_manifest"]
    if not case_id.startswith(removed_prefixes)
]
replay["cases"] = [
    case for case in replay["cases"]
    if not case["id"].startswith(removed_prefixes)
]
replay["deferred_phase3_misuse_ids"] = [
    item for item in replay["deferred_phase3_misuse_ids"]
    if item not in {"duplicate_advisory_dispatch", "fallback_advisory_dispatch"}
]
for path in (mapping_path, misuse_path):
    replay["sources"][path.as_posix()] = "sha256:" + sha256(path.read_bytes()).hexdigest()
replay_path.write_text(json.dumps(replay, indent=2) + "\n", encoding="utf-8")
```

Use this only as a bulk mechanical fixture rewrite. Update `v1_surface_inventory.json` by removing the exact `chatgpt_guard_and_browser_executor` and `opus_reservation_and_bridge` components and their dependency/orphan entries. Then run the adapter CLI and replace the parity artifact with its single canonical JSON line:

```bash
env -u GIT_INDEX_FILE .venv/bin/python scripts/capability_v1_adapter.py \
  --check-corpus tests/fixtures/compact_kernel/v1_to_v2_replay.json \
  > /tmp/provider-tools-phase2b-shadow-parity.json
env -u GIT_INDEX_FILE .venv/bin/python -m json.tool \
  /tmp/provider-tools-phase2b-shadow-parity.json >/dev/null
```

Copy the validated single line into `logs/capability-first/phase2b-shadow-parity.json` using `apply_patch`, then delete the temporary file. Do not add a fixture generator to production.

- [ ] **Step 5: Run focused and import-absence verification**

Run:

```bash
env -u GIT_INDEX_FILE .venv/bin/python -m pytest \
  tests/unit/test_compact_state_mapping.py \
  tests/unit/test_capability_v1_adapter.py \
  tests/unit/test_compact_kernel_surface_inventory.py -q
! rg -n 'chatgpt_pro_consult|opus_review_bridge|opus_review_receipts|"chatgpt"|"opus_receipt"|"provider_result"' \
  scripts/compact_state_mapping.py scripts/capability_v1_adapter.py \
  tests/fixtures/compact_state_mapping/v1.json \
  tests/fixtures/compact_kernel/v1_to_v2_replay.json \
  logs/capability-first/phase2b-shadow-parity.json
env -u GIT_INDEX_FILE git diff --check
```

Expected: all focused tests pass; the absence search exits 1 with no matches; diff check prints nothing.

- [ ] **Step 6: Commit the compact contraction**

Commit only the ten listed files with subject:

```text
refactor: remove provider lifecycle compact states
```

Fresh spec review question: does the commit remove exactly the three provider domains while preserving every generic producer? Fresh quality review question: are fixtures, replay digests, parity output, and source imports mutually consistent?

### Task 3: Delete ChatGPT Pro and Its Active Hooks

**Owner:** Director

**Files:**

- Delete: `scripts/chatgpt_pro_consult.py`
- Delete: `tests/unit/test_chatgpt_pro_consult.py`
- Delete: `.agents/skills/chatgpt-pro-consultation/SKILL.md`
- Delete: `docs/protocol/codex/chatgpt-pro-consultation-acceptance.md`
- Modify: `scripts/codex_protocol_model.py`
- Modify: `tests/unit/test_protocol_prompt_sync.py`
- Modify: `AGENTS.md`
- Modify: `docs/protocol/codex/continuation.md`
- Modify: `.agents/skills/four-seat-protocol/SKILL.md`
- Modify: `.agents/skills/seat-director/SKILL.md`
- Modify: `.agents/skills/seat-operator/SKILL.md`
- Modify: `.agents/skills/seat-coordinator/SKILL.md`
- Modify: `.agents/skills/seat-operator/verification-report-format.md`
- Modify: `.claude/skills/seat-operator/verification-report-format.md`
- Modify: `.codex/agents/readiness-bridge.toml`
- Modify: `.codex/agents/lane-v-verifier.toml`
- Modify: `.codex/agents/protocol-director.toml`
- Modify: `.codex/agents/protocol-operator.toml`
- Modify: `.codex/agents/protocol-coordinator.toml`
- Modify: `.claude/agents/readiness-bridge.md`
- Modify: `.claude/agents/lane-v-verifier.md`
- Modify: `docs/protocol/threeway/ANTIGRAVITY-ADOPTION.md`
- Modify: `docs/protocol/threeway/ARCHITECTURE-DIAGRAM.md`
- Modify: `docs/protocol/threeway/ONBOARDING.md`
- Modify: `docs/protocol/threeway/UNIFIED-OPERATING-DOCTRINE.md`

**Interfaces:**

- Consumes: Task 2's provider-free compact sources.
- Produces: no tracked ChatGPT Pro executable, dedicated test, skill, acceptance procedure, model contract, activation validator, role prompt, or operative launch instruction.

- [ ] **Step 1: Replace consultation contract tests with deletion tests**

Delete the consultation-specific test block in `tests/unit/test_protocol_prompt_sync.py` and add:

```python
CHATGPT_DELETED_PATHS = (
    "scripts/chatgpt_pro_consult.py",
    "tests/unit/test_chatgpt_pro_consult.py",
    ".agents/skills/chatgpt-pro-consultation/SKILL.md",
    "docs/protocol/codex/chatgpt-pro-consultation-acceptance.md",
)


def test_chatgpt_pro_executable_surface_is_deleted() -> None:
    for relative in CHATGPT_DELETED_PATHS:
        assert not (ROOT / relative).exists(), relative


def test_protocol_model_has_no_chatgpt_consultation_contract() -> None:
    source = (ROOT / "scripts/codex_protocol_model.py").read_text(encoding="utf-8")
    forbidden = (
        "render_chatgpt_pro_consultation",
        "chatgpt_pro_consultation_default",
        "validate_chatgpt_pro_activation_evidence",
        "chatgpt_pro_guard_manifest_hash",
    )
    assert all(token not in source for token in forbidden)
```

- [ ] **Step 2: Run the new tests and observe failure**

Run:

```bash
env -u GIT_INDEX_FILE .venv/bin/python -m pytest \
  tests/unit/test_protocol_prompt_sync.py -q
```

Expected: FAIL because the four deleted paths and model functions still exist.

- [ ] **Step 3: Delete executable assets and strip the protocol model**

Delete the four exact files. In `scripts/codex_protocol_model.py`, remove:

- consultation modes, default/transport constants, trigger rules, runtime field, and runtime inference;
- `render_chatgpt_pro_consultation()` and every renderer call;
- `_chatgpt_pro_git`, `_chatgpt_pro_field`, `chatgpt_pro_guard_manifest_hash`, `validate_chatgpt_pro_activation_evidence`, and `chatgpt_pro_consultation_default`;
- activation/guard manifest paths and consultation acceptance commands;
- command output that prints the consultation contract.

Keep the risk-tier router, seat model, mailbox law, user-gated side effects, and provider-neutral independent verification rules unchanged.

- [ ] **Step 4: Remove active consultation instructions**

From each listed skill, role prompt, continuation/adoption/doctrine document, and `AGENTS.md`, remove text that tells a seat to trigger, prepare, send, import, reconcile, retry, or block on ChatGPT Pro. Do not add a replacement external-advice workflow. Historical plans, mailbox events, logs, and handoffs are excluded.

The new operative statement where context is needed is:

```text
No ChatGPT Pro consultation tool is installed in this repository. External advisory work requires a separately approved design and implementation; it grants no protocol or side-effect authority.
```

- [ ] **Step 5: Verify the ChatGPT deletion**

Run:

```bash
env -u GIT_INDEX_FILE .venv/bin/python -m pytest \
  tests/unit/test_protocol_prompt_sync.py \
  tests/unit/test_compact_state_mapping.py \
  tests/unit/test_capability_v1_adapter.py \
  tests/unit/test_compact_kernel_surface_inventory.py -q
! test -e scripts/chatgpt_pro_consult.py
! test -e tests/unit/test_chatgpt_pro_consult.py
! test -e .agents/skills/chatgpt-pro-consultation/SKILL.md
! test -e docs/protocol/codex/chatgpt-pro-consultation-acceptance.md
! rg -n 'import chatgpt_pro_consult|render_chatgpt_pro_consultation|chatgpt_pro_consultation_default|validate_chatgpt_pro_activation_evidence' \
  scripts tests/unit .agents/skills .codex/agents .claude/agents AGENTS.md docs/protocol/codex docs/protocol/threeway
env -u GIT_INDEX_FILE .venv/bin/python scripts/ci_smoke.py
env -u GIT_INDEX_FILE git diff --check
```

Expected: focused tests and smoke pass; all absence commands produce no matches; diff check prints nothing.

- [ ] **Step 6: Commit the ChatGPT deletion**

Commit only the listed paths with subject:

```text
refactor: remove ChatGPT Pro consultation tool
```

Mark the Director packet `done` only after fresh spec and quality reviews return no blocking finding. Task 4 may not start before that packet transition is committed by the coordinator or recorded through the validated route mechanism.

### Task 4: Replace Lane V v2 and Delete Opus

**Owner:** Director2

**Files:**

- Create: `scripts/baselines/lane_v_reports_pre_v3.json`
- Modify: `scripts/verification_report_gate.py`
- Modify: `scripts/check_go_schema.py`
- Modify: `coordination/bin/send-event`
- Modify: `tests/unit/test_verification_report_gate.py`
- Modify: `tests/unit/test_check_go_schema.py`
- Modify: `tests/unit/test_coordination_tooling.py`
- Delete: `scripts/opus_review_bridge.py`
- Delete: `scripts/opus_review_receipts.py`
- Delete: `tests/unit/test_opus_review_bridge.py`
- Delete: `tests/unit/test_opus_review_receipts.py`
- Delete: `scripts/prompts/opus_lane_v_advisory.md`
- Delete: `scripts/prompts/opus_lane_v_advisory.authority.583cdcb5b5129b629ae4ada21627a4fc5bab1b9c.json`
- Modify: `.agents/skills/seat-operator/verification-report-format.md`
- Modify: `.claude/skills/seat-operator/verification-report-format.md`
- Modify: `.codex/agents/lane-v-verifier.toml`
- Modify: `.claude/agents/lane-v-verifier.md`
- Modify: `.codex/agents/protocol-operator.toml`
- Modify: `.agents/skills/seat-operator/SKILL.md`

**Interfaces:**

- Consumes: Tasks 2-3, every tracked pre-v3 verification-report byte, the current structural authority parser, and the existing `TaskPublicationStore` transaction.
- Produces: `parse_lane_v_report(relative_path: str, raw: bytes) -> LaneVReport`, `validate_structural_authority(root: Path, report: LaneVReport) -> StructuralAuthority`, `validate_live_report(root: Path, report: LaneVReport, *, task_store_factory=TaskPublicationStore.for_repo) -> TaskPublicationRecord`, and one task-ID-only publish/resume/status CLI.

**Binding independence-first correction:** A fresh independent design-time
preflight at `b459327addaf0e18a6c1e62b062bcad84b986cee` blocked implementation
before any Task-4 code edit. The following acceptance criteria are additions to
Steps 1-8 and must be implemented and tested before the Task-4 commit:

- The new default `scripts/baselines/lane_v_reports_pre_v3.json` is a one-shot
  frozen cutover manifest. Once it exists, neither `--replace-baseline` nor the
  Python generation API may change it. A regression must alter historical
  report bytes, attempt replacement, prove the command/API fails without
  changing manifest bytes, and prove validation still reports digest drift.
- Port the complete provider-neutral abuse matrix for the moved JSON, canonical
  encoding, repository-path, scope-reference, trigger, and descriptor
  primitives into `test_verification_report_gate.py` before deleting the Opus
  test modules. Coverage includes duplicate keys at nested levels, invalid
  UTF-8, non-finite values, size limits, exact descriptor fields and literals,
  canonical UUID/SHA/digest forms, absolute/dot/dot-dot/empty/trailing-slash/
  backslash/glob/oversize paths, and byte/component-aware allowed roots.
- Exercise private `TaskPublicationStore` state directly: root mode `0700` and
  current ownership; lock/record mode `0600`, regular-file type, current
  ownership, and single-link count; symlink, directory, FIFO, hard-link,
  wrong-mode, and wrong-owner substitutions must fail before any record
  transition or report publication.
- Bind `Reviewer identity` to the filename/envelope sender with positive
  canonical `operator` and `operator2` reports and negative other-seat,
  non-operator, empty, decorated, and case-changed identities. Rejection occurs
  during parsing before task-state access.
- Add a source/CLI closure test proving the live gate has only task-ID
  publication, rejects `--receipt-id`, contains no receipt store/record,
  provider-mode, lazy-bridge, or provider-field branch, and that `send-event`
  extracts only `verification_report_gate.py` as trusted report source.

The preflight found the existing structural-authority, no-replace publication,
crash/fsync/staged-index recovery, hostile-Git, and exact historical path/digest
coverage adequate if retained. No criterion above authorizes Opus, receipt, or
local-runtime access.

- [ ] **Step 1: Rewrite parser tests for the exact v3 contract**

Replace `_codex_fields()` and `_claude_fields()` with one helper:

```python
def _lane_v_fields() -> list[tuple[str, str]]:
    return [
        ("Verification schema", "lane-v-report/v3"),
        ("Verification mode", "independent-lane-v"),
        ("Verification harness", "lane-v:independent-verifier"),
        ("Verification task ID", TASK_ID),
        ("Scope authority", f"{DESCRIPTOR_PATH}@{DESCRIPTOR_DIGEST}"),
        ("Trigger identity", f"shipping-commit:{HEAD}"),
        ("Reviewed head", HEAD),
        ("Reviewed base", BASE),
        ("Review profile", "independent-lane-v"),
        ("Reviewer identity", "operator"),
    ]
```

Add parameterized parser coverage for GO/NITS/FAIL and rejection of each removed field:

```python
@pytest.mark.parametrize("verdict", ("GO", "NITS", "FAIL"))
def test_parse_provider_neutral_v3_verdicts(verdict: str) -> None:
    report = gate.parse_lane_v_report(
        REPORT_PATH,
        _report_bytes(_lane_v_fields(), verdict=f"VERDICT: {verdict}"),
    )
    assert report.verdict == verdict
    assert tuple(report.fields) == gate.ATTESTATION_FIELDS


@pytest.mark.parametrize(
    "label",
    (
        "Authorization identity",
        "Opus receipt ID",
        "Opus scope digest",
        "Cross-model review",
        "Effective Opus model",
        "Opus finding dispositions",
        "Reconciliation guard",
        "Degraded reason",
        "Provider",
        "Model",
    ),
)
def test_v3_rejects_provider_and_receipt_fields(label: str) -> None:
    with pytest.raises(gate.ReportGateError, match="invalid_attestation"):
        gate.parse_lane_v_report(
            REPORT_PATH,
            _report_bytes([*_lane_v_fields(), (label, "forbidden")]),
        )
```

Retain and adapt the existing malformed order, duplicate field, filename, H1, envelope, stale trigger, reviewed-head, descriptor, no-replace, recovery, fsync, index, hostile-Git, and crash-matrix tests. Delete only receipt-store/provider-binding tests whose authority disappears.

- [ ] **Step 2: Write historical cutover tests**

In `tests/unit/test_check_go_schema.py`, change the manifest schema to `lane-v-report-pre-v3-baseline/v1` and add tests proving:

```python
def test_pre_v3_report_requires_exact_manifest_path_and_digest(tmp_path: pathlib.Path) -> None:
    raw = b"# historical\n\nVERDICT: FAIL\n"
    path = _REPOSITORY_REPORT
    manifest = _manifest((path, hashlib.sha256(raw).hexdigest()))
    assert cgs.repository_report_violations(
        tmp_path, [cgs.RawReport(path, raw)], manifest
    ) == []
    assert cgs.repository_report_violations(
        tmp_path, [cgs.RawReport(path, raw + b"changed\n")], manifest
    )
    copied = path.replace("06-00-00", "06-00-01")
    assert cgs.repository_report_violations(
        tmp_path, [cgs.RawReport(copied, raw)], manifest
    )
```

Also prove a new unlisted v1/v2 report fails even when structurally plausible, while a new v3 report is parsed live.

- [ ] **Step 3: Run the v3 and cutover tests and observe failure**

Run:

```bash
env -u GIT_INDEX_FILE .venv/bin/python -m pytest \
  tests/unit/test_verification_report_gate.py \
  tests/unit/test_check_go_schema.py \
  tests/unit/test_coordination_tooling.py -q
```

Expected: FAIL because the parser still requires v2 provider fields, `check_go_schema.py` imports the receipt module, and `send-event` trusts three provider files.

- [ ] **Step 4: Move only generic primitives into the report gate**

Move the full existing implementations—not reduced rewrites—of these provider-neutral primitives from `scripts/opus_review_receipts.py` into `scripts/verification_report_gate.py`, then update all local call sites to use them directly:

```text
ChangedPath
ReviewScope
ScopeDescriptor
ScopeReference
PIPELINE_MARKER_PATHS
strict_json_loads
canonical_json_bytes
normalize_repo_path
parse_scope_reference
canonical_trigger_identity
require_pipeline_root
_ensure_private_directory
_private_file_flags
_publication_path
_publication_witness_from_values
_validate_private_file
_write_all
```

Move their complete private transitive helper closure as identified by `rg`/AST call inspection; do not leave a wrapper import back to the deleted module. Before moving them, verify the full definitions and callers. Preserve strict duplicate-key rejection, canonical JSON bytes, UTF-8/POSIX path rules, descriptor exact-field validation, pipeline-root markers, private-file metadata checks, and publication witness semantics.

- [ ] **Step 5: Implement the exact v3 attestation and task-only live path**

Set:

```python
REPORT_SCHEMA_VERSION = "lane-v-report/v3"
PRE_V3_MANIFEST_SCHEMA_VERSION = "lane-v-report-pre-v3-baseline/v1"
ATTESTATION_FIELDS = (
    "Verification schema",
    "Verification mode",
    "Verification harness",
    "Verification task ID",
    "Scope authority",
    "Trigger identity",
    "Reviewed head",
    "Reviewed base",
    "Review profile",
    "Reviewer identity",
)
```

`_validate_fields()` must require the three exact provider-neutral literals, canonical UUID/scope/trigger/SHA values, and `Reviewer identity` equal to the report filename/envelope sender (`operator` or `operator2`). An extra, missing, duplicated, decorated, reordered, or continued attestation line remains fail-closed.

Update `ScopeDescriptor.from_mapping()` to require `verification_mode == "independent-lane-v"`, `verification_harness == "lane-v:independent-verifier"`, and `review_profile == "independent-lane-v"`; remove the Codex/Claude provider-mode alternatives while retaining exact descriptor fields, reviewed-base policy, requirement paths, allowed roots, and verification commands.

Remove `ReceiptStore`, `ReceiptRecord`, receipt IDs, attempt keys, provider reconciliation, lazy bridge import, Codex/Claude mode branches, and receipt-based CLI identifiers. `validate_live_report()` always opens `TaskPublicationStore` by task ID and validates structural authority before any state write. `publish`, `resume`, and `status` accept `--task-id` only. Preserve no-replace publication, witnessed recovery, staged-index binding, fsync boundaries, interruption status codes, and sanitized output.

- [ ] **Step 6: Cut over repository report validation**

In `scripts/check_go_schema.py`:

- remove `import opus_review_receipts as receipts`;
- import/use `strict_json_loads`, `canonical_json_bytes`, and `normalize_repo_path` from `verification_report_gate`;
- set `DEFAULT_MANIFEST` to `scripts/baselines/lane_v_reports_pre_v3.json`;
- accept an exact manifest path/digest before decoding historical bytes;
- send every unlisted report to the live v3 parser;
- keep GO evidence gates unchanged;
- preserve atomic/no-clobber baseline generation and hostile-Git protections.

Generate the complete cutover manifest from one pinned `HEAD` containing Tasks 1-3 but no v3 report:

```bash
env -u GIT_INDEX_FILE .venv/bin/python scripts/check_go_schema.py \
  --generate-baseline scripts/baselines/lane_v_reports_pre_v3.json
env -u GIT_INDEX_FILE .venv/bin/python -m json.tool \
  scripts/baselines/lane_v_reports_pre_v3.json >/dev/null
```

Expected: the manifest contains every tracked `coordination/mailbox/sent/*-verification-report.md` path exactly once, sorted by path, with raw SHA-256 digests. Do not replace or edit `lane_v_report_v1.json`.

- [ ] **Step 7: Simplify the trusted publisher and delete Opus**

In `coordination/bin/send-event`, change the trusted source loop to:

```bash
for SOURCE in verification_report_gate.py; do
```

Update the comment to `Verification reports use the task-bound Python publisher`. Retain the primary-checkout proof, trusted committed blob extraction, isolated Python environment, final-path validation, and staging behavior.

Delete the six exact Opus code/test/prompt assets. Update operator skills, report-format mirrors, and Lane V agent prompts to produce only the ten v3 fields and to run no provider command.

- [ ] **Step 8: Run the full focused Lane V suite**

Run:

```bash
env -u GIT_INDEX_FILE .venv/bin/python -m pytest \
  tests/unit/test_verification_report_gate.py \
  tests/unit/test_check_go_schema.py \
  tests/unit/test_coordination_tooling.py \
  tests/unit/test_protocol_prompt_sync.py -q
env -u GIT_INDEX_FILE .venv/bin/python scripts/check_go_schema.py
! test -e scripts/opus_review_bridge.py
! test -e scripts/opus_review_receipts.py
! test -e tests/unit/test_opus_review_bridge.py
! test -e tests/unit/test_opus_review_receipts.py
! rg -n 'import opus_review|Opus receipt ID|standing-policy:codex-lane-v-opus-v1' \
  scripts/verification_report_gate.py scripts/check_go_schema.py \
  coordination/bin/send-event .agents/skills/seat-operator \
  .claude/skills/seat-operator .codex/agents/lane-v-verifier.toml \
  .claude/agents/lane-v-verifier.md
env -u GIT_INDEX_FILE git diff --check
```

Expected: all tests and schema validation pass; deletion/absence checks produce no matches; diff check prints nothing.

- [ ] **Step 9: Commit provider-neutral Lane V and Opus deletion**

Commit only the listed files with subject:

```text
refactor: replace Opus bridge with provider-neutral Lane V
```

Fresh spec review question: does v3 retain every generic Lane V authority/publication invariant while removing every Opus behavior? Fresh quality review question: do the cutover manifest and task-only transaction fail closed under changed history, malformed state, crash recovery, and hostile Git?

### Task 5: Converge Operative Surfaces and Add the Decommission Gate

**Owner:** Director2

**Files:**

- Modify: `AGENTS.md`
- Modify: `ARCHITECTURE.md`
- Modify: `DECISIONS.md`
- Modify: `scripts/codex_protocol_model.py`
- Modify: `docs/protocol/codex/continuation.md`
- Modify: `docs/protocol/claude/independence-first.md`
- Modify: `docs/PROTOCOL-RULES-LOG.md`
- Modify: `.agents/skills/four-seat-protocol/SKILL.md`
- Modify: `.agents/skills/seat-director/SKILL.md`
- Modify: `.agents/skills/seat-operator/SKILL.md`
- Modify: `.agents/skills/seat-coordinator/SKILL.md`
- Modify: `.codex/agents/readiness-bridge.toml`
- Modify: `.codex/agents/protocol-director.toml`
- Modify: `.codex/agents/protocol-operator.toml`
- Modify: `.codex/agents/protocol-coordinator.toml`
- Modify: `.claude/agents/readiness-bridge.md`
- Modify: `docs/protocol/threeway/ANTIGRAVITY-ADOPTION.md`
- Modify: `docs/protocol/threeway/ARCHITECTURE-DIAGRAM.md`
- Modify: `docs/protocol/threeway/ONBOARDING.md`
- Modify: `docs/protocol/threeway/UNIFIED-OPERATING-DOCTRINE.md`
- Modify: `tests/unit/test_protocol_prompt_sync.py`
- Modify: `tests/unit/test_protocol_doc_integrity.py`

**Interfaces:**

- Consumes: the Task 3 ChatGPT deletion and Task 4 provider-neutral Lane V implementation.
- Produces: one synchronized operative doctrine with no provider launch contract, one append-only superseding decision, and a regression test that keeps executable/launchable surfaces provider-free.

**Binding independence-first correction:** A fresh independent design-time
preflight at `72c9eeb34f7a73ade3f0e9fec1ae4f10e4401b32` blocked implementation
before any Task-5 code or doctrine edit. The following acceptance criteria are
additions to Steps 1-5 and must be implemented and tested before the Task-5
commit:

- Converge `docs/protocol/claude/independence-first.md`, its positive pin in
  `tests/unit/test_protocol_doc_integrity.py`, and the current R-GATE-EVIDENCE
  enforcement description in `docs/PROTOCOL-RULES-LOG.md` from live v2/receipt
  behavior to v3 and `TaskPublicationStore`. Preserve rule provenance and run
  the doc-integrity test in the focused suite.
- Replace `CROSS_MODEL_VERIFICATION_RULES` and
  `render_cross_model_verification()` with a named provider-neutral Lane-V v3
  contract used by model output, summaries, continuation, skills, and prompts.
  Adapt rather than delete the exact trigger/descriptor tests. The negative
  operative scan must also reject `verdict-blind Opus`, `opus-review/v3`,
  `opus-reconciliation/v2`, `lane-v-report/v2`, `--receipt-id`,
  `attempt_state_uncertain`, `Opus scope digest`, standing provider policy,
  provider retry/degradation/process branches, and the removed renderer.
- Add positive synchronization coverage for mailbox/body-first decisions,
  intentional seat cursors and no coordinator cursor, exact committed trigger
  and descriptor binding with fail-closed invalid forms, non-author operator
  independence, GO/NITS/FAIL, atomic task-bound v3 publication, coordinator
  no-production-fix authority, and separately gated push, merge, spend, and
  other side effects. Add merge to `ACTIVE_KERNEL_INVARIANTS`; provider-text
  deletion must not erase these generic boundaries.
- Make the launchable-capacity assertion field-aware. Provider names or deleted
  paths may occur only in this decommission cycle's identity/scope and exact
  negative prohibitions; any executable provider command, receipt/retry
  instruction, or contradictory affirmative action in a `ready` or `active`
  packet must fail even when the packet also contains the expected negative
  acceptance text.
- Preserve the existing provider-neutral two-input dual-chief regression, the
  Task-4 frozen historical path/digest tests, and append-only history in
  `DECISIONS.md`. Operative scanning must exclude historical evidence and the
  real `.codex/runtime` residue; no Task-5 test or helper may traverse or mutate
  that runtime.

**Binding post-implementation review correction:** Fresh spec and adversarial
reviews of `d97a6c46c8da20441a3dff6939801e6489695444..6bc19e2745b9f381e6e1a710c231604d20661545`
blocked Task-5 closure. Before re-review, a bounded correction must:

- Rewrite the remaining live statements in
  `docs/protocol/claude/independence-first.md` so a same-model independent
  reviewer is weaker and identified, not categorically invalid, and no report
  must attest to cross-model identity. Pin this in
  `tests/unit/test_protocol_doc_integrity.py`.
- Normalize operative provider matching case-insensitively and make the
  launchable-packet gate reject affirmative ChatGPT, Claude, Opus, Gemini,
  provider CLI/process/call/launch/retry/receipt, in-app browser, paid API, and
  equivalent nested commands even when exact negative acceptance text is also
  present. Add bypass regressions for lowercase and alternate-provider forms.
- Add `merge` to both `render_runtime_env_contract()` and
  `render_seat_contract()` and mutation-pin both executable renderers, not only
  `ACTIVE_KERNEL_INVARIANTS` and `render_lane_v_v3()`.
- Synchronize the exact provider-neutral v3 contract, including atomic
  `TaskPublicationStore` publication and identity-no-authority, into both
  verifier agent prompts and both verification-report format mirrors; include
  all four in the positive sync surface set.

- [ ] **Step 1: Add the failing operative-surface gate**

Add to `tests/unit/test_protocol_prompt_sync.py`:

```python
DELETED_PROVIDER_PATHS = (
    "scripts/chatgpt_pro_consult.py",
    "scripts/opus_review_bridge.py",
    "scripts/opus_review_receipts.py",
    "tests/unit/test_chatgpt_pro_consult.py",
    "tests/unit/test_opus_review_bridge.py",
    "tests/unit/test_opus_review_receipts.py",
    ".agents/skills/chatgpt-pro-consultation/SKILL.md",
    "docs/protocol/codex/chatgpt-pro-consultation-acceptance.md",
    "scripts/prompts/opus_lane_v_advisory.md",
    "scripts/prompts/opus_lane_v_advisory.authority.583cdcb5b5129b629ae4ada21627a4fc5bab1b9c.json",
)
FORBIDDEN_OPERATIVE_FRAGMENTS = (
    "import chatgpt_pro_consult",
    "import opus_review_bridge",
    "import opus_review_receipts",
    "render_chatgpt_pro_consultation(",
    "chatgpt_pro_consultation_default(",
    "Opus receipt ID:",
    "standing-policy:codex-lane-v-opus-v1",
    "scripts/prompts/opus_lane_v_advisory.md",
)


def test_provider_tools_are_absent_from_executable_and_operative_surfaces() -> None:
    for relative in DELETED_PROVIDER_PATHS:
        assert not (ROOT / relative).exists(), relative
    active_files = [
        ROOT / "AGENTS.md",
        ROOT / "ARCHITECTURE.md",
        ROOT / "scripts/codex_protocol_model.py",
        *sorted((ROOT / ".agents/skills").glob("**/*")),
        *sorted((ROOT / ".codex/agents").glob("*.toml")),
        *sorted((ROOT / ".claude/agents").glob("*.md")),
        *sorted((ROOT / "docs/protocol/codex").glob("*.md")),
        *sorted((ROOT / "docs/protocol/threeway").glob("*.md")),
    ]
    for path in active_files:
        if not path.is_file():
            continue
        text = path.read_text(encoding="utf-8")
        assert all(fragment not in text for fragment in FORBIDDEN_OPERATIVE_FRAGMENTS), path
```

Add a capacity assertion that parses packet JSON and checks only launchable statuses `ready` and `active`; `excepted` historical packets remain evidence:

```python
def test_launchable_capacity_packets_do_not_invoke_deleted_providers() -> None:
    for path in sorted((ROOT / "coordination/capacity/packets").glob("*.json")):
        packet = json.loads(path.read_text(encoding="utf-8"))
        if packet["status"] not in {"ready", "active"}:
            continue
        body = json.dumps(packet, sort_keys=True).lower()
        if "chatgpt" not in body and "opus" not in body:
            continue
        assert packet["cycle"] == "provider-tools-targeted-decommission-2026-07-16", path
        acceptance = "\n".join(packet["acceptance"])
        assert "No ChatGPT Pro, Claude, Opus" in acceptance, path
        assert "provider retry, or provider receipt action is authorized" in acceptance, path
```

- [ ] **Step 2: Run the gate and observe operative drift**

Run:

```bash
env -u GIT_INDEX_FILE .venv/bin/python -m pytest \
  tests/unit/test_protocol_prompt_sync.py -q
```

Expected: FAIL with the remaining active provider-contract fragments identified by exact path.

- [ ] **Step 3: Rewrite current doctrine around provider-neutral Lane V**

Every current role/skill/continuation surface must state:

```text
Lane V is independent verification by a non-author operator over one committed descriptor and lawful trigger. New reports use lane-v-report/v3 and publish atomically through TaskPublicationStore. Model or provider identity grants no authority.
```

Remove standing paid-call authority, provider availability branches, receipt reservation/reconciliation, Opus model checks, ChatGPT consultation triggers, and retry/fallback language. Preserve mailbox-first decisions, exact range/descriptor/trigger binding, operator non-authorship, GO/NITS/FAIL, and user-gated side effects.

Update `ARCHITECTURE.md` topology and smoke claims in the same commit. In `DECISIONS.md`, append a new dated decision titled `Targeted decommission of Opus and ChatGPT Pro tools`; state the user-approved deletion, provider-neutral v3 replacement, frozen historical evidence rule, local-runtime preservation, and separate approval required for any future provider tool. Do not edit prior decision entries.

- [ ] **Step 4: Verify synchronization and absence**

Run:

```bash
env -u GIT_INDEX_FILE .venv/bin/python -m pytest \
  tests/unit/test_protocol_prompt_sync.py \
  tests/unit/test_verification_report_gate.py \
  tests/unit/test_check_go_schema.py \
  tests/unit/test_coordination_tooling.py \
  tests/unit/test_compact_state_mapping.py \
  tests/unit/test_capability_v1_adapter.py \
  tests/unit/test_compact_kernel_surface_inventory.py -q
env -u GIT_INDEX_FILE .venv/bin/python scripts/check_coordination.py
env -u GIT_INDEX_FILE .venv/bin/python scripts/check_go_schema.py
env -u GIT_INDEX_FILE .venv/bin/python scripts/ci_smoke.py
env -u GIT_INDEX_FILE git diff --check
```

Expected: all focused tests, coordination, report validation, and smoke pass; diff check prints nothing.

- [ ] **Step 5: Commit operative convergence**

Commit only the listed files with subject:

```text
docs(protocol): converge on provider-neutral verification
```

Mark the Director2 packet `done` only after fresh task spec and quality reviews return no blocking finding. The commit at this point is the provisional `DECOMMISSION_HEAD` pending Task 6 corrections.

### Task 6: Perform Two Non-Duplicative Independent Full-Range Reviews

**Owner:** Director2 routes the spec review; Operator2 owns the quality preflight. Neither reviewer repairs the diff.

**Files:**

- Create: the canonical Director2-to-Coordinator `findings` path returned in `SPEC_REVIEW_EVENT`
- Create: the canonical Operator2-to-Coordinator `findings` path returned in `QUALITY_REVIEW_EVENT`
- Modify on findings only: the smallest Task 2-5 owned source/test/doc set required by the finding, in a separate correction commit

**Interfaces:**

- Consumes: exact `DECOMMISSION_BASE..DECOMMISSION_HEAD`, approved design, this plan, all task review results, and fresh verification output.
- Produces: two committed no-blocker findings events or bounded correction commits followed by refreshed no-blocker events. Same-model independent review is explicitly recorded as weaker than cross-model review because both external provider tools are being deleted.

- [ ] **Step 1: Freeze and state the two different review questions**

Spec review question:

```text
Against the approved design and plan only, enumerate every required deletion, retained generic Lane V invariant, historical-preservation boundary, route transition, compact producer removal, operative-surface update, and forbidden side effect. Report any missing, extra, or historical modification by exact path. Do not assess implementation style.
```

Quality review question:

```text
Against the actual diff only, challenge v3 field parsing, path/digest grandfathering, descriptor/trigger/range binding, task-state publication, hostile filesystem/Git handling, compact fixture consistency, and active-reference absence. Report exploitable or fail-open behavior with one reproducer/test target. Do not repeat the spec inventory question.
```

Persist those exact question bodies in `SPEC_REVIEW_QUESTION` and `QUALITY_REVIEW_QUESTION`, including punctuation and excluding the Markdown fences. Compute their identities before dispatch:

```bash
SPEC_QUESTION_DIGEST="sha256:$(printf '%s' "$SPEC_REVIEW_QUESTION" | \
  /usr/bin/shasum -a 256 | /usr/bin/awk '{print $1}')"
QUALITY_QUESTION_DIGEST="sha256:$(printf '%s' "$QUALITY_REVIEW_QUESTION" | \
  /usr/bin/shasum -a 256 | /usr/bin/awk '{print $1}')"
printf '%s\n%s\n' "$SPEC_QUESTION_DIGEST" "$QUALITY_QUESTION_DIGEST" | \
  /usr/bin/grep -Ec '^sha256:[0-9a-f]{64}$' | /usr/bin/grep -Fx '2'
```

- [ ] **Step 2: Dispatch a fresh-context spec reviewer**

Use a fresh advisory subagent with only the approved design, this plan, `DECOMMISSION_BASE`, `DECOMMISSION_HEAD`, and the spec question. Require output fields:

```text
Reviewer identity: codex-subagent:provider-decommission-spec
Harness: fresh-context read-only diff review
Reviewed range: ${DECOMMISSION_BASE}..${DECOMMISSION_HEAD}
Question digest: ${SPEC_QUESTION_DIGEST}
Verdict: PASS|FINDINGS
Findings: none or exact path/requirement/evidence rows
```

Director2 records the result verbatim except for secrets in one `findings` event and commits that event alone.

- [ ] **Step 3: Activate the Operator2 preflight packet**

After the spec event is committed and the Director2 implementation packet is `done`, Coordinator refreshes capacity/mailbox state, sets `coordination/capacity/packets/2026-07-16-provider-tools-decommission-operator2-quality-preflight.json` to `active`, binds `commit_range` to `${DECOMMISSION_BASE}..${DECOMMISSION_HEAD}`, and validates/commits that one metadata change. Operator2 must not start from the dependency alone.

- [ ] **Step 4: Run Operator2's bounded quality preflight**

Operator2 refreshes the routed packet, reads the actual diff, and executes at least:

```bash
env -u GIT_INDEX_FILE git diff --name-status "$DECOMMISSION_BASE..$DECOMMISSION_HEAD"
env -u GIT_INDEX_FILE .venv/bin/python -m pytest \
  tests/unit/test_verification_report_gate.py \
  tests/unit/test_check_go_schema.py \
  tests/unit/test_coordination_tooling.py \
  tests/unit/test_protocol_prompt_sync.py \
  tests/unit/test_compact_state_mapping.py \
  tests/unit/test_capability_v1_adapter.py \
  tests/unit/test_compact_kernel_surface_inventory.py -q
env -u GIT_INDEX_FILE .venv/bin/python scripts/check_go_schema.py
env -u GIT_INDEX_FILE .venv/bin/python scripts/ci_smoke.py
```

Operator2 sends one `findings` event with its seat identity, `codex:operator2-quality-preflight` harness, exact range, question digest, PASS/FINDINGS, and exact evidence. It is not a Lane V verdict and releases no lock.

- [ ] **Step 5: Correct only concrete findings**

If either review returns FINDINGS, route each finding to the owner of the affected task. Add the failing regression first, observe it fail, make the smallest correction, rerun the affected task suite, and commit with either:

```text
fix: close provider decommission spec gap
```

or:

```text
fix: harden provider-neutral Lane V cutover
```

Refresh `DECOMMISSION_HEAD` and rerun only the review whose question was not satisfied. Do not launch a third same-question review. Task 7 starts only when both exact-range review events say PASS/no findings.

### Task 7: Obtain Formal Provider-Neutral Operator Lane V

**Owner:** Director2 creates authority; Coordinator activates; Operator verifies and publishes.

**Files:**

- Create: `coordination/verification/scopes/11249ae3-1a0f-45c0-aa90-7d558537b001.json`
- Create: the canonical Director2-to-Operator verify-request path returned in `VERIFY_REQUEST_PATH`
- Modify: `coordination/capacity/packets/2026-07-16-provider-tools-decommission-operator-lanev.json`
- Create: the canonical Operator-to-All verification-report path returned in `VERIFICATION_REPORT_PATH`

**Interfaces:**

- Consumes: final reviewed range `DECOMMISSION_BASE..DECOMMISSION_HEAD`, two Task 6 PASS events, v3 parser/publisher, and task ID `11249ae3-1a0f-45c0-aa90-7d558537b001`.
- Produces: one lawful descriptor, one verify-request strictly after the reviewed head, and one task-bound v3 GO/NITS/FAIL published through `TaskPublicationStore` without any provider or receipt state.

- [ ] **Step 1: Freeze the final production head and exact write set**

Run:

```bash
ROUTE_BASE_COUNT="$(env -u GIT_INDEX_FILE git log --format=%H \
  --grep='^coord(coordinator): retire provider routes and open decommission$' | \
  wc -l | tr -d ' ')"
test "$ROUTE_BASE_COUNT" -eq 1
DECOMMISSION_BASE="$(env -u GIT_INDEX_FILE git log -1 --format=%H \
  --grep='^coord(coordinator): retire provider routes and open decommission$')"
DECOMMISSION_HEAD="$(env -u GIT_INDEX_FILE git rev-parse 'HEAD^{commit}')"
test "$(printf '%s' "$DECOMMISSION_BASE" | wc -c | tr -d ' ')" -eq 40
env -u GIT_INDEX_FILE git diff --name-status --no-renames \
  "$DECOMMISSION_BASE..$DECOMMISSION_HEAD"
env -u GIT_INDEX_FILE git status --short
```

Expected: the uniquely resolved Task 1 route commit is a full SHA, the diff contains the exact Task 2-6 reviewed paths, and the index/worktree is clean except ambient untracked user files. Stop if the subject is absent or non-unique.

- [ ] **Step 2: Commit the fixed v3 scope descriptor**

Create `coordination/verification/scopes/11249ae3-1a0f-45c0-aa90-7d558537b001.json` with:

```json
{
  "schema_version": "lane-v-scope/v1",
  "task_id": "11249ae3-1a0f-45c0-aa90-7d558537b001",
  "question_id": "provider-tools-targeted-decommission",
  "trigger_kind": "verify-request",
  "verification_mode": "independent-lane-v",
  "verification_harness": "lane-v:independent-verifier",
  "review_profile": "independent-lane-v",
  "reviewed_base": {
    "policy": "exact",
    "commit": "${DECOMMISSION_BASE}"
  },
  "requirement_paths": [
    "docs/superpowers/specs/2026-07-16-opus-chatgpt-pro-targeted-decommission-design.md",
    "docs/superpowers/plans/2026-07-16-provider-tools-targeted-decommission.md"
  ],
  "allowed_path_roots": [
    ".agents/skills",
    ".claude/agents",
    ".claude/skills/seat-operator",
    ".codex/agents",
    "AGENTS.md",
    "ARCHITECTURE.md",
    "DECISIONS.md",
    "coordination/bin",
    "coordination/capacity/packets",
    "docs/protocol",
    "logs/capability-first",
    "scripts",
    "tests/fixtures",
    "tests/unit"
  ],
  "verification_commands": [
    "env -u GIT_INDEX_FILE .venv/bin/python -m pytest tests/unit -q",
    "env -u GIT_INDEX_FILE .venv/bin/python scripts/check_coordination.py",
    "env -u GIT_INDEX_FILE .venv/bin/python scripts/protocol_capacity_board.py --wave 2",
    "env -u GIT_INDEX_FILE .venv/bin/python scripts/protocol_doctor.py --wave 2",
    "env -u GIT_INDEX_FILE .venv/bin/python scripts/check_doc_claims.py --sha-refs",
    "env -u GIT_INDEX_FILE .venv/bin/python scripts/ci_smoke.py",
    "env -u GIT_INDEX_FILE git diff --check"
  ]
}
```

Render `${DECOMMISSION_BASE}` to its literal full value before staging; the literal variable expression must not remain in the file. Validate the descriptor through the report-gate structural tests and commit it alone. Then compute its exact authority reference:

```bash
SCOPE_PATH='coordination/verification/scopes/11249ae3-1a0f-45c0-aa90-7d558537b001.json'
SCOPE_DIGEST="sha256:$(/usr/bin/shasum -a 256 "$SCOPE_PATH" | /usr/bin/awk '{print $1}')"
SCOPE_REF="${SCOPE_PATH}@${SCOPE_DIGEST}"
printf '%s\n' "$SCOPE_REF" | /usr/bin/grep -E \
  '^coordination/verification/scopes/11249ae3-1a0f-45c0-aa90-7d558537b001\.json@sha256:[0-9a-f]{64}$'
```

- [ ] **Step 3: Send and commit one canonical verify-request**

Director2 uses `coordination/bin/send-event director2 operator verify-request` once. Run:

```bash
SEND_OUTPUT="$(coordination/bin/send-event director2 operator verify-request \
  "verify provider tool decommission commit ${DECOMMISSION_HEAD}" <<EOF
Event type: verify-request
Reviewed head: ${DECOMMISSION_HEAD}
Reviewed base: ${DECOMMISSION_BASE}
Lane-V-Scope: ${SCOPE_REF}

Exact Next Trigger: Operator independently verifies the exact range and publishes one lane-v-report/v3 GO, NITS, or FAIL through the task-bound trusted publisher; no provider or receipt action is permitted.
EOF
)"
VERIFY_REQUEST_PATH="${SEND_OUTPUT#created }"
VERIFY_REQUEST_PATH="${VERIFY_REQUEST_PATH%% *}"
test -f "$VERIFY_REQUEST_PATH"
```

The generated body contains exactly one each:

```text
Event type: verify-request
Reviewed head: ${DECOMMISSION_HEAD}
Reviewed base: ${DECOMMISSION_BASE}
Lane-V-Scope: ${SCOPE_REF}

Exact Next Trigger: Operator independently verifies the exact range and publishes one lane-v-report/v3 GO, NITS, or FAIL through the task-bound trusted publisher; no provider or receipt action is permitted.
```

Commit the request alone. Record its full commit SHA and exact path. The request commit must be strictly after `DECOMMISSION_HEAD` and the descriptor commit:

```bash
VERIFY_REQUEST_COMMIT="$(env -u GIT_INDEX_FILE git rev-parse 'HEAD^{commit}')"
env -u GIT_INDEX_FILE git merge-base --is-ancestor \
  "$DECOMMISSION_HEAD" "$VERIFY_REQUEST_COMMIT"
test "$DECOMMISSION_HEAD" != "$VERIFY_REQUEST_COMMIT"
```

- [ ] **Step 4: Activate the Operator packet through coordinator metadata**

Coordinator sets the Operator packet to `active` and fills:

```json
{
  "verify_request": "${VERIFY_REQUEST_PATH}",
  "target_commit": "${DECOMMISSION_HEAD}",
  "commit_range": "${DECOMMISSION_BASE}..${DECOMMISSION_HEAD}",
  "status": "active"
}
```

Validate the updated route/capacity state and commit that packet change alone. Operator must not start from chat text or an uncommitted request.

- [ ] **Step 5: Operator performs the formal verification**

Operator independently resolves the descriptor, request commit, exact range, Task 6 PASS events, and every requirement path from Git. Run the complete command set from the descriptor. For `check_doc_claims.py --sha-refs`, compare against the pre-existing baseline and require zero new drift from `DECOMMISSION_BASE..DECOMMISSION_HEAD`.

Mutation/negative checks must prove:

- one changed historical report digest fails;
- one copied/unlisted v1/v2 report fails;
- one extra provider/receipt field in v3 fails;
- one wrong reviewer identity fails;
- one stale trigger and one wrong reviewed head fail;
- one changed descriptor digest fails;
- task publication remains no-replace and recoverable;
- no launchable packet or operative surface invokes a deleted provider.

Capture one exact summary line per successful verification command for the report body:

```bash
EVIDENCE_FILE="$(/usr/bin/mktemp /tmp/provider-decommission-evidence.XXXXXX)"
record_evidence() {
  label=$1
  shift
  output_file="$(/usr/bin/mktemp /tmp/provider-decommission-command.XXXXXX)"
  if ! "$@" >"$output_file" 2>&1; then
    /bin/cat "$output_file" >&2
    /bin/rm -f "$output_file"
    return 1
  fi
  summary="$(/usr/bin/awk 'NF {line=$0} END {print line}' "$output_file")"
  printf '$ %s\n→ %s\n\n' "$label" "$summary" >>"$EVIDENCE_FILE"
  /bin/rm -f "$output_file"
}
```

Call `record_evidence` once for each exit-zero descriptor command using the literal command string as `label` and the tokenized command as the remaining arguments. Record the full repository `check_doc_claims.py --sha-refs` baseline separately when it has the known historical nonzero result; require the exact pre-recorded issue set and add `→ zero new SHA-reference drift in DECOMMISSION_BASE..DECOMMISSION_HEAD` only after comparing the before/after outputs. Set `EVIDENCE_BLOCK="$(/bin/cat "$EVIDENCE_FILE")"` after every check succeeds.

- [ ] **Step 6: Publish one exact v3 report**

The report's attestation block is exactly:

```text
## Verification Attestation

Verification schema: lane-v-report/v3
Verification mode: independent-lane-v
Verification harness: lane-v:independent-verifier
Verification task ID: 11249ae3-1a0f-45c0-aa90-7d558537b001
Scope authority: ${SCOPE_REF}
Trigger identity: verify-request:${VERIFY_REQUEST_COMMIT}:${VERIFY_REQUEST_PATH}
Reviewed head: ${DECOMMISSION_HEAD}
Reviewed base: ${DECOMMISSION_BASE}
Review profile: independent-lane-v
Reviewer identity: operator
```

For GO, run the trusted publisher with the exact tested evidence inserted above the attestation:

```bash
SEND_OUTPUT="$(coordination/bin/send-event operator all verification-report \
  "Lane V verification report — commit \`${DECOMMISSION_HEAD}\`" <<EOF
VERDICT: GO

## Evidence

${EVIDENCE_BLOCK}

## Verification Attestation

Verification schema: lane-v-report/v3
Verification mode: independent-lane-v
Verification harness: lane-v:independent-verifier
Verification task ID: 11249ae3-1a0f-45c0-aa90-7d558537b001
Scope authority: ${SCOPE_REF}
Trigger identity: verify-request:${VERIFY_REQUEST_COMMIT}:${VERIFY_REQUEST_PATH}
Reviewed head: ${DECOMMISSION_HEAD}
Reviewed base: ${DECOMMISSION_BASE}
Review profile: independent-lane-v
Reviewer identity: operator

## Findings

None.
EOF
)"
VERIFICATION_REPORT_PATH="${SEND_OUTPUT#created }"
VERIFICATION_REPORT_PATH="${VERIFICATION_REPORT_PATH%% *}"
test -f "$VERIFICATION_REPORT_PATH"
```

Confirm `EVIDENCE_BLOCK` contains every descriptor command and no raw secret or private runtime path. Prose alone cannot satisfy the GO evidence gate. Use the same ten-field block with `VERDICT: NITS` or `VERDICT: FAIL` and exact findings if verification does not support GO. Commit the single report path, then delete `EVIDENCE_FILE`. On NITS/FAIL, stop and route only the bounded finding; do not repair as Operator.

### Task 8: Close the Decommission Cycle

**Owner:** Coordinator

**Files:**

- Modify: the five `coordination/capacity/packets/2026-07-16-provider-tools-decommission-*.json` files
- Create: `docs/HANDOFF-coordinator-2026-07-16-provider-tools-decommission-closeout.md`
- Create: the canonical Coordinator-to-All convergence path returned in `CLOSEOUT_EVENT`

**Interfaces:**

- Consumes: one schema-valid committed Operator GO for the exact final range, both Task 6 PASS events, fresh capacity/mailbox state, and full verification output.
- Produces: five terminal packets, one closeout event/handoff, and no production, runtime, push, merge, or external side effect.

- [ ] **Step 1: Reconcile GO from committed evidence**

Run:

```bash
env -u GIT_INDEX_FILE git log --oneline -3
env -u GIT_INDEX_FILE .venv/bin/python \
  .agents/skills/four-seat-protocol/scripts/seat_status.py coordinator --wave 2
env -u GIT_INDEX_FILE .venv/bin/python scripts/check_go_schema.py
env -u GIT_INDEX_FILE .venv/bin/python scripts/protocol_capacity_board.py --wave 2
```

Expected: one exact Operator report validates as v3 GO and binds the descriptor/request/range; no newer NITS/FAIL or ownership change exists.

- [ ] **Step 2: Mark the five packets terminal**

Set Director, Director2, Operator2, and Operator packets to `done`; set the coordinator join to `done` only after all four dependencies are terminal. Each `done_evidence` names the exact implementing commits, two review event paths, descriptor/request, and Operator GO report path. Do not rewrite the four retired legacy packets again.

- [ ] **Step 3: Create closeout evidence**

The convergence event and `docs/HANDOFF-coordinator-2026-07-16-provider-tools-decommission-closeout.md` must state:

```text
- executable ChatGPT Pro and Opus tools, dedicated tests, skills/prompts, and active hooks are removed;
- provider-neutral lane-v-report/v3 and TaskPublicationStore are the only live Lane V path;
- all pre-v3 reports are frozen by path/digest manifest;
- generic Lane V and historical/local audit evidence are preserved;
- no provider was called, no runtime evidence was touched, and nothing was pushed or merged;
- any future provider tool requires a separate user-approved design and compliant implementation plan.
```

End both artifacts with `Exact Next Trigger: none; decommission is terminal unless the user separately authorizes a future provider-tool design.`

- [ ] **Step 4: Run final completion verification**

Run fresh, after all closeout edits:

```bash
env -u GIT_INDEX_FILE .venv/bin/python -m pytest tests/unit -q
env -u GIT_INDEX_FILE .venv/bin/python scripts/check_coordination.py
env -u GIT_INDEX_FILE .venv/bin/python scripts/protocol_capacity_board.py --wave 2
env -u GIT_INDEX_FILE .venv/bin/python scripts/protocol_doctor.py --wave 2
env -u GIT_INDEX_FILE .venv/bin/python scripts/check_doc_claims.py --sha-refs
env -u GIT_INDEX_FILE .venv/bin/python scripts/check_go_schema.py
env -u GIT_INDEX_FILE .venv/bin/python scripts/ci_smoke.py
env -u GIT_INDEX_FILE git diff --check
env -u GIT_INDEX_FILE git status --short
```

Expected: unit, coordination, capacity, doctor, GO schema, and smoke pass; doc-claim output adds zero new drift relative to the recorded baseline; diff check prints nothing; status shows only the intended closeout artifacts plus preserved ambient untracked files.

- [ ] **Step 5: Commit closeout metadata only**

Commit the five packet updates, one handoff, and one convergence event with subject:

```text
coord(coordinator): close provider tool decommission
```

Do not push, merge, delete branches/worktrees, inspect runtime evidence, or clean ambient files.

## Final Acceptance Checklist

- [ ] The four retired provider-cycle packets are `excepted`; the five decommission packets are terminal and capacity-valid.
- [ ] Both executable provider tools, four dedicated test modules, one ChatGPT skill, one acceptance doc, and two Opus prompt assets are absent.
- [ ] Compact state exposes exactly `capacity`, `capability`, `local_verdict`, and `work_result`.
- [ ] New reports accept only the ten ordered `lane-v-report/v3` fields.
- [ ] All pre-v3 reports are accepted only by exact path and SHA-256 digest in `lane_v_reports_pre_v3.json`.
- [ ] `TaskPublicationStore` is the sole live publisher and uses task ID only.
- [ ] Operative instructions contain no lawful provider invocation or receipt/model contract.
- [ ] Historical Git/mailbox/plan/spec/log/descriptor/handoff evidence is unchanged.
- [ ] Ignored local runtime evidence was neither inspected nor touched.
- [ ] Independent spec and quality reviews are committed and nonblocking.
- [ ] Formal Operator Lane V returns GO for the exact final range.
- [ ] Full unit, coordination, capacity, doctor, schema, smoke, and diff verification passes with zero new doc-claim drift.
- [ ] No provider call, retry, fallback, receipt mutation, push, merge, or runtime cleanup occurred.
