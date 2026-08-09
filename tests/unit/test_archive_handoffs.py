from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

import archive_handoffs


def _git(repo: Path, *args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", "-C", str(repo), *args],
        check=check,
        capture_output=True,
        text=True,
    )


def _repo_with_handoffs(tmp_path: Path) -> tuple[Path, list[Path]]:
    repo = tmp_path / "repo"
    docs = repo / "docs"
    docs.mkdir(parents=True)
    _git(repo, "init", "-b", "main")
    _git(repo, "config", "user.name", "Archive Test")
    _git(repo, "config", "user.email", "archive@example.invalid")
    paths = [docs / "HANDOFF-one.md", docs / "HANDOFF-two.md"]
    for path in paths:
        path.write_text(path.name + "\n", encoding="utf-8")
    _git(repo, "add", ".")
    _git(repo, "commit", "-m", "handoffs")
    return repo, paths


def test_archive_index_accumulates_same_day_runs(tmp_path: Path) -> None:
    archive_handoffs._write_index(tmp_path, "2026-08-09", ["one.md"], ["live.md"])
    archive_handoffs._write_index(tmp_path, "2026-08-09", ["two.md"], ["live.md"])

    body = (tmp_path / "INDEX.md").read_text(encoding="utf-8")
    assert body.count("[one.md](one.md)") == 1
    assert body.count("[two.md](two.md)") == 1


def test_git_move_failure_is_not_replaced_by_untracked_filesystem_move(
    tmp_path: Path, monkeypatch
) -> None:
    def fail(*_args, **_kwargs):
        raise subprocess.CalledProcessError(1, ["git", "mv"], stderr=b"rejected")

    monkeypatch.setattr(archive_handoffs.subprocess, "run", fail)

    with pytest.raises(RuntimeError, match="git mv failed"):
        archive_handoffs._git_mv(tmp_path, "docs/a.md", "docs/archive/a.md")


def test_later_move_failure_restores_earlier_staged_move(
    tmp_path: Path, monkeypatch
) -> None:
    repo, paths = _repo_with_handoffs(tmp_path)
    target = repo / "docs/archive/2026-08-09"
    real_move = archive_handoffs._git_mv

    def fail_second(repo_root, rel_src, rel_dst):
        if rel_src.endswith("HANDOFF-two.md"):
            raise RuntimeError("forced second move failure")
        return real_move(repo_root, rel_src, rel_dst)

    monkeypatch.setattr(archive_handoffs, "_git_mv", fail_second)

    with pytest.raises(RuntimeError, match="forced second move failure"):
        archive_handoffs._archive_batch(
            str(repo), str(target), "2026-08-09", [str(path) for path in paths], []
        )

    assert all(path.is_file() for path in paths)
    assert _git(repo, "status", "--porcelain").stdout == ""
    assert not (target / "INDEX.md").exists()


def test_keyboard_interrupt_restores_earlier_staged_move(
    tmp_path: Path, monkeypatch
) -> None:
    repo, paths = _repo_with_handoffs(tmp_path)
    target = repo / "docs/archive/2026-08-09"
    real_move = archive_handoffs._git_mv

    def interrupt_second(repo_root, rel_src, rel_dst):
        if rel_src.endswith("HANDOFF-two.md"):
            raise KeyboardInterrupt
        return real_move(repo_root, rel_src, rel_dst)

    monkeypatch.setattr(archive_handoffs, "_git_mv", interrupt_second)

    with pytest.raises(KeyboardInterrupt):
        archive_handoffs._archive_batch(
            str(repo), str(target), "2026-08-09", [str(path) for path in paths], []
        )

    assert all(path.is_file() for path in paths)
    assert _git(repo, "status", "--porcelain").stdout == ""
    assert not (target / "INDEX.md").exists()


def test_unmatched_keep_name_is_rejected_before_archiving(tmp_path: Path) -> None:
    handoffs = [tmp_path / "HANDOFF-one.md", tmp_path / "HANDOFF-two.md"]

    with pytest.raises(ValueError, match="did not match"):
        archive_handoffs._select_handoffs(handoffs, {"HANDOFF-typo.md"})


def test_tracked_symlink_archive_target_is_rejected_without_mutation(
    tmp_path: Path,
) -> None:
    repo, paths = _repo_with_handoffs(tmp_path)
    outside = tmp_path / "outside"
    outside.mkdir()
    archive = repo / "docs/archive"
    archive.mkdir()
    target = archive / "2026-08-09"
    target.symlink_to(outside, target_is_directory=True)
    _git(repo, "add", "docs/archive/2026-08-09")
    _git(repo, "commit", "-m", "tracked archive symlink")

    with pytest.raises(RuntimeError, match="symlink"):
        archive_handoffs._archive_batch(
            str(repo), str(target), "2026-08-09", [str(path) for path in paths], []
        )

    assert all(path.is_file() for path in paths)
    assert target.is_symlink()
    assert list(outside.iterdir()) == []
    assert _git(repo, "status", "--porcelain").stdout == ""


def test_tracked_symlink_archive_index_is_rejected_without_external_write(
    tmp_path: Path,
) -> None:
    repo, paths = _repo_with_handoffs(tmp_path)
    target = repo / "docs/archive/2026-08-09"
    target.mkdir(parents=True)
    outside = tmp_path / "outside-index.md"
    outside.write_text("do not overwrite\n", encoding="utf-8")
    (target / "INDEX.md").symlink_to(outside)
    _git(repo, "add", "docs/archive/2026-08-09/INDEX.md")
    _git(repo, "commit", "-m", "tracked archive index symlink")

    with pytest.raises(RuntimeError, match="regular non-symlink"):
        archive_handoffs._archive_batch(
            str(repo), str(target), "2026-08-09", [str(path) for path in paths], []
        )

    assert all(path.is_file() for path in paths)
    assert (target / "INDEX.md").is_symlink()
    assert outside.read_text(encoding="utf-8") == "do not overwrite\n"
    assert _git(repo, "status", "--porcelain").stdout == ""


def test_successful_batch_stages_moves_and_index(tmp_path: Path) -> None:
    repo, paths = _repo_with_handoffs(tmp_path)
    target = repo / "docs/archive/2026-08-09"

    index, moved = archive_handoffs._archive_batch(
        str(repo), str(target), "2026-08-09", [str(path) for path in paths], []
    )

    assert moved == 2
    assert Path(index).is_file()
    staged = _git(repo, "diff", "--cached", "--name-status").stdout
    assert "HANDOFF-one.md" in staged
    assert "HANDOFF-two.md" in staged
    assert "docs/archive/2026-08-09/INDEX.md" in staged
