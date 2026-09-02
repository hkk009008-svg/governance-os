#!/usr/bin/env python3
"""Compose and validate the repository's exact-range review pair."""

from __future__ import annotations

import argparse
import os
import re
import stat
import sys
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path, PurePosixPath

import codex_protocol_model
import git_runner
import protocol_mailbox


SHA_RE = re.compile(r"[0-9a-f]{40}")
REQUEST_RE = re.compile(
    r"coordination/mailbox/sent/"
    r"[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}-[0-9]{2}-[0-9]{2}Z-"
    r"(?P<author>codex|claude|agy)-to-(?P<reviewer>codex|claude)-"
    r"verify-request\.md"
)
REPORT_RE = re.compile(
    r"coordination/mailbox/sent/"
    r"[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}-[0-9]{2}-[0-9]{2}Z-"
    r"(?P<reviewer>codex|claude)-to-(?P<recipient>codex|claude|agy|all)-"
    r"verification-report\.md"
)
MAX_EVENT_BYTES = 262_144
MATERIAL_BEHAVIOR_RISK = "material-behavior"
HIGH_RISK_CONTROL = "high-risk-control"
ABUSE_ASSESSMENT_BOUND_TO_REQUEST = "bound-to-request"


class CompactPairError(ValueError):
    pass


@dataclass(frozen=True)
class VerifyRequest:
    path: str
    trigger_commit: str
    reviewed_head: str
    reviewed_base: str
    author_member: str
    author_model: str
    reviewer_member: str
    risk_class: str
    abuse_class_assessment: tuple[str, ...]
    outcome: str


@dataclass(frozen=True)
class VerificationReport:
    path: str
    verdict: str
    request_path: str
    request_commit: str
    reviewer_member: str
    reviewer_model: str
    findings: str
    evidence: tuple[str, ...]
    supersedes: tuple[str, str] | None
    abuse_class_assessment_binding: str | None


def _repo_path(root: Path, value: str | os.PathLike[str]) -> str:
    root = root.resolve()
    path = Path(value)
    if path.is_absolute():
        try:
            value = path.relative_to(root).as_posix()
        except ValueError as exc:
            raise CompactPairError("artifact path is outside the repository") from exc
    else:
        value = path.as_posix()
    pure = PurePosixPath(value)
    if (
        not value
        or pure.is_absolute()
        or pure.as_posix() != value
        or any(part in {"", ".", ".."} for part in pure.parts)
    ):
        raise CompactPairError("artifact path is not canonical repository-relative")
    return value


def _git(root: Path, *arguments: str) -> bytes:
    result = git_runner.run_git(root, arguments, mode="authority")
    if result.returncode != 0:
        detail = result.stderr.decode("utf-8", "replace").strip()
        raise CompactPairError(detail or f"git {arguments[0]} failed")
    return result.stdout


def _full_commit(root: Path, value: str, label: str) -> str:
    if SHA_RE.fullmatch(value) is None:
        raise CompactPairError(f"{label} must be one full lowercase commit SHA")
    resolved = _git(root, "rev-parse", "--verify", f"{value}^{{commit}}").decode().strip()
    if resolved != value:
        raise CompactPairError(f"{label} commit does not resolve exactly")
    return value


def _resolve_rev(root: Path, value: str, label: str) -> str:
    if not value or value != value.strip() or value.startswith("-"):
        raise CompactPairError(f"{label} must be one Git revision")
    resolved = _git(root, "rev-parse", "--verify", f"{value}^{{commit}}").decode().strip()
    if SHA_RE.fullmatch(resolved) is None:
        raise CompactPairError(f"{label} did not resolve to one commit")
    return resolved


def _resolve_range(root: Path, base: str, head: str) -> tuple[str, str]:
    first = (_resolve_rev(root, base, "Reviewed base"), _resolve_rev(root, head, "Reviewed head"))
    second = (_resolve_rev(root, base, "Reviewed base"), _resolve_rev(root, head, "Reviewed head"))
    if first != second:
        raise CompactPairError("Reviewed range moved while composing; use explicit SHAs")
    return first


def _is_ancestor(root: Path, ancestor: str, descendant: str) -> bool:
    result = git_runner.run_git(
        root, ("merge-base", "--is-ancestor", ancestor, descendant), mode="authority"
    )
    if result.returncode not in {0, 1}:
        raise CompactPairError("Git ancestry check failed")
    return result.returncode == 0


