"""Tests for the local per-seat AGY (Antigravity) launcher."""

from __future__ import annotations

import json
import re
import shutil
import subprocess
from pathlib import Path

import pytest

from scripts import agy_seat_launcher as launcher


SEATS = ("director", "director2", "operator", "operator2", "coordinator")


def _write_config(path: Path, overrides: dict[str, tuple[str, str]] | None = None) -> None:
    settings = {seat: (f"gemini-{seat}", "default") for seat in SEATS}
    settings.update(overrides or {})
    blocks = []
    for seat, (model, tier) in settings.items():
        blocks.append(f'[seats.{seat}]\nmodel = "{model}"\nservice_tier = "{tier}"\n')
    path.write_text("\n".join(blocks), encoding="utf-8")


def _settings(tmp_path: Path, overrides=None):
    config_path = tmp_path / "seats.toml"
    _write_config(config_path, overrides)
    return launcher.load_seat_settings(config_path)


def test_build_launch_spec_defaults_to_single_model_autonomous_and_cleans_authority(
    tmp_path: Path,
) -> None:
    ambient = {
        "PATH": "/bin",
        "AGY_SEAT": "wrong-seat",
        "AGY_AGENT_MODE": "wrong-mode",
        "AGY_AGENT_ROLE": "wrong-role",
        "AGY_BEHAVIOR_SOURCE": "wrong-source",
        "AGY_UNKNOWN_FUTURE_FIELD": "stale",
        "AGY_API_KEY": "agy-test-key",
        "CLAUDE_CODE_ENTRYPOINT": "foreign-authority",
        "CURSOR_SEAT": "operator",
        "CODEX_SEAT": "director",
        "CODEX_AGENT_MODE": "live-seat",
        "ANTIGRAVITY_SEAT": "director2",
        "GIT_INDEX_FILE": "/wrong-index",
        "GIT_DIR": "/foreign/git",
        "GIT_WORK_TREE": "/foreign/tree",
    }

    spec = launcher.build_launch_spec(
        repo_root=tmp_path,
        seat="director",
        settings=_settings(tmp_path),
        inherited_env=ambient,
        agy_executable="/opt/agy",
        forwarded_args=[],
    )

    assert spec.env["AGY_SEAT"] == "agy-unit-director"
    assert spec.env["AGY_AGENT_MODE"] == "single-model-autonomous"
    assert spec.env["AGY_AGENT_ROLE"] == "agy-unit-director"
    assert spec.env["AGY_BEHAVIOR_SOURCE"] == "agy-unit-director"
    assert spec.env["AGY_API_KEY"] == "agy-test-key"
    assert spec.env["PATH"] == "/bin"
    assert not any(
        key.startswith(("CLAUDE_", "CURSOR_", "CODEX_", "ANTIGRAVITY_"))
        for key in spec.env
    )
    assert "AGY_UNKNOWN_FUTURE_FIELD" not in spec.env
    assert "GIT_DIR" not in spec.env
    assert "GIT_WORK_TREE" not in spec.env


def test_launch_spec_binds_no_index_and_scrubs_inherited_git_authority(
    tmp_path: Path,
) -> None:
    """A launched AGY process uses the worktree's native index.

    The launcher used to seed `.git/index-agy-<seat>` and export
    `GIT_INDEX_FILE`, which made seat identity a property of an inherited
    environment variable that any process can forge. Codex's launcher never did
    this and Claude's was retired; AGY now matches. An inherited GIT_* value is
    dropped rather than replaced, so nothing downstream inherits a stale index.
    """
    spec = launcher.build_launch_spec(
        repo_root=tmp_path,
        seat="operator",
        settings=_settings(tmp_path),
        inherited_env={"PATH": "/bin", "GIT_INDEX_FILE": "/stale-index"},
        agy_executable="/opt/agy",
        forwarded_args=[],
    )

    assert "GIT_INDEX_FILE" not in spec.env
    assert "AGY_GIT_INDEX_FILE" not in spec.env
    assert not any(key.startswith("GIT_") for key in spec.env)
    assert not hasattr(spec, "index_path")


def test_retired_index_seeding_helpers_are_absent() -> None:
    assert not hasattr(launcher, "ensure_seat_index")
    assert not hasattr(launcher, "resolve_git_dir")


def test_build_launch_spec_requires_explicit_isolated_mode_for_agy_unit(
    tmp_path: Path,
) -> None:
    spec = launcher.build_launch_spec(
        repo_root=tmp_path,
        seat="director",
        settings=_settings(tmp_path),
        inherited_env={"PATH": "/bin"},
        agy_executable="/opt/agy",
        forwarded_args=[],
        mode=launcher.ADVISORY_MODE,
    )

    assert spec.env["AGY_SEAT"] == "agy-advisory"
    assert spec.env["AGY_AGENT_MODE"] == "advisory-readiness"
    assert spec.env["AGY_AGENT_ROLE"] == "readiness-bridge"
    assert spec.mode == launcher.ADVISORY_MODE


