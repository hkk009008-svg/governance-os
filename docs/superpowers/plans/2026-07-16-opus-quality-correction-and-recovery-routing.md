# Opus Quality Correction and Recovery Routing Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking. Live-seat authority remains with the routed Director2 and Operator2 seats.

**Goal:** Close the two independently confirmed Stage-A quality defects with one append-only provider-free correction, obtain lawful Operator2 GO, and resume the existing transport-first Stage B-D recovery without retry, fallback, or authority drift.

**Architecture:** Preserve the immutable `R -> M0 -> F` history and append exactly one quality commit `Q`. `Q` adds semantic reason/stage and detail consistency validators and distinguishes broker startup from broker cleanup through a finite `broker_cleanup/broker_cleanup_failed` classification. Cleanup failure before any completed provider result fails closed with that tuple; cleanup failure after one completed result does not discard it, relabel it, or cause a retry, and the completed result continues through the existing parser and contract checks. A separately committed external authority object binds the correction plan, umbrella design, correction route, and two pre-descriptor review results without widening `R..Q`. A descriptor-only commit `D` and canonical verify-request-only commit `T` then bind `R..Q`, with `T` referencing that external object exactly once. Only a provider-free Operator2 GO may reopen the original plan's Stage B root repair; Stage C remains one separately authorized fresh canary and Stage D remains GO-before-integration and separately authorized publication.

**Tech Stack:** Python 3.14, frozen dataclasses, context managers, the existing Opus review and receipt schemas, pytest, Git append-only ranges, Lane-V descriptors, and the Pipeline mailbox/capacity protocol.

## Global Constraints

- The approved umbrella design is `docs/superpowers/specs/2026-07-16-pipeline-recovery-sequence-design.md` at `426744766711d4d6057a4698f5bb19d454ad621d`.
- This plan is a correction companion to `docs/superpowers/plans/2026-07-15-opus-transport-first-recovery.md`; it supersedes only that plan's Stage-A exact-one-fix topology and finite-stage clauses.
- Preserve this immutable history byte-for-byte:

  ```text
  R   40fd0a5e43c6b28330ced9ddffe01483cde42b65
  └─ M0  56091d107382abfe9f06df1aa4cd003d71be7b5e
     └─ F   16c4f83aef4130d977a91d623a9254c4fd46980a
  ```

- The only authorized implementation continuation is `F -> Q`, where `Q` is one commit and `parent(Q) == F`. Do not amend, rebase, reset, replace, rebuild, merge into, or cherry-pick onto `R`, `M0`, or `F`.
- The `F..Q` write set and aggregate `R..Q` write set are both bounded to these four paths:

  - `scripts/opus_review_bridge.py`
  - `scripts/opus_review_receipts.py`
  - `tests/unit/test_opus_review_bridge.py`
  - `tests/unit/test_opus_review_receipts.py`

- Descriptor task `b8c59c86-2426-46cf-8975-7b075d75fc09` retains exact reviewed base `R`. The legacy `lane-v-scope/v1` descriptor has no `reviewed_head` field; canonical verify-request `T` changes the bound reviewed head from `F` to `Q`. Its descriptor commit is `D`; its request-only commit is `T`.
- Stage A, including `Q`, authorizes zero Claude/Opus provider attempts and zero receipt mutations. All tests use injected factories, fake runners, and temporary paths.
- Preserve every existing public unavailable reason. Preserve every existing failure stage and add exactly one stage, `broker_cleanup`; add exactly one finite detail, `broker_cleanup_failed`.
- Broker cleanup failure before a provider result exists remains fail-closed as `sandbox_unavailable/broker_cleanup/broker_cleanup_failed`. If the runner already returned one completed result, broker cleanup failure must not discard or relabel it: parse it once through the existing model/review contract, preserve the resulting pass/issues/unavailable semantics, perform no retry, and serialize no raw cleanup text. A completed result never gains findings or authority merely because broker cleanup failed.
- Legacy `opus-review/v3` records with no diagnostic detail remain readable only for reason/stage pairs actually emitted by a legacy or current producer. Null detail is not permission for a contradictory reason/stage pair. Every current record must be semantically consistent across reason, stage, truncation flags, detail, and return code.
- Raw exception strings, stdout, stderr, paths, socket names, prompts, credentials, session identifiers, and provider content must never enter durable review, receipt, mailbox, or test artifacts.
- Coordinator owns only metadata correction, route validation, joins, and reconciliation. Director2 owns production/test changes. Operator2 owns GO, NITS, or FAIL.
- Use the isolated worktree `.worktrees/opus-transport-first-stage-a-director2`. Every ordinary Git and pytest command starts with `env -u GIT_INDEX_FILE`.
- Commit, provider launch, receipt mutation, local integration, push, and external publication remain separate authorities. This plan authorizes none merely by existing.

## R-INDEPENDENCE Abuse Cases and Coverage Targets

The independent Stage-A code-quality review and the Director2 provider-free reproductions require the final diff and Operator2 review to cover all of these cases:

1. A current review cannot pair `claude_not_found` with `provider_spawn/stdout_limit`, a nonzero return code, and false truncation flags.
2. Every finite detail is accepted only with its emitted public reason and stage; details shared by more than one lawful public result, such as `binary_missing`, enumerate those results explicitly.
3. Legacy unavailable reviews without `failure_detail` or `provider_returncode` remain readable and do not gain invented diagnostics.
4. Output-limit detail exactly matches the two truncation booleans; any other reason or stage with a true truncation flag is rejected.
5. `provider_signal` requires a negative return code; positive exits require their matching non-signal detail; zero remains forbidden; no return code is accepted for startup, cleanup, parse, model, contract, or receipt-recovery details.
6. A runtime or broker `__enter__` `OSError` before the fake runner remains `sandbox_unavailable/broker_start/broker_start_failed` and launches nothing.
7. A broker `__exit__` `OSError` before any completed fake-runner result becomes `sandbox_unavailable/broker_cleanup/broker_cleanup_failed`, never `broker_start`.
8. Broker cleanup failure before a completed result exists returns the finite cleanup tuple; broker cleanup failure after exactly one completed result preserves and parses that result once, runs no retry, and leaks no raw error text.
9. A body exception is neither swallowed nor relabeled as cleanup unless `__exit__` itself fails; the lifecycle wrapper preserves normal context-manager suppression semantics.
10. Receipt serialization and reloading accept the new finite stage/detail, reject unknown values, and preserve terminal receipt identity rules.
11. All existing resolver, spawn, timeout, output-limit, parser, model, contract, and receipt-recovery tuples remain accepted and round-trip exactly.
12. The complete Stage-A provider-free suite, smoke, diff check, topology check, and terminal prior-receipt digest remain green and unchanged.
13. The provider-free authority resolver binds exactly `R..Q`, descriptor `D`, request `T`, all requirement blobs, the exact changed paths, and the trigger identity without reserving an attempt, creating a receipt/lock, or calling either provider-capable resolver.
14. The external authority object is content-addressed and binds the exact correction-plan, umbrella-design, correction-route, and two independent-review identities/results; it remains outside descriptor `requirement_paths` and is referenced exactly once by `T`.

---

### Task 1: Commit the coordinator correction route

**Files:**

- Modify: `coordination/capacity/packets/2026-07-15-pipeline-opus-transport-first-recovery-stage-a-director2-diagnostics.json`
- Modify: `coordination/capacity/packets/2026-07-15-pipeline-opus-transport-first-recovery-stage-a-operator2-lanev.json`
- Modify: `coordination/capacity/packets/2026-07-15-pipeline-opus-transport-first-recovery-stage-a-coordinator-join.json`
- Create: the canonical coordinator-to-all coordination event produced by `coordination/bin/send-event`

**Interfaces:**

- Consumes: quality blocker `coordination/mailbox/sent/2026-07-15T16-49-37Z-director2-to-coordinator-coordination.md`, umbrella design `4267447`, and the fixed owner freeze `docs/HANDOFF-owner-2026-07-16-opus-stage-a.md` bound by its unique introduction commit, Git blob OID, and SHA-256 digest.
- Produces: one capacity-valid correction that authorizes `Q`, binds `R..Q`, retains descriptor identity, and keeps provider attempts at zero.

