# Autonomous Seat Outcome Contract Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace coordinator-centered, checklist-driven four-seat routing with a compact outcome contract that lets seats reroute and exchange ownership directly while preserving durable evidence, non-author verification, and explicit external-effect authority.

**Architecture:** Migrate in two sequential deliverables. First, add semantic outcome/ownership primitives, teach route selection and compact-pair verification to accept autonomous seat work, demote capacity machinery to diagnostics, and shrink duplicated prompt surfaces. After that exact protocol commit receives non-author Operator GO, publish one compatible outcome-contract transition event that supersedes the blocked maintenance route; the accepting owner then chooses the chronology implementation and tests.

**Tech Stack:** Python 3.11+ standard library, pytest, Markdown protocol adapters, TOML Codex role prompts, fixed Git-backed mailbox writer.

## Global Constraints

- Source specification: `docs/superpowers/specs/2026-07-18-autonomous-seat-outcome-contract-design.md` at commit `5d0185c`.
- Durable repository and mailbox evidence outranks chat summaries and stale prose.
- An author cannot approve its own behavior-changing work; request and report
  preserve durable seat plus model or actor-context identity, and the reviewer
  identity must differ even when the seats differ. A truthful distinct cold
  context is acceptable only when durably stated; a distinct model is stronger.
- Every ownership event binds task ID, exact current contract or route,
  immutable parent/revision, previous owners, recipient-authored acceptance
  references from every new owner, and all known finding references.
- Any stale/dangling parent, fork, conflicting same-task tip, forged acceptance,
  or unsupported takeover makes only the overlapping task non-actionable.
- External or difficult-to-reverse effects require durable explicit user-
  authority provenance plus an exact canonical effect, one executor, exact
  target, and bounded scope. Structural token completeness is not execution
  authorization.
- Known material `finding_refs` remain immutable through outcome, ownership,
  request, report, reviewer, and owner changes; reports explicitly disposition
  every carried reference.
- Ordinary internal ownership changes require neither coordinator approval nor separate user authorization after cutover.
- The coordinator does not author behavior-changing production work unless the user explicitly assigns that model a director seat.
- Tasks 1–6 are authored by a user-named `director` or `director2`; the current coordinator may route, observe, and reconcile but does not implement them.
- Until Task 6 receives GO, the current R-INDEPENDENCE rule remains binding. Task 0 satisfies its design-time requirement once, without creating a preflight `CLEAR` gate.
- Historical mailbox events and capacity packets remain immutable evidence;
  legacy coordinator Task-board `coordination`, `status`, and `decision` event
  kinds and pre-v3/v3/current report forms remain corpus-readable.
- The current maintenance route remains binding until Task 7 publishes and commits the transition event.
- Task 7 authorizes only a local mailbox transition event and local metadata commit when execution reaches that task; it does not authorize ledger resume, push, merge, lock, cursor consumption, target mutation, paid spend, or any remote effect.
- Use `env -u GIT_INDEX_FILE` for ordinary Git and pytest commands.
- Refresh `git log --oneline -3` and scoped status immediately before every write, stage, commit, or live gate decision.
- Preserve unrelated peer changes and stage only the exact task paths.

## File Structure

- `scripts/protocol_mailbox.py`: loads committed `path@commit` event references
  and derives immutable sender identity from repository evidence.
- `scripts/codex_protocol_model.py`: canonical semantic model for outcomes,
  ownership, work states, durable review identity, finding propagation, and
  exact external-effect authority.
- `scripts/route_lineage.py`: recognizes legacy coordinator Task-board kinds and
  conflict-free autonomous parent/revision lineages per task.
- `scripts/ledger_start_guard.py`: selects an authoritative compatible event for
  a bound target and fails closed when that task's route lineage is ambiguous.
- `scripts/protocol_capacity.py`: retains capacity observability while limiting route blocking to structural and hard-boundary failures.
- `scripts/compact_pair_loop.py`: validates a minimal outcome-bound request/report instead of prescribing author tests and allowed paths.
- `tests/unit/test_protocol_mailbox.py`: committed event-reference and sender
  provenance tests.
- `tests/unit/test_autonomous_seat_contract.py`: focused semantic contract,
  immutable finding, actor-identity, and exact user-authority tests.
- `tests/unit/test_route_lineage.py`: route compatibility and autonomous selection tests.
- `tests/unit/test_protocol_capacity.py`: advisory diagnostics and compact external-effect authorization tests.
- `tests/unit/test_compact_pair_loop.py`: minimal request/report and non-author verification tests.
- `tests/unit/test_protocol_prompt_sync.py`: semantic single-source and thin-adapter assertions.
- `AGENTS.md`, `CLAUDE.md`, both continuation adapters, both seat-skill trees, and selected Codex/Claude role prompts: thin routing and role adapters over the same compact source.
- `ARCHITECTURE.md`: current post-cutover topology and invariants.
- `DECISIONS.md`: append-only rationale for the autonomy cutover.
- `coordination/mailbox/sent/<timestamp>-<seat>-to-all-coordination.md`: Task 7 live transition event, created only through `coordination/bin/send-event`.

---

### Task 0: Bridge the current protocol without recreating the blocker

**Files:**
- Create through fixed writer: one bounded `coordination` request under `coordination/mailbox/sent/`
- Create through fixed writer: one independent `findings` response under `coordination/mailbox/sent/`

**Interfaces:**
- Consumes: approved design spec at `5d0185c`, this plan, and the current R-INDEPENDENCE rule.
- Produces: the durable Task 0 findings ref
  `coordination/mailbox/sent/2026-07-18T06-05-32Z-operator-to-director-findings.md@fedfbe3`
  that the authoring Director carries with the existing Director2 maintenance
  findings ref into Tasks 1–6.

- [ ] **Step 1: Establish the authoring seat**

The user names `director` or `director2` for implementation. If this plan is launched from the coordinator task, the coordinator routes the approved outcome to that seat and remains facilitator. It does not edit the behavior-changing paths in Tasks 1–6.

- [ ] **Step 2: Request one bounded independent design review**

The authoring Director uses `coordination/bin/send-event <director-seat> <operator-seat> coordination "autonomous outcome contract design review"`, commits the generated event, and asks only for abuse cases against these hard boundaries. Bind the approved design and plan commits in the body:

```text
1. self-approval or reviewer-author identity collapse
2. unwanted or ambiguous ownership transfer
3. competing autonomous route events at the same effective chronology
4. loss of legacy route/report readability
5. external-effect execution without explicit executor, target, and scope
6. concealment of a known material finding during transfer or review
```

The request does not ask whether the plan is exhaustive and does not require `CLEAR` before coding.

- [ ] **Step 3: Preserve the independent findings**

The reviewer publishes with `coordination/bin/send-event <operator-seat> <director-seat> findings "autonomous outcome contract design findings"` and commits the generated event. The committed result is
`coordination/mailbox/sent/2026-07-18T06-05-32Z-operator-to-director-findings.md@fedfbe3`.
The author adds every material finding to the Task 6 verification outcome and
converts each feasible abuse case into semantic coverage; when a test is
infeasible, the plan records the exact repository evidence the actual-diff
Operator must inspect. A hard-boundary contradiction must be resolved before
implementation; ordinary edge cases remain acceptance evidence for the actual-
diff review. This is a single current-law bridge, not a recurring preflight
convergence loop or `CLEAR` gate.

- [ ] **Step 4: Confirm no implementation mutation occurred under coordinator authority**

```bash
env -u GIT_INDEX_FILE git status --short --branch
env -u GIT_INDEX_FILE git diff --name-only
```

Expected: only the two fixed-writer mailbox events and their commits were created before the authoring Director begins Task 1.

### Task 1: Add provenance-backed outcome and ownership semantics

