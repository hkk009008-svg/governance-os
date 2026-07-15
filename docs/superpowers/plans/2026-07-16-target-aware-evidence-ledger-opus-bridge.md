# Target-Aware Evidence-Ledger Opus Bridge Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a Pipeline-owned, receipt-bound Opus advisory bridge that can inspect a sealed evidence-ledger question without exposing either live repository, granting protocol authority, or allowing more than one provider attempt for the same review-family/question/sequence identity.

**Architecture:** The generic bridge gains one explicit `TargetReviewPolicy` boundary. Its existing Pipeline policy remains the byte-for-byte default. The evidence-ledger policy instead materializes a content-addressed closure of committed target Python blobs, selected committed Pipeline requirement blobs, and a copied/hash-verified runtime into a private snapshot with no live `.git` directory or link to either checkout. Authority is acyclic: render canonical scope bytes privately; commit a scope-preparation route that authorizes exactly that path+byte digest and zero provider actions; commit the immutable scope; commit a fresh active attempt route that binds preparation route+scope; record distinct explicit user consent that binds scope+attempt route; then commit a complete Side-Effect Executor Token that binds scope+attempt route+consent. All artifacts must agree before CAS reservation. Findings are advisory and can be reconciled only from another committed active route whose finite evidence references are bound into the same receipt.

**Tech Stack:** Python 3.11+ standard library, pytest, Git plumbing, existing `scripts/opus_review_bridge.py` and `scripts/opus_review_receipts.py`, POSIX `flock`, macOS Seatbelt, Claude CLI existing-session transport, and the Pipeline mailbox/capacity protocol.

## Global Constraints

- Binding umbrella design: `docs/superpowers/specs/2026-07-16-pipeline-recovery-sequence-design.md` at commit `426744766711d4d6057a4698f5bb19d454ad621d`.
- Binding hold: `coordination/mailbox/sent/2026-07-13T11-38-14Z-coordinator-to-all-coordination.md`, especially “Successor Workflow Boundary.”
- Hard predecessor: `docs/HANDOFF-director-2026-07-16-opus-b-d-recovery.md` must be committed and must bind the final Stage-D Operator GO, the exact locally integrated Opus head, merged-tree verification, and the terminal Opus join packet whose `done_evidence` names that handoff and report. The handoff commit, report commit, reviewed head, and integrated head must all be ancestors of the current primary `main`; any post-GO edit to `scripts/opus_review_bridge.py`, `scripts/opus_review_receipts.py`, `tests/unit/test_opus_review_bridge.py`, or `tests/unit/test_opus_review_receipts.py` blocks this plan.
- This plan is also the fixed recovery-succession wrapper for the overlapping candidate-policy and targeted-web plans. It terminally supersedes only the old Stage-A companion action/topology in `2026-07-15-pre-trigger-append-only-candidate-range.md`: the lawful predecessor is now the exact `R -> M0 -> F -> Q -> D -> T` Stage-A chain plus the final Stage-B-D handoff, and candidate-policy work must not mutate any Opus correction, descriptor, request, report, or handoff artifact. All other candidate-policy requirements remain binding.
- Because the target bridge and candidate policy share four implementation/test paths, their execution is serialized: target-bridge GO and its committed handoff/current-`main` ancestry gate precede a fresh candidate-policy route. The targeted-web route is later still and requires candidate-policy GO plus a separately authorized local integration and merged-tree handoff. The coordinator may route and reconcile these transitions but never performs or infers a production merge; if a routed plan uses an isolated worktree, the user-principal must separately name the local integrator and exact reviewed head/base.
- Pipeline remains the governance kernel. Evidence-ledger remains the product repository and retains one non-Codex controller plus independent Codex verification.
- The target bridge is advisory only. It receives no edit, controller, seat, verdict, route, mailbox, cursor, lock, publication, activation, push, spend, cleanup, credential-entry, or side-effect authority.
- The bound target is repository `hkk009008-svg/evidence-ledger`, linked worktree `/Users/hyungkoookkim/Pipeline/.worktrees/evidence-ledger-workbook-refresh-2026-07-11`, Gitdir `/Users/hyungkoookkim/evidence-ledger/.git/worktrees/evidence-ledger-workbook-refresh-2026-07-11`, common directory `/Users/hyungkoookkim/evidence-ledger/.git`, correction base `8eaed44f803d871f09135c5d89395d38cf9e939e`, and cumulative base `6941cb1eb5167da0b50d21cbf0e93ceff62cb1fa`.
- The initial family write allowlist is exactly `recommendation/cli.py`, `recommendation/tests/test_cli.py`, and `ARCHITECTURE.md` only when implementation makes its current publication claims stale.
- The first family is `e7c41a3d-8069-44e2-a0c7-cc1745947951`. It starts with `design-time/1`; its first implementation review is `actual-diff/2`. An issue-driven additive correction uses `actual-diff/3`, then `/4`, monotonically. It never retries an earlier identity. A changed repository, base, allowlist, policy, authority boundary, or design assumption requires a new family beginning at `design-time/1`.
- Every question uses the acyclic order `scope-preparation route → scope → fresh attempt route → distinct explicit user-consent event → complete Side-Effect Executor Token`. The preparation route binds a precomputed canonical scope path+digest, never a future commit. Earlier approval, standing approval, the umbrella-design approval, a prior question’s consent, or a token alone is insufficient. A scope never embeds the later attempt route/consent/token blobs, and no artifact refers to a not-yet-committed descendant. The committed consent event records an already received user-principal decision; it cannot fabricate or substitute for that live decision. If the executor context cannot authenticate the exact user reply/correlation, it stops and asks again.
- Every question after sequence 1 requires the immediately preceding receipt in the same family to be `reconciled`, not merely `reviewed`. Static family invariants must match exactly while question route, task ID, scope, consent, token, head, and sequence are fresh.
- One provider attempt is permitted per CAS identity `(review_family_id, question_kind, challenge_sequence)` and exact `task_id` plus scope digest. Exact replay returns the terminal receipt; the same CAS identity with a different task or scope is a conflict and launches no provider.
- Challenge material is limited to committed target Python code/tests, selected committed Pipeline requirements, and content-free command/authority metadata. Never materialize, read from the provider sandbox, hash into a prompt, log, or persist mutable databases, workbooks, resources, `data/`, `.superpowers/`, DSNs, credentials, business values, live Git metadata, or live worktree files.
- A successful receipt proves only that one advisory attempt occurred. Only the target controller edits/commits; only the Pipeline Operator issues cumulative GO/NITS/FAIL.
- Before every task shell block, use `set -euo pipefail`, define `PIPELINE_ROOT=/Users/hyungkoookkim/Pipeline`, and `cd "$PIPELINE_ROOT"`. Use explicit `git -C "$PIPELINE_ROOT"` or `git -C "$TARGET_WORKTREE"`; prefix ordinary Git and pytest with `env -u GIT_INDEX_FILE`.
- This plan authorizes no provider attempt, target edit/commit, mailbox send/consume, route mutation, lock, merge, push, publication, activation, cleanup, or paid spend by itself.

## File Structure

| File | Responsibility |
|---|---|
| `scripts/opus_target_review_bridge.py` | Strict scope/route/consent/token contracts, two-repository resolution, sealed closure, target CAS identity, review/reconciliation, and CLI. |
| `scripts/opus_review_bridge.py` | Default-preserving `TargetReviewPolicy` seam across source, snapshot, runtime, sandbox, verification grammar, prompt/schema, parsing, and unavailable results. |
| `scripts/opus_review_receipts.py` | Existing receipt lifecycle plus caller-supplied attempt identity with exact task/scope conflict checks and the target advisory verifier tuple. |
| `tests/unit/test_opus_target_review_bridge.py` | Contract, binding, closure, exclusion, consent/token, attempt, replay, reconciliation, authority, and CLI coverage. |
| `tests/unit/test_opus_review_bridge.py` | Byte-for-byte Pipeline default compatibility and policy-boundary tests. |
| `tests/unit/test_opus_review_receipts.py` | Target CAS/conflict and state-root coverage without widening Lane-V authority. |
| `tests/unit/test_protocol_prompt_sync.py` | Rendered target prompt/schema authority-negative assertions. |
| `docs/protocol/codex/ledger-cli-adoption.md` | Exact entry, consent, sequencing, reconciliation, and stop rules. |
| `ARCHITECTURE.md` | Verified policy/snapshot/receipt topology after implementation. |
| `docs/HANDOFF-target-aware-evidence-ledger-opus-bridge-2026-07-16.md` | Exact implementation range, independent report path+commit, tests, exclusions, and next route trigger. |

