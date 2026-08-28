from __future__ import annotations

import json
import os
import plistlib
from pathlib import Path

import pytest

import harness_preflight as preflight


def _project_configs(
    root: Path, *, extra_servers: bool = False, broad_claude_approval: bool = False,
) -> None:
    (root / "bin").mkdir(parents=True)
    (root / "bin/pipeline").write_text("#!/bin/sh\n", encoding="utf-8")
    codex = root / ".codex/config.toml"
    codex.parent.mkdir()
    codex.write_text(
        '[mcp_servers.pipeline-team]\ncommand = "./bin/pipeline"\n'
        'args = ["team", "serve", "--member", "codex"]\n'
        + (
            '\n[mcp_servers.unreviewed]\ncommand = "/tmp/unreviewed"\n'
            if extra_servers else ""
        ),
        encoding="utf-8",
    )
    servers = {
        "pipeline-team": {
            "type": "stdio",
            "command": "${CLAUDE_PROJECT_DIR:-.}/bin/pipeline",
            "args": ["team", "serve", "--member", "claude"],
        }
    }
    if extra_servers:
        servers["unreviewed"] = {"command": "/tmp/unreviewed"}
    (root / ".mcp.json").write_text(
        json.dumps({"mcpServers": servers}), encoding="utf-8"
    )
    claude = root / ".claude"
    claude.mkdir()
    (claude / "settings.json").write_text(
        json.dumps({
            "enabledMcpjsonServers": ["pipeline-team"],
            "enableAllProjectMcpServers": broad_claude_approval,
        }),
        encoding="utf-8",
    )
    plugin = root / ".agents/plugins/pipeline-team"
    plugin.mkdir(parents=True)
    (plugin / "plugin.json").write_text(
        '{"name":"pipeline-team"}\n', encoding="utf-8"
    )
    (plugin / "mcp_config.json").write_text(
        json.dumps({"mcpServers": {"pipeline-team": {
            "command": "./bin/pipeline",
            "args": ["team", "serve", "--member", "agy"],
            "cwd": ".",
        }}}),
        encoding="utf-8",
    )


def _app(applications: Path, name: str, version: str = "1.0") -> None:
    contents = applications / f"{name}.app" / "Contents"
    executable, bundle_id = {
        "ChatGPT": ("ChatGPT", "com.openai.codex"),
        "Codex": ("Codex", "com.openai.codex"),
        "Claude": ("Claude", "com.anthropic.claudefordesktop"),
        "Antigravity": ("Antigravity", "com.google.antigravity"),
        "Antigravity IDE": ("Electron", "com.google.antigravity-ide"),
    }[name]
    binary = contents / "MacOS" / executable
    binary.parent.mkdir(parents=True)
    binary.write_text("fixture\n", encoding="utf-8")
    os.chmod(binary, 0o755)
    with (contents / "Info.plist").open("wb") as handle:
        plistlib.dump({
            "CFBundleShortVersionString": version,
            "CFBundleIdentifier": bundle_id,
            "CFBundleExecutable": executable,
        }, handle)


def test_desktop_preflight_requires_all_three_apps(tmp_path: Path) -> None:
    applications = tmp_path / "Applications"
    _app(applications, "ChatGPT")
    _app(applications, "Claude")

    results = preflight.check_apps(applications)
    by_member = {result.harness: result for result in results}

    assert by_member["codex"].ok
    assert by_member["claude"].ok
    assert by_member["agy"].ok is False
    assert "Antigravity" in by_member["agy"].remedy


def test_antigravity_ide_bundle_is_a_supported_app_name(tmp_path: Path) -> None:
    applications = tmp_path / "Applications"
    _app(applications, "ChatGPT")
    _app(applications, "Claude")
    _app(applications, "Antigravity IDE", "2.0")

    results = preflight.check_apps(applications)

    assert all(result.ok for result in results)
    assert any("2.0" in result.detail for result in results if result.harness == "agy")


def test_same_named_directory_with_wrong_bundle_identity_is_rejected(
    tmp_path: Path,
) -> None:
    applications = tmp_path / "Applications"
    _app(applications, "ChatGPT")
    plist = applications / "ChatGPT.app/Contents/Info.plist"
    with plist.open("wb") as handle:
        plistlib.dump({
            "CFBundleShortVersionString": "1.0",
            "CFBundleIdentifier": "example.impostor",
            "CFBundleExecutable": "ChatGPT",
        }, handle)

    result = {row.harness: row for row in preflight.check_apps(applications)}[
        "codex"
    ]

    assert not result.ok
    assert "identity" in result.detail


