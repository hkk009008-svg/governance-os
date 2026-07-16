# Opus Provider-Free Lane V Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a committed provider-free Codex Lane V mode that publishes through task state without making an Opus receipt or weakening ordinary receipt-backed Codex reports.

**Architecture:** Split descriptor-supported verifier tuples from receipt-capable review-scope tuples. Add exact `codex-provider-free-lane-v` report validation and route only that mode plus Claude mode through the existing task-publication transaction; ordinary `codex-lane-v` remains receipt-backed.

**Tech Stack:** Python 3.14, pytest, Git-backed authority fixtures, private receipt/task state stores.

## Global Constraints

- Work only in `/Users/hyungkoookkim/Pipeline/.worktrees/opus-provider-free-lane-v` on branch `codex/opus-provider-free-lane-v`.
- Prefix every ordinary Git and pytest command with `env -u GIT_INDEX_FILE`.
- Do not invoke Opus or any other provider; provider attempts and receipt mutations remain zero.
- Do not write mailbox events, consume cursors, mutate routes/capacity, integrate into `main`, push, publish externally, or touch the separate shared-tree WIP.
- Preserve ordinary `codex-lane-v` and `claude-lane-v` behavior byte-for-byte unless a new regression test proves a required shared hardening.
- Commit each task separately with strict pathspec staging.

---

### Task 1: Separate descriptor authority from receipt-capable review scope

**Files:**
- Modify: `scripts/opus_review_receipts.py:27-30,102-107,429-443,679-697,779-787`
- Modify: `tests/unit/test_opus_review_receipts.py:245-282`
- Test: `tests/unit/test_opus_review_receipts.py`

**Interfaces:**
- Consumes: existing `ScopeDescriptor.from_mapping()`, `ReviewScope.to_mapping()`, and exact verifier tuple validation.
- Produces: `CODEX_PROVIDER_FREE_MODE`, an exact descriptor-only verifier tuple, and a receipt/review-scope allowlist that excludes provider-free mode.

- [ ] **Step 1: Write failing descriptor and no-receipt tests**

Add tests with these exact behaviors:

```python
def test_scope_descriptor_accepts_provider_free_codex_pair() -> None:
    value = _descriptor_mapping()
    value.update(
        verification_mode="codex-provider-free-lane-v",
        verification_harness="codex:lane-v-verifier",
        review_profile="codex-provider-free-lane-v",
    )
    descriptor = receipts.ScopeDescriptor.from_mapping(value)
    assert descriptor.verification_mode == receipts.CODEX_PROVIDER_FREE_MODE


@pytest.mark.parametrize(
    ("harness", "profile"),
    [
        ("claude:lane-v-verifier", "codex-provider-free-lane-v"),
        ("codex:lane-v-verifier", "codex-lane-v"),
        ("codex:lane-v-verifier", "claude-lane-v"),
    ],
)
def test_scope_descriptor_rejects_mixed_provider_free_pair(harness, profile):
    value = _descriptor_mapping()
    value.update(
        verification_mode="codex-provider-free-lane-v",
        verification_harness=harness,
        review_profile=profile,
    )
    with pytest.raises(receipts.ReceiptContractError):
        receipts.ScopeDescriptor.from_mapping(value)


def test_review_scope_rejects_provider_free_mode_before_receipt_state(tmp_path):
    scope = dataclasses.replace(
        _review_scope(),
        verification_mode="codex-provider-free-lane-v",
        review_profile="codex-provider-free-lane-v",
    )
    state_root = tmp_path / "state"
    with pytest.raises(receipts.ReceiptContractError, match="invalid_review_scope"):
        receipts.compute_attempt_key(scope)
    assert not state_root.exists()
```

- [ ] **Step 2: Run the new tests and verify RED**

Run:

```sh
env -u GIT_INDEX_FILE ../../.venv/bin/python -m pytest \
  tests/unit/test_opus_review_receipts.py \
  -q -k 'provider_free or mixed_provider_free'
```

Expected: descriptor acceptance fails because the tuple is unsupported; assertions must fail for the new behavior rather than from fixture errors.

- [ ] **Step 3: Implement the minimal verifier-domain split**

Add:

```python
CODEX_PROVIDER_FREE_MODE = "codex-provider-free-lane-v"

_DESCRIPTOR_SUPPORTED_VERIFIERS = frozenset(
    {
        (CODEX_MODE, CODEX_HARNESS, CODEX_MODE),
        (CODEX_PROVIDER_FREE_MODE, CODEX_HARNESS, CODEX_PROVIDER_FREE_MODE),
        (CLAUDE_MODE, CLAUDE_HARNESS, CLAUDE_MODE),
    }
)
_REVIEW_SCOPE_SUPPORTED_VERIFIERS = frozenset(
    {
        (CODEX_MODE, CODEX_HARNESS, CODEX_MODE),
        (CLAUDE_MODE, CLAUDE_HARNESS, CLAUDE_MODE),
    }
)
```