**Files:**
- Modify: `scripts/protocol_mailbox.py`
- Modify: `scripts/codex_protocol_model.py`
- Modify: `tests/unit/test_protocol_mailbox.py`
- Create: `tests/unit/test_autonomous_seat_contract.py`

**Interfaces:**
- Consumes: Git-committed fixed-writer events, the existing
  `protocol_mailbox.RECEIVING_SEATS`, and existing `OPERATOR_SEATS`.
- Produces: `protocol_mailbox.CommittedEventRef`,
  `load_committed_event_ref(root, ref)`, `OutcomeContract`, `OwnershipChange`,
  `ReviewDecision`, `UserAuthorityGrant`, `ExternalEffectAuthorization`,
  `claim_outcome()`, `ownership_change_is_effective(contract, change)`,
  `apply_ownership_change()`, `review_accepts_outcome()`,
  `external_effect_token_is_complete()`, and
  `external_effect_is_authorized(token, grant, used_authority_refs=())`.

- [ ] **Step 1: Write committed-event provenance tests**

Extend `tests/unit/test_protocol_mailbox.py` with a temporary Git repository
fixture and tests that prove `load_committed_event_ref()` accepts only
`coordination/mailbox/sent/<event>.md@<40-hex>` when that exact commit contains
that exact path and the filename sender equals the fixed-writer envelope sender.
The same tests reject a missing commit, a path not present at the commit, a
non-mailbox path, a filename/envelope sender mismatch, and a mutable working-tree
file. Use a real `git commit` in the fixture so the sender fact is repository-
derived rather than caller-supplied.

- [ ] **Step 2: Write semantic contract tests**

Create `tests/unit/test_autonomous_seat_contract.py`. Its fixtures must obtain
proposal, acceptance, finding, takeover-evidence, and authority references via
`load_committed_event_ref()`; do not instantiate trusted refs from free-form
body fields. Cover these assertions:

```python
def test_transfer_binds_current_parent_and_recipient_authored_acceptance(): ...
def test_stale_parent_forged_acceptance_and_active_incumbent_self_claim_fail(): ...
def test_split_exchange_waits_for_every_new_owner(): ...
def test_abandoned_takeover_needs_fresh_work_and_lock_event_refs(): ...
def test_ownership_change_cannot_drop_or_reorder_finding_refs(): ...
def test_finding_is_advisory_unless_hard_boundary_is_unresolved(): ...
def test_review_rejects_equal_seat_or_equal_actor_identity(): ...
def test_operator_to_operator2_identity_collapse_is_rejected(): ...
def test_review_requires_exact_range_and_every_finding_disposition(): ...
def test_external_token_completeness_does_not_create_authority(): ...
def test_external_authority_requires_exact_effect_executor_target_and_scope(): ...
def test_external_authority_rejects_substring_replay_and_second_executor(): ...
```

The positive review case uses different seats and durable unequal identities.
The positive external-effect case passes a separate trusted
`UserAuthorityGrant`; the same route token with `grant=None` fails.

- [ ] **Step 3: Run the new selectors and confirm RED**

```bash
env -u GIT_INDEX_FILE .venv/bin/python -m pytest \
  tests/unit/test_protocol_mailbox.py \
  tests/unit/test_autonomous_seat_contract.py -q
```

Expected: collection or focused assertions fail because the provenance loader
and amended semantic types do not exist.

- [ ] **Step 4: Implement immutable event-reference loading**

Add to `scripts/protocol_mailbox.py`:

```python
@dataclass(frozen=True)
class CommittedEventRef:
    ref: str
    path: str
    commit: str
    sender: str


def load_committed_event_ref(root: Path, value: str) -> CommittedEventRef:
    """Load sender identity from an exact committed fixed-writer event.

    Split on the final ``@``, require a full lowercase commit, normalize the
    relative mailbox path, prove ``commit:path`` exists with ``git cat-file``,
    and require filename sender == ``**From:**`` envelope sender. Never fall
    back to the working tree and never accept a sender supplied by the caller.
    """
```

Use the module's existing roster constants. Add explicit standard-library
imports for `dataclass`, `Path`, `re`, and `subprocess` as needed.

- [ ] **Step 5: Implement the semantic dataclasses and guards**

In `scripts/codex_protocol_model.py`, add `dataclass` and `replace` imports and
**retain the existing explicit `protocol_mailbox` import**. The plan previously
used `protocol_mailbox` implicitly; the implementation must keep this visible
import block before the new definitions:

```python
try:
    from scripts import protocol_mailbox
except ImportError:  # direct script execution
    import protocol_mailbox
```

Add these fields and signatures after the seat tuples:

```python
@dataclass(frozen=True)
class OutcomeContract:
    task_id: str
    contract_ref: str
    parent_ref: str | None
    revision: int
    outcome: str
    owners: tuple[str, ...]
    evidence_bar: tuple[str, ...]
    hard_boundaries: tuple[str, ...]
    finding_refs: tuple[str, ...]
    external_effect: str | None = None


@dataclass(frozen=True)
class OwnershipChange:
    task_id: str
    parent_contract_ref: str
    revision: int
    previous_owners: tuple[str, ...]
    new_owners: tuple[str, ...]
    proposal_ref: protocol_mailbox.CommittedEventRef
    acceptance_refs: tuple[protocol_mailbox.CommittedEventRef, ...]
    finding_refs: tuple[str, ...]
    outcome: str | None = None
    abandoned_takeover: bool = False
    fresh_work_ref: protocol_mailbox.CommittedEventRef | None = None
    lock_state_ref: protocol_mailbox.CommittedEventRef | None = None


@dataclass(frozen=True)
class ReviewDecision:
    task_id: str
    author_seat: str
    author_identity: str
    reviewer_seat: str
    reviewer_identity: str
    reviewer_identity_kind: str
    reviewed_base: str
    reviewed_head: str
    verdict: str
    finding_refs: tuple[str, ...]
    finding_dispositions: tuple[tuple[str, str], ...]


@dataclass(frozen=True)
class ExternalEffectAuthorization:
    effect: str
    executor: str
    target: str
    scope: tuple[str, ...]
    user_authority_ref: str


@dataclass(frozen=True)
class UserAuthorityGrant:
    provenance_ref: str
    effect: str
    executor: str
    target: str
    scope: tuple[str, ...]
```

`claim_outcome()` requires `contract_ref`, `revision`, and canonical unique
`finding_refs`. `ownership_change_is_effective(contract, change)` requires the
same task, exact current `contract_ref`, `revision == contract.revision + 1`,
exact previous owners, unchanged complete finding refs, a proposal authored by
an incumbent, and acceptance-ref senders exactly equal to every new owner. For
an abandoned takeover only, the proposal may be authored by a new owner, but
both fresh-work and lock-state committed refs are mandatory. Caller booleans are
not accepted by the API.

`review_accepts_outcome()` requires an Operator reviewer, unequal seats,
nonblank unequal case-folded actor identities, `reviewer_identity_kind` in
`{"model", "cold-context"}`, an exact 40-hex base/head pair, GO, unique
canonical finding refs, and exactly one nonblank disposition for every ref.
An ordinary finding does not itself imply `BLOCKED`; an unresolved hard-
boundary finding does.

`external_effect_token_is_complete()` validates only shape. The execution gate
accepts a separately supplied `UserAuthorityGrant`, rejects `None`, wildcard or
blank targets, unknown/multiple executors, any non-exact canonical tuple,
authority refs already present in `used_authority_refs`, and any second
executor. It compares canonical effect and target values for equality, never
substring containment. No route parser may construct `UserAuthorityGrant` from
seat-authored token text.

- [ ] **Step 6: Run focused tests and confirm GREEN**

```bash
env -u GIT_INDEX_FILE .venv/bin/python -m pytest \
  tests/unit/test_protocol_mailbox.py \
  tests/unit/test_autonomous_seat_contract.py -q
```

Expected: all committed-event, ownership, review-identity, finding-propagation,
and exact-authority cases pass.

