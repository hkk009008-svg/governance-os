#!/usr/bin/env python3
"""Small, fail-closed validator for the current Director→Operator pair loop."""

from __future__ import annotations

import argparse
import os
import re
import stat
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path, PurePosixPath

import protocol_mailbox


SHA_RE = re.compile(r"[0-9a-f]{40}")
REQUEST_RE = re.compile(
    r"coordination/mailbox/sent/"
    r"[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}-[0-9]{2}-[0-9]{2}Z-"
    r"(?P<author>director2?|operator2?)-to-(?P<operator>operator2?)-verify-request\.md"
)
REPORT_RE = re.compile(
    r"coordination/mailbox/sent/"
    r"[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}-[0-9]{2}-[0-9]{2}Z-"
    r"(?P<reviewer>operator2?)-to-(?:director2?|operator2?|coordinator2?|all)-"
    r"verification-report\.md"
)
MAX_EVENT_BYTES = 262_144
LEGACY_VERBOSE_CUTOFF = "ab7fd77081448008f1de30c17a8aaf156a9506c5"
PAIR_SEATS = frozenset({"director", "director2", "operator", "operator2"})
OPERATOR_SEATS = frozenset({"operator", "operator2"})
FINDING_DISPOSITIONS = frozenset(
    {"addressed", "counter-evidence", "ordinary-risk", "unresolved-hard-boundary"}
)


class CompactPairError(ValueError):
    """A current pair artifact is malformed or lacks structural authority."""


@dataclass(frozen=True)
class VerifyRequest:
    path: str
    trigger_commit: str
    reviewed_head: str
    reviewed_base: str
    author_seat: str
    author_model: str
    assigned_operator: str
    outcome: str
    finding_refs: tuple[str, ...]


@dataclass(frozen=True)
class VerificationReport:
    path: str
    verdict: str
    request_path: str
    request_commit: str
    reviewed_head: str
    reviewed_base: str
    reviewer_seat: str
    reviewer_model: str
    evidence: tuple[str, ...]
    finding_refs: tuple[str, ...]
    finding_dispositions: tuple[tuple[str, str], ...]
    filename_reviewer: str
    envelope_sender: str


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
        or value.startswith("/")
        or "\\" in value
        or any(part in {"", ".", ".."} for part in pure.parts)
        or pure.as_posix() != value
    ):
        raise CompactPairError("artifact path is not canonical repository-relative")
    return value


def _git(root: Path, *arguments: str, check: bool = True) -> bytes:
    environment = {
        key: value for key, value in os.environ.items() if not key.startswith("GIT_")
    }
    completed = subprocess.run(
        ["/usr/bin/git", "--no-replace-objects", *arguments],
        cwd=root,
        env=environment,
        capture_output=True,
        check=False,
    )
    if check and completed.returncode != 0:
        detail = completed.stderr.decode("utf-8", errors="backslashreplace").strip()
        raise CompactPairError(f"Git commit or path validation failed: {detail}")
    return completed.stdout


def _full_commit(root: Path, value: str, label: str) -> str:
    if SHA_RE.fullmatch(value) is None:
        raise CompactPairError(f"{label} must be one full lowercase commit SHA")
    resolved = _git(root, "rev-parse", "--verify", f"{value}^{{commit}}").decode().strip()
    if resolved != value:
        raise CompactPairError(f"{label} commit does not resolve exactly")
    return value


def _is_ancestor(root: Path, ancestor: str, descendant: str) -> bool:
    environment = {
        key: value for key, value in os.environ.items() if not key.startswith("GIT_")
    }
    result = subprocess.run(
        ["/usr/bin/git", "--no-replace-objects", "merge-base", "--is-ancestor", ancestor, descendant],
        cwd=root,
        env=environment,
        capture_output=True,
        check=False,
    )
    if result.returncode not in {0, 1}:
        raise CompactPairError("Git ancestry validation failed")
    return result.returncode == 0


def _decode(raw: bytes, label: str) -> str:
    if len(raw) > MAX_EVENT_BYTES:
        raise CompactPairError(f"{label} exceeds {MAX_EVENT_BYTES} bytes")
    if b"\x00" in raw:
        raise CompactPairError(f"{label} contains NUL")
    try:
        return raw.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise CompactPairError(f"{label} is not UTF-8") from exc


def _one(lines: list[str], prefix: str, label: str) -> str:
    values = [line[len(prefix) :] for line in lines if line.startswith(prefix)]
    if len(values) != 1:
        state = "missing" if not values else "duplicate"
        raise CompactPairError(f"{state} {label}")
    value = values[0]
    if not value or value != value.strip():
        raise CompactPairError(f"invalid {label}")
    return value


