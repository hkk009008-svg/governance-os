# Opus Transport-First Recovery Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking. Live-seat authority remains with the routed Director2 and Operator2 seats.

**Goal:** Restore one real, receipt-bound Opus review through the existing signed-in Claude CLI while preserving fail-closed model checks, one-shot finality, and independent GO authority.

**Architecture:** Recovery is split into four gates. Stage A adds provider-free, secret-safe diagnostics and deterministic fake-client coverage without changing transport behavior. Stage B fixes only the first boundary proven by Stage A. Stage C uses one fresh route-bound canary through `anthropic-claude-existing-session-v1`. Stage D requires independent Operator2 GO, then local merge, post-merge verification, and only then a separately authorized push.

**Tech Stack:** Python 3, `subprocess`, macOS `sandbox-exec`, AF_UNIX verification broker, Claude CLI existing-session transport, pytest, the Opus receipt store, and the Pipeline four-seat mailbox/capacity protocol.

## Global Constraints

- Bind this plan to local `main` at `f0fb231f64b6a22e19ef214e7994f0ab2f3e6183` and prior cycle `pipeline-level5-opus-receipt-integration-2026-07-15` until a committed coordinator route supplies the execution base.
- Receipt `opr1:de2f5b672b8e1ea03b7575d7a636e0d56bef9817f0d8b5b74fb0632678b68f85` is immutable terminal evidence: `status=unavailable`, `unavailable_reason=process_failed`, `failure_stage=provider_exit`, no effective model, and zero findings. Never retry, reset, replay, relabel, or reuse it.
- Stage A authorizes zero provider process attempts. Static binary inspection, local configuration inspection, mock clients, and fixture subprocesses are allowed only when they cannot initiate network transport or a model turn.
- Keep transport profile `anthropic-claude-existing-session-v1`; do not substitute a browser, API, alternate provider, automatic retry, credential entry, token copying, or a broadened environment.
- Preserve the current authoritative model source `system/init.model`. Accept only the existing `is_opus_model` policy during Stage A; any model-family narrowing is a separate reviewed policy change.
- Never serialize raw stdout, raw stderr, prompts, repository content, credentials, tokens, unrestricted environment dumps, or session identifiers into Git, receipts, mailbox events, logs, or diagnostics.
- Coordinator writes only plans, capacity packets, routes, handoffs, and reconciliation evidence. Director2 owns production/test changes; Operator2 owns GO, NITS, or FAIL.
- Every ordinary Git and pytest command starts with `env -u GIT_INDEX_FILE`. Work occurs in an isolated worktree because the shared root contains unrelated live WIP.

## R-INDEPENDENCE Abuse Cases And Coverage Targets

The design-time challenge was supplied by guarded manual ChatGPT Pro consultation `ca74dca9-948a-4b59-8b01-07840cb65715`. The implementation and final verification must enforce these cases:

1. Missing, non-executable, permission-denied, `ENOEXEC`, `EIO`, and generic spawn failures remain fail-closed before or at `provider_spawn` and expose only a finite diagnostic code.
2. Broker creation failure and sandbox-probe failure remain distinguishable as `broker_start` and `sandbox_probe` without leaking filesystem or socket details.
3. A silent or timed-out child is killed as a process group, records one launch, and never retries.
4. Positive child exit, negative signal return, authentication/session failure, sandbox denial, invalid invocation, and unknown nonzero exit remain distinguishable without retaining stderr text.
5. Output truncation wins over otherwise parseable output and preserves only bounded truncation flags plus a finite diagnostic code.
6. Invalid UTF-8, invalid JSON, duplicate or missing `system/init`, events after `result`, missing structured output, and invalid review schema fail at the existing parse/contract/model boundaries.
7. Requested model text is never sufficient. Missing identity and non-Opus `system/init.model` fail closed; an allowed Opus identity plus valid zero findings is an explicit pass.
8. A provider exception after reservation persists one sanitized terminal result; exact replay performs no second provider call, a reserved receipt degrades uncertain, and changed scope conflicts.
9. A fake existing-session client that attempts a startup write under a temporary HOME proves whether the current outer sandbox blocks that boundary. The test may touch only a pytest-owned temporary directory.
10. Every fixture output, serialized review, stored receipt, CLI result, and mailbox summary is scanned for injected sentinel secrets and raw diagnostic text.

