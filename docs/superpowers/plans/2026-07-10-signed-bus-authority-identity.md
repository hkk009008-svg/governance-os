# Signed-Bus Authority And Runtime Identity Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Activate the signed ref bus for signed control and promotion facts while keeping the Markdown mailbox authoritative for human coordination and rejecting every mixed runtime identity before mutation or GO authority.

**Architecture:** Add a versioned channel-authority manifest and typed authority/identity resolvers, then migrate human-mailbox callers away from cursor-shape inference. Harden and execute a no-dual-write signed-bus cutover, provision the public-key trust root, prepare remote CI signing and a protected merge-gate deployment, and synchronize executable truth surfaces only after focused RED/GREEN/non-vacuity verification.

**Tech Stack:** Python 3.13 standard library (`dataclasses`, `enum`, `tomllib`, `subprocess`), existing `threeway` Ed25519/refstore modules, Bash protocol tools, GitHub Actions YAML, pytest, git with `env -u GIT_INDEX_FILE`.

## Global Constraints

- Execute from an isolated worktree created from Pipeline commit `78b48ed` using `superpowers:using-git-worktrees` before the first implementation task.
- Prefix every ordinary git and pytest command with `env -u GIT_INDEX_FILE`.
- Use `apply_patch` for repository file edits; use explicit pathspecs for staging and commits.
- Coordinator owns planning/routing only and does not author behavior-changing code.
- Each task uses a fresh director-owned implementer, then a fresh spec reviewer and code-quality reviewer; the paired operator independently issues GO/NITS/FAIL on the landed commit.
- Tasks are sequential unless a coordinator route explicitly proves disjoint worktrees and write sets. Tasks 1–5 share authority interfaces and must remain sequential.
- The Markdown mailbox remains the only human route/brief/report/handoff channel.
- Signed control and promotion facts use only `refs/threeway/*` after cutover. Never dual-write one fact class.
- Coordinators are all-scope and unpinned for the human mailbox; they never consume a human-mailbox cursor.
- Private `*.ed25519` files never enter the repository, staging area, command output, logs, or candidate-executing environments.
- No authoritative-ref creation, key upload, repository-variable mutation, Actions-secret mutation, runner deployment, or remote publication occurs without a complete target-bound side-effect executor token.
- No push occurs before operator GO for the exact target commit.
- Closed historical artifacts remain readable; do not rewrite mailbox history.
- Every regression proves RED, GREEN, and a one-fact non-vacuity flip.

## File And Interface Map

| File | Responsibility |
|---|---|
| `coordination/authority.toml` | Committed channel authority and activation state |
| `scripts/protocol_authority.py` | Typed manifest loader and live-state validation |
| `scripts/protocol_mailbox.py` | Human-mailbox addressability, cursor, receipt, and all-scope policy |
| `scripts/status.py` | Human-mailbox unread collection independent of signed-bus state |
| `scripts/check_coordination.py` | Fail-closed human-mailbox cursor and event validation |
| `scripts/mailbox_monitor.py` | Read-only human-mailbox and signed-fact observability |
| `scripts/bus_unread.py` | Signed-fact unread with explicit authority checks |
| `scripts/consume_bus.py` | Signed-fact cursor consumption only |
| `coordination/bin/send-event` | Human-mailbox sender with unpinned coordinator envelope handling |
| `coordination/bin/consume-events` | Pair-seat human-mailbox consumption only |
| `scripts/codex_protocol_model.py` | Typed runtime identity and narrow-only override policy |
| `.codex/hooks/update-state.sh` | Mutation-time identity validation before presence writes |
| `.agents/skills/four-seat-protocol/scripts/seat_status.py` | Channel-labeled seat orientation |
| `threeway/cutover.py` | Ref-bus projection, cursor initialization, teardown, and ready-to-flip result |
| `threeway/keys_bootstrap.py` | Idempotent, complete-roster key provisioning without re-key |
| `scripts/execute_threeway_cutover.sh` | Double-gated activation driver and preflight |
| `.github/workflows/ci.yml` | Trusted manual CI signer, inert until remote activation |
| `scripts/run_merge_gate.py` | Protected-main merge-gate runner with deployment attestation |

---

### Task 1: Add The Channel Authority Manifest And Typed Loader

**Owner:** Pair A director implementation; Pair A operator verification.

**Files:**
- Create: `coordination/authority.toml`
- Create: `scripts/protocol_authority.py`
- Create: `tests/unit/test_protocol_authority.py`
- Modify: `tests/unit/test_imports_smoke.py`

**Interfaces:**
- Produces `AuthorityConfigError(ValueError)`.
- Produces `ChannelAuthority` enum values `dormant`, `shadow`, and `live`.
- Produces immutable `HumanMailboxAuthority`, `SignedFactsAuthority`, and `AuthorityManifest` dataclasses.
- Produces `load_authority(root: Path) -> AuthorityManifest`.
- Produces `validate_authority_runtime(root: Path, manifest: AuthorityManifest) -> tuple[str, ...]` where an empty tuple is valid and each nonempty item is a stable error string.
- The initial committed state is `human_mailbox.authority="live"` and `signed_facts.authority="shadow"`; Task 6 performs the only transition to signed-facts `live`.

