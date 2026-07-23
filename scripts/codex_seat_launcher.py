#!/usr/bin/env python3
"""Launch one local Codex seat with independent model and speed settings."""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import tomllib
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path

try:
    from scripts.codex_protocol_model import infer_runtime_env
except ModuleNotFoundError as exc:
    if exc.name != "scripts":
        raise
    from codex_protocol_model import infer_runtime_env


LAUNCH_SEATS = ("director", "director2", "operator", "operator2", "coordinator")
SERVICE_TIERS = ("fast", "default")
DEFAULT_CONFIG_PATH = Path("~/.codex/pipeline-seat-launcher.toml")


class ConfigError(ValueError):
    """Raised when the local per-seat configuration is invalid."""


class LaunchError(RuntimeError):
    """Raised when local launch preparation fails."""


@dataclass(frozen=True)
class SeatSettings:
    model: str
    service_tier: str


@dataclass(frozen=True)
class LaunchSpec:
    argv: tuple[str, ...]
    env: dict[str, str]
    repo_root: Path
    index_path: Path


def load_seat_settings(path: Path) -> dict[str, SeatSettings]:
    """Load a complete, strictly per-seat local TOML configuration."""
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
        if not isinstance(value, dict) or set(value) != {"model", "service_tier"}:
            raise ConfigError(
                f"[seats.{seat}] must contain exactly model and service_tier"
            )
        model = value["model"]
        service_tier = value["service_tier"]
        if (
            not isinstance(model, str)
            or not model
            or model.strip() != model
            or any(character.isspace() or ord(character) < 32 for character in model)
        ):
            raise ConfigError(f"[seats.{seat}].model must be a non-empty model name")
        if service_tier not in SERVICE_TIERS:
            raise ConfigError(
                f"[seats.{seat}].service_tier must be fast or default"
            )
        settings[seat] = SeatSettings(model=model, service_tier=service_tier)
    return settings


def build_launch_spec(
    repo_root: Path,
    git_dir: Path,
    seat: str,
    settings: Mapping[str, SeatSettings],
    inherited_env: Mapping[str, str],
    codex_executable: str,
    forwarded_args: Sequence[str],
) -> LaunchSpec:
    """Build an argv/env launch specification without performing side effects."""
    if seat not in LAUNCH_SEATS:
        raise LaunchError(f"unsupported seat: {seat}")
    if seat not in settings:
        raise LaunchError(f"missing settings for seat: {seat}")

    runtime = infer_runtime_env({"CODEX_SEAT": seat})
    env = dict(inherited_env)
    env.update(
        {
            "CODEX_SEAT": seat,
            "CODEX_AGENT_MODE": runtime["CODEX_AGENT_MODE"],
            "CODEX_AGENT_ROLE": runtime["CODEX_AGENT_ROLE"],
        }
    )
    behavior_source = runtime["CODEX_BEHAVIOR_SOURCE"]
    if behavior_source == "(none)":
        env.pop("CODEX_BEHAVIOR_SOURCE", None)
    else:
        env["CODEX_BEHAVIOR_SOURCE"] = behavior_source

    index_path = git_dir / f"index-codex-{seat}"
    env["GIT_INDEX_FILE"] = str(index_path)
    selected = settings[seat]
    argv = (
        codex_executable,
        "--model",
        selected.model,
        "--config",
        f'service_tier="{selected.service_tier}"',
        "--cd",
        str(repo_root),
        *forwarded_args,
    )
    return LaunchSpec(
        argv=argv,
        env=env,
        repo_root=repo_root,
        index_path=index_path,
    )


def _without_ambient_index(environ: Mapping[str, str]) -> dict[str, str]:
    clean_env = dict(environ)
    clean_env.pop("GIT_INDEX_FILE", None)
    return clean_env


