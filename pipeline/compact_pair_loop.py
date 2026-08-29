#!/usr/bin/env python3
"""Small, fail-closed validator for the current Director→Operator pair loop."""

from __future__ import annotations

import argparse
import hashlib
import os
import re
import stat
import subprocess
import sys
from collections.abc import Sequence
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath

import codex_protocol_model
import git_commit_projection
import protocol_mailbox


SHA_RE = re.compile(r"[0-9a-f]{40}")
REQUEST_RE = re.compile(
    r"coordination/mailbox/sent/"
    r"[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}-[0-9]{2}-[0-9]{2}Z-"
    r"(?P<author>codex|claude|agy|author|director2?|operator2?)-to-"
    r"(?P<operator>codex|claude|reviewer|operator2?)-verify-request\.md"
)
REPORT_RE = re.compile(
    r"coordination/mailbox/sent/"
    r"[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}-[0-9]{2}-[0-9]{2}Z-"
    r"(?P<reviewer>codex|claude|agy|reviewer|operator2?)-to-"
    r"(?P<recipient>codex|claude|agy|author|director2?|operator2?|coordinator2?|all)-"
    r"verification-report\.md"
)
MAX_EVENT_BYTES = 262_144
LEGACY_VERBOSE_CUTOFF = "ab7fd77081448008f1de30c17a8aaf156a9506c5"
# Last request published under the old same-repository-only base convention.
REMEDIATION_BASE_CUTOFF = "c04935f44c00e3146f429931c2a51637df4a3c1b"
_FROZEN_MODEL_LABEL_EXCEPTION = {
    "path": (
        "coordination/mailbox/sent/"
        "2026-08-01T05-02-15Z-operator-to-director2-verification-report.md"
    ),
    "introduction": "8471c6d6c35daa74dd24cc24d6ece3eea48f3f22",
    "sha256": "90586eb9d2399ed69a2f1bc0af7bb7c43ba9187e61fedc734e58fc32ce21f48c",
}
PAIR_SEATS = frozenset(protocol_mailbox.SEATS)
OPERATOR_SEATS = frozenset({"operator", "operator2"})
# Reader-only compatibility for current formal-review responsibility labels.
_READ_PAIR_SEATS = PAIR_SEATS | {"author", *protocol_mailbox.APP_MEMBERS}
_READ_OPERATOR_SEATS = OPERATOR_SEATS | {"reviewer", *protocol_mailbox.FORMAL_REVIEWERS}
MATERIAL_BEHAVIOR_RISK = codex_protocol_model.review_profile_for(
    "material-behavior"
).risk_class
HIGH_RISK_CONTROL = codex_protocol_model.review_profile_for(
    "high-risk-control"
).risk_class
ABUSE_ASSESSMENT_BOUND_TO_REQUEST = "bound-to-request"
FINDING_DISPOSITIONS = frozenset(
    {"addressed", "counter-evidence", "ordinary-risk", "unresolved-hard-boundary"}
)


class CompactPairError(ValueError):
    """A current pair artifact is malformed or lacks structural authority."""


@dataclass(frozen=True)
class VerifyRequest:
    path: str
    trigger_commit: str
    reviewed_repository: str | None
    reviewed_head: str
    reviewed_base: str
    author_seat: str
    author_model: str
    assigned_operator: str
    risk_class: str
    risk_class_explicit: bool
    abuse_class_assessment: tuple[str, ...]
    outcome: str
    finding_refs: tuple[str, ...]
    remediates_failed_report: tuple[str, str] | None
    historical_remediation_base_compatibility: bool = False


@dataclass(frozen=True)
class VerificationReport:
    path: str
    verdict: str
    request_path: str
    request_commit: str
    reviewed_repository: str | None
    reviewed_head: str
    reviewed_base: str
    reviewer_seat: str
    reviewer_model: str
    risk_class: str
    risk_class_explicit: bool
    abuse_class_assessment_binding: str | None
    evidence: tuple[str, ...]
    finding_refs: tuple[str, ...]
    finding_dispositions: tuple[tuple[str, str], ...]
    supersedes: tuple[str, str] | None
    filename_reviewer: str
    envelope_sender: str
    frozen_model_label_exception: bool
    historical_model_family_compatibility: bool


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


def _is_frozen_model_label_exception(root: Path, path: str, raw: bytes) -> bool:
    """Accept one immutable historical label without widening current grammar."""

    exception = _FROZEN_MODEL_LABEL_EXCEPTION
    if (
        path != exception["path"]
        or hashlib.sha256(raw).hexdigest() != exception["sha256"]
    ):
        return False
    # Reintroduction doctrine (protocol_mailbox): byte-identical restoration
    # is not mutation. Every introduction of the path — the pinned one and
    # any delete/revert reintroduction — must carry exactly the pinned
    # bytes, or the exception stays refused.
    try:
        introductions = protocol_mailbox.path_introduction_commits(root, path)
    except ValueError:
        return False
    if exception["introduction"] not in introductions:
        return False
    for commit in introductions:
        replayed = protocol_mailbox.committed_blob_or_none(root, commit, path)
        if (
            replayed is None
            or hashlib.sha256(replayed).hexdigest() != exception["sha256"]
        ):
            return False
    return True


def _is_historical_model_family_compatibility(
    root: Path, path: str, raw: bytes
) -> bool:
    """Keep exact retirement-boundary reports readable without new authority."""

    historical = protocol_mailbox.committed_blob_or_none(
        root,
        codex_protocol_model.CURRENT_REVIEW_FAMILY_CUTOVER,
        path,
    )
    return historical is not None and historical == raw


def _full_commit(
    root: Path,
    value: str,
    label: str,
    *,
    commit_projection: git_commit_projection.CommitGraphProjection | None = None,
    allow_git_fallback: bool = True,
) -> str:
    if SHA_RE.fullmatch(value) is None:
        raise CompactPairError(f"{label} must be one full lowercase commit SHA")
    if commit_projection is not None and commit_projection.matches_root(root):
        try:
            return commit_projection.require_commit(value, label)
        except git_commit_projection.CommitGraphProjectionError as exc:
            raise CompactPairError(str(exc)) from exc
    if not allow_git_fallback:
        raise CompactPairError(
            f"{label} cannot use a commit projection for the reviewed repository"
        )
    resolved = _git(root, "rev-parse", "--verify", f"{value}^{{commit}}").decode().strip()
    if resolved != value:
        raise CompactPairError(f"{label} commit does not resolve exactly")
    return value


def _resolve_rev(root: Path, value: str, label: str) -> str:
    """Resolve any git revision to the one full SHA it names right now.

    `_full_commit` deliberately refuses anything but a full SHA, because a
    committed artifact must never be re-resolvable. Composition is the opposite
    situation: the author names a revision before the artifact exists, so
    `HEAD~3` has to become a fixed SHA here rather than in the reader.
    """
    if not value or value.strip() != value or value.startswith("-"):
        raise CompactPairError(f"{label} must be one git revision")
    resolved = _git(root, "rev-parse", "--verify", f"{value}^{{commit}}").decode().strip()
    if SHA_RE.fullmatch(resolved) is None:
        raise CompactPairError(f"{label} did not resolve to one commit")
    return resolved


