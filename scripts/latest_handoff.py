#!/usr/bin/env python3
"""Select the newest durable canonical handoff for a concrete seat."""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from datetime import date, datetime, timezone
from pathlib import Path
import re
import subprocess
import sys

import git_runner
import protocol_mailbox


REPO_ROOT = Path(__file__).resolve().parent.parent
VALID_SEATS = frozenset(protocol_mailbox.RECEIVING_SEATS)
_METADATA_PREFIX_RE = re.compile(r"^(When|Created|Date):(.*)$")
_FULL_UTC_RE = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$")
_DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
_FILENAME_DATE_RE = re.compile(
    r"^HANDOFF-(?:director|director2|operator|operator2|coordinator)-"
    r"(\d{4}-\d{2}-\d{2})"
)
_METADATA_LINE_LIMIT = 20


@dataclass(frozen=True)
class HandoffSelection:
    seat: str
    pattern: str
    path: Path | None
    warnings: tuple[str, ...]


@dataclass(frozen=True)
class _Candidate:
    path: Path
    introduction_sha: str
    metadata_precision: int
    metadata_value: int


def canonical_pattern(seat: str) -> str:
    if seat not in VALID_SEATS:
        raise ValueError(f"unknown seat: {seat}")
    token = "coordinator" if seat.startswith("coordinator") else seat
    return f"HANDOFF-{token}-*.md"


def _warning_tokens(seat: str) -> tuple[str, ...]:
    if seat.startswith("coordinator"):
        return ("coordinator", "coordinator2")
    return (seat,)


def _is_near_match(path: Path, seat: str, pattern: str) -> bool:
    if path.name.startswith("HANDOFF-") is False or path.suffix != ".md":
        return False
    if path.match(pattern):
        return False
    tokens = path.stem.split("-")[1:]
    return any(token in tokens for token in _warning_tokens(seat))


