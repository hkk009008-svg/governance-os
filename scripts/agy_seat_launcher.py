#!/usr/bin/env python3
"""Launch one local AGY (Antigravity) seat with independent model and speed settings."""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import tomllib
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path

try:
    from scripts.agy_protocol_model import (
        ADVISORY_MODE,
        MODES,
        SINGLE_MODEL_MODE,
        RuntimeIdentityError,
        infer_runtime_env,
    )
except ModuleNotFoundError as exc:
    if exc.name != "scripts":
        raise
    from agy_protocol_model import (  # type: ignore[no-redef]
        ADVISORY_MODE,
        MODES,
        SINGLE_MODEL_MODE,
        RuntimeIdentityError,
        infer_runtime_env,
    )


LAUNCH_SEATS = ("director", "director2", "operator", "operator2", "coordinator")
EFFORT_LEVELS = ("low", "medium", "high")
DEFAULT_CONFIG_PATH = Path("~/.agy/pipeline-seat-launcher.toml")

# Every flag this launcher may put on an `agy` command line. AGY parses flags
# with Go's `flag` package, which aborts the whole invocation on the first
# undefined flag rather than ignoring it, so one wrong name breaks every seat.
#
# This launcher was cloned from `scripts/codex_seat_launcher.py` and inherited
# `--config key=value` and `--cd DIR`. Both are real *Codex* flags and neither
# exists on AGY, so `coordination/bin/agy-seat <seat>` failed at parse time for
# every seat with `flags provided but not defined: -config`. The set is
# committed so `tests/unit/test_agy_seat_launcher.py` can hold the emitted argv
# to it hermetically, and separately feed a real argv through the installed
# CLI's parser instead of trusting that this set is still true.
EMITTED_CLI_FLAGS = frozenset({"--model", "--effort"})

# Flags a seat may forward after `--`, by normalized name. This is a positive
# control on purpose. A denylist was tried first and leaked twice: a forwarded
# `--model` overrode the checked one because AGY resolves a repeated flag to its
# last occurrence, and then a `--` consumed as `--log-file`'s value defeated the
# obvious guard against that. Both were found by independent review rather than
# by this launcher's own reasoning.
#
# The residual weakness of any denylist is what settles it: a flag AGY has not
# shipped yet cannot be enumerated, so a future short alias for `--model` would
# be admitted silently. An allowlist refuses it by default instead. Adding an
# entry here is a deliberate act; forgetting to add one is a launch failure with
# a clear message, not a silent identity override.
#
# Excluded and why:
#   --model, --effort            set from the seat config; forwarding one lets
#                                the seat run on something it does not report
#   --agent, --mode, --project   behaviour and session identity the seat's own
#                                AGY_* runtime already declares
#   --add-dir, --new-project,    workspace and filesystem side effects beyond
#   --log-file                   the repository the seat was launched for
#   --dangerously-skip-...       blanket tool approval; an external-effect
#                                amplifier that needs its own authorization
FORWARDABLE_FLAG_NAMES = frozenset(
    {
        "p",
        "print",
        "prompt",
        "i",
        "prompt-interactive",
        "c",
        "continue",
        "conversation",
        "print-timeout",
        "sandbox",
    }
)

# AGY exposes no service-tier flag. Speed is expressed as reasoning effort,
# both as a `--effort` value and as a suffix on the model IDs that
# `agy models` lists (`gemini-3.1-pro-high`, `gemini-3.6-flash-low`, ...).
#
# `agy models` is the sole authority for a model name: it is the only form
# `--model` accepts, and reports must cite that exact string so a reader can
# re-run the listing and confirm the seat could have run on it. Do not decorate
# it with a harness prefix. `codex_protocol_model.model_family` strips
# `antigravity-`/`agy-` before comparing, so a prefix buys no independence and
# only makes the report unverifiable.
MODEL_LISTING_COMMAND = ("agy", "models")

# The canonical model string documented in `coordination/README.md` and cited
# by AGY verification reports. It is pinned here rather than in prose so a test
# can assert it is still a literal `agy models` entry. The seat config shipped
# `gemini-2.5-pro`, which that listing has never contained.
REFERENCE_MODEL = "gemini-3.1-pro-high"