def _resolve_range(root: Path, base_rev: str, head_rev: str) -> tuple[str, str]:
    """Resolve both ends of a range, refusing one assembled from two states.

    Resolving base and head in separate Git calls lets a shared ref move
    between them, so `HEAD~1..HEAD` can yield ends read from different
    repository states. The result is still a strict ancestor pair and passes
    every later check, while binding concurrent work the author never reviewed.
    Reading each name twice around the pair turns that race into a refusal
    instead of a silently wider range.
    """
    first = (
        _resolve_rev(root, base_rev, "Reviewed base"),
        _resolve_rev(root, head_rev, "Reviewed head"),
    )
    second = (
        _resolve_rev(root, base_rev, "Reviewed base"),
        _resolve_rev(root, head_rev, "Reviewed head"),
    )
    if first != second:
        raise CompactPairError(
            "Reviewed base/head moved while composing; name explicit commit "
            "SHAs or re-run against a quiet repository"
        )
    return first


def _is_ancestor(
    root: Path,
    ancestor: str,
    descendant: str,
    *,
    commit_projection: git_commit_projection.CommitGraphProjection | None = None,
    allow_git_fallback: bool = True,
) -> bool:
    if commit_projection is not None and commit_projection.matches_root(root):
        try:
            return commit_projection.is_ancestor(ancestor, descendant)
        except git_commit_projection.CommitGraphProjectionError as exc:
            raise CompactPairError(str(exc)) from exc
    if not allow_git_fallback:
        raise CompactPairError(
            "ancestry cannot use a commit projection for the reviewed repository"
        )
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
    occurrences = normalized_field_occurrences(lines, label)
    if len(occurrences) != 1:
        state = "missing" if not occurrences else "duplicate"
        raise CompactPairError(f"{state} {label}")
    line = occurrences[0].strip()
    if line.startswith(("- ", "* ", "+ ")):
        line = line[2:].strip()
    if not line.startswith(prefix):
        raise CompactPairError(f"invalid {label}")
    value = line[len(prefix) :]
    if not value or value != value.strip():
        raise CompactPairError(f"invalid {label}")
    return value


def _section(lines: list[str], heading: str) -> list[str]:
    positions = _normalized_heading_occurrences(lines, heading)
    if len(positions) != 1:
        state = "missing" if not positions else "duplicate"
        raise CompactPairError(f"{state} {heading}")
    if lines[positions[0]] != heading:
        raise CompactPairError(f"invalid {heading}")
    body: list[str] = []
    for line in lines[positions[0] + 1 :]:
        if re.match(r"^\s*#{2,6}\s+\S", line) or line.startswith("Cursor at send:"):
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


def _object_exists(root: Path, commit: str, path: str) -> bool:
    """Whether `<commit>:<path>` names an object in *root*'s object store.

    `cat-file -e` answers by exit code and prints nothing, so no output is
    parsed. It reads the object store rather than any branch, which is what a
    finding reference needs: evidence committed on a branch invisible from the
    default one is still citable, and a fabricated commit is in no store at all.
    """
    try:
        completed = subprocess.run(
            ["/usr/bin/git", "--no-replace-objects", "cat-file", "-e", f"{commit}:{path}"],
            cwd=root,
            env={key: value for key, value in os.environ.items() if not key.startswith("GIT_")},
            capture_output=True,
            check=False,
        )
    except OSError:
        # A missing or unreadable cwd is "no such object", not a crash: the
        # caller turns False into a clean CompactPairError refusal.
        return False
    return completed.returncode == 0


def _require_path_references_resolve(
    root: Path, references: Sequence[str]
) -> None:
    """Refuse to compose a `path@commit` reference whose object does not exist.

    Canonical shape was the only check, and shape is satisfied by any forty hex
    characters. Three references were composed in one session that were
    well-formed and wrong: two named commits that do not exist, invented while
    transcribing, and the shape check accepted both. A reference is the one part
    of a request a reader cannot verify by reading the request, so a fabricated
    one is worse than a missing one — it reads as provenance and resolves to
    nothing.

    Deliberately only at compose time, not in the shared parser. Of 581
    `path@commit` references across committed events, 23 no longer resolve
    because the history they named was rewritten. Those are frozen artifacts and
    re-judging them would turn the historical-report gate in `governance_verify_all` red for
    events nobody can now amend. New references are the ones an author can still
    get right, and this is where they are written.

    The governance root is the ONLY store consulted. A finding reference is a
    fixed-writer mailbox path of this repository, and the round-one
    high-risk review showed why an either-root allowance is a laundering
    route, not a convenience: the reviewed-repository field comes from the
    candidate's own unvalidated bytes and `_reviewed_root` accepts any
    existing local path, so an author-controlled repository could make a
    fabricated reference "resolve". Cross-repository evidence travels as a
    `sha256:` digest, which the next paragraph is honest about.

    A `sha256:` digest is not checked, because nothing here holds the bytes it
    digests. That is a real gap and the reason it stays a gap is worth stating:
    the third bad reference of that session was a digest naming the wrong
    document, and this guard would not have caught it.
    """
    for reference in references:
        if "@" not in reference or reference.startswith("sha256:"):
            continue
        path, _, commit = reference.rpartition("@")
        if not path or not commit:
            continue
        if _object_exists(root, commit, path):
            continue
        raise CompactPairError(
            f"finding ref names an object that does not exist: {reference}. "
            "A reference is the part of a request a reader cannot check by "
            "reading it, so a well-formed one that resolves to nothing reads as "
            "provenance and is not. Verify the commit and path before citing them."
        )


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


def _risk_class(
    lines: list[str], *, allow_legacy_missing: bool, artifact: str
) -> tuple[str, bool]:
    value = _optional_one(lines, "Risk class: ", "Risk class")
    if value is None:
        if allow_legacy_missing:
            return HIGH_RISK_CONTROL, False
        raise CompactPairError(f"missing Risk class for new {artifact}")
    try:
        profile = codex_protocol_model.review_profile_for(value)
    except ValueError:
        profile = None
    if (
        profile is None
        or not profile.requires_non_author_review
        or not profile.requires_exact_range
        or profile.requires_live_authorization
    ):
        raise CompactPairError(
            "Risk class must be material-behavior or high-risk-control for formal review"
        )
    return value, True


def _abuse_class_assessment(
    lines: list[str], *, required: bool
) -> tuple[str, ...]:
    body = _section_optional(lines, "## Abuse Class Assessment")
    if body is None:
        if required:
            raise CompactPairError(
                "high-risk-control request requires nonempty ## Abuse Class Assessment"
            )
        return ()
    values: list[str] = []
    for line in body:
        if not line.startswith("- ") or not line[2:].strip():
            raise CompactPairError(
                "Abuse Class Assessment must contain only nonempty '- assessment' entries"
            )
        values.append(line[2:])
    if not values:
        raise CompactPairError("## Abuse Class Assessment must be nonempty")
    if len(values) != len(set(values)):
        raise CompactPairError("Abuse Class Assessment entries must be unique")
    return tuple(values)


