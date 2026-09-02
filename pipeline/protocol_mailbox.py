#!/usr/bin/env python3
"""Shared filename and route grammar for formal-review artifacts."""

from __future__ import annotations

import re
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
APP_MEMBERS = ("codex", "claude", "agy")
FORMAL_REVIEWERS = frozenset({"codex", "claude"})
SENDERS = APP_MEMBERS
RECIPIENTS = (*APP_MEMBERS, "all")
EVENT_STAMP_PATTERN = r"\d{4}-\d{2}-\d{2}T\d{2}-\d{2}-\d{2}Z"
EVENT_NAME_PATTERN = (
    rf"(?P<stamp>{EVENT_STAMP_PATTERN})-"
    rf"(?P<sender>{'|'.join(SENDERS)})-to-"
    rf"(?P<recipient>{'|'.join(RECIPIENTS)})-"
    r"(?P<kind>[a-z0-9-]+)\.md"
)
EVENT_NAME_RE = re.compile(rf"^{EVENT_NAME_PATTERN}$")


def load_known_kinds(root: Path | None = None) -> frozenset[str]:
    path = (root or ROOT) / "coordination/mailbox/kinds.txt"
    return frozenset(
        line.strip()
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip() and not line.lstrip().startswith("#")
    )


KNOWN_KINDS = load_known_kinds()


def formal_review_route_problem(kind: str, sender: str, recipient: str) -> str | None:
    if kind == "verify-request":
        if sender not in APP_MEMBERS:
            return "verify-request author must be codex, claude, or agy"
        if recipient not in FORMAL_REVIEWERS:
            return "verify-request reviewer must be codex or claude"
    elif kind == "verification-report":
        if sender not in FORMAL_REVIEWERS:
            return "verification-report publisher must be codex or claude"
        if recipient not in {*APP_MEMBERS, "all"}:
            return "verification-report recipient must be codex, claude, agy, or all"
    else:
        return f"{kind} is not a formal-review kind"
    return f"{kind} cannot be self-addressed" if sender == recipient else None
