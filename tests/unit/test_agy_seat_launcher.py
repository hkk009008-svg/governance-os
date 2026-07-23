"""Tests for the local per-seat AGY (Antigravity) launcher."""

from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path

import pytest

from scripts import agy_seat_launcher as launcher


SEATS = ("director", "director2", "operator", "operator2", "coordinator")


def _write_config(path: Path, overrides: dict[str, tuple[str, str]] | None = None) -> None:
    settings = {
        seat: (f"gemini-{seat}", "default")
        for seat in SEATS
    }
    settings.update(overrides or {})
    blocks = []
    for seat, (model, tier) in settings.items():
        blocks.append(
            f'[seats.{seat}]\nmodel = "{model}"\nservice_tier = "{tier}"\n'
        )
    path.write_text("\n".join(blocks), encoding="utf-8")


def test_build_launch_spec_defaults_to_advisory_agy_identity_and_cleans_authority(
    tmp_path: Path,
) -> None:
    config_path = tmp_path / "seats.toml"
    _write_config(config_path)
    settings = launcher.load_seat_settings(config_path)
    ambient = {
        "PATH": "/bin",
        "AGY_SEAT": "wrong-seat",
        "AGY_AGENT_MODE": "wrong-mode",
        "AGY_AGENT_ROLE": "wrong-role",
        "AGY_BEHAVIOR_SOURCE": "wrong-source",
        "AGY_UNKNOWN_FUTURE_FIELD": "stale",
        "AGY_API_KEY": "agy-test-key",
        "CLAUDE_CODE_ENTRYPOINT": "foreign-authority",
        "CURSOR_SEAT": "operator",
        "CODEX_SEAT": "director",
        "CODEX_AGENT_MODE": "live-seat",
        "ANTIGRAVITY_SEAT": "director2",
        "GIT_INDEX_FILE": "/wrong-index",
        "GIT_DIR": "/foreign/git",
        "GIT_WORK_TREE": "/foreign/tree",
    }

    spec = launcher.build_launch_spec(
        repo_root=tmp_path,
        git_dir=tmp_path / ".git",
        seat="director",
        settings=settings,
        inherited_env=ambient,
        agy_executable="/opt/agy",
        forwarded_args=[],
    )

    assert spec.env["AGY_SEAT"] == "agy-advisory"
    assert spec.env["AGY_AGENT_MODE"] == "advisory-readiness"
    assert spec.env["AGY_AGENT_ROLE"] == "readiness-bridge"
    assert spec.env["AGY_BEHAVIOR_SOURCE"] == "advisory-read-only"
    assert spec.env["AGY_GIT_INDEX_FILE"] == str(
        tmp_path / ".git" / "index-agy-director"
    )
    assert spec.env["GIT_INDEX_FILE"] == str(
        tmp_path / ".git" / "index-agy-director"
    )
    assert spec.env["AGY_API_KEY"] == "agy-test-key"
    assert spec.env["PATH"] == "/bin"
    assert not any(
        key.startswith(("CLAUDE_", "CURSOR_", "CODEX_", "ANTIGRAVITY_"))
        for key in spec.env
    )
    assert "AGY_UNKNOWN_FUTURE_FIELD" not in spec.env
    assert "GIT_DIR" not in spec.env
    assert "GIT_WORK_TREE" not in spec.env


def test_build_launch_spec_requires_explicit_isolated_mode_for_agy_unit(
    tmp_path: Path,
) -> None:
    config_path = tmp_path / "seats.toml"
    _write_config(config_path)

    spec = launcher.build_launch_spec(
        repo_root=tmp_path,
        git_dir=tmp_path / ".git",
        seat="director",
        settings=launcher.load_seat_settings(config_path),
        inherited_env={},
        agy_executable="/opt/agy",
        forwarded_args=[],
        mode=launcher.SINGLE_MODEL_MODE,
    )

    assert spec.env["AGY_SEAT"] == "agy-unit-director"
    assert spec.env["AGY_AGENT_MODE"] == launcher.SINGLE_MODEL_MODE
    assert spec.env["AGY_AGENT_ROLE"] == "agy-unit-director"
    assert spec.env["AGY_BEHAVIOR_SOURCE"] == "agy-unit-director"
    assert not any(key.startswith("CODEX_") for key in spec.env)


