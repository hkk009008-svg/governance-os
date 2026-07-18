# Autonomous Seat Outcome Contract Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace coordinator-centered, checklist-driven four-seat routing with a compact outcome contract that lets seats reroute and exchange ownership directly while preserving durable evidence, non-author verification, and explicit external-effect authority.

**Architecture:** Migrate in two sequential deliverables. First, add semantic outcome/ownership primitives, teach route selection and compact-pair verification to accept autonomous seat work, demote capacity machinery to diagnostics, and shrink duplicated prompt surfaces. After that exact protocol commit receives non-author Operator GO, publish one compatible outcome-contract transition event that supersedes the blocked maintenance route; the accepting owner then chooses the chronology implementation and tests.

**Tech Stack:** Python 3.11+ standard library, pytest, Markdown protocol adapters, TOML Codex role prompts, fixed Git-backed mailbox writer.

## Global Constraints

- Source specification: `docs/superpowers/specs/2026-07-18-autonomous-seat-outcome-contract-design.md` at commit `5d0185c`.
- Durable repository and mailbox evidence outranks chat summaries and stale prose.
- An author cannot approve its own behavior-changing work; a non-author Operator supplies GO/NITS/FAIL for the actual committed change.
- External or difficult-to-reverse effects require explicit user authority, one executor, a target, and authorized scope.
- Known material findings remain visible through reviewer or ownership changes.
- Ordinary internal ownership changes require neither coordinator approval nor separate user authorization after cutover.
- The coordinator does not author behavior-changing production work unless the user explicitly assigns that model a director seat.
- Tasks 1–6 are authored by a user-named `director` or `director2`; the current coordinator may route, observe, and reconcile but does not implement them.
- Until Task 6 receives GO, the current R-INDEPENDENCE rule remains binding. Task 0 satisfies its design-time requirement once, without creating a preflight `CLEAR` gate.
- Historical mailbox events and capacity packets remain immutable evidence.
- The current maintenance route remains binding until Task 7 publishes and commits the transition event.
- Task 7 authorizes only a local mailbox transition event and local metadata commit when execution reaches that task; it does not authorize ledger resume, push, merge, lock, cursor consumption, target mutation, paid spend, or any remote effect.
- Use `env -u GIT_INDEX_FILE` for ordinary Git and pytest commands.
- Refresh `git log --oneline -3` and scoped status immediately before every write, stage, commit, or live gate decision.
- Preserve unrelated peer changes and stage only the exact task paths.

## File Structure

- `scripts/codex_protocol_model.py`: canonical semantic model for outcomes, ownership, work states, review independence, and external-effect authority.
- `scripts/route_lineage.py`: recognizes both legacy coordinator routes and autonomous seat outcome-contract events.
- `scripts/ledger_start_guard.py`: selects the authoritative compatible event for a bound target.
- `scripts/protocol_capacity.py`: retains capacity observability while limiting route blocking to structural and hard-boundary failures.
- `scripts/compact_pair_loop.py`: validates a minimal outcome-bound request/report instead of prescribing author tests and allowed paths.
- `tests/unit/test_autonomous_seat_contract.py`: focused semantic contract tests.
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
- Produces: a durable independent abuse-case enumeration that the authoring Director carries into Tasks 1–6.

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

The reviewer publishes with `coordination/bin/send-event <operator-seat> <director-seat> findings "autonomous outcome contract design findings"` and commits the generated event. The author adds every material finding to the Task 6 verification outcome and converts each feasible abuse case into a semantic test; when a test is infeasible, the plan records the exact repository evidence the actual-diff Operator must inspect. A hard-boundary contradiction must be resolved before implementation; ordinary edge cases remain acceptance evidence for the actual-diff review. This is a single current-law bridge, not a recurring preflight convergence loop.

- [ ] **Step 4: Confirm no implementation mutation occurred under coordinator authority**

```bash
env -u GIT_INDEX_FILE git status --short --branch
env -u GIT_INDEX_FILE git diff --name-only
```

Expected: only the two fixed-writer mailbox events and their commits were created before the authoring Director begins Task 1.

### Task 1: Add the semantic outcome and ownership model

**Files:**
- Modify: `scripts/codex_protocol_model.py`
- Create: `tests/unit/test_autonomous_seat_contract.py`

**Interfaces:**
- Consumes: `protocol_mailbox.RECEIVING_SEATS` and existing `OPERATOR_SEATS`.
- Produces: `OutcomeContract`, `OwnershipChange`, `ReviewDecision`, `ExternalEffectAuthorization`, `claim_outcome()`, `ownership_change_is_effective()`, `apply_ownership_change()`, `work_is_blocked()`, `review_accepts_outcome()`, and `external_effect_is_authorized()`.

- [ ] **Step 1: Write the semantic contract tests**