def test_project_configs_bind_each_configured_label(repo_root: Path) -> None:
    results = preflight.check_team_configs(repo_root)

    assert all(result.ok for result in results), [result.detail for result in results]
    assert {result.harness for result in results} == {"codex", "claude", "agy"}


def test_project_config_rejects_unreviewed_executable_servers(
    tmp_path: Path,
) -> None:
    _project_configs(tmp_path, extra_servers=True)

    rows = {row.harness: row for row in preflight.check_team_configs(tmp_path)}

    assert not rows["codex"].ok
    assert not rows["claude"].ok
    assert rows["agy"].ok
    assert "exactly pipeline-team" in rows["codex"].detail
    assert "exactly pipeline-team" in rows["claude"].detail


def test_codex_profile_cannot_hide_an_alternate_mcp_server(tmp_path: Path) -> None:
    _project_configs(tmp_path)
    config = tmp_path / ".codex/config.toml"
    config.write_text(
        config.read_text(encoding="utf-8")
        + '\n[profiles.evasion.mcp_servers.unreviewed]\ncommand = "/tmp/unreviewed"\n',
        encoding="utf-8",
    )

    rows = {row.harness: row for row in preflight.check_team_configs(tmp_path)}

    assert not rows["codex"].ok
    assert rows["claude"].ok
    assert rows["agy"].ok
    assert "only the mcp_servers table" in rows["codex"].detail


@pytest.mark.parametrize(
    "member,key,value",
    (
        ("codex", "approval_policy", '"never"'),
        ("codex", "sandbox_mode", '"danger-full-access"'),
        ("claude", "permissions", {"allow": ["Bash(*)"]}),
    ),
)
def test_project_configs_reject_personal_or_authority_settings(
    tmp_path: Path, member: str, key: str, value: object,
) -> None:
    _project_configs(tmp_path)
    if member == "codex":
        config = tmp_path / ".codex/config.toml"
        config.write_text(
            f"{key} = {value}\n" + config.read_text(encoding="utf-8"),
            encoding="utf-8",
        )
    else:
        settings = tmp_path / ".claude/settings.json"
        payload = json.loads(settings.read_text(encoding="utf-8"))
        payload[key] = value
        settings.write_text(json.dumps(payload), encoding="utf-8")

    rows = {row.harness: row for row in preflight.check_team_configs(tmp_path)}

    assert not rows[member].ok
    assert rows[{"codex": "claude", "claude": "codex"}[member]].ok
    assert rows["agy"].ok


@pytest.mark.parametrize("broad_value", (True, 1, "true", [], {}))
def test_claude_broad_project_mcp_approval_is_rejected(
    tmp_path: Path, broad_value: object,
) -> None:
    _project_configs(tmp_path)
    settings = tmp_path / ".claude/settings.json"
    settings.write_text(
        json.dumps({
            "enabledMcpjsonServers": ["pipeline-team"],
            "enableAllProjectMcpServers": broad_value,
        }),
        encoding="utf-8",
    )

    rows = {row.harness: row for row in preflight.check_team_configs(tmp_path)}

    assert rows["codex"].ok
    assert not rows["claude"].ok
    assert rows["agy"].ok
    assert "broadly approve" in rows["claude"].detail


def test_missing_or_spoofable_config_fails(tmp_path: Path) -> None:
    (tmp_path / ".codex").mkdir()
    (tmp_path / ".codex/config.toml").write_text(
        '[mcp_servers.pipeline-team]\ncommand = "./bin/pipeline"\n'
        'args = ["team", "serve", "--member", "claude"]\n',
        encoding="utf-8",
    )
    (tmp_path / ".mcp.json").write_text('{"mcpServers": {}}\n', encoding="utf-8")

    results = preflight.check_team_configs(tmp_path)

    assert not all(result.ok for result in results)
    details = "\n".join(result.detail for result in results if not result.ok)
    assert "codex" in details and "claude" in details and "agy" in details


