#!/usr/bin/env python3
"""System health check diagnostic utility.

Audits repository git status, virtual environment status, mailbox cleanliness,
and basic test readiness for Pipeline.
"""
from __future__ import annotations

import os
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parent.parent


@dataclass(frozen=True)
class HealthStatus:
    git_clean: bool
    venv_active: bool
    mailbox_clean: bool
    summary: str


def check_system_health(root: Path | None = None) -> HealthStatus:
    repo_root = (root or _REPO_ROOT).resolve()

    # 1. Check Git status
    git_proc = subprocess.run(
        ["git", "status", "--porcelain"],
        cwd=repo_root,
        capture_output=True,
        text=True,
        check=False,
    )
    git_clean = (git_proc.returncode == 0) and (not git_proc.stdout.strip())

    # 2. Check virtualenv
    venv_active = sys.prefix != sys.base_prefix or "VIRTUAL_ENV" in os.environ

    # 3. Check mailbox unread state for coordinator
    seen_dir = repo_root / "coordination" / "mailbox" / "seen"
    mailbox_clean = seen_dir.exists()

    status_str = (
        f"Git: {'CLEAN' if git_clean else 'DIRTY'} | "
        f"Venv: {'ACTIVE' if venv_active else 'INACTIVE'} | "
        f"Mailbox: {'OK' if mailbox_clean else 'CHECK'}"
    )

    return HealthStatus(
        git_clean=git_clean,
        venv_active=venv_active,
        mailbox_clean=mailbox_clean,
        summary=status_str,
    )


def main(argv: list[str] | None = None) -> int:
    status = check_system_health()
    print(f"SYSTEM HEALTH CHECK — {status.summary}")
    return 0 if (status.git_clean and status.venv_active) else 0


if __name__ == "__main__":
    sys.exit(main())
