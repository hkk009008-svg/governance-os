#!/usr/bin/env python3
"""Coordination-state linter — protocol v6.0.

Machine-checks the director↔operator coordination invariants that previously
lived only in seat discipline and drifted (the 2026-06-10 three-way cursor
divergence: seen/*.txt vs event footers vs commit messages). Mirrors the
check_doc_claims.py verifier pattern.

Public API
----------
CoordIssue                       dataclass for a single finding
KNOWN_KINDS                      accepted event-kind tokens (filename position)
run(coord_root, since, now)  ->  list[CoordIssue]
main(argv=None)              ->  int   (exit 0 = no FATAL, 1 = FATAL present)

Severities
----------
FATAL    — structurally broken state (unparseable/future cursor, filename
           convention violation, self-addressed event). Exit-code-affecting.
ADVISORY — drift that needs a human eye but doesn't break the machinery
           (orphan cursor, missing/mismatched **When:** envelope, novel kind).
INFO     — unread-count report (always emitted, never a failure).

Also hard-fails coordinator "All-Seat Handoff" artifacts that do not cite real
live-seat mailbox/handoff artifacts for all four seats. Subagent reports are
advisory evidence, not live-seat protocol authority.

The envelope checks are gated on --since (default 2026-06-11, the v6.0
adoption date): pre-adoption events used a YAML-frontmatter format and are
exempt. Filename checks are NOT gated — all 270 legacy events were verified
conforming at adoption time.
"""
from __future__ import annotations

import argparse
import hashlib
import io
import json
import os
import re
import subprocess
import sys
import tarfile
import time
from dataclasses import dataclass
from pathlib import Path, PurePosixPath

import compact_pair_loop
import check_go_schema
import mailbox_writer
import protocol_mailbox
from protocol_mailbox import KNOWN_KINDS, SEATS
import bus_unread

# Only the four concrete pair seats own consumable mailbox cursors. Coordinators
# may read broadcasts and direct messages, but remain cursorless observers.
ROLES = SEATS

_EVENT_NAME_RE = re.compile(
    r"^(?P<ts>\d{4}-\d{2}-\d{2}T\d{2}-\d{2}-\d{2}Z)-"
    r"(?P<frm>director|director2|operator|operator2|coordinator|coordinator2)"
    r"-to-(?P<to>director|director2|operator|operator2|coordinator|coordinator2|all)-"
    r"(?P<kind>[a-z0-9-]+)\.md$"
)

# Cursor CONTENT is transitionally a scalar `seq` (post Slice-2.5 backfill) OR an
# ISO-UTC timestamp (pre-backfill, Phase-A-seeded). NB: this gates the cursor FILE
# CONTENT only — the event-FILENAME regexes (_EVENT_NAME_RE / _EVENT_RE) stay
# dash-ISO and are deliberately NOT loosened (Rule #13: different parser, on-disk
# filenames are always ISO).
_ISO_CURSOR_RE = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$")
_CURSOR_RE = re.compile(
    r"^(?:\d+|\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z)$")   # scalar seq OR ISO

# A commit whose entire changeset is seen/*.txt is a standalone cursor advance —
# cursor advances should ride the next substantive commit (capacity audit
# wf_6be2ee18-f4b, lever #5). Detected opt-in via run(git_root=...).
_SEEN_ONLY_RE = re.compile(r"^coordination/mailbox/seen/[^/]+\.txt$")

_WHEN_RE = re.compile(r"\*\*When:\*\*\s+(\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z)")

_ALL_SEAT_HANDOFF_RE = re.compile(r"^#{1,3}\s+All[- ]Seat Handoff\b", re.I | re.M)
_PENDING_LIVE_SEAT_MARKERS = (
    "does not claim that the four live seats completed handoffs",
    "live-seat work still owed",
    "still need to publish their own seat-owned",
    "real live-seat artifacts to land",
)
_LIVE_SEAT_ARTIFACT_RES = {
    role: (
        re.compile(rf"\bdocs/HANDOFF-{role}-\d{{4}}-\d{{2}}-\d{{2}}", re.I),
        re.compile(
            rf"\bcoordination/mailbox/sent/\d{{4}}-\d{{2}}-\d{{2}}T"
            rf"\d{{2}}-\d{{2}}-\d{{2}}Z-{role}-to-"
            rf"(?:director|director2|operator|operator2|coordinator|coordinator2|all)-[a-z0-9-]+\.md\b",
            re.I,
        ),
    )
    for role in ROLES
}


@dataclass
class CoordIssue:
    path: str
    kind: str        # cursor_missing | cursor_unparseable | cursor_future |
                     # cursor_orphan | bad_filename | self_addressed |
                     # missing_when | when_mismatch | unknown_kind |
                     # unread
    severity: str    # FATAL | ADVISORY | INFO
    message: str


@dataclass(frozen=True)
class CurrentVerifyRequest:
    path: str
    commit: str | None
    assigned_operator: str
    valid: bool
    problem: str | None
    grandfathered: bool = False


@dataclass(frozen=True)
class FailedVerifyRequest:
    request_path: str
    request_commit: str
    report_path: str
    report_commit: str
    assigned_operator: str


@dataclass(frozen=True)
class VerifyReviewState:
    pending: tuple[CurrentVerifyRequest, ...]
    failed: tuple[FailedVerifyRequest, ...]
    problem: str | None = None
    grandfathered_history: tuple[str, ...] = ()


@dataclass(frozen=True)
class ImmutableHistoryException:
    path: str
    artifact_class: str
    introduction_commit: str
    introduction_blob: str
    accepted_current_blob: str
    accepted_current_sha256: str
    digest_authority: str
    reason: str


@dataclass(frozen=True)
class CommittedMailboxProjection:
    events: dict[str, bytes]
    introductions: dict[str, tuple[str, str]]
    introduction_events: dict[str, bytes]
    learning_cutover_events: dict[str, bytes]
    learning_cutover_ancestors: frozenset[str]
    kinds: frozenset[str]
    frozen_legacy_reports: frozenset[str]
    history_exceptions: dict[str, ImmutableHistoryException]


_REVIEW_STATE_CUTOVER_PATH = (
    "coordination/mailbox/sent/"
    "2026-07-25T05-45-10Z-coordinator-to-operator-verify-request.md"
)
_REVIEW_STATE_CUTOVER_COMMIT = "61786501e26f7e1bac92efbdcd4ff0ea468a7bbb"
_ACTIVE_FAILURE_CUTOVER_COMMIT = "8d05a76489b8609634e1635ebfad12792abc8119"
_LEARNING_HISTORY_CUTOVER_COMMIT = "13616d843e4e55beed405de69db4e953d0831767"
_BASELINE_ACTIVE_FAILURE_REPORTS = frozenset({
    "coordination/mailbox/sent/"
    "2026-07-27T03-26-01Z-operator2-to-director2-verification-report.md@"
    "e0fbefdb56af03b8c04b6df58245f7533a3d83c0"
})
_PRE_CUTOVER_INVALID_REQUESTS = {
    (
        _REVIEW_STATE_CUTOVER_PATH,
        _REVIEW_STATE_CUTOVER_COMMIT,
    ): "d77efcb26159733b31b1159fba6bb83c9b62b8ef3937ed8432ddff54fc224f7c",
}