- [ ] **Step 1: Write the failing manifest tests**

Create tests with this exact behavioral shape:

```python
def test_load_authority_separates_human_mailbox_and_signed_facts(tmp_path):
    _write_manifest(tmp_path, human="live", signed="shadow")
    manifest = protocol_authority.load_authority(tmp_path)
    assert manifest.human_mailbox.backend == "legacy-files"
    assert manifest.human_mailbox.authority is protocol_authority.ChannelAuthority.LIVE
    assert manifest.signed_facts.backend == "signed-ref-bus"
    assert manifest.signed_facts.authority is protocol_authority.ChannelAuthority.SHADOW


def test_live_signed_facts_without_events_ref_is_unavailable(tmp_path, git_repo):
    _write_manifest(tmp_path, human="live", signed="live")
    manifest = protocol_authority.load_authority(tmp_path)
    assert protocol_authority.validate_authority_runtime(git_repo, manifest) == (
        "signed-facts live but refs/threeway/events is absent",
    )


def test_unknown_authority_value_fails_closed(tmp_path):
    _write_manifest(tmp_path, human="live", signed="automatic")
    with pytest.raises(protocol_authority.AuthorityConfigError, match="automatic"):
        protocol_authority.load_authority(tmp_path)
```

- [ ] **Step 2: Run the focused tests to prove RED**

```bash
env -u GIT_INDEX_FILE .venv/bin/python -m pytest tests/unit/test_protocol_authority.py -q
```

Expected: collection fails with `ModuleNotFoundError: No module named 'protocol_authority'`.

- [ ] **Step 3: Add the initial authority manifest**

Create exactly:

```toml
schema_version = 1

[human_mailbox]
backend = "legacy-files"
authority = "live"
read_scope = "addressed-pairs-all-scope-coordinators"

[signed_facts]
backend = "signed-ref-bus"
authority = "shadow"
events_ref = "refs/threeway/events"
cursor_namespace = "refs/threeway/cursors/"

[decision]
adr = "DECISIONS.md#signed-bus-activation-and-channel-authority-split"
activated_by = "user-principal"
activation_date = "2026-07-10"
```

- [ ] **Step 4: Implement the typed loader and runtime validator**

Use these exact public types and field names:

```python
class ChannelAuthority(str, Enum):
    DORMANT = "dormant"
    SHADOW = "shadow"
    LIVE = "live"


@dataclass(frozen=True)
class HumanMailboxAuthority:
    backend: str
    authority: ChannelAuthority
    read_scope: str


@dataclass(frozen=True)
class SignedFactsAuthority:
    backend: str
    authority: ChannelAuthority
    events_ref: str
    cursor_namespace: str


@dataclass(frozen=True)
class AuthorityManifest:
    schema_version: int
    human_mailbox: HumanMailboxAuthority
    signed_facts: SignedFactsAuthority
    adr: str
    activated_by: str
    activation_date: str
```

`load_authority()` must reject a missing file, schema versions other than `1`,
unknown backends, unknown authority values, a human mailbox that is not live,
and events/cursor refs outside `refs/threeway/`. `validate_authority_runtime()`
must use local git ref inspection only and must report missing live refs rather
than treating them as empty.

- [ ] **Step 5: Prove GREEN and non-vacuity**

```bash
env -u GIT_INDEX_FILE .venv/bin/python -m pytest tests/unit/test_protocol_authority.py tests/unit/test_imports_smoke.py -q
```

Then change only the live-ref fixture to create `refs/threeway/events`, confirm
the missing-ref assertion fails, restore it, and rerun the suite to GREEN.

- [ ] **Step 6: Review and commit Task 1**

```bash
env -u GIT_INDEX_FILE git add -- coordination/authority.toml scripts/protocol_authority.py tests/unit/test_protocol_authority.py tests/unit/test_imports_smoke.py
env -u GIT_INDEX_FILE git diff --cached --check
env -u GIT_INDEX_FILE git commit -m "feat(protocol): add explicit channel authority model" -- coordination/authority.toml scripts/protocol_authority.py tests/unit/test_protocol_authority.py tests/unit/test_imports_smoke.py
```

---

### Task 2: Separate Human-Mailbox Policy From Signed-Fact Cursors

**Owner:** Pair A director implementation; Pair A operator verification.

**Files:**
- Modify: `scripts/protocol_mailbox.py`
- Modify: `scripts/status.py`
- Modify: `scripts/check_coordination.py`
- Modify: `scripts/mailbox_monitor.py`
- Modify: `scripts/bus_unread.py`
- Modify: `scripts/consume_bus.py`
- Modify: `scripts/check_go_schema.py`
- Modify: `coordination/bin/send-event`
- Modify: `coordination/bin/consume-events`
- Modify: `.agents/skills/four-seat-protocol/scripts/seat_status.py`
- Modify: `tests/unit/test_protocol_mailbox.py`
- Modify: `tests/unit/test_status.py`
- Modify: `tests/unit/test_check_coordination.py`
- Modify: `tests/unit/test_coordination_tooling.py`
- Modify: `tests/unit/test_governance_hardening.py`
- Modify: `tests/unit/test_threeway_activation_scripts.py`
- Modify: `tests/unit/test_seat_status_all.py`
- Modify: `tests/unit/test_check_go_schema.py`
- Delete: `coordination/mailbox/seen/coordinator.txt`
- Delete: `coordination/mailbox/seen/coordinator2.txt`

