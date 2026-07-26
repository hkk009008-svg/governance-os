#!/usr/bin/env python3
"""Launch one local AGY (Antigravity) seat with independent model and speed settings."""

from __future__ import annotations

import argparse
import json
import os
import shutil
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
DEFAULT_CONFIG_PATH = Path("~/.agy/pipeline-seat-launcher.toml")
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
        # `service_tier` is accepted and ignored rather than required. The
        # installed CLI exposes no service-tier option, so validating one made
        # the launcher advertise a speed control that selected nothing:
        # changing `fast` to `default` altered no launch behaviour. Existing
        # configs still load; the field may be deleted.
        if not isinstance(value, dict) or not {"model"} <= set(value) <= {
            "model",
            "service_tier",
        }:
            raise ConfigError(f"[seats.{seat}] must contain exactly model")
        model = value["model"]
        if (
            not isinstance(model, str)
            or not model
            or model.strip() != model
            or any(character.isspace() or ord(character) < 32 for character in model)
        ):
            raise ConfigError(f"[seats.{seat}].model must be a non-empty model name")
        settings[seat] = SeatSettings(model=model)
    return settings


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

    try:
        runtime = infer_runtime_env(profile=seat, mode=mode)
    except RuntimeIdentityError as exc:
        raise LaunchError(str(exc)) from exc
    env = _clean_inherited_environment(inherited_env)
    env.update(runtime)
    selected = settings[seat]
    # `--config` and `--cd` were emitted here but the installed CLI defines
    # neither, so every seat launch died at argument parsing. The working root
    # moves to the process cwd set just before exec, and the service tier has
    # no CLI surface at all — it stays configuration the launcher records
    # rather than a flag it invents.
    argv = (
        agy_executable,
        "--model",
        selected.model,
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
        agy_executable = "agy" if args.dry_run else (
            shutil.which("agy") or shutil.which("antigravity")
        )
        if agy_executable is None:
            raise LaunchError("agy/antigravity executable not found on PATH")
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
