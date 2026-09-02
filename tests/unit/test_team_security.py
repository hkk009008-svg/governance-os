"""Negative controls for repository and filesystem confinement."""
from __future__ import annotations

import os
import sqlite3
from pathlib import Path
from types import SimpleNamespace

import pytest

import team
import team_store
from team_test_support import make_repo


def test_store_directory_symlink_is_refused(tmp_path: Path) -> None:
    repo = make_repo(tmp_path / "repo")
    outside = tmp_path / "outside"
    outside.mkdir()
    (repo / ".git" / "pipeline-team").symlink_to(outside, target_is_directory=True)

    with pytest.raises(team.TeamError, match="real directory"):
        team.Team(repo, "codex")
    assert list(outside.iterdir()) == []


def test_store_file_symlink_is_refused(tmp_path: Path) -> None:
    repo = make_repo(tmp_path / "repo")
    directory = repo / ".git" / "pipeline-team"
    directory.mkdir(mode=0o700)
    outside = tmp_path / "outside.sqlite3"
    outside.write_bytes(b"unchanged")
    (directory / "messages.sqlite3").symlink_to(outside)

    with pytest.raises(team.TeamError, match="regular file"):
        team.Team(repo, "codex")
    assert outside.read_bytes() == b"unchanged"


def test_store_file_hardlink_is_refused(tmp_path: Path) -> None:
    repo = make_repo(tmp_path / "repo")
    directory = repo / ".git" / "pipeline-team"
    directory.mkdir(mode=0o700)
    outside = tmp_path / "outside.sqlite3"
    outside.write_bytes(b"")
    os.chmod(outside, 0o600)
    os.link(outside, directory / "messages.sqlite3")

    with pytest.raises(team.TeamError, match="one filesystem name"):
        team.Team(repo, "codex")
    assert outside.read_bytes() == b""


def test_store_path_is_revalidated_before_every_open(tmp_path: Path) -> None:
    repo = make_repo(tmp_path / "repo")
    member = team.Team(repo, "codex")
    store = member.store_path
    outside = tmp_path / "outside.sqlite3"
    store.replace(outside)
    store.symlink_to(outside)

    with pytest.raises(team.TeamError, match="regular file"):
        member.send("claude", "must not escape", idempotency_key="escape")


def test_unlinked_sidecar_snapshot_is_a_safe_close_race(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    repo = make_repo(tmp_path / "repo")
    member = team.Team(repo, "codex")
    sidecar = Path(f"{member.store_path}-shm")
    sidecar.write_bytes(b"")
    sidecar.chmod(0o600)
    real_lstat = Path.lstat

    def lstat_during_unlink(path: Path):
        observed = real_lstat(path)
        if path == sidecar:
            return SimpleNamespace(
                st_mode=observed.st_mode,
                st_uid=observed.st_uid,
                st_nlink=0,
            )
        return observed

    monkeypatch.setattr(Path, "lstat", lstat_during_unlink)

    assert team_store._validate_store_path(member.common_dir, member.store_path)


def test_failed_post_open_validation_closes_connection(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    member = team.Team(make_repo(tmp_path / "repo"), "codex")
    calls = 0

    def fail_after_open(_common: Path, _store: Path) -> tuple[int, int]:
        nonlocal calls
        calls += 1
        if calls == 2:
            raise team.TeamError("post-open failure")
        return member.store._file_identity

    class FakeConnection:
        closed = False

        def close(self) -> None:
            self.closed = True

    connection = FakeConnection()
    monkeypatch.setattr(team_store, "_validate_store_path", fail_after_open)
    monkeypatch.setattr(team_store.sqlite3, "connect", lambda *_a, **_k: connection)

    with pytest.raises(team.TeamError, match="post-open failure"):
        member.store.connect()

    assert connection.closed is True


def test_store_schema_and_compatibility_trigger_bound_json_message_ids(
    tmp_path: Path,
) -> None:
    member = team.Team(make_repo(tmp_path / "repo"), "codex")
    connection = sqlite3.connect(member.store_path)
    try:
        table_sql = connection.execute(
            "SELECT sql FROM sqlite_master WHERE type='table' AND name='messages'"
        ).fetchone()[0]
        trigger_sql = connection.execute(
            "SELECT sql FROM sqlite_master WHERE type='trigger' "
            "AND name='messages_json_safe_id'"
        ).fetchone()[0]
    finally:
        connection.close()

    assert f"CHECK(id <= {team.MAX_MESSAGE_ID})" in table_sql
    assert f"NEW.id > {team.MAX_MESSAGE_ID}" in trigger_sql


def test_group_or_world_accessible_store_is_refused(tmp_path: Path) -> None:
    repo = make_repo(tmp_path / "repo")
    directory = repo / ".git" / "pipeline-team"
    directory.mkdir(mode=0o755)
    os.chmod(directory, 0o755)

    with pytest.raises(team.TeamError, match="group/world"):
        team.Team(repo, "codex")


def test_repo_root_must_be_exact_and_ignores_git_environment(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    repo = make_repo(tmp_path / "repo")
    other = make_repo(tmp_path / "other")
    subdirectory = repo / "subdirectory"
    subdirectory.mkdir()
    monkeypatch.setenv("GIT_DIR", str(other / ".git"))

    with pytest.raises(team.TeamError, match="exact Git worktree root"):
        team.Team(subdirectory, "codex")
    instance = team.Team(repo, "codex")
    assert instance.common_dir == (repo / ".git").resolve()


def test_group_or_world_writable_git_common_directory_is_refused(
    tmp_path: Path,
) -> None:
    repo = make_repo(tmp_path / "repo")
    common = repo / ".git"
    common.chmod(common.stat().st_mode | 0o020)

    with pytest.raises(team.TeamError, match="Git common directory.*writable"):
        team.Team(repo, "codex")


def test_git_common_directory_owned_by_another_user_is_refused(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    repo = make_repo(tmp_path / "repo")
    different_uid = os.geteuid() + 1
    monkeypatch.setattr(team_store.os, "geteuid", lambda: different_uid)

    with pytest.raises(team.TeamError, match="Git common directory.*owned"):
        team.Team(repo, "codex")


@pytest.mark.parametrize("value", (float("nan"), float("inf"), -float("inf")))
def test_nonfinite_waits_are_refused(tmp_path: Path, value: float) -> None:
    repo = make_repo(tmp_path / "repo")
    with pytest.raises(team.TeamError, match="wait_seconds"):
        team.Team(repo, "codex").wait(wait_seconds=value)