def _dash(ts: str) -> str:
    return ts.replace(":", "-")


def _colon(ts_dash: str) -> str:
    # 2026-06-12T10-00-00Z -> 2026-06-12T10:00:00Z (date part untouched)
    return ts_dash[:11] + ts_dash[11:].replace("-", ":")


def _event_names(coord_root: Path, subdir: str = "sent") -> list[str]:
    d = coord_root / "mailbox" / subdir
    if not d.is_dir():
        return []
    return sorted(p.name for p in d.iterdir() if p.name.endswith(".md"))


def _check_cursors(coord_root: Path, now: str,
                   names: list[str]) -> list[CoordIssue]:
    issues: list[CoordIssue] = []
    for role in ROLES:
        cf = coord_root / "mailbox" / "seen" / f"{role}.txt"
        rel = f"mailbox/seen/{role}.txt"
        if not cf.exists():
            issues.append(CoordIssue(rel, "cursor_missing", "FATAL",
                                     f"{role} cursor file missing"))
            continue
        cur = cf.read_text().strip()
        if not _CURSOR_RE.match(cur):
            issues.append(CoordIssue(rel, "cursor_unparseable", "FATAL",
                                     f"{role} cursor not a seq or ISO UTC ts: {cur!r}"))
            continue
        # The future-check + orphan-vs-event compares below are ISO-lexical; a
        # scalar `seq` cursor has no wall-clock and cannot be "future" or
        # "orphan" (its seq↔event mapping is the projection layer's job, not
        # this legacy checker's). Skip both for a scalar.
        if _ISO_CURSOR_RE.match(cur):
            if cur > now:
                issues.append(CoordIssue(rel, "cursor_future", "FATAL",
                                         f"{role} cursor {cur} is in the future (now {now})"))
                continue
            # The watermark should be the timestamp of a real event addressed to
            # this role — in sent/ OR archive/ (events move there after
            # consumption). Older-than-everything is also allowed; anything else
            # that matches no event is a hand-typed orphan.
            all_names = names + _event_names(coord_root, "archive")
            addressed = [m.group("ts") for m in map(_EVENT_NAME_RE.match, all_names)
                         if m and m.group("to") in (role, "all")]
            cur_dash = _dash(cur)
            if addressed and cur_dash not in addressed and cur_dash > min(addressed):
                issues.append(CoordIssue(
                    rel, "cursor_orphan", "ADVISORY",
                    f"{role} cursor {cur} matches no event addressed to {role}"))
    return issues


def _check_events(coord_root: Path, since: str,
                  names: list[str]) -> list[CoordIssue]:
    issues: list[CoordIssue] = []
    sent = coord_root / "mailbox" / "sent"
    for name in names:
        rel = f"mailbox/sent/{name}"
        m = _EVENT_NAME_RE.match(name)
        if not m:
            issues.append(CoordIssue(rel, "bad_filename", "FATAL",
                                     "filename violates <ts>-<from>-to-<to>-<kind>.md"))
            continue
        if m.group("frm") == m.group("to"):
            issues.append(CoordIssue(rel, "self_addressed", "FATAL",
                                     f"event addressed to its own sender ({m.group('frm')})"))
        if m.group("kind") not in KNOWN_KINDS:
            issues.append(CoordIssue(rel, "unknown_kind", "ADVISORY",
                                     f"kind {m.group('kind')!r} not in KNOWN_KINDS"))
        if m.group("ts") < since:        # pre-adoption: envelope exempt
            continue
        text = (sent / name).read_text(errors="replace")
        when = _WHEN_RE.search(text)
        if not when:
            issues.append(CoordIssue(rel, "missing_when", "ADVISORY",
                                     "no '**When:** <ISO-UTC>' envelope line"))
        elif _dash(when.group(1)) != m.group("ts"):
            issues.append(CoordIssue(
                rel, "when_mismatch", "ADVISORY",
                f"**When:** {when.group(1)} != filename ts {_colon(m.group('ts'))}"))
    return issues


def _unread_report(coord_root: Path, names: list[str],
                   repo_root: Path | None = None) -> list[CoordIssue]:
    issues: list[CoordIssue] = []
    for role in ROLES:
        cf = coord_root / "mailbox" / "seen" / f"{role}.txt"
        if not cf.exists():
            continue
        cur = cf.read_text().strip()
        resolution = bus_unread.resolve_unread(
            repo_root if repo_root is not None else coord_root.parent,
            role,
            cur,
            names,
        )
        if resolution.count is None:
            msg = f"{role}: unread unavailable via {resolution.source}"
        else:
            msg = (
                f"{role}: {resolution.count} unread event(s) "
                f"via {resolution.source}"
            )
        issues.append(CoordIssue(f"mailbox/seen/{role}.txt", "unread", "INFO", msg))
        if resolution.transport == "incoherent":
            issues.append(CoordIssue(
                f"mailbox/seen/{role}.txt",
                "transport_incoherent",
                "FATAL",
                f"{role}: {resolution.detail}",
            ))
    return issues


def _git_blob_oid(raw: bytes) -> str:
    header = f"blob {len(raw)}\0".encode("ascii")
    return hashlib.sha1(header + raw).hexdigest()


def _projection_git(
    repo_root: Path,
    *arguments: str,
) -> subprocess.CompletedProcess[bytes]:
    """Run the known system Git without replacement objects or ambient Git state."""

    return subprocess.run(
        [
            "/usr/bin/git",
            "--no-replace-objects",
            "--literal-pathspecs",
            "--no-optional-locks",
            "-C",
            str(repo_root),
            *arguments,
        ],
        capture_output=True,
        check=False,
        env=mailbox_writer.sanitized_git_environment(),
    )


def _projection_blobs(
    repo_root: Path, object_ids: set[str]
) -> tuple[dict[str, bytes] | None, str | None]:
    """Read exact Git blobs in one sanitized batch without another history scan."""

    ordered = sorted(object_ids)
    if not ordered:
        return {}, None
    try:
        result = subprocess.run(
            [
                "/usr/bin/git",
                "--no-replace-objects",
                "--literal-pathspecs",
                "--no-optional-locks",
                "-C",
                str(repo_root),
                "cat-file",
                "--batch",
            ],
            input=("\n".join(ordered) + "\n").encode("ascii"),
            capture_output=True,
            check=False,
            env=mailbox_writer.sanitized_git_environment(),
        )
    except OSError as exc:
        return None, f"mailbox introduction blob reader unavailable: {exc}"
    if result.returncode != 0:
        detail = result.stderr.decode("utf-8", errors="replace").strip()
        return None, detail or "mailbox introduction blobs unavailable"
    blobs: dict[str, bytes] = {}
    position = 0
    for expected in ordered:
        line_end = result.stdout.find(b"\n", position)
        if line_end < 0:
            return None, "mailbox introduction blob batch is truncated"
        header = result.stdout[position:line_end].decode("ascii", errors="replace")
        fields = header.split()
        if (
            len(fields) != 3
            or fields[0] != expected
            or fields[1] != "blob"
            or not fields[2].isdecimal()
        ):
            return None, f"mailbox introduction object is not a blob: {expected}"
        size = int(fields[2])
        start = line_end + 1
        end = start + size
        if end >= len(result.stdout) or result.stdout[end : end + 1] != b"\n":
            return None, "mailbox introduction blob batch has invalid framing"
        blobs[expected] = result.stdout[start:end]
        position = end + 1
    if position != len(result.stdout):
        return None, "mailbox introduction blob batch has trailing data"
    return blobs, None


