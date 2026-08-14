from __future__ import annotations

import subprocess
from pathlib import Path
from types import SimpleNamespace

import harness_preflight as preflight


def test_codex_check_runs_config_controls_when_binary_is_absent(
    tmp_path: Path, monkeypatch
) -> None:
    monkeypatch.setattr(preflight, "_binary", lambda _name: None)
    config = tmp_path / ".codex/config.toml"
    config.parent.mkdir()
    config.write_text('sandbox_mode = "danger-full-access"\n', encoding="utf-8")

    results = preflight.check_codex(tmp_path)

    assert [result.ok for result in results] == [False, False, True]
    assert "sandbox_mode" in results[1].detail


def test_codex_check_accepts_capability_neutral_project_config(
    tmp_path: Path, monkeypatch
) -> None:
    monkeypatch.setattr(preflight, "_binary", lambda _name: "/bin/codex")
    config = tmp_path / ".codex/config.toml"
    config.parent.mkdir()
    config.write_text(
        'model = "gpt-5.6-sol"\n'
        '[mcp_servers.claude_task_connector]\n'
        'command = "coordination/bin/claude-task-connector"\n'
        'args = ["mcp"]\n'
        'cwd = "."\n',
        encoding="utf-8",
    )

    assert all(result.ok for result in preflight.check_codex(tmp_path))


def test_codex_check_rejects_decoded_ambient_key_and_extra_mcp(
    tmp_path: Path, monkeypatch
) -> None:
    monkeypatch.setattr(preflight, "_binary", lambda _name: "/bin/codex")
    config = tmp_path / ".codex/config.toml"
    config.parent.mkdir()
    config.write_text(
        '"approval\\u005fpolicy" = "never"\n'
        '[mcp_servers.claude_task_connector]\n'
        'command = "coordination/bin/claude-task-connector"\n'
        'args = ["mcp"]\n'
        'cwd = "."\n'
        '[mcp_servers.unreviewed]\ncommand = "arbitrary"\n',
        encoding="utf-8",
    )

    result = preflight.check_codex(tmp_path)[1]
    assert result.ok is False
    assert "approval_policy" in result.detail


def test_codex_check_allows_neutral_nested_features_name(
    tmp_path: Path, monkeypatch
) -> None:
    monkeypatch.setattr(preflight, "_binary", lambda _name: "/bin/codex")
    config = tmp_path / ".codex/config.toml"
    config.parent.mkdir()
    config.write_text(
        '[mcp_servers.claude_task_connector]\n'
        'command = "coordination/bin/claude-task-connector"\n'
        'args = ["mcp"]\n'
        'cwd = "."\n'
        '[mcp_servers.claude_task_connector.features]\nneutral = true\n',
        encoding="utf-8",
    )

    assert preflight.check_codex(tmp_path)[1].ok is True


def test_codex_check_rejects_profile_ambient_authority(
    tmp_path: Path, monkeypatch
) -> None:
    monkeypatch.setattr(preflight, "_binary", lambda _name: "/bin/codex")
    config = tmp_path / ".codex/config.toml"
    config.parent.mkdir()
    config.write_text(
        '[mcp_servers.claude_task_connector]\n'
        'command = "coordination/bin/claude-task-connector"\n'
        'args = ["mcp"]\n'
        'cwd = "."\n'
        '[profiles.loose]\n'
        'approval_policy = "never"\n'
        'sandbox_mode = "danger-full-access"\n',
        encoding="utf-8",
    )

    result = preflight.check_codex(tmp_path)[1]
    assert result.ok is False
    assert "profiles.loose.approval_policy" in result.detail
    assert "profiles.loose.sandbox_mode" in result.detail


def test_codex_check_rejects_mcp_environment_or_other_unreviewed_keys(
    tmp_path: Path, monkeypatch
) -> None:
    monkeypatch.setattr(preflight, "_binary", lambda _name: "/bin/codex")
    config = tmp_path / ".codex/config.toml"
    config.parent.mkdir()
    config.write_text(
        '[mcp_servers.claude_task_connector]\n'
        'command = "coordination/bin/claude-task-connector"\n'
        'args = ["mcp"]\n'
        'cwd = "."\n'
        '[mcp_servers.claude_task_connector.env]\n'
        'PIPELINE_CLAUDE_CONNECTOR_PYTHON = "/tmp/untrusted-python"\n',
        encoding="utf-8",
    )

    result = preflight.check_codex(tmp_path)[1]
    assert result.ok is False
    assert "unsupported keys: env" in result.detail


def test_live_probe_requires_exact_positive_artifact(
    tmp_path: Path, monkeypatch
) -> None:
    expected = f"{tmp_path.resolve()}\nabc1234\n"
    monkeypatch.setattr(preflight, "_git_identity", lambda _root: expected)

    def runner(argv, **kwargs):
        assert argv == [
            "codex", "exec", "-C", str(tmp_path.resolve()),
            "--sandbox", "read-only", "-c", 'approval_policy="never"',
            'Run exactly this command once in the supplied repository and reply with ONLY stdout: "git rev-parse --show-toplevel --short HEAD"',
        ]
        assert kwargs["stdin"] is subprocess.DEVNULL
        assert all(not key.startswith("GIT_") for key in kwargs["env"])
        return SimpleNamespace(returncode=0, stdout=expected, stderr="")

    assert preflight.live_probe(tmp_path, runner=runner).ok is True


def test_live_probe_rejects_exit_zero_with_noncanonical_output(
    tmp_path: Path, monkeypatch
) -> None:
    expected = f"{tmp_path.resolve()}\nabc1234\n"
    monkeypatch.setattr(preflight, "_git_identity", lambda _root: expected)

    result = preflight.live_probe(
        tmp_path,
        runner=lambda *args, **kwargs: SimpleNamespace(
            returncode=0, stdout=expected.rstrip(), stderr=""
        ),
    )

    assert result.ok is False
    assert "no exact positive artifact" in result.detail


def test_main_fails_when_any_capability_check_fails(
    tmp_path: Path, monkeypatch
) -> None:
    monkeypatch.setattr(
        preflight,
        "check_codex",
        lambda _root: [preflight.Result("codex", False, "missing")],
    )

    assert preflight.main(["--repo-root", str(tmp_path)]) == 1
