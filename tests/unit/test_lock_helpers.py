"""Hermetic controls for the Git-native cross-cutting lock helpers."""
from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[2]
CLAIM = ROOT / "coordination/bin/claim-lock"
RELEASE = ROOT / "coordination/bin/release-lock"


def _lock_path(wave: str, module: str) -> str:
    return f"coordination/locks/{wave}-m-{module.encode('ascii').hex()}.lock"


def _env() -> dict[str, str]:
    env = {key: value for key, value in os.environ.items() if key != "GIT_INDEX_FILE"}
    env["GIT_CONFIG_GLOBAL"] = os.devnull
    env["GIT_CONFIG_SYSTEM"] = os.devnull
    return env


def _git(repo: Path, *args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", "-C", str(repo), *args],
        check=check,
        capture_output=True,
        text=True,
        env=_env(),
        timeout=15,
    )


def _run(
    repo: Path,
    script: Path,
    *args: str,
    env: dict[str, str] | None = None,
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [str(script), *args],
        cwd=repo,
        capture_output=True,
        text=True,
        env=env or _env(),
        timeout=20,
    )


def _ack_lost_env(tmp_path: Path) -> dict[str, str]:
    """A git shim that applies a successful push, then loses its acknowledgement."""

    real_git = shutil.which("git")
    assert real_git is not None
    shim_dir = tmp_path / "git-shim"
    shim_dir.mkdir()
    shim = shim_dir / "git"
    shim.write_text(
        "#!/bin/sh\n"
        "if [ \"$1\" = push ]; then\n"
        f"  {real_git!r} \"$@\"\n"
        "  status=$?\n"
        "  if [ \"$status\" -eq 0 ]; then exit 1; fi\n"
        "  exit \"$status\"\n"
        "fi\n"
        f"exec {real_git!r} \"$@\"\n",
        encoding="utf-8",
    )
    shim.chmod(0o755)
    env = _env()
    env["PATH"] = f"{shim_dir}{os.pathsep}{env['PATH']}"
    return env


def _push_rejected_then_fetch_lost_env(tmp_path: Path) -> dict[str, str]:
    """Reject the push and make only its reconciliation fetch unavailable."""

    real_git = shutil.which("git")
    assert real_git is not None
    shim_dir = tmp_path / "git-reject-shim"
    shim_dir.mkdir()
    flag = shim_dir / "fail-next-fetch"
    shim = shim_dir / "git"
    shim.write_text(
        "#!/bin/sh\n"
        "if [ \"$1\" = push ]; then\n"
        f"  touch {str(flag)!r}\n"
        "  exit 1\n"
        "fi\n"
        f"if [ \"$1\" = fetch ] && [ -f {str(flag)!r} ]; then\n"
        f"  rm -f {str(flag)!r}\n"
        "  exit 1\n"
        "fi\n"
        f"exec {real_git!r} \"$@\"\n",
        encoding="utf-8",
    )
    shim.chmod(0o755)
    env = _env()
    env["PATH"] = f"{shim_dir}{os.pathsep}{env['PATH']}"
    return env


@pytest.fixture
def lock_repo(tmp_path: Path) -> tuple[Path, Path]:
    remote = tmp_path / "remote.git"
    repo = tmp_path / "repo"
    _git(tmp_path, "init", "--bare", str(remote))
    repo.mkdir()
    _git(repo, "init", "-b", "main")
    _git(repo, "config", "user.name", "Lock Test")
    _git(repo, "config", "user.email", "lock@example.invalid")
    (repo / "coordination/locks").mkdir(parents=True)
    (repo / "coordination/locks/.gitkeep").write_text("", encoding="utf-8")
    (repo / ".gitignore").write_text(
        "coordination/locks/*\n!coordination/locks/.gitkeep\n", encoding="utf-8"
    )
    (repo / "README.md").write_text("fixture\n", encoding="utf-8")
    _git(repo, "add", ".gitignore", "README.md", "coordination/locks/.gitkeep")
    _git(repo, "commit", "-m", "fixture")
    _git(repo, "remote", "add", "origin", str(remote))
    _git(repo, "push", "-u", "origin", "main")
    return repo, remote


def _reject_pushes(remote: Path) -> None:
    hook = remote / "hooks/pre-receive"
    hook.write_text("#!/bin/sh\nexit 1\n", encoding="utf-8")
    hook.chmod(0o755)


