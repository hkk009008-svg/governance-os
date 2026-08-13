#!/usr/bin/env python3
"""Materialize one committed review head into bounded scratch without Git mutation."""

from __future__ import annotations

import argparse
import io
import os
from pathlib import Path, PurePosixPath
import shutil
import subprocess
import sys
import tarfile
import tempfile
from collections.abc import Mapping, Sequence


MAX_ARCHIVE_BYTES = 512 * 1024 * 1024
MARKER = ".pipeline-review-head"


class ReviewSnapshotError(RuntimeError):
    """A requested immutable review snapshot is unsafe or unavailable."""


def _git(
    repository: Path,
    *args: str,
    environ: Mapping[str, str] | None = None,
) -> bytes:
    source = os.environ if environ is None else environ
    env = {key: value for key, value in source.items() if not key.startswith("GIT_")}
    result = subprocess.run(
        [
            "git",
            "--no-optional-locks",
            "-C",
            str(repository),
            *args,
        ],
        env=env,
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        detail = result.stderr.decode("utf-8", "replace").strip()
        raise ReviewSnapshotError(detail or f"git {' '.join(args)} failed")
    return result.stdout


def _full_commit(repository: Path, revision: str) -> str:
    if not revision or revision.startswith("-"):
        raise ReviewSnapshotError("review head is invalid")
    resolved = _git(repository, "rev-parse", "--verify", f"{revision}^{{commit}}")
    commit = resolved.decode("ascii", "strict").strip()
    if len(commit) != 40:
        raise ReviewSnapshotError("review head did not resolve to one full commit")
    return commit


def _scratch_destination(workspace: Path, output: Path) -> Path:
    root = workspace.resolve()
    scratch = (root / ".pytest-verify-tmp" / "cursor-reviews").resolve()
    destination = (
        output.expanduser().resolve(strict=False)
        if output.is_absolute()
        else (root / output).resolve(strict=False)
    )
    try:
        destination.relative_to(scratch)
    except ValueError as exc:
        raise ReviewSnapshotError(
            "review snapshot output must be under .pytest-verify-tmp/cursor-reviews"
        ) from exc
    if destination == scratch:
        raise ReviewSnapshotError("review snapshot output must name a commit directory")
    return destination


def _member_path(root: Path, name: str) -> Path:
    relative = PurePosixPath(name)
    if relative.is_absolute() or ".." in relative.parts or not relative.parts:
        raise ReviewSnapshotError(f"unsafe archive path: {name}")
    destination = root.joinpath(*relative.parts).resolve(strict=False)
    try:
        destination.relative_to(root.resolve())
    except ValueError as exc:
        raise ReviewSnapshotError(f"archive path escapes snapshot: {name}") from exc
    return destination


def _extract(archive: bytes, destination: Path) -> None:
    if len(archive) > MAX_ARCHIVE_BYTES:
        raise ReviewSnapshotError("review archive exceeds the 512 MiB limit")
    with tarfile.open(fileobj=io.BytesIO(archive), mode="r:") as tar:
        for member in tar:
            target = _member_path(destination, member.name)
            if member.isdir():
                target.mkdir(mode=0o755, parents=True, exist_ok=True)
                continue
            target.parent.mkdir(mode=0o755, parents=True, exist_ok=True)
            if member.isfile():
                source = tar.extractfile(member)
                if source is None:
                    raise ReviewSnapshotError(f"cannot read archive member: {member.name}")
                with source, target.open("wb") as output:
                    shutil.copyfileobj(source, output)
                target.chmod(member.mode & 0o777)
                continue
            if member.issym():
                link_target = (target.parent / member.linkname).resolve(strict=False)
                try:
                    link_target.relative_to(destination.resolve())
                except ValueError as exc:
                    raise ReviewSnapshotError(
                        f"archive symlink escapes snapshot: {member.name}"
                    ) from exc
                target.symlink_to(member.linkname)
                continue
            raise ReviewSnapshotError(
                f"unsupported archive member type: {member.name}"
            )


def require_exact_head(repository: Path, reviewed_head: str) -> str:
    """Fail closed unless the repository HEAD is exactly ``reviewed_head``.

    Repository-level gates (``governance_verify_all.py``, ``cursor_land_gate.py``) need a
    real ``.git`` history. Call this before those gates, or host them in a
    detached worktree checked out at ``reviewed_head``.
    """

    repository = repository.expanduser().resolve(strict=True)
    expected = _full_commit(repository, reviewed_head)
    head = _full_commit(repository, "HEAD")
    if head != expected:
        raise ReviewSnapshotError(
            f"repository HEAD {head} is not reviewed_head {expected}; "
            "run repository-level gates only at the exact reviewed head"
        )
    return head


def materialize(
    workspace: Path,
    *,
    repository: Path,
    head: str,
    output: Path,
) -> Path:
    workspace = workspace.resolve()
    repository = repository.expanduser().resolve(strict=True)
    commit = _full_commit(repository, head)
    destination = _scratch_destination(workspace, output)
    marker = destination / MARKER
    if destination.exists():
        if marker.is_file() and marker.read_text(encoding="ascii").strip() == commit:
            return destination
        raise ReviewSnapshotError("review snapshot destination already exists")
    destination.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
    temporary = Path(
        tempfile.mkdtemp(prefix=f".{commit[:12]}.", dir=destination.parent)
    )
    try:
        archive = _git(repository, "archive", "--format=tar", commit)
        _extract(archive, temporary)
        (temporary / MARKER).write_text(commit + "\n", encoding="ascii")
        os.replace(temporary, destination)
    finally:
        if temporary.exists():
            shutil.rmtree(temporary)
    return destination


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="cursor-review-snapshot")
    parser.add_argument("--workspace", type=Path, default=Path.cwd())
    parser.add_argument("--repository", type=Path, required=True)
    parser.add_argument("--head", required=True)
    parser.add_argument("--output", type=Path)
    parser.add_argument(
        "--require-exact-head",
        action="store_true",
        help="verify repository HEAD equals --head; do not materialize",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        if args.require_exact_head:
            print(require_exact_head(args.repository, args.head))
            return 0
        if args.output is None:
            raise ReviewSnapshotError("--output is required unless --require-exact-head")
        destination = materialize(
            args.workspace,
            repository=args.repository,
            head=args.head,
            output=args.output,
        )
    except (OSError, UnicodeError, ReviewSnapshotError) as exc:
        print(f"cursor-review-snapshot: {exc}", file=sys.stderr)
        return 2
    print(destination)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