def _envelope_sender(text: str) -> str:
    values = re.findall(r"\*\*From:\*\* ([a-z0-9]+) \(online\)", text)
    if len(values) != 1:
        raise CompactPairError("missing or duplicate envelope sender")
    return values[0]


# Public parser locations are stable architecture smoke anchors.
# Internal helper definitions intentionally follow validate_report.
def _parse_verify_request_bytes(
    root: Path,
    path: str,
    raw: bytes,
    *,
    trigger_commit: str,
    allow_frozen_legacy: bool,
    historical_remediation_base_compatibility: bool | None = None,
    commit_projection: git_commit_projection.CommitGraphProjection | None = None,
    allow_git_fallback: bool = True,
) -> VerifyRequest:
    """Parse request fields once for committed artifacts and new candidates."""

    match = REQUEST_RE.fullmatch(path)
    if match is None:
        raise CompactPairError("verify-request path is not canonical")
    filename_author = match.group("author")
    filename_reviewer = match.group("operator")
    app_route = (
        filename_author in protocol_mailbox.APP_MEMBERS
        or filename_reviewer in protocol_mailbox.APP_MEMBERS
    )
    if app_route:
        problem = protocol_mailbox.formal_review_route_problem(
            "verify-request", filename_author, filename_reviewer
        )
        if problem is not None:
            raise CompactPairError(problem)
    elif (filename_author == "author") != (filename_reviewer == "reviewer"):
        raise CompactPairError("verify-request cannot mix current and legacy roles")
    text = _decode(raw, "verify-request")
    lines = text.splitlines()
    if _one(lines, "Event type: ", "Event type") != "verify-request":
        raise CompactPairError("missing or duplicate Event type: verify-request")
    reviewed_repository = _optional_one(
        lines, "Reviewed repository: ", "Reviewed repository"
    )
    if reviewed_repository is not None:
        _reviewed_repository_path(reviewed_repository)
    head = _one(lines, "Reviewed head: ", "Reviewed head")
    base = _one(lines, "Reviewed base: ", "Reviewed base")
    if SHA_RE.fullmatch(head) is None or SHA_RE.fullmatch(base) is None:
        raise CompactPairError("Reviewed base/head must be full lowercase commit SHAs")
    author = _one(lines, "Author seat: ", "Author seat")
    assigned = _one(lines, "Assigned operator: ", "Assigned operator")
    if author not in _READ_PAIR_SEATS or assigned not in _READ_OPERATOR_SEATS:
        raise CompactPairError("request author or assigned reviewer is not a pair seat")
    if author != filename_author or _envelope_sender(text) != author:
        raise CompactPairError("Author seat does not match verify-request envelope/path")
    if assigned != filename_reviewer:
        raise CompactPairError("Assigned operator does not match verify-request path")
    risk_class, risk_class_explicit = _risk_class(
        lines,
        allow_legacy_missing=allow_frozen_legacy,
        artifact="verify-request",
    )
    profile = codex_protocol_model.review_profile_for(risk_class)
    abuse_class_assessment = _abuse_class_assessment(
        lines,
        required=profile.requires_abuse_class_assessment and risk_class_explicit,
    )
    legacy = (
        allow_frozen_legacy
        and _git_blob(root, LEGACY_VERBOSE_CUTOFF, path) is not None
        and _section_optional(lines, "## Finding Refs") is None
    )
    if legacy and not _is_ancestor(
        root,
        trigger_commit,
        LEGACY_VERBOSE_CUTOFF,
        commit_projection=commit_projection,
        allow_git_fallback=allow_git_fallback,
    ):
        raise CompactPairError("missing ## Finding Refs or frozen historical provenance")
    outcome_heading = "## Acceptance Question" if legacy else "## Outcome"
    if _section_optional(lines, outcome_heading) is not None:
        outcome = "\n".join(_section(lines, outcome_heading)).strip()
    elif _section_optional(lines, "### Summary of Changes") is not None:
        outcome = "\n".join(_section(lines, "### Summary of Changes")).strip()
    elif _section_optional(lines, "## Summary of Changes") is not None:
        outcome = "\n".join(_section(lines, "## Summary of Changes")).strip()
    else:
        raise CompactPairError(f"{outcome_heading[3:]} must be nonempty")
    if not outcome:
        raise CompactPairError(f"{outcome_heading[3:]} must be nonempty")
    return VerifyRequest(
        path=path,
        trigger_commit=trigger_commit,
        reviewed_repository=reviewed_repository,
        reviewed_head=head,
        reviewed_base=base,
        author_seat=author,
        author_model=_identity(_one(lines, "Author model: ", "Author model"), "Author model"),
        assigned_operator=assigned,
        risk_class=risk_class,
        risk_class_explicit=risk_class_explicit,
        abuse_class_assessment=abuse_class_assessment,
        outcome=outcome,
        finding_refs=_finding_refs(lines, required=False),
        remediates_failed_report=_remediates_failed_report(root, lines),
        historical_remediation_base_compatibility=(
            _git_blob(root, REMEDIATION_BASE_CUTOFF, path) == raw
            if historical_remediation_base_compatibility is None
            else historical_remediation_base_compatibility
        ),
    )


def parse_verify_request_structure(
    root: Path, request_path: str | os.PathLike[str], trigger_commit: str
) -> VerifyRequest:
    """Validate immutable request bytes and fields without opening the reviewed repo."""
    root = root.resolve()
    path = _repo_path(root, request_path)
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
    return _parse_verify_request_bytes(
        root,
        path,
        raw,
        trigger_commit=trigger,
        allow_frozen_legacy=True,
    )


def parse_verify_request_committed_bytes(
    root: Path,
    request_path: str | os.PathLike[str],
    trigger_commit: str,
    raw: bytes,
    *,
    allow_frozen_legacy: bool = True,
    historical_remediation_base_compatibility: bool | None = None,
    commit_projection: git_commit_projection.CommitGraphProjection | None = None,
    allow_git_fallback: bool = True,
) -> VerifyRequest:
    """Parse bytes from a caller's committed mailbox projection."""

    root = root.resolve()
    path = _repo_path(root, request_path)
    if SHA_RE.fullmatch(trigger_commit) is None:
        raise CompactPairError("request trigger must be one full lowercase commit SHA")
    return _parse_verify_request_bytes(
        root,
        path,
        raw,
        trigger_commit=trigger_commit,
        allow_frozen_legacy=allow_frozen_legacy,
        historical_remediation_base_compatibility=(
            historical_remediation_base_compatibility
        ),
        commit_projection=commit_projection,
        allow_git_fallback=allow_git_fallback,
    )


