#!/usr/bin/env python3
"""Shared mailbox protocol vocabulary."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import os
from pathlib import Path, PurePosixPath
import re
import subprocess

import git_runner


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
# The seats a provider launcher or app binding may start. coordinator2 is
# cold capacity: a lawful mailbox identity (it can send, receive, and appear
# in committed history) that is not launchable and holds no app-seat binding
# until the standing topology explicitly warms it. This is the single
# declaration of that split; launchers, guards, and app-surface rosters
# import or are test-bound to it.
LAUNCHABLE_SEATS = (*SEATS, "coordinator")


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


def seat_alternation(names: tuple[str, ...]) -> str:
    """Regex alternation over seat names, longest-first so "director2" is
    tried before its "director" prefix. Public so composed patterns (e.g.
    check_coordination's per-role artifact scans) derive from the roster."""
    return "|".join(re.escape(name) for name in sorted(names, key=len, reverse=True))


# One canonical grammar for committed event filenames, derived from the seat
# roster above. Every Python parser imports EVENT_NAME_RE (or composes from
# EVENT_NAME_PATTERN); parser drift was a measured defect class — status
# accepted any sender, slope_metrics dropped the Z from the stamp and forbade
# digits in kinds. The import-light literal copy in
# threeway/legacy_projector.py is bound to this grammar by
# tests/unit/test_event_grammar_sync.py.
EVENT_STAMP_PATTERN = r"\d{4}-\d{2}-\d{2}T\d{2}-\d{2}-\d{2}Z"
EVENT_NAME_PATTERN = (
    rf"(?P<stamp>{EVENT_STAMP_PATTERN})-"
    rf"(?P<sender>{seat_alternation(SENDERS)})-to-"
    rf"(?P<recipient>{seat_alternation(RECIPIENTS)})-"
    r"(?P<kind>[a-z0-9-]+)\.md"
)
EVENT_NAME_RE = re.compile(rf"^{EVENT_NAME_PATTERN}$")

_EVENT_PATH_RE = re.compile(r"coordination/mailbox/sent/" + EVENT_NAME_PATTERN)
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


@dataclass(frozen=True)
class TakeoverConfirmationStatement:
    event: CommittedEventRef
    task_id: str
    parent_ref: str
    revision: int
    proposed_owner: str
    takeover_claim_ref: str
    observed_at: str
    finding_refs: tuple[str, ...]


class _CommittedEventBatchBackend:
    """Marker for the in-process exact-object proof backend."""

    def _protocol_load_committed_event_ref(self, value: str) -> CommittedEventRef:
        raise NotImplementedError

    def _protocol_committed_event_is_strict_ancestor(
        self,
        earlier: CommittedEventRef,
        later: CommittedEventRef,
    ) -> bool:
        raise NotImplementedError

    def _protocol_load_committed_blob(self, commit: str, path: str) -> bytes:
        raise NotImplementedError


class CommittedObjectBatchReader(_CommittedEventBatchBackend):
    """Resolve exact committed refs through one immutable Git object stream."""

    def __init__(self, root: Path) -> None:
        self.root = Path(root)
        self._entered = False
        self._process: subprocess.Popen[bytes] | None = None
        # These are process-local memoized immutable Git objects, not an
        # authority index or a worktree-derived cache.
        self._objects: dict[str, tuple[str, str, bytes] | None] = {}
        self._trees: dict[str, dict[bytes, tuple[str, str]]] = {}
        self._commits: dict[str, tuple[str, tuple[str, ...]]] = {}

    @staticmethod
    def _clean_env() -> dict[str, str]:
        env = {
            key: value for key, value in os.environ.items() if not key.startswith("GIT_")
        }
        env.update({"LANG": "C", "LC_ALL": "C"})
        return env

    def __enter__(self) -> CommittedObjectBatchReader:
        if self._entered:
            raise RuntimeError("CommittedObjectBatchReader cannot be entered twice")
        self._entered = True
        try:
            self._process = subprocess.Popen(
                [
                    "/usr/bin/git",
                    "--no-replace-objects",
                    "--no-optional-locks",
                    "-C",
                    str(self.root),
                    "cat-file",
                    "--batch",
                ],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                env=self._clean_env(),
            )
        except OSError as exc:
            raise ValueError("batch committed-object reader is unavailable") from exc
        return self

    def __exit__(self, exc_type, exc, traceback) -> None:
        process = self._process
        self._process = None
        if process is None:
            return
        if process.stdin is not None and not process.stdin.closed:
            try:
                process.stdin.close()
            except OSError:
                pass
        try:
            process.wait(timeout=2)
        except subprocess.TimeoutExpired:
            process.terminate()
            try:
                process.wait(timeout=2)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait(timeout=2)
        if process.stdout is not None:
            process.stdout.close()
        if process.stderr is not None:
            process.stderr.close()

    def _cat(self, expression: str) -> tuple[str, str, bytes] | None:
        if expression in self._objects:
            return self._objects[expression]
        process = self._process
        if process is None or process.stdin is None or process.stdout is None:
            raise ValueError("batch committed-object reader is not active")
        try:
            process.stdin.write(expression.encode("utf-8") + b"\n")
            process.stdin.flush()
            header = process.stdout.readline()
            if not header:
                raise ValueError("batch committed-object reader ended unexpectedly")
            fields = header.rstrip(b"\n").split(b" ")
            if fields[-1:] == [b"missing"]:
                self._objects[expression] = None
                return None
            if (
                len(fields) != 3
                or _FULL_SHA_RE.fullmatch(fields[0].decode("ascii")) is None
                or fields[1] not in {b"blob", b"tree", b"commit", b"tag"}
                or not fields[2].isdigit()
            ):
                raise ValueError("batch committed-object metadata is malformed")
            object_id = fields[0].decode("ascii")
            object_type = fields[1].decode("ascii")
            size = int(fields[2])
            body = process.stdout.read(size)
            terminator = process.stdout.read(1)
            if len(body) != size or terminator != b"\n":
                raise ValueError("batch committed-object content is truncated")
        except (BrokenPipeError, OSError, UnicodeError, ValueError) as exc:
            if isinstance(exc, ValueError):
                raise
            raise ValueError("batch committed-object reader failed") from exc
        result = (object_id, object_type, body)
        self._objects[expression] = result
        return result

    def _tree_entries(self, tree_id: str) -> dict[bytes, tuple[str, str]]:
        if tree_id in self._trees:
            return self._trees[tree_id]
        loaded = self._cat(tree_id)
        if loaded is None or loaded[1] != "tree":
            raise ValueError("committed path tree is not readable")
        raw = loaded[2]
        entries: dict[bytes, tuple[str, str]] = {}
        cursor = 0
        try:
            while cursor < len(raw):
                space = raw.index(b" ", cursor)
                nul = raw.index(b"\0", space + 1)
                mode = raw[cursor:space].decode("ascii")
                name = raw[space + 1 : nul]
                object_id = raw[nul + 1 : nul + 21].hex()
                if len(object_id) != 40 or name in entries:
                    raise ValueError
                entries[name] = (mode, object_id)
                cursor = nul + 21
        except (UnicodeError, ValueError) as exc:
            raise ValueError("committed tree object is malformed") from exc
        self._trees[tree_id] = entries
        return entries

    def _commit_tree_and_parents(self, commit: str) -> tuple[str, tuple[str, ...]]:
        if commit in self._commits:
            return self._commits[commit]
        loaded = self._cat(commit)
        if loaded is None or loaded[1] != "commit":
            raise ValueError("committed event reference must name a commit object")
        try:
            header = loaded[2].split(b"\n\n", 1)[0].decode("ascii")
        except UnicodeError as exc:
            raise ValueError("commit object headers are malformed") from exc
        tree: str | None = None
        parents: list[str] = []
        for line in header.splitlines():
            if line.startswith("tree "):
                tree = line[5:]
            elif line.startswith("parent "):
                parents.append(line[7:])
        if tree is None or not _FULL_SHA_RE.fullmatch(tree):
            raise ValueError("commit object has no canonical tree")
        if any(not _FULL_SHA_RE.fullmatch(parent) for parent in parents):
            raise ValueError("commit object has a malformed parent")
        result = (tree, tuple(parents))
        self._commits[commit] = result
        return result

    def _path_entry(self, commit: str, path: str) -> tuple[str, str, str, bytes]:
        tree_id, _parents = self._commit_tree_and_parents(commit)
        parts = path.split("/")
        for index, part in enumerate(parts):
            entry = self._tree_entries(tree_id).get(part.encode("utf-8"))
            if entry is None:
                raise ValueError("path is absent from the named commit")
            mode, object_id = entry
            if index < len(parts) - 1:
                if mode not in {"40000", "040000"}:
                    raise ValueError("committed path crosses a non-tree object")
                tree_id = object_id
                continue
            loaded = self._cat(object_id)
            if loaded is None:
                raise ValueError("committed path object is unreadable")
            return mode, loaded[1], object_id, loaded[2]
        raise ValueError("path is absent from the named commit")

    def _protocol_load_committed_event_ref(self, value: str) -> CommittedEventRef:
        path, commit, _match = _committed_event_parts(value)
        mode, object_type, _object_id, raw = self._path_entry(commit, path)
        if mode != "100644" or object_type != "blob":
            raise ValueError("event path is not a regular fixed-writer blob")
        try:
            text = raw.decode("utf-8", errors="strict")
        except UnicodeDecodeError as exc:
            raise ValueError("committed event body is not UTF-8") from exc
        return parse_committed_event_text(value, text)

    def _protocol_committed_event_is_strict_ancestor(
        self,
        earlier: CommittedEventRef,
        later: CommittedEventRef,
    ) -> bool:
        if earlier.commit == later.commit:
            return False
        pending = [later.commit]
        seen: set[str] = set()
        while pending:
            commit = pending.pop()
            if commit in seen:
                continue
            seen.add(commit)
            try:
                _tree, parents = self._commit_tree_and_parents(commit)
            except ValueError:
                return False
            if earlier.commit in parents:
                return True
            pending.extend(parents)
        return False

    def _protocol_load_committed_blob(self, commit: str, path: str) -> bytes:
        try:
            _mode, object_type, _object_id, raw = self._path_entry(commit, path)
        except ValueError as exc:
            raise ValueError(f"target is absent at commit {commit}: {path}") from exc
        if object_type != "blob":
            raise ValueError(f"target is absent at commit {commit}: {path}")
        return raw


def _git(root: Path, *args: str) -> subprocess.CompletedProcess[str]:
    try:
        return git_runner.run_git(
            root,
            args,
            mode="authority",
            text=True,
            encoding="utf-8",
            check=True,
        )
    except (OSError, subprocess.CalledProcessError, UnicodeError) as exc:
        raise ValueError("committed event reference is not readable") from exc


def _filename_timestamp_to_iso(value: str) -> str:
    return value[:11] + value[11:19].replace("-", ":") + "Z"


def _committed_event_parts(value: str) -> tuple[str, str, re.Match[str]]:
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
    return path, commit, match


def parse_committed_event_text(value: str, text: str) -> CommittedEventRef:
    """Parse fixed-writer bytes already proven to be ``value``'s exact blob."""

    path, commit, match = _committed_event_parts(value)
    if not isinstance(text, str):
        raise ValueError("committed event text must be decoded UTF-8")
    sender = match.group("sender")
    recipient = match.group("recipient")
    kind = match.group("kind")
    envelope_lines = [line for line in text.splitlines() if line.startswith("**When:**")]
    if len(envelope_lines) != 1:
        raise ValueError("committed event requires exactly one fixed-writer envelope")
    envelope = _ENVELOPE_RE.fullmatch(envelope_lines[0])
    if envelope is None:
        raise ValueError("committed event has a malformed fixed-writer envelope")
    when = envelope.group("when")
    if envelope.group("sender") != sender:
        raise ValueError("filename sender does not match committed envelope sender")
    if when != _filename_timestamp_to_iso(match.group("stamp")):
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


def load_committed_event_ref(root: Path, value: str) -> CommittedEventRef:
    """Load an exact full-SHA fixed-writer event without reading the worktree."""

    if isinstance(root, _CommittedEventBatchBackend):
        return root._protocol_load_committed_event_ref(value)
    path, commit, _match = _committed_event_parts(value)

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
    return parse_committed_event_text(value, text)


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


def parse_ownership_proposal_statement(
    event: CommittedEventRef,
) -> OwnershipProposalStatement:
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


def load_ownership_proposal_statement(root: Path, value: str) -> OwnershipProposalStatement:
    return parse_ownership_proposal_statement(load_committed_event_ref(root, value))


def parse_ownership_acceptance_statement(
    event: CommittedEventRef,
) -> OwnershipAcceptanceStatement:
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


def load_ownership_acceptance_statement(root: Path, value: str) -> OwnershipAcceptanceStatement:
    return parse_ownership_acceptance_statement(load_committed_event_ref(root, value))


def parse_takeover_evidence_statement(
    event: CommittedEventRef,
) -> TakeoverEvidenceStatement:
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


def load_takeover_evidence_statement(root: Path, value: str) -> TakeoverEvidenceStatement:
    return parse_takeover_evidence_statement(load_committed_event_ref(root, value))


def parse_takeover_confirmation_statement(
    event: CommittedEventRef,
) -> TakeoverConfirmationStatement:
    _require_kind(event, "acknowledgement")
    proposed_owner = _single_body_field(event, "Proposed owner")
    if proposed_owner not in SEATS:
        raise ValueError("takeover confirmation proposed owner must be a pair seat")
    takeover_claim_ref = _single_body_field(event, "Takeover claim ref")
    if not immutable_reference_is_canonical(takeover_claim_ref):
        raise ValueError("takeover confirmation requires an immutable claim ref")
    observed_at = _single_body_field(event, "Observed at")
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z", observed_at):
        raise ValueError("takeover confirmation observation must be ISO UTC")
    return TakeoverConfirmationStatement(
        event=event,
        task_id=_single_body_field(event, "Task ID"),
        parent_ref=_single_body_field(event, "Parent contract"),
        revision=_revision(event),
        proposed_owner=proposed_owner,
        takeover_claim_ref=takeover_claim_ref,
        observed_at=observed_at,
        finding_refs=_finding_refs(event),
    )


def load_takeover_confirmation_statement(
    root: Path, value: str
) -> TakeoverConfirmationStatement:
    return parse_takeover_confirmation_statement(load_committed_event_ref(root, value))


def committed_event_is_strict_ancestor(
    root: Path,
    earlier: CommittedEventRef,
    later: CommittedEventRef,
) -> bool:
    """Return whether ``later`` is committed strictly after ``earlier``."""

    if isinstance(root, _CommittedEventBatchBackend):
        return root._protocol_committed_event_is_strict_ancestor(earlier, later)
    if earlier.commit == later.commit:
        return False
    try:
        _git(root, "merge-base", "--is-ancestor", earlier.commit, later.commit)
    except ValueError:
        return False
    return True


# ---------------------------------------------------------------------------
# Learning-candidate lifecycle (read side) — ADR-067, contract §3.
#
# These parsers are typed readers over committed events; nothing here refuses
# a publication. Until the Stage 2b writer-side branch lands in
# scripts/mailbox_writer.py, a malformed or self-approved candidate/decision
# publishes durably and is caught only when a reader runs these functions
# (contract I4 states this; do not describe these checks as binding).
# ---------------------------------------------------------------------------

LEARNING_CATEGORIES = (
    "fact",
    "preference",
    "procedure",
    "episode-summary",
    "governance-rule",
)
LEARNING_SCOPES = ("repository", "workspace", "user")
LEARNING_DISPOSITIONS = ("accepted", "declined", "expired")

_CANDIDATE_ID_RE = re.compile(r"[0-9a-f]{64}")
_PROVIDER_SCOPE_RE = re.compile(r"provider:[a-z][a-z0-9-]*")
_LEARNING_ID_FIELD_ORDER = (
    "Category",
    "Scope",
    "Statement",
    "Proposed content hash",
    "Target",
    "Target base hash",
    "Source refs",
    "Evidence provenance",
    "Applicability",
    "Exclusions",
    "Risk class",
    "Supersedes",
    "Producer seat",
    "Producer model",
)


@dataclass(frozen=True)
class LearningCandidateStatement:
    event: CommittedEventRef
    candidate_id: str
    category: str
    scope: str
    statement: str
    proposed_content_hash: str | None
    target: str | None
    target_base_hash: str | None
    source_refs: tuple[str, ...]
    evidence_provenance: str
    applicability: str
    exclusions: str
    risk_class: str
    supersedes: str | None
    producer_seat: str
    producer_model: str


@dataclass(frozen=True)
class LearningDispositionStatement:
    event: CommittedEventRef
    candidate_ref: str
    disposition: str
    disposer_seat: str


def _optional_single_body_field(event: CommittedEventRef, label: str) -> str | None:
    prefix = f"{label}:"
    matches = [
        line[len(prefix) :].strip()
        for line in event.text.splitlines()
        if line.startswith(prefix)
    ]
    if not matches:
        return None
    if len(matches) != 1 or not matches[0]:
        raise ValueError(f"event allows at most one nonblank {label!r} field")
    return matches[0]


def compute_learning_candidate_id(fields: dict[str, str | None]) -> str:
    """sha256 of the normalized payload — the candidate's identity/dedup key.

    Normalization: the schema fields in fixed order, absent optionals
    omitted, each rendered ``Label: value`` with stripped values — and
    ``Source refs`` recanonicalized to comma-space separation, the same form
    the parser reconstructs, so an author writing ``a,b`` gets the identical
    ID the parser will recompute (round-two NIT: hashing the raw separator
    made the helper emit IDs its own parser refused). Content-derived
    identity makes a byte-identical duplicate detectable from committed
    events alone (contract §3).
    """

    import hashlib

    lines = []
    for label in _LEARNING_ID_FIELD_ORDER:
        value = fields.get(label)
        if value is None:
            continue
        if label == "Source refs":
            value = ", ".join(part.strip() for part in value.split(","))
        lines.append(f"{label}: {value.strip()}")
    return hashlib.sha256(("\n".join(lines) + "\n").encode("utf-8")).hexdigest()


def _learning_identity(value: str, label: str) -> str:
    if len(value) > 120 or any(ord(character) < 0x20 for character in value):
        raise ValueError(f"invalid {label}")
    return value


def parse_learning_candidate_statement(
    event: CommittedEventRef,
) -> LearningCandidateStatement:
    # The closed vocabularies are imported (not re-declared, contract §3) but
    # only when a learning event is read. Flat imports are the one supported
    # convention for scripts/ modules (tests/unit/test_import_identity.py).
    import claim_check
    import codex_protocol_model

    _require_kind(event, "learning-candidate")
    candidate_id = _single_body_field(event, "Candidate ID")
    if not _CANDIDATE_ID_RE.fullmatch(candidate_id):
        raise ValueError("Candidate ID must be a lowercase sha256 hex digest")
    category = _single_body_field(event, "Category")
    if category not in LEARNING_CATEGORIES:
        raise ValueError("Category must be one of the closed learning categories")
    scope = _single_body_field(event, "Scope")
    if scope not in LEARNING_SCOPES and not _PROVIDER_SCOPE_RE.fullmatch(scope):
        raise ValueError("Scope must be repository|workspace|user|provider:<name>")
    statement = _single_body_field(event, "Statement")
    proposed_content_hash = _optional_single_body_field(
        event, "Proposed content hash"
    )
    if proposed_content_hash is not None and not _DIGEST_REF_RE.fullmatch(
        proposed_content_hash
    ):
        raise ValueError("Proposed content hash must be sha256:<64-hex>")
    target = _optional_single_body_field(event, "Target")
    if target is not None:
        pure = PurePosixPath(target)
        if (
            pure.is_absolute()
            or not pure.parts
            or any(part in {"", ".", ".."} for part in pure.parts)
            or pure.as_posix() != target
            or "\\" in target
            or target.startswith("~")
            or any(
                ord(character) < 0x20 or ord(character) == 0x7F
                for character in target
            )
        ):
            raise ValueError("Target must be a canonical repository-relative POSIX path")
    target_base_hash = _optional_single_body_field(event, "Target base hash")
    if (target is None) != (target_base_hash is None):
        raise ValueError("Target and Target base hash are present together")
    if target_base_hash is not None and not _DIGEST_REF_RE.fullmatch(
        target_base_hash
    ):
        raise ValueError("Target base hash must be sha256:<64-hex>")
    raw_refs = _single_body_field(event, "Source refs")
    source_refs = tuple(part.strip() for part in raw_refs.split(","))
    if not source_refs or any(
        not immutable_reference_is_canonical(value) for value in source_refs
    ):
        raise ValueError(
            "Source refs must be immutable full-SHA event refs or sha256 digests"
        )
    if len(source_refs) != len(set(source_refs)):
        raise ValueError("Source refs must be unique")
    evidence_provenance = _single_body_field(event, "Evidence provenance")
    if evidence_provenance not in claim_check.PROVENANCE:
        raise ValueError(
            "Evidence provenance must be one of the claim_check ladder"
        )
    applicability = _single_body_field(event, "Applicability")
    exclusions = _single_body_field(event, "Exclusions")
    risk_class = _single_body_field(event, "Risk class")
    if risk_class not in codex_protocol_model.RISK_BASED_REVIEW_PROFILES:
        raise ValueError("Risk class must come from the closed set")
    supersedes = _optional_single_body_field(event, "Supersedes")
    if supersedes is not None:
        if not immutable_reference_is_canonical(supersedes):
            raise ValueError("Supersedes must be an immutable committed event ref")
        superseded_path = supersedes.rsplit("@", 1)[0]
        match = _EVENT_PATH_RE.fullmatch(superseded_path)
        if match is None or match.group("kind") != "learning-candidate":
            raise ValueError("Supersedes must name a learning-candidate event")
    producer_seat = _single_body_field(event, "Producer seat")
    if producer_seat not in SEATS:
        raise ValueError("Producer seat must be a pair seat")
    if producer_seat != event.sender:
        # A self-declared producer that differs from the envelope sender
        # would pre-defeat the Stage 2b self-approval refusal: publish under
        # a false label, then dispose your own candidate. No relay allowance
        # exists in the contract, so the binding is exact.
        raise ValueError("Producer seat must match the envelope sender")
    producer_model = _learning_identity(
        _single_body_field(event, "Producer model"), "Producer model"
    )
    expected = compute_learning_candidate_id(
        {
            "Category": category,
            "Scope": scope,
            "Statement": statement,
            "Proposed content hash": proposed_content_hash,
            "Target": target,
            "Target base hash": target_base_hash,
            "Source refs": ", ".join(source_refs),
            "Evidence provenance": evidence_provenance,
            "Applicability": applicability,
            "Exclusions": exclusions,
            "Risk class": risk_class,
            "Supersedes": supersedes,
            "Producer seat": producer_seat,
            "Producer model": producer_model,
        }
    )
    if candidate_id != expected:
        raise ValueError(
            "Candidate ID does not match the sha256 of the normalized payload"
        )
    return LearningCandidateStatement(
        event=event,
        candidate_id=candidate_id,
        category=category,
        scope=scope,
        statement=statement,
        proposed_content_hash=proposed_content_hash,
        target=target,
        target_base_hash=target_base_hash,
        source_refs=source_refs,
        evidence_provenance=evidence_provenance,
        applicability=applicability,
        exclusions=exclusions,
        risk_class=risk_class,
        supersedes=supersedes,
        producer_seat=producer_seat,
        producer_model=producer_model,
    )


def load_learning_candidate_statement(
    root: Path, value: str
) -> LearningCandidateStatement:
    return parse_learning_candidate_statement(load_committed_event_ref(root, value))


def parse_learning_disposition_statement(
    event: CommittedEventRef,
) -> LearningDispositionStatement:
    """Type a ``decision`` event that disposes a learning candidate.

    A ``decision`` event is a learning disposition exactly when it carries a
    ``Candidate:`` field; other decision events are untouched by this parser.
    """

    _require_kind(event, "decision")
    candidate_ref = _single_body_field(event, "Candidate")
    if not immutable_reference_is_canonical(candidate_ref):
        raise ValueError("Candidate must be an immutable committed event ref")
    candidate_path = candidate_ref.rsplit("@", 1)[0]
    match = _EVENT_PATH_RE.fullmatch(candidate_path)
    if match is None or match.group("kind") != "learning-candidate":
        raise ValueError("Candidate must name a learning-candidate event")
    disposition = _single_body_field(event, "Disposition")
    if disposition not in LEARNING_DISPOSITIONS:
        raise ValueError("Disposition must be accepted|declined|expired")
    return LearningDispositionStatement(
        event=event,
        candidate_ref=candidate_ref,
        disposition=disposition,
        disposer_seat=event.sender,
    )


def learning_disposition_intent(text: str) -> bool:
    """Return whether decision text carries the canonical machine intent shape."""

    if not isinstance(text, str):
        return False
    candidate_values = [
        line.removeprefix("Candidate:").strip()
        for line in text.splitlines()
        if line.startswith("Candidate:")
    ]
    return any(line.startswith("Disposition:") for line in text.splitlines()) and any(
        immutable_reference_is_canonical(value)
        and value.rsplit("@", 1)[0].endswith("-learning-candidate.md")
        for value in candidate_values
    )


def validate_learning_candidate_references(
    root: Path, statement: LearningCandidateStatement
) -> None:
    """Resolve every path ref; sha256 refs intentionally carry no local preimage."""

    for reference in statement.source_refs:
        if reference.startswith("sha256:"):
            continue
        try:
            load_committed_event_ref(root, reference)
        except ValueError as exc:
            raise ValueError(f"source ref does not resolve: {reference}") from exc
    if statement.supersedes is not None:
        try:
            load_learning_candidate_statement(root, statement.supersedes)
        except ValueError as exc:
            raise ValueError(
                f"Supersedes ref does not resolve: {statement.supersedes}"
            ) from exc


def validate_learning_candidate_unique(
    statement: LearningCandidateStatement,
    candidate_paths_by_id: dict[str, tuple[str, ...]],
) -> None:
    peers = tuple(
        path
        for path in candidate_paths_by_id.get(statement.candidate_id, ())
        if path != statement.event.path
    )
    if peers:
        raise ValueError(
            f"duplicate Candidate ID {statement.candidate_id}; peers: {', '.join(peers)}"
        )


def _committed_blob(root: Path, commit: str, path: str) -> bytes:
    if isinstance(root, _CommittedEventBatchBackend):
        return root._protocol_load_committed_blob(commit, path)
    try:
        result = git_runner.run_git(
            root,
            ("cat-file", "blob", f"{commit}:{path}"),
            mode="authority",
            check=True,
        )
    except (OSError, subprocess.CalledProcessError) as exc:
        raise ValueError(f"target is absent at commit {commit}: {path}") from exc
    return result.stdout


def validate_learning_disposition(
    root: Path,
    event: CommittedEventRef,
    *,
    target_commit: str,
    target_context: str = "disposition commit",
) -> tuple[LearningDispositionStatement, LearningCandidateStatement]:
    """Apply the shared disposition policy at one exact target-tree commit."""

    disposition = parse_learning_disposition_statement(event)
    try:
        candidate = load_learning_candidate_statement(root, disposition.candidate_ref)
    except ValueError as exc:
        raise ValueError(
            "Candidate does not resolve to a committed learning-candidate"
        ) from exc
    if disposition.disposer_seat == candidate.producer_seat:
        raise ValueError("disposer equals candidate producer (self-approval)")
    if disposition.disposition != "accepted":
        return disposition, candidate
    if candidate.evidence_provenance == "ASSUMED":
        raise ValueError("ASSUMED-provenance candidate may not be accepted")
    if (
        candidate.category == "governance-rule"
        and candidate.risk_class != "high-risk-control"
    ):
        raise ValueError(
            "governance-rule candidate below the high-risk-control floor may not be accepted"
        )
    if candidate.target is not None:
        data = _committed_blob(root, target_commit, candidate.target)
        digest = "sha256:" + hashlib.sha256(data).hexdigest()
        if digest != candidate.target_base_hash:
            raise ValueError(
                f"target base hash is stale at the {target_context} (CAS)"
            )
    return disposition, candidate


def committed_learning_candidate_ids(root: Path, commit: str) -> dict[str, str]:
    """Map Candidate ID -> event path for parseable committed candidates.

    Dedup derives from committed ``sent/`` events at the pinned commit — a
    deterministic scan of the same substrate the parsers read — never from
    the gitignored local index, which gives checkout-dependent verdicts
    (contract §3). Malformed committed candidates are skipped, not fatal:
    this is a read-side projection, not a gate. When two committed events
    carry the same Candidate ID (a byte-idempotent republish that predates
    Stage 2b, or one that bypassed the writer), the FIRST path in tree order
    wins — the ID names one content, so either path serves it.
    """

    resolved = _git(root, "rev-parse", commit).stdout.strip()
    listing = _git(
        root, "ls-tree", "-r", resolved, "--name-only", "coordination/mailbox/sent"
    ).stdout
    ids: dict[str, str] = {}
    for path in listing.splitlines():
        if not path.endswith("-learning-candidate.md"):
            continue
        try:
            statement = load_learning_candidate_statement(
                root, f"{path}@{resolved}"
            )
        except ValueError:
            continue
        ids.setdefault(statement.candidate_id, path)
    return ids


# ---------------------------------------------------------------------------
# Reintroduction doctrine (delete/revert cycles)
#
# One rule, shared by every consumer of committed-path introduction history:
# byte-identical restoration of a committed mailbox artifact is not mutation
# — the earliest introduction stays the immutable identity — while a
# reintroduction with DIFFERENT bytes is the laundering vector and stays
# refused. Consumers today: the committed-mailbox projection
# (scripts/check_coordination.py, which keeps its own single-pass stream
# walk for performance) and the frozen-history helpers in
# scripts/compact_pair_loop.py, which call the primitives below.
# tests/unit/test_reintroduction_doctrine.py is the cross-consumer
# contract; a new consumer of these primitives belongs in that module.
# ---------------------------------------------------------------------------


def committed_blob_or_none(root: Path, commit: str, path: str) -> bytes | None:
    """Exact committed blob bytes, or None when absent at that commit."""

    try:
        return _committed_blob(root, commit, path)
    except ValueError:
        return None


def path_introduction_commits(root: Path, path: str) -> tuple[str, ...]:
    """Every commit that ADDED the path in HEAD's history, newest-first."""

    out = _git(root, "log", "--diff-filter=A", "--format=%H", "HEAD", "--", path)
    commits = tuple(line for line in out.stdout.splitlines() if line)
    if any(_FULL_SHA_RE.fullmatch(commit) is None for commit in commits):
        raise ValueError("path introduction history is unreadable")
    return commits


def newest_commit_touching(root: Path, path: str) -> str | None:
    """The newest commit in HEAD's history that touched the path, if any."""

    out = _git(root, "log", "-1", "--format=%H", "HEAD", "--", path)
    value = out.stdout.strip()
    return value if _FULL_SHA_RE.fullmatch(value) else None


# ---------------------------------------------------------------------------
# Checkpoint statements (durable continuation records)
# ---------------------------------------------------------------------------

CHECKPOINT_BOUNDARIES = ("transfer", "interruption", "compaction", "wrap")
CHECKPOINT_NONE = "none"
CHECKPOINT_LESSONS_NONE = "none-considered"

_CHECKPOINT_SLUG_RE = re.compile(r"[a-z0-9][a-z0-9-]{0,79}")


@dataclass(frozen=True)
class CheckpointStatement:
    """One durable continuation record (AGENTS.md universal contract item 7).

    A checkpoint is a ``findings`` event typed at read time by its
    ``Checkpoint:`` and ``Next action:`` fields, exactly as a learning
    disposition is a ``decision`` event typed by ``Candidate:`` plus
    ``Disposition:``. It carries the payload that must survive a transfer,
    an interruption, or context compaction: objective, accepted scope,
    owner, policy revision, base/head, evidence refs, verification status,
    unresolved blockers, the next executable action, and the boundary
    lessons answer. Advisory under learning contract I1/I2 — a checkpoint
    recalls state; it grants no task, review, or effect authority, and
    current Git plus committed event bodies outrank it.
    """

    event: CommittedEventRef
    checkpoint: str
    boundary: str
    objective: str
    accepted_scope: str
    owner: str
    policy_revision: str
    base: str
    head: str
    evidence_refs: tuple[str, ...]
    verification_status: str
    blockers: str
    next_action: str
    lessons: tuple[str, ...]


def parse_checkpoint_statement(event: CommittedEventRef) -> CheckpointStatement:
    _require_kind(event, "findings")
    checkpoint = _single_body_field(event, "Checkpoint")
    if not _CHECKPOINT_SLUG_RE.fullmatch(checkpoint):
        raise ValueError(
            "Checkpoint must be a lowercase slug (a-z, 0-9, hyphens, <=80)"
        )
    boundary = _single_body_field(event, "Boundary")
    if boundary not in CHECKPOINT_BOUNDARIES:
        raise ValueError("Boundary must be transfer|interruption|compaction|wrap")
    objective = _single_body_field(event, "Objective")
    accepted_scope = _single_body_field(event, "Accepted scope")
    owner = _single_body_field(event, "Owner")
    if owner not in SEATS:
        raise ValueError("Owner must be a pair seat")
    if owner != event.sender:
        # A checkpoint claiming another seat's ownership would launder a
        # transfer that never happened; the binding is exact, mirroring the
        # learning-candidate producer-seat rule.
        raise ValueError("Owner must match the envelope sender")
    policy_revision = _single_body_field(event, "Policy revision")
    base = _single_body_field(event, "Base")
    head = _single_body_field(event, "Head")
    for label, value in (
        ("Policy revision", policy_revision),
        ("Base", base),
        ("Head", head),
    ):
        if not _FULL_SHA_RE.fullmatch(value):
            # Shape only, deliberately: a routed-target range resolves in the
            # target repository, not in Pipeline, so demanding local
            # resolution here would refuse honest checkpoints.
            raise ValueError(f"{label} must be a 40-hex commit SHA")
    raw_evidence = _single_body_field(event, "Evidence refs")
    if raw_evidence == CHECKPOINT_NONE:
        evidence_refs: tuple[str, ...] = ()
    else:
        evidence_refs = tuple(part.strip() for part in raw_evidence.split(","))
        if any(
            not immutable_reference_is_canonical(value) for value in evidence_refs
        ):
            raise ValueError(
                "Evidence refs must be immutable full-SHA event refs or "
                "sha256 digests, or the single word none"
            )
        if len(evidence_refs) != len(set(evidence_refs)):
            raise ValueError("Evidence refs must be unique")
    verification_status = _single_body_field(event, "Verification status")
    blockers = _single_body_field(event, "Blockers")
    next_action = _single_body_field(event, "Next action")
    raw_lessons = _single_body_field(event, "Lessons")
    if raw_lessons == CHECKPOINT_LESSONS_NONE:
        lessons: tuple[str, ...] = ()
    else:
        lessons = tuple(part.strip() for part in raw_lessons.split(","))
        for value in lessons:
            if not immutable_reference_is_canonical(value) or value.startswith(
                "sha256:"
            ):
                raise ValueError(
                    "Lessons must be learning-candidate event refs or the "
                    "single word none-considered"
                )
            lesson_path = value.rsplit("@", 1)[0]
            match = _EVENT_PATH_RE.fullmatch(lesson_path)
            if match is None or match.group("kind") != "learning-candidate":
                raise ValueError("Lessons refs must name learning-candidate events")
        if len(lessons) != len(set(lessons)):
            raise ValueError("Lessons refs must be unique")
    return CheckpointStatement(
        event=event,
        checkpoint=checkpoint,
        boundary=boundary,
        objective=objective,
        accepted_scope=accepted_scope,
        owner=owner,
        policy_revision=policy_revision,
        base=base,
        head=head,
        evidence_refs=evidence_refs,
        verification_status=verification_status,
        blockers=blockers,
        next_action=next_action,
        lessons=lessons,
    )


def checkpoint_intent(text: str) -> bool:
    """Return whether findings text carries the canonical checkpoint shape.

    Two-field discipline, mirroring ``learning_disposition_intent``: prose
    that merely mentions ``Checkpoint:`` never enters checkpoint parsing;
    text carrying both a slug-shaped ``Checkpoint:`` field and a
    ``Next action:`` field is exactly what a reader would parse as a
    checkpoint, so validating it at publication is correct.
    """

    if not isinstance(text, str):
        return False
    checkpoint_values = [
        line.removeprefix("Checkpoint:").strip()
        for line in text.splitlines()
        if line.startswith("Checkpoint:")
    ]
    return any(
        line.startswith("Next action:") for line in text.splitlines()
    ) and any(
        _CHECKPOINT_SLUG_RE.fullmatch(value) for value in checkpoint_values
    )


def validate_checkpoint_references(
    root: Path, statement: CheckpointStatement
) -> None:
    """Resolve every path ref; sha256 refs intentionally carry no local preimage."""

    for reference in (*statement.evidence_refs, *statement.lessons):
        if reference.startswith("sha256:"):
            continue
        try:
            load_committed_event_ref(root, reference)
        except ValueError as exc:
            raise ValueError(f"checkpoint ref does not resolve: {reference}") from exc


def load_checkpoint_statement(root: Path, value: str) -> CheckpointStatement:
    return parse_checkpoint_statement(load_committed_event_ref(root, value))


def committed_checkpoints(root: Path, commit: str) -> tuple[CheckpointStatement, ...]:
    """Parseable committed checkpoints at the pinned commit, oldest first.

    A read-side projection, not a gate: malformed committed findings are
    skipped exactly as ``committed_learning_candidate_ids`` skips malformed
    candidates.
    """

    resolved = _git(root, "rev-parse", commit).stdout.strip()
    listing = _git(
        root, "ls-tree", "-r", resolved, "--name-only", "coordination/mailbox/sent"
    ).stdout
    statements: list[CheckpointStatement] = []
    for path in sorted(listing.splitlines()):
        if not path.endswith("-findings.md"):
            continue
        try:
            event = load_committed_event_ref(root, f"{path}@{resolved}")
        except ValueError:
            continue
        if not checkpoint_intent(event.text):
            continue
        try:
            statements.append(parse_checkpoint_statement(event))
        except ValueError:
            continue
    return tuple(statements)
