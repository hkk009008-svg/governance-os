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
- No route, lock, human/signed cursor, authoritative-ref, key, repository-variable,
  Actions-secret, runner, or remote-publication mutation occurs without both
  runtime eligibility and a current executable target-bound side-effect token.
- No push occurs before operator GO for the exact target commit.
- Closed historical artifacts remain readable; do not rewrite mailbox history.
- Every regression proves RED, GREEN, and a one-fact non-vacuity flip.
- Local cutover uses verified-exact resume only: while authority is `shadow`,
  a complete managed-ref set may be verified against the exact committed
  scratch-derived expected-post OID map in the activation manifest without ref rewrites before completing the `live`
  marker. Partial, extra, mismatched, changed-HEAD, or already-`live` state
  fails closed.
- Trust-root bootstrap/public-key commit and authoritative-ref cutover are
  separate target-bound executor-token actions. Task 6A cannot mutate refs or
  authority; Tasks 6B and 6C cannot generate or replace keys.

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
| `.claude/skills/four-seat-protocol/scripts/seat_status.py` | Claude mirror of channel-labeled seat orientation |
| `scripts/draft_handoff.py` | Pair-addressed or coordinator all-scope human-mailbox handoff context |
| `scripts/protocol_capacity.py` | Route and terminal-trigger validation with typed cursor envelopes |
| `scripts/codex_protocol_model.py` | Typed runtime identity and narrow-only override policy |
| `scripts/protocol_executor_token.py` | Single typed executable side-effect token parser and verifier |
| `scripts/codex_session_binding.py` | Versioned, non-rebindable local session identity binding |
| `.codex/hooks/update-state.sh` | Mutation-time identity validation before presence writes |
| `.agents/skills/four-seat-protocol/scripts/seat_status.py` | Channel-labeled seat orientation |
| `coordination/threeway/activation/pipeline-local-authority-2026-07-10.toml` | Secret-free activation intent, deterministic importer, exact expected ref OIDs, and resume boundary |
| `threeway/cutover.py` | Ref-bus projection, cursor initialization, teardown, and ready-to-flip result |
| `threeway/keys_bootstrap.py` | Idempotent, complete-roster key provisioning without re-key |
| `scripts/execute_threeway_cutover.sh` | Double-gated activation driver and preflight |
| `.github/workflows/ci.yml` | Trusted manual CI signer, inert until remote activation |
| `scripts/run_merge_gate.py` | Protected-main merge-gate runner with deployment attestation |

---

### Task 1: Add The Channel Authority Manifest And Typed Loader

**Owner:** Pair A director implementation; Pair A operator verification.

**Files:**
- Append: `DECISIONS.md`
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
- Records ADR-012, `Signed-bus activation and channel authority split`, before
  the manifest cites it. The ADR records the user-principal's activation
  decision, the shadow-to-live staged cutover, the continuing Markdown
  human-mailbox authority, and the separate external activation gate.
- The initial committed state is `human_mailbox.authority="live"` and `signed_facts.authority="shadow"`; Task 6C performs the only transition to signed-facts `live`.

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

- [ ] **Step 3: Append ADR-012 and add the initial authority manifest**

Append `ADR-012: Signed-bus activation and channel authority split` without
editing ADR-010. Record that the user-principal fired the signed-bus activation
trigger on 2026-07-10, that Tasks 1-5 remain a shadow/preflight phase until the
Task-6C executor token completes local cutover and postcheck, that Markdown
remains authoritative for human coordination with unpinned coordinators, and
that remote CI/merge-gate deployment remains separately gated. The ADR itself
does not authorize key, ref, secret, or remote mutation.

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
adr = "DECISIONS.md#adr-012-signed-bus-activation-and-channel-authority-split"
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
env -u GIT_INDEX_FILE git add -- DECISIONS.md coordination/authority.toml scripts/protocol_authority.py tests/unit/test_protocol_authority.py tests/unit/test_imports_smoke.py
env -u GIT_INDEX_FILE git diff --cached --check
env -u GIT_INDEX_FILE git commit -m "feat(protocol): add explicit channel authority model" -- DECISIONS.md coordination/authority.toml scripts/protocol_authority.py tests/unit/test_protocol_authority.py tests/unit/test_imports_smoke.py
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
- Modify: `.claude/skills/four-seat-protocol/scripts/seat_status.py`
- Modify: `scripts/draft_handoff.py`
- Modify: `scripts/protocol_capacity.py`
- Modify: `tests/unit/test_protocol_mailbox.py`
- Modify: `tests/unit/test_status.py`
- Modify: `tests/unit/test_check_coordination.py`
- Modify: `tests/unit/test_coordination_tooling.py`
- Modify: `tests/unit/test_governance_hardening.py`
- Modify: `tests/unit/test_threeway_activation_scripts.py`
- Modify: `tests/unit/test_seat_status_all.py`
- Modify: `tests/unit/test_check_go_schema.py`
- Create: `tests/unit/test_draft_handoff.py`
- Modify: `tests/unit/test_protocol_capacity.py`
- Modify: `coordination/mailbox/seen/director.txt`
- Modify: `coordination/mailbox/seen/director2.txt`
- Modify: `coordination/mailbox/seen/operator.txt`
- Modify: `coordination/mailbox/seen/operator2.txt`
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
- execute the same pair/coordinator behavior contract through both the
  `.agents` and `.claude` seat-status mirrors;
- render draft handoffs for coordinators as all-scope/unpinned without reading
  a cursor, while pair seats remain addressed and watermarked;
- treat ISO, `UNINITIALIZED`, and `all-scope-unpinned` cursor envelopes as
  terminal footer metadata rather than substantive Exact Next Trigger text.

- [ ] **Step 2: Run the focused tests to prove RED**

```bash
env -u GIT_INDEX_FILE .venv/bin/python -m pytest tests/unit/test_protocol_mailbox.py tests/unit/test_status.py tests/unit/test_check_coordination.py tests/unit/test_coordination_tooling.py tests/unit/test_governance_hardening.py tests/unit/test_threeway_activation_scripts.py tests/unit/test_seat_status_all.py tests/unit/test_draft_handoff.py tests/unit/test_protocol_capacity.py -q
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

Apply the identical policy in both seat-status mirrors. In
`scripts/draft_handoff.py`, pair seats collect only addressed events newer than
their human cursor, while coordinator aliases require no cursor and collect
all human-mailbox events with the `all-scope-unpinned` marker. In
`scripts/protocol_capacity.py`, exclude ISO, `UNINITIALIZED`, and
`all-scope-unpinned` `Cursor at send:` footer lines from substantive terminal
trigger detection; keep legacy numeric footer compatibility for historical
artifacts.

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
env -u GIT_INDEX_FILE .venv/bin/python -m pytest tests/unit/test_protocol_mailbox.py tests/unit/test_status.py tests/unit/test_check_coordination.py tests/unit/test_coordination_tooling.py tests/unit/test_governance_hardening.py tests/unit/test_threeway_activation_scripts.py tests/unit/test_seat_status_all.py tests/unit/test_check_go_schema.py tests/unit/test_draft_handoff.py tests/unit/test_protocol_capacity.py -q
```

Change only one coordinator to a cursor owner in the test fixture and confirm
the policy-disjointness test fails. Restore the policy and rerun GREEN.
Then flip the draft-handoff identity from coordinator to director and confirm a
foreign-seat event disappears, and flip a footer-only trigger to one
substantive sentence and confirm terminal-trigger detection changes from false
to true. Restore both fixtures and rerun GREEN.

- [ ] **Step 8: Review and commit Task 2**

Stage only the paths listed above, inspect the cached diff, and commit:

```bash
env -u GIT_INDEX_FILE git commit -m "fix(protocol): separate mailbox and signed-fact cursors"
```

---

### Task 3A: Add The Typed Runtime Identity And Authorization Foundation

**Owner:** Pair B director2 implementation in a separate worktree after Task 2; Pair B operator2 verification.

**Files:**
- Modify: `scripts/codex_protocol_model.py`
- Create: `scripts/protocol_executor_token.py`
- Modify: `scripts/protocol_capacity.py`
- Create: `tests/unit/test_codex_protocol_model.py`
- Create: `tests/unit/test_protocol_executor_token.py`
- Modify: `tests/unit/test_protocol_capacity.py`
- Modify: `tests/unit/test_codex_ledger_bridge.py`

**Interfaces:**
- Produces `RuntimeIdentityError(ValueError)`.
- Produces `SessionBindingView(Protocol)` with read-only `session_id`,
  `mode`, `concrete_seat`, and `role_family` attributes. Task 3B's concrete
  `SessionBinding` implements this protocol without requiring Task 3A to import
  a later module.
