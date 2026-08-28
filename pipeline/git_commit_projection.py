#!/usr/bin/env python3
"""Immutable, process-local Git commit graph for one pinned repository HEAD."""

from __future__ import annotations

import re
import subprocess
from collections.abc import Callable, Iterable, Mapping
from dataclasses import dataclass, field
from pathlib import Path
from types import MappingProxyType


FULL_SHA_RE = re.compile(r"[0-9a-f]{40}")
MAX_CANDIDATES = 20_000
MAX_GRAPH_NODES = 100_000
MAX_GRAPH_BYTES = 32 * 1024 * 1024


class CommitGraphProjectionError(ValueError):
    """The frozen repository identity or commit graph is unavailable."""


GitRunner = Callable[..., subprocess.CompletedProcess[bytes]]


def sanitized_git_environment() -> dict[str, str]:
    """Return the fixed read-only Git environment used by the projection."""

    return {
        "PATH": "/usr/bin:/bin",
        "LANG": "C",
        "LC_ALL": "C",
        "HOME": "/var/empty",
        "XDG_CONFIG_HOME": "/var/empty",
        "GIT_CONFIG_NOSYSTEM": "1",
        "GIT_CONFIG_GLOBAL": "/dev/null",
    }


def _run_git(
    root: Path,
    arguments: tuple[str, ...],
    *,
    input_bytes: bytes | None = None,
) -> subprocess.CompletedProcess[bytes]:
    return subprocess.run(
        [
            "/usr/bin/git",
            "--no-replace-objects",
            "--literal-pathspecs",
            "--no-optional-locks",
            "-C",
            str(root),
            *arguments,
        ],
        input=input_bytes,
        capture_output=True,
        check=False,
        env=sanitized_git_environment(),
    )


@dataclass(frozen=True)
class RepositoryIdentity:
    root: Path
    git_dir: Path
    head: str


def _identity(root: Path, runner: GitRunner) -> RepositoryIdentity:
    result = runner(
        root,
        (
            "rev-parse",
            "--path-format=absolute",
            "--show-toplevel",
            "--absolute-git-dir",
            "--verify",
            "HEAD^{commit}",
        ),
    )
    if result.returncode != 0:
        detail = result.stderr.decode("utf-8", errors="replace").strip()
        raise CommitGraphProjectionError(
            f"repository identity is unavailable: {detail or 'rev-parse failed'}"
        )
    try:
        lines = result.stdout.decode("utf-8", errors="strict").splitlines()
    except UnicodeDecodeError as exc:
        raise CommitGraphProjectionError("repository identity is not UTF-8") from exc
    if len(lines) != 3 or FULL_SHA_RE.fullmatch(lines[2]) is None:
        raise CommitGraphProjectionError("repository identity output is malformed")
    try:
        reported_root = Path(lines[0]).resolve(strict=True)
        git_dir = Path(lines[1]).resolve(strict=True)
    except OSError as exc:
        raise CommitGraphProjectionError("repository identity path is unavailable") from exc
    # Ask the filesystem whether these are the same directory rather than
    # comparing strings. On a case-insensitive volume `/Users/x/pipeline` and
    # `/Users/x/Pipeline` are ONE directory that Path.resolve() does not
    # normalize, so a caller entering by the lowercase spelling -- which is a
    # declared working directory of this machine's Claude harness -- got a
    # fabricated "root drifted" FATAL on every governance projection. Identity
    # is a filesystem fact, and samefile is how you ask for it.
    if reported_root != root and not _same_directory(reported_root, root):
        raise CommitGraphProjectionError(
            f"repository root drifted: expected {root}, observed {reported_root}"
        )
    return RepositoryIdentity(reported_root, git_dir, lines[2])


def _same_root(left: Path, right: Path) -> bool:
    """The one question every root comparison in this module has to ask.

    Three sites compared roots; the case-insensitivity fix reached one. Naming
    the comparison makes the next site use it by default instead of
    rediscovering `==`.
    """

    return left == right or _same_directory(left, right)


def _same_directory(left: Path, right: Path) -> bool:
    """True when two paths name one directory, case-insensitivity included."""

    try:
        return left.stat().st_ino == right.stat().st_ino and (
            left.stat().st_dev == right.stat().st_dev
        )
    except OSError:
        return False


def capture_repository_identity(
    repo_root: Path | str,
    *,
    runner: GitRunner = _run_git,
) -> RepositoryIdentity:
    """Capture one exact root/git-dir/HEAD identity before projection reads."""

    root = Path(repo_root).resolve(strict=True)
    return _identity(root, runner)