def _git_text(root: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return git_runner.run_git(
        root, args, mode="authority", text=True
    )


def _git_bytes(root: Path, *args: str) -> subprocess.CompletedProcess[bytes]:
    return git_runner.run_git(
        root, args, mode="authority", text=False
    )


def _head_canonical_paths(
    root: Path, pattern: str
) -> tuple[set[str] | None, tuple[str, ...]]:
    tree = _git_text(root, "ls-tree", "-r", "--name-only", "-z", "HEAD", "--", "docs")
    if tree.returncode != 0:
        detail = tree.stderr.strip() or "git ls-tree failed"
        return None, (
            f"warning: Git chronology unavailable for canonical handoffs: {detail}",
        )
    paths = {
        relative
        for relative in tree.stdout.split("\0")
        if relative
        and Path(relative).parent == Path("docs")
        and Path(relative).match(f"docs/{pattern}")
    }
    return paths, ()


def _metadata_order(relative: str, content: bytes) -> tuple[int, int, tuple[str, ...]]:
    try:
        leading_lines = content.decode("utf-8").splitlines()[:_METADATA_LINE_LIMIT]
    except UnicodeDecodeError:
        return 0, 0, (
            f"warning: canonical handoff {relative} has unusable metadata: invalid UTF-8",
        )

    occurrences = [
        match
        for line in leading_lines
        if (match := _METADATA_PREFIX_RE.fullmatch(line)) is not None
    ]
    if len(occurrences) != 1:
        reason = "missing metadata" if not occurrences else "duplicate metadata"
        return 0, 0, (
            f"warning: canonical handoff {relative} has unusable metadata: {reason}",
        )

    value = occurrences[0].group(2).strip()
    try:
        if _FULL_UTC_RE.fullmatch(value):
            parsed = datetime.strptime(value, "%Y-%m-%dT%H:%M:%SZ").replace(
                tzinfo=timezone.utc
            )
            precision = 2
            order_value = int(parsed.timestamp())
            metadata_day = parsed.date().isoformat()
        elif _DATE_RE.fullmatch(value):
            parsed_day = date.fromisoformat(value)
            precision = 1
            order_value = parsed_day.toordinal()
            metadata_day = parsed_day.isoformat()
        else:
            raise ValueError("expected full UTC or date-only value")
    except (OverflowError, ValueError) as exc:
        return 0, 0, (
            f"warning: canonical handoff {relative} has unusable metadata: {exc}",
        )

    warnings: list[str] = []
    filename_match = _FILENAME_DATE_RE.match(Path(relative).name)
    if filename_match and filename_match.group(1) != metadata_day:
        warnings.append(
            f"warning: canonical handoff {relative} filename date "
            f"{filename_match.group(1)} disagrees with metadata date {metadata_day}"
        )
    return precision, order_value, tuple(warnings)


def _candidate(
    root: Path, path: Path, head_paths: set[str]
) -> tuple[_Candidate | None, tuple[str, ...], bool]:
    relative = path.relative_to(root).as_posix()
    if relative not in head_paths:
        return None, (
            f"warning: ignored canonical handoff {relative}: not tracked at HEAD",
        ), False
    if path.is_symlink():
        return None, (
            f"warning: ignored canonical handoff {relative}: not a regular non-symlink file",
        ), False
    if not path.exists():
        return None, (
            f"warning: ignored canonical handoff {relative}: missing from working tree",
        ), False
    if not path.is_file():
        return None, (
            f"warning: ignored canonical handoff {relative}: not a regular non-symlink file",
        ), False

    head_content = _git_bytes(root, "show", f"HEAD:{relative}")
    if head_content.returncode != 0:
        return None, (
            f"warning: ignored canonical handoff {relative}: HEAD content unavailable",
        ), True
    try:
        worktree_content = path.read_bytes()
    except OSError as exc:
        return None, (
            f"warning: ignored canonical handoff {relative}: unreadable working tree: {exc}",
        ), False
    if worktree_content != head_content.stdout:
        return None, (
            f"warning: ignored canonical handoff {relative}: working tree differs from HEAD",
        ), False

    history = _git_text(
        root,
        "log",
        "--diff-filter=A",
        "--format=%H",
        "--",
        relative,
    )
    introducing_shas = [line for line in history.stdout.splitlines() if line]
    if history.returncode != 0 or len(introducing_shas) != 1:
        detail = "unavailable" if not introducing_shas else "ambiguous"
        return None, (
            f"warning: ignored canonical handoff {relative}: "
            f"exact-path introduction {detail}",
        ), True
    introducing_sha = introducing_shas[0]
    reachable = _git_text(root, "merge-base", "--is-ancestor", introducing_sha, "HEAD")
    if reachable.returncode != 0:
        return None, (
            f"warning: ignored canonical handoff {relative}: "
            "exact-path introduction unreachable from HEAD",
        ), True

    precision, metadata_value, metadata_warnings = _metadata_order(
        relative, head_content.stdout
    )
    return (
        _Candidate(path, introducing_sha, precision, metadata_value),
        metadata_warnings,
        False,
    )


def _is_ancestor(root: Path, older: str, newer: str) -> bool | None:
    relation = _git_text(root, "merge-base", "--is-ancestor", older, newer)
    if relation.returncode == 0:
        return True
    if relation.returncode == 1:
        return False
    return None


def find_latest_handoff(root: Path, seat: str) -> HandoffSelection:
    pattern = canonical_pattern(seat)
    docs_root = root / "docs"
    warnings = [
        f"warning: ignored noncanonical same-seat handoff candidate docs/{path.name}; "
        f"expected {pattern}"
        for path in sorted(docs_root.glob("HANDOFF-*.md"))
        if _is_near_match(path, seat, pattern)
    ]

    head_paths, head_warnings = _head_canonical_paths(root, pattern)
    warnings.extend(head_warnings)
    if head_paths is None:
        return HandoffSelection(seat, pattern, None, tuple(warnings))

    worktree_paths = {
        path.relative_to(root).as_posix() for path in docs_root.glob(pattern)
    }
    valid_candidates: list[_Candidate] = []
    chronology_failed = False
    for relative in sorted(head_paths | worktree_paths):
        candidate, candidate_warnings, candidate_failed = _candidate(
            root, root / relative, head_paths
        )
        warnings.extend(candidate_warnings)
        chronology_failed = chronology_failed or candidate_failed
        if candidate is not None:
            valid_candidates.append(candidate)
    if chronology_failed:
        return HandoffSelection(seat, pattern, None, tuple(warnings))

    dominated: set[int] = set()
    for index, candidate in enumerate(valid_candidates):
        for other in valid_candidates:
            if candidate.introduction_sha == other.introduction_sha:
                continue
            relation = _is_ancestor(
                root, candidate.introduction_sha, other.introduction_sha
            )
            if relation is None:
                warnings.append(
                    "warning: Git chronology unavailable while comparing "
                    f"{candidate.introduction_sha} and {other.introduction_sha}"
                )
                return HandoffSelection(seat, pattern, None, tuple(warnings))
            if relation:
                dominated.add(index)
                break

    maximal = [
        candidate
        for index, candidate in enumerate(valid_candidates)
        if index not in dominated
    ]
    if len({item.introduction_sha for item in maximal}) > 1:
        warnings.append(
            "warning: canonical handoffs have incomparable introducing commits; "
            "applying bounded metadata tiebreak"
        )

    selected = max(
        maximal,
        key=lambda item: (item.metadata_precision, item.metadata_value, item.path.name),
        default=None,
    )
    if selected is not None:
        selected_order = (selected.metadata_precision, selected.metadata_value)
        tied = [
            item
            for item in maximal
            if (item.metadata_precision, item.metadata_value) == selected_order
        ]
        if len(tied) > 1:
            relative = selected.path.relative_to(root).as_posix()
            warnings.append(
                "warning: canonical handoffs share ancestry and metadata order; "
                f"selected {relative} by basename tiebreak"
            )

    return HandoffSelection(
        seat=seat,
        pattern=pattern,
        path=selected.path if selected else None,
        warnings=tuple(warnings),
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Print the newest durable canonical same-seat handoff."
    )
    parser.add_argument("seat", choices=protocol_mailbox.RECEIVING_SEATS)
    parser.add_argument("--root", type=Path, default=REPO_ROOT)
    args = parser.parse_args(argv)

    selection = find_latest_handoff(args.root, args.seat)
    for warning in selection.warnings:
        print(warning, file=sys.stderr)
    if selection.path is None:
        print(
            f"no canonical handoff found for {args.seat} under {args.root / 'docs'} "
            f"(expected {selection.pattern})",
            file=sys.stderr,
        )
        return 0
    print(selection.path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
