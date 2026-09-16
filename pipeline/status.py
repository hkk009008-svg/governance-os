#!/usr/bin/env python3
"""Read-only desktop-team readiness and current formal-review status."""

from __future__ import annotations

import argparse
import dataclasses
import hashlib
import json
import os
import stat
import sys
import tempfile
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

# The dashboard remembers one validated review state per exact repository
# fingerprint. `check` and the admission gate never read it; they re-prove
# every artifact from Git on every run.
REVIEW_STATE_CACHE_NAME = "pipeline-status-cache.json"
_CACHE_LIMIT_BYTES = 1_048_576


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


def _cache_enabled() -> bool:
    """Opt-out switch for the dashboard cache (tests and probes set it to 0)."""
    return os.environ.get("PIPELINE_STATUS_CACHE", "1") != "0"


def _entry_digest(entry: os.DirEntry, info: os.stat_result) -> str:
    """SHA-256 of a regular mailbox entry's bytes; symlinks and others get a marker."""
    if not stat.S_ISREG(info.st_mode):
        return "not-a-regular-file"
    descriptor = os.open(
        entry.path,
        os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0) | getattr(os, "O_CLOEXEC", 0),
    )
    try:
        handle = os.fdopen(descriptor, "rb")
    except OSError:
        os.close(descriptor)
        raise
    with handle:
        return hashlib.file_digest(handle, "sha256").hexdigest()


def _review_state_key(repo_root: Path) -> tuple[Path, str] | None:
    """Fingerprint everything the review state depends on, or None if unknown.

    HEAD, the committed mailbox tree, every worktree mailbox entry (inode,
    size, mtime, mode, and a digest of its bytes), and the validator modules'
    bytes all enter the key, so a new commit, a tampered artifact, or a code
    change is a miss, never a stale hit. The digest matters: a same-length
    rewrite with its timestamp restored leaves every stat field unchanged.
    """
    import check_coordination  # type: ignore
    import compact_pair_loop  # type: ignore

    try:
        head = _run_git(repo_root, ["rev-parse", "--verify", "HEAD^{commit}"])
        common = _run_git(
            repo_root, ["rev-parse", "--path-format=absolute", "--git-common-dir"]
        )
        tree = _run_git(
            repo_root, ["ls-tree", "-r", "HEAD", "--", "coordination/mailbox/sent"]
        )
        parts = [head, tree]
        sent = repo_root / "coordination/mailbox/sent"
        try:
            with os.scandir(sent) as entries:
                for entry in sorted(entries, key=lambda item: item.name):
                    info = entry.stat(follow_symlinks=False)
                    parts.append(
                        f"{entry.name}:{info.st_mode}:{info.st_ino}:"
                        f"{info.st_size}:{info.st_mtime_ns}:{_entry_digest(entry, info)}"
                    )
        except FileNotFoundError:
            parts.append("worktree-mailbox-absent")
        for module in (check_coordination, compact_pair_loop):
            parts.append(hashlib.sha256(Path(module.__file__).read_bytes()).hexdigest())
    except Exception:
        return None
    key = hashlib.sha256("\n".join(parts).encode("utf-8")).hexdigest()
    return Path(common) / REVIEW_STATE_CACHE_NAME, key


def _state_from_json(data: dict):
    import check_coordination  # type: ignore

    return check_coordination.VerifyReviewState(
        pending=tuple(
            check_coordination.CurrentVerifyRequest(**item) for item in data["pending"]
        ),
        failed=tuple(
            check_coordination.FailedVerifyRequest(**item) for item in data["failed"]
        ),
        problem=data["problem"],
        historical_failed=tuple(
            check_coordination.FailedVerifyRequest(**item)
            for item in data["historical_failed"]
        ),
    )


