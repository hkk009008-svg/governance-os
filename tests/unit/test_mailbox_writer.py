"""Focused tests for the fixed mailbox writer and shared writer fence."""

from __future__ import annotations

import stat
import subprocess
import threading
import time
from pathlib import Path

import pytest

import mailbox_writer


def _git(root: Path, *args: str, input_bytes: bytes | None = None) -> str:
    result = subprocess.run(
        ["/usr/bin/git", "-C", str(root), *args],
        input=input_bytes,
        capture_output=True,
        check=True,
    )
    return result.stdout.decode("ascii").strip()


def _repo(tmp_path: Path) -> Path:
    root = tmp_path / "repo"
    root.mkdir()
    _git(root, "init", "-q")
    (root / "README.md").write_text("fixture\n", encoding="utf-8")
    _git(root, "add", "README.md")
    _git(
        root,
        "-c",
        "user.name=Fixture",
        "-c",
        "user.email=fixture@example.invalid",
        "commit",
        "-q",
        "-m",
        "chore: seed mailbox fixture",
    )
    return root


def test_writer_fence_is_shared_by_linked_worktrees_and_mode_0600(
    tmp_path: Path,
) -> None:
    root = _repo(tmp_path)
    linked = tmp_path / "linked"
    _git(root, "worktree", "add", "-q", "-b", "linked", str(linked))
    acquired = threading.Event()

    def contender() -> None:
        with mailbox_writer.writer_fence(linked):
            acquired.set()

    with mailbox_writer.writer_fence(root):
        common = Path(_git(root, "rev-parse", "--path-format=absolute", "--git-common-dir"))
        lock = common / "protocol-kernel-writer.lock"
        assert stat.S_IMODE(lock.stat().st_mode) == 0o600
        thread = threading.Thread(target=contender)
        thread.start()
        time.sleep(0.1)
        assert not acquired.is_set()
    thread.join(timeout=2)
    assert acquired.is_set()


def test_send_event_finalizer_rejects_filename_envelope_identity_mismatch(
    tmp_path: Path,
) -> None:
    root = _repo(tmp_path)
    sent = root / "coordination/mailbox/sent"
    sent.mkdir(parents=True)
    kinds = root / "coordination/mailbox/kinds.txt"
    kinds.write_text("status\n", encoding="utf-8")
    relative = (
        "coordination/mailbox/sent/"
        "2026-07-17T01-02-03Z-director-to-operator-status.md"
    )
    candidate = sent / ".2026-07-17T01-02-03Z-director-to-operator-status.fixture.tmp"
    candidate.write_text(
        "# Operator → Director: spoofed identity\n\n"
        "**When:** 2026-07-17T01:02:03Z · **From:** operator (online)\n\n"
        "body\n\nCursor at send: 0\n",
        encoding="utf-8",
    )
    candidate.chmod(0o600)

    with pytest.raises(mailbox_writer.MailboxWriterError, match="envelope"):
        mailbox_writer._send_event_finalize(root, candidate, relative)

    assert candidate.exists()
    assert not (root / relative).exists()
    assert _git(root, "diff", "--cached", "--name-only") == ""


@pytest.mark.parametrize(
    "duplicate",
    (
        "# Director → Operator: repeated\n",
        "**When:** 2026-07-17T01:02:03Z · **From:** director (online)\n",
        "Cursor at send: 0\n",
    ),
)
def test_send_event_finalizer_rejects_duplicate_envelope_or_footer(
    tmp_path: Path, duplicate: str
) -> None:
    root = _repo(tmp_path)
    sent = root / "coordination/mailbox/sent"
    sent.mkdir(parents=True)
    (root / "coordination/mailbox/kinds.txt").write_text(
        "status\n", encoding="utf-8"
    )
    relative = (
        "coordination/mailbox/sent/"
        "2026-07-17T01-02-03Z-director-to-operator-status.md"
    )
    candidate = sent / ".2026-07-17T01-02-03Z-director-to-operator-status.fixture.tmp"
    candidate.write_text(
        "# Director → Operator: repeated\n\n"
        "**When:** 2026-07-17T01:02:03Z · **From:** director (online)\n\n"
        f"{duplicate}\n"
        "body\n\n"
        "Cursor at send: 0\n",
        encoding="utf-8",
    )
    candidate.chmod(0o600)

    with pytest.raises(mailbox_writer.MailboxWriterError, match="duplicate"):
        mailbox_writer._send_event_finalize(root, candidate, relative)

    assert candidate.exists()
    assert not (root / relative).exists()
    assert _git(root, "diff", "--cached", "--name-only") == ""


