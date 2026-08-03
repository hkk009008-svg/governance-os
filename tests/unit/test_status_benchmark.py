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

    def snapshot(repo_root: Path, seat: str) -> dict:
        subprocess.run(
            ["/usr/bin/git", "rev-parse", "HEAD"],
            cwd=repo_root,
            capture_output=True,
            check=True,
        )
        return {
            "gate": {
                "status": "PASS",
                "fatal": 0,
                "advisory": 0,
                "failed_review": 0,
            },
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
        "per_run": [1, 1, 1],
        "git_per_run": [1, 1, 1],
        "candidate_independent_observation": True,
    }
    assert report["timing_seconds"]["p95_nearest_rank"] == max(
        report["timing_seconds"]["per_run"]
    )


def test_benchmark_refuses_dirty_worktree(tmp_path: Path) -> None:
    root = _repo(tmp_path / "repo")
    (root / "untracked.txt").write_text("dirty\n", encoding="utf-8")

    with pytest.raises(RuntimeError, match="refuses a dirty worktree"):
        status_benchmark.benchmark(root, runs=1)