def test_build_launch_spec_rejects_unknown_agy_mode(tmp_path: Path) -> None:
    config_path = tmp_path / "seats.toml"
    _write_config(config_path)

    with pytest.raises(launcher.LaunchError, match="unsupported AGY mode"):
        launcher.build_launch_spec(
            repo_root=tmp_path,
            git_dir=tmp_path / ".git",
            seat="director",
            settings=launcher.load_seat_settings(config_path),
            inherited_env={},
            agy_executable="/opt/agy",
            forwarded_args=[],
            mode="live-seat",
        )


def test_each_seat_uses_only_its_own_model_and_tier(tmp_path: Path) -> None:
    config_path = tmp_path / "seats.toml"
    _write_config(
        config_path,
        {
            "director": ("gemini-director", "fast"),
            "director2": ("gemini-director2", "default"),
        },
    )
    settings = launcher.load_seat_settings(config_path)

    first = launcher.build_launch_spec(
        tmp_path,
        tmp_path / ".git",
        "director",
        settings,
        {},
        "agy",
        [],
    )
    second = launcher.build_launch_spec(
        tmp_path,
        tmp_path / ".git",
        "director2",
        settings,
        {},
        "agy",
        [],
    )

    assert first.argv[:5] == (
        "agy",
        "--model",
        "gemini-director",
        "--config",
        'service_tier="fast"',
    )
    assert second.argv[:5] == (
        "agy",
        "--model",
        "gemini-director2",
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
            "agy",
            [],
        ).index_path
        for seat in SEATS
    }

    assert len(paths) == len(SEATS)


def test_forwarded_agy_arguments_remain_literal(tmp_path: Path) -> None:
    config_path = tmp_path / "seats.toml"
    _write_config(config_path)
    forwarded = ["prompt with spaces", "'quoted'", ";", "$(touch nope)", "--search"]

    spec = launcher.build_launch_spec(
        tmp_path,
        tmp_path / ".git",
        "operator",
        launcher.load_seat_settings(config_path),
        {},
        "agy",
        forwarded,
    )

    assert spec.argv[-len(forwarded) :] == tuple(forwarded)


@pytest.mark.parametrize(
    "body",
    [
        "[seats.director]\nmodel='gemini'\nservice_tier='default'\n",
        "".join(
            f"[seats.{seat}]\nmodel='gemini'\nservice_tier='turbo'\n"
            for seat in SEATS
        ),
        "".join(
            f"[seats.{seat}]\nmodel='gemini'\nservice_tier='default'\nextra=true\n"
            for seat in SEATS
        ),
        "".join(
            f"[seats.{seat}]\nmodel={1 if seat == 'director' else repr('gemini')}\n"
            "service_tier='default'\n"
            for seat in SEATS
        ),
        "".join(
            f"[seats.{seat}]\nmodel='gemini'\nservice_tier='default'\n"
            for seat in (*SEATS, "extra")
        ),
    ],
)
def test_config_rejects_incomplete_or_unknown_settings(tmp_path: Path, body: str) -> None:
    config_path = tmp_path / "bad.toml"
    config_path.write_text(body, encoding="utf-8")

    with pytest.raises(launcher.ConfigError):
        launcher.load_seat_settings(config_path)