---

### Task 1: Define committed scope, route, consent, token, and family contracts

**Files:**
- Create: `scripts/opus_target_review_bridge.py`
- Create: `tests/unit/test_opus_target_review_bridge.py`

**Interfaces:**
- Consumes: content-addressed committed-blob references of the form `<canonical-path>@commit:<40-lowercase-hex>@blob:<40-lowercase-hex>@sha256:<64-lowercase-hex>`.
- Produces: `CommittedBlobReference`, `GitBlobBinding`, `ScopePreparationRouteBinding`, `CommittedRouteBinding`, `AttemptAuthorizationBundle`, `PipelineBinding`, `TargetBinding`, `TargetReviewScope`, strict JSON/canonicalization helpers, and scope/route/consent/token parsers.

- [ ] **Step 1: Capture the exact implementation base from a fresh route**

Before routing, the coordinator resolves the fixed Opus handoff from committed `main`, verifies its unique introduction commit and blob, follows its exact Stage-D report and terminal join `done_evidence`, validates the reported GO, and proves the reviewed and integrated heads are ancestors of current `main`. It then proves that none of the four shared bridge paths changed after the reviewed Opus head. Missing, duplicate, stale, NITS/FAIL, non-ancestor, or post-GO-edit evidence is a hard stop.

The coordinator then creates and commits one consolidated implementation route. Its body binds unique `Implementation binding ID: 523e6be9-609b-4b2b-b43f-0b2139d282b3`, the umbrella design commit, these two plan paths, the Opus handoff path/commit/blob, exact Stage-D report path/commit and GO, terminal join packet and `done_evidence`, integrated Opus head, `Implementation base: <full parent SHA>`, the exact bridge file allowlist, owner, tests, stop conditions, and zero provider/target actions. The route commit must be a one-parent commit whose parent is that implementation base. Before editing, the owner runs:

```bash
set -euo pipefail
PIPELINE_ROOT=/Users/hyungkoookkim/Pipeline
cd "$PIPELINE_ROOT"
ROUTE_OUTPUT="$(env -u GIT_INDEX_FILE "$PIPELINE_ROOT/.venv/bin/python" scripts/ledger_start_guard.py --seat coordinator --wave 2)"
IMPLEMENTATION_ROUTE="$(printf '%s\n' "$ROUTE_OUTPUT" | sed -n 's/^Active route: //p')"
test -n "$IMPLEMENTATION_ROUTE"
env -u GIT_INDEX_FILE "$PIPELINE_ROOT/.venv/bin/python" scripts/protocol_capacity_board.py --wave 2 --validate-route "$IMPLEMENTATION_ROUTE"
IMPLEMENTATION_ROUTE_COMMIT="$(env -u GIT_INDEX_FILE git -C "$PIPELINE_ROOT" log -1 --format=%H -- "$IMPLEMENTATION_ROUTE")"
BRIDGE_IMPLEMENTATION_BASE="$(env -u GIT_INDEX_FILE git -C "$PIPELINE_ROOT" show "$IMPLEMENTATION_ROUTE_COMMIT:$IMPLEMENTATION_ROUTE" | sed -n 's/^Implementation base: //p')"
test "$(env -u GIT_INDEX_FILE git -C "$PIPELINE_ROOT" rev-parse "$IMPLEMENTATION_ROUTE_COMMIT^")" = "$BRIDGE_IMPLEMENTATION_BASE"
test "$(env -u GIT_INDEX_FILE git -C "$PIPELINE_ROOT" rev-parse HEAD)" = "$IMPLEMENTATION_ROUTE_COMMIT"
```

The route parser must resolve every Opus binding from the exact committed route bytes and revalidate it against the committed handoff/report/join objects. Any missing/duplicate field, non-active route, dirty in-scope path, changed HEAD, or Opus-binding drift blocks Task 1. The exact `BRIDGE_IMPLEMENTATION_BASE` is carried through every task commit and the final Lane-V descriptor; it is never inferred later from ambient history.

- [ ] **Step 2: Write RED schema and canonicalization tests**

Test duplicate/unknown keys, uppercase or abbreviated SHAs, malformed digests, noncanonical paths, symlink-sensitive roots, duplicate arrays, unsupported repository/remote/profile, out-of-family allowlists, and every missing scope/route/consent/token field. Pin these sequence and authorization rules:

```python
def test_question_sequence_contract_is_monotonic() -> None:
    assert _scope("design-time", 1).question_id == "design-time/1"
    assert _scope("actual-diff", 2).question_id == "actual-diff/2"
    assert _scope("actual-diff", 3).question_id == "actual-diff/3"
    with pytest.raises(target.TargetReviewContractError, match="question_sequence_mismatch"):
        _scope("design-time", 2)


def test_each_question_requires_distinct_consent_and_complete_token() -> None:
    design = _authorization(_scope("design-time", 1))
    actual = _authorization(_scope("actual-diff", 2))
    assert design.user_consent != actual.user_consent
    assert set(actual.token_fields) == target.REQUIRED_TOKEN_FIELDS


def test_authority_chain_is_acyclic() -> None:
    scope, route, consent, token = _committed_authority_chain()
    assert route.bound_scope == scope.reference
    assert consent.bound_inputs == (scope.reference, route.reference)
    assert token.bound_inputs == (scope.reference, route.reference, consent.reference)
    assert token.side_effect_id == route.side_effect_id
    assert "token-reference" not in token.token_fields["allowed_command_class"]
    assert "consent" not in scope.to_mapping()
    assert "executor_token" not in scope.to_mapping()
```

The required Side-Effect Executor Token fields are exactly `side_effect_id`, `executor`, `target`, `allowed_command_class`, `preflight`, `stop_if_newer_mail_or_live_target_satisfied`, `postcheck`, `observer_seats`, `final_closeout_owner`, and `non_goals`. The route predeclares one UUID `side_effect_id`. Despite the historical field name, `allowed_command_class` contains the one exact argv literal for `opus_target_review_bridge.py review` with the already committed scope/route/consent references and `--side-effect-id <that UUID>`; it is not a category, regex, shell expansion, or prose description. It cannot contain a token reference, which would self-hash the token. The bridge resolves exactly one later committed token by that ID and binds its path/commit/blob/digest into CAS. The token names one executor and grants no edit, retry, credential, API, browser, push, or downstream authority.

- [ ] **Step 3: Implement exact immutable value objects**

Use these public shapes; nested `from_mapping()` methods require exact key sets:

```python
@dataclass(frozen=True)
class GitBlobBinding:
    repository: str
    commit: str
    path: str
    blob_oid: str
    sha256: str


@dataclass(frozen=True)
class ScopePreparationRouteBinding:
    blob: GitBlobBinding
    wave: int
    event_type: str
    review_family_id: str
    question_id: str
    scope_path: str
    scope_sha256: str
    provider_attempts_authorized: int


@dataclass(frozen=True)
class CommittedRouteBinding:
    blob: GitBlobBinding
    wave: int
    event_type: str
    review_family_id: str
    question_id: str
    scope_digest: str
    side_effect_id: str


@dataclass(frozen=True)
class AttemptAuthorizationBundle:
    bound_scope: GitBlobBinding
    scope_preparation_route: ScopePreparationRouteBinding
    attempt_route: CommittedRouteBinding
    user_consent: GitBlobBinding
    executor_token: GitBlobBinding
    consent_id: str
    side_effect_id: str
    token_fields: Mapping[str, object]


@dataclass(frozen=True)
class TargetReviewScope:
    task_id: str
    review_family_id: str
    family_invariants_sha256: str
    question_kind: str
    challenge_sequence: int
    prior_receipt_id: str | None
    prior_scope_digest: str | None
    receipt_namespace: str
    review_profile: str
    pipeline: PipelineBinding
    target: TargetBinding
    source_closure: tuple[GitBlobBinding, ...]
    pipeline_requirements: tuple[GitBlobBinding, ...]
    runtime_manifest_sha256: str
    verification_commands: tuple[str, ...]
    prompt_authority: GitBlobBinding

    @property
    def question_id(self) -> str:
        return f"{self.question_kind}/{self.challenge_sequence}"
```

`ScopePreparationRouteBinding.from_mapping()` requires `provider_attempts_authorized == 0` and has no side-effect ID. `CommittedRouteBinding` is the later attempt route and requires one UUID side-effect ID. `family_invariants_sha256` canonically binds repository/remote/root/Gitdir/common-dir, cumulative/correction bases, target allowlist, receipt namespace, target policy/profile, prompt authority, and non-data rule. It excludes per-question task/scope, routes, consent, token, head, prior receipt, and sequence. Sequence 1 has null prior fields; each later sequence names the exact preceding receipt and scope digest. `render_target_scope_bytes()` produces canonical bytes and digest without writing the protocol path. `TargetReviewScope` contains no route, consent, or token reference. `AttemptAuthorizationBundle` is assembled from the earlier preparation route, committed scope, and three later attempt-authority blobs.

- [ ] **Step 4: Run Task 1 GREEN and commit only its files**

```bash
set -euo pipefail
PIPELINE_ROOT=/Users/hyungkoookkim/Pipeline
cd "$PIPELINE_ROOT"
env -u GIT_INDEX_FILE "$PIPELINE_ROOT/.venv/bin/python" -m pytest tests/unit/test_opus_target_review_bridge.py -q
env -u GIT_INDEX_FILE git -C "$PIPELINE_ROOT" diff --check
env -u GIT_INDEX_FILE git -C "$PIPELINE_ROOT" add -- scripts/opus_target_review_bridge.py tests/unit/test_opus_target_review_bridge.py
env -u GIT_INDEX_FILE git -C "$PIPELINE_ROOT" commit -m "feat(opus): define target review authority contract" -- scripts/opus_target_review_bridge.py tests/unit/test_opus_target_review_bridge.py
```

### Task 2: Resolve both repositories and build the sealed dependency closure

**Files:**
- Modify: `scripts/opus_target_review_bridge.py`
- Modify: `tests/unit/test_opus_target_review_bridge.py`

**Interfaces:**
- Consumes: exact committed scope, attempt-route, and consent references plus the route-predeclared side-effect ID; resolves exactly one later committed executor token in strict ancestry order.
- Produces: `ResolvedTargetReview`, `SealedFile`, `SealedRuntimeManifest`, `SealedSnapshotProvenance`, `resolve_target_scope()`, `seal_evidence_ledger_snapshot()`, and target receipt-state helpers.

- [ ] **Step 1: Write RED identity, active-route, closure, and exclusion tests**

Create synthetic Pipeline and linked-target repositories. Mutate one fact at a time: scope commit/blob/digest, route commit/blob/digest, Wave, active route, family/question/scope line, consent, token field/executor/command, roots, remote, Gitdir/common-dir, ancestry, allowed paths, requirement blob, target source blob, runtime file, prior chain, or family invariant. Every mismatch must occur before state-root creation and provider construction:

```python
with pytest.raises(target.TargetReviewContractError):
    target.resolve_target_scope(
        pipeline_root,
        scope_reference,
        route_reference,
        consent_reference,
        side_effect_id,
    )
assert not target.target_receipt_state_root(pipeline_root).exists()
assert provider_calls == 0
```

Add live-root sentinels under both `.git` directories, `data/`, `resources/`, `.superpowers/`, workbook/database names, target WIP, and the live venv. Successful snapshot tests prove none is present or readable from the provider/verification sandbox.

- [ ] **Step 2: Implement hostile-environment Git resolution**

Every Git child uses `/usr/bin/git --no-replace-objects --literal-pathspecs`, an explicit `cwd`, and a positive environment containing only fixed `PATH`, `LANG`, `LC_ALL`, and private `HOME`/`XDG_CONFIG_HOME`. Never resolve a committed blob from ambient `HEAD`; parse its exact commit, verify `ls-tree` gives its bound OID, then hash `cat-file blob` bytes.

`resolve_target_scope(pipeline_root, scope_reference, route_reference, consent_reference, side_effect_id)` must:

1. resolve and validate the exact committed scope blob;
2. resolve the later committed attempt-route blob and require it binds the exact scope path+commit+blob+digest, family/question, and an exact earlier scope-preparation route; resolve that preparation route and require it predates the scope commit and binds the scope path plus canonical byte digest while authorizing zero provider attempts;
3. run the Wave-2 capacity validator and the same active-route selector used by `ledger_start_guard.py`, requiring the bound path to be current;
4. validate route family, question, scope digest, named executor, stop conditions, and zero inherited authority;
5. resolve a still-later non-route `decision` event that records authenticated explicit user consent and binds exact scope+attempt route, then locate exactly one still-later non-route `decision` token artifact whose exact `side_effect_id` was predeclared by the attempt route and whose body binds scope+attempt route+consent; capture its canonical path/introduction commit/blob/digest, require strict ancestry `preparation route < scope < attempt route < consent < token`, and reject duplicates, later modifications, backward/descendant references, or self-reference;
6. verify current Pipeline/target identities, clean relevant paths, fixed bases, ancestry, reviewed head, and allowlist;
7. for sequence greater than 1, load exactly the prior receipt and require state `reconciled`, outcome `pass|issues` rather than `unavailable`, same family invariants, exact previous sequence, and distinct task/scope/consent/token/route.

No directory scan may substitute for an exact prior receipt ID.

- [ ] **Step 3: Materialize a content-addressed sealed closure**

Define:

```python
@dataclass(frozen=True)
class SealedFile:
    logical_path: str
    source_kind: str
    blob_oid: str | None
    sha256: str
    size_bytes: int
    mode: int


@dataclass(frozen=True)
class SealedSnapshotProvenance:
    policy_id: str
    repository_identity: str
    reviewed_head: str
    closure_digest: str
    runtime_digest: str
    files: tuple[SealedFile, ...]
    snapshot_root: Path
```

The target source closure is every tracked `recommendation/**/*.py` blob at the bound reviewed head, enumerated and content-addressed in the scope. Static selected Pipeline requirements are the umbrella design, binding hold, both binding FAIL reports, both committed plans, and policy prompt authority. At resolution, append the exact scope-preparation route, attempt route, consent, and token blobs from the validated acyclic authorization bundle. Materialize them below `requirements/pipeline/` and target blobs below `src/`. There is no checkout, clone, pre-existing `.git`, symlink, socket, device, FIFO, mutable WIP read, or pathname copied from a live root.

`seal_evidence_ledger_snapshot()` is a context manager and owns the entire target materialization exactly once. In one private mutable staging root it writes committed source/requirements, then builds `src/.review-runtime/` by resolving and copying regular files for the exact Python executable, standard-library closure, and `pytest`, `psycopg`, plus their declared transitive distributions. It resolves symlinks before copying, rejects special files, hashes every copied byte, records mode/size, and never symlinks a live `.venv`. Only after source, requirements, and runtime are complete does it re-open/hash every file, chmod the whole closure read-only, compute final runtime/closure digests, and yield immutable `SealedSnapshotProvenance`. The snapshot remains alive through validation, sandbox, verification, provider execution, and parsing, then the context manager removes its private root after exit. There is no later runtime installation step and no provenance object describing a partial or already-deleted tree. OS kernel and signed system-library roots are sandbox baseline dependencies, not review inputs; document and test that limitation.

