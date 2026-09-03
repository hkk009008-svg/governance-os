from __future__ import annotations

import subprocess
from pathlib import Path

import cli


ROOT = Path(__file__).resolve().parents[2]


def run(*arguments: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [ROOT / "bin/pipeline", *arguments],
        cwd=ROOT,
        capture_output=True,
        text=True,
        check=False,
    )


def test_help_lists_only_live_commands() -> None:
    result = run("--help")
    assert result.returncode == 0
    assert "team" in result.stdout and "mail send" in result.stdout
    for retired in ("doctor", "checkpoint", "learn", "claim", "ceremony"):
        assert retired not in result.stdout


def test_longest_prefix_dispatch_keeps_team_subcommands() -> None:
    resolved = cli._resolve(["team", "serve", "--member", "codex"])
    assert resolved is not None
    key, target, rest = resolved
    assert key == ("team",)
    assert target[:2] == ("team", "main")
    assert rest == ["serve", "--member", "codex"]


def test_unknown_command_is_a_usage_error() -> None:
    result = run("retired")
    assert result.returncode == 2
    assert "unknown command" in result.stderr


def test_live_subcommands_answer_help_without_running() -> None:
    for arguments in (("check", "--help"), ("review", "request", "--help"), ("mail", "send", "--help")):
        result = run(*arguments)
        assert result.returncode == 0, result.stderr
        assert "usage:" in result.stdout.lower()


def test_review_request_help_names_required_stdin_outcome() -> None:
    result = run("review", "request", "--help")
    assert result.returncode == 0
    assert "required Outcome text is read from stdin" in result.stdout