def test_send_event_finalizer_rejects_coordinator_verify_request(
    tmp_path: Path,
) -> None:
    root = _repo(tmp_path)
    sent = root / "coordination/mailbox/sent"
    sent.mkdir(parents=True)
    (root / "coordination/mailbox/kinds.txt").write_text(
        "verify-request\n", encoding="utf-8"
    )
    relative = (
        "coordination/mailbox/sent/"
        "2026-07-17T01-02-03Z-coordinator-to-operator-verify-request.md"
    )
    candidate = sent / (
        ".2026-07-17T01-02-03Z-coordinator-to-operator-verify-request.fixture.tmp"
    )
    sha = _git(root, "rev-parse", "HEAD")
    candidate.write_text(
        "# Coordinator → Operator: invalid author\n\n"
        "**When:** 2026-07-17T01:02:03Z · **From:** coordinator (online)\n\n"
        "Event type: verify-request\n"
        f"Reviewed head: {sha}\n"
        f"Reviewed base: {sha}\n"
        "Author seat: coordinator\n"
        "Author model: fixture\n"
        "Assigned operator: operator\n\n"
        "## Outcome\n\n"
        "Review this range.\n\n"
        "Cursor at send: cursorless\n",
        encoding="utf-8",
    )
    candidate.chmod(0o600)

    with pytest.raises(mailbox_writer.MailboxWriterError, match="verify-request"):
        mailbox_writer._send_event_finalize(root, candidate, relative)

    assert candidate.exists()
    assert not (root / relative).exists()


def test_consume_scalar_cursor_falls_back_to_mailbox_and_converts_to_iso(
    tmp_path: Path,
) -> None:
    root = _repo(tmp_path)
    sent = root / "coordination/mailbox/sent"
    seen = root / "coordination/mailbox/seen"
    sent.mkdir(parents=True)
    seen.mkdir()
    cursor = seen / "director.txt"
    cursor.write_text("0\n", encoding="ascii")
    event = "2026-07-17T01-02-03Z-operator-to-director-status.md"
    (sent / event).write_text("fixture\n", encoding="utf-8")

    output = mailbox_writer._consume_events_finalize(root, "director", None)

    assert "mailbox fallback" in output
    assert cursor.read_text(encoding="ascii") == "2026-07-17T01:02:03Z\n"
    assert _git(root, "diff", "--cached", "--name-only") == (
        "coordination/mailbox/seen/director.txt"
    )


def test_consume_scalar_cursor_rejects_position_beyond_mailbox_corpus(
    tmp_path: Path,
) -> None:
    root = _repo(tmp_path)
    sent = root / "coordination/mailbox/sent"
    seen = root / "coordination/mailbox/seen"
    sent.mkdir(parents=True)
    seen.mkdir()
    cursor = seen / "director.txt"
    cursor.write_text("2\n", encoding="ascii")
    (sent / "2026-07-17T01-02-03Z-operator-to-director-status.md").write_text(
        "fixture\n", encoding="utf-8"
    )

    with pytest.raises(mailbox_writer.MailboxWriterError, match="beyond mailbox"):
        mailbox_writer._consume_events_finalize(root, "director", None)

    assert cursor.read_text(encoding="ascii") == "2\n"
    assert _git(root, "diff", "--cached", "--name-only") == ""


def test_consume_rejects_coordinator_before_cursor_access(tmp_path: Path) -> None:
    root = _repo(tmp_path)

    with pytest.raises(mailbox_writer.MailboxWriterError, match="role is invalid"):
        mailbox_writer._consume_events_finalize(root, "coordinator", None)


@pytest.mark.parametrize(
    ("current", "target"),
    [
        ("not-a-time", None),
        ("2026-99-99T99:99:99Z", None),
        ("2026-07-17T01:00:00Z", "2026-07-17T01:02-03Z"),
        ("2026-07-17T01:00:00Z", "2026-99-99T99:99:99Z"),
    ],
)
def test_consume_finalizer_rejects_malformed_or_mixed_cursor_formats_before_mutation(
    tmp_path: Path, current: str, target: str | None
) -> None:
    root = _repo(tmp_path)
    sent = root / "coordination/mailbox/sent"
    seen = root / "coordination/mailbox/seen"
    sent.mkdir(parents=True)
    seen.mkdir()
    cursor = seen / "director.txt"
    cursor.write_text(current + "\n", encoding="ascii")
    (sent / "2026-07-17T01-02-03Z-operator-to-director-status.md").write_text(
        "fixture\n", encoding="utf-8"
    )

    with pytest.raises(mailbox_writer.MailboxWriterError):
        mailbox_writer._consume_events_finalize(root, "director", target)

    assert cursor.read_text(encoding="ascii") == current + "\n"
    assert _git(root, "diff", "--cached", "--name-only") == ""