- Produces the complete interactive `RuntimeOperation` enum in Task 3A:

```python
class RuntimeOperation(str, Enum):
    ORIENT = "orient"
    REPOSITORY_MUTATE = "repository-mutate"
    MAIL_SEND = "mail-send"
    ROUTE_MUTATE = "route-mutate"
    HUMAN_CURSOR_CONSUME = "human-cursor-consume"
    LOCK_MUTATE = "lock-mutate"
    SIGNED_CURSOR_CONSUME = "signed-cursor-consume"
    SIGNED_FACT_EMIT = "signed-fact-emit"
    OPERATOR_VERDICT = "operator-verdict"
    REMOTE_PUBLISH = "remote-publish"
    TRUST_ROOT_BOOTSTRAP = "trust-root-bootstrap"
    AUTHORITY_CUTOVER = "authority-cutover"
```

- Pins the complete default actor-operation matrix:

```python
DEFAULT_RUNTIME_OPERATIONS = {
    "readiness-bridge": frozenset({
        RuntimeOperation.ORIENT,
    }),
    "subagent": frozenset({
        RuntimeOperation.ORIENT,
        RuntimeOperation.REPOSITORY_MUTATE,
    }),
    "director": frozenset({
        RuntimeOperation.ORIENT,
        RuntimeOperation.REPOSITORY_MUTATE,
        RuntimeOperation.MAIL_SEND,
        RuntimeOperation.HUMAN_CURSOR_CONSUME,
        RuntimeOperation.LOCK_MUTATE,
        RuntimeOperation.SIGNED_CURSOR_CONSUME,
        RuntimeOperation.SIGNED_FACT_EMIT,
    }),
    "operator": frozenset({
        RuntimeOperation.ORIENT,
        RuntimeOperation.REPOSITORY_MUTATE,
        RuntimeOperation.MAIL_SEND,
        RuntimeOperation.HUMAN_CURSOR_CONSUME,
        RuntimeOperation.LOCK_MUTATE,
        RuntimeOperation.SIGNED_CURSOR_CONSUME,
        RuntimeOperation.SIGNED_FACT_EMIT,
        RuntimeOperation.OPERATOR_VERDICT,
    }),
    "coordinator": frozenset({
        RuntimeOperation.ORIENT,
        RuntimeOperation.REPOSITORY_MUTATE,
        RuntimeOperation.MAIL_SEND,
        RuntimeOperation.ROUTE_MUTATE,
        RuntimeOperation.LOCK_MUTATE,
        RuntimeOperation.SIGNED_CURSOR_CONSUME,
        RuntimeOperation.SIGNED_FACT_EMIT,
    }),
}
TOKEN_ONLY_RUNTIME_OPERATIONS = frozenset({
    RuntimeOperation.REMOTE_PUBLISH,
    RuntimeOperation.TRUST_ROOT_BOOTSTRAP,
    RuntimeOperation.AUTHORITY_CUTOVER,
})
TOKEN_REQUIRED_INTERACTIVE_OPERATIONS = frozenset({
    RuntimeOperation.ROUTE_MUTATE,
    RuntimeOperation.LOCK_MUTATE,
    RuntimeOperation.HUMAN_CURSOR_CONSUME,
    RuntimeOperation.SIGNED_CURSOR_CONSUME,
})

RUNTIME_ACTOR_CLASS_BY_IDENTITY = {
    ("readiness-bridge", None): "readiness-bridge",
    ("subagent", None): "subagent",
    ("live-seat", "director"): "director",
    ("live-seat", "director2"): "director",
    ("live-seat", "operator"): "operator",
    ("live-seat", "operator2"): "operator",
    ("coordinator", "coordinator"): "coordinator",
    ("coordinator", "coordinator2"): "coordinator",
}
```

`REPOSITORY_MUTATE` never widens the identity's path-limited mutation scope.
The `(mode, concrete_seat)` map above is exhaustive: every tuple not listed is
invalid and receives no operation defaults. The two pair directors share the
director operation set, the two pair operators share the operator operation
set, and both coordinator spellings share the coordinator set without gaining
a human-mailbox cursor. The readiness and subagent modes never carry a
concrete seat.
Token-only operations belong to no default set and become eligible only when a
complete target-bound token names the same concrete executor, the user has
authorized the action, and all operation-specific gates pass. Readiness,
subagent, and mechanical principals can never receive token-only interactive
operations.

- Produces immutable `SideEffectExecutorToken` in
  `scripts/protocol_executor_token.py` and these single-source entry points:

```python
def load_side_effect_executor_token(
    root: Path, *, token_path: Path, side_effect_id: str
) -> SideEffectExecutorToken: ...

def require_side_effect_executor_token(
    root: Path,
    *,
    token_path: Path,
    side_effect_id: str,
    executor: str,
    target: str,
    command_class: str,
    expected_head: str,
    current_appointment_path: Path,
    newer_appointment_paths: Sequence[Path],
    target_satisfied: bool,
    failed_preflight: Sequence[str],
    triggered_stop_predicates: Sequence[str],
) -> SideEffectExecutorToken: ...
```

The frozen token records source path, ID, executor, normalized target, command
class, expected HEAD, preflight, stop predicates, postcheck, observer seats,
closeout owner, and non-goals. The loader requires a no-follow, committed
coordinator appointment under `coordination/mailbox/sent/` and selects exactly
one complete ID. The executable verifier rejects unknown/duplicate,
uncommitted, wrong executor/target/class/HEAD, non-current, superseded,
already-satisfied, failed-preflight, or triggered-stop state. It never treats
field presence or runtime-operation eligibility as execution authority.
`scripts/protocol_capacity.py` imports this parser for route validation and
deletes its parallel token parser.

- Produces immutable `RuntimeIdentity` with fields `mode`, `concrete_seat`,
  `behavior_source`, `capability_scope`, `mutation_scope`, `mailbox_policy`,
  `git_policy`, `verification_policy`, `routing_authority`,
  `publication_eligibility`, `identity_valid`, and `validation_errors`.
- Produces a derived `role_family` property. Pair mappings are
  `director -> director`, `director2 -> director`, `operator -> operator`,
  and `operator2 -> operator`; both coordinator aliases map to `coordinator`.
- Produces `resolve_runtime_identity(environ: Mapping[str, str], *, session_binding: SessionBindingView | None = None) -> RuntimeIdentity`. It returns an invalid object for malformed ambient state and never raises.
- Produces `require_runtime_identity(...) -> RuntimeIdentity` and
  `authorize_operation(..., operation: RuntimeOperation, expected_actor: str | None) -> RuntimeIdentity`; these raise `RuntimeIdentityError` with the same stable ordered error tuple.
- Keeps `infer_runtime_env()` as the compatibility renderer; it calls the resolver and adds `CODEX_IDENTITY_VALID` and `CODEX_IDENTITY_ERRORS`.
- Produces CLI validation: `scripts/codex_protocol_model.py --validate-runtime-env` exits `0` only for a valid identity.
- Adds `tests/unit/test_codex_protocol_model.py` to
  `CODEX_VERIFICATION_COMMANDS` and updates
  `tests/unit/test_codex_ledger_bridge.py` so `protocol_doctor.py` executes it.

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


@pytest.mark.parametrize(("seat", "role_family"), [
    ("director", "director"),
    ("director2", "director"),
    ("operator", "operator"),
    ("operator2", "operator"),
])
def test_explicit_role_matches_role_family_not_concrete_seat(seat, role_family):
    identity = model.resolve_runtime_identity({
        "CODEX_SEAT": seat,
        "CODEX_AGENT_ROLE": role_family,
    })
    assert identity.identity_valid is True
    assert identity.role_family == role_family


def test_override_cannot_widen_readiness_bridge():
    identity = model.resolve_runtime_identity({
        "CODEX_AUTHORITY_SCOPE": "seat-owned",
        "CODEX_VERIFICATION_POLICY": "independent-go-nits-fail",
    })
    assert identity.identity_valid is False
    assert "widen" in " ".join(identity.validation_errors)


