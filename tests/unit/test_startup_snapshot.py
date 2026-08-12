from __future__ import annotations

import os
import subprocess
from pathlib import Path
from types import SimpleNamespace

import startup_snapshot


def _git(repo: Path, *args: str) -> str:
    completed = subprocess.run(
        ["git", *args],
        cwd=repo,
        check=True,
        capture_output=True,
        text=True,
        env={key: value for key, value in os.environ.items() if not key.startswith("GIT_")},
    )
    return completed.stdout.strip()


def _init_repo(repo: Path) -> None:
    _git(repo, "init", "-q")
    _git(repo, "config", "user.name", "Snapshot Test")
    _git(repo, "config", "user.email", "snapshot@example.test")
    (repo / "tracked.txt").write_text("base\n", encoding="utf-8")
    _git(repo, "add", "tracked.txt")
    _git(repo, "commit", "-qm", "initial state")


def _worktree_bytes(repo: Path) -> dict[str, bytes]:
    return {
        path.relative_to(repo).as_posix(): path.read_bytes()
        for path in repo.rglob("*")
        if path.is_file() and ".git" not in path.relative_to(repo).parts
    }


def test_git_snapshot_returns_full_head_branch_log_and_exact_dirty_paths(
    tmp_path: Path,
) -> None:
    _init_repo(tmp_path)
    (tmp_path / "tracked.txt").write_text("changed\n", encoding="utf-8")
    unusual = "line\nbreak.txt"
    (tmp_path / unusual).write_text("new\n", encoding="utf-8")

    snapshot = startup_snapshot.collect_git_snapshot(tmp_path, commits=1)

    assert snapshot.root == tmp_path.resolve()
    assert snapshot.head == _git(tmp_path, "rev-parse", "HEAD")
    assert len(snapshot.head) == 40
    assert snapshot.branch == _git(tmp_path, "rev-parse", "--abbrev-ref", "HEAD")
    assert snapshot.recent_commits == (_git(tmp_path, "log", "--oneline", "-1"),)
    assert snapshot.dirty_paths == (
        startup_snapshot.GitPathState(" M", "tracked.txt"),
        startup_snapshot.GitPathState("??", unusual),
    )
    assert snapshot.errors == ()


def test_git_snapshot_parses_rename_and_untracked_paths_without_loss(
    tmp_path: Path,
) -> None:
    _init_repo(tmp_path)
    old_path = "tracked.txt"
    renamed_path = "renamed\tfile.txt"
    _git(tmp_path, "mv", old_path, renamed_path)
    unusual = "untracked\nname.txt"
    (tmp_path / unusual).write_text("untracked\n", encoding="utf-8")

    snapshot = startup_snapshot.collect_git_snapshot(tmp_path)

    assert snapshot.dirty_paths == (
        startup_snapshot.GitPathState("R ", renamed_path, old_path),
        startup_snapshot.GitPathState("??", unusual),
    )
    assert snapshot.errors == ()


def test_git_snapshot_clears_inherited_git_index_file(
    tmp_path: Path,
    monkeypatch,
) -> None:
    _init_repo(tmp_path)
    monkeypatch.setenv("GIT_INDEX_FILE", str(tmp_path / "not-the-real-index"))
    monkeypatch.setenv("GIT_DIR", str(tmp_path / "not-a-git-dir"))

    snapshot = startup_snapshot.collect_git_snapshot(tmp_path)

    assert snapshot.head == _git(tmp_path, "rev-parse", "HEAD")
    assert snapshot.branch is not None
    assert snapshot.errors == ()


def test_git_snapshot_reports_unavailable_state_instead_of_clean_state(
    tmp_path: Path,
) -> None:
    snapshot = startup_snapshot.collect_git_snapshot(tmp_path)

    assert snapshot.head is None
    assert snapshot.branch is None
    assert snapshot.recent_commits == ()
    assert snapshot.dirty_paths == ()
    assert snapshot.errors
    assert any(error.startswith("dirty paths unavailable:") for error in snapshot.errors)


def test_git_snapshot_never_reports_the_enclosing_repository(
    tmp_path: Path, monkeypatch
) -> None:
    # A non-repository root inside a real checkout (e.g. an in-worktree
    # scratch directory) must answer "unavailable" — never the enclosing
    # repository's HEAD. The guarantee belongs to the runtime itself, so
    # drop any ambient ceiling the test session may have installed.
    monkeypatch.delenv("GIT_CEILING_DIRECTORIES", raising=False)
    _init_repo(tmp_path)
    scratch = tmp_path / "scratch"
    scratch.mkdir()

    snapshot = startup_snapshot.collect_git_snapshot(scratch)

    assert snapshot.head is None
    assert snapshot.branch is None
    assert snapshot.recent_commits == ()
    assert snapshot.errors


