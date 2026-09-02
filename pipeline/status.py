#!/usr/bin/env python3
"""Read-only desktop-team readiness and current formal-review status."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional


_REPO_ROOT = Path(__file__).resolve().parent.parent

import git_runner  # noqa: E402
from status_desktop import (  # noqa: E402
    collect_desktop_readiness,
    render_orientation_snapshot as _render_desktop_orientation_snapshot,
)
from status_team_store import collect_team_transport  # noqa: E402

def _run_git(repo_root: Path, args: list[str], timeout: int = 5) -> str:
    """Run a git command; return stdout stripped or raise."""
    result = git_runner.run_git(
        repo_root, args, mode="dashboard", text=True, timeout=timeout
    )
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or f"git {args[0]} failed")
    return result.stdout.strip()


def collect_git(repo_root: Path) -> dict:
    """Collect only the Git facts rendered by desktop status."""

    def _get(label: str, args: list[str]):
        try:
            return _run_git(repo_root, args)
        except Exception as e:
            return f"(unavailable: {label}: {e})"

    sha = _get("sha", ["rev-parse", "--short", "HEAD"])
    branch = _get("branch", ["rev-parse", "--abbrev-ref", "HEAD"])

    try:
        status_out = _run_git(repo_root, ["status", "--porcelain"])
        dirty = len([l for l in status_out.splitlines() if l.strip()])
    except Exception as e:
        dirty = f"(unavailable: dirty: {e})"

    return {
        "git_sha": sha,
        "git_branch": branch,
        "git_dirty": dirty,
    }


def _collect_review_state(repo_root: Path) -> dict:
    """Collect current formal-review state independently of routine dialogue."""

    # Local import avoids making the status helper/checker module dependency
    # recursive at import time.
    import check_coordination  # type: ignore

    review_state = check_coordination.inspect_verify_review_state(repo_root)
    requests = list(review_state.pending)
    failed_reviews = list(review_state.failed)
    current = max(requests, key=lambda request: request.path, default=None)
    failed = max(
        failed_reviews, key=lambda review: review.report_path, default=None
    )
    issues = check_coordination.run(
        repo_root / "coordination",
        review_state=review_state,
    )
    fatals = [issue for issue in issues if issue.severity == "FATAL"]
    advisories = [issue for issue in issues if issue.severity == "ADVISORY"]

    blocker = None
    if fatals:
        blocker = f"{fatals[0].kind}: {fatals[0].message}"
    elif current is not None and not current.valid:
        blocker = (
            f"invalid current request for {current.reviewer_member}: "
            f"{current.problem}"
        )
    elif failed is not None:
        blocker = (
            f"failed review for {failed.reviewer_member}: "
            f"{failed.report_path}@{failed.report_commit}"
        )

    if blocker is not None:
        if fatals or (current is not None and not current.valid):
            next_action = "repair the blocker before implementation or review"
        elif failed is not None:
            next_action = (
                f"remediate failed review for {failed.request_path}@"
                f"{failed.request_commit}"
            )
    elif current is not None:
        next_action = (
            f"{current.reviewer_member} reviews the exact committed request"
        )
    else:
        next_action = "continue scoped team work; request formal review when risk requires it"

    current_data = None
    if current is not None:
        current_data = {
            "path": current.path,
            "commit": current.commit,
            "reviewer": current.reviewer_member,
            "valid": current.valid,
            "problem": current.problem,
            "reviewed_base": current.reviewed_base,
            "reviewed_head": current.reviewed_head,
        }
    failed_data = None
    if failed is not None:
        failed_data = {
            "request_path": failed.request_path,
            "request_commit": failed.request_commit,
            "report_path": failed.report_path,
            "report_commit": failed.report_commit,
            "reviewer": failed.reviewer_member,
        }
    gate_status = (
        "FAIL" if fatals or failed_reviews else ("WARN" if advisories else "PASS")
    )
    state = {
        "current_request": current_data,
        "failed_review": failed_data,
        "gate": {
            "status": gate_status,
            "fatal": len(fatals),
            "advisory": len(advisories),
            "failed_review": len(failed_reviews),
        },
        "blocker": blocker,
        "next_action": next_action,
    }
    return state


def collect_orientation_snapshot(repo_root: Path) -> dict:
    """Collect the live desktop-team snapshot."""
    now = datetime.now(tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    git = collect_git(repo_root)
    review = _collect_review_state(repo_root)
    return {
        "generated_at": now,
        "git": {
            "sha": git["git_sha"],
            "branch": git["git_branch"],
            "dirty": git["git_dirty"],
        },
        "desktop": collect_desktop_readiness(repo_root),
        "team_transport": collect_team_transport(repo_root),
        "formal_review": review,
    }


def render_orientation_snapshot(snapshot: dict) -> str:
    """Render the live desktop-team snapshot."""
    return _render_desktop_orientation_snapshot(snapshot)


def main(argv: Optional[list[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        description="Print compact desktop-team readiness and formal-review state.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Emit the desktop-team snapshot as JSON.",
    )
    args = parser.parse_args(argv)
    snapshot = collect_orientation_snapshot(_REPO_ROOT)
    if args.json:
        print(json.dumps(snapshot, sort_keys=True))
    else:
        print(render_orientation_snapshot(snapshot), end="")
    return 0


if __name__ == "__main__":
    sys.exit(main())