Reopen every sealed file by descriptor, re-hash it, ensure it remains below the private snapshot root, then compute one canonical closure digest. Delete the incomplete snapshot on pre-provider validation failure; after provider reservation, receipt terminalization rules govern failure.

- [ ] **Step 4: Fix and test the Pipeline-common-dir receipt root**

```python
def target_receipt_state_root(pipeline_root: Path) -> Path:
    common = git_stdout(pipeline_root, "rev-parse", "--path-format=absolute", "--git-common-dir")
    return Path(common).resolve().parent / ".codex/runtime/opus-target-review-receipts/v1"
```

Tests must assert `not target.target_receipt_state_root(pipeline_root).exists()` after every pre-reservation failure. The old `pipeline_root.parent` assertion is forbidden because it points at the wrong namespace.

- [ ] **Step 5: Run Task 2 GREEN and commit**

```bash
set -euo pipefail
PIPELINE_ROOT=/Users/hyungkoookkim/Pipeline
cd "$PIPELINE_ROOT"
env -u GIT_INDEX_FILE "$PIPELINE_ROOT/.venv/bin/python" -m pytest tests/unit/test_opus_target_review_bridge.py -k 'resolve or route or consent or token or closure or sandbox or state_root' -q
env -u GIT_INDEX_FILE git -C "$PIPELINE_ROOT" diff --check
env -u GIT_INDEX_FILE git -C "$PIPELINE_ROOT" add -- scripts/opus_target_review_bridge.py tests/unit/test_opus_target_review_bridge.py
env -u GIT_INDEX_FILE git -C "$PIPELINE_ROOT" commit -m "feat(opus): seal target review closure" -- scripts/opus_target_review_bridge.py tests/unit/test_opus_target_review_bridge.py
```

### Task 3: Introduce the default-preserving `TargetReviewPolicy` seam

**Files:**
- Modify: `scripts/opus_review_bridge.py`
- Modify: `scripts/opus_target_review_bridge.py`
- Modify: `tests/unit/test_opus_review_bridge.py`
- Modify: `tests/unit/test_opus_target_review_bridge.py`

**Interfaces:**
- Consumes: existing Pipeline `_ProviderReviewRequest` or resolved target request.
- Produces: `TargetReviewPolicy`, `PIPELINE_REVIEW_POLICY`, `EVIDENCE_LEDGER_TARGET_POLICY`, exact verification grammar, target schema/parser/unavailable factory, and target sandbox/runtime adapters.

- [ ] **Step 1: Write RED default-equivalence and target-policy tests**

Capture the current Pipeline request’s source validation, snapshot tree, prompt bytes, JSON schema bytes, command argv, verification parsing, sandbox profile, parsed result, and every unavailable failure stage. After the seam, an omitted policy must be byte-for-byte identical. Target tests must prove no Pipeline validator/parser/verification grammar or live-venv installation path is invoked. Add pre-provider negatives for request/profile mismatch and returned provenance/policy-ID mismatch; both must launch zero provider commands, and profile mismatch must occur before snapshot construction.

- [ ] **Step 2: Add the exact policy contract**

Use a generic structural provenance contract so `opus_review_bridge.py` never imports the target adapter and cannot form an import cycle. The target `SealedSnapshotProvenance` and a small generic `PipelineSnapshotProvenance` both satisfy it. Use precise callable aliases, not variadic callbacks:

```python
@runtime_checkable
class SnapshotProvenance(Protocol):
    policy_id: str
    snapshot_root: Path
    closure_digest: str


SourceRootResolver = Callable[[_ProviderReviewRequest], Path]
SnapshotBuilder = Callable[[_ProviderReviewRequest, Path], ContextManager[SnapshotProvenance]]
SnapshotValidator = Callable[[_ProviderReviewRequest, SnapshotProvenance], None]
RuntimeValidator = Callable[[_ProviderReviewRequest, SnapshotProvenance], None]
VerificationParser = Callable[[_ProviderReviewRequest, SnapshotProvenance, str], tuple[str, ...]]
SandboxFactory = Callable[[Path, SnapshotProvenance], ContextManager[SandboxRuntime]]
PromptBuilder = Callable[[_ProviderReviewRequest, SnapshotProvenance], str]
SchemaBuilder = Callable[[_ProviderReviewRequest, SnapshotProvenance], Mapping[str, object]]
ReviewParser = Callable[[Mapping[str, object], _ProviderReviewRequest, SnapshotProvenance], OpusReview]
UnavailableFactory = Callable[[_ProviderReviewRequest, str, str], OpusReview]


@dataclass(frozen=True)
class TargetReviewPolicy:
    policy_id: str
    review_profile: str
    source_root: SourceRootResolver
    build_snapshot: SnapshotBuilder
    validate_snapshot: SnapshotValidator
    validate_runtime: RuntimeValidator
    parse_verification: VerificationParser
    sandbox: SandboxFactory
    build_prompt: PromptBuilder
    build_schema: SchemaBuilder
    parse_review: ReviewParser
    unavailable_review: UnavailableFactory
```

`_perform_provider_review(..., policy: TargetReviewPolicy = PIPELINE_REVIEW_POLICY)` first requires `request.review_profile == policy.review_profile` before source resolution or snapshot construction. It then uses this fixed lifetime: resolve source, then `with policy.build_snapshot(request, temporary_parent) as provenance:` immediately require `provenance.policy_id == policy.policy_id`, validate snapshot/runtime, parse verification argv, enter sandbox, invoke provider/parser, and leave the context only after the terminal review object exists. `PIPELINE_REVIEW_POLICY.build_snapshot` is a wrapper context manager around the current `_immutable_review_snapshot`; while that existing context is open it computes/yields final Pipeline provenance. The current function still installs runtime exactly once, and `validate_runtime` only validates it. The target context manager performs the one target runtime copy described in Task 2 and its validator never mutates. Tests assert snapshot existence through parsing and deletion only after context exit. The generic module defines the protocol and Pipeline wrapper only; it never imports `opus_target_review_bridge`. Do not retain an ad-hoc `repository_validator`, `task_prompt`, `output_schema`, second runtime-install bypass, or returned path whose owner context has exited.

- [ ] **Step 3: Implement the finite target verification grammar and runtime**

The target policy accepts only argv-equivalent commands with this exact fixed prefix:

```text
env -u GIT_INDEX_FILE PYTHONNOUSERSITE=1 PYTEST_DISABLE_PLUGIN_AUTOLOAD=1 .review-runtime/bin/python -m pytest -p no:cacheprovider
```

The only path operands are `recommendation/tests/test_cli.py` or `recommendation/tests`; optional `-k` values must be one member of a committed finite selector set; the final token is `-q`. Reject absolute paths, `..`, `-c`, `@`, extra `-p`, config/override options, environment substitution, shell metacharacters, redirections, and unrecognized tokens. Execute parsed argv directly without a shell, with `cwd=<sealed-root>/src` and a positive environment.

The target sandbox exposes read-only sealed `src/`, `requirements/`, `src/.review-runtime/`, provider scratch/broker endpoints, required signed OS runtime roots, `/usr/bin/git`, and one fresh writable snapshot-private scratch root exported as `TMPDIR`. It denies network and the original Pipeline root, evidence-ledger root/common-dir/Gitdir, every pre-existing `.git`, receipt state, `data/`, `resources/`, `.superpowers/`, `*.xlsx`, database files, DSNs, credentials, sockets, and user configuration. `test_cli.py` may create synthetic repositories, including ephemeral `.git` directories, only below that empty scratch root; the sandbox denies traversal or symlink escape from it and destroys it after verification. Sentinel tests attempt live/pre-existing Git reads and scratch escape at the last broker boundary and require refusal.