## Consultation Summary

- Consultation ID: `ca74dca9-948a-4b59-8b01-07840cb65715`
- Phase: design-time adversarial recovery planning
- Bound HEAD/route: `f0fb231f64b6a22e19ef214e7994f0ab2f3e6183` / `pipeline-level5-opus-receipt-integration-2026-07-15`
- Question: how to restore the existing-session Opus path end to end after one terminal `provider_exit/process_failed` receipt without retry, fallback, or authority drift
- Advice summary: isolate executable, process, I/O, sandbox, session, authentication, parser, model, and receipt layers with zero-provider evidence; add minimum sanitized observability; repair only the first proven boundary; then use one fresh canary and independent GO
- Codex dispositions: adopted transport-first isolation, fake-client coverage, fresh identity per provider attempt, one-shot canary, and GO-before-merge; modified the advice to extend the existing bridge/receipt contract rather than create a parallel diagnostic framework; rejected replacement-first, broad HOME access, API/browser fallback, automatic retry, and canary-before-root-cause; left exact original return code/signal/category and session entitlement unresolved pending Stage A
- Resulting change: the active coordinator route authorizes Stage A only; later repair, canary, merge, and publication each require fresh durable evidence and the appropriate executor token

---

### Task 1: Add a backward-compatible sanitized diagnostic contract

**Files:**

- Modify: `scripts/opus_review_bridge.py`
- Modify: `scripts/opus_review_receipts.py`
- Modify: `tests/unit/test_opus_review_bridge.py`
- Modify: `tests/unit/test_opus_review_receipts.py`

**Interfaces:**

- Consumes: existing `OpusReview`, `_unavailable`, `_perform_provider_review`, `_run_process_group`, `ReceiptRecord`, and `stored_review_from_record` behavior.
- Produces: an additive review schema that preserves legacy `opus-review/v3` reads and emits sanitized `failure_detail` plus nonzero `provider_returncode` only for unavailable results.

- [ ] **Step 1: Write RED schema and secrecy tests**

Add exact tests proving that legacy v3 receipts still load, pass/issues require both diagnostic fields to be null, unavailable results reject unknown detail codes and zero return codes, negative return codes represent signals, and injected stderr sentinels never appear in `json.dumps(review.to_dict())` or persisted receipt bytes.

- [ ] **Step 2: Run the RED selectors**

Run:

```bash
env -u GIT_INDEX_FILE .venv/bin/python -m pytest \
  tests/unit/test_opus_review_bridge.py -k 'failure_detail or provider_returncode or legacy_v3' -q
env -u GIT_INDEX_FILE .venv/bin/python -m pytest \
  tests/unit/test_opus_review_receipts.py -k 'review_schema or legacy_v3 or diagnostic' -q
```

Expected: the new tests fail because the diagnostic fields and legacy/current schema dispatch do not exist.

- [ ] **Step 3: Implement the minimum schema extension**

Keep receipt identity and `opus-review-receipt/v1` unchanged. Teach the review parser to accept the exact legacy v3 field set and the exact current field set; emit the current schema with nullable `failure_detail` and `provider_returncode`. Use a finite `PROVIDER_FAILURE_DETAILS` set containing `binary_missing`, `resolver_error`, `spawn_permission_denied`, `spawn_executable_format`, `spawn_io_error`, `spawn_failed`, `broker_start_failed`, `sandbox_probe_failed`, `provider_timeout`, `authentication`, `session_unavailable`, `sandbox_denied`, `invalid_invocation`, `provider_signal`, `nonzero_exit`, `stdout_limit`, `stderr_limit`, `both_output_limits`, `stream_encoding`, `stream_json`, `stream_schema`, `model_missing`, `model_not_opus`, `review_contract`, and `receipt_recovery`. Never store diagnostic text.

- [ ] **Step 4: Make existing failures populate the finite contract**

Add a pure classifier for `OSError` errno/type and a pure classifier for nonzero child return plus bounded stderr bytes. Authentication/session markers may retain the existing public `authentication_failed` mapping; all other nonzero exits retain `process_failed/provider_exit`. Store the exact nonzero `CapturedProcess.returncode`; derive `provider_signal` only from a negative value. Preserve every existing public unavailable reason and failure stage.

