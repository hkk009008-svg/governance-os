#!/usr/bin/env python3
"""Resolve legacy and autonomous mailbox routes without trusting filenames.

Legacy coordinator Task-board events retain ADR-015 compatibility.  Autonomous
seat routes are effective only when their exact committed fixed-writer bodies
bind an immutable parent and Task 1 validates the ownership evidence.
"""
from __future__ import annotations

import argparse
import os
import re
import subprocess
from dataclasses import dataclass, field, replace
from pathlib import Path

import codex_protocol_model
import protocol_mailbox


_REPO_ROOT = Path(__file__).resolve().parent.parent

_GENERATION_FIELD_RE = re.compile(
    r"^\s*Route generation:\s*(?P<value>.*?)\s*$", re.IGNORECASE
)
_GENERATION_SHAPED_RE = re.compile(r"^\s*Route\s+generation\b", re.IGNORECASE)
_SUPERSEDES_FIELD_RE = re.compile(
    r"^\s*Supersedes(?P<active>\s+active)?\s+route:\s*(?P<value>.*?)\s*$",
    re.IGNORECASE,
)
_SUPERSEDES_SHAPED_RE = re.compile(
    r"^\s*Supersedes(?:\s+active)?\s+route\b", re.IGNORECASE
)
_CONTROL_HEAD_FIELD_RE = re.compile(
    r"^\s*(?P<label>Expected control HEAD|Control HEAD):\s*(?P<value>.*?)\s*$",
    re.IGNORECASE,
)
_CONTROL_HEAD_SHAPED_RE = re.compile(
    r"^\s*(?:Expected\s+control\s+HEAD|Control\s+HEAD)\b", re.IGNORECASE
)
_ROUTE_NAME_RE = re.compile(
    r"^\d{4}-\d{2}-\d{2}T\d{2}-\d{2}-\d{2}Z-"
    r"(?P<sender>[a-z][a-z0-9]*)-to-all-"
    r"(?P<kind>coordination|status|decision)\.md$"
)
_AUTONOMOUS_FIELDS = (
    "Task ID",
    "Outcome contract",
    "Parent contract",
    "Contract revision",
    "Previous owners",
    "Owners",
    "Proposal ref",
    "Acceptance refs",
    "Finding refs",
)
_NONE_VALUES = {"none", "(none)"}


def route_id_of(path_or_name: str) -> str:
    """Normalize a route reference (path or filename) to its bare stem."""

    name = Path(path_or_name.strip()).name
    if name.endswith(".md"):
        name = name[:-3]
    return name


@dataclass(frozen=True)
class RouteLineage:
    generation: int | None
    parent_route_id: str | None
    expected_control_head: str | None
    parent_route_ids: tuple[str, ...] = ()

    def __post_init__(self) -> None:
        """Retain the legacy scalar while making every merge edge explicit."""

        parent_ids = tuple(self.parent_route_ids)
        if parent_ids:
            if self.parent_route_id is not None and (
                len(parent_ids) != 1 or parent_ids[0] != self.parent_route_id
            ):
                raise ValueError("scalar and multi-parent lineage fields disagree")
        elif self.parent_route_id is not None:
            parent_ids = (self.parent_route_id,)
        if any(not isinstance(parent, str) or not parent for parent in parent_ids):
            raise ValueError("lineage parent IDs must be nonblank strings")
        if len(parent_ids) != len(set(parent_ids)):
            raise ValueError("lineage parent IDs must be unique")
        object.__setattr__(self, "parent_route_ids", parent_ids)
        object.__setattr__(
            self,
            "parent_route_id",
            parent_ids[0] if len(parent_ids) == 1 else None,
        )


def _parse_parent_reference(raw: str) -> str:
    value = raw.strip()
    if not value:
        raise ValueError("Supersedes route requires a nonblank parent")
    has_open_tick = value.startswith("`")
    has_close_tick = value.endswith("`")
    if has_open_tick or has_close_tick:
        if not (has_open_tick and has_close_tick and value.count("`") == 2):
            raise ValueError("Supersedes route has malformed backticks")
        value = value[1:-1].strip()
    if (
        not value
        or "`" in value
        or "," in value
        or any(char.isspace() for char in value)
    ):
        raise ValueError("Supersedes route requires one unambiguous parent")
    route_path = Path(value)
    if route_path.is_absolute() or any(part in {".", ".."} for part in route_path.parts):
        raise ValueError("Supersedes route parent must be a relative route reference")
    parent_id = route_id_of(value)
    if not parent_id:
        raise ValueError("Supersedes route requires a nonblank parent")
    return parent_id


def _single_header_value(
    body: str,
    *,
    field_re: re.Pattern[str],
    shaped_re: re.Pattern[str],
    label: str,
) -> str | None:
    values: list[str] = []
    for line in body.splitlines():
        if not shaped_re.match(line):
            continue
        match = field_re.fullmatch(line)
        if match is None:
            raise ValueError(f"malformed {label} field")
        value = match.group("value").strip()
        if not value:
            raise ValueError(f"{label} requires a nonblank value")
        values.append(value)
    if len(values) > 1:
        raise ValueError(f"route requires exactly one {label} field")
    return values[0] if values else None


