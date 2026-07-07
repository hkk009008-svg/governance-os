"""Regression tests for protocol coordination shell tooling."""

from __future__ import annotations

import os
import subprocess
from pathlib import Path

import pytest


def _run(
    args: list[str | Path],
    cwd: Path,
    *,
    env: dict[str, str] | None = None,
    input_text: str | None = None,
) -> subprocess.CompletedProcess[str]:
    full_env = os.environ.copy()
    if env:
        full_env.update(env)
    return subprocess.run(
        [str(arg) for arg in args],
        cwd=cwd,
        env=full_env,
        input=input_text,
        text=True,
        capture_output=True,
        check=False,
    )


def _git(repo: Path, *args: str, env: dict[str, str] | None = None) -> str:
    result = _run(["git", *args], repo, env=env)
    assert result.returncode == 0, result.stderr
    return result.stdout.strip()


def _init_repo(repo: Path) -> None:
    _git(repo, "init", "-q")
    _git(repo, "config", "user.email", "test@example.com")
    _git(repo, "config", "user.name", "Test User")


def test_send_event_force_stages_ignored_mailbox_event(tmp_path: Path, repo_root: Path):
    repo = tmp_path / "repo"
    repo.mkdir()
    _init_repo(repo)
    (repo / ".gitignore").write_text(
        "coordination/mailbox/sent/*\n"
        "!coordination/mailbox/sent/.gitkeep\n",
        encoding="utf-8",
    )
    mailbox = repo / "coordination" / "mailbox"
    (mailbox / "sent").mkdir(parents=True)
    (mailbox / "seen").mkdir()
    (mailbox / "kinds.txt").write_text("status\n", encoding="utf-8")
    (mailbox / "seen" / "director.txt").write_text("0\n", encoding="utf-8")
    (mailbox / "sent" / ".gitkeep").write_text("", encoding="utf-8")
    _git(repo, "add", ".")
    _git(repo, "commit", "-q", "-m", "seed")

    result = _run(
        [
            repo_root / "coordination" / "bin" / "send-event",
            "director",
            "operator",
            "status",
            "ignored mailbox event",
        ],
        repo,
        input_text="body\n",
    )

    assert result.returncode == 0, result.stderr
    staged = _git(repo, "diff", "--cached", "--name-only")
    assert "coordination/mailbox/sent/" in staged
    assert staged.endswith("-director-to-operator-status.md")


@pytest.mark.parametrize(
    "from_seat",
    ["director", "director2", "operator", "operator2", "coordinator", "coordinator2"],
)
def test_send_event_keeps_mailbox_event_when_git_index_is_locked_for_every_sender(
    tmp_path: Path, repo_root: Path, from_seat: str
):
    repo = tmp_path / "repo"
    repo.mkdir()
    _init_repo(repo)
    mailbox = repo / "coordination" / "mailbox"
    (mailbox / "sent").mkdir(parents=True)
    (mailbox / "seen").mkdir()
    (mailbox / "kinds.txt").write_text("status\n", encoding="utf-8")
    (mailbox / "seen" / f"{from_seat}.txt").write_text("0\n", encoding="utf-8")
    (mailbox / "sent" / ".gitkeep").write_text("", encoding="utf-8")
    _git(repo, "add", ".")
    _git(repo, "commit", "-q", "-m", "seed")

    index_lock = repo / ".git" / "index.lock"
    index_lock.write_text("locked\n", encoding="utf-8")
    try:
        result = _run(
            [
                repo_root / "coordination" / "bin" / "send-event",
                from_seat,
                "all",
                "status",
                "index locked mailbox event",
            ],
            repo,
            input_text="body\n",
        )
    finally:
        index_lock.unlink()

    assert result.returncode == 0, result.stderr
    assert "not staged" in result.stdout
    sent_files = sorted((mailbox / "sent").glob(f"*-{from_seat}-to-all-status.md"))
    assert len(sent_files) == 1
    assert "index locked mailbox event" in sent_files[0].read_text(encoding="utf-8")
    assert _git(repo, "diff", "--cached", "--name-only") == ""


@pytest.mark.parametrize(
    ("hook_path", "marker_dir"),
    [
        (".claude/hooks/update-state.sh", ".claude/hooks"),
        (".codex/hooks/update-state.sh", ".codex/hooks"),
    ],
)
def test_update_state_syncs_markerless_clean_seeded_seat_index(
    tmp_path: Path, repo_root: Path, hook_path: str, marker_dir: str
):
    repo = tmp_path / "repo"
    repo.mkdir()
    _init_repo(repo)
    hook_destination = repo / hook_path
    hook_destination.parent.mkdir(parents=True)
    hook_destination.write_text((repo_root / hook_path).read_text(encoding="utf-8"), encoding="utf-8")
    hook_destination.chmod(0o755)

    (repo / "coordination" / "mailbox" / "sent").mkdir(parents=True)
    (repo / "coordination" / "mailbox" / "seen").mkdir(parents=True)
    (repo / "coordination" / "presence").mkdir(parents=True)
    (repo / "tracked.txt").write_text("before\n", encoding="utf-8")
    _git(repo, "add", ".")
    _git(repo, "commit", "-q", "-m", "baseline")

    seat_index = repo / ".git" / "index-director"
    _git(repo, "read-tree", f"--index-output={seat_index}", "HEAD")
    assert not (repo / marker_dir / f".last-index-sync-{seat_index.name}").exists()

    (repo / "tracked.txt").write_text("after\n", encoding="utf-8")
    _git(repo, "add", "tracked.txt")
    _git(repo, "commit", "-q", "-m", "peer commit")
    head_tree = _git(repo, "show", "-s", "--format=%T", "HEAD")

    result = _run([hook_destination], repo, env={"GIT_INDEX_FILE": str(seat_index)})

    assert result.returncode == 0, result.stderr
    marker = repo / marker_dir / f".last-index-sync-{seat_index.name}"
    assert marker.read_text(encoding="utf-8").strip() == _git(repo, "rev-parse", "HEAD")
    index_tree = _git(repo, "write-tree", env={"GIT_INDEX_FILE": str(seat_index)})
    assert index_tree == head_tree
