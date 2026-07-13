# Opus Lane V Receipt And Report Hardening Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make every Pipeline Codex Lane V verdict depend on one authoritative, receipt-backed Opus attempt whose complete scope and final verification report are mechanically bound and replay-safe.

**Architecture:** A new stdlib-only receipt module owns canonical scope hashing, secure shared state, per-attempt locks, and lifecycle transitions. The existing bridge resolves immutable Git authority and performs the one provider attempt inside that lifecycle; a separate report gate validates `lane-v-report/v2` and atomically publishes one bound mailbox report while `check_go_schema.py` preserves exact historical reports through a content-hash baseline.

**Tech Stack:** Python 3.11+ standard library, pytest, Git plumbing, POSIX `flock`, Bash, and macOS Seatbelt only behind a runtime capability probe.

## Global Constraints

- The approved design is `docs/superpowers/specs/2026-07-13-opus-lanev-receipt-hardening-design.md`; its Sections 6, 8, 9, and 10 are binding acceptance criteria.
- The authoritative descriptor is `coordination/verification/scopes/9655cc07-e71a-4ca4-9201-5492be8bb91f.json` with exact digest `sha256:90d72201235c5eeca3f18df6fe16064f24847b4da3b46ef29ffb8f3889f5bb62`.
- Every Task 1-7 commit must end with the exact trailer `Lane-V-Scope: coordination/verification/scopes/9655cc07-e71a-4ca4-9201-5492be8bb91f.json@sha256:90d72201235c5eeca3f18df6fe16064f24847b4da3b46ef29ffb8f3889f5bb62`.
- Production receipt state is shared across linked worktrees at `<resolved-git-common-dir-parent>/.codex/runtime/opus-review-receipts/v1/`; non-Codex publication state is at the sibling `lane-v-report-publications/v1/` directory. There is no production CLI flag that changes either root.
- State directories are owned by the current uid, real directories, and mode `0700`; lock and JSON files are regular, non-symlink files owned by the current uid and mode `0600`.
- Receipt writes use descriptor-relative opens, same-directory temporary files, file `fsync`, `os.replace`, and directory `fsync`; every read-modify-write runs under the same per-attempt `flock` and checks a monotonically increasing generation.
- Receipt lifecycle is exactly `reserved -> reviewed -> reconciled -> publishing -> published`; a released lock plus `reserved` state degrades to `attempt_state_uncertain` and never launches the provider again.
- Public review schema is `opus-review/v3`; reconciliation schema is `opus-reconciliation/v2`; receipt schema is `opus-review-receipt/v1`; scope schema is `lane-v-scope/v1`; new report schema is `lane-v-report/v2`.
- Production `review` derives task ID, requirements, allowed roots, commands, mode, and harness from a committed trigger-bound descriptor. Production `reconcile` accepts only `--receipt-id`; `--opus-review-json` and every stdin/file import variant are rejected.
- A descriptor is at most `65536` bytes and has the exact keys shown by the committed authority artifact. `question_id` uses 1-128 ASCII letters/digits/dot/underscore/hyphen; requirement and allowed-root lists normalize to 1-128 unique UTF-8 paths of at most 512 bytes each; command lists normalize to 1-32 unique UTF-8 strings of at most 4096 bytes each.
- Attempt identity is repository identity + profile + authoritative task ID + effective base + reviewed HEAD. Scope digest binds all canonical scope inputs, exact Git blob identities, trigger identity, and resolved authorization.
- Changed paths are obtained with NUL-delimited Git output, `--no-renames`, `--no-ext-diff`, and `--no-textconv`; comparison is byte-exact, case-sensitive, component-aware, and performs no Unicode normalization. Invalid UTF-8 changed paths fail closed.
- One provider launch is allowed per authoritative task and immutable range. There is no retry, reset CLI, substitute provider, or caller-created receipt.
- Provider stdout and stderr are drained concurrently, each retains at most `131072` bytes, and any truncation yields sanitized unavailable reason `output_limit` rather than parseable success.
- New reports contain one exact `## Verification Attestation` section with all fields in canonical order. Codex reports must match live reconciled receipt state and the exact stored Codex verdict; supported non-Codex reports use descriptor-derived `claude-lane-v` / `claude:lane-v-verifier` authority and literal `not-applicable` for every Opus field.
- Historical reports are accepted only by exact repository-relative path plus SHA-256 in `scripts/baselines/lane_v_report_v1.json`; modified or deleted baseline entries fail CI.
- `send-event` validates and no-replace publishes verification reports before staging. Validation failure leaves no final event; staging failure preserves the one validated final event for manual staging.
- Pure contract, parser, cleanup-injection, and output-bound tests always run. Actual Seatbelt, AF_UNIX, Claude, credential, or network integrations skip only after a shared capability probe names the unavailable facility; production remains fail-closed.
- Use `/Users/hyungkoookkim/Pipeline/.venv/bin/python` for worktree tests and prefix ordinary Git/pytest commands with `env -u GIT_INDEX_FILE`.
- No task emits a live mailbox event, consumes a cursor, mutates a route/lock, pushes, or performs any external publication.

## File Structure

| File | Responsibility |
|---|---|
| `scripts/opus_review_receipts.py` | Strict scope contracts, canonical hashes, shared secure receipt storage, attempt locks, lifecycle/replay rules, and receipt-backed publication transitions. |
| `scripts/opus_review_bridge.py` | Immutable trigger/descriptor resolution, complete Git scope construction, one provider execution, receipt-only reconciliation, report-field rendering, and resource safety. |
| `scripts/verification_report_gate.py` | Strict v2 report parsing, descriptor/trigger binding, live receipt comparison, non-Codex publication records, recovery, and atomic no-replace publication. |
| `scripts/check_go_schema.py` | Existing GO evidence checks plus historical manifest accounting and repository-wide v2 structural validation. |
| `scripts/baselines/lane_v_report_v1.json` | Exact path and SHA-256 manifest for every pre-v2 verification report. |
| `coordination/bin/send-event` | Compose a complete candidate, route verification reports through the Python publisher, then stage the exact published path. |
| `tests/unit/test_opus_review_receipts.py` | Canonicalization, Git-path, security, lock, lifecycle, replay, and concurrency coverage. |
| `tests/unit/test_opus_review_bridge.py` | Authority resolution, CLI incompatibility, receipt integration, severity preservation, output bounds, cleanup, and capability behavior. |
| `tests/unit/test_verification_report_gate.py` | Strict parser, authority/live-state comparison, publication race, and recovery coverage. |
| `tests/unit/test_check_go_schema.py` | Historical manifest, v2 repository scan, and existing GO evidence coverage. |
| `tests/unit/test_coordination_tooling.py` | End-to-end `send-event` failure, success, collision, and staging-failure behavior in temporary repositories. |
| `scripts/codex_protocol_model.py` and mirrored prompt/docs files | Canonical receipt CLI/report workflow and generated/mirrored operator doctrine. |

---

### Task 1: Canonical Scope Contracts And Complete Git Path Coverage

**Files:**
- Create: `scripts/opus_review_receipts.py`
- Create: `tests/unit/test_opus_review_receipts.py`
- Modify: `.gitignore`

**Interfaces:**
- Consumes: committed `lane-v-scope/v1` JSON bytes, repository identity, full base/head SHAs, NUL-delimited Git name-status bytes, and exact requirement blob bytes.
- Produces: `ScopeDescriptor`, `ScopeReference`, `ChangedPath`, `ReviewScope`, `strict_json_loads()`, `parse_scope_reference()`, `canonical_trigger_identity()`, `normalize_repo_path()`, `parse_name_status_z()`, `assert_changed_path_coverage()`, `canonical_json_bytes()`, `compute_attempt_key()`, and `compute_scope_digest()`.

- [ ] **Step 1: Write failing strict-contract and canonical-hash tests**

Add tests that import the not-yet-created module and pin the public value objects and canonicalization:

```python
def test_scope_descriptor_rejects_duplicate_and_unknown_fields() -> None:
    duplicate = b'{"schema_version":"lane-v-scope/v1","task_id":"a","task_id":"b"}'
    with pytest.raises(receipts.ReceiptContractError, match="duplicate_json_key"):
        receipts.strict_json_loads(duplicate)

    value = _descriptor_mapping()
    value["unexpected"] = True
    with pytest.raises(receipts.ReceiptContractError, match="invalid_scope_descriptor"):
        receipts.ScopeDescriptor.from_mapping(value)


def test_attempt_key_ignores_scope_order_but_scope_digest_tracks_every_input() -> None:
    left = _review_scope(commands=(CMD_B, CMD_A), allowed=("scripts", "tests/unit"))
    reordered = _review_scope(commands=(CMD_A, CMD_B, CMD_A), allowed=("tests/unit", "scripts"))
    assert receipts.compute_attempt_key(left) == receipts.compute_attempt_key(reordered)
    assert receipts.compute_scope_digest(left) == receipts.compute_scope_digest(reordered)

    changed = dataclasses.replace(left, authorization_identity="user-task:other")
    assert receipts.compute_attempt_key(left) == receipts.compute_attempt_key(changed)
    assert receipts.compute_scope_digest(left) != receipts.compute_scope_digest(changed)
```