def parse_lineage(body: str) -> RouteLineage:
    generation_text = _single_header_value(
        body,
        field_re=_GENERATION_FIELD_RE,
        shaped_re=_GENERATION_SHAPED_RE,
        label="Route generation",
    )
    if generation_text is not None and (
        not generation_text.isascii() or not generation_text.isdecimal()
    ):
        raise ValueError("Route generation must be a nonnegative decimal integer")

    canonical_parents: list[str] = []
    active_parents: list[str] = []
    for line in body.splitlines():
        if not _SUPERSEDES_SHAPED_RE.match(line):
            continue
        match = _SUPERSEDES_FIELD_RE.fullmatch(line)
        if match is None:
            raise ValueError("malformed Supersedes route field")
        parent_id = _parse_parent_reference(match.group("value"))
        if match.group("active"):
            active_parents.append(parent_id)
        else:
            canonical_parents.append(parent_id)
    if canonical_parents and active_parents:
        raise ValueError("cannot mix Supersedes route and Supersedes active route")
    if len(active_parents) > 1:
        raise ValueError("Supersedes active route permits only one parent")
    parent_ids = tuple(canonical_parents or active_parents)
    if len(parent_ids) != len(set(parent_ids)):
        raise ValueError("Supersedes route parents must be unique")

    control_head_text = _single_header_value(
        body,
        field_re=_CONTROL_HEAD_FIELD_RE,
        shaped_re=_CONTROL_HEAD_SHAPED_RE,
        label="Expected control HEAD",
    )
    if control_head_text is not None:
        has_open_tick = control_head_text.startswith("`")
        has_close_tick = control_head_text.endswith("`")
        if has_open_tick or has_close_tick:
            if not (
                has_open_tick
                and has_close_tick
                and control_head_text.count("`") == 2
            ):
                raise ValueError("Expected control HEAD has malformed backticks")
            control_head_text = control_head_text[1:-1].strip()
        if not re.fullmatch(r"[0-9a-fA-F]{7,40}", control_head_text):
            raise ValueError("Expected control HEAD requires a hexadecimal commit prefix")
    return RouteLineage(
        generation=int(generation_text) if generation_text is not None else None,
        parent_route_id=parent_ids[0] if len(parent_ids) == 1 else None,
        expected_control_head=(
            control_head_text.lower() if control_head_text is not None else None
        ),
        parent_route_ids=parent_ids,
    )


@dataclass(frozen=True)
class LineageRoute:
    # The first two fields retain the constructor used by ADR-015 callers.
    route_id: str
    lineage: RouteLineage
    task_id: str | None = None
    route_ref: str | None = None
    parent_ref: str | None = None
    revision: int | None = None
    previous_owners: tuple[str, ...] = ()
    owners: tuple[str, ...] = ()
    acceptance_refs: tuple[str, ...] = ()
    finding_refs: tuple[str, ...] = ()
    proposal_ref: str | None = None
    outcome: str | None = None
    path: Path | None = None
    effective: bool = True
    legacy: bool = True
    issues: tuple[str, ...] = field(default_factory=tuple)
    body: str | None = None


@dataclass(frozen=True)
class Resolution:
    winner: str | None
    mode: str  # "autonomous" | "lineage" | "legacy" | "empty"
    issues: tuple[str, ...] = field(default_factory=tuple)
    authoritative: LineageRoute | None = None


@dataclass(frozen=True)
class RouteCandidateIssue:
    message: str
    task_id: str | None
    legacy: bool = False


@dataclass(frozen=True)
class LineageState:
    """Derived generated-route graph state used by resolution and admission."""

    generated_routes: tuple[LineageRoute, ...]
    tips: tuple[LineageRoute, ...]
    structural_issues: tuple[str, ...]


def inspect_lineage(routes: list[LineageRoute]) -> LineageState:
    """Inspect every generated legacy edge without choosing a fork winner."""

    generated_routes = tuple(
        route for route in routes if route.lineage.generation is not None
    )
    if not generated_routes:
        return LineageState((), (), ())

    known_by_id = {route.route_id: route for route in routes}
    generated_by_id = {route.route_id: route for route in generated_routes}
    superseded = {
        parent_id
        for route in generated_routes
        for parent_id in route.lineage.parent_route_ids
    }
    tips = tuple(
        sorted(
            (
                route
                for route in generated_routes
                if route.route_id not in superseded
            ),
            key=lambda route: route.route_id,
        )
    )
    issues: list[str] = []

    dangling = sorted(
        {
            (route.route_id, parent_id)
            for route in generated_routes
            for parent_id in route.lineage.parent_route_ids
            if parent_id not in known_by_id
        }
    )
    issues.extend(
        f"dangling parent: {route_id} supersedes unknown {parent_id}"
        for route_id, parent_id in dangling
    )

    for route in sorted(generated_routes, key=lambda item: item.route_id):
        assert route.lineage.generation is not None
        for parent_id in route.lineage.parent_route_ids:
            parent = generated_by_id.get(parent_id)
            if (
                parent is not None
                and parent.lineage.generation is not None
                and route.lineage.generation <= parent.lineage.generation
            ):
                issues.append(
                    f"non-increasing generation: {route.route_id} generation "
                    f"{route.lineage.generation} must exceed parent {parent_id} "
                    f"generation {parent.lineage.generation}"
                )

    visit_state: dict[str, int] = {}
    active: list[str] = []
    cycles: set[tuple[str, ...]] = set()

    def visit(route_id: str) -> None:
        state = visit_state.get(route_id, 0)
        if state == 1:
            start = active.index(route_id)
            cycles.add(tuple(sorted(set(active[start:]))))
            return
        if state == 2:
            return
        visit_state[route_id] = 1
        active.append(route_id)
        route = generated_by_id[route_id]
        for parent_id in sorted(route.lineage.parent_route_ids):
            if parent_id in generated_by_id:
                visit(parent_id)
        active.pop()
        visit_state[route_id] = 2

    for route_id in sorted(generated_by_id):
        visit(route_id)
    issues.extend(
        "cyclic lineage: " + ", ".join(cycle) for cycle in sorted(cycles)
    )
    return LineageState(
        generated_routes=generated_routes,
        tips=tips,
        structural_issues=tuple(dict.fromkeys(issues)),
    )


def resolve_authoritative(routes: list[LineageRoute]) -> Resolution:
    """Resolve ADR-015 generations, returning no winner on any conflict."""

    if not routes:
        return Resolution(winner=None, mode="empty")
    state = inspect_lineage(routes)
    if not state.generated_routes:
        return Resolution(winner=None, mode="legacy")

    tips = list(state.tips)
    issues = list(state.structural_issues)
    if not tips:
        issues.append("lineage has no tip (cycle or every generation superseded)")
    elif len(tips) > 1:
        issues.append(
            "forked lineage: multiple unsuperseded tips: "
            + ", ".join(sorted(route.route_id for route in tips))
        )
        generations = {route.lineage.generation for route in tips}
        for generation in sorted(value for value in generations if value is not None):
            same_generation = [
                route.route_id
                for route in tips
                if route.lineage.generation == generation
            ]
            if len(same_generation) > 1:
                issues.append(
                    f"forked lineage: multiple tips at generation {generation}: "
                    + ", ".join(sorted(same_generation))
                )
    if issues:
        return Resolution(winner=None, mode="lineage", issues=tuple(issues))
    assert len(tips) == 1
    return Resolution(
        winner=tips[0].route_id,
        mode="lineage",
        authoritative=tips[0],
    )


