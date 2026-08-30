#!/usr/bin/env python3
"""Committed-history path compatibility across the scripts/ -> pipeline/ move."""
from __future__ import annotations

_REVIEWING_IDENTITIES = ("codex", "claude", "reviewer", "operator", "operator2")

# Current code names pipeline/ paths, while older commits store the same
# manifests under scripts/. Ask Git only for paths present at that commit and
# normalize archive members so downstream projection keys stay stable.
_LEGACY_PREFIX = "scripts/"
_CURRENT_PREFIX = "pipeline/"


def _legacy_twin(path: str) -> str:
    if not path.startswith(_CURRENT_PREFIX):
        return path
    return _LEGACY_PREFIX + path[len(_CURRENT_PREFIX):]


def _normalize_archive_name(name: str) -> str:
    if name.startswith(_LEGACY_PREFIX):
        return _CURRENT_PREFIX + name[len(_LEGACY_PREFIX):]
    return name


def _paths_present_at(repo_root, commit: str, candidates: tuple[str, ...], run_git):
    """Return the candidate paths that exist at one committed tree."""

    listed = run_git(
        repo_root, "ls-tree", "-r", "--name-only", "-z", commit, "--", *candidates
    )
    if listed.returncode != 0:
        return None
    return tuple(
        name.decode("utf-8", errors="replace")
        for name in listed.stdout.split(b"\0")
        if name
    )