- [ ] **Step 7: Commit Task 1**

```bash
env -u GIT_INDEX_FILE git add -- \
  scripts/protocol_mailbox.py \
  scripts/codex_protocol_model.py \
  tests/unit/test_protocol_mailbox.py \
  tests/unit/test_autonomous_seat_contract.py
env -u GIT_INDEX_FILE git diff --cached --check
env -u GIT_INDEX_FILE git commit -m "feat(protocol): model provenance-backed outcomes"
```

### Task 2: Resolve autonomous routes by immutable per-task lineage

**Files:**
- Modify: `scripts/route_lineage.py`
- Modify: `scripts/ledger_start_guard.py`
- Modify: `tests/unit/test_route_lineage.py`
- Modify: `tests/unit/test_target_binding.py`

**Interfaces:**
- Consumes: committed-event refs from Task 1; legacy coordinator Task-board
  `coordination`, `status`, and `decision` events; autonomous `Outcome contract:`
  events with task, parent, revision, previous-owner, owner, acceptance, and
  finding bindings.
- Produces: `route_lineage.is_route_event(path, body) -> bool`,
  `load_route_paths(root) -> list[Path]`,
  `resolve_task_routes(routes, task_id) -> Resolution`, and a guard that returns
  no actionable route when the selected task has any lineage conflict.

- [ ] **Step 1: Add autonomous lineage and legacy-corpus tests**

Extend `tests/unit/test_route_lineage.py` with committed Git fixtures and these
cases:

```python
def test_recipient_authored_route_accepts_exact_incumbent_proposal(): ...
def test_incumbent_proposal_alone_does_not_transfer(): ...
def test_stale_or_dangling_parent_has_no_authoritative_route(): ...
def test_same_revision_tips_fail_closed_in_both_input_orders(): ...
def test_different_seat_same_timestamp_fails_closed(): ...
def test_unsuperseded_tips_at_different_revisions_fail_closed(): ...
def test_forged_acceptance_and_active_incumbent_self_claim_fail(): ...
def test_split_exchange_requires_each_recipient_authored_ref(): ...
def test_unrelated_task_continues_when_another_task_forks(): ...
def test_unmarked_seat_coordination_is_not_a_route(): ...
def test_legacy_task_board_coordination_status_and_decision_are_readable(): ...
```

The legacy test reads these committed corpus paths without rewriting them:

```text
coordination/mailbox/sent/2026-07-07T09-36-23Z-coordinator-to-all-coordination.md
coordination/mailbox/sent/2026-07-07T16-52-18Z-coordinator-to-all-status.md
coordination/mailbox/sent/2026-07-07T17-12-12Z-coordinator-to-all-decision.md
```

Record each legacy kind's disposition: readable and eligible for legacy route
interpretation when it carries `Task-board:`; new autonomous publication uses
`coordination` only.

- [ ] **Step 2: Add the real-consumer fail-closed tests**

Extend `tests/unit/test_target_binding.py` so `find_latest_ledger_route()` and
`build_guard()` reject a fork, stale parent, dangling parent, same-revision tips,
and conflicting live tips for the selected ledger task. Assert the error names
the task and lineage issue and does not return a deterministic filename winner.
Add a second unrelated task and prove its guard still resolves.

- [ ] **Step 3: Run the new selectors and confirm RED**

```bash
env -u GIT_INDEX_FILE .venv/bin/python -m pytest \
  tests/unit/test_route_lineage.py \
  tests/unit/test_target_binding.py \
  -k "outcome or parent or fork or tip or acceptance or legacy_kind" -q
```

Expected: the current resolver still returns a lexicographic winner with fork
issues and direct-seat events lack the required parent/acceptance parser.

- [ ] **Step 4: Implement compatible discovery and immutable route fields**

In `scripts/route_lineage.py`, extend `LineageRoute` with `task_id`,
`route_ref`, `parent_ref`, `revision`, `previous_owners`, `owners`,
`acceptance_refs`, and `finding_refs`. Autonomous bodies require exactly one of
each scalar field and canonical unique lists:

```text
Task ID: <stable task id>
Outcome contract:
Parent contract: <path@commit>
Contract revision: <positive integer>
Previous owners: <comma-separated seats or none>
Owners: <comma-separated seats>
Proposal ref: <path@commit or self>
Acceptance refs: <comma-separated path@commit refs; the committed route itself may satisfy its sender>
Finding refs: <comma-separated path@commit refs or none>
```

`is_route_event()` recognizes two disjoint forms:

1. existing coordinator/coordinator2 `*-to-all-(coordination|status|decision).md`
   events carrying `Task-board:`; and
2. direct-seat `*-to-all-coordination.md` events carrying the complete
   autonomous form.

Iterate all regular mailbox files rather than globbing only coordination
filenames. Load every referenced acceptance through
`protocol_mailbox.load_committed_event_ref()`. The route's own committed ref is
derived from Git and may count only for its actual fixed-writer sender. Build an
`OwnershipChange` and call Task 1's semantic guard; never trust an `accepted_by`
string or a declared sender.

- [ ] **Step 5: Make resolution per-task and fail closed**

Implement `resolve_task_routes(routes, task_id)` so a valid next autonomous
revision must point to the unique current tip. Return
`Resolution(authoritative=None, issues=...)` for a fork, stale/dangling parent,
same-revision tips, conflicting unsuperseded tips at different revisions, or
any ineffective ownership change. Do not sort conflicting tips into a winner.
Legacy-only history retains its existing compatible selection until a valid
autonomous child names the exact legacy parent. Resolution issues for another
task do not affect the requested task.

In `scripts/ledger_start_guard.py`, discover candidates through
`load_route_paths()`, filter by the bound target/task, call
`resolve_task_routes()`, and fail closed if `authoritative is None` or issues are
present. Update user-facing text from “coordinator route” to “outcome-contract
route” without changing the ledger guard's existing target binding.

- [ ] **Step 6: Run route, corpus, and guard tests**

```bash
env -u GIT_INDEX_FILE .venv/bin/python -m pytest \
  tests/unit/test_route_lineage.py \
  tests/unit/test_target_binding.py -q
```

Expected: autonomous lineage cases, all three committed legacy kinds, and the
real ledger consumer pass; no conflict case returns a winner.

- [ ] **Step 7: Commit Task 2**

```bash
env -u GIT_INDEX_FILE git add -- \
  scripts/route_lineage.py \
  scripts/ledger_start_guard.py \
  tests/unit/test_route_lineage.py \
  tests/unit/test_target_binding.py
env -u GIT_INDEX_FILE git diff --cached --check
env -u GIT_INDEX_FILE git commit -m "feat(protocol): resolve seat routes by immutable lineage"
```

### Task 3: Demote capacity rules and separate effect token shape from authority

**Files:**
- Modify: `scripts/protocol_capacity.py`
- Modify: `tests/unit/test_protocol_capacity.py`

**Interfaces:**
- Consumes: `route_lineage.is_route_event()`, Task 1's exact authority model,
  compact tokens, legacy ten-field tokens, and a separately trusted
  `UserAuthorityGrant` supplied by the execution caller.
- Produces: structural token diagnostics,
  `validate_external_effect_execution(token, grant, used_authority_refs)`,
  advisory capacity findings, and hard-boundary-only route validity. Route
  parsing never creates a user grant.

- [ ] **Step 1: Write focused route and execution-authority tests**

Extend `tests/unit/test_protocol_capacity.py` with valid committed autonomous
route fixtures from Task 2 and these cases:

```python
def test_autonomous_route_needs_no_packets_join_or_capacity_split(): ...
def test_internal_ownership_event_is_not_an_external_effect(): ...
def test_complete_compact_token_is_only_structural_without_user_grant(): ...
def test_legacy_token_is_readable_but_still_needs_separate_user_grant(): ...
def test_execution_rejects_absent_user_authority(): ...
def test_execution_rejects_unknown_or_multiple_executor(): ...
def test_execution_rejects_blank_wildcard_or_substring_target(): ...
def test_origin_main_does_not_match_evil_origin_main_backup(): ...
def test_execution_rejects_blank_or_broadened_scope_and_effect_mismatch(): ...
def test_execution_rejects_cross_target_replay_and_used_authority_ref(): ...
def test_execution_rejects_second_executor(): ...
def test_exact_compact_and_legacy_tuples_pass_with_matching_user_grant(): ...
```

The positive cases pass `UserAuthorityGrant` as a separate function argument.
No route body or token fixture is allowed to manufacture that object.

- [ ] **Step 2: Run the new tests and confirm RED**

```bash
env -u GIT_INDEX_FILE .venv/bin/python -m pytest \
  tests/unit/test_protocol_capacity.py \
  -k "autonomous_outcome or internal_outcome or external or authority or target" -q
```

Expected: failures from coordinator-only validation, capacity coupling,
substring target coverage, and the absence of a separate execution-authority
gate.

- [ ] **Step 3: Make capacity findings advisory for route validity**

Import `route_lineage` in `scripts/protocol_capacity.py`. Replace `RouteValidation` properties with:

```python
    @property
    def blocking_issues(self) -> list[dict[str, Any]]:
        return list(self.route_issues)

    @property
    def advisories(self) -> list[dict[str, Any]]:
        return list(self.report.blocking_issues)

    @property
    def valid(self) -> bool:
        return not self.blocking_issues
```

Add `"advisories": self.advisories` to `RouteValidation.to_dict()`.

Replace `_validate_route_file()` with the hard-boundary-only implementation:

```python
def _validate_route_file(path: Path, report: CapacityReport) -> list[dict[str, Any]]:
    del report
    try:
        body = path.read_text(encoding="utf-8")
    except OSError as exc:
        return [_issue("G7", f"{path.name}: unreadable route ({exc})")]

    issues: list[dict[str, Any]] = []
    route_posix = path.as_posix()
    if not (
        route_posix.startswith("coordination/mailbox/sent/")
        or "/coordination/mailbox/sent/" in route_posix
    ):
        issues.append(
            _issue("G7", f"{path.name}: route path must be under coordination/mailbox/sent/")
        )
    if not route_lineage.is_route_event(path, body):
        issues.append(_issue("G7", f"{path.name}: not a recognized outcome-contract route"))

    forbidden = _forbidden_side_effects(body)
    subagent_forbidden = [label for label in forbidden if label.startswith("subagent ")]
    if subagent_forbidden:
        issues.append(
            _issue(
                "G7",
                "forbidden side effect authorization: " + ", ".join(subagent_forbidden),
            )
        )
    issues.extend(_side_effect_executor_issues(body))
    issues.extend(_side_effect_success_claim_issues(body))
    return issues
```

Delete `_capacity_split_route_issues()` and its direct tests. Preserve capacity-board packet reporting tests; only route gating is demoted.

- [ ] **Step 4: Parse compact and legacy tokens without minting authority**

Replace the token constants with:

```python
REQUIRED_SIDE_EFFECT_TOKEN_FIELDS = (
    "effect",
    "executor",
    "target",
    "authorized_scope",
    "user_authority_ref",
)
LEGACY_SIDE_EFFECT_TOKEN_FIELDS = (
    "side_effect_id",
    "executor",
    "target",
    "allowed_command_class",
    "preflight",
    "stop_if_newer_mail_or_live_target_satisfied",
    "postcheck",
    "observer_seats",
    "final_closeout_owner",
    "non_goals",
)
```

Add aliases for `effect`, `authorized_scope`, `authorized scope`, `scope`, and
`user_authority_ref`. Remove `route mutation` from
`SHARED_SIDE_EFFECT_PATTERNS`; internal mailbox ownership events are not
external effects. Legacy tokens remain structurally readable even though they
do not contain user provenance; the caller must supply the separate grant.

Add:

```python
def _token_is_structurally_complete(token: dict[str, str]) -> bool:
    compact = all(token.get(field) for field in REQUIRED_SIDE_EFFECT_TOKEN_FIELDS)
    legacy = all(token.get(field) for field in LEGACY_SIDE_EFFECT_TOKEN_FIELDS)
    return compact or legacy
```

Use `_token_is_structurally_complete()` only for structural diagnostics. Replace
`_token_covers_side_effect()` substring construction with canonical field
extraction:

```python
def _canonical_effect(token: dict[str, str]) -> str:
    return " ".join(
        (token.get("effect") or token.get("allowed_command_class", "")).split()
    ).casefold()


def _token_exact_tuple(token: dict[str, str]) -> tuple[str, str, str, tuple[str, ...]]:
    return (
        _canonical_effect(token),
        token.get("executor", "").strip(),
        token.get("target", "").strip(),
        tuple(item.strip() for item in _scope_items(token) if item.strip()),
    )
```

Keep the exactly-one-executor structural check. Target and effect comparisons
use equality; no concatenated token text or `in` test remains.

- [ ] **Step 5: Implement the execution gate**

Add:

```python
def validate_external_effect_execution(
    token: dict[str, str],
    grant: model.UserAuthorityGrant | None,
    used_authority_refs: tuple[str, ...] = (),
) -> list[dict[str, Any]]:
    """Validate exact authority supplied by the trusted execution caller."""
```

Delegate the semantic decision to Task 1's
`external_effect_is_authorized()`. Reject missing provenance, blank/wildcard
target, noncanonical or multiple executors, effect/target/scope inequality,
cross-target replay, a provenance ref already used, and a second executor. This
function may receive a grant from a user-prompt/signed-bus adapter; it must never
parse one from the route. `validate_route()` reports token structure only and
must not describe a complete token as execution-authorized.

- [ ] **Step 6: Run the capacity and exact-authority tests**

```bash
env -u GIT_INDEX_FILE .venv/bin/python -m pytest tests/unit/test_protocol_capacity.py -q
```

Expected: all pass after rewriting coordinator-only/capacity-split assertions;
both compact and legacy tokens require the same separate exact user grant.

- [ ] **Step 7: Commit Task 3**

```bash
env -u GIT_INDEX_FILE git add -- scripts/protocol_capacity.py tests/unit/test_protocol_capacity.py
env -u GIT_INDEX_FILE git diff --cached --check
env -u GIT_INDEX_FILE git commit -m "refactor(protocol): make capacity routing advisory"
```

### Task 4: Bind compact-pair review to durable identity and findings

**Files:**
- Modify: `scripts/compact_pair_loop.py`
- Modify: `tests/unit/test_compact_pair_loop.py`
- Modify: `tests/unit/test_coordination_tooling.py`
- Modify: `tests/unit/test_check_go_schema.py`
- Modify: `.agents/skills/seat-operator/verification-report-format.md`
- Modify: `.claude/skills/seat-operator/verification-report-format.md`

**Interfaces:**
- Consumes: existing committed request/report envelopes, historical verbose
  identity fields, immutable `finding_refs`, and frozen report manifests.
- Produces: request authority `(range, outcome, author seat, author identity,
  assigned Operator, finding_refs)` and report authority `(request, range,
  reviewer seat, unequal reviewer identity, verdict, evidence, finding
  dispositions)`.

- [ ] **Step 1: Rewrite fixtures and add independence/finding tests**

The minimal request fixture contains:

```markdown
Event type: verify-request
Reviewed head: <40-hex>
Reviewed base: <40-hex>
Author seat: director
Author identity: codex-director-context-a
Author identity kind: cold-context
Assigned operator: operator

## Outcome

The committed change satisfies the routed maintenance outcome.

## Finding Refs

- coordination/mailbox/sent/2026-07-18T06-05-32Z-operator-to-director-findings.md@fedfbe3
```