Create `tests/unit/test_autonomous_seat_contract.py`:

```python
from __future__ import annotations

from dataclasses import replace

import pytest

import codex_protocol_model as model


def _contract() -> model.OutcomeContract:
    return model.claim_outcome(
        task_id="maintenance-handoff-chronology",
        outcome="Select the newest durable same-seat handoff without mtime authority.",
        claimant="director",
        evidence_bar=("focused regression evidence", "non-author Operator review"),
        hard_boundaries=model.AUTONOMOUS_HARD_BOUNDARIES,
    )


def test_claim_creates_five_fact_outcome_contract() -> None:
    contract = _contract()
    assert contract.owners == ("director",)
    assert contract.external_effect is None
    assert contract.outcome.startswith("Select the newest")
    assert contract.evidence_bar == (
        "focused regression evidence",
        "non-author Operator review",
    )


def test_transfer_requires_receiving_owner_acceptance() -> None:
    contract = _contract()
    proposed = model.OwnershipChange(
        task_id=contract.task_id,
        previous_owners=("director",),
        new_owners=("director2",),
        accepted_by=(),
    )
    assert not model.ownership_change_is_effective(proposed)
    with pytest.raises(ValueError, match="not effective"):
        model.apply_ownership_change(contract, proposed)

    accepted = model.OwnershipChange(
        task_id=contract.task_id,
        previous_owners=("director",),
        new_owners=("director2",),
        accepted_by=("director2",),
    )
    assert model.apply_ownership_change(contract, accepted).owners == ("director2",)


def test_split_merge_and_exchange_need_no_coordinator() -> None:
    contract = _contract()
    split = model.OwnershipChange(
        task_id=contract.task_id,
        previous_owners=("director",),
        new_owners=("director", "operator2"),
        accepted_by=("director", "operator2"),
    )
    changed = model.apply_ownership_change(contract, split)
    assert changed.owners == ("director", "operator2")
    assert "coordinator" not in split.accepted_by


def test_abandoned_takeover_requires_fresh_work_and_lock_checks() -> None:
    contract = _contract()
    incomplete = model.OwnershipChange(
        task_id=contract.task_id,
        previous_owners=("director",),
        new_owners=("director2",),
        accepted_by=(),
        abandoned_takeover=True,
        fresh_work_checked=True,
        active_lock_checked=False,
    )
    assert not model.ownership_change_is_effective(incomplete)

    complete = model.OwnershipChange(
        task_id=contract.task_id,
        previous_owners=("director",),
        new_owners=("director2",),
        accepted_by=(),
        abandoned_takeover=True,
        fresh_work_checked=True,
        active_lock_checked=True,
    )
    assert model.apply_ownership_change(contract, complete).owners == ("director2",)


def test_finding_alone_is_not_blocked() -> None:
    assert not model.work_is_blocked()
    assert model.work_is_blocked(new_authority_required=True)
    assert model.work_is_blocked(external_state_unavailable=True)
    assert model.work_is_blocked(hard_boundary_violation=True)


def test_only_non_author_operator_go_accepts_actual_revision() -> None:
    accepted = model.ReviewDecision(
        task_id="maintenance-handoff-chronology",
        author="director",
        operator="operator",
        reviewed_revision="a" * 40,
        verdict="GO",
        material_findings=(),
    )
    assert model.review_accepts_outcome(accepted)
    assert not model.review_accepts_outcome(
        replace(accepted, operator="director")
    )
    assert not model.review_accepts_outcome(
        replace(accepted, verdict="NITS")
    )


def test_external_effect_requires_one_known_executor_target_and_scope() -> None:
    authorization = model.ExternalEffectAuthorization(
        effect="git push",
        executor="director",
        target="origin/main",
        scope=("fast-forward only",),
    )
    assert model.external_effect_is_authorized(authorization)
    assert not model.external_effect_is_authorized(
        model.ExternalEffectAuthorization(
            effect="git push",
            executor="director, operator",
            target="origin/main",
            scope=("fast-forward only",),
        )
    )
```

- [ ] **Step 2: Run the new tests and confirm RED**

Run:

```bash
env -u GIT_INDEX_FILE .venv/bin/python -m pytest tests/unit/test_autonomous_seat_contract.py -q
```

Expected: collection fails because the new dataclasses and functions do not exist.

- [ ] **Step 3: Implement the semantic model**

Add `dataclass` and `replace` imports to `scripts/codex_protocol_model.py`, then add this block after the seat tuples:

```python
from dataclasses import dataclass, replace


AUTONOMOUS_WORK_STATES = (
    "WORKING",
    "NEEDS_PEER",
    "FINDING",
    "BLOCKED",
    "READY_FOR_REVIEW",
    "ACCEPTED",
)

AUTONOMOUS_HARD_BOUNDARIES = (
    "durable evidence outranks chat and stale prose",
    "an author cannot approve its own behavior-changing work",
    "external effects require explicit authority, one executor, target, and scope",
    "known material evidence cannot be concealed",
    "coordinator does not author behavior-changing production work",
)


@dataclass(frozen=True)
class OutcomeContract:
    task_id: str
    outcome: str
    owners: tuple[str, ...]
    evidence_bar: tuple[str, ...]
    hard_boundaries: tuple[str, ...]
    external_effect: str | None = None


@dataclass(frozen=True)
class OwnershipChange:
    task_id: str
    previous_owners: tuple[str, ...]
    new_owners: tuple[str, ...]
    accepted_by: tuple[str, ...]
    outcome: str | None = None
    abandoned_takeover: bool = False
    fresh_work_checked: bool = False
    active_lock_checked: bool = False


@dataclass(frozen=True)
class ReviewDecision:
    task_id: str
    author: str
    operator: str
    reviewed_revision: str
    verdict: str
    material_findings: tuple[str, ...]


@dataclass(frozen=True)
class ExternalEffectAuthorization:
    effect: str
    executor: str
    target: str
    scope: tuple[str, ...]


def claim_outcome(
    *,
    task_id: str,
    outcome: str,
    claimant: str,
    evidence_bar: tuple[str, ...],
    hard_boundaries: tuple[str, ...],
    external_effect: str | None = None,
) -> OutcomeContract:
    if claimant not in protocol_mailbox.RECEIVING_SEATS:
        raise ValueError(f"unknown claimant: {claimant}")
    if not task_id.strip() or not outcome.strip() or not evidence_bar:
        raise ValueError("outcome claim requires task, outcome, and evidence")
    return OutcomeContract(
        task_id=task_id,
        outcome=outcome,
        owners=(claimant,),
        evidence_bar=evidence_bar,
        hard_boundaries=hard_boundaries,
        external_effect=external_effect,
    )


def ownership_change_is_effective(change: OwnershipChange) -> bool:
    if not change.new_owners or any(
        owner not in protocol_mailbox.RECEIVING_SEATS for owner in change.new_owners
    ):
        return False
    if change.abandoned_takeover:
        return change.fresh_work_checked and change.active_lock_checked
    return set(change.new_owners).issubset(change.accepted_by)


def apply_ownership_change(
    contract: OutcomeContract,
    change: OwnershipChange,
) -> OutcomeContract:
    if change.task_id != contract.task_id:
        raise ValueError("ownership change targets another task")
    if change.previous_owners != contract.owners:
        raise ValueError("ownership change does not match current owners")
    if not ownership_change_is_effective(change):
        raise ValueError("ownership change is not effective")
    return replace(
        contract,
        owners=change.new_owners,
        outcome=change.outcome or contract.outcome,
    )


def work_is_blocked(
    *,
    new_authority_required: bool = False,
    external_state_unavailable: bool = False,
    hard_boundary_violation: bool = False,
) -> bool:
    return any(
        (new_authority_required, external_state_unavailable, hard_boundary_violation)
    )


def review_accepts_outcome(decision: ReviewDecision) -> bool:
    return (
        decision.operator in OPERATOR_SEATS
        and decision.operator != decision.author
        and len(decision.reviewed_revision) == 40
        and decision.verdict == "GO"
    )


def external_effect_is_authorized(
    authorization: ExternalEffectAuthorization,
) -> bool:
    return (
        bool(authorization.effect.strip())
        and authorization.executor in protocol_mailbox.RECEIVING_SEATS
        and bool(authorization.target.strip())
        and bool(authorization.scope)
        and all(item.strip() for item in authorization.scope)
    )
```

- [ ] **Step 4: Run the focused tests and confirm GREEN**

Run:

```bash
env -u GIT_INDEX_FILE .venv/bin/python -m pytest tests/unit/test_autonomous_seat_contract.py -q
```

Expected: `7 passed`.

- [ ] **Step 5: Commit Task 1**

```bash
env -u GIT_INDEX_FILE git add -- scripts/codex_protocol_model.py tests/unit/test_autonomous_seat_contract.py
env -u GIT_INDEX_FILE git diff --cached --check
env -u GIT_INDEX_FILE git commit -m "feat(protocol): model autonomous seat outcomes"
```

### Task 2: Let any seat publish an authoritative outcome-contract route

**Files:**
- Modify: `scripts/route_lineage.py`
- Modify: `scripts/ledger_start_guard.py`
- Modify: `tests/unit/test_route_lineage.py`

**Interfaces:**
- Consumes: legacy coordinator route filenames and `Outcome contract:` markers.
- Produces: `route_lineage.is_route_event(path, body) -> bool` and `route_lineage.load_route_paths(root) -> list[Path]`.