Also cover invalid UUIDs, unsupported mode/harness/profile pairs, both exact-base fields, descriptors over 65536 bytes, question IDs outside `[A-Za-z0-9][A-Za-z0-9._-]{0,127}`, empty/oversized collections, path items over 512 UTF-8 bytes, command items over 4096 UTF-8 bytes, invalid command strings, duplicate paths, and canonical digest rendering as `sha256:<64 lowercase hex>`.

- [ ] **Step 2: Run the focused tests and confirm RED**

Run:

```bash
env -u GIT_INDEX_FILE /Users/hyungkoookkim/Pipeline/.venv/bin/python -m pytest tests/unit/test_opus_review_receipts.py -q
```

Expected: collection fails with `ModuleNotFoundError: No module named 'opus_review_receipts'`.

- [ ] **Step 3: Implement strict JSON, descriptor, and canonical scope types**

Create these exact public contracts and keep filesystem/provider behavior out of this first slice:

```python
SCOPE_SCHEMA_VERSION = "lane-v-scope/v1"
RECEIPT_SCHEMA_VERSION = "opus-review-receipt/v1"
REVIEW_SCHEMA_VERSION = "opus-review/v3"
RECONCILIATION_SCHEMA_VERSION = "opus-reconciliation/v2"
CODEX_MODE = "codex-lane-v"
CODEX_HARNESS = "codex:lane-v-verifier"
CLAUDE_MODE = "claude-lane-v"
CLAUDE_HARNESS = "claude:lane-v-verifier"


class ReceiptContractError(ValueError):
    def __init__(self, reason: str, detail: str) -> None:
        super().__init__(f"{reason}: {detail}")
        self.reason = reason
        self.detail = detail


@dataclass(frozen=True)
class ScopeDescriptor:
    task_id: str
    question_id: str
    trigger_kind: str
    verification_mode: str
    verification_harness: str
    review_profile: str
    base_policy: str
    base_commit: str
    requirement_paths: tuple[str, ...]
    allowed_path_roots: tuple[str, ...]
    verification_commands: tuple[str, ...]


@dataclass(frozen=True)
class ScopeReference:
    descriptor_path: str
    descriptor_digest: str

@dataclass(frozen=True, order=True)
class ChangedPath:
    status: str
    path: str
    path_bytes: bytes = field(compare=False, repr=False)


@dataclass(frozen=True)
class ReviewScope:
    repository_identity: str
    task_id: str
    question_id: str
    trigger_kind: str
    trigger_identity: str
    trigger_commit: str
    trigger_path: str | None
    trigger_blob_id: str | None
    descriptor_path: str
    descriptor_digest: str
    descriptor_blob_id: str
    review_profile: str
    verification_mode: str
    verification_harness: str
    authorization_identity: str
    reviewed_head: str
    requested_base: str | None
    effective_base: str
    changed_paths: tuple[ChangedPath, ...]
    requirements: tuple[Mapping[str, str], ...]
    allowed_path_roots: tuple[str, ...]
    verification_commands: tuple[str, ...]
```

Implement `ScopeDescriptor.from_mapping()` and `ReviewScope.to_mapping()` with these exact rules: reject duplicate JSON keys through `object_pairs_hook`; require exact key sets; require lowercase full SHAs and UUID text; normalize unordered collections with `sorted(set(values))`; and emit UTF-8 canonical JSON with `sort_keys=True`, `separators=(",", ":")`, and `ensure_ascii=False`. `parse_scope_reference()` accepts exactly `<normalized-relative-path>@sha256:<64-lowercase-hex>`. `canonical_trigger_identity()` emits exactly `shipping-commit:<sha>` or `verify-request:<trigger-sha>:<normalized-event-path>`. Do not accept decorated or partially valid values.

- [ ] **Step 4: Write failing byte-path and coverage tests**

Pin parsing and coverage before adding Git helpers:

```python
@pytest.mark.parametrize("bad", ["", ".", "./x", "x/.", "x/../y", "/x", "x/", "x//y", "x\\y", "x*", "x?", "x[0]"])
def test_normalize_repo_path_rejects_ambiguous_authority_paths(bad: str) -> None:
    with pytest.raises(receipts.ReceiptContractError, match="invalid_repo_path"):
        receipts.normalize_repo_path(bad)


def test_coverage_is_byte_exact_component_aware_and_covers_deletes() -> None:
    changed = receipts.parse_name_status_z(b"M\0scripts/foo.py\0D\0tests/old.py\0")
    receipts.assert_changed_path_coverage(changed, ("scripts/foo.py", "tests"))
    with pytest.raises(receipts.ReceiptContractError, match="changed_path_not_allowed"):
        receipts.assert_changed_path_coverage(changed, ("scripts/foo", "tests/old"))


def test_invalid_utf8_changed_path_fails_closed() -> None:
    with pytest.raises(receipts.ReceiptContractError, match="unsupported_git_path_encoding"):
        receipts.parse_name_status_z(b"A\0bad-\xff.py\0")
```

Add fixtures for case-colliding names, NFC/NFD spellings, delete/add rename representation, copy-as-add, empty diff, malformed/truncated NUL records, and prefix collision `scripts/foo` versus `scripts/foobar`.

- [ ] **Step 5: Run the new path tests and confirm RED**

Run the exact node IDs added in Step 4. Expected: attribute failures for the three missing path functions.

- [ ] **Step 6: Implement byte-exact path parsing, coverage, and hash functions**

Implement `normalize_repo_path()` without `Path.resolve()` or Unicode/case normalization. Implement `parse_name_status_z()` for the exact `STATUS\0PATH\0` stream emitted by `git diff --name-status -z --no-renames`; accept only `A`, `D`, `M`, `T`, `U`, and `X`. Reject `C`/`R` because the production invocation disables copy/rename detection: a rename must arrive as `D` plus `A`, and a copy as `A`. Store both decoded text and original bytes. Coverage is true only for `path == root` or `path.startswith(root + b"/")`.

`compute_attempt_key()` hashes exactly this canonical mapping:

```python
{
    "schema_version": "opus-review-attempt-key/v1",
    "repository_identity": scope.repository_identity,
    "review_profile": scope.review_profile,
    "task_id": scope.task_id,
    "effective_base": scope.effective_base,
    "reviewed_head": scope.reviewed_head,
}
```

Render the receipt ID as `opr1:<64 lowercase hex>` and the scope digest as `sha256:<64 lowercase hex>` over `ReviewScope.to_mapping()`.

- [ ] **Step 7: Add the narrow runtime ignore rules**

Append exactly:

```gitignore
.codex/runtime/opus-review-receipts/
.codex/runtime/lane-v-report-publications/
```

Do not ignore `.codex/runtime/` broadly.

- [ ] **Step 8: Run Task 1 tests and commit**

Run:

```bash
env -u GIT_INDEX_FILE /Users/hyungkoookkim/Pipeline/.venv/bin/python -m pytest tests/unit/test_opus_review_receipts.py -q
env -u GIT_INDEX_FILE git diff --check
```

Expected: all Task 1 tests pass and diff check is silent.

Commit with explicit pathspecs and the required trailer:

```bash
env -u GIT_INDEX_FILE git add .gitignore scripts/opus_review_receipts.py tests/unit/test_opus_review_receipts.py
env -u GIT_INDEX_FILE git commit -m "feat(opus): define authoritative Lane V scopes" -m "Lane-V-Scope: coordination/verification/scopes/9655cc07-e71a-4ca4-9201-5492be8bb91f.json@sha256:90d72201235c5eeca3f18df6fe16064f24847b4da3b46ef29ffb8f3889f5bb62"
```

---

### Task 2: Secure Shared Receipt Store And Replay-Safe Lifecycle

**Files:**
- Modify: `scripts/opus_review_receipts.py`
- Modify: `tests/unit/test_opus_review_receipts.py`

**Interfaces:**
- Consumes: `ReviewScope` from Task 1 and normalized review/reconciliation/publication mappings supplied by the policy-owning bridge/gate.
- Produces: `ReceiptStore.for_repo()`, `ReceiptStore.lock_attempt()`, `LockedAttempt.reserve_or_load()`, `LockedAttempt.record_review()`, `LockedAttempt.record_reconciliation()`, `LockedAttempt.begin_publication()`, `LockedAttempt.finish_publication()`, and immutable `ReceiptRecord`/`ReservationDecision` values.

- [ ] **Step 1: Write failing state-root and metadata tests**

Create a temporary Git repository plus two linked worktrees and assert both `ReceiptStore.for_repo()` calls derive the primary repository root's shared runtime directory. Add injected `stat_fn` cases for wrong uid, mode `0755`, symlink, directory-in-place-of-file, FIFO, truncated JSON, duplicate keys, wrong attempt key, wrong digest, and generation rollback.

Use this public shape:

```python
store = receipts.ReceiptStore.for_repo(worktree, state_root=tmp_path / "state")
with store.lock_attempt(scope, blocking=False) as attempt:
    decision = attempt.reserve_or_load(scope)
assert decision.action == "launch"
assert decision.record.state == "reserved"
assert decision.record.generation == 1
```

`state_root` is keyword-only and available only to Python callers/tests; no CLI in any task exposes it.

- [ ] **Step 2: Run the metadata tests and confirm RED**

Expected: `AttributeError` for `ReceiptStore`.

- [ ] **Step 3: Implement secure root derivation and descriptor-relative I/O**

Implement production derivation with:

```python
git_common = subprocess.run(
    ["env", "-u", "GIT_INDEX_FILE", "git", "rev-parse", "--path-format=absolute", "--git-common-dir"],
    cwd=repo_root,
    check=True,
    capture_output=True,
    text=True,
).stdout.strip()
primary_root = Path(git_common).resolve().parent
state_root = primary_root / ".codex/runtime/opus-review-receipts/v1"
```

Create the narrow parents with mode `0700`, open the validated final directory with `O_RDONLY|O_DIRECTORY|O_CLOEXEC|O_NOFOLLOW`, and perform lock/receipt operations by name plus `dir_fd`. A file is valid only when `fstat()` reports current uid, regular type, exact `0600`, and link count `1`. Initial reservation creates the final receipt name with `O_CREAT|O_EXCL|O_WRONLY|O_CLOEXEC|O_NOFOLLOW`, writes canonical bytes, and fsyncs file plus directory before provider work. Later atomic replacement uses a random same-directory `O_CREAT|O_EXCL|O_NOFOLLOW` temp, canonical bytes, `fsync(temp_fd)`, `os.replace(temp_name, final_name, src_dir_fd=dir_fd, dst_dir_fd=dir_fd)`, then `fsync(dir_fd)`; clean the temp on every exception.

- [ ] **Step 4: Write failing reservation, abandonment, and concurrency tests**

Pin these decisions:

```python
assert first.action == "launch"
assert identical_while_reviewed.action == "return"
assert identical_after_reconcile.action == "return"
assert abandoned_reserved.action == "degrade_uncertain"
```

Two processes racing the same scope must yield exactly one `launch` and one `attempt_in_progress`/stored return. Two linked worktrees use the same state root. Reordered/duplicate commands and allowed roots remain idempotent; changed requirement digest, authorization, command tokenization, trigger blob, or descriptor digest under the same attempt key raises `attempt_scope_conflict`. A second lawful task ID on the same range creates a distinct receipt. Inject failures before reservation, after reservation, during provider ownership, after a normalized result exists, and during atomic replacement; only the pre-reservation case may leave no receipt, and no post-reservation recovery may return `launch`.

- [ ] **Step 5: Run the reservation tests and confirm RED**

Expected: missing `lock_attempt()` and transition methods.

- [ ] **Step 6: Implement receipt records, locking, and review transitions**

Define exact states and decision actions:

```python
RECEIPT_STATES = ("reserved", "reviewed", "reconciled", "publishing", "published")
RESERVATION_ACTIONS = ("launch", "return", "degrade_uncertain")

@dataclass(frozen=True)
class ReceiptRecord:
    receipt_id: str
    attempt_key: str
    scope_digest: str
    scope: Mapping[str, Any]
    state: str
    generation: int
    review: Mapping[str, Any] | None
    reconciliation: Mapping[str, Any] | None
    publication: Mapping[str, Any] | None

@dataclass(frozen=True)
class ReservationDecision:
    action: str
    record: ReceiptRecord
```

Hold the regular mode-`0600` lock file's exclusive `flock` for the entire `with` block. `blocking=False` maps `EWOULDBLOCK` to `ReceiptStateError("attempt_in_progress", "attempt lock is held")`. `reserve_or_load()` creates generation 1 before provider work; exact existing `reviewed` or later state returns; existing `reserved` acquired after prior owner release returns `degrade_uncertain`. `record_review()` accepts only `reserved`, increments generation, and writes one normalized review; it may be called by the bridge to persist `attempt_state_uncertain` without provider use.

- [ ] **Step 7: Write failing reconciliation and publication transition tests**

Cover identical replay, changed replay, two simultaneous identical reconcilers, two conflicting reconcilers, exact generation checks, pass/unavailable dispositions rejection, issue-ID set equality, and every illegal state edge. Pin publication transitions for one path/digest, conflicting second path, exact idempotent finish, absent/exact/mismatched recovery, and no transition from an unreconciled record.

- [ ] **Step 8: Implement reconciliation/publication transitions**

`record_reconciliation(input_mapping, result_mapping)` computes a canonical `sha256:` input digest, stores both mapping and digest under `reconciliation`, and returns the stored record on exact replay. Any byte-relevant change raises `reconciliation_replay_conflict`.

`begin_publication(path, candidate_digest)` requires `reconciled`, stores `publishing` metadata, and increments generation. `finish_publication()` requires the exact planned pair, stores `published`, and increments generation. `recover_publication(path, observed_digest)` returns one of `finalize`, `clear`, or raises `publication_replay_conflict`; `clear` moves back to `reconciled` with a new generation before one new candidate can begin.

- [ ] **Step 9: Run Task 2 tests and commit**

Run:

```bash
env -u GIT_INDEX_FILE /Users/hyungkoookkim/Pipeline/.venv/bin/python -m pytest tests/unit/test_opus_review_receipts.py -q
env -u GIT_INDEX_FILE git diff --check
```

Expected: all receipt tests pass with no resource warnings.

Commit:

```bash
env -u GIT_INDEX_FILE git add scripts/opus_review_receipts.py tests/unit/test_opus_review_receipts.py
env -u GIT_INDEX_FILE git commit -m "feat(opus): persist one replay-safe review receipt" -m "Lane-V-Scope: coordination/verification/scopes/9655cc07-e71a-4ca4-9201-5492be8bb91f.json@sha256:90d72201235c5eeca3f18df6fe16064f24847b4da3b46ef29ffb8f3889f5bb62"
```

---
### Task 2A: Add Secure Receipt-ID Lookup For Reconciliation

**Files:**
- Modify: `scripts/opus_review_receipts.py`
- Modify: `tests/unit/test_opus_review_receipts.py`

**Interfaces:**
- Consumes: Task 2's validated common-directory store, descriptor-relative
  receipt naming, metadata checks, and per-attempt lock.
- Produces: `ReceiptStore.lock_receipt()` and
  `LockedAttempt.load_existing()` for Task 4's receipt-only reconciliation.

- [ ] **Step 1: Write failing receipt-ID lookup tests**

Create a receipt through `lock_attempt(scope)`, then acquire it through
`lock_receipt(record.receipt_id)` and prove `load_existing()` returns the same
record and enables an ordinary reconciliation transition. Reject wrong prefix,
wrong length, uppercase hex, non-hex, path separators, and traversal-shaped
identifiers before opening the state directory. A canonical but absent ID must
raise `receipt_missing` and must not create a receipt. Corrupt, symlink, special,
wrong-mode, wrong-owner, and link-count cases continue through the existing
descriptor-relative metadata checks. Two access paths for the same ID must
contend on the same lock.

- [ ] **Step 2: Run the lookup tests and confirm RED**

Expected: `ReceiptStore` has no `lock_receipt()` method.

- [ ] **Step 3: Implement exact receipt-ID lookup without directory scanning**

Validate the exact grammar `opr1:<64 lowercase hex>`, derive the existing
receipt and lock basenames directly from that digest, and reuse `LockedAttempt`
plus the existing private-directory/file checks. `load_existing()` requires an
active lock, reads exactly that receipt, stores it as the current checked
generation for later transitions, and never reserves or creates a receipt.
Keep `state_root` internal and expose no CLI here.

- [ ] **Step 4: Run Task 2A tests and commit**

Run:

```bash
env -u GIT_INDEX_FILE /Users/hyungkoookkim/Pipeline/.venv/bin/python -m pytest tests/unit/test_opus_review_receipts.py -q
env -u GIT_INDEX_FILE git diff --check
```

Commit:

```bash
env -u GIT_INDEX_FILE git add scripts/opus_review_receipts.py tests/unit/test_opus_review_receipts.py
env -u GIT_INDEX_FILE git commit -m "feat(opus): lock existing receipts by id" -m "Lane-V-Scope: coordination/verification/scopes/9655cc07-e71a-4ca4-9201-5492be8bb91f.json@sha256:90d72201235c5eeca3f18df6fe16064f24847b4da3b46ef29ffb8f3889f5bb62"
```

---
### Task 3: Bound Provider Resources And Classify Host Capabilities

**Files:**
- Modify: `scripts/opus_review_bridge.py`
- Modify: `tests/unit/test_opus_review_bridge.py`

**Interfaces:**
- Consumes: the current provider runner, broker/sandbox process-group code, and Tasks 1-2 receipt contracts for sanitized failure metadata.
- Produces: `CapturedProcess`, `HostCapabilities`, `probe_host_capabilities()`, bounded concurrent drains, deterministic partial-constructor cleanup, and capability-gated integration markers.

- [ ] **Step 1: Write failing bounded-output tests**

Use real short-lived subprocesses that independently and simultaneously write more than `PROVIDER_OUTPUT_LIMIT_BYTES = 131072` to stdout/stderr. Assert both pipes are fully drained, retained bytes never exceed the cap, per-stream truncation flags are exact, the child cannot deadlock on a full pipe, timeout kills descendants, reader failure still kills the group and joins the other drainer, and reader threads are joined before return. Preserve/add provider parsing cases for malformed JSON, oversized JSON, invalid UTF-8, trailing stream events, mismatched returned scope, missing/non-Opus model, and nonzero exit while drainers are active.

Pin the return type:

```python
@dataclass(frozen=True)
class CapturedProcess:
    args: tuple[str, ...]
    returncode: int
    stdout: bytes
    stderr: bytes
    stdout_truncated: bool
    stderr_truncated: bool
```