@dataclass(frozen=True)
class CommitGraphProjection:
    """One bounded graph projection, never cached or reused across HEAD changes."""

    identity: RepositoryIdentity
    object_types: Mapping[str, str]
    parents: Mapping[str, tuple[str, ...]]
    _runner: GitRunner = field(repr=False, compare=False)

    @classmethod
    def build(
        cls,
        repo_root: Path | str,
        candidate_object_ids: Iterable[str],
        *,
        runner: GitRunner = _run_git,
        expected_identity: RepositoryIdentity | None = None,
    ) -> "CommitGraphProjection":
        root = Path(repo_root).resolve(strict=True)
        observed = _identity(root, runner)
        if expected_identity is not None:
            # Filesystem identity, for the reason _identity() gives above, and
            # because that fix was applied there ONLY. This comparison sat one
            # function away with a plain `!=`, so entering by the lowercase
            # spelling kept fabricating a FATAL -- just with a different
            # message, which read as a different bug.
            if not _same_root(expected_identity.root, root) or observed != expected_identity:
                raise CommitGraphProjectionError(
                    "repository identity changed before commit graph projection"
                )
            before = expected_identity
        else:
            before = observed
        candidates = set(candidate_object_ids)
        if len(candidates) > MAX_CANDIDATES:
            raise CommitGraphProjectionError(
                f"commit projection exceeds {MAX_CANDIDATES} candidate objects"
            )
        invalid = sorted(value for value in candidates if FULL_SHA_RE.fullmatch(value) is None)
        if invalid:
            raise CommitGraphProjectionError(
                "commit projection candidate is not one full lowercase object ID"
            )
        ordered = sorted(candidates | {before.head})
        batch = runner(
            root,
            ("cat-file", "--batch-check=%(objectname) %(objecttype)"),
            input_bytes=("\n".join(ordered) + "\n").encode("ascii"),
        )
        if batch.returncode != 0:
            raise CommitGraphProjectionError("Git object-type batch failed")
        try:
            batch_lines = batch.stdout.decode("ascii", errors="strict").splitlines()
        except UnicodeDecodeError as exc:
            raise CommitGraphProjectionError("Git object-type batch is not ASCII") from exc
        if len(batch_lines) != len(ordered):
            raise CommitGraphProjectionError("Git object-type batch is truncated or extended")
        object_types: dict[str, str] = {}
        for requested, line in zip(ordered, batch_lines, strict=True):
            fields = line.split()
            if fields == [requested, "missing"]:
                object_types[requested] = "missing"
                continue
            if (
                len(fields) != 2
                or fields[0] != requested
                or fields[1] not in {"commit", "tree", "blob", "tag"}
            ):
                raise CommitGraphProjectionError("Git object-type batch is malformed")
            object_types[requested] = fields[1]
        if object_types.get(before.head) != "commit":
            raise CommitGraphProjectionError("pinned HEAD is not a commit")

        roots = sorted(
            object_id for object_id, object_type in object_types.items()
            if object_type == "commit"
        )
        graph = runner(
            root,
            (
                "rev-list",
                "--parents",
                "--topo-order",
                f"--max-count={MAX_GRAPH_NODES + 1}",
                "--stdin",
            ),
            input_bytes=("\n".join(roots) + "\n").encode("ascii"),
        )
        if graph.returncode != 0:
            raise CommitGraphProjectionError("Git commit graph projection failed")
        if len(graph.stdout) > MAX_GRAPH_BYTES:
            raise CommitGraphProjectionError(
                f"Git commit graph exceeds {MAX_GRAPH_BYTES} bytes"
            )
        try:
            graph_lines = graph.stdout.decode("ascii", errors="strict").splitlines()
        except UnicodeDecodeError as exc:
            raise CommitGraphProjectionError("Git commit graph is not ASCII") from exc
        if len(graph_lines) > MAX_GRAPH_NODES:
            raise CommitGraphProjectionError(
                f"Git commit graph exceeds {MAX_GRAPH_NODES} nodes"
            )
        parents: dict[str, tuple[str, ...]] = {}
        for line in graph_lines:
            fields = line.split()
            if not fields or any(FULL_SHA_RE.fullmatch(value) is None for value in fields):
                raise CommitGraphProjectionError("Git commit graph is malformed")
            commit, *commit_parents = fields
            if commit in parents:
                raise CommitGraphProjectionError("Git commit graph contains a duplicate node")
            parents[commit] = tuple(commit_parents)
        if any(root_commit not in parents for root_commit in roots):
            raise CommitGraphProjectionError("Git commit graph is truncated")
        if any(parent not in parents for values in parents.values() for parent in values):
            raise CommitGraphProjectionError("Git commit graph omits a referenced parent")

        after = _identity(root, runner)
        if after != before:
            raise CommitGraphProjectionError("repository identity changed during projection")
        return cls(
            before,
            MappingProxyType(object_types),
            MappingProxyType(parents),
            runner,
        )

    @property
    def head(self) -> str:
        return self.identity.head

    def matches_root(self, repo_root: Path | str) -> bool:
        try:
            return _same_root(Path(repo_root).resolve(strict=True), self.identity.root)
        except OSError:
            return False

    def require_commit(self, value: str, label: str) -> str:
        if FULL_SHA_RE.fullmatch(value) is None:
            raise CommitGraphProjectionError(
                f"{label} must be one full lowercase commit SHA"
            )
        if self.object_types.get(value) != "commit" or value not in self.parents:
            raise CommitGraphProjectionError(f"{label} commit does not resolve exactly")
        return value

    def is_ancestor(self, ancestor: str, descendant: str) -> bool:
        ancestor = self.head if ancestor == "HEAD" else self.require_commit(
            ancestor, "ancestor"
        )
        descendant = self.head if descendant == "HEAD" else self.require_commit(
            descendant, "descendant"
        )
        pending = [descendant]
        seen: set[str] = set()
        while pending:
            current = pending.pop()
            if current == ancestor:
                return True
            if current in seen:
                continue
            seen.add(current)
            pending.extend(self.parents[current])
        return False

    def ancestors_of(self, value: str) -> frozenset[str]:
        commit = self.head if value == "HEAD" else self.require_commit(value, "commit")
        pending = [commit]
        seen: set[str] = set()
        while pending:
            current = pending.pop()
            if current in seen:
                continue
            seen.add(current)
            pending.extend(self.parents[current])
        return frozenset(seen)

    def assert_current(self) -> None:
        if _identity(self.identity.root, self._runner) != self.identity:
            raise CommitGraphProjectionError(
                "repository identity changed after commit projection"
            )