def test_mailbox_snapshot_uses_live_ref_bus_cursor_without_consuming_it(
    tmp_path: Path,
    monkeypatch,
) -> None:
    cursor_path = tmp_path / "coordination/mailbox/seen/director.txt"
    cursor_path.parent.mkdir(parents=True)
    cursor_path.write_bytes(b"17\n")
    event = SimpleNamespace(seq=18, kind="status", sender="operator", recipient="director")
    calls: list[tuple[Path, str]] = []

    def fake_events(root: Path, seat: str):
        calls.append((Path(root), seat))
        return [event]

    monkeypatch.setattr(startup_snapshot.bus_unread, "bus_unread_events", fake_events)
    monkeypatch.setattr(
        startup_snapshot.bus_unread,
        "format_unread",
        lambda value: f"live-ref-seq-{value.seq}",
    )

    snapshot = startup_snapshot.collect_mailbox_snapshot(tmp_path, "director")

    assert calls == [(tmp_path.resolve(), "director")]
    assert snapshot == startup_snapshot.MailboxSnapshot(
        seat="director",
        cursor="17",
        unread_refs=("live-ref-seq-18",),
        unavailable_reason=None,
    )
    assert cursor_path.read_bytes() == b"17\n"


def test_mailbox_snapshot_surfaces_legacy_filenames_and_unavailable_bus(
    tmp_path: Path,
    monkeypatch,
) -> None:
    seen = tmp_path / "coordination/mailbox/seen"
    sent = tmp_path / "coordination/mailbox/sent"
    seen.mkdir(parents=True)
    sent.mkdir(parents=True)
    (seen / "director.txt").write_text("2026-07-19T00:00:00Z\n", encoding="utf-8")
    names = (
        "2026-07-18T23-59-59Z-operator-to-director-old.md",
        "2026-07-19T00-00-01Z-operator-to-director-note.md",
        "2026-07-19T00-00-02Z-operator2-to-all-status.md",
        "2026-07-19T00-00-03Z-operator-to-operator2-other.md",
    )
    for name in names:
        (sent / name).write_text("# event\n", encoding="utf-8")

    legacy = startup_snapshot.collect_mailbox_snapshot(tmp_path, "director")

    assert legacy.unread_refs == names[1:3]
    assert legacy.unavailable_reason is None

    (seen / "director.txt").write_text("17\n", encoding="utf-8")
    monkeypatch.setattr(startup_snapshot.bus_unread, "bus_unread_events", lambda *_: None)
    unavailable = startup_snapshot.collect_mailbox_snapshot(tmp_path, "director")

    assert unavailable.cursor == "17"
    assert unavailable.unread_refs == ()
    assert unavailable.unavailable_reason == "ref-bus"


def test_snapshot_collection_changes_no_cursor_index_ref_or_worktree_byte(
    tmp_path: Path,
) -> None:
    _init_repo(tmp_path)
    cursor_path = tmp_path / "coordination/mailbox/seen/director.txt"
    cursor_path.parent.mkdir(parents=True)
    cursor_path.write_text("2026-07-19T00:00:00Z\n", encoding="utf-8")
    sent_path = (
        tmp_path
        / "coordination/mailbox/sent/2026-07-19T00-00-01Z-operator-to-director-note.md"
    )
    sent_path.parent.mkdir(parents=True)
    sent_path.write_text("# note\n", encoding="utf-8")
    _git(tmp_path, "add", "coordination")
    _git(tmp_path, "commit", "-qm", "mailbox fixture")
    _git(tmp_path, "update-ref", "refs/threeway/cursors/director", "HEAD")

    index_path = Path(_git(tmp_path, "rev-parse", "--git-path", "index"))
    if not index_path.is_absolute():
        index_path = tmp_path / index_path
    before = (
        cursor_path.read_bytes(),
        index_path.read_bytes(),
        _git(tmp_path, "for-each-ref", "--format=%(refname) %(objectname)"),
        _worktree_bytes(tmp_path),
    )

    git_snapshot = startup_snapshot.collect_git_snapshot(tmp_path)
    mailbox_snapshot = startup_snapshot.collect_mailbox_snapshot(tmp_path, "director")

    after = (
        cursor_path.read_bytes(),
        index_path.read_bytes(),
        _git(tmp_path, "for-each-ref", "--format=%(refname) %(objectname)"),
        _worktree_bytes(tmp_path),
    )
    assert git_snapshot.errors == ()
    assert mailbox_snapshot.unavailable_reason is None
    assert after == before
