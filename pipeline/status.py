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

import protocol_mailbox  # noqa: E402
import codex_protocol_model  # noqa: E402
import git_commit_projection  # noqa: E402
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


def _review_event_identity(
    path: str,
) -> tuple[str, str, str] | None:
    if Path(path).parent.as_posix() != "coordination/mailbox/sent":
        return None
    match = protocol_mailbox.EVENT_NAME_RE.fullmatch(Path(path).name)
    if match is None:
        return None
    return match.group("sender"), match.group("recipient"), match.group("kind")


def _live_review_state(review_state: object, projection: object) -> object:
    """Keep formal artifacts strictly after current model-policy admission.

    The full review projection remains the historical view.  Desktop status
    uses this narrower slice so an old failure is not promoted into a current
    blocker, while a genuinely new author/reviewer request remains visible.
    """

    import check_coordination  # type: ignore

    cutover = codex_protocol_model.CURRENT_REVIEW_FAMILY_CUTOVER
    commits = projection.commits

    def epoch(commit: str | None, label: str) -> tuple[str, str | None]:
        if commit is None:
            return "problem", f"{label} has no introduction commit"
        try:
            commits.require_commit(cutover, "formal-review live cutover")
            commits.require_commit(commit, label)
            if commit == cutover or commits.is_ancestor(commit, cutover):
                return "history", None
            if commits.is_ancestor(cutover, commit):
                return "live", None
        except git_commit_projection.CommitGraphProjectionError as exc:
            return "problem", f"{label} cannot be classified: {exc}"
        return "problem", f"{label} is unrelated to the formal-review cutover"

    problems: list[str] = []
    if review_state.problem:
        problems.append(review_state.problem)
    pending = []
    for request in review_state.pending:
        classification, problem = epoch(request.commit, "verify-request commit")
        if problem is not None:
            problems.append(problem)
            continue
        if classification != "live":
            continue
        identity = _review_event_identity(request.path)
        if (
            identity is not None
            and protocol_mailbox.formal_review_route_problem(
                identity[2], identity[0], identity[1]
            ) is None
            and request.assigned_operator == identity[1]
        ):
            pending.append(request)

    failed = []
    for item in review_state.failed:
        request_epoch, request_problem = epoch(
            item.request_commit, "failed-review request commit"
        )
        report_epoch, report_problem = epoch(
            item.report_commit, "failed-review report commit"
        )
        for problem in (request_problem, report_problem):
            if problem is not None:
                problems.append(problem)
        if request_problem is not None or report_problem is not None:
            continue
        if request_epoch != "live" or report_epoch != "live":
            continue
        request_identity = _review_event_identity(item.request_path)
        report_identity = _review_event_identity(item.report_path)
        if (
            request_identity is not None
            and report_identity is not None
            and protocol_mailbox.formal_review_route_problem(
                request_identity[2], request_identity[0], request_identity[1]
            ) is None
            and protocol_mailbox.formal_review_route_problem(
                report_identity[2], report_identity[0], report_identity[1]
            ) is None
            and item.assigned_operator == request_identity[1]
            and report_identity[0] == request_identity[1]
            and report_identity[1] in {request_identity[0], "all"}
        ):
            failed.append(item)

    return check_coordination.VerifyReviewState(
        pending=tuple(pending),
        failed=tuple(failed),
        problem="; ".join(dict.fromkeys(problems)) if problems else None,
        grandfathered_history=(),
    )


def _collect_review_state(
    repo_root: Path,
    git: dict,
) -> tuple[dict, object | None]:
    """Collect current formal-review state independently of routine dialogue."""

    # Local import avoids making the status helper/checker module dependency
    # recursive at import time.
    import check_coordination  # type: ignore

    projection_result = check_coordination.committed_mailbox_projection(repo_root)
    review_state = check_coordination.inspect_verify_review_state(
        repo_root, projection_result=projection_result
    )
    projection = projection_result[0]
    if projection is None:
        review_state = check_coordination.VerifyReviewState(
            pending=(),
            failed=(),
            problem=(
                review_state.problem
                or "committed mailbox projection unavailable for live review state"
            ),
        )
    else:
        review_state = _live_review_state(review_state, projection)
    requests = list(review_state.pending)
    failed_reviews = list(review_state.failed)
    current = max(requests, key=lambda request: request.path, default=None)
    failed = max(
        failed_reviews, key=lambda review: review.report_path, default=None
    )
    issues = check_coordination.run(
        repo_root / "coordination",
        docs_root=repo_root / "docs",
        review_state=review_state,
        committed_projection=projection_result,
    )
    if (
        projection is not None
        and (
            not isinstance(git["git_sha"], str)
            or not projection.commits.head.startswith(git["git_sha"])
        )
    ):
        issues.append(check_coordination.CoordIssue(
            "coordination/mailbox/sent/",
            "commit_projection_identity_drift",
            "FATAL",
            "Git status and committed mailbox projection observed different HEADs",
        ))
    fatals = [issue for issue in issues if issue.severity == "FATAL"]
    advisories = [issue for issue in issues if issue.severity == "ADVISORY"]

    blocker = None
    if fatals:
        blocker = f"{fatals[0].kind}: {fatals[0].message}"
    elif current is not None and not current.valid:
        blocker = (
            f"invalid current request for {current.assigned_operator}: "
            f"{current.problem}"
        )
    elif failed is not None:
        blocker = (
            f"failed review for {failed.assigned_operator}: "
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
            f"{current.assigned_operator} reviews the exact committed request"
        )
    else:
        next_action = "continue scoped team work; request formal review when risk requires it"

    current_data = None
    if current is not None:
        current_data = {
            "path": current.path,
            "commit": current.commit,
            "assigned_operator": current.assigned_operator,
            "valid": current.valid,
            "grandfathered": current.grandfathered,
            "problem": current.problem,
            "reviewed_repository": current.reviewed_repository,
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
            "assigned_operator": failed.assigned_operator,
        }
    gate_status = (
        "FAIL" if fatals or failed_reviews else ("WARN" if advisories else "PASS")
    )
    state = {
        "projection": (
            {
                "head": projection.commits.head,
                "root": str(projection.commits.identity.root),
                "git_dir": str(projection.commits.identity.git_dir),
            }
            if projection is not None
            else None
        ),
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
    return state, projection


def collect_orientation_snapshot(repo_root: Path) -> dict:
    """Collect the live desktop-team snapshot."""
    now = datetime.now(tz=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    git = collect_git(repo_root)
    review, _projection = _collect_review_state(repo_root, git)
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
