#!/usr/bin/env python3
"""Check current durable formal-review state.

Team conversation lives in the local SQLite transport.  This module only
checks retained formal request/report files, including supersession and visible
historical failures. Exact-range integration admission is a separate check.
"""

from __future__ import annotations

import argparse
import os
import sys
from dataclasses import dataclass
from pathlib import Path

import compact_pair_loop
import git_runner
import protocol_mailbox


@dataclass(frozen=True)
class CoordIssue:
    path: str
    kind: str
    severity: str
    message: str


@dataclass(frozen=True)
class CurrentVerifyRequest:
    path: str
    commit: str | None
    reviewer_member: str
    valid: bool
    problem: str | None
    reviewed_base: str | None = None
    reviewed_head: str | None = None


@dataclass(frozen=True)
class FailedVerifyRequest:
    request_path: str
    request_commit: str
    report_path: str
    report_commit: str
    reviewer_member: str


@dataclass(frozen=True)
class VerifyReviewState:
    pending: tuple[CurrentVerifyRequest, ...]
    failed: tuple[FailedVerifyRequest, ...]
    problem: str | None = None
    historical_failed: tuple[FailedVerifyRequest, ...] = ()


def _git(root: Path, *arguments: str) -> bytes:
    result = git_runner.run_git(root, arguments, mode="authority")
    if result.returncode != 0:
        detail = result.stderr.decode("utf-8", "replace").strip()
        raise RuntimeError(detail or f"git {arguments[0]} failed")
    return result.stdout


def _introduction_commit(root: Path, path: str) -> str | None:
    result = git_runner.run_git(
        root,
        (
            "log",
            "--full-history",
            "--diff-filter=A",
            "--format=%H",
            "-1",
            "HEAD",
            "--",
            path,
        ),
        mode="authority",
    )
    if result.returncode != 0:
        return None
    value = result.stdout.decode("ascii", "strict").strip()
    return value if compact_pair_loop.SHA_RE.fullmatch(value) else None


def _current_formal_paths(root: Path) -> tuple[list[str], list[str], list[str]]:
    sent = root / "coordination/mailbox/sent"
    if not sent.exists():
        return [], [], []
    requests: list[str] = []
    reports: list[str] = []
    unknown: list[str] = []
    for name in sorted(os.listdir(sent)):
        relative = f"coordination/mailbox/sent/{name}"
        if name == ".gitkeep":
            continue
        if compact_pair_loop.REQUEST_RE.fullmatch(relative):
            requests.append(relative)
        elif compact_pair_loop.REPORT_RE.fullmatch(relative):
            reports.append(relative)
        else:
            unknown.append(relative)
    return requests, reports, unknown


def _immutable_bytes(root: Path, path: str, commit: str) -> bytes:
    worktree = compact_pair_loop._read_regular(root, path)
    current = _git(root, "show", f"HEAD:{path}")
    introduced = _git(root, "show", f"{commit}:{path}")
    if worktree != current:
        raise RuntimeError("formal artifact differs from committed HEAD")
    if current != introduced:
        raise RuntimeError("formal artifact changed after publication")
    return current


