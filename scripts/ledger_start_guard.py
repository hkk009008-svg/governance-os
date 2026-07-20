#!/usr/bin/env python3
"""Enforce Pipeline-first startup for Codex seats working on evidence-ledger."""

from __future__ import annotations

import argparse
import os
import re
import subprocess
from dataclasses import dataclass
from enum import Enum
from pathlib import Path

import protocol_mailbox
import route_lineage
import startup_snapshot
import target_binding

# The kernel is wherever this script lives; the target repo and forbidden
# roots come from the governance.toml binding registry (ADR-013), so future
# works register a [targets.<name>] table instead of editing constants here.
PIPELINE_KERNEL = Path(__file__).resolve().parent.parent
VALID_SEATS = ("coordinator", "director", "director2", "operator", "operator2")


@dataclass(frozen=True)
class GuardResult:
    ok: bool
    lines: tuple[str, ...]
    errors: tuple[str, ...]


@dataclass(frozen=True)
class RouteGuidance:
    base: str | None = None
    worktree: str | None = None
    accepted_target_head: str | None = None
    allowed_paths: tuple[str, ...] = ()


class ResumeClassification(str, Enum):
    FAST_RESUME_PASS = "FAST RESUME: PASS"
    FULL_ORIENTATION_REQUIRED = "FULL ORIENTATION REQUIRED"
    START_GUARD_FAIL = "START GUARD: FAIL"


@dataclass(frozen=True)
class ResumeEvidence:
    expected_route_ref: str
    current_route_ref: str | None
    route: route_lineage.LineageRoute | None
    pipeline: startup_snapshot.GitSnapshot
    target: startup_snapshot.GitSnapshot | None
    mailbox: startup_snapshot.MailboxSnapshot
    guidance: RouteGuidance
    reasons: tuple[str, ...]


@dataclass(frozen=True)
class ResumeResult:
    classification: ResumeClassification
    lines: tuple[str, ...]
    reasons: tuple[str, ...]


_ROUTE_BASE_RE = re.compile(
    r"^\s*(?:Route base|Target base|Base commit):\s*`?(?P<value>[^`\n]+)`?\s*$",
    re.IGNORECASE | re.MULTILINE,
)
_ROUTE_WORKTREE_RE = re.compile(
    r"^\s*(?:Route worktree|Target worktree|Worktree):\s*`?(?P<value>[^`\n]+)`?\s*$",
    re.IGNORECASE | re.MULTILINE,
)
_FULL_SHA_RE = re.compile(r"[0-9a-f]{40}")
_ALLOWED_PATH_HEADING_RE = re.compile(
    r"^## (?:Allowed Paths|Target Allowed Paths)\s*$", re.MULTILINE
)


def _display(path: Path) -> str:
    return path.as_posix()


def _safe_relative(path: Path, root: Path) -> str:
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return path.as_posix()


def _resolve(path: Path) -> Path:
    return path.expanduser().resolve(strict=False)


def _route_matches_target(route: route_lineage.LineageRoute, target: target_binding.TargetBinding) -> bool:
    if route.path is None or route.body is None:
        return False
    searchable = ((route.task_id or "").lower(), route.body.lower())
    return any(
        keyword in value for keyword in target.route_keywords for value in searchable
    ) or target.path.as_posix() in route.body


def resolve_latest_ledger_route(
    root: Path,
    target: target_binding.TargetBinding | None = None,
    *,
    reader: route_lineage.RouteBatchReader | None = None,
) -> route_lineage.LineageRoute | None:
    """Return the selected target task's live conflict-free route object."""
    if target is None:
        target = target_binding.resolve_target()
    routes = reader.load_all_routes() if reader is not None else route_lineage.load_routes(root)
    candidates: list[route_lineage.LineageRoute] = []
    for route in routes:
        if _route_matches_target(route, target):
            candidates.append(route)
    if not candidates:
        return None
    if all(route.legacy for route in candidates):
        legacy_resolution = route_lineage.resolve_authoritative(candidates)
        if legacy_resolution.mode == "lineage":
            if legacy_resolution.issues or legacy_resolution.authoritative is None:
                selected_task = max(
                    candidates, key=lambda route: route.route_id,
                ).task_id
                detail = "; ".join(legacy_resolution.issues)
                raise RouteResolutionError(
                    f"Outcome-contract route for task {selected_task!r} is non-actionable: {detail}"
                )
            return _actionable_route(root, legacy_resolution.authoritative, reader=reader)
        return _actionable_route(
            root, max(candidates, key=lambda route: route.route_id), reader=reader,
        )
    selected = max(candidates, key=lambda route: route.route_id)
    if selected.task_id is None:
        return _actionable_route(root, selected, reader=reader)
    resolution = route_lineage.resolve_task_routes(routes, selected.task_id)
    if resolution.issues or resolution.authoritative is None:
        detail = "; ".join(resolution.issues) or "no authoritative route"
        raise RouteResolutionError(
            f"Outcome-contract route for task {selected.task_id!r} is non-actionable: {detail}"
        )
    return _actionable_route(root, resolution.authoritative, reader=reader)


