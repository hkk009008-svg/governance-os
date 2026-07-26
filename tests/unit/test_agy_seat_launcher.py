"""Tests for the local per-seat AGY (Antigravity) launcher."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
from pathlib import Path

import pytest

from scripts import agy_seat_launcher as launcher
from scripts import codex_protocol_model


SEATS = ("director", "director2", "operator", "operator2", "coordinator")

# Go's `flag` package aborts the whole invocation on the first undefined flag
# and prints this. It is the marker that makes the probe below a real check.
UNDEFINED_FLAG_MARKER = "flags provided but not defined"

_AGY_ON_PATH = shutil.which("agy")


def _parse_probe(flags: list[str]) -> subprocess.CompletedProcess[str]:
    """Run `agy <flags> models`: real flag parsing, no UI and no model call.

    `models` is a local listing subcommand, so a fully-defined command line
    exits 0 having printed the model list, while an undefined flag anywhere
    ahead of it still fails with `UNDEFINED_FLAG_MARKER`.

    A trailing argument-hungry flag such as `--print` is not usable as the
    terminator: for at least some argv shapes AGY reports the missing argument
    instead of the undefined flag, which masks exactly the defect the probe
    exists to catch. `models` was checked against both retired flags and masks
    neither.

    `start_new_session` leaves the child without a controlling terminal, so it
    cannot fall through to the interactive UI and hang when pytest itself is
    run from a real terminal.
    """
    return subprocess.run(
        [str(_AGY_ON_PATH), *flags, *launcher.MODEL_LISTING_COMMAND[1:]],
        stdin=subprocess.DEVNULL,
        capture_output=True,
        text=True,
        timeout=launcher.MODEL_LISTING_TIMEOUT_SECONDS,
        start_new_session=True,
        check=False,
    )


def _canonical_model() -> str:
    """The committed model string; compared against the live listing, not from it."""
    return launcher.REFERENCE_MODEL


def _listing_probe() -> tuple[frozenset[str], str]:
    """Return the live model listing, or why this machine cannot produce one."""
    if _AGY_ON_PATH is None:
        return frozenset(), "installed agy CLI not on PATH"
    try:
        return launcher.list_models(str(_AGY_ON_PATH)), ""
    except launcher.LaunchError as exc:
        return frozenset(), str(exc)


_LIVE_LISTING, _LIVE_BLOCKED_REASON = _listing_probe()

# pytest prints only the first line of a skip reason, and the launcher error
# deliberately carries the whole stderr stream, so the cause has to be folded
# onto one line or `-rs` shows a bare "cannot be checked:" and hides it.
_LIVE_BLOCKED_SUMMARY = " ".join(_LIVE_BLOCKED_REASON.split())

# Whether missing live coverage may pass silently is decided structurally, never
# by reading AGY's error text. Two earlier attempts classified the message and
# both were wrong in the same direction: keying on one rejection phrase let any
# other refusal skip, and an allowlist of "environmental" substrings let an
# interface rejection reading `Permission denied` skip too. Vendor prose is not
# a trustworthy signal, so nothing here parses it.
#
# `agy` absent from PATH is structural and unambiguous -- the ordinary CI case,
# and safe to skip. An `agy` that is present but cannot produce a listing is not
# distinguishable from one that refused our command, so it fails unless a human
# waives it for a known-constrained environment.
_LIVE_WAIVER_ENV = "PIPELINE_AGY_LIVE_TESTS"
_LIVE_WAIVED = os.environ.get(_LIVE_WAIVER_ENV, "").strip().casefold() == "waive"

# Skipping still suppresses the whole live group, so one clear failure names the
# problem instead of a cascade -- see
# `test_live_listing_is_available_absent_or_explicitly_waived`, which always
# runs. The hermetic tests never skip at all.
_needs_agy = pytest.mark.skipif(
    not _LIVE_LISTING,
    reason=f"cannot run the live agy listing: {_LIVE_BLOCKED_SUMMARY}",
)


def _emitted_flags(argv: tuple[str, ...]) -> set[str]:
    """Return the flag tokens the launcher itself put on the command line."""
    return {token for token in argv[1:] if token.startswith("-")}


def _stub_installed_cli(
    monkeypatch: pytest.MonkeyPatch, listed: tuple[str, ...] | None = None
) -> None:
    """Make `main` independent of whether AGY is installed on this machine.

    `main` resolves the executable and checks the seat model against the live
    listing, so without this a test of chdir/exec ordering silently turns into
    a test of whether the developer happens to have AGY on PATH. The default
    listing accepts exactly what `_write_config` writes.
    """
    if listed is None:
        listed = tuple(f"gemini-{seat}" for seat in SEATS) + (launcher.REFERENCE_MODEL,)
    monkeypatch.setattr(launcher.shutil, "which", lambda name: "/opt/agy")
    monkeypatch.setattr(launcher, "list_models", lambda executable: frozenset(listed))


def _write_config(path: Path, overrides: dict[str, tuple[str, str]] | None = None) -> None:
    settings = {seat: (f"gemini-{seat}", "high") for seat in SEATS}
    settings.update(overrides or {})
    blocks = []
    for seat, (model, effort) in settings.items():
        blocks.append(f'[seats.{seat}]\nmodel = "{model}"\neffort = "{effort}"\n')
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


def test_each_seat_uses_only_its_own_model_and_effort(tmp_path: Path) -> None:
    overrides = {seat: (f"model-{seat}", "low" if seat == "coordinator" else "high") for seat in SEATS}
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
        argv = list(spec.argv)
        expected_effort = "low" if seat == "coordinator" else "high"
        assert argv[argv.index("--model") + 1] == f"model-{seat}"
        assert argv[argv.index("--effort") + 1] == expected_effort


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


def test_emitted_flags_are_exactly_the_declared_cli_flag_set(tmp_path: Path) -> None:
    """The launcher may only emit flags it has declared the CLI defines.

    This is the hermetic half of the anti-rot check and always runs. It is an
    exact set comparison, so adding an undeclared flag and silently dropping a
    declared one both fail here, on any machine, with no `agy` installed.
    """
    spec = launcher.build_launch_spec(
        repo_root=tmp_path,
        seat="operator",
        settings=_settings(tmp_path),
        inherited_env={"PATH": "/bin"},
        agy_executable="/opt/agy",
        forwarded_args=[],
    )

    assert launcher.EMITTED_CLI_FLAGS, "the declared flag set must not be empty"
    assert _emitted_flags(spec.argv) == set(launcher.EMITTED_CLI_FLAGS)


@pytest.mark.parametrize(
    "override",
    (
        ["--model", "definitely-not-an-agy-model"],
        ["--model=definitely-not-an-agy-model"],
        # Go accepts the single-dash spelling identically.
        ["-model", "definitely-not-an-agy-model"],
        ["-model=definitely-not-an-agy-model"],
        ["--effort", "low"],
        ["--add-dir", "/somewhere/else"],
    ),
)
def test_forwarded_arguments_cannot_restate_a_launcher_owned_flag(
    tmp_path: Path, override: list[str]
) -> None:
    """Forwarding must not be able to redefine the seat's own identity.

    Forwarded tokens land after the launcher's flags and AGY honours the last
    occurrence, so `agy-seat operator -- --model X` ran on X while `AGY_MODEL`
    still advertised the configured model. Checking the config value alone
    never saw it: the config was fine, the command line was not.
    """
    with pytest.raises(launcher.LaunchError, match="restates"):
        launcher.build_launch_spec(
            repo_root=tmp_path,
            seat="operator",
            settings=_settings(tmp_path),
            inherited_env={"PATH": "/bin"},
            agy_executable="/opt/agy",
            forwarded_args=override,
        )


def test_forwarding_still_carries_prompts_and_other_agy_flags(tmp_path: Path) -> None:
    """The guard is aimed at identity, not at forwarding generally."""
    forwarded = ["--dangerously-skip-permissions", "-p", "continue as operator"]

    spec = launcher.build_launch_spec(
        repo_root=tmp_path,
        seat="operator",
        settings=_settings(tmp_path),
        inherited_env={"PATH": "/bin"},
        agy_executable="/opt/agy",
        forwarded_args=forwarded,
    )

    assert list(spec.argv)[-len(forwarded) :] == forwarded


def test_live_listing_is_available_absent_or_explicitly_waived() -> None:
    """Silent loss of live coverage is the failure this prevents.

    An installed `agy` that cannot produce a listing is indistinguishable from
    one refusing the command this suite sends, and that second case is exactly
    the interface rot the live tests exist to catch. Two earlier versions tried
    to tell them apart from AGY's error text and both let a refusal through as a
    green skip, so no message is read here at all: a present-but-failing CLI
    fails until a human sets the waiver for a known-constrained environment.
    """
    if _LIVE_LISTING or _AGY_ON_PATH is None or _LIVE_WAIVED:
        return
    raise AssertionError(
        f"agy is installed at {_AGY_ON_PATH} but produced no model listing, so the "
        f"live checks covered nothing. Set {_LIVE_WAIVER_ENV}=waive to accept that "
        f"knowingly. Cause: {_LIVE_BLOCKED_SUMMARY}"
    )


@pytest.mark.parametrize(
    "value_taking", ("--log-file", "--agent", "--conversation", "--project", "--mode")
)
def test_a_value_consumed_bare_token_cannot_smuggle_a_model_override(
    tmp_path: Path, value_taking: str
) -> None:
    """A bare `--` is not a terminator when a value-taking flag eats it.

    The guard briefly returned early on the first bare `--`, on the premise that
    nothing after AGY's terminator can be a flag. Real AGY 1.1.7 disproved it:
    `--log-file --` takes the bare token as the log filename, so `--model X`
    after it stayed a flag and AGY resolved it (`defaulting to CCPA`) while
    `AGY_MODEL` still advertised the configured model. Each flag here was
    observed consuming the bare token that way.

    The guard reads spelling only and must scan the whole list, so the `--`
    buys the override nothing.
    """
    forwarded = [value_taking, "--", "--model", "definitely-not-an-agy-model"]

    with pytest.raises(launcher.LaunchError, match="restates"):
        launcher.build_launch_spec(
            repo_root=tmp_path,
            seat="operator",
            settings=_settings(tmp_path),
            inherited_env={"PATH": "/bin"},
            agy_executable="/opt/agy",
            forwarded_args=forwarded,
        )


def test_a_bare_forwarded_terminator_does_not_stop_the_scan(tmp_path: Path) -> None:
    """Even the unambiguous-looking case is scanned through.

    Distinguishing this from the `--log-file --` shape needs AGY's parser state,
    which the launcher does not model, so it declines to try.
    """
    with pytest.raises(launcher.LaunchError, match="restates"):
        launcher.build_launch_spec(
            repo_root=tmp_path,
            seat="operator",
            settings=_settings(tmp_path),
            inherited_env={"PATH": "/bin"},
            agy_executable="/opt/agy",
            forwarded_args=["--", "--model", "definitely-not-an-agy-model"],
        )


def test_a_flag_like_token_inside_a_prompt_value_still_forwards(tmp_path: Path) -> None:
    """The documented workaround has to actually work.

    Only a *bare* launcher-owned flag is refused. Quoted into another flag's
    value it is a single token that names no flag, so prompts mentioning
    `--model` still reach AGY.
    """
    forwarded = ["-p", "explain why --model is set from the seat config"]

    spec = launcher.build_launch_spec(
        repo_root=tmp_path,
        seat="operator",
        settings=_settings(tmp_path),
        inherited_env={"PATH": "/bin"},
        agy_executable="/opt/agy",
        forwarded_args=forwarded,
    )

    assert list(spec.argv)[-len(forwarded) :] == forwarded


def test_failed_listing_reports_the_whole_error_stream(tmp_path: Path) -> None:
    """The cause must survive, wherever in the stream it appeared.

    AGY ends a failed listing with a generic Go stack summary and puts the real
    cause further up, so keeping only the last stderr line reported
    `Error types: ... syscall.Errno` and dropped
    `bind: operation not permitted` -- and every skip reason inherited that.
    """
    failing = tmp_path / "failing-agy"
    failing.write_text(
        "#!/bin/sh\n"
        "echo 'listen tcp 127.0.0.1:0: bind: operation not permitted' >&2\n"
        "echo 'Error types: (1) *withstack.withStack (4) syscall.Errno' >&2\n"
        "exit 1\n",
        encoding="utf-8",
    )
    failing.chmod(0o755)

    with pytest.raises(launcher.LaunchError) as blocked:
        launcher.list_models(str(failing))

    assert "bind: operation not permitted" in str(blocked.value)


def test_codex_only_flags_never_return_to_the_agy_command_line(tmp_path: Path) -> None:
    """`--config` and `--cd` are Codex flags this launcher was cloned from.

    AGY defines neither, so their presence broke `agy-seat <seat>` at parse
    time for every seat. They are named explicitly because the failure mode is
    re-copying from `scripts/codex_seat_launcher.py`, where both are correct.
    """
    spec = launcher.build_launch_spec(
        repo_root=tmp_path,
        seat="director",
        settings=_settings(tmp_path),
        inherited_env={"PATH": "/bin"},
        agy_executable="/opt/agy",
        forwarded_args=[],
    )

    assert "--config" not in spec.argv
    assert "--cd" not in spec.argv
    assert not any(token.startswith("service_tier=") for token in spec.argv)


@_needs_agy
@pytest.mark.parametrize("retired", ("--config", "--cd"))
def test_probe_still_detects_flags_the_installed_cli_does_not_define(
    retired: str,
) -> None:
    """Negative control: the probe must reject what the launcher used to emit.

    Without this, a probe that quietly stopped detecting rejection would let
    the acceptance test below pass while asserting nothing. The two retired
    Codex flags are used as the controls because they are the concrete strings
    that broke every seat.
    """
    control = _parse_probe(["--model", _canonical_model(), retired, "/tmp"])

    assert control.returncode != 0
    assert UNDEFINED_FLAG_MARKER in control.stdout + control.stderr


@_needs_agy
def test_installed_cli_accepts_the_emitted_argv_at_parse_time(tmp_path: Path) -> None:
    """The installed CLI parses a real emitted command line and exits clean."""
    spec = launcher.build_launch_spec(
        repo_root=tmp_path,
        seat="operator",
        settings=_settings(tmp_path, {"operator": (_canonical_model(), "high")}),
        inherited_env={"PATH": "/bin"},
        agy_executable="/opt/agy",
        forwarded_args=[],
    )

    accepted = _parse_probe(list(spec.argv[1:]))
    output = accepted.stdout + accepted.stderr

    assert UNDEFINED_FLAG_MARKER not in output, output
    assert accepted.returncode == 0, output


@_needs_agy
def test_canonical_model_is_a_model_the_installed_cli_lists() -> None:
    """The canonical model form is literally an `agy models` entry.

    The launcher config shipped `gemini-2.5-pro`, which the CLI has never
    listed, so `--model` was wrong even independently of the flag names. A
    report citing the canonical form can be re-checked by re-running the same
    command the launcher itself checks against.
    """
    assert _canonical_model() in _LIVE_LISTING
    assert "gemini-2.5-pro" not in _LIVE_LISTING


def test_unlisted_model_is_rejected_before_it_can_be_cited(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    """A model the CLI does not offer must never reach `--model` or AGY_MODEL.

    Syntactic validation accepted any nonempty token, so a typo became the
    citable `Reviewer model:` of a launch that could not have happened. The
    check runs on `--dry-run` as well, because dry-run is the surface a report
    quotes.
    """
    config_path = tmp_path / "seats.toml"
    _write_config(config_path, {"operator": ("definitely-not-an-agy-model", "high")})
    _stub_installed_cli(monkeypatch, (launcher.REFERENCE_MODEL,))

    code = launcher.main(["--dry-run", "--config", str(config_path), "operator"])
    captured = capsys.readouterr()

    assert code == 2
    assert "definitely-not-an-agy-model" not in captured.out
    assert "is not offered by" in captured.err


def test_unavailable_model_listing_fails_closed(tmp_path: Path) -> None:
    """An unusable listing must not be read as an empty allowlist or a pass.

    A sandbox that blocks AGY's language-server socket makes the listing
    unobtainable. Treating that as "no models matched" or as "checked" would
    both be wrong; the model is simply unsubstantiated.
    """
    failing = tmp_path / "failing-agy"
    failing.write_text(
        "#!/bin/sh\necho 'bind: operation not permitted' >&2\nexit 1\n", encoding="utf-8"
    )
    failing.chmod(0o755)

    with pytest.raises(launcher.LaunchError) as blocked:
        launcher.list_models(str(failing))
    assert "cannot be checked" in str(blocked.value)
    # The real cause has to reach the operator, or a blocked sandbox is
    # indistinguishable from a genuinely rejected model.
    assert "bind: operation not permitted" in str(blocked.value)

    with pytest.raises(launcher.LaunchError, match="cannot run"):
        launcher.list_models(str(tmp_path / "no-such-executable"))


def test_configured_model_reaches_the_cli_and_the_report_surface_verbatim(
    tmp_path: Path,
) -> None:
    """One string reaches `--model` and `AGY_MODEL`, undecorated.

    A verification report cites `AGY_MODEL`; `--model` is what actually ran.
    They must be the same token, or the report names a launch that never
    happened. An ambient AGY_MODEL is authoritative-overwritten, never trusted.
    """
    configured = "gemini-3.1-pro-high"
    spec = launcher.build_launch_spec(
        repo_root=tmp_path,
        seat="operator",
        settings=_settings(tmp_path, {"operator": (configured, "high")}),
        inherited_env={"PATH": "/bin", "AGY_MODEL": "forged-model"},
        agy_executable="/opt/agy",
        forwarded_args=[],
    )
    argv = list(spec.argv)

    assert argv[argv.index("--model") + 1] == configured
    assert spec.env["AGY_MODEL"] == configured


def test_harness_decorated_model_ids_buy_no_independence(tmp_path: Path) -> None:
    """Why the bare `agy models` ID is canonical rather than a prefixed form.

    The mailbox recorded `antigravity-gemini-3.6` while the one committed AGY
    report said `gemini-3.6-flash` and the launcher config said
    `gemini-2.5-pro`. `model_family` strips harness prefixes, so all of these
    already key the same independence decision -- the divergence never changed
    a verdict, it only made the cited string unverifiable against `agy models`.
    """
    family = codex_protocol_model.model_family
    assert (
        family("antigravity-gemini-3.6")
        == family("gemini-3.6-flash")
        == family("gemini-2.5-pro")
        == family("gemini-3.1-pro-high")
        == "gemini"
    )
    assert codex_protocol_model.models_are_independent(
        "claude-opus-5", "gemini-3.1-pro-high"
    )


@pytest.mark.parametrize(
    "body",
    (
        '[seats.director]\nmodel = "m"\neffort = "high"\n',
        '[seats]\n',
        '[other]\nkey = "value"\n',
    ),
)
def test_config_rejects_incomplete_or_unknown_settings(tmp_path: Path, body: str) -> None:
    config_path = tmp_path / "seats.toml"
    config_path.write_text(body, encoding="utf-8")

    with pytest.raises(launcher.ConfigError):
        launcher.load_seat_settings(config_path)


def test_config_rejects_bad_model_or_effort(tmp_path: Path) -> None:
    for overrides in (
        {"director": ("", "high")},
        {"director": (" leading-space", "high")},
        {"director": ("model", "turbo")},
        # The retired Codex-shaped vocabulary must not quietly still work.
        {"director": ("model", "fast")},
        {"director": ("model", "default")},
    ):
        config_path = tmp_path / "seats.toml"
        _write_config(config_path, overrides)
        with pytest.raises(launcher.ConfigError):
            launcher.load_seat_settings(config_path)


def test_dry_run_prints_identity_and_does_not_start_agy(
    tmp_path: Path, capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch
) -> None:
    config_path = tmp_path / "seats.toml"
    _write_config(config_path)

    def _fail(*args, **kwargs):  # pragma: no cover - must never run
        raise AssertionError("dry run must not exec the provider")

    _stub_installed_cli(monkeypatch)
    monkeypatch.setattr(launcher.os, "execvpe", _fail)

    code = launcher.main(["--dry-run", "--config", str(config_path), "director"])

    assert code == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["env"]["AGY_SEAT"] == "agy-unit-director"
    assert "GIT_INDEX_FILE" not in payload["env"]
    assert "index_exists" not in payload


def test_launch_enters_the_repository_before_exec(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The seat starts in its repository even though AGY has no `--cd`.

    `--add-dir` only adds the repository to the AGY workspace; it does not move
    the process. The working directory the retired `--cd` was reaching for now
    comes from a chdir, and it has to happen before exec replaces the process.
    """
    config_path = tmp_path / "seats.toml"
    _write_config(config_path)
    repo_root = Path(launcher.__file__).resolve().parents[1]
    calls: list[tuple[str, object]] = []

    _stub_installed_cli(monkeypatch)
    monkeypatch.setattr(launcher.os, "chdir", lambda path: calls.append(("chdir", path)))
    monkeypatch.setattr(
        launcher.os,
        "execvpe",
        lambda file, argv, env: calls.append(("execvpe", file)),
    )

    launcher.main(["--config", str(config_path), "operator"])

    assert [name for name, _ in calls] == ["chdir", "execvpe"]
    assert calls[0][1] == repo_root


