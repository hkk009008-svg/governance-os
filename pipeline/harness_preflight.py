#!/usr/bin/env python3
"""Read-only readiness check for the three desktop-app integrations.

Measures app bundles, project MCP bindings, adapter handshakes, native config
views, and the AGY permission without launching a model or sending a message.
"""
from __future__ import annotations

import argparse
import json
import os
import plistlib
import select
import subprocess
import tempfile
import tomllib
from pathlib import Path

import team
from native_app_readiness import (
    DEFAULT_AGY_SETTINGS,
    TEAM_TOOLS,
    NativeResult as Result,
    _command_is_repo_pipeline,
    check_agy_permission,
    check_native_discovery,
    load_agy_plugin_config,
)


APP_BUNDLES = {
    "codex": (
        ("ChatGPT.app", "com.openai.codex", "ChatGPT"),
        ("Codex.app", "com.openai.codex", "Codex"),
    ),
    "claude": (("Claude.app", "com.anthropic.claudefordesktop", "Claude"),),
    "agy": (
        ("Antigravity.app", "com.google.antigravity", "Antigravity"),
        ("Antigravity IDE.app", "com.google.antigravity-ide", "Electron"),
    ),
}
CONFIG_PATHS = {
    "codex": ".codex/config.toml",
    "claude": ".mcp.json",
    "agy": ".agents/plugins/pipeline-team/mcp_config.json",
}
AGY_PLUGIN_MANIFEST = ".agents/plugins/pipeline-team/plugin.json"


def check_apps(applications: Path = Path("/Applications")) -> list[Result]:
    results = []
    for member, identities in APP_BUNDLES.items():
        present = [item for item in identities if (applications / item[0]).is_dir()]
        if not present:
            labels = " / ".join(item[0].removesuffix(".app") for item in identities)
            results.append(Result(member, False, f"desktop app not found under {applications}", f"install {labels}"))
            continue
        failures = []
        for name, expected_id, expected_executable in present:
            bundle = applications / name
            try:
                with (bundle / "Contents/Info.plist").open("rb") as handle:
                    payload = plistlib.load(handle)
                executable = payload.get("CFBundleExecutable")
                binary = bundle / "Contents/MacOS" / str(executable)
                if (
                    payload.get("CFBundleIdentifier") != expected_id
                    or executable != expected_executable
                    or not binary.is_file()
                    or not os.access(binary, os.X_OK)
                ):
                    raise ValueError("bundle identifier or executable does not match")
                version = payload.get("CFBundleShortVersionString") or payload.get("CFBundleVersion") or "version unreported"
            except (OSError, ValueError, plistlib.InvalidFileException) as exc:
                failures.append(f"{name}: {exc}")
                continue
            results.append(Result(member, True, f"{name} {version}"))
            break
        else:
            results.append(Result(member, False, "desktop app identity invalid: " + "; ".join(failures), "reinstall the expected desktop app"))
    return results


def _load_member_config(root: Path, member: str) -> dict:
    if member == "agy":
        return load_agy_plugin_config(root)
    path = root / CONFIG_PATHS[member]
    payload = (
        tomllib.loads(path.read_text(encoding="utf-8"))
        if member == "codex"
        else json.loads(path.read_text(encoding="utf-8"))
    )
    table = "mcp_servers" if member == "codex" else "mcpServers"
    if not isinstance(payload, dict) or set(payload) != {table}:
        raise ValueError(f"project config must contain only the {table} table")
    servers = payload.get(table)
    if not isinstance(servers, dict):
        raise ValueError("MCP server table is missing")
    if set(servers) != {"pipeline-team"}:
        raise ValueError(
            "project MCP server inventory must contain exactly pipeline-team"
        )
    config = servers["pipeline-team"]
    if not isinstance(config, dict):
        raise ValueError("pipeline-team server config must be an object")
    return config


def _validate_member_config(root: Path, member: str, config: dict) -> None:
    expected_args = ["team", "serve", "--member", member]
    if config.get("args") != expected_args:
        raise ValueError(f"{member} label must be configured by args {expected_args!r}, got {config.get('args')!r}")
    command = config.get("command")
    if not _command_is_repo_pipeline(root, command) or not (root / "bin/pipeline").is_file():
        raise ValueError("command must resolve to this repository's bin/pipeline")
    if extras := set(config) - {"command", "args", "type", "cwd", "env"}:
        raise ValueError(f"unsupported config keys: {sorted(extras)}")
    if config.get("type", "stdio") != "stdio":
        raise ValueError("pipeline-team must use stdio transport")
    if config.get("cwd", ".") != ".":
        raise ValueError("workspace cwd, when present, must be '.'")
    if config.get("env") not in ({}, None):
        raise ValueError("team label and repository may not come from environment overrides")
    if member == "claude":
        settings = json.loads(
            (root / ".claude/settings.json").read_text(encoding="utf-8")
        )
        if not isinstance(settings, dict):
            raise ValueError("Claude project settings must be an object")
        allowed_settings = {
            "$comment", "enabledMcpjsonServers", "enableAllProjectMcpServers",
        }
        if extras := set(settings) - allowed_settings:
            raise ValueError(
                f"Claude project settings contain unsupported keys: {sorted(extras)}"
            )
        if settings.get("enabledMcpjsonServers") != ["pipeline-team"]:
            raise ValueError(
                "Claude must approve exactly the pipeline-team project server"
            )
        broad_approval = settings.get("enableAllProjectMcpServers")
        if broad_approval is not None and broad_approval is not False:
            raise ValueError("Claude may not broadly approve all project MCP servers")