- [ ] **Step 5: Run the schema and existing receipt tests GREEN**

Run:

```bash
env -u GIT_INDEX_FILE .venv/bin/python -m pytest \
  tests/unit/test_opus_review_bridge.py tests/unit/test_opus_review_receipts.py -q
```

Expected: all tests pass and no real Claude executable is launched.

### Task 2: Exercise the exact process and sandbox boundaries with fake clients

**Files:**

- Modify: `tests/unit/test_opus_review_bridge.py`
- Modify only if a production defect in diagnostics is exposed: `scripts/opus_review_bridge.py`

**Interfaces:**

- Consumes: `_sandbox_runtime`, `_run_process_group`, `_perform_provider_review`, `parse_claude_stream`, and pytest temporary directories.
- Produces: generated local fake Claude executables that accept the real argv but cannot access a provider or network transport.

- [ ] **Step 1: Add generated fake-client fixtures**

Create a test helper that writes an executable under `tmp_path` with one baked behavior per file: valid Opus zero-findings stream, valid issues stream, auth exit, session-unavailable exit, sandbox-denied exit, invalid-invocation exit, generic nonzero exit, self-signal, malformed UTF-8, malformed JSON, missing model, non-Opus model, and oversized output. Do not select behavior through the child environment.

- [ ] **Step 2: Prove the existing-session HOME boundary without real session data**

Set `HOME` to a pytest-owned temporary fake home, run a fake client through the real outer profile, and have it attempt one startup write below that fake home. Assert only the finite `sandbox_denied` result and nonzero return code. Never read the user's actual session paths and never broaden the sandbox in Stage A.

- [ ] **Step 3: Prove one launch and exact model parsing**

For every fake client, count `_run_process_group` entry exactly once. Assert success requires exit zero, authoritative `system/init.model`, and parseable structured output; assert zero findings is a valid pass and a Sonnet identity remains unavailable.

- [ ] **Step 4: Run the fake-client matrix**

Run:

```bash
env -u GIT_INDEX_FILE .venv/bin/python -m pytest \
  tests/unit/test_opus_review_bridge.py -k 'fake_cli or process_group or sandbox or effective_model or output_limit' -q
```

Expected: all selected tests pass, provider-attempt count remains zero, and no test writes outside pytest temporary roots.

### Task 3: Commit Stage A and request provider-free Lane V

**Files:**

- Modify: `scripts/opus_review_bridge.py`
- Modify: `scripts/opus_review_receipts.py`
- Modify: `tests/unit/test_opus_review_bridge.py`
- Modify: `tests/unit/test_opus_review_receipts.py`
- Create: `coordination/verification/scopes/b8c59c86-2426-46cf-8975-7b075d75fc09.json`
- Create: one canonical `coordination/mailbox/sent/*-director2-to-operator2-verify-request.md`

**Interfaces:**

- Consumes: the committed coordinator Stage A route and Tasks 1-2 evidence.
- Produces: one shipping diagnostics commit, one exact descriptor-only commit, and one verify-request-only commit; no provider receipt.

- [ ] **Step 1: Run the complete provider-free gate**

Run:

```bash
env -u GIT_INDEX_FILE .venv/bin/python -m pytest \
  tests/unit/test_opus_review_bridge.py tests/unit/test_opus_review_receipts.py \
  tests/unit/test_verification_report_gate.py -q
env -u GIT_INDEX_FILE .venv/bin/python scripts/ci_smoke.py
env -u GIT_INDEX_FILE git diff --check
```

Expected: all tests and smoke pass; `git diff --check` has no output; no provider process or receipt is created.

- [ ] **Step 2: Commit only the diagnostic implementation**

Commit the four implementation/test paths with subject `fix(opus): expose sanitized transport failure detail`. Exclude the shared root's unrelated WIP and every route/receipt/runtime file.

- [ ] **Step 3: Bind descriptor `b8c59c86-2426-46cf-8975-7b075d75fc09`**

Use the committed coordinator route as reviewed base and the shipping diagnostics commit as reviewed head. Set allowed roots to the exact shipping diff. Require this plan, the coordinator route, the prior terminal GO report, and the existing content-addressed Opus advisory prompt authority. Verification commands are the complete provider-free gate above. Commit the descriptor alone.

