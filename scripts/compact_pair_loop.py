#!/usr/bin/env python3
"""Small, fail-closed validator for the current Director→Operator pair loop."""

from __future__ import annotations

import os
import re
import stat
import subprocess
from dataclasses import dataclass
from pathlib import Path, PurePosixPath


SHA_RE = re.compile(r"[0-9a-f]{40}")
REQUEST_RE = re.compile(
    r"coordination/mailbox/sent/"
    r"[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}-[0-9]{2}-[0-9]{2}Z-"
    r"(?P<author>director2?)-to-(?P<operator>operator2?)-verify-request\.md"
)
REPORT_RE = re.compile(
    r"coordination/mailbox/sent/"
    r"[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}-[0-9]{2}-[0-9]{2}Z-"
    r"(?P<reviewer>operator2?)-to-(?:director2?|operator2?|coordinator2?|all)-"
    r"verification-report\.md"
)
MAX_EVENT_BYTES = 262_144


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
    question: str
    allowed_paths: tuple[str, ...]
    commands: tuple[str, ...]


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
    reviewer_harness: str
    reviewer_context: str
    allowed_paths: tuple[str, ...]
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


def _allowed_paths(lines: list[str]) -> tuple[str, ...]:
    body = _section(lines, "## Allowed Paths")
    values: list[str] = []
    for line in body:
        if not line.startswith("- "):
            raise CompactPairError("Allowed Paths must contain only '- path' entries")
        value = line[2:]
        directory = value.endswith("/")
        raw = value[:-1] if directory else value
        pure = PurePosixPath(raw)
        if (
            not raw
            or raw.startswith("/")
            or "\\" in raw
            or any(part in {"", ".", ".."} for part in pure.parts)
            or pure.as_posix() != raw
            or any(character in value for character in "*?[]")
        ):
            raise CompactPairError("invalid allowed path")
        values.append(raw + ("/" if directory else ""))
    if not values or len(values) != len(set(values)):
        raise CompactPairError("allowed paths must be nonempty and unique")
    return tuple(values)


def _commands(lines: list[str]) -> tuple[str, ...]:
    body = _section(lines, "## Verification Commands")
    commands = [line[2:] for line in body if line.startswith("$ ")]
    if len(commands) != len(body) or not commands or len(commands) != len(set(commands)):
        raise CompactPairError("verification commands must be nonempty unique '$ command' entries")
    return tuple(commands)


def _envelope_sender(text: str) -> str:
    values = re.findall(r"\*\*From:\*\* ([a-z0-9]+) \(online\)", text)
    if len(values) != 1:
        raise CompactPairError("missing or duplicate envelope sender")
    return values[0]


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
    text = _decode(_git(root, "show", f"{trigger}:{path}"), "verify-request")
    lines = text.splitlines()
    if lines.count("Event type: verify-request") != 1:
        raise CompactPairError("missing or duplicate Event type: verify-request")
    head = _full_commit(root, _one(lines, "Reviewed head: ", "Reviewed head"), "Reviewed head")
    base = _full_commit(root, _one(lines, "Reviewed base: ", "Reviewed base"), "Reviewed base")
    author = _one(lines, "Author seat: ", "Author seat")
    assigned = _one(lines, "Assigned operator: ", "Assigned operator")
    if author != match.group("author") or _envelope_sender(text) != author:
        raise CompactPairError("Author seat does not match verify-request envelope/path")
    if assigned != match.group("operator"):
        raise CompactPairError("Assigned operator does not match verify-request path")
    if head == trigger or not _is_ancestor(root, head, trigger):
        raise CompactPairError("request trigger must be strictly after Reviewed head")
    if base == head or not _is_ancestor(root, base, head):
        raise CompactPairError("Reviewed base must be a strict ancestor of Reviewed head")
    question_lines = _section(lines, "## Acceptance Question")
    question = "\n".join(question_lines).strip()
    if not question:
        raise CompactPairError("Acceptance Question must be nonempty")
    return VerifyRequest(
        path=path,
        trigger_commit=trigger,
        reviewed_head=head,
        reviewed_base=base,
        author_seat=author,
        author_model=_identity(_one(lines, "Author model: ", "Author model"), "Author model"),
        assigned_operator=assigned,
        question=question,
        allowed_paths=_allowed_paths(lines),
        commands=_commands(lines),
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


def parse_verification_report(
    root: Path, report_path: str | os.PathLike[str]
) -> VerificationReport:
    root = root.resolve()
    path = _repo_path(root, report_path)
    match = REPORT_RE.fullmatch(path)
    if match is None:
        raise CompactPairError("verification-report path is not canonical Operator output")
    text = _decode(_read_regular(root, path), "verification-report")
    lines = text.splitlines()
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
    return VerificationReport(
        path=path,
        verdict=verdict,
        request_path=request_path,
        request_commit=request_commit,
        reviewed_head=head,
        reviewed_base=base,
        reviewer_seat=_one(lines, "Reviewer seat: ", "Reviewer seat"),
        reviewer_model=_identity(_one(lines, "Reviewer model: ", "Reviewer model"), "Reviewer model"),
        reviewer_harness=_identity(_one(lines, "Verification harness: ", "Verification harness"), "Verification harness"),
        reviewer_context=_identity(_one(lines, "Verification context: ", "Verification context"), "Verification context"),
        allowed_paths=_allowed_paths(lines),
        filename_reviewer=match.group("reviewer"),
        envelope_sender=_envelope_sender(text),
    )


def _path_allowed(path: str, allowed_paths: tuple[str, ...]) -> bool:
    return any(
        path == allowed.rstrip("/")
        or (allowed.endswith("/") and path.startswith(allowed))
        for allowed in allowed_paths
    )


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
    if report.allowed_paths != request.allowed_paths:
        violations.append("report allowed paths changed from request")
    try:
        changed = _git(
            root,
            "diff",
            "--name-only",
            "-z",
            request.reviewed_base,
            request.reviewed_head,
        ).split(b"\x00")
        changed_paths = [item.decode("utf-8") for item in changed if item]
    except (CompactPairError, UnicodeDecodeError) as exc:
        violations.append(f"reviewed range unavailable: {exc}")
    else:
        outside = [path for path in changed_paths if not _path_allowed(path, request.allowed_paths)]
        if outside:
            violations.append("reviewed range contains paths outside allowed paths: " + ", ".join(outside))
    return violations