def _single_field(body: str, label: str) -> str:
    prefix = f"{label}:"
    values = [
        line[len(prefix) :].strip()
        for line in body.splitlines()
        if line.startswith(prefix)
    ]
    if len(values) != 1 or not values[0]:
        raise ValueError(f"route requires exactly one nonblank {label!r} field")
    return values[0].strip("`")


def _optional_none(value: str) -> str | None:
    return None if value.casefold() in _NONE_VALUES else value


def _seats(value: str, *, allow_none: bool) -> tuple[str, ...]:
    if value.casefold() in _NONE_VALUES:
        if allow_none:
            return ()
        raise ValueError("Owners cannot be empty")
    seats = tuple(part.strip() for part in value.split(","))
    if (
        not seats
        or len(seats) != len(set(seats))
        or any(seat not in protocol_mailbox.RECEIVING_SEATS for seat in seats)
    ):
        raise ValueError("owner fields require unique known seats")
    return seats


def _refs(value: str, *, allow_self: bool) -> tuple[str, ...]:
    if value.casefold() in _NONE_VALUES:
        return ()
    values = tuple(part.strip() for part in value.split(","))
    if not values or len(values) != len(set(values)):
        raise ValueError("reference lists must be nonempty and unique")
    for item in values:
        if item == "self-candidate" and allow_self:
            continue
        if not protocol_mailbox.immutable_reference_is_canonical(item):
            raise ValueError("route references require full immutable refs")
    return values


def task_board_of(body: str) -> str | None:
    matches = re.findall(r"^\s*Task-board:\s*`?([^`\n]+?)`?\s*$", body, re.MULTILINE)
    if len(matches) != 1:
        return None
    task_id = matches[0].strip()
    if task_id.casefold().startswith("none"):
        return None
    return task_id


def is_route_event(path: Path, body: str) -> bool:
    """Recognize legacy Task-board broadcasts and complete autonomous routes."""

    match = _ROUTE_NAME_RE.fullmatch(path.name)
    if match is None:
        return False
    sender = match.group("sender")
    kind = match.group("kind")
    if sender in {"coordinator", "coordinator2"}:
        if kind not in {"coordination", "status", "decision"} or task_board_of(body) is None:
            return False
        try:
            parse_lineage(body)
        except ValueError:
            return False
        return True
    if sender not in protocol_mailbox.SEATS or kind != "coordination":
        return False
    try:
        validate_route_candidate_structure(path, body)
    except ValueError:
        return False
    return True


def validate_route_candidate_structure(path: Path, body: str) -> LineageRoute:
    """Validate staged autonomous bytes without granting route effectiveness."""

    match = _ROUTE_NAME_RE.fullmatch(path.name)
    if match is None or match.group("sender") not in protocol_mailbox.SEATS or match.group("kind") != "coordination":
        raise ValueError("autonomous routes require a pair-seat to-all coordination filename")
    values = {label: _single_field(body, label) for label in _AUTONOMOUS_FIELDS}
    revision_text = values["Contract revision"]
    if not revision_text.isascii() or not revision_text.isdecimal():
        raise ValueError("contract revision must be a nonnegative decimal integer")
    parent_ref = _optional_none(values["Parent contract"])
    if parent_ref is not None and not protocol_mailbox.immutable_reference_is_canonical(parent_ref):
        raise ValueError("parent contract requires a full immutable ref")
    proposal_ref = _optional_none(values["Proposal ref"])
    if proposal_ref not in {None, "self-candidate"} and not protocol_mailbox.immutable_reference_is_canonical(proposal_ref):
        raise ValueError("proposal ref requires a full immutable ref")
    return LineageRoute(
        route_id=route_id_of(path.name),
        lineage=RouteLineage(None, None, None),
        task_id=values["Task ID"],
        parent_ref=parent_ref,
        revision=int(revision_text),
        previous_owners=_seats(values["Previous owners"], allow_none=True),
        owners=_seats(values["Owners"], allow_none=False),
        acceptance_refs=_refs(values["Acceptance refs"], allow_self=True),
        finding_refs=_refs(values["Finding refs"], allow_self=False),
        proposal_ref=proposal_ref,
        outcome=values["Outcome contract"],
        path=path,
        effective=False,
        legacy=False,
        body=body,
    )


def _git_output(root: Path, *args: str) -> str:
    env = {key: value for key, value in os.environ.items() if not key.startswith("GIT_")}
    env.update({"LANG": "C", "LC_ALL": "C"})
    result = subprocess.run(
        ["git", "--no-replace-objects", "-C", str(root), *args],
        text=True,
        encoding="utf-8",
        capture_output=True,
        check=True,
        env=env,
    )
    return result.stdout


def _git(root: Path, *args: str) -> str:
    return _git_output(root, *args).strip()


def _is_git_repo(root: Path) -> bool:
    try:
        return _git(root, "rev-parse", "--is-inside-work-tree") == "true"
    except (OSError, subprocess.CalledProcessError, UnicodeError):
        return False


def current_committed_route_body(root: Path, path: Path) -> str:
    """Return current HEAD's exact route blob, or filesystem bytes outside Git."""

    if _is_git_repo(root):
        relative = path.relative_to(root).as_posix()
        try:
            return _git_output(root, "show", f"HEAD:{relative}")
        except (OSError, subprocess.CalledProcessError, UnicodeError) as exc:
            raise ValueError("route path is absent from the current committed tree") from exc
    return path.read_text(encoding="utf-8")


def worktree_matches_committed_route(root: Path, route: LineageRoute) -> bool:
    """Check that a returned Path still exposes the validated committed bytes."""

    if route.path is None or route.body is None:
        return False
    try:
        return (
            current_committed_route_body(root, route.path) == route.body
            and route.path.read_text(encoding="utf-8") == route.body
        )
    except (OSError, UnicodeError, ValueError):
        return False