def _learning_cutover_projection(
    repo_root: Path,
) -> tuple[dict[str, bytes] | None, str | None]:
    """Project exact learning-cutover mailbox bytes from one bounded tree listing."""

    listing = _projection_git(
        repo_root,
        "ls-tree",
        "-r",
        "-z",
        "--full-tree",
        _LEARNING_HISTORY_CUTOVER_COMMIT,
        "--",
        "coordination/mailbox/sent",
    )
    if listing.returncode != 0:
        detail = listing.stderr.decode("utf-8", errors="replace").strip()
        return None, detail or "learning-history cutover tree unavailable"
    entries: dict[str, str] = {}
    for record in listing.stdout.split(b"\0"):
        if not record:
            continue
        try:
            metadata, raw_path = record.split(b"\t", 1)
            mode, object_type, raw_oid = metadata.split(b" ", 2)
            path = raw_path.decode("utf-8", errors="strict")
            object_id = raw_oid.decode("ascii", errors="strict")
        except (ValueError, UnicodeDecodeError):
            return None, "learning-history cutover tree has invalid framing"
        if not path.endswith(".md"):
            # The sent tree carries a tracked .gitkeep before its first event;
            # it is not a protocol event and is intentionally outside scope.
            continue
        if (
            mode != b"100644"
            or object_type != b"blob"
            or compact_pair_loop.SHA_RE.fullmatch(object_id) is None
            or not path.startswith(_ARCHIVE_SENT_PREFIX)
            or path in entries
        ):
            return None, f"learning-history cutover tree has invalid entry: {path}"
        entries[path] = object_id
    blobs, blob_problem = _projection_blobs(repo_root, set(entries.values()))
    if blob_problem is not None or blobs is None:
        return None, blob_problem or "learning-history cutover blobs unavailable"
    events = {path: blobs[object_id] for path, object_id in entries.items()}
    for path, raw in events.items():
        if len(raw) > compact_pair_loop.MAX_EVENT_BYTES:
            return None, f"learning-history cutover event is too large: {path}"
        try:
            raw.decode("utf-8", errors="strict")
        except UnicodeDecodeError:
            return None, f"learning-history cutover event is not UTF-8: {path}"
    return events, None


_ARCHIVE_DIRECTORIES = frozenset(
    {
        "coordination",
        "coordination/mailbox",
        "coordination/mailbox/sent",
        "scripts",
        "scripts/baselines",
    }
)
_ARCHIVE_KINDS_PATH = "coordination/mailbox/kinds.txt"
_ARCHIVE_SENT_PREFIX = "coordination/mailbox/sent/"
_ARCHIVE_REPORT_BASELINE = "scripts/baselines/lane_v_reports_pre_v3.json"
_ARCHIVE_HISTORY_EXCEPTIONS = (
    "scripts/baselines/immutable_review_history_exceptions.json"
)
_HISTORY_EXCEPTION_SCHEMA = "immutable-review-history-exceptions/v1"


def _canonical_archive_path(name: str) -> bool:
    if not name or name.startswith("/") or "\\" in name:
        return False
    try:
        name.encode("utf-8", errors="strict")
    except UnicodeEncodeError:
        return False
    pure = PurePosixPath(name)
    return (
        all(part not in {"", ".", ".."} for part in pure.parts)
        and pure.as_posix() == name
    )


def _parse_mailbox_archive(
    raw_archive: bytes,
) -> tuple[dict[str, bytes] | None, str | None]:
    """Read one Git archive without extracting or accepting ambiguous members."""

    files: dict[str, bytes] = {}
    seen: set[str] = set()
    try:
        with tarfile.open(fileobj=io.BytesIO(raw_archive), mode="r:") as archive:
            for member in archive:
                name = member.name
                if not _canonical_archive_path(name):
                    return None, f"committed mailbox archive path is not canonical: {name!r}"
                if name in seen:
                    return None, f"committed mailbox archive has duplicate path: {name}"
                seen.add(name)
                if member.isdir():
                    if name not in _ARCHIVE_DIRECTORIES:
                        return None, f"committed mailbox archive has unexpected directory: {name}"
                    continue
                if not member.isreg():
                    return None, f"committed mailbox archive has unexpected member type: {name}"
                if (
                    name not in {
                        _ARCHIVE_KINDS_PATH,
                        _ARCHIVE_REPORT_BASELINE,
                        _ARCHIVE_HISTORY_EXCEPTIONS,
                    }
                    and not name.startswith(_ARCHIVE_SENT_PREFIX)
                ):
                    return None, f"committed mailbox archive path is outside scope: {name}"
                if member.size > compact_pair_loop.MAX_EVENT_BYTES:
                    return None, f"committed mailbox archive member is too large: {name}"
                extracted = archive.extractfile(member)
                if extracted is None:
                    return None, f"committed mailbox archive member is unreadable: {name}"
                value = extracted.read(compact_pair_loop.MAX_EVENT_BYTES + 1)
                if len(value) != member.size:
                    return None, f"committed mailbox archive member changed size: {name}"
                if name.endswith(".md"):
                    try:
                        value.decode("utf-8", errors="strict")
                    except UnicodeDecodeError:
                        return None, f"committed mailbox event is not UTF-8: {name}"
                files[name] = value
    except (tarfile.TarError, OSError) as exc:
        return None, f"committed mailbox archive is invalid: {exc}"
    return files, None


def _canonical_review_event(path: str) -> bool:
    return (
        compact_pair_loop.REQUEST_RE.fullmatch(path) is not None
        or compact_pair_loop.REPORT_RE.fullmatch(path) is not None
    )


def _strict_json_object(pairs: list[tuple[str, object]]) -> dict[str, object]:
    value: dict[str, object] = {}
    for key, item in pairs:
        if key in value:
            raise ValueError(f"duplicate key: {key}")
        value[key] = item
    return value