def find_latest_ledger_route(
    root: Path, target: target_binding.TargetBinding | None = None) -> Path | None:
    """Compatibility wrapper returning only the selected route path."""
    route = resolve_latest_ledger_route(root, target)
    return route.path if route is not None else None


def _single_guidance_field(body: str, labels: tuple[str, ...]) -> str | None:
    label_pattern = "|".join(re.escape(label) for label in labels)
    matches = re.findall(
        rf"^\s*(?:{label_pattern}):\s*(?P<value>[^\n]+?)\s*$",
        body,
        re.MULTILINE,
    )
    if len(matches) > 1:
        raise ValueError(f"duplicate route guidance field: {'/'.join(labels)}")
    if not matches:
        return None
    value = matches[0].strip()
    if value.startswith("`") or value.endswith("`"):
        if len(value) < 2 or not (value.startswith("`") and value.endswith("`")):
            raise ValueError(f"malformed route guidance field: {'/'.join(labels)}")
        value = value[1:-1].strip()
    if not value:
        raise ValueError(f"blank route guidance field: {'/'.join(labels)}")
    return value


def build_guard(
    *,
    seat: str,
    root: Path,
    kernel: Path = PIPELINE_KERNEL,
    wave: int = 2,
    target_name: str | None = None,
    binding_root: Path | None = None,
) -> GuardResult:
    """Build a guard result without mutating repo state."""
    root = _resolve(root)
    kernel = _resolve(kernel)

    try:
        target = target_binding.resolve_target(binding_root, name=target_name)
        forbidden = target_binding.forbidden_roots(binding_root)
    except target_binding.BindingError as exc:
        return GuardResult(
            ok=False,
            lines=(
                "Ledger seat start guard: FAIL",
                f"Pipeline kernel: {_display(kernel)}",
            ),
            errors=(str(exc),),
        )

    route: route_lineage.LineageRoute | None
    resolution_errors: list[str] = []
    try:
        route = resolve_latest_ledger_route(root, target)
    except RouteResolutionError as exc:
        route = None
        resolution_errors.append(str(exc))
    if resolution_errors:
        return GuardResult(
            ok=False,
            lines=(
                "Ledger seat start guard: FAIL",
                f"Pipeline kernel: {_display(kernel)}",
                f"Target repo: {_display(target.path)}",
            ),
            errors=tuple(resolution_errors),
        )
    return _build_guard_from_route(
        seat=seat,
        root=root,
        route=route,
        kernel=kernel,
        wave=wave,
        target=target,
        forbidden=forbidden,
    )


def _valid_allowed_path(value: str) -> bool:
    path = Path(value)
    return (
        bool(value)
        and not path.is_absolute()
        and "\\" not in value
        and not any(character in value for character in "*?[]")
        and all(part not in {"", ".", ".."} for part in path.parts)
    )