def _section(lines: list[str], heading: str) -> list[str]:
    positions = [index for index, line in enumerate(lines) if line == heading]
    if len(positions) != 1:
        state = "missing" if not positions else "duplicate"
        raise CompactPairError(f"{state} {heading}")
    body: list[str] = []
    for line in lines[positions[0] + 1 :]:
        if line.startswith("## ") or line.startswith("Cursor at send:"):
            break
        body.append(line)
    while body and not body[0]:
        body.pop(0)
    while body and not body[-1]:
        body.pop()
    return body


def _identity(value: str, label: str) -> str:
    if len(value) > 120 or any(ord(character) < 0x20 for character in value):
        raise CompactPairError(f"invalid {label}")
    return value


def _finding_refs(lines: list[str], *, required: bool) -> tuple[str, ...]:
    body = _section_optional(lines, "## Finding Refs")
    if body is None:
        if required:
            raise CompactPairError("missing ## Finding Refs")
        return ()
    values: list[str] = []
    for line in body:
        if not line.startswith("- "):
            raise CompactPairError("Finding Refs must contain only '- reference' entries")
        value = line[2:]
        if not protocol_mailbox.immutable_reference_is_canonical(value):
            raise CompactPairError("finding refs must use immutable full-SHA paths or digests")
        values.append(value)
    if len(values) != len(set(values)):
        raise CompactPairError("finding refs must be unique")
    return tuple(values)


def _envelope_sender(text: str) -> str:
    values = re.findall(r"\*\*From:\*\* ([a-z0-9]+) \(online\)", text)
    if len(values) != 1:
        raise CompactPairError("missing or duplicate envelope sender")
    return values[0]


# ARCHITECTURE.md pins the public entry-point locations as smoke evidence.
# Keep parser helpers below validate_report when their internal shape grows.
# This preserves factual anchors without changing the public call surface.
# The ordering is intentional; Python resolves these helpers when called.
# Update the architecture anchor only for a genuine public-surface move.


def parse_verify_request(
    root: Path, request_path: str | os.PathLike[str], trigger_commit: str
) -> VerifyRequest:
    root = root.resolve()
    path = _repo_path(root, request_path)
    match = REQUEST_RE.fullmatch(path)
    if match is None:
        raise CompactPairError("verify-request path is not canonical")
    trigger = _full_commit(root, trigger_commit, "request trigger")
    change = _git(
        root,
        "diff-tree",
        "--root",
        "--no-commit-id",
        "--name-status",
        "-r",
        trigger,
        "--",
        path,
    ).decode("utf-8", errors="strict").splitlines()
    if change != [f"A\t{path}"]:
        raise CompactPairError("verify-request must be added by trigger commit")
    raw = _git(root, "show", f"{trigger}:{path}")
    text = _decode(raw, "verify-request")
    lines = text.splitlines()
    if lines.count("Event type: verify-request") != 1:
        raise CompactPairError("missing or duplicate Event type: verify-request")
    head = _full_commit(root, _one(lines, "Reviewed head: ", "Reviewed head"), "Reviewed head")
    base = _full_commit(root, _one(lines, "Reviewed base: ", "Reviewed base"), "Reviewed base")
    author = _one(lines, "Author seat: ", "Author seat")
    assigned = _one(lines, "Assigned operator: ", "Assigned operator")
    if author not in PAIR_SEATS or assigned not in OPERATOR_SEATS:
        raise CompactPairError("request author or assigned reviewer is not a pair seat")
    if author != match.group("author") or _envelope_sender(text) != author:
        raise CompactPairError("Author seat does not match verify-request envelope/path")
    if assigned != match.group("operator"):
        raise CompactPairError("Assigned operator does not match verify-request path")
    if head == trigger or not _is_ancestor(root, head, trigger):
        raise CompactPairError("request trigger must be strictly after Reviewed head")
    if base == head or not _is_ancestor(root, base, head):
        raise CompactPairError("Reviewed base must be a strict ancestor of Reviewed head")
    legacy = _section_optional(lines, "## Finding Refs") is None
    if legacy and not _is_frozen_verbose_blob(root, path, raw):
        raise CompactPairError("missing ## Finding Refs")
    outcome_heading = "## Acceptance Question" if legacy else "## Outcome"
    outcome = "\n".join(_section(lines, outcome_heading)).strip()
    if not outcome:
        raise CompactPairError(f"{outcome_heading[3:]} must be nonempty")
    return VerifyRequest(
        path=path,
        trigger_commit=trigger,
        reviewed_head=head,
        reviewed_base=base,
        author_seat=author,
        author_model=_identity(_one(lines, "Author model: ", "Author model"), "Author model"),
        assigned_operator=assigned,
        outcome=outcome,
        finding_refs=_finding_refs(lines, required=not legacy),
    )


