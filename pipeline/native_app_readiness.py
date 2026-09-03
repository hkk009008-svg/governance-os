"""Native MCP discovery proxies and the explicit AGY team permission."""
from __future__ import annotations

import json
import os
import shutil
import stat
import subprocess
from pathlib import Path
from typing import NamedTuple

import git_runner
from team_mcp import tool_definitions


SERVER = "pipeline-team"
AGY_TOOL_PERMISSION = f"mcp({SERVER}/*)"
DEFAULT_AGY_SETTINGS = Path.home() / ".gemini/antigravity-cli/settings.json"
DEFAULT_AGY_WORKSPACES = tuple(
    Path.home() / f"Library/Application Support/{name}/User/workspaceStorage"
    for name in ("Antigravity", "Antigravity IDE")
)
DEFAULT_AGY_PROJECTS = Path.home() / ".gemini/config/projects"
DEFAULT_AGY_TOOL_ROOTS = tuple(
    Path.home() / f".gemini/{name}/mcp"
    for name in ("antigravity", "antigravity-ide", "antigravity-cli")
)
AGY_PLUGIN_CONFIG = Path(".agents/plugins/pipeline-team/mcp_config.json")
AGY_PLUGIN_MANIFEST = Path(".agents/plugins/pipeline-team/plugin.json")
class NativeResult(NamedTuple):
    harness: str
    ok: bool
    detail: str
    remedy: str = ""


def _tool_payloads() -> dict[str, dict]:
    return {
        item["name"]: {
            "name": item["name"],
            "description": item["description"],
            "parameters": item["inputSchema"],
        }
        for item in tool_definitions("agy")
    }


TEAM_TOOLS = frozenset(_tool_payloads())
def _many(value: Path | tuple[Path, ...]) -> tuple[Path, ...]:
    return (value,) if isinstance(value, Path) else value


def _owned(path: Path, kind, *, private: bool = False):
    info = path.lstat()
    if (
        not kind(info.st_mode)
        or stat.S_ISLNK(info.st_mode)
        or info.st_uid != os.geteuid()
        or (private and stat.S_IMODE(info.st_mode) & 0o022)
    ):
        raise ValueError(f"{path} is not an owned trusted path")
    return info


def _command_is_repo_pipeline(root: Path, command: object) -> bool:
    if not isinstance(command, str) or not command:
        return False
    candidate = Path(command.replace("${CLAUDE_PROJECT_DIR:-.}", str(root)))
    return (candidate if candidate.is_absolute() else root / candidate).resolve() == (
        root / "bin/pipeline"
    ).resolve()


def _codex(root: Path, text: str) -> tuple[bool, str]:
    try:
        payload = json.loads(text)
    except json.JSONDecodeError:
        payload = {}
    transport = payload.get("transport") if isinstance(payload, dict) else None
    ok = (
        isinstance(transport, dict)
        and payload.get("name") == SERVER
        and payload.get("enabled") is True
        and transport.get("type") == "stdio"
        and _command_is_repo_pipeline(root, transport.get("command"))
        and transport.get("args") == ["team", "serve", "--member", "codex"]
        and transport.get("cwd") in (None, ".", str(root))
    )
    detail = "Codex natively discovers enabled pipeline-team as member=codex"
    return ok, detail if ok else "Codex does not discover the expected enabled pipeline-team"


def _claude(root: Path, text: str) -> tuple[bool, str]:
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    fields = dict(line.split(":", 1) for line in lines[1:] if ":" in line)
    fields = {key: value.strip() for key, value in fields.items()}
    ok = (
        bool(lines)
        and lines[0] == f"{SERVER}:"
        and fields.get("Scope") == "Project config (shared via .mcp.json)"
        and fields.get("Status") == "✔ Connected"
        and fields.get("Type") == "stdio"
        and _command_is_repo_pipeline(root, fields.get("Command"))
        and fields.get("Args") == "team serve --member claude"
    )
    detail = "Claude natively discovers connected pipeline-team as member=claude"
    return ok, detail if ok else "Claude has not approved and connected the expected pipeline-team"