**Interfaces:**
- Produces `ADDRESSABLE_IDENTITIES`, `HUMAN_MAILBOX_CURSOR_OWNERS`, `HUMAN_MAILBOX_RECEIPT_IDENTITIES`, `HUMAN_MAILBOX_ALL_SCOPE_READERS`, and `SIGNED_FACT_CURSOR_IDENTITIES`.
- Keeps `RECEIVING_SEATS` as a deprecated compatibility alias for addressability only; no cursor or receipt code may consume that alias.
- Produces `UNINITIALIZED_CURSOR = "UNINITIALIZED"`.
- Produces `count_human_unread(cursor: str, event_filenames: Iterable[str], seat: str) -> int`.
- `bus_unread_events()` consults `protocol_authority`; shadow/live missing refs return `None`, not `[]`.

- [ ] **Step 1: Replace roster tests with semantic-policy tests**

Add assertions equivalent to:

```python
assert set(protocol_mailbox.ADDRESSABLE_IDENTITIES) == {
    "director", "director2", "operator", "operator2", "coordinator", "coordinator2"
}
assert set(protocol_mailbox.HUMAN_MAILBOX_CURSOR_OWNERS) == {
    "director", "director2", "operator", "operator2"
}
assert set(protocol_mailbox.HUMAN_MAILBOX_ALL_SCOPE_READERS) == {
    "coordinator", "coordinator2"
}
assert not set(protocol_mailbox.HUMAN_MAILBOX_CURSOR_OWNERS) & set(
    protocol_mailbox.HUMAN_MAILBOX_ALL_SCOPE_READERS
)
```

Add integration tests that:

- reject `coordination/bin/consume-events coordinator` and `coordinator2`;
- allow pair-seat human-mailbox consume;
- render coordinator status as `ALL-SCOPE EVENTS / unpinned`;
- count every addressed event from `UNINITIALIZED`;
- ignore signed-bus cursor refs when computing human-mailbox unread;
- report signed-bus `unavailable` when authority is shadow/live and the events ref is missing;
- permit coordinator signed-fact identities only through `scripts/consume_bus.py`.

- [ ] **Step 2: Run the focused tests to prove RED**

```bash
env -u GIT_INDEX_FILE .venv/bin/python -m pytest tests/unit/test_protocol_mailbox.py tests/unit/test_status.py tests/unit/test_check_coordination.py tests/unit/test_coordination_tooling.py tests/unit/test_governance_hardening.py tests/unit/test_threeway_activation_scripts.py tests/unit/test_seat_status_all.py -q
```

Expected: failures show coordinators still own cursor files, scalar cursors still
select ref-bus unread, and absent refs still produce zero.

- [ ] **Step 3: Add semantic mailbox constants**

Replace the conflated roster with:

```python
SEATS = ("director", "director2", "operator", "operator2")
COORDINATORS = ("coordinator", "coordinator2")
ADDRESSABLE_IDENTITIES = (*SEATS, *COORDINATORS)
HUMAN_MAILBOX_CURSOR_OWNERS = SEATS
HUMAN_MAILBOX_RECEIPT_IDENTITIES = SEATS
HUMAN_MAILBOX_ALL_SCOPE_READERS = COORDINATORS
SIGNED_FACT_CURSOR_IDENTITIES = (*SEATS, *COORDINATORS)
RECEIVING_SEATS = ADDRESSABLE_IDENTITIES
SENDERS = ADDRESSABLE_IDENTITIES
RECIPIENTS = (*ADDRESSABLE_IDENTITIES, "all")
UNINITIALIZED_CURSOR = "UNINITIALIZED"
```

- [ ] **Step 4: Make human unread independent of signed refs**

`count_human_unread()` must treat `UNINITIALIZED` as older than every valid
event, ISO timestamps as strict watermarks, and all other cursor values as a
visible invalid state handled by the caller. Remove scalar-ref-bus switching
from `status.collect_mailbox()` and `seat_status.py`.

Use `HUMAN_MAILBOX_CURSOR_OWNERS` for cursor loops and
`HUMAN_MAILBOX_ALL_SCOPE_READERS` for coordinator rendering. Use
`HUMAN_MAILBOX_RECEIPT_IDENTITIES` in receipt monitoring.

- [ ] **Step 5: Restrict mutation tools**

Change `coordination/bin/consume-events` to accept only the four pair seats.
Teach it that `UNINITIALIZED` has no lower watermark: an intentional consume
may advance it to the newest addressed ISO event, while an explicit `--to`
still must name a real addressed event. Preserve regression refusal once the
cursor is ISO.
Keep all six addressable identities in `send-event`, but render coordinator
envelopes as:

```text
Cursor at send: all-scope-unpinned
```

Change the GO-schema cursor-envelope regex to accept an ISO or
`UNINITIALIZED` pair-seat cursor, or this exact coordinator marker.

- [ ] **Step 6: Migrate current human cursor files honestly**

