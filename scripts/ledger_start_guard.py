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


_ROUTE_BASE_RE = re.compile(
    r"^\s*(?:Route base|Target base|Base commit):\s*`?(?P<value>[^`\n]+)`?\s*$",
    re.IGNORECASE | re.MULTILINE,
)
_ROUTE_WORKTREE_RE = re.compile(
    r"^\s*(?:Route worktree|Target worktree|Worktree):\s*`?(?P<value>[^`\n]+)`?\s*$",
    re.IGNORECASE | re.MULTILINE,
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


def find_latest_ledger_route(
    root: Path, target: target_binding.TargetBinding | None = None
) -> Path | None:
    """Return the authoritative coordinator-to-all route for target work.

    Lineage-first (ADR-015): when candidate routes carry a Route generation
    header, return the lineage tip; otherwise fall back to reverse-lex
    filename order (byte-identical to the prior behavior).
    """
    if target is None:
        target = target_binding.resolve_target()
    sent = root / "coordination" / "mailbox" / "sent"
    if not sent.exists():
        return None
    candidates: list[Path] = []
    for path in sorted(sent.glob("*coordinator-to-all*.md"), reverse=True):
        try:
            body = path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        body_lower = body.lower()
        if "Task-board:" in body and (
            any(keyword in body_lower for keyword in target.route_keywords)
            or target.path.as_posix() in body
        ):
            candidates.append(path)
    if not candidates:
        return None
    lineage_routes = [
        route_lineage.LineageRoute(
            route_lineage.route_id_of(path.name),
            route_lineage.parse_lineage(
                path.read_text(encoding="utf-8", errors="replace")
            ),
        )
        for path in candidates
    ]
    resolution = route_lineage.resolve_authoritative(lineage_routes)
    if resolution.mode == "lineage" and resolution.winner is not None:
        for path in candidates:
            if route_lineage.route_id_of(path.name) == resolution.winner:
                return path
    return candidates[0]  # legacy fallback: reverse-lex newest


def route_guidance(route: Path) -> RouteGuidance:
    """Extract optional route base/worktree hints from a coordinator route."""
    try:
        body = route.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return RouteGuidance()
    base_match = _ROUTE_BASE_RE.search(body)
    worktree_match = _ROUTE_WORKTREE_RE.search(body)
    return RouteGuidance(
        base=base_match.group("value").strip() if base_match else None,
        worktree=worktree_match.group("value").strip() if worktree_match else None,
    )


def _seat_status_command(seat: str, wave: int) -> str:
    return (
        "env -u GIT_INDEX_FILE .venv/bin/python "
        f".agents/skills/four-seat-protocol/scripts/seat_status.py {seat} --wave {wave}"
    )


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
    route_ref = _safe_relative(route, kernel)
    guidance = route_guidance(route)
    commands = [
        f"cd {_display(kernel)}",
        (
            "env -u GIT_INDEX_FILE .venv/bin/python "
            f"scripts/ledger_start_guard.py --seat {seat} --wave {wave}"
        ),
        _seat_status_command(seat, wave),
        "env -u GIT_INDEX_FILE git log --oneline -5",
        "env -u GIT_INDEX_FILE git status --short",
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

    route = find_latest_ledger_route(root, target)
    if route is None:
        errors.append(
            "No active ledger coordinator route found under "
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

    assert route is not None
    route_ref = _safe_relative(route, root)
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
    lines.extend(
        f"- {command}" for command in first_commands(seat, wave, kernel, route, target)
    )
    return GuardResult(ok=True, lines=tuple(lines), errors=())


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
    result = build_guard(
        seat=args.seat,
        root=Path(args.root),
        kernel=Path(args.kernel),
        wave=args.wave,
        target_name=args.target,
        binding_root=Path(args.binding_root) if args.binding_root else None,
    )
    print("\n".join(result.lines))
    if result.errors:
        print("Errors:")
        for error in result.errors:
            print(f"- {error}")
    return 0 if result.ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
