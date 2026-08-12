"""git_runner: one Git environment policy, containment by construction."""

from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

import git_runner
from threeway import gitcas

ROOT = Path(__file__).resolve().parents[2]


def _init_repo(repo: Path) -> None:
    subprocess.run(["git", "init", "-q", str(repo)], check=True)


def test_authority_env_is_hermetic(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("GIT_DIR", "/tmp/evil-git-dir")
    monkeypatch.setenv("GIT_INDEX_FILE", "/tmp/evil-index")
    monkeypatch.setenv("SSH_AUTH_SOCK", "/tmp/agent.sock")
    env = git_runner.authority_env(tmp_path)
    assert "GIT_DIR" not in env
    assert "GIT_INDEX_FILE" not in env
    assert "SSH_AUTH_SOCK" not in env
    assert env["GIT_CONFIG_NOSYSTEM"] == "1"
    assert env["GIT_CEILING_DIRECTORIES"] == str(tmp_path.resolve().parent)


def test_dashboard_env_keeps_credentials_and_strips_retargeting(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("GIT_DIR", "/tmp/evil-git-dir")
    monkeypatch.setenv("GIT_WORK_TREE", "/tmp/evil-tree")
    monkeypatch.setenv("SSH_AUTH_SOCK", "/tmp/agent.sock")
    env = git_runner.dashboard_env(tmp_path)
    assert "GIT_DIR" not in env
    assert "GIT_WORK_TREE" not in env
    assert env["SSH_AUTH_SOCK"] == "/tmp/agent.sock"
    assert env["GIT_CEILING_DIRECTORIES"] == str(tmp_path.resolve().parent)


@pytest.mark.parametrize("mode", ("authority", "dashboard"))
def test_run_git_answers_for_the_named_root_only(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, mode: str
) -> None:
    # The guarantee belongs to the runner itself, so drop any ambient
    # ceiling the test session installed.
    monkeypatch.delenv("GIT_CEILING_DIRECTORIES", raising=False)
    _init_repo(tmp_path)
    scratch = tmp_path / "scratch"
    scratch.mkdir()

    at_root = git_runner.run_git(
        tmp_path, ["rev-parse", "--is-inside-work-tree"], mode=mode, text=True
    )
    assert at_root.returncode == 0
    assert at_root.stdout.strip() == "true"

    # A root that is not itself a repository must answer "not a repository",
    # never the enclosing checkout's facts.
    inside = git_runner.run_git(
        scratch, ["rev-parse", "--is-inside-work-tree"], mode=mode, text=True
    )
    assert inside.returncode != 0


def test_run_git_rejects_unknown_mode(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="unknown git_runner mode"):
        git_runner.run_git(tmp_path, ["status"], mode="casual")


def test_gitcas_env_strips_every_retargeting_variable(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    for name in git_runner.RETARGETING_GIT_VARS:
        monkeypatch.setenv(name, "/tmp/evil")
    env = gitcas._env()
    for name in git_runner.RETARGETING_GIT_VARS:
        assert name not in env, name
    # The mirrored list must not drift from the canonical one.
    assert set(gitcas._RETARGETING_GIT_VARS) == set(git_runner.RETARGETING_GIT_VARS)


@pytest.mark.parametrize(
    "relative",
    ("coordination/bin/claim-lock", "coordination/bin/release-lock"),
)
def test_lock_scripts_strip_repo_retargeting_variables(relative: str) -> None:
    # The lock scripts strip the repo-retargeting set but deliberately keep
    # the config-selection variables: those carry credential-helper
    # configuration for the push, and tests inject hermetic identity
    # through them.
    text = (ROOT / relative).read_text(encoding="utf-8")
    for name in git_runner.REPO_RETARGETING_GIT_VARS:
        assert name in text, (relative, name)
    for name in git_runner.CONFIG_GIT_VARS:
        assert name not in text, (relative, name)
    assert 'unset "$retarget_var"' in text