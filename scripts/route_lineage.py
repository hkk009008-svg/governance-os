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
