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
- Task 2 corrective topology preserves the failed candidate as immutable
  review provenance: `78b48ed -> e43acc2 -> 205f077 -> <corrective-child>`.
  Do not amend, reset, rebase, or rewrite any of those three existing commits.
- The corrective child commits
  `human_mailbox.cursor_envelope_schema = "typed-v1"` with the typed generator.
  Numeric mail remains legacy only when the unique marker-introduction commit
  is not an ancestor of its unique introducing commit and current bytes equal
  the introducing blob; post-marker or
  uncommitted numeric mail fails closed.

## File And Interface Map

| File | Responsibility |
|---|---|
| `coordination/authority.toml` | Committed channel authority and activation state |
| `scripts/protocol_authority.py` | Typed manifest loader and live-state validation |
| `scripts/protocol_mailbox.py` | Human-mailbox addressability, cursor, receipt, and all-scope policy |
| `scripts/status.py` | Human-mailbox unread collection independent of signed-bus state |
| `scripts/check_coordination.py` | Fail-closed human-mailbox cursor and event validation |
| `scripts/mailbox_monitor.py` | Read-only human-mailbox and signed-fact observability |
| `scripts/protocol_effectiveness_report.py` | Effectiveness metrics derived from canonical human-mailbox policy |
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
| `.claude/hooks/update-state.sh` | Claude mirror using the same canonical mailbox-state helper |
| `.agents/skills/four-seat-protocol/scripts/seat_status.py` | Channel-labeled seat orientation |
| `coordination/threeway/activation/pipeline-local-authority-2026-07-10.toml` | Secret-free activation intent, deterministic importer, exact expected ref OIDs, and resume boundary |
| `threeway/cutover.py` | Ref-bus projection, cursor initialization, teardown, and ready-to-flip result |
| `threeway/gate.py` | Split non-mutating merge evaluation from token-gated ref/fact mutation |
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
- Append: `DECISIONS.md`
- Modify: `coordination/authority.toml`
- Modify: `scripts/protocol_authority.py`
- Modify: `scripts/protocol_mailbox.py`
- Modify: `scripts/status.py`
- Modify: `scripts/check_coordination.py`
- Modify: `scripts/mailbox_monitor.py`
- Modify: `scripts/protocol_effectiveness_report.py`
- Modify: `scripts/bus_unread.py`
- Modify: `scripts/consume_bus.py`
- Modify: `scripts/check_go_schema.py`
- Modify: `coordination/bin/send-event`
- Modify: `coordination/bin/consume-events`
- Modify: `.codex/hooks/update-state.sh`
- Modify: `.claude/hooks/update-state.sh`
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
- Modify: `tests/unit/test_protocol_authority.py`
- Create: `tests/unit/test_protocol_effectiveness_report.py`
- Modify only if changed symbols make a current claim stale: `ARCHITECTURE.md`
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
- Produces `count_human_unread(cursor: str, events:
  Sequence[MailboxEventEnvelope], seat: str) -> int`; no caller may count raw
  filenames or bypass `parse_mailbox_event()`.
- `bus_unread_events()` consults `protocol_authority`; shadow/live missing refs return `None`, not `[]`.
- Extends `HumanMailboxAuthority` with
  `cursor_envelope_schema: Literal["typed-v1"]`. A committed numeric envelope
  is legacy only when there is exactly one HEAD-ancestor marker-introduction
  commit, exactly one HEAD-ancestor event-introduction commit, the marker commit
  is not an ancestor of the event commit, and current bytes equal the
  introducing blob. Zero or multiple candidates fail closed.
- Fixes `SIGNED_FACT_EVENTS_REF = "refs/threeway/events"` and
  `SIGNED_FACT_CURSOR_NAMESPACE = "refs/threeway/cursors/"` in
  `protocol_authority`; `load_authority()` rejects any other manifest values.
- Produces frozen `MailboxEventEnvelope(timestamp, sender, target, kind, path,
  cursor_envelope)` and
  `parse_mailbox_event(root: Path, path: Path, *, manifest: AuthorityManifest)
  -> MailboxEventEnvelope`.
- The parser validates a real UTC calendar timestamp, exact sender/target
  rosters, registered kind, no self-address, H1/`When`/`From` agreement, one
  terminal cursor line, and provenance-sensitive envelope before the event may
  affect a count or mutation.
- Produces `read_human_cursor(path: Path) -> str`, which accepts exactly one
  newline-terminated ISO or `UNINITIALIZED` line and rejects trailing content,
  and `advance_human_cursor(root: Path, seat: str, *, target: str | None)
  -> CursorAdvanceResult`.
- `advance_human_cursor()` opens and exclusively locks the stable
  `coordination/mailbox/seen/` directory descriptor, rereads under lock,
  selects only parsed addressed events, refuses regression, fsyncs a
  same-directory temporary file, atomically replaces the cursor, fsyncs the
  directory, and returns before the Bash wrapper stages the explicit path.
- `scripts/status.py` exposes one machine-readable mailbox snapshot used by
  both `update-state.sh` mirrors. Pair identities render addressed counts;
  coordinator aliases render `all-scope-unpinned`; missing/corrupt live state
  renders unavailable and never zero.

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
- accept numeric events whose introducing commit does not descend from the
  `typed-v1` marker-introduction commit, including parallel pre-integration
  mail; reject marker-descendant numeric events, uncommitted numeric events
  while the marker is active, and any renamed, backdated, or byte-modified
  legacy event;
- prove `send-event` emits no numeric envelope after `typed-v1` deployment;
- make `protocol_effectiveness_report.mailbox_cursor_unread()` equal canonical
  unread for ISO, `UNINITIALIZED`, invalid, missing, and coordinator-alias
  cases;
- make both `update-state.sh` mirrors equal canonical pair/all-scope output and
  expose missing/corrupt state as unavailable;
- race two consumers from the same old cursor and prove the final cursor is the
  newer target; inject interruption before replace and prove prior bytes remain;
- reject unknown sender, target, kind, self-addressing, malformed calendar,
  H1/header mismatch, trailing cursor data, and invalid envelope before
  implicit or `--to` consumption changes cursor/index state;
- make checker severity FATAL for every event that mutation rejects;
- reject syntactically valid noncanonical event ref and cursor namespace
  values, and require `consume_bus.py` to load the validated manifest before
  constructing `RefEventStore`;
- render missing `sent/` as unavailable through checker, status, monitor,
  draft-handoff, effectiveness, and both seat-status mirrors;
- recognize `coordinator` and `coordinator2` on observational monitor,
  draft-handoff, and effectiveness surfaces. Keep canonical route discovery in
  `ledger_start_guard.py` and `protocol_capacity.py` explicitly exempt and
  unchanged.

Use these exact per-finding selectors. Run each node alone for causal RED,
implement the minimum correction, rerun the same node to GREEN, apply the named
one-fact flip, require that node to RED again, restore, and rerun GREEN:

| Finding | Exact pytest node | Initial RED | One-fact flip |
|---|---|---|---|
| 1 | `tests/unit/test_check_coordination.py::test_numeric_envelope_uses_introducing_commit_typed_marker` | lawful parallel pre-integration numeric mail is rejected or marker-ancestor numeric mail passes | change the fixture DAG so the marker-introduction commit is no longer an ancestor of the event-introduction commit |
| 2 | `tests/unit/test_protocol_authority.py::test_adr_013_binds_live_transition_to_task6c_only` | ADR-012 still grants broad Task 6 transition | change expected transition from `6C` to `6B` |
| 3 | `tests/unit/test_protocol_effectiveness_report.py::test_mailbox_cursor_unread_matches_canonical_policy` | canonical unread `1` becomes effectiveness `0` | restore lexical `UNINITIALIZED` comparison |
| 4 | `tests/unit/test_coordination_tooling.py::test_update_state_mirrors_use_canonical_mailbox_snapshot` | one or both hooks render false-zero state | bypass the shared snapshot in one mirror |
| 5 | `tests/unit/test_coordination_tooling.py::test_concurrent_consume_is_monotonic_and_atomic` | interleaving regresses or interruption truncates the cursor | remove the `seen/` directory lock around reread/replace |
| 6 | `tests/unit/test_protocol_mailbox.py::test_invalid_event_schema_never_advances_cursor` | an invalid sender/target/kind/self-address/envelope advances | admit one unknown kind in the parser fixture |
| 7 | `tests/unit/test_protocol_authority.py::test_noncanonical_signed_refs_fail_closed` | a valid alternative ref splits read/consume state | allow one alternative cursor namespace |
| 8 | `tests/unit/test_seat_status_all.py::test_seat_status_mirrors_fail_visible_on_corrupt_or_missing_mailbox` | trailing cursor data or missing `sent/` renders zero | read only the first cursor line in one mirror |
| 9 | `tests/unit/test_draft_handoff.py::test_observational_coordinator_aliases_are_symmetric` | `coordinator2` is omitted from one observational surface | remove `coordinator2` from the typed coordinator roster |

For every row the runnable shape is:

```bash
env -u GIT_INDEX_FILE .venv/bin/python -m pytest <exact-node-from-table> -q
```

- [ ] **Step 2: Run the focused tests to prove RED**

```bash
env -u GIT_INDEX_FILE .venv/bin/python -m pytest tests/unit/test_protocol_authority.py tests/unit/test_protocol_mailbox.py tests/unit/test_status.py tests/unit/test_check_coordination.py tests/unit/test_coordination_tooling.py tests/unit/test_governance_hardening.py tests/unit/test_threeway_activation_scripts.py tests/unit/test_seat_status_all.py tests/unit/test_check_go_schema.py tests/unit/test_draft_handoff.py tests/unit/test_protocol_capacity.py tests/unit/test_protocol_effectiveness_report.py -q
```

Expected: failures show the fixed timestamp cutoff rejects lawful current
history; effectiveness/hooks/seat mirrors disagree with canonical unread;
consume can regress or truncate; invalid filenames can advance a cursor;
noncanonical manifest refs split readers/writers; coordinators still own cursor
files; scalar cursors still select ref-bus unread; and absent state produces
zero.

- [ ] **Step 3: Append the corrective ADR and deploy the typed marker**

Append `ADR-013: Narrow signed-facts activation to Task 6C` without editing
ADR-012. State that Task 6A trust-root provisioning and Task 6B manifest
measurement remain `shadow`; only a separately authorized Task 6C performs the
local ref/authority transition. Update `coordination/authority.toml`'s decision
pointer to ADR-013 and add exactly:

```toml
cursor_envelope_schema = "typed-v1"
```

This marker is deployed in the same corrective child as the typed generator.
Find exactly one marker-introduction commit on HEAD ancestry: its tree contains
the exact `typed-v1` field and none of its parents does. Find exactly one event-
introduction commit on HEAD ancestry and require current bytes to equal its
blob. The numeric event is legacy only when the marker-introduction commit is
not an ancestor of the event-introduction commit. This admits parallel main
mail created before candidate integration, but a later deletion/restoration of
the marker cannot make post-marker mail legacy. Zero/multiple candidates and
uncommitted numeric events with the current marker active reject. Timestamp
comparison alone never grants legacy status.

- [ ] **Step 4: Add semantic mailbox constants and the canonical parser**

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

Add the frozen event/cursor types and functions named in the Interfaces block.
Load the kind registry once per scan. Validate the entire event and cursor file,
not the first line or a filename substring. `check_coordination.py` and
`check_go_schema.py` replace the wall-clock cutoff with the unique marker/event
introduction ancestry-and-byte rule; mutation-invalid events are FATAL checker
input.

- [ ] **Step 5: Make every human unread reader use the canonical policy**

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

Replace the independent cursor logic in
`scripts/protocol_effectiveness_report.py` and both `update-state.sh` mirrors
with the shared machine-readable status helper. Apply coordinator-alias parity
to effectiveness, monitor, and draft handoff. A missing mailbox directory or
invalid full cursor file is unavailable/invalid on every surface.

- [ ] **Step 6: Restrict mutation tools and serialize cursor advance**

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

`send-event` validates the full sender cursor and emits only the typed form.
`consume-events` delegates event selection and compare-and-replace to
`advance_human_cursor()` before staging. The helper holds an exclusive lock on
the stable `coordination/mailbox/seen/` directory descriptor across the reread,
monotonic comparison, temporary-file fsync, atomic replace, and directory
fsync. No lock file is created or deleted, and no filename-only grep may select
a mutation target.

- [ ] **Step 7: Reject configurable signed refs at the authority boundary**

Require the two exact constants from the Interfaces block in
`load_authority()`. `bus_unread.py` and `consume_bus.py` both load the same
manifest before constructing a store. Because alternatives are rejected,
`RefEventStore._cursor_ref()` remains unchanged and the broader cutover sibling
audit is explicitly out of this bounded Task 2 correction.

- [ ] **Step 8: Migrate current human cursor files honestly**

Because no committed cursor-backfill manifest can reconstruct the prior ISO
watermarks, set the four pair files to exactly `UNINITIALIZED\n` and delete the
two coordinator files. Do not invent consumed timestamps.

- [ ] **Step 9: Prove GREEN and per-finding non-vacuity**

```bash
env -u GIT_INDEX_FILE .venv/bin/python -m pytest tests/unit/test_protocol_authority.py tests/unit/test_protocol_mailbox.py tests/unit/test_status.py tests/unit/test_check_coordination.py tests/unit/test_coordination_tooling.py tests/unit/test_governance_hardening.py tests/unit/test_threeway_activation_scripts.py tests/unit/test_seat_status_all.py tests/unit/test_check_go_schema.py tests/unit/test_draft_handoff.py tests/unit/test_protocol_capacity.py tests/unit/test_protocol_effectiveness_report.py -q
```

Change only one coordinator to a cursor owner in the test fixture and confirm
the policy-disjointness test fails. Restore the policy and rerun GREEN.
Then flip the draft-handoff identity from coordinator to director and confirm a
foreign-seat event disappears, and flip a footer-only trigger to one
substantive sentence and confirm terminal-trigger detection changes from false
to true. Restore both fixtures and rerun GREEN.

Then independently flip each corrective guard: treat one post-marker numeric
event as legacy; bypass canonical unread in effectiveness; make one hook treat
`UNINITIALIZED` lexically; remove the cursor lock; admit one invalid kind;
permit one noncanonical ref; truncate a cursor read to the first line; and
remove `coordinator2` from observational discovery. Each named selector must
fail for its own reason before restoration and the final GREEN run.

- [ ] **Step 10: Review and commit the additive Task 2 correction**

Start from the clean failed candidate `205f077a23291496ea4b84c8de1f8acdfa2bd040`.
Confirm its sole parent is accepted Task 1
`e43acc245e2492883ca04b0d835268708ad0995d`. Do not amend, reset, rebase, or
rewrite either commit. Stage only the paths listed above, inspect the cached
diff, and create exactly one corrective child:

```bash
env -u GIT_INDEX_FILE git commit -m "fix(protocol): close mailbox authority verification gaps"
```

Dispatch fresh Task-2 specification and code-quality reviewers over the actual
`205f077..<corrective-child>` diff. After both pass, send one verify-request
for the cumulative three-commit range
`78b48ed493899dd126de2d1764cbdbf022111dfd..<corrective-child>` and cite the
accepted Task-1 artifacts, failed-candidate provenance, corrective reviews,
all nine RED/GREEN/non-vacuity selectors, changed paths, and exclusions.

---

### Task 2R: Repair The Specification-Review Gaps Additively

**Owner:** Pair A director implementation as exactly one child of spec-failed
commit `92d1fbcd1bb76ccb377d6bca1631374569696626`; Pair A operator performs one
final cumulative Lane V only after fresh specification and quality reviews pass.