def _committed_ref_for_path(root: Path, path: Path) -> str | None:
    try:
        relative = path.relative_to(root).as_posix()
        current_blob = _git(root, "rev-parse", f"HEAD:{relative}")
        commits = _git(
            root, "log", "--full-history", "--format=%H", "--", relative
        ).splitlines()
    except (OSError, ValueError, subprocess.CalledProcessError, UnicodeError):
        return None
    for commit in commits:
        try:
            candidate_blob = _git(root, "rev-parse", f"{commit}:{relative}")
        except (OSError, subprocess.CalledProcessError, UnicodeError):
            continue
        if candidate_blob == current_blob:
            return f"{relative}@{commit}"
    return None


def _legacy_route(
    root: Path,
    path: Path,
    body: str,
    *,
    route_ref: str | None = None,
) -> LineageRoute:
    lineage = parse_lineage(body)
    return LineageRoute(
        route_id=route_id_of(path.name),
        lineage=lineage,
        task_id=task_board_of(body),
        route_ref=route_ref if route_ref is not None else _committed_ref_for_path(root, path),
        revision=lineage.generation,
        path=path,
        effective=True,
        legacy=True,
        body=body,
    )


def _route_from_exact_ref(
    root: Path,
    route_ref: str,
    seen: frozenset[str],
    reader: RouteBatchReader | None = None,
) -> LineageRoute:
    if route_ref in seen:
        raise ValueError("cyclic autonomous parent reference")
    proof_root = reader if reader is not None else root
    event = protocol_mailbox.load_committed_event_ref(proof_root, route_ref)
    path = root / event.path
    if not is_route_event(path, event.text):
        raise ValueError("parent ref is not a route event")
    match = _ROUTE_NAME_RE.fullmatch(path.name)
    assert match is not None
    if match.group("sender") in {"coordinator", "coordinator2"}:
        return _legacy_route(root, path, event.text, route_ref=event.ref)
    return _validate_committed_autonomous(root, event, seen | {route_ref}, reader)


def _validate_committed_autonomous(
    root: Path,
    event: protocol_mailbox.CommittedEventRef,
    seen: frozenset[str],
    reader: RouteBatchReader | None = None,
) -> LineageRoute:
    candidate = validate_route_candidate_structure(root / event.path, event.text)
    candidate = replace(candidate, route_ref=event.ref)
    sender = event.sender
    self_proposal = candidate.proposal_ref == "self-candidate"
    self_acceptance = candidate.acceptance_refs == ("self-candidate",)

    if self_proposal or self_acceptance:
        if not (self_proposal and self_acceptance and candidate.owners == (sender,)):
            raise ValueError("self-candidate is only valid for a seat's own initial contract")
        if candidate.parent_ref is None:
            if candidate.revision != 0 or candidate.previous_owners:
                raise ValueError("initial contract requires revision zero and no previous owners")
        else:
            parent = _route_from_exact_ref(root, candidate.parent_ref, seen, reader)
            if (
                not parent.effective
                or parent.task_id != candidate.task_id
                or candidate.revision != (parent.revision or 0) + 1
                or candidate.previous_owners not in {(sender,), parent.owners}
                or (parent.owners and sender not in parent.owners)
            ):
                raise ValueError("self-claim does not continue the exact incumbent parent")
        codex_protocol_model.claim_outcome(
            task_id=candidate.task_id or "",
            contract_ref=event.ref,
            parent_ref=candidate.parent_ref,
            revision=candidate.revision or 0,
            outcome=candidate.outcome or "",
            owners=candidate.owners,
            evidence_bar=("route evidence",),
            hard_boundaries=("immutable lineage",),
            finding_refs=candidate.finding_refs,
        )
        return replace(candidate, effective=True)

    if candidate.parent_ref is None or candidate.proposal_ref is None:
        raise ValueError("ownership successor requires parent and proposal refs")
    parent = _route_from_exact_ref(root, candidate.parent_ref, seen, reader)
    if not parent.effective or parent.task_id != candidate.task_id or parent.revision is None:
        raise ValueError("ownership successor has an ineffective or mismatched parent")
    contract = codex_protocol_model.claim_outcome(
        task_id=parent.task_id or "",
        contract_ref=parent.route_ref or "",
        parent_ref=parent.parent_ref,
        revision=parent.revision,
        outcome=parent.outcome or candidate.outcome or "",
        owners=parent.owners,
        evidence_bar=("route evidence",),
        hard_boundaries=("immutable lineage",),
        finding_refs=parent.finding_refs,
    )
    proof_root = reader if reader is not None else root
    proposal_event = protocol_mailbox.load_committed_event_ref(proof_root, candidate.proposal_ref)
    if proposal_event.kind == "proposal":
        proposal = protocol_mailbox.load_ownership_proposal_statement(
            proof_root, candidate.proposal_ref
        )
        acceptances = tuple(
            protocol_mailbox.load_ownership_acceptance_statement(proof_root, ref)
            for ref in candidate.acceptance_refs
        )
        change = codex_protocol_model.OwnershipChange(
            task_id=candidate.task_id or "",
            parent_contract_ref=candidate.parent_ref,
            revision=candidate.revision or 0,
            previous_owners=candidate.previous_owners,
            new_owners=candidate.owners,
            proposal=proposal,
            acceptances=acceptances,
            finding_refs=candidate.finding_refs,
            outcome=(candidate.outcome if candidate.outcome != parent.outcome else None),
        )
    elif proposal_event.kind == "dispatch-claim":
        evidence = protocol_mailbox.load_takeover_evidence_statement(
            proof_root, candidate.proposal_ref
        )
        confirmations = tuple(
            protocol_mailbox.load_takeover_confirmation_statement(proof_root, ref)
            for ref in candidate.acceptance_refs
        )
        change = codex_protocol_model.OwnershipChange(
            task_id=candidate.task_id or "",
            parent_contract_ref=candidate.parent_ref,
            revision=candidate.revision or 0,
            previous_owners=candidate.previous_owners,
            new_owners=candidate.owners,
            proposal=None,
            acceptances=(),
            finding_refs=candidate.finding_refs,
            outcome=(candidate.outcome if candidate.outcome != parent.outcome else None),
            abandoned_takeover=True,
            takeover_evidence=evidence,
            takeover_confirmations=confirmations,
        )
    else:
        raise ValueError("proposal ref must name a proposal or takeover claim")
    if sender not in candidate.owners or not codex_protocol_model.ownership_change_is_effective(
        contract, change, root=proof_root
    ):
        raise ValueError("ownership evidence is ineffective")
    return replace(candidate, effective=True)