def parse_route_guidance_body(body: str) -> RouteGuidance:
    """Parse only exact structured scope from one immutable route body."""
    base = _single_guidance_field(body, ("Route base", "Target base", "Base commit"))
    worktree = _single_guidance_field(body, ("Target worktree", "Route worktree"))
    if worktree is not None:
        worktree_path = Path(worktree)
        if not worktree_path.is_absolute():
            raise ValueError("route worktree must be an absolute path")
        if ".." in worktree_path.parts or any(
            character in worktree for character in "*?[]"
        ):
            raise ValueError("route worktree must not contain traversal or wildcards")
    accepted_head = _single_guidance_field(
        body, ("Accepted target HEAD", "Target reviewed head")
    )
    if accepted_head is not None and _FULL_SHA_RE.fullmatch(accepted_head) is None:
        raise ValueError("accepted target HEAD must be a full lowercase SHA")

    headings = list(_ALLOWED_PATH_HEADING_RE.finditer(body))
    if len(headings) > 1:
        raise ValueError("route guidance requires at most one allowed-path heading")
    allowed_paths: list[str] = []
    if headings:
        start = headings[0].end()
        following = body[start:]
        next_heading = re.search(r"^#{1,6}\s+", following, re.MULTILINE)
        section = following[: next_heading.start()] if next_heading else following
        for raw_line in section.splitlines():
            line = raw_line.strip()
            if not line:
                continue
            if not line.startswith("- "):
                raise ValueError("allowed-path section accepts bullet paths only")
            value = line[2:].strip()
            if value.startswith("`") or value.endswith("`"):
                if len(value) < 2 or not (
                    value.startswith("`") and value.endswith("`")
                ):
                    raise ValueError("malformed allowed path")
                value = value[1:-1].strip()
            if not _valid_allowed_path(value):
                raise ValueError(f"unsafe allowed path: {value!r}")
            if value in allowed_paths:
                raise ValueError(f"duplicate allowed path: {value}")
            allowed_paths.append(value)
    return RouteGuidance(
        base=base,
        worktree=worktree,
        accepted_target_head=accepted_head,
        allowed_paths=tuple(allowed_paths),
    )


def route_guidance(route: Path) -> RouteGuidance:
    """Extract optional route base/worktree hints from a coordinator route."""
    body = _validated_route_guidance_body(route)
    try:
        guidance = parse_route_guidance_body(body)
    except ValueError as exc:
        raise RouteResolutionError(f"invalid committed route guidance: {exc}") from exc
    base_match = _ROUTE_BASE_RE.search(body)
    worktree_match = _ROUTE_WORKTREE_RE.search(body)
    return RouteGuidance(
        base=guidance.base
        or (base_match.group("value").strip() if base_match else None),
        worktree=guidance.worktree
        or (worktree_match.group("value").strip() if worktree_match else None),
        accepted_target_head=guidance.accepted_target_head,
        allowed_paths=guidance.allowed_paths,
    )


def _seat_status_command(seat: str, wave: int) -> str:
    return (
        "env -u GIT_INDEX_FILE .venv/bin/python "
        f".agents/skills/four-seat-protocol/scripts/seat_status.py {seat} --wave {wave}"
    )


def _first_commands_from_guidance(
    seat: str,
    wave: int,
    kernel: Path,
    route: Path,
    target: target_binding.TargetBinding,
    guidance: RouteGuidance,
) -> tuple[str, ...]:
    route_ref = _safe_relative(route, kernel)
    commands = [
        f"cd {_display(kernel)}",
        (
            "env -u GIT_INDEX_FILE .venv/bin/python "
            f"scripts/ledger_start_guard.py --seat {seat} --wave {wave}"
        ),
        _seat_status_command(seat, wave),
        f"read Pipeline route body: {route_ref}",
    ]
    if target.name == "evidence-ledger":
        commands.append(
            "read docs/protocol/codex/ledger-cli-adoption.md before entering evidence-ledger"
        )
    if guidance.base:
        commands.append(f"route base: {guidance.base}")
    if guidance.worktree:
        commands.append(f"route worktree: {guidance.worktree}")
        commands.append(
            "env -u GIT_INDEX_FILE git -C "
            f"{guidance.worktree} status --short --branch"
        )
    commands.append(
        "normal target checkout may be stale; do not start product work there "
        "unless the route names it"
    )
    commands.append(
        "env -u GIT_INDEX_FILE git -C "
        f"{_display(target.path)} status --short --branch"
    )
    if seat == "coordinator":
        commands.append(
            "coordinator may reconcile ledger evidence only; no evidence-ledger product fixes"
        )
    return tuple(commands)


def first_commands(
    seat: str,
    wave: int,
    kernel: Path,
    route: Path,
    target: target_binding.TargetBinding | None = None,
) -> tuple[str, ...]:
    """Return the ordered commands/instructions a target-routed seat must start with."""
    if target is None:
        target = target_binding.resolve_target()
    return _first_commands_from_guidance(
        seat,
        wave,
        kernel,
        route,
        target,
        route_guidance(route),
    )