DIRECTOR_EXPECTED = frozenset({
    "orient", "repository-mutate", "mail-send", "human-cursor-consume",
    "lock-mutate", "signed-cursor-consume", "signed-fact-emit",
})
OPERATOR_EXPECTED = DIRECTOR_EXPECTED | {"operator-verdict"}
COORDINATOR_EXPECTED = frozenset({
    "orient", "repository-mutate", "mail-send", "route-mutate",
    "lock-mutate", "signed-cursor-consume", "signed-fact-emit",
})
EXPECTED_BY_RUNTIME_IDENTITY = {
    ("readiness-bridge", None): frozenset({"orient"}),
    ("subagent", None): frozenset({"orient", "repository-mutate"}),
    ("live-seat", "director"): DIRECTOR_EXPECTED,
    ("live-seat", "director2"): DIRECTOR_EXPECTED,
    ("live-seat", "operator"): OPERATOR_EXPECTED,
    ("live-seat", "operator2"): OPERATOR_EXPECTED,
    ("coordinator", "coordinator"): COORDINATOR_EXPECTED,
    ("coordinator", "coordinator2"): COORDINATOR_EXPECTED,
}
ALL_RUNTIME_MODES = (
    "readiness-bridge", "live-seat", "coordinator", "subagent",
)
ALL_CONCRETE_SEATS = (
    None, "director", "director2", "operator", "operator2",
    "coordinator", "coordinator2",
)
ALL_OPERATION_VALUES = frozenset({
    "orient", "repository-mutate", "mail-send", "route-mutate",
    "human-cursor-consume", "lock-mutate", "signed-cursor-consume",
    "signed-fact-emit", "operator-verdict", "remote-publish",
    "trust-root-bootstrap", "authority-cutover",
})


def test_runtime_operation_enum_is_exact():
    assert {operation.value for operation in RuntimeOperation} == ALL_OPERATION_VALUES


@pytest.mark.parametrize(
    ("mode", "seat"),
    [
        (mode, seat)
        for mode in ALL_RUNTIME_MODES
        for seat in ALL_CONCRETE_SEATS
    ],
)
def test_complete_mode_seat_operation_matrix_is_exact(mode, seat):
    identity = _identity_for_mode_and_seat(mode, seat)
    expected = EXPECTED_BY_RUNTIME_IDENTITY.get((mode, seat))
    if expected is None:
        assert identity.identity_valid is False
        assert identity.validation_errors
        for value in ALL_OPERATION_VALUES:
            assert model.operation_is_allowed(
                identity, RuntimeOperation(value)
            ) is False
        return

    assert identity.identity_valid is True
    for value in ALL_OPERATION_VALUES:
        assert model.operation_is_allowed(
            identity, RuntimeOperation(value)
        ) is (value in expected)


def test_token_only_operations_have_no_default_actor():
    for mode, seat in EXPECTED_BY_RUNTIME_IDENTITY:
        identity = _identity_for_mode_and_seat(mode, seat)
        for operation in (
            RuntimeOperation.REMOTE_PUBLISH,
            RuntimeOperation.TRUST_ROOT_BOOTSTRAP,
            RuntimeOperation.AUTHORITY_CUTOVER,
        ):
            assert model.operation_is_allowed(identity, operation) is False