def _partial_route_task_id(path: Path, body: str) -> str | None:
    match = _ROUTE_NAME_RE.fullmatch(path.name)
    if match is None:
        return None
    label = (
        "Task-board"
        if match.group("sender") in {"coordinator", "coordinator2"}
        else "Task ID"
    )
    prefix = f"{label}:"
    values = [
        line[len(prefix) :].strip().strip(chr(96))
        for line in body.splitlines()
        if line.startswith(prefix)
    ]
    if len(values) != 1 or not values[0]:
        return None
    value = values[0]
    if value.casefold().startswith("none"):
        return None
    return value


class RouteBatchReader(protocol_mailbox._CommittedEventBatchBackend):
    """Read route and ownership proof with a fixed number of Git processes."""

    def __init__(self, root: Path) -> None:
        self.root = Path(root)
        self._entered = False
        self._git_repo = False
        self._cat_process: subprocess.Popen[bytes] | None = None
        self._head_entries: dict[str, tuple[str, str, str]] = {}
        self._history: dict[str, tuple[str, ...]] = {}
        self._cat_cache: dict[str, tuple[str, str, bytes] | None] = {}
        self._tree_cache: dict[str, dict[str, tuple[str, str]]] = {}
        self._candidate_cache: tuple[LineageRoute, ...] | None = None
        self._validated_cache: dict[str, LineageRoute] = {}
        self._issues: list[RouteCandidateIssue] = []

    @staticmethod
    def _clean_env() -> dict[str, str]:
        env = {
            key: value for key, value in os.environ.items() if not key.startswith("GIT_")
        }
        env.update({"LANG": "C", "LC_ALL": "C"})
        return env

    def _run(self, *args: str) -> bytes:
        try:
            return subprocess.run(
                ["git", "--no-replace-objects", "-C", str(self.root), *args],
                capture_output=True,
                check=True,
                env=self._clean_env(),
            ).stdout
        except (OSError, subprocess.CalledProcessError) as exc:
            raise ValueError("batch route Git evidence is not readable") from exc

    def __enter__(self) -> RouteBatchReader:
        if self._entered:
            raise RuntimeError("RouteBatchReader cannot be entered twice")
        self._entered = True
        self._git_repo = (self.root / ".git").exists()
        if not self._git_repo:
            return self
        try:
            self._load_head_entries()
            self._load_history()
            self._cat_process = subprocess.Popen(
                [
                    "git",
                    "--no-replace-objects",
                    "-C",
                    str(self.root),
                    "cat-file",
                    "--batch",
                ],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                env=self._clean_env(),
            )
        except BaseException:
            self.__exit__(None, None, None)
            raise
        return self

    def __exit__(self, exc_type, exc, traceback) -> None:
        process = self._cat_process
        if process is None:
            return
        if process.stdin is not None and not process.stdin.closed:
            try:
                process.stdin.close()
            except OSError:
                pass
        try:
            process.wait(timeout=2)
        except subprocess.TimeoutExpired:
            process.terminate()
            try:
                process.wait(timeout=2)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait(timeout=2)
        if process.stdout is not None:
            process.stdout.close()
        if process.stderr is not None:
            process.stderr.close()

    def _require_entered(self) -> None:
        if not self._entered:
            raise RuntimeError("RouteBatchReader must be used as a context manager")

    def _load_head_entries(self) -> None:
        raw = self._run(
            "ls-tree", "-r", "-z", "HEAD", "--", "coordination/mailbox/sent"
        )
        for entry in raw.split(b"\0"):
            if not entry:
                continue
            try:
                metadata, raw_path = entry.split(b"\t", 1)
                mode, object_type, object_id = metadata.decode("ascii").split(" ", 2)
                path = raw_path.decode("utf-8")
            except (UnicodeError, ValueError) as exc:
                raise ValueError("malformed current mailbox tree entry") from exc
            self._head_entries[path] = (mode, object_type, object_id)

    def _load_history(self) -> None:
        raw = self._run(
            "-c",
            "diff.renames=false",
            "log",
            "--full-history",
            "--format=%x1e%H%x00",
            "--name-only",
            "-z",
            "--",
            "coordination/mailbox/sent",
        )
        history: dict[str, list[str]] = {}
        for record in raw.split(b"\x1e"):
            if not record:
                continue
            fields = record.split(b"\0")
            try:
                commit = fields[0].decode("ascii")
            except UnicodeError as exc:
                raise ValueError("malformed mailbox introduction history") from exc
            if not re.fullmatch(r"[0-9a-f]{40}", commit):
                raise ValueError("malformed mailbox introduction commit")
            for raw_path in fields[1:]:
                raw_path = raw_path.lstrip(b"\n")
                if not raw_path:
                    continue
                try:
                    path = raw_path.decode("utf-8")
                except UnicodeError as exc:
                    raise ValueError("mailbox history path is not UTF-8") from exc
                history.setdefault(path, []).append(commit)
        self._history = {path: tuple(commits) for path, commits in history.items()}

    def _cat(self, expression: str) -> tuple[str, str, bytes] | None:
        self._require_entered()
        if expression in self._cat_cache:
            return self._cat_cache[expression]
        process = self._cat_process
        if process is None or process.stdin is None or process.stdout is None:
            raise ValueError("batch object reader is unavailable")
        try:
            process.stdin.write(expression.encode("utf-8") + b"\n")
            process.stdin.flush()
            header = process.stdout.readline()
            if not header:
                raise ValueError("batch object reader ended unexpectedly")
            parts = header.rstrip(b"\n").split(b" ")
            if parts[-1:] == [b"missing"]:
                self._cat_cache[expression] = None
                return None
            if len(parts) != 3:
                raise ValueError("batch object reader returned malformed metadata")
            object_id = parts[0].decode("ascii")
            object_type = parts[1].decode("ascii")
            size = int(parts[2])
            body = process.stdout.read(size)
            terminator = process.stdout.read(1)
            if len(body) != size or terminator != b"\n":
                raise ValueError("batch object reader returned truncated content")
        except (BrokenPipeError, OSError, UnicodeError, ValueError) as exc:
            if isinstance(exc, ValueError):
                raise
            raise ValueError("batch object reader failed") from exc
        result = (object_id, object_type, body)
        self._cat_cache[expression] = result
        return result

    def _tree_entries(self, tree_id: str) -> dict[str, tuple[str, str]]:
        if tree_id in self._tree_cache:
            return self._tree_cache[tree_id]
        loaded = self._cat(tree_id)
        if loaded is None or loaded[1] != "tree":
            raise ValueError("historical path tree is not readable")
        raw = loaded[2]
        entries: dict[str, tuple[str, str]] = {}
        cursor = 0
        try:
            while cursor < len(raw):
                space = raw.index(b" ", cursor)
                nul = raw.index(b"\0", space + 1)
                mode = raw[cursor:space].decode("ascii")
                name = raw[space + 1 : nul].decode("utf-8")
                object_id = raw[nul + 1 : nul + 21].hex()
                if len(object_id) != 40:
                    raise ValueError
                entries[name] = (mode, object_id)
                cursor = nul + 21
        except (UnicodeError, ValueError) as exc:
            raise ValueError("historical tree object is malformed") from exc
        self._tree_cache[tree_id] = entries
        return entries

    def _commit_tree_and_parents(self, commit: str) -> tuple[str, tuple[str, ...]]:
        loaded = self._cat(commit)
        if loaded is None or loaded[1] != "commit":
            raise ValueError("committed event reference must name a commit object")
        try:
            header = loaded[2].split(b"\n\n", 1)[0].decode("ascii")
        except UnicodeError as exc:
            raise ValueError("commit object headers are malformed") from exc
        tree: str | None = None
        parents: list[str] = []
        for line in header.splitlines():
            if line.startswith("tree "):
                tree = line[5:]
            elif line.startswith("parent "):
                parents.append(line[7:])
        if tree is None or not re.fullmatch(r"[0-9a-f]{40}", tree):
            raise ValueError("commit object has no canonical tree")
        if any(not re.fullmatch(r"[0-9a-f]{40}", parent) for parent in parents):
            raise ValueError("commit object has a malformed parent")
        return tree, tuple(parents)

    def _path_entry(self, commit: str, path: str) -> tuple[str, str, str]:
        tree_id, _parents = self._commit_tree_and_parents(commit)
        parts = path.split("/")
        for index, part in enumerate(parts):
            entry = self._tree_entries(tree_id).get(part)
            if entry is None:
                raise ValueError("event path is absent from the named commit")
            mode, object_id = entry
            if index < len(parts) - 1:
                if mode not in {"40000", "040000"}:
                    raise ValueError("event path crosses a non-tree object")
                tree_id = object_id
                continue
            loaded = self._cat(object_id)
            if loaded is None:
                raise ValueError("event path object is unreadable")
            return mode, loaded[1], object_id
        raise ValueError("event path is absent from the named commit")

    def _protocol_load_committed_event_ref(
        self, value: str
    ) -> protocol_mailbox.CommittedEventRef:
        path, commit, _match = protocol_mailbox._committed_event_parts(value)
        self._commit_tree_and_parents(commit)
        mode, object_type, object_id = self._path_entry(commit, path)
        if mode != "100644" or object_type != "blob":
            raise ValueError("event path is not a regular fixed-writer blob")
        expression = self._cat(f"{commit}:{path}")
        if (
            expression is None
            or expression[0] != object_id
            or expression[1] != "blob"
        ):
            raise ValueError("event commit:path object does not match its exact tree entry")
        try:
            text = expression[2].decode("utf-8")
        except UnicodeError as exc:
            raise ValueError("committed event body is not UTF-8") from exc
        return protocol_mailbox.parse_committed_event_text(value, text)

    def _protocol_committed_event_is_strict_ancestor(
        self,
        earlier: protocol_mailbox.CommittedEventRef,
        later: protocol_mailbox.CommittedEventRef,
    ) -> bool:
        if earlier.commit == later.commit:
            return False
        pending = [later.commit]
        seen: set[str] = set()
        while pending:
            commit = pending.pop()
            if commit in seen:
                continue
            seen.add(commit)
            try:
                _tree, parents = self._commit_tree_and_parents(commit)
            except ValueError:
                return False
            if earlier.commit in parents:
                return True
            pending.extend(parents)
        return False

    def _introduction_ref(self, path: str, current_blob: str) -> str | None:
        for commit in self._history.get(path, ()):
            loaded = self._cat(f"{commit}:{path}")
            if loaded is not None and loaded[0] == current_blob and loaded[1] == "blob":
                return f"{path}@{commit}"
        return None

    @staticmethod
    def _looks_route_shaped(path: Path, body: str) -> bool:
        match = _ROUTE_NAME_RE.fullmatch(path.name)
        if match is None:
            return False
        if match.group("sender") in {"coordinator", "coordinator2"}:
            task_boards = re.findall(
                r"^\s*Task-board:\s*`?([^`\n]+?)`?\s*$", body, re.MULTILINE
            )
            return any(
                not task_board.strip().casefold().startswith("none")
                for task_board in task_boards
            )
        return match.group("kind") == "coordination" and any(
            f"{label}:" in body for label in _AUTONOMOUS_FIELDS
        )

    def _record_issue(self, message: str, *, path: Path, body: str) -> None:
        match = _ROUTE_NAME_RE.fullmatch(path.name)
        self._issues.append(
            RouteCandidateIssue(
                message=message,
                task_id=_partial_route_task_id(path, body),
                legacy=(
                    match is not None
                    and match.group("sender") in {"coordinator", "coordinator2"}
                ),
            )
        )

    def _non_git_candidates(self) -> tuple[LineageRoute, ...]:
        sent = self.root / "coordination" / "mailbox" / "sent"
        if not sent.exists():
            return ()
        routes: list[LineageRoute] = []
        for path in sorted(sent.iterdir()):
            if not path.is_file():
                continue
            try:
                body = path.read_text(encoding="utf-8", errors="replace")
            except OSError:
                continue
            if not is_route_event(path, body):
                if self._looks_route_shaped(path, body):
                    self._record_issue(
                        f"malformed route-shaped event: {path.name}",
                        path=path,
                        body=body,
                    )
                continue
            match = _ROUTE_NAME_RE.fullmatch(path.name)
            assert match is not None
            if match.group("sender") in {"coordinator", "coordinator2"}:
                routes.append(_legacy_route(self.root, path, body))
            else:
                routes.append(validate_route_candidate_structure(path, body))
        return tuple(routes)

    def candidate_routes(self) -> tuple[LineageRoute, ...]:
        self._require_entered()
        if self._candidate_cache is not None:
            return self._candidate_cache
        if not self._git_repo:
            self._candidate_cache = self._non_git_candidates()
            return self._candidate_cache

        exact_bodies: list[tuple[str, Path, str, str, str]] = []
        for relative, (mode, object_type, object_id) in sorted(self._head_entries.items()):
            path = self.root / relative
            if _ROUTE_NAME_RE.fullmatch(path.name) is None:
                continue
            loaded = self._cat(object_id)
            if loaded is None or loaded[1] != "blob" or loaded[0] != object_id:
                raise ValueError(f"current committed route object is unreadable: {relative}")
            try:
                body = loaded[2].decode("utf-8")
            except UnicodeError as exc:
                raise ValueError(f"current committed route body is not UTF-8: {relative}") from exc
            exact_bodies.append((relative, path, body, object_id, mode))

        routes: list[LineageRoute] = []
        for relative, path, body, object_id, mode in exact_bodies:
            if mode != "100644":
                self._record_issue(
                    f"malformed route-shaped event has non-regular mode: {path.name}",
                    path=path,
                    body=body,
                )
                continue
            if not is_route_event(path, body):
                if self._looks_route_shaped(path, body):
                    self._record_issue(
                        f"malformed route-shaped event: {path.name}",
                        path=path,
                        body=body,
                    )
                continue
            match = _ROUTE_NAME_RE.fullmatch(path.name)
            assert match is not None
            route_ref = self._introduction_ref(relative, object_id)
            if match.group("sender") in {"coordinator", "coordinator2"}:
                routes.append(
                    _legacy_route(
                        self.root, path, body, route_ref=route_ref
                    )
                )
                continue
            candidate = validate_route_candidate_structure(path, body)
            routes.append(replace(candidate, route_ref=route_ref))
        self._candidate_cache = tuple(routes)
        return self._candidate_cache

    def load_route_ref(self, route_ref: str) -> LineageRoute:
        self._require_entered()
        if not self._git_repo:
            raise ValueError("exact committed route refs require a Git repository")
        cached = self._validated_cache.get(route_ref)
        if cached is not None:
            return cached
        event = self._protocol_load_committed_event_ref(route_ref)
        path = self.root / event.path
        if not is_route_event(path, event.text):
            raise ValueError("committed ref is not a route event")
        match = _ROUTE_NAME_RE.fullmatch(path.name)
        assert match is not None
        if match.group("sender") in {"coordinator", "coordinator2"}:
            route = _legacy_route(
                self.root, path, event.text, route_ref=event.ref
            )
        else:
            route = _validate_committed_autonomous(
                self.root, event, frozenset({route_ref}), self
            )
        self._validated_cache[route_ref] = route
        return route

    def _validate_candidates(self, candidates: tuple[LineageRoute, ...]) -> list[LineageRoute]:
        routes: list[LineageRoute] = []
        for candidate in candidates:
            if candidate.legacy:
                routes.append(candidate)
                continue
            if candidate.route_ref is None:
                routes.append(
                    replace(
                        candidate,
                        issues=(
                            "uncommitted autonomous route is structurally valid but ineffective",
                        ),
                    )
                )
                continue
            try:
                validated = self.load_route_ref(candidate.route_ref)
                if validated.body != candidate.body:
                    raise ValueError(
                        "validated event blob differs from current committed tree blob"
                    )
                routes.append(validated)
            except (OSError, ValueError) as exc:
                routes.append(
                    replace(
                        candidate,
                        issues=(f"ineffective autonomous route: {exc}",),
                    )
                )
        return routes

    def load_task_routes(self, task_id: str) -> list[LineageRoute]:
        candidates = tuple(
            route for route in self.candidate_routes() if route.task_id == task_id
        )
        return self._validate_candidates(candidates)

    def load_all_routes(self) -> list[LineageRoute]:
        return self._validate_candidates(self.candidate_routes())

    @property
    def issues(self) -> tuple[str, ...]:
        return tuple(dict.fromkeys(issue.message for issue in self._issues))

    def issues_for_task(self, task_id: str) -> tuple[str, ...]:
        return tuple(
            dict.fromkeys(
                issue.message
                for issue in self._issues
                if issue.task_id in {None, task_id}
            )
        )

    @property
    def legacy_issues(self) -> tuple[str, ...]:
        return tuple(
            dict.fromkeys(issue.message for issue in self._issues if issue.legacy)
        )


