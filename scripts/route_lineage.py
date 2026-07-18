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

_GENERATION_RE = re.compile(
    r"^\s*Route generation:\s*(?P<value>\d+)\s*$", re.IGNORECASE | re.MULTILINE
)
_SUPERSEDES_RE = re.compile(
    r"^\s*Supersedes(?: active)? route:\s*`?(?P<value>[^`\n]+?)`?\s*$",
    re.IGNORECASE | re.MULTILINE,
)
_CONTROL_HEAD_RE = re.compile(
    r"^\s*(?:Expected control HEAD|Control HEAD):\s*`?(?P<value>[0-9a-fA-F]{7,40})`?\s*$",
    re.MULTILINE,
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


def parse_lineage(body: str) -> RouteLineage:
    gen_match = _GENERATION_RE.search(body)
    sup_match = _SUPERSEDES_RE.search(body)
    head_match = _CONTROL_HEAD_RE.search(body)
    return RouteLineage(
        generation=int(gen_match.group("value")) if gen_match else None,
        parent_route_id=route_id_of(sup_match.group("value")) if sup_match else None,
        expected_control_head=head_match.group("value").lower() if head_match else None,
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


@dataclass(frozen=True)
class Resolution:
    winner: str | None
    mode: str  # "autonomous" | "lineage" | "legacy" | "empty"
    issues: tuple[str, ...] = field(default_factory=tuple)
    authoritative: LineageRoute | None = None


def resolve_authoritative(routes: list[LineageRoute]) -> Resolution:
    """Resolve ADR-015 generations, returning no winner on any conflict."""

    if not routes:
        return Resolution(winner=None, mode="empty")
    gen_routes = [route for route in routes if route.lineage.generation is not None]
    if not gen_routes:
        return Resolution(winner=None, mode="legacy")

    known_ids = {route.route_id for route in routes}
    superseded = {
        route.lineage.parent_route_id
        for route in gen_routes
        if route.lineage.parent_route_id is not None
    }
    tips = [route for route in gen_routes if route.route_id not in superseded]
    issues: list[str] = []
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

    dangling = sorted(
        {
            (route.route_id, route.lineage.parent_route_id)
            for route in gen_routes
            if route.lineage.parent_route_id is not None
            and route.lineage.parent_route_id not in known_ids
        }
    )
    issues.extend(
        f"dangling parent: {route_id} supersedes unknown {parent_id}"
        for route_id, parent_id in dangling
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


def _task_board(body: str) -> str | None:
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
        return kind in {"coordination", "status", "decision"} and _task_board(body) is not None
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
    )


def _git(root: Path, *args: str) -> str:
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
    return result.stdout.strip()


def _committed_ref_for_path(root: Path, path: Path) -> str | None:
    try:
        relative = path.relative_to(root).as_posix()
        commits = _git(root, "log", "--diff-filter=A", "--format=%H", "--", relative).splitlines()
    except (OSError, ValueError, subprocess.CalledProcessError, UnicodeError):
        return None
    if not commits:
        return None
    return f"{relative}@{commits[-1]}"


def _legacy_route(root: Path, path: Path, body: str) -> LineageRoute:
    lineage = parse_lineage(body)
    return LineageRoute(
        route_id=route_id_of(path.name),
        lineage=lineage,
        task_id=_task_board(body),
        route_ref=_committed_ref_for_path(root, path),
        revision=lineage.generation,
        path=path,
        effective=True,
        legacy=True,
    )


def _route_from_exact_ref(root: Path, route_ref: str, seen: frozenset[str]) -> LineageRoute:
    if route_ref in seen:
        raise ValueError("cyclic autonomous parent reference")
    event = protocol_mailbox.load_committed_event_ref(root, route_ref)
    path = root / event.path
    if not is_route_event(path, event.text):
        raise ValueError("parent ref is not a route event")
    match = _ROUTE_NAME_RE.fullmatch(path.name)
    assert match is not None
    if match.group("sender") in {"coordinator", "coordinator2"}:
        return _legacy_route(root, path, event.text)
    return _validate_committed_autonomous(root, event, seen | {route_ref})


def _validate_committed_autonomous(
    root: Path,
    event: protocol_mailbox.CommittedEventRef,
    seen: frozenset[str],
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
            parent = _route_from_exact_ref(root, candidate.parent_ref, seen)
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
    parent = _route_from_exact_ref(root, candidate.parent_ref, seen)
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
    proposal_event = protocol_mailbox.load_committed_event_ref(root, candidate.proposal_ref)
    if proposal_event.kind == "proposal":
        proposal = protocol_mailbox.load_ownership_proposal_statement(root, candidate.proposal_ref)
        acceptances = tuple(
            protocol_mailbox.load_ownership_acceptance_statement(root, ref)
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
        evidence = protocol_mailbox.load_takeover_evidence_statement(root, candidate.proposal_ref)
        confirmations = tuple(
            protocol_mailbox.load_takeover_confirmation_statement(root, ref)
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
            abandoned_takeover=True,
            takeover_evidence=evidence,
            takeover_confirmations=confirmations,
        )
    else:
        raise ValueError("proposal ref must name a proposal or takeover claim")
    if sender not in candidate.owners or not codex_protocol_model.ownership_change_is_effective(
        contract, change, root=root
    ):
        raise ValueError("ownership evidence is ineffective")
    return replace(candidate, effective=True)


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

    sent = root / "coordination" / "mailbox" / "sent"
    if not sent.exists():
        return []
    paths: list[Path] = []
    for path in sorted(sent.iterdir()):
        if not path.is_file():
            continue
        try:
            body = path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        if is_route_event(path, body):
            paths.append(path)
    return paths


def load_routes(root: Path) -> list[LineageRoute]:
    """Load compatible legacy routes and provenance-checked autonomous routes."""

    routes: list[LineageRoute] = []
    for path in load_route_paths(root):
        body = path.read_text(encoding="utf-8", errors="replace")
        match = _ROUTE_NAME_RE.fullmatch(path.name)
        assert match is not None
        if match.group("sender") in {"coordinator", "coordinator2"}:
            routes.append(_legacy_route(root, path, body))
            continue
        candidate = validate_route_candidate_structure(path, body)
        route_ref = _committed_ref_for_path(root, path)
        if route_ref is None:
            routes.append(
                replace(
                    candidate,
                    issues=("uncommitted autonomous route is structurally valid but ineffective",),
                )
            )
            continue
        try:
            routes.append(validate_committed_route_effectiveness(root, route_ref))
        except (OSError, ValueError) as exc:
            routes.append(
                replace(
                    candidate,
                    route_ref=route_ref,
                    issues=(f"ineffective autonomous route: {exc}",),
                )
            )
    return routes


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


def resolve_task_routes(routes: list[LineageRoute], task_id: str) -> Resolution:
    """Resolve one task independently and fail closed on every overlapping fork."""

    matching = [route for route in routes if route.task_id == task_id]
    if not matching:
        return Resolution(winner=None, mode="empty")
    legacy = [route for route in matching if route.legacy]
    autonomous = [route for route in matching if not route.legacy]
    if not autonomous:
        return _legacy_resolution(legacy)

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
        base_resolution = _legacy_resolution(legacy)
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
    routes = load_routes(Path(args.root))
    issues: list[str] = []
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
