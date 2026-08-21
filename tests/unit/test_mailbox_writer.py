"""Focused tests for the fixed mailbox writer and shared writer fence."""

from __future__ import annotations

import os
import stat
import subprocess
import threading
import time
from pathlib import Path

import pytest

import mailbox_writer


# Hermetic fixture-git environment: the ambient VM configuration (commit
# signing via the exec-daemon shim, fsmonitor daemons) must not run inside
# throwaway test repositories; see tests/unit/test_check_coordination.py.
_GIT_ENV = {
    "PATH": "/usr/bin:/bin",
    "HOME": "/var/empty" if Path("/var/empty").is_dir() else "/nonexistent",
    "GIT_CONFIG_NOSYSTEM": "1",
    "GIT_CONFIG_COUNT": "1",
    "GIT_CONFIG_KEY_0": "init.defaultBranch",
    "GIT_CONFIG_VALUE_0": "main",
}


def _git(root: Path, *args: str, input_bytes: bytes | None = None) -> str:
    result = subprocess.run(
        ["/usr/bin/git", "-C", str(root), *args],
        input=input_bytes,
        capture_output=True,
        check=True,
        env=_GIT_ENV,
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


def _send_fixture(root: Path) -> tuple[Path, str, Path, bytes]:
    sent = root / "coordination/mailbox/sent"
    sent.mkdir(parents=True, exist_ok=True)
    (root / "coordination/mailbox/kinds.txt").write_text(
        "findings\n", encoding="utf-8"
    )
    relative = (
        "coordination/mailbox/sent/"
        "2026-07-17T01-02-03Z-author-to-reviewer-findings.md"
    )
    candidate = sent / ".2026-07-17T01-02-03Z-author-to-reviewer-findings.fixture.tmp"
    raw = (
        "# Author → Reviewer: snapshot\n\n"
        "**When:** 2026-07-17T01:02:03Z · **From:** author (online)\n\n"
        "body\n\nCursor at send: cursorless\n"
    ).encode("utf-8")
    candidate.write_bytes(raw)
    candidate.chmod(0o600)
    return sent, relative, candidate, raw


def _writer_temps(sent: Path) -> list[Path]:
    return [path for path in sent.iterdir() if path.name.startswith(".mailbox-writer-")]


def _index_bytes(root: Path, relative: str) -> bytes | None:
    result = subprocess.run(
        ["/usr/bin/git", "-C", str(root), "show", f":{relative}"],
        capture_output=True,
        check=False,
    )
    return result.stdout if result.returncode == 0 else None


def _put_index_bytes(root: Path, relative: str, raw: bytes) -> None:
    blob = subprocess.run(
        ["/usr/bin/git", "-C", str(root), "hash-object", "-w", "--stdin"],
        input=raw,
        capture_output=True,
        check=True,
    ).stdout.decode("ascii").strip()
    subprocess.run(
        [
            "/usr/bin/git",
            "-C",
            str(root),
            "update-index",
            "--add",
            "--cacheinfo",
            "100644",
            blob,
            relative,
        ],
        capture_output=True,
        check=True,
    )


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
    kinds.write_text("findings\n", encoding="utf-8")
    relative = (
        "coordination/mailbox/sent/"
        "2026-07-17T01-02-03Z-author-to-reviewer-findings.md"
    )
    candidate = sent / ".2026-07-17T01-02-03Z-author-to-reviewer-findings.fixture.tmp"
    candidate.write_text(
        "# Reviewer → Author: spoofed identity\n\n"
        "**When:** 2026-07-17T01:02:03Z · **From:** reviewer (online)\n\n"
        "body\n\nCursor at send: cursorless\n",
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
        "findings\n", encoding="utf-8"
    )
    relative = (
        "coordination/mailbox/sent/"
        "2026-07-17T01-02-03Z-author-to-reviewer-findings.md"
    )
    candidate = sent / ".2026-07-17T01-02-03Z-author-to-reviewer-findings.fixture.tmp"
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

    # The refusal moved earlier and got stricter: a retired seat cannot
    # publish ANY new event, so its malformed verify-request never reaches the
    # request parser. The property under test -- a non-review identity cannot
    # open a formal pair -- holds more broadly than before.
    with pytest.raises(
        mailbox_writer.MailboxWriterError, match="retired for new writes"
    ):
        mailbox_writer._send_event_finalize(root, candidate, relative)

    assert candidate.exists()
    assert not (root / relative).exists()


def test_send_event_finalizer_publishes_snapshot_not_retained_caller_inode(
    tmp_path: Path, monkeypatch
) -> None:
    root = _repo(tmp_path)
    sent, relative, candidate, raw = _send_fixture(root)
    alias = sent / "external-hardlink-alias"
    os.link(candidate, alias)
    retained_fd = os.open(candidate, os.O_RDWR)
    validate = mailbox_writer.validate_event_candidate_bytes

    def mutate_after_validation(root_arg: Path, raw_arg: bytes, relative_arg: str) -> None:
        validate(root_arg, raw_arg, relative_arg)
        os.lseek(retained_fd, 0, os.SEEK_SET)
        os.write(retained_fd, b"X" * len(raw))
        os.fsync(retained_fd)

    monkeypatch.setattr(
        mailbox_writer, "validate_event_candidate_bytes", mutate_after_validation
    )
    try:
        assert mailbox_writer._send_event_finalize(root, candidate, relative)
    finally:
        os.close(retained_fd)

    final = root / relative
    assert final.read_bytes() == raw
    assert alias.read_bytes() == b"X" * len(raw)
    assert final.stat().st_ino != alias.stat().st_ino
    assert not candidate.exists()
    assert stat.S_IMODE(final.stat().st_mode) == 0o600


def test_send_event_finalizer_keeps_replacement_at_candidate_path(
    tmp_path: Path, monkeypatch
) -> None:
    root = _repo(tmp_path)
    _sent, relative, candidate, raw = _send_fixture(root)
    replacement = b"caller replacement must survive\n"
    validate = mailbox_writer.validate_event_candidate_bytes

    def swap_after_validation(root_arg: Path, raw_arg: bytes, relative_arg: str) -> None:
        validate(root_arg, raw_arg, relative_arg)
        candidate.unlink()
        candidate.write_bytes(replacement)
        candidate.chmod(0o600)

    monkeypatch.setattr(
        mailbox_writer, "validate_event_candidate_bytes", swap_after_validation
    )

    assert mailbox_writer._send_event_finalize(root, candidate, relative)

    assert (root / relative).read_bytes() == raw
    assert candidate.read_bytes() == replacement


@pytest.mark.parametrize("kind", ("symlink", "directory"))
def test_send_event_finalizer_rejects_symlink_and_nonregular_candidate(
    tmp_path: Path, kind: str
) -> None:
    root = _repo(tmp_path)
    sent, relative, candidate, raw = _send_fixture(root)
    candidate.unlink()
    if kind == "symlink":
        outside = root / "outside-candidate"
        outside.write_bytes(raw)
        outside.chmod(0o600)
        candidate.symlink_to(outside)
    else:
        candidate.mkdir(mode=0o600)

    with pytest.raises(mailbox_writer.MailboxWriterError, match="candidate"):
        mailbox_writer._send_event_finalize(root, candidate, relative)

    assert not (root / relative).exists()


def test_send_event_finalizer_write_all_handles_partial_writes(
    tmp_path: Path, monkeypatch
) -> None:
    root = _repo(tmp_path)
    _sent, relative, candidate, raw = _send_fixture(root)
    real_write = os.write
    calls = 0

    def partial_write(fd: int, data: bytes) -> int:
        nonlocal calls
        calls += 1
        return real_write(fd, data[:7])

    monkeypatch.setattr(mailbox_writer.os, "write", partial_write)

    assert mailbox_writer._send_event_finalize(root, candidate, relative)
    assert calls > 1
    assert (root / relative).read_bytes() == raw


def test_send_event_finalizer_rolls_back_partial_write_failure(
    tmp_path: Path, monkeypatch
) -> None:
    root = _repo(tmp_path)
    sent, relative, candidate, _raw = _send_fixture(root)
    real_write = os.write
    calls = 0

    def fail_after_partial(fd: int, data: bytes) -> int:
        nonlocal calls
        calls += 1
        if calls == 1:
            return real_write(fd, data[:5])
        raise OSError("injected write failure")

    monkeypatch.setattr(mailbox_writer.os, "write", fail_after_partial)

    with pytest.raises(mailbox_writer.MailboxWriterError, match="public"):
        mailbox_writer._send_event_finalize(root, candidate, relative)

    assert candidate.exists()
    assert not (root / relative).exists()
    assert _writer_temps(sent) == []


@pytest.mark.parametrize("failure_point", ("file", "directory"))
def test_send_event_finalizer_rolls_back_fsync_failure(
    tmp_path: Path, monkeypatch, failure_point: str
) -> None:
    root = _repo(tmp_path)
    sent, relative, candidate, _raw = _send_fixture(root)
    real_fsync = os.fsync

    def fail_selected(fd: int) -> None:
        mode = os.fstat(fd).st_mode
        if failure_point == "file" and stat.S_ISREG(mode):
            raise OSError("injected file fsync failure")
        if failure_point == "directory" and stat.S_ISDIR(mode):
            raise OSError("injected directory fsync failure")
        real_fsync(fd)

    monkeypatch.setattr(mailbox_writer.os, "fsync", fail_selected)

    with pytest.raises(mailbox_writer.MailboxWriterError, match="public"):
        mailbox_writer._send_event_finalize(root, candidate, relative)

    assert candidate.exists()
    assert not (root / relative).exists()
    assert _writer_temps(sent) == []


@pytest.mark.parametrize("failure", ("error", "exists"))
def test_send_event_finalizer_rolls_back_link_failure_without_clobber(
    tmp_path: Path, monkeypatch, failure: str
) -> None:
    root = _repo(tmp_path)
    sent, relative, candidate, _raw = _send_fixture(root)
    final = root / relative
    if failure == "exists":
        final.write_bytes(b"pre-existing final\n")
        expected = final.read_bytes()
    else:
        expected = None
        monkeypatch.setattr(
            mailbox_writer.os,
            "link",
            lambda *args, **kwargs: (_ for _ in ()).throw(
                OSError("injected link failure")
            ),
        )

    with pytest.raises(mailbox_writer.MailboxWriterError, match="public"):
        mailbox_writer._send_event_finalize(root, candidate, relative)

    assert candidate.exists()
    assert (final.read_bytes() if final.exists() else None) == expected
    assert _writer_temps(sent) == []


def test_send_event_main_reports_exact_final_bytes_and_unstaged_contract(
    tmp_path: Path, monkeypatch, capsys
) -> None:
    root = _repo(tmp_path)
    _sent, relative, candidate, raw = _send_fixture(root)
    monkeypatch.setattr(
        mailbox_writer,
        "_stage_event_snapshot",
        lambda *args, **kwargs: (_ for _ in ()).throw(
            mailbox_writer.MailboxWriterError("injected git add failure")
        ),
    )

    rc = mailbox_writer.main(
        [
            "send-event-finalize",
            "--repo-root",
            str(root),
            "--candidate",
            str(candidate),
            "--final-relative",
            relative,
        ]
    )

    assert rc == 0
    assert capsys.readouterr().out == f"unstaged:{relative}\n"
    assert (root / relative).read_bytes() == raw
    assert not candidate.exists()


def test_send_event_finalizer_rejects_final_path_swap_before_staging(
    tmp_path: Path, monkeypatch
) -> None:
    root = _repo(tmp_path)
    sent, relative, candidate, _raw = _send_fixture(root)
    final = root / relative
    replacement = b"unowned replacement must survive\n"
    real_fsync = os.fsync
    injected = False

    def swap_at_directory_fsync(fd: int) -> None:
        nonlocal injected
        real_fsync(fd)
        if stat.S_ISDIR(os.fstat(fd).st_mode) and not injected:
            injected = True
            final.unlink()
            final.write_bytes(replacement)
            final.chmod(0o600)

    monkeypatch.setattr(mailbox_writer.os, "fsync", swap_at_directory_fsync)

    with pytest.raises(mailbox_writer.MailboxWriterError, match="final.*changed"):
        mailbox_writer._send_event_finalize(root, candidate, relative)

    assert final.read_bytes() == replacement
    assert candidate.exists()
    assert _index_bytes(root, relative) is None
    assert _writer_temps(sent) == []


def test_send_event_finalizer_stages_snapshot_then_rejects_final_alias_mutation(
    tmp_path: Path, monkeypatch
) -> None:
    root = _repo(tmp_path)
    sent, relative, candidate, raw = _send_fixture(root)
    final = root / relative
    alias = sent / "writer-inode-alias"
    corrupted = b"Y" * len(raw)
    staged_observations: list[bytes | None] = []
    real_fsync = os.fsync
    injected = False

    def mutate_at_directory_fsync(fd: int) -> None:
        nonlocal injected
        real_fsync(fd)
        if stat.S_ISDIR(os.fstat(fd).st_mode) and not injected:
            injected = True
            os.link(final, alias)
            alias.write_bytes(corrupted)

    stage_snapshot = mailbox_writer._stage_event_snapshot

    def observe_stage(root_arg: Path, relative_arg: str, raw_arg: bytes) -> None:
        stage_snapshot(root_arg, relative_arg, raw_arg)
        staged_observations.append(_index_bytes(root_arg, relative_arg))

    monkeypatch.setattr(mailbox_writer.os, "fsync", mutate_at_directory_fsync)
    monkeypatch.setattr(mailbox_writer, "_stage_event_snapshot", observe_stage)

    with pytest.raises(mailbox_writer.MailboxWriterError, match="final.*changed"):
        mailbox_writer._send_event_finalize(root, candidate, relative)

    assert staged_observations == [raw]
    assert alias.read_bytes() == corrupted
    assert not final.exists()
    assert candidate.exists()
    assert _index_bytes(root, relative) is None
    assert _writer_temps(sent) == []


def test_send_event_finalizer_rejects_final_mode_change_after_publication(
    tmp_path: Path, monkeypatch
) -> None:
    root = _repo(tmp_path)
    sent, relative, candidate, _raw = _send_fixture(root)
    final = root / relative
    real_fsync = os.fsync
    injected = False

    def chmod_at_directory_fsync(fd: int) -> None:
        nonlocal injected
        real_fsync(fd)
        if stat.S_ISDIR(os.fstat(fd).st_mode) and not injected:
            injected = True
            final.chmod(0o644)

    monkeypatch.setattr(mailbox_writer.os, "fsync", chmod_at_directory_fsync)

    with pytest.raises(mailbox_writer.MailboxWriterError, match="final mode changed"):
        mailbox_writer._send_event_finalize(root, candidate, relative)

    assert not final.exists()
    assert candidate.exists()
    assert _index_bytes(root, relative) is None
    assert _writer_temps(sent) == []


def test_send_event_finalizer_reports_nonvalidated_index_when_real_lock_blocks_rollback(
    tmp_path: Path, monkeypatch
) -> None:
    root = _repo(tmp_path)
    sent, relative, candidate, raw = _send_fixture(root)
    corrupt = b"corrupt staged bytes\n"
    lock = root / ".git/index.lock"

    def stage_corrupt_then_lock(
        root_arg: Path, relative_arg: str, _raw_arg: bytes
    ) -> None:
        _put_index_bytes(root_arg, relative_arg, corrupt)
        lock.write_text("real lock\n", encoding="utf-8")

    monkeypatch.setattr(
        mailbox_writer, "_stage_event_snapshot", stage_corrupt_then_lock
    )

    try:
        with pytest.raises(
            mailbox_writer.MailboxWriterError,
            match=(
                "current index state and bytes unconfirmed.*"
                "last observed: nonvalidated bytes"
            ),
        ):
            mailbox_writer._send_event_finalize(root, candidate, relative)
    finally:
        lock.unlink(missing_ok=True)

    assert _index_bytes(root, relative) == corrupt
    assert _index_bytes(root, relative) != raw
    assert not (root / relative).exists()
    assert candidate.exists()
    assert _writer_temps(sent) == []


def test_send_event_finalizer_reports_index_unconfirmed_after_observed_stage_changes(
    tmp_path: Path, monkeypatch
) -> None:
    root = _repo(tmp_path)
    sent, relative, candidate, raw = _send_fixture(root)
    corrupt = b"corrupt staged bytes after observation\n"
    lock = root / ".git/index.lock"
    real_staged_snapshot = mailbox_writer._staged_event_snapshot

    def observe_then_replace_index(root_arg: Path, relative_arg: str) -> bytes:
        observed = real_staged_snapshot(root_arg, relative_arg)
        assert observed == raw
        _put_index_bytes(root_arg, relative_arg, corrupt)
        lock.write_text("real lock\n", encoding="utf-8")
        (root_arg / relative_arg).chmod(0o644)
        return observed

    monkeypatch.setattr(
        mailbox_writer, "_staged_event_snapshot", observe_then_replace_index
    )

    try:
        with pytest.raises(
            mailbox_writer.MailboxWriterError,
            match=(
                "current index state and bytes unconfirmed.*"
                "last observed: validated snapshot"
            ),
        ):
            mailbox_writer._send_event_finalize(root, candidate, relative)
    finally:
        lock.unlink(missing_ok=True)

    assert _index_bytes(root, relative) == corrupt
    assert not (root / relative).exists()
    assert candidate.exists()
    assert _writer_temps(sent) == []


def test_send_event_finalizer_reports_retained_state_on_writer_temp_cleanup_failure(
    tmp_path: Path, monkeypatch
) -> None:
    root = _repo(tmp_path)
    sent, relative, candidate, raw = _send_fixture(root)
    real_unlink = os.unlink

    def fail_writer_temp(name, *args, **kwargs):
        if str(name).startswith(".mailbox-writer-"):
            raise OSError("injected writer temp cleanup failure")
        return real_unlink(name, *args, **kwargs)

    monkeypatch.setattr(mailbox_writer.os, "unlink", fail_writer_temp)

    with pytest.raises(
        mailbox_writer.MailboxWriterError,
        match="final retained.*index staged.*candidate retained.*writer temp retained",
    ):
        mailbox_writer._send_event_finalize(root, candidate, relative)

    assert (root / relative).read_bytes() == raw
    assert _index_bytes(root, relative) == raw
    assert candidate.exists()
    assert len(_writer_temps(sent)) == 1


def test_send_event_finalizer_reports_incomplete_rollback_after_directory_fsync_failure(
    tmp_path: Path, monkeypatch
) -> None:
    root = _repo(tmp_path)
    sent, relative, candidate, raw = _send_fixture(root)
    final = root / relative
    real_fsync = os.fsync
    real_unlink = os.unlink

    def fail_directory_fsync(fd: int) -> None:
        if stat.S_ISDIR(os.fstat(fd).st_mode):
            raise OSError("injected directory fsync failure")
        real_fsync(fd)

    def fail_final_rollback(name, *args, **kwargs):
        if str(name) == final.name:
            raise OSError("injected final rollback failure")
        return real_unlink(name, *args, **kwargs)

    monkeypatch.setattr(mailbox_writer.os, "fsync", fail_directory_fsync)
    monkeypatch.setattr(mailbox_writer.os, "unlink", fail_final_rollback)

    with pytest.raises(
        mailbox_writer.MailboxWriterError,
        match="publication failed.*final retained.*durability unconfirmed.*candidate retained",
    ):
        mailbox_writer._send_event_finalize(root, candidate, relative)

    assert final.read_bytes() == raw
    assert candidate.exists()
    assert _index_bytes(root, relative) is None
    assert _writer_temps(sent) == []


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


def _consume_fixture(root: Path) -> Path:
    sent = root / "coordination/mailbox/sent"
    seen = root / "coordination/mailbox/seen"
    sent.mkdir(parents=True)
    seen.mkdir()
    cursor = seen / "director.txt"
    cursor.write_text("2026-07-17T00:00:00Z\n", encoding="ascii")
    (sent / "2026-07-17T01-02-03Z-operator-to-director-status.md").write_text(
        "fixture\n", encoding="utf-8"
    )
    return cursor


def test_consume_directory_pin_failure_leaves_cursor_unadvanced(
    tmp_path: Path, monkeypatch
) -> None:
    # The seen/ directory handle is pinned before os.replace advances the
    # cursor. If that pin fails after the advance instead, the cursor is
    # left half-advanced on disk with nothing staged and no rollback.
    root = _repo(tmp_path)
    cursor = _consume_fixture(root)
    seen = cursor.parent
    real_open = os.open

    def fail_directory_open(path, flags, *args, **kwargs):
        if flags & getattr(os, "O_DIRECTORY", 0) and Path(path) == seen:
            raise OSError("injected directory pin failure")
        return real_open(path, flags, *args, **kwargs)

    monkeypatch.setattr(mailbox_writer.os, "open", fail_directory_open)

    with pytest.raises(OSError, match="injected directory pin failure"):
        mailbox_writer._consume_events_finalize(root, "director", None)

    assert cursor.read_text(encoding="ascii") == "2026-07-17T00:00:00Z\n"
    assert list(seen.glob(".director.*")) == []
    assert _git(root, "diff", "--cached", "--name-only") == ""


def test_consume_stage_failure_rolls_back_cursor_bytes(
    tmp_path: Path, monkeypatch
) -> None:
    root = _repo(tmp_path)
    cursor = _consume_fixture(root)

    def fail_stage(*args, **kwargs):
        raise OSError("injected stage failure")

    monkeypatch.setattr(mailbox_writer, "_stage", fail_stage)

    with pytest.raises(OSError, match="injected stage failure"):
        mailbox_writer._consume_events_finalize(root, "director", None)

    assert cursor.read_text(encoding="ascii") == "2026-07-17T00:00:00Z\n"
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
