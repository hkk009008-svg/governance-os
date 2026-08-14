#!/usr/bin/env python3
"""One Git subprocess environment policy, applied per call.

Before this seam existed, at least nine modules each built their own Git
environment: some stripped every ``GIT_*`` variable, some stripped only
``GIT_INDEX_FILE``, and several inherited the ambient environment unchanged,
so ``GIT_DIR`` or a leaked index could silently retarget a gate. None pinned
repository discovery, so a non-repository root (for example a scratch
directory inside a real checkout) walked up and confidently answered with the
*enclosing* repository's state.

Two explicit modes:

- :func:`authority_env` — hermetic. Fixed ``PATH`` and C locale, isolated
  HOME/XDG, no inherited ``GIT_*``, no user/system config, prompts disabled.
  For validators and gates whose answers grant or deny authority.
- :func:`dashboard_env` — best-effort. Inherits the caller's environment
  (credential helpers, ssh-agent, proxies keep working) minus the variables
  that can retarget which repository, index, or config answers. For
  read-only status and metrics surfaces.

Both modes pin repository discovery to the requested root via
``GIT_CEILING_DIRECTORIES``: a root that is not itself a repository (or a
linked worktree) answers "not a repository" instead of escaping upward.

The two strictest existing seams — ``scripts/mailbox_writer.py`` and
``scripts/git_commit_projection.py`` — keep their own proven fixed
environments; this module unifies everything that was weaker than them.
"""

from __future__ import annotations

import os
import subprocess
from pathlib import Path

# Variables that change WHICH repository/index a git command answers for.
# These are stripped everywhere: no legitimate caller retargets a governance
# git call through the ambient environment.
REPO_RETARGETING_GIT_VARS = (
    "GIT_ALTERNATE_OBJECT_DIRECTORIES",
    "GIT_CEILING_DIRECTORIES",
    "GIT_COMMON_DIR",
    "GIT_DIR",
    "GIT_DISCOVERY_ACROSS_FILESYSTEM",
    "GIT_INDEX_FILE",
    "GIT_NAMESPACE",
    "GIT_OBJECT_DIRECTORY",
    "GIT_WORK_TREE",
)

# Config-selection variables additionally change WHAT configuration answers
# (aliases, hooksPath). Python dashboard/authority callers strip these too;
# the bash lock scripts deliberately keep them because they carry the
# credential-helper configuration a real push needs, and tests use them to
# inject hermetic identity.
CONFIG_GIT_VARS = (
    "GIT_CONFIG",
    "GIT_CONFIG_COUNT",
    "GIT_CONFIG_GLOBAL",
    "GIT_CONFIG_PARAMETERS",
    "GIT_CONFIG_SYSTEM",
)

RETARGETING_GIT_VARS = tuple(sorted(REPO_RETARGETING_GIT_VARS + CONFIG_GIT_VARS))

_ISOLATED_HOME = "/var/empty" if os.path.isdir("/var/empty") else "/nonexistent"


def _ceiling(root: Path) -> str:
    # Discovery starting inside ``root`` may find ``root`` itself but must
    # not ascend past it. git excludes the listed directory and everything
    # above it, so the parent is the correct pin.
    return str(Path(root).resolve().parent)


def authority_env(root: Path) -> dict[str, str]:
    """Hermetic environment for authority-bearing git reads/writes."""

    return {
        "PATH": "/usr/bin:/bin",
        "LANG": "C",
        "LC_ALL": "C",
        "LANGUAGE": "C",
        "HOME": _ISOLATED_HOME,
        "XDG_CONFIG_HOME": _ISOLATED_HOME,
        "GIT_CONFIG_NOSYSTEM": "1",
        "GIT_TERMINAL_PROMPT": "0",
        "GIT_OPTIONAL_LOCKS": "0",
        "GIT_CEILING_DIRECTORIES": _ceiling(root),
    }


def dashboard_env(root: Path) -> dict[str, str]:
    """Best-effort environment for read-only dashboard/metrics git reads."""

    env = {
        key: value
        for key, value in os.environ.items()
        if key not in RETARGETING_GIT_VARS
        and not key.startswith(("GIT_CONFIG_KEY_", "GIT_CONFIG_VALUE_"))
    }
    env.update(
        {
            "LANG": "C",
            "LC_ALL": "C",
            "LANGUAGE": "C",
            "GIT_OPTIONAL_LOCKS": "0",
            "GIT_CEILING_DIRECTORIES": _ceiling(root),
        }
    )
    return env


def run_git(
    root: Path,
    args: list[str] | tuple[str, ...],
    *,
    mode: str = "authority",
    check: bool = False,
    timeout: int = 120,
    text: bool = False,
    input_data: str | bytes | None = None,
    encoding: str | None = None,
) -> subprocess.CompletedProcess:
    """Run one git command rooted at ``root`` under the selected policy."""

    if mode == "authority":
        env = authority_env(root)
    elif mode == "dashboard":
        env = dashboard_env(root)
    else:
        raise ValueError(f"unknown git_runner mode {mode!r}")
    return subprocess.run(
        ["git", "--no-replace-objects", "-C", str(root), *args],
        env=env,
        capture_output=True,
        check=check,
        timeout=timeout,
        text=text,
        input=input_data,
        encoding=encoding,
    )
