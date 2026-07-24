from __future__ import annotations

import json
import os
from pathlib import Path
import shutil
import subprocess

from scripts import cursor_app_binding


ROOT = Path(__file__).resolve().parents[2]


def _install(repo: Path) -> None:
    (repo / ".claude/hooks").mkdir(parents=True)
    (repo / "scripts").mkdir()
    for relative in (
        ".claude/hooks/guard-git-index.sh",
        "scripts/cursor_app_binding.py",
        "scripts/cursor_hook_policy.py",
    ):
        target = repo / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(ROOT / relative, target)


def _run_guard(
    repo: Path,
    *,
    tool: str,
    command: str = "",
    conversation_id: str = "",
    model_id: str = "",
    extra_env: dict[str, str] | None = None,
) -> subprocess.CompletedProcess[str]:
    payload = {
        "session_id": "cursor-compatible-session",
        "cwd": str(repo),
        "hook_event_name": "PreToolUse",
        "tool_name": tool,
        "workspace_roots": [str(repo)],
        "tool_input": (
            {"command": command}
            if command
            else {"path": str(repo / "allowed.txt")}
            if tool in {"Write", "Edit"}
            else {}
        ),
    }
    if conversation_id:
        payload["conversation_id"] = conversation_id
    if model_id:
        payload["model_id"] = model_id
    env = os.environ.copy()
    env.pop("CLAUDE_SEAT", None)
    env.pop("GIT_INDEX_FILE", None)
    env["CURSOR_PROJECT_DIR"] = str(repo)
    env["CLAUDE_PROJECT_DIR"] = str(repo)
    env["CURSOR_VERSION"] = "test"
    if extra_env:
        env.update(extra_env)
    return subprocess.run(
        ["/bin/bash", str(repo / ".claude/hooks/guard-git-index.sh")],
        cwd=repo,
        env=env,
        input=json.dumps(payload),
        text=True,
        capture_output=True,
        check=False,
    )


def test_cursor_alias_does_not_bypass_claude_write_guard(tmp_path: Path) -> None:
    repo = tmp_path / "pipeline"
    _install(repo)

    write = _run_guard(repo, tool="Write")
    mutation = _run_guard(repo, tool="Bash", command="touch forbidden.txt")

    assert json.loads(write.stdout)["permission"] == "deny"
    assert json.loads(mutation.stdout)["permission"] == "deny"


def test_cursor_alias_retains_conservative_read_only_subset(tmp_path: Path) -> None:
    repo = tmp_path / "pipeline"
    _install(repo)

    result = _run_guard(repo, tool="Bash", command="pwd")
    assert result.returncode == 0, result.stderr
    assert json.loads(result.stdout)["permission"] == "allow"


def test_cursor_alias_delegates_to_valid_app_seat_policy(tmp_path: Path) -> None:
    repository = tmp_path / "repo"
    repository.mkdir()
    for args in (
        ("init", "-q"),
        ("config", "user.email", "tests@example.invalid"),
        ("config", "user.name", "Tests"),
    ):
        subprocess.run(["git", "-C", str(repository), *args], check=True)
    (repository / "seed.txt").write_text("seed\n", encoding="utf-8")
    subprocess.run(["git", "-C", str(repository), "add", "seed.txt"], check=True)
    subprocess.run(
        ["git", "-C", str(repository), "commit", "-q", "-m", "seed"],
        check=True,
    )
    worktree = tmp_path / "director"
    subprocess.run(
        [
            "git",
            "-C",
            str(repository),
            "worktree",
            "add",
            "-q",
            "-b",
            "cursor-seat/director",
            str(worktree),
        ],
        check=True,
    )
    _install(worktree)
    identity = cursor_app_binding.resolve_worktree_seat(worktree)
    assert identity is not None
    home = tmp_path / "home"
    registry = home / ".cursor/pipeline-app-seats.json"
    active = cursor_app_binding.register_session(
        identity,
        conversation_id="director-conversation",
        model_id="composer-2.5",
        registry_path=registry,
    )
    env = cursor_app_binding.session_environment(active)
    env["HOME"] = str(home)

    result = _run_guard(
        worktree,
        tool="Write",
        conversation_id=active.conversation_id,
        model_id=active.model_id,
        extra_env=env,
    )

    assert result.returncode == 0, result.stderr
    assert json.loads(result.stdout)["permission"] == "allow"