def _read_regular(root: Path, path: str) -> bytes:
    current = root.resolve()
    for component in PurePosixPath(path).parts[:-1]:
        current /= component
        if current.is_symlink():
            raise CompactPairError("artifact path traverses a symlink")
    descriptor = os.open(
        root / path,
        os.O_RDONLY | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0),
    )
    try:
        before = os.fstat(descriptor)
        if not stat.S_ISREG(before.st_mode) or before.st_size > MAX_EVENT_BYTES:
            raise CompactPairError("artifact is not one bounded regular file")
        raw = os.read(descriptor, before.st_size + 1)
        after = os.fstat(descriptor)
        if len(raw) != before.st_size or (
            before.st_dev,
            before.st_ino,
            before.st_size,
        ) != (after.st_dev, after.st_ino, after.st_size):
            raise CompactPairError("artifact changed while reading")
        return raw
    finally:
        os.close(descriptor)


def _decode(raw: bytes, label: str) -> str:
    if len(raw) > MAX_EVENT_BYTES or b"\x00" in raw:
        raise CompactPairError(f"{label} is not one bounded text artifact")
    try:
        return raw.decode("utf-8", "strict")
    except UnicodeDecodeError as exc:
        raise CompactPairError(f"{label} is not UTF-8") from exc


def _field(lines: list[str], label: str, *, optional: bool = False) -> str | None:
    prefix = f"{label}: "
    matches = [line[len(prefix) :] for line in lines if line.startswith(prefix)]
    if not matches and optional:
        return None
    if len(matches) != 1 or not matches[0] or matches[0] != matches[0].strip():
        raise CompactPairError(f"missing, duplicate, or invalid {label}")
    return matches[0]


def _section(lines: list[str], heading: str, *, optional: bool = False) -> list[str] | None:
    positions = [index for index, line in enumerate(lines) if line == heading]
    if not positions and optional:
        return None
    if len(positions) != 1:
        raise CompactPairError(f"missing or duplicate {heading}")
    start = positions[0] + 1
    end = next(
        (
            index
            for index in range(start, len(lines))
            if lines[index].startswith("## ")
            or lines[index].startswith("Cursor at send: ")
        ),
        len(lines),
    )
    return lines[start:end]


def _envelope_sender(text: str) -> str:
    matches = re.findall(r"\*\*From:\*\* ([a-z0-9]+) \(online\)", text)
    if len(matches) != 1:
        raise CompactPairError("missing or duplicate envelope sender")
    return matches[0]


def _abuse_entries(lines: list[str], required: bool) -> tuple[str, ...]:
    body = _section(lines, "## Abuse Class Assessment", optional=not required)
    if body is None:
        return ()
    entries = tuple(line[2:].strip() for line in body if line.startswith("- "))
    if not entries or any(not entry for entry in entries) or len(entries) != len(set(entries)):
        raise CompactPairError("Abuse Class Assessment must contain unique nonempty bullets")
    if any(line.strip() and not line.startswith("- ") for line in body):
        raise CompactPairError("Abuse Class Assessment accepts only bullet entries")
    return entries


def _parse_request_bytes(root: Path, path: str, raw: bytes, trigger_commit: str) -> VerifyRequest:
    match = REQUEST_RE.fullmatch(path)
    if match is None:
        raise CompactPairError("verify-request path is not canonical")
    route_problem = protocol_mailbox.formal_review_route_problem(
        "verify-request", match.group("author"), match.group("reviewer")
    )
    if route_problem:
        raise CompactPairError(route_problem)
    text = _decode(raw, "verify-request")
    lines = text.splitlines()
    if _field(lines, "Event type") != "verify-request":
        raise CompactPairError("Event type must be verify-request")
    if _envelope_sender(text) != match.group("author"):
        raise CompactPairError("request envelope sender does not match filename")
    base = str(_field(lines, "Reviewed base"))
    head = str(_field(lines, "Reviewed head"))
    if SHA_RE.fullmatch(base) is None or SHA_RE.fullmatch(head) is None:
        raise CompactPairError("Reviewed base/head must be full lowercase commit SHAs")
    risk_class = str(_field(lines, "Risk class"))
    try:
        profile = codex_protocol_model.review_profile_for(risk_class)
    except ValueError as exc:
        raise CompactPairError(str(exc)) from exc
    if risk_class not in {MATERIAL_BEHAVIOR_RISK, HIGH_RISK_CONTROL}:
        raise CompactPairError("formal review risk must be material-behavior or high-risk-control")
    outcome_lines = _section(lines, "## Outcome") or []
    outcome = "\n".join(outcome_lines).strip()
    if not outcome:
        raise CompactPairError("Outcome must be nonempty")
    return VerifyRequest(
        path=path,
        trigger_commit=trigger_commit,
        reviewed_base=base,
        reviewed_head=head,
        author_member=match.group("author"),
        author_model=str(_field(lines, "Author model")),
        reviewer_member=match.group("reviewer"),
        risk_class=risk_class,
        abuse_class_assessment=_abuse_entries(
            lines, required=profile.requires_abuse_class_assessment
        ),
        outcome=outcome,
    )