Remove prescribed path/command assertions but retain exact range, request-
commit, envelope, and non-author assertions. Add tests for: same seat; different
seats with equal identity including `operator -> operator2`; missing or blank
identity; accepted unequal `model` and truthful `cold-context` identities;
dropped, duplicate, and reordered finding refs; missing disposition; GO without
evidence; and truthful NITS/FAIL with preserved refs. Extend
`test_check_go_schema.py` across frozen pre-v3, historical v3, current verbose,
and new compact reports.

- [ ] **Step 2: Run compact-pair tests and confirm RED**

```bash
env -u GIT_INDEX_FILE .venv/bin/python -m pytest \
  tests/unit/test_compact_pair_loop.py \
  tests/unit/test_coordination_tooling.py \
  tests/unit/test_check_go_schema.py -q
```

Expected: failures because paths/commands are still mandatory and the reduced
shape does not yet preserve actor identity or finding refs.

- [ ] **Step 3: Implement the compatible parser**

Allow any pair seat as request author while keeping only Operator seats as
reviewers. Replace request/report dataclasses with:

```python
@dataclass(frozen=True)
class VerifyRequest:
    path: str
    trigger_commit: str
    reviewed_head: str
    reviewed_base: str
    author_seat: str
    author_identity: str
    author_identity_kind: str
    assigned_operator: str
    outcome: str
    finding_refs: tuple[str, ...]


@dataclass(frozen=True)
class VerificationReport:
    path: str
    verdict: str
    request_path: str
    request_commit: str
    reviewed_head: str
    reviewed_base: str
    reviewer_seat: str
    reviewer_identity: str
    reviewer_identity_kind: str
    evidence: tuple[str, ...]
    finding_refs: tuple[str, ...]
    finding_dispositions: tuple[tuple[str, str], ...]
    filename_reviewer: str
    envelope_sender: str
```

Keep exact Git, envelope, assignment, and ancestry checks. Parse `Author
identity`/`Reviewer identity` plus kind `model | cold-context`; map legacy
`Author model`/`Reviewer model` to kind `model`. Require nonblank identities and
reject case-folded equality even across different seats. Parse canonical unique
`path@commit` lines under `## Finding Refs`. Reports require exactly the same
refs and one nonblank disposition per ref under `## Finding Dispositions`.

Delete only allowed-path equality and requested-command enforcement. Retain the
Git range-existence check, seat inequality, actor-identity inequality, request
binding, assigned reviewer, exact base/head, and GO evidence requirement.

- [ ] **Step 4: Update both byte-identical report mirrors**

```markdown
Event type: verification-report
VERDICT: GO | NITS | FAIL
Verification request: coordination/mailbox/sent/<request>.md@<request-commit>
Reviewed head: <40-hex>
Reviewed base: <40-hex>
Reviewer seat: operator | operator2
Reviewer identity: <durable model or truthful cold-context identity>
Reviewer identity kind: model | cold-context

## Finding Refs

- <immutable-path@commit>

## Finding Dispositions

- <immutable-path@commit>: addressed | counter-evidence | ordinary-risk | unresolved-hard-boundary

## Evidence

$ <reviewer-chosen command or inspection>
→ <observed result>
```

GO requires evidence, unequal durable identity, and no unresolved hard-boundary
disposition. NITS/FAIL may state unavailable evidence but must still preserve
and disposition every ref.

- [ ] **Step 5: Run compact-pair and corpus compatibility tests**

```bash
env -u GIT_INDEX_FILE .venv/bin/python -m pytest \
  tests/unit/test_compact_pair_loop.py \
  tests/unit/test_coordination_tooling.py \
  tests/unit/test_check_go_schema.py -q
```

Expected: all new independence/finding cases and all frozen pre-v3,
historical-v3, and current verbose compatibility cases pass.

- [ ] **Step 6: Commit Task 4**

```bash
env -u GIT_INDEX_FILE git add -- \
  scripts/compact_pair_loop.py \
  tests/unit/test_compact_pair_loop.py \
  tests/unit/test_coordination_tooling.py \
  tests/unit/test_check_go_schema.py \
  .agents/skills/seat-operator/verification-report-format.md \
  .claude/skills/seat-operator/verification-report-format.md
env -u GIT_INDEX_FILE git diff --cached --check
env -u GIT_INDEX_FILE git commit -m "refactor(protocol): bind reviews to identity and findings"
```

### Task 5: Consolidate the protocol model and thin every active seat adapter

**Files:**
- Modify: `scripts/codex_protocol_model.py`
- Modify: `tests/unit/test_protocol_prompt_sync.py`
- Modify: `tests/unit/test_protocol_doc_integrity.py`
- Modify: `AGENTS.md`
- Modify: `CLAUDE.md`
- Modify: `docs/protocol/codex/continuation.md`
- Modify: `docs/protocol/claude/continuation.md`
- Modify: `docs/protocol/claude/independence-first.md`
- Modify: `docs/protocol/agents/orchestration.md`
- Modify: `.agents/skills/four-seat-protocol/SKILL.md`
- Modify: `.agents/skills/seat-director/SKILL.md`
- Modify: `.agents/skills/seat-operator/SKILL.md`
- Modify: `.agents/skills/seat-coordinator/SKILL.md`
- Modify: `.codex/agents/readiness-bridge.toml`
- Modify: `.codex/agents/protocol-director.toml`
- Modify: `.codex/agents/protocol-operator.toml`
- Modify: `.codex/agents/protocol-coordinator.toml`
- Modify: `.codex/agents/agent01.toml`
- Modify: `.codex/agents/lane-v-verifier.toml`
- Modify: `.claude/skills/four-seat-protocol/SKILL.md`
- Modify: `.claude/skills/seat-director/SKILL.md`
- Modify: `.claude/skills/seat-operator/SKILL.md`
- Modify: `.claude/skills/seat-coordinator/SKILL.md`
- Modify: `.claude/agents/readiness-bridge.md`
- Modify: `.claude/agents/lane-v-verifier.md`

**Interfaces:**
- Consumes: Tasks 1–4 semantic model and mechanics.
- Produces: `render_autonomous_seat_contract() -> str` as the sole active behavior capsule; adapters contain one pointer plus role-local consequences.

- [ ] **Step 1: Replace wording-sync tests with semantic single-source tests**

In `tests/unit/test_protocol_prompt_sync.py`, delete tests that require full copies of Capacity Split Default, mandatory subagent utilization, ten-field tokens, two-cycle escalation, blocked-wave coordinator convergence, and exact generic authority paragraphs in every surface. Add:

```python
AUTONOMOUS_REFERENCE = (
    "Autonomous Seat Outcome Contract: scripts/codex_protocol_model.py"
)
AUTONOMOUS_SURFACES = (
    "AGENTS.md",
    "CLAUDE.md",
    "docs/protocol/codex/continuation.md",
    "docs/protocol/claude/continuation.md",
    "docs/protocol/claude/independence-first.md",
    "docs/protocol/agents/orchestration.md",
    ".agents/skills/four-seat-protocol/SKILL.md",
    ".agents/skills/seat-director/SKILL.md",
    ".agents/skills/seat-operator/SKILL.md",
    ".agents/skills/seat-coordinator/SKILL.md",
    ".codex/agents/readiness-bridge.toml",
    ".codex/agents/protocol-director.toml",
    ".codex/agents/protocol-operator.toml",
    ".codex/agents/protocol-coordinator.toml",
    ".codex/agents/agent01.toml",
    ".codex/agents/lane-v-verifier.toml",
    ".claude/skills/four-seat-protocol/SKILL.md",
    ".claude/skills/seat-director/SKILL.md",
    ".claude/skills/seat-operator/SKILL.md",
    ".claude/skills/seat-coordinator/SKILL.md",
    ".claude/agents/readiness-bridge.md",
    ".claude/agents/lane-v-verifier.md",
)


def test_autonomous_contract_is_model_backed_and_adapters_are_thin() -> None:
    rendered = model.render_autonomous_seat_contract()
    for phrase in (
        "own the outcome",
        "choose the method",
        "ownership change",
        "without coordinator approval",
        "FINDING is not BLOCKED",
        "non-author Operator GO",
        "distinct actor identity",
        "immutable parent and revision",
        "finding refs",
        "external effect",
    ):
        assert phrase.casefold() in rendered.casefold()

    forbidden_copies = (
        "Capacity Split Default:",
        "Subagent utilization decision",
        "2-cycle escalation limit",
        "coordinator owns convergence",
        "stop_if_newer_mail_or_live_target_satisfied",
    )
    for path in AUTONOMOUS_SURFACES:
        text = _read(path)
        assert _compact(text.replace("`", "")).count(AUTONOMOUS_REFERENCE) == 1
        for phrase in forbidden_copies:
            assert phrase not in text, (path, phrase)


