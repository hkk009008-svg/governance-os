#!/usr/bin/env python3
"""Archive stale top-level docs/HANDOFF-*.md into docs/archive/<UTC-date>/.

AUDIT-2026-06-13.md H5 remediation tool (handoff doc sprawl). SAFE BY DEFAULT:

  * DRY-RUN unless you pass --yes. Run once to preview, then again with --yes.
  * You MUST preserve the ACTIVE handoff set — the MEMORY "current state"
    READ-FIRST handoff per seat, the roadmap handoff, and anything an active
    instruction doc links to (e.g. DECISIONS.md). Pass each as --keep <basename>
    (repeatable). Moving EVERY handoff breaks those READ-FIRST links, so the
    script prints a loud warning (and, with --strict, refuses) when --keep is
    empty. Filenames do NOT sort by recency, so a heuristic "latest" is unsafe;
    the keep-set is a human/MEMORY judgment passed in explicitly.
  * Requires a clean repository and uses only `git mv` (history preserved).
    A later move/index failure restores earlier moves before returning failure.
  * Writes/extends INDEX.md in the target archive dir.

Example (reproduces a curated archive — keep the active READ-FIRST set for each seat):
  python scripts/archive_handoffs.py --yes \
    --keep HANDOFF-coordinator-<date>.md \
    --keep HANDOFF-roadmap-<date>.md \
    --keep HANDOFF-director-<date>-<slug>.md \
    --keep HANDOFF-operator-<date>-<slug>.md \
    --keep HANDOFF-director2-<date>-<slug>.md \
    --keep HANDOFF-operator2-<date>-<slug>.md \
    --keep HANDOFF-director-transplant-<date>-<slug>.md
"""
import argparse
import datetime
import glob
import os
import stat
import subprocess
import tempfile


def _git_mv(repo_root, rel_src, rel_dst):
    """Stage one history-preserving move or fail visibly."""
    try:
        subprocess.run(
            ["git", "mv", rel_src, rel_dst],
            cwd=repo_root,
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.PIPE,
        )
    except (OSError, subprocess.CalledProcessError) as exc:
        detail = getattr(exc, "stderr", b"")
        if isinstance(detail, bytes):
            detail = detail.decode("utf-8", errors="replace")
        raise RuntimeError(f"git mv failed for {rel_src}: {str(detail).strip()}") from exc