def test_dry_run_does_not_move_the_calling_shell(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    config_path = tmp_path / "seats.toml"
    _write_config(config_path)

    def _fail(*args, **kwargs):  # pragma: no cover - must never run
        raise AssertionError("dry run must not chdir or exec")

    _stub_installed_cli(monkeypatch)
    monkeypatch.setattr(launcher.os, "chdir", _fail)
    monkeypatch.setattr(launcher.os, "execvpe", _fail)

    assert launcher.main(["--dry-run", "--config", str(config_path), "operator"]) == 0


def test_dry_run_prints_the_model_string_a_report_must_cite(
    tmp_path: Path, capsys: pytest.CaptureFixture[str], monkeypatch: pytest.MonkeyPatch
) -> None:
    """`--dry-run` is the citable source for `Reviewer model:`.

    A seat that cannot see which model it runs on invents a plausible label,
    which is how the mailbox ended up recording strings no launch produced.
    """
    config_path = tmp_path / "seats.toml"
    _write_config(config_path, {"operator": (launcher.REFERENCE_MODEL, "high")})
    _stub_installed_cli(monkeypatch)
    monkeypatch.setattr(launcher.os, "execvpe", lambda *a, **k: None)

    launcher.main(["--dry-run", "--config", str(config_path), "operator"])

    payload = json.loads(capsys.readouterr().out)
    argv = payload["argv"]

    assert payload["env"]["AGY_MODEL"] == launcher.REFERENCE_MODEL
    assert argv[argv.index("--model") + 1] == launcher.REFERENCE_MODEL


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