Because no committed cursor-backfill manifest can reconstruct the prior ISO
watermarks, set the four pair files to exactly `UNINITIALIZED\n` and delete the
two coordinator files. Do not invent consumed timestamps.

- [ ] **Step 7: Prove GREEN and non-vacuity**

```bash
env -u GIT_INDEX_FILE .venv/bin/python -m pytest tests/unit/test_protocol_mailbox.py tests/unit/test_status.py tests/unit/test_check_coordination.py tests/unit/test_coordination_tooling.py tests/unit/test_governance_hardening.py tests/unit/test_threeway_activation_scripts.py tests/unit/test_seat_status_all.py tests/unit/test_check_go_schema.py -q
```

Change only one coordinator to a cursor owner in the test fixture and confirm
the policy-disjointness test fails. Restore the policy and rerun GREEN.

- [ ] **Step 8: Review and commit Task 2**

Stage only the paths listed above, inspect the cached diff, and commit:

```bash
env -u GIT_INDEX_FILE git commit -m "fix(protocol): separate mailbox and signed-fact cursors"
```

---

### Task 3: Add Fail-Closed Runtime Identity Resolution

**Owner:** Pair B director2 implementation in a separate worktree after Task 2; Pair B operator2 verification.

**Files:**
- Modify: `scripts/codex_protocol_model.py`
- Modify: `scripts/continuation_readiness.py`
- Modify: `.codex/hooks/update-state.sh`
- Modify: `.codex/hooks/session-smoke.sh`
- Create: `tests/unit/test_codex_protocol_model.py`
- Modify: `tests/unit/test_coordination_tooling.py`
- Modify: `tests/unit/test_protocol_prompt_sync.py`

**Interfaces:**
- Produces `RuntimeIdentityError(ValueError)`.
- Produces immutable `RuntimeIdentity` with fields `mode`, `concrete_seat`, `role`, `behavior_source`, `identity_valid`, and `validation_errors` plus the existing rendered policy fields.
- Produces `resolve_runtime_identity(environ: Mapping[str, str]) -> RuntimeIdentity`.
- Keeps `infer_runtime_env()` as the compatibility renderer; it calls the resolver and adds `CODEX_IDENTITY_VALID` and `CODEX_IDENTITY_ERRORS`.
- Produces CLI validation: `scripts/codex_protocol_model.py --validate-runtime-env` exits `0` only for a valid identity.

- [ ] **Step 1: Write the identity matrix regressions**

Include these exact cases:

```python
@pytest.mark.parametrize("env", [
    {"CODEX_SEAT": "director2", "CODEX_AGENT_ROLE": "operator2"},
    {"CODEX_SEAT": "operator", "CODEX_AGENT_ROLE": "director"},
    {"CODEX_SEAT": "coordinator", "CODEX_AGENT_MODE": "live-seat"},
    {"CODEX_AGENT_ROLE": "director"},
    {"CODEX_SEAT": "not-a-seat"},
])
def test_mixed_or_incomplete_identity_is_invalid(env):
    identity = model.resolve_runtime_identity(env)
    assert identity.identity_valid is False
    assert identity.validation_errors


def test_operator_identity_has_go_authority_only_with_operator_seat():
    identity = model.resolve_runtime_identity({"CODEX_SEAT": "operator"})
    assert identity.identity_valid is True
    assert identity.verification_policy == "independent-go-nits-fail"


def test_override_cannot_widen_readiness_bridge():
    identity = model.resolve_runtime_identity({
        "CODEX_AUTHORITY_SCOPE": "seat-owned",
        "CODEX_VERIFICATION_POLICY": "independent-go-nits-fail",
    })
    assert identity.identity_valid is False
    assert "widen" in " ".join(identity.validation_errors)
```

Add hook integration tests proving an invalid `CODEX_SEAT` creates no heartbeat
file and exits nonzero before any repository mutation.

- [ ] **Step 2: Run tests to prove RED**

```bash
env -u GIT_INDEX_FILE .venv/bin/python -m pytest tests/unit/test_codex_protocol_model.py tests/unit/test_coordination_tooling.py tests/unit/test_protocol_prompt_sync.py -q
```

Expected: import/attribute failures for the resolver and a hook test showing the
current arbitrary presence path write.

- [ ] **Step 3: Implement `RuntimeIdentity` and strict resolution**

Resolve mode and role from concrete seat first. An explicit role must equal the
concrete seat; canonical behavior source is derived separately and never
accepted as a substitute role. Reject every mismatch and unknown value.
Implement narrow-only override allowlists for each resolved mode.

Read-only rendering returns an invalid object with errors. The CLI validator and
mutation hooks treat any invalid object as fatal.

- [ ] **Step 4: Gate mutation hooks before presence/index writes**

Call:

```bash
env -u GIT_INDEX_FILE .venv/bin/python scripts/codex_protocol_model.py --validate-runtime-env
```

at the beginning of mutation-capable hook paths. A readiness bridge with no
seat remains valid and performs no seat heartbeat write.

- [ ] **Step 5: Prove GREEN and non-vacuity**

```bash
env -u GIT_INDEX_FILE .venv/bin/python -m pytest tests/unit/test_codex_protocol_model.py tests/unit/test_coordination_tooling.py tests/unit/test_protocol_prompt_sync.py -q
```