def _require_clean_repo(repo_root):
    result = subprocess.run(
        ["git", "status", "--porcelain", "--untracked-files=normal"],
        cwd=repo_root,
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    if result.stdout:
        raise RuntimeError("archive_handoffs requires a clean worktree and index")


def _stage_index(repo_root, index):
    relative = os.path.relpath(index, repo_root)
    subprocess.run(
        ["git", "add", "--", relative],
        cwd=repo_root,
        check=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.PIPE,
    )


def _validate_archive_target(repo_root, target):
    """Reject targets or existing ancestors that would escape through a symlink."""

    root = os.path.abspath(repo_root)
    destination = os.path.abspath(target)
    if os.path.commonpath((root, destination)) != root:
        raise RuntimeError(f"archive target is outside the repository: {target}")
    current = root
    for component in os.path.relpath(destination, root).split(os.sep):
        current = os.path.join(current, component)
        if not os.path.lexists(current):
            continue
        metadata = os.lstat(current)
        if stat.S_ISLNK(metadata.st_mode):
            raise RuntimeError(f"archive target path must not contain a symlink: {current}")
        if not stat.S_ISDIR(metadata.st_mode):
            raise RuntimeError(f"archive target path component is not a directory: {current}")


def _read_regular_bytes(path):
    flags = os.O_RDONLY
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    try:
        descriptor = os.open(path, flags)
    except OSError as exc:
        raise RuntimeError(f"archive index must be a regular non-symlink file: {path}") from exc
    try:
        metadata = os.fstat(descriptor)
        if not stat.S_ISREG(metadata.st_mode):
            raise RuntimeError(f"archive index must be a regular non-symlink file: {path}")
        with os.fdopen(descriptor, "rb", closefd=True) as handle:
            descriptor = -1
            return handle.read()
    finally:
        if descriptor >= 0:
            os.close(descriptor)


def _atomic_write_bytes(path, data):
    directory = os.path.dirname(path)
    descriptor, temporary = tempfile.mkstemp(prefix=".INDEX.md.", dir=directory)
    try:
        os.fchmod(descriptor, 0o644)
        with os.fdopen(descriptor, "wb", closefd=True) as handle:
            descriptor = -1
            handle.write(data)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    except BaseException:
        if descriptor >= 0:
            os.close(descriptor)
        try:
            os.unlink(temporary)
        except FileNotFoundError:
            pass
        raise


def _archive_batch(repo_root, target, date_str, to_move, kept):
    """Move and index one archive batch, rolling back this batch on failure."""
    _require_clean_repo(repo_root)
    _validate_archive_target(repo_root, target)
    target_existed = os.path.exists(target)
    pairs = []
    for src in to_move:
        basename = os.path.basename(src)
        destination = os.path.join(target, basename)
        if not os.path.isfile(src):
            raise RuntimeError(f"handoff source is not a file: {src}")
        if os.path.lexists(destination):
            raise RuntimeError(f"archive destination already exists: {destination}")
        pairs.append(
            (
                os.path.relpath(src, repo_root),
                os.path.relpath(destination, repo_root),
            )
        )

    os.makedirs(target, exist_ok=True)
    _validate_archive_target(repo_root, target)
    index = os.path.join(target, "INDEX.md")
    index_existed = os.path.lexists(index)
    if index_existed:
        index_before = _read_regular_bytes(index)
    else:
        index_before = None
    moved = []
    try:
        for rel_src, rel_dst in pairs:
            _git_mv(repo_root, rel_src, rel_dst)
            moved.append((rel_src, rel_dst))
            print("    moved %s" % os.path.basename(rel_src))
        _write_index(
            target,
            date_str,
            [os.path.basename(src) for src in to_move],
            [os.path.basename(path) for path in kept],
        )
        _stage_index(repo_root, index)
    except BaseException as original:
        rollback_failures = []
        try:
            if index_existed:
                _atomic_write_bytes(index, index_before)
            else:
                try:
                    os.unlink(index)
                except FileNotFoundError:
                    pass
            subprocess.run(
                ["git", "reset", "-q", "HEAD", "--", os.path.relpath(index, repo_root)],
                cwd=repo_root,
                check=False,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
        except OSError as exc:
            rollback_failures.append(f"index restore failed: {exc}")
        for rel_src, rel_dst in reversed(moved):
            try:
                _git_mv(repo_root, rel_dst, rel_src)
            except Exception as exc:
                rollback_failures.append(f"move restore failed for {rel_src}: {exc}")
        if not target_existed:
            try:
                os.rmdir(target)
            except OSError:
                pass
        if rollback_failures:
            raise RuntimeError(
                "archive failed and rollback was incomplete: "
                + "; ".join(rollback_failures)
            ) from original
        raise
    return index, len(moved)


def _write_index(target, date_str, moved_names, kept_names):
    """Write one cumulative, idempotent daily archive index."""
    index = os.path.join(target, "INDEX.md")
    indexed = set()
    if os.path.lexists(index):
        try:
            existing_text = _read_regular_bytes(index).decode("utf-8")
        except UnicodeError as exc:
            raise RuntimeError(f"archive index is not UTF-8: {index}") from exc
        for line in existing_text.splitlines():
            if line.startswith("- [") and "](" in line:
                indexed.add(line[3:].split("](", 1)[0])
    indexed.update(os.path.basename(name) for name in moved_names)
    lines = [
        "# Handoff archive — %s\n\n" % date_str,
        "Index contains %d archived handoffs. Kept active at docs/: %s.\n\n"
        % (len(indexed), ", ".join(sorted(kept_names)) or "(none)"),
    ]
    lines.extend("- [%s](%s)\n" % (name, name) for name in sorted(indexed))
    _atomic_write_bytes(index, "".join(lines).encode("utf-8"))
    return index


def _select_handoffs(handoffs, keep):
    """Partition discovered handoffs and reject every unmatched keep name."""

    by_name = {os.path.basename(path): path for path in handoffs}
    unknown = sorted(set(keep) - set(by_name))
    if unknown:
        raise ValueError("--keep did not match a top-level handoff: " + ", ".join(unknown))
    return (
        [path for path in handoffs if os.path.basename(path) not in keep],
        [path for path in handoffs if os.path.basename(path) in keep],
    )


def main():
    ap = argparse.ArgumentParser(description="Archive stale docs/HANDOFF-*.md (AUDIT H5).")
    ap.add_argument("--keep", action="append", default=[], metavar="BASENAME",
                    help="Handoff basename to KEEP at top-level (repeatable). The active READ-FIRST set.")
    ap.add_argument("--yes", action="store_true", help="Actually move (default is a dry-run preview).")
    ap.add_argument("--strict", action="store_true", help="Refuse to run if --keep is empty.")
    args = ap.parse_args()

    repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    docs_dir = os.path.join(repo_root, "docs")
    keep = set(args.keep)

    handoffs = sorted(glob.glob(os.path.join(docs_dir, "HANDOFF-*.md")))
    if not handoffs:
        print("No top-level docs/HANDOFF-*.md found — nothing to archive.")
        return

    try:
        to_move, kept = _select_handoffs(handoffs, keep)
    except ValueError as exc:
        ap.error(str(exc))

    if not keep:
        msg = ("WARNING: no --keep given — this would archive ALL %d handoffs, breaking the "
               "MEMORY/CLAUDE/DECISIONS READ-FIRST links. Pass --keep <basename> for the active set." % len(handoffs))
        if args.strict:
            raise SystemExit("REFUSING (--strict): " + msg)
        print(msg)

    date_str = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d")
    target = os.path.join(docs_dir, "archive", date_str)
    mode = "MOVE" if args.yes else "DRY-RUN (pass --yes to apply)"
    print("== archive_handoffs [%s] -> docs/archive/%s/ ==" % (mode, date_str))
    print("  keep (%d): %s" % (len(kept), ", ".join(sorted(os.path.basename(p) for p in kept)) or "(none)"))
    print("  move (%d):" % len(to_move))

    if not args.yes:
        for p in to_move:
            print("    would move %s" % os.path.basename(p))
        print("== dry-run complete; re-run with --yes to apply ==")
        return

    index, moved = _archive_batch(repo_root, target, date_str, to_move, kept)
    print("== archived %d handoffs; wrote %s ==" % (moved, os.path.relpath(index, repo_root)))


if __name__ == "__main__":
    main()