- [ ] **Step 4: Send one canonical verify-request**

Commit exactly one Director2-to-Operator2 verify-request after the descriptor. It must contain one `Event type: verify-request`, one full lowercase reviewed head, one full lowercase reviewed base, and one exact `Lane-V-Scope` reference. Explicitly state `Opus process attempts authorized: 0`.

### Task 4: Independently verify Stage A and route the proven root boundary

**Files:**

- Read: the exact Stage A base-to-head diff, descriptor, request, plan, and terminal prior receipt evidence.
- Create: one canonical `coordination/mailbox/sent/*-operator2-to-all-verification-report.md`.

**Interfaces:**

- Consumes: the canonical Stage A verify-request.
- Produces: GO, NITS, or FAIL for diagnostic correctness only, plus a first-failed-layer conclusion or an explicit unresolved boundary.

- [ ] **Step 1: Re-run the fake-client and receipt matrices provider-free**

Operator2 verifies the exact diff, legacy receipt readability, public reason/stage compatibility, one-launch behavior, fake HOME boundary, model identity, raw-output secrecy, and no provider/receipt mutation.

- [ ] **Step 2: Return one canonical verdict**

GO means only that Stage A diagnostics are safe and sufficient to route the next hypothesis. It does not mean Opus is fixed. NITS or FAIL blocks repair routing. The report must name the first proven failing boundary or state that zero-provider evidence still leaves a specific two-layer ambiguity.

- [ ] **Step 3: Coordinator opens a fresh Stage B route**

After GO, route one smallest root-cause fix. Executable discovery changes only resolver/path validation; spawn changes only argv, descriptors, cwd, or allowlisted environment; sandbox/session changes grant only a dedicated scratch write path while retaining read-only session access; authentication or entitlement stops for authorized human remediation; parser/model changes require authoritative local fixtures. No provider invocation belongs to Stage B implementation tests.

### Task 5: Run one fresh end-to-end canary, then integrate and publish in order

**Files:**

- Create under a later route: one fresh Lane-V scope descriptor, canonical verify-request, receipt, verification report, coordinator closeout, and side-effect executor tokens.

**Interfaces:**

- Consumes: a proven Stage B root fix with focused tests and independent review.
- Produces: one terminal canary receipt and, only on success, final independent GO and publication evidence.

- [ ] **Step 1: Authorize one canary with a fresh identity**

The later coordinator route names one executor, one non-sensitive minimal review fixture, one state binding, one route-bound descriptor, and exactly one provider process attempt through `anthropic-claude-existing-session-v1`. A failed diagnostic route is not reused as the canary.

- [ ] **Step 2: Require full-path success**

Success requires process exit zero; correlation to the fresh route and receipt; authoritative allowed Opus identity from `system/init.model`; parseable structured findings or explicit zero findings; receipt publication; zero raw secret leakage; and exactly one launch. Timeout, missing/non-Opus model, malformed output, receipt mismatch, secrecy breach, or retry need is terminal failure.

- [ ] **Step 3: Obtain independent Operator2 GO**

Operator2 verifies the final repair diff, Stage A abuse cases, Stage B root-cause evidence, fresh canary receipt, effective model, one-shot compliance, and exact state binding. Opus remains advisory and cannot self-certify GO.

- [ ] **Step 4: Merge locally, verify, then push**

After binding GO and with no post-GO changes, the coordinator performs the local merge first. Re-run focused tests, smoke, exact merged-tree and remote-divergence checks. Only after those pass may the named coordinator executor push under a separate remote-ref side-effect token. Any post-GO edit requires renewed independent review.

## Self-Review

- Spec coverage: terminal receipt finality, zero-provider isolation, minimum diagnostics, fake clients, root-cause-only repair, one fresh canary, independent GO, local merge, and push order are each assigned to a task.
- Placeholder scan: the plan contains no deferred implementation marker; later-route artifacts are explicitly gated deliverables rather than missing design.
- Type consistency: `failure_detail` and `provider_returncode` are nullable only outside successful reviews; the same names flow through bridge serialization, receipt reading, tests, and Lane V evidence.
