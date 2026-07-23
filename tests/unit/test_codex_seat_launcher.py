"""Tests for the local per-seat Codex launcher."""

from __future__ import annotations

import os
import subprocess
from pathlib import Path

import pytest

from scripts import codex_seat_launcher as launcher


SEATS = ("director", "director2", "operator", "operator2", "coordinator")


def _write_config(path: Path, overrides: dict[str, tuple[str, str]] | None = None) -> None:
    settings = {
        seat: (f"model-{seat}", "default")
        for seat in SEATS
    }
    settings.update(overrides or {})
    blocks = []
    for seat, (model, tier) in settings.items():
        blocks.append(
            f'[seats.{seat}]\nmodel = "{model}"\nservice_tier = "{tier}"\n'
        )
    path.write_text("\n".join(blocks), encoding="utf-8")


@pytest.mark.parametrize(
    ("seat", "mode", "role", "behavior_source"),
    [
        ("director", "live-seat", "director", "director"),
        ("director2", "live-seat", "director2", "director"),
        ("operator", "live-seat", "operator", "operator2"),
        ("operator2", "live-seat", "operator2", "operator2"),
        ("coordinator", "coordinator", "coordinator", None),
    ],
)
def test_build_launch_spec_sets_exact_seat_identity(
    tmp_path: Path,
    seat: str,
    mode: str,
    role: str,
    behavior_source: str | None,
) -> None:
    config_path = tmp_path / "seats.toml"
    _write_config(config_path)
    settings = launcher.load_seat_settings(config_path)
    ambient = {
        "PATH": "/bin",
        "CODEX_SEAT": "wrong-seat",
        "CODEX_AGENT_MODE": "wrong-mode",
        "CODEX_AGENT_ROLE": "wrong-role",
        "CODEX_BEHAVIOR_SOURCE": "wrong-source",
        "GIT_INDEX_FILE": "/wrong-index",
    }

    spec = launcher.build_launch_spec(
        repo_root=tmp_path,
        git_dir=tmp_path / ".git",
        seat=seat,
        settings=settings,
        inherited_env=ambient,
        codex_executable="/opt/codex",
        forwarded_args=[],
    )

    assert spec.env["CODEX_SEAT"] == seat
    assert spec.env["CODEX_AGENT_MODE"] == mode
    assert spec.env["CODEX_AGENT_ROLE"] == role
    assert spec.env.get("CODEX_BEHAVIOR_SOURCE") == behavior_source
    assert spec.env["GIT_INDEX_FILE"] == str(
        tmp_path / ".git" / f"index-codex-{seat}"
    )


def test_each_seat_uses_only_its_own_model_and_tier(tmp_path: Path) -> None:
    config_path = tmp_path / "seats.toml"
    _write_config(
        config_path,
        {
            "director": ("gpt-director", "fast"),
            "director2": ("gpt-director2", "default"),
        },
    )
    settings = launcher.load_seat_settings(config_path)

    first = launcher.build_launch_spec(
        tmp_path,
        tmp_path / ".git",
        "director",
        settings,
        {},
        "codex",
        [],
    )
    second = launcher.build_launch_spec(
        tmp_path,
        tmp_path / ".git",
        "director2",
        settings,
        {},
        "codex",
        [],
    )

    assert first.argv[:5] == (
        "codex",
        "--model",
        "gpt-director",
        "--config",
        'service_tier="fast"',
    )
    assert second.argv[:5] == (
        "codex",
        "--model",
        "gpt-director2",
        "--config",
        'service_tier="default"',
    )


def test_all_seat_indexes_are_distinct(tmp_path: Path) -> None:
    config_path = tmp_path / "seats.toml"
    _write_config(config_path)
    settings = launcher.load_seat_settings(config_path)

    paths = {
        launcher.build_launch_spec(
            tmp_path,
            tmp_path / ".git",
            seat,
            settings,
            {},
            "codex",
            [],
        ).index_path
        for seat in SEATS
    }

    assert len(paths) == len(SEATS)


def test_forwarded_codex_arguments_remain_literal(tmp_path: Path) -> None:
    config_path = tmp_path / "seats.toml"
    _write_config(config_path)
    forwarded = ["prompt with spaces", "'quoted'", ";", "$(touch nope)", "--search"]

    spec = launcher.build_launch_spec(
        tmp_path,
        tmp_path / ".git",
        "operator",
        launcher.load_seat_settings(config_path),
        {},
        "codex",
        forwarded,
    )

    assert spec.argv[-len(forwarded) :] == tuple(forwarded)


@pytest.mark.parametrize(
    "body",
    [
        "[seats.director]\nmodel='gpt'\nservice_tier='default'\n",
        "".join(
            f"[seats.{seat}]\nmodel='gpt'\nservice_tier='turbo'\n"
            for seat in SEATS
        ),
        "".join(
            f"[seats.{seat}]\nmodel='gpt'\nservice_tier='default'\nextra=true\n"
            for seat in SEATS
        ),
        "".join(
            f"[seats.{seat}]\nmodel={1 if seat == 'director' else repr('gpt')}\n"
            "service_tier='default'\n"
            for seat in SEATS
        ),
        "".join(
            f"[seats.{seat}]\nmodel='gpt'\nservice_tier='default'\n"
            for seat in (*SEATS, "extra")
        ),
    ],
)
def test_config_rejects_incomplete_or_unknown_settings(tmp_path: Path, body: str) -> None:
    config_path = tmp_path / "bad.toml"
    config_path.write_text(body, encoding="utf-8")

    with pytest.raises(launcher.ConfigError):
        launcher.load_seat_settings(config_path)


