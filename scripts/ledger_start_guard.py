#!/usr/bin/env python3
"""Enforce Pipeline-first startup for Codex seats working on evidence-ledger."""

from __future__ import annotations

import argparse
import re
from dataclasses import dataclass
from pathlib import Path

import route_lineage
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
            f"git -C {guidance.worktree} status --short --branch"
        )
        commands.append(
            "normal target checkout may be stale; use the route worktree above"
        )
    else:
        commands.append(
            f"git -C {_display(target.path)} status --short --branch"
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
    args = parser.parse_args(argv)
    common = {
        "seat": args.seat,
        "root": Path(args.root),
        "kernel": Path(args.kernel),
        "wave": args.wave,
        "target_name": args.target,
        "binding_root": Path(args.binding_root) if args.binding_root else None,
    }
    guard = build_guard(**common)
    print("\n".join(guard.lines))
    if guard.errors:
        print("Errors:")
        for error in guard.errors:
            print(f"- {error}")
    return 0 if guard.ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