def test_build_launch_spec_rejects_unknown_agy_mode(tmp_path: Path) -> None:
    with pytest.raises(launcher.LaunchError, match="unsupported AGY mode"):
        launcher.build_launch_spec(
            repo_root=tmp_path,
            seat="director",
            settings=_settings(tmp_path),
            inherited_env={"PATH": "/bin"},
            agy_executable="/opt/agy",
            forwarded_args=[],
            mode="not-a-mode",
        )


def test_build_launch_spec_rejects_unknown_seat(tmp_path: Path) -> None:
    with pytest.raises(launcher.LaunchError, match="unsupported seat"):
        launcher.build_launch_spec(
            repo_root=tmp_path,
            seat="intruder",
            settings=_settings(tmp_path),
            inherited_env={"PATH": "/bin"},
            agy_executable="/opt/agy",
            forwarded_args=[],
        )


def test_each_seat_uses_only_its_own_model(tmp_path: Path) -> None:
    """Model is the only per-seat control the CLI can actually apply.

    `service_tier` was mandatory, validated and advertised as a speed control
    while nothing consumed it: changing `fast` to `default` altered no launch
    behaviour. A validated setting that selects nothing is a false capability,
    so it is no longer part of the settings a seat carries.
    """
    overrides = {seat: (f"model-{seat}", "default") for seat in SEATS}
    settings = _settings(tmp_path, overrides)

    for seat in SEATS:
        spec = launcher.build_launch_spec(
            repo_root=tmp_path,
            seat=seat,
            settings=settings,
            inherited_env={"PATH": "/bin"},
            agy_executable="/opt/agy",
            forwarded_args=[],
        )
        assert f"model-{seat}" in spec.argv
        assert not any("service_tier" in token for token in spec.argv)
        assert not hasattr(settings[seat], "service_tier")


def test_a_stale_service_tier_still_loads_and_is_ignored(tmp_path: Path) -> None:
    """Existing configs must keep working; the field simply selects nothing."""
    config_path = tmp_path / "seats.toml"
    _write_config(config_path, {seat: (f"model-{seat}", "fast") for seat in SEATS})

    settings = launcher.load_seat_settings(config_path)

    assert set(settings) == set(SEATS)
    assert all(not hasattr(value, "service_tier") for value in settings.values())


def test_forwarded_agy_arguments_remain_literal(tmp_path: Path) -> None:
    forwarded = ["--resume", "--", "weird arg with spaces", "$(touch pwned)"]

    spec = launcher.build_launch_spec(
        repo_root=tmp_path,
        seat="director",
        settings=_settings(tmp_path),
        inherited_env={"PATH": "/bin"},
        agy_executable="/opt/agy",
        forwarded_args=forwarded,
    )

    assert list(spec.argv)[-len(forwarded) :] == forwarded


@pytest.mark.parametrize(
    "body",
    (
        '[seats.director]\nmodel = "m"\nservice_tier = "default"\n',
        '[seats]\n',
        '[other]\nkey = "value"\n',
    ),
)
def test_config_rejects_incomplete_or_unknown_settings(tmp_path: Path, body: str) -> None:
    config_path = tmp_path / "seats.toml"
    config_path.write_text(body, encoding="utf-8")

    with pytest.raises(launcher.ConfigError):
        launcher.load_seat_settings(config_path)


def test_config_rejects_bad_model(tmp_path: Path) -> None:
    """Model is still strictly validated; only the inert tier stopped being.

    An arbitrary tier value is now accepted precisely because it selects
    nothing — rejecting `turbo` would be the launcher pretending to gate a
    control it does not apply.
    """
    for overrides in (
        {"director": ("", "default")},
        {"director": (" leading-space", "default")},
    ):
        config_path = tmp_path / "seats.toml"
        _write_config(config_path, overrides)
        with pytest.raises(launcher.ConfigError):
            launcher.load_seat_settings(config_path)


def test_config_still_rejects_unknown_per_seat_keys(tmp_path: Path) -> None:
    config_path = tmp_path / "seats.toml"
    config_path.write_text(
        "\n".join(
            f'[seats.{seat}]\nmodel = "m"\nspeed = "fast"\n' for seat in SEATS
        ),
        encoding="utf-8",
    )

    with pytest.raises(launcher.ConfigError):
        launcher.load_seat_settings(config_path)


def test_dry_run_prints_identity_and_does_not_start_agy(
    tmp_path: Path, capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch
) -> None:
    config_path = tmp_path / "seats.toml"
    _write_config(config_path)

    def _fail(*args, **kwargs):  # pragma: no cover - must never run
        raise AssertionError("dry run must not exec the provider")

    monkeypatch.setattr(launcher.os, "execvpe", _fail)

    code = launcher.main(["--dry-run", "--config", str(config_path), "director"])

    assert code == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["env"]["AGY_SEAT"] == "agy-unit-director"
    assert "GIT_INDEX_FILE" not in payload["env"]
    assert "index_exists" not in payload


