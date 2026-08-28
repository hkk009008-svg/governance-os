"""Read-only status coverage for the desktop-team transport."""

import os
import shutil
import sqlite3
import subprocess
from pathlib import Path
from types import SimpleNamespace

import pytest

import status
import status_team_store
import team


def _git(repo: Path, *args: str) -> str:
    return subprocess.run(
        ["git", *args],
        cwd=repo,
        capture_output=True,
        text=True,
        check=True,
    ).stdout.strip()


def _init_repo(tmp_path: Path) -> Path:
    repo = tmp_path / "repo"
    repo.mkdir()
    _git(repo, "init", "-b", "main")
    _git(repo, "config", "user.email", "status-test@example.com")
    _git(repo, "config", "user.name", "Status Test")
    (repo / "tracked.txt").write_text("tracked\n", encoding="utf-8")
    _git(repo, "add", "tracked.txt")
    _git(repo, "commit", "-m", "test: initial state")
    return repo


def _store(repo: Path) -> Path:
    common = Path(
        _git(repo, "rev-parse", "--path-format=absolute", "--git-common-dir")
    )
    return common / "pipeline-team" / "messages.sqlite3"


def test_status_does_not_create_an_absent_store(tmp_path: Path) -> None:
    repo = _init_repo(tmp_path)
    store = _store(repo)
    assert not store.parent.exists()

    observed = status.collect_team_transport(repo)

    assert observed["state"] == "absent"
    assert "did not create" in observed["detail"]
    assert not store.parent.exists()


def test_status_refuses_group_or_world_writable_git_common_directory(
    tmp_path: Path,
) -> None:
    repo = _init_repo(tmp_path)
    common = repo / ".git"
    common.chmod(common.stat().st_mode | 0o020)

    observed = status.collect_team_transport(repo)

    assert observed["state"] == "unavailable"
    assert "Git common directory is group/world writable" in observed["detail"]


def test_observation_does_not_touch_members_or_database(tmp_path: Path) -> None:
    repo = _init_repo(tmp_path)
    codex = team.Team(repo, "codex")
    claude = team.Team(repo, "claude")
    queued = codex.send(
        "claude", "Please inspect this range.", idempotency_key="status-review"
    )
    store = _store(repo)
    connection = sqlite3.connect(store)
    try:
        members_before = connection.execute(
            "SELECT name,instance_id,last_seen FROM members ORDER BY name"
        ).fetchall()
    finally:
        connection.close()
    files_before = {path.name: path.read_bytes() for path in store.parent.iterdir()}

    before_acknowledgement = status.collect_team_transport(repo)

    connection = sqlite3.connect(store)
    try:
        members_after = connection.execute(
            "SELECT name,instance_id,last_seen FROM members ORDER BY name"
        ).fetchall()
    finally:
        connection.close()
    assert {path.name: path.read_bytes() for path in store.parent.iterdir()} == files_before
    assert members_after == members_before
    assert before_acknowledgement["queued_messages"] == 1
    assert before_acknowledgement["acknowledgement_receipts"] == 0
    assert before_acknowledgement["reply_messages"] == 0
    assert before_acknowledgement["pending"]["claude"] == 1

    claude.wait(after_id=0)
    claude.wait(after_id=queued["id"])
    claude.send(
        "codex",
        "I read it.",
        reply_to=queued["id"],
        idempotency_key="status-review-reply",
    )
    after_reply = status.collect_team_transport(repo)
    assert after_reply["queued_messages"] == 2
    assert after_reply["acknowledgement_receipts"] == 1
    assert after_reply["reply_messages"] == 1
    assert after_reply["pending"]["codex"] == 1


def test_live_wal_is_read_without_touching_shared_files(tmp_path: Path) -> None:
    repo = _init_repo(tmp_path)
    team.Team(repo, "codex")
    store = _store(repo)
    writer = sqlite3.connect(store)
    try:
        writer.execute("PRAGMA journal_mode = WAL")
        writer.execute(
            "INSERT INTO messages("
            "idempotency_key,sender,recipient,body,created_at"
            ") VALUES(?,?,?,?,?)",
            ("live-wal", "codex", "claude", "live", "fixture"),
        )
        writer.commit()
        files_before = {path.name: path.read_bytes() for path in store.parent.iterdir()}

        observed = status.collect_team_transport(repo)

        assert observed["state"] == "ready"
        assert observed["queued_messages"] == 1
        assert observed["pending"]["claude"] == 1
        assert {path.name: path.read_bytes() for path in store.parent.iterdir()} == files_before
    finally:
        writer.close()


