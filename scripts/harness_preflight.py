#!/usr/bin/env python3
"""Fail-closed capability preflight for the supported headless Codex path.

The check reports capability only.  It neither launches a provider unless
``--live`` is explicitly selected nor grants authority for any later action.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path


HARNESSES = ("codex",)
CODEX_AMBIENT_KEYS = ("approval_policy", "sandbox_mode", "features")
RUNBOOK = "docs/protocol/threeway/HEADLESS-REVIEW.md"


@dataclass(frozen=True)
class Result:
    harness: str
    ok: bool
    detail: str
    remedy: str = ""


def _binary(name: str) -> str | None:
    return shutil.which(name)


def check_codex(root: Path) -> list[Result]:
    """Codex is capable only with a binary and no ambient project grant."""

    binary = _binary("codex")
    results = [
        Result(
            "codex",
            bool(binary),
            f"binary {binary or 'NOT FOUND on PATH'}",
            "" if binary else "install the Codex CLI",
        )
    ]

    config = root / ".codex/config.toml"
    ambient: list[str] = []
    if config.is_file():
        text = config.read_text(encoding="utf-8")
        ambient = [key for key in CODEX_AMBIENT_KEYS if key in text]
    results.append(
        Result(
            "codex",
            not ambient,
            "project config implies no ambient runtime authority"
            if not ambient
            else f"project config carries {', '.join(ambient)}",
            ""
            if not ambient
            else "remove the keys and pin sandbox/approval per invocation",
        )
    )
    results.append(
        Result(
            "codex",
            True,
            "invocation contract: < /dev/null, --sandbox, explicit approval_policy",
        )
    )
    return results


def _git_identity(root: Path) -> str:
    environment = {
        key: value for key, value in os.environ.items() if not key.startswith("GIT_")
    }
    completed = subprocess.run(
        [
            "/usr/bin/git",
            "--no-replace-objects",
            "rev-parse",
            "--show-toplevel",
            "--short",
            "HEAD",
        ],
        cwd=root,
        env=environment,
        capture_output=True,
        text=True,
        check=False,
    )
    if completed.returncode != 0:
        raise ValueError("could not resolve repository root and HEAD")
    output = completed.stdout
    lines = output.splitlines()
    if not (
        len(lines) == 2
        and lines[0] == str(root.resolve())
        and re.fullmatch(r"[0-9a-f]{4,40}", lines[1]) is not None
        and output == f"{lines[0]}\n{lines[1]}\n"
    ):
        raise ValueError("repository identity output is not canonical")
    return output


def live_probe(root: Path, *, runner=subprocess.run) -> Result:
    """Spend one Codex prompt and require the exact positive Git artifact."""

    root = root.resolve()
    try:
        expected = _git_identity(root)
    except ValueError as exc:
        return Result("codex", False, str(exc), f"see {RUNBOOK}")

    command = "git rev-parse --show-toplevel --short HEAD"
    prompt = (
        "Run exactly this command once in the supplied repository and reply with "
        f"ONLY stdout: {json.dumps(command)}"
    )
    argv = [
        "codex",
        "exec",
        "-C",
        str(root),
        "--sandbox",
        "workspace-write",
        "-c",
        'approval_policy="never"',
        prompt,
    ]
    environment = {
        key: value for key, value in os.environ.items() if not key.startswith("GIT_")
    }
    try:
        completed = runner(
            argv,
            cwd=root,
            env=environment,
            stdin=subprocess.DEVNULL,
            capture_output=True,
            text=True,
            timeout=600,
            check=False,
        )
    except (OSError, subprocess.SubprocessError) as exc:
        return Result("codex", False, f"probe failed to run: {exc}", f"see {RUNBOOK}")

    hit = completed.returncode == 0 and completed.stdout == expected
    return Result(
        "codex",
        hit,
        "live probe returned exact positive artifact"
        if hit
        else (
            "live probe produced no exact positive artifact "
            f"(exit {completed.returncode}, stdout {len(completed.stdout or '')} bytes, "
            f"stderr {len(completed.stderr or '')} bytes)"
        ),
        "" if hit else f"exit code is not evidence; see {RUNBOOK}",
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="harness_preflight.py")
    parser.add_argument("harness", choices=(*HARNESSES, "all"))
    parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    parser.add_argument(
        "--live",
        action="store_true",
        help="launch one separately authorized positive-artifact probe",
    )
    args = parser.parse_args(argv)

    root = args.repo_root.resolve()
    results = check_codex(root)
    if args.live:
        results.append(live_probe(root))
    for result in results:
        marker = "PASS" if result.ok else "FAIL"
        print(f"{marker} {result.harness}: {result.detail}")
        if result.remedy:
            print(f"  remedy: {result.remedy}")
    return 0 if all(result.ok for result in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
