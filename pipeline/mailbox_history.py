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


def _tree_event_blobs(run_git, repo_root, commit: str, prefix: str):
    """event name -> every blob committed under that name at *commit*.

    Keyed by NAME, not by path, because the name is the protocol identity:
    EVENT_NAME_RE reads the sender and the recipient out of it, and
    `coordination/README.md` sanctions moving an event from `sent/` into
    `archive/` by hand for log hygiene. Keyed by path, that one lawful move
    read as a delete plus a create -- two FATALs for one tidy-up, against the
    519 retired-identity events the immutable-review projection does not pin.

    The value is a SET so the move stays free without making a second copy
    free: every blob a name carries has to answer for itself.
    """

    listed = run_git(
        repo_root, "ls-tree", "-r", "-z", commit, "--", prefix.rstrip("/")
    )
    if listed.returncode != 0:
        return None
    blobs: dict[str, set[str]] = {}
    for entry in listed.stdout.split(b"\0"):
        if not entry:
            continue
        meta, _, name = entry.partition(b"\t")
        fields = meta.split()
        if len(fields) >= 3:
            path = name.decode("utf-8", errors="replace")
            blobs.setdefault(Path(path).name, set()).add(fields[2].decode("ascii"))
    return blobs


def _check_post_cutover_identities(
    projection, issue_factory, sent_prefix, run_git, repo_root
) -> list:
    """A retired identity is lawful only with the BYTES it had at the cutover.

    This has been asked wrong three times and each wrong answer was a real
    bypass.

    Introduction DATE lost to delete-and-reintroduce: the projection keeps the
    EARLIEST introduction by design, so re-committing an event after the
    boundary brought its old introduction commit along with the new content.

    Path PRESENCE lost to laundering: the path survives a rewrite, so
    re-committing arbitrary content at a path that already existed published
    post-cutover bytes under a retired name and passed. Presence is inherited;
    content is not.

    Introduction ANCESTRY lost to Git. It was added to keep a branch older
    than the boundary mergeable, and it answered a temporal question with a
    topological test, which no direction of that test can do. A branch forked
    before the cutover is a SIBLING of it, not an ancestor, so the deadlock it
    was written to dissolve was never dissolved; and the mirrored form is
    forgeable by branching from any pre-boundary commit. It also compared no
    bytes, so a pre-cutover event deleted and re-committed with new content
    inherited its own earliest introduction and passed. It is gone with no
    replacement: a branch genuinely stuck behind the boundary takes a
    committed exception, which someone reviews, and a hatch is not reviewed.

    One question remains. Every blob an event name carries at HEAD must be a
    blob that name carried at the cutover commit. Absent there is a new
    publication; different there is a laundered one; a move between `sent/`
    and `archive/` is neither, so log hygiene stays free and the historical
    corpus -- byte-identical to itself -- is untouched.
    """

    commits = projection.commits
    live_events = [
        path
        for path in projection.events
        if path.startswith(sent_prefix)
        and (match := protocol_mailbox.EVENT_NAME_RE.fullmatch(Path(path).name))
        and not ({match.group("sender"), match.group("recipient")} - _LIVE_IDENTITIES)
    ]
    if commits.object_types.get(_ROLE_CUTOVER_COMMIT) != "commit":
        # Genuinely pre-boundary history binds nothing. A history that already
        # contains post-cutover state but has LOST the boundary -- a squash, a
        # rebase, a clone made after the branch was deleted -- must not answer
        # the same bytes differently from the checkout that produced them.
        if not live_events:
            return []
        return [issue_factory(
            "mailbox/sent/",
            "post_cutover_identity_unavailable",
            "FATAL",
            f"the role cutover {_ROLE_CUTOVER_COMMIT[:8]} is not in this "
            "history, but the mailbox already contains role-addressed events: "
            "the identity boundary cannot be checked and is not assumed to hold",
        )]

    # Both trees are read at the MAILBOX root, not at sent/ alone: an event
    # published under a retired identity and then moved to archive/ in a
    # follow-up commit left HEAD's sent/ tree and took the FATAL with it, while
    # the event stayed in committed history.
    mailbox_root = sent_prefix.rstrip("/").rsplit("/", 1)[0]
    at_cutover = _tree_event_blobs(run_git, repo_root, _ROLE_CUTOVER_COMMIT, mailbox_root)
    at_head = _tree_event_blobs(run_git, repo_root, "HEAD", mailbox_root)
    if at_cutover is None or at_head is None:
        return [issue_factory(
            "mailbox/sent/",
            "post_cutover_identity_unavailable",
            "FATAL",
            "cannot list the mailbox at the role cutover or at HEAD; the "
            "identity boundary cannot be checked and is not assumed to hold",
        )]

    issues: list = []
    names = set(at_head) | {Path(path).name for path in projection.events}
    for name in sorted(names):
        match = protocol_mailbox.EVENT_NAME_RE.fullmatch(name)
        if match is None:
            continue
        retired = {match.group("sender"), match.group("recipient")} - _LIVE_IDENTITIES
        if not retired:
            continue
        original = at_cutover.get(name, set())
        current = at_head.get(name, set())
        if current <= original:
            # Every blob it carries now is one it carried at the boundary.
            # Carrying none is a deletion, which this gate does not own: the
            # immutable-review projection refuses that for the events it pins.
            continue
        reason = (
            "carries different bytes than it had at" if original
            else "was not present at"
        )
        issues.append(issue_factory(
            f"mailbox/sent/{name}",
            "post_cutover_retired_identity",
            "FATAL",
            f"event carries retired identity {sorted(retired)} and {reason} "
            f"the role cutover {_ROLE_CUTOVER_COMMIT[:8]}: new events use "
            f"{' and '.join(sorted(protocol_mailbox.ROLES))}",
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
