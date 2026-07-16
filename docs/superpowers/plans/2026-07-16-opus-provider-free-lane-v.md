# Opus Provider-Free Lane V Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add a committed provider-free Codex Lane V mode that publishes through task state without making an Opus receipt or weakening ordinary receipt-backed Codex reports.

**Architecture:** Split descriptor-supported verifier tuples from receipt-capable review-scope tuples. Add exact `codex-provider-free-lane-v` report validation and route only that mode plus Claude mode through the existing task-publication transaction; ordinary `codex-lane-v` remains receipt-backed.

**Tech Stack:** Python 3.11/3.13/3.14, pytest, `tarfile.data_filter`, Git-backed authority fixtures, private receipt/task state stores.

## Global Constraints

- Work only in `/Users/hyungkoookkim/Pipeline/.worktrees/opus-provider-free-lane-v` on branch `codex/opus-provider-free-lane-v`.
- Prefix every ordinary Git and pytest command with `env -u GIT_INDEX_FILE`.
- Do not invoke Opus or any other provider; provider attempts and receipt mutations remain zero.
- Do not write mailbox events, consume cursors, mutate routes/capacity, integrate into `main`, force-push, merge, publish externally, or touch the separate shared-tree WIP. The post-integration Task 4 permits exactly one normal push to `codex/opus-provider-free-lane-v` after both append-only commits are verified.
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
  tests/unit/test_check_go_schema.py -q
env -u GIT_INDEX_FILE ../../.venv/bin/python scripts/check_go_schema.py
```

Expected: all tests pass and the repository report schema reports zero violations.

- [ ] **Step 7: Commit Task 2**

```sh
env -u GIT_INDEX_FILE git add -- \
  scripts/verification_report_gate.py \
  tests/unit/test_verification_report_gate.py \
  tests/unit/test_check_go_schema.py
env -u GIT_INDEX_FILE git diff --cached --check
env -u GIT_INDEX_FILE git commit -m "fix(opus): publish provider-free Codex reports"
```

Stage `tests/unit/test_check_go_schema.py` only if it changed.

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
  tests/unit/test_check_go_schema.py -q
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

---

### Task 4: Repair Python 3.13 archive extraction after hosted E2E

**Files:**
- Modify: `scripts/opus_review_bridge.py:1845-1860`
- Modify: `tests/unit/test_opus_review_bridge.py`
- Test: `tests/unit/test_opus_review_bridge.py`

**Interfaces:**
- Consumes: `_extract_review_archive(archive: bytes, destination: Path) -> None`, exact `git archive` bytes, and the existing all-members-first safety checks.
- Produces: extraction through the exact `tarfile.data_filter` callable, a stable fail-closed `invalid_scope` error when that callable is unavailable, and multi-version regression evidence.

- [ ] **Step 1: Add an archive fixture helper and focused failing tests**

Add `io` and `tarfile` imports, then add this helper and the filter tests near
`test_snapshot_fetches_later_trigger_and_reverifies_bound_blobs`:

```python
def _review_archive(member: tarfile.TarInfo, payload: bytes = b"") -> bytes:
    raw = io.BytesIO()
    with tarfile.open(fileobj=raw, mode="w") as bundle:
        if member.isfile():
            member.size = len(payload)
            bundle.addfile(member, io.BytesIO(payload))
        else:
            bundle.addfile(member)
    return raw.getvalue()


