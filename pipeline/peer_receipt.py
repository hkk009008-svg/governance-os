#!/usr/bin/env python3
"""The receipt: what a peer invocation actually did, written once.

Three invariants, each of which was a real defect before the 2026-08-21 review
made it a rule. `--task` becomes a directory name, so it must be one safe path
component or a receipt could be written over committed mail. A sequence number
comes from the highest present, never from a count, because counting reuses a
number the moment the sequence has a gap. And the file is created exclusively,
because a record of something that happened must not be silently replaced.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
from pathlib import Path

from peer_backends import PeerError

RECEIPTS = "coordination/peer"
# Unconstrained, `../mailbox/sent` and absolute paths escaped coordination/peer/.
TASK_RE = re.compile(r"^[a-z0-9][a-z0-9._-]{0,63}$")


def validate_task(task: str) -> str:
    """Refuse anything that is not one safe path component."""

    if TASK_RE.fullmatch(task) is None:
        raise PeerError(
            f"--task {task!r} must match {TASK_RE.pattern}: it becomes a "
            "directory name under coordination/peer/, and a task that can "
            "traverse can overwrite committed mail"
        )
    return task


def receipt_path(repo_root: Path, task: str, seq: int, side: str) -> Path:
    return repo_root / RECEIPTS / validate_task(task) / f"{seq:04d}-{side}.json"


def next_seq(repo_root: Path, task: str) -> int:
    """One past the highest sequence present, never a count.

    Counting files reused a number whenever the sequence had a gap: a 0001
    plus 0003 directory returned 3 and the next receipt overwrote 0003.
    """

    directory = repo_root / RECEIPTS / validate_task(task)
    if not directory.is_dir():
        return 1
    highest = 0
    for path in directory.glob("*.json"):
        head = path.name.split("-", 1)[0]
        if head.isdigit():
            highest = max(highest, int(head))
    return highest + 1


def write_receipt(repo_root: Path, outcome: Outcome, started: str) -> Path:
    path = receipt_path(repo_root, outcome.task, next_seq(repo_root, outcome.task), outcome.side)
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        raise PeerError(f"refusing to overwrite an existing receipt: {path}")
    payload = {
        "schema": "peer-receipt/1",
        "task": outcome.task,
        "side": outcome.side,
        "role": outcome.role,
        "advisory": outcome.advisory,
        "started": started,
        "duration_s": round(outcome.duration_s, 2),
        "exit_code": outcome.exit_code,
        "argv_sha256": hashlib.sha256("\x00".join(outcome.argv).encode()).hexdigest(),
        "argv_binary": outcome.argv[0] if outcome.argv else None,
        "prompt_sha256": outcome.prompt_sha256,
        "result_sha256": hashlib.sha256(outcome.result.encode()).hexdigest(),
        "model_reported": outcome.model_reported,
        "cost_usd": outcome.cost_usd,
        "notes": outcome.notes,
    }
    # Exclusive create: losing a race must fail loudly, not replace a record.
    with os.fdopen(
        os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o644), "w", encoding="utf-8"
    ) as handle:
        handle.write(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    return path


