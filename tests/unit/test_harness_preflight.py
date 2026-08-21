from __future__ import annotations

import subprocess
from pathlib import Path
from types import SimpleNamespace

import harness_preflight as preflight


def test_codex_check_runs_config_controls_when_binary_is_absent(
    tmp_path: Path, monkeypatch
) -> None:
    """A missing binary must not stop the config controls from running.

    Asserted on meaning rather than position: an earlier version pinned the
    exact row list, so adding a control broke it for the wrong reason.
    """

    monkeypatch.setattr(preflight, "_binary", lambda _name: None)
    monkeypatch.setenv("CODEX_HOME", str(tmp_path / "absent"))
    config = tmp_path / ".codex/config.toml"
    config.parent.mkdir()
    config.write_text('sandbox_mode = "danger-full-access"\n', encoding="utf-8")

    results = preflight.check_codex(tmp_path)
    failures = [result.detail for result in results if not result.ok]

    assert any("NOT FOUND on PATH" in detail for detail in failures), failures
    assert any("sandbox_mode" in detail for detail in failures), failures


def test_codex_check_accepts_capability_neutral_project_config(
    tmp_path: Path, monkeypatch
) -> None:
    monkeypatch.setattr(preflight, "_binary", lambda _name: "/bin/codex")
    config = tmp_path / ".codex/config.toml"
    config.parent.mkdir()
    config.write_text('model = "gpt-5.6-sol"\n', encoding="utf-8")

    assert all(result.ok for result in preflight.check_codex(tmp_path))


def test_codex_check_rejects_decoded_ambient_key(
    tmp_path: Path, monkeypatch
) -> None:
    monkeypatch.setattr(preflight, "_binary", lambda _name: "/bin/codex")
    config = tmp_path / ".codex/config.toml"
    config.parent.mkdir()
    config.write_text('"approval\\u005fpolicy" = "never"\n', encoding="utf-8")

    result = preflight.check_codex(tmp_path)[1]
    assert result.ok is False
    assert "approval_policy" in result.detail


def test_codex_check_rejects_any_declared_mcp_server(
    tmp_path: Path, monkeypatch
) -> None:
    """A CLI-exclusive repo invokes peers as child processes, never as servers."""

    monkeypatch.setattr(preflight, "_binary", lambda _name: "/bin/codex")
    config = tmp_path / ".codex/config.toml"
    config.parent.mkdir()
    config.write_text(
        '[mcp_servers.anything]\ncommand = "whatever"\n', encoding="utf-8"
    )

    result = preflight.check_codex(tmp_path)[1]
    assert result.ok is False
    assert "declares MCP servers: anything" in result.detail


def test_codex_check_rejects_profile_ambient_authority(
    tmp_path: Path, monkeypatch
) -> None:
    monkeypatch.setattr(preflight, "_binary", lambda _name: "/bin/codex")
    config = tmp_path / ".codex/config.toml"
    config.parent.mkdir()
    config.write_text(
        '[profiles.loose]\n'
        'approval_policy = "never"\n'
        'sandbox_mode = "danger-full-access"\n',
        encoding="utf-8",
    )

    result = preflight.check_codex(tmp_path)[1]
    assert result.ok is False
    assert "profiles.loose.approval_policy" in result.detail
    assert "profiles.loose.sandbox_mode" in result.detail


def test_live_probe_requires_exact_positive_artifact(
    tmp_path: Path, monkeypatch
) -> None:
    expected = f"{tmp_path.resolve()}\nabc1234\n"
    monkeypatch.setattr(preflight, "_git_identity", lambda _root: expected)

    def runner(argv, **kwargs):
        assert argv == [
            "codex", "exec", "-C", str(tmp_path.resolve()),
            "--sandbox", "read-only", "-c", 'approval_policy="never"',
            'Run exactly this command once in the supplied repository and reply with ONLY stdout: "git rev-parse --show-toplevel --short HEAD"',
        ]
        assert kwargs["stdin"] is subprocess.DEVNULL
        assert all(not key.startswith("GIT_") for key in kwargs["env"])
        return SimpleNamespace(returncode=0, stdout=expected, stderr="")

    assert preflight.live_probe(tmp_path, runner=runner).ok is True