def validate_request_candidate(root: Path, request: VerifyRequest) -> list[str]:
    violations: list[str] = []
    if not codex_protocol_model.model_is_current_author(request.author_model):
        violations.append("Author model is not currently admitted")
    if not codex_protocol_model.model_family_matches_member(
        request.author_model, request.author_member
    ):
        violations.append("author model family does not match author member")
    if request.risk_class != HIGH_RISK_CONTROL and request.abuse_class_assessment:
        violations.append("Abuse Class Assessment is only valid for high-risk-control")
    try:
        base = _full_commit(root, request.reviewed_base, "Reviewed base")
        head = _full_commit(root, request.reviewed_head, "Reviewed head")
        if base == head or not _is_ancestor(root, base, head):
            violations.append("Reviewed base must be a strict ancestor of Reviewed head")
    except CompactPairError as exc:
        violations.append(str(exc))
    return violations


def parse_verify_request_structure(
    root: Path, request_path: str | os.PathLike[str], trigger_commit: str
) -> VerifyRequest:
    root = root.resolve()
    path = _repo_path(root, request_path)
    trigger = _full_commit(root, trigger_commit, "request trigger")
    changed = _git(
        root,
        "diff-tree",
        "--root",
        "--no-commit-id",
        "--name-status",
        "-r",
        trigger,
        "--",
        path,
    ).decode("utf-8", "strict").splitlines()
    if changed != [f"A\t{path}"]:
        raise CompactPairError("verify-request must be added by its trigger commit")
    raw = _git(root, "show", f"{trigger}:{path}")
    return _parse_request_bytes(root, path, raw, trigger)


def parse_verify_request(
    root: Path, request_path: str | os.PathLike[str], trigger_commit: str
) -> VerifyRequest:
    root = root.resolve()
    request = parse_verify_request_structure(root, request_path, trigger_commit)
    violations = validate_request_candidate(root, request)
    parents = _git(root, "show", "-s", "--format=%P", request.trigger_commit).decode().split()
    changed = _git(
        root,
        "diff-tree",
        "--root",
        "--no-commit-id",
        "--name-only",
        "-r",
        request.trigger_commit,
    ).decode("utf-8", "strict").splitlines()
    if parents != [request.reviewed_head] or changed != [request.path]:
        violations.append(
            "verify-request must be the only change in a commit directly after Reviewed head"
        )
    if violations:
        raise CompactPairError("; ".join(violations))
    return request


def parse_verify_request_candidate(
    root: Path, candidate_path: str | os.PathLike[str], final_path: str | os.PathLike[str]
) -> VerifyRequest:
    root = root.resolve()
    candidate = _repo_path(root, candidate_path)
    final = _repo_path(root, final_path)
    return _parse_request_bytes(root, final, _read_regular(root, candidate), "")


