from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path

import native_app_readiness as native


def _outputs() -> dict[str, str]:
    return {
        "codex": json.dumps({
            "name": "pipeline-team",
            "enabled": True,
            "transport": {
                "type": "stdio",
                "command": "./bin/pipeline",
                "args": ["team", "serve", "--member", "codex"],
                "cwd": None,
            },
        }),
        "claude": (
            "pipeline-team:\n"
            "  Scope: Project config (shared via .mcp.json)\n"
            "  Status: ✔ Connected\n"
            "  Type: stdio\n"
            "  Command: ${CLAUDE_PROJECT_DIR:-.}/bin/pipeline\n"
            "  Args: team serve --member claude\n"
        ),
    }


def _install_fakes(monkeypatch, outputs: dict[str, str]) -> None:
    monkeypatch.setattr(native.shutil, "which", lambda member: f"/bin/{member}")
    monkeypatch.setattr(
        native.subprocess,
        "run",
        lambda argv, **_kwargs: subprocess.CompletedProcess(
            argv, 0, outputs[Path(argv[0]).name], ""
        ),
    )


def _agy_plugin(root: Path) -> None:
    manifest = root / native.AGY_PLUGIN_MANIFEST
    config = root / native.AGY_PLUGIN_CONFIG
    config.parent.mkdir(parents=True, exist_ok=True)
    manifest.write_text(
        json.dumps({"name": native.SERVER}) + "\n", encoding="utf-8"
    )
    config.write_text(
        json.dumps({"mcpServers": {native.SERVER: {
            "command": "./bin/pipeline",
            "args": ["team", "serve", "--member", "agy"],
            "cwd": ".",
        }}}) + "\n",
        encoding="utf-8",
    )


def _native_tools(root: Path, tools_root: Path) -> None:
    _agy_plugin(root)
    directory = tools_root / native.SERVER
    directory.mkdir(parents=True)
    for tool, payload in native._tool_payloads().items():
        (directory / f"{tool}.json").write_text(
            json.dumps(payload),
            encoding="utf-8",
        )


def test_native_products_discover_expected_project_server(
    tmp_path: Path, monkeypatch,
) -> None:
    _install_fakes(monkeypatch, _outputs())
    projects = tmp_path / "projects"
    projects.mkdir()
    (projects / "pipeline.json").write_text(
        json.dumps({"projectResources": {"resources": [
            {"gitFolder": {"folderUri": tmp_path.resolve().as_uri()}}
        ]}}),
        encoding="utf-8",
    )
    tools = tmp_path / "tools"
    _native_tools(tmp_path, tools)

    results = native.check_native_discovery(
        tmp_path, tmp_path / "storage", projects, tools
    )

    assert all(result.ok for result in results), results
    assert {result.harness for result in results} == {
        "codex", "claude", "agy-registration", "agy-native-mcp"
    }


def test_registration_does_not_substitute_for_native_tool_discovery(
    tmp_path: Path, monkeypatch,
) -> None:
    _install_fakes(monkeypatch, _outputs())
    projects = tmp_path / "projects"
    projects.mkdir()
    (projects / "pipeline.json").write_text(
        json.dumps({"projectResources": {"resources": [
            {"gitFolder": {"folderUri": tmp_path.resolve().as_uri()}}
        ]}}),
        encoding="utf-8",
    )
    _agy_plugin(tmp_path)

    results = {row.harness: row for row in native.check_native_discovery(
        tmp_path, tmp_path / "storage", projects, tmp_path / "empty-tools"
    )}

    assert results["agy-registration"].ok
    assert not results["agy-native-mcp"].ok
    assert "no fresh native tool inventory" in results["agy-native-mcp"].detail


def test_both_antigravity_workspace_storage_roots_are_supported(
    tmp_path: Path,
) -> None:
    ide_storage = tmp_path / "Antigravity IDE/User/workspaceStorage"
    workspace = ide_storage / "hash"
    workspace.mkdir(parents=True)
    (workspace / "workspace.json").write_text(
        json.dumps({"folder": tmp_path.resolve().as_uri()}), encoding="utf-8"
    )

    ok, detail = native._agy_workspace(
        tmp_path,
        (tmp_path / "Antigravity/User/workspaceStorage", ide_storage),
        tmp_path / "projects",
    )

    assert ok and "workspace" in detail


def test_linked_worktree_accepts_primary_workspace_registration(
    tmp_path: Path,
) -> None:
    primary = tmp_path / "primary"
    linked = tmp_path / "linked"
    primary.mkdir()
    subprocess.run(["git", "init", "-q"], cwd=primary, check=True)
    subprocess.run(
        ["git", "config", "user.email", "test@example.com"],
        cwd=primary,
        check=True,
    )
    subprocess.run(
        ["git", "config", "user.name", "Test"], cwd=primary, check=True
    )
    (primary / "tracked.txt").write_text("base\n", encoding="utf-8")
    subprocess.run(["git", "add", "tracked.txt"], cwd=primary, check=True)
    subprocess.run(["git", "commit", "-q", "-m", "base"], cwd=primary, check=True)
    subprocess.run(
        ["git", "worktree", "add", "-q", "--detach", str(linked)],
        cwd=primary,
        check=True,
    )
    storage = tmp_path / "storage" / "hash"
    storage.mkdir(parents=True)
    (storage / "workspace.json").write_text(
        json.dumps({"folder": primary.resolve().as_uri()}), encoding="utf-8"
    )

    ok, detail = native._agy_workspace(
        linked, tmp_path / "storage", tmp_path / "projects"
    )

    assert ok and "workspace" in detail


