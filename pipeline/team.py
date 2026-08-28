#!/usr/bin/env python3
"""Desktop-app team entry point and stable public imports."""
from __future__ import annotations

import argparse
import os
import sqlite3
import subprocess
import sys
from pathlib import Path

from team_mcp import MCP_PROTOCOL_VERSION, McpServer
from team_messages import Team
from team_store import (
    CAPABILITIES, CURSOR_SEMANTICS, IDENTITY_ASSURANCE, MAX_BODY_BYTES,
    MAX_IDEMPOTENCY_KEY_BYTES, MAX_MESSAGE_ID, MAX_READ_LIMIT, MAX_WAIT_SECONDS,
    MEMBERS,
    RECIPIENTS, TeamError,
)

__all__ = [
    "CAPABILITIES", "CURSOR_SEMANTICS", "IDENTITY_ASSURANCE", "MAX_BODY_BYTES",
    "MAX_IDEMPOTENCY_KEY_BYTES", "MAX_MESSAGE_ID", "MAX_READ_LIMIT", "MAX_WAIT_SECONDS",
    "MCP_PROTOCOL_VERSION", "MEMBERS", "RECIPIENTS", "McpServer", "Team",
    "TeamError", "main",
]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="bin/pipeline team")
    subparsers = parser.add_subparsers(dest="command", required=True)
    serve = subparsers.add_parser("serve", help="run one app's stdio MCP adapter")
    serve.add_argument("--member", required=True, choices=MEMBERS)
    serve.add_argument("--repo-root", type=Path, default=Path.cwd())
    args = parser.parse_args(argv)
    try:
        member = (
            _DiscoveryTeam(args.member)
            if os.environ.get("PIPELINE_TEAM_DISCOVERY_ONLY") == "1"
            else Team(args.repo_root, args.member)
        )
    except (TeamError, OSError, sqlite3.Error, subprocess.SubprocessError) as exc:
        print(f"bin/pipeline team: {exc}", file=sys.stderr)
        return 2
    return McpServer(member).serve()


class _DiscoveryTeam:
    """Schema-only member used by read-only native discovery."""

    def __init__(self, member: str) -> None:
        self.member = member

    @staticmethod
    def _unavailable(*_args, **_kwargs):
        raise TeamError("team operations are disabled during read-only discovery")

    status = send = wait = _unavailable


if __name__ == "__main__":
    raise SystemExit(main())