def validate_committed_route_effectiveness(root: Path, route_ref: str) -> LineageRoute:
    """Load one exact route blob and validate its immutable ownership claims."""

    event = protocol_mailbox.load_committed_event_ref(root, route_ref)
    path = root / event.path
    match = _ROUTE_NAME_RE.fullmatch(path.name)
    if match is None or match.group("sender") not in protocol_mailbox.SEATS:
        raise ValueError("committed autonomous route must be authored by a pair seat")
    return _validate_committed_autonomous(root, event, frozenset({route_ref}))


def load_route_paths(root: Path) -> list[Path]:
    """Discover all regular legacy or autonomous route events in the mailbox."""

    with RouteBatchReader(root) as reader:
        return sorted(
            route.path for route in reader.candidate_routes() if route.path is not None
        )


def load_routes(root: Path) -> list[LineageRoute]:
    """Load compatible legacy routes and provenance-checked autonomous routes."""

    with RouteBatchReader(root) as reader:
        return reader.load_all_routes()


def _legacy_resolution(routes: list[LineageRoute]) -> Resolution:
    generated = resolve_authoritative(routes)
    if generated.mode == "lineage":
        return generated
    winner = max(routes, key=lambda route: route.route_id)
    return Resolution(
        winner=winner.route_id,
        mode="legacy",
        authoritative=winner,
    )