def _base_guard_errors(
    *,
    seat: str,
    root: Path,
    kernel: Path,
    forbidden: tuple[Path, ...],
) -> list[str]:
    errors: list[str] = []
    if seat not in VALID_SEATS:
        errors.append(f"Unknown seat `{seat}`; expected one of {', '.join(VALID_SEATS)}.")
    for forbidden_root in forbidden:
        if root == forbidden_root:
            errors.append(f"Refusing `{_display(forbidden_root)}` for ledger work.")
    if root != kernel:
        errors.append(
            "Ledger seat work must start from Pipeline governance kernel "
            f"`{_display(kernel)}`, not `{_display(root)}`."
        )
    return errors


def _build_guard_from_route(
    *,
    seat: str,
    root: Path,
    route: route_lineage.LineageRoute | None,
    kernel: Path,
    wave: int,
    target: target_binding.TargetBinding,
    forbidden: tuple[Path, ...] = (),
) -> GuardResult:
    """Apply ordinary hard boundaries to one already-resolved route object."""
    errors = _base_guard_errors(
        seat=seat, root=root, kernel=kernel, forbidden=forbidden
    )
    if route is None:
        errors.append(
            "No active ledger outcome-contract route found under "
            "`coordination/mailbox/sent/`."
        )
    if errors:
        return GuardResult(
            ok=False,
            lines=(
                "Ledger seat start guard: FAIL",
                f"Pipeline kernel: {_display(kernel)}",
                f"Target repo: {_display(target.path)}",
            ),
            errors=tuple(errors),
        )

    assert route is not None and route.path is not None
    route_ref = _safe_relative(route.path, root)
    lines = [
        "Ledger seat start guard: PASS",
        f"Pipeline kernel: {_display(kernel)}",
        f"Target: {target.name} ({target.repository})",
        f"Target repo: {_display(target.path)}",
        "Forbidden kernel: "
        + ", ".join(_display(forbidden_root) for forbidden_root in forbidden),
        f"Seat: {seat}",
        f"Wave: {wave}",
        f"Active route: {route_ref}",
        "First commands:",
    ]
    try:
        lines.extend(
            f"- {command}"
            for command in first_commands(seat, wave, kernel, route.path, target)
        )
    except RouteResolutionError as exc:
        return GuardResult(
            ok=False,
            lines=(
                "Ledger seat start guard: FAIL",
                f"Pipeline kernel: {_display(kernel)}",
                f"Target repo: {_display(target.path)}",
            ),
            errors=(str(exc),),
        )
    return GuardResult(ok=True, lines=tuple(lines), errors=())


class RouteResolutionError(RuntimeError):
    """The selected target task has no conflict-free authoritative route."""


def _actionable_route(
    root: Path,
    route: route_lineage.LineageRoute,
    *,
    reader: route_lineage.RouteBatchReader | None,
) -> route_lineage.LineageRoute:
    matches = False
    if reader is None:
        matches = route_lineage.worktree_matches_committed_route(root, route)
    elif route.path is not None and route.body is not None:
        try:
            matches = route.path.read_text(encoding="utf-8") == route.body
        except (OSError, UnicodeError):
            matches = False
    if not matches:
        raise RouteResolutionError(
            f"Outcome-contract route {route.route_id!r} working tree bytes differ "
            "from the validated current committed blob"
        )
    return route


def _validated_route_guidance_body(route: Path) -> str:
    root = route.parents[3]
    body = route_lineage.current_committed_route_body(root, route)
    try:
        worktree_body = route.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        raise RouteResolutionError("outcome-contract route is not readable") from exc
    if worktree_body != body:
        raise RouteResolutionError(
            "outcome-contract route working tree bytes differ from committed blob"
        )
    return body


def _git_environment() -> dict[str, str]:
    env = {
        key: value for key, value in os.environ.items() if not key.startswith("GIT_")
    }
    env.update(
        {
            "LANG": "C",
            "LC_ALL": "C",
            "LANGUAGE": "C",
            "GIT_OPTIONAL_LOCKS": "0",
        }
    )
    return env


def _git_identity(path: Path) -> tuple[Path | None, Path | None, str | None]:
    try:
        completed = subprocess.run(
            ["git", "rev-parse", "--show-toplevel", "--git-common-dir"],
            cwd=path,
            env=_git_environment(),
            capture_output=True,
            text=True,
            timeout=120,
            check=False,
        )
    except Exception as exc:
        return None, None, f"Git identity unavailable: {exc}"
    if completed.returncode != 0:
        detail = (completed.stderr or completed.stdout).strip()
        suffix = f": {detail}" if detail else ""
        return None, None, f"Git identity unavailable: git exited {completed.returncode}{suffix}"
    lines = completed.stdout.splitlines()
    if len(lines) != 2 or not lines[0] or not lines[1]:
        return None, None, "Git identity parse error"
    top = _resolve(Path(lines[0]))
    common_raw = Path(lines[1])
    common = _resolve(common_raw if common_raw.is_absolute() else path / common_raw)
    return top, common, None


