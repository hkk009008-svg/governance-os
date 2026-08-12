from __future__ import annotations

from pathlib import Path
import subprocess

import pytest

from scripts import cursor_review_snapshot as snapshot


def _git(root: Path, *args: str) -> str:
    return subprocess.run(
        ["git", "-C", str(root), *args],
        text=True,
        capture_output=True,
        check=True,
    ).stdout.strip()


def _repo(tmp_path: Path) -> tuple[Path, str]:
    repo = tmp_path / "repo"
    repo.mkdir()
    _git(repo, "init", "-q")
    _git(repo, "config", "user.email", "tests@example.invalid")
    _git(repo, "config", "user.name", "Tests")
    (repo / "payload.txt").write_text("reviewed\n", encoding="utf-8")
    _git(repo, "add", "payload.txt")
    _git(repo, "commit", "-q", "-m", "reviewed")
    head = _git(repo, "rev-parse", "HEAD")
    (repo / "payload.txt").write_text("later\n", encoding="utf-8")
    _git(repo, "commit", "-q", "-am", "later")
    return repo, head


def test_materializes_exact_commit_into_workspace_scratch(tmp_path: Path) -> None:
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    repository, head = _repo(tmp_path)
    output = Path(f".pytest-verify-tmp/cursor-reviews/{head}")

    destination = snapshot.materialize(
        workspace,
        repository=repository,
        head=head,
        output=output,
    )

    assert destination == (workspace / output).resolve()
    assert (destination / "payload.txt").read_text(encoding="utf-8") == "reviewed\n"
    assert (destination / snapshot.MARKER).read_text(encoding="ascii").strip() == head
    assert (
        snapshot.materialize(
            workspace,
            repository=repository,
            head=head,
            output=output,
        )
        == destination
    )


def test_rejects_output_outside_review_scratch(tmp_path: Path) -> None:
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    repository, head = _repo(tmp_path)
    with pytest.raises(snapshot.ReviewSnapshotError, match="must be under"):
        snapshot.materialize(
            workspace,
            repository=repository,
            head=head,
            output=Path("outside"),
        )


def test_rejects_archive_symlink_that_escapes_snapshot(tmp_path: Path) -> None:
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    repository, _ = _repo(tmp_path)
    (repository / "escape").symlink_to("../../outside")
    _git(repository, "add", "escape")
    _git(repository, "commit", "-q", "-m", "escaping symlink")
    head = _git(repository, "rev-parse", "HEAD")

    with pytest.raises(snapshot.ReviewSnapshotError, match="symlink escapes"):
        snapshot.materialize(
            workspace,
            repository=repository,
            head=head,
            output=Path(f".pytest-verify-tmp/cursor-reviews/{head}"),
        )


def test_require_exact_head_accepts_match_and_rejects_drift(tmp_path: Path) -> None:
    repository, reviewed = _repo(tmp_path)
    later = _git(repository, "rev-parse", "HEAD")
    assert later != reviewed

    with pytest.raises(snapshot.ReviewSnapshotError, match="not reviewed_head"):
        snapshot.require_exact_head(repository, reviewed)

    _git(repository, "checkout", "-q", reviewed)
    assert snapshot.require_exact_head(repository, reviewed) == reviewed