def _agy_workspace(
    root: Path, storage: Path | tuple[Path, ...], projects: Path,
) -> tuple[bool, str]:
    expected = {path.as_uri() for path in _registration_roots(root)}
    for storage_root in _many(storage):
        for path in storage_root.glob("*/workspace.json"):
            try:
                payload = json.loads(path.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError):
                continue
            if isinstance(payload, dict) and payload.get(
                "folder", payload.get("workspace")
            ) in expected:
                return True, "Antigravity has registered this repository workspace"
    for path in projects.glob("*.json"):
        try:
            resources = json.loads(path.read_text(encoding="utf-8"))["projectResources"]["resources"]
        except (OSError, json.JSONDecodeError, KeyError, TypeError):
            continue
        if isinstance(resources, list) and any(
            item.get("gitFolder", {}).get("folderUri") in expected
            for item in resources if isinstance(item, dict)
        ):
            return True, "Antigravity has registered this repository project"
    return False, "Antigravity has not registered this repository project or workspace"


def _registration_roots(root: Path) -> tuple[Path, ...]:
    """Return this checkout and its canonical primary worktree when linked."""
    resolved = root.resolve()
    roots = [resolved]
    if not (resolved / ".git").exists():
        return tuple(roots)
    result = git_runner.run_git(
        resolved,
        ["rev-parse", "--path-format=absolute", "--git-common-dir"],
        mode="dashboard",
        text=True,
        timeout=5,
    )
    if result.returncode == 0:
        common = Path(result.stdout.strip()).resolve()
        primary = common.parent
        if primary not in roots:
            roots.append(primary)
    return tuple(roots)


def load_agy_plugin_config(root: Path) -> dict:
    """Load the exact workspace-plugin binding."""
    paths = (root / AGY_PLUGIN_MANIFEST, root / AGY_PLUGIN_CONFIG)
    for path in paths:
        try:
            _owned(path, stat.S_ISREG)
        except ValueError as exc:
            raise ValueError(f"{path.relative_to(root)} must be an owned regular file") from exc
    manifest = json.loads(paths[0].read_text(encoding="utf-8"))
    if not isinstance(manifest, dict) or manifest.get("name") != SERVER:
        raise ValueError("Antigravity plugin manifest name must be pipeline-team")
    if extras := set(manifest) - {"$schema", "name", "description"}:
        raise ValueError(f"Antigravity plugin manifest has unsupported keys: {sorted(extras)}")
    payload = json.loads(paths[1].read_text(encoding="utf-8"))
    if not isinstance(payload, dict) or set(payload) != {"mcpServers"}:
        raise ValueError("Antigravity plugin MCP config must contain only mcpServers")
    servers = payload["mcpServers"]
    if not isinstance(servers, dict) or set(servers) != {SERVER}:
        raise ValueError("Antigravity plugin must configure exactly pipeline-team")
    config = servers[SERVER]
    expected = {"command": "./bin/pipeline", "args": ["team", "serve", "--member", "agy"], "cwd": "."}
    if config != expected:
        raise ValueError("Antigravity pipeline-team binding is not the exact member=agy adapter")
    return config


def _agy_tools(root: Path, tool_roots: Path | tuple[Path, ...]) -> tuple[bool, str]:
    """Require native Antigravity tool-cache evidence newer than the plugin."""
    try:
        load_agy_plugin_config(root)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        return False, f"Antigravity workspace plugin binding is invalid: {exc}"
    expected = _tool_payloads()
    for product_root in _many(tool_roots):
        directory = product_root / SERVER
        try:
            _owned(directory, stat.S_ISDIR, private=True)
            json_names = {
                path.name for path in directory.iterdir() if path.suffix == ".json"
            }
            if json_names != {f"{tool}.json" for tool in TEAM_TOOLS}:
                raise ValueError("unexpected tool inventory")
            for tool in TEAM_TOOLS:
                path = directory / f"{tool}.json"
                _owned(path, stat.S_ISREG)
                if json.loads(path.read_text(encoding="utf-8")) != expected[tool]:
                    raise ValueError("stale or mismatched tool")
        except (OSError, ValueError, json.JSONDecodeError):
            continue
        return True, f"Antigravity native cache matches the exact {SERVER} workspace-plugin tools"
    return False, "Antigravity has no fresh native tool inventory for the pipeline-team plugin"