- [ ] **Step 1: Refresh the hot-tree and mailbox state**

Run from the primary checkout:

```bash
env -u GIT_INDEX_FILE git log --oneline -3
env -u GIT_INDEX_FILE .venv/bin/python \
  .agents/skills/four-seat-protocol/scripts/seat_status.py coordinator --wave 2
env -u GIT_INDEX_FILE .venv/bin/python scripts/protocol_capacity_board.py --wave 2
RECEIPT_COMMON_DIR="$(env -u GIT_INDEX_FILE git rev-parse \
  --path-format=absolute --git-common-dir)"
RECEIPT_STORE_ROOT="$(dirname "$RECEIPT_COMMON_DIR")/.codex/runtime/opus-review-receipts/v1"
RECEIPT_MANIFEST_BEFORE_SHA="$(
  RECEIPT_STORE_ROOT="$RECEIPT_STORE_ROOT" \
  env -u GIT_INDEX_FILE .venv/bin/python - <<'PY'
import hashlib
import json
import os
from pathlib import Path
import stat

root = Path(os.environ["RECEIPT_STORE_ROOT"])
rows = []
if root.exists():
    for path in sorted(root.iterdir(), key=lambda item: os.fsencode(item.name)):
        observed = path.lstat()
        if not stat.S_ISREG(observed.st_mode):
            raise SystemExit(f"non-regular receipt-store entry: {path.name}")
        rows.append(
            {
                "name": path.name,
                "mode": stat.S_IMODE(observed.st_mode),
                "uid": observed.st_uid,
                "nlink": observed.st_nlink,
                "size": observed.st_size,
                "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
            }
        )
raw = json.dumps(
    rows, sort_keys=True, separators=(",", ":"), ensure_ascii=True
).encode("ascii")
print("sha256:" + hashlib.sha256(raw).hexdigest())
PY
)"
printf '%s\n' "$RECEIPT_MANIFEST_BEFORE_SHA" | \
  grep -Eq '^sha256:[0-9a-f]{64}$'
```

Expected: the quality blocker remains the unresolved Stage-A join input, the coordinator mailbox is surfaced without consumption, the capacity board identifies Director2 as the only implementation owner and Operator2 as the blocked verifier, and the manifest command emits one deterministic digest without creating or opening a receipt lock. If newer mail, a moved Stage-A branch, or a non-regular receipt-store entry changes that state, stop and reconcile before writing.

Resolve `docs/HANDOFF-owner-2026-07-16-opus-stage-a.md` from committed primary `main`, prove its unique introduction commit is an ancestor of current `main`, validate its exact blob and SHA-256 digest, and require it binds Director2, `R`, `M0`, `F`, the four-path aggregate range, zero provider attempts, and no descriptor/GO/integration claim. Re-read the Stage-A worktree and require exact clean head `F`. The correction route must carry the owner-handoff path/commit/blob/digest and exact-old `F`; a missing, duplicate, stale, or mismatched freeze blocks before packet or branch mutation. Once that route commits, only its exact `Q` append may advance the branch without a replacement owner handoff.

- [ ] **Step 2: Amend the three Stage-A packets**

Keep every existing task-board, owner, pair, and zero-provider constraint. Replace the `F` terminal boundary with this exact topology:

```text
R -> M0 -> F -> Q -> D -> T
```

Record `parent(Q) == F`, one `Q`, exact four-path `F..Q` and `R..Q` allowlists, the new finite cleanup stage/detail, renewed spec and quality review before `D`, and Operator2 as the only Stage-A verdict owner. The coordinator join remains blocked on one canonical GO/NITS/FAIL for `R..Q`.

- [ ] **Step 3: Generate one consolidated correction event**

Run and capture the one exact generated path:

```bash
SEND_OUTPUT="$(coordination/bin/send-event coordinator all coordination \
  "authorize Stage A semantic diagnostic and cleanup correction")"
ROUTE_EVENT="${SEND_OUTPUT#created }"
ROUTE_EVENT="${ROUTE_EVENT%% *}"
test -f "$ROUTE_EVENT"
printf '%s\n' "$ROUTE_EVENT"
```

Populate the generated body with findings first, exact SHAs, exact packet IDs, the `R -> M0 -> F -> Q -> D -> T` contract, the two finite additions, provider-attempt count zero, `Receipt-store manifest before Stage A: $RECEIPT_MANIFEST_BEFORE_SHA`, and the join condition. This committed field is the comparison baseline for Task 6 and Completion Verification. Do not consume coordinator mail.

- [ ] **Step 4: Validate before commit**

Run the board against the generated route path:

```bash
env -u GIT_INDEX_FILE .venv/bin/python scripts/protocol_capacity_board.py --wave 2
env -u GIT_INDEX_FILE .venv/bin/python scripts/protocol_capacity_board.py \
  --wave 2 --validate-route "$ROUTE_EVENT"
env -u GIT_INDEX_FILE .venv/bin/python scripts/check_coordination.py
env -u GIT_INDEX_FILE git diff --check -- \
  coordination/capacity/packets/2026-07-15-pipeline-opus-transport-first-recovery-stage-a-director2-diagnostics.json \
  coordination/capacity/packets/2026-07-15-pipeline-opus-transport-first-recovery-stage-a-operator2-lanev.json \
  coordination/capacity/packets/2026-07-15-pipeline-opus-transport-first-recovery-stage-a-coordinator-join.json \
  coordination/mailbox/sent/
```

Expected: both board commands and coordination check pass; diff check prints nothing; `ROUTE_EVENT` is one canonical coordinator-to-all event path.

- [ ] **Step 5: Commit only correction metadata**

Use a scoped temporary index if the shared index is dirty. Stage the three exact packet paths and the one exact generated event with `git add -f`, inspect `git diff --cached --name-only`, and commit with subject:

```text
docs(protocol): authorize Opus Stage A quality correction
```

Expected: exactly four paths in the commit and no production/test file.

### Task 2: Add RED semantic-consistency tests

**Files:**

- Modify: `tests/unit/test_opus_review_bridge.py`
- Modify: `tests/unit/test_opus_review_receipts.py`

**Interfaces:**

- Consumes: `OpusReview.unavailable`, `OpusReview.from_dict`, `_failure_diagnostics`, and `PROVIDER_FAILURE_DETAILS`.
- Produces: table-driven current-schema rejection and legacy-schema compatibility tests.

- [ ] **Step 1: Prove the reproduced contradiction is accepted before the fix**

Add `test_opus_review_rejects_semantically_contradictory_diagnostics`. Construct the exact reproduced tuple:

```python
bridge.OpusReview.unavailable(
    reviewed_head="a" * 40,
    reviewed_base="b" * 40,
    review_profile="codex-lane-v",
    authorization_source="user-task:quality-correction",
    reason="claude_not_found",
    failure_stage="provider_spawn",
    failure_detail="stdout_limit",
    provider_returncode=7,
)
```

Assert `ReviewContractError.reason == "invalid_schema"` after implementation. Before implementation the constructor must return normally, proving the test is non-vacuous.

- [ ] **Step 2: Add the complete valid-tuple matrix**

Add `test_opus_review_accepts_every_emitted_diagnostic_tuple` covering all current emitter families: resolver/binary, spawn errno, broker start, sandbox probe, timeout, authentication/session, nonzero/signal, every output-limit flag combination, stream encoding/JSON/schema, missing/non-Opus model, review contract/scope mismatch, the fail-closed provider-wrapper `process_failed/provider_exit/review_contract` tuple, and receipt recovery. Add one row for `sandbox_unavailable/broker_cleanup/broker_cleanup_failed`. For every reason/stage pair historically emitted by a legacy producer, add the corresponding null-detail/null-return-code row with false truncation flags.

- [ ] **Step 3: Add invalid cross-product cases**

Parameterize one mutation at a time: wrong reason, wrong stage, wrong truncation booleans, forbidden return-code sign, forbidden non-null return code, and detail with no matching rule. Include the exact null-detail mutation `claude_not_found/contract_validation/null/null` with both truncation flags false; it must fail despite having the legacy field shape. Assert all cases fail as `invalid_schema`, without matching raw error text.

- [ ] **Step 4: Pin legacy and receipt behavior**