Change the mismatched `director2/operator2` fixture to `operator2/operator2`
and confirm the invalid assertion fails; restore it and rerun GREEN.

- [ ] **Step 6: Review and commit Task 3**

```bash
env -u GIT_INDEX_FILE git commit -m "fix(protocol): reject mixed runtime identity"
```

---

### Task 4: Harden The Signed-Bus Cutover For Two Independent Channels

**Owner:** Pair A director implementation; Pair A operator verification.

**Files:**
- Modify: `threeway/cutover.py`
- Modify: `threeway/cursor_backfill.py`
- Modify: `scripts/execute_threeway_cutover.sh`
- Modify: `scripts/bus_unread.py`
- Create: `tests/unit/test_threeway_cutover.py`
- Modify: `tests/unit/test_threeway_activation_scripts.py`
- Modify: `tests/unit/test_protocol_authority.py`

**Interfaces:**
- `run_cutover()` preserves human `coordination/mailbox/seen/` bytes.
- Produces `initialize_signed_fact_cursors(store: RefEventStore, identities: Sequence[str], seq: int) -> dict[str, int]`.
- `CutoverResult` includes `human_mailbox_unchanged: bool` and `ready_to_flip: bool`.
- `scripts/execute_threeway_cutover.sh --preflight` performs no writes and exits nonzero on partial key registries, dirty tracked files, pre-existing unexplained refs, or non-shadow authority.
- `--yes` remains the only mutating cutover flag.

- [ ] **Step 1: Write cutover regressions**

Tests must snapshot every `seen/*.txt` byte before `run_cutover()` and assert the
same bytes after success and injected failure. Add cases for:

- missing live/shadow events ref reported unavailable, not empty;
- all signed-fact cursor refs initialized to the explicit projected head;
- partial ref creation torn down to the exact pre-run snapshot;
- partial public-key registry rejected by preflight;
- a second cutover refused unless the existing refs exactly match the activation manifest;
- `--preflight` producing no refs, files, cursor changes, or staging.

- [ ] **Step 2: Run tests to prove RED**

```bash
env -u GIT_INDEX_FILE .venv/bin/python -m pytest tests/unit/test_threeway_cutover.py tests/unit/test_threeway_activation_scripts.py tests/unit/test_protocol_authority.py -q
```

Expected: tests show the current cutover rewrites human cursor files and treats
missing refs as an empty bus.

- [ ] **Step 3: Remove human cursor rewriting from cutover**

Keep legacy carrier projection for audit continuity, but initialize only
`refs/threeway/cursors/*`. Set signed-fact cursors to the projected event head
as an explicit activation decision recorded in the cutover result. Do not call
`cursor_backfill.backfill()` on the human mailbox.

Retain exact-ref snapshot/teardown behavior. Keep `cursor_backfill` readable for
historical manifests, but no live human-mailbox caller may depend on its scalar
sentinels.

- [ ] **Step 4: Add pure preflight to the driver**

The preflight checks:

```text
authority manifest is human live / signed shadow
working tree has no tracked changes
public-key registry is either empty or complete for the exact signing roster
private keystore is outside the repository
refs/threeway/events and signed cursor refs are absent, or explicitly recognized for a verified resume
focused tests and operator GO are named in the executor token before --yes
```

- [ ] **Step 5: Prove GREEN and non-vacuity**

```bash
env -u GIT_INDEX_FILE .venv/bin/python -m pytest tests/unit/test_threeway_cutover.py tests/unit/test_threeway_activation_scripts.py tests/unit/test_protocol_authority.py -q
```

Change one expected signed cursor from the projected head to `0`; confirm the
test fails, restore it, and rerun GREEN.

- [ ] **Step 6: Review and commit Task 4**

```bash
env -u GIT_INDEX_FILE git commit -m "fix(threeway): separate bus cutover from human cursors"
```

---

### Task 5: Make Key Bootstrap Idempotent And Complete-Roster Safe

**Owner:** Pair B director2 implementation; Pair B operator2 verification.

**Files:**
- Modify: `threeway/keys_bootstrap.py`
- Modify: `threeway/keys.py`
- Modify: `scripts/execute_threeway_cutover.sh`
- Modify: `tests/unit/test_keys.py`
- Modify: `tests/unit/test_threeway_activation_scripts.py`

**Interfaces:**
- Produces `expected_public_key_names(seats: Sequence[str] = SEATS) -> frozenset[str]`.
- Produces `registry_state(registry: Path, seats: Sequence[str] = SEATS) -> Literal["empty", "complete"]`; partial/extra registries raise `RegistryStateError`.
- Bootstrap refuses to overwrite any existing complete trust root and verifies each public/private pair instead.

- [ ] **Step 1: Write key-registry regressions**

Add tests proving:

- an empty registry generates the exact 11-seat roster;
- a complete matching registry/keystore is a no-op and preserves every byte;
- a partial registry fails before writing;
- an extra public key fails before writing;
- a public/private mismatch fails before writing;
- no private-key filename appears below the repository root.

- [ ] **Step 2: Run tests to prove RED**