def test_checkpoint_between_main_and_wal_copy_retries_consistently(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    repo = _init_repo(tmp_path)
    team.Team(repo, "codex")
    store = _store(repo)
    writer = sqlite3.connect(store)
    try:
        writer.execute("PRAGMA journal_mode = WAL")
        writer.execute(
            "INSERT INTO messages("
            "idempotency_key,sender,recipient,body,created_at"
            ") VALUES(?,?,?,?,?)",
            ("raced-wal", "codex", "claude", "committed", "fixture"),
        )
        writer.commit()
        assert Path(f"{store}-wal").exists()

        real_copyfile = shutil.copyfile
        main_copies = 0

        def copy_with_checkpoint(source, destination, *args, **kwargs):
            nonlocal main_copies
            result = real_copyfile(source, destination, *args, **kwargs)
            if Path(source) == store:
                main_copies += 1
                if main_copies == 1:
                    checkpoint = sqlite3.connect(store)
                    try:
                        checkpoint.execute("PRAGMA wal_checkpoint(TRUNCATE)")
                    finally:
                        checkpoint.close()
                    writer.execute(
                        "INSERT INTO messages("
                        "idempotency_key,sender,recipient,body,created_at"
                        ") VALUES(?,?,?,?,?)",
                        ("new-wal", "agy", "claude", "new generation", "fixture"),
                    )
                    writer.commit()
            return result

        monkeypatch.setattr(status_team_store.shutil, "copyfile", copy_with_checkpoint)

        observed = status.collect_team_transport(repo)

        assert main_copies >= 2
        assert observed["state"] == "ready"
        assert observed["queued_messages"] == 2
        assert observed["pending"]["claude"] == 2
    finally:
        writer.close()


def test_malformed_store_is_unavailable_not_absent(tmp_path: Path) -> None:
    repo = _init_repo(tmp_path)
    store = _store(repo)
    store.parent.mkdir(mode=0o700)
    store.write_text("not sqlite", encoding="utf-8")
    store.chmod(0o600)

    observed = status.collect_team_transport(repo)

    assert observed["state"] == "unavailable"
    assert "unreadable" in observed["detail"]


def test_status_refuses_a_hard_linked_database(tmp_path: Path) -> None:
    repo = _init_repo(tmp_path)
    team.Team(repo, "codex")
    store = _store(repo)
    os.link(store, tmp_path / "second-name.sqlite3")

    observed = status.collect_team_transport(repo)

    assert observed["state"] == "unavailable"
    assert "one filesystem name" in observed["detail"]


def test_status_refuses_git_common_directory_owned_by_another_user(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    repo = _init_repo(tmp_path)
    team.Team(repo, "codex")
    different_uid = os.geteuid() + 1
    monkeypatch.setattr(
        status_team_store.os, "geteuid", lambda: different_uid
    )

    observed = status.collect_team_transport(repo)

    assert observed["state"] == "unavailable"
    assert (
        observed["detail"]
        == "Git common directory is not owned by the current user"
    )


@pytest.mark.parametrize("suffix", ("-wal", "-shm"))
@pytest.mark.parametrize("violation", ("group-readable", "hard-linked"))
def test_status_refuses_unsafe_sqlite_sidecars(
    tmp_path: Path, suffix: str, violation: str
) -> None:
    repo = _init_repo(tmp_path)
    team.Team(repo, "codex")
    sidecar = Path(f"{_store(repo)}{suffix}")
    sidecar.write_bytes(b"")
    sidecar.chmod(0o600)
    if violation == "group-readable":
        sidecar.chmod(0o640)
    else:
        os.link(sidecar, tmp_path / f"second-name{suffix}")

    observed = status.collect_team_transport(repo)

    assert observed["state"] == "unavailable"
    expected = (
        "group/world accessible"
        if violation == "group-readable"
        else "one filesystem name"
    )
    assert expected in observed["detail"]


@pytest.mark.parametrize("suffix", ("-wal", "-shm"))
def test_status_refuses_symlinked_sqlite_sidecars(
    tmp_path: Path, suffix: str,
) -> None:
    repo = _init_repo(tmp_path)
    team.Team(repo, "codex")
    sidecar = Path(f"{_store(repo)}{suffix}")
    target = tmp_path / f"target{suffix}"
    target.write_bytes(b"")
    sidecar.symlink_to(target)

    observed = status.collect_team_transport(repo)

    assert observed["state"] == "unavailable"
    assert "not one regular file" in observed["detail"]


@pytest.mark.parametrize("suffix", ("-wal", "-shm"))
def test_status_refuses_sqlite_sidecars_owned_by_another_user(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, suffix: str,
) -> None:
    repo = _init_repo(tmp_path)
    team.Team(repo, "codex")
    store = _store(repo)
    sidecar = Path(f"{store}{suffix}")
    sidecar.write_bytes(b"")
    sidecar.chmod(0o600)
    real_lstat = Path.lstat

    def lstat_with_foreign_sidecar(path: Path):
        observed = real_lstat(path)
        if path == sidecar:
            return SimpleNamespace(
                st_mode=observed.st_mode,
                st_uid=os.geteuid() + 1,
                st_nlink=observed.st_nlink,
            )
        return observed

    monkeypatch.setattr(Path, "lstat", lstat_with_foreign_sidecar)

    observed = status_team_store._secure_existing_store(store)

    assert observed == (
        f"team store {suffix[1:]} sidecar is not owned by the current user"
    )


def test_status_refuses_a_store_bound_to_another_repository(tmp_path: Path) -> None:
    repo = _init_repo(tmp_path)
    team.Team(repo, "codex")
    store = _store(repo)
    connection = sqlite3.connect(store)
    try:
        connection.execute(
            "UPDATE metadata SET value=? WHERE key='git_common_dir'",
            (str(tmp_path / "another-repository/.git"),),
        )
        connection.commit()
    finally:
        connection.close()

    observed = status.collect_team_transport(repo)

    assert observed["state"] == "unavailable"
    assert "repository identity is missing or mismatched" in observed["detail"]