def test_live_probe_rejects_exit_zero_with_noncanonical_output(
    tmp_path: Path, monkeypatch
) -> None:
    expected = f"{tmp_path.resolve()}\nabc1234\n"
    monkeypatch.setattr(preflight, "_git_identity", lambda _root: expected)

    result = preflight.live_probe(
        tmp_path,
        runner=lambda *args, **kwargs: SimpleNamespace(
            returncode=0, stdout=expected.rstrip(), stderr=""
        ),
    )

    assert result.ok is False
    assert "no exact positive artifact" in result.detail


def test_main_fails_when_any_capability_check_fails(
    tmp_path: Path, monkeypatch
) -> None:
    monkeypatch.setattr(
        preflight,
        "check_codex",
        lambda _root: [preflight.Result("codex", False, "missing")],
    )

    assert preflight.main(["--repo-root", str(tmp_path)]) == 1


def test_peer_check_requires_both_cli_binaries(monkeypatch) -> None:
    """Neither peer can be invoked if its binary is missing from PATH."""

    monkeypatch.setattr(preflight, "_binary", lambda name: None if name == "codex" else "/bin/claude")
    results = {result.harness: result for result in preflight.check_peers()}

    assert set(results) == {"claude", "codex"}
    assert results["claude"].ok is True
    assert results["codex"].ok is False
    assert "NOT FOUND on PATH" in results["codex"].detail
    assert results["codex"].remedy == "install the codex CLI"


def test_preflight_reads_the_config_codex_actually_resolves(tmp_path, monkeypatch) -> None:
    """The project's .codex/config.toml is a declaration, not the runtime.

    Measured 2026-08-22: `codex doctor`, run inside this checkout, reported
    three MCP servers loaded from the USER config while the project file
    declared none — and one of them pointed at a command this repository had
    already deleted. A control that reads only the project file measures a
    document. This one reads what the CLI resolves.
    """

    monkeypatch.setenv("CODEX_HOME", str(tmp_path))
    (tmp_path / "config.toml").write_text(
        '[mcp_servers.dead]\ncommand = "/nonexistent/binary"\n', encoding="utf-8"
    )

    results = {result.detail: result for result in preflight.check_resolved_codex_config()}
    unresolved = [result for result in results.values() if not result.ok]

    assert unresolved, "an unresolvable MCP command must fail"
    assert "DOES NOT RESOLVE" in unresolved[0].detail
    assert "dead" in unresolved[0].detail


def test_a_disabled_server_is_not_a_failure(tmp_path, monkeypatch) -> None:
    monkeypatch.setenv("CODEX_HOME", str(tmp_path))
    (tmp_path / "config.toml").write_text(
        '[mcp_servers.off]\ncommand = "/nonexistent"\nenabled = false\n', encoding="utf-8"
    )

    results = preflight.check_resolved_codex_config()

    assert all(result.ok for result in results), [r.detail for r in results]
    assert any("disabled" in result.detail for result in results)


def test_an_absent_user_config_is_capability_not_failure(tmp_path, monkeypatch) -> None:
    """CI has no ~/.codex. A machine-local file must never fail a checkout."""

    monkeypatch.setenv("CODEX_HOME", str(tmp_path / "missing"))

    results = preflight.check_resolved_codex_config()

    assert all(result.ok for result in results)
    assert any("nothing to load" in result.detail for result in results)


def test_no_preflight_row_is_unconditionally_true(tmp_path, monkeypatch) -> None:
    """Reversion control for a green row that could not fail.

    A hardcoded `Result("codex", True, "invocation contract: ...")` passed with
    no codex binary and no config file, and asserted a contract the shipped
    peer argv does not implement. Every row must depend on something.
    """

    monkeypatch.setattr(preflight, "_binary", lambda name: None)
    monkeypatch.setenv("CODEX_HOME", str(tmp_path / "absent"))

    rows = preflight.check_peers() + preflight.check_codex(tmp_path)

    assert any(not row.ok for row in rows), "a stripped environment must fail something"
    assert not any(
        "invocation contract" in row.detail for row in rows
    ), "the unfalsifiable contract row must stay gone"