def _target_identity_reasons(
    target: target_binding.TargetBinding, worktree: Path
) -> tuple[str, ...]:
    reasons: list[str] = []
    worktree_top, worktree_common, worktree_error = _git_identity(worktree)
    if worktree_error:
        reasons.append(f"target-worktree-unavailable: {worktree_error}")
    elif worktree_top != worktree:
        reasons.append(
            "target-worktree-top-level-mismatch: "
            f"expected {worktree.as_posix()}, got "
            f"{worktree_top.as_posix() if worktree_top else 'unavailable'}"
        )

    registered = _resolve(target.path)
    if registered == worktree:
        registered_top, registered_common, registered_error = (
            worktree_top,
            worktree_common,
            worktree_error,
        )
    else:
        registered_top, registered_common, registered_error = _git_identity(registered)
    if registered_error:
        reasons.append(f"target-binding-unavailable: {registered_error}")
    elif registered_top != registered:
        reasons.append(
            "target-binding-top-level-mismatch: "
            f"expected {registered.as_posix()}, got "
            f"{registered_top.as_posix() if registered_top else 'unavailable'}"
        )
    if (
        worktree_common is not None
        and registered_common is not None
        and worktree_common != registered_common
    ):
        reasons.append(
            "target-binding-common-dir-mismatch: route worktree is not linked to "
            "the registered target repository"
        )
    return tuple(reasons)


def _dirty_path_names(snapshot: startup_snapshot.GitSnapshot) -> tuple[str, ...]:
    values: list[str] = []
    for state in snapshot.dirty_paths:
        values.append(state.path)
        if state.original_path is not None:
            values.append(state.original_path)
    return tuple(dict.fromkeys(values))


def _format_dirty(snapshot: startup_snapshot.GitSnapshot) -> str:
    if not snapshot.dirty_paths:
        return "clean"
    return ", ".join(
        f"{state.status} {state.path}"
        + (f" <- {state.original_path}" if state.original_path else "")
        for state in snapshot.dirty_paths
    )


def _ordinary_actions(
    *,
    seat: str,
    root: Path,
    kernel: Path,
    wave: int,
    target: target_binding.TargetBinding | None,
    route: route_lineage.LineageRoute | None,
    guidance: RouteGuidance | None = None,
) -> tuple[str, ...]:
    if target is not None and route is not None and route.path is not None:
        if guidance is not None:
            return _first_commands_from_guidance(
                seat,
                wave,
                kernel,
                route.path,
                target,
                guidance,
            )
        try:
            return first_commands(seat, wave, kernel, route.path, target)
        except RouteResolutionError:
            pass
    actions = [
        f"cd {_display(kernel)}",
        (
            "env -u GIT_INDEX_FILE .venv/bin/python "
            f"scripts/ledger_start_guard.py --seat {seat} --wave {wave}"
        ),
        _seat_status_command(seat, wave),
    ]
    if route is not None and route.path is not None:
        actions.append(
            f"read Pipeline route body: {_safe_relative(route.path, root)}"
        )
    if target is not None:
        if target.name == "evidence-ledger":
            actions.append(
                "read docs/protocol/codex/ledger-cli-adoption.md before entering evidence-ledger"
            )
        actions.extend(
            (
                "normal target checkout may be stale; do not start product work there "
                "unless the route names it",
                "env -u GIT_INDEX_FILE git -C "
                f"{_display(target.path)} status --short --branch",
            )
        )
    if seat == "coordinator":
        actions.append(
            "coordinator may reconcile ledger evidence only; no evidence-ledger product fixes"
        )
    return tuple(actions)