# `agy models` starts a local language server, so it is slower than a plain
# subprocess but still makes no inference request and costs nothing.
MODEL_LISTING_TIMEOUT_SECONDS = 120
_FOREIGN_AUTHORITY_PREFIXES = (
    "CLAUDE_",
    "CURSOR_",
    "CODEX_",
    "ANTIGRAVITY_",
    "GIT_",
)
_PRESERVED_AGY_CREDENTIALS = frozenset({"AGY_API_KEY"})
# Options the installed AGY CLI actually defines, per `agy --help`. This exists
# because the launcher and the binary are separate artifacts: a flag removed
# upstream, or invented here, produces `flags provided but not defined` and the
# seat never starts. Nothing in a pure-Python test can see that on its own, so
# the emitted argv is checked against this set and this set against `agy --help`.
AGY_CLI_FLAGS = frozenset(
    {
        "--add-dir",
        "--agent",
        "--continue",
        "--conversation",
        "--dangerously-skip-permissions",
        "--effort",
        "--log-file",
        "--mode",
        "--model",
        "--new-project",
        "--print",
        "--print-timeout",
        "--project",
        "--prompt",
        "--prompt-interactive",
        "--sandbox",
    }
)


class ConfigError(ValueError):
    """Raised when the local per-seat configuration is invalid."""


class LaunchError(RuntimeError):
    """Raised when local launch preparation fails."""


@dataclass(frozen=True)
class SeatSettings:
    model: str
    effort: str


@dataclass(frozen=True)
class LaunchSpec:
    argv: tuple[str, ...]
    env: dict[str, str]
    repo_root: Path
    mode: str


def load_seat_settings(path: Path) -> dict[str, SeatSettings]:
    """Load a complete, strictly per-seat local TOML configuration for AGY."""
    try:
        with path.expanduser().open("rb") as handle:
            document = tomllib.load(handle)
    except (OSError, tomllib.TOMLDecodeError) as exc:
        raise ConfigError(f"cannot load seat config {path.expanduser()}: {exc}") from exc

    if set(document) != {"seats"} or not isinstance(document["seats"], dict):
        raise ConfigError("config must contain only a [seats] table")
    seats = document["seats"]
    if set(seats) != set(LAUNCH_SEATS):
        raise ConfigError("config must define exactly: " + ", ".join(LAUNCH_SEATS))

    settings: dict[str, SeatSettings] = {}
    for seat in LAUNCH_SEATS:
        value = seats[seat]
        # `effort` is required, not ignored, because it is applied: it reaches
        # the CLI as `--effort`. The sibling line reached the opposite fix for
        # the same finding -- it dropped `service_tier` because nothing consumed
        # it, so validating it made the launcher advertise a speed control that
        # selected nothing. Both answer "no false capabilities"; this one keeps
        # the capability instead of the field. A config still carrying
        # `service_tier` is on the retired schema and is refused by name rather
        # than silently ignored, so the migration is visible.
        if not isinstance(value, dict) or set(value) != {"model", "effort"}:
            raise ConfigError(
                f"[seats.{seat}] must contain exactly model and effort"
            )
        model = value["model"]
        effort = value["effort"]
        if (
            not isinstance(model, str)
            or not model
            or model.strip() != model
            or any(character.isspace() or ord(character) < 32 for character in model)
        ):
            raise ConfigError(f"[seats.{seat}].model must be a non-empty model name")
        if effort not in EFFORT_LEVELS:
            raise ConfigError(
                f"[seats.{seat}].effort must be one of: " + ", ".join(EFFORT_LEVELS)
            )
        settings[seat] = SeatSettings(model=model, effort=effort)
    return settings


def list_models(agy_executable: str) -> frozenset[str]:
    """Return the model IDs the installed CLI reports as usable.

    Syntactic config validation cannot establish that a model exists, and a
    launcher that accepts any well-formed string will happily promote a typo to
    `--model` and to the `AGY_MODEL` a verification report cites. That is the
    whole failure this launcher is supposed to close, so the check runs against
    the CLI rather than against a list committed here that would drift.

    Fails closed: if the listing cannot be obtained the model is unsubstantiated
    and the caller must not proceed as though it had been checked.
    """
    try:
        completed = subprocess.run(
            [agy_executable, *MODEL_LISTING_COMMAND[1:]],
            stdin=subprocess.DEVNULL,
            capture_output=True,
            text=True,
            timeout=MODEL_LISTING_TIMEOUT_SECONDS,
            start_new_session=True,
            check=False,
        )
    except (OSError, subprocess.SubprocessError) as exc:
        raise LaunchError(
            f"cannot run `{' '.join(MODEL_LISTING_COMMAND)}` to check the seat model: {exc}"
        ) from exc
    if completed.returncode != 0:
        # Keep the whole stream, not a chosen line. AGY ends a failed listing
        # with a generic Go stack summary (`Error types: ... syscall.Errno`)
        # and puts the cause -- `bind: operation not permitted`, an
        # authentication complaint, `flags provided but not defined` -- further
        # up, so tailing the last line reliably reported nothing useful. The
        # caller decides which failures are environmental, and it can only do
        # that if the real text survives.
        detail = (completed.stderr or completed.stdout).strip()
        raise LaunchError(
            f"`{' '.join(MODEL_LISTING_COMMAND)}` failed (exit {completed.returncode}), "
            "so the seat model cannot be checked"
            + (f":\n{detail}" if detail else "")
        )
    return frozenset(
        line.strip() for line in completed.stdout.splitlines() if line.strip()
    )