```bash
env -u GIT_INDEX_FILE .venv/bin/python -m pytest tests/unit/test_keys.py tests/unit/test_threeway_activation_scripts.py -q
```

Expected: the current bootstrap overwrites complete keys and accepts partial
state when called directly.

- [ ] **Step 3: Implement fail-closed registry inspection**

Validate the complete expected filename set before generation or reuse. For a
complete registry, load every private key from the configured keystore and
verify its derived public key equals the committed value. Never print private
key material.

- [ ] **Step 4: Prove GREEN and non-vacuity**

```bash
env -u GIT_INDEX_FILE .venv/bin/python -m pytest tests/unit/test_keys.py tests/unit/test_threeway_activation_scripts.py -q
```

Replace one public key with another valid 64-hex key and confirm the
public/private matching test fails; restore it and rerun GREEN.

- [ ] **Step 5: Review and commit Task 5**

```bash
env -u GIT_INDEX_FILE git commit -m "fix(threeway): make key bootstrap fail closed"
```

---

### Task 6: Provision The Trust Root And Execute The Local Authority Flip

**Owner:** One executor elected by coordinator; all other seats observer-only. Pair A operator verifies the resulting commit and refs.

**Files and state:**
- Create: `coordination/threeway/keys/*.pub` for the exact 11-seat roster
- Modify: `coordination/authority.toml` (`signed_facts.authority` from `shadow` to `live` only after successful cutover)
- Create: `logs/threeway-activation-2026-07-10/preflight.txt`
- Create: `logs/threeway-activation-2026-07-10/postcheck.txt`
- Mutate local refs: `refs/threeway/events` and `refs/threeway/cursors/*`
- Write private keys only to the approved off-repo seat-local keystore

**Side-effect executor token:**

```text
side_effect_id: threeway-local-authority-flip-2026-07-10
executor: director
target: Pipeline local refs/threeway/* plus coordination/threeway/keys/*.pub
allowed_command_class: threeway key bootstrap and execute_threeway_cutover.sh --yes
preflight: clean tracked tree; Tasks 1-5 operator GO; empty key registry; no unexplained refs; keystore outside repo; authority shadow
stop_if_newer_mail_or_live_target_satisfied: stop on newer executor appointment, any existing unexplained ref, changed HEAD, missing GO, or already-live manifest
postcheck: complete public registry; no private key tracked; events/cursor refs present; human cursor bytes unchanged; authority validator clean
observer_seats: director2, operator, operator2, coordinator, coordinator2
final_closeout_owner: coordinator
non_goals: remote push, GitHub settings, Actions secret, protected-main update, lock claim, mailbox consume, target checkout refresh
```

- [ ] **Step 1: Re-run live preflight immediately before mutation**

```bash
env -u GIT_INDEX_FILE git log --oneline -3
env -u GIT_INDEX_FILE git status --short --branch
env -u GIT_INDEX_FILE git for-each-ref --format='%(refname) %(objectname)' 'refs/threeway/'
env -u GIT_INDEX_FILE .venv/bin/python scripts/execute_threeway_cutover.sh --preflight
```

Expected: exact routed HEAD, clean tracked tree, no unexplained refs, complete
preflight, and no state mutation.

- [ ] **Step 2: Execute the single authority flip**

Run only as the token's executor with the approved off-repo keystore:

```bash
THREEWAY_KEYSTORE="$HOME/.threeway/keys" env -u GIT_INDEX_FILE scripts/execute_threeway_cutover.sh --yes
```

Do not copy private keys into the repository or terminal output.

- [ ] **Step 3: Change the committed manifest to live**

Change only:

```toml
[signed_facts]
authority = "live"
```

Preserve the remaining manifest fields byte-for-byte.

- [ ] **Step 4: Capture postcheck evidence**

Record command output, without private material, from:

```bash
env -u GIT_INDEX_FILE git for-each-ref --format='%(refname) %(objectname)' 'refs/threeway/'
env -u GIT_INDEX_FILE .venv/bin/python -c 'from pathlib import Path; from scripts.protocol_authority import load_authority, validate_authority_runtime; m=load_authority(Path(".")); print(validate_authority_runtime(Path("."), m))'
env -u GIT_INDEX_FILE git ls-files 'coordination/threeway/keys/*.pub'
env -u GIT_INDEX_FILE git ls-files '*.ed25519'
env -u GIT_INDEX_FILE git diff -- coordination/mailbox/seen
```

Expected: events and signed cursor refs exist; authority validation prints
`()`, exactly 11 public keys are listed, no private keys are listed, and the
human cursor diff is empty.

- [ ] **Step 5: Commit the trust root and live marker**

Stage only the 11 public keys, manifest, and secret-free evidence logs. Inspect
every staged filename and diff before committing:

```bash
env -u GIT_INDEX_FILE git commit -m "feat(threeway): activate signed fact bus"
```

- [ ] **Step 6: Send one verify-request**

The request names the commit/range, Tasks 1–6 selectors, ref postchecks, public
key count, human-cursor unchanged proof, private-key absence proof, and all
excluded remote side effects. Operator returns GO/NITS/FAIL before any remote
activation.

---

### Task 7: Harden And Prepare The Remote CI Signer