- [ ] **Step 1: Add autonomous route-selection tests**

Append to `tests/unit/test_route_lineage.py`:

```python
def test_director_outcome_contract_can_supersede_legacy_coordinator_route(tmp_path):
    import ledger_start_guard

    legacy = _write_route(
        tmp_path,
        "2026-07-18T04-37-59Z-coordinator-to-all-coordination.md",
        "Task-board: evidence-ledger-maintenance\nThis routes ledger work.\n",
    )
    autonomous = _write_route(
        tmp_path,
        "2026-07-18T06-00-00Z-director-to-all-coordination.md",
        "Task-board: evidence-ledger-maintenance\n"
        "Outcome contract:\n"
        "Outcome: implement and verify the maintenance selector\n"
        "Owner: director\n"
        f"Supersedes route: {legacy.as_posix()}\n",
    )

    assert route_lineage.is_route_event(autonomous, autonomous.read_text())
    assert ledger_start_guard.find_latest_ledger_route(tmp_path) == autonomous


def test_unmarked_seat_coordination_does_not_become_a_route(tmp_path):
    unmarked = _write_route(
        tmp_path,
        "2026-07-18T06-00-00Z-director2-to-all-coordination.md",
        "Task-board: evidence-ledger-maintenance\nThis is advisory only.\n",
    )
    assert not route_lineage.is_route_event(unmarked, unmarked.read_text())


def test_load_routes_includes_marked_operator_authored_outcome(tmp_path):
    route = _write_route(
        tmp_path,
        "2026-07-18T06-10-00Z-operator2-to-all-coordination.md",
        "Task-board: evidence-ledger-maintenance\n"
        "Outcome contract:\n"
        "Owner: operator2\n"
        "Route generation: 1\n",
    )
    assert [item.route_id for item in route_lineage.load_routes(tmp_path)] == [
        route_lineage.route_id_of(route.name)
    ]


def test_seat_cannot_assign_an_unwilling_owner_by_route(tmp_path):
    route = _write_route(
        tmp_path,
        "2026-07-18T06-20-00Z-director-to-all-coordination.md",
        "Task-board: evidence-ledger-maintenance\n"
        "Outcome contract:\n"
        "Owner: operator2\n",
    )
    assert not route_lineage.is_route_event(route, route.read_text())
```

- [ ] **Step 2: Run the focused tests and confirm RED**

```bash
env -u GIT_INDEX_FILE .venv/bin/python -m pytest tests/unit/test_route_lineage.py -k "outcome_contract or unmarked_seat or operator_authored or unwilling_owner" -q
```

Expected: failures because direct seat route events are not recognized.

- [ ] **Step 3: Centralize compatible route discovery**

Add to `scripts/route_lineage.py`:

```python
_OUTCOME_CONTRACT_RE = re.compile(
    r"^\s*Outcome contract:\s*$",
    re.IGNORECASE | re.MULTILINE,
)
_DIRECT_SEAT_ROUTE_RE = re.compile(
    r"Z-(?P<sender>director2?|operator2?)-to-all-coordination\.md$"
)
_OWNER_RE = re.compile(r"^\s*Owner:\s*(?P<value>[a-z0-9]+)\s*$", re.MULTILINE)


def is_route_event(path: Path, body: str) -> bool:
    name = path.name
    if not name.endswith("-to-all-coordination.md") or "Task-board:" not in body:
        return False
    if "-coordinator-to-all-" in name or "-coordinator2-to-all-" in name:
        return True
    match = _DIRECT_SEAT_ROUTE_RE.search(name)
    owners = _OWNER_RE.findall(body)
    return (
        match is not None
        and _OUTCOME_CONTRACT_RE.search(body) is not None
        and len(owners) == 1
        and owners[0] == match.group("sender")
    )


def load_route_paths(root: Path) -> list[Path]:
    sent = root / "coordination" / "mailbox" / "sent"
    if not sent.exists():
        return []
    paths: list[Path] = []
    for path in sorted(sent.glob("*-to-all-coordination.md")):
        try:
            body = path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        if is_route_event(path, body):
            paths.append(path)
    return paths
```

Replace `load_routes()` with:

```python
def load_routes(root: Path) -> list[LineageRoute]:
    routes: list[LineageRoute] = []
    for path in load_route_paths(root):
        body = path.read_text(encoding="utf-8", errors="replace")
        routes.append(LineageRoute(route_id_of(path.name), parse_lineage(body)))
    return routes
```

In `scripts/ledger_start_guard.py`, replace the coordinator-only glob loop with:

```python
    candidates: list[Path] = []
    for path in sorted(route_lineage.load_route_paths(root), reverse=True):
        try:
            body = path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        body_lower = body.lower()
        if any(keyword in body_lower for keyword in target.route_keywords) or (
            target.path.as_posix() in body
        ):
            candidates.append(path)
```