- [ ] **Step 2: Run bounded-output tests and confirm RED**

Expected: the existing tempfile-backed runner has no truncation fields and retains all bytes.

- [ ] **Step 3: Replace unbounded temporary streams with concurrent bounded drains**

Launch with `stdout=PIPE`, `stderr=PIPE`, and `start_new_session=True`. Start one reader thread per pipe before waiting. Each reader loops to EOF, appends only the first 131072 bytes, and marks truncation while continuing to discard. On timeout, kill the process group, wait, close parent pipe handles, and join both readers. Decode only after the bound check; any truncation returns unavailable reason `output_limit` with failure stage `provider_exit` and exact truncation flags. Never persist raw retained bytes.

- [ ] **Step 4: Write failing broker-constructor cleanup tests**

Inject factories so socket allocation succeeds while bind, listen, or thread start fails. For every failure assert listener `close()` ran, any started thread was stopped/joined, socket path was removed, and calling `close()` again is harmless. Preserve a regression that enables `ResourceWarning` as an error.

- [ ] **Step 5: Implement constructor ownership from allocation onward**

Initialize every cleanup field before socket allocation, wrap the rest of `__init__` in `try/except BaseException`, call one idempotent `_close_partial()` on error, then re-raise. Normal `__exit__` calls the same cleanup. Do not depend on `__del__`.

- [ ] **Step 6: Write failing capability-probe and integration-selection tests**

Define:

```python
@dataclass(frozen=True)
class HostCapabilities:
    seatbelt: bool
    af_unix: bool
    claude_cli: bool
    missing: tuple[str, ...]
```

Pure tests inject command/socket probes and verify exact missing names. Actual Seatbelt/AF_UNIX/Claude tests share one fixture that runs the real probe once and skips with `host capability unavailable: <comma-separated names>` only when the required facility is absent. Add the pure injected provider/broker harness in this task; provider contract tests must use it and must never be hidden by this skip.

- [ ] **Step 7: Implement capability probing without weakening production**

Seatbelt probes `/usr/bin/sandbox-exec -p '(version 1) (allow default)' /usr/bin/true`; AF_UNIX creates/binds/closes a socket in a temporary directory; Claude resolution uses the existing allowlisted environment resolver. The probe reports capability only. Production review still reserves first and converts unavailable facilities to one stored `sandbox_unavailable`/`claude_not_found` result; it never bypasses sandboxing. Pin failure stages to the exact enum `broker_start|sandbox_probe|provider_spawn|provider_timeout|provider_exit|response_parse|contract_validation|model_validation|receipt_recovery`, and assert no raw argv/environment/stdout/stderr/provider text appears in stored state or CLI errors.

- [ ] **Step 8: Run Task 3 tests and commit**

Run:

```bash
env -u GIT_INDEX_FILE /Users/hyungkoookkim/Pipeline/.venv/bin/python -W error::ResourceWarning -m pytest tests/unit/test_opus_review_bridge.py -q
env -u GIT_INDEX_FILE git diff --check
```

Expected in this managed host: pure tests pass, actual Seatbelt/AF_UNIX cases skip with named capability reasons, and no ResourceWarning occurs.

Commit:

```bash
env -u GIT_INDEX_FILE git add scripts/opus_review_bridge.py tests/unit/test_opus_review_bridge.py
env -u GIT_INDEX_FILE git commit -m "fix(opus): bound provider output and cleanup" -m "Lane-V-Scope: coordination/verification/scopes/9655cc07-e71a-4ca4-9201-5492be8bb91f.json@sha256:90d72201235c5eeca3f18df6fe16064f24847b4da3b46ef29ffb8f3889f5bb62"
```

---

### Task 4: Bind Bridge Review And Reconciliation To Authoritative Receipts

**Files:**
- Modify: `scripts/opus_review_bridge.py`
- Modify: `tests/unit/test_opus_review_bridge.py`

**Interfaces:**
- Consumes: `ScopeDescriptor`, `ReviewScope`, `ReceiptStore`, and the secure
  `lock_receipt()`/`load_existing()` seam from Tasks 1-2A; the bounded
  provider/capability seams from Task 3; a shipping-commit or committed
  verify-request trigger; Codex verdict/dispositions/evidence.
- Produces: trigger-only `ReviewRequest`, `ResolvedReviewRequest`, `ReviewReceiptResult`, `resolve_authoritative_scope()`, receipt-backed `review()`, receipt-backed `reconcile_receipt()`, `opus-review/v3`, `opus-reconciliation/v2`, and canonical report attestation fields.

- [ ] **Step 1: Write failing CLI-boundary tests**

Replace the old caller-list CLI expectations with tests that prove:

```python
def test_review_cli_rejects_caller_selected_scope_lists(capsys: pytest.CaptureFixture[str]) -> None:
    for old_flag in ("--requirement", "--allow-path", "--verification-command"):
        with pytest.raises(SystemExit):
            bridge._parser().parse_args(["review", old_flag, "x"])


def test_reconcile_cli_rejects_caller_json(capsys: pytest.CaptureFixture[str]) -> None:
    with pytest.raises(SystemExit):
        bridge._parser().parse_args(["reconcile", "--opus-review-json", "{}"])


def test_reconcile_cli_requires_receipt_id() -> None:
    args = bridge._parser().parse_args([
        "reconcile", "--repo-root", ".", "--receipt-id", "opr1:" + "a" * 64,
        "--head", "b" * 40, "--codex-verdict", "GO",
    ])
    assert args.receipt_id == "opr1:" + "a" * 64
```

The review parser must expose exactly one trigger form: either `--shipping-commit <full-sha>` or the pair `--verify-request-commit <full-sha> --verify-request-path <relative-path>`. Both forms also require `--repo-root`, `--head`, optional `--base`, `--review-profile codex-lane-v`, and optional explicit `--authorization-source`.

- [ ] **Step 2: Run the CLI tests and confirm RED**

Expected: old flags still parse and `--receipt-id` is unknown.

- [ ] **Step 3: Split provider payload schema from bridge-issued v3 evidence**

Do not bump the current shared `SCHEMA_VERSION` in place. Replace it with:

```python
PROVIDER_SCHEMA_VERSION = "opus-provider-review/v1"
REVIEW_SCHEMA_VERSION = receipts.REVIEW_SCHEMA_VERSION
RECONCILIATION_SCHEMA_VERSION = receipts.RECONCILIATION_SCHEMA_VERSION
```

`OPUS_OUTPUT_SCHEMA` and `parse_structured_review()` validate only provider-owned fields under `opus-provider-review/v1`. `OpusReview.to_dict()` and `from_dict()` validate the stored normalized `opus-review/v3` mapping, including exact fields `failure_stage`, `stdout_truncated`, and `stderr_truncated`; no public CLI accepts that mapping. `ReviewReceiptResult.to_dict()` merges the normalized review with bridge-owned `receipt_id`, `scope_digest`, and `receipt_state` for stdout. This separation prevents the provider from asserting its own receipt metadata.

- [ ] **Step 4: Write failing shipping-trigger and verify-request authority tests**

Build real temporary Git histories. For shipping triggers, commit the descriptor first, then create a `feat:` commit with exactly this trailer shape:

```text
Lane-V-Scope: coordination/verification/scopes/<uuid>.json@sha256:<64 lowercase hex>
```

Assert rejection for zero or two trailers, wrong digest, descriptor absent at trigger commit, mutable working-tree descriptor changes, arbitrary task IDs, non-`feat|fix|refactor` subjects, shipping SHA unequal to reviewed HEAD, wrong base policy, abbreviated/moving commit names, and unsupported mode/harness/profile. Preserve the existing full-SHA compatibility rule: a 40-character uppercase SHA is canonicalized to lowercase before reservation and therefore resolves to the same attempt as its lowercase form.

For verify requests, use the canonical committed basename
`<timestamp>-<sender>-to-<recipient>-verify-request.md`, where `recipient` is
exactly `operator` or `operator2`. Require the filename timestamp/sender/
recipient, H1 sender/recipient, `**When:**` timestamp, `**From:** <sender>
(online)` envelope, `Event type: verify-request`, one exact `Reviewed head:`,
one exact `Reviewed base:`, and one exact `Lane-V-Scope:` field to agree.
Assert rejection for sender/envelope mismatch, wrong kind/recipient, trigger
path mismatch, wrong head/base, altered event blob, or descriptor not named by
the event. Prove the exact committed descriptor and verify-request blobs enter
the immutable requirements supplied to Opus even when the trigger commit is
later than the reviewed HEAD. Preserve the parsed operator recipient for the
later verification-report sender check.

- [ ] **Step 5: Run the authority tests and confirm RED**

Expected: missing `resolve_authoritative_scope()` and old `ReviewRequest` constructor mismatch.

- [ ] **Step 6: Implement immutable trigger, descriptor, requirement, and changed-path resolution**

Use this production request shape:

```python
@dataclass(frozen=True)
class ReviewRequest:
    repo_root: Path
    reviewed_head: str
    reviewed_base: str | None
    review_profile: str
    authorization_source: str
    trigger_kind: str
    trigger_commit: str
    trigger_path: str | None = None
    max_turns: int = DEFAULT_MAX_TURNS
    timeout_seconds: int = DEFAULT_TIMEOUT_SECONDS


@dataclass(frozen=True)
class ImmutableGitBlob:
    purpose: str
    commit: str
    path: str
    blob_id: str
    digest: str
    size_bytes: int


@dataclass(frozen=True)
class VerifyRequestEnvelope:
    timestamp: str
    sender: str
    recipient: str


@dataclass(frozen=True)
class ResolvedReviewRequest:
    request: ReviewRequest
    authority: receipts.ScopeDescriptor
    scope: receipts.ReviewScope
    review_requirements: tuple[ImmutableGitBlob, ...]
    authority_requirements: tuple[ImmutableGitBlob, ...]
    allowed_path_roots: tuple[str, ...]
    verification_commands: tuple[str, ...]
    verify_request: VerifyRequestEnvelope | None
```

Run Git with `env -u GIT_INDEX_FILE` and full SHAs. Accept only a literal 40-hex input, canonicalize it to lowercase, then prove it resolves to an existing commit without accepting branches/tags/abbreviations. Read committed bytes with `git show <commit>:<path>` and blob IDs with `git rev-parse <commit>:<path>`. Compute changed paths with:

```text
git -c core.quotepath=false -c diff.renames=false diff --name-status -z --no-renames --no-ext-diff --no-textconv <effective-base> <head> --
```

Pass the raw bytes to Task 1's parser, reject an empty set, and check complete
coverage before opening the receipt store. Requirement bytes come from
`<head>:<path>` and contribute path, blob ID, `sha256:` digest, and size.
Descriptor and verify-request authority blobs come from the full trigger
commit, are each limited to 65,536 bytes, and are retained only as
`ImmutableGitBlob` metadata after parsing. The isolated snapshot fetches full
reviewed HEAD, effective base, and any distinct trigger commit, then rechecks
each `commit:path` blob ID/digest before becoming read-only. The prompt embeds
no raw authority body or source-worktree absolute path; it exposes the bounded
metadata and exact `git show <full-commit>:<relative-path>` commands instead.
Tests mutate working-tree requirement bytes without changing HEAD and prove
the digest stays bound to the Git blob, then commit changed requirement bytes
at a new HEAD and prove the digest changes. Also pin later-trigger fetch,
oversized authority rejection, prompt sentinel absence, and both operator-seat
recipients. Repository identity is `sha256:` over the UTF-8 resolved absolute
Git common-directory path after `_pipeline_root()` succeeds.

- [ ] **Step 7: Write failing receipt-backed review tests with a pure provider seam**

Use Task 3's pure provider seam so policy/receipt cases inject a provider callable and never construct a real broker:

```python
calls = 0
def provider(resolved: bridge.ResolvedReviewRequest) -> bridge.OpusReview:
    nonlocal calls
    calls += 1
    return _normalized_pass_review(resolved)

first = bridge.review(request, provider=provider, store_factory=store_factory)
second = bridge.review(request, provider=provider, store_factory=store_factory)
assert calls == 1
assert first.receipt_id == second.receipt_id
assert second.receipt_state == "reviewed"
```

Add cases for two concurrent invocations, scope conflict, an abandoned reservation becoming `reviewed/unavailable` with `attempt_state_uncertain` and zero provider calls, changed HEAD producing a different attempt key, profile/authorization variation failing before or conflicting under the original attempt rather than unlocking a retry, pre-reservation scope failure creating no file, and a receipt-write failure leaving `reserved` for uncertain recovery.

- [ ] **Step 8: Implement the one-attempt review orchestration**

Give `review()` keyword-only injection seams whose defaults are production implementations:

```python
def review(
    request: ReviewRequest,
    *,
    scope_resolver: Callable[[ReviewRequest], ResolvedReviewRequest] = resolve_authoritative_scope,
    store_factory: Callable[[Path], receipts.ReceiptStore] = receipts.ReceiptStore.for_repo,
    provider: Callable[[ResolvedReviewRequest], OpusReview] = _perform_provider_review,
) -> ReviewReceiptResult:
```

Resolve and validate everything before `reserve_or_load()`. Hold the attempt lock across `provider()` and `record_review()`. Exact reviewed/reconciled/published repeats return stored normalized evidence. `degrade_uncertain` writes a normalized unavailable v3 result with `failure_stage="receipt_recovery"` and reason `attempt_state_uncertain` without broker construction. Provider/environment failures after reservation become one stored unavailable review; a final receipt-write error reports sanitized `receipt_write` and leaves the durable reservation.

Move Task 3's current provider body into `_perform_provider_review()` while
preserving its low-level resolver, runtime-factory, broker-factory,
sandbox-probe, runner, and resource tests. Receipt/replay tests inject only the
high-level `provider(resolved)` callable and therefore construct no real host
resource; Task 3 tests continue exercising the low-level seams directly.

- [ ] **Step 9: Write failing receipt-only reconciliation tests**

Assert fabricated JSON has no callable path, wrong repo/head/base/receipt fails, exact replay returns identical output, changed verdict/disposition/evidence/commit fails, simultaneous identical calls converge, simultaneous conflicting calls produce one success and one `reconciliation_replay_conflict`, and pass/unavailable receipts reject supplied dispositions.

Pin exact evidence hashing: empty evidence yields `none`; non-empty evidence yields `sha256:` over the exact UTF-8 bytes, without `.strip()` altering the digest.

- [ ] **Step 10: Implement receipt-only reconciliation and report-field rendering**

Keep the existing severity calculation as a private pure helper that consumes a validated stored `OpusReview`; the CLI must first acquire the receipt lock and verify repository/head/base/scope. Store a canonical input mapping containing receipt/scope IDs, exact verdict, sorted finding dispositions, exact evidence plus its digest, and expected commits. Emit `opus-reconciliation/v2` plus this ordered field mapping:

```python
{
    "Review profile": "codex-lane-v",
    "Authorization identity": stored_review.authorization_source,
    "Opus receipt ID": record.receipt_id,
    "Opus scope digest": record.scope_digest,
    "Cross-model review": stored_review.status,
    "Effective Opus model": stored_review.effective_model or "not-available",
    "Opus finding dispositions": canonical_dispositions_or_none,
    "Reconciliation guard": canonical_json({"go_allowed": result.go_allowed, "digest": input_digest}),
    "Degraded reason": stored_review.unavailable_reason or "none",
}
```

The canonical dispositions object contains exactly `disposition`, `evidence`, and `evidence_digest` for each finding ID. Require the exact stored Codex verdict later at publication; do not infer NITS versus FAIL from `go_allowed` alone.

- [ ] **Step 11: Run Task 4 tests and commit**

Run:

```bash
env -u GIT_INDEX_FILE /Users/hyungkoookkim/Pipeline/.venv/bin/python -m pytest tests/unit/test_opus_review_receipts.py tests/unit/test_opus_review_bridge.py -q
env -u GIT_INDEX_FILE git diff --check
```

Expected: pure bridge/receipt tests pass; actual host integration cases are not yet reclassified and may be selected out by their existing integration marker for this task.

Commit:

```bash
env -u GIT_INDEX_FILE git add scripts/opus_review_bridge.py tests/unit/test_opus_review_bridge.py
env -u GIT_INDEX_FILE git commit -m "feat(opus): reconcile only bridge-issued receipts" -m "Lane-V-Scope: coordination/verification/scopes/9655cc07-e71a-4ca4-9201-5492be8bb91f.json@sha256:90d72201235c5eeca3f18df6fe16064f24847b4da3b46ef29ffb8f3889f5bb62"
```

---

### Task 5: Strict Lane V Report V2 And Exact Historical Baseline

**Files:**
- Create: `scripts/verification_report_gate.py`
- Create: `tests/unit/test_verification_report_gate.py`
- Create: `scripts/baselines/lane_v_report_v1.json`
- Modify: `scripts/check_go_schema.py`
- Modify: `tests/unit/test_check_go_schema.py`
- Modify: `scripts/ci_smoke.py`

**Interfaces:**
- Consumes: committed mailbox report bodies, the strict scope descriptor/reference parser from Task 1, and no private receipt state during CI scans.
- Produces: `LaneVReport`, `parse_lane_v_report()`, `validate_structural_authority()`, `legacy_manifest_violations()`, `repository_report_violations()`, and a reviewed baseline-generation CLI.

- [ ] **Step 1: Write failing strict-attestation parser tests**

Create one valid Codex fixture and one valid non-Codex fixture. Both have exactly one section with this field order:

```python
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
    "Authorization identity",
    "Opus receipt ID",
    "Opus scope digest",
    "Cross-model review",
    "Effective Opus model",
    "Opus finding dispositions",
    "Reconciliation guard",
    "Degraded reason",
)
```

Assert rejection for a missing/duplicate section, missing/duplicate/reordered/unknown field, decorated field label, continuation line, duplicate/off-form verdict, non-operator filename sender, filename/envelope sender mismatch, abbreviated/uppercase H1 SHA, H1 SHA unequal to `Reviewed head`, bad UUID/digest/receipt ID, non-canonical JSON, oversized line, and attestation section over `ATTESTATION_MAX_BYTES = 65536`.

- [ ] **Step 2: Run parser tests and confirm RED**

Expected: `ModuleNotFoundError: No module named 'verification_report_gate'`.

- [ ] **Step 3: Implement the strict parser and structural value validation**

Create:

```python
REPORT_SCHEMA_VERSION = "lane-v-report/v2"
ATTESTATION_MAX_BYTES = 65_536
ATTESTATION_LINE_MAX_BYTES = 49_152


class ReportGateError(ValueError):
    def __init__(self, reason: str, detail: str) -> None:
        super().__init__(f"{reason}: {detail}")
        self.reason = reason
        self.detail = detail


@dataclass(frozen=True)
class LaneVReport:
    relative_path: str
    sender: str
    verdict: str
    h1_head: str
    fields: Mapping[str, str]
    body_digest: str
```

Parse the body as UTF-8 strictly and reject every carriage return or NUL.
Require exactly one undecorated `VERDICT: GO|NITS|FAIL` line and exactly one
exact `## Verification Attestation` heading. The heading is followed by exactly
one blank framing line, then the 17 consecutive physical `Label: value` lines
in canonical order. After field 17, accept only EOF or exactly one blank line
followed by an exact level-two heading. A blank, continuation, prose line,
`###` heading, extra framing blank, or eighteenth field cannot terminate the
section successfully. Measure each raw UTF-8 line and the exact heading-through-
field-17 byte span before value/JSON parsing. Parse dispositions and guard with
duplicate-key rejection, then require
`canonical_json_bytes(parsed).decode() == original_value`.

For `codex-lane-v`, require harness `codex:lane-v-verifier`, profile `codex-lane-v`, valid receipt/scope values, status `pass|issues|unavailable`, model/reason consistency, dispositions `none` or exact objects, and guard keys exactly `digest` then `go_allowed` in canonical JSON, where digest matches `sha256:<64-lowercase-hex>`. For `claude-lane-v`, require harness `claude:lane-v-verifier` and every Opus-specific value exactly `not-applicable`.

- [ ] **Step 4: Write failing committed-authority structure tests**

Use real temporary Git blobs for shipping and verify-request descriptors. Assert common fields must equal the committed descriptor/trigger: mode, harness, task ID, scope path/digest, trigger identity, head, and base. Report prose must not select a different mode. For a verify-request trigger, the report sender must equal the exact `operator` or `operator2` recipient encoded in the committed event filename; a shipping-commit trigger may be reported by either operator seat. Pin canonical trigger identities as:

```text
shipping-commit:<40-lowercase-sha>
verify-request:<40-lowercase-trigger-commit>:<relative-event-path>
```

The non-Codex positive fixture uses a committed descriptor with `verification_mode=claude-lane-v`, `verification_harness=claude:lane-v-verifier`, and no Codex receipt lookup.

- [ ] **Step 5: Implement structural authority validation**

Do not call Task 4's Codex-only `resolve_authoritative_scope()`. Build a
provider-neutral committed-authority loader from Task 1's public
`strict_json_loads()`, `ScopeDescriptor.from_mapping()`,
`parse_scope_reference()`, `canonical_trigger_identity()`, and path
normalization primitives. It accepts both supported Codex and Claude
mode/harness tuples, loads bounded descriptor/trigger bytes from Git rather
than the working tree, and returns:

```python
@dataclass(frozen=True)
class StructuralAuthority:
    descriptor: receipts.ScopeDescriptor
    reference: receipts.ScopeReference
    trigger_kind: str
    trigger_commit: str
    trigger_path: str | None
    trigger_identity: str
    verify_request_recipient: str | None
```

Require `Scope authority` to equal
`<descriptor-path>@<descriptor-digest>` and `Trigger identity` to equal the
canonical trigger identity. `validate_structural_authority()` returns this
provider-neutral authority for live validation in Task 6 and performs no
private-state read, changed-path review, provider validation, or receipt access.

- [ ] **Step 6: Write failing historical-manifest tests**

Pin manifest schema and drift:

```json
{
  "schema_version": "lane-v-report-v1-baseline/v1",
  "reports": [
    {
      "path": "coordination/mailbox/sent/<exact-name>-verification-report.md",
      "sha256": "<64 lowercase hex>"
    }
  ]
}
```

Tests must hash raw bytes before any decoding and prove exact path+body acceptance,
changed body detection, deleted baseline detection, duplicate path/digest
rejection, a new non-v2 report rejection regardless of timestamp/filename,
and a modified historical path being accepted only if its new body fully
satisfies v2. Unmatched new reports decode as strict UTF-8; `errors="replace"`
is not allowed at the trust boundary. `legacy_manifest_violations()` validates
manifest shape, duplicates, and missing paths; a changed digest is passed to
`repository_report_violations()` for a possible full v2 migration before it is
reported as drift.

- [ ] **Step 7: Extend `check_go_schema.py` and generate the exact baseline**

Preserve `go_report_violations()` and every existing GO evidence rule. Add a
raw carrier such as `RawReport(relative_path: str, raw: bytes)` and one public
`repository_report_violations(root, named_reports, manifest)` path. Hash raw
bytes first, strict-decode each report once, require either an exact legacy
path+digest or full v2 parsing/structural authority, and then apply the existing
GO evidence rules to that same decoded text when the verdict is GO. NITS/FAIL
skip only GO-specific evidence rules, not legacy/v2 structural validation.
Validate every baseline path exists; a modified baseline path is accepted only
after complete v2 migration. Update the live-mailbox test to assert the real
baseline-backed corpus rather than describing it as empty.

Add an explicit maintainer command:

```bash
env -u GIT_INDEX_FILE /Users/hyungkoookkim/Pipeline/.venv/bin/python scripts/check_go_schema.py --generate-baseline scripts/baselines/lane_v_report_v1.json
```

Initial generation enumerates only NUL-delimited Git-tracked `HEAD`
`coordination/mailbox/sent/*-verification-report.md` paths and hashes raw Git
blob bytes. It sorts by repository-relative path, writes canonical pretty JSON
through a same-directory temporary, fsyncs it, publishes with atomic
no-clobber semantics, and fsyncs the directory. An existing target fails.
`--replace-baseline` is valid only with `--generate-baseline`, requires an
existing valid manifest, and may update digests only for the exact existing
path set: it cannot add later reports, remove a missing historical path, or
change paths. After validation, explicit replacement uses same-directory
`os.replace` plus directory fsync. Tests pin concurrent creation, unchanged
target on failure, untracked-new detection, v2 migration of changed history,
missing-history retention, and path-set-preserving replacement. Run initial
generation once in this task, inspect every listed path, and commit the exact
hashes. Normal `check_go_schema.py` separately scans current filesystem reports
as raw bytes and never mutates.

- [ ] **Step 8: Wire CI smoke to the repository scan and confirm no private-state dependency**

Change both the CLI and smoke report gate to call the same public
repository-aware validator with the committed manifest; do not retain a second
private scan/trust path. A test sets `.codex/runtime` absent/unreadable and
proves the historical/v2 structural scan still completes; CI must not load a
receipt.

- [ ] **Step 9: Run Task 5 tests and commit**

Run:

```bash
env -u GIT_INDEX_FILE /Users/hyungkoookkim/Pipeline/.venv/bin/python -m pytest tests/unit/test_check_go_schema.py tests/unit/test_verification_report_gate.py -q
env -u GIT_INDEX_FILE /Users/hyungkoookkim/Pipeline/.venv/bin/python scripts/check_go_schema.py
env -u GIT_INDEX_FILE /Users/hyungkoookkim/Pipeline/.venv/bin/python scripts/ci_smoke.py
env -u GIT_INDEX_FILE git diff --check
```

Expected: all report tests pass, the exact historical corpus passes, smoke stays green, and no receipt store is required.

Commit:

```bash
env -u GIT_INDEX_FILE git add scripts/verification_report_gate.py tests/unit/test_verification_report_gate.py scripts/baselines/lane_v_report_v1.json scripts/check_go_schema.py tests/unit/test_check_go_schema.py scripts/ci_smoke.py
env -u GIT_INDEX_FILE git commit -m "feat(verify): require Lane V report attestations" -m "Lane-V-Scope: coordination/verification/scopes/9655cc07-e71a-4ca4-9201-5492be8bb91f.json@sha256:90d72201235c5eeca3f18df6fe16064f24847b4da3b46ef29ffb8f3889f5bb62"
```

---

### Task 6: Live Receipt Validation And Atomic Mailbox Publication

**Files:**
- Modify: `scripts/verification_report_gate.py`
- Modify: `scripts/opus_review_receipts.py`
- Modify: `coordination/bin/send-event`
- Modify: `tests/unit/test_verification_report_gate.py`
- Modify: `tests/unit/test_opus_review_receipts.py`
- Modify: `tests/unit/test_coordination_tooling.py`

**Interfaces:**
- Consumes: one fully composed temporary verification-report, intended final repository-relative path, committed authority from Task 5, and either a reconciled Codex receipt or descriptor-authorized non-Codex task.
- Produces: `validate_live_report()`, `publish_candidate()`, receipt/publication recovery, one no-clobber final report, and a `send-event` verifier-only publication branch.

- [ ] **Step 1: Write failing live Codex binding tests**

Build reconciled receipt fixtures and vary one report field at a time. Reject nonexistent/reserved/reviewed receipts; repository/head/base/task/scope mismatch; profile/authorization/status/model/dispositions/degraded reason mismatch; guard digest mismatch; GO with `go_allowed=false`; NITS/FAIL with `go_allowed=true`; and exact stored verdict mismatch including NITS substituted for FAIL and FAIL substituted for NITS.

Positive cases cover pass GO, unavailable degraded GO with exact reason, issues NITS, and issues FAIL. Sender must be `operator` or `operator2`; no other seat can publish even if its prose/receipt fields are otherwise valid.