def _validate_request_range(
    root: Path,
    request: VerifyRequest,
    *,
    commit_projection: git_commit_projection.CommitGraphProjection | None = None,
    allow_git_fallback: bool = True,
) -> None:
    root = root.resolve()
    reviewed_root = _reviewed_root(
        root,
        request.reviewed_repository,
        commit_projection=commit_projection,
        allow_git_fallback=allow_git_fallback,
    )
    head = _full_commit(
        reviewed_root,
        request.reviewed_head,
        "Reviewed head",
        commit_projection=commit_projection,
        allow_git_fallback=allow_git_fallback,
    )
    base = _full_commit(
        reviewed_root,
        request.reviewed_base,
        "Reviewed base",
        commit_projection=commit_projection,
        allow_git_fallback=allow_git_fallback,
    )
    if reviewed_root == root and (
        head == request.trigger_commit
        or not _is_ancestor(
            root,
            head,
            request.trigger_commit,
            commit_projection=commit_projection,
            allow_git_fallback=allow_git_fallback,
        )
    ):
        raise CompactPairError("request trigger must be strictly after Reviewed head")
    if base == head or not _is_ancestor(
        reviewed_root,
        base,
        head,
        commit_projection=commit_projection,
        allow_git_fallback=allow_git_fallback,
    ):
        raise CompactPairError("Reviewed base must be a strict ancestor of Reviewed head")


def validate_request_range(
    root: Path,
    request: VerifyRequest,
    *,
    commit_projection: git_commit_projection.CommitGraphProjection | None = None,
    allow_git_fallback: bool = True,
) -> list[str]:
    """Validate one already parsed request's repository and exact range."""

    try:
        _validate_request_range(
            root,
            request,
            commit_projection=commit_projection,
            allow_git_fallback=allow_git_fallback,
        )
    except CompactPairError as exc:
        return [str(exc)]
    return []


def parse_verify_request(
    root: Path, request_path: str | os.PathLike[str], trigger_commit: str
) -> VerifyRequest:
    request = parse_verify_request_structure(root, request_path, trigger_commit)
    _validate_request_range(root, request)
    return request


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


def parse_verify_request_candidate(
    root: Path,
    candidate_path: str | os.PathLike[str],
    final_path: str | os.PathLike[str],
) -> VerifyRequest:
    """Parse new request bytes using the intended final path as identity authority."""

    root = root.resolve()
    candidate = _repo_path(root, candidate_path)
    final = _repo_path(root, final_path)
    request = _parse_verify_request_bytes(
        root,
        final,
        _read_regular(root, candidate),
        trigger_commit="",
        allow_frozen_legacy=False,
        historical_remediation_base_compatibility=False,
    )
    # Publication-time resolvability. The compose hook alone left the route
    # the defect actually travels: a hand-written body through send-event
    # (measured 2026-07-31 — two fabricated Finding Ref tails published that
    # way; one caught only by post-compose hand verification). Candidates
    # only: committed events use the committed parsers, which stay untouched
    # so the historical gates keep judging frozen artifacts as frozen.
    _require_path_references_resolve(root, request.finding_refs)
    if request.remediates_failed_report is not None:
        _require_path_references_resolve(
            root,
            (f"{request.remediates_failed_report[0]}@{request.remediates_failed_report[1]}",),
        )
    return request


def validate_request_candidate(root: Path, request: VerifyRequest) -> list[str]:
    """Validate a candidate's reviewed range before it can be finalized."""

    if not codex_protocol_model.model_is_current_author(request.author_model):
        return [
            "Author model must resolve to a currently admitted author model "
            "for a new verify-request"
        ]
    if request.author_seat in protocol_mailbox.APP_MEMBERS and not (
        codex_protocol_model.model_family_matches_member(
            request.author_model, request.author_seat
        )
    ):
        return ["author model family does not match author member"]
    try:
        reviewed_root = _reviewed_root(root.resolve(), request.reviewed_repository)
        base = _full_commit(reviewed_root, request.reviewed_base, "Reviewed base")
        head = _full_commit(reviewed_root, request.reviewed_head, "Reviewed head")
        if base == head or not _is_ancestor(reviewed_root, base, head):
            raise CompactPairError(
                "Reviewed base must be a strict ancestor of Reviewed head"
            )
    except CompactPairError as exc:
        return [str(exc)]
    return _remediation_request_target_violations(root.resolve(), request)


def _compose_self_check(
    root: Path, body: str, *, author_seat: str, assigned_operator: str
) -> None:
    """Refuse a body this module would reject once `send-event` wraps it.

    The writer validates the finished candidate, never the body it was handed,
    so a composer that only checked its own output would still emit requests
    that die at publication. Simulating the exact envelope, footer and path the
    writer builds is what makes the check mean the same thing.
    """
    stamp = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H-%M-%SZ")
    final = (
        f"coordination/mailbox/sent/{stamp}-{author_seat}"
        f"-to-{assigned_operator}-verify-request.md"
    )
    when = f"{stamp[:11]}{stamp[11:19].replace('-', ':')}Z"
    candidate = (
        f"# Compose: verify-request self-check\n\n"
        f"**When:** {when} · **From:** {author_seat} (online)\n\n"
        f"{body}\n\nCursor at send: cursorless\n"
    ).encode("utf-8")
    if len(candidate) > MAX_EVENT_BYTES:
        raise CompactPairError("composed request exceeds the event size limit")
    request = _parse_verify_request_bytes(
        root.resolve(),
        final,
        candidate,
        trigger_commit="",
        allow_frozen_legacy=False,
        historical_remediation_base_compatibility=False,
    )
    violations = validate_request_candidate(root, request)
    if violations:
        raise CompactPairError("; ".join(violations))