```

In `tests/unit/test_protocol_executor_token.py`, hard-code complete token
fixtures and cover absent/unreadable/symlinked/uncommitted paths, duplicate or
wrong IDs, missing fields, wrong executor/target/class/HEAD, stale and newer
appointments, satisfied target, failed preflight, and each triggered stop
predicate. Every rejection occurs before a supplied mutation callback can run.
`tests/unit/test_protocol_capacity.py` proves route validation and the runtime
verifier parse identical fields and reject the same malformed token.

Hook integration coverage belongs to Task 3B so this foundation commit remains
independently reviewable.
The modes, seats, operation values, and matrix expectations above are
hard-coded in the test module independently from production defaults; tests
must not import production enums or matrices to discover their cases. The
cross-product proves that every unlisted topology is invalid and has no
operation capability, while the enum-equality assertion makes addition or
deletion of an operation an explicit test change.

- [ ] **Step 2: Run tests to prove RED**

```bash
env -u GIT_INDEX_FILE .venv/bin/python -m pytest tests/unit/test_codex_protocol_model.py tests/unit/test_protocol_executor_token.py tests/unit/test_protocol_capacity.py tests/unit/test_codex_ledger_bridge.py -q
```

Expected: import/attribute failures for `RuntimeIdentity`,
`SessionBindingView`, `RuntimeOperation`, the resolver, and the typed token
module. Hook failures are not expected from this selector and belong to Task
3B.

- [ ] **Step 3: Implement `RuntimeIdentity` and strict resolution**

Resolve mode and role family from the concrete seat first. An explicit role
must equal the derived role family, never the concrete-seat spelling or
behavior source. Canonical behavior source is derived separately and must match
exactly when explicitly supplied.

Represent capability, mutation, mailbox, git, verification, and routing
policies as immutable token sets. An override is valid only when its requested
tokens are a subset of the resolved defaults; absent means no override, while
present-but-empty and unknown tokens are invalid. Publication eligibility may
only narrow from eligible to ineligible. Runtime eligibility never substitutes
for user consent, executor election, operator GO, or a target-bound
side-effect token.

Emit errors in this deterministic order: unknown values; topology mismatch;
role-family mismatch; behavior-source mismatch; missing or conflicting session
binding; unknown policy tokens; widening override; positional-actor mismatch;
missing operation capability.

Read-only rendering returns an invalid object with errors. The CLI validator and
mutation hooks treat any invalid object as fatal.

- [ ] **Step 4: Add strict and operation-aware entry points**

`require_runtime_identity()` and `authorize_operation()` must preserve the
resolver's ordered errors and add only actor/operation errors after the
identity checks. CLI success is quiet. CLI failure writes stable error codes to
stderr without dumping the environment and exits nonzero.

Implement the generic token module and move capacity validation onto it in the
same commit. Token paths are resolved beneath the primary checkout, opened
without following symlinks, and must be present in the exact committed HEAD.
Appointment freshness is determined from durable mailbox order, not caller
prose. `failed_preflight` and `triggered_stop_predicates` must both be empty;
the verifier does not attempt to reinterpret free-form safety text.

Update `CODEX_VERIFICATION_COMMANDS` in the same commit so the new identity
suite is part of the model-derived doctor gate.

- [ ] **Step 5: Prove GREEN and non-vacuity**

```bash
env -u GIT_INDEX_FILE .venv/bin/python -m pytest tests/unit/test_codex_protocol_model.py tests/unit/test_protocol_executor_token.py tests/unit/test_protocol_capacity.py tests/unit/test_codex_ledger_bridge.py -q
```

Change the mismatched `director2/operator2` fixture to
`director2/director` and confirm the invalid assertion fails, restore it, and
rerun GREEN. Separately widen one readiness capability token and confirm the
narrowing test fails. Then change one expected token HEAD and confirm the
executable verifier refuses before its mutation callback; restore and rerun
GREEN.

- [ ] **Step 6: Review and commit Task 3A**

```bash
env -u GIT_INDEX_FILE git commit -m "fix(protocol): reject mixed runtime identity"
```

---

### Task 3B: Bind Sessions And Enforce Identity Before Hook Mutation

**Owner:** Pair B director2 implementation after Task 3A GO; Pair B operator2 verification.

**Files:**
- Create: `scripts/codex_session_binding.py`
- Modify: `scripts/continuation_readiness.py`
- Modify: `scripts/seat_banner.py`
- Modify: `.env.example`
- Modify: `.gitignore`
- Modify: `coordination/README.md`
- Modify: `.codex/hooks/guard-git-index.sh`
- Modify: `.codex/hooks/update-state.sh`
- Modify: `.codex/hooks/session-smoke.sh`
- Modify: `.codex/hooks.json`
- Create: `tests/unit/test_codex_session_binding.py`
- Modify: `tests/unit/test_coordination_tooling.py`
- Modify: `tests/unit/test_protocol_prompt_sync.py`

**Interfaces:**
- Produces frozen `SessionBinding(schema_version, session_id, mode, concrete_seat, role_family, created_head)`.
- Produces `bind_session(root: Path, *, session_id: str, mode: str, concrete_seat: str | None, role_family: str | None) -> SessionBinding` and `load_session_binding(root: Path, session_id: str) -> SessionBinding`.
- Accepts only ASCII session IDs matching
  `\A[A-Za-z0-9][A-Za-z0-9._-]{0,127}\Z` and stores ignored local bindings
  beneath the primary checkout's `.codex/session-bindings/`.
- Resolves the primary root and every binding component with directory-relative,
  no-follow operations. It rejects traversal, absolute paths, Unicode
  lookalikes, overlong IDs, symlinked parents/base/final paths, and non-regular
  existing files.
- Publishes fully written and fsynced same-directory temporary content through
  an atomic hard-link/no-replace operation (or an equivalent no-replace
  primitive), then fsyncs the directory. Plain rename/`os.replace()` is
  forbidden because it can overwrite a racing binding.
- A binding cannot be silently rebound. Ambient environment and binding must
  agree. A racing or pre-existing identical binding is idempotent after a
  no-follow reread; a conflicting winner fails. A binding corroborates
  identity but a legacy
  `presence-seat.{session_id}` marker never establishes it.
- Hooks locate the primary checkout through the absolute git common directory
  and use that checkout's `.venv/bin/python`. Missing validation machinery is
  fatal for mutation gates.
- `guard-git-index.sh` is also the path-aware route-write gate for Bash, Edit,
  Write, and `apply_patch`. A literal intended target matching
  `coordination/mailbox/sent/*-coordinator-to-all-coordination.md` or
  `coordination/mailbox/sent/*-coordinator2-to-all-coordination.md` requires
  `RuntimeOperation.ROUTE_MUTATE` before the tool runs. Non-route mailbox
  paths remain under `MAIL_SEND`; ambiguous or dynamically hidden route paths
  fail closed rather than bypass the route gate.
- A route-shaped tool call also requires `CODEX_EXECUTOR_TOKEN_PATH` and
  `CODEX_SIDE_EFFECT_ID` from the bound session. The guard calls
  `require_side_effect_executor_token()` with the actual executor, normalized
  route target, route-mutation command class, current HEAD/appointment, and
  freshly evaluated preflight/stop results before allowing the tool.

- [ ] **Step 1: Write session-binding and zero-mutation regressions**

Cover create-once, identical idempotent bind, conflicting rebind refusal,
unknown values, missing `CODEX_SESSION_ID`, environment/binding conflict,
legacy-marker-only refusal, and isolated-worktree execution without a local
`.venv`. Snapshot the index lock, heartbeat, seat index, skip-worktree log,
state marker, and `STATE.md` before invalid-hook cases and assert byte-for-byte
identity afterward.

Add strict path/concurrency cases for empty, traversal, absolute, separator,
Unicode, and overlong IDs; symlinked binding directory/final file; non-regular
destinations; two processes racing identical bindings; and two processes
racing conflicting bindings. Assert exactly one complete regular file is
published, the identical loser succeeds idempotently, the conflicting loser
fails, and no path outside the binding directory changes.

Add path-aware route cases for each registered mutation tool: a bound
coordinator may pass the runtime route-capability gate for the exact route
pattern, while director, director2, operator, operator2, readiness, and
subagent identities fail before any route file, temporary file, index entry,
or hook-owned state changes. The positive case proves runtime eligibility
only; user consent, one target-bound route token, route validation, and commit
scope remain separate mandatory gates. Add absent/wrong/uncommitted/stale
`CODEX_EXECUTOR_TOKEN_PATH` and wrong/newer `CODEX_SIDE_EFFECT_ID` cases; each
must fail before the tool reads route content or mutates any snapshot.

- [ ] **Step 2: Run tests to prove RED**

```bash
env -u GIT_INDEX_FILE .venv/bin/python -m pytest tests/unit/test_codex_session_binding.py tests/unit/test_coordination_tooling.py tests/unit/test_protocol_prompt_sync.py -q
```

Expected: missing binding module/CLI and current hook mutations before identity
validation.

- [ ] **Step 3: Implement the tracked binding launcher**

Expose:

```bash
scripts/codex_session_binding.py bind --session-id "$CODEX_SESSION_ID" \
  --mode live-seat --seat director --role-family director
scripts/codex_session_binding.py validate --session-id "$CODEX_SESSION_ID"
```

The bind command validates through Task 3A before writing. It refuses a
different binding at the same path, uses the no-follow/no-replace publication
contract above, and never reads a legacy presence marker.
Update the startup docs and environment example with exact live-seat,
coordinator, readiness, and subagent invocations.

- [ ] **Step 4: Move authority enforcement before every hook-owned write**

Register identity validation in PreToolUse for Bash, Edit, Write, and
`apply_patch` through `guard-git-index.sh`. In `update-state.sh`, validate
again before stale-lock deletion or any heartbeat, index, skip-worktree,
marker, or `STATE.md` mutation. Marker fallback is removed.
`session-smoke.sh` remains explicitly diagnostic and fail-open; it is never
used as an authority gate.

For the exact coordinator-route path patterns above, the PreToolUse guard calls
`authorize_operation(..., RuntimeOperation.ROUTE_MUTATE,
expected_actor=identity.concrete_seat)` before allowing the tool. A generic
valid identity check is insufficient. It then requires the Task-3A executor
token using the session's explicit path/ID. Literal Bash route targets are
classified before execution; unclassifiable dynamic route writes are refused
with a stable error code.

- [ ] **Step 5: Prove GREEN and non-vacuity**

```bash
env -u GIT_INDEX_FILE .venv/bin/python -m pytest tests/unit/test_codex_session_binding.py tests/unit/test_coordination_tooling.py tests/unit/test_protocol_prompt_sync.py -q
```

Flip one bound director session to operator in the fixture and confirm the
environment/binding test fails. Then remove the route token path from a valid
coordinator fixture and confirm the hook refuses before reading the patch.
Restore both and rerun GREEN.

- [ ] **Step 6: Review and commit Task 3B**

```bash
env -u GIT_INDEX_FILE git commit -m "fix(protocol): bind runtime identity before hooks"
```

---

### Task 3C: Guard Interactive Mutators And Verdict Commands

**Owner:** Pair B director2 implementation after Task 3B GO; Pair B operator2 verification.

**Files:**
- Modify: `coordination/bin/send-event`
- Modify: `coordination/bin/consume-events`
- Modify: `coordination/bin/claim-lock`
- Modify: `coordination/bin/release-lock`
- Modify: `scripts/consume_bus.py`
- Modify: `scripts/seat_emit.py`
- Create: `tests/unit/test_runtime_operation_guards.py`
- Modify: `tests/unit/test_coordination_tooling.py`

**Interfaces:**
- Each command calls `authorize_operation()` before its first file, index, ref,
  or lock mutation.
- Route-shaped `send-event`, `claim-lock`, `release-lock`, `consume-events`,
  and `scripts/consume_bus.py` require explicit `--executor-token PATH` and
  `--side-effect-id ID` arguments. Each calls the Task-3A
  `require_side_effect_executor_token()` with its actual executor, normalized
  target, command class, current HEAD/appointment, target state, and freshly
  evaluated preflight/stop results.
- `coordination/bin/send-event` requires `MAIL_SEND` for every event. When and
  only when the validated bound sender is `coordinator` or `coordinator2`, the
  target is `all`, and the kind is `coordination`, it additionally requires
  `ROUTE_MUTATE` before reading stdin or creating a temporary file. Direct
  Edit/Write/`apply_patch` route creation remains covered by Task 3B's
  path-aware PreToolUse gate.
- Positional actor must equal the validated bound actor and never establishes
  identity.
- GO/NITS/FAIL emission requires an operator-family concrete seat with
  verification authority. Director, coordinator, readiness, and subagent
  identities cannot acquire verdict authority.

- [ ] **Step 1: Write actor/operation mismatch regressions**

Cover mail send, human cursor consume, lock claim/release, signed-fact cursor
consume, signed-fact emission, and GO/NITS/FAIL. For every denial, assert zero
mailbox, cursor, lock, ref, and index mutation. Include readiness, subagent,
coordinator-consume, director-verdict, and positional/bound-actor mismatch.

For route mutation, add a coordinator-positive fixture plus pair-seat,
readiness, and subagent denials for both `send-event` and the path-aware hook.
The negative cases snapshot the sent-mail directory, temporary-file namespace,
index, and hook-owned state and prove zero mutation. A non-route coordinator
status event proves that ordinary `MAIL_SEND` is not accidentally promoted to
`ROUTE_MUTATE`.

For route, lock claim/release, human cursor consume, and signed cursor consume,
parameterize absent/unreadable/uncommitted token paths, wrong or duplicate IDs,
wrong executor/target/class/HEAD, stale/current/newer appointment, already-
satisfied target, failed preflight, and every triggered stop predicate. Snapshot
stdin-read probes, temporary namespaces, mailbox, index, locks, both cursor
stores, and signed refs; every denial must leave all snapshots identical.

- [ ] **Step 2: Run tests to prove RED**

```bash
env -u GIT_INDEX_FILE .venv/bin/python -m pytest tests/unit/test_runtime_operation_guards.py tests/unit/test_protocol_executor_token.py tests/unit/test_coordination_tooling.py -q
```

Expected: current commands mutate from positional identity without a bound
operation authorization.

- [ ] **Step 3: Add operation guards at every entry point**

Use exact operation tokens `mail-send`, `human-cursor-consume`,
`route-mutate`, `lock-mutate`, `signed-cursor-consume`,
`signed-fact-emit`, and
`operator-verdict` from the Task-3A `RuntimeOperation` enum; Task 3C does not
redefine or modify that enum. Validate before reading stdin into a durable artifact,
creating temporary files, staging, committing, pushing, or updating refs.
Runtime authorization is followed by the executable Task-3A token check;
neither substitutes for user consent or operation-specific preflight.
`send-event` performs the route classification described above and requires
both `MAIL_SEND` and `ROUTE_MUTATE`; it never treats the positional `FROM`
value as proof of coordinator identity.

- [ ] **Step 4: Prove GREEN and non-vacuity**

```bash
env -u GIT_INDEX_FILE .venv/bin/python -m pytest tests/unit/test_runtime_operation_guards.py tests/unit/test_protocol_executor_token.py tests/unit/test_coordination_tooling.py -q
```

Change one expected actor to match the bound actor and confirm the mismatch
assertion fails. Then replace a valid token's expected HEAD with a sibling SHA
and confirm the command refuses before its stdin-read probe. Restore both and
rerun GREEN.

- [ ] **Step 5: Review and commit Task 3C**

```bash
env -u GIT_INDEX_FILE git commit -m "fix(protocol): authorize interactive mutations"
```

---

### Task 3D: Close Mechanical And Service-Principal Authority

**Owner:** Pair B director2 implementation after Task 3C GO; Pair B operator2 verification.

**Files:**
- Create: `scripts/protocol_principal.py`
- Modify: `scripts/chief_emit.py`
- Modify: `scripts/overseer_emit.py`
- Modify: `scripts/sign_ci_result.py`
- Modify: `scripts/run_merge_gate.py`
- Create: `tests/unit/test_service_principals.py`
- Modify: `tests/unit/test_codex_ledger_bridge.py`

**Interfaces:**
- Produces frozen
  `MechanicalPrincipal(principal_id, allowed_operations, signer_identity, executor_token_required, identity_valid, validation_errors)`.
- Exact operation map:

```python
SERVICE_OPERATIONS = {
    "overseer": frozenset({"emit-overseer-fact"}),
    "chief-gemini": frozenset({"emit-chief-fact"}),
    "chief-chatgpt": frozenset({"emit-chief-fact"}),
    "ci": frozenset({"sign-ci-result"}),
    "merge-gate": frozenset({"evaluate-merge-gate", "update-protected-main"}),
}
```

- Mechanical principals never synthesize `CODEX_SEAT` or interactive seat
  authority. Protected-main update additionally requires the exact
  target-bound executor token and protected runner credential.

- [ ] **Step 1: Write service-principal regressions**

Cover every principal/operation pair, unknown principals, cross-principal
operation attempts, signer mismatch, candidate-environment denial, missing
executor token for protected-main update, and zero fact/ref/main mutation on
denial.

- [ ] **Step 2: Run tests to prove RED**

```bash
env -u GIT_INDEX_FILE .venv/bin/python -m pytest tests/unit/test_service_principals.py tests/unit/test_codex_ledger_bridge.py -q
```

Expected: missing principal resolver and current entry points lacking the
typed operation check.

- [ ] **Step 3: Implement service-principal authorization**

Bind each entry point to the exact map above. `ci` may sign only a
`ci_result`; chiefs and overseer may emit only their own fact classes;
`merge-gate` may evaluate without publication credentials but cannot update
protected main without the separate token and credential. Add the new suite to
the model-derived doctor gate in the same commit.

- [ ] **Step 4: Prove GREEN and non-vacuity**

```bash
env -u GIT_INDEX_FILE .venv/bin/python -m pytest tests/unit/test_service_principals.py tests/unit/test_codex_ledger_bridge.py -q
```

Swap `ci` to `merge-gate` in one allowed-operation fixture and confirm the
assertion fails. Restore and rerun GREEN.

- [ ] **Step 5: Review and commit Task 3D**

```bash
env -u GIT_INDEX_FILE git commit -m "fix(protocol): bind service principals"
```

---

### Task 4: Harden The Signed-Bus Cutover For Two Independent Channels

**Owner:** Pair A director implementation; Pair A operator verification.

**Files:**
- Create: `threeway/activation.py`
- Modify: `threeway/cutover.py`
- Modify: `threeway/cursor_backfill.py`
- Modify: `threeway/legacy_projector.py`
- Create: `scripts/build_threeway_activation_manifest.py`
- Modify: `scripts/execute_threeway_cutover.sh`
- Modify: `scripts/protocol_capacity.py`
- Modify: `scripts/bus_unread.py`
- Create: `tests/unit/test_threeway_cutover.py`
- Create: `tests/unit/test_threeway_activation_manifest.py`
- Modify: `tests/unit/test_threeway_activation_scripts.py`
- Modify: `tests/unit/test_protocol_authority.py`
- Modify: `tests/unit/test_protocol_capacity.py`

**Interfaces:**
- `run_cutover()` preserves human `coordination/mailbox/seen/` bytes.
- Produces `initialize_signed_fact_cursors(store: RefEventStore, identities: Sequence[str], seq: int) -> dict[str, int]`.
- Produces frozen `ActivationManifest` from
  `coordination/threeway/activation/pipeline-local-authority-2026-07-10.toml`
  with schema version,
  resume policy, trusted-code/trust-root commits, authority
  before/after states, structured-source and projection digests, nonzero
  projected head, signing roster, public-registry digest, signed-cursor roster,
  Git object format, deterministic non-authoritative importer binding, ordered
  managed-ref records with object type/exact pre-run OID/exact expected-post
  OID, exact shadow-authority preimage/non-marker/expected-live digests, and
  rollback boundary.
- `CutoverResult` includes `projected_head: int`,
  `signed_cursor_identities: tuple[str, ...]`,
  `human_mailbox_unchanged: bool`, `ready_to_flip: bool`, and
  `verified_exact_resume: bool`.
- Consumes Task 3A's `scripts.protocol_executor_token` from route validation
  and the cutover driver; Task 4 must not redefine or wrap a second Markdown
  token parser. The executor token, not the manifest, binds the exact HEAD that
  contains the manifest and its digest.
- Replaces the ephemeral importer with principal
  `migration-importer:legacy:v1` and deterministic Ed25519 seed derivation from
  the public domain-separated context
  `Pipeline/threeway/legacy-import/v1/pipeline-local-authority-2026-07-10`.
  Derive the 32-byte seed exactly as
  `SHA256(UTF8("threeway/non-authoritative-legacy-importer/v1") || 0x00 ||
  UTF8(key_context))` and load it with
  `Ed25519PrivateKey.from_private_bytes()`.
  The manifest records the derivation profile, context, and public key. This
  importer is outside the trusted signing roster and can sign only non-
  load-bearing `event_sent` carriers.
- Produces in `threeway/activation.py`
  `compare_and_swap_authority_marker(path: Path, *, expected_bytes: bytes,
  expected_state: ChannelAuthority = ChannelAuthority.SHADOW,
  new_state: ChannelAuthority = ChannelAuthority.LIVE) -> None` using no-follow
  access, an exclusive sibling lock, exact reread under lock, a one-field
  transformation, fsynced same-directory temporary output, atomic replacement,
  and directory fsync. Every sanctioned marker writer uses this helper.
- `scripts/execute_threeway_cutover.sh --preflight` performs no writes and exits nonzero on partial key registries, dirty tracked files, pre-existing unexplained refs, or non-shadow authority.
- All driver modes require `--activation-manifest`, `--executor-token`, and
  `--side-effect-id`. `--yes` is the sole mode permitted to mutate managed refs
  or authority; `--postcheck` is a separate finalized-state mode that may
  append only the named secret-free evidence file and cannot change refs,
  authority, keys, cursors, the activation manifest, the index, or staging. `--yes` and
  `--postcheck` require `--evidence-file`; `--preflight` accepts no evidence
  output path and writes nothing. Mutation mode
  revalidates the clean tracked tree/index, token-bound HEAD and current
  appointment, exact manifest bytes/digest, exact shadow-authority preimage and
  non-marker bytes, public-registry digest and pair correspondence,
  trusted-code/trust-root commits, source/projection/importer/roster bindings,
  exact managed refs, GO artifacts/reviewed SHAs, concrete executor, and every
  stop predicate immediately before the cooperative compare-and-swap marker
  change.

- [ ] **Step 1: Write cutover regressions**

Tests must snapshot every `seen/*.txt` byte before `run_cutover()` and assert the
same bytes after success and injected failure. Add cases for:

- missing live/shadow events ref reported unavailable, not empty;
- all signed-fact cursor refs initialized to the explicit projected head;
- partial ref creation torn down to the exact pre-run snapshot;
- partial public-key registry rejected by preflight;
- a second invocation with `shadow` authority and a complete managed-ref set
  exactly matching the activation manifest performs no ref rewrite and reports
  `verified_exact_resume=True`;
- partial, extra, mismatched, changed-HEAD, changed-projection,
  changed-trust-root, or already-`live` repeated invocation refused;
- initializer, snapshot, rollback, and postcheck using the identical ordered
  signed-cursor roster
  `director,director2,operator,operator2,coordinator,coordinator2`;
- wrong or ambiguous side-effect ID, executor, target, action class, expected
  HEAD, manifest digest, GO artifact, reviewed SHA, or newer appointment
  refused before writes;
- two fresh subprocesses and scratch repositories with the same source,
  object format, and importer context produce byte-identical expected-post OID
  maps; a one-byte context change changes the expected events OID;
- the measurement builder snapshots live `refs/threeway/*` before and after
  scratch projection and proves byte-for-byte identity;
- substituting each one of the seven expected-post OIDs independently causes
  verified-exact resume to refuse without a ref rewrite;
- parameterized mid-cutover race injection after fresh managed-ref creation or
  verified-exact-resume verification, but before the `live` marker, for each of:
  tracked-tree change, staged-index change, HEAD change, newer appointment,
  activation-manifest byte/digest change, shadow-authority non-marker change,
  authority state change, public-registry digest/pair change, trusted-code or
  trust-root change, structured-source or projection change, importer binding
  change, signing/cursor-roster change, one managed-ref OID change, GO artifact
  or reviewed-SHA change, and triggered stop predicate. Every injection must
  leave authority `shadow`. Fresh-cutover failures restore the exact pre-run ref snapshot,
  deleting only refs absent before the attempt; exact-resume failures leave
  every matching pre-existing ref OID unchanged and perform no ref rewrite.
  Removing the single injected change must let the same fixture reach `live`;
- `--preflight` producing no refs, files, cursor changes, or staging.

- [ ] **Step 2: Run tests to prove RED**

```bash
env -u GIT_INDEX_FILE .venv/bin/python -m pytest tests/unit/test_threeway_cutover.py tests/unit/test_threeway_activation_manifest.py tests/unit/test_threeway_activation_scripts.py tests/unit/test_protocol_authority.py tests/unit/test_protocol_capacity.py -q
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

- [ ] **Step 4: Add the activation manifest and executor-token contract**

`scripts/build_threeway_activation_manifest.py` is the committed R-MEASURE
instrument. It computes the structured-source cutoff/digest, projection digest,
nonzero projected head, public-registry digest, rosters, importer binding,
authority preimage/live digests, and ordered managed refs. In two fresh scratch
repositories it derives the exact events commit OID plus all six cursor blob
OIDs without creating or updating a live ref. It snapshots live refs before
and after and writes the secret-free TOML plus a citable log under
`logs/threeway-activation-pipeline-local-authority-2026-07-10/`. Ad-hoc
numbers are forbidden.

`load_activation_manifest()` rejects unknown versions/fields, duplicate or
unordered rosters, a zero projected head, ref names outside the declared events
ref/cursor namespace, a managed-ref set that differs from events plus the
cursor roster, wrong object types or object-format lengths, duplicate/missing
pre/post OIDs, scratch-process disagreement, and any digest or HEAD mismatch.

The token loader selects exactly one complete standard token by side-effect ID
and additionally requires the activation-manifest path and digest, expected
HEAD, required GO artifact paths and reviewed SHAs, concrete executor, and
cutover action class.

- [ ] **Step 5: Add pure preflight and verified-exact resume**

The preflight checks:

```text
authority manifest is human live / signed shadow
working tree has no tracked changes
public-key registry is either empty or complete for the exact signing roster
private keystore is outside the repository
refs/threeway/events and signed cursor refs are all absent for a fresh cutover,
or all present with exact independently measured expected-post manifest OIDs
for verified-exact resume
focused tests and operator GO are named in the executor token before --yes
```

Fresh cutover may create refs. Verified-exact resume is read-only over refs and
may only enable the later authority-marker step. Partial/extra/mismatched refs
and already-live authority always refuse. Automatic rollback restores each
managed ref to its exact pre-run OID and deletes only refs absent before the
attempt; it is permitted only before the durable `live` marker.

- [ ] **Step 6: Prove GREEN and non-vacuity**

```bash
env -u GIT_INDEX_FILE .venv/bin/python -m pytest tests/unit/test_threeway_cutover.py tests/unit/test_threeway_activation_manifest.py tests/unit/test_threeway_activation_scripts.py tests/unit/test_protocol_authority.py tests/unit/test_protocol_capacity.py -q
```

Change one expected signed cursor from the projected head to `0`; confirm the
test fails. Then change one exact-resume ref OID and confirm resume refuses.
Change one importer-context byte and confirm the expected events OID and
manifest validation change. Restore all three and rerun GREEN. Disable one mid-cutover race injection and
confirm the same fixture reaches `live`; restore the injection and confirm the
driver fails closed with the mode-specific ref disposition above.

- [ ] **Step 7: Review and commit Task 4**

```bash
env -u GIT_INDEX_FILE git commit -m "fix(threeway): separate bus cutover from human cursors"
```

---

### Task 5: Make Key Bootstrap Idempotent And Complete-Roster Safe

**Owner:** Pair B director2 implementation; Pair B operator2 verification.

**Files:**
- Modify: `threeway/keys_bootstrap.py`
- Modify: `threeway/keys.py`
- Modify: `tests/unit/test_keys.py`
- Modify: `tests/unit/test_threeway_activation_scripts.py`

**Interfaces:**
- Produces `expected_public_key_names(seats: Sequence[str] = SEATS) -> frozenset[str]`.
- Produces `registry_state(registry: Path, seats: Sequence[str] = SEATS) -> Literal["empty", "complete"]`; partial/extra registries raise `RegistryStateError`.
- Bootstrap refuses to overwrite any existing complete trust root and verifies each public/private pair instead.
- Production CLI binds the exact ordered 11-principal roster and rejects a
  subset or reordered `--seats` value. Pure helpers may accept an injected
  roster only for hermetic tests.
- Tests define this independent literal rather than deriving expectations from
  production `SEATS`:

```python
EXPECTED_SIGNING_ROSTER = (
    "director",
    "operator",
    "coordinator",
    "director2",
    "operator2",
    "coordinator2",
    "overseer",
    "ci",
    "merge-gate",
    "chief-gemini",
    "chief-chatgpt",
)
```
- Produces `load_private(identity: str, *, keystore: Path | None = None)`;
  an explicit keystore always wins over the environment fallback.
- Public and private trees are independently classified as `empty`,
  `complete`, or invalid. Only `empty/empty -> generate-complete` and
  `complete/complete -> verify-and-no-op` are legal.
- Production CLI modes are `--preflight`, `--verify`, and the sole mutating
  flag `--yes`. Every mode requires explicit `--registry`, `--keystore`, and
  `--evidence-dir` paths.

- [ ] **Step 1: Write key-registry regressions**

Add tests proving:

- `tuple(SEATS) == EXPECTED_SIGNING_ROSTER` and an empty registry generates
  exactly those ordered identities;
- a complete matching registry/keystore is a no-op and preserves every byte;
- a partial registry fails before writing;
- an extra public key fails before writing;
- an empty or metadata-only public registry with any canonical private key
  fails before writing;
- a complete public registry with a missing, partial, or extra private tree
  fails before writing;
- a public/private mismatch fails before writing;
- production subset/reordered roster input fails before writing;
- lexical or resolved in-repo keystore, symlink re-entry, and symlink key files
  fail before directory creation;
- complete matching state preserves every public/private byte and mtime;
- explicit keystore loading ignores a conflicting environment keystore;
- injected generation failure restores both trees to their exact pre-run state;
- no private-key filename appears below the repository root.

- [ ] **Step 2: Run tests to prove RED**

```bash
env -u GIT_INDEX_FILE .venv/bin/python -m pytest tests/unit/test_keys.py tests/unit/test_threeway_activation_scripts.py -q
```

Expected: the current bootstrap overwrites complete keys and accepts partial
state when called directly.

- [ ] **Step 3: Implement fail-closed registry inspection**

Before any `mkdir`, generation, or write, validate the exact public and private
filename sets, lexical and resolved off-repo containment, symlink-free key
files, file syntax, and pair correspondence. Registry metadata without
`*.pub` is empty; any mixed, partial, extra, malformed, or mismatched state is
invalid. For complete state, verify every pair and preserve bytes and mtimes.

For empty state, generate the full roster into same-parent temporary
directories, set private files owner-only, verify all pairs, then atomically
install the two complete trees. On any failure, restore the exact pre-run
trees. Never print private material or a private path containing secret data.

- [ ] **Step 4: Prove GREEN and non-vacuity**

```bash
env -u GIT_INDEX_FILE .venv/bin/python -m pytest tests/unit/test_keys.py tests/unit/test_threeway_activation_scripts.py -q
```

Replace one public key with another valid 64-hex key and confirm the
public/private matching test fails. Then point the keystore through a symlink
back into the repo and confirm containment fails before directory creation.
Finally remove `chief-chatgpt` from production `SEATS` while leaving the
independent expected literal unchanged and confirm the roster contract fails.
Restore all three mutations and rerun GREEN.

- [ ] **Step 5: Review and commit Task 5**

```bash
env -u GIT_INDEX_FILE git commit -m "fix(threeway): make key bootstrap fail closed"
```

---

### Task 6A: Provision And Verify The Public Trust Root

**Owner:** One executor elected by a later coordinator route; all other seats observer-only. Pair B operator2 verifies the trust-root commit.

**Files and state:**
- Create: `coordination/threeway/keys/*.pub` for the exact 11-seat roster
- Create: `logs/threeway-trust-root-pipeline-local-authority-2026-07-10/preflight.txt`
- Create: `logs/threeway-trust-root-pipeline-local-authority-2026-07-10/postcheck.txt`
- Write private keys only to the approved off-repo seat-local keystore
- Preserve `coordination/authority.toml` at signed-facts `shadow`
- Preserve every `refs/threeway/*` ref byte-for-byte

**Future side-effect token contract — this plan does not authorize execution:**

The later route instantiates side-effect ID
`threeway-trust-root-bootstrap-pipeline-local-authority-2026-07-10` with
exactly one concrete executor. Its target is only the off-repo keystore,
`coordination/threeway/keys/*.pub`, and secret-free trust-root logs. Its
allowed command class is the Task-5 bootstrap CLI plus strict-pathspec
public-key/log commit. Preflight requires Tasks 1–5 GO, a clean exact HEAD,
legal `empty/empty` or `complete/complete` key state, and an off-repo
keystore. Postcheck requires the complete matching roster, private-key absence
from git/repo/logs, unchanged refs, and `shadow` authority. Non-goals include
ref mutation, authority flip, cutover, remote settings, push, locks, cursor
consume, checkout refresh, and production generation.

- [ ] **Step 1: Re-run trust-root preflight immediately before mutation**

```bash
env -u GIT_INDEX_FILE git log --oneline -3
env -u GIT_INDEX_FILE git status --short --branch
env -u GIT_INDEX_FILE git for-each-ref --format='%(refname) %(objectname)' 'refs/threeway/'
env -u GIT_INDEX_FILE .venv/bin/python -m threeway.keys_bootstrap \
  --registry coordination/threeway/keys \
  --keystore "$THREEWAY_KEYSTORE" \
  --evidence-dir logs/threeway-trust-root-pipeline-local-authority-2026-07-10 \
  --preflight
```

Expected: exact routed HEAD, clean tracked tree, legal empty/empty or
complete/complete state, off-repo keystore, unchanged refs, `shadow` authority,
and no state mutation.

- [ ] **Step 2: Generate or verify the complete trust root**

Run only as the later token's executor:

```bash
env -u GIT_INDEX_FILE .venv/bin/python -m threeway.keys_bootstrap \
  --registry coordination/threeway/keys \
  --keystore "$THREEWAY_KEYSTORE" \
  --evidence-dir logs/threeway-trust-root-pipeline-local-authority-2026-07-10 \
  --yes
```

The production CLI uses the exact 11-principal roster. It either atomically
generates complete empty state or verifies complete matching state without
changing bytes or mtimes. Do not copy private keys into the repository,
staging area, logs, or terminal output.

- [ ] **Step 3: Capture secret-free trust-root postcheck**

```bash
env -u GIT_INDEX_FILE .venv/bin/python -m threeway.keys_bootstrap \
  --registry coordination/threeway/keys \
  --keystore "$THREEWAY_KEYSTORE" \
  --evidence-dir logs/threeway-trust-root-pipeline-local-authority-2026-07-10 \
  --verify
env -u GIT_INDEX_FILE git ls-files 'coordination/threeway/keys/*.pub'
env -u GIT_INDEX_FILE git ls-files '*.ed25519'
env -u GIT_INDEX_FILE git status --short --untracked-files=all | rg '\.ed25519$' && exit 1 || true
env -u GIT_INDEX_FILE git for-each-ref --format='%(refname) %(objectname)' 'refs/threeway/'
env -u GIT_INDEX_FILE git diff -- coordination/authority.toml coordination/mailbox/seen
```

Expected: exactly 11 matching public/private pairs, 11 public files and no
private files under the repo, no private path/material in logs, unchanged refs,
unchanged human cursors, and unchanged `shadow` authority.

- [ ] **Step 4: Commit only the public trust root and evidence**

```bash
env -u GIT_INDEX_FILE git add -- coordination/threeway/keys \
  logs/threeway-trust-root-pipeline-local-authority-2026-07-10
env -u GIT_INDEX_FILE git diff --cached --check
env -u GIT_INDEX_FILE git commit -m "feat(threeway): provision public trust root"
```

Inspect every staged path and diff before commit. Private filenames, authority
changes, refs, and cursor changes are a hard stop.

- [ ] **Step 5: Send one trust-root verify-request**

The request names the commit, exact roster and public-registry digest,
public/private correspondence proof, containment and idempotence selectors,
private-key absence proof, unchanged refs/authority/cursors, and excluded
side effects. Operator2 returns GO/NITS/FAIL. Task 6B cannot start before GO.

---

### Task 6B: Freeze The Secret-Free Activation Manifest

**Owner:** Pair A director implementation after Task 6A GO; Pair A operator verification.

**Files and state:**
- Create: `coordination/threeway/activation/pipeline-local-authority-2026-07-10.toml`
- Create: `logs/threeway-activation-pipeline-local-authority-2026-07-10/manifest.txt`
- Preserve `coordination/authority.toml` at signed-facts `shadow`
- Preserve the public/private key trees and every `refs/threeway/*` ref

**Interfaces:**
- The manifest has `schema_version = 1` and
  `resume_policy = "verified-exact"`.
- It records exact trusted-code and Task-6A trust-root commits,
  structured-source cutoff/digest, projection digest, nonzero projected head,
  authority before/after states, exact signing and signed-cursor rosters,
  public-registry digest, Git object format, the pinned non-authoritative
  importer principal/derivation/context/public key, events/cursor namespace,
  exact authority shadow-preimage/non-marker/expected-live digests, and an
  ordered managed-ref table. Every managed-ref record names object type,
  exact pre-run OID or `ABSENT`, and the independently scratch-derived exact
  expected-post OID. It also records the rollback boundary.
- It contains no self-referential HEAD. The later Task-6C executor token binds
  the exact Task-6B commit plus the manifest digest.

- [ ] **Step 1: Generate the manifest with the committed measurement tool**

```bash
env -u GIT_INDEX_FILE .venv/bin/python scripts/build_threeway_activation_manifest.py \
  --activation-id pipeline-local-authority-2026-07-10 \
  --trust-root-commit "$(env -u GIT_INDEX_FILE git rev-parse HEAD)" \
  --importer-principal migration-importer:legacy:v1 \
  --importer-key-context Pipeline/threeway/legacy-import/v1/pipeline-local-authority-2026-07-10 \
  --scratch-runs 2 \
  --output coordination/threeway/activation/pipeline-local-authority-2026-07-10.toml \
  --evidence-dir logs/threeway-activation-pipeline-local-authority-2026-07-10
```

The tool, not ad-hoc shell or REPL code, produces every digest/count and the
citable measurement log. It creates both projections in fresh temporary Git
repositories with the live repository's object format and fixed Git metadata,
requires byte-identical seven-ref OID maps across separate subprocesses, and
proves the live ref snapshot is unchanged. The deterministic importer is not a
secret and is never accepted for a load-bearing event.

- [ ] **Step 2: Validate the generated manifest without mutation**

```bash
env -u GIT_INDEX_FILE .venv/bin/python -m threeway.activation validate \
  --manifest coordination/threeway/activation/pipeline-local-authority-2026-07-10.toml \
  --repo .
```

Validation must report the fresh-cutover state, independently rebuild the
expected-post map in a new scratch process, and leave live refs, keys,
authority, cursors, index, and staging unchanged. Executor-token validation
belongs to Task 6C after the manifest commit and digest exist.

- [ ] **Step 3: Commit the manifest and measurement**

```bash
env -u GIT_INDEX_FILE git add -- \
  coordination/threeway/activation/pipeline-local-authority-2026-07-10.toml \
  logs/threeway-activation-pipeline-local-authority-2026-07-10/manifest.txt
env -u GIT_INDEX_FILE git diff --cached --check
env -u GIT_INDEX_FILE git commit -m "chore(threeway): freeze local activation manifest"
```

- [ ] **Step 4: Send one manifest verify-request**

Operator verifies the exact commit, manifest schema/digests/rosters/ref map,
two-process measurement provenance, deterministic importer separation from the
trusted roster, exact expected-post OIDs, unchanged live refs, Task-6A
trust-root binding, preflight non-mutation, and `shadow` authority. Task 6C
waits for GO and a new user-authorized executor token binding this exact commit
and manifest digest.

---

### Task 6C: Execute The Local Authority Flip

**Owner:** One executor elected by a later coordinator route; all other seats observer-only. Pair A operator verifies the resulting commit and refs.

**Files and state:**
- Modify: `coordination/authority.toml` (`signed_facts.authority` from `shadow` to `live` only after successful cutover or verified-exact resume)
- Create: `logs/threeway-activation-pipeline-local-authority-2026-07-10/cutover.txt`
- Create or verify exactly: `refs/threeway/events` and the six
  `refs/threeway/cursors/*` refs named by the activation manifest
- Treat public registry, off-repo private keystore, activation manifest, and
  human-mailbox cursor files as read-only inputs

**Future side-effect token contract — this plan does not authorize execution:**

The later route instantiates side-effect ID
`threeway-local-authority-flip-pipeline-local-authority-2026-07-10` with
one concrete executor. It binds the exact Task-6B HEAD, activation-manifest
path/digest, Task-6A and Task-6B GO artifacts and reviewed SHAs, target managed
refs plus the sole authority-marker edit, fresh/exact-resume action class,
preflight, stop-if-newer-appointment-or-state-change, exact-ref postcheck,
observer seats, coordinator closeout, and non-goals. It cannot generate or
replace keys, push, mutate remote settings, consume mail, claim locks, refresh
checkouts, deploy runners, or update protected main.

The authorizing route exports its concrete mailbox path as
`TASK6C_TOKEN_ROUTE`. The executor refuses to run unless that variable is
nonempty, names a committed coordinator-to-all route, and contains the exact
side-effect ID below. The driver calls Task 3A's
`require_side_effect_executor_token()`; field presence or route validation
alone is insufficient.

- [ ] **Step 1: Re-run exact live preflight**

```bash
env -u GIT_INDEX_FILE git log --oneline -3
env -u GIT_INDEX_FILE git status --short --branch
test -n "$TASK6C_TOKEN_ROUTE"
test -f "$TASK6C_TOKEN_ROUTE"
env -u GIT_INDEX_FILE scripts/execute_threeway_cutover.sh \
  --preflight \
  --activation-manifest coordination/threeway/activation/pipeline-local-authority-2026-07-10.toml \
  --executor-token "$TASK6C_TOKEN_ROUTE" \
  --side-effect-id threeway-local-authority-flip-pipeline-local-authority-2026-07-10
```

Expected: exact token-bound HEAD and manifest digest, `shadow` authority,
complete trust root, GO artifacts, off-repo keystore, and either all managed
refs absent or the complete exact expected-post manifest ref set. No state
changes.

- [ ] **Step 2: Execute fresh cutover or verified-exact resume**

```bash
env -u GIT_INDEX_FILE scripts/execute_threeway_cutover.sh \
  --yes \
  --activation-manifest coordination/threeway/activation/pipeline-local-authority-2026-07-10.toml \
  --executor-token "$TASK6C_TOKEN_ROUTE" \
  --side-effect-id threeway-local-authority-flip-pipeline-local-authority-2026-07-10 \
  --evidence-file logs/threeway-activation-pipeline-local-authority-2026-07-10/cutover.txt
```

Fresh mode creates the exact managed-ref set. Verified-exact resume verifies
every existing OID against the independently scratch-derived expected-post map
and performs no ref rewrite. Partial, extra, substituted, mismatched,
changed-HEAD/digest, or already-`live` state refuses. After fresh creation or
exact-resume verification, the driver rechecks the clean tracked tree and
index; token-bound HEAD/current appointment; exact manifest bytes/digest;
shadow-authority preimage, state, and non-marker bytes; public registry and
pair correspondence; trusted-code/trust-root commits; source, projection,
importer, and roster bindings; every expected ref; GO/reviewed-SHA evidence;
and all stop predicates. It then uses
`compare_and_swap_authority_marker()` to change only
`signed_facts.authority = "live"` under the no-follow cooperative lock. It writes secret-free command inputs,
mode, ref OIDs, validation results, and marker result to `cutover.txt`.

Inject a change to each revalidated input after ref readiness/exact-resume
verification and before the locked preimage comparison. Every case refuses the
marker. Fresh mode restores the exact pre-run ref map; exact-resume mode leaves
all pre-existing matching refs untouched. Removing each one-fact injection
must let the same fixture reach `live`.

- [ ] **Step 3: Revalidate the driver-finalized live state**

```bash
env -u GIT_INDEX_FILE scripts/execute_threeway_cutover.sh \
  --postcheck \
  --activation-manifest coordination/threeway/activation/pipeline-local-authority-2026-07-10.toml \
  --executor-token "$TASK6C_TOKEN_ROUTE" \
  --side-effect-id threeway-local-authority-flip-pipeline-local-authority-2026-07-10 \
  --evidence-file logs/threeway-activation-pipeline-local-authority-2026-07-10/cutover.txt
```

Postcheck cannot change refs, authority, keys, cursors, or the index. It fails
unless the same token-bound HEAD and manifest digest remain current, the exact
managed refs match, the marker is `live`, every other authority-manifest byte
is unchanged, and no newer appointment exists; only the designated
`cutover.txt` evidence append is permitted.

- [ ] **Step 4: Capture secret-free postcheck**

```bash
env -u GIT_INDEX_FILE git for-each-ref --format='%(refname) %(objectname)' 'refs/threeway/'
env -u GIT_INDEX_FILE .venv/bin/python -c 'from pathlib import Path; from scripts.protocol_authority import load_authority, validate_authority_runtime; m=load_authority(Path(".")); print(validate_authority_runtime(Path("."), m))'
env -u GIT_INDEX_FILE git ls-files 'coordination/threeway/keys/*.pub'
env -u GIT_INDEX_FILE git ls-files '*.ed25519'
env -u GIT_INDEX_FILE git diff -- coordination/mailbox/seen
```

Expected: exact manifest-matched events/cursor refs, authority validation `()`,
11 public keys, no private keys, and unchanged human cursors.

- [ ] **Step 5: Commit the live marker and secret-free cutover evidence**

```bash
env -u GIT_INDEX_FILE scripts/execute_threeway_cutover.sh \
  --postcheck \
  --activation-manifest coordination/threeway/activation/pipeline-local-authority-2026-07-10.toml \
  --executor-token "$TASK6C_TOKEN_ROUTE" \
  --side-effect-id threeway-local-authority-flip-pipeline-local-authority-2026-07-10 \
  --evidence-file logs/threeway-activation-pipeline-local-authority-2026-07-10/cutover.txt
env -u GIT_INDEX_FILE git add -- coordination/authority.toml \
  logs/threeway-activation-pipeline-local-authority-2026-07-10/cutover.txt
env -u GIT_INDEX_FILE git diff --cached --check
env -u GIT_INDEX_FILE git commit -m "feat(threeway): activate signed fact bus"
```

- [ ] **Step 6: Send one authority-flip verify-request**

The request names the exact commit/range, activation manifest and token,
fresh/resume mode, ref OIDs, projection evidence, unchanged human cursors,
private-key absence, authority validation, and every excluded remote side
effect. Operator returns GO/NITS/FAIL before any remote activation.

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
- Verify the Task-1 ADR titled `Signed-bus activation and channel authority split` remains true; do not append a duplicate.
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

- [ ] **Step 3: Verify the activation ADR and synchronize mirrors**

Do not edit ADR-010 or the Task-1 ADR-012. Verify ADR-012 records that the
user-principal triggered bus activation on 2026-07-10, ends only the signed-bus
deferral, and leaves the pre-push-hook and Antigravity decisions unchanged.

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
