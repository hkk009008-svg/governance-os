from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

import status_benchmark


def _git(root: Path, *arguments: str) -> str:
    return subprocess.run(
        ["/usr/bin/git", *arguments],
        cwd=root,
        text=True,
        capture_output=True,
        check=True,
    ).stdout.strip()


def _repo(path: Path) -> Path:
    path.mkdir()
    _git(path, "init", "-q", "-b", "main")
    _git(path, "config", "user.email", "benchmark@example.invalid")
    _git(path, "config", "user.name", "Benchmark Test")
    (path / "tracked.txt").write_text("tracked\n", encoding="utf-8")
    _git(path, "add", "tracked.txt")
    _git(path, "commit", "-q", "-m", "base")
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
            "projection": {"head": head},
            "seat": seat,
        }

    monkeypatch.setattr(status_benchmark.status, "collect_orientation_snapshot", snapshot)
    report = status_benchmark.benchmark(root, runs=3, seat="coordinator")

    assert report["schema_version"] == "status-benchmark/v1"
    assert report["repository"] == {
        "root": str(root),
        "head": _git(root, "rev-parse", "HEAD"),
        "dirty": False,
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
            "projection": {"head": "f" * 40},
        },
    )

    with pytest.raises(RuntimeError, match="projection HEAD"):
        status_benchmark.benchmark(root, runs=2)