def _evidence_capsule_lines(
    evidence: ResumeEvidence,
    target_value: target_binding.TargetBinding,
) -> tuple[str, ...]:
    route = evidence.route
    target = evidence.target
    owners = (
        ", ".join(route.owners)
        if route is not None and route.owners
        else "(none)"
    )
    findings = (
        ", ".join(route.finding_refs)
        if route is not None and route.finding_refs
        else "(none)"
    )
    unread = (
        ", ".join(evidence.mailbox.unread_refs)
        if evidence.mailbox.unread_refs
        else "(none)"
    )
    allowed = (
        ", ".join(evidence.guidance.allowed_paths)
        if evidence.guidance.allowed_paths
        else "(none)"
    )
    lines = [
        f"Expected route ref: {evidence.expected_route_ref}",
        f"Current route ref: {evidence.current_route_ref or '(unavailable)'}",
    ]
    if route is not None and route.body is not None:
        lines.extend(("Route body:", route.body))
    else:
        lines.append("Route body: (unavailable)")
    lines.extend(
        (
            f"Task ID: {route.task_id if route and route.task_id else '(unavailable)'}",
            f"Revision: {route.revision if route and route.revision is not None else '(legacy)'}",
            f"Current owners: {owners}",
            f"Immutable finding refs: {findings}",
            f"Routed outcome: {route.outcome if route and route.outcome else '(legacy route body governs)'}",
            f"Pipeline HEAD: {evidence.pipeline.head or '(unavailable)'}",
            f"Pipeline branch: {evidence.pipeline.branch or '(detached)'}",
            f"Pipeline dirty: {_format_dirty(evidence.pipeline)}",
            f"Target name: {target_value.name}",
            f"Target registered repo: {target_value.repository}",
            f"Target worktree: {target.root.as_posix() if target else '(unavailable)'}",
            f"Target HEAD: {target.head if target and target.head else '(unavailable)'}",
            f"Target dirty: {_format_dirty(target) if target else '(unavailable)'}",
            f"Mailbox cursor: {evidence.mailbox.cursor or '(unavailable)'}",
            "Mailbox availability: "
            + (evidence.mailbox.unavailable_reason or "available"),
            f"Unread refs: {unread}",
            f"Route base: {evidence.guidance.base or '(none)'}",
            f"Allowed paths: {allowed}",
        )
    )
    return tuple(lines)


def _full_orientation(
    *,
    seat: str,
    root: Path,
    kernel: Path,
    wave: int,
    target: target_binding.TargetBinding | None,
    route: route_lineage.LineageRoute | None,
    reasons: tuple[str, ...],
    evidence: ResumeEvidence | None = None,
    target_value: target_binding.TargetBinding | None = None,
) -> ResumeResult:
    lines = [
        ResumeClassification.FULL_ORIENTATION_REQUIRED.value,
        f"Seat: {seat}",
        "Reasons:",
    ]
    lines.extend(f"- {reason}" for reason in reasons)
    if evidence is not None and target_value is not None:
        lines.append("Orientation capsule:")
        lines.extend(_evidence_capsule_lines(evidence, target_value))
    lines.append("Ordinary startup actions:")
    lines.extend(
        f"- {action}"
        for action in _ordinary_actions(
            seat=seat,
            root=root,
            kernel=kernel,
            wave=wave,
            target=target,
            route=route,
            guidance=evidence.guidance if evidence is not None else None,
        )
    )
    lines.append("External effects authorized: none by fast resume")
    return ResumeResult(
        ResumeClassification.FULL_ORIENTATION_REQUIRED,
        tuple(lines),
        reasons,
    )


def _start_guard_failure(seat: str, reasons: tuple[str, ...]) -> ResumeResult:
    lines = [
        ResumeClassification.START_GUARD_FAIL.value,
        f"Seat: {seat}",
        "Errors:",
    ]
    lines.extend(f"- {reason}" for reason in reasons)
    lines.append("External effects authorized: none by fast resume")
    return ResumeResult(
        ResumeClassification.START_GUARD_FAIL,
        tuple(lines),
        reasons,
    )


def _fast_capsule(
    *,
    seat: str,
    evidence: ResumeEvidence,
    target_value: target_binding.TargetBinding,
) -> ResumeResult:
    lines = (
        ResumeClassification.FAST_RESUME_PASS.value,
        f"Seat: {seat}",
        *_evidence_capsule_lines(evidence, target_value),
        "External effects authorized: none by fast resume",
    )
    return ResumeResult(ResumeClassification.FAST_RESUME_PASS, lines, ())