**Files:**
- Modify: `scripts/protocol_mailbox.py`
- Modify: `scripts/protocol_effectiveness_report.py`
- Modify: `scripts/continuation_readiness.py`
- Modify: `scripts/draft_handoff.py`
- Modify: `tests/unit/test_protocol_mailbox.py`
- Modify: `tests/unit/test_check_coordination.py`
- Modify: `tests/unit/test_protocol_effectiveness_report.py`
- Modify: `tests/unit/test_codex_ledger_bridge.py`
- Modify: `tests/unit/test_draft_handoff.py`
- Modify only if changed implementation makes a current claim stale: `ARCHITECTURE.md`

`scripts/latest_handoff.py` remains unchanged. Its canonical discovery mapping
is the reference behavior; the draft producer must match it.

**Interfaces:**
- Numeric legacy acceptance additionally requires
  `_current_head_blob_matches_exact_path(root, path, current_bytes)`. That
  helper derives the repo-relative mailbox path lexically without `resolve()`,
  rejects a symlink at the leaf or any component below the repository root,
  requires a regular file at that exact path, and proves
  `_blob(root, "HEAD", lexical_rel) == current_bytes`. Acceptance separately
  retains `introducing_blob == current_bytes`. A missing `HEAD:<path>`,
  committed modification, deletion plus uncommitted restoration, symlink/path
  rebound, or Git read failure rejects.
- `recent_mailbox_events(root, limit)` uses
  `protocol_mailbox.scan_mailbox_events()` and returns canonical envelope/text
  pairs plus the invalid `(path, reason)` scan state. Invalid envelopes never
  enter classification or route-to-GO samples, and the report preserves their
  visible invalid count/reasons.
- Produces frozen `MailboxUnreadObservation(state, count, event_names, detail)`
  where `state` is exactly `count`, `unavailable`, or `all-scope-unpinned`;
  `count` is an integer only for `count`. `mailbox_cursor_unread()` and
  `classify_seat_utilization()` exchange this type, and JSON/Markdown rendering
  never coerces either sentinel to zero.
- `continuation_readiness.py` loops
  `HUMAN_MAILBOX_CURSOR_OWNERS` plus `HUMAN_MAILBOX_ALL_SCOPE_READERS` for human
  mail and loops `SIGNED_FACT_CURSOR_IDENTITIES` for ref-bus probes. No cursor
  path consumes the deprecated addressability alias `RECEIVING_SEATS`.
- `default_output_path(root, "coordinator2")` returns a filename beginning
  `HANDOFF-coordinator-`; pair-seat tokens remain unchanged.
- `route_to_go_seconds()` recognizes the frozen typed coordinator roster, so
  `coordinator` and `coordinator2` request/route samples are symmetric without
  widening canonical route ownership.

- [ ] **Step 1: Write the six specification-review regressions**

Run each exact node alone to causal RED, then use its named one-fact flip after
GREEN:

| Finding | Exact pytest node | Initial RED | One-fact flip |
|---|---|---|---|
| 10 | `tests/unit/test_protocol_mailbox.py::test_numeric_legacy_requires_head_blob_at_exact_lexical_mailbox_path` | an exact-byte restoration after HEAD deletion/modification or a leaf/parent symlink rebound passes | bypass `_current_head_blob_matches_exact_path()` and retain only introducing-blob equality |
| 11 | `tests/unit/test_protocol_effectiveness_report.py::test_recent_mailbox_events_uses_canonical_parser_and_surfaces_invalid_scan` | malformed H1/When/From/kind/envelope affects classification | reinsert one invalid envelope into the returned canonical event pairs |
| 12 | `tests/unit/test_protocol_effectiveness_report.py::test_generate_report_preserves_unavailable_and_all_scope_unread` | missing/corrupt or coordinator state renders `unread=0` | coerce one sentinel observation to integer zero |
| 13 | `tests/unit/test_codex_ledger_bridge.py::test_readiness_uses_explicit_human_and_signed_fact_identity_rosters` | readiness probes signed cursors through `RECEIVING_SEATS` | substitute the deprecated alias for `SIGNED_FACT_CURSOR_IDENTITIES` |
| 14 | `tests/unit/test_draft_handoff.py::test_default_output_path_canonicalizes_coordinator_alias` | coordinator2 automatic output is undiscoverable | render the concrete coordinator2 token in the filename |
| 15 | `tests/unit/test_protocol_effectiveness_report.py::test_route_to_go_seconds_supports_both_coordinator_aliases` | equivalent coordinator2 route has no sample | hard-code only `coordinator` in request pairing |

- [ ] **Step 2: Prove the review-fix nodes RED**

```bash
env -u GIT_INDEX_FILE .venv/bin/python -m pytest tests/unit/test_protocol_mailbox.py::test_numeric_legacy_requires_head_blob_at_exact_lexical_mailbox_path tests/unit/test_protocol_effectiveness_report.py::test_recent_mailbox_events_uses_canonical_parser_and_surfaces_invalid_scan tests/unit/test_protocol_effectiveness_report.py::test_generate_report_preserves_unavailable_and_all_scope_unread tests/unit/test_codex_ledger_bridge.py::test_readiness_uses_explicit_human_and_signed_fact_identity_rosters tests/unit/test_draft_handoff.py::test_default_output_path_canonicalizes_coordinator_alias tests/unit/test_protocol_effectiveness_report.py::test_route_to_go_seconds_supports_both_coordinator_aliases -q
```

Expected: six failures reproduce the six source-confirmed specification gaps at
`92d1fbc`.

- [ ] **Step 3: Implement the minimum review fix**

Add the no-follow lexical-path/regular-file/HEAD-blob guard before legacy
acceptance; never derive the Git path through `Path.resolve()`. Replace
effectiveness raw filename/text scanning with canonical envelopes while
retaining invalid scan state. Thread `MailboxUnreadObservation` through
utilization and rendering. Split continuation-readiness loops by explicit human
and signed-fact policy, canonicalize only coordinator draft filenames, and use
the typed coordinator roster for route-to-GO pairing. Do not change canonical
discovery or route authority.

- [ ] **Step 4: Prove GREEN, all fifteen flips, and full focus**

Run the six nodes above, all nine Task-2 nodes, and the focused Task-2 suite.
Independently apply each row's one-fact flip, require only its named selector to
RED for the intended reason, restore, and rerun final GREEN.

```bash
env -u GIT_INDEX_FILE .venv/bin/python -m pytest tests/unit/test_protocol_authority.py tests/unit/test_protocol_mailbox.py tests/unit/test_status.py tests/unit/test_check_coordination.py tests/unit/test_coordination_tooling.py tests/unit/test_governance_hardening.py tests/unit/test_threeway_activation_scripts.py tests/unit/test_seat_status_all.py tests/unit/test_check_go_schema.py tests/unit/test_draft_handoff.py tests/unit/test_protocol_capacity.py tests/unit/test_protocol_effectiveness_report.py tests/unit/test_codex_ledger_bridge.py -q
```

- [ ] **Step 5: Commit one immutable review-fix child and review it**

Confirm the exact topology is
`78b48ed -> e43acc2 -> 205f077 -> 92d1fbc -> <review-fix-child>` and the final
child's sole parent is `92d1fbc`. Do not amend, reset, rebase, squash, or add a
second routed child.

```bash
env -u GIT_INDEX_FILE git commit -m "fix(protocol): close mailbox spec-review gaps"
```

Run fresh specification review over `92d1fbc..<review-fix-child>`. Only after it
passes, run fresh code-quality review. Director then sends one Operator
verify-request for `78b48ed..<review-fix-child>` covering all four cumulative
implementation commits, all fifteen selectors/flips, exact paths, provenance,
and exclusions.

---

### Task 2S: Close The Race-Safety Review Gaps Additively

**Owner:** Pair A director implementation as exactly one child of the
reviewed-but-spec-failed Task2R commit
`ef76fd11ea61e27778d0cedf65c1a608cf826354`; Pair A operator performs one
final cumulative Lane V only after fresh specification and quality reviews
pass.

**Files:**
- Modify: `scripts/protocol_mailbox.py`
- Modify: `scripts/protocol_effectiveness_report.py`
- Modify: `tests/unit/test_protocol_mailbox.py`
- Modify: `tests/unit/test_protocol_effectiveness_report.py`
- Modify only if the frozen snapshot representation requires bounded
  compatibility repair: `scripts/continuation_readiness.py`
- Modify only if the frozen snapshot representation requires bounded
  compatibility repair: `scripts/draft_handoff.py`
- Modify only if the frozen snapshot representation requires bounded
  compatibility repair: `tests/unit/test_check_coordination.py`
- Modify only if the frozen snapshot representation requires bounded
  compatibility repair: `tests/unit/test_codex_ledger_bridge.py`
- Modify only if the frozen snapshot representation requires bounded
  compatibility repair: `tests/unit/test_draft_handoff.py`
- Modify only if changed implementation makes a current claim stale:
  `ARCHITECTURE.md`

No new production path is authorized. Preserve route base `78b48ed`, accepted
Task 1 `e43acc2`, failed candidate `205f077`, first reviewed-but-spec-failed
child `92d1fbc`, and Task2R candidate `ef76fd1` as immutable provenance. Do not
amend, reset, rebase, squash, rewrite, or create another routed child after the
one Task2S child.

**Interfaces:**
- `MailboxEventEnvelope` remains the compatible canonical scanner result for
  existing callers and additionally carries immutable `body_bytes: bytes` and
  `body_text: str` populated by the parser. Defaults may preserve test-fixture
  construction, but every envelope returned by `parse_mailbox_event()` or
  `scan_mailbox_events()` must contain the real validated snapshot.
- A private frozen `_MailboxFileSnapshot` contains the lexical repo-relative
  path, exact bytes, decoded text, and an ordered root-to-leaf identity chain.
  `_read_mailbox_file_snapshot(root, path)` returns one snapshot or fails
  closed; no parser or provenance check reopens the path.
- Descriptor traversal opens every below-root directory relative to its held
  parent descriptor with `O_NOFOLLOW | O_DIRECTORY | O_CLOEXEC`, opens the leaf
  with `O_NOFOLLOW | O_CLOEXEC`, requires `fstat()` regular-file mode, reads the
  leaf descriptor once, and rechecks device, inode, mode, size, and
  nanosecond mutation metadata for the captured component/leaf chain before
  success. Any unavailable flag, component, type, identity, or decode result
  rejects.
- `_numeric_envelope_is_legacy()` consumes that same snapshot. Its exact bytes
  feed envelope parsing, `HEAD:<lexical-path>`, event-introduction, and
  introducing-blob comparisons; a leaf or parent rebound cannot substitute
  separately read bytes.
- `recent_mailbox_events()` returns canonical envelope/body pairs from the
  envelope snapshot, never `safe_read(event.path)`. `collect_report()` obtains
  one full `scan_mailbox_events()` result and reuses it for classifications,
  route/GO samples, invalid metrics, event counts, and every unread
  observation. It performs no second canonical scan in the same report.

- [ ] **Step 1: Write the two causal race regressions and honest controls**

Add exactly these selectors:

| Finding | Exact pytest node | Injected race at `ef76fd1` | Honest control | One-fact flip after GREEN |
|---|---|---|---|---|
| 16 | `tests/unit/test_protocol_effectiveness_report.py::test_effectiveness_reuses_one_validated_body_snapshot_after_atomic_replace` | wrap the real canonical scanner, atomically replace the valid body before `recent_mailbox_events()`/`collect_report()` resumes, and observe replacement bytes affect classification/accounting | leave the validated path unchanged and require its original classification, route/GO sample, event count, invalid count, and unread observation | reintroduce `safe_read(event.path)` or a second canonical scan; only this selector becomes RED |
| 17 | `tests/unit/test_protocol_mailbox.py::test_numeric_legacy_descriptor_snapshot_rejects_transient_leaf_and_parent_rebound` | in a real temporary Git repository, transiently substitute first the leaf and then its parent at the descriptor-read boundary while preserving same bytes | keep the ordinary regular leaf/parent unchanged and require lawful pre-marker numeric mail to pass | remove descriptor-relative no-follow opening or final component-identity revalidation; the corresponding leaf/parent case becomes RED |

Each selector must prove its injected race occurred. A test that passes because
the hook never ran, the substitute was not observed, or the honest control did
not reach legacy/classification acceptance is invalid.

- [ ] **Step 2: Prove both race selectors RED at `ef76fd1`**

```bash
env -u GIT_INDEX_FILE .venv/bin/python -m pytest tests/unit/test_protocol_effectiveness_report.py::test_effectiveness_reuses_one_validated_body_snapshot_after_atomic_replace tests/unit/test_protocol_mailbox.py::test_numeric_legacy_descriptor_snapshot_rejects_transient_leaf_and_parent_rebound -q
```

Expected: both injected-race assertions fail for their named reason while both
unchanged-path controls pass. A missing-node, fixture, or unrelated setup
failure is not causal RED.

- [ ] **Step 3: Bind parsing and numeric provenance to one descriptor snapshot**

Add the frozen snapshot representation and descriptor-relative acquisition in
`scripts/protocol_mailbox.py`. Acquire once at the start of
`_parse_mailbox_event()`, decode once, parse only `snapshot.body_text`, pass the
same snapshot into numeric-legacy provenance, and populate the returned frozen
envelope with its bytes/text. Preserve `scan_mailbox_events()`'s public return
shape for status, monitor, draft-handoff, coordination-check, and cursor
consumers. Do not add a fallback `Path.read_bytes()`/`Path.read_text()` path.

- [ ] **Step 4: Reuse that snapshot for the complete effectiveness report**

Remove the mailbox-body use of `safe_read(event.path)`. Let
`recent_mailbox_events()` accept or derive the already completed canonical scan
and pair each event with its frozen `body_text`. In `collect_report()`, perform
one canonical scan, pass the same event/error collections to recent-event
classification and unread computation, and derive route/GO samples, event and
invalid counts, and rendered metrics from those collections. Inventory reads
may continue to use `safe_read()`; only mailbox bodies are prohibited from
path reopening.

- [ ] **Step 5: Prove GREEN, both non-vacuity flips, all seventeen selectors, and focus**

Run the two exact nodes from Step 2 to GREEN. Apply the finding-16 one-fact
flip, require only finding 16 to RED for replacement-body use, restore, and
rerun GREEN. Separately remove descriptor-relative no-follow opening and then
final identity revalidation, require the corresponding finding-17 leaf/parent
case to RED, restore after each flip, and rerun GREEN.

Then rerun the nine exact Task-2 selectors, the six exact Task2R selectors, the
two Task2S selectors, and the focused suite:

```bash
env -u GIT_INDEX_FILE .venv/bin/python -m pytest tests/unit/test_protocol_authority.py tests/unit/test_protocol_mailbox.py tests/unit/test_status.py tests/unit/test_check_coordination.py tests/unit/test_coordination_tooling.py tests/unit/test_governance_hardening.py tests/unit/test_threeway_activation_scripts.py tests/unit/test_seat_status_all.py tests/unit/test_check_go_schema.py tests/unit/test_draft_handoff.py tests/unit/test_protocol_capacity.py tests/unit/test_protocol_effectiveness_report.py tests/unit/test_codex_ledger_bridge.py -q
```

Also run smoke, doc claims for every changed doc, `git diff --check`, and the
real effectiveness-render command. A green focused suite does not replace the
two causal race selectors and their flips.

- [ ] **Step 6: Commit one immutable race-fix child and review it**

Confirm the exact topology is
`78b48ed -> e43acc2 -> 205f077 -> 92d1fbc -> ef76fd1 -> <race-fix-child>`
and the final child's sole parent is `ef76fd1`. Commit only the bounded
implementation/test/doc scope:

```bash
env -u GIT_INDEX_FILE git commit -m "fix(protocol): bind mailbox reads to one snapshot"
```

Run fresh specification review over `ef76fd1..<race-fix-child>`. Only after it
passes, run fresh code-quality review. Director then sends one Operator
verify-request for `78b48ed..<race-fix-child>` covering all five cumulative
implementation/provenance commits, all seventeen selectors/flips, exact paths,
provenance, and exclusions. Do not dispatch Operator or add another child after
a specification-review issue.

