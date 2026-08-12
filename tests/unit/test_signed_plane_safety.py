"""Focused safety regressions for signed-bus activation CLIs and cutover."""
from __future__ import annotations

import os
import subprocess
from pathlib import Path
from types import SimpleNamespace

import pytest

from scripts import consume_bus, run_merge_gate
from threeway import cursor_backfill, cutover, gitcas
from threeway.refstore import EVENTS_REF


def _git(repo: Path, *args: str) -> str:
    env = {key: value for key, value in os.environ.items() if key != "GIT_INDEX_FILE"}
    env["GIT_CONFIG_GLOBAL"] = os.devnull
    env["GIT_CONFIG_SYSTEM"] = os.devnull
    return subprocess.run(
        ["git", "-C", str(repo), *args],
        check=True,
        capture_output=True,
        text=True,
        env=env,
    ).stdout.strip()


@pytest.mark.parametrize("seat", ("coordinator", "coordinator2"))
def test_consume_bus_rejects_cursorless_coordinator_before_store_access(
    monkeypatch: pytest.MonkeyPatch, seat: str
) -> None:
    class ForbiddenStore:
        def __init__(self, *_args, **_kwargs):
            raise AssertionError("cursorless coordinator reached the cursor store")

    monkeypatch.setattr(consume_bus, "RefEventStore", ForbiddenStore)

    with pytest.raises(SystemExit) as exc:
        consume_bus.main([seat, "--no-advance"])

    assert exc.value.code == 2


@pytest.mark.parametrize("kinds", ("candidate", ""))
def test_consume_bus_filtered_view_refuses_advancement_before_store_access(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    kinds: str,
) -> None:
    class ForbiddenStore:
        def __init__(self, *_args, **_kwargs):
            raise AssertionError("unsafe filtered consume reached the cursor store")

    monkeypatch.setattr(consume_bus, "RefEventStore", ForbiddenStore)

    assert consume_bus.main(["director", "--kinds", kinds]) == 2
    assert "--kinds requires --no-advance" in capsys.readouterr().err