Change `_validated_verifier()` to require a keyword-only `supported` tuple set. Pass `_DESCRIPTOR_SUPPORTED_VERIFIERS` from `ScopeDescriptor.from_mapping()` and `_REVIEW_SCOPE_SUPPORTED_VERIFIERS` from `ReviewScope.to_mapping()`. Do not add provider-free mode to receipt-capable review scopes.

- [ ] **Step 4: Run focused and complete receipt tests**

Run:

```sh
env -u GIT_INDEX_FILE ../../.venv/bin/python -m pytest \
  tests/unit/test_opus_review_receipts.py -q
```

Expected: all receipt tests pass, including the new provider-free rejection before receipt state.

- [ ] **Step 5: Commit Task 1**

```sh
env -u GIT_INDEX_FILE git add -- \
  scripts/opus_review_receipts.py \
  tests/unit/test_opus_review_receipts.py
env -u GIT_INDEX_FILE git diff --cached --check
env -u GIT_INDEX_FILE git commit -m "fix(opus): separate provider-free descriptor authority"
```

---

### Task 2: Add provider-free report validation and task-backed publication

**Files:**
- Modify: `scripts/verification_report_gate.py:309-373,813-835,1517-1530,1585-1630,2369-2450,2848-2938`
- Modify: `tests/unit/test_verification_report_gate.py:35-135,360-525,930-1040,1470-1635`
- Test: `tests/unit/test_verification_report_gate.py`

**Interfaces:**
- Consumes: `receipts.CODEX_PROVIDER_FREE_MODE`, committed descriptor authority, `TaskPublicationStore`, `ReceiptStore`.
- Produces: exact provider-free report parsing plus live validation, publication, resume, and status that never call receipt state.

- [ ] **Step 1: Write failing report-shape and mismatch tests**

Add a helper that starts from `_codex_fields()`, sets `Verification mode` and `Review profile` to `receipts.CODEX_PROVIDER_FREE_MODE`, preserves `Verification harness: codex:lane-v-verifier`, and sets every field in `gate.ATTESTATION_FIELDS[9:]` to `not-applicable`.

Add tests that:

- parse this exact provider-free report;
- reject each provider field when changed away from `not-applicable`;
- preserve ordinary Codex rejection of `not-applicable` receipt fields;
- reject provider-free mode with Claude harness or ordinary Codex profile;
- reject descriptor/report mode mismatches for both trigger kinds;
- preserve verify-request recipient enforcement;
- reject an unknown mode before any task-store factory call.

- [ ] **Step 2: Write failing live/publication end-to-end test**

Create a provider-free authority fixture by extending `_authority_fixture()` to select the Codex harness for both Codex modes. The end-to-end test must:

```python
def bomb_receipt_store(_root):
    raise AssertionError("provider-free mode touched receipt state")

validated = gate.validate_live_report(
    fixture.root,
    fixture.report,
    receipt_store_factory=bomb_receipt_store,
    task_store_factory=lambda _root: fixture.task_store,
)
published = gate.publish_candidate(
    repo_root=fixture.root,
    candidate_path=fixture.candidate,
    final_relative=fixture.report.relative_path,
    receipt_store_factory=bomb_receipt_store,
    task_store_factory=lambda _root: fixture.task_store,
)
status = gate.publication_status(
    repo_root=fixture.root,
    task_id=TASK_ID,
    task_store_factory=lambda _root: fixture.task_store,
)
assert validated == fixture.authority
assert published.read_bytes() == fixture.raw
assert status["state"] == "published"
assert not fixture.receipt_state_root.exists()
```

Also exercise one injected publication interruption and resume by task ID, and preserve task-authority collision failure.

- [ ] **Step 3: Run the new tests and verify RED**

Run:

```sh
env -u GIT_INDEX_FILE ../../.venv/bin/python -m pytest \
  tests/unit/test_verification_report_gate.py \
  -q -k 'provider_free'
```

Expected: report parsing rejects the unsupported mode before task publication.

- [ ] **Step 4: Implement exact report-mode classification**

Add an exact provider-free validation branch:

```python
def _validate_provider_free_codex_fields(fields: Mapping[str, str]) -> None:
    if fields["Verification harness"] != receipts.CODEX_HARNESS:
        _fail("invalid_attestation_value", "provider-free Codex harness does not match")
    if fields["Review profile"] != receipts.CODEX_PROVIDER_FREE_MODE:
        _fail("invalid_attestation_value", "provider-free Codex profile does not match")
    for label in ATTESTATION_FIELDS[9:]:
        if fields[label] != "not-applicable":
            _fail("invalid_attestation_value", f"{label} must be not-applicable")
```

