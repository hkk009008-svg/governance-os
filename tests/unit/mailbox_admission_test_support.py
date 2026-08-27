"""Fixtures for committed desktop-mailbox admission controls."""
from __future__ import annotations

from pathlib import Path

import check_coordination as coordination
import mailbox_admission
import mailbox_review_admission
import protocol_mailbox

POST = "b" * 40
PRE = "a" * 40
HISTORICAL = (
    "coordination/mailbox/sent/"
    "2026-07-01T00-00-00Z-director-to-operator-findings.md"
)
APP_FINDINGS = (
    "coordination/mailbox/sent/"
    "2026-09-03T00-00-00Z-codex-to-all-findings.md"
)
APP_STATUS = (
    "coordination/mailbox/sent/"
    "2026-09-05T00-00-00Z-codex-to-claude-status.md"
)
APP_FORMAL = (
    "coordination/mailbox/sent/"
    "2026-09-06T00-00-00Z-codex-to-reviewer-verify-request.md"
)
ORPHAN_REPORT = (
    "coordination/mailbox/sent/"
    "2026-09-08T00-00-00Z-reviewer-to-author-verification-report.md"
)


class FakeGitResult:
    def __init__(self, returncode: int, stdout: bytes) -> None:
        self.returncode = returncode
        self.stdout = stdout


def tree(entries: dict[str, str | tuple[str, str, str]]) -> bytes:
    return b"\0".join(
        f"{value[0]} {value[1]} {value[2]}\t{path}".encode()
        if isinstance(value, tuple)
        else f"100644 blob {value}\t{path}".encode()
        for path, value in entries.items()
    ) + b"\0"


def event(path: str, body: str = "body") -> bytes:
    match = protocol_mailbox.EVENT_NAME_RE.fullmatch(Path(path).name)
    assert match is not None
    stamp = match.group("stamp")
    when = f"{stamp[:11]}{stamp[11:19].replace('-', ':')}Z"
    sender, recipient = match.group("sender"), match.group("recipient")
    return (
        f"# {sender.capitalize()} → {recipient.capitalize()}: test\n\n"
        f"**When:** {when} · **From:** {sender} (online)\n\n"
        f"{body}\n\nCursor at send: cursorless\n"
    ).encode()


def run_gate(
    monkeypatch,
    events: dict[str, bytes],
    at_cutover: dict[str, str | tuple[str, str, str]],
    at_head: dict[str, str | tuple[str, str, str]],
    validator=None,
    *,
    history=None,
    repo_root: Path = Path("."),
    boundary: bool = True,
    introductions_override=None,
):
    cutover = mailbox_admission.DESKTOP_WRITE_CUTOVER_COMMIT
    history = history or [(POST, at_head)]

    class Commits:
        object_types = (
            {cutover: "commit", **{commit: "commit" for commit, _ in history}}
            if boundary
            else {}
        )
        head = "HEAD"

        @staticmethod
        def is_ancestor(ancestor, descendant):
            return ancestor == cutover and descendant == "HEAD"

    class Projection:
        commits = Commits()
        frozen_legacy_reports = frozenset()
        review_family_cutover_events = {}
        kinds = frozenset({
            "decision", "findings", "learning-candidate", "status",
            "verification-report", "verify-request",
        })

    projection = Projection()
    introductions = {}
    for path in events:
        for commit, snapshot in history:
            if path in snapshot:
                value = snapshot[path]
                introductions[path] = (
                    commit, value[2] if isinstance(value, tuple) else value
                )
                break
    projection.introductions = introductions_override or introductions
    projection.introduction_events = dict(events)

    def run_git(_repo_root, *args):
        if args[0] == "rev-list":
            commits = "\n".join(commit for commit, _ in history) + "\n"
            return FakeGitResult(0, commits.encode())
        commit = args[3]
        snapshot = (
            at_head if commit == "HEAD" else
            at_cutover if commit == cutover else
            dict(history).get(commit, {})
        )
        return FakeGitResult(0, tree(snapshot))

    if validator is not None:
        monkeypatch.setattr(
            mailbox_review_admission, "validate_committed_new_event", validator
        )
    return mailbox_admission.check_post_cutover_event_admission(
        projection,
        coordination.CoordIssue,
        coordination._ARCHIVE_SENT_PREFIX,
        run_git,
        repo_root,
    )