def check_team_configs(root: Path) -> list[Result]:
    root = root.resolve()
    results = []
    for member in team.MEMBERS:
        try:
            _validate_member_config(root, member, _load_member_config(root, member))
        except (OSError, ValueError, json.JSONDecodeError, tomllib.TOMLDecodeError) as exc:
            repair = CONFIG_PATHS[member]
            if member == "agy":
                repair = f"{AGY_PLUGIN_MANIFEST} and {repair}"
            results.append(Result(member, False, f"{member} project MCP config invalid: {exc}", f"repair {repair}"))
        else:
            results.append(Result(member, True, f"{CONFIG_PATHS[member]} configures member={member}"))
    return results


def _handshake_requests() -> tuple[dict, ...]:
    return (
        {"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {
            "protocolVersion": team.MCP_PROTOCOL_VERSION,
            "capabilities": {},
            "clientInfo": {"name": "pipeline-preflight", "version": "1"},
        }},
        {"jsonrpc": "2.0", "method": "notifications/initialized", "params": {}},
        {"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}},
        {
            "jsonrpc": "2.0", "id": 3, "method": "tools/call",
            "params": {"name": "team_status", "arguments": {}},
        },
    )


def _send_protocol_line(process: subprocess.Popen, payload: dict) -> None:
    if process.stdin is None:
        raise OSError("adapter stdin is unavailable")
    process.stdin.write(json.dumps(payload, separators=(",", ":")) + "\n")
    process.stdin.flush()


def _read_protocol_line(
    process: subprocess.Popen, argv: list[str], timeout: float,
) -> str:
    if process.stdout is None:
        raise OSError("adapter stdout is unavailable")
    readable, _, _ = select.select([process.stdout], [], [], timeout)
    if not readable:
        raise subprocess.TimeoutExpired(argv, timeout)
    line = process.stdout.readline()
    if not line:
        raise OSError("adapter closed stdout before completing the handshake")
    return line


def _run_handshake(
    argv: list[str], *, cwd: Path, env: dict[str, str], timeout: float = 10,
) -> subprocess.CompletedProcess:
    """Exchange MCP frames in lifecycle order with a disposable adapter."""

    process = subprocess.Popen(
        argv, cwd=cwd, env=env, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
        stderr=subprocess.PIPE, text=True, bufsize=1,
    )
    stdout = []
    try:
        initialize, initialized, listed, status = _handshake_requests()
        _send_protocol_line(process, initialize)
        stdout.append(_read_protocol_line(process, argv, timeout))
        try:
            first = json.loads(stdout[0])
        except json.JSONDecodeError:
            first = None
        if not (
            isinstance(first, dict)
            and first.get("id") == 1
            and isinstance(first.get("result"), dict)
        ):
            process.stdin.close()
            returncode = process.wait(timeout=timeout)
            stderr = process.stderr.read() if process.stderr is not None else ""
            return subprocess.CompletedProcess(
                argv, returncode, "".join(stdout), stderr
            )
        _send_protocol_line(process, initialized)
        _send_protocol_line(process, listed)
        stdout.append(_read_protocol_line(process, argv, timeout))
        _send_protocol_line(process, status)
        stdout.append(_read_protocol_line(process, argv, timeout))
        process.stdin.close()
        returncode = process.wait(timeout=timeout)
        stderr = process.stderr.read() if process.stderr is not None else ""
        return subprocess.CompletedProcess(argv, returncode, "".join(stdout), stderr)
    except BaseException:
        process.kill()
        process.wait()
        raise
    finally:
        for stream in (process.stdout, process.stderr):
            if stream is not None:
                stream.close()


