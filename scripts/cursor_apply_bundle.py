#!/usr/bin/env python3
"""Apply a readiness-staged Cursor scratch bundle into the managed tree."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import sys
from collections.abc import Mapping, Sequence
from pathlib import Path

BUNDLE_ROOT = Path(".pytest-verify-tmp/cursor-bundles")
FORBIDDEN_PREFIXES = (
    "coordination/mailbox/",
    "coordination/locks/",
    ".cursor/runtime/",
    "scripts/agy_",
    "scripts/codex_",
    "scripts/claude_",
    "coordination/bin/agy-",
    "coordination/bin/codex-",
    "coordination/bin/claude-",
)


class BundleError(RuntimeError):
    """Bundle apply cannot proceed without guessing or new authority."""


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _confirm(prompt: str, *, stdin_isatty: bool) -> None:
    if not stdin_isatty:
        raise BundleError("bundle apply requires an interactive controlling terminal")
    answer = input(prompt).strip()
    if answer != "yes":
        raise BundleError("bundle apply cancelled; type exact yes to continue")


def may_skip_tty(environ: Mapping[str, str]) -> bool:
    """Skip TTY only for a build seat bind (not mailbox live_bound)."""

    if environ.get("CURSOR_OPERATION") != "build":
        return False
    seat = environ.get("CURSOR_SEAT", "")
    index = environ.get("GIT_INDEX_FILE", "")
    # build is intentionally outside mailbox LIVE_OPERATIONS; require seat index only.
    return bool(seat) and bool(index) and index.endswith("index-cursor-" + seat)


def load_manifest(root: Path, bundle_id: str) -> tuple[Path, dict]:
    bundle_dir = (root / BUNDLE_ROOT / bundle_id).resolve()
    scratch_root = (root / ".pytest-verify-tmp").resolve()
    if not str(bundle_dir).startswith(str(scratch_root) + os.sep):
        raise BundleError("bundle id escapes scratch root")
    manifest_path = bundle_dir / "manifest.json"
    if not manifest_path.is_file():
        raise BundleError("missing manifest: " + str(manifest_path))
    try:
        document = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise BundleError("cannot read manifest: " + str(exc)) from exc
    if not isinstance(document, dict) or not isinstance(document.get("files"), list):
        raise BundleError("manifest must be an object with a files list")
    return bundle_dir, document


def validate_entry(rel: str, digest: str) -> None:
    if not rel or rel.startswith("/") or ".." in Path(rel).parts:
        raise BundleError("illegal bundle path: " + repr(rel))
    if any(rel == prefix.rstrip("/") or rel.startswith(prefix) for prefix in FORBIDDEN_PREFIXES):
        raise BundleError("forbidden bundle path: " + rel)
    if not isinstance(digest, str) or len(digest) != 64:
        raise BundleError("invalid sha256 for " + rel)


def plan_copies(root: Path, bundle_dir: Path, document: dict) -> list[tuple[Path, Path, str]]:
    planned: list[tuple[Path, Path, str]] = []
    for entry in document["files"]:
        if not isinstance(entry, dict):
            raise BundleError("each files entry must be an object")
        rel = entry.get("path")
        digest = entry.get("sha256")
        if not isinstance(rel, str) or not isinstance(digest, str):
            raise BundleError("files entries require path and sha256 strings")
        validate_entry(rel, digest)
        source = bundle_dir / "tree" / rel
        if not source.is_file():
            raise BundleError("missing staged file: " + str(source))
        actual = _sha256(source)
        if actual != digest:
            raise BundleError("hash mismatch for " + rel + ": " + actual + " != " + digest)
        planned.append((source, root / rel, rel))
    return planned


def apply_bundle(
    root: Path,
    bundle_id: str,
    *,
    dry_run: bool,
    environ: Mapping[str, str],
    stdin_isatty: bool,
) -> int:
    bundle_dir, document = load_manifest(root, bundle_id)
    planned = plan_copies(root, bundle_dir, document)
    print("bundle=" + bundle_id + " files=" + str(len(planned)))
    for _, dest, rel in planned:
        print("  " + rel + " -> " + str(dest))
    if dry_run:
        print("dry-run: no files copied")
        return 0
    if not may_skip_tty(environ):
        _confirm(
            "Type yes to copy " + str(len(planned)) + " file(s) from bundle " + repr(bundle_id) + ": ",
            stdin_isatty=stdin_isatty,
        )
    for source, dest, rel in planned:
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, dest)
        dest.chmod(source.stat().st_mode)
        print("copied " + rel)
    print("next: env -u GIT_INDEX_FILE .venv/bin/python scripts/cursor_land_gate.py")
    return 0


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="cursor-apply-bundle")
    parser.add_argument("bundle_id")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument(
        "--root",
        type=Path,
        default=Path(__file__).resolve().parents[1],
    )
    args = parser.parse_args(sys.argv[1:] if argv is None else argv)
    try:
        return apply_bundle(
            args.root.resolve(),
            args.bundle_id,
            dry_run=args.dry_run,
            environ=os.environ,
            stdin_isatty=sys.stdin.isatty(),
        )
    except BundleError as exc:
        print("cursor-apply-bundle: " + str(exc), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
