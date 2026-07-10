from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

import pytest


def test_codex_hooks_keep_commands_without_success_status_messages(
    repo_root: Path,
):
    config = json.loads(
        (repo_root / ".codex/hooks.json").read_text(encoding="utf-8")
    )
    commands = [
        hook
        for registrations in config["hooks"].values()
        for registration in registrations
        for hook in registration["hooks"]
    ]

    assert len(commands) == 3
    assert all("command" in hook for hook in commands)
    assert all("statusMessage" not in hook for hook in commands)
    assert any("session-smoke.sh" in hook["command"] for hook in commands)
    assert any("guard-git-index.sh" in hook["command"] for hook in commands)
    assert any("update-state.sh" in hook["command"] for hook in commands)


def _run(
    args: list[str | Path],
    cwd: Path,
    *,
    env: dict[str, str] | None = None,
) -> subprocess.CompletedProcess[str]:
    full_env = os.environ.copy()
    full_env.pop("GIT_INDEX_FILE", None)
    if env:
        full_env.update(env)
    return subprocess.run(
        [str(arg) for arg in args],
        cwd=cwd,
        env=full_env,
        text=True,
        capture_output=True,
        check=False,
    )


def _git(
    repo: Path,
    *args: str,
    env: dict[str, str] | None = None,
) -> str:
    result = _run(["git", *args], repo, env=env)
    assert result.returncode == 0, result.stderr
    return result.stdout.strip()


def _init_repo(repo: Path) -> None:
    _git(repo, "init", "-q")
    _git(repo, "config", "user.email", "test@example.com")
    _git(repo, "config", "user.name", "Test User")


def _install_smoke_hook_repo(repo: Path, repo_root: Path) -> Path:
    _init_repo(repo)
    hook_dir = repo / ".codex/hooks"
    hook_dir.mkdir(parents=True)
    hook = hook_dir / "session-smoke.sh"
    shutil.copy2(repo_root / ".codex/hooks/session-smoke.sh", hook)

    python_dir = repo / ".venv/bin"
    python_dir.mkdir(parents=True)
    (python_dir / "python").symlink_to(sys.executable)

    scripts = repo / "scripts"
    scripts.mkdir()
    (scripts / "ci_smoke.py").write_text(
        "import os\n"
        "from pathlib import Path\n"
        "counter = Path('.smoke-runs')\n"
        "count = int(counter.read_text() or '0') if counter.exists() else 0\n"
        "counter.write_text(str(count + 1))\n"
        "Path('.smoke-index-env').write_text(os.environ.get('GIT_INDEX_FILE', ''))\n"
        "if Path('.force-smoke-fail').exists():\n"
        "    raise SystemExit(1)\n"
        "print('OK')\n",
        encoding="utf-8",
    )
    (repo / "AGENTS.md").write_text("initial\n", encoding="utf-8")
    (repo / "ARCHITECTURE.md").write_text("initial\n", encoding="utf-8")
    (repo / ".codex/hooks.json").write_text("{}\n", encoding="utf-8")
    (repo / ".gitignore").write_text(
        ".codex/hooks/.last-smoke-pass\n.smoke-runs\n.smoke-index-env\n",
        encoding="utf-8",
    )
    _git(repo, "add", ".")
    _git(repo, "commit", "-q", "-m", "baseline")
    return hook


def test_session_smoke_caches_pass_by_governance_content(
    tmp_path: Path,
    repo_root: Path,
):
    repo = tmp_path / "repo"
    repo.mkdir()
    hook = _install_smoke_hook_repo(repo, repo_root)

    first = _run([hook], repo)

    assert first.returncode == 0, first.stderr
    assert first.stdout == ""
    assert (repo / ".smoke-runs").read_text(encoding="utf-8") == "1"

    second = _run([hook], repo)

    assert second.returncode == 0, second.stderr
    assert second.stdout == ""
    assert (repo / ".smoke-runs").read_text(encoding="utf-8") == "1"

    mailbox = repo / "coordination/mailbox"
    mailbox.mkdir(parents=True)
    (mailbox / "kinds.txt").write_text("changed\n", encoding="utf-8")
    third = _run([hook], repo)

    assert third.returncode == 0, third.stderr
    assert third.stdout == ""
    assert (repo / ".smoke-runs").read_text(encoding="utf-8") == "2"


def test_session_smoke_unsets_ambient_git_index(
    tmp_path: Path,
    repo_root: Path,
):
    repo = tmp_path / "repo"
    repo.mkdir()
    hook = _install_smoke_hook_repo(repo, repo_root)

    result = _run(
        [hook],
        repo,
        env={"GIT_INDEX_FILE": str(tmp_path / "ambient-seat-index")},
    )

    assert result.returncode == 0, result.stderr
    assert (repo / ".smoke-index-env").read_text(encoding="utf-8") == ""


def test_session_smoke_never_caches_failure(
    tmp_path: Path,
    repo_root: Path,
):
    repo = tmp_path / "repo"
    repo.mkdir()
    hook = _install_smoke_hook_repo(repo, repo_root)
    (repo / ".force-smoke-fail").write_text("fail\n", encoding="utf-8")

    first = _run([hook], repo)
    second = _run([hook], repo)

    assert first.returncode == 0
    assert second.returncode == 0
    assert "smoke FAILED or timed out" in first.stdout
    assert "smoke FAILED or timed out" in second.stdout
    assert (repo / ".smoke-runs").read_text(encoding="utf-8") == "2"
    assert not (repo / ".codex/hooks/.last-smoke-pass").exists()