def compose_request(
    root: Path,
    *,
    author_seat: str,
    author_model: str,
    assigned_operator: str,
    risk_class: str,
    base_rev: str,
    head_rev: str,
    outcome: str,
    reviewed_repository: str | None = None,
    abuse_assessments: Sequence[str] = (),
    finding_refs: Sequence[str] = (),
    remediates_failed_report: str | None = None,
) -> str:
    """Build one verify-request body that this module's own parser accepts.

    The request format lives only in `_parse_verify_request_bytes`, so authors
    have had to reconstruct it by reading the parser and copying an older
    event. Generating the body from the same constants closes that gap: the
    author supplies the judgement — seats, risk class, outcome — and everything
    git already knows is resolved here instead of transcribed by hand.
    """
    route_problem = protocol_mailbox.formal_review_route_problem(
        "verify-request", author_seat, assigned_operator
    )
    if route_problem is not None:
        raise CompactPairError(route_problem)
    try:
        profile = codex_protocol_model.review_profile_for(risk_class)
    except ValueError:
        profile = None
    if (
        profile is None
        or not profile.requires_non_author_review
        or not profile.requires_exact_range
        or profile.requires_live_authorization
    ):
        raise CompactPairError(
            f"Risk class must be {MATERIAL_BEHAVIOR_RISK} or {HIGH_RISK_CONTROL}"
        )

    author_model = _identity(author_model, "Author model")
    if not codex_protocol_model.model_is_current_author(author_model):
        raise CompactPairError(
            "Author model must resolve to a currently admitted author model "
            "for a new verify-request"
        )
    if not codex_protocol_model.model_family_matches_member(author_model, author_seat):
        raise CompactPairError("author model family does not match author member")
    outcome = outcome.strip()
    if not outcome:
        raise CompactPairError("Outcome must be nonempty")

    assessments = [entry.strip() for entry in abuse_assessments if entry.strip()]
    if profile.requires_abuse_class_assessment and not assessments:
        raise CompactPairError(
            f"{HIGH_RISK_CONTROL} requires a nonempty Abuse Class Assessment"
        )
    references = [entry.strip() for entry in finding_refs if entry.strip()]
    for reference in references:
        if not protocol_mailbox.immutable_reference_is_canonical(reference):
            raise CompactPairError(
                f"finding refs must use immutable full-SHA paths or digests: {reference}"
            )
    if len(references) != len(set(references)):
        raise CompactPairError("finding refs must be unique")

    remediation_ref = None
    if remediates_failed_report is not None:
        remediation_ref = _parse_report_reference(
            root.resolve(),
            remediates_failed_report,
            "Remediates failed report",
        )

    reviewed_root = _reviewed_root(root.resolve(), reviewed_repository)
    _require_path_references_resolve(root.resolve(), references)
    base, head = _resolve_range(reviewed_root, base_rev, head_rev)

    lines = ["Event type: verify-request"]
    if reviewed_repository is not None:
        lines.append(f"Reviewed repository: {reviewed_repository}")
    lines += [
        f"Reviewed base: {base}",
        f"Reviewed head: {head}",
        f"Author seat: {author_seat}",
        f"Author model: {author_model}",
        f"Assigned operator: {assigned_operator}",
        f"Risk class: {risk_class}",
    ]
    if remediation_ref is not None:
        lines.append(
            "Remediates failed report: "
            f"{remediation_ref[0]}@{remediation_ref[1]}"
        )
    lines += ["", "## Outcome", "", outcome]
    if assessments:
        lines += ["", "## Abuse Class Assessment", ""]
        lines += [f"- {entry}" for entry in assessments]
    if references:
        lines += ["", "## Finding Refs", ""]
        lines += [f"- {entry}" for entry in references]

    body = "\n".join(lines)
    _compose_self_check(
        root, body, author_seat=author_seat, assigned_operator=assigned_operator
    )
    return body


def _parse_verification_report_bytes(
    root: Path,
    path: str,
    raw: bytes,
    *,
    allow_legacy_missing_risk: bool = True,
    frozen_legacy: bool | None = None,
    historical_model_family_compatibility: bool | None = None,
) -> VerificationReport:
    match = REPORT_RE.fullmatch(path)
    if match is None:
        raise CompactPairError("verification-report path is not canonical Operator output")
    filename_reviewer = match.group("reviewer")
    filename_recipient = match.group("recipient")
    app_route = (
        filename_reviewer in protocol_mailbox.APP_MEMBERS
        or filename_recipient in protocol_mailbox.APP_MEMBERS
    )
    if app_route:
        problem = protocol_mailbox.formal_review_route_problem(
            "verification-report", filename_reviewer, filename_recipient
        )
        if problem is not None:
            raise CompactPairError(problem)
    elif filename_recipient != "all" and (
        (filename_reviewer == "reviewer") != (filename_recipient == "author")
    ):
        raise CompactPairError("verification-report cannot mix current and legacy roles")
    text = _decode(raw, "verification-report")
    lines = text.splitlines()
    if _one(lines, "Event type: ", "Event type") != "verification-report":
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
    reviewed_repository = _optional_one(
        lines, "Reviewed repository: ", "Reviewed repository"
    )
    head = _one(lines, "Reviewed head: ", "Reviewed head")
    base = _one(lines, "Reviewed base: ", "Reviewed base")
    if SHA_RE.fullmatch(head) is None or SHA_RE.fullmatch(base) is None:
        raise CompactPairError("Reviewed base/head must be full lowercase commit SHAs")
    risk_class, risk_class_explicit = _risk_class(
        lines,
        allow_legacy_missing=allow_legacy_missing_risk,
        artifact="verification-report",
    )
    abuse_class_assessment_binding = _optional_one(
        lines, "Abuse Class Assessment: ", "Abuse Class Assessment"
    )
    profile = codex_protocol_model.review_profile_for(risk_class)
    if profile.requires_abuse_class_assessment and risk_class_explicit:
        if abuse_class_assessment_binding != ABUSE_ASSESSMENT_BOUND_TO_REQUEST:
            raise CompactPairError(
                "high-risk-control report must bind Abuse Class Assessment to request"
            )
    elif abuse_class_assessment_binding is not None:
        raise CompactPairError(
            "Abuse Class Assessment binding is only valid for high-risk-control reports"
        )
    legacy = _section_optional(lines, "## Finding Refs") is None
    if legacy:
        is_frozen_legacy = (
            _is_frozen_verbose_report(root, path, raw)
            if frozen_legacy is None
            else frozen_legacy
        )
        if not is_frozen_legacy:
            raise CompactPairError("missing ## Finding Refs or frozen historical provenance")
    finding_refs = _finding_refs(lines, required=not legacy)
    return VerificationReport(
        path=path,
        verdict=verdict,
        request_path=request_path,
        request_commit=request_commit,
        reviewed_repository=reviewed_repository,
        reviewed_head=head,
        reviewed_base=base,
        reviewer_seat=_one(lines, "Reviewer seat: ", "Reviewer seat"),
        reviewer_model=_identity(_one(lines, "Reviewer model: ", "Reviewer model"), "Reviewer model"),
        risk_class=risk_class,
        risk_class_explicit=risk_class_explicit,
        abuse_class_assessment_binding=abuse_class_assessment_binding,
        evidence=_evidence(lines),
        finding_refs=finding_refs,
        finding_dispositions=_finding_dispositions(
            lines, finding_refs, required=not legacy
        ),
        supersedes=_supersedes(root, lines, path),
        filename_reviewer=match.group("reviewer"),
        envelope_sender=_envelope_sender(text),
        frozen_model_label_exception=_is_frozen_model_label_exception(
            root, path, raw
        ),
        historical_model_family_compatibility=(
            _is_historical_model_family_compatibility(root, path, raw)
            if historical_model_family_compatibility is None
            else historical_model_family_compatibility
        ),
    )


def parse_verification_report(
    root: Path, report_path: str | os.PathLike[str]
) -> VerificationReport:
    root = root.resolve()
    path = _repo_path(root, report_path)
    return _parse_verification_report_bytes(root, path, _read_regular(root, path))


def parse_verification_report_committed_bytes(
    root: Path,
    report_path: str | os.PathLike[str],
    raw: bytes,
    *,
    frozen_legacy: bool | None = None,
    historical_model_family_compatibility: bool | None = None,
) -> VerificationReport:
    """Parse bytes from a caller's committed mailbox projection."""

    root = root.resolve()
    path = _repo_path(root, report_path)
    return _parse_verification_report_bytes(
        root,
        path,
        raw,
        frozen_legacy=frozen_legacy,
        historical_model_family_compatibility=(
            historical_model_family_compatibility
        ),
    )