def test_native_cli_checks_reject_wrong_command_and_scope(
    tmp_path: Path, monkeypatch,
) -> None:
    outputs = _outputs()
    codex = json.loads(outputs["codex"])
    codex["transport"]["command"] = "/tmp/not-pipeline"
    outputs["codex"] = json.dumps(codex)
    outputs["claude"] = outputs["claude"].replace(
        "Scope: Project config (shared via .mcp.json)", "Scope: User config"
    )
    _install_fakes(monkeypatch, outputs)
    plugin = tmp_path / native.AGY_PLUGIN_CONFIG
    plugin.parent.mkdir(parents=True)
    plugin.write_text('{}\n', encoding="utf-8")

    rows = {row.harness: row for row in native.check_native_discovery(
        tmp_path, tmp_path / "storage", tmp_path / "projects", tmp_path / "tools"
    )}

    assert not rows["codex"].ok
    assert not rows["claude"].ok


def test_identical_native_tools_survive_newer_checkout_mtime(tmp_path: Path) -> None:
    tools = tmp_path / "tools"
    _native_tools(tmp_path, tools)
    config = tmp_path / native.AGY_PLUGIN_CONFIG
    future = config.stat().st_mtime_ns + 2_000_000_000
    os.utime(config, ns=(future, future))

    ok, detail = native._agy_tools(tmp_path, tools)

    assert ok and "exact" in detail


def test_tampered_native_tool_schema_is_rejected(tmp_path: Path) -> None:
    tools = tmp_path / "tools"
    _native_tools(tmp_path, tools)
    tampered = tools / native.SERVER / "team_send.json"
    payload = json.loads(tampered.read_text(encoding="utf-8"))
    payload["parameters"] = {"type": "object"}
    tampered.write_text(json.dumps(payload), encoding="utf-8")

    ok, detail = native._agy_tools(tmp_path, tools)

    assert not ok and "no fresh" in detail


def test_extra_native_tool_is_rejected_from_exact_inventory(tmp_path: Path) -> None:
    tools = tmp_path / "tools"
    _native_tools(tmp_path, tools)
    (tools / native.SERVER / "dangerous_extra.json").write_text(
        '{"name":"dangerous_extra"}\n', encoding="utf-8"
    )

    ok, detail = native._agy_tools(tmp_path, tools)

    assert not ok and "no fresh" in detail


def test_non_tool_plugin_instructions_do_not_expand_tool_inventory(
    tmp_path: Path,
) -> None:
    tools = tmp_path / "tools"
    _native_tools(tmp_path, tools)
    (tools / native.SERVER / "instructions.md").write_text(
        "Use the three declared team tools.\n", encoding="utf-8"
    )

    ok, detail = native._agy_tools(tmp_path, tools)

    assert ok and "exact" in detail


def test_native_discovery_pins_repository_and_disables_team_operations(
    tmp_path: Path, monkeypatch,
) -> None:
    outputs = _outputs()
    observed: list[tuple[Path, dict[str, str]]] = []

    def run(argv, **kwargs):
        observed.append((Path(kwargs["cwd"]), kwargs["env"]))
        return subprocess.CompletedProcess(
            argv, 0, outputs[Path(argv[0]).name], ""
        )

    monkeypatch.setattr(native.shutil, "which", lambda member: f"/bin/{member}")
    monkeypatch.setattr(native.subprocess, "run", run)
    monkeypatch.setenv("CLAUDE_PROJECT_DIR", "/tmp/untrusted-project")
    monkeypatch.setenv("GIT_INDEX_FILE", "/tmp/untrusted-index")

    rows = native.check_native_discovery(
        tmp_path, tmp_path / "storage", tmp_path / "projects", tmp_path / "tools"
    )

    assert all(row.ok for row in rows if row.harness in {"codex", "claude"})
    assert len(observed) == 2
    for cwd, environment in observed:
        assert cwd == tmp_path.resolve()
        assert environment["CLAUDE_PROJECT_DIR"] == str(tmp_path.resolve())
        assert environment["PIPELINE_TEAM_DISCOVERY_ONLY"] == "1"
        assert "GIT_INDEX_FILE" not in environment


def test_malformed_json_shapes_fail_closed_without_crashing(tmp_path: Path) -> None:
    assert native._codex(tmp_path, '{"transport": []}')[0] is False

    tools = tmp_path / "tools"
    _native_tools(tmp_path, tools)
    (tools / native.SERVER / "team_status.json").write_text(
        "[]", encoding="utf-8"
    )
    assert native._agy_tools(tmp_path, tools)[0] is False

    settings = tmp_path / "settings.json"
    settings.write_text('{"permissions": []}', encoding="utf-8")
    assert native.check_agy_permission(settings).ok is False


def test_agy_permission_honors_deny_ask_allow_precedence(tmp_path: Path) -> None:
    settings = tmp_path / "settings.json"

    def observed(permissions: dict) -> native.NativeResult:
        settings.write_text(json.dumps({"permissions": permissions}), encoding="utf-8")
        return native.check_agy_permission(settings)

    assert not observed({"allow": ["command(git status)"]}).ok
    assert not observed({
        "allow": [native.AGY_TOOL_PERMISSION], "ask": [native.AGY_TOOL_PERMISSION]
    }).ok
    assert not observed({
        "allow": [native.AGY_TOOL_PERMISSION], "deny": [native.AGY_TOOL_PERMISSION]
    }).ok
    assert not observed({
        "allow": [native.AGY_TOOL_PERMISSION, "mcp(*)"]
    }).ok
    assert not observed({
        "allow": [native.AGY_TOOL_PERMISSION], "ask": ["mcp(*)"]
    }).ok
    assert observed({"allow": [native.AGY_TOOL_PERMISSION]}).ok