- [ ] **Step 4: Implement target schema, parser, and unavailable behavior**

The provider schema permits only `pass|issues`; it requires exact `review_profile`, `review_family_id`, `question_id`, task ID, base/head, scope digest, route digest, and sealed closure digest. The target parser validates each field before constructing `OpusReview`. Provider output cannot claim `unavailable`, GO, NITS, FAIL, authority, or reconciliation.

Every transport, timeout, sandbox, broker, output-limit, malformed-output, and model-validation failure calls `policy.unavailable_review(request, enumerated_reason, failure_stage)`. The target unavailable factory preserves the target profile and all expected bindings. No generic Pipeline unavailable object may leak into a target receipt.

- [ ] **Step 5: Run Task 3 GREEN and commit**

```bash
set -euo pipefail
PIPELINE_ROOT=/Users/hyungkoookkim/Pipeline
cd "$PIPELINE_ROOT"
env -u GIT_INDEX_FILE "$PIPELINE_ROOT/.venv/bin/python" -m pytest tests/unit/test_opus_review_bridge.py tests/unit/test_opus_target_review_bridge.py -q
env -u GIT_INDEX_FILE git -C "$PIPELINE_ROOT" diff --check
env -u GIT_INDEX_FILE git -C "$PIPELINE_ROOT" add -- scripts/opus_review_bridge.py scripts/opus_target_review_bridge.py tests/unit/test_opus_review_bridge.py tests/unit/test_opus_target_review_bridge.py
env -u GIT_INDEX_FILE git -C "$PIPELINE_ROOT" commit -m "feat(opus): add sealed target review policy" -- scripts/opus_review_bridge.py scripts/opus_target_review_bridge.py tests/unit/test_opus_review_bridge.py tests/unit/test_opus_target_review_bridge.py
```

### Task 4: Enforce CAS attempt identity and route-bound advisory reconciliation

**Files:**
- Modify: `scripts/opus_review_receipts.py`
- Modify: `scripts/opus_target_review_bridge.py`
- Modify: `tests/unit/test_opus_review_receipts.py`
- Modify: `tests/unit/test_opus_target_review_bridge.py`

**Interfaces:**
- Consumes: resolved question, exact attempt route/consent/token, terminal review, and exact committed reconciliation route.
- Produces: `compute_target_attempt_key()`, target reservation identity, `TargetReviewResult`, `TargetEvidenceReference`, `TargetFindingDisposition`, `TargetReconciliationResult`, `review_target()`, and `reconcile_target()`.

- [ ] **Step 1: Write RED CAS, consent-race, replay, and reconciliation tests**

Cover concurrent exact replay, same family/question/sequence with a different task or scope, stale active route after resolution, consent/token replacement, abandoned reservation, provider exception, malformed/unavailable result, prior receipt not reconciled, skipped sequence, reconciliation replay/conflict, and a route changed after lookup. Assert one fake provider call for exact concurrency and zero for every mismatch.

- [ ] **Step 2: Add target CAS identity without changing generic defaults**

```python
def compute_target_attempt_key(scope: TargetReviewScope) -> str:
    material = {
        "schema": "target-attempt-key/v1",
        "review_family_id": scope.review_family_id,
        "question_kind": scope.question_kind,
        "challenge_sequence": scope.challenge_sequence,
    }
    return "ota1:" + hashlib.sha256(canonical_json_bytes(material)).hexdigest()
```

Allow `ReceiptStore.lock_attempt()` to accept an explicit attempt key plus reservation identity; omission uses the current generic key and behavior. A target reservation persists exact task ID, scope digest, scope-preparation-route blob/digest, attempt-route blob/digest, consent blob/digest, token blob/digest, family-invariants digest, and sealed-closure digest. An existing key with identical identity returns the terminal record. Any differing identity is `attempt_identity_conflict`; it is never cached success and never launches a provider.

Immediately before reservation and again immediately before provider construction, refresh current HEAD/mail, Wave-2 active route, scope/route/consent/token blobs and strict ancestry, authenticated explicit-consent correlation, token executor/command/preflight/stop/postcheck, target head, and relevant clean paths. The consent/token artifacts are the only permitted post-route mailbox successors; any other newer mail after the route, or any mail after the token, triggers the token’s stop condition. They are non-route events, so the bound attempt route must remain the active route. A change terminalizes or blocks according to whether reservation has begun; it never substitutes authority.

- [ ] **Step 3: Implement finite, committed reconciliation**

`reconcile_target()` has this signature only:

```python
def reconcile_target(
    pipeline_root: Path,
    receipt_id: str,
    route_reference: str,
) -> TargetReconciliationResult:
    ...
```

Resolve `route_reference` as an exact committed path+commit+blob+digest. Require Wave 2, current active route, canonical sent-mailbox path, one reconciliation event, matching family/question/receipt/scope/closure digest, and exactly one canonical disposition mapping. The route must be fresh for this reconciliation and distinct from the attempt route.

Each evidence value is a structured `TargetEvidenceReference` from this finite grammar only:

- `target-commit`: full target commit plus allowlisted repository path;
- `pipeline-commit`: full Pipeline commit plus committed requirement/test path;
- `pytest`: full target commit plus canonical test node ID from the sealed suite;
- `operator-report`: full Pipeline commit plus canonical sent-mailbox verification-report path;
- `scope`: exact `sha256:` scope or closure digest.

Reject free text, URLs, absolute paths, shell text, uncommitted paths, unknown kinds, and evidence whose Git blob/test identity cannot be resolved. Require one `adopted|modified|rejected|unresolved` disposition per stored issue; `pass|unavailable` requires an empty mapping. Bind reconciliation route path, commit, blob OID, byte digest, canonical mapping digest, and result into the receipt CAS. No reconciliation field may carry a protocol verdict or grant authority.

- [ ] **Step 4: Require reconciled prior questions and monotonic continuation**

For sequence `N > 1`, require the exact same-family receipt at `N-1` to be `reconciled`, its outcome to be `pass|issues` rather than `unavailable`, and family invariants unchanged. If an `actual-diff/N` issue requires a code change, the next lawful question is `actual-diff/N+1` after a new additive commit, fresh route, distinct explicit consent, complete new token, unique task/scope, and reconciliation of `N`. If allowlist/base/policy/authority/design assumptions change, close the family and start a newly authorized `design-time/1`.

- [ ] **Step 5: Run Task 4 GREEN and commit**

```bash
set -euo pipefail
PIPELINE_ROOT=/Users/hyungkoookkim/Pipeline
cd "$PIPELINE_ROOT"
env -u GIT_INDEX_FILE "$PIPELINE_ROOT/.venv/bin/python" -m pytest tests/unit/test_opus_review_receipts.py tests/unit/test_opus_target_review_bridge.py -q
env -u GIT_INDEX_FILE git -C "$PIPELINE_ROOT" diff --check
env -u GIT_INDEX_FILE git -C "$PIPELINE_ROOT" add -- scripts/opus_review_receipts.py scripts/opus_target_review_bridge.py tests/unit/test_opus_review_receipts.py tests/unit/test_opus_target_review_bridge.py
env -u GIT_INDEX_FILE git -C "$PIPELINE_ROOT" commit -m "feat(opus): bind target advisory CAS" -- scripts/opus_review_receipts.py scripts/opus_target_review_bridge.py tests/unit/test_opus_review_receipts.py tests/unit/test_opus_target_review_bridge.py
```

### Task 5: Add the fail-closed CLI, prompt pins, and operative documentation

**Files:**
- Modify: `scripts/opus_target_review_bridge.py`
- Modify: `tests/unit/test_opus_target_review_bridge.py`
- Modify: `tests/unit/test_protocol_prompt_sync.py`
- Modify: `docs/protocol/codex/ledger-cli-adoption.md`
- Modify: `ARCHITECTURE.md`

- [ ] **Step 1: Pin exact CLI grammar and authority-negative prompts**

The only production forms are:

```text
opus_target_review_bridge.py review --pipeline-root /Users/hyungkoookkim/Pipeline --scope-reference COMMITTED_SCOPE_REFERENCE --route-reference COMMITTED_ATTEMPT_ROUTE_REFERENCE --consent-reference COMMITTED_CONSENT_REFERENCE --side-effect-id ROUTE_PREDECLARED_SIDE_EFFECT_ID
opus_target_review_bridge.py reconcile --pipeline-root /Users/hyungkoookkim/Pipeline --receipt-id EXACT_RECEIPT_ID --route-reference COMMITTED_RECONCILIATION_ROUTE_REFERENCE
```

Here the three review reference arguments and reconciliation route reference use the exact path+commit+blob+digest grammar from Task 1 and are values captured from committed Git objects, not literal placeholder input. `ROUTE_PREDECLARED_SIDE_EFFECT_ID` is the exact UUID already in the route; it lets the bridge resolve the unique later token without making that token refer to its own digest. The CLI does not permit authorization contents to be overridden. Reject caller-supplied target root, base/head, allowlist, command, prompt, policy, parser, provider, token path/reference, state root, disposition/evidence text, response import, retry, seat, verdict, or controller options.

Rendered prompt tests require exact family/question/base/head/scope/route/closure identities and these sentences:

```text
Independent target-aware evidence review; advisory evidence only.
You are not a Pipeline or evidence-ledger seat, controller, committer, verifier of record, or side-effect executor.
Do not issue GO, NITS, FAIL, authorize a lock release, write either repository, or infer access to excluded business data.
Receipt presence proves one attempt only; the Pipeline Operator owns the cumulative verdict.
```

- [ ] **Step 2: Document sequencing and architecture**

Document: guard and active route; exact committed scope; distinct explicit user consent plus complete token; design receipt and committed reconciliation before edits; controller commit; monotonic actual-diff question and reconciliation; then independent Operator verdict. Document that generic Lane-V authority cannot be fabricated for evidence-ledger and that a real attempt always needs fresh user consent even when the family already exists.

Update `ARCHITECTURE.md` with the policy seam, sealed closure, target state namespace, CAS identity, route-bound reconciliation, and advisory-only boundary. Refresh its verification footer and shifted anchors.

- [ ] **Step 3: Run full provider-free verification and commit**

```bash
set -euo pipefail
PIPELINE_ROOT=/Users/hyungkoookkim/Pipeline
cd "$PIPELINE_ROOT"
env -u GIT_INDEX_FILE "$PIPELINE_ROOT/.venv/bin/python" -m pytest tests/unit/test_opus_target_review_bridge.py tests/unit/test_opus_review_bridge.py tests/unit/test_opus_review_receipts.py tests/unit/test_protocol_prompt_sync.py -q
env -u GIT_INDEX_FILE "$PIPELINE_ROOT/.venv/bin/python" scripts/check_doc_claims.py ARCHITECTURE.md
env -u GIT_INDEX_FILE "$PIPELINE_ROOT/.venv/bin/python" scripts/ci_smoke.py
env -u GIT_INDEX_FILE git -C "$PIPELINE_ROOT" diff --check
env -u GIT_INDEX_FILE git -C "$PIPELINE_ROOT" add -- scripts/opus_target_review_bridge.py tests/unit/test_opus_target_review_bridge.py tests/unit/test_protocol_prompt_sync.py docs/protocol/codex/ledger-cli-adoption.md ARCHITECTURE.md
env -u GIT_INDEX_FILE git -C "$PIPELINE_ROOT" commit -m "docs(opus): bind target advisory workflow" -- scripts/opus_target_review_bridge.py tests/unit/test_opus_target_review_bridge.py tests/unit/test_protocol_prompt_sync.py docs/protocol/codex/ledger-cli-adoption.md ARCHITECTURE.md
```

### Task 6: Obtain independent Pipeline verification and freeze the exact handoff

**Files:**
- Create during routed execution: `coordination/verification/scopes/523e6be9-609b-4b2b-b43f-0b2139d282b3.json`
- Create during routed execution: one canonical verify-request event.
- Create during verification: one canonical Operator verification-report event.
- Create after GO: `docs/HANDOFF-target-aware-evidence-ledger-opus-bridge-2026-07-16.md`

- [ ] **Step 1: Freeze and validate the exact implementation range**

Re-resolve the unique Task-1 implementation route from its committed binding ID, capture its path/commit/blob/digest, re-read `BRIDGE_IMPLEMENTATION_BASE`, and verify the route commit parent plus current ancestry before setting the reviewed base. Separately freeze `BRIDGE_REVIEWED_HEAD` from the finished task commits. Require the exact range contains only the bridge plan’s allowlist and the worktree has no in-scope changes. The strict Lane-V descriptor embeds the literal reviewed base, requirements, changed roots, and commands; it does **not** contain `reviewed_head`. Commit only the descriptor, capture `BRIDGE_SCOPE_COMMIT`, then resolve its blob OID and digest from that exact commit. The later verify-request carries the frozen reviewed head and must validate the exact base..head range.

```bash
set -euo pipefail
PIPELINE_ROOT=/Users/hyungkoookkim/Pipeline
cd "$PIPELINE_ROOT"
IMPLEMENTATION_ROUTE_MATCHES="$(env -u GIT_INDEX_FILE git -C "$PIPELINE_ROOT" grep -l -F 'Implementation binding ID: 523e6be9-609b-4b2b-b43f-0b2139d282b3' HEAD -- coordination/mailbox/sent | sed -n 's/^HEAD://p')"
test "$(printf '%s\n' "$IMPLEMENTATION_ROUTE_MATCHES" | sed '/^$/d' | wc -l | tr -d ' ')" = 1
IMPLEMENTATION_ROUTE="$IMPLEMENTATION_ROUTE_MATCHES"
IMPLEMENTATION_ROUTE_COMMIT="$(env -u GIT_INDEX_FILE git -C "$PIPELINE_ROOT" log -1 --format=%H -- "$IMPLEMENTATION_ROUTE")"
IMPLEMENTATION_ROUTE_BLOB="$(env -u GIT_INDEX_FILE git -C "$PIPELINE_ROOT" rev-parse "$IMPLEMENTATION_ROUTE_COMMIT:$IMPLEMENTATION_ROUTE")"
IMPLEMENTATION_ROUTE_DIGEST="$(env -u GIT_INDEX_FILE git -C "$PIPELINE_ROOT" cat-file blob "$IMPLEMENTATION_ROUTE_BLOB" | "$PIPELINE_ROOT/.venv/bin/python" -c 'import hashlib,sys; print(hashlib.sha256(sys.stdin.buffer.read()).hexdigest())')"
BRIDGE_IMPLEMENTATION_BASE="$(env -u GIT_INDEX_FILE git -C "$PIPELINE_ROOT" show "$IMPLEMENTATION_ROUTE_COMMIT:$IMPLEMENTATION_ROUTE" | sed -n 's/^Implementation base: //p')"
test -n "$BRIDGE_IMPLEMENTATION_BASE"
test "$(env -u GIT_INDEX_FILE git -C "$PIPELINE_ROOT" rev-parse "$IMPLEMENTATION_ROUTE_COMMIT^")" = "$BRIDGE_IMPLEMENTATION_BASE"
BRIDGE_REVIEWED_BASE="$BRIDGE_IMPLEMENTATION_BASE"
BRIDGE_REVIEWED_HEAD="$(env -u GIT_INDEX_FILE git -C "$PIPELINE_ROOT" rev-parse HEAD)"
env -u GIT_INDEX_FILE git -C "$PIPELINE_ROOT" merge-base --is-ancestor "$IMPLEMENTATION_ROUTE_COMMIT" "$BRIDGE_REVIEWED_HEAD"
env -u GIT_INDEX_FILE git -C "$PIPELINE_ROOT" merge-base --is-ancestor "$BRIDGE_REVIEWED_BASE" "$BRIDGE_REVIEWED_HEAD"
BRIDGE_SCOPE_PATH=coordination/verification/scopes/523e6be9-609b-4b2b-b43f-0b2139d282b3.json
env -u GIT_INDEX_FILE git -C "$PIPELINE_ROOT" add -- "$BRIDGE_SCOPE_PATH"
env -u GIT_INDEX_FILE git -C "$PIPELINE_ROOT" commit -m "docs(verify): bind target bridge Lane V scope" -- "$BRIDGE_SCOPE_PATH"
BRIDGE_SCOPE_COMMIT="$(env -u GIT_INDEX_FILE git -C "$PIPELINE_ROOT" rev-parse HEAD)"
test "$(env -u GIT_INDEX_FILE git -C "$PIPELINE_ROOT" diff-tree --no-commit-id --name-only -r "$BRIDGE_SCOPE_COMMIT")" = "$BRIDGE_SCOPE_PATH"
BRIDGE_SCOPE_BLOB="$(env -u GIT_INDEX_FILE git -C "$PIPELINE_ROOT" rev-parse "$BRIDGE_SCOPE_COMMIT:$BRIDGE_SCOPE_PATH")"
BRIDGE_SCOPE_DIGEST="$(env -u GIT_INDEX_FILE git -C "$PIPELINE_ROOT" cat-file blob "$BRIDGE_SCOPE_BLOB" | "$PIPELINE_ROOT/.venv/bin/python" -c 'import hashlib,sys; print(hashlib.sha256(sys.stdin.buffer.read()).hexdigest())')"
BRIDGE_SCOPE_REFERENCE="$BRIDGE_SCOPE_PATH@sha256:$BRIDGE_SCOPE_DIGEST"
```