def check_native_discovery(
    root: Path, agy_workspaces: Path | tuple[Path, ...] = DEFAULT_AGY_WORKSPACES,
    agy_projects: Path = DEFAULT_AGY_PROJECTS,
    agy_tool_roots: Path | tuple[Path, ...] = DEFAULT_AGY_TOOL_ROOTS,
) -> list[NativeResult]:
    """Inspect native config views without launching a model."""
    checks = {
        "codex": (["mcp", "get", SERVER, "--json"], _codex),
        "claude": (["mcp", "get", SERVER], _claude),
    }
    environment = {key: value for key, value in os.environ.items() if key != "GIT_INDEX_FILE"}
    environment["CLAUDE_PROJECT_DIR"] = str(root.resolve())
    environment["PIPELINE_TEAM_DISCOVERY_ONLY"] = "1"
    results = []
    for member, (arguments, validate) in checks.items():
        executable = shutil.which(member)
        if executable is None:
            results.append(NativeResult(member, False, f"{member} CLI is unavailable for native discovery", f"install or expose the {member} app CLI on PATH"))
            continue
        try:
            completed = subprocess.run(
                [executable, *arguments], cwd=root.resolve(), env=environment,
                stdin=subprocess.DEVNULL, capture_output=True, text=True,
                timeout=15, check=False,
            )
        except (OSError, subprocess.SubprocessError) as exc:
            results.append(NativeResult(member, False, f"native discovery failed: {exc}"))
            continue
        if completed.returncode:
            detail = completed.stderr.strip() or completed.stdout.strip() or "no output"
            results.append(NativeResult(member, False, f"native discovery exited {completed.returncode}: {detail}", f"open this repository in {member} and inspect its MCP settings"))
            continue
        ok, detail = validate(root.resolve(), completed.stdout)
        results.append(NativeResult(member, ok, detail, "open this repository and approve or reload pipeline-team" if not ok else ""))
    for harness, check, remedy in (
        ("agy-registration", _agy_workspace(root, agy_workspaces, agy_projects), "open this exact folder in Antigravity, then refresh Installed MCP Servers"),
        ("agy-native-mcp", _agy_tools(root.resolve(), agy_tool_roots), "open this project and refresh its pipeline-team plugin; AGY CLI /mcp can refresh without a model"),
    ):
        ok, detail = check
        results.append(NativeResult(harness, ok, detail, remedy if not ok else ""))
    return results


def check_agy_permission(settings: Path = DEFAULT_AGY_SETTINGS) -> NativeResult:
    """Read the CLI permission needed for interruption-free AGY tool calls."""
    remedy = f"approve {AGY_TOOL_PERMISSION} in Antigravity"
    failed = lambda detail, fix=remedy: NativeResult("agy-cli-permission", False, detail, fix)
    try:
        permissions = json.loads(settings.read_text(encoding="utf-8"))["permissions"]
    except (OSError, json.JSONDecodeError, KeyError, TypeError):
        return failed("AGY CLI permission settings are missing or invalid")
    if not isinstance(permissions, dict):
        return failed("AGY CLI permissions must be an object")
    rules = {priority: permissions.get(priority, []) for priority in ("deny", "ask", "allow")}
    for priority, values in rules.items():
        if not isinstance(values, list) or not all(isinstance(item, str) for item in values):
            return failed(f"AGY CLI permissions.{priority} must be strings")
    if any("mcp(*)" in values for values in rules.values()):
        return failed("AGY CLI has an unsafe or overriding broad mcp(*) rule", f"remove mcp(*) and allow only {AGY_TOOL_PERMISSION}")
    matching = {AGY_TOOL_PERMISSION, *(f"mcp({SERVER}/{tool})" for tool in TEAM_TOOLS)}
    for priority in ("deny", "ask"):
        if matching.intersection(rules[priority]):
            return failed(f"AGY CLI {priority} rules override the pipeline-team allow")
    if AGY_TOOL_PERMISSION in rules["allow"]:
        return NativeResult("agy-cli-permission", True, f"AGY CLI allows global name scope {AGY_TOOL_PERMISSION}; avoid same-named untrusted servers")
    return failed("AGY CLI will ask before pipeline-team tool calls")
