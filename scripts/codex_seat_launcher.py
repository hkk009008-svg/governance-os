#!/usr/bin/env python3
"""Launch one local Codex seat with independent model and speed settings."""

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
    from scripts.codex_protocol_model import RuntimeIdentity, RUNTIME_SCRUB_ENV_KEYS
except ModuleNotFoundError as exc:
    if exc.name != "scripts":
        raise
    from codex_protocol_model import RuntimeIdentity, RUNTIME_SCRUB_ENV_KEYS


LAUNCH_SEATS = ("director", "director2", "operator", "operator2", "coordinator")
SERVICE_TIERS = ("fast", "default")
DEFAULT_CONFIG_PATH = Path("~/.codex/pipeline-seat-launcher.toml")

# The launcher owns runtime identity and repository scope. Approval and sandbox
# posture remain capabilities of the trusted user/project Codex configuration;
# this launcher does not attest their effective values. It rejects per-invocation
# forwarded overrides so an otherwise fixed launch cannot silently change its
# execution shape. Scan every token, including tokens after a bare ``--``.
_FORBIDDEN_FORWARDED_LONG_FLAGS = frozenset(
    {
        "--add-dir",
        "--ask-for-approval",
        "--bypass",
        "--cd",
        "--config",
        "--dangerously-bypass-approvals-and-sandbox",
        "--dangerously-bypass-hook-trust",
        "--disable",
        "--enable",
        "--full-auto",
        "--ignore-rules",
        "--local-provider",
        "--model",
        "--oss",
        "--profile",
        "--remote",
        "--remote-auth-token-env",
        "--sandbox",
        "--yolo",
    }
)
_FORBIDDEN_FORWARDED_SHORT_FLAGS = frozenset({"-C", "-a", "-c", "-m", "-p", "-s"})
_FORBIDDEN_FORWARDED_SUBCOMMANDS = frozenset(
    {
        "a",
        "app",
        "app-server",
        "apply",
        "archive",
        "cloud",
        "completion",
        "debug",
        "delete",
        "doctor",
        "e",
        "exec",
        "exec-server",
        "features",
        "fork",
        "help",
        "login",
        "logout",
        "mcp",
        "mcp-server",
        "plugin",
        "remote-control",
        "resume",
        "review",
        "sandbox",
        "unarchive",
        "update",
    }
)


class ConfigError(ValueError):
    """Raised when the local per-seat configuration is invalid."""


class LaunchError(RuntimeError):
    """Raised when local launch preparation fails."""


def _forbidden_forwarded_flag(token: str) -> str | None:
    if token.startswith("--"):
        name = token.split("=", 1)[0]
        return name if name in _FORBIDDEN_FORWARDED_LONG_FLAGS else None
    for name in _FORBIDDEN_FORWARDED_SHORT_FLAGS:
        if (
            token == name
            or token.startswith(name + "=")
            or (token.startswith(name) and len(token) > 2)
        ):
            return name
    return None


def reject_security_overrides(forwarded_args: Sequence[str]) -> None:
    """Reject child-CLI arguments that can contradict launcher-owned state."""

    for token in forwarded_args:
        if token in _FORBIDDEN_FORWARDED_SUBCOMMANDS:
            raise LaunchError(
                f"forwarded argument {token!r} may not override launcher-owned "
                "identity, workspace, or security policy (Codex subcommand)"
            )
        forbidden = _forbidden_forwarded_flag(token)
        if forbidden is not None:
            raise LaunchError(
                f"forwarded argument {token!r} may not override launcher-owned "
                f"identity, workspace, or security policy ({forbidden})"
            )


@dataclass(frozen=True)
class SeatSettings:
    model: str
    service_tier: str


@dataclass(frozen=True)
class LaunchSpec:
    argv: tuple[str, ...]
    env: dict[str, str]
    repo_root: Path
    identity: RuntimeIdentity


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

    reject_security_overrides(forwarded_args)
    selected = settings[seat]
    identity = RuntimeIdentity.for_seat(seat, model=selected.model)
    env = {
        key: value
        for key, value in inherited_env.items()
        if key not in RUNTIME_SCRUB_ENV_KEYS
    }
    env.update(identity.as_env())
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
        identity=identity,
    )


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
    repo_root = Path.cwd().resolve()
    try:
        settings = load_seat_settings(args.config)
        codex_executable = shutil.which("codex")
        if codex_executable is None and not args.dry_run:
            raise LaunchError("codex executable not found on PATH")
        spec = build_launch_spec(
            repo_root,
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
            )
            print(
                json.dumps(
                    {
                        "argv": list(spec.argv),
                        "env": {key: spec.env[key] for key in identity_keys if key in spec.env},
                    },
                    indent=2,
                    sort_keys=True,
                )
            )
            return 0

        os.execvpe(spec.argv[0], list(spec.argv), spec.env)
    except (ConfigError, LaunchError) as exc:
        print(f"codex-seat: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