def _read_cached_state(path: Path, key: str):
    """Return the cached state for ``key`` or None; never raise."""
    try:
        descriptor = os.open(
            path,
            os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0) | getattr(os, "O_CLOEXEC", 0),
        )
    except OSError:
        return None
    try:
        info = os.fstat(descriptor)
        if (
            not stat.S_ISREG(info.st_mode)
            or info.st_uid != os.geteuid()
            or stat.S_IMODE(info.st_mode) & 0o077
            or info.st_size > _CACHE_LIMIT_BYTES
        ):
            return None
        raw = os.read(descriptor, info.st_size)
    except OSError:
        return None
    finally:
        os.close(descriptor)
    try:
        payload = json.loads(raw.decode("utf-8"))
        if not isinstance(payload, dict) or payload.get("key") != key:
            return None
        return _state_from_json(payload["state"])
    except (KeyError, TypeError, ValueError, UnicodeDecodeError):
        return None


def _write_cached_state(path: Path, key: str, state) -> None:
    """Replace the cache atomically with owner-only permissions; never raise."""
    payload = json.dumps(
        {"key": key, "state": dataclasses.asdict(state)}, sort_keys=True
    ).encode("utf-8")
    try:
        descriptor, temporary = tempfile.mkstemp(
            prefix=".status-cache-", dir=path.parent
        )
    except OSError:
        return
    try:
        os.fchmod(descriptor, 0o600)
        view = memoryview(payload)
        while view:
            view = view[os.write(descriptor, view):]
        os.close(descriptor)
        descriptor = -1
        os.replace(temporary, path)
    except OSError:
        if descriptor != -1:
            os.close(descriptor)
        try:
            os.unlink(temporary)
        except OSError:
            pass


def _review_state(repo_root: Path):
    """Current formal-review state, from the fingerprint cache when it matches."""
    import check_coordination  # type: ignore

    located = _review_state_key(repo_root) if _cache_enabled() else None
    if located is not None:
        cached = _read_cached_state(*located)
        if cached is not None:
            return cached
    state = check_coordination.inspect_verify_review_state(repo_root)
    if located is not None:
        _write_cached_state(*located, state)
    return state


def _collect_review_state(repo_root: Path) -> dict:
    """Collect current formal-review state independently of routine dialogue."""

    # Local import avoids making the status helper/checker module dependency
    # recursive at import time.
    import check_coordination  # type: ignore

    review_state = _review_state(repo_root)
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

    pending_data = [
        {
            "path": item.path,
            "commit": item.commit,
            "reviewer": item.reviewer_member,
            "valid": item.valid,
            "problem": item.problem,
            "reviewed_base": item.reviewed_base,
            "reviewed_head": item.reviewed_head,
        }
        for item in requests
    ]
    current_data = max(pending_data, key=lambda item: item["path"], default=None)
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
        "pending_requests": pending_data,
        "current_request": current_data,
        "failed_review": failed_data,
        "historical_failed_reviews": [
            {
                "request_path": item.request_path,
                "request_commit": item.request_commit,
                "report_path": item.report_path,
                "report_commit": item.report_commit,
                "reviewer": item.reviewer_member,
            }
            for item in review_state.historical_failed
        ],
        "admission": "not-run; use check admission with an explicit base/head range",
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


def render_orientation_snapshot(snapshot: dict, *, verbose: bool = False) -> str:
    """Render the live desktop-team snapshot."""
    return _render_desktop_orientation_snapshot(snapshot, verbose=verbose)


def main(argv: Optional[list[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        description="Print compact desktop-team readiness and formal-review state.",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Emit the desktop-team snapshot as JSON.",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Also list historical unresolved FAIL reports.",
    )
    args = parser.parse_args(argv)
    snapshot = collect_orientation_snapshot(_REPO_ROOT)
    if args.json:
        print(json.dumps(snapshot, sort_keys=True))
    else:
        print(render_orientation_snapshot(snapshot, verbose=args.verbose), end="")
    return 0


if __name__ == "__main__":
    sys.exit(main())