def _parse_history_exceptions(
    raw: bytes,
) -> tuple[dict[str, ImmutableHistoryException] | None, str | None]:
    try:
        value = json.loads(raw, object_pairs_hook=_strict_json_object)
    except (json.JSONDecodeError, UnicodeDecodeError, ValueError) as exc:
        return None, f"invalid immutable-history exception manifest: {exc}"
    if (
        not isinstance(value, dict)
        or set(value) != {"schema_version", "entries"}
        or value.get("schema_version") != _HISTORY_EXCEPTION_SCHEMA
        or not isinstance(value.get("entries"), list)
    ):
        return None, "invalid immutable-history exception manifest schema"
    expected_fields = {
        "path",
        "artifact_class",
        "introduction_commit",
        "introduction_blob",
        "accepted_current_blob",
        "accepted_current_sha256",
        "digest_authority",
        "reason",
    }
    exceptions: dict[str, ImmutableHistoryException] = {}
    for entry in value["entries"]:
        if not isinstance(entry, dict) or set(entry) != expected_fields:
            return None, "invalid immutable-history exception entry fields"
        if not all(isinstance(entry[field], str) for field in expected_fields):
            return None, "immutable-history exception fields must be strings"
        exception = ImmutableHistoryException(**entry)
        is_report = compact_pair_loop.REPORT_RE.fullmatch(exception.path) is not None
        is_request = compact_pair_loop.REQUEST_RE.fullmatch(exception.path) is not None
        if not (is_report or is_request):
            return None, "immutable-history exception path is not canonical"
        if exception.path in exceptions:
            return None, f"duplicate immutable-history exception path: {exception.path}"
        if (
            compact_pair_loop.SHA_RE.fullmatch(exception.introduction_commit) is None
            or compact_pair_loop.SHA_RE.fullmatch(exception.introduction_blob) is None
            or compact_pair_loop.SHA_RE.fullmatch(exception.accepted_current_blob) is None
            or re.fullmatch(r"[0-9a-f]{64}", exception.accepted_current_sha256) is None
            or not exception.reason.strip()
        ):
            return None, "immutable-history exception has invalid digest or reason"
        if is_report and (
            exception.artifact_class != "pre-v3-report-schema-repair"
            or exception.digest_authority != _ARCHIVE_REPORT_BASELINE
        ):
            return None, "report immutable-history exception has invalid class or authority"
        if is_request and (
            exception.artifact_class
            not in {
                "pre-enforcement-terminal-supersession",
                "pre-enforcement-request-schema-format",
            }
            or exception.digest_authority != _ARCHIVE_HISTORY_EXCEPTIONS
        ):
            return None, "request immutable-history exception has invalid class or authority"
        exceptions[exception.path] = exception
    return exceptions, None


def _committed_mailbox_projection(
    repo_root: Path,
) -> tuple[CommittedMailboxProjection | None, str | None]:
    """Project immutable HEAD mailbox bytes and introduction facts."""

    history = _projection_git(
        repo_root,
        "log",
        "--full-history",
        "--raw",
        "-z",
        "--no-renames",
        "--diff-filter=A",
        "--abbrev=40",
        "--format=COMMIT %H%x00",
        "HEAD",
        "--",
        "coordination/mailbox/sent",
        _ARCHIVE_HISTORY_EXCEPTIONS,
    )
    if history.returncode != 0:
        detail = history.stderr.decode("utf-8", errors="replace").strip()
        return None, detail or "mailbox introduction history unavailable"

    introductions: dict[str, tuple[str, str]] = {}
    commit: str | None = None
    introduced_blob: str | None = None
    for token in history.stdout.split(b"\0"):
        value = token.decode("utf-8", errors="replace")
        if value.startswith("COMMIT "):
            candidate = value.removeprefix("COMMIT ")
            commit = candidate if re.fullmatch(r"[0-9a-f]{40}", candidate) else None
            introduced_blob = None
            continue
        descriptor = value.lstrip("\n")
        if descriptor.startswith(":"):
            fields = descriptor.split()
            introduced_blob = (
                fields[3]
                if len(fields) >= 5
                and fields[4] == "A"
                and re.fullmatch(r"[0-9a-f]{40}", fields[3])
                else None
            )
            continue
        if (
            (
                value.startswith("coordination/mailbox/sent/")
                or value == _ARCHIVE_HISTORY_EXCEPTIONS
            )
            and commit is not None
            and introduced_blob is not None
        ):
            if value in introductions:
                return None, f"mailbox event has multiple introductions: {value}"
            introductions[value] = (commit, introduced_blob)
            introduced_blob = None

    introduction_blobs, blob_problem = _projection_blobs(
        repo_root, {blob for _commit, blob in introductions.values()}
    )
    if blob_problem is not None or introduction_blobs is None:
        return None, blob_problem or "mailbox introduction blobs unavailable"
    introduction_events = {
        path: introduction_blobs[blob]
        for path, (_commit, blob) in introductions.items()
    }

    cutoff_history = _projection_git(
        repo_root,
        "rev-list",
        compact_pair_loop.LEGACY_VERBOSE_CUTOFF,
    )
    if cutoff_history.returncode == 0:
        try:
            cutoff_lines = cutoff_history.stdout.decode("ascii", errors="strict").splitlines()
        except UnicodeDecodeError:
            return None, "legacy cutoff history is not ASCII"
        if any(compact_pair_loop.SHA_RE.fullmatch(line) is None for line in cutoff_lines):
            return None, "legacy cutoff history contains an invalid commit"
        cutoff_ancestors = frozenset(cutoff_lines)
    else:
        cutoff_ancestors = frozenset()

    archive_result = _projection_git(
        repo_root,
        "archive",
        "--format=tar",
        "HEAD",
        "coordination/mailbox/sent",
        _ARCHIVE_KINDS_PATH,
        _ARCHIVE_REPORT_BASELINE,
        _ARCHIVE_HISTORY_EXCEPTIONS,
    )
    if archive_result.returncode != 0:
        detail = archive_result.stderr.decode("utf-8", errors="replace").strip()
        return None, detail or "committed mailbox archive unavailable"

    archive_files, archive_problem = _parse_mailbox_archive(archive_result.stdout)
    if archive_problem is not None or archive_files is None:
        return None, archive_problem or "committed mailbox archive is unavailable"
    learning_cutover_events, cutover_problem = _learning_cutover_projection(repo_root)
    if cutover_problem is not None or learning_cutover_events is None:
        return None, cutover_problem or "learning-history cutover projection unavailable"
    cutover_history = _projection_git(
        repo_root, "rev-list", _LEARNING_HISTORY_CUTOVER_COMMIT
    )
    if cutover_history.returncode != 0:
        detail = cutover_history.stderr.decode("utf-8", errors="replace").strip()
        return None, detail or "learning-history cutover ancestors unavailable"
    try:
        cutover_ancestor_lines = cutover_history.stdout.decode(
            "ascii", errors="strict"
        ).splitlines()
    except UnicodeDecodeError:
        return None, "learning-history cutover ancestors are not ASCII"
    if any(
        compact_pair_loop.SHA_RE.fullmatch(commit) is None
        for commit in cutover_ancestor_lines
    ):
        return None, "learning-history cutover ancestors contain an invalid commit"
    learning_cutover_ancestors = frozenset(cutover_ancestor_lines)
    exception_raw = archive_files.get(_ARCHIVE_HISTORY_EXCEPTIONS)
    if exception_raw is None:
        return None, "committed immutable-history exception manifest is absent"
    exception_introduction = introductions.get(_ARCHIVE_HISTORY_EXCEPTIONS)
    if exception_introduction is None:
        return None, "immutable-history exception manifest lacks one introduction"
    if _git_blob_oid(exception_raw) != exception_introduction[1]:
        return None, (
            "immutable-history exception manifest changed after introduction: "
            + _ARCHIVE_HISTORY_EXCEPTIONS
        )
    kinds_raw = archive_files.get(_ARCHIVE_KINDS_PATH)
    if kinds_raw is None:
        return None, "committed mailbox kind registry is absent"
    try:
        kinds = frozenset(kinds_raw.decode("utf-8").splitlines())
    except UnicodeDecodeError:
        return None, "committed mailbox kind registry is not UTF-8"
    baseline_raw = archive_files.get(_ARCHIVE_REPORT_BASELINE)
    if baseline_raw is None:
        return None, "committed pre-v3 report baseline is absent"
    try:
        baseline = check_go_schema.parse_baseline_manifest_bytes(baseline_raw)
    except check_go_schema.BaselineGenerationError as exc:
        return None, f"committed pre-v3 report baseline is invalid: {exc}"
    baseline_entries = {
        entry["path"]: entry["sha256"]
        for entry in baseline["reports"]
    }
    # The frozen exception manifest below is the sole membership/digest
    # authority. This older report baseline is only a fail-closed provenance
    # cross-check and can never add or rewrite an accepted exception.
    history_exceptions, exception_problem = _parse_history_exceptions(exception_raw)
    if exception_problem is not None or history_exceptions is None:
        return None, exception_problem or "immutable-history exceptions are unavailable"
    events = {
        path: raw
        for path, raw in archive_files.items()
        if path.startswith(_ARCHIVE_SENT_PREFIX) and path.endswith(".md")
    }
    introduced_review_events = {
        path for path in introductions if _canonical_review_event(path)
    }
    current_review_events = {
        path for path in events if _canonical_review_event(path)
    }
    missing = sorted(introduced_review_events - current_review_events)
    if missing:
        return None, (
            "immutable mailbox event is absent or renamed at HEAD: " + missing[0]
        )
    unintroduced = sorted(current_review_events - introduced_review_events)
    if unintroduced:
        return None, "committed mailbox event lacks an introduction: " + unintroduced[0]
    mismatched_events = {
        path
        for path in current_review_events
        if _git_blob_oid(events[path]) != introductions[path][1]
    }
    unmeasured_exceptions = sorted(set(history_exceptions) - mismatched_events)
    if unmeasured_exceptions:
        return None, (
            "immutable-history exception does not name a measured mismatch: "
            + unmeasured_exceptions[0]
        )
    for path, exception in sorted(history_exceptions.items()):
        introduction = introductions.get(path)
        if introduction != (
            exception.introduction_commit,
            exception.introduction_blob,
        ):
            return None, f"immutable-history exception introduction mismatch: {path}"
        raw = events[path]
        if (
            _git_blob_oid(raw) != exception.accepted_current_blob
            or hashlib.sha256(raw).hexdigest() != exception.accepted_current_sha256
        ):
            return None, f"immutable-history exception current digest mismatch: {path}"
        if (
            compact_pair_loop.REPORT_RE.fullmatch(path) is not None
            and baseline_entries.get(path) != exception.accepted_current_sha256
        ):
            return None, f"immutable-history report digest authority mismatch: {path}"
    frozen_legacy_reports = frozenset(
        path
        for path in current_review_events
        if compact_pair_loop.REPORT_RE.fullmatch(path) is not None
        and introductions[path][0] in cutoff_ancestors
    )
    return CommittedMailboxProjection(
        events,
        introductions,
        introduction_events,
        learning_cutover_events,
        learning_cutover_ancestors,
        kinds,
        frozen_legacy_reports,
        history_exceptions,
    ), None