---

### Task 2T: Make A Failed Canonical Scan Fail Visible Additively

**Owner:** Pair A director implementation as exactly one child of the
reviewed-but-spec-failed Task2S commit
`8cc4beed2c6c5836f915113ccd5104c3f039c8de`; Pair A operator performs one
final cumulative Lane V only after fresh specification and quality reviews
pass.

**Files:**
- Modify: `scripts/protocol_effectiveness_report.py`
- Modify: `tests/unit/test_protocol_effectiveness_report.py`

No mailbox parser, cursor file, compatibility module, or architecture claim
changes in this slice. Preserve route base `78b48ed`, accepted Task 1
`e43acc2`, failed candidate `205f077`, reviewed-but-spec-failed children
`92d1fbc`, `ef76fd1`, and `8cc4bee` as immutable provenance. Do not amend,
reset, rebase, squash, rewrite, or create another routed child after the one
Task2T child.

**Interfaces:**
- `collect_report()` retains a distinct `global_scan_error: str | None` from
  the single canonical `scan_mailbox_events()` call. A completed scan with
  invalid individual envelopes remains available and uses its valid events;
  only an exception from the complete scan sets the global error.
- When `global_scan_error` is present, every pair and all-scope reader receives
  `MailboxUnreadObservation("unavailable", None, (), global_scan_error)`.
  Valid cursor text remains separately rendered as cursor evidence, but no
  reader may emit numeric zero or `all-scope-unpinned` success from an
  unavailable scan.
- The same exception still contributes exactly one invalid-scan record and no
  second mailbox scan occurs.

- [ ] **Step 1: Write the causal global-scan regression and honest control**

Add exactly this selector:

`tests/unit/test_protocol_effectiveness_report.py::test_collect_report_marks_every_reader_unavailable_when_canonical_scan_fails`

The honest control uses valid cursors, one valid `to-all` event, and one
malformed individual envelope. A successfully completed scan must retain
`invalid_mailbox_event_count == 1`, pair unread counts of one, and coordinator
`all-scope-unpinned` observations. The regression then injects one global
scanner exception and proves the hook ran exactly once, the invalid scan stays
visible, and all six observations are typed unavailable with `count is None`,
empty event names, and preserved error detail. JSON and summary rendering must
contain neither numeric-zero nor all-scope success for that failed scan.

- [ ] **Step 2: Prove the selector RED at `8cc4bee`**

```bash
env -u GIT_INDEX_FILE .venv/bin/python -m pytest tests/unit/test_protocol_effectiveness_report.py::test_collect_report_marks_every_reader_unavailable_when_canonical_scan_fails -q
```

Expected: the global-exception branch reports pair `count=0` and coordinator
`all-scope-unpinned`, while the completed-scan control passes. A missing node,
bad fixture, or failure of the completed-scan control is not causal RED.

- [ ] **Step 3: Retain scan availability explicitly**

Keep the implementation local to `collect_report()`:

```python
global_scan_error: str | None = None
try:
    parsed_events, scanned_invalid_events = protocol_mailbox.scan_mailbox_events(root)
except (OSError, ValueError, protocol_authority.AuthorityConfigError) as exc:
    parsed_events = []
    global_scan_error = f"canonical mailbox scan unavailable: {exc}"
    scanned_invalid_events = [(sent, global_scan_error)]

# Inside the one unread-observation loop:
if global_scan_error is not None:
    observation = MailboxUnreadObservation(
        "unavailable", None, (), global_scan_error,
    )
else:
    observation = mailbox_cursor_unread(seat, cursor, parsed_events, repo_root=root)
```

Do not encode the scan error as a fabricated cursor error, do not infer global
failure from ordinary per-envelope invalid entries, and do not add a fallback
scan.

- [ ] **Step 4: Prove GREEN, non-vacuity, all eighteen selectors, and focus**

Run the exact node from Step 2 to GREEN. Then ignore only the retained global
error when constructing observations; only this new selector must RED. Restore
the branch and rerun GREEN. Run all seventeen prior named selectors plus this
new selector; the current parameterization yields twenty pytest cases. Run the
full Task-2 focused suite, smoke, the real effectiveness renderer, and
`git diff --check` over the two changed paths.

- [ ] **Step 5: Commit one immutable fail-visible child and review it**

Confirm the exact topology is
`78b48ed -> e43acc2 -> 205f077 -> 92d1fbc -> ef76fd1 -> 8cc4bee -> <fail-visible-child>`
and the final child's sole parent is `8cc4bee`. Commit only the two named files:

```bash
env -u GIT_INDEX_FILE git commit -m "fix(protocol): fail visible on mailbox scan errors"
```

Run fresh specification review over `8cc4bee..<fail-visible-child>`. Only after
it passes, run fresh code-quality review. Director then sends one Operator
verify-request for `78b48ed..<fail-visible-child>` covering all six cumulative
implementation/provenance commits, all eighteen selectors/flips, exact paths,
provenance, and exclusions. Do not dispatch Operator or add another child after
a specification-review issue.

---

### Task 3A: Add The Typed Runtime Identity And Authorization Foundation

**Owner:** Pair B director2 implementation in a separate worktree after Task 2; Pair B operator2 verification.

**Files:**
- Modify: `scripts/codex_protocol_model.py`
- Modify: `.env.example`
- Create: `scripts/protocol_executor_token.py`
- Modify: `scripts/protocol_capacity.py`
- Create: `tests/unit/test_codex_protocol_model.py`
- Create: `tests/unit/test_protocol_executor_token.py`
- Modify: `tests/unit/test_protocol_capacity.py`
- Modify: `tests/unit/test_codex_ledger_bridge.py`

**Interfaces:**
- Produces `RuntimeIdentityError(ValueError)`.
- Produces `SessionBindingView(Protocol)` with read-only `session_id`,
  `mode`, `concrete_seat`, `role_family`, and `agent_role` attributes. Task 3B's concrete
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


class RuntimeCommandClass(str, Enum):
    ROUTE_MUTATION = "route-mutation"
    LOCK_MUTATION_LOCAL = "lock-mutation-local"
    LOCK_CLAIM_REMOTE = "lock-claim-remote"
    LOCK_RELEASE_REMOTE = "lock-release-remote"
    HUMAN_CURSOR_CONSUME = "human-cursor-consume"
    SIGNED_CURSOR_LOCAL = "signed-cursor-local"
    SIGNED_CURSOR_FROM_REMOTE = "signed-cursor-from-remote"
    SIGNED_FACT_EMIT_LOCAL = "signed-fact-emit-local"
    SIGNED_FACT_EMIT_REMOTE = "signed-fact-emit-remote"
    TRUST_ROOT_BOOTSTRAP = "trust-root-bootstrap"
    AUTHORITY_CUTOVER = "authority-cutover"


class ServiceCommandClass(str, Enum):
    OVERSEER_FACT_EMIT = "overseer-fact-emit"
    CHIEF_GEMINI_FACT_EMIT = "chief-gemini-fact-emit"
    CHIEF_CHATGPT_FACT_EMIT = "chief-chatgpt-fact-emit"
    CI_RESULT_SIGN = "ci-result-sign"
    MERGE_GATE_TARGET_REF_UPDATE = "merge-gate-target-ref-update"
    MERGE_GATE_COMPLETION_EMIT = "merge-gate-completion-emit"