def test_agy_guides_never_teach_manual_index_binding(repo_root: Path) -> None:
    """The doc-side counterpart to the launcher's no-index assertion.

    `test_launch_spec_binds_no_index_and_scrubs_inherited_git_authority` proves
    the launcher exports no `GIT_INDEX_FILE`, but a seat reads its guides too. A
    stale guide bullet survived the `09d04fb` retirement telling AGY seats they
    each own `.git/index-agy-<seat>`; a seat obeying it hand-rolls
    `export GIT_INDEX_FILE=...`, which silently rebinds every later Git command
    in the session including commits, and follows `cd` into unrelated
    repositories.

    `.agy/agents/*.toml` is covered by `test_agy_agent_surfaces.py` and the
    Claude guides by `test_claude_seat_launcher.py`. These two trees were the
    uncovered surface, which is why the drift landed here.
    """
    guides: list[Path] = []
    for root in (repo_root / ".agents/skills", repo_root / "docs/protocol/agy"):
        # rglob and a per-root nonempty check, not a combined one: a plain glob
        # lets a nested stale guide through, and a combined check stays green
        # when one root disappears because the other still supplies files.
        found = sorted(root.rglob("*.md"))
        assert found, f"no guides under {root.relative_to(repo_root)}"
        guides.extend(found)

    for guide in guides:
        text = guide.read_text(encoding="utf-8")
        relative = guide.relative_to(repo_root)
        assert "export GIT_INDEX_FILE=" not in text, relative
        for retired in ("index-agy-", "index-claude-", "index-codex-", "index-cursor-"):
            assert retired not in text, f"{relative}: {retired}"


def test_continuation_documents_read_only_bridge_and_stdin_writer(
    repo_root: Path,
) -> None:
    """The AGY adapter states the same two things every other adapter states.

    The `--mode single-model-autonomous` flag assertion was retired with the
    flag itself: AGY's direct-autonomous default made it unnecessary, and the
    string only survived inside a sentence saying it was not required.
    """
    text = (repo_root / "docs/protocol/agy/continuation.md").read_text(
        encoding="utf-8"
    )

    assert "no role claim or durable mutation" in text
    assert (
        "coordination/bin/send-event <sender> <recipient> <kind> <subject...>" in text
    )
    assert "<body-file>" not in text
    assert "scripts/codex_protocol_model.py" in text


def test_launcher_emits_only_flags_the_agy_cli_defines(tmp_path: Path) -> None:
    """The launcher and the binary are separate artifacts that can disagree.

    `--config` and `--cd` were emitted here for every seat while the installed
    CLI defined neither, so `coordination/bin/agy-seat <seat>` died at argument
    parsing before any model call. Nothing in the repository could observe that:
    the launcher was internally consistent and fully tested against itself.
    """
    config_path = tmp_path / "seats.toml"
    _write_config(config_path)
    settings = launcher.load_seat_settings(config_path)

    for seat in SEATS:
        spec = launcher.build_launch_spec(
            repo_root=tmp_path,
            seat=seat,
            settings=settings,
            inherited_env={"PATH": "/bin"},
            agy_executable="/opt/agy",
            forwarded_args=[],
        )
        emitted = {token for token in spec.argv if token.startswith("--")}
        assert emitted, seat
        assert emitted <= launcher.AGY_CLI_FLAGS, (seat, emitted - launcher.AGY_CLI_FLAGS)


CLI_FLAG_SNAPSHOT = Path(__file__).resolve().parents[1] / "fixtures/agy-cli-flags.txt"


def _snapshot_flags() -> set[str]:
    return {
        line.strip()
        for line in CLI_FLAG_SNAPSHOT.read_text(encoding="utf-8").splitlines()
        if line.strip()
    }


def test_declared_agy_flag_set_matches_the_committed_cli_snapshot() -> None:
    """Always runs, including where the CLI is absent.

    The previous form skipped when `agy` was missing, and the unit job installs
    only `requirements-dev.txt` — so a flag added to both the argv and
    `AGY_CLI_FLAGS`, or removed upstream, passed CI untouched. Checking against
    a committed snapshot of the real `--help` keeps a real assertion in every
    environment; `test_cli_snapshot_matches_the_installed_cli` is what keeps the
    snapshot itself honest wherever the binary exists.
    """
    defined = _snapshot_flags()

    assert defined, "the committed CLI snapshot is empty"
    assert launcher.AGY_CLI_FLAGS <= defined, launcher.AGY_CLI_FLAGS - defined


def test_cli_snapshot_matches_the_installed_cli() -> None:
    """Catch upstream drift where the binary exists; never the only guard."""
    executable = shutil.which("agy") or shutil.which("antigravity")
    if executable is None:
        pytest.skip("agy CLI absent; the snapshot assertion above still ran")

    helped = subprocess.run(
        [executable, "--help"], capture_output=True, text=True, check=False
    )
    text = helped.stdout + helped.stderr
    defined = set(re.findall(r"^\s+(--[a-z][a-z0-9-]*)", text, re.MULTILINE))

    assert defined, "could not parse any flags from agy --help"
    drifted = _snapshot_flags() - defined
    assert not drifted, (
        f"tests/fixtures/agy-cli-flags.txt lists flags the CLI no longer defines: "
        f"{sorted(drifted)}"
    )
