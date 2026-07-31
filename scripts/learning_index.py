#!/usr/bin/env python3
"""Read-only episodic index over committed governance artifacts (Stage 1).

Contract: docs/protocol/learning/contract.md (ADR-067). The index is a
derived, rebuildable, WORKSPACE-scope projection with no authority: it grants
nothing, gates nothing, and is never committed (`coordination/learning/` is
gitignored). It ingests committed repository-scope sources only — never
user-scope paths (home directories, session transcripts); the bridge for
those is a learning-candidate event, not this index.

Sources and per-source timestamp rules (all read from the committed tree at
the build commit, never the worktree):

- ``coordination/mailbox/sent/*.md`` — fixed-writer events; timestamp is the
  filename timestamp (rule ``filename``).
- ``docs/HANDOFF-*.md`` and ``docs/superpowers/plans/*.md`` — timestamp is
  the leading ``YYYY-MM-DD`` date token in the filename when present (rule
  ``filename``), else the build commit's committer date (rule
  ``commit-date``).
- ``logs/**/*.jsonl`` — row-record ledgers; timestamp is the first
  ``ts``/``when``/``timestamp`` value found in the first parseable row (rule
  ``row-field``), else the build commit's committer date. Plain ``.json``
  evidence blobs are deliberately not ingested: they are structured effect
  dumps with no prose to retrieve.

Every row carries: source path, scope label, timestamp, timestamp rule, the
git blob SHA at the build commit (content hash), and the build commit itself
(meta table). Query availability follows the bus_unread taxonomy: an absent
or unreadable index is ``None`` (rendered ``(unavailable: …)``), never an
empty list — an empty list is a real zero from a proven-built index.

No embeddings. No automatic prompt injection. FTS5 only.
"""

from __future__ import annotations

import argparse
import json
import re
import sqlite3
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path, PurePosixPath

_REPO_ROOT = Path(__file__).resolve().parent.parent
if str(_REPO_ROOT) not in sys.path:  # ADR-055 self-bootstrap (no PYTHONPATH)
    sys.path.insert(0, str(_REPO_ROOT))


DB_RELATIVE = "coordination/learning/index.sqlite"

_EVENT_NAME_RE = re.compile(
    r"^(?P<ts>\d{4}-\d{2}-\d{2}T\d{2}-\d{2}-\d{2}Z)-"
    r"(?P<sender>[a-z][a-z0-9]*)-to-(?P<recipient>[a-z][a-z0-9]*)-"
    r"(?P<kind>[a-z][a-z0-9-]*)\.md$"
)
_DATE_PREFIX_RE = re.compile(r"(\d{4}-\d{2}-\d{2})")
_ROW_TS_KEYS = ("ts", "when", "timestamp")


class LearningIndexError(Exception):
    """Raised when a build precondition fails (never by query availability)."""


@dataclass(frozen=True)
class IndexRow:
    path: str
    kind: str
    scope: str
    timestamp: str
    timestamp_rule: str
    blob_sha: str
    snippet: str


def _git(root: Path, *args: str) -> subprocess.CompletedProcess[bytes]:
    return subprocess.run(
        ["git", "-C", str(root), *args],
        capture_output=True,
        check=True,
    )


def _require_repository_scope(relative: str) -> str:
    """Refuse any source path that is not a repository-relative committed path.

    This is the I1 ingest boundary: user-scope sources (absolute paths, home
    expansions, parent escapes) must never enter the index.
    """

    if not isinstance(relative, str) or not relative:
        raise LearningIndexError("source path must be a nonempty string")
    if relative.startswith(("/", "~")):
        raise LearningIndexError(
            f"refusing non-repository-scope source path: {relative!r}"
        )
    pure = PurePosixPath(relative)
    if pure.is_absolute() or ".." in pure.parts:
        raise LearningIndexError(
            f"refusing non-repository-scope source path: {relative!r}"
        )
    return relative


def _source_kind(relative: str) -> str | None:
    pure = PurePosixPath(relative)
    if pure.parent.as_posix() == "coordination/mailbox/sent":
        match = _EVENT_NAME_RE.fullmatch(pure.name)
        if match is None:
            return None
        return f"mailbox:{match.group('kind')}"
    if pure.parent.as_posix() == "docs" and pure.name.startswith("HANDOFF-"):
        return "handoff"
    if pure.parent.as_posix() == "docs/superpowers/plans":
        return "plan"
    if pure.parts and pure.parts[0] == "logs" and pure.suffix == ".jsonl":
        return "log"
    return None


