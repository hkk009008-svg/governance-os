"""Tests for the local per-seat Codex launcher."""

from __future__ import annotations

import json
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
        "CODEX_HOME": "/preserve-codex-home",
        "CODEX_SEAT": "wrong-seat",
        "CODEX_AGENT_MODE": "wrong-mode",
        "CODEX_AGENT_ROLE": "wrong-role",
        "CODEX_BEHAVIOR_SOURCE": "wrong-source",
        "CODEX_CAPABILITY_MODE": "ambient-capability",
        "CODEX_MUTATION_SCOPE": "ambient-mutation",
        "CODEX_AUTHORITY_SCOPE": "ambient-authority",
        "CODEX_MAILBOX_POLICY": "ambient-mailbox",
        "CODEX_GIT_POLICY": "ambient-git-policy",
        "CODEX_VERIFICATION_POLICY": "ambient-verification",
        "CODEX_CONTEXT_SOURCES": "ambient-context",
        "CODEX_OUTPUT_CONTRACT": "ambient-output",
        "CODEX_DECISION_BOUNDARY": "ambient-decision",
        "CODEX_NEXT_ACTION_POLICY": "ambient-next-action",
        "CODEX_SIDE_EFFECT_POLICY": "ambient-side-effect",
        "GIT_INDEX_FILE": "/wrong-index",
    }

    spec = launcher.build_launch_spec(
        repo_root=tmp_path,
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
    assert spec.identity.model == f"model-{seat}"
    assert spec.env["CODEX_HOME"] == "/preserve-codex-home"
    assert "GIT_INDEX_FILE" not in spec.env
    assert not {
        "CODEX_CAPABILITY_MODE",
        "CODEX_MUTATION_SCOPE",
        "CODEX_AUTHORITY_SCOPE",
        "CODEX_MAILBOX_POLICY",
        "CODEX_GIT_POLICY",
        "CODEX_VERIFICATION_POLICY",
        "CODEX_CONTEXT_SOURCES",
        "CODEX_OUTPUT_CONTRACT",
        "CODEX_DECISION_BOUNDARY",
        "CODEX_NEXT_ACTION_POLICY",
        "CODEX_SIDE_EFFECT_POLICY",
    } & spec.env.keys()


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
        "director",
        settings,
        {},
        "codex",
        [],
    )
    second = launcher.build_launch_spec(
        tmp_path,
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


def test_launch_spec_uses_caller_checkout_native_index(tmp_path: Path) -> None:
    config_path = tmp_path / "seats.toml"
    _write_config(config_path)

    spec = launcher.build_launch_spec(
        tmp_path,
        "director",
        launcher.load_seat_settings(config_path),
        {"GIT_INDEX_FILE": "/ambient/index"},
        "codex",
        [],
    )

    assert spec.repo_root == tmp_path
    assert spec.argv[-2:] == ("--cd", str(tmp_path))
    assert "GIT_INDEX_FILE" not in spec.env
    assert not hasattr(spec, "index_path")
    assert not hasattr(launcher, "ensure_seat_index")


def test_forwarded_codex_arguments_remain_literal(tmp_path: Path) -> None:
    config_path = tmp_path / "seats.toml"
    _write_config(config_path)
    forwarded = ["prompt with spaces", "'quoted'", ";", "$(touch nope)", "--search"]

    spec = launcher.build_launch_spec(
        tmp_path,
        "operator",
        launcher.load_seat_settings(config_path),
        {},
        "codex",
        forwarded,
    )

    assert spec.argv[-len(forwarded) :] == tuple(forwarded)


@pytest.mark.parametrize(
    "forwarded",
    (
        ["--model", "other-model"],
        ["--model=other-model"],
        ["-m", "other-model"],
        ["-mother-model"],
        ["--config", 'approval_policy="never"'],
        ['--config=approval_policy="never"'],
        ["-c", 'approval_policy="never"'],
        ["--cd", "/tmp/other"],
        ["--cd=/tmp/other"],
        ["-C", "/tmp/other"],
        ["--sandbox", "danger-full-access"],
        ["--sandbox=danger-full-access"],
        ["-s", "danger-full-access"],
        ["--ask-for-approval", "never"],
        ["--ask-for-approval=never"],
        ["-a", "never"],
        ["--full-auto"],
        ["--dangerously-bypass-approvals-and-sandbox"],
        ["--dangerously-bypass-hook-trust"],
        ["--enable", "hooks"],
        ["--disable", "approval-prompts"],
        ["--oss"],
        ["--local-provider", "ollama"],
        ["--remote", "ws://127.0.0.1:9999"],
        ["--remote-auth-token-env", "TOKEN"],
        ["--bypass"],
        ["--yolo"],
        ["--profile", "unsafe"],
        ["-p", "unsafe"],
        ["--add-dir", "/tmp/other"],
        ["exec", "--ignore-rules", "--help"],
    ),
)
def test_forwarded_launcher_owned_or_security_flags_are_rejected(
    tmp_path: Path, forwarded: list[str]
) -> None:
    config_path = tmp_path / "seats.toml"
    _write_config(config_path)

    with pytest.raises(launcher.LaunchError, match="may not override"):
        launcher.build_launch_spec(
            tmp_path,
            "operator",
            launcher.load_seat_settings(config_path),
            {},
            "codex",
            forwarded,
        )


def test_forwarded_terminator_cannot_hide_a_security_override(tmp_path: Path) -> None:
    config_path = tmp_path / "seats.toml"
    _write_config(config_path)

    with pytest.raises(launcher.LaunchError, match="may not override"):
        launcher.build_launch_spec(
            tmp_path,
            "operator",
            launcher.load_seat_settings(config_path),
            {},
            "codex",
            ["--", "--sandbox", "danger-full-access"],
        )


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


def test_dry_run_uses_cwd_without_creating_index_or_starting_codex(
    tmp_path: Path, repo_root: Path
) -> None:
    config_path = tmp_path / "seats.toml"
    _write_config(config_path)
    marker = tmp_path / "codex-was-run"
    fake_bin = tmp_path / "bin"
    fake_bin.mkdir()
    fake_codex = fake_bin / "codex"
    fake_codex.write_text(f"#!/bin/sh\ntouch '{marker}'\n", encoding="utf-8")
    fake_codex.chmod(0o755)
    env = os.environ.copy()
    env["PATH"] = f"{fake_bin}:{env['PATH']}"
    env["GIT_INDEX_FILE"] = "/ambient/index"
    env["CODEX_AUTHORITY_SCOPE"] = "ambient-authority"

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
    payload = json.loads(result.stdout)
    assert "unchanged start input" in payload["argv"]
    assert payload["argv"][payload["argv"].index("--cd") + 1] == str(repo_root)
    assert "index_exists" not in payload
    assert "GIT_INDEX_FILE" not in payload["env"]
    assert "CODEX_AUTHORITY_SCOPE" not in payload["env"]
    assert not marker.exists()