In bridge tests, load a `_LEGACY_REVIEW_FIELDS` unavailable mapping with no detail or return code and one historically emitted reason/stage pair and assert it remains readable; mutate only its stage and assert rejection. Add structural assertions that the reason/stage table keys equal `UNAVAILABLE_REASONS` and the detail-rule keys equal `PROVIDER_FAILURE_DETAILS`, including the new cleanup detail. In receipt tests, assert `broker_cleanup_failed` is finite and round-trips, unknown detail/stage fails, and terminal receipt identity remains unchanged.

- [ ] **Step 5: Run RED**

```bash
env -u GIT_INDEX_FILE .venv/bin/python -m pytest \
  tests/unit/test_opus_review_bridge.py \
  -k 'semantically_contradictory or emitted_diagnostic_tuple or diagnostic_cross_product or legacy_unavailable' -q
env -u GIT_INDEX_FILE .venv/bin/python -m pytest \
  tests/unit/test_opus_review_receipts.py \
  -k 'broker_cleanup or failure_detail or terminal' -q
```

Expected: the contradiction and new cleanup-vocabulary tests fail for the intended missing validation/vocabulary reasons; existing legacy tests pass.

### Task 3: Implement one semantic diagnostic contract

**Files:**

- Modify: `scripts/opus_review_bridge.py`
- Modify: `scripts/opus_review_receipts.py`
- Modify: `tests/unit/test_opus_review_bridge.py`
- Modify: `tests/unit/test_opus_review_receipts.py`

**Interfaces:**

- Consumes: `_failure_diagnostics(failure_detail, provider_returncode)` and the current emitted tuple vocabulary.
- Produces: `_validate_failure_diagnostics` returning `tuple[str | None, int | None]`, one finite rule table, and additive cleanup vocabulary.

- [ ] **Step 1: Add the two finite vocabulary entries**

Add `broker_cleanup` to `PROVIDER_FAILURE_STAGES` in `scripts/opus_review_bridge.py`. Add `broker_cleanup_failed` to `PROVIDER_FAILURE_DETAILS` in `scripts/opus_review_receipts.py`. Do not rename or remove an existing value or bump receipt identity.

- [ ] **Step 2: Define complete reason/stage and detail contract tables**

Keep `_failure_diagnostics` as the primitive type/sign validator. Add a private immutable reason-to-stage mapping applied to both null and non-null detail records. Its keys equal `UNAVAILABLE_REASONS`, and its values contain exactly the producer-audited pairs:

| Unavailable reason | Allowed failure stages |
|---|---|
| `authorization_missing` | `contract_validation` |
| `claude_not_found` | `provider_spawn` |
| `authentication_failed` | `provider_exit` |
| `timeout` | `provider_timeout` |
| `process_failed` | `provider_spawn`, `provider_exit` |
| `invalid_json` | `response_parse` |
| `invalid_schema` | `response_parse`, `contract_validation` |
| `reviewed_scope_mismatch` | `contract_validation` |
| `effective_model_missing` | `model_validation` |
| `effective_model_not_opus` | `model_validation` |
| `sandbox_unavailable` | `broker_start`, `sandbox_probe`, `broker_cleanup` |
| `output_limit` | `provider_exit` |
| `attempt_state_uncertain` | `receipt_recovery` |

Before implementation, grep every `OpusReview.unavailable` and `_unavailable` production write at immutable `F` and reconcile the table against actual legacy/current emitters. A newly discovered lawful pair updates the table and valid matrix before `Q`; an unexplained pair blocks rather than being accepted generically.

Add a second private immutable mapping whose key is each non-null finite detail and whose value enumerates the allowed `(unavailable_reason, failure_stage)` pairs. Assert its key set is exactly `PROVIDER_FAILURE_DETAILS`. `binary_missing` explicitly allows both `claude_not_found/provider_spawn` and `process_failed/provider_spawn`. `review_contract` explicitly allows all three existing emitters: `invalid_schema/contract_validation`, `reviewed_scope_mismatch/contract_validation`, and the fail-closed provider-wrapper exception tuple `process_failed/provider_exit`. Every other detail has the emitted pair documented by Task 2; `broker_cleanup_failed` maps only to `sandbox_unavailable/broker_cleanup`.

- [ ] **Step 3: Add the cross-field validator**

Implement this exact interface:

```python
def _validate_failure_diagnostics(
    *,
    unavailable_reason: str,
    failure_stage: str,
    stdout_truncated: bool,
    stderr_truncated: bool,
    failure_detail: object,
    provider_returncode: object,
) -> tuple[str | None, int | None]:
```

It first calls `_failure_diagnostics`, then:

- rejects every unavailable reason/failure-stage pair absent from the reason/stage table, regardless of whether detail and return code are null;
- accepts both diagnostics as null as the backward-compatible unavailable form only when the public pair is producer-audited and both truncation flags are false, without inventing a detail or return code;
- rejects a non-null detail whose public pair is absent from its rule;
- requires output-limit details to match their exact boolean pair and rejects truncation for every non-output detail;
- requires negative return code only for `provider_signal` or an output-limit result whose captured process was signaled;
- permits a positive return code only for provider-exit details emitted from a nonzero child or for output-limit precedence;
- forbids a return code for startup, cleanup, probe, timeout, parse, model, contract, and recovery details.

Call it from `OpusReview.unavailable`; `from_dict` continues to delegate through that constructor. Keep error reason `invalid_schema` and use only finite field names in messages.

- [ ] **Step 4: Run focused GREEN**

```bash
env -u GIT_INDEX_FILE .venv/bin/python -m pytest \
  tests/unit/test_opus_review_bridge.py \
  -k 'diagnostic or failure_detail or provider_returncode or legacy_v3' -q
env -u GIT_INDEX_FILE .venv/bin/python -m pytest \
  tests/unit/test_opus_review_receipts.py \
  -k 'review_schema or diagnostic or broker_cleanup or terminal' -q
```

Expected: all selected tests pass and no provider process runs.

### Task 4: Distinguish startup and cleanup lifecycle failures

**Files:**

- Modify: `scripts/opus_review_bridge.py`
- Modify: `tests/unit/test_opus_review_bridge.py`

**Interfaces:**

- Consumes: injected `broker_factory`, fake runner, and `_perform_provider_review`; the sandbox runtime's existing behavior remains outside this confirmed broker-cleanup correction.
- Produces: a private broker lifecycle wrapper that carries only `start` or `cleanup`, a causally correct unavailable result when no completed provider result exists, and preservation of an already completed result.

- [ ] **Step 1: Add RED lifecycle tests**

Add these exact tests:

- Rename the existing runtime-factory regression to `test_review_failure_detail_sanitizes_runtime_enter_oserror_without_launch`; retain its existing finite `broker_start` compatibility result and runner-calls-zero assertion. This test does not prove broker entry. Relabeling sandbox-runtime enter or exit failures is explicitly outside this correction.
- `test_review_broker_enter_oserror_is_broker_start_without_launch` supplies a broker-factory object whose actual `__enter__` raises an `OSError` containing a secret sentinel. Assert runner calls zero, status unavailable, reason `sandbox_unavailable`, stage `broker_start`, detail `broker_start_failed`, return code null, and sentinel absent from the serialized result.
- `test_review_failure_detail_distinguishes_broker_cleanup_oserror_before_result` uses a broker whose `__enter__` succeeds, a false sandbox probe that prevents the runner, and an `__exit__` `OSError` containing a secret sentinel. Assert runner calls zero, status unavailable, reason `sandbox_unavailable`, stage `broker_cleanup`, detail `broker_cleanup_failed`, return code null, and sentinel absent from `json.dumps(result.to_dict())`.
- `test_lifecycle_wrapper_preserves_body_exception_and_suppression` proves an ordinary body exception is propagated or suppressed according to `__exit__`, while an `__exit__` `OSError` becomes cleanup.
- `test_review_broker_cleanup_failure_preserves_completed_pass_without_retry` returns one valid pass stream, raises during cleanup, and asserts one runner call, status pass, the existing parsed model, no unavailable fields, and no retry.
- `test_review_broker_cleanup_failure_preserves_completed_issues_without_retry` returns one valid issues stream, raises during cleanup, and asserts one runner call, the exact parsed finite findings, no unavailable fields, and no retry.
- `test_review_broker_cleanup_failure_matches_completed_unavailable_baseline_without_retry` is parameterized over positive nonzero exit, negative provider signal, stdout truncation, malformed stream JSON, missing model, and review-contract mismatch. For each case, compare the cleanup-failure result with a no-cleanup-failure baseline. Assert identical finite `to_dict()` semantics, exactly one runner call per invocation, no retry, and no raw cleanup sentinel.

