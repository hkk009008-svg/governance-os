"""Unit tests for scripts/status.py helpers and bounded Git collection.

Focus: count_unread — the never-crashing unread-count helper that the mailbox
collector (and the `mailbox-unread` subcommand) drives — plus bounded real-Git
coverage for `collect_git` repository and index isolation.

Behavior pinned (read from scripts/status.py, the source of truth):
  * count_unread(cursor_ts, event_filenames, seat) returns the number of events
    addressed to *seat* whose embedded timestamp is STRICTLY GREATER THAN the
    (ISO) cursor.
  * Filenames have the shape "<ts>-<from>-to-<to>-<kind>.md" where ts is
    "YYYY-MM-DDTHH-MM-SSZ". Cursor timestamps may use colons (T20:38:34Z);
    both sides are normalized to dashes before comparison.
  * A scalar / non-ISO ("migrated") cursor returns 0 — the real unread for a
    migrated seat is computed on the ref-bus, not this legacy filename path.
  * Broadcast events (to == "all") count for every seat.
  * Malformed filenames are silently skipped; an empty list returns 0.
  * Git collection runs in the requested repository and ignores an ambient
    seat-specific index.
"""

import os
import subprocess

import status


def _git(repo, *args, env=None) -> str:
    result = subprocess.run(
        ["git", *args],
        cwd=repo,
        env=env,
        capture_output=True,
        text=True,
        check=True,
    )
    return result.stdout.strip()


def _init_clean_repo(tmp_path):
    repo = tmp_path / "repo"
    repo.mkdir()
    _git(repo, "init", "-b", "main")
    _git(repo, "config", "user.email", "status-test@example.com")
    _git(repo, "config", "user.name", "Status Test")
    (repo / "tracked.txt").write_text("tracked\n", encoding="utf-8")
    _git(repo, "add", "tracked.txt")
    _git(repo, "commit", "-m", "test: initial state")
    return repo


def test_collect_git_runs_in_requested_repo(tmp_path, monkeypatch):
    repo = _init_clean_repo(tmp_path)
    expected_sha = _git(repo, "rev-parse", "--short", "HEAD")
    outside = tmp_path / "outside"
    outside.mkdir()
    monkeypatch.chdir(outside)

    result = status.collect_git(repo)

    assert result["git_sha"] == expected_sha
    assert result["git_branch"] == "main"


def test_collect_git_ignores_ambient_index(tmp_path, monkeypatch):
    repo = _init_clean_repo(tmp_path)
    alternate_index = tmp_path / "seat.index"
    alternate_env = os.environ.copy()
    alternate_env["GIT_INDEX_FILE"] = str(alternate_index)
    _git(repo, "read-tree", "--empty", env=alternate_env)
    monkeypatch.chdir(repo)
    monkeypatch.setenv("GIT_INDEX_FILE", str(alternate_index))

    result = status.collect_git(repo)

    assert result["git_dirty"] == 0


def _fname(ts: str, frm: str, to: str, kind: str = "verification-report") -> str:
    """Build a well-formed mailbox event filename.

    ts is the dash-form timestamp embedded in real sent/*.md names, e.g.
    "2026-05-28T20-38-34Z".
    """
    return f"{ts}-{frm}-to-{to}-{kind}.md"


def test_empty_event_list_returns_zero():
    assert status.count_unread("2026-05-28T20:38:34Z", [], "director") == 0


def test_iso_cursor_counts_only_strictly_newer_events_for_seat():
    cursor = "2026-05-28T20:38:34Z"
    events = [
        _fname("2026-05-28T20-38-33Z", "operator", "director"),  # older -> no
        _fname("2026-05-28T20-38-34Z", "operator", "director"),  # equal -> no (strict)
        _fname("2026-05-28T20-38-35Z", "operator", "director"),  # newer -> yes
        _fname("2026-05-29T09-00-00Z", "operator", "director"),  # newer -> yes
    ]
    assert status.count_unread(cursor, events, "director") == 2


def test_events_addressed_to_other_seat_are_not_counted():
    cursor = "2026-05-28T00:00:00Z"
    events = [
        _fname("2026-05-29T09-00-00Z", "director", "operator"),   # to operator
        _fname("2026-05-29T10-00-00Z", "director", "operator2"),  # to operator2
        _fname("2026-05-29T11-00-00Z", "director", "director"),   # to director
    ]
    assert status.count_unread(cursor, events, "director") == 1
    assert status.count_unread(cursor, events, "operator") == 1
    assert status.count_unread(cursor, events, "operator2") == 1
    assert status.count_unread(cursor, events, "coordinator") == 0


def test_broadcast_events_count_for_every_seat():
    cursor = "2026-05-28T00:00:00Z"
    events = [
        _fname("2026-05-29T09-00-00Z", "director", "all", "wave-gate"),
        _fname("2026-05-29T10-00-00Z", "operator", "all", "wave-gate"),
    ]
    for seat in ("director", "director2", "operator", "operator2", "coordinator"):
        assert status.count_unread(cursor, events, seat) == 2


def test_broadcast_plus_directed_mix():
    cursor = "2026-05-28T00:00:00Z"
    events = [
        _fname("2026-05-29T09-00-00Z", "director", "all"),       # broadcast -> all
        _fname("2026-05-29T10-00-00Z", "director", "operator"),  # only operator
        _fname("2026-05-29T11-00-00Z", "operator", "director"),  # only director
    ]
    # director sees the broadcast + the one addressed to it = 2
    assert status.count_unread(cursor, events, "director") == 2
    # operator sees the broadcast + the one addressed to it = 2
    assert status.count_unread(cursor, events, "operator") == 2
    # operator2 only sees the broadcast = 1
    assert status.count_unread(cursor, events, "operator2") == 1


def test_scalar_migrated_cursor_returns_zero():
    # Non-ISO scalar 'seq' cursor (post Slice-2.5 backfill): the legacy
    # filename path must NOT count anything — unread lives on the ref-bus.
    events = [
        _fname("2026-05-29T09-00-00Z", "operator", "director"),
        _fname("2026-05-29T10-00-00Z", "operator", "all"),
    ]
    assert status.count_unread("42", events, "director") == 0
    assert status.count_unread("migrated", events, "director") == 0


def test_colon_form_cursor_is_normalized_to_dashes():
    # The cursor uses colons; filenames use dashes. They must compare equal
    # at the same wall-clock instant (so an equal-instant event is NOT unread).
    events = [_fname("2026-05-28T20-38-34Z", "operator", "director")]
    assert status.count_unread("2026-05-28T20:38:34Z", events, "director") == 0
    # And a one-second-newer event IS unread under the colon cursor.
    newer = [_fname("2026-05-28T20-38-35Z", "operator", "director")]
    assert status.count_unread("2026-05-28T20:38:34Z", newer, "director") == 1


def test_malformed_filenames_are_silently_skipped():
    cursor = "2026-05-28T00:00:00Z"
    events = [
        "not-an-event.md",                                   # no ts/to structure
        "2026-05-29T09-00-00Z-director-operator.md",         # missing '-to-'
        "2026-05-29T09-00-00Z-director-to-director.txt",     # wrong extension
        _fname("2026-05-29T09-00-00Z", "operator", "director"),  # the one valid one
    ]
    assert status.count_unread(cursor, events, "director") == 1


def test_does_not_crash_on_weird_inputs():
    # The helper is designed to NEVER crash; non-ISO cursors short-circuit to 0
    # before any filename is inspected, so even garbage filenames are inert.
    assert status.count_unread("", ["whatever.md"], "director") == 0
    assert status.count_unread("not-a-timestamp", [], "director") == 0