def compose_request(
    root: Path,
    *,
    author_member: str,
    author_model: str,
    reviewer_member: str,
    risk_class: str,
    base_rev: str,
    head_rev: str,
    outcome: str,
    abuse_assessments: Sequence[str] = (),
    **_ignored: object,
) -> str:
    root = root.resolve()
    problem = protocol_mailbox.formal_review_route_problem(
        "verify-request", author_member, reviewer_member
    )
    if problem:
        raise CompactPairError(problem)
    profile = codex_protocol_model.review_profile_for(risk_class)
    if risk_class not in {MATERIAL_BEHAVIOR_RISK, HIGH_RISK_CONTROL}:
        raise CompactPairError("formal review risk must be material-behavior or high-risk-control")
    if not codex_protocol_model.model_is_current_author(author_model):
        raise CompactPairError("Author model is not currently admitted")
    if not codex_protocol_model.model_family_matches_member(author_model, author_member):
        raise CompactPairError("author model family does not match author member")
    base, head = _resolve_range(root, base_rev, head_rev)
    if base == head or not _is_ancestor(root, base, head):
        raise CompactPairError("Reviewed base must be a strict ancestor of Reviewed head")
    outcome = outcome.strip()
    if not outcome:
        raise CompactPairError("Outcome must be nonempty")
    assessments = tuple(item.strip() for item in abuse_assessments if item.strip())
    if profile.requires_abuse_class_assessment and not assessments:
        raise CompactPairError("high-risk-control requires an Abuse Class Assessment")
    if not profile.requires_abuse_class_assessment and assessments:
        raise CompactPairError("Abuse Class Assessment is only valid for high-risk-control")
    if len(assessments) != len(set(assessments)):
        raise CompactPairError("Abuse Class Assessment entries must be unique")
    lines = [
        "Event type: verify-request",
        f"Reviewed base: {base}",
        f"Reviewed head: {head}",
        f"Author model: {author_model}",
        f"Risk class: {risk_class}",
        "",
        "## Outcome",
        "",
        outcome,
    ]
    if assessments:
        lines += ["", "## Abuse Class Assessment", ""]
        lines += [f"- {item}" for item in assessments]
    return "\n".join(lines)


def _report_reference(root: Path, value: str, label: str) -> tuple[str, str]:
    path, separator, commit = value.rpartition("@")
    if not separator:
        raise CompactPairError(f"{label} must bind report-path@commit")
    path = _repo_path(root, path)
    if REPORT_RE.fullmatch(path) is None or SHA_RE.fullmatch(commit) is None:
        raise CompactPairError(f"{label} must name a canonical report at a full commit")
    return path, commit


def _parse_report_bytes(root: Path, path: str, raw: bytes) -> VerificationReport:
    match = REPORT_RE.fullmatch(path)
    if match is None:
        raise CompactPairError("verification-report path is not canonical")
    problem = protocol_mailbox.formal_review_route_problem(
        "verification-report", match.group("reviewer"), match.group("recipient")
    )
    if problem:
        raise CompactPairError(problem)
    text = _decode(raw, "verification-report")
    lines = text.splitlines()
    if _field(lines, "Event type") != "verification-report":
        raise CompactPairError("Event type must be verification-report")
    if _envelope_sender(text) != match.group("reviewer"):
        raise CompactPairError("report envelope sender does not match filename")
    verdict = str(_field(lines, "VERDICT"))
    if verdict not in {"GO", "NITS", "FAIL"}:
        raise CompactPairError("VERDICT must be GO, NITS, or FAIL")
    request_value = str(_field(lines, "Verification request"))
    request_path, separator, request_commit = request_value.rpartition("@")
    request_path = _repo_path(root, request_path)
    if (
        not separator
        or REQUEST_RE.fullmatch(request_path) is None
        or SHA_RE.fullmatch(request_commit) is None
    ):
        raise CompactPairError("Verification request must bind a canonical request@commit")
    supersedes_value = _field(lines, "Supersedes", optional=True)
    supersedes = (
        _report_reference(root, str(supersedes_value), "Supersedes")
        if supersedes_value is not None
        else None
    )
    findings = "\n".join(_section(lines, "## Findings") or []).strip()
    if not findings:
        raise CompactPairError("Findings must be nonempty")
    evidence = tuple(line for line in (_section(lines, "## Evidence", optional=True) or []) if line.strip())
    return VerificationReport(
        path=path,
        verdict=verdict,
        request_path=request_path,
        request_commit=request_commit,
        reviewer_member=match.group("reviewer"),
        reviewer_model=str(_field(lines, "Reviewer model")),
        findings=findings,
        evidence=evidence,
        supersedes=supersedes,
        abuse_class_assessment_binding=_field(
            lines, "Abuse Class Assessment", optional=True
        ),
    )