- [ ] **Step 2: Run lifecycle RED**

```bash
env -u GIT_INDEX_FILE .venv/bin/python -m pytest \
  tests/unit/test_opus_review_bridge.py \
  -k 'runtime_enter_oserror or broker_enter_oserror or broker_cleanup_oserror or lifecycle_wrapper or cleanup_failure_preserves or cleanup_failure_matches' -q
```

Expected: the renamed runtime-enter regression passes under existing behavior; the true broker-entry test pins the intended branch; the no-result cleanup test fails because cleanup is mislabeled as startup; and the completed-result comparison tests fail because the result is discarded before the normal parser/contract path.

- [ ] **Step 3: Implement the private lifecycle wrapper**

Add a private exception that stores only the finite phase `start` or `cleanup`, never the caught exception text. Add a private broker context manager that explicitly calls the supplied broker's `__enter__` and `__exit__`, maps only `OSError` from `__enter__` to `start`, maps only `OSError` from `__exit__` to `cleanup`, and preserves normal body exception/suppression semantics.

Wrap only the verification broker; do not silently classify sandbox-runtime lifecycle failures as broker failures in this bounded correction. Initialize the completed-process slot before entering the broker, and catch the private broker-lifecycle exception inside the sandbox-runtime `with` boundary so the runtime cannot suppress or reinterpret it. In `_perform_provider_review`, map lifecycle `start` to the existing `sandbox_unavailable/broker_start/broker_start_failed` tuple. On lifecycle `cleanup`, return `sandbox_unavailable/broker_cleanup/broker_cleanup_failed` only when the runner has not produced a completed process. When a completed process exists, retain it and continue exactly once through the existing output-limit, return-code, stream, model, and review-contract parsing path. Keep resolver, sandbox-probe, runner, parser, and model handling otherwise unchanged; never serialize the caught cleanup exception or retry the runner.

- [ ] **Step 4: Run lifecycle GREEN and mutation checks**

```bash
env -u GIT_INDEX_FILE .venv/bin/python -m pytest \
  tests/unit/test_opus_review_bridge.py \
  -k 'broker or lifecycle or injected_host_seam or timeout_without_retry' -q
```

Expected: all selected tests pass; startup, no-result cleanup, and completed-result-preservation mutations each flip at least one assertion; provider-attempt count remains zero.

### Task 5: Create exactly one append-only quality commit `Q`

**Files:**

- Modify exactly the four Stage-A implementation/test paths named in Global Constraints.

**Interfaces:**

- Consumes: committed coordinator correction from Task 1 and green Tasks 2-4.
- Produces: one commit `Q` whose sole parent is `F` and whose subject is `fix(opus): validate diagnostics and cleanup lifecycle`.

- [ ] **Step 1: Rebind to the exact branch and verify scope**

```bash
env -u GIT_INDEX_FILE git -C .worktrees/opus-transport-first-stage-a-director2 \
  rev-parse HEAD^{commit}
env -u GIT_INDEX_FILE git -C .worktrees/opus-transport-first-stage-a-director2 \
  status --short
```

Expected: HEAD is exactly `16c4f83aef4130d977a91d623a9254c4fd46980a` and only the four authorized paths contain the Task 2-4 edits. Any other path or moved HEAD stops the task.

- [ ] **Step 2: Run the complete provider-free gate**

```bash
env -u GIT_INDEX_FILE .venv/bin/python -m pytest \
  tests/unit/test_opus_review_bridge.py \
  tests/unit/test_opus_review_receipts.py \
  tests/unit/test_verification_report_gate.py -q
env -u GIT_INDEX_FILE .venv/bin/python scripts/ci_smoke.py
env -u GIT_INDEX_FILE git diff --check
```

Run these commands inside the Stage-A worktree. Expected: all tests and smoke pass, diff check prints nothing, no provider process launches, and no receipt changes.

- [ ] **Step 3: Commit `Q` with strict pathspecs**

Stage exactly the four paths, inspect `git diff --cached --name-only`, then commit once with the fixed subject. Do not create a separate test or cleanup commit.

- [ ] **Step 4: Prove topology and aggregate scope**

```bash
Q_SHA="$(env -u GIT_INDEX_FILE git rev-parse 'HEAD^{commit}')"
test "$(env -u GIT_INDEX_FILE git rev-parse "${Q_SHA}^")" = \
  16c4f83aef4130d977a91d623a9254c4fd46980a
env -u GIT_INDEX_FILE git rev-list --parents --max-count=4 "$Q_SHA"
env -u GIT_INDEX_FILE git diff --name-only \
  16c4f83aef4130d977a91d623a9254c4fd46980a.."$Q_SHA"
env -u GIT_INDEX_FILE git diff --name-only \
  40fd0a5e43c6b28330ced9ddffe01483cde42b65.."$Q_SHA"
```

Expected: strict `R -> M0 -> F -> Q`; `F..Q` and `R..Q` each list only the four allowed paths, with `R..Q` listing all four.

### Task 6: Re-review `R..Q`, freeze descriptor `D`, and trigger `T`

**Files:**

- Create on the primary branch: `coordination/verification/authorities/b8c59c86-2426-46cf-8975-7b075d75fc09.json`
- Create: `coordination/verification/scopes/b8c59c86-2426-46cf-8975-7b075d75fc09.json`
- Create: one canonical Director2-to-Operator2 verify-request event

**Interfaces:**

- Consumes: immutable `R..Q`, provider-free evidence, the committed correction plan and umbrella design, and the committed correction route.
- Produces: fresh independent spec pass, fresh independent code-quality pass, one content-addressed external authority commit on the primary branch, descriptor-only `D`, and request-only `T`.

- [ ] **Step 1: Obtain two fresh independent reviews**

The spec reviewer checks `R..Q` against both the original Stage-A plan and this correction plan. The code-quality reviewer asks only whether the actual diff closes the semantic-tuple and lifecycle defects without regressions or secret leakage. Record two distinct reviewer identities, their harnesses, exact reviewed range, exact question digests, result, and finite findings. Both results must be `PASS` with empty blocking findings. Any Critical or Important finding stops before authority-object or descriptor creation and returns to the coordinator; no second post-`Q` implementation commit is authorized.

- [ ] **Step 2: Seal one external authority object outside `R..Q`**

The coordinator refreshes mailbox/capacity and creates exactly one canonical JSON object at:

```text
coordination/verification/authorities/b8c59c86-2426-46cf-8975-7b075d75fc09.json
```

Before writing it, require a clean committed copy of this plan and resolve every source identity with Git:

```bash
CORRECTION_PLAN_PATH=docs/superpowers/plans/2026-07-16-opus-quality-correction-and-recovery-routing.md
test -z "$(env -u GIT_INDEX_FILE git status --short -- \
  "$CORRECTION_PLAN_PATH")"
CORRECTION_PLAN_COMMIT="$(env -u GIT_INDEX_FILE git log -1 \
  --format=%H -- "$CORRECTION_PLAN_PATH")"
CORRECTION_PLAN_BLOB="$(env -u GIT_INDEX_FILE git rev-parse \
  "$CORRECTION_PLAN_COMMIT:$CORRECTION_PLAN_PATH")"
UMBRELLA_COMMIT=426744766711d4d6057a4698f5bb19d454ad621d
UMBRELLA_PATH=docs/superpowers/specs/2026-07-16-pipeline-recovery-sequence-design.md
UMBRELLA_BLOB="$(env -u GIT_INDEX_FILE git rev-parse \
  "$UMBRELLA_COMMIT:$UMBRELLA_PATH")"
ROUTE_COMMIT="$(env -u GIT_INDEX_FILE git log --all --format=%H \
  --grep='^docs(protocol): authorize Opus Stage A quality correction$')"
test "$(printf '%s\n' "$ROUTE_COMMIT" | grep -Ec '^[0-9a-f]{40}$')" = 1
env -u GIT_INDEX_FILE git merge-base --is-ancestor \
  "$UMBRELLA_COMMIT" "$ROUTE_COMMIT"
ROUTE_EVENT="$(env -u GIT_INDEX_FILE git diff-tree \
  --no-commit-id --name-only -r "$ROUTE_COMMIT" | sed -n \
  '/^coordination\/mailbox\/sent\/.*-coordinator-to-all-coordination\.md$/p')"
test "$(printf '%s\n' "$ROUTE_EVENT" | grep -Ec \
  '^coordination/mailbox/sent/.*-coordinator-to-all-coordination\.md$')" = 1
ROUTE_BLOB="$(env -u GIT_INDEX_FILE git rev-parse \
  "$ROUTE_COMMIT:$ROUTE_EVENT")"
printf '%s\n' \
  "$CORRECTION_PLAN_COMMIT" "$CORRECTION_PLAN_BLOB" \
  "$UMBRELLA_COMMIT" "$UMBRELLA_BLOB" \
  "$ROUTE_COMMIT" "$ROUTE_BLOB" | \
  grep -Ec '^[0-9a-f]{40}$' | grep -qx '6'
```

