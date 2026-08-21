#!/usr/bin/env python3
"""Strict read-only protocol validation bundle."""

from __future__ import annotations

import argparse
import os
import shlex
import subprocess
import sys
import codex_protocol_model as protocol_model
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent


@dataclass(frozen=True)
class CommandResult:
    cmd: list[str]
    returncode: int
    stdout: str
    stderr: str


def run_command(cmd: list[str], cwd: Path, timeout: int = 120) -> CommandResult:
    env = dict(os.environ)
    env.pop("GIT_INDEX_FILE", None)
    proc = subprocess.run(
        cmd,
        cwd=cwd,
        capture_output=True,
        text=True,
        timeout=timeout,
        env=env,
    )
    return CommandResult(
        cmd=cmd,
        returncode=proc.returncode,
        stdout=proc.stdout,
        stderr=proc.stderr,
    )


def _python() -> str:
    return sys.executable


def _materialize_model_command(command: str, python_executable: str) -> list[str]:
    tokens = shlex.split(command)
    if tokens[:3] == ["env", "-u", "GIT_INDEX_FILE"]:
        tokens = tokens[3:]
    return [python_executable, *tokens[1:]]


def verification_commands(python_executable: str) -> list[list[str]]:
    return [
        _materialize_model_command(command, python_executable)
        for command in protocol_model.CODEX_VERIFICATION_COMMANDS
    ]


def base_commands(python_executable: str, wave: int) -> list[list[str]]:
    """The unconditional read-only checks every doctor run performs."""
    return [
        [python_executable, "pipeline/check_coordination.py"],
        [python_executable, "pipeline/target_binding.py", "--check"],
        [python_executable, "pipeline/route_lineage.py", "--check"],
    ]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run strict read-only protocol checks.")
    parser.add_argument("--root", default=str(ROOT))
    parser.add_argument(
        "--wave", type=int, default=0, help="retained for call compatibility; unused"
    )
    args = parser.parse_args(argv)

    root = Path(args.root)
    py = _python()
    commands = base_commands(py, args.wave)
    commands.extend(verification_commands(py))

    for cmd in commands:
        result = run_command(cmd, root)
        print("$ " + " ".join(cmd))
        if result.stdout:
            print(result.stdout.rstrip())
        if result.stderr:
            print(result.stderr.rstrip(), file=sys.stderr)
        if result.returncode != 0:
            print("PROTOCOL DOCTOR: FAIL")
            return result.returncode
    print("PROTOCOL DOCTOR: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