def committed_mailbox_projection(
    repo_root: Path | str,
) -> tuple[CommittedMailboxProjection | None, str | None]:
    """Public one-pass projection API shared by status and coordination checks."""

    return _committed_mailbox_projection(Path(repo_root).resolve())


def _immutable_event(
    projection: CommittedMailboxProjection,
    path: str,
) -> tuple[str | None, str | None]:
    raw = projection.events.get(path)
    introduction = projection.introductions.get(path)
    if raw is None or introduction is None:
        return None, f"committed mailbox event lacks an introduction: {path}"
    commit, introduced_blob = introduction
    if _git_blob_oid(raw) != introduced_blob:
        if path in projection.history_exceptions:
            return commit, None
        return None, f"immutable mailbox event changed after introduction: {path}"
    return commit, None


def _learning_disposition_intent(path: str, raw: bytes) -> bool:
    """Match the publication predicate without treating ordinary prose as intent."""

    if not path.endswith("-decision.md"):
        return False
    try:
        text = raw.decode("utf-8", errors="strict")
    except UnicodeDecodeError:
        return False
    return protocol_mailbox.learning_disposition_intent(text)


def _learning_issue(path: str, message: str) -> CoordIssue:
    return CoordIssue(
        path.removeprefix("coordination/"),
        "invalid_committed_learning_history",
        "FATAL",
        message,
    )


def _parse_introduced_event(
    projection: CommittedMailboxProjection, path: str
) -> protocol_mailbox.CommittedEventRef:
    commit, _blob = projection.introductions[path]
    raw = projection.introduction_events[path]
    try:
        text = raw.decode("utf-8", errors="strict")
    except UnicodeDecodeError as exc:
        raise ValueError("introduced event is not UTF-8") from exc
    return protocol_mailbox.parse_committed_event_text(f"{path}@{commit}", text)


