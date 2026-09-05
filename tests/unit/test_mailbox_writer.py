from __future__ import annotations

import os
from pathlib import Path

import pytest

import mailbox_writer
from formal_review_support import commit, event, git, init_repo, report_body, request_body


class _FixedDateTime:
    @classmethod
    def now(cls, _timezone):
        from datetime import datetime

        return datetime.fromisoformat("2026-09-02T10:00:00+00:00")


def test_writer_publishes_and_stages_exact_request(tmp_path, monkeypatch) -> None:
    root = tmp_path / "repo"
    base = init_repo(root)
    head = commit(root, {"pipeline/control.py": "enabled = True\n"}, "candidate")
    monkeypatch.setattr(mailbox_writer, "datetime", _FixedDateTime)
    path = mailbox_writer.publish(
        root,
        sender="codex",
        recipient="claude",
        kind="verify-request",
        subject="review control",
        body=request_body(base, head),
    )
    assert git(root, "diff", "--cached", "--name-only") == path
    assert (root / path).read_bytes() == mailbox_writer._git(root, "show", f":{path}")
    assert os.stat(root / path).st_mode & 0o777 == 0o600


def test_writer_never_overwrites_existing_path(tmp_path, monkeypatch) -> None:
    root = tmp_path / "repo"
    base = init_repo(root)
    head = commit(root, {"pipeline/control.py": "enabled = True\n"}, "candidate")
    monkeypatch.setattr(mailbox_writer, "datetime", _FixedDateTime)
    arguments = dict(
        sender="codex",
        recipient="claude",
        kind="verify-request",
        subject="review",
        body=request_body(base, head),
    )
    path = mailbox_writer.publish(root, **arguments)
    original = (root / path).read_bytes()
    with pytest.raises(mailbox_writer.MailboxWriterError, match="already exists"):
        mailbox_writer.publish(root, **arguments)
    assert (root / path).read_bytes() == original


@pytest.mark.parametrize("kind", ["findings", "decision", "status"])
def test_writer_accepts_only_formal_artifacts(kind: str) -> None:
    assert mailbox_writer.new_write_envelope_problem(kind, "codex", "claude")


def test_agy_cannot_publish_a_verdict() -> None:
    problem = mailbox_writer.new_write_envelope_problem(
        "verification-report", "agy", "codex"
    )
    assert problem == "verification-report publisher must be codex or claude"


def test_envelope_validation_binds_filename_sender(tmp_path) -> None:
    root = tmp_path / "repo"
    init_repo(root)
    path, text = event(
        "2026-09-02T10-00-00Z", "codex", "claude", "verify-request", "body"
    )
    with pytest.raises(mailbox_writer.MailboxWriterError, match="envelope"):
        mailbox_writer.validate_event_envelope_bytes(
            root, text.replace("From:** codex", "From:** agy").encode(), path
        )


@pytest.mark.parametrize("author,author_model,reviewer,reviewer_model", (
    ("codex", "gpt-5.6-sol", "claude", "claude-sonnet-5"),
    ("claude", "claude-sonnet-5", "codex", "gpt-5.6-sol"),
))
def test_report_publication_reproduces_request_binding(
    tmp_path, monkeypatch, author, author_model, reviewer, reviewer_model,
) -> None:
    root = tmp_path / "repo"
    base = init_repo(root)
    head = commit(root, {"pipeline/control.py": "enabled = True\n"}, "candidate")
    request_path, request_text = event(
        "2026-09-02T09-59-00Z",
        author,
        reviewer,
        "verify-request",
        request_body(base, head, author_model=author_model),
    )
    request_commit = commit(root, {request_path: request_text}, "request")
    monkeypatch.setattr(mailbox_writer, "datetime", _FixedDateTime)
    report_path = mailbox_writer.publish(
        root,
        sender=reviewer,
        recipient=author,
        kind="verification-report",
        subject="GO",
        body=report_body(request_path, request_commit, reviewer_model=reviewer_model),
    )
    assert report_path.endswith(f"{reviewer}-to-{author}-verification-report.md")


def test_invalid_report_leaves_no_artifact(tmp_path, monkeypatch) -> None:
    root = tmp_path / "repo"
    init_repo(root)
    monkeypatch.setattr(mailbox_writer, "datetime", _FixedDateTime)
    with pytest.raises(mailbox_writer.MailboxWriterError):
        mailbox_writer.publish(
            root,
            sender="claude",
            recipient="codex",
            kind="verification-report",
            subject="invalid",
            body="Event type: verification-report",
        )
    assert list((root / "coordination/mailbox/sent").glob("*verification-report.md")) == []


def test_git_stage_failure_removes_the_created_artifact(tmp_path, monkeypatch) -> None:
    root = tmp_path / "repo"
    base = init_repo(root)
    head = commit(root, {"pipeline/control.py": "enabled = True\n"}, "candidate")
    original_git = mailbox_writer._git

    def fail_stage(repo, *arguments, **kwargs):
        if arguments and arguments[0] == "update-index":
            raise mailbox_writer.MailboxWriterError("injected stage failure")
        return original_git(repo, *arguments, **kwargs)

    monkeypatch.setattr(mailbox_writer, "datetime", _FixedDateTime)
    monkeypatch.setattr(mailbox_writer, "_git", fail_stage)
    with pytest.raises(mailbox_writer.MailboxWriterError, match="injected"):
        mailbox_writer.publish(
            root,
            sender="codex",
            recipient="claude",
            kind="verify-request",
            subject="review control",
            body=request_body(base, head),
        )
    assert list((root / "coordination/mailbox/sent").glob("*verify-request.md")) == []


def test_envelope_validation_accepts_plain_and_online(tmp_path) -> None:
    root = tmp_path / "repo"
    init_repo(root)
    path, text = event(
        "2026-09-02T10-00-00Z", "codex", "claude", "verify-request", "body"
    )
    # Baseline with (online) and Cursor at send: cursorless
    mailbox_writer.validate_event_envelope_bytes(root, text.encode(), path)

    # Without (online)
    text_no_online = text.replace(" (online)", "")
    mailbox_writer.validate_event_envelope_bytes(root, text_no_online.encode(), path)

    # Without Cursor at send: cursorless
    text_no_cursor = text_no_online.replace("\n\nCursor at send: cursorless\n", "\n")
    mailbox_writer.validate_event_envelope_bytes(root, text_no_cursor.encode(), path)

    # With duplicate cursor lines fails
    text_dup_cursor = text + "Cursor at send: cursorless\n"
    with pytest.raises(mailbox_writer.MailboxWriterError, match="duplicate cursor declaration"):
        mailbox_writer.validate_event_envelope_bytes(root, text_dup_cursor.encode(), path)

    # With non-cursorless cursor line fails
    text_bad_cursor = text_no_cursor + "\nCursor at send: invalid-cursor\n"
    with pytest.raises(mailbox_writer.MailboxWriterError, match="cursor must be cursorless"):
        mailbox_writer.validate_event_envelope_bytes(root, text_bad_cursor.encode(), path)