**Owner:** Pair A director implementation; Pair A operator verification. Remote setting changes remain a later executor-only action.

**Files:**
- Modify: `.github/workflows/ci.yml`
- Modify: `scripts/sign_ci_result.py`
- Modify: `tests/unit/test_threeway_activation_scripts.py`

**Interfaces:**
- CI signer rejects an empty/malformed private seed before creating a key file.
- CI signer verifies `integration_sha` is lowercase 40-hex and is reachable at the supplied integration ref.
- Signed `ci_result` binds `integration_sha`, `candidate_id`, `result`, and `policy_digest`.
- Workflow remains inert unless manual dispatch, trusted main, both test jobs GREEN, and `THREEWAY_BUS_LIVE=true`.

- [ ] **Step 1: Add CI signer regressions**

Test source and behavior for empty secret refusal, malformed SHA refusal,
candidate binding, exact policy digest, remote argument propagation, and
workflow gating on manual dispatch plus trusted main.

- [ ] **Step 2: Run tests to prove RED**

```bash
env -u GIT_INDEX_FILE .venv/bin/python -m pytest tests/unit/test_threeway_activation_scripts.py -q
```

Expected: the workflow currently writes an empty secret to disk before
`load_private()` fails and lacks the new explicit pre-write assertion.

- [ ] **Step 3: Implement the minimal guards**

Add a shell guard before the key file write:

```bash
test -n "$CI_PRIVATE_KEY" || {
  echo "THREEWAY_CI_KEY is empty or unavailable" >&2
  exit 1
}
```

Keep candidate code out of the signer job. Preserve `needs: [smoke,
pytest-unit]`, trusted-main checkout, explicit SHA validation, and remote
push-CAS through `sign_ci_result.py --remote origin`.

- [ ] **Step 4: Prove GREEN and non-vacuity**

```bash
env -u GIT_INDEX_FILE .venv/bin/python -m pytest tests/unit/test_threeway_activation_scripts.py -q
```

Remove only the `test -n` guard in a mutation diff and confirm the new test
fails; restore it and rerun GREEN.

- [ ] **Step 5: Review and commit Task 7**

```bash
env -u GIT_INDEX_FILE git commit -m "fix(threeway): fail closed before CI signing"
```

---

### Task 8: Add A Verifiable Protected-Main Deployment Contract

**Owner:** Pair B director2 implementation; Pair B operator2 verification.

**Files:**
- Create: `threeway/deployment.py`
- Modify: `scripts/run_merge_gate.py`
- Create: `tests/unit/test_threeway_protected_main.py`
- Modify: `tests/unit/test_threeway_activation_scripts.py`

**Interfaces:**
- Produces `DeploymentAttestationError(ValueError)`.
- Produces immutable `ProtectedMainAttestation` with `schema_version`, `repository`, `main_ref`, `runner_identity`, `branch_protection_required`, `force_push_disabled`, and `verified_at`.
- Produces `load_protected_main_attestation(path: Path) -> ProtectedMainAttestation`.
- Protected main requires `--allow-protected-main`, `--remote`, and `--deployment-attestation`; test-main behavior remains unchanged.

- [ ] **Step 1: Write protected-main regressions**

Tests must prove:

- protected main refuses without the flag;
- the flag alone still refuses;
- missing remote refuses;
- missing, malformed, wrong-repository, wrong-ref, force-push-enabled, or
  branch-protection-disabled attestation refuses;
- a valid attestation reaches credential loading and gate execution;
- test-main remains usable without a deployment attestation;
- a textual conflict or integration-SHA mismatch never updates main.

- [ ] **Step 2: Run tests to prove RED**

```bash
env -u GIT_INDEX_FILE .venv/bin/python -m pytest tests/unit/test_threeway_protected_main.py tests/unit/test_threeway_activation_scripts.py -q
```

Expected: module import failure and current unconditional protected-main
refusal.

- [ ] **Step 3: Implement attestation loading and protected preflight**

Use JSON with strict exact keys and reject unknown keys. Parse `verified_at` as
UTC ISO-8601 and require the attestation to be no older than 24 hours when the
daemon starts. Require repository and ref to match CLI arguments exactly.

- [ ] **Step 4: Prove GREEN and non-vacuity**

```bash
env -u GIT_INDEX_FILE .venv/bin/python -m pytest tests/unit/test_threeway_protected_main.py tests/unit/test_threeway_activation_scripts.py -q
```

Flip only `force_push_disabled` to `false` and confirm refusal; restore it and
rerun GREEN.

- [ ] **Step 5: Review and commit Task 8**

```bash
env -u GIT_INDEX_FILE git commit -m "feat(threeway): validate protected-main deployment"
```

The actual runner deployment, secret installation, repository variable update,
and protected-main credential remain external side effects. They execute only
after Tasks 7–9 operator GO, final publication of the trusted code, and a fresh
executor token.

---

### Task 9: Synchronize Doctrine And Run The Full Verification Gate

**Owner:** Pair A director docs/model sync; Pair A operator final verification.