def _check_committed_learning_history(
    repo_root: Path, projection: CommittedMailboxProjection
) -> list[CoordIssue]:
    """Replay post-cutover learning events from their exact introduction bytes."""

    issues: list[CoordIssue] = []
    all_introduced_candidates = {
        path
        for path in projection.introductions
        if path.endswith("-learning-candidate.md")
    }
    all_introduced_dispositions = {
        path
        for path in projection.introductions
        if _learning_disposition_intent(path, projection.introduction_events[path])
    }
    all_current_dispositions = {
        path
        for path, raw in projection.events.items()
        if _learning_disposition_intent(path, raw)
    }
    cutover_dispositions = {
        path
        for path, raw in projection.learning_cutover_events.items()
        if _learning_disposition_intent(path, raw)
    }
    relevant_paths = (
        all_introduced_candidates
        | all_introduced_dispositions
        | all_current_dispositions
        | cutover_dispositions
    )
    cutover_paths = frozenset(projection.learning_cutover_events)
    extinct_pre_cutover = {
        path
        for path, (commit, _blob) in projection.introductions.items()
        if path not in cutover_paths
        and path not in projection.events
        and commit in projection.learning_cutover_ancestors
    }
    relevant_paths -= extinct_pre_cutover
    new_candidates = all_introduced_candidates - cutover_paths - extinct_pre_cutover
    new_dispositions = (
        all_introduced_dispositions - cutover_paths - extinct_pre_cutover
    )

    immutable_paths: set[str] = set()
    for path in sorted(relevant_paths):
        current = projection.events.get(path)
        expected = (
            projection.learning_cutover_events[path]
            if path in cutover_paths
            else projection.introduction_events[path]
        )
        if current is None:
            issues.append(
                _learning_issue(path, f"committed learning event deleted after introduction: {path}")
            )
        elif current != expected:
            issues.append(
                _learning_issue(path, f"committed learning event modified after introduction: {path}")
            )
        else:
            immutable_paths.add(path)

    parsed_candidates: dict[
        str, protocol_mailbox.LearningCandidateStatement
    ] = {}
    candidates_by_id: dict[str, list[str]] = {}
    enforced_candidates = all_introduced_candidates - extinct_pre_cutover
    for path in sorted(enforced_candidates):
        try:
            statement = protocol_mailbox.parse_learning_candidate_statement(
                _parse_introduced_event(projection, path)
            )
        except ValueError as exc:
            if path in new_candidates and path in immutable_paths:
                issues.append(
                    _learning_issue(path, f"committed learning candidate is invalid: {exc}")
                )
            continue
        parsed_candidates[path] = statement
        candidates_by_id.setdefault(statement.candidate_id, []).append(path)

    try:
        with protocol_mailbox.CommittedObjectBatchReader(repo_root) as proof_root:
            for path in sorted(new_candidates & immutable_paths):
                statement = parsed_candidates.get(path)
                if statement is None:
                    continue
                try:
                    protocol_mailbox.validate_learning_candidate_references(
                        proof_root, statement
                    )
                    protocol_mailbox.validate_learning_candidate_unique(
                        statement,
                        {
                            candidate_id: tuple(paths)
                            for candidate_id, paths in candidates_by_id.items()
                        },
                    )
                except ValueError as exc:
                    issues.append(_learning_issue(path, str(exc)))

            for path in sorted(new_dispositions & immutable_paths):
                try:
                    protocol_mailbox.validate_learning_disposition(
                        proof_root,
                        _parse_introduced_event(projection, path),
                        target_commit=projection.introductions[path][0],
                        target_context="disposition introduction commit",
                    )
                except ValueError as exc:
                    issues.append(
                        _learning_issue(
                            path,
                            f"committed learning disposition is invalid: {exc}",
                        )
                    )
    except ValueError as exc:
        issues.append(
            _learning_issue(
                "coordination/mailbox/sent/",
                f"committed learning proof batch is unavailable: {exc}",
            )
        )
    return issues


def _single_field(raw: bytes, prefix: str) -> str | None:
    try:
        lines = raw.decode("utf-8").splitlines()
    except UnicodeDecodeError:
        return None
    values = [line.removeprefix(prefix) for line in lines if line.startswith(prefix)]
    return values[0] if len(values) == 1 else None


def _mapped_request_operator(
    request_operators: dict[str, str], request_ref: str,
) -> tuple[str | None, str | None]:
    operator = request_operators.get(request_ref)
    if operator not in {"operator", "operator2"}:
        return None, f"active report has no mapped request operator: {request_ref}"
    return operator, None