def _timestamp_for(relative: str, kind: str, text: str, commit_date: str) -> tuple[str, str]:
    name = PurePosixPath(relative).name
    if kind.startswith("mailbox:"):
        match = _EVENT_NAME_RE.fullmatch(name)
        assert match is not None  # _source_kind proved this shape
        raw = match.group("ts")
        return raw[:11] + raw[11:19].replace("-", ":") + "Z", "filename"
    if kind in ("handoff", "plan"):
        match = _DATE_PREFIX_RE.search(name)
        if match:
            return match.group(1), "filename"
        return commit_date, "commit-date"
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            row = json.loads(line)
        except ValueError:
            break
        if isinstance(row, dict):
            for key in _ROW_TS_KEYS:
                value = row.get(key)
                if isinstance(value, str) and value:
                    return value, "row-field"
        break
    return commit_date, "commit-date"


def _tracked_sources(root: Path, commit: str) -> list[tuple[str, str]]:
    """Return (path, blob_sha) for every committed source at *commit*."""

    out = _git(root, "ls-tree", "-r", commit).stdout.decode("utf-8", "replace")
    sources: list[tuple[str, str]] = []
    for line in out.splitlines():
        try:
            metadata, path = line.split("\t", 1)
            _mode, object_type, sha = metadata.split(" ", 2)
        except ValueError:
            continue
        if object_type != "blob":
            continue
        if _source_kind(path) is not None:
            sources.append((path, sha))
    return sources


def _blob_texts(root: Path, shas: list[str]) -> dict[str, str]:
    if not shas:
        return {}
    payload = "\n".join(shas).encode("ascii") + b"\n"
    proc = subprocess.run(
        ["git", "-C", str(root), "cat-file", "--batch"],
        input=payload,
        capture_output=True,
        check=True,
    )
    texts: dict[str, str] = {}
    view = memoryview(proc.stdout)
    offset = 0
    while offset < len(view):
        header_end = proc.stdout.index(b"\n", offset)
        header = proc.stdout[offset:header_end].decode("ascii", "replace")
        parts = header.split(" ")
        if len(parts) == 3 and parts[1] == "blob":
            size = int(parts[2])
            body = bytes(view[header_end + 1 : header_end + 1 + size])
            texts[parts[0]] = body.decode("utf-8", "replace")
            offset = header_end + 1 + size + 1
        else:
            offset = header_end + 1
    return texts


def build_index(
    root: Path,
    *,
    commit: str = "HEAD",
    db_path: Path | None = None,
    extra_source_paths: tuple[str, ...] = (),
) -> dict[str, object]:
    """Build the index from the committed tree at *commit*.

    ``extra_source_paths`` exist so callers (and the ingest-boundary test) can
    name additional committed paths explicitly; every one passes the same
    repository-scope refusal as the derived set.
    """

    resolved = (
        _git(root, "rev-parse", commit).stdout.decode("ascii").strip()
    )
    commit_date = (
        _git(root, "show", "-s", "--format=%cI", resolved)
        .stdout.decode("ascii")
        .strip()
    )
    for value in extra_source_paths:
        _require_repository_scope(value)
    sources = _tracked_sources(root, resolved)
    for value in extra_source_paths:
        out = _git(root, "ls-tree", resolved, "--", value).stdout.decode(
            "utf-8", "replace"
        )
        try:
            metadata, path = out.rstrip("\n").split("\t", 1)
            _mode, object_type, sha = metadata.split(" ", 2)
        except ValueError as exc:
            raise LearningIndexError(
                f"extra source path is not committed at {resolved}: {value!r}"
            ) from exc
        if object_type == "blob":
            sources.append((path, sha))
    for path, _sha in sources:
        _require_repository_scope(path)

    texts = _blob_texts(root, [sha for _path, sha in sources])
    target = db_path if db_path is not None else root / DB_RELATIVE
    target.parent.mkdir(parents=True, exist_ok=True)
    if target.exists():
        target.unlink()
    connection = sqlite3.connect(target)
    try:
        connection.execute(
            "CREATE VIRTUAL TABLE rows USING fts5("
            "text, path UNINDEXED, kind UNINDEXED, scope UNINDEXED, "
            "ts UNINDEXED, ts_rule UNINDEXED, blob_sha UNINDEXED)"
        )
        connection.execute("CREATE TABLE meta (key TEXT PRIMARY KEY, value TEXT)")
        skipped: list[str] = []
        for path, sha in sources:
            kind = _source_kind(path)
            if kind is None:
                kind = "extra"
            text = texts.get(sha)
            if text is None:
                skipped.append(f"{path} (unavailable: blob unreadable)")
                continue
            timestamp, rule = _timestamp_for(path, kind, text, commit_date)
            connection.execute(
                "INSERT INTO rows (text, path, kind, scope, ts, ts_rule, blob_sha)"
                " VALUES (?, ?, ?, ?, ?, ?, ?)",
                (text, path, kind, "repository", timestamp, rule, sha),
            )
        connection.execute(
            "INSERT INTO meta VALUES ('built_at_commit', ?)", (resolved,)
        )
        connection.execute(
            "INSERT INTO meta VALUES ('built_at_commit_date', ?)", (commit_date,)
        )
        connection.commit()
    finally:
        connection.close()
    return {
        "built_at_commit": resolved,
        "rows": len(sources) - len(skipped),
        "skipped": tuple(skipped),
        "db_path": str(target),
    }