- [ ] **Step 2: Run live binding tests and confirm RED**

Expected: missing `validate_live_report()`.

- [ ] **Step 3: Implement live receipt and non-Codex task validation**

For Codex, derive the receipt store from the report's repository, acquire the receipt's attempt lock by receipt ID, reload under lock, require state `reconciled|publishing|published`, and compare every field to stored scope/review/reconciliation. Require `report.verdict == reconciliation.codex_verdict` before any `go_allowed` consistency check, and require a verify-request-backed report sender to equal that request's operator recipient.

For non-Codex, use a sibling secure `TaskPublicationStore` at `.codex/runtime/lane-v-report-publications/v1/`, keyed by authoritative task UUID. It uses the same uid/mode/symlink/atomic-write rules as receipts and stores only task ID, authority digest, state, path, candidate digest, and generation.

- [ ] **Step 4: Write failing atomic publication and recovery tests**

Pin the contract:

```python
published = gate.publish_candidate(
    repo_root=repo,
    candidate_path=temp_report,
    final_relative=final_relative,
    receipt_store_factory=store_factory,
)
assert published == repo / final_relative
assert published.read_bytes() == temp_report.read_bytes()
```

Run two processes against one task/path and assert exactly one succeeds. Run one task against two paths and one path against altered bytes; reject both replays. Simulate crashes after `publishing` and after `os.link()`: absent final clears to permit one new candidate, exact final finalizes, mismatched final fails closed. Assert validation failure creates no final file and does not enter `publishing`.

- [ ] **Step 5: Implement no-replace publication under the task lock**

Require candidate and final parent to be the same validated mailbox directory. After live validation, record `publishing`, then call:

```python
os.link(
    candidate_path.name,
    final_path.name,
    src_dir_fd=directory_fd,
    dst_dir_fd=directory_fd,
    follow_symlinks=False,
)
os.fsync(directory_fd)
```

`FileExistsError` is never overwritten. Hash the final through the same directory descriptor and finish only when it equals the candidate digest. Recovery follows the exact absent/exact/mismatched rules from the design. The CLI is:

```text
verification_report_gate.py publish --repo-root <root> --candidate <temp-path> --final-relative <relative-path>
```

It has no `--state-root`, no bypass, and returns nonzero with a sanitized reason.

- [ ] **Step 6: Write failing `send-event` end-to-end tests**

In temporary Git repositories, install a `.venv/bin/python` symlink to `sys.executable`, copy the required Python scripts, seed committed descriptor/trigger/receipt fixtures, then invoke the real shell tool. Cover:

- invalid report leaves no final path and no staged path;
- valid report preserves the exact composed envelope and stages its final path;
- same-second/no-replace collision never overwrites;
- a publication race yields one final report;
- forced `git add` failure preserves the validated final report, prints the manual-staging recovery, and a second emission for the same task is rejected; and
- non-verification event behavior remains byte-for-byte compatible with existing tests.

- [ ] **Step 7: Route only verification reports through the Python publisher**

Keep current validation/composition for every event kind. Remove the shell pre-existence check only from the verification-report branch. After the temp file is complete:

```bash
if [ "$KIND" = "verification-report" ]; then
  COMMON=$(env -u GIT_INDEX_FILE git -C "$ROOT" rev-parse --path-format=absolute --git-common-dir)
  PRIMARY_ROOT=$(dirname "$COMMON")
  TRUSTED_PYTHON="$PRIMARY_ROOT/.venv/bin/python"
  [ -x "$TRUSTED_PYTHON" ] || { echo "send-event: trusted Pipeline Python unavailable" >&2; exit 4; }
  env -u GIT_INDEX_FILE "$TRUSTED_PYTHON" "$PRIMARY_ROOT/scripts/verification_report_gate.py" \
    publish --repo-root "$ROOT" --candidate "$TMP" --final-relative "$REL"
else
  mv "$TMP" "$F"
fi
```

Then retain the existing `git add -f -- "$REL"` behavior. If staging fails after publication, print the exact retained path and exit 0. The trap removes only the temporary candidate, never the published final.

- [ ] **Step 8: Run Task 6 tests and commit**

Run:

```bash
env -u GIT_INDEX_FILE /Users/hyungkoookkim/Pipeline/.venv/bin/python -m pytest tests/unit/test_opus_review_receipts.py tests/unit/test_verification_report_gate.py tests/unit/test_coordination_tooling.py -q
bash -n coordination/bin/send-event
env -u GIT_INDEX_FILE git diff --check
```

Expected: live binding, publication/recovery, and shell tests pass; shell syntax is clean.

Commit:

```bash
env -u GIT_INDEX_FILE git add scripts/verification_report_gate.py scripts/opus_review_receipts.py coordination/bin/send-event tests/unit/test_verification_report_gate.py tests/unit/test_opus_review_receipts.py tests/unit/test_coordination_tooling.py
env -u GIT_INDEX_FILE git commit -m "feat(mailbox): publish one receipt-bound Lane V report" -m "Lane-V-Scope: coordination/verification/scopes/9655cc07-e71a-4ca4-9201-5492be8bb91f.json@sha256:90d72201235c5eeca3f18df6fe16064f24847b4da3b46ef29ffb8f3889f5bb62"
```

---

### Task 7: Converge Protocol Model, Prompts, Report Format, And Architecture

**Files:**
- Modify: `scripts/codex_protocol_model.py`
- Modify: `tests/unit/test_protocol_prompt_sync.py`
- Modify: `.codex/agents/lane-v-verifier.toml`
- Modify: `.codex/agents/protocol-operator.toml`
- Modify: `.agents/skills/seat-operator/SKILL.md`
- Modify: `.agents/skills/seat-operator/verification-report-format.md`
- Modify: `.claude/skills/seat-operator/verification-report-format.md`
- Modify: `.github/workflows/ci.yml`
- Modify: `docs/protocol/codex/continuation.md`
- Modify: `docs/protocol/claude/independence-first.md`
- Modify: `docs/protocol/protocol-assembly-map.md`
- Modify: `docs/PROTOCOL-RULES-LOG.md`
- Modify: `ARCHITECTURE.md`
- Modify: `DECISIONS.md`
- Modify: `scripts/route_capability.py`
- Modify: `docs/superpowers/plans/2026-07-12-codex-opus-cross-model-verification.md`
- Modify: `docs/superpowers/plans/2026-07-12-codex-r-independence-standing-opus-authorization.md`
- Modify: `docs/superpowers/specs/2026-07-12-codex-opus-cross-model-verification-design.md`
- Modify: `docs/superpowers/specs/2026-07-12-codex-r-independence-standing-opus-authorization-design.md`
- Modify: `docs/superpowers/specs/2026-07-13-opus-lanev-receipt-hardening-design.md`

**Interfaces:**
- Consumes: final Task 1-6 CLI/schema names and the authoritative scope descriptor path/digest.
- Produces: one canonical executable doctrine in `CROSS_MODEL_VERIFICATION_RULES`, synchronized operator/verifier surfaces, exact v2 report skeleton, updated truth/ADR/assembly docs, and prompt-sync regressions.

- [ ] **Step 1: Write failing prompt and documentation sync assertions**

Update the existing cross-model prompt-sync test to require these exact concepts across the model, continuation, operator skill, lane-v verifier, and protocol operator:

```python
required = (
    "lane-v-scope/v1",
    "opus-review/v3",
    "opus-reconciliation/v2",
    "--shipping-commit",
    "--verify-request-commit",
    "--verify-request-path",
    "--receipt-id",
    "--opus-review-json is removed",
    "attempt_state_uncertain",
    "one provider process attempt and no automatic retry",
    "lane-v-report/v2",
    "## Verification Attestation",
    "Opus receipt ID:",
    "Opus scope digest:",
    "exact stored Codex verdict",
)
```

Assert the old caller-selected `--requirement`, `--allow-path`, `--verification-command`, normalized `opus-review/v2`, and reconcile-JSON instructions are absent from active operator/verifier surfaces. Assert `.codex/hooks.json` is unchanged by checking that the Lane V rule is documented as a `send-event` publication gate rather than a hook.

- [ ] **Step 2: Run prompt-sync tests and confirm RED**

Run:

```bash
env -u GIT_INDEX_FILE /Users/hyungkoookkim/Pipeline/.venv/bin/python -m pytest tests/unit/test_protocol_prompt_sync.py -q
```

Expected: the new receipt/schema phrases are absent and old CLI text remains.

- [ ] **Step 3: Update the executable protocol model first**

Rewrite `CROSS_MODEL_VERIFICATION_RULES` so the generated doctrine says:

- the trigger-bound committed descriptor, not caller arguments, defines requirements/paths/commands;
- `review` accepts one of the two authoritative trigger forms and returns `opus-review/v3` with receipt/scope IDs;
- exact identical review is idempotent and changed scope conflicts; no retry/reset exists;
- `reconcile` loads only `--receipt-id` and returns `opus-reconciliation/v2` report fields;
- final reports use `lane-v-report/v2`, exact attestation, exact stored verdict, and `send-event` live validation;
- unavailable/uncertain remains visibly degraded; and
- Opus remains advisory while the operator retains GO/NITS/FAIL authority.

Render once and copy that exact doctrine into the mirrored active surfaces. Do not preserve stale v2/caller-JSON instructions for compatibility.