The test-covered Lane-V descriptor loader must read `BRIDGE_SCOPE_PATH` from `BRIDGE_SCOPE_COMMIT`, confirm its Git blob equals `BRIDGE_SCOPE_BLOB`, and confirm its sole embedded reviewed-base field equals `BRIDGE_REVIEWED_BASE`. The verify-request validator separately requires `Reviewed head: $BRIDGE_REVIEWED_HEAD`, the same base, and exact range/scope agreement. `BRIDGE_SCOPE_REFERENCE` keeps the existing Lane-V grammar; `BRIDGE_SCOPE_COMMIT`, `BRIDGE_SCOPE_BLOB`, and frozen head are separately retained in the handoff rather than invented as new descriptor fields.

- [ ] **Step 2: Send and commit one exact verify request**

After the descriptor variables are frozen, the Director first runs this parent preflight:

```bash
set -euo pipefail
PIPELINE_ROOT=/Users/hyungkoookkim/Pipeline
BODY_ROOT="$PIPELINE_ROOT/.codex/runtime/protocol-bodies"
cd "$PIPELINE_ROOT"
if test -e "$BODY_ROOT" || test -L "$BODY_ROOT"; then
  test -d "$BODY_ROOT"
  test ! -L "$BODY_ROOT"
  test "$(stat -f %u "$BODY_ROOT")" = "$(id -u)"
  test "$(stat -f %Lp "$BODY_ROOT")" = 700
else
  install -d -m 700 "$BODY_ROOT"
fi
test ! -L "$BODY_ROOT"
test "$(stat -f %u "$BODY_ROOT")" = "$(id -u)"
test "$(stat -f %Lp "$BODY_ROOT")" = 700
```

The Director then creates the complete request body with `apply_patch` at `$PIPELINE_ROOT/.codex/runtime/protocol-bodies/523e6be9-609b-4b2b-b43f-0b2139d282b3-verify-request.md`. It contains literal full base/head/scope values, not shell placeholders, and passes the test-covered request parser before send.

```bash
set -euo pipefail
PIPELINE_ROOT=/Users/hyungkoookkim/Pipeline
cd "$PIPELINE_ROOT"
BODY_ROOT="$PIPELINE_ROOT/.codex/runtime/protocol-bodies"
VERIFY_REQUEST_BODY="$BODY_ROOT/523e6be9-609b-4b2b-b43f-0b2139d282b3-verify-request.md"
test -f "$VERIFY_REQUEST_BODY"
test ! -L "$VERIFY_REQUEST_BODY"
test "$(dirname "$(realpath "$VERIFY_REQUEST_BODY")")" = "$BODY_ROOT"
chmod 600 "$VERIFY_REQUEST_BODY"
VERIFY_REQUEST_BODY_DIGEST="$("$PIPELINE_ROOT/.venv/bin/python" -c 'import hashlib,pathlib,sys; print(hashlib.sha256(pathlib.Path(sys.argv[1]).read_bytes()).hexdigest())' "$VERIFY_REQUEST_BODY")"
REQUEST_SEND_OUTPUT="$(coordination/bin/send-event director operator verify-request "verify target-aware evidence-ledger Opus bridge" < "$VERIFY_REQUEST_BODY")"
BRIDGE_VERIFY_REQUEST_PATH="${REQUEST_SEND_OUTPUT#created }"
BRIDGE_VERIFY_REQUEST_PATH="${BRIDGE_VERIFY_REQUEST_PATH%% *}"
test -f "$BRIDGE_VERIFY_REQUEST_PATH"
env -u GIT_INDEX_FILE git -C "$PIPELINE_ROOT" add -f -- "$BRIDGE_VERIFY_REQUEST_PATH"
env -u GIT_INDEX_FILE git -C "$PIPELINE_ROOT" commit -m "docs(verify): request target bridge Lane V" -- "$BRIDGE_VERIFY_REQUEST_PATH"
BRIDGE_REQUEST_COMMIT="$(env -u GIT_INDEX_FILE git -C "$PIPELINE_ROOT" rev-parse HEAD)"
test "$(env -u GIT_INDEX_FILE git -C "$PIPELINE_ROOT" diff-tree --no-commit-id --name-only -r "$BRIDGE_REQUEST_COMMIT")" = "$BRIDGE_VERIFY_REQUEST_PATH"
```

The committed request carries exact base/head/scope reference and authorizes zero Opus process attempts and zero evidence-ledger edits.

- [ ] **Step 3: Operator verifies independently**

Operator reruns all Task-5 tests and smoke, validates descriptor/request law, mutates each source/route/consent/token/runtime/CAS binding, proves live-root sentinel denial, proves default Pipeline behavior byte-identical, and confirms both repositories/control-plane artifacts remain unchanged. GO/NITS/FAIL applies only to the bridge implementation.

- [ ] **Step 4: Capture the report from its producer, never ambient `HEAD`**

After verification, the Operator runs the same `install -d -m 700`, no-symlink, effective-UID, and mode-`0700` parent preflight from Step 2. The Operator then creates the final schema-valid body with `apply_patch` at `$PIPELINE_ROOT/.codex/runtime/protocol-bodies/523e6be9-609b-4b2b-b43f-0b2139d282b3-verification-report.md`. The body names the exact request path/commit, reviewed range, commands/results, and GO/NITS/FAIL. It is parsed before send.