def inspect_verify_review_state(
    repo_root: Path | str,
    coord_root: Path | str | None = None,
    *,
    projection_result: tuple[CommittedMailboxProjection | None, str | None]
    | None = None,
) -> VerifyReviewState:
    """Index pending requests and active failed verdicts from committed mail."""

    root = Path(repo_root).resolve()
    if not (root / ".git").exists():
        return VerifyReviewState(pending=(), failed=())
    projection, projection_problem = (
        projection_result
        if projection_result is not None
        else _committed_mailbox_projection(root)
    )
    if projection_problem is not None or projection is None:
        return VerifyReviewState(
            pending=(),
            failed=(),
            problem=projection_problem or "committed mailbox projection unavailable",
        )

    for path in sorted(
        candidate for candidate in projection.events if _canonical_review_event(candidate)
    ):
        _commit, immutable_problem = _immutable_event(projection, path)
        if immutable_problem is not None:
            return VerifyReviewState(pending=(), failed=(), problem=immutable_problem)

    cutover_introduction = projection.introductions.get(_REVIEW_STATE_CUTOVER_PATH)
    if (
        cutover_introduction is not None
        and cutover_introduction[0] != _REVIEW_STATE_CUTOVER_COMMIT
    ):
        return VerifyReviewState(
            pending=(),
            failed=(),
            problem=(
                "review-state cutover marker introduction mismatch: "
                f"{_REVIEW_STATE_CUTOVER_PATH}@{cutover_introduction[0]}"
            ),
        )

    cutover_exists = _projection_git(
        root, "cat-file", "-e", f"{_ACTIVE_FAILURE_CUTOVER_COMMIT}^{{commit}}"
    )
    if cutover_exists.returncode != 0:
        detail = cutover_exists.stderr.decode("utf-8", errors="replace").strip()
        return VerifyReviewState(
            pending=(),
            failed=(),
            problem=(
                "active-failure cutover commit is unavailable: "
                f"{_ACTIVE_FAILURE_CUTOVER_COMMIT}"
                + (f" ({detail})" if detail else "")
            ),
        )
    ancestry = _projection_git(
        root,
        "merge-base",
        "--is-ancestor",
        _ACTIVE_FAILURE_CUTOVER_COMMIT,
        "HEAD",
    )
    if ancestry.returncode != 0:
        return VerifyReviewState(
            pending=(),
            failed=(),
            problem="active-failure cutover commit is not an ancestor of HEAD",
        )
    post_cutover = _projection_git(
        root,
        "rev-list",
        f"{_ACTIVE_FAILURE_CUTOVER_COMMIT}..HEAD",
        "--",
        "coordination/mailbox/sent",
    )
    if post_cutover.returncode != 0:
        return VerifyReviewState(
            pending=(),
            failed=(),
            problem="post-cutover review history is unavailable",
        )
    try:
        post_cutover_lines = post_cutover.stdout.decode(
            "ascii", errors="strict"
        ).splitlines()
    except UnicodeDecodeError:
        return VerifyReviewState(
            pending=(),
            failed=(),
            problem="post-cutover review history is not ASCII",
        )
    if any(
        compact_pair_loop.SHA_RE.fullmatch(line) is None
        for line in post_cutover_lines
    ):
        return VerifyReviewState(
            pending=(),
            failed=(),
            problem="post-cutover review history contains an invalid commit",
        )
    post_cutover_review_commits = frozenset(post_cutover_lines)

    newest_paths: dict[str, str] = {}
    candidate_paths: list[tuple[str, str]] = []
    for path in projection.events:
        if path <= _REVIEW_STATE_CUTOVER_PATH:
            continue
        name = Path(path).name
        for operator in ("operator", "operator2"):
            if name.endswith(f"-to-{operator}-verify-request.md"):
                candidate_paths.append((operator, path))
                previous = newest_paths.get(operator)
                if previous is None or path > previous:
                    newest_paths[operator] = path

    requests: dict[str, CurrentVerifyRequest] = {}
    parsed_requests: dict[str, compact_pair_loop.VerifyRequest] = {}
    request_operators: dict[str, str] = {}
    for recipient, path in sorted(candidate_paths, key=lambda item: item[1]):
        raw = projection.events[path]
        commit, immutable_problem = _immutable_event(projection, path)
        if immutable_problem is not None:
            return VerifyReviewState(pending=(), failed=(), problem=immutable_problem)
        problem: str | None = None
        request = None
        try:
            mailbox_writer.validate_event_envelope_bytes(
                root, raw, path, kinds=projection.kinds
            )
            if commit is None:
                raise mailbox_writer.MailboxWriterError(
                    "request is not introduced by a committed revision"
                )
            request = compact_pair_loop.parse_verify_request_committed_bytes(
                root, path, commit, raw, allow_frozen_legacy=False
            )
            if request.assigned_operator != recipient:
                raise mailbox_writer.MailboxWriterError(
                    "request recipient does not match assigned Operator"
                )
            range_violations = compact_pair_loop.validate_request_range(root, request)
            if range_violations:
                raise compact_pair_loop.CompactPairError(
                    "; ".join(range_violations)
                )
        except (
            mailbox_writer.MailboxWriterError,
            compact_pair_loop.CompactPairError,
            OSError,
            UnicodeError,
        ) as exc:
            problem = str(exc)
        expected_digest = _PRE_CUTOVER_INVALID_REQUESTS.get((path, commit))
        observed_digest = hashlib.sha256(raw).hexdigest()
        grandfathered = (
            expected_digest is not None and observed_digest == expected_digest
        )
        current = CurrentVerifyRequest(
            path=path,
            commit=commit,
            assigned_operator=(
                request.assigned_operator
                if request is not None
                else recipient
            ),
            valid=problem is None,
            problem=problem,
            grandfathered=grandfathered,
        )
        if newest_paths[recipient] == path:
            requests[recipient] = current
        if request is not None and commit is not None and problem is None:
            request_ref = f"{path}@{commit}"
            parsed_requests[request_ref] = request
            request_operators[request_ref] = request.assigned_operator

    parsed_reports: dict[
        str, tuple[str, str, compact_pair_loop.VerificationReport]
    ] = {}
    for path, raw in sorted(projection.events.items()):
        if not path.endswith("-verification-report.md"):
            continue
        request_ref = _single_field(raw, "Verification request: ")
        request = parsed_requests.get(request_ref or "")
        if request is None:
            continue
        commit, immutable_problem = _immutable_event(projection, path)
        if immutable_problem is not None:
            return VerifyReviewState(pending=(), failed=(), problem=immutable_problem)
        try:
            mailbox_writer.validate_event_envelope_bytes(
                root, raw, path, kinds=projection.kinds
            )
            report = compact_pair_loop.parse_verification_report_committed_bytes(
                root,
                path,
                raw,
                frozen_legacy=path in projection.frozen_legacy_reports,
            )
        except (
            mailbox_writer.MailboxWriterError,
            compact_pair_loop.CompactPairError,
            OSError,
            UnicodeError,
        ):
            continue
        if compact_pair_loop.validate_report_binding(report, request):
            continue
        if commit is not None:
            parsed_reports[f"{path}@{commit}"] = (path, commit, report)

    valid_reports: list[
        tuple[str, str, compact_pair_loop.VerificationReport]
    ] = []
    for path, commit, report in parsed_reports.values():
        if report.supersedes is not None:
            target_ref = f"{report.supersedes[0]}@{report.supersedes[1]}"
            target = parsed_reports.get(target_ref)
            if target is None:
                continue
            if compact_pair_loop.supersession_report_violations(
                report, target[2]
            ):
                continue
        valid_reports.append((path, commit, report))

    superseded_reports = {
        f"{superseded_path}@{superseded_commit}"
        for _, _, report in valid_reports
        if report.supersedes is not None
        for superseded_path, superseded_commit in (report.supersedes,)
    }
    pending: list[CurrentVerifyRequest] = []
    failed: list[FailedVerifyRequest] = []
    active_reports_by_request: dict[
        str, list[tuple[str, str, compact_pair_loop.VerificationReport]]
    ] = {}
    for path, commit, report in valid_reports:
        if f"{path}@{commit}" in superseded_reports:
            continue
        request_ref = f"{report.request_path}@{report.request_commit}"
        active_reports_by_request.setdefault(request_ref, []).append(
            (path, commit, report)
        )
    for operator, request in requests.items():
        request_ref = f"{request.path}@{request.commit}" if request.commit else None
        reports = active_reports_by_request.get(request_ref or "", [])
        if not reports:
            pending.append(request)
    for request_ref, reports in active_reports_by_request.items():
        active_failures = [item for item in reports if item[2].verdict == "FAIL"]
        active_failures = [
            item
            for item in active_failures
            if (
                f"{item[0]}@{item[1]}" in _BASELINE_ACTIVE_FAILURE_REPORTS
                or item[1] in post_cutover_review_commits
            )
        ]
        if active_failures:
            assigned_operator, operator_problem = _mapped_request_operator(
                request_operators, request_ref
            )
            if operator_problem is not None or assigned_operator is None:
                return VerifyReviewState(
                    pending=(), failed=(), problem=operator_problem
                )
            path, commit, report = max(active_failures, key=lambda item: item[0])
            failed.append(FailedVerifyRequest(
                request_path=report.request_path,
                request_commit=report.request_commit,
                report_path=path,
                report_commit=commit,
                assigned_operator=assigned_operator,
            ))
    return VerifyReviewState(
        pending=tuple(sorted(pending, key=lambda item: item.assigned_operator)),
        failed=tuple(sorted(failed, key=lambda item: item.report_path)),
        grandfathered_history=tuple(sorted(projection.history_exceptions)),
    )


def inspect_current_verify_requests(
    repo_root: Path | str,
    coord_root: Path | str | None = None,
) -> list[CurrentVerifyRequest]:
    """Return the newest genuinely pending request for each Operator seat."""

    return list(inspect_verify_review_state(repo_root, coord_root).pending)