def test_extract_review_archive_passes_exact_data_filter(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    member = tarfile.TarInfo("bin/reviewer")
    member.mode = 0o755
    archive = _review_archive(member, b"reviewer\n")
    destination = tmp_path / "snapshot"
    observed_filters: list[object] = []
    original_extractall = bridge.tarfile.TarFile.extractall

    def capture_extractall(
        bundle,
        path=".",
        members=None,
        *,
        numeric_owner=False,
        filter=None,
    ):
        observed_filters.append(filter)
        return original_extractall(
            bundle,
            path,
            members,
            numeric_owner=numeric_owner,
            filter=filter,
        )

    monkeypatch.setattr(bridge.tarfile.TarFile, "extractall", capture_extractall)
    bridge._extract_review_archive(archive, destination)

    extracted = destination / "bin" / "reviewer"
    assert observed_filters == [bridge.tarfile.data_filter]
    assert extracted.read_bytes() == b"reviewer\n"
    assert extracted.stat().st_mode & stat.S_IXUSR


@pytest.mark.parametrize("condition", ("missing", "not-callable"))
def test_extract_review_archive_fails_closed_without_callable_data_filter(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, condition: str
) -> None:
    member = tarfile.TarInfo("safe.txt")
    archive = _review_archive(member, b"safe\n")
    destination = tmp_path / "snapshot"
    if condition == "missing":
        monkeypatch.delattr(bridge.tarfile, "data_filter")
    else:
        monkeypatch.setattr(bridge.tarfile, "data_filter", None)

    with pytest.raises(bridge.ReviewContractError) as excinfo:
        bridge._extract_review_archive(archive, destination)

    assert excinfo.value.reason == "invalid_scope"
    assert excinfo.value.detail == "safe tar data filter is unavailable"
    assert not destination.exists()
```

- [ ] **Step 2: Pin the existing unsafe-member boundary**

Add this parametrized characterization test. It must remain green before and
after the production repair because the existing manual validation is retained:

```python
@pytest.mark.parametrize(
    ("name", "member_type", "linkname"),
    [
        ("/absolute", tarfile.REGTYPE, ""),
        ("../escape", tarfile.REGTYPE, ""),
        (".git/config", tarfile.REGTYPE, ""),
        ("symlink", tarfile.SYMTYPE, "target"),
        ("hardlink", tarfile.LNKTYPE, "target"),
        ("fifo", tarfile.FIFOTYPE, ""),
    ],
)
def test_extract_review_archive_rejects_unsafe_members(
    tmp_path: Path, name: str, member_type: bytes, linkname: str
) -> None:
    member = tarfile.TarInfo(name)
    member.type = member_type
    member.linkname = linkname
    payload = b"unsafe\n" if member.isfile() else b""
    destination = tmp_path / "snapshot"

    with pytest.raises(bridge.ReviewContractError) as excinfo:
        bridge._extract_review_archive(_review_archive(member, payload), destination)

    assert excinfo.value.reason == "invalid_scope"
    assert not destination.exists()
```

Add a defense-in-depth case for the realpath containment supplied by
`tarfile.data_filter`:

```python
def test_extract_review_archive_blocks_preexisting_destination_symlink(
    tmp_path: Path,
) -> None:
    outside = tmp_path / "outside"
    outside.mkdir()
    destination = tmp_path / "snapshot"
    destination.mkdir()
    (destination / "pivot").symlink_to(outside, target_is_directory=True)
    member = tarfile.TarInfo("pivot/escaped.txt")

    with pytest.raises(tarfile.OutsideDestinationError):
        bridge._extract_review_archive(
            _review_archive(member, b"blocked\n"), destination
        )

    assert not (outside / "escaped.txt").exists()
```

- [ ] **Step 3: Run the new behavior tests and verify RED**

Run:

```sh
env -u GIT_INDEX_FILE ../../.venv/bin/python -m pytest \
  tests/unit/test_opus_review_bridge.py::test_extract_review_archive_passes_exact_data_filter \
  tests/unit/test_opus_review_bridge.py::test_extract_review_archive_fails_closed_without_callable_data_filter \
  tests/unit/test_opus_review_bridge.py::test_extract_review_archive_blocks_preexisting_destination_symlink -q
```

Expected: four parametrized failures. The first observes `None` instead of
`tarfile.data_filter`; the two unavailable-filter cases extract instead of
raising `invalid_scope`; the symlink case writes outside the destination instead
of raising `OutsideDestinationError`.
Run the unsafe-member test separately and expect all six cases to pass.

- [ ] **Step 4: Implement the minimal fail-closed repair**

Keep every existing member check and replace only the unfiltered extraction:

```python
        try:
            data_filter = tarfile.data_filter
        except AttributeError as exc:
            raise ReviewContractError(
                "invalid_scope", "safe tar data filter is unavailable"
            ) from exc
        if not callable(data_filter):
            raise ReviewContractError(
                "invalid_scope", "safe tar data filter is unavailable"
            )
        bundle.extractall(destination, members=members, filter=data_filter)
```

- [ ] **Step 5: Verify GREEN on every supported Python runtime**

Create temporary Python 3.11 and 3.13 virtual environments outside the
repository, install `requirements-dev.txt`, and run the four new test names
under Python 3.11, 3.13, and 3.14. Expected: ten parametrized cases pass on
each runtime with no warnings. Then run all of
`tests/unit/test_opus_review_bridge.py` under Python 3.13.

- [ ] **Step 6: Run complete local and hermetic hosted-shape verification**

Run the complete unit suite under Python 3.13. Also create a temporary
single-branch, non-local clone of the feature branch and run with a runner-like
home so local-only Git objects and user paths cannot mask the four excluded
failures. Expected: the 36 Opus failures are absent; only the two ledger-path
and two missing-trigger-object/smoke failures remain. Run `scripts/ci_smoke.py`,
recording its known missing-trigger-object result in the hermetic clone.

- [ ] **Step 7: Review and commit the implementation**

Obtain an independent diff review against this Task 4 acceptance criteria.
Stage only the bridge and bridge-test paths, verify the staged diff, and commit:

```sh
env -u GIT_INDEX_FILE git add -- \
  scripts/opus_review_bridge.py \
  tests/unit/test_opus_review_bridge.py
env -u GIT_INDEX_FILE git diff --cached --check
env -u GIT_INDEX_FILE git commit -m "fix(opus): use safe archive extraction filter"
```

- [ ] **Step 8: Push once and rerun hosted CI**

After a fresh remote-ref and PR preflight, perform one normal push to
`codex/opus-provider-free-lane-v`. Do not force-push, push `main`, or merge.
Monitor the automatically triggered hosted CI run. Success means its unit
summary changes from `40 failed` to `4 failed`, with no Opus bridge failures;
the four remaining failures must be the two ledger-path assertions and the two
missing-trigger-object/smoke assertions. Do not modify those excluded surfaces.