def _read_regular(root: Path, path: str) -> bytes:
    current = root.resolve()
    for component in PurePosixPath(path).parts[:-1]:
        current = current / component
        if current.is_symlink():
            raise CompactPairError("artifact path traverses a symlink")
    flags = os.O_RDONLY | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0)
    descriptor = os.open(root / path, flags)
    try:
        opened = os.fstat(descriptor)
        if not stat.S_ISREG(opened.st_mode) or opened.st_size > MAX_EVENT_BYTES:
            raise CompactPairError("artifact is not one bounded regular file")
        raw = os.read(descriptor, opened.st_size + 1)
        after = os.fstat(descriptor)
        if len(raw) != opened.st_size or (opened.st_dev, opened.st_ino, opened.st_size) != (
            after.st_dev,
            after.st_ino,
            after.st_size,
        ):
            raise CompactPairError("artifact changed while reading")
        return raw
    finally:
        os.close(descriptor)


def _parse_verification_report_bytes(root: Path, path: str, raw: bytes) -> VerificationReport:
    match = REPORT_RE.fullmatch(path)
    if match is None:
        raise CompactPairError("verification-report path is not canonical Operator output")
    text = _decode(raw, "verification-report")
    lines = text.splitlines()
    if lines.count("Event type: verification-report") != 1:
        raise CompactPairError("missing or duplicate Event type: verification-report")
    verdict = _one(lines, "VERDICT: ", "VERDICT")
    if verdict not in {"GO", "NITS", "FAIL"}:
        raise CompactPairError("VERDICT must be GO, NITS, or FAIL")
    request_ref = _one(lines, "Verification request: ", "Verification request")
    request_path, separator, request_commit = request_ref.rpartition("@")
    if not separator:
        raise CompactPairError("Verification request must bind path@commit")
    request_path = _repo_path(root, request_path)
    if REQUEST_RE.fullmatch(request_path) is None:
        raise CompactPairError("Verification request path is not canonical")
    if SHA_RE.fullmatch(request_commit) is None:
        raise CompactPairError("request commit must be one full lowercase commit SHA")
    head = _one(lines, "Reviewed head: ", "Reviewed head")
    base = _one(lines, "Reviewed base: ", "Reviewed base")
    if SHA_RE.fullmatch(head) is None or SHA_RE.fullmatch(base) is None:
        raise CompactPairError("Reviewed base/head must be full lowercase commit SHAs")
    legacy = _section_optional(lines, "## Finding Refs") is None
    if legacy and not _is_frozen_verbose_blob(root, path, raw):
        raise CompactPairError("missing ## Finding Refs")
    finding_refs = _finding_refs(lines, required=not legacy)
    return VerificationReport(
        path=path,
        verdict=verdict,
        request_path=request_path,
        request_commit=request_commit,
        reviewed_head=head,
        reviewed_base=base,
        reviewer_seat=_one(lines, "Reviewer seat: ", "Reviewer seat"),
        reviewer_model=_identity(_one(lines, "Reviewer model: ", "Reviewer model"), "Reviewer model"),
        evidence=_evidence(lines),
        finding_refs=finding_refs,
        finding_dispositions=_finding_dispositions(
            lines, finding_refs, required=not legacy
        ),
        filename_reviewer=match.group("reviewer"),
        envelope_sender=_envelope_sender(text),
    )


def parse_verification_report(
    root: Path, report_path: str | os.PathLike[str]
) -> VerificationReport:
    root = root.resolve()
    path = _repo_path(root, report_path)
    return _parse_verification_report_bytes(root, path, _read_regular(root, path))


def parse_verification_report_candidate(
    root: Path,
    candidate_path: str | os.PathLike[str],
    final_path: str | os.PathLike[str],
) -> VerificationReport:
    """Parse candidate bytes using the intended final path as identity authority."""
    root = root.resolve()
    candidate = _repo_path(root, candidate_path)
    final = _repo_path(root, final_path)
    return _parse_verification_report_bytes(root, final, _read_regular(root, candidate))