def require_listed_model(model: str, listed: frozenset[str]) -> None:
    """Reject a seat model the installed CLI does not offer."""
    if model in listed:
        return
    raise LaunchError(
        f"model {model!r} is not offered by `{' '.join(MODEL_LISTING_COMMAND)}`; "
        "choose one of: " + ", ".join(sorted(listed))
    )


def _flag_name(token: str) -> str:
    """Return the bare flag name one argv token spells, or '' if it spells none.

    Go's flag package accepts `-flag`, `--flag`, `-flag=v` and `--flag=v`
    interchangeably, so a check that only looks for the `--flag value` spelling
    is trivially evaded. `-` and `--` name no flag.
    """
    if not token.startswith("-") or token in ("-", "--"):
        return ""
    return token.lstrip("-").split("=", 1)[0]


_LAUNCHER_OWNED_FLAG_NAMES = frozenset(
    flag.lstrip("-") for flag in EMITTED_CLI_FLAGS
)


def _spell(name: str) -> str:
    """Render a bare flag name the way AGY documents it: `-p`, but `--print`."""
    return f"-{name}" if len(name) == 1 else f"--{name}"


def reject_unforwardable_flags(forwarded_args: Sequence[str]) -> None:
    """Allow only the flags a seat is permitted to forward after `--`.

    Forwarded tokens land after the launcher's own flags, and AGY resolves a
    repeated flag to the *last* occurrence. `agy-seat operator -- --model X`
    therefore ran on X while `AGY_MODEL` still advertised the configured model,
    so a verification report could cite a model that never ran -- the same
    unsubstantiated identity the listing check exists to prevent, reached
    through the forwarding seam instead of the config file.

    This is an allowlist because two denylists leaked here first. The second
    leak is the instructive one: it returned early on a bare `--`, reasoning
    that AGY's terminator makes later tokens positional. That is false, because
    whether `--` terminates depends on what precedes it. `--log-file --`
    consumes the bare token as the log *filename*, so it terminates nothing, and
    a following `--model X` was still a flag AGY resolved -- observed on AGY
    1.1.7 as `Model ID X not in local config, defaulting to CCPA`. `--agent`,
    `--conversation`, `--project` and `--mode` behave the same way.

    Deciding which forwarded tokens are really flags means modelling AGY's
    parser, including every value-taking flag it may add later. This launcher
    does not attempt that, and does not need to: it reads spelling only, and
    anything it does not recognize is refused rather than guessed at. The cost
    is that a command line AGY would have parsed harmlessly is sometimes
    rejected -- loudly, immediately, with a documented workaround. An admitted
    identity override is silent and falsifies a report.
    """
    for token in forwarded_args:
        name = _flag_name(token)
        if not name:
            continue
        if name in _LAUNCHER_OWNED_FLAG_NAMES:
            raise LaunchError(
                f"forwarded argument {token!r} restates {_spell(name)}, which the "
                "launcher sets from the seat config; AGY would honour the forwarded "
                "value while the seat kept advertising the configured one"
            )
        if name not in FORWARDABLE_FLAG_NAMES:
            raise LaunchError(
                f"forwarded argument {token!r} is not a flag a seat may forward; "
                "allowed: "
                + ", ".join(_spell(allowed) for allowed in sorted(FORWARDABLE_FLAG_NAMES))
                + ". To pass it as text, keep it inside another flag's value. If "
                f"{_spell(name)} should be forwardable, add it to "
                "FORWARDABLE_FLAG_NAMES deliberately rather than widening the check."
            )


