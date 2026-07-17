#!/usr/bin/env python3
"""Route lineage: generation + parent + compare-and-swap authority (ADR-015).

Route currency stops depending on filename timestamp sort. A route carries a
monotone ``Route generation:`` and a ``Supersedes route:`` parent pointer (both
already emitted by route/v1 render_markdown; the parent form is used by live
coordinator routes). The authoritative route is the lineage TIP: the
highest-generation route that no other route supersedes. A proposed route is
accepted only when its parent is the current tip and its generation is
current+1 (compare-and-swap); otherwise a structured stale_parent result is
returned. Legacy routes without a generation header fall back to the previous
reverse-lexicographic filename resolution, so the live campaign is unaffected.
This does not activate the dormant signed bus (ADR-010).
"""
from __future__ import annotations

import argparse
import re
from dataclasses import dataclass, field
from pathlib import Path
from kernel_activation import _reader_guard

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
    route_id: str
    lineage: RouteLineage


@dataclass(frozen=True)
class Resolution:
    winner: str | None
    mode: str  # "lineage" | "legacy" | "empty"
    issues: tuple[str, ...] = field(default_factory=tuple)


def resolve_authoritative(routes: list[LineageRoute]) -> Resolution:
    """Pick the authoritative route. Lineage-first; caller does legacy fallback.

    Lineage resolution fires only when at least one route carries a
    generation. The tip is a generation-bearing route no other route
    supersedes; the winner is the highest-generation tip (ties broken by
    route_id for determinism). Structured issues are reported for: any case
    of multiple unsuperseded generation-bearing tips (a fork — whether the
    abandoned branch stalled at the same generation or a different one), a
    tip-less cycle (every generation superseded), and any dangling parent
    (a route naming a supersedes parent that is not in the input set).
    """
    if not routes:
        return Resolution(winner=None, mode="empty")
    gen_routes = [r for r in routes if r.lineage.generation is not None]
    if not gen_routes:
        return Resolution(winner=None, mode="legacy")
    superseded = {
        r.lineage.parent_route_id for r in routes if r.lineage.parent_route_id
    }
    tips = [r for r in gen_routes if r.route_id not in superseded]
    if not tips:
        return Resolution(
            winner=None,
            mode="lineage",
            issues=("lineage has no tip (cycle or every generation superseded)",),
        )
    tips.sort(key=lambda r: (r.lineage.generation, r.route_id), reverse=True)
    issues: list[str] = []
    # Any multiple unsuperseded generation-bearing tips is a fork, whether the
    # abandoned branch stalled at the same generation or a different one. The
    # winner stays the highest-generation tip (route_id tiebreak) — deterministic.
    if len(tips) > 1:
        issues.append(
            "forked lineage: multiple unsuperseded tips: "
            + ", ".join(sorted(r.route_id for r in tips))
        )
        top_generation = tips[0].lineage.generation
        top_tips = [r for r in tips if r.lineage.generation == top_generation]
        if len(top_tips) > 1:
            issues.append(
                f"forked lineage: multiple tips at generation {top_generation}: "
                + ", ".join(sorted(r.route_id for r in top_tips))
            )
    # A parent pointer that names no route in the input set is broken/partial
    # lineage. Report it (sorted, deduped); it does not change the winner.
    known_ids = {r.route_id for r in routes}
    dangling = sorted(
        {
            (r.route_id, r.lineage.parent_route_id)
            for r in routes
            if r.lineage.parent_route_id is not None
            and r.lineage.parent_route_id not in known_ids
        }
    )
    issues.extend(
        f"dangling parent: {route_id} supersedes unknown {parent_id}"
        for route_id, parent_id in dangling
    )
    return Resolution(winner=tips[0].route_id, mode="lineage", issues=tuple(issues))


@dataclass(frozen=True)
class CasResult:
    ok: bool
    reason: str = ""


def check_cas(current: LineageRoute, proposed: LineageRoute) -> CasResult:
    """Accept proposed as the next authoritative route only under compare-and-swap.

    parent must equal the current tip AND generation must be current + 1.
    Any mismatch is a structured stale_parent refusal (the writer must rebase).
    """
    if proposed.lineage.parent_route_id != current.route_id:
        return CasResult(
            ok=False,
            reason=(
                f"stale_parent: proposed parent {proposed.lineage.parent_route_id!r} "
                f"is not the current tip {current.route_id!r}"
            ),
        )
    if current.lineage.generation is None or proposed.lineage.generation is None:
        return CasResult(
            ok=False, reason="stale_parent: missing generation on current or proposed"
        )
    # Int-only generations (Rule #13 symmetry with capability_is_current). A bool
    # is an int subclass, so `True == 1 == 0 + 1` would otherwise ride the
    # successor arithmetic below; reject a boolean (or any non-int) generation on
    # either side so a bool can never be accepted as an int generation.
    if not (type(current.lineage.generation) is int and type(proposed.lineage.generation) is int):
        return CasResult(
            ok=False,
            reason="stale_parent: generation must be an integer (a boolean must never ride an int successor)",
        )
    if proposed.lineage.generation != current.lineage.generation + 1:
        return CasResult(
            ok=False,
            reason=(
                f"stale_parent: proposed generation {proposed.lineage.generation} "
                f"is not current {current.lineage.generation} + 1"
            ),
        )
    return CasResult(ok=True)


def load_routes(root: Path) -> list[LineageRoute]:
    """Parse lineage for every coordinator-to-all route under root's mailbox."""
    sent = root / "coordination" / "mailbox" / "sent"
    routes: list[LineageRoute] = []
    if not sent.exists():
        return routes
    for path in sorted(sent.glob("*coordinator-to-all*.md")):
        try:
            body = path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        routes.append(LineageRoute(route_id_of(path.name), parse_lineage(body)))
    return routes


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Validate coordinator route lineage consistency (read-only).",
    )
    parser.add_argument("--root", default=str(_REPO_ROOT))
    parser.add_argument(
        "--check",
        action="store_true",
        help="report the authoritative route and fail on lineage inconsistency (the default and only action)",
    )
    args = parser.parse_args(argv)
    if not _reader_guard(_REPO_ROOT, "route-lineage"):
        return 2

    resolution = resolve_authoritative(load_routes(Path(args.root)))
    if resolution.mode == "legacy":
        print("ROUTE LINEAGE — legacy route set (no generations); resolution by filename.")
        return 0
    if resolution.mode == "empty":
        print("ROUTE LINEAGE — no coordinator routes found.")
        return 0
    print(f"ROUTE LINEAGE — authoritative route: {resolution.winner}")
    for issue in resolution.issues:
        print(f"- {issue}")
    return 1 if resolution.issues else 0


if __name__ == "__main__":
    raise SystemExit(main())
