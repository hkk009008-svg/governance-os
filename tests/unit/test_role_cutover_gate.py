"""The role-identity boundary: what a retired seat name may still carry.

This question has been asked wrong twice and each wrong answer was a real
bypass, so the controls live together with the reasoning.

  Introduction date  -- lost to delete-and-reintroduce, because the projection
                        keeps the EARLIEST introduction by design.
  Path presence      -- lost to LAUNDERING: the path is still present, so
                        re-committing arbitrary new content at it republished
                        that content under a retired identity.
  Blob identity      -- what the gate asks now. Presence is inheritable;
                        content is not.
"""
from __future__ import annotations

from pathlib import Path

import check_coordination as cc
import mailbox_history


class _FakeGitResult:
    def __init__(self, returncode: int, stdout: bytes) -> None:
        self.returncode = returncode
        self.stdout = stdout


def _tree(entries: dict[str, str]) -> bytes:
    return b"\0".join(
        f"100644 blob {oid}\t{path}".encode() for path, oid in entries.items()
    ) + b"\0"


_HISTORICAL = "coordination/mailbox/sent/2026-07-01T00-00-00Z-director-to-operator-findings.md"
_FRESH = "coordination/mailbox/sent/2026-09-01T00-00-00Z-director-to-operator-findings.md"
_HYBRID = "coordination/mailbox/sent/2026-09-02T00-00-00Z-author-to-operator-findings.md"
_LAWFUL = "coordination/mailbox/sent/2026-09-03T00-00-00Z-author-to-reviewer-findings.md"


_PRE = "a" * 40    # a commit that precedes the cutover
_POST = "b" * 40   # a commit that does not


def _gate(events, at_cutover, at_head, *, boundary=True, introductions=None):
    class _Commits:
        object_types = (
            {
                mailbox_history._ROLE_CUTOVER_COMMIT: "commit",
                _PRE: "commit",
                _POST: "commit",
            }
            if boundary
            else {}
        )

        @staticmethod
        def is_ancestor(candidate, target):
            return candidate == _PRE

    class _Projection:
        commits = _Commits()

    projection = _Projection()
    projection.events = events
    projection.introductions = introductions or {}

    def run_git(repo_root, *args):
        tree = at_head if "HEAD" in args else at_cutover
        return _FakeGitResult(0, _tree(tree)) if tree is not None else _FakeGitResult(128, b"")

    return mailbox_history._check_post_cutover_identities(
        projection, cc.CoordIssue, cc._ARCHIVE_SENT_PREFIX, run_git, Path(".")
    )


def test_a_retired_identity_must_carry_its_cutover_bytes() -> None:
    """The boundary is blob identity, because presence is inheritable.

    Asked twice before and wrong both times. Introduction date lost to
    delete-and-reintroduce (the projection keeps the EARLIEST introduction).
    Path presence lost to LAUNDERING: re-committing arbitrary new content at a
    path that already existed republished it under a retired identity while the
    path stayed present. Blob identity is inheritable by nothing.

    One control, four cases: unchanged history is lawful, laundered bytes are
    fatal, a brand-new event is fatal, a hybrid is caught on its recipient
    alone, and a fully live event is never touched.
    """

    issues = _gate(
        [_HISTORICAL, _FRESH, _HYBRID, _LAWFUL],
        at_cutover={_HISTORICAL: "1" * 40, _FRESH: "2" * 40},
        at_head={_HISTORICAL: "1" * 40, _FRESH: "3" * 40, _HYBRID: "4" * 40, _LAWFUL: "5" * 40},
        introductions={_HYBRID: (_POST, "4" * 40)},
    )

    flagged = {issue.path: issue.message for issue in issues}
    assert set(flagged) == {
        "mailbox/sent/2026-09-01T00-00-00Z-director-to-operator-findings.md",
        "mailbox/sent/2026-09-02T00-00-00Z-author-to-operator-findings.md",
    }, flagged
    assert "different bytes" in flagged[
        "mailbox/sent/2026-09-01T00-00-00Z-director-to-operator-findings.md"
    ], "laundering must be named as laundering"
    assert "not present at" in flagged[
        "mailbox/sent/2026-09-02T00-00-00Z-author-to-operator-findings.md"
    ]
    assert all(issue.severity == "FATAL" for issue in issues)


def test_unchanged_history_is_never_flagged() -> None:
    """The corpus is byte-identical to itself; the gate must leave it alone."""

    assert _gate(
        [_HISTORICAL],
        at_cutover={_HISTORICAL: "1" * 40},
        at_head={_HISTORICAL: "1" * 40},
    ) == []


def test_a_pre_boundary_event_merged_later_is_lawful() -> None:
    """A branch that predates the cutover must stay mergeable.

    A legacy verify-request authored before the boundary but living on a branch
    that never contained the boundary commit is absent from the cutover tree.
    Refusing it made the branch unmergeable while deleting the event is itself
    forbidden -- a deadlock with no lawful remedy. Ancestry of the INTRODUCTION
    separates "authored earlier, merged later" from "published after".
    """

    assert _gate(
        [_FRESH],
        at_cutover={},
        at_head={_FRESH: "9" * 40},
        introductions={_FRESH: (_PRE, "9" * 40)},
    ) == []


def test_an_event_that_cannot_be_shown_to_predate_the_boundary_is_refused() -> None:
    """No usable introduction record is not evidence of innocence."""

    issues = _gate(
        [_FRESH],
        at_cutover={},
        at_head={_FRESH: "9" * 40},
        introductions={},
    )

    assert [issue.kind for issue in issues] == ["post_cutover_retired_identity"]


def test_an_event_moved_to_archive_keeps_its_verdict() -> None:
    """Publishing under a retired identity then moving it must not clear it.

    The gate read HEAD's sent/ tree, so a follow-up commit moving the event to
    archive/ took the FATAL with it while the event stayed in history.
    """

    archived = _FRESH.replace("/sent/", "/archive/2026/")
    issues = _gate(
        [],
        at_cutover={},
        at_head={archived: "9" * 40},
        introductions={archived: (_POST, "9" * 40)},
    )

    assert [issue.kind for issue in issues] == ["post_cutover_retired_identity"]


def test_a_lost_boundary_with_post_cutover_state_fails_closed() -> None:
    """Same bytes must not get opposite verdicts in two clones.

    A squash, a rebase, or a clone made after the branch was deleted removes
    the pinned commit. Returning [] there made the gate silently inert while
    still reporting PASS.
    """

    issues = _gate([_HISTORICAL, _LAWFUL], None, None, boundary=False)

    assert [issue.kind for issue in issues] == ["post_cutover_identity_unavailable"]
    assert issues[0].severity == "FATAL"


def test_genuinely_pre_boundary_history_binds_nothing() -> None:
    """A history with no role-addressed events predates the cutover honestly."""

    assert _gate([_HISTORICAL], None, None, boundary=False) == []


def test_an_unlistable_tree_fails_closed() -> None:
    issues = _gate([_FRESH], at_cutover=None, at_head=None)

    assert [issue.kind for issue in issues] == ["post_cutover_identity_unavailable"]
    assert issues[0].severity == "FATAL"
