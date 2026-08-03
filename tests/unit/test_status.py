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
  * A scalar / non-ISO cursor raises visibly. Production unread resolution uses
    bus_unread.resolve_unread and cannot silently degrade to zero.
  * Broadcast events (to == "all") count for every seat.
  * Malformed filenames are silently skipped; an empty list returns 0.
  * Git collection runs in the requested repository and ignores an ambient
    seat-specific index.
"""

import json
import os
import subprocess
from pathlib import Path

import pytest

import check_coordination as cc
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


def test_broadcast_events_count_for_every_seat():
    cursor = "2026-05-28T00:00:00Z"
    events = [
        _fname("2026-05-29T09-00-00Z", "director", "all", "wave-gate"),
        _fname("2026-05-29T10-00-00Z", "operator", "all", "wave-gate"),
    ]
    for seat in ("director", "director2", "operator", "operator2"):
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


def test_scalar_migrated_cursor_fails_visibly():
    # Non-ISO scalar cursors must never recreate the silent-zero footgun.
    events = [
        _fname("2026-05-29T09-00-00Z", "operator", "director"),
        _fname("2026-05-29T10-00-00Z", "operator", "all"),
    ]
    with pytest.raises(ValueError, match="ISO mailbox cursor"):
        status.count_unread("42", events, "director")
    with pytest.raises(ValueError, match="ISO mailbox cursor"):
        status.count_unread("migrated", events, "director")


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


def test_weird_cursor_inputs_fail_visibly():
    with pytest.raises(ValueError, match="ISO mailbox cursor"):
        status.count_unread("", ["whatever.md"], "director")
    with pytest.raises(ValueError, match="ISO mailbox cursor"):
        status.count_unread("not-a-timestamp", [], "director")


def test_calendar_invalid_iso_cursor_fails_visibly():
    with pytest.raises(ValueError, match="ISO mailbox cursor"):
        status.count_unread("2026-99-99T99:99:99Z", [], "director")


def _seed_mailbox(root: Path, cursor: str = "0") -> None:
    sent = root / "coordination/mailbox/sent"
    seen = root / "coordination/mailbox/seen"
    sent.mkdir(parents=True)
    seen.mkdir()
    for seat in status._MAILBOX_SEATS:
        (seen / f"{seat}.txt").write_text(cursor + "\n", encoding="ascii")


def test_collect_mailbox_scalar_without_live_bus_uses_mailbox_projection(
    tmp_path: Path,
) -> None:
    _seed_mailbox(tmp_path)
    sent = tmp_path / "coordination/mailbox/sent"
    (sent / _fname("2026-07-17T01-00-00Z", "director", "operator")).write_text(
        "one\n", encoding="utf-8"
    )
    (sent / _fname("2026-07-17T01-00-01Z", "director", "all")).write_text(
        "two\n", encoding="utf-8"
    )

    data = status.collect_mailbox(tmp_path)

    assert data["mailbox_operator_unread"] == 2
    assert data["mailbox_operator_source"] == "mailbox-fallback"
    assert data["mailbox_operator_transport"] == "absent"
    assert data["mailbox_coordinator_cursor"] == "(cursorless)"
    assert data["mailbox_coordinator_source"] == "broadcast-read-only"


def test_collect_mailbox_surfaces_scalar_beyond_mailbox_corpus(
    tmp_path: Path,
) -> None:
    _seed_mailbox(tmp_path, cursor="9")

    data = status.collect_mailbox(tmp_path)

    assert data["mailbox_operator_unread"].startswith("(unavailable:")
    assert data["mailbox_operator_transport"] == "incoherent"


def test_collect_mailbox_surfaces_calendar_invalid_cursor(
    tmp_path: Path,
) -> None:
    _seed_mailbox(tmp_path, cursor="2026-99-99T99:99:99Z")

    data = status.collect_mailbox(tmp_path)

    assert data["mailbox_operator_unread"].startswith("(unavailable:")
    assert data["mailbox_operator_transport"] == "incoherent"


def _orientation_mailbox() -> dict[str, object]:
    data: dict[str, object] = {}
    for seat in status._CURSOR_SEATS:
        data.update({
            f"mailbox_{seat}_cursor": "0",
            f"mailbox_{seat}_unread": 0,
            f"mailbox_{seat}_source": "mailbox-fallback",
            f"mailbox_{seat}_transport": "absent",
            f"mailbox_{seat}_detail": "test fixture",
        })
    return data


def test_repository_global_failed_review_forces_seat_snapshot_gate_fail(
    tmp_path: Path, monkeypatch,
) -> None:
    failed = cc.FailedVerifyRequest(
        request_path="coordination/mailbox/sent/request.md",
        request_commit="a" * 40,
        report_path="coordination/mailbox/sent/report.md",
        report_commit="b" * 40,
        assigned_operator="operator2",
    )
    review_state = cc.VerifyReviewState(pending=(), failed=(failed,))
    monkeypatch.setattr(
        status,
        "collect_git",
        lambda _root: {"git_sha": "abc1234", "git_branch": "test", "git_dirty": 0},
    )
    monkeypatch.setattr(status, "collect_mailbox", lambda _root: _orientation_mailbox())
    monkeypatch.setattr(
        cc, "committed_mailbox_projection", lambda _root: (None, "fixture")
    )
    monkeypatch.setattr(
        cc,
        "inspect_verify_review_state",
        lambda _root, **_kwargs: review_state,
    )
    monkeypatch.setattr(
        cc,
        "run",
        lambda *_args, **_kwargs: [
            cc.CoordIssue("report.md", "failed_verify_review", "ADVISORY", "failed")
        ],
    )

    snapshot = status.collect_orientation_snapshot(tmp_path, "operator")

    assert snapshot["gate"] == {
        "status": "FAIL",
        "fatal": 0,
        "advisory": 1,
        "failed_review": 1,
    }
    assert snapshot["failed_review"]["report_commit"] == "b" * 40
    assert snapshot["failed_review"]["assigned_operator"] == "operator2"


def test_structural_fatal_outranks_failed_review_without_dropping_failure_data(
    tmp_path: Path, monkeypatch,
) -> None:
    failed = cc.FailedVerifyRequest(
        request_path="coordination/mailbox/sent/request.md",
        request_commit="a" * 40,
        report_path="coordination/mailbox/sent/report.md",
        report_commit="b" * 40,
        assigned_operator="operator",
    )
    review_state = cc.VerifyReviewState(pending=(), failed=(failed,))
    monkeypatch.setattr(
        status,
        "collect_git",
        lambda _root: {"git_sha": "abc1234", "git_branch": "test", "git_dirty": 0},
    )
    monkeypatch.setattr(status, "collect_mailbox", lambda _root: _orientation_mailbox())
    monkeypatch.setattr(
        cc, "committed_mailbox_projection", lambda _root: (None, "fixture")
    )
    monkeypatch.setattr(
        cc,
        "inspect_verify_review_state",
        lambda _root, **_kwargs: review_state,
    )
    monkeypatch.setattr(
        cc,
        "run",
        lambda *_args, **_kwargs: [
            cc.CoordIssue("kinds.txt", "unknown_kind", "FATAL", "structural break"),
            cc.CoordIssue("report.md", "failed_verify_review", "ADVISORY", "failed"),
        ],
    )

    snapshot = status.collect_orientation_snapshot(tmp_path, "operator")

    assert snapshot["blocker"] == "unknown_kind: structural break"
    assert snapshot["next_action"] == "repair the blocker before implementation or review"
    assert snapshot["failed_review"]["report_commit"] == "b" * 40
    assert snapshot["gate"] == {
        "status": "FAIL",
        "fatal": 1,
        "advisory": 1,
        "failed_review": 1,
    }


def test_compact_orientation_render_is_bounded_and_names_authority_source() -> None:
    snapshot = {
        "generated_at": "2026-07-25T00:00:00Z",
        "git": {"sha": "abc1234", "branch": "main", "dirty": 2},
        "unread": {
            "operator": {
                "cursor": "0",
                "count": 3,
                "source": "mailbox-fallback",
                "transport": "absent",
            }
        },
        "current_request": {
            "path": "coordination/mailbox/sent/request.md",
            "commit": "a" * 40,
            "assigned_operator": "operator",
            "valid": True,
        },
        "gate": {"status": "PASS", "fatal": 0, "advisory": 1},
        "blocker": None,
        "next_action": "operator reviews the exact committed request",
    }

    rendered = status.render_orientation_snapshot(snapshot)

    assert len(rendered.splitlines()) <= 20
    assert "mailbox-fallback" in rendered
    assert "operator reviews the exact committed request" in rendered


def test_snapshot_json_cli_emits_machine_readable_object(
    monkeypatch, capsys
) -> None:
    snapshot = {
        "generated_at": "2026-07-25T00:00:00Z",
        "git": {"sha": "abc1234", "branch": "main", "dirty": 0},
        "unread": {},
        "current_request": None,
        "gate": {"status": "PASS", "fatal": 0, "advisory": 0},
        "blocker": None,
        "next_action": "continue routed work",
    }
    monkeypatch.setattr(
        status, "collect_orientation_snapshot", lambda _root, seat=None: snapshot
    )

    assert status.main(["snapshot", "operator", "--json"]) == 0
    assert json.loads(capsys.readouterr().out)["git"]["sha"] == "abc1234"
