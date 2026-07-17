# Compact Pair Loop Replacement Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use `superpowers:subagent-driven-development` to implement this single task with TDD and one independent final review.

**Goal:** Replace the self-locking Lane V descriptor/publication system with one committed verify-request, one independently staffed Operator verdict, and coordinator-driven internal seat continuation.

**Architecture:** A small `scripts/compact_pair_loop.py` validates current verify-requests and reports. `coordination/bin/send-event` sends every mailbox kind through the already-verified `kernel_activation.py` fixed finalizer and permits verification reports only from Operator seats. Frozen historical reports remain readable through the existing digest manifest; active descriptors, shipping triggers, trusted-code extraction, publication state, resume/recovery, and user-as-message-bus behavior are retired.

**Tech Stack:** Python standard library, Bash shims, Git, pytest.

## Global Constraints

- Pipeline only; no evidence-ledger, provider, Opus, GPT-Pro, PPL, target-bridge, or target-repository work.
- Keep `scripts/kernel_activation.py` writer-fence and fixed finalizer behavior unchanged.
- Active compact-pair production code must stay below roughly 500 lines; this change must be a large net deletion.
- Preserve historical mailbox reports, scope JSON, manifests, and old plans as read-only history.
- Only a committed verify-request is a current trigger. Remove the shipping-trigger alternative.
- A current verify-request names full reviewed base/head, author seat/model, assigned Operator, question, allowed paths, and commands.
- Only the assigned non-author Operator issues GO/NITS/FAIL. Reports name reviewer seat/model/harness/context and bind the exact request/base/head.
- GO, NITS, and FAIL reports must all be directly publishable through the normal fixed mailbox writer; no task state, receipt, trusted-source extraction, resume, retry, or recovery path.
- `continue as coordinator` internally executes an already-authorized local Director→Operator chain and returns to the user only at completion, a genuine blocker, scope expansion, or a separately gated effect.
- Activation, selector updates, push, merge, cleanup, cursor consumption, locks, provider use, and spend remain separately user-gated and are forbidden in this task.
- Do not modify or regenerate unrelated Claude provider-decommission work; change only active compact-pair doctrine phrases where prompt-sync requires it.

## Independent Abuse Cases

- Reject missing, duplicate, abbreviated, uppercase, or mismatched base/head fields.
- Reject a report from the wrong seat, same author seat, or same author model.
- Reject report/request path or commit mismatch and changed allowed-path scope.
- Permit truthful NITS/FAIL publication even when verification commands or external tools are unavailable.
- Prevent Directors/coordinators from publishing verification reports while preserving ordinary mailbox kinds.
- Preserve the shared common-dir lock, selector reread, no-follow publication, fsync, no-clobber, and exact-path staging in the existing fixed finalizer.
- Do not recurse internal seat continuation, infer side-effect consent, duplicate unchanged verification, or cross blocker/scope/effect boundaries.

---

### Task 1: Retire the publication machine and install the compact pair loop

**Files:**

- Create: `scripts/compact_pair_loop.py`
- Create: `tests/unit/test_compact_pair_loop.py`
- Delete: `scripts/verification_report_gate.py`
- Delete: `tests/unit/test_verification_report_gate.py`
- Modify: `coordination/bin/send-event`
- Modify: `scripts/check_go_schema.py`
- Modify: `scripts/protocol_capacity.py`
- Modify: `scripts/codex_protocol_model.py`
- Modify: `tests/unit/test_coordination_tooling.py`
- Modify: `tests/unit/test_check_go_schema.py`
- Modify: `tests/unit/test_protocol_capacity.py`
- Modify: `tests/unit/test_protocol_prompt_sync.py`
- Modify: `tests/unit/test_protocol_doc_integrity.py`
- Modify: `tests/unit/test_compact_kernel_surface_inventory.py`
- Modify: `tests/fixtures/compact_kernel/v1_surface_inventory.json`
- Modify only where active doctrine requires: `AGENTS.md`, `ARCHITECTURE.md`, `RUNBOOK-DAILY.md`, `docs/PROGRAM-MANUAL.md`, `docs/protocol/agents/director-operator.md`, `docs/protocol/claude/director-operator.md`, `docs/protocol/claude/continuation.md`, `docs/protocol/codex/continuation.md`, `.agents/skills/four-seat-protocol/SKILL.md`, `.agents/skills/seat-director/SKILL.md`, `.agents/skills/seat-operator/SKILL.md`, `.agents/skills/seat-coordinator/SKILL.md`, `.agents/skills/seat-operator/verification-report-format.md`, `.claude/skills/seat-director/SKILL.md`, `.claude/skills/seat-operator/SKILL.md`, `.claude/skills/seat-operator/verification-report-format.md`, `.codex/agents/protocol-director.toml`, `.codex/agents/protocol-operator.toml`, `.codex/agents/protocol-coordinator.toml`, `.codex/agents/lane-v-verifier.toml`, `.codex/agents/readiness-bridge.toml`, `.claude/agents/lane-v-verifier.md`, and the canonical invariants spec.