def parse_verification_report_candidate(
    root: Path,
    candidate_path: str | os.PathLike[str],
    final_path: str | os.PathLike[str],
) -> VerificationReport:
    """Parse candidate bytes using the intended final path as identity authority."""
    root = root.resolve()
    candidate = _repo_path(root, candidate_path)
    final = _repo_path(root, final_path)
    report = _parse_verification_report_bytes(
        root,
        final,
        _read_regular(root, candidate),
        allow_legacy_missing_risk=False,
    )
    # Same publication-time resolvability as request candidates. Root-only:
    # a report's ref targets are mailbox events of this repository. The
    # report's own `Verification request:` binding ref is already resolved
    # by validate_report on the publication path.
    _require_path_references_resolve(root, report.finding_refs)
    _require_path_references_resolve(
        root, tuple(ref for ref, _ in report.finding_dispositions)
    )
    return report



def _report_structure_violations(
    report: VerificationReport, request: VerifyRequest
) -> list[str]:
    violations: list[str] = []
    if report.reviewer_seat != report.filename_reviewer or report.envelope_sender != report.filename_reviewer:
        violations.append("reviewer seat does not match verification-report envelope/path")
    if report.reviewer_seat != request.assigned_operator:
        violations.append("reviewer seat is not the assigned Operator")
    if report.reviewer_seat == request.author_seat:
        violations.append("reviewer seat equals author seat")
    if request.author_seat in protocol_mailbox.APP_MEMBERS and not (
        codex_protocol_model.model_family_matches_member(
            request.author_model, request.author_seat
        )
    ):
        violations.append("author model family does not match author member")
    if report.reviewer_seat in protocol_mailbox.APP_MEMBERS and not (
        codex_protocol_model.model_family_matches_member(
            report.reviewer_model, report.reviewer_seat
        )
    ):
        violations.append("reviewer model family does not match reviewer member")
    report_match = REPORT_RE.fullmatch(report.path)
    if (
        report_match is not None
        and report_match.group("recipient") != "all"
        and report_match.group("recipient") != request.author_seat
    ):
        violations.append("report recipient does not match request author")
    profile = codex_protocol_model.review_profile_for(request.risk_class)
    if (
        report.risk_class_explicit
        and not report.historical_model_family_compatibility
        and not report.frozen_model_label_exception
        and not codex_protocol_model.model_is_current_reviewer(
            report.reviewer_model
        )
    ):
        violations.append(
            "reviewer model must resolve to a currently admitted reviewer model"
        )
    if profile.requires_different_model:
        if request.risk_class_explicit:
            # Artifacts that declare a risk class must clear model-family
            # independence: a harness prefix or version suffix is not a
            # different reviewer.
            pair_is_admissible = (
                codex_protocol_model.models_are_independent(
                    request.author_model, report.reviewer_model
                )
                if report.historical_model_family_compatibility
                else codex_protocol_model.models_are_current_review_pair(
                    request.author_model, report.reviewer_model
                )
            )
            if not pair_is_admissible and not report.frozen_model_label_exception:
                violations.append("reviewer model shares the author model family")
        elif report.reviewer_model.casefold() == request.author_model.casefold():
            # Legacy artifacts predate the Risk class field and are graded on
            # the exact-label rule that was in force when they were accepted.
            # Committed evidence stays readable; it is not retroactively voided.
            violations.append("reviewer model equals author model")
    if report.risk_class != request.risk_class:
        violations.append("report Risk class does not match request")
    if profile.requires_abuse_class_assessment and request.risk_class_explicit:
        if not request.abuse_class_assessment:
            violations.append("high-risk-control request lacks Abuse Class Assessment")
        if (
            report.risk_class_explicit
            and report.abuse_class_assessment_binding
            != ABUSE_ASSESSMENT_BOUND_TO_REQUEST
        ):
            violations.append("high-risk-control report does not bind Abuse Class Assessment")
    if report.reviewed_repository != request.reviewed_repository:
        violations.append("report Reviewed repository does not match request")
    if report.reviewed_head != request.reviewed_head:
        violations.append("report Reviewed head does not match request")
    if report.reviewed_base != request.reviewed_base:
        violations.append("report Reviewed base does not match request")
    if report.finding_refs != request.finding_refs:
        violations.append("report finding refs changed from request")
    if report.verdict == "GO" and (
        not any(line.startswith("$ ") and line[2:].strip() for line in report.evidence)
        or not any(line.startswith("→ ") and line[2:].strip() for line in report.evidence)
    ):
        violations.append("GO requires evidence")
    if report.verdict in {"GO", "NITS"} and any(
        disposition == "unresolved-hard-boundary"
        for _, disposition in report.finding_dispositions
    ):
        violations.append(
            f"{report.verdict} cannot carry unresolved hard-boundary findings"
        )
    return violations


def validate_report_structure(root: Path, report: VerificationReport) -> list[str]:
    """Validate the exact report/request pair without resolving its reviewed range."""
    try:
        request = parse_verify_request_structure(
            root, report.request_path, report.request_commit
        )
    except CompactPairError as exc:
        return [f"request binding invalid: {exc}"]
    return validate_report_structure_against_request(root, report, request)


def validate_report_structure_against_request(
    root: Path,
    report: VerificationReport,
    request: VerifyRequest,
) -> list[str]:
    """Validate a report against an already parsed exact request binding."""

    violations = validate_report_binding(report, request)
    violations += _supersedes_violations(root, report, request)
    return violations


def validate_report_binding(
    report: VerificationReport,
    request: VerifyRequest,
) -> list[str]:
    """Validate report fields against an already parsed request, without Git."""

    violations: list[str] = []
    if (
        report.request_path != request.path
        or report.request_commit != request.trigger_commit
    ):
        violations.append("report Verification request does not match indexed request")
    violations += _report_structure_violations(report, request)
    return violations


def supersession_report_violations(
    report: VerificationReport,
    superseded: VerificationReport,
    *,
    request: VerifyRequest | None = None,
    superseded_commit: str | None = None,
) -> list[str]:
    """Validate the pure report-to-report portion of a Supersedes binding."""

    violations: list[str] = []
    if superseded.reviewer_seat != report.reviewer_seat:
        violations.append("a seat supersedes only its own verdicts")
    different_request = (
        superseded.request_path != report.request_path
        or superseded.request_commit != report.request_commit
    )
    if not different_request:
        return violations
    if request is None:
        violations.append("a report supersedes only a verdict for the same exact request")
        return violations
    if request.remediates_failed_report is None:
        violations.append(
            "a report supersedes only a verdict for the same exact request unless "
            "the different-request remediation request explicitly names the failed report"
        )
        return violations
    expected = request.remediates_failed_report
    if report.supersedes != expected:
        violations.append("a remediation report must supersede the exact failed report")
    if superseded_commit is None or expected != (superseded.path, superseded_commit):
        violations.append("remediation request does not bind the superseded report")
        return violations
    violations += remediation_request_violations(
        request,
        superseded,
        superseded_commit,
    )
    # FAIL belongs here, and its absence was a trap. A remediation report is
    # REQUIRED to supersede the failed report it answers, so restricting
    # supersession to GO/NITS made a failed remediation unpublishable: without
    # Supersedes the writer rejected it as an unbound remediation, and with
    # Supersedes it rejected the verdict. The only publishable outcomes were the
    # two that CLEAR the blocker, which pressures a reviewer toward a verdict
    # they do not hold. Reported by a reviewer who refused to issue it.
    #
    # Permitting FAIL cannot weaken admission, because admission is decided
    # elsewhere and independently: ci_admission_gate._ADMITTING_VERDICTS is
    # {GO, NITS}, so a superseding FAIL retires the older report and then fails
    # to admit in its own right. The range stays blocked and the active blocker
    # becomes the one describing the current head.
    if report.verdict not in {"GO", "NITS", "FAIL"}:
        violations.append("a remediation supersession verdict must be GO, NITS, or FAIL")
    return violations