Update its docstrings and user-facing error from “coordinator route” to “outcome-contract route”.

For a direct-seat route, the fixed-writer sender must be the declared owner. Publishing the superseding event is therefore the receiving owner's durable acceptance; an incumbent may propose a transfer but cannot assign an unwilling seat. A split or exchange becomes a set of recipient-authored outcome events for the accepted child outcomes. Seats pause only overlapping writes if competing claims appear.

- [ ] **Step 4: Run route and guard tests**

```bash
env -u GIT_INDEX_FILE .venv/bin/python -m pytest tests/unit/test_route_lineage.py tests/unit/test_target_binding.py -q
```

Expected: all pass, including legacy fallback and the four new autonomous cases.

- [ ] **Step 5: Commit Task 2**

```bash
env -u GIT_INDEX_FILE git add -- scripts/route_lineage.py scripts/ledger_start_guard.py tests/unit/test_route_lineage.py
env -u GIT_INDEX_FILE git diff --cached --check
env -u GIT_INDEX_FILE git commit -m "feat(protocol): accept seat-owned outcome routes"
```

### Task 3: Demote capacity rules and compact external-effect authorization

**Files:**
- Modify: `scripts/protocol_capacity.py`
- Modify: `tests/unit/test_protocol_capacity.py`

**Interfaces:**
- Consumes: `route_lineage.is_route_event()` and legacy ten-field side-effect tokens.
- Produces: four-field compact authorization, advisory capacity findings, and hard-boundary-only route validity.

- [ ] **Step 1: Write focused route and authorization tests**

Append to `tests/unit/test_protocol_capacity.py`:

```python
def test_autonomous_outcome_route_needs_no_packets_join_or_capacity_split(tmp_path: Path):
    route = _write_route(
        tmp_path,
        "2026-07-18T06-00-00Z-director-to-all-coordination.md",
        "Task-board: maintenance\n"
        "Outcome contract:\n"
        "Outcome: deliver the reviewed maintenance selector\n"
        "Owner: director\n"
        "Evidence bar: focused tests and non-author GO\n"
        "Hard boundaries: no external effect\n",
    )
    result = protocol_capacity.validate_route(tmp_path, 2, route)
    assert result.valid
    assert result.blocking_issues == []
    assert any("no capacity packets" in item["message"] for item in result.advisories)


def test_internal_outcome_route_is_not_a_shared_external_effect(tmp_path: Path):
    route = _write_route(
        tmp_path,
        "2026-07-18T06-01-00Z-director2-to-all-coordination.md",
        "Task-board: maintenance\n"
        "Outcome contract:\n"
        "Owner: director2\n"
        "Ownership change: director -> director2, accepted by director2\n",
    )
    assert protocol_capacity.validate_route(tmp_path, 2, route).valid


def test_compact_external_effect_authorization_is_sufficient(tmp_path: Path):
    route = _write_route(
        tmp_path,
        "2026-07-18T06-02-00Z-director-to-all-coordination.md",
        "Task-board: publish\n"
        "Outcome contract:\n"
        "Owner: director\n"
        "This route authorizes director to push origin/main.\n\n"
        "## Side-Effect Executor Token\n\n"
        "- effect: git push\n"
        "- executor: director\n"
        "- target: origin/main\n"
        "- authorized_scope: fast-forward only\n",
    )
    assert protocol_capacity.validate_route(tmp_path, 2, route).valid


def test_compact_external_effect_authorization_requires_scope(tmp_path: Path):
    route = _write_route(
        tmp_path,
        "2026-07-18T06-03-00Z-director-to-all-coordination.md",
        "Task-board: publish\n"
        "Outcome contract:\n"
        "Owner: director\n"
        "This route authorizes director to push origin/main.\n\n"
        "## Side-Effect Executor Token\n\n"
        "- effect: git push\n"
        "- executor: director\n"
        "- target: origin/main\n",
    )
    result = protocol_capacity.validate_route(tmp_path, 2, route)
    assert not result.valid
    assert "authorized_scope" in "\n".join(
        item["message"] for item in result.blocking_issues
    )
```

- [ ] **Step 2: Run the new tests and confirm RED**

```bash
env -u GIT_INDEX_FILE .venv/bin/python -m pytest tests/unit/test_protocol_capacity.py -k "autonomous_outcome or internal_outcome or compact_external" -q
```

Expected: failures from coordinator-only validation, capacity coupling, and the legacy ten-field token requirement.

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

- [ ] **Step 4: Accept compact and legacy external-effect tokens**

Replace the token constants with:

```python
REQUIRED_SIDE_EFFECT_TOKEN_FIELDS = (
    "effect",
    "executor",
    "target",
    "authorized_scope",
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

Add aliases for `effect`, `authorized_scope`, `authorized scope`, and `scope`. Remove `route mutation` from `SHARED_SIDE_EFFECT_PATTERNS`; internal mailbox ownership events are not external effects.

Add:

```python
def _token_is_complete(token: dict[str, str]) -> bool:
    compact = all(token.get(field) for field in REQUIRED_SIDE_EFFECT_TOKEN_FIELDS)
    legacy = all(token.get(field) for field in LEGACY_SIDE_EFFECT_TOKEN_FIELDS)
    return compact or legacy
```

Use `_token_is_complete()` wherever completeness is currently calculated. In `_token_covers_side_effect()`, build token text from `effect` when present and otherwise `allowed_command_class`:

```python
    effect = token.get("effect") or token.get("allowed_command_class", "")
    token_text = f"{effect} {token.get('target', '')}".lower()
```

Keep the existing exactly-one-executor check and legacy-token positive test.

The four-field token is structural evidence of the separately granted authorization; route validity does not create user authority. Keep the hard-boundary text and tests explicit that an executor may act only after the user has authorized that effect, target, and scope.

- [ ] **Step 5: Run the capacity tests**

```bash
env -u GIT_INDEX_FILE .venv/bin/python -m pytest tests/unit/test_protocol_capacity.py -q
```

Expected: all pass after deleting or rewriting the coordinator-only and capacity-split route assertions.

- [ ] **Step 6: Commit Task 3**

```bash
env -u GIT_INDEX_FILE git add -- scripts/protocol_capacity.py tests/unit/test_protocol_capacity.py
env -u GIT_INDEX_FILE git diff --cached --check
env -u GIT_INDEX_FILE git commit -m "refactor(protocol): make capacity routing advisory"
```

### Task 4: Reduce compact-pair authority to outcome and independent review

**Files:**
- Modify: `scripts/compact_pair_loop.py`
- Modify: `tests/unit/test_compact_pair_loop.py`
- Modify: `tests/unit/test_coordination_tooling.py`
- Modify: `tests/unit/test_check_go_schema.py`
- Modify: `.agents/skills/seat-operator/verification-report-format.md`
- Modify: `.claude/skills/seat-operator/verification-report-format.md`

**Interfaces:**
- Consumes: existing committed verify-request/report envelopes and historical verbose fields.
- Produces: minimal request authority `(reviewed base/head, outcome, author seat, assigned non-author Operator)` and report authority `(request binding, reviewed range, reviewer seat, verdict, evidence)`.

- [ ] **Step 1: Rewrite fixtures to prove the minimal contract**

Change `_request_text()` in `tests/unit/test_compact_pair_loop.py` to:

```python
def _request_text(base: str, head: str) -> str:
    return f"""\
# Director → Operator: verify outcome

**When:** 2026-07-17T08:00:00Z · **From:** director (online)

Event type: verify-request
Reviewed head: {head}
Reviewed base: {base}
Author seat: director
Assigned operator: operator

## Outcome

The committed change satisfies the routed maintenance outcome.

Cursor at send: 0
"""
```

Remove `allowed` arguments and assertions. Keep exact commit/range, request-commit, envelope, and non-author tests. Update the writer fixture in `tests/unit/test_coordination_tooling.py` to emit the same minimal request/report shapes. Add:

```python
def test_request_needs_outcome_but_not_prescribed_paths_or_commands(tmp_path: Path) -> None:
    root, base, head, trigger = _repo(tmp_path)
    request = pair.parse_verify_request(root, REQUEST_PATH, trigger)
    assert request.outcome == "The committed change satisfies the routed maintenance outcome."
    assert request.reviewed_base == base
    assert request.reviewed_head == head


def test_operator_authored_change_can_be_reviewed_by_operator2(tmp_path: Path) -> None:
    path = REQUEST_PATH.replace("director-to-operator", "operator-to-operator2")
    root, _, _, trigger = _repo(
        tmp_path,
        request_path=path,
        request_transform=lambda text: text.replace(
            "**From:** director", "**From:** operator"
        ).replace("Author seat: director", "Author seat: operator").replace(
            "Assigned operator: operator", "Assigned operator: operator2"
        ),
    )
    assert pair.parse_verify_request(root, path, trigger).assigned_operator == "operator2"


def test_author_cannot_assign_itself_as_reviewer(tmp_path: Path) -> None:
    path = REQUEST_PATH.replace("director-to-operator", "operator-to-operator")
    root, _, _, trigger = _repo(
        tmp_path,
        request_path=path,
        request_transform=lambda text: text.replace(
            "**From:** director", "**From:** operator"
        ).replace("Author seat: director", "Author seat: operator"),
    )
    with pytest.raises(pair.CompactPairError, match="non-author"):
        pair.parse_verify_request(root, path, trigger)