def _legacy_overlap_closure(
    selected: list[LineageRoute], known: list[LineageRoute]
) -> list[LineageRoute]:
    """Add known ancestors and sibling children along selected parent paths."""

    by_id = {route.route_id: route for route in known}
    children_by_parent: dict[str, list[LineageRoute]] = {}
    for route in known:
        for parent_id in route.lineage.parent_route_ids:
            children_by_parent.setdefault(parent_id, []).append(route)
    closure = list(selected)
    included = {route.route_id for route in closure}
    pending = list(selected)
    traversed: set[str] = set()
    while pending:
        route = pending.pop()
        if route.route_id in traversed:
            continue
        traversed.add(route.route_id)
        for parent_id in route.lineage.parent_route_ids:
            parent = by_id.get(parent_id)
            if parent is None:
                continue
            if parent.route_id not in included:
                closure.append(parent)
                included.add(parent.route_id)
            if parent.route_id not in traversed:
                pending.append(parent)
            for sibling in children_by_parent.get(parent_id, ()):
                if sibling.route_id not in included:
                    closure.append(sibling)
                    included.add(sibling.route_id)
    return closure


def resolve_task_routes(routes: list[LineageRoute], task_id: str) -> Resolution:
    """Resolve one task independently and fail closed on every overlapping fork."""

    matching = [route for route in routes if route.task_id == task_id]
    if not matching:
        return Resolution(winner=None, mode="empty")
    legacy = [route for route in matching if route.legacy]
    autonomous = [route for route in matching if not route.legacy]
    if not autonomous:
        known_legacy = [route for route in routes if route.legacy]
        return _legacy_resolution(_legacy_overlap_closure(legacy, known_legacy))

    issues = sorted({issue for route in autonomous for issue in route.issues})
    if any(not route.effective for route in autonomous):
        issues.append(f"task {task_id}: ineffective autonomous ownership change")
    refs = [route.route_ref for route in autonomous]
    if any(ref is None for ref in refs) or len(refs) != len(set(refs)):
        issues.append(f"task {task_id}: duplicate or missing autonomous route ref")
    if issues:
        return Resolution(winner=None, mode="autonomous", issues=tuple(dict.fromkeys(issues)))

    base: LineageRoute | None = None
    if legacy:
        known_legacy = [route for route in routes if route.legacy]
        base_resolution = _legacy_resolution(
            _legacy_overlap_closure(legacy, known_legacy)
        )
        if base_resolution.issues or base_resolution.authoritative is None:
            return Resolution(
                winner=None,
                mode="autonomous",
                issues=base_resolution.issues or (f"task {task_id}: legacy base is unresolved",),
            )
        base = base_resolution.authoritative
    nodes = ([base] if base is not None else []) + autonomous
    by_ref = {route.route_ref: route for route in nodes if route.route_ref is not None}
    all_matching_refs = {
        route.route_ref for route in matching if route.route_ref is not None
    }
    superseded: set[str] = set()
    for route in autonomous:
        if route.parent_ref is None:
            if base is not None or route.revision != 0:
                issues.append(f"task {task_id}: autonomous root has stale or missing parent")
            continue
        parent = by_ref.get(route.parent_ref)
        if parent is None:
            issue = "stale parent" if route.parent_ref in all_matching_refs else "dangling parent"
            issues.append(f"task {task_id}: {issue} {route.parent_ref}")
            continue
        if route.revision != (parent.revision or 0) + 1:
            issues.append(
                f"task {task_id}: non-monotonic revision {route.revision} after {parent.revision}"
            )
        superseded.add(route.parent_ref)

    tips = [
        route
        for route in nodes
        if route.route_ref is not None and route.route_ref not in superseded
    ]
    if len(tips) != 1:
        issues.append(
            f"task {task_id}: forked lineage has {len(tips)} conflicting tips: "
            + ", ".join(sorted(route.route_id for route in tips))
        )
    if issues:
        return Resolution(winner=None, mode="autonomous", issues=tuple(dict.fromkeys(issues)))
    winner = tips[0]
    return Resolution(
        winner=winner.route_id,
        mode="autonomous",
        authoritative=winner,
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Validate route lineage consistency (read-only).",
    )
    parser.add_argument("--root", default=str(_REPO_ROOT))
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    with RouteBatchReader(Path(args.root)) as reader:
        routes = reader.load_all_routes()
        # The global CLI resolves the legacy coordinator graph. Autonomous
        # candidate faults remain task-scoped, so unrelated historical seat
        # artifacts cannot prevent a lawful legacy reconciliation.
        issues = list(reader.legacy_issues)
    legacy = [route for route in routes if route.legacy]
    if legacy:
        legacy_resolution = resolve_authoritative(legacy)
        issues.extend(legacy_resolution.issues)
    task_ids = sorted({route.task_id for route in routes if route.task_id is not None})
    for task_id in task_ids:
        if any(not route.legacy and route.task_id == task_id for route in routes):
            resolution = resolve_task_routes(routes, task_id)
            issues.extend(resolution.issues)
    if issues:
        print("ROUTE LINEAGE — conflicts")
        for issue in issues:
            print(f"- {issue}")
        return 1
    if not routes:
        print("ROUTE LINEAGE — no routes found.")
    elif all(route.legacy for route in routes):
        print("ROUTE LINEAGE — legacy route set (no autonomous conflicts).")
    else:
        print("ROUTE LINEAGE — autonomous routes valid.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