def test_consume_bus_id_filter_refuses_advancement_before_store_access(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    class ForbiddenStore:
        def __init__(self, *_args, **_kwargs):
            raise AssertionError("filtered bus view reached store before refusal")

    monkeypatch.setattr(consume_bus, "RefEventStore", ForbiddenStore)

    assert consume_bus.main(["director", "--bus-id", "prod"]) == 2
    assert "--bus-id requires --no-advance" in capsys.readouterr().err


def test_consume_bus_filtered_no_advance_reads_without_writing_cursor(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    calls: list[str] = []

    class ReadOnlyStore:
        def __init__(self, *_args, **_kwargs):
            pass

        def cursor_seq(self, seat: str) -> int:
            calls.append(f"cursor:{seat}")
            return 0

        def iter_events(self):
            calls.append("events")
            return iter(())

        def advance_cursor(self, *_args, **_kwargs):
            raise AssertionError("--no-advance wrote a cursor")

    monkeypatch.setattr(consume_bus, "RefEventStore", ReadOnlyStore)

    assert consume_bus.main(["director", "--kinds", "candidate", "--no-advance"]) == 0
    assert calls == ["cursor:director", "events"]


def test_cutover_backfill_failure_restores_exact_ref_snapshot(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    _git(repo, "init", "-b", "main")
    _git(repo, "config", "user.email", "test@example.com")
    _git(repo, "config", "user.name", "Test")
    (repo / "coordination" / "mailbox" / "sent").mkdir(parents=True)
    (repo / "coordination" / "mailbox" / "seen").mkdir()
    tracked = repo / "tracked.txt"
    tracked.write_text("before\n", encoding="utf-8")
    _git(repo, "add", "tracked.txt")
    _git(repo, "commit", "-m", "before")
    before_commit = _git(repo, "rev-parse", "HEAD")
    tracked.write_text("after\n", encoding="utf-8")
    _git(repo, "commit", "-am", "after")
    after_commit = _git(repo, "rev-parse", "HEAD")

    _git(repo, "update-ref", EVENTS_REF, before_commit)
    prior_cursor = gitcas.write_blob(repo, b"7\n")
    _git(repo, "update-ref", cutover._cursor_ref("director"), prior_cursor)
    before_refs = cutover._snapshot_refs(repo)
    assert before_refs[EVENTS_REF] == before_commit
    assert before_refs[cutover._cursor_ref("director2")] is None

    changed_cursor = gitcas.write_blob(repo, b"1\n")

    class MutatingStore:
        def __init__(self, repo_path: Path):
            self.repo = repo_path

        def append(self, _event, _key, _on_commit=None) -> None:
            _git(self.repo, "update-ref", EVENTS_REF, after_commit)
            if _on_commit is not None:
                _on_commit(before_commit, after_commit)

        def advance_cursor(self, seat: str, _seq: int, _on_commit=None) -> bool:
            ref = cutover._cursor_ref(seat)
            previous = gitcas.rev_parse_any(self.repo, ref)
            _git(self.repo, "update-ref", cutover._cursor_ref(seat), changed_cursor)
            if _on_commit is not None:
                _on_commit(previous, changed_cursor)
            return True

        def cursor_seq(self, _seat: str) -> int:
            return 1

    carrier = SimpleNamespace(payload={"source_filename": "2026-01-01T00-00-00Z-a-to-b-status.md"})
    monkeypatch.setattr(cutover, "RefEventStore", MutatingStore)
    monkeypatch.setattr(cutover.legacy_projector, "project", lambda _sent: [carrier])
    monkeypatch.setattr(cutover.cursor_backfill, "total_order", lambda _names: [])
    monkeypatch.setattr(cutover, "_read_iso_cursors", lambda _root: {})
    monkeypatch.setattr(
        cutover.cursor_backfill,
        "iso_to_seq_map",
        lambda _names, _cursors: {seat: 1 for seat in cutover._SEATS},
    )

    def fail_backfill(_root: Path) -> None:
        raise RuntimeError("backfill exploded")

    monkeypatch.setattr(cutover.cursor_backfill, "backfill", fail_backfill)

    with pytest.raises(RuntimeError, match="backfill exploded"):
        cutover.run_cutover(repo, repo, object(), force=True)

    assert cutover._snapshot_refs(repo) == before_refs


def test_cursor_backfill_failure_restores_seen_bytes_and_manifest(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    mailbox = tmp_path / "coordination" / "mailbox"
    (mailbox / "sent").mkdir(parents=True)
    seen = mailbox / "seen"
    seen.mkdir()
    for index, seat in enumerate(cursor_backfill.SEATS):
        (seen / f"{seat}.txt").write_text(
            f"2026-01-01T00:00:0{index}Z\n", encoding="utf-8"
        )
    before = {path.name: path.read_bytes() for path in seen.glob("*.txt")}
    manifest = mailbox / ".migration" / "cursor-backfill.json"
    real_write_cursor = cursor_backfill._write_cursor_text

    def fail_after_one_cursor(path: Path, text: str) -> None:
        if path.name == "director2.txt":
            raise OSError("forced cursor write failure")
        real_write_cursor(path, text)

    monkeypatch.setattr(cursor_backfill, "_write_cursor_text", fail_after_one_cursor)

    with pytest.raises(OSError, match="forced cursor write failure"):
        cursor_backfill.backfill(tmp_path)

    assert {path.name: path.read_bytes() for path in seen.glob("*.txt")} == before
    assert not manifest.exists()


def test_cursor_backfill_interrupt_restores_seen_bytes_and_manifest(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    mailbox = tmp_path / "coordination" / "mailbox"
    (mailbox / "sent").mkdir(parents=True)
    seen = mailbox / "seen"
    seen.mkdir()
    for index, seat in enumerate(cursor_backfill.SEATS):
        (seen / f"{seat}.txt").write_text(
            f"2026-01-01T00:00:0{index}Z\n", encoding="utf-8"
        )
    before = {path.name: path.read_bytes() for path in seen.glob("*.txt")}
    manifest = mailbox / ".migration" / "cursor-backfill.json"
    real_write_cursor = cursor_backfill._write_cursor_text

    def interrupt_after_one_cursor(path: Path, text: str) -> None:
        if path.name == "director2.txt":
            raise KeyboardInterrupt
        real_write_cursor(path, text)

    monkeypatch.setattr(cursor_backfill, "_write_cursor_text", interrupt_after_one_cursor)

    with pytest.raises(KeyboardInterrupt):
        cursor_backfill.backfill(tmp_path)

    assert {path.name: path.read_bytes() for path in seen.glob("*.txt")} == before
    assert not manifest.exists()


@pytest.mark.parametrize("symlink_surface", ("cursor", "seen", "migration"))
def test_cursor_backfill_rejects_symlinked_mailbox_write_surfaces(
    tmp_path: Path, symlink_surface: str
) -> None:
    mailbox = tmp_path / "coordination" / "mailbox"
    (mailbox / "sent").mkdir(parents=True)
    outside = tmp_path / "outside"
    outside.mkdir()
    outside_cursor = outside / "director.txt"
    outside_cursor.write_text("2026-01-01T00:00:00Z\n", encoding="utf-8")

    if symlink_surface == "seen":
        (mailbox / "seen").symlink_to(outside, target_is_directory=True)
    else:
        seen = mailbox / "seen"
        seen.mkdir()
        for index, seat in enumerate(cursor_backfill.SEATS):
            target = seen / f"{seat}.txt"
            if symlink_surface == "cursor" and seat == "director":
                target.symlink_to(outside_cursor)
            else:
                target.write_text(
                    f"2026-01-01T00:00:0{index}Z\n", encoding="utf-8"
                )
        if symlink_surface == "migration":
            (mailbox / ".migration").symlink_to(outside, target_is_directory=True)

    before = outside_cursor.read_bytes()
    with pytest.raises(cursor_backfill.CursorBackfillManifestError):
        cursor_backfill.backfill(tmp_path)

    assert outside_cursor.read_bytes() == before
    assert not (outside / "cursor-backfill.json").exists()


def test_teardown_cas_refuses_to_clobber_concurrent_ref_update(tmp_path: Path) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    _git(repo, "init", "-b", "main")
    ref = "refs/threeway/cursors/director"
    old_oid = gitcas.write_blob(repo, b"old\n")
    written_oid = gitcas.write_blob(repo, b"cutover\n")
    concurrent_oid = gitcas.write_blob(repo, b"concurrent\n")
    _git(repo, "update-ref", ref, old_oid)
    _git(repo, "update-ref", ref, written_oid, old_oid)
    _git(repo, "update-ref", ref, concurrent_oid, written_oid)
    original = RuntimeError("cutover failed")

    with pytest.raises(cutover.TeardownError) as exc:
        cutover._teardown(
            repo,
            {ref: cutover.RefMutation(old_oid, written_oid)},
            original,
        )

    assert exc.value.__cause__ is original
    assert gitcas.rev_parse_any(repo, ref) == concurrent_oid


def test_teardown_restores_the_actual_predecessor_and_preserves_concurrent_ancestor(
    tmp_path: Path,
) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    _git(repo, "init", "-b", "main")
    ref = "refs/threeway/cursors/director"
    snapshot_oid = gitcas.write_blob(repo, b"snapshot\n")
    concurrent_oid = gitcas.write_blob(repo, b"concurrent\n")
    cutover_oid = gitcas.write_blob(repo, b"cutover\n")
    _git(repo, "update-ref", ref, snapshot_oid)
    _git(repo, "update-ref", ref, concurrent_oid, snapshot_oid)
    _git(repo, "update-ref", ref, cutover_oid, concurrent_oid)
    written: dict[str, cutover.RefMutation] = {}
    cutover._record_write(written, ref, concurrent_oid, cutover_oid)

    cutover._teardown(repo, written, RuntimeError("cutover failed"))

    assert gitcas.rev_parse_any(repo, ref) == concurrent_oid


def test_merge_gate_run_once_iteration_exception_returns_nonzero(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    monkeypatch.setattr(run_merge_gate, "_STOP", False)
    monkeypatch.setattr(run_merge_gate, "load_private", lambda _seat: object())
    monkeypatch.setattr(run_merge_gate.signal, "signal", lambda *_args: None)
    monkeypatch.setattr(run_merge_gate, "RefEventStore", lambda *_args, **_kwargs: object())

    def fail_poll(*_args, **_kwargs):
        raise RuntimeError("poll exploded")

    monkeypatch.setattr(run_merge_gate, "poll_once", fail_poll)

    assert run_merge_gate.main(["--run-once"]) == 1
    assert "merge-gate iteration error: poll exploded" in capsys.readouterr().err