Any uncommitted plan byte, missing route, or changed source object stops before authority-object construction.

The object contains exactly these top-level fields:

```json
{
  "schema_version": "stage-a-external-authority/v1",
  "task_id": "b8c59c86-2426-46cf-8975-7b075d75fc09",
  "reviewed_base": "40fd0a5e43c6b28330ced9ddffe01483cde42b65",
  "reviewed_head": "$Q_SHA",
  "correction_plan": {
    "commit": "$CORRECTION_PLAN_COMMIT",
    "path": "docs/superpowers/plans/2026-07-16-opus-quality-correction-and-recovery-routing.md",
    "blob_id": "$CORRECTION_PLAN_BLOB"
  },
  "umbrella_design": {
    "commit": "426744766711d4d6057a4698f5bb19d454ad621d",
    "path": "docs/superpowers/specs/2026-07-16-pipeline-recovery-sequence-design.md",
    "blob_id": "$UMBRELLA_BLOB"
  },
  "correction_route": {
    "commit": "$ROUTE_COMMIT",
    "path": "$ROUTE_EVENT",
    "blob_id": "$ROUTE_BLOB"
  },
  "pre_descriptor_reviews": [
    {
      "kind": "spec",
      "reviewer_identity": "$SPEC_REVIEWER_ID",
      "harness": "$SPEC_REVIEW_HARNESS",
      "question_sha256": "$SPEC_QUESTION_SHA256",
      "reviewed_base": "40fd0a5e43c6b28330ced9ddffe01483cde42b65",
      "reviewed_head": "$Q_SHA",
      "result": "PASS",
      "findings": []
    },
    {
      "kind": "code-quality",
      "reviewer_identity": "$QUALITY_REVIEWER_ID",
      "harness": "$QUALITY_REVIEW_HARNESS",
      "question_sha256": "$QUALITY_QUESTION_SHA256",
      "reviewed_base": "40fd0a5e43c6b28330ced9ddffe01483cde42b65",
      "reviewed_head": "$Q_SHA",
      "result": "PASS",
      "findings": []
    }
  ]
}
```

Resolve every commit and blob from Git, never from the working tree. Require both reviewer identities to be nonempty and distinct from Director2 and from each other; require exact `R..Q`; require the two ordered review kinds and `PASS` results. Canonicalize with sorted keys and compact separators, parse back with duplicate-key rejection, and validate the exact field sets before commit. With a scoped temporary index, commit only this object on the primary branch as `coord(opus): bind Stage A external review authority`. Capture `EXTERNAL_AUTHORITY_COMMIT` and prove:

```bash
EXTERNAL_AUTHORITY_PATH=coordination/verification/authorities/b8c59c86-2426-46cf-8975-7b075d75fc09.json
EXTERNAL_AUTHORITY_COMMIT="$(env -u GIT_INDEX_FILE git log -1 \
  --format=%H -- "$EXTERNAL_AUTHORITY_PATH")"
EXTERNAL_AUTHORITY_BLOB="$(env -u GIT_INDEX_FILE git rev-parse \
  "$EXTERNAL_AUTHORITY_COMMIT:$EXTERNAL_AUTHORITY_PATH")"
test "$(env -u GIT_INDEX_FILE git diff-tree --no-commit-id --name-only -r \
  "$EXTERNAL_AUTHORITY_COMMIT")" = "$EXTERNAL_AUTHORITY_PATH"
printf '%s\n%s\n' "$EXTERNAL_AUTHORITY_COMMIT" "$EXTERNAL_AUTHORITY_BLOB" | \
  grep -Ec '^[0-9a-f]{40}$' | grep -qx '2'
```

This is an out-of-range authority input. Do not add the correction plan, umbrella design, correction route, external authority object, or pre-descriptor review records to descriptor `requirement_paths`: those paths do not exist at reviewed head `Q`. `T` binds the external object exactly once, and Operator2 validates every referenced Git object before GO.

- [ ] **Step 3: Write and validate the descriptor**

Set `Q_SHA` from the reviewed worktree's exact committed HEAD. Build this exact `lane-v-scope/v1` descriptor shape, with no additional field:

```json
{
  "schema_version": "lane-v-scope/v1",
  "task_id": "b8c59c86-2426-46cf-8975-7b075d75fc09",
  "question_id": "stage-a-quality-correction",
  "trigger_kind": "verify-request",
  "verification_mode": "codex-lane-v",
  "verification_harness": "codex:lane-v-verifier",
  "review_profile": "codex-lane-v",
  "reviewed_base": {
    "policy": "exact",
    "commit": "40fd0a5e43c6b28330ced9ddffe01483cde42b65"
  },
  "requirement_paths": [
    "docs/superpowers/plans/2026-07-15-opus-transport-first-recovery.md",
    "coordination/mailbox/sent/2026-07-15T12-19-46Z-coordinator-to-all-coordination.md",
    "coordination/mailbox/sent/2026-07-15T13-03-19Z-coordinator-to-all-coordination.md",
    "coordination/mailbox/sent/2026-07-15T08-50-32Z-operator2-to-all-verification-report.md",
    "scripts/prompts/opus_lane_v_advisory.authority.583cdcb5b5129b629ae4ada21627a4fc5bab1b9c.json"
  ],
  "allowed_path_roots": [
    "scripts/opus_review_bridge.py",
    "scripts/opus_review_receipts.py",
    "tests/unit/test_opus_review_bridge.py",
    "tests/unit/test_opus_review_receipts.py"
  ],
  "verification_commands": [
    "env -u GIT_INDEX_FILE .venv/bin/python -m pytest tests/unit/test_opus_review_bridge.py tests/unit/test_opus_review_receipts.py tests/unit/test_verification_report_gate.py -q",
    "env -u GIT_INDEX_FILE .venv/bin/python scripts/ci_smoke.py"
  ]
}
```

The exact semantic bindings are:

- `task_id`: `b8c59c86-2426-46cf-8975-7b075d75fc09`;
- `question_id`: `stage-a-quality-correction`;
- `trigger_kind`: `verify-request`;
- `verification_mode`: `codex-lane-v`;
- `verification_harness`: `codex:lane-v-verifier`;
- `review_profile`: `codex-lane-v`;
- `reviewed_base`: object `{"policy":"exact","commit":"40fd0a5e43c6b28330ced9ddffe01483cde42b65"}`;
- `requirement_paths`, exactly:
  - `docs/superpowers/plans/2026-07-15-opus-transport-first-recovery.md`;
  - `coordination/mailbox/sent/2026-07-15T12-19-46Z-coordinator-to-all-coordination.md`;
  - `coordination/mailbox/sent/2026-07-15T13-03-19Z-coordinator-to-all-coordination.md`;
  - `coordination/mailbox/sent/2026-07-15T08-50-32Z-operator2-to-all-verification-report.md`;
  - `scripts/prompts/opus_lane_v_advisory.authority.583cdcb5b5129b629ae4ada21627a4fc5bab1b9c.json`;
- `allowed_path_roots`: exactly the four production/test paths in Global Constraints; and
- no `reviewed_head` or other extra field, because `T` binds `$Q_SHA` under the v1 contract.