@compact_pair_loop.request_read_scope()
def inspect_verify_review_state(
    repo_root: Path | str,
) -> VerifyReviewState:
    """Return pending requests and active FAIL reports in the current tree."""

    root = Path(repo_root).resolve()
    requests, reports, unknown = _current_formal_paths(root)
    problems = [f"{path}: unsupported current mailbox entry" for path in unknown]
    try:
        committed_paths = _git(
            root, "ls-tree", "-r", "--name-only", "HEAD", "--", "coordination/mailbox/sent"
        ).decode("utf-8").splitlines()
    except RuntimeError as exc:
        problems.append(str(exc))
    else:
        current_paths = set(requests) | set(reports)
        problems.extend(
            f"{path}: published formal artifact missing from worktree"
            for path in committed_paths
            if (compact_pair_loop.REQUEST_RE.fullmatch(path) or compact_pair_loop.REPORT_RE.fullmatch(path))
            and path not in current_paths
        )
    parsed_requests: dict[
        tuple[str, str],
        tuple[CurrentVerifyRequest, compact_pair_loop.VerifyRequest | None],
    ] = {}

    for path in requests:
        commit = _introduction_commit(root, path)
        assigned = Path(path).name.split("-to-", 1)[1].removesuffix(
            "-verify-request.md"
        )
        if commit is None:
            current = CurrentVerifyRequest(
                path, None, assigned, False, "request is not committed"
            )
            parsed_requests[(path, "")] = (current, None)
            continue
        try:
            _immutable_bytes(root, path, commit)
            parsed = compact_pair_loop.parse_verify_request(root, path, commit)
        except (OSError, RuntimeError, UnicodeError, compact_pair_loop.CompactPairError) as exc:
            current = CurrentVerifyRequest(path, commit, assigned, False, str(exc))
            parsed_requests[(path, commit)] = (current, None)
            continue
        current = CurrentVerifyRequest(
            path=path,
            commit=commit,
            reviewer_member=parsed.reviewer_member,
            valid=True,
            problem=None,
            reviewed_base=parsed.reviewed_base,
            reviewed_head=parsed.reviewed_head,
        )
        parsed_requests[(path, commit)] = (current, parsed)

    parsed_reports: list[
        tuple[str, str, compact_pair_loop.VerificationReport]
    ] = []
    for path in reports:
        commit = _introduction_commit(root, path)
        if commit is None:
            problems.append(f"{path}: report is not committed")
            continue
        try:
            _immutable_bytes(root, path, commit)
            report = compact_pair_loop.parse_verification_report(root, path)
            violations = compact_pair_loop.validate_published_report(
                root, report, commit
            )
            if violations:
                raise compact_pair_loop.CompactPairError("; ".join(violations))
        except (OSError, RuntimeError, UnicodeError, compact_pair_loop.CompactPairError) as exc:
            problems.append(f"{path}: {exc}")
            continue
        parsed_reports.append((path, commit, report))

    superseded = {
        report.supersedes for _path, _commit, report in parsed_reports
        if report.supersedes is not None
    }
    active_reports = [
        item for item in parsed_reports if (item[0], item[1]) not in superseded
    ]

    pending: list[CurrentVerifyRequest] = []
    failed: list[FailedVerifyRequest] = []
    historical_failed = [
        FailedVerifyRequest(
            report.request_path, report.request_commit, path, commit, report.reviewer_member
        )
        for path, commit, report in active_reports
        if report.verdict == "FAIL"
        and (report.request_path, report.request_commit) not in parsed_requests
    ]
    for (path, commit), (current, _parsed) in parsed_requests.items():
        if not current.valid or not commit:
            pending.append(current)
            continue
        matches = [
            item
            for item in active_reports
            if item[2].request_path == path and item[2].request_commit == commit
        ]
        failures = [item for item in matches if item[2].verdict == "FAIL"]
        if failures:
            report_path, report_commit, _report = max(failures, key=lambda item: item[0])
            failed.append(
                FailedVerifyRequest(
                    request_path=path,
                    request_commit=commit,
                    report_path=report_path,
                    report_commit=report_commit,
                    reviewer_member=current.reviewer_member,
                )
            )
        elif any(item[2].verdict in compact_pair_loop.ADMITTING_VERDICTS for item in matches):
            continue
        elif any(
            report.request_path == path and report.request_commit == commit
            for _report_path, _report_commit, report in parsed_reports
        ):
            # A superseded FAIL remains historical evidence, but its request
            # is closed by the valid remediation report that superseded it.
            continue
        else:
            pending.append(current)

    return VerifyReviewState(
        pending=tuple(sorted(pending, key=lambda item: item.path)),
        failed=tuple(sorted(failed, key=lambda item: item.report_path)),
        problem="; ".join(problems) if problems else None,
        historical_failed=tuple(sorted(historical_failed, key=lambda item: item.report_path)),
    )


def run(
    coord_root: Path | str,
    *,
    review_state: VerifyReviewState | None = None,
) -> list[CoordIssue]:
    root = Path(coord_root).resolve().parent
    state = review_state or inspect_verify_review_state(root)
    issues: list[CoordIssue] = []
    if state.problem:
        issues.append(
            CoordIssue(
                "mailbox/sent",
                "invalid_formal_artifact",
                "FATAL",
                state.problem,
            )
        )
    for request in state.pending:
        if not request.valid:
            issues.append(
                CoordIssue(
                    request.path.removeprefix("coordination/"),
                    "invalid_verify_request",
                    "FATAL",
                    request.problem or "invalid verify-request",
                )
            )
    for item in state.failed:
        issues.append(
            CoordIssue(
                item.report_path.removeprefix("coordination/"),
                "failed_review",
                "FATAL",
                f"FAIL remains active for {item.request_path}@{item.request_commit}",
            )
        )
    for item in state.historical_failed:
        issues.append(
            CoordIssue(
                item.report_path.removeprefix("coordination/"),
                "historical_fail",
                "ADVISORY",
                f"unsuperseded historical FAIL for {item.request_path}@{item.request_commit}; "
                "request absent from current tree; evaluate integration with an explicit admission range",
            )
        )
    return issues


def main(argv: list[str] | None = None) -> int:
    repo_root = Path(__file__).resolve().parent.parent
    parser = argparse.ArgumentParser(
        description="Check current durable formal-review state."
    )
    parser.add_argument(
        "--root", default=str(repo_root / "coordination"), help="coordination directory"
    )
    arguments = parser.parse_args(argv)
    issues = run(arguments.root)
    for issue in issues:
        print(f"{issue.severity}: {issue.path}: {issue.message}")
    fatals = sum(issue.severity == "FATAL" for issue in issues)
    print(
        "COORDINATION CHECK — "
        + (f"FAIL: {fatals} fatal" if fatals else "PASS: current formal state valid")
    )
    return 1 if fatals else 0


if __name__ == "__main__":
    sys.exit(main())