def test_active_seat_adapter_line_budgets_prevent_protocol_regrowth() -> None:
    budgets = {
        "AGENTS.md": 210,
        "CLAUDE.md": 220,
        "docs/protocol/codex/continuation.md": 220,
        "docs/protocol/claude/continuation.md": 220,
        ".agents/skills/four-seat-protocol/SKILL.md": 100,
        ".agents/skills/seat-director/SKILL.md": 130,
        ".agents/skills/seat-operator/SKILL.md": 130,
        ".agents/skills/seat-coordinator/SKILL.md": 130,
        ".claude/skills/four-seat-protocol/SKILL.md": 100,
        ".claude/skills/seat-director/SKILL.md": 130,
        ".claude/skills/seat-operator/SKILL.md": 130,
        ".claude/skills/seat-coordinator/SKILL.md": 130,
    }
    for path, maximum in budgets.items():
        assert len(_read(path).splitlines()) <= maximum, path
```

Update `tests/unit/test_protocol_doc_integrity.py` to assert that advisory preflight and direct ownership transfer are present, while keeping the fixed-mailbox, non-author, and no-self-approval checks.

- [ ] **Step 2: Run the new surface tests and confirm RED**

```bash
env -u GIT_INDEX_FILE .venv/bin/python -m pytest tests/unit/test_protocol_prompt_sync.py tests/unit/test_protocol_doc_integrity.py -q
```

Expected: failures on duplicated capsules and missing autonomous renderer/reference.

- [ ] **Step 3: Replace the active behavior capsule in the model**

In `scripts/codex_protocol_model.py`, replace the existing compact-pair prose, coordinator convergence, capacity-split, mandatory subagent, disagreement-cycle, blocked-wave, and ten-field side-effect renderers with:

```python
AUTONOMOUS_SEAT_REFERENCE = (
    "Autonomous Seat Outcome Contract: scripts/codex_protocol_model.py"
)
AUTONOMOUS_SEAT_RULES = (
    "Own the outcome, choose the method, and show credible evidence.",
    "Any seat may claim, split, merge, transfer, exchange, or reroute work without coordinator approval; every new owner accepts through its own durable event bound to the exact task, parent contract, revision, and previous owners.",
    "A route fork, stale or dangling parent, or conflicting same-task tip makes only that task non-actionable; unrelated tasks continue.",
    "WORKING means meaningful progress remains; NEEDS_PEER requests help; FINDING is not BLOCKED; BLOCKED means no lawful path exists without new authority, unavailable external state, or hard-boundary resolution.",
    "Preflight is advisory and preserves material findings; it does not require CLEAR before implementation.",
    "Behavior-changing work is accepted only by non-author Operator GO with a distinct durable actor identity on the actual reviewed commit or range.",
    "External effects require durable explicit user authority and an exact canonical effect, one executor, exact target, and bounded scope; token completeness is not execution authority.",
    "Known material finding refs remain immutable through ownership and reviewer changes and receive explicit report dispositions.",
    "Coordinator observes and facilitates but is not the mandatory route author or convergence gate and does not author behavior-changing production work.",
)


def render_autonomous_seat_contract() -> str:
    return AUTONOMOUS_SEAT_REFERENCE + "\n" + "\n".join(
        f"- {rule}" for rule in AUTONOMOUS_SEAT_RULES
    )
```

Revise `COMPACT_PAIR_INVARIANT` to require the committed reviewed base/head,
outcome, author seat and durable actor identity, assigned non-author Operator,
immutable finding refs, and one bound report with unequal reviewer identity and
explicit dispositions. Revise R-INDEPENDENCE in the model, `CLAUDE.md`, and
`docs/protocol/claude/independence-first.md`: an adversarial-surface owner
explicitly assesses plausible abuse classes and preserves material independent
findings, while the owner and actual-diff Operator choose proportional review
depth. Early independent review is encouraged when it adds signal; it is not a
universal pre-implementation `CLEAR` gate. Distinct-identity non-author actual-
diff GO remains mandatory.

Keep runtime identity, ledger bridge, mailbox, signed-bus, environment, and optional consultation renderers that still have production consumers. Delete renderer calls and constants used only by the retired copied capsules. Add `render_autonomous_seat_contract()` once to `render_surface_summary()` and `main()`.

- [ ] **Step 4: Thin the router, continuation adapter, seat skills, and role prompts**

For every listed Codex and Claude surface, retain only:

1. its role or mode purpose;
2. one exact `AUTONOMOUS_SEAT_REFERENCE` pointer;
3. role-local authority consequences;
4. necessary startup or mailbox commands; and
5. the optional ChatGPT Pro pointer where already required.

Use this shared paragraph once per surface:

```text
Autonomous Seat Outcome Contract: scripts/codex_protocol_model.py
Own the routed outcome and choose the method. Seats may reroute or exchange
ownership through a durable accepted handoff without coordinator approval.
Preserve material findings, require non-author Operator GO for behavior-changing
work with distinct durable actor identity, bind autonomous ownership to an
immutable parent/revision, preserve immutable finding refs, and keep external
effects separately user-authorized for the exact effect/executor/target/scope.
```

Role-local consequences:

```text
Director/director2: may implement, split, transfer, or exchange accepted work;
submits the actual commit/range and outcome for independent review.

Operator/operator2: may implement accepted work but cannot verify anything it
authored; when acting as reviewer, chooses sufficient evidence and issues
GO/NITS/FAIL against the actual outcome.

Coordinator: observes, facilitates, and may mediate or claim eligible
non-production work; it is not a route-approval gate and does not author
behavior-changing production work.

Readiness bridge: reads durable state and reports the active outcome and owner;
it does not claim work without an explicit seat assignment.
```

Remove mandatory Capacity Split Default sections, exact R-BRIEF checklists, exact verification commands, required subagent-decision reporting, two-cycle escalation, coordinator-only convergence, and copied side-effect-token fields. Revise `docs/protocol/agents/orchestration.md` so delegation is a model-chosen capacity tool, not a task-count or line-count mandate. Keep `env -u GIT_INDEX_FILE`, fixed writer mechanics, cursor ownership, clean scoped Git handling, and non-author verdict boundaries.

- [ ] **Step 5: Run model, prompt, ledger, and doc tests**

```bash
env -u GIT_INDEX_FILE .venv/bin/python -m pytest \
  tests/unit/test_protocol_mailbox.py \
  tests/unit/test_autonomous_seat_contract.py \
  tests/unit/test_protocol_prompt_sync.py \
  tests/unit/test_protocol_doc_integrity.py \
  tests/unit/test_codex_ledger_bridge.py -q
