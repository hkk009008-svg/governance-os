#!/usr/bin/env python3
"""Shared mailbox protocol vocabulary."""

from __future__ import annotations

from dataclasses import dataclass
import os
from pathlib import Path
import re
import subprocess


ROOT = Path(__file__).resolve().parent.parent
KIND_FILE = ROOT / "coordination" / "mailbox" / "kinds.txt"
SEATS = ("director", "director2", "operator", "operator2")
# Oversight-inclusive receiving roster: the 4 pair seats + both coordinators.
# `all` is a broadcast TARGET only (kept in RECIPIENTS), never a real seat, so it
# is NOT in RECEIVING_SEATS. Every independent Python roster copy imports THIS as
# its source of truth (Slice 2.5 D1 consolidation); the 4 shell whitelists are
# hand-synced and guarded by the token-extraction test (spec §8 clause #2).
RECEIVING_SEATS = (*SEATS, "coordinator", "coordinator2")
SENDERS = (*SEATS, "coordinator", "coordinator2")
RECIPIENTS = (*RECEIVING_SEATS, "all")


def load_known_kinds(root: Path | None = None) -> frozenset[str]:
    base = root if root is not None else ROOT
    path = base / "coordination" / "mailbox" / "kinds.txt"
    kinds = []
    for line in path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if stripped and not stripped.startswith("#"):
            kinds.append(stripped)
    return frozenset(kinds)


KNOWN_KINDS = load_known_kinds()
COORDINATION_KINDS = KNOWN_KINDS - {"verification-report"}


_FULL_SHA_RE = re.compile(r"[0-9a-f]{40}")
_EVENT_PATH_RE = re.compile(
    r"coordination/mailbox/sent/"
    r"(?P<timestamp>\d{4}-\d{2}-\d{2}T\d{2}-\d{2}-\d{2}Z)-"
    r"(?P<sender>[a-z][a-z0-9]*)-to-"
    r"(?P<recipient>[a-z][a-z0-9]*)-"
    r"(?P<kind>[a-z][a-z0-9-]*)\.md"
)
_ENVELOPE_RE = re.compile(
    r"^\*\*When:\*\* (?P<when>\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z)"
    r" · \*\*From:\*\* (?P<sender>[a-z][a-z0-9]*) \(online\)$",
    re.MULTILINE,
)
_DIGEST_REF_RE = re.compile(r"sha256:[0-9a-f]{64}")


@dataclass(frozen=True)
class CommittedEventRef:
    """An event body and sender loaded from one exact committed Git blob."""

    ref: str
    path: str
    commit: str
    sender: str
    recipient: str
    kind: str
    when: str
    text: str


@dataclass(frozen=True)
class OwnershipProposalStatement:
    event: CommittedEventRef
    task_id: str
    parent_ref: str
    revision: int
    previous_owners: tuple[str, ...]
    proposed_owners: tuple[str, ...]
    outcome: str
    finding_refs: tuple[str, ...]


@dataclass(frozen=True)
class OwnershipAcceptanceStatement:
    event: CommittedEventRef
    task_id: str
    parent_ref: str
    revision: int
    previous_owners: tuple[str, ...]
    proposed_owners: tuple[str, ...]
    proposal_ref: str
    outcome: str
    finding_refs: tuple[str, ...]


@dataclass(frozen=True)
class TakeoverEvidenceStatement:
    event: CommittedEventRef
    task_id: str
    parent_ref: str
    revision: int
    observed_at: str
    fresh_work_state: str
    lock_state: str
    finding_refs: tuple[str, ...]


def _git(root: Path, *args: str) -> subprocess.CompletedProcess[str]:
    clean_env = {key: value for key, value in os.environ.items() if not key.startswith("GIT_")}
    clean_env.update({"LANG": "C", "LC_ALL": "C"})
    try:
        return subprocess.run(
            ["git", "--no-replace-objects", "-C", str(root), *args],
            encoding="utf-8",
            capture_output=True,
            check=True,
            env=clean_env,
        )
    except (OSError, subprocess.CalledProcessError, UnicodeError) as exc:
        raise ValueError("committed event reference is not readable") from exc


def _filename_timestamp_to_iso(value: str) -> str:
    return value[:11] + value[11:19].replace("-", ":") + "Z"