def test_claim_collision_and_holder_checked_release(
    lock_repo: tuple[Path, Path],
) -> None:
    repo, remote = lock_repo
    lock = _lock_path("w1", "src/module.py")

    claimed = _run(repo, CLAIM, "w1", "src/module.py", "director", "DEF-1")
    assert claimed.returncode == 0, claimed.stderr
    assert _git(remote, "show", f"refs/heads/main:{lock}").stdout.startswith(
        "director w1 "
    )
    assert _git(remote, "show", f"refs/heads/main:{lock}").stdout.rstrip().endswith(
        "DEF-1 src/module.py"
    )

    collision = _run(repo, CLAIM, "w1", "src/module.py", "operator", "DEF-2")
    assert collision.returncode == 1
    assert "already held" in collision.stderr

    unauthorized = _run(repo, RELEASE, "w1", "src/module.py", "operator")
    assert unauthorized.returncode == 1
    assert "held by director" in unauthorized.stderr
    assert (repo / lock).exists()

    released = _run(repo, RELEASE, "w1", "src/module.py", "director")
    assert released.returncode == 0, released.stderr
    assert _git(remote, "cat-file", "-e", f"refs/heads/main:{lock}", check=False).returncode != 0
    assert _git(repo, "status", "--porcelain").stdout == ""


def test_distinct_modules_cannot_alias_one_lock_path(
    lock_repo: tuple[Path, Path],
) -> None:
    repo, remote = lock_repo
    first_module = "src/a/b.py"
    second_module = "src/a__b.py"
    first = _lock_path("w1", first_module)
    second = _lock_path("w1", second_module)
    assert first != second

    assert _run(repo, CLAIM, "w1", first_module, "director", "DEF-1").returncode == 0
    assert _run(repo, CLAIM, "w1", second_module, "director", "DEF-2").returncode == 0
    assert _git(remote, "cat-file", "-e", f"refs/heads/main:{first}").returncode == 0
    assert _git(remote, "cat-file", "-e", f"refs/heads/main:{second}").returncode == 0

    assert _run(repo, RELEASE, "w1", first_module, "director").returncode == 0
    assert _git(remote, "cat-file", "-e", f"refs/heads/main:{first}", check=False).returncode != 0
    assert _git(remote, "cat-file", "-e", f"refs/heads/main:{second}").returncode == 0


@pytest.mark.parametrize(
    "args",
    (
        ("../escape", "src/module.py", "director", "DEF-1"),
        ("w1", "../module.py", "director", "DEF-1"),
        ("w1", "src//module.py", "director", "DEF-1"),
        ("w1", "src/module.py", "bad\nseat", "DEF-1"),
        ("w1", "src/module.py", "director", "DEF 1"),
    ),
)
def test_claim_rejects_unsafe_identifiers_before_writing(
    lock_repo: tuple[Path, Path], args: tuple[str, str, str, str]
) -> None:
    repo, _ = lock_repo
    before = _git(repo, "rev-parse", "HEAD").stdout

    result = _run(repo, CLAIM, *args)

    assert result.returncode == 2
    assert _git(repo, "rev-parse", "HEAD").stdout == before
    assert list((repo / "coordination/locks").glob("*.lock")) == []


def test_claim_refuses_dirty_tree_without_touching_the_change(
    lock_repo: tuple[Path, Path],
) -> None:
    repo, _ = lock_repo
    readme = repo / "README.md"
    readme.write_text("user work\n", encoding="utf-8")
    before = _git(repo, "rev-parse", "HEAD").stdout

    result = _run(repo, CLAIM, "w1", "src/module.py", "director", "DEF-1")

    assert result.returncode == 1
    assert "clean worktree" in result.stderr
    assert readme.read_text(encoding="utf-8") == "user work\n"
    assert _git(repo, "rev-parse", "HEAD").stdout == before


def test_rejected_claim_push_rolls_back_only_the_claim(
    lock_repo: tuple[Path, Path],
) -> None:
    repo, remote = lock_repo
    before = _git(repo, "rev-parse", "HEAD").stdout
    _reject_pushes(remote)

    result = _run(repo, CLAIM, "w1", "src/module.py", "director", "DEF-1")

    assert result.returncode == 1
    assert _git(repo, "rev-parse", "HEAD").stdout == before
    assert _git(repo, "status", "--porcelain").stdout == ""
    assert not (repo / _lock_path("w1", "src/module.py")).exists()