- [ ] **Step 4: Update the operator report skeleton and CLI examples**

In both byte-identical `verification-report-format.md` mirrors, retain the existing evidence/findings sections and terminal `## Exact Next Trigger` section, and replace the body skeleton with all 17 ordered attestation lines. The Codex example obtains the field block from `reconcile --receipt-id`; the non-Codex example uses `not-applicable` for every Opus line. Show full lowercase SHA in the H1 subject, exact undecorated verdict, and `send-event` as the only publisher.

Use this review command shape:

```bash
env -u GIT_INDEX_FILE .venv/bin/python scripts/opus_review_bridge.py review \
  --repo-root . --head "$HEAD" --base "$BASE" --review-profile codex-lane-v \
  --shipping-commit "$HEAD"
```

Use this reconcile command shape:

```bash
env -u GIT_INDEX_FILE .venv/bin/python scripts/opus_review_bridge.py reconcile \
  --repo-root . --receipt-id "$RECEIPT_ID" --head "$HEAD" --base "$BASE" \
  --codex-verdict GO
```

Finding dispositions/evidence remain repeated `--disposition ID=value` and `--evidence ID=value` flags.

- [ ] **Step 5: Document the authority artifact and append the decision**

Add `coordination/verification/scopes/` to the protocol assembly map as the committed owner of pre-stated Lane V questions, not a mailbox/cursor authority. Append `ADR-024: Bind Lane V to shared receipts and one report publication` to `DECISIONS.md`; record the cooperative-local trust boundary, common-dir state, authoritative descriptor, receipt-only incompatibility, no fake HMAC, strict legacy hash baseline, and no-replace publisher. Do not edit earlier ADR bodies.

Add a two-line supersession notice near the status of each of the two 2026-07-12 Opus plans and two designs: their blindness/sandbox/severity decisions remain historical, while caller-selected scope/reconciliation is superseded by the 2026-07-13 approved design. Mark the `check_go_schema.py` cross-model follow-up in `docs/protocol/claude/independence-first.md` as mechanized, update the rule-log entry from partial prompt enforcement to the v2 write gate, refresh the CI gate comment, and remove stale checker line-number coupling from `scripts/route_capability.py` while preserving its non-vacuous evidence rule.

- [ ] **Step 6: Refresh architecture truth and anchors**

Replace the obsolete `_resolved_authorization_source` module-map row with stable new anchors for receipt store, authoritative scope resolution, and report publication. Update Runtime Invariants with the shared lifecycle, byte-complete scope, output cap, v2 report gate, historical manifest, and host-capability split. Bump `*Last verified:*` to 2026-07-13 and the current implementation HEAD's short SHA immediately before this task's commit.

- [ ] **Step 7: Run Task 7 tests/checkers and commit**

Run:

```bash
env -u GIT_INDEX_FILE /Users/hyungkoookkim/Pipeline/.venv/bin/python -m pytest tests/unit/test_protocol_prompt_sync.py tests/unit/test_check_go_schema.py -q
env -u GIT_INDEX_FILE /Users/hyungkoookkim/Pipeline/.venv/bin/python scripts/check_doc_claims.py ARCHITECTURE.md docs/superpowers/specs/2026-07-13-opus-lanev-receipt-hardening-design.md docs/superpowers/plans/2026-07-13-opus-lanev-receipt-hardening.md
env -u GIT_INDEX_FILE /Users/hyungkoookkim/Pipeline/.venv/bin/python scripts/check_doc_claims.py --sha-refs
env -u GIT_INDEX_FILE /Users/hyungkoookkim/Pipeline/.venv/bin/python scripts/ci_smoke.py
env -u GIT_INDEX_FILE git diff --check
```

Expected: prompt/schema tests pass, doc anchors and SHA baseline show no drift, smoke is green, and `.codex/hooks.json` is not in the diff.

Commit:

```bash
env -u GIT_INDEX_FILE git add scripts/codex_protocol_model.py scripts/route_capability.py tests/unit/test_protocol_prompt_sync.py .codex/agents/lane-v-verifier.toml .codex/agents/protocol-operator.toml .agents/skills/seat-operator/SKILL.md .agents/skills/seat-operator/verification-report-format.md .claude/skills/seat-operator/verification-report-format.md .github/workflows/ci.yml docs/protocol/codex/continuation.md docs/protocol/claude/independence-first.md docs/protocol/protocol-assembly-map.md docs/PROTOCOL-RULES-LOG.md ARCHITECTURE.md DECISIONS.md docs/superpowers/plans/2026-07-12-codex-opus-cross-model-verification.md docs/superpowers/plans/2026-07-12-codex-r-independence-standing-opus-authorization.md docs/superpowers/specs/2026-07-12-codex-opus-cross-model-verification-design.md docs/superpowers/specs/2026-07-12-codex-r-independence-standing-opus-authorization-design.md docs/superpowers/specs/2026-07-13-opus-lanev-receipt-hardening-design.md
env -u GIT_INDEX_FILE git commit -m "refactor(codex): bind Lane V workflow to receipts" -m "Lane-V-Scope: coordination/verification/scopes/9655cc07-e71a-4ca4-9201-5492be8bb91f.json@sha256:90d72201235c5eeca3f18df6fe16064f24847b4da3b46ef29ffb8f3889f5bb62"
```

---

## Final Integration And Verification

After every task's implementer report and task review are clean, run one broad whole-branch review for plan/spec integration and maintainability. This is a different pre-stated question from Lane V's final adversarial gate.

- [ ] **Run the complete focused acceptance bundle**

```bash
env -u GIT_INDEX_FILE /Users/hyungkoookkim/Pipeline/.venv/bin/python -m pytest \
  tests/unit/test_opus_review_receipts.py \
  tests/unit/test_opus_review_bridge.py \
  tests/unit/test_check_go_schema.py \
  tests/unit/test_verification_report_gate.py \
  tests/unit/test_coordination_tooling.py \
  tests/unit/test_protocol_prompt_sync.py -q
```

- [ ] **Run the full unit suite once**

```bash
env -u GIT_INDEX_FILE /Users/hyungkoookkim/Pipeline/.venv/bin/python -m pytest tests/unit -q
```

- [ ] **Run repository gates and diff checks**

```bash
env -u GIT_INDEX_FILE /Users/hyungkoookkim/Pipeline/.venv/bin/python scripts/check_go_schema.py
env -u GIT_INDEX_FILE /Users/hyungkoookkim/Pipeline/.venv/bin/python scripts/check_doc_claims.py
env -u GIT_INDEX_FILE /Users/hyungkoookkim/Pipeline/.venv/bin/python scripts/check_doc_claims.py --sha-refs
env -u GIT_INDEX_FILE /Users/hyungkoookkim/Pipeline/.venv/bin/python scripts/ci_smoke.py
env -u GIT_INDEX_FILE git diff --check 555041477bcdb9a432a1b238d664be0958c5c9ef..HEAD
shasum -a 256 coordination/verification/scopes/9655cc07-e71a-4ca4-9201-5492be8bb91f.json
```

Expected descriptor digest: `90d72201235c5eeca3f18df6fe16064f24847b4da3b46ef29ffb8f3889f5bb62`.

- [ ] **Run the independent actual-diff adversarial gate**

The primary Codex Lane V question is: “Does the final `5550414..HEAD` implementation mechanically enforce every abuse/edge case in approved design Section 9, with non-vacuous tests and no bypass around attempt uniqueness, scope authority, exact report verdict, or no-replace publication?” Inspect the actual diff and test mutations before forming the provisional verdict.

Then invoke the receipt-backed review exactly once for the final unchanged HEAD using the shipping-commit trigger and the descriptor's exact base. If the capability probe reports Seatbelt/AF_UNIX/Claude unavailable, preserve the resulting single degraded receipt/reason and do not retry or substitute another provider. Reconcile the stored receipt with the provisional Codex verdict and evidence-backed dispositions. Do not emit a mailbox report, consume a cursor, release a lock, or push.

- [ ] **Verify final branch state**

```bash
env -u GIT_INDEX_FILE git log --oneline -12
env -u GIT_INDEX_FILE git status --short
env -u GIT_INDEX_FILE git show --stat --oneline HEAD
```

Expected: one reviewed commit per Task 1-7 after the plan/descriptor preparation commit, clean worktree, no live mailbox/cursor/route/lock changes, and no push.

## Plan Self-Review Record

- Spec coverage: Tasks 1-7 map all design Sections 6.1-6.10, 8, 9.1-9.5, 10.1-10.4, and 11.
- File boundaries: receipt serialization/storage does not import provider policy; bridge owns provider/severity behavior; report gate owns report parsing/publication; `check_go_schema` owns CI corpus accounting.
- Type consistency: Task 1 produces `ScopeDescriptor`/`ReviewScope`; Task 2 consumes them and produces `ReceiptStore`; Task 3 consumes the store and produces stored v3/v2 evidence; Tasks 5-6 consume those exact mappings; Task 7 documents the final names.
- Execution conflict scan: Tasks are sequential where they share `opus_review_bridge.py`, `opus_review_receipts.py`, or their tests; no two implementers run concurrently on shared files.
- Authority scan: the scope descriptor is committed before implementation, every shipping task commit carries its exact path/digest trailer, and no planned step performs a live protocol or external-publication side effect.
