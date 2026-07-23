"""Tests for the provider-pure local Claude seat launcher."""

from __future__ import annotations

import os
import subprocess
from pathlib import Path

import pytest

from scripts import claude_seat_launcher as launcher


SEATS = ("director", "director2", "operator", "operator2")


def test_build_launch_spec_scrubs_foreign_authority_and_binds_selected_seat(
    tmp_path: Path,
) -> None:
    ambient = {
        "PATH": "/bin",
        "CLAUDE_SEAT": "operator",
        "CLAUDE_PROJECT_DIR": "/foreign/project",
        "CLAUDE_CODE_SESSION_ID": "foreign-session",
        "CLAUDE_AGENT_ID": "foreign-agent",
        "CLAUDE_AGENT_TYPE": "foreign-type",
        "CLAUDE_RUNTIME_PROFILE": "foreign-profile",
        "CLAUDE_CODE_OAUTH_TOKEN": "preserved-test-token",
        "CODEX_SEAT": "director",
        "CURSOR_SEAT": "operator2",
        "AGY_SEAT": "agy-unit-director",
        "ANTIGRAVITY_SEAT": "director2",
        "GIT_INDEX_FILE": "/foreign/index",
        "GIT_DIR": "/foreign/git",
        "GIT_WORK_TREE": "/foreign/tree",
    }

    spec = launcher.build_launch_spec(
        repo_root=tmp_path,
        git_dir=tmp_path / ".git",
        seat="director2",
        inherited_env=ambient,
        claude_executable="/opt/claude",
        forwarded_args=["--resume", "literal prompt"],
    )

    assert spec.argv == ("/opt/claude", "--resume", "literal prompt")
    assert spec.env["CLAUDE_SEAT"] == "director2"
    assert spec.env["CLAUDE_PROJECT_DIR"] == str(tmp_path)
    assert spec.env["GIT_INDEX_FILE"] == str(
        tmp_path / ".git" / "index-claude-director2"
    )
    assert spec.env["CLAUDE_CODE_OAUTH_TOKEN"] == "preserved-test-token"
    assert spec.env["PATH"] == "/bin"
    assert "CLAUDE_CODE_SESSION_ID" not in spec.env
    assert "CLAUDE_AGENT_ID" not in spec.env
    assert "CLAUDE_AGENT_TYPE" not in spec.env
    assert "CLAUDE_RUNTIME_PROFILE" not in spec.env
    assert not any(
        key.startswith(("CODEX_", "CURSOR_", "AGY_", "ANTIGRAVITY_", "GIT_"))
        and key != "GIT_INDEX_FILE"
        for key in spec.env
    )


def test_all_four_claude_seats_use_distinct_provider_indexes(tmp_path: Path) -> None:
    paths = {
        launcher.build_launch_spec(
            tmp_path,
            tmp_path / ".git",
            seat,
            {},
            "claude",
            [],
        ).index_path
        for seat in SEATS
    }

    assert paths == {
        tmp_path / ".git" / f"index-claude-{seat}" for seat in SEATS
    }


def test_existing_non_regular_claude_index_fails_without_git_or_mutation(
    tmp_path: Path,
) -> None:
    index_path = tmp_path / ".git" / "index-claude-director"
    missing_target = tmp_path / "must-not-be-created"
    index_path.parent.mkdir()
    index_path.symlink_to(missing_target)
    calls: list[list[str]] = []

    def fake_run(argv: list[str], **kwargs: object) -> subprocess.CompletedProcess[str]:
        calls.append(argv)
        return subprocess.CompletedProcess(argv, 0, "", "")

    with pytest.raises(launcher.LaunchError, match="regular file"):
        launcher.ensure_seat_index(tmp_path, index_path, runner=fake_run)

    assert index_path.is_symlink()
    assert not missing_target.exists()
    assert calls == []