**Files:**
- Append: `DECISIONS.md`
- Modify: `ARCHITECTURE.md`
- Modify: `coordination/README.md`
- Modify: `docs/protocol/codex/continuation.md`
- Modify: `docs/protocol/threeway/CODEX-ADOPTION.md`
- Modify: `docs/protocol/threeway/README.md`
- Modify: `.agents/skills/four-seat-protocol/SKILL.md`
- Modify: `.agents/skills/seat-coordinator/SKILL.md`
- Modify: `.agents/skills/seat-director/SKILL.md`
- Modify: `.agents/skills/seat-operator/SKILL.md`
- Modify: `.codex/agents/README.md`
- Modify: `.codex/agents/protocol-director.toml`
- Modify: `.codex/agents/protocol-operator.toml`
- Modify: `.codex/agents/protocol-coordinator.toml`
- Modify: `tests/unit/test_protocol_prompt_sync.py`
- Modify: `tests/unit/test_protocol_doc_integrity.py`

**Interfaces:**
- Append an ADR titled `Signed-bus activation and channel authority split`.
- Render one model-backed authority table into Codex continuation and agent README surfaces.
- Document that signed facts are live, human mail remains Markdown, coordinators are human-mailbox unpinned, and protected-main release is deployment-controlled.

- [ ] **Step 1: Add prompt/doc-integrity regressions**

Pin exact generated strings for the two-channel authority split, unpinned
coordinators, no dual-write, strict runtime identity, private-key custody, and
protected-main runner boundary. Add a regression forbidding stale statements
that the bus is dormant or that scalar human cursors select bus unread.

- [ ] **Step 2: Run tests to prove RED**

```bash
env -u GIT_INDEX_FILE .venv/bin/python -m pytest tests/unit/test_protocol_prompt_sync.py tests/unit/test_protocol_doc_integrity.py -q
```

Expected: current docs still contain dormant/cutover-era claims and lack the
new authority matrix.

- [ ] **Step 3: Append the ADR and synchronize mirrors**

Do not edit ADR-010. The new ADR records that the user-principal triggered bus
activation on 2026-07-10, ends only the signed-bus deferral, and leaves the
pre-push-hook and Antigravity decisions unchanged.

Update ARCHITECTURE facts only after verifying each named source. Describe the
local signed-fact bus as live and remote CI/merge-gate activation as pending
until the external activation gate completes. Set its
`Last verified` SHA to the exact final implementation commit proven by `git
rev-parse --short HEAD`; do not use an arbitrary hex string.

- [ ] **Step 4: Run focused and full verification**

```bash
env -u GIT_INDEX_FILE .venv/bin/python -m pytest tests/unit/test_protocol_authority.py tests/unit/test_protocol_mailbox.py tests/unit/test_status.py tests/unit/test_check_coordination.py tests/unit/test_coordination_tooling.py tests/unit/test_governance_hardening.py tests/unit/test_threeway_activation_scripts.py tests/unit/test_threeway_cutover.py tests/unit/test_keys.py tests/unit/test_codex_protocol_model.py tests/unit/test_threeway_protected_main.py tests/unit/test_protocol_prompt_sync.py tests/unit/test_protocol_doc_integrity.py -q
env -u GIT_INDEX_FILE .venv/bin/python -m pytest tests/unit -q
env -u GIT_INDEX_FILE .venv/bin/python scripts/threeway_mechanism_ledger.py --check
env -u GIT_INDEX_FILE .venv/bin/python scripts/protocol_doctor.py --wave 2
env -u GIT_INDEX_FILE .venv/bin/python scripts/ci_smoke.py
```

Expected: zero failures, mechanism ledger exit `0`, protocol doctor `PASS`, and
smoke `OK`.

- [ ] **Step 5: Verify secret and side-effect boundaries**

```bash
env -u GIT_INDEX_FILE git ls-files '*.ed25519'
env -u GIT_INDEX_FILE git grep -nE '[0-9a-f]{64}' -- ':!coordination/threeway/keys/*.pub' ':!tests/**'
env -u GIT_INDEX_FILE git diff --check
env -u GIT_INDEX_FILE git status --short --branch
```

Expected: no tracked private key, no unexplained private-seed-shaped material,
clean diff check, and only intentional task paths before commit.

- [ ] **Step 6: Commit and request final operator verification**

```bash
env -u GIT_INDEX_FILE git commit -m "docs(protocol): record signed-bus authority"
```

Send one verify-request naming the complete Task 1–9 commit range, focused and
full evidence, local ref postchecks, excluded remote mutations, and expected
GO/NITS/FAIL.

---

## Deferred External Activation Gate

After Task 9 operator GO and trusted-code publication, the coordinator may
elect one executor for each external target:

1. publish the verified code/public-key trust root to `origin/main` after live
   divergence and ancestry preflight;
2. set GitHub repository variable `THREEWAY_BUS_LIVE=true`;
3. upload the CI private seed as Actions secret `THREEWAY_CI_KEY` without
   printing it;
4. deploy the protected merge-gate runner with the merge-gate key and protected
   credential;
5. trigger manual CI for an explicit integration ref/SHA and verify the signed
   `ci_result` on the authoritative remote bus;
6. verify the live protected-main ref equals the gate-completed SHA.

Every external action gets a distinct side-effect ID, one executor, observer
seats, stop conditions, and live postcheck. A success claim without the matching
token ID and target fails closeout.