Copy exactly these two trusted-Python descriptor commands from the original Opus plan, in this order and with no additional serialized command:

```bash
env -u GIT_INDEX_FILE .venv/bin/python -m pytest \
  tests/unit/test_opus_review_bridge.py tests/unit/test_opus_review_receipts.py \
  tests/unit/test_verification_report_gate.py -q
env -u GIT_INDEX_FILE .venv/bin/python scripts/ci_smoke.py
```

Keep `env -u GIT_INDEX_FILE git diff --check` as mandatory Director2 and Operator2 supplemental evidence, not a descriptor command. Validate the actual descriptor and capture its digest before commit:

```bash
DESCRIPTOR_PATH=coordination/verification/scopes/b8c59c86-2426-46cf-8975-7b075d75fc09.json
env -u GIT_INDEX_FILE .venv/bin/python -c \
  'from pathlib import Path; import sys; from scripts.opus_review_receipts import ScopeDescriptor, strict_json_loads; ScopeDescriptor.from_mapping(strict_json_loads(Path(sys.argv[1]).read_bytes()))' \
  "$DESCRIPTOR_PATH"
DESCRIPTOR_DIGEST="$(env -u GIT_INDEX_FILE .venv/bin/python -c \
  'from pathlib import Path; import hashlib, sys; print("sha256:" + hashlib.sha256(Path(sys.argv[1]).read_bytes()).hexdigest())' \
  "$DESCRIPTOR_PATH")"
printf '%s\n' "$DESCRIPTOR_DIGEST" | \
  grep -Eq '^sha256:[0-9a-f]{64}$'
```

Expected: parser success and one lowercase `sha256:` digest. The forthcoming request uses exactly `"$DESCRIPTOR_PATH@$DESCRIPTOR_DIGEST"`.

- [ ] **Step 4: Commit descriptor-only `D`**

From the Stage-A worktree, run:

```bash
env -u GIT_INDEX_FILE git add -- "$DESCRIPTOR_PATH"
test "$(env -u GIT_INDEX_FILE git diff --cached --name-only)" = \
  "$DESCRIPTOR_PATH"
env -u GIT_INDEX_FILE git commit -m \
  "coord(opus): bind Stage A quality scope"
D_SHA="$(env -u GIT_INDEX_FILE git rev-parse 'HEAD^{commit}')"
test "$(env -u GIT_INDEX_FILE git rev-parse "${D_SHA}^")" = "$Q_SHA"
test "$(env -u GIT_INDEX_FILE git diff-tree --no-commit-id --name-only -r \
  "$D_SHA")" = "$DESCRIPTOR_PATH"
```

Expected: `D_SHA` directly parents `Q_SHA` and changes exactly the descriptor path.

- [ ] **Step 5: Generate and commit request-only `T`**

Use the canonical event producer from the Stage-A worktree and capture its actual path:

```bash
EXTERNAL_AUTHORITY_PATH=coordination/verification/authorities/b8c59c86-2426-46cf-8975-7b075d75fc09.json
EXTERNAL_AUTHORITY_COMMIT="$(env -u GIT_INDEX_FILE git log --all \
  --format=%H \
  --grep='^coord(opus): bind Stage A external review authority$')"
test "$(printf '%s\n' "$EXTERNAL_AUTHORITY_COMMIT" | \
  grep -Ec '^[0-9a-f]{40}$')" = 1
EXTERNAL_AUTHORITY_BLOB="$(env -u GIT_INDEX_FILE git rev-parse \
  "$EXTERNAL_AUTHORITY_COMMIT:$EXTERNAL_AUTHORITY_PATH")"
REQUEST_SEND_OUTPUT="$(coordination/bin/send-event \
  director2 operator2 verify-request \
  "verify Opus Stage A quality correction" <<EOF
Event type: verify-request
Task-board: pipeline-opus-transport-first-recovery-stage-a-2026-07-15
Protocol wave: 2
Reviewed head: $Q_SHA
Reviewed base: 40fd0a5e43c6b28330ced9ddffe01483cde42b65
Lane-V-Scope: $DESCRIPTOR_PATH@$DESCRIPTOR_DIGEST
Stage-A-External-Authority: $EXTERNAL_AUTHORITY_COMMIT:$EXTERNAL_AUTHORITY_PATH@$EXTERNAL_AUTHORITY_BLOB
Opus process attempts authorized: 0
EOF
)"
REQUEST_PATH="${REQUEST_SEND_OUTPUT#created }"
REQUEST_PATH="${REQUEST_PATH%% (*}"
case "$REQUEST_PATH" in
  coordination/mailbox/sent/*-director2-to-operator2-verify-request.md) ;;
  *) exit 1 ;;
esac
test -f "$REQUEST_PATH"
env -u GIT_INDEX_FILE git add -f -- "$REQUEST_PATH"
test "$(env -u GIT_INDEX_FILE git diff --cached --name-only)" = \
  "$REQUEST_PATH"
env -u GIT_INDEX_FILE git commit -m \
  "coord(director2): request Stage A quality verification"
T_SHA="$(env -u GIT_INDEX_FILE git rev-parse 'HEAD^{commit}')"
test "$(env -u GIT_INDEX_FILE git rev-parse "${T_SHA}^")" = "$D_SHA"
test "$(env -u GIT_INDEX_FILE git diff-tree --no-commit-id --name-only -r \
  "$T_SHA")" = "$REQUEST_PATH"
test "$(env -u GIT_INDEX_FILE .venv/bin/python -c \
  'from pathlib import Path; import hashlib, sys; print("sha256:" + hashlib.sha256(Path(sys.argv[1]).read_bytes()).hexdigest())' \
  "$DESCRIPTOR_PATH")" = "$DESCRIPTOR_DIGEST"
test "$(env -u GIT_INDEX_FILE git show "$T_SHA:$REQUEST_PATH" | grep -Fxc \
  "Stage-A-External-Authority: $EXTERNAL_AUTHORITY_COMMIT:$EXTERNAL_AUTHORITY_PATH@$EXTERNAL_AUTHORITY_BLOB")" = 1
```

Expected: the body contains exactly one of each binding field and exactly one external-authority reference, `T_SHA` directly parents `D_SHA`, the request commit changes exactly one sent-mailbox path, and the committed descriptor bytes still produce `$DESCRIPTOR_DIGEST`. A same-second collision or uncertain producer result is reconciled before any retry.

- [ ] **Step 6: Resolve authority provider-free and prove zero receipt mutation**

First validate the referenced external object and recover the committed pre-Stage-A receipt manifest from the correction route:

```bash
EXTERNAL_AUTHORITY_PATH=coordination/verification/authorities/b8c59c86-2426-46cf-8975-7b075d75fc09.json
EXTERNAL_AUTHORITY_COMMIT="$(env -u GIT_INDEX_FILE git log --all \
  --format=%H \
  --grep='^coord(opus): bind Stage A external review authority$')"
test "$(printf '%s\n' "$EXTERNAL_AUTHORITY_COMMIT" | \
  grep -Ec '^[0-9a-f]{40}$')" = 1
EXTERNAL_AUTHORITY_BLOB="$(env -u GIT_INDEX_FILE git rev-parse \
  "$EXTERNAL_AUTHORITY_COMMIT:$EXTERNAL_AUTHORITY_PATH")"
test "$(env -u GIT_INDEX_FILE git rev-parse \
  "$EXTERNAL_AUTHORITY_COMMIT:$EXTERNAL_AUTHORITY_PATH")" = \
  "$EXTERNAL_AUTHORITY_BLOB"
test "$(env -u GIT_INDEX_FILE git show "$T_SHA:$REQUEST_PATH" | grep -Fxc \
  "Stage-A-External-Authority: $EXTERNAL_AUTHORITY_COMMIT:$EXTERNAL_AUTHORITY_PATH@$EXTERNAL_AUTHORITY_BLOB")" = 1
EXTERNAL_AUTHORITY_RAW="$(env -u GIT_INDEX_FILE git show \
  "$EXTERNAL_AUTHORITY_COMMIT:$EXTERNAL_AUTHORITY_PATH")"
ROUTE_COMMIT="$(printf '%s' "$EXTERNAL_AUTHORITY_RAW" | \
  env -u GIT_INDEX_FILE PYTHONPATH=scripts .venv/bin/python -c \
  'import sys; from opus_review_receipts import strict_json_loads; value=strict_json_loads(sys.stdin.buffer.read()); print(value["correction_route"]["commit"])')"
ROUTE_EVENT="$(printf '%s' "$EXTERNAL_AUTHORITY_RAW" | \
  env -u GIT_INDEX_FILE PYTHONPATH=scripts .venv/bin/python -c \
  'import sys; from opus_review_receipts import strict_json_loads; value=strict_json_loads(sys.stdin.buffer.read()); print(value["correction_route"]["path"])')"
ROUTE_BLOB="$(printf '%s' "$EXTERNAL_AUTHORITY_RAW" | \
  env -u GIT_INDEX_FILE PYTHONPATH=scripts .venv/bin/python -c \
  'import sys; from opus_review_receipts import strict_json_loads; value=strict_json_loads(sys.stdin.buffer.read()); print(value["correction_route"]["blob_id"])')"
printf '%s\n%s\n' "$ROUTE_COMMIT" "$ROUTE_BLOB" | \
  grep -Ec '^[0-9a-f]{40}$' | grep -qx '2'
printf '%s\n' "$ROUTE_EVENT" | grep -Eq \
  '^coordination/mailbox/sent/.*-coordinator-to-all-coordination\.md$'
test "$(env -u GIT_INDEX_FILE git rev-parse \
  "$ROUTE_COMMIT:$ROUTE_EVENT")" = "$ROUTE_BLOB"
env -u GIT_INDEX_FILE git merge-base --is-ancestor \
  426744766711d4d6057a4698f5bb19d454ad621d "$ROUTE_COMMIT"
env -u GIT_INDEX_FILE git merge-base --is-ancestor \
  "$ROUTE_COMMIT" "$EXTERNAL_AUTHORITY_COMMIT"
test "$(env -u GIT_INDEX_FILE git show "$ROUTE_COMMIT:$ROUTE_EVENT" | \
  grep -Ec '^Receipt-store manifest before Stage A: sha256:[0-9a-f]{64}$')" = 1
RECEIPT_MANIFEST_BEFORE_SHA="$(env -u GIT_INDEX_FILE git show \
  "$ROUTE_COMMIT:$ROUTE_EVENT" | sed -n \
  's/^Receipt-store manifest before Stage A: //p')"
printf '%s\n' "$RECEIPT_MANIFEST_BEFORE_SHA" | \
  grep -Eq '^sha256:[0-9a-f]{64}$'
```

Then run this exact read-only resolver check from the Stage-A worktree. It calls `resolve_authoritative_scope()` directly. It must never call `review()`, `resolve_provider_authoritative_scope()`, a receipt-store lock method, or any provider-capable CLI:

```bash
RECEIPT_COMMON_DIR="$(env -u GIT_INDEX_FILE git rev-parse \
  --path-format=absolute --git-common-dir)"
RECEIPT_STORE_ROOT="$(dirname "$RECEIPT_COMMON_DIR")/.codex/runtime/opus-review-receipts/v1"
Q_SHA="$Q_SHA" T_SHA="$T_SHA" REQUEST_PATH="$REQUEST_PATH" \
DESCRIPTOR_DIGEST="$DESCRIPTOR_DIGEST" \
RECEIPT_STORE_ROOT="$RECEIPT_STORE_ROOT" \
env -u GIT_INDEX_FILE .venv/bin/python - <<'PY'
import json
import os
from pathlib import Path
import sys

sys.path.insert(0, str(Path.cwd() / "scripts"))

from opus_review_bridge import ReviewRequest, resolve_authoritative_scope
from opus_review_receipts import (
    canonical_trigger_identity,
    compute_attempt_key,
)

base = "40fd0a5e43c6b28330ced9ddffe01483cde42b65"
head = os.environ["Q_SHA"]
trigger = os.environ["T_SHA"]
request_path = os.environ["REQUEST_PATH"]
resolved = resolve_authoritative_scope(
    ReviewRequest(
        repo_root=Path.cwd(),
        reviewed_head=head,
        reviewed_base=base,
        review_profile="codex-lane-v",
        authorization_source="",
        trigger_kind="verify-request",
        trigger_commit=trigger,
        trigger_path=request_path,
    )
)
expected_requirements = (
    "coordination/mailbox/sent/2026-07-15T08-50-32Z-operator2-to-all-verification-report.md",
    "coordination/mailbox/sent/2026-07-15T12-19-46Z-coordinator-to-all-coordination.md",
    "coordination/mailbox/sent/2026-07-15T13-03-19Z-coordinator-to-all-coordination.md",
    "docs/superpowers/plans/2026-07-15-opus-transport-first-recovery.md",
    "scripts/prompts/opus_lane_v_advisory.authority.583cdcb5b5129b629ae4ada21627a4fc5bab1b9c.json",
)
expected_changed = {
    "scripts/opus_review_bridge.py",
    "scripts/opus_review_receipts.py",
    "tests/unit/test_opus_review_bridge.py",
    "tests/unit/test_opus_review_receipts.py",
}
assert resolved.scope.effective_base == base
assert resolved.scope.reviewed_head == head
assert resolved.scope.descriptor_digest == os.environ["DESCRIPTOR_DIGEST"]
assert resolved.scope.trigger_commit == trigger
assert resolved.scope.trigger_path == request_path
assert resolved.scope.trigger_identity == canonical_trigger_identity(
    "verify-request", trigger, request_path
)
assert tuple(blob.path for blob in resolved.review_requirements) == expected_requirements
assert resolved.scope.requirements == tuple(
    {
        "path": blob.path,
        "blob_id": blob.blob_id,
        "digest": blob.digest,
    }
    for blob in resolved.review_requirements
)
assert {item.path for item in resolved.scope.changed_paths} == expected_changed
assert len(resolved.scope.changed_paths) == len(expected_changed)
assert tuple(blob.purpose for blob in resolved.authority_requirements) == (
    "scope_descriptor",
    "verify_request",
)
attempt_key = compute_attempt_key(resolved.scope)
key_digest = attempt_key.removeprefix("opr1:")
state_root = Path(os.environ["RECEIPT_STORE_ROOT"])
assert not (state_root / f"{key_digest}.json").exists()
assert not (state_root / f"{key_digest}.lock").exists()
print(
    json.dumps(
        {
            "attempt_key": attempt_key,
            "changed_paths": sorted(expected_changed),
            "descriptor_digest": resolved.scope.descriptor_digest,
            "effective_base": resolved.scope.effective_base,
            "reviewed_head": resolved.scope.reviewed_head,
            "trigger_identity": resolved.scope.trigger_identity,
        },
        sort_keys=True,
        separators=(",", ":"),
    )
)
PY
```

Finally recompute the receipt-store manifest with the exact Task-1 algorithm and compare it with the committed baseline:

```bash
RECEIPT_MANIFEST_AFTER_SHA="$(
  RECEIPT_STORE_ROOT="$RECEIPT_STORE_ROOT" \
  env -u GIT_INDEX_FILE .venv/bin/python - <<'PY'
import hashlib
import json
import os
from pathlib import Path
import stat

root = Path(os.environ["RECEIPT_STORE_ROOT"])
rows = []
if root.exists():
    for path in sorted(root.iterdir(), key=lambda item: os.fsencode(item.name)):
        observed = path.lstat()
        if not stat.S_ISREG(observed.st_mode):
            raise SystemExit(f"non-regular receipt-store entry: {path.name}")
        rows.append(
            {
                "name": path.name,
                "mode": stat.S_IMODE(observed.st_mode),
                "uid": observed.st_uid,
                "nlink": observed.st_nlink,
                "size": observed.st_size,
                "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
            }
        )
raw = json.dumps(
    rows, sort_keys=True, separators=(",", ":"), ensure_ascii=True
).encode("ascii")
print("sha256:" + hashlib.sha256(raw).hexdigest())
PY
)"
test "$RECEIPT_MANIFEST_AFTER_SHA" = "$RECEIPT_MANIFEST_BEFORE_SHA"
```

Any prospective receipt/lock, manifest drift, resolver mismatch, or external-object mismatch blocks Operator2; do not delete or repair runtime state and do not retry through another resolver.