def test_rejected_release_push_restores_the_exact_lock(
    lock_repo: tuple[Path, Path],
) -> None:
    repo, remote = lock_repo
    assert _run(
        repo, CLAIM, "w1", "src/module.py", "director", "DEF-1"
    ).returncode == 0
    lock = repo / _lock_path("w1", "src/module.py")
    original = lock.read_bytes()
    before = _git(repo, "rev-parse", "HEAD").stdout
    _reject_pushes(remote)

    result = _run(repo, RELEASE, "w1", "src/module.py", "director")

    assert result.returncode == 1
    assert _git(repo, "rev-parse", "HEAD").stdout == before
    assert _git(repo, "status", "--porcelain").stdout == ""
    assert lock.read_bytes() == original


def test_claim_recovers_when_remote_accepted_but_acknowledgement_was_lost(
    lock_repo: tuple[Path, Path], tmp_path: Path
) -> None:
    repo, remote = lock_repo
    lock = _lock_path("w1", "src/module.py")

    result = _run(
        repo,
        CLAIM,
        "w1",
        "src/module.py",
        "director",
        "DEF-1",
        env=_ack_lost_env(tmp_path),
    )

    assert result.returncode == 0, result.stderr
    assert "acknowledgement was lost" in result.stdout
    assert _git(remote, "cat-file", "-e", f"refs/heads/main:{lock}").returncode == 0
    assert (repo / lock).is_file()
    assert _git(repo, "status", "--porcelain").stdout == ""


def test_release_recovers_when_remote_accepted_but_acknowledgement_was_lost(
    lock_repo: tuple[Path, Path], tmp_path: Path
) -> None:
    repo, remote = lock_repo
    lock = _lock_path("w1", "src/module.py")
    assert _run(
        repo, CLAIM, "w1", "src/module.py", "director", "DEF-1"
    ).returncode == 0

    result = _run(
        repo,
        RELEASE,
        "w1",
        "src/module.py",
        "director",
        env=_ack_lost_env(tmp_path),
    )

    assert result.returncode == 0, result.stderr
    assert "acknowledgement was lost" in result.stdout
    assert _git(
        remote, "cat-file", "-e", f"refs/heads/main:{lock}", check=False
    ).returncode != 0
    assert not (repo / lock).exists()
    assert _git(repo, "status", "--porcelain").stdout == ""


def test_unknown_rejected_release_cannot_retry_as_false_success(
    lock_repo: tuple[Path, Path], tmp_path: Path
) -> None:
    repo, remote = lock_repo
    lock = _lock_path("w1", "src/module.py")
    assert _run(
        repo, CLAIM, "w1", "src/module.py", "director", "DEF-1"
    ).returncode == 0

    unknown = _run(
        repo,
        RELEASE,
        "w1",
        "src/module.py",
        "director",
        env=_push_rejected_then_fetch_lost_env(tmp_path),
    )
    retry = _run(repo, RELEASE, "w1", "src/module.py", "director")

    assert unknown.returncode == 3
    assert "UNKNOWN" in unknown.stderr
    assert retry.returncode == 1
    assert "exactly match" in retry.stderr
    assert _git(remote, "cat-file", "-e", f"refs/heads/main:{lock}").returncode == 0


def test_claim_refuses_to_publish_unrelated_local_commits(
    lock_repo: tuple[Path, Path],
) -> None:
    repo, remote = lock_repo
    (repo / "README.md").write_text("unrelated local work\n", encoding="utf-8")
    _git(repo, "add", "README.md")
    _git(repo, "commit", "-m", "local unrelated commit")
    local_head = _git(repo, "rev-parse", "HEAD").stdout.strip()

    result = _run(repo, CLAIM, "w1", "src/module.py", "director", "DEF-1")

    assert result.returncode == 1
    assert "exactly match" in result.stderr
    assert _git(remote, "merge-base", "--is-ancestor", local_head, "main", check=False).returncode != 0
    assert _git(
        remote,
        "cat-file",
        "-e",
        f"refs/heads/main:{_lock_path('w1', 'src/module.py')}",
        check=False,
    ).returncode != 0


def test_claim_rejects_broken_symlink_without_following_it(
    lock_repo: tuple[Path, Path], tmp_path: Path
) -> None:
    repo, _ = lock_repo
    relative = _lock_path("w1", "src/module.py")
    lock = repo / relative
    outside = tmp_path / "outside-lock-target"
    lock.symlink_to(outside)
    _git(repo, "add", "-f", relative)
    _git(repo, "commit", "-m", "tracked broken lock symlink")
    _git(repo, "push", "origin", "main")

    result = _run(repo, CLAIM, "w1", "src/module.py", "director", "DEF-1")

    assert result.returncode == 1
    assert "already held" in result.stderr
    assert lock.is_symlink()
    assert not outside.exists()
    assert _git(repo, "status", "--porcelain").stdout == ""