def parse_verification_report(
    root: Path, report_path: str | os.PathLike[str]
) -> VerificationReport:
    root = root.resolve()
    path = _repo_path(root, report_path)
    return _parse_report_bytes(root, path, _read_regular(root, path))


def parse_verification_report_committed_bytes(
    root: Path,
    report_path: str | os.PathLike[str],
    raw: bytes,
    **_ignored: object,
) -> VerificationReport:
    root = root.resolve()
    return _parse_report_bytes(root, _repo_path(root, report_path), raw)


def parse_verification_report_candidate(
    root: Path, candidate_path: str | os.PathLike[str], final_path: str | os.PathLike[str]
) -> VerificationReport:
    root = root.resolve()
    candidate = _repo_path(root, candidate_path)
    final = _repo_path(root, final_path)
    return _parse_report_bytes(root, final, _read_regular(root, candidate))


def request_for_report(root: Path, report: VerificationReport) -> VerifyRequest:
    return parse_verify_request(root, report.request_path, report.request_commit)


def _basic_report_violations(
    report: VerificationReport, request: VerifyRequest
) -> list[str]:
    violations: list[str] = []
    request_match = REQUEST_RE.fullmatch(request.path)
    report_match = REPORT_RE.fullmatch(report.path)
    if request_match is None or report_match is None:
        return ["request or report path is not canonical"]
    if report.reviewer_member != request.reviewer_member:
        violations.append("report publisher is not the requested reviewer")
    if report_match.group("recipient") not in {request.author_member, "all"}:
        violations.append("report recipient does not match request author")
    if not codex_protocol_model.model_is_current_reviewer(report.reviewer_model):
        violations.append("Reviewer model is not currently admitted")
    if not codex_protocol_model.model_family_matches_member(
        report.reviewer_model, report.reviewer_member
    ):
        violations.append("reviewer model family does not match reviewer member")
    profile = codex_protocol_model.review_profile_for(request.risk_class)
    if profile.requires_different_model and not codex_protocol_model.models_are_current_review_pair(
        request.author_model, report.reviewer_model
    ):
        violations.append("author and reviewer must use different admitted model families")
    if profile.requires_abuse_class_assessment:
        if not request.abuse_class_assessment:
            violations.append("high-risk-control request lacks Abuse Class Assessment")
        if report.abuse_class_assessment_binding != ABUSE_ASSESSMENT_BOUND_TO_REQUEST:
            violations.append("high-risk-control report must bind Abuse Class Assessment")
    elif report.abuse_class_assessment_binding is not None:
        violations.append("Abuse Class Assessment binding is only valid for high-risk-control")
    if report.verdict == "GO" and (
        not any(line.startswith("$ ") and line[2:].strip() for line in report.evidence)
        or not any(line.startswith("→ ") and line[2:].strip() for line in report.evidence)
    ):
        violations.append("GO requires command and output evidence")
    return violations


def _load_report_at_introduction(
    root: Path, path: str, commit: str, history_head: str
) -> tuple[VerificationReport, VerifyRequest]:
    commit = _full_commit(root, commit, "report introduction")
    if not _is_ancestor(root, commit, history_head):
        raise CompactPairError("superseded report is not in candidate history")
    changed = _git(
        root,
        "diff-tree",
        "--root",
        "--no-commit-id",
        "--name-status",
        "-r",
        commit,
        "--",
        path,
    ).decode("utf-8", "strict").splitlines()
    if changed != [f"A\t{path}"]:
        raise CompactPairError("Supersedes must name the report introduction commit")
    report = _parse_report_bytes(root, path, _git(root, "show", f"{commit}:{path}"))
    request = request_for_report(root, report)
    basic = _basic_report_violations(report, request)
    if basic:
        raise CompactPairError("superseded report is invalid: " + "; ".join(basic))
    return report, request


def _supersedes_violations(
    root: Path,
    report: VerificationReport,
    request: VerifyRequest,
    history_head: str,
) -> list[str]:
    if report.supersedes is None:
        return []
    path, commit = report.supersedes
    if path == report.path:
        return ["Supersedes cannot name the report itself"]
    try:
        previous, previous_request = _load_report_at_introduction(
            root, path, commit, history_head
        )
    except CompactPairError as exc:
        return [f"Supersedes binding invalid: {exc}"]
    violations: list[str] = []
    if previous.reviewer_member != report.reviewer_member:
        violations.append("a reviewer supersedes only its own report")
    same_request = (
        previous.request_path == report.request_path
        and previous.request_commit == report.request_commit
    )
    if not same_request:
        if previous.verdict != "FAIL":
            violations.append("a different-request supersession must replace a FAIL")
        if request.risk_class != previous_request.risk_class:
            violations.append("remediation risk class changed")
        if request.reviewed_base != previous_request.reviewed_head:
            violations.append("remediation base must equal the failed reviewed head")
    return violations