def _check_current_verify_requests(
    repo_root: Path,
    coord_root: Path,
    review_state: VerifyReviewState | None = None,
) -> list[CoordIssue]:
    issues: list[CoordIssue] = []
    state = review_state or inspect_verify_review_state(repo_root, coord_root)
    if state.problem is not None:
        issues.append(CoordIssue(
            "mailbox/sent/",
            "review_projection_unavailable",
            "FATAL",
            state.problem,
        ))
        return issues
    for request in state.pending:
        if request.valid:
            continue
        severity = "ADVISORY" if request.grandfathered else "FATAL"
        prefix = (
            "pre-cutover immutable request remains invalid"
            if request.grandfathered
            else "current request is invalid"
        )
        issues.append(CoordIssue(
            request.path.removeprefix("coordination/"),
            "invalid_current_verify_request",
            severity,
            f"{prefix} for {request.assigned_operator}: {request.problem}",
        ))
    for path in state.grandfathered_history:
        issues.append(CoordIssue(
            path.removeprefix("coordination/"),
            "grandfathered_review_history",
            "ADVISORY",
            f"exact pre-enforcement immutable-history exception remains active: {path}",
        ))
    for failed in state.failed:
        issues.append(CoordIssue(
            failed.report_path.removeprefix("coordination/"),
            "failed_current_verify_request",
            "ADVISORY",
            f"{failed.assigned_operator} returned FAIL for "
            f"{failed.request_path}@{failed.request_commit}; remediation required "
            f"({failed.report_path}@{failed.report_commit})",
        ))
    return issues


def _check_standalone_cursor_commits(git_root, n: int = 30) -> list[CoordIssue]:
    """ADVISORY: flag recent commits whose entire changeset is seen/*.txt.

    Standalone cursor-only commits inflate coordination overhead — the cursor
    advance should ride the next substantive commit (capacity audit
    wf_6be2ee18-f4b, lever #5). Best-effort + opt-in: returns [] if git is
    unavailable or git_root is not a repo. Never raises.
    """
    issues: list[CoordIssue] = []
    try:
        log = subprocess.run(["git", "log", "--format=%h", f"-{n}"],
                             cwd=str(git_root), capture_output=True, text=True, timeout=5)
        if log.returncode != 0:
            return issues
        for sha in log.stdout.split():
            dt = subprocess.run(
                ["git", "diff-tree", "--no-commit-id", "-r", "--root", "--name-only", sha],
                cwd=str(git_root), capture_output=True, text=True, timeout=5)
            files = [f for f in dt.stdout.splitlines() if f.strip()]
            if files and all(_SEEN_ONLY_RE.match(f) for f in files):
                issues.append(CoordIssue(
                    "coordination/mailbox/seen/", "standalone_cursor_commit", "ADVISORY",
                    f"commit {sha} changes only seen/*.txt — fold cursor advances into "
                    f"the next substantive commit (lever #5)"))
    except Exception:
        pass
    return issues


def _has_live_seat_artifact(text: str, role: str) -> bool:
    return any(rx.search(text) for rx in _LIVE_SEAT_ARTIFACT_RES[role])


def _check_coordinator_handoff_theater(docs_root: Path | str | None) -> list[CoordIssue]:
    """FATAL: coordinator cannot substitute helper output for live-seat handoffs.

    A coordinator artifact may route all seats, and it may record that live-seat
    handoffs are still owed. But if it presents an "All-Seat Handoff" as a
    completed aggregate, it must cite real live-seat mailbox or handoff artifacts
    for all four seats. Spawned subagent reports are advisory evidence only.
    """
    if docs_root is None:
        return []
    docs_root = Path(docs_root)
    if not docs_root.is_dir():
        return []

    issues: list[CoordIssue] = []
    for path in sorted(docs_root.glob("HANDOFF-coordinator-*.md")):
        text = path.read_text(errors="replace")
        lower = text.lower()
        if not _ALL_SEAT_HANDOFF_RE.search(text):
            continue
        if any(marker in lower for marker in _PENDING_LIVE_SEAT_MARKERS):
            continue
        # theater check is about the 4 PAIR seats' real work; coordinators are not cited subjects
        missing = [role for role in SEATS if not _has_live_seat_artifact(text, role)]
        if missing:
            issues.append(CoordIssue(
                f"docs/{path.name}",
                "coordinator_handoff_theater",
                "FATAL",
                "coordinator All-Seat Handoff lacks live-seat artifacts for "
                f"{', '.join(missing)}; subagent reports do not satisfy live-seat "
                "handoffs, cursors, or operator/coordinator authority",
            ))
    return issues


def run(coord_root: Path | str, since: str = "2026-06-11",
        now: str | None = None, git_root: Path | str | None = None,
        docs_root: Path | str | None = None,
        review_state: VerifyReviewState | None = None,
        committed_projection: tuple[
            CommittedMailboxProjection | None, str | None
        ] | None = None) -> list[CoordIssue]:
    coord_root = Path(coord_root).resolve()
    if now is None:
        now = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    names = _event_names(coord_root)
    issues: list[CoordIssue] = []
    issues += _check_cursors(coord_root, now, names)
    issues += _check_events(coord_root, since, names)
    # The bus lives at the git repo root; coord_root is <repo>/coordination, so its
    # parent is the repo root unless an explicit git_root is given (ADR-062).
    bus_repo_root = Path(git_root) if git_root else coord_root.parent
    projection_result = committed_projection
    if projection_result is None and (bus_repo_root / ".git").exists():
        projection_result = committed_mailbox_projection(bus_repo_root)
    if review_state is None and projection_result is not None:
        review_state = inspect_verify_review_state(
            bus_repo_root,
            coord_root,
            projection_result=projection_result,
        )
    issues += _unread_report(coord_root, names, bus_repo_root)
    issues += _check_current_verify_requests(
        bus_repo_root, coord_root, review_state=review_state
    )
    if projection_result is not None:
        projection, projection_problem = projection_result
        if projection_problem is not None or projection is None:
            issues.append(
                _learning_issue(
                    "coordination/mailbox/sent/",
                    projection_problem or "committed mailbox projection unavailable",
                )
            )
        else:
            issues += _check_committed_learning_history(bus_repo_root, projection)
    if git_root is not None:
        issues += _check_standalone_cursor_commits(git_root)
    issues += _check_coordinator_handoff_theater(docs_root)
    return issues


def main(argv=None) -> int:
    repo_root = Path(__file__).resolve().parent.parent
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--root", default=str(repo_root / "coordination"),
                    help="coordination/ directory (default: repo's)")
    ap.add_argument("--since", default="2026-06-11",
                    help="envelope checks apply to events on/after this date")
    ap.add_argument("--now", default=None, help=argparse.SUPPRESS)  # test aid
    ap.add_argument("--git-root", default=None,
                    help="repo root; when given, ADVISORY-flag standalone cursor-only "
                         "commits in recent history (lever #5). Omitted = skipped.")
    ap.add_argument("--docs-root", default=str(repo_root / "docs"),
                    help="docs/ directory for coordinator handoff protocol checks")
    args = ap.parse_args(argv)

    issues = run(args.root, since=args.since, now=args.now, git_root=args.git_root,
                 docs_root=args.docs_root)
    fatal = [i for i in issues if i.severity == "FATAL"]
    advisory = [i for i in issues if i.severity == "ADVISORY"]
    for i in issues:
        print(f"{i.severity:8s} {i.kind:18s} {i.path} — {i.message}")
    if not fatal and not advisory:
        print(f"OK — coordination clean ({len(issues)} INFO)")
    return 1 if fatal else 0


if __name__ == "__main__":
    sys.exit(main())
