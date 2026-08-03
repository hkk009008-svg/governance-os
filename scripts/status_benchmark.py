#!/usr/bin/env python3
"""Benchmark the direct production orientation snapshot without timing gates."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import platform
import statistics
import subprocess
import sys
import time
from pathlib import Path

import status


SCHEMA_VERSION = "status-benchmark/v1"
MAX_REFLOG_SIGNAL_BYTES = 65_536


def _git(root: Path, *arguments: str) -> bytes:
    completed = subprocess.run(
        [
            "/usr/bin/git",
            "--no-replace-objects",
            "--literal-pathspecs",
            "--no-optional-locks",
            "-C",
            str(root),
            *arguments,
        ],
        capture_output=True,
        check=False,
        env={
            "PATH": "/usr/bin:/bin",
            "LANG": "C",
            "LC_ALL": "C",
            "HOME": "/var/empty",
            "XDG_CONFIG_HOME": "/var/empty",
            "GIT_CONFIG_NOSYSTEM": "1",
            "GIT_CONFIG_GLOBAL": "/dev/null",
        },
    )
    if completed.returncode != 0:
        detail = completed.stderr.decode("utf-8", errors="replace").strip()
        raise RuntimeError(f"sanitized Git failed: {detail or arguments[0]}")
    return completed.stdout


def _repository_state(root: Path) -> tuple[Path, str, bytes, str]:
    output = _git(
        root,
        "rev-parse",
        "--path-format=absolute",
        "--show-toplevel",
        "--verify",
        "HEAD^{commit}",
    ).decode("utf-8", errors="strict").splitlines()
    if len(output) != 2:
        raise RuntimeError("repository identity output is malformed")
    top = Path(output[0]).resolve(strict=True)
    if top != root:
        raise RuntimeError(f"--root must be the exact Git worktree root: {top}")
    head = output[1]
    if len(head) != 40 or any(character not in "0123456789abcdef" for character in head):
        raise RuntimeError("HEAD is not one full lowercase commit SHA")
    dirty = _git(root, "status", "--porcelain", "--untracked-files=normal")
    reflog = _git(root, "reflog", "show", "-32", "--format=%H%x00%gs", "HEAD")
    if not reflog:
        raise RuntimeError("HEAD reflog signal is unavailable")
    if len(reflog) > MAX_REFLOG_SIGNAL_BYTES:
        raise RuntimeError("bounded HEAD reflog identity signal is too large")
    latest_reflog_head = reflog.split(b"\n", 1)[0].split(b"\0", 1)[0]
    if latest_reflog_head != head.encode("ascii"):
        raise RuntimeError("HEAD reflog signal does not match current HEAD")
    return top, head, dirty, hashlib.sha256(reflog).hexdigest()


def _validate_snapshot_repository_binding(
    root: Path,
    snapshot: dict,
    pinned_head: str,
) -> None:
    git_observation = snapshot.get("git")
    if not isinstance(git_observation, dict):
        raise RuntimeError("snapshot Git observation is absent")
    dirty = git_observation.get("dirty")
    if type(dirty) is not int or dirty != 0:
        raise RuntimeError("snapshot Git dirty observation is not typed integer zero")
    sha = git_observation.get("sha")
    if (
        not isinstance(sha, str)
        or not 4 <= len(sha) <= 40
        or any(character not in "0123456789abcdef" for character in sha)
    ):
        raise RuntimeError("snapshot Git SHA is not a lowercase commit prefix")
    if not pinned_head.startswith(sha):
        raise RuntimeError("snapshot Git SHA does not prefix benchmark pinned HEAD")
    try:
        resolved = _git(root, "rev-parse", "--verify", f"{sha}^{{commit}}")
    except RuntimeError as exc:
        raise RuntimeError("snapshot Git SHA is not an unambiguous commit prefix") from exc
    if resolved.decode("ascii", errors="strict").strip() != pinned_head:
        raise RuntimeError("snapshot Git SHA does not resolve to benchmark pinned HEAD")
    projection = snapshot.get("projection")
    if not isinstance(projection, dict) or projection.get("head") != pinned_head:
        raise RuntimeError(
            "snapshot projection HEAD does not match benchmark pinned HEAD"
        )


def _nearest_rank(values: list[float], probability: float) -> float:
    ordered = sorted(values)
    return ordered[max(0, math.ceil(probability * len(ordered)) - 1)]


def _is_git_process(arguments: object) -> bool:
    if not isinstance(arguments, (list, tuple)) or not arguments:
        return False
    executable = Path(str(arguments[0])).name
    return executable == "git"


def benchmark(
    repo_root: Path | str,
    *,
    runs: int = 10,
    seat: str = "coordinator",
) -> dict:
    """Measure direct snapshots that agree at explicit Git checkpoints."""

    if runs < 2:
        raise ValueError("runs must be at least 2 for a non-vacuous stability observation")
    root = Path(repo_root).resolve(strict=True)
    _top, head, dirty, initial_ref_signal = _repository_state(root)
    if dirty:
        raise RuntimeError(
            "benchmark refuses a dirty worktree because timing would not bind "
            "one committed mechanism"
        )

    elapsed_values: list[float] = []
    process_counts: list[int] = []
    git_process_counts: list[int] = []
    observed_gates: list[dict] = []
    real_popen = subprocess.Popen
    for _index in range(runs):
        _before_top, before_head, before_dirty, before_ref_signal = _repository_state(
            root
        )
        if (
            before_head != head
            or before_dirty
            or before_ref_signal != initial_ref_signal
        ):
            raise RuntimeError(
                "repository identity or cleanliness changed before benchmark run"
            )
        calls: list[object] = []

        def counted_popen(*args, **kwargs):
            calls.append(args[0] if args else kwargs.get("args"))
            return real_popen(*args, **kwargs)

        subprocess.Popen = counted_popen
        started = time.perf_counter()
        try:
            snapshot = status.collect_orientation_snapshot(root, seat)
        finally:
            elapsed = time.perf_counter() - started
            subprocess.Popen = real_popen
        _after_top, after_head, after_dirty, after_ref_signal = _repository_state(root)
        if (
            after_head != head
            or after_dirty
            or after_ref_signal != before_ref_signal
        ):
            raise RuntimeError(
                "repository identity or cleanliness changed during benchmark run"
            )
        _validate_snapshot_repository_binding(root, snapshot, head)
        elapsed_values.append(elapsed)
        process_counts.append(len(calls))
        git_process_counts.append(sum(_is_git_process(call) for call in calls))
        observed_gates.append(dict(snapshot["gate"]))

    _top_after, head_after, dirty_after, final_ref_signal = _repository_state(root)
    if head_after != head or dirty_after or final_ref_signal != initial_ref_signal:
        raise RuntimeError("repository HEAD or cleanliness changed during benchmark")
    if any(gate != observed_gates[0] for gate in observed_gates[1:]):
        raise RuntimeError("snapshot gate counts changed during benchmark")

    return {
        "schema_version": SCHEMA_VERSION,
        "parameters": {"runs": runs, "seat": seat},
        "repository": {
            "root": str(root),
            "head": head,
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
        },
        "runtime": {
            "python_implementation": platform.python_implementation(),
            "python_version": platform.python_version(),
            "platform": platform.platform(),
            "system": platform.system(),
            "machine": platform.machine(),
        },
        "gate": observed_gates[0],
        "processes": {
            "per_run": process_counts,
            "git_per_run": git_process_counts,
            "repeated_run_process_count_stable": len(set(process_counts)) == 1,
        },
        "timing_seconds": {
            "per_run": elapsed_values,
            "min": min(elapsed_values),
            "max": max(elapsed_values),
            "p50": statistics.median(elapsed_values),
            "p95_nearest_rank": _nearest_rank(elapsed_values, 0.95),
            "interpretation": "report-only machine-local observation; not a gate",
        },
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--root",
        type=Path,
        default=Path(__file__).resolve().parent.parent,
    )
    parser.add_argument("--runs", type=int, default=10)
    parser.add_argument("--seat", default="coordinator")
    arguments = parser.parse_args(argv)
    try:
        report = benchmark(
            arguments.root, runs=arguments.runs, seat=arguments.seat
        )
    except (OSError, RuntimeError, ValueError) as exc:
        print(f"status benchmark refused: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(report, sort_keys=True, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
