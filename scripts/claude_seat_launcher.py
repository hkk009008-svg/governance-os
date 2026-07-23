#!/usr/bin/env python3
"""Launch one provider-pure local Claude seat."""

from __future__ import annotations

import argparse
import json
import os
import shutil
import stat
import subprocess
import sys
from collections.abc import Callable, Mapping, Sequence
from dataclasses import dataclass
from pathlib import Path


LAUNCH_SEATS = ("director", "director2", "operator", "operator2")
_FOREIGN_AUTHORITY_PREFIXES = (
    "CODEX_",
    "CURSOR_",
    "AGY_",
    "ANTIGRAVITY_",
    "GIT_",
)
_PRESERVED_CLAUDE_CREDENTIALS = frozenset({"CLAUDE_CODE_OAUTH_TOKEN"})


class LaunchError(RuntimeError):
    """Raised when Claude launch preparation fails."""


@dataclass(frozen=True)
class LaunchSpec:
    argv: tuple[str, ...]
    env: dict[str, str]
    repo_root: Path
    index_path: Path


def _clean_inherited_environment(environ: Mapping[str, str]) -> dict[str, str]:
    """Preserve ordinary/credential state while removing runtime authority."""

    return {
        key: value
        for key, value in environ.items()
        if not key.startswith(_FOREIGN_AUTHORITY_PREFIXES)
        and (not key.startswith("CLAUDE_") or key in _PRESERVED_CLAUDE_CREDENTIALS)
    }


def _without_inherited_git_authority(environ: Mapping[str, str]) -> dict[str, str]:
    return {key: value for key, value in environ.items() if not key.startswith("GIT_")}


def build_launch_spec(
    repo_root: Path,
    git_dir: Path,
    seat: str,
    inherited_env: Mapping[str, str],
    claude_executable: str,
    forwarded_args: Sequence[str],
) -> LaunchSpec:
    """Build the provider-pure argv/env without performing side effects."""

    if seat not in LAUNCH_SEATS:
        raise LaunchError(f"unsupported Claude seat: {seat}")
    index_path = git_dir / f"index-claude-{seat}"
    env = _clean_inherited_environment(inherited_env)
    env.update(
        {
            "CLAUDE_SEAT": seat,
            "CLAUDE_PROJECT_DIR": str(repo_root),
            "GIT_INDEX_FILE": str(index_path),
        }
    )
    return LaunchSpec(
        argv=(claude_executable, *forwarded_args),
        env=env,
        repo_root=repo_root,
        index_path=index_path,
    )


def resolve_git_dir(repo_root: Path) -> Path:
    """Resolve the Git directory without trusting inherited Git authority."""

    result = subprocess.run(
        ["git", "-C", str(repo_root), "rev-parse", "--absolute-git-dir"],
        env=_without_inherited_git_authority(os.environ),
        text=True,
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        raise LaunchError(result.stderr.strip() or "cannot resolve Git directory")
    return Path(result.stdout.strip())


def ensure_seat_index(
    repo_root: Path,
    index_path: Path,
    *,
    runner: Callable[..., subprocess.CompletedProcess[str]] = subprocess.run,
) -> None:
    """Seed one missing Claude index; validate and preserve an existing one."""

    try:
        index_mode = index_path.lstat().st_mode
    except FileNotFoundError:
        index_mode = None
    if index_mode is not None:
        if not stat.S_ISREG(index_mode):
            raise LaunchError(
                f"existing Claude seat index {index_path} must be a regular file; "
                "refusing to launch without changing it"
            )
        index_env = _without_inherited_git_authority(os.environ)
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
                f"existing Claude seat index {index_path} is unusable: "
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
                env=_without_inherited_git_authority(os.environ),
                text=True,
                capture_output=True,
                check=False,
            )
            if head_entries.returncode != 0:
                detail = head_entries.stderr.strip() or head_entries.stdout.strip()
                raise LaunchError(detail or "cannot inspect HEAD before Claude launch")
            if head_entries.stdout:
                raise LaunchError(
                    f"existing Claude seat index {index_path} is empty while HEAD "
                    "tracks files; refusing to launch without changing the index"
                )
        status_result = runner(
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
        if status_result.returncode != 0:
            detail = status_result.stderr.strip() or status_result.stdout.strip()
            raise LaunchError(
                f"existing Claude seat index {index_path} is unusable: "
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
        env=_without_inherited_git_authority(os.environ),
        text=True,
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        raise LaunchError(
            result.stderr.strip() or f"cannot seed Claude seat index {index_path}"
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
        description="Launch Claude with one provider-pure Pipeline seat index."
    )
    parser.add_argument("--dry-run", action="store_true", help="print launch data only")
    parser.add_argument("seat", choices=LAUNCH_SEATS)
    return parser.parse_args(launcher_args), forwarded_args


def main(argv: Sequence[str] | None = None) -> int:
    args, forwarded_args = _parse_args(sys.argv[1:] if argv is None else argv)
    repo_root = Path(__file__).resolve().parents[1]
    try:
        git_dir = resolve_git_dir(repo_root)
        claude_executable = shutil.which("claude")
        if claude_executable is None and not args.dry_run:
            raise LaunchError("claude executable not found on PATH")
        spec = build_launch_spec(
            repo_root,
            git_dir,
            args.seat,
            os.environ,
            claude_executable or "claude",
            forwarded_args,
        )
        if args.dry_run:
            print(
                json.dumps(
                    {
                        "argv": list(spec.argv),
                        "env": {
                            key: spec.env[key]
                            for key in ("CLAUDE_SEAT", "CLAUDE_PROJECT_DIR", "GIT_INDEX_FILE")
                        },
                        "index_exists": spec.index_path.exists(),
                    },
                    indent=2,
                    sort_keys=True,
                )
            )
            return 0
        ensure_seat_index(spec.repo_root, spec.index_path)
        os.chdir(spec.repo_root)
        os.execvpe(spec.argv[0], list(spec.argv), spec.env)
    except LaunchError as exc:
        print(f"claude-seat: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