def _select_resume_task(
    *,
    root: Path,
    target: target_binding.TargetBinding,
    reader: route_lineage.RouteBatchReader,
    resume_from: str,
) -> tuple[
    route_lineage.LineageRoute | None,
    route_lineage.LineageRoute | None,
    tuple[str, ...],
]:
    reasons: list[str] = []
    if not protocol_mailbox.immutable_reference_is_canonical(resume_from):
        return (
            None,
            None,
            ("expected-route-invalid: expected a canonical path@full-commit reference",),
        )
    try:
        expected = reader.load_route_ref(resume_from)
    except (OSError, ValueError) as exc:
        return None, None, (f"expected-route-unreadable: {exc}",)
    if expected.task_id is None:
        return expected, None, ("expected-task-unavailable: route has no task identity",)
    if not _route_matches_target(expected, target):
        reasons.append(
            "expected-task-target-mismatch: route does not identify the selected target"
        )

    routes = reader.load_task_routes(expected.task_id)
    resolution = route_lineage.resolve_task_routes(routes, expected.task_id)
    reasons.extend(
        f"route-candidate-issue: {issue}"
        for issue in reader.issues_for_task(expected.task_id)
    )
    reasons.extend(f"route-state-changed: {issue}" for issue in resolution.issues)
    current = resolution.authoritative
    if current is None:
        reasons.append(
            f"route-state-changed: task {expected.task_id} has no authoritative route"
        )
    else:
        try:
            current = _actionable_route(root, current, reader=reader)
        except RouteResolutionError as exc:
            reasons.append(f"route-state-changed: {exc}")
        if current.route_ref != resume_from:
            reasons.append(
                f"expected-route-mismatch: expected {resume_from}, "
                f"current {current.route_ref or 'unavailable'}"
            )
        if current.body != expected.body:
            reasons.append(
                "expected-route-body-mismatch: exact route bodies differ"
            )
    return expected, current, tuple(dict.fromkeys(reasons))


