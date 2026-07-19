#!/usr/bin/env python3
"""Measure one read-only ledger fast-resume evaluation truthfully."""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import time
from pathlib import Path
from typing import Any

import ledger_start_guard


class _GitProcessCounter:
    def __init__(self, popen: Any) -> None:
        self._popen = popen
        self.count = 0

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        command = args[0] if args else kwargs.get("args")
        if isinstance(command, (list, tuple)) and command:
            executable = os.fspath(command[0])
            if Path(executable).name == "git":
                self.count += 1
        return self._popen(*args, **kwargs)


def _pipeline_head(root: Path) -> str:
    environment = os.environ.copy()
    environment.pop("GIT_INDEX_FILE", None)
    return subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=root,
        check=True,
        capture_output=True,
        text=True,
        env=environment,
    ).stdout.strip()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Measure one ledger start-guard resume classification"
    )
    parser.add_argument("--seat", required=True, choices=ledger_start_guard.VALID_SEATS)
    parser.add_argument("--wave", type=int, default=2)
    parser.add_argument("--target", default=None)
    parser.add_argument("--resume-from", required=True, metavar="ROUTE_REF")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args(argv)

    root = Path.cwd().resolve(strict=False)
    counter = _GitProcessCounter(subprocess.Popen)
    original_popen = subprocess.Popen
    started = time.perf_counter()
    try:
        subprocess.Popen = counter
        result = ledger_start_guard.build_resume(
            seat=args.seat,
            root=root,
            wave=args.wave,
            target_name=args.target,
            resume_from=args.resume_from,
        )
        pipeline_head = _pipeline_head(root)
    finally:
        elapsed = time.perf_counter() - started
        subprocess.Popen = original_popen

    payload = {
        "schema": "ledger-start-guard-benchmark-v1",
        "classification": result.classification.value,
        "elapsed_seconds": round(elapsed, 6),
        "git_processes": counter.count,
        "pipeline_head": pipeline_head,
        "resume_from": args.resume_from,
    }
    rendered = json.dumps(payload, indent=2) + "\n"
    if args.output is not None:
        args.output.write_text(rendered, encoding="utf-8")
    print(rendered, end="")
    return (
        1
        if result.classification
        is ledger_start_guard.ResumeClassification.START_GUARD_FAIL
        else 0
    )


if __name__ == "__main__":
    raise SystemExit(main())