```

Expected: all pass; no active Codex or Claude adapter contains the retired behavior capsules.

- [ ] **Step 6: Commit Task 5**

```bash
env -u GIT_INDEX_FILE git add -- \
  scripts/codex_protocol_model.py \
  tests/unit/test_protocol_prompt_sync.py \
  tests/unit/test_protocol_doc_integrity.py \
  AGENTS.md \
  CLAUDE.md \
  docs/protocol/codex/continuation.md \
  docs/protocol/claude/continuation.md \
  docs/protocol/claude/independence-first.md \
  docs/protocol/agents/orchestration.md \
  .agents/skills/four-seat-protocol/SKILL.md \
  .agents/skills/seat-director/SKILL.md \
  .agents/skills/seat-operator/SKILL.md \
  .agents/skills/seat-coordinator/SKILL.md \
  .codex/agents/readiness-bridge.toml \
  .codex/agents/protocol-director.toml \
  .codex/agents/protocol-operator.toml \
  .codex/agents/protocol-coordinator.toml \
  .codex/agents/agent01.toml \
  .codex/agents/lane-v-verifier.toml \
  .claude/skills/four-seat-protocol/SKILL.md \
  .claude/skills/seat-director/SKILL.md \
  .claude/skills/seat-operator/SKILL.md \
  .claude/skills/seat-coordinator/SKILL.md \
  .claude/agents/readiness-bridge.md \
  .claude/agents/lane-v-verifier.md
env -u GIT_INDEX_FILE git diff --cached --check
env -u GIT_INDEX_FILE git commit -m "refactor(protocol): trust autonomous seat outcomes"
```

### Task 6: Sync architecture, record the decision, and obtain protocol GO

**Files:**
- Modify: `ARCHITECTURE.md`
- Modify: `DECISIONS.md`
- Modify only if current-claim search proves stale: `RUNBOOK-DAILY.md`, `docs/PROGRAM-MANUAL.md`

**Interfaces:**
- Consumes: Tasks 1–5 landed protocol behavior.
- Produces: factual topology, append-only decision rationale, full verification evidence, and a committed verification request to an eligible non-author Operator.

- [ ] **Step 1: Update architecture topology and invariants**

Replace `ARCHITECTURE.md` section 2 control flow with:

```text
user or parent prompt
  -> readiness or named-seat orientation
  -> active outcome contract + durable owner
  -> seat-chosen implementation, collaboration, or ownership exchange
  -> committed actual change + outcome-bound verify-request
  -> distinct-identity non-author Operator GO/NITS/FAIL with finding dispositions
  -> separately user-authorized exact external-effect tuple, if any
```

Update section 4 to state that conflict-free autonomous seat events may
supersede legacy coordinator routes by exact parent/revision, capacity tools are
diagnostics, preflight is advisory, actor identity cannot collapse across seats,
finding refs remain immutable, exact user authority is separate from token
shape, and actual-diff non-author GO remains the acceptance gate.

- [ ] **Step 2: Append the decision record**

Append to `DECISIONS.md` without modifying prior entries:

```markdown
## Autonomous seat outcome contract replaces coordinator-centered routing ceremony (2026-07-18)

**Decision.** Seats may claim, split, transfer, exchange, and reroute work through
durable accepted ownership events without coordinator approval. Routes bind an
outcome, owner, evidence bar, hard boundaries, and external-effect authority;
models choose the method and sufficient tests. Preflight is advisory. A
non-author Operator GO on the actual committed change remains required for
behavior-changing acceptance, and external effects remain separately
user-authorized.

**Why.** The maintenance chronology route repeatedly blocked implementation on
new omissions in a prescriptive preflight plan. The findings were useful, but
category-by-category plan closure became an unbounded convergence mechanism.
Outcome ownership plus actual-diff review preserves evidence and independence
while letting capable models choose the right engineering path.

**Compatibility.** Historical coordinator routes and capacity packets remain
immutable evidence. New outcome-contract events can supersede them explicitly.
Capacity boards and doctors remain diagnostics rather than discretionary route
authority.
```

- [ ] **Step 3: Search for live contradictory claims**

Run:

```bash
rg -n "coordinator owns convergence|Director2.*CLEAR|preflight.*CLEAR|Capacity Split Default|Subagent utilization decision|2-cycle escalation limit|route must be coordinator-to-all|exact test function|allowed paths, and commands" \
  AGENTS.md CLAUDE.md ARCHITECTURE.md RUNBOOK-DAILY.md docs/PROGRAM-MANUAL.md \
  docs/protocol/codex/continuation.md docs/protocol/claude/continuation.md \
  docs/protocol/claude/independence-first.md docs/protocol/agents/orchestration.md \
  .agents/skills .claude/skills .codex/agents .claude/agents scripts tests
```

Expected: no active normative claim contradicts the new model. Historical specs, plans, decisions, mailbox events, and archived evidence may still contain the phrases and must not be rewritten.

- [ ] **Step 4: Run the complete protocol verification profile**

```bash
env -u GIT_INDEX_FILE .venv/bin/python -m pytest \
  tests/unit/test_protocol_mailbox.py \
  tests/unit/test_autonomous_seat_contract.py \
  tests/unit/test_route_lineage.py \
  tests/unit/test_target_binding.py \
  tests/unit/test_protocol_capacity.py \
  tests/unit/test_compact_pair_loop.py \
  tests/unit/test_coordination_tooling.py \
  tests/unit/test_check_go_schema.py \
  tests/unit/test_protocol_prompt_sync.py \
  tests/unit/test_protocol_doc_integrity.py \
  tests/unit/test_codex_ledger_bridge.py -q
env -u GIT_INDEX_FILE .venv/bin/python scripts/check_coordination.py
env -u GIT_INDEX_FILE .venv/bin/python scripts/ci_smoke.py
env -u GIT_INDEX_FILE git diff --check
```

Expected: all pytest tests pass, coordination check passes, smoke ends `OK`, and diff check prints nothing.

This profile must include the Task 0 coverage targets: equal actor identity
across seats; recipient-authored acceptance, stale/forged/self claims and
takeover evidence; same-time/same-revision forks in both orders plus ledger
consumer fail-closed behavior; committed legacy coordination/status/decision
routes and pre-v3/v3/current reports; absent/exact/replayed effect authority;
and dropped/reordered/dispositioned finding refs.

- [ ] **Step 5: Commit docs and publish the actual-diff verify-request**

```bash
env -u GIT_INDEX_FILE git add -- ARCHITECTURE.md DECISIONS.md
env -u GIT_INDEX_FILE git diff --cached --name-status
env -u GIT_INDEX_FILE git diff --cached --check
env -u GIT_INDEX_FILE git commit -m "docs(protocol): record autonomous seat cutover"
```

If the contradiction search required a current-claim correction in `RUNBOOK-DAILY.md` or `docs/PROGRAM-MANUAL.md`, add only that proven-changed path explicitly before inspecting the staged diff. Historical decisions, archived mailbox evidence, and superseded doctrine not referenced by active adapters remain untouched. Then the authoring Director sends one committed verify-request through `coordination/bin/send-event` containing:

```text
Event type: verify-request
Reviewed head: <full Task-6 HEAD>
Reviewed base: <full parent before Task-1>
Author seat: <authoring director seat>
Author identity: <durable model or truthful cold-context identity>
Author identity kind: model | cold-context
Assigned operator: <eligible non-author operator seat>

## Finding Refs

- coordination/mailbox/sent/2026-07-18T06-05-32Z-operator-to-director-findings.md@fedfbe3
- coordination/mailbox/sent/2026-07-18T04-55-26Z-director2-to-coordinator-findings.md@6c11193

## Outcome

