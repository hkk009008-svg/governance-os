"""Small process helpers shared by desktop-team tests."""
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import team


def git(repo: Path, *args: str) -> str:
    completed = subprocess.run(
        ["git", *args], cwd=repo, text=True, capture_output=True, check=True
    )
    return completed.stdout.strip()


def make_repo(path: Path) -> Path:
    path.mkdir()
    git(path, "init", "-q", "-b", "main")
    git(path, "config", "user.name", "Team Test")
    git(path, "config", "user.email", "team@example.invalid")
    (path / "tracked.txt").write_text("base\n", encoding="utf-8")
    git(path, "add", "tracked.txt")
    git(path, "commit", "-q", "-m", "test: base")
    return path


class McpProcess:
    def __init__(self, repo: Path, member: str) -> None:
        environment = {
            key: value for key, value in os.environ.items() if key != "GIT_INDEX_FILE"
        }
        self.process = subprocess.Popen(
            [
                sys.executable,
                str(Path(team.__file__).resolve()),
                "serve",
                "--repo-root",
                str(repo),
                "--member",
                member,
            ],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
            env=environment,
        )
        self._next_id = 1
        initialized = self.request(
            "initialize",
            {
                "protocolVersion": team.MCP_PROTOCOL_VERSION,
                "capabilities": {},
                "clientInfo": {"name": "pytest", "version": "1"},
            },
        )
        assert initialized["protocolVersion"] == team.MCP_PROTOCOL_VERSION
        self.notify("notifications/initialized", {})

    def _write(self, payload: dict) -> None:
        assert self.process.stdin is not None
        self.process.stdin.write(json.dumps(payload, separators=(",", ":")) + "\n")
        self.process.stdin.flush()

    def request(self, method: str, params: dict | None = None) -> dict:
        request_id = self._next_id
        self._next_id += 1
        payload = {"jsonrpc": "2.0", "id": request_id, "method": method}
        if params is not None:
            payload["params"] = params
        self._write(payload)
        assert self.process.stdout is not None
        response = json.loads(self.process.stdout.readline())
        assert response["id"] == request_id
        assert "error" not in response, response
        return response["result"]

    def notify(self, method: str, params: dict | None = None) -> None:
        payload = {"jsonrpc": "2.0", "method": method}
        if params is not None:
            payload["params"] = params
        self._write(payload)

    def tool(self, name: str, arguments: dict | None = None) -> dict:
        result = self.request(
            "tools/call", {"name": name, "arguments": arguments or {}}
        )
        assert result["isError"] is False, result
        return result["structuredContent"]

    def close(self) -> None:
        if self.process.stdin is not None:
            self.process.stdin.close()
        self.process.wait(timeout=5)
        error = self.process.stderr.read() if self.process.stderr is not None else ""
        if self.process.stdout is not None:
            self.process.stdout.close()
        if self.process.stderr is not None:
            self.process.stderr.close()
        assert self.process.returncode == 0, error
