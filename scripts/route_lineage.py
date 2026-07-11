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
import sys
from dataclasses import dataclass, field
from pathlib import Path

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
    route_id for determinism), and a same-generation multi-tip fork or a
    tip-less cycle is reported as a structured issue.
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
    top_generation = tips[0].lineage.generation
    top_tips = [r for r in tips if r.lineage.generation == top_generation]
    issues: tuple[str, ...] = ()
    if len(top_tips) > 1:
        issues = (
            f"forked lineage: multiple tips at generation {top_generation}: "
            + ", ".join(sorted(r.route_id for r in top_tips)),
        )
    return Resolution(winner=tips[0].route_id, mode="lineage", issues=issues)


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
    if proposed.lineage.generation != current.lineage.generation + 1:
        return CasResult(
            ok=False,
            reason=(
                f"stale_parent: proposed generation {proposed.lineage.generation} "
                f"is not current {current.lineage.generation} + 1"
            ),
        )
    return CasResult(ok=True)