def remediation_request_violations(
    request: VerifyRequest,
    failed_report: VerificationReport,
    failed_report_commit: str,
) -> list[str]:
    """Validate the pure request-to-failed-report remediation binding."""

    violations: list[str] = []
    expected = (failed_report.path, failed_report_commit)
    if request.remediates_failed_report != expected:
        violations.append("request must explicitly name the exact failed report")
    if failed_report.verdict != "FAIL":
        violations.append("remediation target is not a FAIL report")
    if request.assigned_operator != failed_report.reviewer_seat:
        violations.append("remediation reviewer seat does not match failed report")
    if request.reviewed_repository != failed_report.reviewed_repository:
        violations.append("remediation repository does not match failed report")
    if request.risk_class != failed_report.risk_class:
        violations.append("remediation Risk class does not match failed report")
    expected_base = (
        failed_report_commit
        if request.historical_remediation_base_compatibility
        else failed_report.reviewed_head
    )
    if request.reviewed_base != expected_base:
        violations.append(
            "remediation Reviewed base must equal the failed report Reviewed head"
        )
    missing_refs = tuple(
        reference
        for reference in failed_report.finding_refs
        if reference not in request.finding_refs
    )
    if missing_refs:
        violations.append("remediation request does not carry every failed finding ref")
    return violations


def validate_report(root: Path, report: VerificationReport) -> list[str]:
    root = root.resolve()
    try:
        request = parse_verify_request(root, report.request_path, report.request_commit)
    except CompactPairError as exc:
        return [f"request binding invalid: {exc}"]
    violations = _report_structure_violations(report, request)
    violations += _supersedes_violations(root, report, request)
    try:
        reviewed_root = _reviewed_root(root, request.reviewed_repository)
        base = _full_commit(reviewed_root, request.reviewed_base, "Reviewed base")
        head = _full_commit(reviewed_root, request.reviewed_head, "Reviewed head")
        if base == head or not _is_ancestor(reviewed_root, base, head):
            raise CompactPairError(
                "Reviewed base must be a strict ancestor of Reviewed head"
            )
    except CompactPairError as exc:
        violations.append(f"reviewed range unavailable: {exc}")
    return violations


def _optional_one(lines: list[str], prefix: str, label: str) -> str | None:
    occurrences = normalized_field_occurrences(lines, label)
    if len(occurrences) > 1:
        raise CompactPairError(f"duplicate {label}")
    if not occurrences:
        return None
    line = occurrences[0].strip()
    if line.startswith(("- ", "* ", "+ ")):
        line = line[2:].strip()
    if not line.startswith(prefix):
        raise CompactPairError(f"invalid {label}")
    value = line[len(prefix) :]
    if not value or value != value.strip():
        raise CompactPairError(f"invalid {label}")
    return value


def _reviewed_root(
    pipeline_root: Path,
    repository_field: str | None,
    *,
    commit_projection: git_commit_projection.CommitGraphProjection | None = None,
    allow_git_fallback: bool = True,
) -> Path:
    pipeline_root = pipeline_root.resolve()
    if repository_field is None:
        return pipeline_root
    candidate = _reviewed_repository_path(repository_field)
    current = Path(candidate.anchor)
    for component in candidate.parts[1:]:
        current = current / component
        if current.is_symlink():
            raise CompactPairError("Reviewed repository traverses a symlink")
    try:
        resolved = candidate.resolve(strict=True)
    except OSError:
        # The field records where the review ran: an absolute path on the
        # authoring machine. A CI runner or a fresh clone holds the same
        # repository under a different path, so demanding this one exist made
        # every event fail everywhere except the machine that wrote it, while
        # passing locally — a gate that only ever runs green where it cannot
        # catch anything. Degrade to the local root, which is exactly what an
        # absent field already does. Nothing is skipped: the Reviewed
        # base/head lookups below still have to resolve here, so an
        # unreachable range fails and naming a path that is not a repository
        # buys no leniency.
        return pipeline_root
    if not resolved.is_dir() or resolved.as_posix() != repository_field:
        raise CompactPairError("Reviewed repository must be one canonical directory")
    if commit_projection is not None and commit_projection.matches_root(resolved):
        return resolved
    if not allow_git_fallback:
        raise CompactPairError(
            "Reviewed repository does not match the committed projection root"
        )
    top_level = _git(resolved, "rev-parse", "--show-toplevel").decode().strip()
    if top_level != repository_field:
        raise CompactPairError("Reviewed repository must be a Git worktree root")
    return resolved


def _reviewed_repository_path(repository_field: str) -> Path:
    candidate = Path(repository_field)
    if not candidate.is_absolute():
        raise CompactPairError("Reviewed repository must be absolute")
    if (
        candidate.as_posix() != repository_field
        or any(component in {".", ".."} for component in candidate.parts)
    ):
        raise CompactPairError("Reviewed repository must be normalized")
    return candidate


def _section_optional(lines: list[str], heading: str) -> list[str] | None:
    positions = _normalized_heading_occurrences(lines, heading)
    if len(positions) > 1:
        raise CompactPairError(f"duplicate {heading}")
    if not positions:
        return None
    if lines[positions[0]] != heading:
        raise CompactPairError(f"invalid {heading}")
    return _section(lines, heading)


def normalized_field_occurrences(lines: list[str], label: str) -> list[str]:
    """Return every canonical or normalized-lookalike occurrence of a field."""

    words = r"\s+".join(re.escape(word) for word in label.split())
    pattern = re.compile(rf"^\s*(?:[-*+]\s+)?{words}\s*(?::.*)?\s*$", re.IGNORECASE)
    return [line for line in lines if pattern.fullmatch(line)]


def _normalized_heading_occurrences(lines: list[str], heading: str) -> list[int]:
    title = heading.lstrip("#").strip()
    words = r"\s+".join(re.escape(word) for word in title.split())
    pattern = re.compile(rf"^\s*#{{2,6}}\s*{words}\s*:?\s*$", re.IGNORECASE)
    return [index for index, line in enumerate(lines) if pattern.fullmatch(line)]


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