def validate_report(
    root: Path, report: VerificationReport, *, history_head: str = "HEAD"
) -> list[str]:
    root = root.resolve()
    try:
        request = request_for_report(root, report)
        resolved_history = _git(root, "rev-parse", f"{history_head}^{{commit}}").decode().strip()
        if not _is_ancestor(root, request.trigger_commit, resolved_history):
            raise CompactPairError("request commit is not in candidate history")
    except CompactPairError as exc:
        return [f"request binding invalid: {exc}"]
    return _basic_report_violations(report, request) + _supersedes_violations(
        root, report, request, resolved_history
    )


def validate_published_report(
    root: Path,
    report: VerificationReport,
    report_commit: str,
    *,
    history_head: str = "HEAD",
) -> list[str]:
    """Validate the report and require its commit to contain only that report."""

    violations = validate_report(root, report, history_head=history_head)
    try:
        commit = _full_commit(root.resolve(), report_commit, "report introduction")
        parents = _git(root, "show", "-s", "--format=%P", commit).decode().split()
        changed = _git(
            root,
            "diff-tree",
            "--root",
            "--no-commit-id",
            "--name-status",
            "-r",
            commit,
        ).decode("utf-8", "strict").splitlines()
        if parents != [report.request_commit] or changed != [f"A\t{report.path}"]:
            violations.append(
                "verification-report must be the only change in a commit directly after its request"
            )
    except CompactPairError as exc:
        violations.append(str(exc))
    return violations


def _validate_candidate(
    root: Path, candidate: str, final_relative: str
) -> list[str]:
    if final_relative.endswith("-verify-request.md"):
        request = parse_verify_request_candidate(root, candidate, final_relative)
        return validate_request_candidate(root, request)
    report = parse_verification_report_candidate(root, candidate, final_relative)
    return validate_report(root, report)


def _main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="compact_pair_loop.py")
    commands = parser.add_subparsers(dest="command", required=True)
    candidate = commands.add_parser("validate-candidate")
    candidate.add_argument("--repo-root", required=True, type=Path)
    candidate.add_argument("--candidate", required=True)
    candidate.add_argument("--final-relative", required=True)
    compose = commands.add_parser("compose-request")
    compose.add_argument("--repo-root", required=True, type=Path)
    compose.add_argument("--author", required=True)
    compose.add_argument("--author-model", required=True)
    compose.add_argument("--reviewer", required=True)
    compose.add_argument("--risk-class", required=True)
    compose.add_argument("--base", required=True)
    compose.add_argument("--head", default="HEAD")
    compose.add_argument("--abuse-class", action="append", default=[])
    arguments = parser.parse_args(argv)
    try:
        if arguments.command == "compose-request":
            body = compose_request(
                arguments.repo_root,
                author_member=arguments.author,
                author_model=arguments.author_model,
                reviewer_member=arguments.reviewer,
                risk_class=arguments.risk_class,
                base_rev=arguments.base,
                head_rev=arguments.head,
                outcome=sys.stdin.read(),
                abuse_assessments=arguments.abuse_class,
            )
            print(body)
            return 0
        violations = _validate_candidate(
            arguments.repo_root, arguments.candidate, arguments.final_relative
        )
        if violations:
            raise CompactPairError("; ".join(violations))
    except (CompactPairError, OSError) as exc:
        print(f"formal review validation failed: {exc}", file=sys.stderr)
        return 1
    print("formal review validation passed")
    return 0


def review_validate_main(argv: list[str] | None = None) -> int:
    arguments = list(sys.argv[1:] if argv is None else argv)
    return _main(["validate-candidate", *arguments])


def review_request_main(argv: list[str] | None = None) -> int:
    arguments = list(sys.argv[1:] if argv is None else argv)
    return _main(["compose-request", *arguments])


if __name__ == "__main__":
    sys.exit(_main())
