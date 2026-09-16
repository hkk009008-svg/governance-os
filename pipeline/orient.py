#!/usr/bin/env python3
"""One compact, read-only digest for the start of a task.

Replaces re-reading the reference documents at every session start: Git
state, project bindings, transport and per-member focus, the caller's own
resume cursor and handoff note, formal-review state, the most recent formal
artifacts, and the next action. It touches nothing and grants nothing.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


_REPO_ROOT = Path(__file__).resolve().parent.parent

import status  # noqa: E402
from status_team_store import TEAM_MEMBERS  # noqa: E402

RECENT_ARTIFACTS = 3
MAX_HANDOFF_LINES = 8
MAX_PENDING_LINES = 5
MAX_LINES = 40


def recent_artifacts(repo_root: Path, limit: int = RECENT_ARTIFACTS) -> list[dict]:
    """Newest formal artifacts with their subject line; no Git calls."""
    sent = repo_root / "coordination/mailbox/sent"
    items = []
    for path in sorted(sent.glob("*.md"))[-limit:]:
        try:
            with path.open(encoding="utf-8", errors="replace") as handle:
                subject = handle.readline().strip().removeprefix("# ")
        except OSError:
            subject = "(unreadable)"
        items.append({"path": path.name, "subject": subject})
    return items


def collect(repo_root: Path, member: str | None = None) -> dict:
    snapshot = status.collect_orientation_snapshot(repo_root)
    transport = snapshot["team_transport"]
    you = None
    if member is not None:
        notes = transport.get("members", {}).get(member, {})
        you = {
            "member": member,
            "pending": transport.get("pending", {}).get(member),
            **transport.get("resume", {}).get(
                member, {"next_unread_id": None, "resume_cursor": None}
            ),
            "focus": notes.get("focus", ""),
            "handoff": notes.get("handoff", ""),
        }
    return {**snapshot, "you": you, "recent_artifacts": recent_artifacts(repo_root)}


def render(digest: dict) -> str:
    git, desktop = digest["git"], digest["desktop"]
    transport, review = digest["team_transport"], digest["formal_review"]
    lines = [
        f"Pipeline orient {digest['generated_at']}",
        f"Git: {git['sha']} branch={git['branch']} dirty={git['dirty']}",
    ]
    if desktop.get("state") == "unavailable":
        lines.append(f"Configs: unavailable ({desktop.get('detail')})")
    else:
        manifests = desktop.get("manifests", {})
        lines.append("Configs: " + " ".join(
            f"{member}={'ready' if manifests.get(member, {}).get('ready') else 'FAIL'}"
            for member in TEAM_MEMBERS
        ))
    if transport.get("state") == "ready":
        pending = transport.get("pending", {})
        lines.append("Transport: ready pending[" + " ".join(
            f"{member}={pending.get(member, 0)}" for member in TEAM_MEMBERS
        ) + "]")
        for member in TEAM_MEMBERS:
            focus = transport.get("members", {}).get(member, {}).get("focus")
            lines.append(f"  {member} focus: {focus or '-'}")
    else:
        lines.append(f"Transport: {transport.get('state')} ({transport.get('detail', '')})")
    you = digest.get("you")
    if you:
        lines.append(
            f"You: {you['member']} resume_cursor={you.get('resume_cursor')} "
            f"next_unread={you.get('next_unread_id')} pending={you.get('pending')}"
        )
        handoff = (you.get("handoff") or "").splitlines()
        if handoff:
            lines.append(f"  handoff: {handoff[0]}")
            lines.extend(f"           {line}" for line in handoff[1:MAX_HANDOFF_LINES])
            if len(handoff) > MAX_HANDOFF_LINES:
                lines.append(
                    f"           (+{len(handoff) - MAX_HANDOFF_LINES} more lines; see team_status)"
                )
    pending_requests = review.get("pending_requests") or []
    if review.get("blocker"):
        lines.append(f"Formal review: BLOCKED ({review['blocker']})")
    elif pending_requests:
        lines.append(f"Formal review: {len(pending_requests)} pending")
    else:
        lines.append("Formal review: none")
    for request in pending_requests[:MAX_PENDING_LINES]:
        lines.append(
            f"  {request['path']}@{request.get('commit') or 'uncommitted'} "
            f"reviewer={request['reviewer']}"
        )
    if len(pending_requests) > MAX_PENDING_LINES:
        lines.append(f"  (+{len(pending_requests) - MAX_PENDING_LINES} more; see status)")
    gate = review["gate"]
    lines.append(
        f"Mailbox: {gate['status']} ({gate['fatal']} fatal, {gate['advisory']} advisory, "
        f"{gate.get('failed_review', 0)} failed)"
    )
    artifacts = digest.get("recent_artifacts") or []
    lines.append("Recent artifacts:" if artifacts else "Recent artifacts: none")
    lines.extend(f"  {item['path']} — {item['subject']}" for item in artifacts)
    lines.append(f"Next: {review.get('next_action')}")
    assert len(lines) <= MAX_LINES
    return "\n".join(lines) + "\n"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="bin/pipeline orient",
        description="Print one compact read-only digest for the start of a task.",
    )
    parser.add_argument("--member", choices=TEAM_MEMBERS, help="show this member's resume cursor and handoff")
    parser.add_argument("--repo-root", type=Path, default=_REPO_ROOT)
    parser.add_argument("--json", action="store_true", help="emit the digest as JSON")
    args = parser.parse_args(argv)
    digest = collect(args.repo_root.resolve(), args.member)
    if args.json:
        print(json.dumps(digest, sort_keys=True))
    else:
        print(render(digest), end="")
    return 0


if __name__ == "__main__":
    sys.exit(main())