The reviewed range implements the approved autonomous seat outcome contract,
preserves legacy coordination/status/decision route and historical report
readability, fails closed on overlapping route lineage conflicts, preserves and
dispositions immutable material finding refs, requires distinct-identity non-
author actual-diff GO, and retains exact separately granted external-effect
authority.
```

Commit only the generated verify-request. No push, merge, route transition, cursor consumption, or ledger action is authorized by this step.

- [ ] **Step 6: Stop for non-author Operator verdict**

The assigned Operator independently reads the complete Task-1-through-Task-6
range, receives both required finding refs, chooses sufficient tests, and
issues GO/NITS/FAIL with an explicit disposition for every ref. Task 7 must not
begin on NITS, FAIL, unable-to-verify, an uncommitted report, equal actor
identity, missing finding disposition, or a report bound to another range.

### Task 7: Transition the blocked maintenance task to an autonomous outcome

**Files:**
- Create through fixed writer: `coordination/mailbox/sent/<timestamp>-director-to-all-coordination.md`

**Interfaces:**
- Consumes: Task 6 distinct-identity non-author GO, exact parent route
  `coordination/mailbox/sent/2026-07-18T04-37-59Z-coordinator-to-all-coordination.md`,
  Task 0 findings at `fedfbe3`, and Director2 findings at `6c11193`.
- Produces: the authoritative maintenance outcome contract selected by `ledger_start_guard.py`.

- [ ] **Step 1: Reconfirm the transition gate**

Run immediately before writing:

```bash
env -u GIT_INDEX_FILE git log --oneline -3
env -u GIT_INDEX_FILE git status --short --branch
env -u GIT_INDEX_FILE .venv/bin/python scripts/ledger_start_guard.py --seat director --wave 2
```

Read the committed Task 6 Operator GO body and confirm its reviewed head equals current `HEAD` or the exact implementation head named by the report. Stop if newer mail changes the maintenance outcome, ownership, hard boundaries, or ledger state.

- [ ] **Step 2: Publish the minimal transition event**

The already named owner `director` publishes its own acceptance; coordinator
approval is neither requested nor inferred. Use `coordination/bin/send-event
director all coordination "maintenance autonomous outcome transition"` with
this sender-supplied body:

```markdown
Task-board: pipeline-maintenance-priority-pause-2026-07-18
Task ID: pipeline-maintenance-priority-pause-2026-07-18
Outcome contract:
Parent contract: coordination/mailbox/sent/2026-07-18T04-37-59Z-coordinator-to-all-coordination.md@f752c88
Contract revision: 1
Previous owners: director
Owners: director
Proposal ref: self
Acceptance refs: self
Finding refs: coordination/mailbox/sent/2026-07-18T06-05-32Z-operator-to-director-findings.md@fedfbe3, coordination/mailbox/sent/2026-07-18T04-55-26Z-director2-to-coordinator-findings.md@6c11193

## Outcome

Deliver a committed handoff-selection correction that chooses the newest
durable same-seat handoff without filesystem-mtime, copy-lineage, commit-time,
or uncommitted-content authority; preserves visible warnings; and remains safe
through the CLI and seat-status consumers.

Evidence bar: focused regression evidence chosen by the owner, complete actual
diff inspection, and non-author Operator GO on the delivered commit or range.

Hard boundaries: preserve both immutable finding refs; no self-approval or
actor-identity collapse; no evidence suppression; no external effect.

External effect authority: none.

## Preserved Findings

- Both merge-base fail-closed paths require credible behavior and warning
  evidence in the delivered result.
- Metadata header occurrence detection must not let a valid field plus a blank
  or malformed sibling evade warning classification.

These are FINDING evidence, not a preflight CLEAR prerequisite. The owner may
choose the implementation and sufficient tests, counter with repository
evidence, narrow the outcome, or transfer ownership through an accepted durable
event.

The five evidence-ledger backend-checkpoint packets remain parked. Ledger
resume still requires the maintenance implementation's non-author Operator GO,
the live ledger guard, and separate resume authorization.
```

- [ ] **Step 3: Verify and commit only the transition event**

```bash
env -u GIT_INDEX_FILE git diff --cached --name-status
env -u GIT_INDEX_FILE git diff --cached --check
env -u GIT_INDEX_FILE .venv/bin/python scripts/check_coordination.py
env -u GIT_INDEX_FILE .venv/bin/python scripts/protocol_capacity_board.py --wave 2 --validate-route coordination/mailbox/sent/<generated-event>.md
env -u GIT_INDEX_FILE git commit -m "coord(protocol): transition maintenance to outcome contract"
```

Expected staged scope: exactly one generated mailbox event. Route validation is valid; capacity packet issues, if any, appear only as advisories.

- [ ] **Step 4: Prove the Director is no longer blocked by preflight CLEAR**

```bash
env -u GIT_INDEX_FILE .venv/bin/python scripts/ledger_start_guard.py --seat director --wave 2
env -u GIT_INDEX_FILE .venv/bin/python .agents/skills/four-seat-protocol/scripts/seat_status.py director --wave 2
env -u GIT_INDEX_FILE git status --short --branch
```

Expected: the guard names the generated outcome-contract event as active. The Director sees the outcome, preserved findings, and freedom to implement or exchange ownership. No output treats Director2 `CLEAR` as a prerequisite.

### Task 8: Run the first autonomous maintenance cycle without re-prescribing it

**Files:**
- Chosen by the accepting owner from current repository impact analysis.
- Verification request/report under `coordination/mailbox/sent/`.

**Interfaces:**
- Consumes: Task 7 outcome contract and preserved findings.
- Produces: owner-chosen implementation evidence, actual committed change, non-author Operator verdict, and a separately gated ledger-resume decision.

- [ ] **Step 1: Owner chooses and records the implementation path**

The Director may implement directly, collaborate, split the outcome, or transfer it through an accepted ownership event. It must inspect current definitions, callers, writes, CLI/seat-status consumers, and tests before editing. The route does not mandate test names, a preflight pass, or a particular parser structure.

- [ ] **Step 2: Preserve evidence while exercising model judgment**

The owner must keep both Director2 findings visible and either address each in the delivered result or provide repository evidence explaining why it does not apply. The owner chooses sufficient focused tests and may add stronger cases discovered during implementation.

- [ ] **Step 3: Commit and request independent review of the actual outcome**

The request binds the actual base/head, outcome, author seat, and chosen eligible Operator. It does not prescribe the Operator's commands or path checklist. The Operator independently inspects the actual diff, runs the tests it judges sufficient, and issues GO/NITS/FAIL.

- [ ] **Step 4: Apply the conditional ledger-resume gate**

Only after GO:

```bash
env -u GIT_INDEX_FILE .venv/bin/python scripts/ledger_start_guard.py --seat <accepted-owner-seat> --wave 2
env -u GIT_INDEX_FILE git status --short --branch
```

Confirm live ledger and mailbox state. Do not resume, merge, push, or mutate the evidence-ledger without a separate explicit authorization naming the effect, executor, target, and scope.

## Final Integration And Verification

After Tasks 1–8 reach their lawful stop conditions, run:

```bash
env -u GIT_INDEX_FILE .venv/bin/python -m pytest \
  tests/unit/test_autonomous_seat_contract.py \
  tests/unit/test_route_lineage.py \
  tests/unit/test_target_binding.py \
  tests/unit/test_protocol_capacity.py \
  tests/unit/test_compact_pair_loop.py \
  tests/unit/test_coordination_tooling.py \
  tests/unit/test_check_go_schema.py \
  tests/unit/test_protocol_prompt_sync.py \
  tests/unit/test_protocol_doc_integrity.py \
  tests/unit/test_codex_ledger_bridge.py -q
env -u GIT_INDEX_FILE .venv/bin/python scripts/check_coordination.py
env -u GIT_INDEX_FILE .venv/bin/python scripts/protocol_doctor.py --wave 2
env -u GIT_INDEX_FILE .venv/bin/python scripts/ci_smoke.py
env -u GIT_INDEX_FILE git diff --check
env -u GIT_INDEX_FILE git status --short --branch
```

Expected: focused pytest passes all Task 0 corpus/consumer cases, coordination
check passes, doctor reports no hard-boundary failure, smoke ends `OK`, diff
check is silent, and the worktree is clean. Diagnostics may report historical
or capacity advisories, but they do not override an exact current Operator
verdict or conflict-free ownership event.