`_OPUS_SPECIFIC_FIELDS` starts at `Review profile` and therefore must not be
used for this loop: the dedicated provider-free review profile remains
`codex-provider-free-lane-v`; only provider/receipt fields beginning with
`Authorization identity` are `not-applicable`.

Classify only the three supported modes. Compare the committed descriptor profile to the report profile in `validate_structural_authority()`. Introduce explicit helpers or exact-set membership so:

- only `codex-lane-v` uses `ReceiptStore`;
- only `{claude-lane-v, codex-provider-free-lane-v}` uses `TaskPublicationStore`;
- unknown modes never reach either backend.

Use the same exact classification in live validation, publish, resume, and status paths. Preserve all existing task transaction and receipt reconciliation logic.

- [ ] **Step 5: Run focused and complete report-gate tests**

Run:

```sh
env -u GIT_INDEX_FILE ../../.venv/bin/python -m pytest \
  tests/unit/test_verification_report_gate.py -q
```

Expected: all report-gate tests pass, including provider-free publication/resume/status and unchanged ordinary Codex receipt enforcement.

- [ ] **Step 6: Run cross-module schema verification**

Run:

```sh
env -u GIT_INDEX_FILE ../../.venv/bin/python -m pytest \
  tests/unit/test_opus_review_receipts.py \
  tests/unit/test_verification_report_gate.py \
  tests/unit/test_go_schema.py -q
env -u GIT_INDEX_FILE ../../.venv/bin/python scripts/check_go_schema.py
```

Expected: all tests pass and the repository report schema reports zero violations.

- [ ] **Step 7: Commit Task 2**

```sh
env -u GIT_INDEX_FILE git add -- \
  scripts/verification_report_gate.py \
  tests/unit/test_verification_report_gate.py \
  tests/unit/test_go_schema.py
env -u GIT_INDEX_FILE git diff --cached --check
env -u GIT_INDEX_FILE git commit -m "fix(opus): publish provider-free Codex reports"
```

Stage `tests/unit/test_go_schema.py` only if it changed.

---

### Task 3: Synchronize architecture and verify the complete bridge repair

**Files:**
- Modify: `ARCHITECTURE.md:70-100`
- Test: `scripts/ci_smoke.py`

**Interfaces:**
- Consumes: verified Task 1 and Task 2 behavior.
- Produces: current architecture truth and the final isolated implementation range for coordinator reconciliation.

- [ ] **Step 1: Update architecture truth**

Document that `codex-provider-free-lane-v` is a committed descriptor mode for provider-prohibited Codex verification, that its Opus attestation fields are `not-applicable`, that it uses task-publication state, and that it cannot be represented as a receipt-capable review scope. Preserve the existing receipt-backed `codex-lane-v` invariant.

- [ ] **Step 2: Run final verification**

Run:

```sh
env -u GIT_INDEX_FILE ../../.venv/bin/python -m pytest \
  tests/unit/test_opus_review_receipts.py \
  tests/unit/test_verification_report_gate.py \
  tests/unit/test_go_schema.py -q
env -u GIT_INDEX_FILE ../../.venv/bin/python scripts/ci_smoke.py
env -u GIT_INDEX_FILE git diff --check acc29ba..HEAD
env -u GIT_INDEX_FILE git status --short
```

Expected: all tests and smoke pass; diff check is empty; worktree is clean after the documentation commit.

- [ ] **Step 3: Commit Task 3**

```sh
env -u GIT_INDEX_FILE git add -- ARCHITECTURE.md
env -u GIT_INDEX_FILE git diff --cached --check
env -u GIT_INDEX_FILE git commit -m "docs(opus): document provider-free report publication"
```

- [ ] **Step 4: Independent final review**

Request one read-only reviewer for exact `acc29ba..HEAD`. The reviewer must verify all abuse cases from the design, confirm ordinary Codex still requires receipts, confirm provider-free ReviewScope cannot create a receipt or lock, inspect the hermetic end-to-end publication evidence, and return `GO`, `NITS`, or `FAIL`. No provider, mailbox, receipt, push, merge, or publication side effect is authorized.

- [ ] **Step 5: Return coordinator evidence**

Report the isolated branch, exact base/head range, commits, changed paths, fresh test outputs, smoke output, independent verdict, and remaining coordinator action: add the standalone manifest line and issue a fresh provider-free descriptor plus canonical verify-request without changing `R..Q2`.