def build_resume(
    *,
    seat: str,
    root: Path,
    resume_from: str,
    kernel: Path = PIPELINE_KERNEL,
    wave: int = 2,
    target_name: str | None = None,
    binding_root: Path | None = None,
) -> ResumeResult:
    """Prove one unchanged routed lane or return a read-only orientation fallback."""
    root = _resolve(root)
    kernel = _resolve(kernel)
    try:
        target = target_binding.resolve_target(binding_root, name=target_name)
        forbidden = target_binding.forbidden_roots(binding_root)
    except target_binding.BindingError as exc:
        return _start_guard_failure(seat, (str(exc),))

    hard_errors = _base_guard_errors(
        seat=seat, root=root, kernel=kernel, forbidden=forbidden
    )
    if hard_errors:
        return _start_guard_failure(seat, tuple(hard_errors))

    route: route_lineage.LineageRoute | None = None
    try:
        with route_lineage.RouteBatchReader(root) as reader:
            expected_route, current_route, selection_reasons = _select_resume_task(
                root=root,
                target=target,
                reader=reader,
                resume_from=resume_from,
            )
            route = current_route or expected_route
            reasons = list(selection_reasons)

            if route is not None:
                guard = _build_guard_from_route(
                    seat=seat,
                    root=root,
                    route=route,
                    kernel=kernel,
                    wave=wave,
                    target=target,
                    forbidden=forbidden,
                )
                if not guard.ok:
                    reasons.extend(
                        f"route-guidance-invalid: {error}" for error in guard.errors
                    )

            current_ref = current_route.route_ref if current_route is not None else None

            guidance = RouteGuidance()
            if route is None or route.body is None:
                reasons.append("route-body-unavailable: current route body is unreadable")
            else:
                try:
                    guidance = parse_route_guidance_body(route.body)
                except ValueError as exc:
                    reasons.append(f"route-guidance-invalid: {exc}")

            if route is not None:
                if not route.effective:
                    reasons.append("ownership-ineffective: current route is ineffective")
                if route.legacy:
                    reasons.append(
                        "ownership-ambiguous: legacy route has no immutable owners"
                    )
                elif route.revision is None or not route.owners:
                    reasons.append(
                        "ownership-ambiguous: revision or current owners are missing"
                    )

            if guidance.worktree is None:
                reasons.append(
                    "target-worktree-unpinned: committed route names no worktree"
                )
                worktree = _resolve(target.path)
            else:
                worktree = _resolve(Path(guidance.worktree))
            reasons.extend(_target_identity_reasons(target, worktree))

            pipeline_snapshot = startup_snapshot.collect_git_snapshot(root)
            target_snapshot = startup_snapshot.collect_git_snapshot(worktree)
            mailbox_snapshot = startup_snapshot.collect_mailbox_snapshot(root, seat)

            if pipeline_snapshot.errors:
                reasons.extend(
                    f"pipeline-state-unavailable: {error}"
                    for error in pipeline_snapshot.errors
                )
            if pipeline_snapshot.dirty_paths:
                reasons.append(
                    "pipeline-dirty: "
                    + ", ".join(_dirty_path_names(pipeline_snapshot))
                )
            if target_snapshot.errors:
                reasons.extend(
                    f"target-state-unavailable: {error}"
                    for error in target_snapshot.errors
                )
            if guidance.accepted_target_head is None:
                reasons.append(
                    "target-head-unpinned: committed route names no accepted target HEAD"
                )
            elif target_snapshot.head != guidance.accepted_target_head:
                reasons.append(
                    "target-head-changed: expected "
                    f"{guidance.accepted_target_head}, current "
                    f"{target_snapshot.head or 'unavailable'}"
                )

            dirty_paths = _dirty_path_names(target_snapshot)
            if dirty_paths and not guidance.allowed_paths:
                reasons.append(
                    "target-dirty-unattributed: committed route has no allowed paths"
                )
            elif dirty_paths:
                outside = tuple(
                    path for path in dirty_paths if path not in guidance.allowed_paths
                )
                if outside:
                    reasons.append(
                        "target-dirty-out-of-lane: " + ", ".join(outside)
                    )

            if mailbox_snapshot.unavailable_reason is not None:
                reasons.append(
                    f"mailbox-unavailable: {mailbox_snapshot.unavailable_reason}"
                )
            if mailbox_snapshot.unread_refs:
                reasons.append(
                    "mailbox-unread: " + ", ".join(mailbox_snapshot.unread_refs)
                )

            evidence = ResumeEvidence(
                expected_route_ref=resume_from,
                current_route_ref=current_ref,
                route=route,
                pipeline=pipeline_snapshot,
                target=target_snapshot,
                mailbox=mailbox_snapshot,
                guidance=guidance,
                reasons=tuple(dict.fromkeys(reasons)),
            )
            if evidence.reasons:
                return _full_orientation(
                    seat=seat,
                    root=root,
                    kernel=kernel,
                    wave=wave,
                    target=target,
                    route=route,
                    reasons=evidence.reasons,
                    evidence=evidence,
                    target_value=target,
                )
            return _fast_capsule(
                seat=seat,
                evidence=evidence,
                target_value=target,
            )
    except (OSError, UnicodeError, ValueError) as exc:
        return _full_orientation(
            seat=seat,
            root=root,
            kernel=kernel,
            wave=wave,
            target=target,
            route=route,
            reasons=(f"batch-unavailable: {exc}",),
        )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Validate Pipeline-first startup for a ledger-routed Codex seat.",
    )
    parser.add_argument("--seat", choices=VALID_SEATS, required=True)
    parser.add_argument("--wave", type=int, default=2)
    parser.add_argument(
        "--target",
        default=None,
        help="registered target name from governance.toml (default: [binding].default_target)",
    )
    parser.add_argument("--root", default=".", help=argparse.SUPPRESS)
    parser.add_argument("--kernel", default=str(PIPELINE_KERNEL), help=argparse.SUPPRESS)
    parser.add_argument("--binding-root", default=None, help=argparse.SUPPRESS)
    parser.add_argument(
        "--resume-from",
        default=None,
        metavar="ROUTE_REF",
        help="optional exact path@full-commit expectation for unchanged-lane resume",
    )
    args = parser.parse_args(argv)
    common = {
        "seat": args.seat,
        "root": Path(args.root),
        "kernel": Path(args.kernel),
        "wave": args.wave,
        "target_name": args.target,
        "binding_root": Path(args.binding_root) if args.binding_root else None,
    }
    if args.resume_from is not None:
        resume = build_resume(resume_from=args.resume_from, **common)
        print("\n".join(resume.lines))
        return (
            1
            if resume.classification is ResumeClassification.START_GUARD_FAIL
            else 0
        )

    guard = build_guard(**common)
    print("\n".join(guard.lines))
    if guard.errors:
        print("Errors:")
        for error in guard.errors:
            print(f"- {error}")
    return 0 if guard.ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