### Task 7: Operator2 verifies Stage A and coordinator resumes Stages B-D

**Files:**

- Create: one canonical Operator2 verification report
- Modify or create only after that report: Stage B-D capacity packets and one consolidated coordinator route
- Create only after final Stage-D GO, separately authorized local integration, and merged-tree verification: `docs/HANDOFF-director-2026-07-16-opus-b-d-recovery.md`

**Interfaces:**

- Consumes: lawful `T`, descriptor `D`, `R..Q`, and zero-provider evidence.
- Produces: GO/NITS/FAIL for Stage A; on GO only, a smallest-boundary Stage B route followed later by one fresh Stage C canary and Stage D integration gates.

- [ ] **Step 1: Run independent Lane V**

Operator2 reruns Task 6 Step 6 using `resolve_authoritative_scope()` directly—never `review()` or `resolve_provider_authoritative_scope()`—and resolves `T` without reconstructing missing fields. It verifies topology, descriptor schema/digest, exact requirement blobs and changed paths, trigger identity, all fourteen abuse cases, provider-attempt count zero, prospective receipt/lock absence, receipt-store manifest equality, and the complete trusted command set. It also parses the single `Stage-A-External-Authority` field, proves the referenced commit/path/blob identity, validates the external object's exact field sets, and independently resolves the bound correction-plan, umbrella-design, and correction-route blobs plus the two distinct pre-descriptor reviewer identities/results. These out-of-range inputs remain external and must not be inserted into descriptor `requirement_paths`. It returns one canonical GO, NITS, or FAIL. NITS/FAIL stops; coordinator does not fix.

- [ ] **Step 2: Reopen only the original plan's Task 4 Stage B**

On GO, the coordinator refreshes mail/capacity and routes one smallest root-boundary repair exactly as `2026-07-15-opus-transport-first-recovery.md` Task 4 specifies. Stage B implementation tests remain provider-free and require their own independent review and Operator2 trigger.

- [ ] **Step 3: Gate one Stage C canary**

Only after Stage B GO may the user-principal give one later explicit consent naming one executor for one new idempotency key and one existing-session provider attempt. The Stage-C side-effect executor token binds the exact repository identity, reviewed base/head, descriptor/request/receipt identities, review profile, provider transport, one-attempt budget, preflight, stop conditions, and read-only postcheck. A coordinator route records that already-granted authority but cannot create it. No retry, browser/API fallback, credential entry, executor substitution, or reuse of the terminal prior receipt is allowed. Unavailable or uncertain delivery stops terminally.

- [ ] **Step 4: Gate Stage D integration and publication separately**

Operator2 verifies the final repair and canary evidence and commits the final Stage-D GO/NITS/FAIL report. After GO only, the user-principal separately names one local integrator and the exact reviewed head/base. That integrator may merge locally and rerun the complete focused suite, smoke, diff check, receipt/CAS checks, provider-attempt accounting, and exact merged-tree ancestry. The coordinator only reconciles the result and cannot perform or infer that integration authority. Push requires another explicit user authorization after those gates; this plan does not grant it.

After a successful authorized local integration and merged-tree verification, Director2 creates and commits only `docs/HANDOFF-director-2026-07-16-opus-b-d-recovery.md`. It binds the final Stage-B repair range, Stage-C canary consent/token/idempotency/receipt identities, exactly one provider attempt, no retry/fallback, effective Opus model result, final Stage-D Operator report path/commit and GO, exact integrated local-main SHA/ancestry, merged-tree command results, no post-GO production edit, and push status `not-authorized`. It names the terminal Opus join packet and expected `done_evidence` path. The coordinator may mark that join terminal only after the committed handoff and exact integrated SHA validate; its `done_evidence` must point to this handoff and the final GO report. A canary or final-verification unavailable/NITS/FAIL outcome produces a durable blocker and next owner, not this recovery handoff, and keeps the target-aware bridge blocked.

## Completion Verification

Before reporting this plan executed, capture fresh output for:

```bash
STAGE_A_ROOT=.worktrees/opus-transport-first-stage-a-director2
T_SHA="$(env -u GIT_INDEX_FILE git -C "$STAGE_A_ROOT" rev-parse 'HEAD^{commit}')"
D_SHA="$(env -u GIT_INDEX_FILE git -C "$STAGE_A_ROOT" rev-parse "${T_SHA}^")"
Q_SHA="$(env -u GIT_INDEX_FILE git -C "$STAGE_A_ROOT" rev-parse "${D_SHA}^")"
test "$(env -u GIT_INDEX_FILE git -C "$STAGE_A_ROOT" rev-parse "${Q_SHA}^")" = \
  16c4f83aef4130d977a91d623a9254c4fd46980a
env -u GIT_INDEX_FILE git -C "$STAGE_A_ROOT" log --oneline -6
env -u GIT_INDEX_FILE git -C "$STAGE_A_ROOT" diff --name-only \
  40fd0a5e43c6b28330ced9ddffe01483cde42b65.."$Q_SHA"
(
  cd "$STAGE_A_ROOT"
  env -u GIT_INDEX_FILE .venv/bin/python -m pytest \
    tests/unit/test_opus_review_bridge.py \
    tests/unit/test_opus_review_receipts.py \
    tests/unit/test_verification_report_gate.py -q
  env -u GIT_INDEX_FILE .venv/bin/python scripts/ci_smoke.py
  env -u GIT_INDEX_FILE git diff --check \
    40fd0a5e43c6b28330ced9ddffe01483cde42b65.."$Q_SHA"
)
env -u GIT_INDEX_FILE .venv/bin/python scripts/protocol_capacity_board.py --wave 2
test "$(shasum -a 256 \
  .codex/runtime/opus-review-receipts/v1/de2f5b672b8e1ea03b7575d7a636e0d56bef9817f0d8b5b74fb0632678b68f85.json \
  | awk '{print $1}')" = \
  a4ea49a79fd6a5e95fe89626d3a3305fcdb31b4a6a9709514ce8a7c8b2263a25
```

Stage-A completion additionally requires the canonical Operator2 Stage-A GO path and commit, zero Stage-A provider attempts, the exact terminal prior-receipt digest check above, and a durable next owner. Green commands without GO do not satisfy that gate. The full Opus recovery plan is complete only when the fixed Stage-B-D recovery handoff, final Operator2 GO, exact locally integrated main SHA, merged-tree evidence, and terminal join `done_evidence` all agree; publication may remain unauthorized.

Before making that claim, rerun the complete Task 6 Step 6 external-object, provider-free resolver, prospective receipt/lock absence, and before/after receipt-manifest blocks against the final `Q`, `D`, `T`, and request path. Capture the printed resolved summary, both equal manifest digests, and the external commit/path/blob proof. The older terminal-receipt hash alone is insufficient because it does not detect a newly created Stage-A receipt.

## Stop Conditions

- `R`, `M0`, or `F` changes, or `Q` does not directly parent `F`.
- Any fifth implementation/test path appears in `F..Q` or `R..Q`.
- A real provider process, receipt mutation, retry, fallback, or credential action occurs during Stage A.
- The prospective Stage-A attempt receipt or lock exists, or the receipt-store manifest differs from the baseline committed in the correction route.
- The semantic rule table rejects a tuple still emitted by production or accepts a contradictory tuple from the invalid matrix.
- Cleanup can still be labeled startup, raw diagnostic text escapes, or a completed result is discarded, retried, relabeled, or allowed to bypass the existing parser and contract checks.
- Independent spec or quality review returns a blocking finding.
- Descriptor, external authority, or request topology, digest, full SHAs/blobs, event count, or command allowlist differs from the committed contract.
- Operator2 returns NITS/FAIL or no lawful trigger exists.
- Any integration, activation, or push is proposed without its separate named authorization.

## Exact Next Trigger

After this plan is committed and the coordinator's three-packet correction route validates, Director2 appends exactly one provider-free `Q` to immutable `F`. Descriptor `D`, request `T`, Operator2 verification, any Stage-C provider attempt, local integration, and publication remain gated in that order by their separate authorities. The target-aware bridge cannot start until `docs/HANDOFF-director-2026-07-16-opus-b-d-recovery.md`, its final GO, integrated head, merged-tree evidence, and terminal join `done_evidence` validate.