def test_ensure_seat_index_seeds_only_when_missing(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    index_path = tmp_path / ".git" / "index-agy-director"
    calls: list[list[str]] = []
    environments: list[dict[str, str]] = []
    monkeypatch.setenv("GIT_DIR", "/foreign/git")
    monkeypatch.setenv("GIT_WORK_TREE", "/foreign/tree")
    monkeypatch.setenv("GIT_INDEX_FILE", "/foreign/index")

    def fake_run(argv: list[str], **kwargs: object) -> subprocess.CompletedProcess[str]:
        calls.append(argv)
        environments.append(dict(kwargs["env"]))  # type: ignore[arg-type]
        index_path.parent.mkdir()
        index_path.write_text("seed", encoding="utf-8")
        return subprocess.CompletedProcess(argv, 0, "", "")

    launcher.ensure_seat_index(tmp_path, index_path, runner=fake_run)
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
    assert not any(key.startswith("GIT_") for key in environments[0])


def test_resolve_git_dir_discards_all_ambient_git_authority(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    captured: dict[str, str] = {}
    monkeypatch.setenv("GIT_DIR", "/foreign/git")
    monkeypatch.setenv("GIT_WORK_TREE", "/foreign/tree")
    monkeypatch.setenv("GIT_CONFIG_COUNT", "1")
    monkeypatch.setenv("GIT_INDEX_FILE", "/foreign/index")

    def fake_run(_: list[str], **kwargs: object) -> subprocess.CompletedProcess[str]:
        captured.update(kwargs["env"])  # type: ignore[arg-type]
        return subprocess.CompletedProcess([], 0, str(tmp_path / ".git") + "\n", "")

    monkeypatch.setattr(launcher.subprocess, "run", fake_run)

    assert launcher.resolve_git_dir(tmp_path) == tmp_path / ".git"
    assert not any(key.startswith("GIT_") for key in captured)


def test_dry_run_does_not_create_index_or_start_agy(tmp_path: Path, repo_root: Path) -> None:
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
    index_path = git_dir / "index-agy-director"
    index_before = (
        (index_path.stat().st_size, index_path.stat().st_mtime_ns)
        if index_path.exists()
        else None
    )
    marker = tmp_path / "agy-was-run"
    fake_bin = tmp_path / "bin"
    fake_bin.mkdir()
    fake_agy = fake_bin / "agy"
    fake_agy.write_text(f"#!/bin/sh\ntouch '{marker}'\n", encoding="utf-8")
    fake_agy.chmod(0o755)
    env = os.environ.copy()
    env["PATH"] = f"{fake_bin}:{env['PATH']}"

    result = subprocess.run(
        [
            str(repo_root / "coordination" / "bin" / "agy-seat"),
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
    payload = json.loads(result.stdout)
    assert payload["env"]["AGY_SEAT"] == "agy-advisory"
    assert payload["env"]["AGY_AGENT_MODE"] == "advisory-readiness"
    assert payload["env"]["AGY_GIT_INDEX_FILE"] == str(index_path)
    assert not any(key.startswith("CODEX_") for key in payload["env"])
    index_after = (
        (index_path.stat().st_size, index_path.stat().st_mtime_ns)
        if index_path.exists()
        else None
    )
    assert index_after == index_before
    assert not marker.exists()


def test_default_advisory_mode_refuses_provider_launch(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    config_path = tmp_path / "seats.toml"
    _write_config(config_path)
    monkeypatch.setattr(launcher, "resolve_git_dir", lambda _: tmp_path / ".git")
    monkeypatch.setattr(
        launcher.shutil,
        "which",
        lambda _: pytest.fail("advisory mode must not inspect a provider executable"),
    )
    monkeypatch.setattr(
        launcher,
        "ensure_seat_index",
        lambda *_args, **_kwargs: pytest.fail("advisory mode must not create an index"),
    )
    monkeypatch.setattr(
        launcher.os,
        "execvpe",
        lambda *_args, **_kwargs: pytest.fail("advisory mode must not launch AGY"),
    )

    assert launcher.main(["--config", str(config_path), "director"]) == 2
    assert "advisory mode does not launch AGY" in capsys.readouterr().err


def test_continuation_documents_advisory_default_and_stdin_writer(
    repo_root: Path,
) -> None:
    text = (repo_root / "docs/protocol/agy/continuation.md").read_text(
        encoding="utf-8"
    )

    assert "--mode single-model-autonomous" in text
    assert "does not claim a shared Pipeline seat" in text
    assert "coordination/bin/send-event <sender> <recipient> <kind> <subject...> < body.md" in text
    assert "<body-file>" not in text
