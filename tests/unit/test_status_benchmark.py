from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

import status_benchmark


PROJECT_ROOT = Path(status_benchmark.__file__).resolve().parent.parent


def _git(root: Path, *arguments: str) -> str:
    return subprocess.run(
        ["/usr/bin/git", *arguments],
        cwd=root,
        text=True,
        capture_output=True,
        check=True,
    ).stdout.strip()


def _repo(path: Path, *, reflog: bool = True) -> Path:
    path.mkdir()
    _git(path, "init", "-q", "-b", "main")
    _git(path, "config", "user.email", "benchmark@example.invalid")
    _git(path, "config", "user.name", "Benchmark Test")
    if not reflog:
        _git(path, "config", "core.logAllRefUpdates", "false")
    (path / "tracked.txt").write_text("tracked\n", encoding="utf-8")
    (path / "README.md").write_text("readme\n", encoding="utf-8")
    _git(path, "add", "tracked.txt", "README.md")
    _git(path, "commit", "-q", "-m", "base")
    return path


def _production_repo(path: Path) -> Path:
    subprocess.run(
        [
            "/usr/bin/git",
            "clone",
            "--quiet",
            "--shared",
            str(PROJECT_ROOT),
            str(path),
        ],
        capture_output=True,
        check=True,
    )
    return path