**Interfaces:**

- `parse_verify_request(root, request_path, trigger_commit) -> VerifyRequest`
- `parse_verification_report(root, report_path) -> VerificationReport`
- `validate_report(root, report) -> list[str]`
- Frozen pre-v3 report bytes remain accepted only through `scripts/baselines/lane_v_reports_pre_v3.json`.
- `send-event operator|operator2 ... verification-report` uses `kernel_activation.py send-event-finalize`; other senders fail before publication.

- [ ] **Step 1: Write RED tests**

  Add focused tests for the valid request/report path and every abuse case above. Add a tooling test proving verification reports use the same fixed finalizer as ordinary events and a prompt-sync test proving internal coordinator continuation stops only at real boundaries.

- [ ] **Step 2: Prove RED**

  Run:

  ```bash
  env -u GIT_INDEX_FILE /Users/hyungkoookkim/Pipeline/.venv/bin/python -m pytest \
    tests/unit/test_compact_pair_loop.py \
    tests/unit/test_coordination_tooling.py \
    tests/unit/test_check_go_schema.py \
    tests/unit/test_protocol_capacity.py \
    tests/unit/test_protocol_prompt_sync.py \
    tests/unit/test_protocol_doc_integrity.py \
    tests/unit/test_compact_kernel_surface_inventory.py -q
  ```

  Expected: new compact-pair assertions fail because the old descriptor/store path is still active.

- [ ] **Step 3: Implement the minimum replacement**

  Implement only the interfaces and guards above. Delete descriptor, shipping-trigger, TaskPublicationStore, trusted-source extraction, publication recovery, and their tests. Keep historical digest validation small and isolated. Replace mirrored lifecycle prose with a short reference to the canonical compact-pair invariant instead of hand-copying it.

- [ ] **Step 4: Prove GREEN and the size tripwire**

  Run the focused command from Step 2, then:

  ```bash
  env -u GIT_INDEX_FILE /Users/hyungkoookkim/Pipeline/.venv/bin/python scripts/ci_smoke.py
  env -u GIT_INDEX_FILE /bin/bash -n coordination/bin/send-event
  env -u GIT_INDEX_FILE git diff --check
  wc -l scripts/compact_pair_loop.py
  rg -n "TaskPublicationStore|Lane-V-Scope|shipping trigger" scripts coordination/bin AGENTS.md ARCHITECTURE.md docs/protocol/codex .agents/skills .codex/agents
  ```

  Expected: tests and smoke pass; shell/diff checks are clean; compact production module is below 500 lines; active-surface search finds no retired authority mechanism except clearly labeled historical references.

- [ ] **Step 5: Commit and self-review**

  Commit the exact task paths as one local implementation commit. Confirm `scripts/kernel_activation.py` is absent from the diff, production delta is strongly net-negative, the worktree is clean, and no forbidden side effect occurred.

- [ ] **Step 6: Independent review and first compact report**

  A fresh non-author-model Operator reviews the exact implementation diff and commits one plain GO/NITS/FAIL report using the new compact path. On GO, reuse the unchanged Phase 4 Task 2 execution evidence to close its final checkbox without rerunning the failed publication campaign.