```

Update `_repo()` to accept `request_path` and `request_transform` explicitly. Add a GO-without-evidence rejection while retaining truthful NITS/FAIL without success evidence. Extend `tests/unit/test_check_go_schema.py` so a structurally valid current GO report with `## Evidence` passes and the same report with an empty evidence section fails.

- [ ] **Step 2: Run compact-pair tests and confirm RED**

```bash
env -u GIT_INDEX_FILE .venv/bin/python -m pytest tests/unit/test_compact_pair_loop.py -q
```

Expected: failures because paths, commands, author model, and the old author-role regex are still mandatory.

- [ ] **Step 3: Implement the minimal compatible parser**

Change `REQUEST_RE` so the author may be any pair seat while the reviewer remains an Operator:

```python
REQUEST_RE = re.compile(
    r"coordination/mailbox/sent/"
    r"[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}-[0-9]{2}-[0-9]{2}Z-"
    r"(?P<author>director2?|operator2?)-to-(?P<operator>operator2?)-verify-request\.md"
)
```

Replace `VerifyRequest` with:

```python
@dataclass(frozen=True)
class VerifyRequest:
    path: str
    trigger_commit: str
    reviewed_head: str
    reviewed_base: str
    author_seat: str
    assigned_operator: str
    outcome: str
```

Replace `VerificationReport` with:

```python
@dataclass(frozen=True)
class VerificationReport:
    path: str
    verdict: str
    request_path: str
    request_commit: str
    reviewed_head: str
    reviewed_base: str
    reviewer_seat: str
    evidence: tuple[str, ...]
    filename_reviewer: str
    envelope_sender: str
```

Add an optional section helper that still rejects duplicates:

```python
def _section_optional(lines: list[str], heading: str) -> list[str] | None:
    positions = [index for index, line in enumerate(lines) if line == heading]
    if not positions:
        return None
    if len(positions) != 1:
        raise CompactPairError(f"duplicate {heading}")
    return _section(lines, heading)
```

In `parse_verify_request()`, keep the exact Git, envelope, author, assigned-operator, and ancestry checks. Reject `assigned == author` with `Assigned operator must be a non-author`. Replace model/question/path/command parsing with:

```python
    outcome_lines = _section_optional(lines, "## Outcome")
    if outcome_lines is None:
        outcome_lines = _section(lines, "## Acceptance Question")
    outcome = "\n".join(outcome_lines).strip()
    if not outcome:
        raise CompactPairError("Outcome must be nonempty")
    return VerifyRequest(
        path=path,
        trigger_commit=trigger,
        reviewed_head=head,
        reviewed_base=base,
        author_seat=author,
        assigned_operator=assigned,
        outcome=outcome,
    )
```

In report parsing, require the existing binding/range/reviewer fields, parse `## Evidence` lines when present, and ignore legacy model/harness/context/allowed-path fields:

```python
    evidence_lines = _section_optional(lines, "## Evidence")
    evidence = tuple(line for line in (evidence_lines or ()) if line)
    if verdict == "GO" and not evidence:
        raise CompactPairError("GO requires material evidence")
```

Return the reduced dataclass. In `validate_report()`, retain request validity, reviewer envelope/path matching, assigned reviewer, reviewer-not-author, and reviewed base/head equality. Delete author-model equality, allowed-path equality, and requested-command enforcement. Still run a Git diff of the reviewed range solely to prove the range exists; do not use it to enforce a predeclared path allowlist.

Replace both report-format mirrors with this minimal body skeleton while keeping their bytes identical:

```markdown
Event type: verification-report
VERDICT: GO | NITS | FAIL
Verification request: coordination/mailbox/sent/<verify-request>.md@<40-lowercase-request-commit>
Reviewed head: <40-lowercase-hex>
Reviewed base: <40-lowercase-hex>
Reviewer seat: operator | operator2

## Evidence

$ <reviewer-chosen command or inspection>
→ <observed result>

## Findings

None.
```

GO requires material evidence. NITS and FAIL remain publishable when evidence is unavailable, provided the report states the limitation truthfully.

- [ ] **Step 4: Run compact-pair and writer integration tests**

```bash
env -u GIT_INDEX_FILE .venv/bin/python -m pytest tests/unit/test_compact_pair_loop.py tests/unit/test_coordination_tooling.py -q
env -u GIT_INDEX_FILE .venv/bin/python -m pytest tests/unit/test_check_go_schema.py -q
```

Expected: all pass, including legacy verbose request/report compatibility.

- [ ] **Step 5: Commit Task 4**