```

`RuntimeOperation` is defined in `scripts/codex_protocol_model.py`.
`RuntimeCommandClass` and `ServiceCommandClass` are defined with
`SignedFactPublicationBinding` in `scripts/protocol_executor_token.py`.
The model re-exports the runtime enum, while `scripts/protocol_principal.py`
imports the service enum directly; the token module never imports either
consumer, avoiding a circular dependency. The token parser's command-class
field is the closed union `RuntimeCommandClass | ServiceCommandClass`; each
authorizer accepts only its own typed half.

- Pins the complete default actor-operation matrix:

```python
DEFAULT_RUNTIME_OPERATIONS = {
    "readiness-bridge": frozenset({
        RuntimeOperation.ORIENT,
    }),
    "protocol-director-subagent": frozenset({
        RuntimeOperation.ORIENT,
        RuntimeOperation.REPOSITORY_MUTATE,
    }),
    "protocol-coordinator-subagent": frozenset({RuntimeOperation.ORIENT}),
    "protocol-operator-subagent": frozenset({RuntimeOperation.ORIENT}),
    "lane-v-verifier-subagent": frozenset({RuntimeOperation.ORIENT}),
    "money-gate-reviewer-subagent": frozenset({RuntimeOperation.ORIENT}),
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
TOKEN_APPOINTABLE_RUNTIME_OPERATIONS = frozenset({
    RuntimeOperation.REMOTE_PUBLISH,
    RuntimeOperation.TRUST_ROOT_BOOTSTRAP,
    RuntimeOperation.AUTHORITY_CUTOVER,
})
TOKEN_REQUIRED_RUNTIME_OPERATIONS = frozenset({
    RuntimeOperation.ROUTE_MUTATE,
    RuntimeOperation.LOCK_MUTATE,
    RuntimeOperation.HUMAN_CURSOR_CONSUME,
    RuntimeOperation.SIGNED_CURSOR_CONSUME,
    RuntimeOperation.SIGNED_FACT_EMIT,
    RuntimeOperation.REMOTE_PUBLISH,
    RuntimeOperation.TRUST_ROOT_BOOTSTRAP,
    RuntimeOperation.AUTHORITY_CUTOVER,
})

TOKEN_APPOINTABLE_RUNTIME_ACTOR_CLASSES_BY_COMMAND_CLASS = {
    RuntimeCommandClass.LOCK_CLAIM_REMOTE: frozenset({"director", "coordinator"}),
    RuntimeCommandClass.LOCK_RELEASE_REMOTE: frozenset({"director", "coordinator"}),
    RuntimeCommandClass.SIGNED_FACT_EMIT_REMOTE: frozenset({
        "director", "operator", "coordinator",
    }),
    RuntimeCommandClass.TRUST_ROOT_BOOTSTRAP: frozenset({"director", "coordinator"}),
    RuntimeCommandClass.AUTHORITY_CUTOVER: frozenset({"director", "coordinator"}),
}

OPERATOR_REMOTE_FACT_KINDS = frozenset({
    "attestation", "co_sign", "re_verify", "attestation_revoked",
})
INDEPENDENT_VERIFIER_BY_OPERATOR = {
    "operator": "operator2",
    "operator2": "operator",
}

RUNTIME_ACTOR_CLASS_BY_IDENTITY = {
    ("readiness-bridge", None, None): "readiness-bridge",
    ("subagent", None, "protocol-director"): "protocol-director-subagent",
    ("subagent", None, "protocol-coordinator"): "protocol-coordinator-subagent",
    ("subagent", None, "protocol-operator"): "protocol-operator-subagent",
    ("subagent", None, "lane-v-verifier"): "lane-v-verifier-subagent",
    ("subagent", None, "money-gate-reviewer"): "money-gate-reviewer-subagent",
    ("live-seat", "director", None): "director",
    ("live-seat", "director2", None): "director",
    ("live-seat", "operator", None): "operator",
    ("live-seat", "operator2", None): "operator",
    ("coordinator", "coordinator", None): "coordinator",
    ("coordinator", "coordinator2", None): "coordinator",
}
```

`REPOSITORY_MUTATE` never widens the identity's path-limited mutation scope.
The `(mode, concrete_seat, agent_role)` map above is exhaustive: every tuple not listed is
invalid and receives no operation defaults. The two pair directors share the
director operation set, the two pair operators share the operator operation
set, and both coordinator spellings share the coordinator set without gaining
a human-mailbox cursor. The readiness and subagent modes never carry a
concrete seat.
Appointable operations belong to no default set. A token never creates static
eligibility: the cumulative authorizer first requires a valid live-seat or
coordinator identity named for the exact command class in
`TOKEN_APPOINTABLE_RUNTIME_ACTOR_CLASSES_BY_COMMAND_CLASS`, then verifies the
complete target-bound token and every operation-specific gate. Readiness,
subagent, and mechanical principals cannot receive appointable interactive
operations. Operators are absent from remote-lock classes; no remote signed-
cursor publication class exists because cursor writes remain local even when
events are read from a remote authority. An operator's only remote-publication
class is its own signed-fact emission under the binding below. Every operation in
`TOKEN_REQUIRED_RUNTIME_OPERATIONS`, including signed-fact emit and remote
publish, fails when either identity eligibility or token authority is absent.

- Produces immutable `SideEffectExecutorToken` in
  `scripts/protocol_executor_token.py` and these single-source entry points:

```python
@dataclass(frozen=True, slots=True)
class SignedFactPublicationBinding:
    fact_kind: str
    signer_seat: str
    candidate_id: str
    independent_verifier: str
    verification_report_path: Path
```

The token stores `signed_fact: SignedFactPublicationBinding | None`. Remote
signed-fact publication requires an exact binding in both the committed token
and caller input; remote locks remain bound by command class and normalized
target. Every remote signed-fact signer must equal the validated concrete seat
and token executor, and the fact kind must be in that seat's static fact-
authority table. The verifier must be a distinct concrete operator seat, and
`verification_report_path` must be a no-follow, HEAD-committed
`coordination/mailbox/sent/*-verification-report.md` GO binding the same fact
kind/signer, candidate, expected HEAD, and publication target. For an operator,
the kind must be in `OPERATOR_REMOTE_FACT_KINDS`,
`independent_verifier` must equal
`INDEPENDENT_VERIFIER_BY_OPERATOR[concrete_seat]`, and the named committed GO
report must come from that verifier and bind the same `candidate_id`,
`expected_head`, and publication target. Any absent, same-seat, uncommitted, or
mismatched field/report fails before token, event construction, key, object,
fetch, append, ref, or push callbacks.

The Markdown token fields are exactly `publication_fact_kind`,
`publication_signer_seat`, `publication_candidate_id`,
`independent_verifier`, and `verification_report_path`. They are all required
for `SIGNED_FACT_EMIT_REMOTE` and all forbidden for every other command class;
unknown, partial, or duplicate publication fields fail token parsing.

The referenced GO report contains exactly one H2 section in this exact field
order and spelling:

```markdown
## Signed-Fact Publication Authorization

publication_fact_kind: attestation
publication_signer_seat: operator
publication_candidate_id: A:candidate-123
publication_expected_head: 0123456789abcdef0123456789abcdef01234567
publication_target: git-remote:origin#refs/threeway/events
```

```python
@dataclass(frozen=True, slots=True)
class SignedFactPublicationGO:
    fact_kind: str
    signer_seat: str
    candidate_id: str
    expected_head: str
    target: str
    verifier_seat: str
    source_path: Path


def load_signed_fact_publication_go(
    root: Path, path: Path,
) -> SignedFactPublicationGO: ...
```

The dataclass and loader live in `scripts/protocol_executor_token.py`. The
loader opens a no-follow regular file present at exact HEAD under
`coordination/mailbox/sent/`, validates it through the canonical mailbox parser
as a `verification-report`, requires `VERDICT: GO`, and derives a concrete
operator verifier from the canonical filename sender. The specialized report
requires a full 40-character H1 commit SHA identical to
`publication_expected_head`. The section has exactly five nonempty unquoted ASCII values: fact kind matches
`[a-z][a-z0-9_]{0,63}`, signer is a concrete seat, candidate matches
`[A-Za-z0-9][A-Za-z0-9._:-]{0,255}`, expected HEAD is 40 lowercase hex, and
target equals the normalized token target. Missing, reordered, duplicate,
unknown, extra, empty, whitespace-padded, non-ASCII, malformed, wrong-sender,
non-GO, or uncommitted reports fail parsing. The cumulative token verifier then
requires the returned verifier, fact kind, signer, candidate, expected HEAD,
and normalized target to equal `SignedFactPublicationBinding`, the token, and
the live caller inputs. Any mismatch fails before the token is returned.

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
    command_class: RuntimeCommandClass | ServiceCommandClass,
    expected_head: str,
    current_appointment_path: Path,
    newer_appointment_paths: Sequence[Path],
    target_satisfied: bool,
    failed_preflight: Sequence[str],
    triggered_stop_predicates: Sequence[str],
    signed_fact: SignedFactPublicationBinding | None = None,
) -> SideEffectExecutorToken: ...
```

The frozen token records source path, ID, executor, normalized target, typed
runtime-or-service command class, expected HEAD, preflight, stop predicates,
postcheck, observer seats, closeout owner, and non-goals. The loader requires a no-follow, committed
coordinator appointment under `coordination/mailbox/sent/` and selects exactly
one complete ID. The executable verifier rejects unknown/duplicate,
uncommitted, wrong executor/target/class/HEAD, non-current, superseded,
already-satisfied, failed-preflight, or triggered-stop state. It never treats
field presence or runtime-operation eligibility as execution authority.
`scripts/protocol_capacity.py` imports this parser for route validation and
deletes its parallel token parser.

- Produces one cumulative authorization result and entry point:

```python
@dataclass(frozen=True)
class AuthorizedRuntimeSideEffect:
    identity: RuntimeIdentity
    command_class: RuntimeCommandClass
    operations: frozenset[RuntimeOperation]
    executor_token: SideEffectExecutorToken
    signed_fact: SignedFactPublicationBinding | None


def authorize_side_effect_operations(
    root: Path,
    environ: Mapping[str, str],
    *,
    session_binding: SessionBindingView,
    operations: AbstractSet[RuntimeOperation],
    command_class: RuntimeCommandClass,
    expected_actor: str,
    token_path: Path,
    side_effect_id: str,
    target: str,
    expected_head: str,
    current_appointment_path: Path,
    newer_appointment_paths: Sequence[Path],
    target_satisfied: bool,
    failed_preflight: Sequence[str],
    triggered_stop_predicates: Sequence[str],
    signed_fact: SignedFactPublicationBinding | None = None,
) -> AuthorizedRuntimeSideEffect: ...


def command_class_is_appointable(
    identity: RuntimeIdentity, command_class: RuntimeCommandClass,
) -> bool: ...
```

It resolves identity, validates the mandatory binding and actor, requires a
nonempty set consisting only of token-required operations, checks static
eligibility and publication eligibility, and validates the one committed token
before returning either component. Token-required mutation entry points must
not call bare `operation_is_allowed()` or `authorize_operation()`. Token-exempt
ordinary `MAIL_SEND` and `OPERATOR_VERDICT` continue to use
`authorize_operation()` and remain identity/authority gated.

Freeze the exhaustive command-class map:

```python
OPERATIONS_BY_COMMAND_CLASS = {
    RuntimeCommandClass.ROUTE_MUTATION: frozenset({RuntimeOperation.ROUTE_MUTATE}),
    RuntimeCommandClass.LOCK_MUTATION_LOCAL: frozenset({RuntimeOperation.LOCK_MUTATE}),
    RuntimeCommandClass.LOCK_CLAIM_REMOTE: frozenset({
        RuntimeOperation.LOCK_MUTATE,
        RuntimeOperation.REMOTE_PUBLISH,
    }),
    RuntimeCommandClass.LOCK_RELEASE_REMOTE: frozenset({
        RuntimeOperation.LOCK_MUTATE,
        RuntimeOperation.REMOTE_PUBLISH,
    }),
    RuntimeCommandClass.HUMAN_CURSOR_CONSUME:
        frozenset({RuntimeOperation.HUMAN_CURSOR_CONSUME}),
    RuntimeCommandClass.SIGNED_CURSOR_LOCAL:
        frozenset({RuntimeOperation.SIGNED_CURSOR_CONSUME}),
    RuntimeCommandClass.SIGNED_CURSOR_FROM_REMOTE:
        frozenset({RuntimeOperation.SIGNED_CURSOR_CONSUME}),
    RuntimeCommandClass.SIGNED_FACT_EMIT_LOCAL:
        frozenset({RuntimeOperation.SIGNED_FACT_EMIT}),
    RuntimeCommandClass.SIGNED_FACT_EMIT_REMOTE: frozenset({
        RuntimeOperation.SIGNED_FACT_EMIT,
        RuntimeOperation.REMOTE_PUBLISH,
    }),
    RuntimeCommandClass.TRUST_ROOT_BOOTSTRAP:
        frozenset({RuntimeOperation.TRUST_ROOT_BOOTSTRAP}),
    RuntimeCommandClass.AUTHORITY_CUTOVER:
        frozenset({RuntimeOperation.AUTHORITY_CUTOVER}),
}
```

The requested set must equal, not merely overlap or be a subset of, the frozen
bundle for `command_class`. Unknown classes, empty sets, extra operations, and
partial remote bundles fail before token or mutation callbacks.

- Produces immutable `RuntimeIdentity` with fields `mode`, `concrete_seat`,
  `agent_role`, `behavior_source`, `capability_scope`, `mutation_scope`, `mailbox_policy`,
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
  `CODEX_VERIFICATION_COMMANDS` together with
  `tests/unit/test_protocol_executor_token.py`, and updates
  `tests/unit/test_codex_ledger_bridge.py` so `protocol_doctor.py` executes both.

- Pins supported subagent defaults exactly:

| `agent_role` | Default operations | Mutation | Verification | Route/publish |
|---|---|---|---|---|
| `protocol-director` | `orient,repository-mutate` | parent-named paths only | no GO | none |
| `protocol-coordinator` | `orient` | none | evidence only | none |
| `protocol-operator` | `orient` | none | read-only review, no GO | none |
| `lane-v-verifier` | `orient` | none | read-only review, no GO | none |
| `money-gate-reviewer` | `orient` | none | read-only review, no GO | none |

```python
POLICY_TOKEN_VOCABULARY_BY_FIELD = {
    "capability_scope": frozenset({
        "read-only", "seat-local", "capacity-max", "orient", "parent-task",
    }),
    "mutation_scope": frozenset({
        "none", "seat-owned", "coordination-only", "parent-named-paths",
    }),
    "mailbox_policy": frozenset({
        "read-only", "no-send", "no-consume", "seat-read",
        "consume-intentional", "all-scope-read",
    }),
    "git_policy": frozenset({
        "env-u-git-index", "read-only", "per-seat-index-for-cursor-status",
        "temp-index", "parent-named-paths",
    }),
    "verification_policy": frozenset({
        "report-evidence-only", "request-operator-go",
        "independent-go-nits-fail", "reconcile-operator-go-only",
        "advisory", "evidence-only", "read-only-review", "no-go",
    }),
    "routing_authority": frozenset({
        "none", "report-only", "seat-owned", "all-scope-reconcile",
    }),
}

DEFAULT_POLICY_TOKENS_BY_ACTOR = {
    "readiness-bridge": {
        "capability_scope": frozenset({"read-only"}),
        "mutation_scope": frozenset({"none"}),
        "mailbox_policy": frozenset({"read-only", "no-send", "no-consume"}),
        "git_policy": frozenset({"env-u-git-index", "read-only"}),
        "verification_policy": frozenset({"report-evidence-only", "no-go"}),
        "routing_authority": frozenset({"report-only"}),
    },
    "director": {
        "capability_scope": frozenset({"seat-local"}),
        "mutation_scope": frozenset({"seat-owned"}),
        "mailbox_policy": frozenset({"seat-read", "consume-intentional"}),
        "git_policy": frozenset({
            "env-u-git-index", "per-seat-index-for-cursor-status",
        }),
        "verification_policy": frozenset({"request-operator-go", "no-go"}),
        "routing_authority": frozenset({"seat-owned"}),
    },
    "operator": {
        "capability_scope": frozenset({"seat-local"}),
        "mutation_scope": frozenset({"seat-owned"}),
        "mailbox_policy": frozenset({"seat-read", "consume-intentional"}),
        "git_policy": frozenset({
            "env-u-git-index", "per-seat-index-for-cursor-status",
        }),
        "verification_policy": frozenset({"independent-go-nits-fail"}),
        "routing_authority": frozenset({"seat-owned"}),
    },
    "coordinator": {
        "capability_scope": frozenset({"capacity-max"}),
        "mutation_scope": frozenset({"coordination-only"}),
        "mailbox_policy": frozenset({"all-scope-read", "no-consume"}),
        "git_policy": frozenset({"env-u-git-index", "temp-index"}),
        "verification_policy": frozenset({
            "reconcile-operator-go-only", "no-go",
        }),
        "routing_authority": frozenset({"all-scope-reconcile"}),
    },
    "protocol-director-subagent": {
        "capability_scope": frozenset({"orient", "parent-task"}),
        "mutation_scope": frozenset({"parent-named-paths"}),
        "mailbox_policy": frozenset({"read-only", "no-send", "no-consume"}),
        "git_policy": frozenset({"env-u-git-index", "parent-named-paths"}),
        "verification_policy": frozenset({"advisory", "no-go"}),
        "routing_authority": frozenset({"none"}),
    },
    "protocol-coordinator-subagent": {
        "capability_scope": frozenset({"orient", "parent-task"}),
        "mutation_scope": frozenset({"none"}),
        "mailbox_policy": frozenset({"read-only", "no-send", "no-consume"}),
        "git_policy": frozenset({"env-u-git-index", "read-only"}),
        "verification_policy": frozenset({"evidence-only", "no-go"}),
        "routing_authority": frozenset({"none"}),
    },
    "protocol-operator-subagent": {
        "capability_scope": frozenset({"orient", "parent-task"}),
        "mutation_scope": frozenset({"none"}),
        "mailbox_policy": frozenset({"read-only", "no-send", "no-consume"}),
        "git_policy": frozenset({"env-u-git-index", "read-only"}),
        "verification_policy": frozenset({"read-only-review", "no-go"}),
        "routing_authority": frozenset({"none"}),
    },
    "lane-v-verifier-subagent": {
        "capability_scope": frozenset({"orient", "parent-task"}),
        "mutation_scope": frozenset({"none"}),
        "mailbox_policy": frozenset({"read-only", "no-send", "no-consume"}),
        "git_policy": frozenset({"env-u-git-index", "read-only"}),
        "verification_policy": frozenset({"read-only-review", "no-go"}),
        "routing_authority": frozenset({"none"}),
    },
    "money-gate-reviewer-subagent": {
        "capability_scope": frozenset({"orient", "parent-task"}),
        "mutation_scope": frozenset({"none"}),
        "mailbox_policy": frozenset({"read-only", "no-send", "no-consume"}),
        "git_policy": frozenset({"env-u-git-index", "read-only"}),
        "verification_policy": frozenset({"read-only-review", "no-go"}),
        "routing_authority": frozenset({"none"}),
    },
}

DEFAULT_PUBLICATION_ELIGIBILITY_BY_ACTOR = {
    "readiness-bridge": False,
    "protocol-director-subagent": False,
    "protocol-coordinator-subagent": False,
    "protocol-operator-subagent": False,
    "lane-v-verifier-subagent": False,
    "money-gate-reviewer-subagent": False,
    "director": True,
    "operator": True,
    "coordinator": True,
}

PUBLICATION_POLICY_ENV = "CODEX_PUBLICATION_POLICY"
PUBLICATION_POLICY_TOKENS = frozenset({"false", "true"})
```

All six policy fields are `frozenset[str]` for every runtime actor. Environment
overrides are comma-delimited token sets, so a singleton legacy spelling is
still represented as a one-element `frozenset`; no actor receives a scalar
policy value.

Unknown or generic subagent roles fail closed. Every policy override is a
comma-separated set of unique lowercase ASCII tokens with no whitespace,
empty item, duplicate, or unknown token. Absent means the literal role default;
a present value must be a subset. Rendering is sorted and deterministic.
The environment serialization is `token,token` in sorted order; the empty
string is invalid rather than an empty set. Tests hard-code independent copies
of every vocabulary, default map, and publication boolean instead of importing
these production constants.

Publication remains a Boolean internally and has one independent wire grammar.
`CODEX_PUBLICATION_POLICY` absent means the resolved actor default. Its exact
lowercase ASCII serialization is one token: `true` or `false`; no trimming or
case-folding occurs. With a `true` default, explicit `true` is a valid no-op and
`false` is valid narrowing. With a `false` default, explicit `false` is a valid
no-op and `true` is invalid widening. `""` or any empty comma item is invalid-
empty; a value outside the vocabulary is invalid-unknown; `true,true` or
`false,false` is invalid-duplicate; and `true,false` or `false,true` is invalid-
conflict. Validation order is empty, unknown/malformed, duplicate, conflict,
then widening. Effective `false` defeats any otherwise-valid
`REMOTE_PUBLISH` appointment before token, key, ref, fetch, or mutation
callbacks. `infer_runtime_env()` renders only lowercase `true` or `false` and
adds `CODEX_PUBLICATION_POLICY` to `RUNTIME_ENV_VARIABLES`; no eligibility-
named alias exists.

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
    assert identity.verification_policy == frozenset({"independent-go-nits-fail"})


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
    ("readiness-bridge", None, None): frozenset({"orient"}),
    ("subagent", None, "protocol-director"): frozenset({"orient", "repository-mutate"}),
    ("subagent", None, "protocol-coordinator"): frozenset({"orient"}),
    ("subagent", None, "protocol-operator"): frozenset({"orient"}),
    ("subagent", None, "lane-v-verifier"): frozenset({"orient"}),
    ("subagent", None, "money-gate-reviewer"): frozenset({"orient"}),
    ("live-seat", "director", None): DIRECTOR_EXPECTED,
    ("live-seat", "director2", None): DIRECTOR_EXPECTED,
    ("live-seat", "operator", None): OPERATOR_EXPECTED,
    ("live-seat", "operator2", None): OPERATOR_EXPECTED,
    ("coordinator", "coordinator", None): COORDINATOR_EXPECTED,
    ("coordinator", "coordinator2", None): COORDINATOR_EXPECTED,
}
ALL_RUNTIME_MODES = (
    "readiness-bridge", "live-seat", "coordinator", "subagent",
)
ALL_CONCRETE_SEATS = (
    None, "director", "director2", "operator", "operator2",
    "coordinator", "coordinator2",
)
ALL_AGENT_ROLES = (
    None, "protocol-director", "protocol-coordinator", "protocol-operator",
    "lane-v-verifier", "money-gate-reviewer", "unknown-role",
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
    ("mode", "seat", "agent_role"),
    [
        (mode, seat, agent_role)
        for mode in ALL_RUNTIME_MODES
        for seat in ALL_CONCRETE_SEATS
        for agent_role in ALL_AGENT_ROLES
    ],
)
def test_complete_mode_seat_role_operation_matrix_is_exact(mode, seat, agent_role):
    identity = _identity_for_mode_seat_and_role(mode, seat, agent_role)
    expected = EXPECTED_BY_RUNTIME_IDENTITY.get((mode, seat, agent_role))
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


ALL_COMMAND_CLASS_VALUES = frozenset({
    "route-mutation", "lock-mutation-local", "lock-claim-remote",
    "lock-release-remote", "human-cursor-consume", "signed-cursor-local",
    "signed-cursor-from-remote", "signed-fact-emit-local",
    "signed-fact-emit-remote", "trust-root-bootstrap", "authority-cutover",
})
ALL_SERVICE_COMMAND_CLASS_VALUES = frozenset({
    "overseer-fact-emit", "chief-gemini-fact-emit",
    "chief-chatgpt-fact-emit", "ci-result-sign",
    "merge-gate-target-ref-update", "merge-gate-completion-emit",
})
EXPECTED_OPERATIONS_BY_COMMAND_CLASS = {
    "route-mutation": frozenset({"route-mutate"}),
    "lock-mutation-local": frozenset({"lock-mutate"}),
    "lock-claim-remote": frozenset({"lock-mutate", "remote-publish"}),
    "lock-release-remote": frozenset({"lock-mutate", "remote-publish"}),
    "human-cursor-consume": frozenset({"human-cursor-consume"}),
    "signed-cursor-local": frozenset({"signed-cursor-consume"}),
    "signed-cursor-from-remote": frozenset({"signed-cursor-consume"}),
    "signed-fact-emit-local": frozenset({"signed-fact-emit"}),
    "signed-fact-emit-remote": frozenset({
        "signed-fact-emit", "remote-publish",
    }),
    "trust-root-bootstrap": frozenset({"trust-root-bootstrap"}),
    "authority-cutover": frozenset({"authority-cutover"}),
}
EXPECTED_APPOINTABLE_ACTORS_BY_COMMAND_CLASS = {
    "lock-claim-remote": frozenset({"director", "coordinator"}),
    "lock-release-remote": frozenset({"director", "coordinator"}),
    "signed-fact-emit-remote": frozenset({
        "director", "operator", "coordinator",
    }),
    "trust-root-bootstrap": frozenset({"director", "coordinator"}),
    "authority-cutover": frozenset({"director", "coordinator"}),
}


def test_runtime_command_class_enum_and_bundles_are_exact():
    assert {command.value for command in RuntimeCommandClass} == ALL_COMMAND_CLASS_VALUES
    assert {
        command.value: frozenset(operation.value for operation in operations)
        for command, operations in model.OPERATIONS_BY_COMMAND_CLASS.items()
    } == EXPECTED_OPERATIONS_BY_COMMAND_CLASS


def test_service_command_class_enum_is_exact_and_disjoint():
    assert {command.value for command in ServiceCommandClass} == (
        ALL_SERVICE_COMMAND_CLASS_VALUES
    )
    assert ALL_COMMAND_CLASS_VALUES.isdisjoint(ALL_SERVICE_COMMAND_CLASS_VALUES)


def test_appointability_is_command_scoped_and_never_token_created():
    for mode, seat, agent_role in EXPECTED_BY_RUNTIME_IDENTITY:
        identity = _identity_for_mode_seat_and_role(mode, seat, agent_role)
        actor_class = model.actor_class(identity)
        for command_value in ALL_COMMAND_CLASS_VALUES:
            expected = actor_class in EXPECTED_APPOINTABLE_ACTORS_BY_COMMAND_CLASS.get(
                command_value, frozenset()
            )
            assert model.command_class_is_appointable(
                identity, RuntimeCommandClass(command_value)
            ) is expected

    operator = model.resolve_runtime_identity({"CODEX_SEAT": "operator"})
    assert model.command_class_is_appointable(
        operator, RuntimeCommandClass.SIGNED_CURSOR_FROM_REMOTE
    ) is False
```

In `tests/unit/test_protocol_executor_token.py`, hard-code complete token
fixtures and cover absent/unreadable/symlinked/uncommitted paths, duplicate or
wrong IDs, missing fields, wrong executor/target/class/HEAD, stale and newer
appointments, satisfied target, failed preflight, and each triggered stop
predicate. Every rejection occurs before a supplied mutation callback can run.
`tests/unit/test_protocol_capacity.py` proves route validation and the runtime
verifier parse identical fields and reject the same malformed token.
Hard-code the signed-fact publication GO section independently and reject a
missing/duplicate/unknown/reordered/extra/empty/non-ASCII field, invalid kind/
seat/candidate/SHA/target, non-GO verdict, wrong canonical sender, uncommitted
path, H1/publication SHA mismatch, and token/report mismatch before callbacks.

Add cumulative cases where valid identity/no token, invalid identity/valid
token, and wrong-actor token all fail before a mutation callback, while both
valid gates succeed. Hard-code the actor x operation x supported-subagent-role
matrix plus every policy's default/narrow/empty/unknown/widen/duplicate/conflict
cases. Assert the doctor command contains both identity and executor-token
suites. One-fact flips remove `SIGNED_FACT_EMIT` from token-required
operations, grant repository mutation to one read-only role, and change the
token HEAD; each must fail independently. Separately add
`SIGNED_CURSOR_FROM_REMOTE` to the appointability map, remove
`REMOTE_PUBLISH` from one remote-lock bundle, and change one runtime or service
command enum value; the hard-coded command-class tests must independently RED
before restoration.

For publication specifically, independently hard-code every actor default and
cover `{default=true,false} × {override absent,true,false}`; `""`, `","`,
uppercase, whitespace, `0`, `1`, unknown, duplicate, and both conflict orders;
deterministic lowercase rendering; and an unknown/generic actor with no
fallback. An effective `false` plus an otherwise-valid remote-publication
appointment must fail before all token and mutation probes.

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
`SessionBindingView`, `RuntimeOperation`, `RuntimeCommandClass`, the resolver,
publication-policy grammar, and the typed token module. Hook failures are not
expected from this selector and belong to Task 3B.

- [ ] **Step 3: Implement `RuntimeIdentity` and strict resolution**

Resolve mode and role family from the concrete seat first. An explicit role
must equal the derived role family, never the concrete-seat spelling or
behavior source. Canonical behavior source is derived separately and must match
exactly when explicitly supplied.

Represent capability, mutation, mailbox, git, verification, and routing
policies as immutable token sets. An override is valid only when its requested
tokens are a subset of the resolved defaults; absent means no override, while
present-but-empty and unknown tokens are invalid. Publication eligibility may
only narrow from eligible to ineligible under the exact Boolean wire grammar
above. Runtime eligibility never substitutes
for user consent, executor election, operator GO, or a target-bound
side-effect token.

Resolve and preserve the exact supported `agent_role` for subagent mode. Apply
the literal role defaults and serialization grammar above; generic/unknown
subagents and any role reinterpreted as a concrete seat are invalid.

Emit errors in this deterministic order: unknown values; topology mismatch;
role-family mismatch; behavior-source mismatch; missing or conflicting session
binding; unknown policy tokens; widening override; positional-actor mismatch;
missing operation capability.

Read-only rendering returns an invalid object with errors. The CLI validator and
mutation hooks treat any invalid object as fatal.

- [ ] **Step 4: Add strict and operation-aware entry points**

`require_runtime_identity()` and bare eligibility checks must preserve the
resolver's ordered errors and add only actor/operation errors after the
identity checks. CLI success is quiet. CLI failure writes stable error codes to
stderr without dumping the environment and exits nonzero.

Implement the generic token module and move capacity validation onto it in the
same commit. Token paths are resolved beneath the primary checkout, opened
without following symlinks, and must be present in the exact committed HEAD.
Appointment freshness is determined from durable mailbox order, not caller
prose. `failed_preflight` and `triggered_stop_predicates` must both be empty;
the verifier does not attempt to reinterpret free-form safety text.

Implement `authorize_side_effect_operations()` as the only token-required
mutation-facing composition point. It validates the whole requested operation bundle and the
one token before returning. A command-class bundle mismatch, partial operation
set, absent publication eligibility, or either gate failing returns no identity
or token object to the caller.

Update `CODEX_VERIFICATION_COMMANDS` in the same commit so the identity and
executor-token suites are both part of the model-derived doctor gate, with
hard-coded ledger-bridge assertions.

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
- Modify: `scripts/codex_protocol_model.py`
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
- Modify: `tests/unit/test_codex_ledger_bridge.py`

**Interfaces:**
- Produces frozen `SessionBinding(schema_version, session_id, mode, concrete_seat, role_family, agent_role, created_head)`.
- Produces `bind_session(root: Path, *, session_id: str, mode: str, concrete_seat: str | None, role_family: str | None, agent_role: str | None) -> SessionBinding` and `load_session_binding(root: Path, session_id: str) -> SessionBinding`.
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
  `authorize_side_effect_operations(...,
  operations={RuntimeOperation.ROUTE_MUTATE},
  command_class=RuntimeCommandClass.ROUTE_MUTATION, ...)` with the actual
  executor, normalized
  route target, current HEAD/appointment, and freshly evaluated preflight/stop
  results before allowing the tool.
- Every supported subagent role round-trips exactly through the binding. A
  changed role at the same session ID is a conflicting rebind; a generic or
  unknown subagent role is invalid.

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

Add one binding round-trip and one conflicting-rebind case for each supported
subagent role. Assert `CODEX_VERIFICATION_COMMANDS` and the ledger bridge both
register `test_codex_session_binding.py`.

- [ ] **Step 2: Run tests to prove RED**

```bash
env -u GIT_INDEX_FILE .venv/bin/python -m pytest tests/unit/test_codex_session_binding.py tests/unit/test_coordination_tooling.py tests/unit/test_protocol_prompt_sync.py tests/unit/test_codex_ledger_bridge.py -q
```

Expected: missing binding module/CLI and current hook mutations before identity
validation.

- [ ] **Step 3: Implement the tracked binding launcher**

Expose:

```bash
scripts/codex_session_binding.py bind --session-id "$CODEX_SESSION_ID" \
  --mode live-seat --seat director --role-family director
scripts/codex_session_binding.py bind --session-id "$CODEX_SESSION_ID" \
  --mode subagent --agent-role protocol-director
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
`authorize_side_effect_operations(..., operations={RuntimeOperation.ROUTE_MUTATE},
expected_actor=identity.concrete_seat, ...)` before allowing the tool. Separate
identity-only and token-only checks are forbidden. It uses the session's
explicit token path/ID. Literal Bash route targets are
classified before execution; unclassifiable dynamic route writes are refused
with a stable error code.

Register `tests/unit/test_codex_session_binding.py` in the model-derived doctor
selector in this commit and pin it in `test_codex_ledger_bridge.py`.

- [ ] **Step 5: Prove GREEN and non-vacuity**

```bash
env -u GIT_INDEX_FILE .venv/bin/python -m pytest tests/unit/test_codex_session_binding.py tests/unit/test_coordination_tooling.py tests/unit/test_protocol_prompt_sync.py tests/unit/test_codex_ledger_bridge.py -q
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
- Modify: `scripts/codex_protocol_model.py`
- Modify: `coordination/bin/send-event`
- Modify: `coordination/bin/consume-events`
- Modify: `coordination/bin/claim-lock`
- Modify: `coordination/bin/release-lock`
- Modify: `scripts/consume_bus.py`
- Modify: `scripts/seat_emit.py`
- Create: `tests/unit/test_runtime_operation_guards.py`
- Modify: `tests/unit/test_coordination_tooling.py`
- Modify: `tests/unit/test_codex_ledger_bridge.py`

**Interfaces:**
- Each token-required mutating command calls
  `authorize_side_effect_operations()` before its first input read, object
  construction, key load, file, index, ref, or lock mutation. Ordinary
  `MAIL_SEND` and `OPERATOR_VERDICT` call `authorize_operation()` and remain
  token-exempt but identity/authority gated.
- Route `send-event`, `claim-lock`, `release-lock`, `consume-events`,
  `scripts/consume_bus.py`, and `scripts/seat_emit.py` require explicit
  `--executor-token PATH` and
  `--side-effect-id ID` arguments. Each calls the Task-3A
  cumulative authorizer with its actual executor, exact target, frozen command
  bundle, current HEAD/appointment, target state, and freshly evaluated
  preflight/stop results.
- `claim-lock` uses `LOCK_CLAIM_REMOTE` and `release-lock` uses
  `LOCK_RELEASE_REMOTE`, each requesting exactly
  `{LOCK_MUTATE, REMOTE_PUBLISH}` against
  `git-remote:<remote>#refs/heads/<branch>:coordination/locks/<lock-file>`.
  Authorization completes before fetch, merge, lock-file write/removal, add,
  commit, push, or reset. `LOCK_MUTATION_LOCAL` is reserved for an explicitly
  local lock-file mutation; the ambiguous `lock-mutation` class does not exist.
- `coordination/bin/send-event` requires `MAIL_SEND` for every event. When and
  only when the validated bound sender is `coordinator` or `coordinator2`, the
  target is `all`, and the kind is `coordination`, it additionally requires
  `ROUTE_MUTATE` before reading stdin or creating a temporary file. Direct
  Edit/Write/`apply_patch` route creation remains covered by Task 3B's
  path-aware PreToolUse gate.
  Thus a route send completes both checks before input: bare
  `authorize_operation(..., MAIL_SEND)` and cumulative
  `authorize_side_effect_operations(..., {ROUTE_MUTATE},
  command_class=RuntimeCommandClass.ROUTE_MUTATION, ...)`.
- Positional actor must equal the validated bound actor and never establishes
  identity.
- GO/NITS/FAIL emission requires an operator-family concrete seat with
  verification authority. Director, coordinator, readiness, and subagent
  identities cannot acquire verdict authority.
- `scripts/seat_emit.py` changes `--remote` from default `origin` to no remote.
  Local emit requests `{SIGNED_FACT_EMIT}` against the exact local events ref;
  opt-in remote emit requests `{SIGNED_FACT_EMIT, REMOTE_PUBLISH}` against the
  exact remote/ref. An operator remote emit additionally supplies the exact
  `SignedFactPublicationBinding`; its opposite-operator committed GO report
  must bind fact signer/kind, candidate, expected HEAD, and publication target.
  The returned binding drives construction and must match the built event.
  Authorization precedes event building, key loading, Git-object creation,
  fetch, append, or push.
- `scripts/consume_bus.py` uses `{SIGNED_CURSOR_CONSUME}` for both local events
  and `--remote` event-source reads. The latter uses
  `SIGNED_CURSOR_FROM_REMOTE`, but cursor mutation remains local-only and never
  requests `REMOTE_PUBLISH`. Any attempted `signed-cursor-remote` class is
  unknown and fails before fetch or cursor mutation.

- [ ] **Step 1: Write actor/operation mismatch regressions**

Cover mail send, human cursor consume, lock claim/release, signed-fact cursor
consume, signed-fact emission, and GO/NITS/FAIL. For every denial, assert zero
mailbox, cursor, lock, ref, and index mutation. Include readiness, subagent,
coordinator-consume, director-verdict, and positional/bound-actor mismatch.

Cover local signed emit, remote signed emit, and local cursor advance while
events are read from a remote authority.
Wrong remote/ref/HEAD, absent/stale/superseded token, valid identity/no token,
and valid token/invalid identity must all leave key-read, Git-object, fetch,
push, ref, cursor, and index probes untouched.

For both lock scripts, cover absent/stale/wrong-target/wrong-HEAD/wrong-class
tokens, `{LOCK_MUTATE}` alone, and `{REMOTE_PUBLISH}` alone. Every denial proves
zero fetch, merge, add/rm, commit, push, and reset calls and byte/OID-identical
lock, HEAD, index, refs, and worktree. The exact two-operation bundle reaches
the expected command path.

For operator remote signed-fact publication, reject a remote cursor class,
another seat's fact, a disallowed kind, a different candidate, same-seat or
missing verifier, an uncommitted/wrong-verifier GO report, or a report bound to
another HEAD/target. Each denial leaves event/ref/key/fetch/object/push probes
untouched; the valid case uses the operator's own fact plus the opposite
operator's committed GO.

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
env -u GIT_INDEX_FILE .venv/bin/python -m pytest tests/unit/test_runtime_operation_guards.py tests/unit/test_protocol_executor_token.py tests/unit/test_coordination_tooling.py tests/unit/test_codex_ledger_bridge.py -q
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

Apply the frozen local/remote operation bundles to both lock scripts,
`seat_emit.py`, and `consume_bus.py`. Register
`tests/unit/test_runtime_operation_guards.py` in
`CODEX_VERIFICATION_COMMANDS` and hard-code the addition in the ledger bridge.

- [ ] **Step 4: Prove GREEN and non-vacuity**

```bash
env -u GIT_INDEX_FILE .venv/bin/python -m pytest tests/unit/test_runtime_operation_guards.py tests/unit/test_protocol_executor_token.py tests/unit/test_coordination_tooling.py tests/unit/test_codex_ledger_bridge.py -q
```

Change one expected actor to match the bound actor and confirm the mismatch
assertion fails. Then replace a valid token's expected HEAD with a sibling SHA
and confirm the command refuses before its stdin-read probe. Restore both and
rerun GREEN. Separately remove `REMOTE_PUBLISH` from each remote-lock and
remote-fact bundle, then independently flip operator fact signer, candidate,
verifier, and command class; every affected node must RED before restoration
and final GREEN.

- [ ] **Step 5: Review and commit Task 3C**

```bash
env -u GIT_INDEX_FILE git commit -m "fix(protocol): authorize interactive mutations"
```

---

### Task 3D: Close Mechanical And Service-Principal Authority

**Owner:** Pair B director2 implementation after Task 3C GO; Pair B operator2 verification.

**Files:**
- Modify: `scripts/codex_protocol_model.py`
- Create: `scripts/protocol_principal.py`
- Modify: `scripts/chief_emit.py`
- Modify: `scripts/overseer_emit.py`
- Modify: `scripts/sign_ci_result.py`
- Modify: `scripts/run_merge_gate.py`
- Modify: `scripts/run_merge_gate.sh`
- Create: `scripts/run_proof_acquirer.py`
- Create: `scripts/verify_proof_acquirer_macos.py`
- Modify: `threeway/gate.py`
- Modify: `threeway/gitcas.py`
- Create: `threeway/proof_acquisition.py`
- Modify: `threeway/refstore.py`
- Create: `coordination/threeway/proof-runtime/com.pipeline.proof-acquirer.plist`
- Create: `tests/unit/test_service_principals.py`
- Create: `tests/unit/test_proof_acquisition.py`
- Modify: `tests/unit/test_threeway_activation_scripts.py`
- Modify: `tests/unit/test_codex_ledger_bridge.py`
- Create: `tests/integration/test_proof_acquisition_macos.py`
- Create from the privileged verifier: `logs/proof-acquisition-isolation-pipeline-local-authority-2026-07-10.json`

**Interfaces:**
- Produces frozen
  `MechanicalPrincipal(principal_id, allowed_operations,
  signer_by_operation, token_required_operations,
  credential_required_targets, execution_context, identity_valid,
  validation_errors)`.
- Produces a closed execution-context contract:

```python
class MechanicalExecutionContext(str, Enum):
    CONTROL_PLANE = "control-plane"
    CI_RUNNER = "ci-runner"
    PROTECTED_RUNNER = "protected-runner"
    CANDIDATE = "candidate"

MECHANICAL_EXECUTION_CONTEXTS_BY_PRINCIPAL = {
    "overseer": frozenset({MechanicalExecutionContext.CONTROL_PLANE}),
    "chief-gemini": frozenset({MechanicalExecutionContext.CONTROL_PLANE}),
    "chief-chatgpt": frozenset({MechanicalExecutionContext.CONTROL_PLANE}),
    "ci": frozenset({MechanicalExecutionContext.CI_RUNNER}),
    "merge-gate": frozenset({MechanicalExecutionContext.PROTECTED_RUNNER}),
}
```

`CANDIDATE` is deliberately absent from every allowed set. Unknown strings,
the candidate context, and every known-but-wrong principal/context pairing
return an invalid principal before key, credential, ref, fact, or token access.
- Exact operation map:

```python
SERVICE_OPERATIONS = {
    "overseer": frozenset({"emit-overseer-fact"}),
    "chief-gemini": frozenset({"emit-chief-fact"}),
    "chief-chatgpt": frozenset({"emit-chief-fact"}),
    "ci": frozenset({"sign-ci-result"}),
    "merge-gate": frozenset({
        "evaluate-merge-gate", "update-target-ref", "emit-merge-completed",
    }),
}

SERVICE_SIGNERS = {
    ("overseer", "emit-overseer-fact"): "overseer",
    ("chief-gemini", "emit-chief-fact"): "chief-gemini",
    ("chief-chatgpt", "emit-chief-fact"): "chief-chatgpt",
    ("ci", "sign-ci-result"): "ci",
    ("merge-gate", "update-target-ref"): "merge-gate",
    ("merge-gate", "emit-merge-completed"): "merge-gate",
}

TOKEN_REQUIRED_SERVICE_OPERATIONS = frozenset(SERVICE_SIGNERS)
CREDENTIAL_REQUIRED_TARGETS = frozenset({"refs/heads/main"})
SERVICE_OPERATION_BY_COMMAND_CLASS = {
    ServiceCommandClass.OVERSEER_FACT_EMIT:
        ("overseer", "emit-overseer-fact"),
    ServiceCommandClass.CHIEF_GEMINI_FACT_EMIT:
        ("chief-gemini", "emit-chief-fact"),
    ServiceCommandClass.CHIEF_CHATGPT_FACT_EMIT:
        ("chief-chatgpt", "emit-chief-fact"),
    ServiceCommandClass.CI_RESULT_SIGN: ("ci", "sign-ci-result"),
    ServiceCommandClass.MERGE_GATE_TARGET_REF_UPDATE:
        ("merge-gate", "update-target-ref"),
    ServiceCommandClass.MERGE_GATE_COMPLETION_EMIT:
        ("merge-gate", "emit-merge-completed"),
}
```

The resolver materializes each principal's `signer_by_operation` as an
immutable `Mapping[str, str]`, `token_required_operations` as a
`frozenset[str]`, and `credential_required_targets` as a `frozenset[str]`.
Pure `evaluate-merge-gate` has no signer and is absent from the token set.
For token-required operations, `command_class` must map exactly to the same
principal/operation pair in `SERVICE_OPERATION_BY_COMMAND_CLASS`; the exact
local or remote ref remains part of the token target.

- Mechanical principals never synthesize `CODEX_SEAT` or interactive seat
  authority. Protected-main update additionally requires the exact
  target-bound executor token and protected runner credential.
- Produces exact entry points:

```python
@dataclass(frozen=True, slots=True)
class RepositoryIdentity:
    common_git_dir: str
    device: int
    inode: int


@dataclass(frozen=True, slots=True)
class AttestedPathIdentity:
    path: Path
    device: int
    inode: int
    owner_uid: int
    owner_gid: int
    mode: int
    acl_sha256: str
    parent_chain: tuple[tuple[str, int, int, int, int, int, str], ...]


@dataclass(frozen=True, slots=True)
class AttestedProofFile:
    purpose: str
    identity: AttestedPathIdentity
    sha256: str
    executable: bool


@dataclass(frozen=True, slots=True)
class ProtectedProofRuntimeAttestation:
    schema_version: Literal["proof-runtime-v1"]
    deployment_id: str
    manifest_identity: AttestedPathIdentity
    manifest_sha256: str
    gate_account: Literal["_pipeline_merge_gate"]
    gate_uid: int
    proof_account: Literal["_pipeline_proof"]
    proof_uid: int
    deployment_root: AttestedPathIdentity
    authority_manifest: AttestedProofFile
    registry_keys: tuple[AttestedProofFile, ...]
    bus_id: Literal["prod"]
    event_store_endpoint: str
    event_ref: Literal["refs/threeway/events"]
    gate_seat: Literal["merge-gate"]
    policy_digest: str
    git: AttestedProofFile
    git_exec_helpers: tuple[AttestedProofFile, ...]
    transport_helpers: tuple[AttestedProofFile, ...]
    tls_ca_bundle: AttestedProofFile
    proof_launchd_plist: AttestedProofFile
    proof_python: AttestedProofFile
    proof_service: AttestedProofFile
    proof_source_commit: str
    proof_source_bundle_sha256: str
    proof_source_plist_sha256: str
    proof_socket_parent: AttestedPathIdentity
    proof_socket_path: Path
    allowed_protocols: tuple[Literal["https"], ...]


@dataclass(frozen=True, slots=True)
class _ProtectedProofRuntime:
    attestation: ProtectedProofRuntimeAttestation


@dataclass(frozen=True, slots=True)
class _ProofAcquisitionSession:
    socket_fd: int
    peer_uid: int
    session_id: str
    acquired_state: "_AcquiredEventState"


@dataclass(frozen=True, slots=True)
class _ProofRepositoryHandle:
    directory_fd: int
    device: int
    inode: int


@dataclass(frozen=True, slots=True)
class EventStoreTarget:
    repository: RepositoryIdentity
    remote: str | None
    push_endpoint: str | None
    events_ref: str
    normalized_target: str


@dataclass(frozen=True, slots=True)
class _AcquiredEventState:
    event_store: EventStoreTarget
    tip_oid: str
    tip_tree_oid: str
    event_json: tuple[bytes, ...]
    digest: str


@dataclass(frozen=True, slots=True)
class _CanonicalGateAuthority:
    registry_dir: Path
    registry_digest: str
    bus_id: str
    gate_seat: Literal["merge-gate"]
    policy: Policy
    policy_digest: str
    authority_digest: str


class SnapshotProvenanceError(ValueError): ...


class RefTransactionDomainError(ValueError): ...


@dataclass(frozen=True, slots=True)
class RefTarget:
    repository: RepositoryIdentity
    remote: str | None
    push_endpoint: str | None
    ref: str
    normalized_target: str


@dataclass(frozen=True, slots=True)
class MergeMaterialization:
    base_sha: str
    branch_sha: str
    tree_oid: str
    commit_oid: str
    message: str


@dataclass(frozen=True, slots=True)
class MergeGateBinding:
    candidate_id: str
    target: RefTarget
    bus_id: str
    gate_authority_digest: str
    event_store: EventStoreTarget
    events_tip_oid: str
    events_digest: str
    materialization: MergeMaterialization | None
    expected_old_sha: str | None
    proposed_merge_sha: str | None


@dataclass(frozen=True, slots=True, init=False)
class _PreparedEventAppend:
    event_store: EventStoreTarget
    expected_tip_oid: str
    new_tip_oid: str
    event_id: str
    # Private quarantine-object capability retained only by preparation.
    _quarantine_object_dir: Path


@dataclass(frozen=True, slots=True)
class MergeGateEvaluation:
    binding: MergeGateBinding
    outcome: Literal["REJECTED", "PENDING", "MERGEABLE", "COMPLETED"]
    reason: str


@dataclass(frozen=True, slots=True)
class PrincipalTokenRevalidation:
    token_path: Path
    side_effect_id: str
    command_class: ServiceCommandClass
    expected_head: str
    current_appointment_path: Path


@dataclass(frozen=True, slots=True)
class AuthorizedPrincipalOperation:
    principal: MechanicalPrincipal
    operation: str
    effect_target: str
    merge_binding: MergeGateBinding | None
    executor_token: SideEffectExecutorToken | None
    token_revalidation: PrincipalTokenRevalidation | None
    protected_credential_attested: bool


class ProtectedRunnerCredential(Protocol):
    def attest_target(self, target: str) -> bool: ...


def resolve_mechanical_principal(
    *, principal_id: str, signer_identity: str | None,
    execution_context: MechanicalExecutionContext | str,
) -> MechanicalPrincipal: ...


def authorize_principal_operation(
    root: Path,
    principal: MechanicalPrincipal,
    *,
    operation: str,
    effect_target: str,
    merge_binding: MergeGateBinding | None = None,
    token_path: Path | None = None,
    side_effect_id: str | None = None,
    command_class: ServiceCommandClass | None = None,
    expected_head: str | None = None,
    current_appointment_path: Path | None = None,
    newer_appointment_paths: Sequence[Path] = (),
    target_satisfied: bool = False,
    failed_preflight: Sequence[str] = (),
    triggered_stop_predicates: Sequence[str] = (),
    protected_runner_credential: ProtectedRunnerCredential | None = None,
) -> AuthorizedPrincipalOperation: ...


def resolve_repository_identity(repo: Path) -> RepositoryIdentity: ...


def _load_protected_proof_runtime() -> _ProtectedProofRuntime: ...


def _resolve_canonical_gate_authority(
    runtime: _ProtectedProofRuntime,
) -> _CanonicalGateAuthority: ...


def _connect_proof_acquirer(
    runtime: _ProtectedProofRuntime,
) -> _ProofAcquisitionSession: ...


def _revalidate_proof_acquisition(
    runtime: _ProtectedProofRuntime,
    session: _ProofAcquisitionSession,
) -> _AcquiredEventState: ...


def _run_proof_git(
    runtime: _ProtectedProofRuntime,
    gitdir_fd: int,
    argv: Sequence[str],
) -> subprocess.CompletedProcess[bytes]: ...


def describe_event_store(store: RefEventStore) -> EventStoreTarget: ...


def resolve_ref_target(
    repo: Path, *, ref: str, remote: str | None,
) -> RefTarget: ...


@contextmanager
def _capture_validated_event_state(
    store: RefEventStore,
    expected_tip_oid: str | None = None,
) -> Iterator[_AcquiredEventState]: ...


def _prepare_append_at(
    store: RefEventStore,
    event: Event,
    private_key,
    *,
    expected_tip_oid: str,
    quarantine: Path,
) -> _PreparedEventAppend: ...


def compute_merge_in_scratch(
    repo: Path, base_sha: str, branch_sha: str, message: str,
) -> MergeMaterialization | None: ...


def materialize_and_cas_verified_merge(
    repo: Path,
    *,
    target: RefTarget,
    expected_old_sha: str,
    materialization: MergeMaterialization,
    completion_append: _PreparedEventAppend,
) -> bool: ...


def evaluate_gate_read_only(
    *,
    candidate_id: str,
    store: RefEventStore,
    repo: Path,
    target: RefTarget,
) -> MergeGateEvaluation: ...


def apply_gate_evaluation(
    evaluation: MergeGateEvaluation,
    store: RefEventStore,
    repo: Path,
    *,
    target_ref_authorization: AuthorizedPrincipalOperation,
    completion_fact_authorization: AuthorizedPrincipalOperation,
) -> GateResult: ...
```

There is no public `EventSnapshot` type, constructor, factory, validation
function, proof capability, or caller-supplied Git/helper/manifest/proof-
repository/target/tip/tree/byte/digest path, authority root, registry, bus ID,
gate seat, or policy. `evaluate_gate_read_only()` accepts the trusted
`RefEventStore` and completes protected-runtime/authority resolution, capture,
independent validation,
reduction, and evaluation inside one private
`_capture_validated_event_state()` lexical lifetime. The runner's real
`poll_once()` enters that private context exactly once for the whole poll; its
private candidate collector and every private candidate evaluator consume the
same `_AcquiredEventState` identity. Neither that state nor the private
`_ProtectedProofRuntime` crosses a public argument or return boundary. The
proof repository path/ref remains closure-local.

The state stores only immutable ordered JSON bytes and their binding. Candidate
discovery parses temporary `Event` values only to return a frozen candidate-ID
set and discards them. Each candidate reduction independently reparses a fresh
`Event` list from `event_json` immediately before verification/reduction. With
two candidates, mutating the first reduction's parsed payload cannot alter the
second reduction, and the capture context entry count remains exactly one.

Public `MergeGateEvaluation` contains immutable `MergeGateBinding`, `outcome`,
and `reason`. The binding's target/event identity, tip, digest, materialization,
expected-old values plus `gate_authority_digest` are comparison data, not
mutation authority; it exposes no proof path/ref, event bytes,
`_ProtectedProofRuntime`, executable/helper handle, private quarantine path, or
live/callable store capability. Direct `evaluate_gate_read_only()` and
`poll_once()` return the same public type. Neither API accepts a root,
registry, bus ID, gate seat, or `Policy`; both resolve those values from the
zero-argument protected runtime before store/candidate access.
`apply_gate_evaluation()` likewise reloads that runtime and canonical authority
instead of accepting any of those choices. It treats every public field as an
untrusted claim. Before loading the runtime or touching a key, object, ref, or
filesystem authority path, it recursively requires exact concrete dataclass/
enum types and canonical primitive/container shapes for the evaluation and both
authorizations, using `object.__getattribute__` on exact slot classes, and
serializes inert primitives without invoking attacker-dispatched `__eq__`. A
subclass, hostile scalar, extra/missing field, or forged nested binding denies
at that first boundary. Only then does apply reload the runtime, resolve the
canonical authority, require its fresh digest to match the validated claimed
primitive, reacquire the canonical event state, and rerun the gate for the
validated candidate/target under the exact policy. It compares fresh canonical
primitives, compares the fresh exact `str` outcome directly to literal
`MERGEABLE`, and uses only the fresh binding downstream. An authorization whose
validated primitives differ from that fresh binding denies before token, key,
object, or ref access. Token/appointment revalidation also uses the attested
deployment root from that runtime, never a caller root. Swapping authorizations
between two same-target evaluations still denies. An alternate key registry,
bus ID, gate seat, or permissive policy is therefore not expressible at the
public boundary and a protected-manifest mismatch fails closed.
Frozen/slot/init restrictions and generated dataclass equality are not treated
as opacity or validation.

For both local and remote stores the private context opens one authenticated
session to the distinct proof-acquisition service. That service resolves the
canonical event ref, copies only that ref into a disposable bare repository
owned by `proof_uid`, records the actual fetched tip and tree OIDs, traverses
that tree for the canonical ordered event bytes, and computes SHA-256 over
length-prefixed bytes plus the complete `EventStoreTarget`, tip OID, and tree
OID. The gate process receives only a versioned length-framed canonical
response; it never receives the proof path, repository descriptor, Git argv, or
writable capability. The service retains `_ProofRepositoryHandle` for the one
session. Immediately before each reduction the gate requests revalidation over
that same session; the service independently resolves the retained proof ref,
re-traverses the actual Git object graph, and returns a fresh canonical frame.
The gate validates exact frame types/lengths and constant-time compares target,
tip, tree, ordered bytes, and digest before parsing fresh event values. Thus a
self-consistent digest over a caller-chosen subset cannot claim provenance from
a real tip. The context sends one close frame and revokes the socket/session;
the service closes and removes all private state. Remote capture never fetches
into the input repository or calls the production remote store's syncing
reader.

Proof creation and traversal do not reuse the general `threeway.gitcas._run()`
or helpers that collapse missing/wrong-type objects to `None` or `[]`.
`run_merge_gate.py` exposes no `--proof-git-executable`, helper-directory,
manifest, exec-path, transport, proof-repository, registry, bus, gate-seat, or
policy option. `scripts/run_merge_gate.sh` supplies none of those flags.
`poll_once()` likewise accepts no registry, bus, gate-seat, or policy keyword;
the existing activation-script caller is migrated rather than retained through
a compatibility parameter. Before store construction, key access, or candidate
input, `_load_protected_proof_runtime()` opens exactly
`/private/etc/pipeline/proof-runtime-v1.json` by walking from `/`
component-by-component with no-follow descriptors. Production exposes no
override; tests replace only the private zero-argument loader.

The manifest requires distinct nonzero `gate_uid` and `proof_uid` values. The
gate loader fails unless `getuid() == geteuid() == gate_uid`; the proof service
loader fails unless both IDs equal `proof_uid`. `pwd.getpwuid()` must map them
exactly to `_pipeline_merge_gate` and `_pipeline_proof`; both accounts use
`/var/empty` and `/usr/bin/false`, and the launchd plist's `UserName` is exactly
`_pipeline_proof`. Both loaders resolve their UID's complete group set and use
Darwin's native extended-ACL API plus mode/owner checks. Any direct, group, or
ACL grant of write, append,
delete/delete-child, write-attributes, write-extended-attributes, write-owner,
or equivalent tree-changing authority on the manifest, an ancestor, or any
attested file fails closed. Root or a distinct deployment identity owns those
paths; neither runtime UID can chmod, replace, chown, or retarget them.

The attestation binds its own digest; the protected deployment root and
committed `coordination/authority.toml`; every exact public key in
`coordination/threeway/keys`; literal bus `prod`; literal seat `merge-gate`;
the canonical HTTPS event-store endpoint and literal
`refs/threeway/events`; the in-code `default_policy()` digest; HTTPS-only proof
acquisition; the
root-owned `/Library/LaunchDaemons/com.pipeline.proof-acquirer.plist`; exact
deployed Python interpreter and proof-service script; a fixed proof-owned Unix
socket parent and socket path; a private proof-owned `0700` temporary root; the
exact regular Git and deployed `git-remote-http[s]`/required exec-helper files;
and one regular TLS CA bundle.
The protected runtime attestation binds the source commit plus committed
service-bundle/plist digests and requires the deployed plist to be
byte-identical to
`coordination/threeway/proof-runtime/com.pipeline.proof-acquirer.plist` at that
commit. This does not add fields to `coordination/authority.toml`; that
separately attested authority manifest keeps its current channel decisions.
`_resolve_canonical_gate_authority(runtime)` accepts no caller path, bus, seat,
registry, or policy. It requires signed-facts authority `live`, the canonical
events ref, exact individual key identities/digests, and an exact policy-digest
match, then length-prefix hashes all of them into `authority_digest`.

Each executable, public key, authority/CA file, runtime/launchd manifest, and
service file is validated individually by absolute lexical path, SHA-256,
device, inode, owner, regular/executable-as-applicable mode, native ACL
disposition, and protected non-writable parent chain. Binding only its directory
is invalid. The system-domain launchd job is `KeepAlive`, names the locked
non-login proof account through `UserName`, and starts the attested interpreter
and service. It is deliberately not socket-activated: the proof process itself
binds and listens on the fixed Unix stream socket so `getpeereid()` reports the
proof UID to the connecting gate rather than launchd's listener credentials.
The socket parent is proof-owned, group-searchable but not group-writable by the
gate, and the socket is connectable only by the exact gate group. The service
accepts only a peer whose effective UID is `gate_uid`; the client accepts only a
listener whose effective UID is `proof_uid`. Unknown frame versions, extra
fields, oversized lengths, caller URL/ref/registry/bus/policy/helper values,
wrong peer credentials, and reconnect/session replay fail closed. The service
derives its endpoint/ref only from its independently loaded protected runtime;
the trusted public store description must match that canonical target but
cannot select it.

The proof Gitdir is created descriptor-relative beneath the proof service's
private root and manually prepared without `config`, `config.worktree`, or
`commondir`. Only `proof_uid` owns the acquisition lifetime; the gate UID and
all candidate/user processes receive neither path nor descriptor and have no
mode/group/ACL authority to create, replace, chmod, or delete its entries.
Before and after every command the service reopens and rechecks the runtime
manifest, launchd plist, service/interpreter, Git executable, every required
exec/transport helper, every registry key, authority manifest, CA file, the
held Gitdir descriptor identity/type, exact top-level redirect absence, and
forbidden proof metadata. A post-load/pre-command barrier is part of the test
contract; a drifted file rejects before launch, and post-command drift discards
all output before parsing or reduction.

`_run_proof_git(runtime, gitdir_fd, argv)` is private to the proof service in
`threeway/proof_acquisition.py`. It creates pipes, forks, and in the child calls
`fchdir(gitdir_fd)` followed immediately by `execve()` of the attested absolute
Git with `--git-dir=.`; the parent captures bytes/status, waits, and rechecks the
held descriptor and lexical disposition. No lexical `--git-dir=<path>`,
`preexec_fn`, or caller command reaches the service. Missing `fork`, `fchdir`,
or `execve`, child launch failure, signal exit, or nonzero status fails closed.
A proof-path rename after the last service-side check therefore cannot redirect
Git, replacing any attested file after successful runtime load is caught at the
command barrier, and the separate proof UID prevents a gate-UID process from
changing repository contents during the child lifetime.

The runner invokes the attested Git with the attested exact `--exec-path`,
`--no-replace-objects --no-lazy-fetch --literal-pathspecs`, explicit
`protocol.allow=never` plus only HTTPS, `--no-write-fetch-head` for remote
acquisition, and no SSH/custom-helper path. Its fixed child `PATH` contains only
attested deployed helpers. The child environment starts from an empty mapping,
not `os.environ`, and contains only the exact attested-helper `PATH`,
`LC_ALL=C`, `LANG=C`, the descriptor-created private `TMPDIR`,
`GIT_NO_REPLACE_OBJECTS=1`, `GIT_CONFIG_NOSYSTEM=1`,
`GIT_CONFIG_GLOBAL=/dev/null`, `GIT_CONFIG_COUNT=0`,
`GIT_TERMINAL_PROMPT=0`, `GIT_PROTOCOL_FROM_USER=0`,
`GIT_ALLOW_PROTOCOL=https`, and the attested CA path in
`GIT_SSL_CAINFO`/`SSL_CERT_FILE`. Every invocation also fixes
`http.sslVerify=true`, `http.sslCAInfo=<attested-ca>`, an empty CA-directory,
empty HTTP/HTTPS proxy values, disabled redirects, and the HTTPS-only protocol
policy on the command line. No `HOME`, dynamic-loader, credential, proxy,
alternate-CA, shell, or caller variable is inherited. Ambient `PATH`,
`GIT_EXEC_PATH`, `GIT_SSH`,
`GIT_SSH_COMMAND`, `GIT_DIR`, `GIT_WORK_TREE`, `GIT_COMMON_DIR`,
`GIT_OBJECT_DIRECTORY`, `GIT_ALTERNATE_OBJECT_DIRECTORIES`, `GIT_NAMESPACE`,
`GIT_REPLACE_REF_BASE`, `GIT_GRAFT_FILE`, `GIT_SHALLOW_FILE`, `GIT_INDEX_FILE`,
`GIT_CONFIG_SYSTEM`, `GIT_CONFIG_PARAMETERS`, `GIT_CONFIG_KEY_*`,
`GIT_CONFIG_VALUE_*`, and pathspec controls cannot redirect proof reads.
Repository-local `config`, `config.worktree`, `commondir`,
`objects/info/alternates`, `objects/info/http-alternates`, `refs/replace/*`,
`info/grafts`, or shallow metadata is independently fatal. SSH, local-path,
custom-helper, and other remote proof protocols remain unsupported until a
later route names their complete executable/shell trust base. Any untrusted
runner/manifest input, attestation mismatch, forbidden local metadata, nonzero
status, missing object, wrong object type, or repository/executable/helper
rebound raises `SnapshotProvenanceError` before parsing or reduction.

`resolve_repository_identity()` resolves the no-follow real Git common
directory and records its absolute path plus device/inode.
`describe_event_store()` and `resolve_ref_target()` record repository identity,
exact remote argument, canonical ref, normalized effect target, and the unique
effective push endpoint (or local). A configured remote name resolves all of
its push URLs, normalizes them, and fails closed unless exactly one value is
configured; an explicit URL/path remote argument is itself the one bound
endpoint. Resolution never substitutes a configured fetch URL. Remote snapshot
acquisition fetches the canonical event ref directly from that bound push
endpoint, and publication addresses the same endpoint rather than the symbolic
remote name. A local event ref and target ref share a transaction domain only
when their repository identities match. Remote refs share a domain only when
both descriptors are remote and their single normalized push endpoints match;
mixed local/remote, different-endpoint, or multiple-push-URL bindings fail
closed. Evaluation binds both descriptors. Apply recomputes them from its
`repo` and `store` handles and raises `RefTransactionDomainError` for a rebound
or cross-repository domain before private-key load, quarantine/object import,
or any ref transaction.

- `authorize_principal_operation()` passes the complete token fields above to
  `require_side_effect_executor_token()` for every token-required operation;
  incomplete context refuses. It carries an opaque credential attestation,
  never raw credential bytes.
- Overseer, both chiefs, and CI use the exact signer map and require a token
  before local or remote fact mutation. Merge-gate pure evaluation is a new
  non-mutating path with no signer or token. It parses fresh events from the
  validated immutable snapshot and still performs signature/bus verification.
  `MergeMaterialization`, `threeway.gitcas.compute_merge_in_scratch()`, and
  `threeway.gitcas.materialize_and_cas_verified_merge()` are defined together
  in `threeway/gitcas.py`. The scratch helper runs merge-tree and commit-tree in
  a temporary primary object directory with the input repository object store
  exposed as a read-only alternate, returning exact base/branch/tree/commit/
  message materialization inputs. Evaluation records them and then
  deletes the scratch directory. Evaluation
  leaves repository objects, refs, index, worktree, keys, and event state byte/
  OID-identical. Any target-ref update or
  `merge_completed` emission requires signer `merge-gate` plus a token;
  `target == "refs/heads/main"` additionally requires a successful
  `ProtectedRunnerCredential.attest_target()` result.
  `apply_gate_evaluation()` accepts no free candidate or target arguments and
  treats its public evaluation as untrusted. Before loading the runtime or
  touching a key, object, ref, or authority path it recursively validates exact
  concrete types and primitive shapes and serializes inert canonical primitives
  without invoking supplied equality. Only then does it reload the zero-
  argument protected runtime, resolve the exact attested registry/bus/seat/
  default-policy authority, require its digest to match the validated claimed
  primitive, reacquire canonical event state without mutating the input store,
  and rerun evaluation for the validated candidate/target. The fresh exact-
  string outcome must be literal `MERGEABLE` with non-null SHAs. Both
  authorizations' validated primitives must match that freshly reproduced
  binding; only the fresh binding flows onward. Operations are exactly
  `update-target-ref` and
  `emit-merge-completed`; and their effect targets equal the binding target ref
  and normalized event target. It also requires the target old SHA to match.
  Immediately before materialization it revalidates each token from the stored
  `PrincipalTokenRevalidation`: discovers newer appointments fresh, rechecks
  supersession/current HEAD, recomputes target-satisfied and standardized stop/
  preflight predicates, and returns no cached token on failure.
  `threeway.gitcas.materialize_and_cas_verified_merge()` then recomputes in a
  fresh quarantine object directory with the input objects as read-only
  alternates. It compares the recomputed tree and commit OIDs to the complete
  frozen materialization before opening an input-object writer. Missing inputs
  or any mismatch deletes the quarantine and leaves input object names/OIDs,
  refs, keys, and facts unchanged. After both authorizations pass, apply loads
  the merge-gate key and calls `_prepare_append_at()` to build and sign the exact
  bound `merge_completed` event commit in quarantine as a child of
  `binding.events_tip_oid`. Preparation never retries, fetches, mutates the
  event store, or rebases onto a newer tip.

  For a local transaction domain, the helper exposes the verified merge and
  event quarantines as read-only alternates, opens one `git update-ref --stdin`
  transaction, queues expected-old updates for both refs, and reaches successful
  `prepare` before any durable input-object import. Only then does it import the
  exact combined verified closure and commit the already-prepared transaction;
  import failure aborts it. A stale target or event ref therefore rejects before
  the input object set changes. For a remote transaction domain, it publishes
  the verified merge commit and prepared event commit directly to the bound
  unique push endpoint in one `git push --atomic` two-ref update with exact old-
  OID leases for both refs. Unsupported atomic publication has no sequential or
  non-atomic fallback. A concurrent event append or target change at any point
  after the preliminary checks therefore rejects the final two-ref transaction
  and neither authority ref advances. There is no later retrying
  `store.append()` call. A second apply fails on expected-old mismatch; a
  changed event tip or newly superseding appointment fails as stale evaluation/
  authority.
  Current mutating `run_gate()` cannot serve as the pure evaluator.
- Candidate execution context is invalid before key, credential, ref, or fact
  access. Runner isolation and absence of service keys/credentials remain the
  security boundary; the context field is an additional fail-closed check.

- [ ] **Step 1: Write service-principal regressions**

Cover every principal/operation pair, unknown principals, cross-principal
operation attempts, signer mismatch, every principal/context cross-product,
candidate and unknown-context denial, missing
executor token for protected-main update, and zero fact/ref/main mutation on
denial.

Cover the signer map, token-required set, credential-required target set, local
and remote fact targets, pure evaluation no-mutation, every target-ref update,
`merge_completed`, and doctor registration. Route the pure-evaluation fixture
through current mutating `run_gate()` as a RED proving it is not yet safe.
Reject a candidate/target/repository/event-ref rebound, either authorization
swapped between two evaluations, a non-MERGEABLE evaluation, changed event
tip, second apply, newly superseding appointment, or a changed expected-old SHA
before object writes, CAS, or key load. Exercise two repositories with matching
commit OIDs and two event refs with matching tips; both replay attempts deny.
Patch the production remote `RefEventStore._sync()` to fail and drive the real
`poll_once()` acquisition/evaluation path; it must still capture through the
proof-repository path and never call `_sync()`. The following exact selectors
are mandatory:

- `test_gate_evaluation_owns_acquisition_and_rejects_caller_snapshot`
- `test_validation_rereads_actual_proof_ref_after_acquisition`
- `test_evaluation_accepts_events_acquired_at_actual_tip`
- `test_candidate_scan_event_mutation_cannot_change_reparsed_evaluation`
- `test_proof_validation_rejects_single_replace_ref_at_real_tip`
- `test_proof_git_commands_disable_replace_objects_and_repository_redirects`
- `test_private_proof_repository_inode_substitution_fails_closed`
- `test_proof_runner_is_deployment_resolved_and_rejects_explicit_substitution`
- `test_bound_proof_helper_file_replacement_fails_closed`
- `test_proof_repository_local_config_redirect_fails_closed`
- `test_proof_repository_recheck_exec_race_uses_bound_descriptor`
- `test_gate_uid_writer_cannot_mutate_proof_service_gitdir`
- `test_poll_once_captures_once_for_two_candidates`
- `test_each_candidate_reduction_reparses_fresh_events`
- `test_public_merge_gate_evaluation_is_consistent_and_non_authorizing`
- `test_local_append_between_check_and_prepare_aborts_both_ref_updates`
- `test_local_two_ref_apply_succeeds_without_injected_race`
- `test_remote_append_between_check_and_atomic_push_rejects_both_leases`
- `test_remote_atomic_two_ref_apply_succeeds_without_injected_race`
- `test_cross_repository_event_and_target_authorities_refuse_before_mutation`
- `test_remote_atomic_unsupported_has_no_non_atomic_fallback`

The first selector asserts the public evaluator signature has no snapshot,
proof path/ref, event bytes, tip, tree, or digest input; constructing and
populating the formerly proposed frozen/slot shape with `object.__new__()` and
`object.__setattr__()` cannot reach a Git command, while the store-owned path is
accepted. The second retains a real claimed tip but substitutes a caller-chosen
authentic event subset plus a valid recomputed self-digest; the independent
proof-ref traversal must reject it. The third is the non-vacuous honest control.

The fourth parses candidate-discovery events from the honest immutable bytes,
mutates one temporary `Event.payload` after collecting IDs, and proves a fresh
parse for evaluation yields the unchanged honest verdict; retaining parsed
events in `_AcquiredEventState` or reusing them for reduction must make it RED.
The fifth starts from the honest control and adds exactly one
`refs/replace/<real-tip>` pointing to a same-type commit that omits a real
revocation; validation raises `SnapshotProvenanceError` before reduction and
leaves durable state unchanged. The sixth parameterizes each forbidden ambient
`GIT_*` repository/object/config/pathspec redirect, `HOME`, `TMPDIR`,
`DYLD_*`/`LD_*`, credential, proxy, and alternate TLS/CA variable one fact at a
time and records the actual attested executable, proof argv, and complete child
environment. It also drives real remote acquisition with fake `ssh`,
`git-upload-pack`, and `git-remote-*` helpers first on ambient `PATH`; none may
execute. The honest child starts from an empty environment, uses only the bound
private `TMPDIR`, exact attested helper `PATH`/`--exec-path` and CA file, disables
proxy/redirect/system/global/local config, and allows only HTTPS. The trusted
graph and verdict remain the honest control; inheriting one ambient value,
removing the deployment-attested runtime or one command-line TLS/protocol
constraint, or weakening the redirect scrub makes the selector RED. The
seventh replaces only the captured proof
directory at the same pathname with an attacker bare repository before
traversal and requires identity refusal. Adding a proof-repository alternate,
graft, or shallow marker likewise fails closed.

The next eight selectors close the focused Task-3E/3F review gaps without
reopening the two-ref CAS questions. The caller-runtime selector proves the
public evaluator, `poll_once()`, CLI parser, and shell wrapper expose no
Git/helper/manifest/proof-runtime/registry/bus/gate-seat/policy argument. It
passes each prohibited CLI flag and requires `argparse` rejection, migrates the
activation-script caller instead of preserving compatibility keywords, and
attempts a stable malicious absolute Git while the honest control loads the
canonical deployment attestation. The same selector parameterizes either UID
as zero, equal gate/proof UIDs, mismatched real/effective UID, mode/group
membership, and one Darwin extended-ACL tree-changing grant; every variant
refuses before store, key, candidate, service connection, or repository access.

The bound-file selector first completes runtime loading, pauses at the exact
pre-command barrier, and then replaces one primary Git executable,
`git-remote-http[s]`/exec helper, registry key, authority manifest, runtime
manifest, launchd plist, deployed service/interpreter, or TLS CA file inside an
unchanged directory. Every case refuses before command launch; removing only
the corresponding lifetime recheck makes this selector RED. The local-metadata
selector independently adds only `config` with `core.sshCommand`, only `config`
with `url.<base>.insteadOf`, only `config.worktree`, only `commondir`, and only
`objects/info/http-alternates`; every case must fail before fetch/traversal
while the exact no-metadata Gitdir passes. The descriptor-race selector renames
the service-owned proof repository after the final service-side recheck but
before child exec and proves Git either uses the held original directory or
refuses; it never traverses the replacement.

The gate-writer selector is a privileged macOS deployment integration, not a
mock unit proof. It installs/uses distinct locked gate/proof accounts and the
root-protected LaunchDaemon, deliberately reveals the service Gitdir pathname
at the post-check barrier to a process running as `gate_uid`, and proves its
create, replace, chmod, and delete attempts all fail while the service returns
the unchanged canonical graph. The negative deployment keeps both manifest
UIDs, account resolution, peer checks, and service process identities distinct
and changes only the prepared Gitdir owner/mode/ACL so `gate_uid` can mutate it.
It must prove the service and writer both reach the post-check barrier, the
injected metadata write succeeds, and the selector becomes RED for the intended
graph-integrity reason rather than an earlier loader denial. Ordinary
unprivileged CI cannot create the second UID or
bootstrap the system LaunchDaemon, so this OS boundary is explicitly
`test-infeasible` there. Unit mocks may cover frame and fail-closed logic but
must never satisfy this selector or authorize Task-3 GO. The committed
`scripts/verify_proof_acquirer_macos.py` emits the deployment evidence consumed
by the integration node.

The capture-count selector drives two candidates and asserts one service
session/context entry plus the same acquired-state identity for discovery and
both evaluations. The reparse selector mutates the first reduction's parsed
payload and proves the second receives a distinct fresh event list with the
honest verdict. The public-contract selector requires direct evaluation and
stable non-mutating `poll_once()` to return the same public
binding/outcome/reason shape, then constructs hostile subclasses at the
evaluation, binding, nested scalar, outcome, and authorization levels. It
asserts attacker `__eq__` is never invoked and proves apply's fresh
protected-runtime/authority resolution and reacquisition/reduction rejects each
object before key/object/ref probes. It also tries an alternate registry, bus
ID, gate seat, and permissive `Policy`; those values are absent from both
public signatures, and changing one protected authority field changes or
invalidates `gate_authority_digest`. Removing full re-evaluation, exact
recursive type/shape validation, canonical primitive comparison, fresh-binding
downstream use, or accepting authorizations whose `merge_binding` differs from
the freshly reproduced binding makes only this selector RED. Each selector has
an honest one-fact control and a named mutation that makes only it RED.

Record refs, object names/OIDs, index, worktree, key bytes, and event bytes
before/after a MERGEABLE evaluation and require exact equality. The current
`run_gate()` fixture must change at least one target/object/event state as the
non-vacuity RED.

The two positive apply selectors are load-bearing controls. The local baseline
uses co-located refs with no injected append and proves both refs advance once;
the local race and cross-repository denial each vary exactly one fact from it.
The remote baseline enables atomic support at one unique push endpoint with no
injected append and proves exactly one atomic two-ref publication advances both
refs; the remote race and atomic-unsupported denial each vary exactly one fact
from it. All four denial selectors assert the durable input object-name/OID set
and both refs remain unchanged. Every apply selector asserts
`RefEventStore.append()` and every sequential-publish helper are never called.
Authorize both operations, then commit a superseding appointment before apply;
fresh token revalidation must deny with byte/OID-identical repository, event
store, key probes, and target. On the positive apply path, require deterministic
materialization of the exact bound tree/commit before CAS; missing base/branch
or a flipped expected tree/commit denies with byte/OID-identical input object
names, no CAS, and no fact emission. Simulate target and event-ref races at
transaction preparation/atomic publication and require both refs plus the input
object set to remain unchanged. Reject cross-repository, mixed-local/remote,
different-endpoint, fetch/push-substitution, and zero/multiple-push-endpoint
domains before key load, object import, or ref mutation. Prove an atomic-
capability rejection cannot call any sequential-publish fallback.
For each token-required operation, vary command class, expected HEAD,
appointment, newer appointment, satisfied target, failed preflight, and stop
predicate. A non-main target needs no protected credential; `refs/heads/main`
refuses an absent, wrong-target, or failed opaque credential attestation.

- [ ] **Step 2: Run tests to prove RED**

```bash
env -u GIT_INDEX_FILE .venv/bin/python -m pytest tests/unit/test_service_principals.py tests/unit/test_proof_acquisition.py tests/unit/test_threeway_activation_scripts.py tests/unit/test_codex_ledger_bridge.py -q
```

Expected: missing principal resolver, deployment-attested private proof
runtime/service, descriptor-anchored proof launch, prohibited authority CLI
inputs, and current entry points lacking the typed operation check. The
privileged selector
`tests/integration/test_proof_acquisition_macos.py::test_gate_uid_writer_cannot_mutate_proof_service_gitdir`
is `test-infeasible` in the ordinary checkout because it requires installed
distinct UIDs and a system LaunchDaemon. It is not skipped-and-green; it runs
only in the protected deployment and must be present before Task-3 GO.

- [ ] **Step 3: Implement service-principal authorization**

Bind each entry point to the exact map above. `ci` may sign only a
`ci_result`; chiefs and overseer may emit only their own fact classes;
split `evaluate_gate_read_only()` from current target-ref and completion-fact
mutation. No target ref or fact changes without the exact merge-gate signer and
token, and target `refs/heads/main` also requires the credential attestation.
Capture remote events only inside the private lexical acquisition path; the
public evaluator accepts the trusted store, and `poll_once()` captures exactly
once so its private candidate collector and both/all candidate evaluators
consume the same validated state. Reparse a distinct fresh event list for each
reduction. Never return or accept a snapshot/proof capability; permit only the
public immutable `MergeGateEvaluation(binding, outcome, reason)` comparison
record, and treat it as untrusted on apply. Freshly reacquire/reduce before any
mutation probe, resolve registry/bus/seat/default policy only from the freshly
loaded protected runtime, require its authority digest, and require both
authorizations to retain the exact reproduced `merge_binding`. Validate every
untrusted object recursively to exact concrete types and canonical primitive
shapes, never invoke supplied equality, compare the fresh exact-string outcome
to literal `MERGEABLE`, and use only the fresh binding for mutation. Public
evaluation/apply/poll signatures and the CLI accept none of those authority
choices; remove the existing registry/bus arguments from the Python caller,
parser, shell wrapper, and activation-script test.

Load the proof runtime only from the canonical protected-runner deployment
attestation before store/key/candidate access. Expose no CLI or public API path
for Git, helpers, manifest, transport, proof repository, registry, bus, gate
seat, or policy. Bind and recheck the manifest, deployment root, authority
manifest, each registry key, TLS CA file, Git, each regular deployed HTTPS
exec/transport helper, launchd plist, deployed service/interpreter, and socket
parent by exact file digest/identity/owner/mode, native ACL/mode parent chain,
and distinct nonzero gate/proof UIDs. The root-protected system LaunchDaemon
runs the locked proof account continuously; the service itself binds/listens so
mutual peer-UID checks are meaningful. The service alone prepares the
proof-owned Gitdir without config/config.worktree/commondir or alternate/
http-alternate redirect files and executes every replacement-disabled proof
command through private fork/fchdir/execve with `--git-dir=.`,
`--no-write-fetch-head` for fetch, and the exact attested exec-path, helper set,
CA file, HTTPS protocol policy, argv, and environment built from an empty
mapping with only a bound private TMPDIR. Fail closed on a wrong peer, malformed
frame, caller runner/authority value, post-load bound-file replacement,
gate-UID repository mutation, forbidden local metadata, recheck/exec path race,
ambient redirect, replacement, graft, shallow marker, missing/wrong-type
object, or attestation/repository/executable/helper rebound.

Pass the immutable comparison binding through evaluation and both authorized
mutations without reconstructing it from free arguments; independently
reproduce it at apply before trusting it. Resolve and bind exactly one effective
push endpoint for each remote authority, acquire from and publish directly to
it, and refuse zero/multiple or mismatched endpoints.
Prepare both local ref updates before combined closure import; use one atomic
two-ref publication remotely. All service emitters bind explicit local versus
remote targets. Add the unprivileged unit suite to the model-derived doctor gate
in the same commit. The privileged macOS isolation selector is a separate
deployment gate: a mock, skip, or ordinary local doctor pass cannot satisfy it.

- [ ] **Step 4: Prove GREEN and non-vacuity**

```bash
env -u GIT_INDEX_FILE .venv/bin/python -m pytest tests/unit/test_service_principals.py tests/unit/test_proof_acquisition.py tests/unit/test_threeway_activation_scripts.py tests/unit/test_codex_ledger_bridge.py -q
```

Swap `ci` to `merge-gate` in one allowed-operation fixture and confirm the
assertion fails. Then mark one emitter token-free and route pure evaluation
through current mutating `run_gate()`; both selectors must fail. Independently
flip candidate ID, target ref, event tip, and one authorization binding; each
must RED before restoration. Run the honest store-owned acquisition control,
then remove exactly one of the public-input prohibition, proof-ref reread,
mutable-event reparse, one-capture boundary, replacement-ref rejection,
deployment-attestation load, exact executable/helper-file identity, local-
config seal, descriptor-anchored launch, public-output boundary,
CLI/environment replacement suppression, hostile-type rejection, proof-service
peer/frame check, or ambient redirect scrub and require its named selector to
RED. Run each
local/remote positive apply control first, then inject
only its named race or domain/capability mismatch and require the corresponding
denial selector to RED if the event expected-old update, remote event
lease/refspec, prepare-before-import boundary, or no-fallback guard is removed.
Restore and rerun GREEN.

In the protected macOS deployment, with the separately user-authorized
installation already complete, run:

```bash
env -u GIT_INDEX_FILE PIPELINE_PROOF_INTEGRATION=1 .venv/bin/python -m pytest tests/integration/test_proof_acquisition_macos.py::test_gate_uid_writer_cannot_mutate_proof_service_gitdir -q
```

Expected: the distinct-UID control passes; changing only the deployment so the
gate owns the Gitdir makes the selector RED. Preserve the verifier's committed
`logs/proof-acquisition-isolation-pipeline-local-authority-2026-07-10.json`
evidence path in the Task-3 handoff. Without this run, report the exact
`test-infeasible` deployment precondition and do not request Task-3 GO.

- [ ] **Step 5: Review and commit Task 3D**

```bash
env -u GIT_INDEX_FILE git commit -m "fix(protocol): bind service principals"
```

The implementation commit may exist before protected deployment, but the
Director must not send a verification request claiming complete Task-3 closure
until the privileged isolation selector has run and its evidence is durable.

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
