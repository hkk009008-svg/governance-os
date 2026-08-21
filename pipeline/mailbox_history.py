#!/usr/bin/env python3
"""Reading committed mailbox history across a rename and an identity cutover.

Two facts about this repository's past have to survive in the present. Its
Python moved from `scripts/` to `pipeline/`, so a manifest committed before
that move lives at the old path. And six seat names stopped being publishable
at a named commit, so an event carrying one is lawful history before that
boundary and a violation after it.

Both are read-side concerns and neither may become a licence to forget: a
manifest missing under BOTH prefixes is still a deletion, and an event that
crosses the cutover with a retired identity is still fatal.
"""
from __future__ import annotations

from pathlib import Path

import protocol_mailbox

_REVIEWING_IDENTITIES = ("reviewer", "operator", "operator2")

# The commit at which six seat names stopped being publishable. An event
# INTRODUCED after this boundary must use a live role on both sides; an event
# introduced before it keeps its historical identity forever. Restricting only
# the fixed writer left two open routes -- a hand-authored file plus `git add`,
# and a hybrid `author -> operator` envelope the writer's sender-only rule
# admitted -- so the boundary is enforced here, against committed bytes,
# where neither route can go around it.
_ROLE_CUTOVER_COMMIT = "4c4371fd953d68a986e46cd71c168a7f0b4e6382"
_LIVE_IDENTITIES = frozenset(protocol_mailbox.ROLES) | {"all"}


def _check_post_cutover_identities(projection, issue_factory, sent_prefix) -> list:
    """Refuse a retired seat name on an event introduced after the cutover."""

    commits = projection.commits
    if commits.object_types.get(_ROLE_CUTOVER_COMMIT) != "commit":
        return []  # the boundary is not in this history yet; nothing to bind
    issues: list = []
    for path, (introduced_at, _blob) in sorted(projection.introductions.items()):
        if not path.startswith(sent_prefix):
            continue
        match = protocol_mailbox.EVENT_NAME_RE.fullmatch(Path(path).name)
        if match is None:
            continue
        retired = {match.group("sender"), match.group("recipient")} - _LIVE_IDENTITIES
        if not retired:
            continue
        if commits.object_types.get(introduced_at) != "commit":
            continue
        if commits.is_ancestor(introduced_at, _ROLE_CUTOVER_COMMIT):
            continue  # introduced before the boundary: historical, and lawful
        issues.append(issue_factory(
            f"mailbox/sent/{Path(path).name}",
            "post_cutover_retired_identity",
            "FATAL",
            "event introduced after the role cutover uses retired identity "
            f"{sorted(retired)}: new events use "
            f"{' and '.join(sorted(protocol_mailbox.ROLES))} (introduced at "
            f"{introduced_at})",
        ))
    return issues


# The kernel's Python moved scripts/ -> pipeline/ when the repository became
# CLI-exclusive. Every constant above names the CURRENT path, but this module
# projects COMMITTED history, and a commit from before the move has its
# manifests under the old prefix. Asking git archive for a path that does not
# exist at that commit is a hard `fatal: pathspec ... did not match any
# files`, which surfaced as "projection unavailable" rather than as the
# rename it was. Each baseline therefore carries its twin; the archive is
# asked only for the paths that actually exist at the commit, and members are
# normalized back to the current name so every downstream key is stable.
_LEGACY_PREFIX = "scripts/"
_CURRENT_PREFIX = "pipeline/"


def _legacy_twin(path: str) -> str:
    """Anchored at the start, so `outside/pipeline/x` is never rewritten."""

    if not path.startswith(_CURRENT_PREFIX):
        return path
    return _LEGACY_PREFIX + path[len(_CURRENT_PREFIX):]


def _normalize_archive_name(name: str) -> str:
    """Anchored for the same reason as _legacy_twin."""

    if name.startswith(_LEGACY_PREFIX):
        return _CURRENT_PREFIX + name[len(_LEGACY_PREFIX):]
    return name


def _paths_present_at(repo_root, commit: str, candidates: tuple[str, ...], run_git):
    """The subset of *candidates* that exists at *commit*, asked of Git."""

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