def load_committed_event_ref(root: Path, value: str) -> CommittedEventRef:
    """Load an exact full-SHA fixed-writer event without reading the worktree."""

    if not isinstance(value, str) or "@" not in value:
        raise ValueError("committed event reference must be path@full-sha")
    path, commit = value.rsplit("@", 1)
    if not _FULL_SHA_RE.fullmatch(commit):
        raise ValueError("committed event reference requires a lowercase full SHA")
    match = _EVENT_PATH_RE.fullmatch(path)
    if match is None:
        raise ValueError("committed event reference must name an exact sent event path")
    sender = match.group("sender")
    recipient = match.group("recipient")
    kind = match.group("kind")
    if sender not in SENDERS or recipient not in RECIPIENTS or kind not in KNOWN_KINDS:
        raise ValueError("committed event filename has an unknown envelope token")

    if _git(root, "cat-file", "-t", commit).stdout.strip() != "commit":
        raise ValueError("committed event reference must name a commit object")

    tree_entry = _git(root, "ls-tree", "--full-tree", commit, "--", path).stdout.rstrip("\n")
    try:
        metadata, committed_path = tree_entry.split("\t", 1)
        mode, object_type, _object_id = metadata.split(" ", 2)
    except ValueError as exc:
        raise ValueError("event path is absent from the named commit") from exc
    if committed_path != path or mode != "100644" or object_type != "blob":
        raise ValueError("event path is not a regular fixed-writer blob")

    text = _git(root, "show", f"{commit}:{path}").stdout
    envelope_lines = [line for line in text.splitlines() if line.startswith("**When:**")]
    if len(envelope_lines) != 1:
        raise ValueError("committed event requires exactly one fixed-writer envelope")
    envelope = _ENVELOPE_RE.fullmatch(envelope_lines[0])
    if envelope is None:
        raise ValueError("committed event has a malformed fixed-writer envelope")
    when = envelope.group("when")
    if envelope.group("sender") != sender:
        raise ValueError("filename sender does not match committed envelope sender")
    if when != _filename_timestamp_to_iso(match.group("timestamp")):
        raise ValueError("filename timestamp does not match committed envelope timestamp")
    return CommittedEventRef(
        ref=value,
        path=path,
        commit=commit,
        sender=sender,
        recipient=recipient,
        kind=kind,
        when=when,
        text=text,
    )


def _single_body_field(event: CommittedEventRef, label: str) -> str:
    prefix = f"{label}:"
    matches = [
        line[len(prefix) :].strip()
        for line in event.text.splitlines()
        if line.startswith(prefix)
    ]
    if len(matches) != 1 or not matches[0]:
        raise ValueError(f"event requires exactly one nonblank {label!r} field")
    return matches[0]


def _revision(event: CommittedEventRef) -> int:
    value = _single_body_field(event, "Contract revision")
    if not value.isascii() or not value.isdecimal():
        raise ValueError("contract revision must be a nonnegative decimal integer")
    return int(value)


def _owners(event: CommittedEventRef, label: str) -> tuple[str, ...]:
    values = tuple(part.strip() for part in _single_body_field(event, label).split(","))
    if not values or any(value not in RECEIVING_SEATS for value in values):
        raise ValueError(f"{label} must contain only known receiving seats")
    if len(values) != len(set(values)):
        raise ValueError(f"{label} must not contain duplicates")
    return values


def immutable_reference_is_canonical(value: str) -> bool:
    """Return whether a finding/contract reference has immutable exact shape."""

    if not isinstance(value, str):
        return False
    if _DIGEST_REF_RE.fullmatch(value):
        return True
    if "@" not in value:
        return False
    path, commit = value.rsplit("@", 1)
    return bool(_EVENT_PATH_RE.fullmatch(path) and _FULL_SHA_RE.fullmatch(commit))


def _finding_refs(event: CommittedEventRef) -> tuple[str, ...]:
    raw = _single_body_field(event, "Finding refs")
    if raw == "(none)":
        return ()
    values = tuple(part.strip() for part in raw.split(","))
    if any(not immutable_reference_is_canonical(value) for value in values):
        raise ValueError("finding refs must be immutable full-SHA event refs or sha256 digests")
    if len(values) != len(set(values)):
        raise ValueError("finding refs must be unique")
    return values


def _require_kind(event: CommittedEventRef, expected: str) -> None:
    if event.kind != expected:
        raise ValueError(f"expected a committed {expected!r} event")


def load_ownership_proposal_statement(root: Path, value: str) -> OwnershipProposalStatement:
    event = load_committed_event_ref(root, value)
    _require_kind(event, "proposal")
    return OwnershipProposalStatement(
        event=event,
        task_id=_single_body_field(event, "Task ID"),
        parent_ref=_single_body_field(event, "Parent contract"),
        revision=_revision(event),
        previous_owners=_owners(event, "Previous owners"),
        proposed_owners=_owners(event, "Proposed owners"),
        outcome=_single_body_field(event, "Outcome"),
        finding_refs=_finding_refs(event),
    )


def load_ownership_acceptance_statement(root: Path, value: str) -> OwnershipAcceptanceStatement:
    event = load_committed_event_ref(root, value)
    _require_kind(event, "proposal-reply")
    return OwnershipAcceptanceStatement(
        event=event,
        task_id=_single_body_field(event, "Task ID"),
        parent_ref=_single_body_field(event, "Parent contract"),
        revision=_revision(event),
        previous_owners=_owners(event, "Previous owners"),
        proposed_owners=_owners(event, "Proposed owners"),
        proposal_ref=_single_body_field(event, "Proposal ref"),
        outcome=_single_body_field(event, "Outcome"),
        finding_refs=_finding_refs(event),
    )


def load_takeover_evidence_statement(root: Path, value: str) -> TakeoverEvidenceStatement:
    event = load_committed_event_ref(root, value)
    _require_kind(event, "dispatch-claim")
    observed_at = _single_body_field(event, "Observed at")
    if observed_at != event.when:
        raise ValueError("takeover observation time must match the fixed-writer envelope")
    return TakeoverEvidenceStatement(
        event=event,
        task_id=_single_body_field(event, "Task ID"),
        parent_ref=_single_body_field(event, "Parent contract"),
        revision=_revision(event),
        observed_at=observed_at,
        fresh_work_state=_single_body_field(event, "Fresh work state"),
        lock_state=_single_body_field(event, "Lock state"),
        finding_refs=_finding_refs(event),
    )