def validate_report(root: Path, report: VerificationReport) -> list[str]:
    root = root.resolve()
    violations: list[str] = []
    try:
        request = parse_verify_request(root, report.request_path, report.request_commit)
    except CompactPairError as exc:
        violations.append(f"request binding invalid: {exc}")
        return violations
    if report.reviewer_seat != report.filename_reviewer or report.envelope_sender != report.filename_reviewer:
        violations.append("reviewer seat does not match verification-report envelope/path")
    if report.reviewer_seat != request.assigned_operator:
        violations.append("reviewer seat is not the assigned Operator")
    if report.reviewer_seat == request.author_seat:
        violations.append("reviewer seat equals author seat")
    if report.reviewer_model.casefold() == request.author_model.casefold():
        violations.append("reviewer model equals author model")
    if report.reviewed_head != request.reviewed_head:
        violations.append("report Reviewed head does not match request")
    if report.reviewed_base != request.reviewed_base:
        violations.append("report Reviewed base does not match request")
    if report.finding_refs != request.finding_refs:
        violations.append("report finding refs changed from request")
    if report.verdict == "GO" and (
        not any(line.startswith("$ ") for line in report.evidence)
        or not any(line.startswith("→ ") for line in report.evidence)
    ):
        violations.append("GO requires evidence")
    if report.verdict == "GO" and any(
        disposition == "unresolved-hard-boundary"
        for _, disposition in report.finding_dispositions
    ):
        violations.append("GO cannot carry unresolved hard-boundary findings")
    try:
        _full_commit(root, request.reviewed_base, "Reviewed base")
        _full_commit(root, request.reviewed_head, "Reviewed head")
    except CompactPairError as exc:
        violations.append(f"reviewed range unavailable: {exc}")
    return violations


def _section_optional(lines: list[str], heading: str) -> list[str] | None:
    positions = [index for index, line in enumerate(lines) if line == heading]
    if len(positions) > 1:
        raise CompactPairError(f"duplicate {heading}")
    if not positions:
        return None
    return _section(lines, heading)


def _finding_dispositions(
    lines: list[str], finding_refs: tuple[str, ...], *, required: bool
) -> tuple[tuple[str, str], ...]:
    body = _section_optional(lines, "## Finding Dispositions")
    if body is None:
        if required:
            raise CompactPairError("missing ## Finding Dispositions")
        return ()
    values: list[tuple[str, str]] = []
    for line in body:
        if not line.startswith("- "):
            raise CompactPairError(
                "Finding Dispositions must contain only '- reference: disposition' entries"
            )
        reference, separator, disposition = line[2:].rpartition(": ")
        if (
            not separator
            or not protocol_mailbox.immutable_reference_is_canonical(reference)
            or disposition not in FINDING_DISPOSITIONS
        ):
            raise CompactPairError("invalid finding disposition")
        values.append((reference, disposition))
    if len(values) != len(finding_refs) or tuple(ref for ref, _ in values) != finding_refs:
        raise CompactPairError("report requires exactly one disposition for each finding ref")
    return tuple(values)


def _evidence(lines: list[str]) -> tuple[str, ...]:
    body = _section_optional(lines, "## Evidence")
    if body is None:
        return ()
    return tuple(line for line in body if line.strip())


def _git_blob(root: Path, commit: str, path: str) -> bytes | None:
    environment = {
        key: value for key, value in os.environ.items() if not key.startswith("GIT_")
    }
    completed = subprocess.run(
        ["/usr/bin/git", "--no-replace-objects", "show", f"{commit}:{path}"],
        cwd=root,
        env=environment,
        capture_output=True,
        check=False,
    )
    return completed.stdout if completed.returncode == 0 else None


def _is_frozen_verbose_blob(root: Path, path: str, raw: bytes) -> bool:
    return _git_blob(root, LEGACY_VERBOSE_CUTOFF, path) == raw


def _main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="compact_pair_loop.py")
    subparsers = parser.add_subparsers(dest="command", required=True)
    candidate = subparsers.add_parser("validate-candidate")
    candidate.add_argument("--repo-root", required=True, type=Path)
    candidate.add_argument("--candidate", required=True)
    candidate.add_argument("--final-relative", required=True)
    arguments = parser.parse_args(argv)
    try:
        report = parse_verification_report_candidate(
            arguments.repo_root,
            arguments.candidate,
            arguments.final_relative,
        )
        violations = validate_report(arguments.repo_root, report)
        if violations:
            raise CompactPairError("; ".join(violations))
    except (CompactPairError, OSError) as exc:
        print(f"compact-pair validation failed: {exc}", file=sys.stderr)
        return 1
    print("compact-pair validation passed")
    return 0


if __name__ == "__main__":
    sys.exit(_main())