```bash
set -euo pipefail
PIPELINE_ROOT=/Users/hyungkoookkim/Pipeline
cd "$PIPELINE_ROOT"
BODY_ROOT="$PIPELINE_ROOT/.codex/runtime/protocol-bodies"
VERIFICATION_REPORT_BODY="$BODY_ROOT/523e6be9-609b-4b2b-b43f-0b2139d282b3-verification-report.md"
test -f "$VERIFICATION_REPORT_BODY"
test ! -L "$VERIFICATION_REPORT_BODY"
test "$(dirname "$(realpath "$VERIFICATION_REPORT_BODY")")" = "$BODY_ROOT"
chmod 600 "$VERIFICATION_REPORT_BODY"
VERIFICATION_REPORT_BODY_DIGEST="$("$PIPELINE_ROOT/.venv/bin/python" -c 'import hashlib,pathlib,sys; print(hashlib.sha256(pathlib.Path(sys.argv[1]).read_bytes()).hexdigest())' "$VERIFICATION_REPORT_BODY")"
REPORT_SEND_OUTPUT="$(coordination/bin/send-event operator all verification-report "target-aware evidence-ledger Opus bridge verdict" < "$VERIFICATION_REPORT_BODY")"
BRIDGE_REPORT_PATH="${REPORT_SEND_OUTPUT#created }"
BRIDGE_REPORT_PATH="${BRIDGE_REPORT_PATH%% *}"
test -f "$BRIDGE_REPORT_PATH"
env -u GIT_INDEX_FILE git -C "$PIPELINE_ROOT" add -f -- "$BRIDGE_REPORT_PATH"
env -u GIT_INDEX_FILE git -C "$PIPELINE_ROOT" commit -m "docs(verify): report target bridge verdict" -- "$BRIDGE_REPORT_PATH"
BRIDGE_REPORT_COMMIT="$(env -u GIT_INDEX_FILE git -C "$PIPELINE_ROOT" rev-parse HEAD)"
test "$(env -u GIT_INDEX_FILE git -C "$PIPELINE_ROOT" diff-tree --no-commit-id --name-only -r "$BRIDGE_REPORT_COMMIT")" = "$BRIDGE_REPORT_PATH"
```

The handoff records `BRIDGE_REPORT_PATH` and `BRIDGE_REPORT_COMMIT`, both validated body digests, exact implementation base/head, descriptor path/commit/blob/digest, request path/commit, commands/results, provider attempts `0`, target edits `0`, state namespace, and limitations. Its next trigger says the coordinator may prepare a fresh `design-time/1` scope/route, but no real attempt occurs until the user separately consents to that exact attempt and the complete executor token passes preflight.

- [ ] **Step 5: Commit the handoff and freeze the current-`main` bridge gate**

GO is necessary but does not itself advance the succession. Only on GO, the Director creates `docs/HANDOFF-target-aware-evidence-ledger-opus-bridge-2026-07-16.md` with `apply_patch`, validates its required fields, and commits that path alone with a strict pathspec. The handoff binds the report path/commit and GO, exact reviewed base/head, route/scope/request identities, the current primary-`main` SHA, and a no-post-GO-edit digest for the four shared bridge paths. Capture `BRIDGE_HANDOFF_COMMIT`, `BRIDGE_HANDOFF_BLOB`, and its SHA-256 digest from that commit and require `git diff-tree --no-commit-id --name-only -r "$BRIDGE_HANDOFF_COMMIT"` to equal only the handoff path. Because this plan executes directly on the primary route history, there is no invented bridge merge step: the handoff commit and report commit must be ancestors of current `main`, and the reviewed bridge head must remain an ancestor with no later changes to the shared paths. NITS/FAIL creates a blocker artifact instead of this success handoff. Any later shared-path edit blocks the PPL and candidate-policy successors.

Only after the exact handoff commit/blob/digest validates may the coordinator close the bridge join. Its terminal `done_evidence` must name that content-addressed handoff and the producer-captured GO report; a report alone, an uncommitted handoff, or an ambient-`HEAD` lookup cannot close the join.

- [ ] **Step 6: Route candidate policy and targeted web in strict succession**

After the bridge handoff gate passes, the coordinator may commit one capacity-valid candidate-policy route. That route must consume this plan as the fixed recovery amendment, the Opus B-D handoff, the bridge handoff/report/current-`main` evidence, and the exact no-post-GO shared-path proof. It must explicitly mark the legacy candidate plan's Stage-A companion action and `40fd0a5e..56091d`/one-additive-fix gate as superseded by the immutable `R -> M0 -> F -> Q -> D -> T` plus final Stage-B-D authority chain; it forbids edits to that chain. Candidate implementation follows the remaining legacy plan in an isolated worktree. Its verification command set must also run `tests/unit/test_opus_target_review_bridge.py` against the candidate's changed generic bridge/receipt code; `scripts/opus_target_review_bridge.py` and `tests/unit/test_opus_target_review_bridge.py` are compatibility inputs and remain read-only unless a separately planned, separately reviewed fix is approved. Candidate work receives one canonical Operator GO/NITS/FAIL, and on GO may be integrated only by the user-principal's separately named local integrator for the exact reviewed base/head.

After merged-tree verification, a fresh bounded Operator compatibility pass asks the distinct question whether the already-reviewed target-aware bridge remains valid at the exact candidate integrated SHA. It reruns the complete target-bridge provider-free suite, binds the original bridge handoff/report plus the candidate report and integrated SHA, proves no target-bridge production/test path changed, and returns one canonical GO/NITS/FAIL. This is not a duplicate candidate Lane-V pass: it verifies a new post-integration consumer-compatibility condition. Only GO produces fixed committed `docs/HANDOFF-director-2026-07-16-candidate-policy-integrated.md`; that handoff binds both reports, merged-tree evidence, the exact integrated SHA, and zero provider/receipt mutation. The candidate coordinator join may become terminal only when `done_evidence` names that handoff and the post-candidate compatibility GO report.

The terminal candidate handoff unlocks PPL first, not targeted web. PPL must finish its target correction and commit `docs/HANDOFF-ledger-ppl-publication-race-correction-2026-07-16.md`; its coordinator join must be terminal with the exact cumulative GO report, and the target-review receipt family must have no reserved, in-flight, or unreconciled attempt. Only then may the targeted-web route start. This prevents edits to `tests/unit/test_protocol_prompt_sync.py` or prompt authority from racing a PPL scope, token, sealed closure, or receipt.

The web route binds the candidate and PPL handoff paths/commits/blobs, candidate exact integrated head and post-candidate compatibility GO, PPL terminal target verdict and no-in-flight-family evidence, and a fresh clean-owner check for every web target. The legacy web plan's phrase “coordinator integration” is interpreted narrowly as coordinator reconciliation: a separately named local integrator performs any merge from the exact reviewed base/head. Web GO, authorized integration, and merged-tree verification produce a fixed committed `docs/HANDOFF-director-2026-07-16-targeted-web-integrated.md`; push remains a later, separate authorization. No route for either successor is created early merely to reserve capacity.

## Plan Self-Review Record

- Default compatibility: all current Pipeline source/snapshot/runtime/sandbox/grammar/prompt/schema/parser/unavailable behavior is pinned byte-for-byte behind `PIPELINE_REVIEW_POLICY`.
- Target isolation: target review uses only a content-addressed sealed source/requirement/runtime closure and explicitly denies live worktree, Git, data, resource, workbook, database, DSN, and user-config access.
- Authority: each attempt binds a fresh active route, distinct explicit user consent, and complete Side-Effect Executor Token; reconciliation binds a second exact committed route and finite evidence grammar.
- Attempt accounting: the CAS key is family/question/sequence, while exact task/scope/route/consent/token/closure identity is conflict-checked. Implementation tests use fake providers only.
- Sequencing: prior design/actual receipts must be reconciled; issue-driven code changes use monotonic `actual-diff/N+1`, and changed family assumptions force a new `design-time/1`.
- Report provenance: the final report path and commit come directly from the producer/commit operation, never a later ambient `HEAD` scan.
- Recovery succession: final Opus B-D evidence gates the bridge; bridge current-`main` evidence gates candidate policy; candidate GO plus authorized integration gates targeted web. The legacy Stage-A companion action is never replayed.
- Known limitation: the sealed runtime still depends on the host kernel and signed system-library roots admitted by the sandbox. Those roots are excluded from review inputs and recorded as trusted runtime baseline rather than claimed as content-addressed target evidence.

## Exact Next Trigger

After this plan and the PPL correction plan are committed, and only after the fixed Opus B-D handoff gate passes, route one Pipeline Director/Operator pair to implement bridge Tasks 1-6 from the exact coordinator-bound base. Do not invoke Opus or edit evidence-ledger while implementing or verifying the bridge. Candidate policy and targeted web remain blocked behind their strict succession gates above.