def test_malformed_config_is_visible_not_treated_as_absent(tmp_path: Path) -> None:
    (tmp_path / ".codex").mkdir()
    (tmp_path / ".codex/config.toml").write_text("broken = [", encoding="utf-8")
    (tmp_path / ".mcp.json").write_text("{broken", encoding="utf-8")
    (tmp_path / ".agents/plugins/pipeline-team").mkdir(parents=True)
    (tmp_path / ".agents/plugins/pipeline-team/plugin.json").write_text(
        '{"name":"pipeline-team"}\n', encoding="utf-8"
    )
    (tmp_path / ".agents/plugins/pipeline-team/mcp_config.json").write_text(
        "[]", encoding="utf-8"
    )

    results = preflight.check_team_configs(tmp_path)

    assert all(not result.ok for result in results)
    assert all("invalid" in result.detail for result in results)


def test_missing_or_malformed_agy_plugin_manifest_fails(tmp_path: Path) -> None:
    plugin = tmp_path / ".agents/plugins/pipeline-team"
    plugin.mkdir(parents=True)
    (plugin / "mcp_config.json").write_text(
        json.dumps({"mcpServers": {"pipeline-team": {
            "command": "./bin/pipeline",
            "args": ["team", "serve", "--member", "agy"],
            "cwd": ".",
        }}}),
        encoding="utf-8",
    )

    missing = {row.harness: row for row in preflight.check_team_configs(tmp_path)}
    assert not missing["agy"].ok
    assert preflight.AGY_PLUGIN_MANIFEST in missing["agy"].remedy

    (plugin / "plugin.json").write_text(
        '{"name":"not-pipeline"}\n', encoding="utf-8"
    )
    malformed = {row.harness: row for row in preflight.check_team_configs(tmp_path)}
    assert not malformed["agy"].ok
    assert "manifest name" in malformed["agy"].detail


def test_main_fails_when_any_required_app_check_fails(
    repo_root: Path, monkeypatch, capsys
) -> None:
    monkeypatch.setattr(
        preflight,
        "check_apps",
        lambda *_a: [preflight.Result("agy", False, "missing")],
    )
    monkeypatch.setattr(preflight, "check_team_configs", lambda *_a: [])
    monkeypatch.setattr(preflight, "check_team_handshakes", lambda *_a: [])
    monkeypatch.setattr(preflight, "check_native_discovery", lambda *_a: [])
    monkeypatch.setattr(
        preflight,
        "check_agy_permission",
        lambda *_a: preflight.Result("agy-permission", True, "fixture"),
    )

    assert preflight.main(["--repo-root", str(repo_root)]) == 1
    assert "FAIL agy" in capsys.readouterr().out


def test_main_requires_native_discovery_and_agy_permission(
    repo_root: Path, monkeypatch, capsys,
) -> None:
    green = preflight.Result("fixture", True, "green")
    monkeypatch.setattr(preflight, "check_apps", lambda *_a: [green])
    monkeypatch.setattr(preflight, "check_team_configs", lambda *_a: [green])
    monkeypatch.setattr(preflight, "check_team_handshakes", lambda *_a: [green])
    monkeypatch.setattr(
        preflight,
        "check_native_discovery",
        lambda *_a: [preflight.Result("agy-native-mcp", False, "not discovered")],
    )
    monkeypatch.setattr(
        preflight,
        "check_agy_permission",
        lambda *_a: preflight.Result("agy-cli-permission", True, "green"),
    )
    assert preflight.main(["--repo-root", str(repo_root)]) == 1
    assert "FAIL agy-native-mcp" in capsys.readouterr().out

    monkeypatch.setattr(preflight, "check_native_discovery", lambda *_a: [green])
    monkeypatch.setattr(
        preflight,
        "check_agy_permission",
        lambda *_a: preflight.Result("agy-cli-permission", False, "ask mode"),
    )
    assert preflight.main(["--repo-root", str(repo_root)]) == 1
    assert "FAIL agy-cli-permission" in capsys.readouterr().out


def test_every_green_row_has_a_measured_failure_mode(
    tmp_path: Path, repo_root: Path
) -> None:
    missing_apps = preflight.check_apps(tmp_path / "none")
    assert any(not row.ok for row in missing_apps)

    broken = tmp_path / "broken"
    broken.mkdir()
    config_rows = preflight.check_team_configs(broken)
    assert all(not row.ok for row in config_rows)

    # Reversion control: the real checked-in rows are independently green.
    assert all(row.ok for row in preflight.check_team_configs(repo_root))
