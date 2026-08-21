#!/usr/bin/env python3
"""Fail-closed capability preflight for the two supported CLI peers.

Both participants are terminal programs: the ``claude`` CLI and the ``codex``
CLI.  This check answers whether a peer invocation *could* run — binaries on
PATH, no ambient authority in the project config — and nothing else.  It
reports capability only.  It neither launches a provider unless ``--live`` is
explicitly selected nor grants authority for any later action.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import tomllib
from dataclasses import dataclass
from pathlib import Path


CODEX_AMBIENT_KEYS = ("approval_policy", "sandbox_mode", "features")
# A CLI-exclusive repo declares no project MCP servers: a peer is invoked as a
# child process with explicit argv, never registered as an ambient server that
# a later session inherits without asking.
PEER_BINARIES = ("claude", "codex")
RUNBOOK = "docs/protocol/peer.md"


@dataclass(frozen=True)
class Result:
    harness: str
    ok: bool
    detail: str
    remedy: str = ""


def _binary(name: str) -> str | None:
    return shutil.which(name)


def _profile_authority_paths(payload: object, *, prefix: str = "profiles") -> list[str]:
    """Return effective profile keys that could widen a later Codex invocation."""

    if not isinstance(payload, dict):
        return []
    found: list[str] = []
    for key, value in payload.items():
        path = f"{prefix}.{key}"
        if key in {*CODEX_AMBIENT_KEYS, "mcp_servers"}:
            found.append(path)
        found.extend(_profile_authority_paths(value, prefix=path))
    return found


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
    config_problem = ""
    try:
        payload = tomllib.loads(config.read_text(encoding="utf-8"))
    except (OSError, tomllib.TOMLDecodeError) as exc:
        payload = {}
        config_problem = f"project config is unavailable or invalid: {exc}"
    if not config_problem:
        ambient = sorted(set(payload) & set(CODEX_AMBIENT_KEYS))
        profiles = payload.get("profiles")
        if profiles is not None:
            if not isinstance(profiles, dict):
                config_problem = "project profiles must be a TOML table"
            elif profile_authority := _profile_authority_paths(profiles):
                config_problem = (
                    "project profiles carry ambient authority: "
                    + ", ".join(sorted(profile_authority))
                )
        servers = payload.get("mcp_servers")
        if not config_problem and servers:
            config_problem = (
                "project config declares MCP servers: "
                + ", ".join(sorted(servers))
                + " — peers are invoked as child processes, not registered servers"
            )
    problem = (
        f"project config carries {', '.join(ambient)}"
        if ambient
        else config_problem
    )
    results.append(
        Result(
            "codex",
            not problem,
            (
                "project config carries no ambient authority and no MCP servers"
                if not problem
                else problem
            ),
            "" if not problem else "restore the closed project configuration",
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


def check_peers() -> list[Result]:
    """Both CLI peers must be on PATH before any peer invocation is possible."""

    results = []
    for name in PEER_BINARIES:
        binary = _binary(name)
        results.append(
            Result(
                name,
                bool(binary),
                f"binary {binary or 'NOT FOUND on PATH'}",
                "" if binary else f"install the {name} CLI",
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
        "read-only",
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
    parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    parser.add_argument(
        "--live",
        action="store_true",
        help="launch one separately authorized positive-artifact probe",
    )
    args = parser.parse_args(argv)

    root = args.repo_root.resolve()
    results = check_peers() + check_codex(root)
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