def _handshake_valid(stdout: str, member: str) -> tuple[bool, str]:
    if not stdout.strip():
        return False, "process exited successfully with an empty response"
    try:
        responses = [json.loads(line) for line in stdout.splitlines() if line.strip()]
    except json.JSONDecodeError as exc:
        return False, f"response is not JSON: {exc}"
    initialized = responses[0]
    if not isinstance(initialized, dict):
        return False, "response is not a JSON-RPC object"
    if initialized.get("jsonrpc") != "2.0":
        return False, "response is not JSON-RPC 2.0"
    try:
        result = initialized["result"]
        name = result["serverInfo"]["name"]
        version = result["protocolVersion"]
        tools = result["capabilities"]["tools"]
    except (KeyError, TypeError):
        return False, "response lacks result.serverInfo, protocolVersion, or tool capabilities"
    if initialized.get("id") != 1 or name != "pipeline-team":
        return False, "response identity does not match pipeline-team request id 1"
    if version != team.MCP_PROTOCOL_VERSION or not isinstance(tools, dict):
        return False, "response protocol or tool capability is incompatible"
    if len(responses) != 3:
        return False, f"expected three protocol responses, got {len(responses)} lines"
    listed = responses[1]
    if not isinstance(listed, dict):
        return False, "tools/list response is not a JSON-RPC object"
    if listed.get("jsonrpc") != "2.0" or listed.get("id") != 2:
        return False, "tools/list response is not JSON-RPC 2.0 request id 2"
    try:
        definitions = listed["result"]["tools"]
    except (KeyError, TypeError):
        return False, "tools/list response lacks tool definitions"
    if not isinstance(definitions, list) or not all(
        isinstance(item, dict) and isinstance(item.get("name"), str)
        and isinstance(item.get("inputSchema"), dict) for item in definitions
    ):
        return False, "tools/list returned invalid tool definitions or input schemas"
    names = {item["name"] for item in definitions}
    if names != TEAM_TOOLS:
        return False, f"tools/list returned unexpected tools: {sorted(names)}"
    called = responses[2]
    if not isinstance(called, dict) or called.get("jsonrpc") != "2.0" or called.get("id") != 3:
        return False, "team_status response is not JSON-RPC 2.0 request id 3"
    try:
        tool_result = called["result"]
        status = tool_result["structuredContent"]
    except (KeyError, TypeError):
        return False, "team_status response lacks structured content"
    if (
        tool_result.get("isError") is not False
        or not isinstance(status, dict)
        or status.get("member") != member
        or status.get("grants_authority") is not False
    ):
        return False, "team_status did not execute under the configured member label"
    return True, (
        f"stdio initialize {version} listed all three tools and executed "
        f"team_status as member={member}"
    )


def check_team_handshakes(root: Path) -> list[Result]:
    root = root.resolve()
    results = []
    environment = {
        key: value for key, value in os.environ.items()
        if key not in {"GIT_INDEX_FILE", "PIPELINE_TEAM_DISCOVERY_ONLY"}
    }
    with tempfile.TemporaryDirectory(prefix="pipeline-team-preflight-") as scratch:
        test_repo = Path(scratch) / "repo"
        test_repo.mkdir()
        try:
            subprocess.run(
                ["/usr/bin/git", "init", "-q", "-b", "main"], cwd=test_repo,
                env={key: value for key, value in environment.items() if not key.startswith("GIT_")},
                stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL,
                stderr=subprocess.PIPE, text=True, timeout=10, check=True,
            )
        except (OSError, subprocess.SubprocessError) as exc:
            return [Result(member, False, f"temporary Git preflight unavailable: {exc}") for member in team.MEMBERS]
        for member in team.MEMBERS:
            try:
                config = _load_member_config(root, member)
                _validate_member_config(root, member, config)
                completed = _run_handshake(
                    [str(root / "bin/pipeline"), *config["args"], "--repo-root", str(test_repo)],
                    cwd=test_repo, env=environment,
                )
            except (OSError, ValueError, json.JSONDecodeError, tomllib.TOMLDecodeError, subprocess.SubprocessError) as exc:
                results.append(Result(member, False, f"handshake failed: {exc}"))
                continue
            if completed.returncode:
                detail = completed.stderr.strip() or "no stderr"
                results.append(Result(member, False, f"adapter exited {completed.returncode}: {detail}"))
                continue
            ok, detail = _handshake_valid(completed.stdout, member)
            results.append(Result(member, ok, detail, "inspect the app's MCP log" if not ok else ""))
    return results


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="bin/pipeline preflight")
    parser.add_argument("--repo-root", type=Path, default=Path.cwd())
    parser.add_argument("--applications", type=Path, default=Path("/Applications"))
    parser.add_argument("--agy-settings", type=Path, default=DEFAULT_AGY_SETTINGS)
    args = parser.parse_args(argv)
    root = args.repo_root.resolve()
    results = (
        check_apps(args.applications) + check_team_configs(root)
        + check_team_handshakes(root) + check_native_discovery(root)
        + [check_agy_permission(args.agy_settings)]
    )
    for result in results:
        print(f"{'PASS' if result.ok else 'FAIL'} {result.harness}: {result.detail}")
        if result.remedy:
            print(f"  remedy: {result.remedy}")
    return 0 if all(result.ok for result in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