def test_ensure_seat_index_seeds_only_when_missing(tmp_path: Path) -> None:
    index_path = tmp_path / ".git" / "index-codex-director"
    calls: list[list[str]] = []

    def fake_run(argv: list[str], **kwargs: object) -> subprocess.CompletedProcess[str]:
        calls.append(argv)
        if "read-tree" in argv:
            index_path.parent.mkdir()
            index_path.write_text("seed", encoding="utf-8")
        if "ls-files" in argv:
            return subprocess.CompletedProcess(
                argv,
                0,
                "100644 deadbeef 0\ttracked.txt\0",
                "",
            )
        return subprocess.CompletedProcess(argv, 0, "", "")

    launcher.ensure_seat_index(tmp_path, index_path, runner=fake_run)
    launcher.ensure_seat_index(tmp_path, index_path, runner=fake_run)

    assert [call for call in calls if "read-tree" in call] == [
        [
            "git",
            "-C",
            str(tmp_path),
            "read-tree",
            f"--index-output={index_path}",
            "HEAD",
        ]
    ]


def test_existing_unreadable_seat_index_fails_closed(tmp_path: Path) -> None:
    index_path = tmp_path / ".git" / "index-codex-director"
    index_path.parent.mkdir()
    index_path.write_bytes(b"preserve-corrupt-index")

    def fake_run(argv: list[str], **kwargs: object) -> subprocess.CompletedProcess[str]:
        return subprocess.CompletedProcess(
            argv,
            128,
            "",
            "fatal: unable to read tree deadbeef",
        )

    with pytest.raises(launcher.LaunchError, match="existing seat index.*unusable"):
        launcher.ensure_seat_index(tmp_path, index_path, runner=fake_run)

    assert index_path.read_bytes() == b"preserve-corrupt-index"


def test_existing_empty_seat_index_against_non_empty_head_fails_closed(
    tmp_path: Path,
) -> None:
    index_path = tmp_path / ".git" / "index-codex-director"
    index_path.parent.mkdir()
    index_path.write_bytes(b"preserve-empty-index")

    def fake_run(argv: list[str], **kwargs: object) -> subprocess.CompletedProcess[str]:
        if "ls-files" in argv:
            return subprocess.CompletedProcess(argv, 0, "", "")
        if "ls-tree" in argv:
            return subprocess.CompletedProcess(argv, 0, "tracked.txt\0", "")
        return subprocess.CompletedProcess(argv, 0, "", "")

    with pytest.raises(launcher.LaunchError, match="empty while HEAD tracks files"):
        launcher.ensure_seat_index(tmp_path, index_path, runner=fake_run)

    assert index_path.read_bytes() == b"preserve-empty-index"


def test_valid_existing_seat_index_preserves_staged_work(tmp_path: Path) -> None:
    index_path = tmp_path / ".git" / "index-codex-director"
    index_path.parent.mkdir()
    index_path.write_bytes(b"preserve-staged-index")
    calls: list[list[str]] = []

    def fake_run(argv: list[str], **kwargs: object) -> subprocess.CompletedProcess[str]:
        calls.append(argv)
        if "ls-files" in argv:
            return subprocess.CompletedProcess(
                argv,
                0,
                "100644 deadbeef 0\ttracked.txt\0",
                "",
            )
        if "status" in argv:
            return subprocess.CompletedProcess(argv, 0, "M  tracked.txt\n", "")
        raise AssertionError(f"unexpected Git command: {argv}")

    launcher.ensure_seat_index(tmp_path, index_path, runner=fake_run)

    assert index_path.read_bytes() == b"preserve-staged-index"
    assert not any("read-tree" in call for call in calls)


def test_dry_run_does_not_create_index_or_start_codex(tmp_path: Path, repo_root: Path) -> None:
    config_path = tmp_path / "seats.toml"
    _write_config(config_path)
    git_dir = Path(
        subprocess.run(
            ["git", "-C", str(repo_root), "rev-parse", "--absolute-git-dir"],
            text=True,
            capture_output=True,
            check=True,
            env={
                key: value
                for key, value in os.environ.items()
                if key != "GIT_INDEX_FILE"
            },
        ).stdout.strip()
    )
    index_path = git_dir / "index-codex-director"
    index_before = (
        (index_path.stat().st_size, index_path.stat().st_mtime_ns)
        if index_path.exists()
        else None
    )
    marker = tmp_path / "codex-was-run"
    fake_bin = tmp_path / "bin"
    fake_bin.mkdir()
    fake_codex = fake_bin / "codex"
    fake_codex.write_text(f"#!/bin/sh\ntouch '{marker}'\n", encoding="utf-8")
    fake_codex.chmod(0o755)
    env = os.environ.copy()
    env["PATH"] = f"{fake_bin}:{env['PATH']}"

    result = subprocess.run(
        [
            str(repo_root / "coordination" / "bin" / "codex-seat"),
            "--dry-run",
            "--config",
            str(config_path),
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
    index_after = (
        (index_path.stat().st_size, index_path.stat().st_mtime_ns)
        if index_path.exists()
        else None
    )
    assert index_after == index_before
    assert not marker.exists()