def _supersedes(
    root: Path, lines: list[str], report_path: str
) -> tuple[str, str] | None:
    """Parse the optional `Supersedes: <report-path>@<commit>` re-issue field.

    A verdict a later report supersedes is dead: re-issued artifacts name the
    orphan explicitly instead of leaving consumers to infer it from prose
    (2026-07-25 duplicate-footer incident, ADR-066). Grammar checks only —
    resolution against Git history is `_supersedes_violations`, so committed
    artifacts stay parseable on a shallow read.
    """
    value = _optional_one(lines, "Supersedes: ", "Supersedes")
    if value is None:
        return None
    path, commit = _parse_report_reference(root, value, "Supersedes")
    if path == report_path:
        raise CompactPairError("Supersedes must not name the report itself")
    return path, commit


def _parse_report_reference(
    root: Path,
    value: str,
    label: str,
) -> tuple[str, str]:
    path, separator, commit = value.rpartition("@")
    if not separator:
        raise CompactPairError(f"{label} must bind report-path@commit")
    path = _repo_path(root, path)
    if REPORT_RE.fullmatch(path) is None:
        raise CompactPairError(
            f"{label} path is not a canonical verification-report"
        )
    if SHA_RE.fullmatch(commit) is None:
        raise CompactPairError(
            f"{label} commit must be one full lowercase commit SHA"
        )
    return path, commit


def _remediates_failed_report(
    root: Path,
    lines: list[str],
) -> tuple[str, str] | None:
    value = _optional_one(
        lines,
        "Remediates failed report: ",
        "Remediates failed report",
    )
    if value is None:
        return None
    return _parse_report_reference(root, value, "Remediates failed report")


def _load_report_at_introduction(
    root: Path,
    path: str,
    commit: str,
) -> VerificationReport:
    resolved = _full_commit(root, commit, "report introduction commit")
    change = _git(
        root,
        "diff-tree",
        "--root",
        "--no-commit-id",
        "--name-status",
        "-r",
        resolved,
        "--",
        path,
    ).decode("utf-8", errors="strict").splitlines()
    if change != [f"A\t{path}"]:
        raise CompactPairError(
            "report reference commit must be the named report's introduction commit"
        )
    if not _is_ancestor(root, resolved, "HEAD"):
        raise CompactPairError("report introduction commit is not in this history")
    return _parse_verification_report_bytes(
        root,
        path,
        _git(root, "show", f"{resolved}:{path}"),
    )


def _remediation_request_target_violations(
    root: Path,
    request: VerifyRequest,
) -> list[str]:
    if request.remediates_failed_report is None:
        return []
    path, commit = request.remediates_failed_report
    try:
        failed_report = _load_report_at_introduction(root, path, commit)
        target_violations = validate_report(root, failed_report)
        if target_violations:
            raise CompactPairError(
                "remediation target report is invalid: " + "; ".join(target_violations)
            )
        request_violations = remediation_request_violations(
            request,
            failed_report,
            commit,
        )
        if request_violations:
            raise CompactPairError("; ".join(request_violations))
    except CompactPairError as exc:
        return [f"remediation binding invalid: {exc}"]
    return []


def _supersedes_violations(
    root: Path,
    report: VerificationReport,
    request: VerifyRequest,
) -> list[str]:
    """Resolve a Supersedes claim against Git: it names the seat's own dead verdict."""
    if report.supersedes is None:
        if request.remediates_failed_report is not None:
            return [
                "supersession binding invalid: remediation report must explicitly "
                "supersede the failed report"
            ]
        return []
    path, commit = report.supersedes
    try:
        superseded = _load_report_at_introduction(root, path, commit)
        different_request = (
            superseded.request_path != report.request_path
            or superseded.request_commit != report.request_commit
        )
        report_violations = supersession_report_violations(
            report,
            superseded,
            request=request,
            superseded_commit=commit,
        )
        if report_violations:
            raise CompactPairError("; ".join(report_violations))
        if different_request:
            target_violations = validate_report(root, superseded)
            if target_violations:
                raise CompactPairError(
                    "superseded report is invalid: " + "; ".join(target_violations)
                )
    except CompactPairError as exc:
        return [f"supersession binding invalid: {exc}"]
    return []


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


def _is_frozen_verbose_report(root: Path, path: str, raw: bytes) -> bool:
    if _git_blob(root, LEGACY_VERBOSE_CUTOFF, path) != raw:
        return False
    latest = protocol_mailbox.newest_commit_touching(root, path)
    if latest is None:
        return False
    if _is_ancestor(root, latest, LEGACY_VERBOSE_CUTOFF):
        return True
    # Reintroduction doctrine (protocol_mailbox): a delete/revert cycle puts
    # the newest touching commit outside the frozen cutoff's ancestry.
    # Byte-identical restoration is not mutation — accept exactly when that
    # commit still carries the frozen bytes; a post-cutoff touch that
    # changed the bytes stays refused.
    return protocol_mailbox.committed_blob_or_none(root, latest, path) == raw


def _main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="compact_pair_loop.py")
    subparsers = parser.add_subparsers(dest="command", required=True)
    candidate = subparsers.add_parser("validate-candidate")
    candidate.add_argument("--repo-root", required=True, type=Path)
    candidate.add_argument("--candidate", required=True)
    candidate.add_argument("--final-relative", required=True)
    compose = subparsers.add_parser("compose-request")
    compose.add_argument("--repo-root", required=True, type=Path)
    compose.add_argument("--author", required=True)
    compose.add_argument("--author-model", required=True)
    compose.add_argument("--operator", required=True)
    compose.add_argument("--risk-class", required=True)
    compose.add_argument("--base", required=True)
    compose.add_argument("--head", default="HEAD")
    compose.add_argument("--reviewed-repository")
    compose.add_argument("--abuse-class", action="append", default=[])
    compose.add_argument("--finding-ref", action="append", default=[])
    compose.add_argument("--remediates-failed-report")
    arguments = parser.parse_args(argv)

    if arguments.command == "compose-request":
        try:
            body = compose_request(
                arguments.repo_root,
                author_seat=arguments.author,
                author_model=arguments.author_model,
                assigned_operator=arguments.operator,
                risk_class=arguments.risk_class,
                base_rev=arguments.base,
                head_rev=arguments.head,
                outcome=sys.stdin.read(),
                reviewed_repository=arguments.reviewed_repository,
                abuse_assessments=arguments.abuse_class,
                finding_refs=arguments.finding_ref,
                remediates_failed_report=arguments.remediates_failed_report,
            )
        except (CompactPairError, OSError) as exc:
            print(f"compose-request failed: {exc}", file=sys.stderr)
            return 1
        sys.stdout.write(f"{body}\n")
        return 0

    try:
        if str(arguments.final_relative).endswith("-verify-request.md"):
            request = parse_verify_request_candidate(
                arguments.repo_root,
                arguments.candidate,
                arguments.final_relative,
            )
            violations = validate_request_candidate(arguments.repo_root, request)
        else:
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


def review_validate_main(argv: list[str] | None = None) -> int:
    """Expose candidate validation without the internal redundant subcommand."""

    arguments = list(sys.argv[1:] if argv is None else argv)
    return _main(["validate-candidate", *arguments])


if __name__ == "__main__":
    sys.exit(_main())