def test_existing_unreadable_and_empty_claude_indexes_fail_closed(
    tmp_path: Path,
) -> None:
    index_path = tmp_path / ".git" / "index-claude-director"
    index_path.parent.mkdir()
    index_path.write_bytes(b"preserve-index")

    def unreadable(
        argv: list[str], **kwargs: object
    ) -> subprocess.CompletedProcess[str]:
        return subprocess.CompletedProcess(argv, 128, "", "fatal: bad index")

    with pytest.raises(launcher.LaunchError, match="unusable"):
        launcher.ensure_seat_index(tmp_path, index_path, runner=unreadable)
    assert index_path.read_bytes() == b"preserve-index"

    def empty(argv: list[str], **kwargs: object) -> subprocess.CompletedProcess[str]:
        if "ls-files" in argv:
            return subprocess.CompletedProcess(argv, 0, "", "")
        if "ls-tree" in argv:
            return subprocess.CompletedProcess(argv, 0, "tracked.txt\0", "")
        return subprocess.CompletedProcess(argv, 0, "", "")

    with pytest.raises(launcher.LaunchError, match="empty while HEAD tracks files"):
        launcher.ensure_seat_index(tmp_path, index_path, runner=empty)
    assert index_path.read_bytes() == b"preserve-index"


def test_valid_existing_claude_index_preserves_staged_work(tmp_path: Path) -> None:
    index_path = tmp_path / ".git" / "index-claude-operator"
    index_path.parent.mkdir()
    index_path.write_bytes(b"preserve-staged-index")
    calls: list[list[str]] = []

    def fake_run(argv: list[str], **kwargs: object) -> subprocess.CompletedProcess[str]:
        calls.append(argv)
        if "ls-files" in argv:
            return subprocess.CompletedProcess(
                argv, 0, "100644 deadbeef 0\ttracked.txt\0", ""
            )
        if "status" in argv:
            return subprocess.CompletedProcess(argv, 0, "M  tracked.txt\n", "")
        raise AssertionError(f"unexpected Git command: {argv}")

    launcher.ensure_seat_index(tmp_path, index_path, runner=fake_run)

    assert index_path.read_bytes() == b"preserve-staged-index"
    assert not any("read-tree" in call for call in calls)


def test_missing_claude_index_is_seeded_once_from_head(tmp_path: Path) -> None:
    index_path = tmp_path / ".git" / "index-claude-operator2"
    index_path.parent.mkdir()
    calls: list[list[str]] = []

    def fake_run(argv: list[str], **kwargs: object) -> subprocess.CompletedProcess[str]:
        calls.append(argv)
        return subprocess.CompletedProcess(argv, 0, "", "")

    launcher.ensure_seat_index(tmp_path, index_path, runner=fake_run)

    assert calls == [
        [
            "git",
            "-C",
            str(tmp_path),
            "read-tree",
            f"--index-output={index_path}",
            "HEAD",
        ]
    ]


def test_dry_run_does_not_seed_index_or_start_claude(
    tmp_path: Path,
    repo_root: Path,
) -> None:
    git_dir = Path(
        subprocess.run(
            ["git", "-C", str(repo_root), "rev-parse", "--absolute-git-dir"],
            text=True,
            capture_output=True,
            check=True,
            env={key: value for key, value in os.environ.items() if not key.startswith("GIT_")},
        ).stdout.strip()
    )
    index_path = git_dir / "index-claude-director"
    index_before = index_path.read_bytes() if index_path.exists() else None
    marker = tmp_path / "claude-was-run"
    fake_bin = tmp_path / "bin"
    fake_bin.mkdir()
    fake_claude = fake_bin / "claude"
    fake_claude.write_text(f"#!/bin/sh\ntouch '{marker}'\n", encoding="utf-8")
    fake_claude.chmod(0o755)
    env = os.environ.copy()
    env["PATH"] = f"{fake_bin}:{env['PATH']}"

    result = subprocess.run(
        [
            str(repo_root / "coordination" / "bin" / "claude-seat"),
            "--dry-run",
            "director",
            "--",
            "unchanged start input",
        ],
        cwd=repo_root,
        env=env,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    assert '"unchanged start input"' in result.stdout
    assert (index_path.read_bytes() if index_path.exists() else None) == index_before
    assert not marker.exists()


def test_claude_guides_use_only_canonical_provider_prefixed_launch(repo_root: Path) -> None:
    continuation = (
        repo_root / "docs/protocol/claude/continuation.md"
    ).read_text(encoding="utf-8")
    extension = (
        repo_root / "docs/protocol/claude/four-seat-extension.md"
    ).read_text(encoding="utf-8")

    for text in (continuation, extension):
        assert "coordination/bin/claude-seat" in text
        assert "index-claude-" in text
    assert "export GIT_INDEX_FILE=" not in extension
    assert "/index-director2" not in extension
    assert "/index-operator2" not in extension
