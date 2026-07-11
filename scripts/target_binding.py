#!/usr/bin/env python3
"""Declarative multi-target binding registry (governance.toml, ADR-013).

The kernel governs product repos declared in governance.toml instead of
Python path constants, so future works can be started here without code
edits. Resolution is fail-closed: a missing file, unknown target, missing
required key, or unknown per-target key raises BindingError with a
corrective message rather than falling back to a guess.

Resolution order for the active target name:
    explicit name argument (CLI --target)
        > GOVERNANCE_TARGET environment variable
        > [binding].default_target in governance.toml
Local-checkout override for the SELECTED target: GOVERNANCE_TARGET_PATH.
"""
from __future__ import annotations

import argparse
import os
import sys
import tomllib
from dataclasses import dataclass
from pathlib import Path
from typing import Mapping

_REPO_ROOT = Path(__file__).resolve().parent.parent

CONFIG_NAME = "governance.toml"
ENV_TARGET_NAME = "GOVERNANCE_TARGET"
ENV_TARGET_PATH = "GOVERNANCE_TARGET_PATH"

_TARGET_REQUIRED_KEYS = ("repository", "path")
_TARGET_OPTIONAL_KEYS = ("route_keywords", "description")


class BindingError(ValueError):
    """The binding registry is absent, structurally invalid, or ambiguous."""


@dataclass(frozen=True)
class TargetBinding:
    name: str
    repository: str
    path: Path
    route_keywords: tuple[str, ...]
    description: str = ""
    source: str = "governance.toml"


def _resolve_path(raw: str) -> Path:
    return Path(raw).expanduser().resolve(strict=False)


def load_config(root: Path | str | None = None) -> dict:
    """Parse and structurally validate governance.toml under root. Fail-closed."""
    root_path = Path(root) if root is not None else _REPO_ROOT
    config_path = root_path / CONFIG_NAME
    try:
        raw = config_path.read_bytes()
    except OSError as exc:
        raise BindingError(
            f"missing binding registry {config_path.as_posix()} — create "
            f"{CONFIG_NAME} with a [targets.<name>] table and "
            "[binding].default_target (ADR-013)"
        ) from exc
    try:
        config = tomllib.loads(raw.decode("utf-8"))
    except (tomllib.TOMLDecodeError, UnicodeDecodeError) as exc:
        raise BindingError(f"{config_path.as_posix()}: unparseable TOML: {exc}") from exc

    binding = config.get("binding")
    if not isinstance(binding, dict) or not isinstance(binding.get("default_target"), str):
        raise BindingError(
            f"{config_path.as_posix()}: [binding].default_target (string) is required"
        )
    targets = config.get("targets")
    if not isinstance(targets, dict) or not targets:
        raise BindingError(
            f"{config_path.as_posix()}: at least one [targets.<name>] table is required"
        )
    for name, table in targets.items():
        if not isinstance(table, dict):
            raise BindingError(f"{config_path.as_posix()}: [targets.{name}] must be a table")
        missing = [key for key in _TARGET_REQUIRED_KEYS if not isinstance(table.get(key), str)]
        if missing:
            raise BindingError(
                f"{config_path.as_posix()}: [targets.{name}] missing required "
                "string key(s): " + ", ".join(missing)
            )
        unknown = sorted(set(table) - set(_TARGET_REQUIRED_KEYS) - set(_TARGET_OPTIONAL_KEYS))
        if unknown:
            raise BindingError(
                f"{config_path.as_posix()}: [targets.{name}] has unknown key(s): "
                + ", ".join(unknown)
            )
        keywords = table.get("route_keywords", [])
        if not isinstance(keywords, list) or not all(
            isinstance(keyword, str) and keyword.strip() for keyword in keywords
        ):
            raise BindingError(
                f"{config_path.as_posix()}: [targets.{name}].route_keywords must be "
                "a list of non-empty strings"
            )
    default = binding["default_target"]
    if default not in targets:
        raise BindingError(
            f"{config_path.as_posix()}: default_target `{default}` is not a registered "
            "target; known targets: " + ", ".join(sorted(targets))
        )
    return config


def _binding_from_table(name: str, table: dict, *, source: str) -> TargetBinding:
    keywords = tuple(keyword.lower() for keyword in table.get("route_keywords", [])) or (
        name.lower(),
    )
    return TargetBinding(
        name=name,
        repository=table["repository"],
        path=_resolve_path(table["path"]),
        route_keywords=keywords,
        description=table.get("description", ""),
        source=source,
    )


def list_targets(root: Path | str | None = None) -> tuple[TargetBinding, ...]:
    config = load_config(root)
    return tuple(
        _binding_from_table(name, table, source="governance.toml")
        for name, table in config["targets"].items()
    )


def resolve_target(
    root: Path | str | None = None,
    *,
    name: str | None = None,
    env: Mapping[str, str] | None = None,
) -> TargetBinding:
    """Resolve the active target binding. Fail-closed on unknown names."""
    environ = os.environ if env is None else env
    config = load_config(root)
    targets = config["targets"]
    selected = name or environ.get(ENV_TARGET_NAME) or config["binding"]["default_target"]
    if selected not in targets:
        raise BindingError(
            f"unknown target `{selected}`; known targets: " + ", ".join(sorted(targets))
        )
    source = "governance.toml"
    binding = _binding_from_table(selected, targets[selected], source=source)
    path_override = environ.get(ENV_TARGET_PATH)
    if path_override:
        binding = TargetBinding(
            name=binding.name,
            repository=binding.repository,
            path=_resolve_path(path_override),
            route_keywords=binding.route_keywords,
            description=binding.description,
            source=f"governance.toml + {ENV_TARGET_PATH} path override",
        )
    return binding


def forbidden_roots(root: Path | str | None = None) -> tuple[Path, ...]:
    """Roots a governed seat must never start from ([paths].forbidden_roots)."""
    config = load_config(root)
    raw = config.get("paths", {}).get("forbidden_roots", [])
    if not isinstance(raw, list) or not all(isinstance(item, str) for item in raw):
        raise BindingError("[paths].forbidden_roots must be a list of strings")
    return tuple(_resolve_path(item) for item in raw)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Validate the governance.toml target-binding registry (read-only).",
    )
    parser.add_argument("--root", default=str(_REPO_ROOT))
    parser.add_argument(
        "--check",
        action="store_true",
        help="validate the registry (the default and only action)",
    )
    args = parser.parse_args(argv)

    try:
        config = load_config(args.root)
        targets = list_targets(args.root)
        roots = forbidden_roots(args.root)
    except BindingError as exc:
        print("TARGET BINDING — FAIL")
        print(f"- {exc}")
        return 1

    default = config["binding"]["default_target"]
    print("TARGET BINDING — registry OK")
    for target in targets:
        marker = " (default)" if target.name == default else ""
        exists = "present" if target.path.exists() else "absent (informational)"
        print(f"- {target.name}{marker}: {target.repository}")
        print(f"    path: {target.path.as_posix()} [{exists}]")
        print(f"    route_keywords: {', '.join(target.route_keywords)}")
    if roots:
        print("- forbidden roots: " + ", ".join(item.as_posix() for item in roots))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
