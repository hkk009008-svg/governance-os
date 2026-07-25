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
EMITTED_CLI_FLAGS = frozenset({"--model", "--effort", "--add-dir"})

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
        detail = (completed.stderr or completed.stdout).strip().splitlines()
        raise LaunchError(
            f"`{' '.join(MODEL_LISTING_COMMAND)}` failed (exit {completed.returncode}), "
            "so the seat model cannot be checked"
            + (f": {detail[-1]}" if detail else "")
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
    # AGY_MODEL is authoritative, not inherited: `_clean_inherited_environment`
    # drops an ambient AGY_MODEL so a launched seat reads back the same string
    # that reached `--model` and can cite it verbatim in a verification report.
    env["AGY_MODEL"] = selected.model
    # `--add-dir` puts the repository in the AGY workspace. It does not set the
    # process working directory the way the old (nonexistent) `--cd` intended
    # to, so `main` also chdirs to `repo_root` before exec.
    argv = (
        agy_executable,
        "--model",
        selected.model,
        "--effort",
        selected.effort,
        "--add-dir",
        str(repo_root),
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

        # AGY has no working-directory flag; the seat must simply start in the
        # repository it was launched for.
        os.chdir(spec.repo_root)
        os.execvpe(spec.argv[0], list(spec.argv), spec.env)
    except (ConfigError, LaunchError) as exc:
        print(f"agy-seat: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