def resolve_git_dir(repo_root: Path) -> Path:
    """Resolve the repository git directory without trusting an ambient index."""
    result = subprocess.run(
        ["git", "-C", str(repo_root), "rev-parse", "--absolute-git-dir"],
        env=_without_ambient_index(os.environ),
        text=True,
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        raise LaunchError(result.stderr.strip() or "cannot resolve repository git directory")
    return Path(result.stdout.strip())


def ensure_seat_index(
    repo_root: Path,
    index_path: Path,
    *,
    runner: Callable[..., subprocess.CompletedProcess[str]] = subprocess.run,
) -> None:
    """Seed a missing per-seat index; validate and preserve an existing one."""
    if index_path.exists():
        index_env = _without_ambient_index(os.environ)
        index_env["GIT_INDEX_FILE"] = str(index_path)
        entries = runner(
            ["git", "-C", str(repo_root), "ls-files", "--stage", "-z"],
            env=index_env,
            text=True,
            capture_output=True,
            check=False,
        )
        if entries.returncode != 0:
            detail = entries.stderr.strip() or entries.stdout.strip()
            raise LaunchError(
                f"existing seat index {index_path} is unusable: "
                f"{detail or 'cannot read index entries'}"
            )
        if not entries.stdout:
            head_entries = runner(
                [
                    "git",
                    "-C",
                    str(repo_root),
                    "ls-tree",
                    "-r",
                    "--name-only",
                    "-z",
                    "HEAD",
                ],
                env=_without_ambient_index(os.environ),
                text=True,
                capture_output=True,
                check=False,
            )
            if head_entries.returncode != 0:
                detail = head_entries.stderr.strip() or head_entries.stdout.strip()
                raise LaunchError(detail or "cannot inspect HEAD before seat launch")
            if head_entries.stdout:
                raise LaunchError(
                    f"existing seat index {index_path} is empty while HEAD tracks files; "
                    "refusing to launch without changing the index"
                )
        status = runner(
            [
                "git",
                "--no-optional-locks",
                "-C",
                str(repo_root),
                "status",
                "--porcelain=v1",
                "--untracked-files=no",
                "--ignore-submodules=all",
            ],
            env=index_env,
            text=True,
            capture_output=True,
            check=False,
        )
        if status.returncode != 0:
            detail = status.stderr.strip() or status.stdout.strip()
            raise LaunchError(
                f"existing seat index {index_path} is unusable: "
                f"{detail or 'Git status validation failed'}"
            )
        return
    result = runner(
        [
            "git",
            "-C",
            str(repo_root),
            "read-tree",
            f"--index-output={index_path}",
            "HEAD",
        ],
        env=_without_ambient_index(os.environ),
        text=True,
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        raise LaunchError(result.stderr.strip() or f"cannot seed seat index {index_path}")


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
        description="Launch a Codex seat with its own local model and speed setting."
    )
    parser.add_argument("--dry-run", action="store_true", help="print launch data only")
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
        git_dir = resolve_git_dir(repo_root)
        codex_executable = shutil.which("codex")
        if codex_executable is None and not args.dry_run:
            raise LaunchError("codex executable not found on PATH")
        spec = build_launch_spec(
            repo_root,
            git_dir,
            args.seat,
            settings,
            os.environ,
            codex_executable or "codex",
            forwarded_args,
        )
        if args.dry_run:
            identity_keys = (
                "CODEX_SEAT",
                "CODEX_AGENT_MODE",
                "CODEX_AGENT_ROLE",
                "CODEX_BEHAVIOR_SOURCE",
                "GIT_INDEX_FILE",
            )
            print(
                json.dumps(
                    {
                        "argv": list(spec.argv),
                        "env": {key: spec.env[key] for key in identity_keys if key in spec.env},
                        "index_exists": spec.index_path.exists(),
                    },
                    indent=2,
                    sort_keys=True,
                )
            )
            return 0

        ensure_seat_index(spec.repo_root, spec.index_path)
        os.execvpe(spec.argv[0], list(spec.argv), spec.env)
    except (ConfigError, LaunchError) as exc:
        print(f"codex-seat: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