@pytest.mark.parametrize(
    "index_flag",
    ["--skip-worktree", "--assume-unchanged"],
)
def test_session_smoke_bypasses_cache_for_hidden_index_flags(
    tmp_path: Path,
    repo_root: Path,
    index_flag: str,
):
    repo = tmp_path / "repo"
    repo.mkdir()
    hook = _install_smoke_hook_repo(repo, repo_root)
    first = _run([hook], repo)
    assert first.returncode == 0, first.stderr
    assert (repo / ".smoke-runs").read_text(encoding="utf-8") == "1"

    _git(repo, "update-index", index_flag, "AGENTS.md")
    (repo / "AGENTS.md").write_text("hidden change\n", encoding="utf-8")
    second = _run([hook], repo)

    assert second.returncode == 0, second.stderr
    assert (repo / ".smoke-runs").read_text(encoding="utf-8") == "2"


def _install_update_state_hook_repo(repo: Path, repo_root: Path) -> Path:
    _init_repo(repo)
    hook_dir = repo / ".codex/hooks"
    hook_dir.mkdir(parents=True)
    hook = hook_dir / "update-state.sh"
    shutil.copy2(repo_root / ".codex/hooks/update-state.sh", hook)

    (repo / "coordination/mailbox/sent").mkdir(parents=True)
    (repo / "coordination/mailbox/seen").mkdir()
    (repo / "coordination/presence").mkdir()
    (repo / "tracked.txt").write_text("tracked\n", encoding="utf-8")
    _git(repo, "add", ".")
    _git(repo, "commit", "-q", "-m", "baseline")

    head = _git(repo, "rev-parse", "HEAD")
    (hook_dir / ".last-state-head").write_text(f"{head}\n", encoding="utf-8")
    (repo / "STATE.md").write_text("cached state\n", encoding="utf-8")
    return hook


def _skip_worktree_paths(
    repo: Path,
    *,
    env: dict[str, str] | None = None,
) -> list[str]:
    lines = _git(repo, "ls-files", "-v", env=env).splitlines()
    return [line[2:] for line in lines if line.startswith("S ")]


def test_update_state_bridge_fast_path_preserves_index_state_and_lock(
    tmp_path: Path,
    repo_root: Path,
):
    repo = tmp_path / "repo"
    repo.mkdir()
    hook = _install_update_state_hook_repo(repo, repo_root)
    _git(repo, "update-index", "--skip-worktree", "tracked.txt")
    head = _git(repo, "rev-parse", "HEAD")
    (repo / ".codex/hooks/.last-skip-worktree-scan-default").write_text(
        f"{head} {int(time.time())}\n",
        encoding="utf-8",
    )
    index_lock = repo / ".git/index.lock"
    index_lock.write_text("active-or-unknown\n", encoding="utf-8")
    os.utime(index_lock, (0, 0))

    result = _run([hook], repo)

    assert result.returncode == 0, result.stderr
    assert _skip_worktree_paths(repo) == ["tracked.txt"]
    assert index_lock.exists()


def test_update_state_bridge_repairs_when_default_scan_is_due(
    tmp_path: Path,
    repo_root: Path,
):
    repo = tmp_path / "repo"
    repo.mkdir()
    hook = _install_update_state_hook_repo(repo, repo_root)
    _git(repo, "update-index", "--skip-worktree", "tracked.txt")

    result = _run([hook], repo)

    assert result.returncode == 0, result.stderr
    assert _skip_worktree_paths(repo) == []


def test_update_state_live_seat_throttles_scan_then_repairs_when_due(
    tmp_path: Path,
    repo_root: Path,
):
    repo = tmp_path / "repo"
    repo.mkdir()
    hook = _install_update_state_hook_repo(repo, repo_root)
    _git(repo, "update-index", "--skip-worktree", "tracked.txt")
    head = _git(repo, "rev-parse", "HEAD")
    scan_marker = repo / ".codex/hooks/.last-skip-worktree-scan-default"
    scan_marker.write_text(f"{head} {int(time.time())}\n", encoding="utf-8")

    throttled = _run([hook], repo, env={"CODEX_SEAT": "director"})

    assert throttled.returncode == 0, throttled.stderr
    assert _skip_worktree_paths(repo) == ["tracked.txt"]
    heartbeat = repo / "coordination/presence/director-heartbeat.ts"
    assert heartbeat.exists()

    scan_marker.write_text(f"{head} 0\n", encoding="utf-8")
    due = _run([hook], repo, env={"CODEX_SEAT": "director"})

    assert due.returncode == 0, due.stderr
    assert _skip_worktree_paths(repo) == []


def test_update_state_scan_throttle_is_scoped_to_each_seat_index(
    tmp_path: Path,
    repo_root: Path,
):
    repo = tmp_path / "repo"
    repo.mkdir()
    hook = _install_update_state_hook_repo(repo, repo_root)
    director_index = repo / ".git/index-director"
    operator_index = repo / ".git/index-operator"
    _git(repo, "read-tree", f"--index-output={director_index}", "HEAD")
    _git(repo, "read-tree", f"--index-output={operator_index}", "HEAD")
    director_scan = _run(
        [hook],
        repo,
        env={
            "CODEX_SEAT": "director",
            "GIT_INDEX_FILE": str(director_index),
        },
    )
    assert director_scan.returncode == 0, director_scan.stderr

    _git(
        repo,
        "update-index",
        "--skip-worktree",
        "tracked.txt",
        env={"GIT_INDEX_FILE": str(operator_index)},
    )

    result = _run(
        [hook],
        repo,
        env={
            "CODEX_SEAT": "operator",
            "GIT_INDEX_FILE": str(operator_index),
        },
    )

    assert result.returncode == 0, result.stderr
    assert _skip_worktree_paths(
        repo, env={"GIT_INDEX_FILE": str(operator_index)}
    ) == []