def build_launch_spec(
    repo_root: Path,
    seat: str,
    settings: Mapping[str, SeatSettings],
    inherited_env: Mapping[str, str],
    agy_executable: str,
    forwarded_args: Sequence[str],
    *,
    mode: str = SINGLE_MODEL_MODE,
) -> LaunchSpec:
    """Build an argv/env launch specification without performing side effects."""
    if seat not in LAUNCH_SEATS:
        raise LaunchError(f"unsupported seat: {seat}")
    if seat not in settings:
        raise LaunchError(f"missing settings for seat: {seat}")
    if mode not in MODES:
        raise LaunchError(f"unsupported AGY mode: {mode}")
    reject_unforwardable_flags(forwarded_args)

    try:
        runtime = infer_runtime_env(profile=seat, mode=mode)
    except RuntimeIdentityError as exc:
        raise LaunchError(str(exc)) from exc
    env = _clean_inherited_environment(inherited_env)
    env.update(runtime)
    selected = settings[seat]
    # AGY_MODEL is authoritative, not inherited: `_clean_inherited_environment`
    # drops an ambient AGY_MODEL so a launched seat reads back the same string
    # that reached `--model` and can cite it verbatim in a verification report.
    env["AGY_MODEL"] = selected.model
    # `--config` and `--cd` were emitted here but the installed CLI defines
    # neither, so every seat launch died at argument parsing. The working root
    # comes from the process cwd set just before exec instead; `--add-dir` was
    # tried too and dropped, because it adds the repository to the workspace
    # without moving the process and the chdir already covers that.
    #
    # The per-seat speed setting does have a CLI surface -- `--effort` -- so it
    # is passed rather than recorded and discarded. A validated config field
    # that reaches nothing is the same class of defect as the flags above.
    argv = (
        agy_executable,
        "--model",
        selected.model,
        "--effort",
        selected.effort,
        *forwarded_args,
    )
    return LaunchSpec(
        argv=argv,
        env=env,
        repo_root=repo_root,
        mode=mode,
    )


def _clean_inherited_environment(environ: Mapping[str, str]) -> dict[str, str]:
    """Keep ordinary process state and a minimal AGY credential allowlist."""

    return {
        key: value
        for key, value in environ.items()
        if not key.startswith(_FOREIGN_AUTHORITY_PREFIXES)
        and (
            not key.startswith("AGY_")
            or key in _PRESERVED_AGY_CREDENTIALS
        )
    }


def _parse_args(argv: Sequence[str]) -> tuple[argparse.Namespace, list[str]]:
    values = list(argv)
    if "--" in values:
        boundary = values.index("--")
        launcher_args = values[:boundary]
        forwarded_args = values[boundary + 1 :]
    else:
        launcher_args = values
        forwarded_args = []

    parser = argparse.ArgumentParser(
        description="Launch an AGY (Antigravity) seat with its own local model and speed setting."
    )
    parser.add_argument("--dry-run", action="store_true", help="print launch data only")
    parser.add_argument(
        "--mode",
        choices=MODES,
        default=SINGLE_MODEL_MODE,
        help=(
            "AGY posture: advisory is dry-run/readiness only; "
            "single-model-autonomous is an explicit independent-unit mode"
        ),
    )
    parser.add_argument(
        "--config",
        type=Path,
        default=DEFAULT_CONFIG_PATH,
        help=f"seat config path (default: {DEFAULT_CONFIG_PATH})",
    )
    parser.add_argument("seat", choices=LAUNCH_SEATS)
    return parser.parse_args(launcher_args), forwarded_args


def main(argv: Sequence[str] | None = None) -> int:
    args, forwarded_args = _parse_args(sys.argv[1:] if argv is None else argv)
    repo_root = Path(__file__).resolve().parents[1]
    try:
        settings = load_seat_settings(args.config)
        agy_executable = shutil.which("agy") or shutil.which("antigravity")
        if agy_executable is None:
            raise LaunchError("agy/antigravity executable not found on PATH")
        # Checked on `--dry-run` too, and deliberately: dry-run is the surface a
        # verification report quotes its `Reviewer model:` from, so an unchecked
        # dry-run would hand out exactly the unsubstantiated identity that
        # citing a live listing is meant to prevent.
        require_listed_model(settings[args.seat].model, list_models(agy_executable))
        spec = build_launch_spec(
            repo_root,
            args.seat,
            settings,
            os.environ,
            agy_executable,
            forwarded_args,
            mode=args.mode,
        )
        if args.dry_run:
            identity_keys = (
                "AGY_SEAT",
                "AGY_AGENT_MODE",
                "AGY_AGENT_ROLE",
                "AGY_BEHAVIOR_SOURCE",
                "AGY_MODEL",
            )
            print(
                json.dumps(
                    {
                        "argv": list(spec.argv),
                        "env": {key: spec.env[key] for key in identity_keys if key in spec.env},
                        "mode": spec.mode,
                    },
                    indent=2,
                    sort_keys=True,
                )
            )
            return 0

        # The CLI has no working-root flag, so the seat inherits this process's
        # directory. Without the chdir a seat launched from anywhere else would
        # silently operate on whatever repository the caller happened to be in.
        # An unreadable or missing root must surface as the launcher's own error
        # contract, not an uncaught OSError traceback past the handler below.
        try:
            os.chdir(spec.repo_root)
        except OSError as exc:
            raise LaunchError(f"cannot enter reviewed root {spec.repo_root}: {exc}") from exc
        os.execvpe(spec.argv[0], list(spec.argv), spec.env)
    except (ConfigError, LaunchError) as exc:
        print(f"agy-seat: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