```bash
env -u GIT_INDEX_FILE git add -- \
  scripts/compact_pair_loop.py \
  tests/unit/test_compact_pair_loop.py \
  tests/unit/test_coordination_tooling.py \
  tests/unit/test_check_go_schema.py \
  .agents/skills/seat-operator/verification-report-format.md \
  .claude/skills/seat-operator/verification-report-format.md
env -u GIT_INDEX_FILE git diff --cached --check
env -u GIT_INDEX_FILE git commit -m "refactor(protocol): bind reviews to outcomes"
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
    "Any seat may claim, split, merge, transfer, exchange, or reroute work without coordinator approval; a receiving owner must accept a normal transfer.",
    "WORKING means meaningful progress remains; NEEDS_PEER requests help; FINDING is not BLOCKED; BLOCKED means no lawful path exists without new authority, unavailable external state, or hard-boundary resolution.",
    "Preflight is advisory and preserves material findings; it does not require CLEAR before implementation.",
    "Behavior-changing work is accepted only by non-author Operator GO on the actual reviewed commit or range.",
    "External effects require explicit user authority, one executor, target, and authorized scope.",
    "Known material evidence remains visible through ownership or reviewer changes.",
    "Coordinator observes and facilitates but is not the mandatory route author or convergence gate and does not author behavior-changing production work.",
)


def render_autonomous_seat_contract() -> str:
    return AUTONOMOUS_SEAT_REFERENCE + "\n" + "\n".join(
        f"- {rule}" for rule in AUTONOMOUS_SEAT_RULES
    )
```

Revise `COMPACT_PAIR_INVARIANT` to require only the committed reviewed base/head, outcome, author seat, assigned non-author Operator, and one bound report. Revise R-INDEPENDENCE in the model, `CLAUDE.md`, and `docs/protocol/claude/independence-first.md`: an adversarial-surface owner explicitly assesses plausible abuse classes and preserves material independent findings, while the owner and actual-diff Operator choose proportional review depth. Early independent review is encouraged when it adds signal; it is not a universal pre-implementation `CLEAR` gate. Non-author actual-diff GO remains mandatory.

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
work, and keep external effects separately user-authorized.
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
  -> non-author Operator GO/NITS/FAIL
  -> separately authorized external effect, if any
```

Update section 4 to state that autonomous seat events may supersede legacy coordinator routes, capacity tools are diagnostics, preflight is advisory, and actual-diff non-author GO remains the acceptance gate.

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
Assigned operator: <eligible non-author operator seat>

## Outcome

The reviewed range implements the approved autonomous seat outcome contract,
preserves legacy route readability, keeps material findings visible, requires
non-author actual-diff GO, and retains explicit external-effect authority.
```

Commit only the generated verify-request. No push, merge, route transition, cursor consumption, or ledger action is authorized by this step.

- [ ] **Step 6: Stop for non-author Operator verdict**

The assigned Operator independently reads the complete Task-1-through-Task-6 range, chooses sufficient tests, and issues GO/NITS/FAIL. Task 7 must not begin on NITS, FAIL, unable-to-verify, an uncommitted report, or a report bound to another range.

### Task 7: Transition the blocked maintenance task to an autonomous outcome

**Files:**
- Create through fixed writer: `coordination/mailbox/sent/<timestamp>-coordinator-to-all-coordination.md`

**Interfaces:**
- Consumes: Task 6 non-author GO, current route `coordination/mailbox/sent/2026-07-18T04-37-59Z-coordinator-to-all-coordination.md`, and Director2 findings `coordination/mailbox/sent/2026-07-18T04-55-26Z-director2-to-coordinator-findings.md` at `6c11193`.
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

Use `coordination/bin/send-event coordinator all coordination "maintenance autonomous outcome transition"` with this sender-supplied body. The writer adds the H1, timestamp/from envelope, cursor footer, and filename:

```markdown
Task-board: pipeline-maintenance-priority-pause-2026-07-18
Outcome contract:
Supersedes route: coordination/mailbox/sent/2026-07-18T04-37-59Z-coordinator-to-all-coordination.md

## Outcome

Deliver a committed handoff-selection correction that chooses the newest
durable same-seat handoff without filesystem-mtime, copy-lineage, commit-time,
or uncommitted-content authority; preserves visible warnings; and remains safe
through the CLI and seat-status consumers.

Owner: director

Evidence bar: focused regression evidence chosen by the owner, complete actual
diff inspection, and non-author Operator GO on the delivered commit or range.

Hard boundaries: preserve both Director2 chronology findings as material risk
evidence; no self-approval; no evidence suppression; no external effect.

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

Expected: focused pytest profile passes, coordination check passes, doctor reports no hard-boundary failure, smoke ends `OK`, diff check is silent, and the worktree is clean. Diagnostics may report historical or capacity advisories, but they do not override an exact current Operator verdict or ownership event.