def test_benchmark_reports_direct_process_counts_and_schema(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    root = _repo(tmp_path / "repo")
    head = _git(root, "rev-parse", "HEAD")

    def snapshot(repo_root: Path, seat: str) -> dict:
        subprocess.run(
            ["/usr/bin/git", "rev-parse", "HEAD"],
            cwd=repo_root,
            capture_output=True,
            check=True,
        )
        process = subprocess.Popen(
            ["/usr/bin/git", "rev-parse", "HEAD"],
            cwd=repo_root,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        process.communicate()
        return {
            "gate": {
                "status": "PASS",
                "fatal": 0,
                "advisory": 0,
                "failed_review": 0,
            },
            "git": {"sha": head[:7], "dirty": 0},
            "projection": {"head": head},
            "seat": seat,
        }

    monkeypatch.setattr(status_benchmark.status, "collect_orientation_snapshot", snapshot)
    report = status_benchmark.benchmark(root, runs=3, seat="coordinator")

    assert report["schema_version"] == "status-benchmark/v1"
    assert report["repository"] == {
        "root": str(root),
        "head": _git(root, "rev-parse", "HEAD"),
        "observed_clean_at_all_checkpoints": True,
        "observation_boundaries": [
            "setup and each pre-run: full HEAD, porcelain status, HEAD reflog signal",
            "snapshot collect_git: unambiguous SHA prefix and typed integer dirty count",
            "snapshot committed projection: exact full HEAD",
            "each post-run and final: full HEAD, porcelain status, HEAD reflog signal",
        ],
        "limitation": (
            "same-user mutation introduced and restored wholly between every "
            "consumed checkpoint is not detectable"
        ),
    }
    assert report["parameters"] == {"runs": 3, "seat": "coordinator"}
    assert report["processes"] == {
        "per_run": [2, 2, 2],
        "git_per_run": [2, 2, 2],
        "repeated_run_process_count_stable": True,
    }
    assert report["timing_seconds"]["p95_nearest_rank"] == max(
        report["timing_seconds"]["per_run"]
    )


def test_benchmark_refuses_dirty_worktree(tmp_path: Path) -> None:
    root = _repo(tmp_path / "repo")
    (root / "untracked.txt").write_text("dirty\n", encoding="utf-8")

    with pytest.raises(RuntimeError, match="refuses a dirty worktree"):
        status_benchmark.benchmark(root, runs=2)


def test_benchmark_refuses_vacuous_single_run(tmp_path: Path) -> None:
    root = _repo(tmp_path / "repo")

    with pytest.raises(ValueError, match="at least 2"):
        status_benchmark.benchmark(root, runs=1)


def test_benchmark_rejects_transient_head_move_restored_within_run(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    root = _repo(tmp_path / "repo")
    head = _git(root, "rev-parse", "HEAD")
    snapshot_calls = 0

    def transient_snapshot(repo_root: Path, _seat: str) -> dict:
        nonlocal snapshot_calls
        snapshot_calls += 1
        if snapshot_calls > 1:
            raise AssertionError("benchmark continued after per-run identity drift")
        _git(repo_root, "commit", "--allow-empty", "-q", "-m", "transient B")
        _git(repo_root, "reset", "--hard", "-q", head)
        return {"gate": {"fatal": 0}, "projection": {"head": head}}

    monkeypatch.setattr(
        status_benchmark.status,
        "collect_orientation_snapshot",
        transient_snapshot,
    )

    with pytest.raises(RuntimeError, match="changed during benchmark run"):
        status_benchmark.benchmark(root, runs=2)
    assert snapshot_calls == 1


def test_benchmark_rejects_snapshot_from_another_head(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    root = _repo(tmp_path / "repo")

    monkeypatch.setattr(
        status_benchmark.status,
        "collect_orientation_snapshot",
        lambda _root, _seat: {
            "gate": {"fatal": 0},
            "git": {
                "sha": _git(root, "rev-parse", "--short", "HEAD"),
                "dirty": 0,
            },
            "projection": {"head": "f" * 40},
        },
    )

    with pytest.raises(RuntimeError, match="projection HEAD"):
        status_benchmark.benchmark(root, runs=2)


def test_benchmark_rejects_untyped_snapshot_clean_observation(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    root = _repo(tmp_path / "repo")
    head = _git(root, "rev-parse", "HEAD")
    monkeypatch.setattr(
        status_benchmark.status,
        "collect_orientation_snapshot",
        lambda _root, _seat: {
            "gate": {"fatal": 0},
            "git": {"sha": head[:7], "dirty": False},
            "projection": {"head": head},
        },
    )

    with pytest.raises(RuntimeError, match="typed integer zero"):
        status_benchmark.benchmark(root, runs=2)


def test_production_snapshot_dirty_observation_is_rejected_after_exact_restore(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    root = _production_repo(tmp_path / "repo")
    readme = root / "README.md"
    original = readme.read_bytes()
    real_collect_git = status_benchmark.status.collect_git
    observed_dirty: list[int] = []

    def collect_git_while_dirty(repo_root: Path) -> dict:
        readme.write_bytes(original + b"temporary benchmark mutation\n")
        try:
            observation = real_collect_git(repo_root)
            observed_dirty.append(observation["git_dirty"])
            return observation
        finally:
            readme.write_bytes(original)

    monkeypatch.setattr(
        status_benchmark.status,
        "collect_git",
        collect_git_while_dirty,
    )

    with pytest.raises(RuntimeError, match="snapshot Git dirty observation"):
        status_benchmark.benchmark(root, runs=2)
    assert observed_dirty == [1]
    assert readme.read_bytes() == original
    assert _git(root, "status", "--porcelain") == ""


def test_reflog_absence_refuses_setup_and_snapshot_binding_rejects_observed_b(
    tmp_path: Path,
) -> None:
    root = _repo(tmp_path / "repo", reflog=False)
    head_a = _git(root, "rev-parse", "HEAD")
    _git(root, "commit", "--allow-empty", "-q", "-m", "transient B")
    observed_b = status_benchmark.status.collect_git(root)
    _git(root, "reset", "--hard", "-q", head_a)
    snapshot = {
        "git": {
            "sha": observed_b["git_sha"],
            "dirty": observed_b["git_dirty"],
        },
        "projection": {"head": head_a},
    }

    with pytest.raises(RuntimeError, match="snapshot Git SHA"):
        status_benchmark._validate_snapshot_repository_binding(
            root, snapshot, head_a
        )
    with pytest.raises(RuntimeError, match="HEAD reflog signal is unavailable"):
        status_benchmark.benchmark(root, runs=2)