def built_at_commit(root: Path, *, db_path: Path | None = None) -> str | None:
    """Return the build commit, or ``None`` when the index is unavailable."""

    target = db_path if db_path is not None else root / DB_RELATIVE
    if not target.exists():
        return None
    try:
        connection = sqlite3.connect(f"file:{target}?mode=ro", uri=True)
        try:
            row = connection.execute(
                "SELECT value FROM meta WHERE key = 'built_at_commit'"
            ).fetchone()
        finally:
            connection.close()
    except sqlite3.Error:
        return None
    return row[0] if row else None


def query_index(
    root: Path,
    terms: str,
    *,
    limit: int = 20,
    db_path: Path | None = None,
) -> list[IndexRow] | None:
    """Query the index. ``None`` means unavailable — never conflate with []."""

    target = db_path if db_path is not None else root / DB_RELATIVE
    if not target.exists():
        return None
    try:
        connection = sqlite3.connect(f"file:{target}?mode=ro", uri=True)
        try:
            meta = connection.execute(
                "SELECT value FROM meta WHERE key = 'built_at_commit'"
            ).fetchone()
            if meta is None:
                return None
            cursor = connection.execute(
                "SELECT path, kind, scope, ts, ts_rule, blob_sha,"
                " snippet(rows, 0, '[', ']', ' … ', 12)"
                " FROM rows WHERE rows MATCH ? ORDER BY rank LIMIT ?",
                (terms, limit),
            )
            results = [
                IndexRow(
                    path=row[0],
                    kind=row[1],
                    scope=row[2],
                    timestamp=row[3],
                    timestamp_rule=row[4],
                    blob_sha=row[5],
                    snippet=row[6],
                )
                for row in cursor.fetchall()
            ]
        finally:
            connection.close()
    except sqlite3.Error:
        return None
    return results


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--repo-root", type=Path, default=_REPO_ROOT)
    commands = parser.add_subparsers(dest="command", required=True)
    build = commands.add_parser("build", help="rebuild the index from HEAD")
    build.add_argument("--commit", default="HEAD")
    query = commands.add_parser("query", help="FTS query over the index")
    query.add_argument("terms")
    query.add_argument("--limit", type=int, default=20)
    arguments = parser.parse_args(argv)

    if arguments.command == "build":
        report = build_index(arguments.repo_root, commit=arguments.commit)
        print(
            f"built {report['rows']} rows at {report['built_at_commit'][:12]}"
            f" -> {report['db_path']}"
        )
        for line in report["skipped"]:
            print(f"  skipped {line}")
        return 0

    rows = query_index(arguments.repo_root, arguments.terms, limit=arguments.limit)
    if rows is None:
        print("(unavailable: index not built — run learning_index.py build)")
        return 1
    commit = built_at_commit(arguments.repo_root)
    print(f"{len(rows)} row(s) — index built at {commit[:12] if commit else '?'}")
    for row in rows:
        print(
            f"- {row.path} [{row.kind} · {row.scope} · {row.timestamp}"
            f" ({row.timestamp_rule}) · {row.blob_sha[:12]}]\n  {row.snippet}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
