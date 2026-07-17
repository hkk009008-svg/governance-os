"""Focused tests for the compact-kernel activation selector and writer fence."""

from __future__ import annotations

import importlib
import importlib.util
import json
import os
import stat
import subprocess
import sys
import threading
import time
from pathlib import Path

import pytest

import kernel_activation


def _git(root: Path, *args: str, input_bytes: bytes | None = None) -> str:
    result = subprocess.run(
        ["/usr/bin/git", "-C", str(root), *args],
        input=input_bytes,
        capture_output=True,
        check=True,
    )
    return result.stdout.decode("ascii").strip()


def _write_mirror(root: Path, epoch: int, writer: str) -> None:
    (root / "governance.toml").write_text(
        "[protocol.kernel]\n"
        f"epoch = {epoch}\n"
        f'writer = "{writer}"\n',
        encoding="utf-8",
    )


def _repo(tmp_path: Path, *, epoch: int = 0, writer: str = "v1") -> Path:
    root = tmp_path / "repo"
    root.mkdir()
    _git(root, "init", "-q")
    _write_mirror(root, epoch, writer)
    _git(root, "add", "governance.toml")
    _git(
        root,
        "-c",
        "user.name=Fixture",
        "-c",
        "user.email=fixture@example.invalid",
        "commit",
        "-q",
        "-m",
        "chore: seed selector fixture",
    )
    return root


def _canonical(epoch: int, writer: str, **extra: object) -> bytes:
    value: dict[str, object] = {
        "schema": "protocol-kernel-selection/v1",
        "epoch": epoch,
        "writer": writer,
        **extra,
    }
    return (json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n").encode()


def _select(root: Path, raw: bytes) -> str:
    oid = _git(root, "hash-object", "-w", "--stdin", input_bytes=raw)
    _git(root, "update-ref", "refs/protocol/kernel-activation", oid)
    return oid


def test_absent_ref_selects_epoch_zero_v1_only_from_exact_mirror(tmp_path: Path) -> None:
    root = _repo(tmp_path)

    assert kernel_activation.read_selection(root) == kernel_activation.KernelSelection(
        epoch=0,
        writer="v1",
        selector_oid=None,
    )


def test_present_canonical_blob_selects_exact_mirrored_value(tmp_path: Path) -> None:
    root = _repo(tmp_path, epoch=3, writer="compact")
    oid = _select(root, _canonical(3, "compact"))

    assert kernel_activation.read_selection(root) == kernel_activation.KernelSelection(
        epoch=3,
        writer="compact",
        selector_oid=oid,
    )


@pytest.mark.parametrize(
    "raw",
    [
        _canonical(1, "v1", extra=True),
        _canonical(True, "v1"),
        _canonical(0, "v1"),
        _canonical(1, "future"),
        b'{"epoch":1,"schema":"protocol-kernel-selection/v1","writer":"v1"}',
        b'{"schema":"protocol-kernel-selection/v1","epoch":1,"writer":"v1"}\n',
        b"not-json\n",
    ],
)
def test_present_selector_rejects_noncanonical_or_invalid_blob(
    tmp_path: Path, raw: bytes
) -> None:
    root = _repo(tmp_path, epoch=1, writer="v1")
    _select(root, raw)

    with pytest.raises(kernel_activation.KernelSelectionError):
        kernel_activation.read_selection(root)


def test_selector_rejects_mirror_mismatch(tmp_path: Path) -> None:
    root = _repo(tmp_path, epoch=2, writer="v1")
    _select(root, _canonical(2, "compact"))

    with pytest.raises(kernel_activation.KernelSelectionError, match="mirror"):
        kernel_activation.read_selection(root)


def test_selector_ignores_inherited_git_selectors(tmp_path: Path, monkeypatch) -> None:
    root = _repo(tmp_path)
    monkeypatch.setenv("GIT_DIR", str(tmp_path / "attacker.git"))
    monkeypatch.setenv("GIT_INDEX_FILE", str(tmp_path / "attacker.index"))
    monkeypatch.setenv("GIT_REPLACE_REF_BASE", "refs/attacker/replace/")

    assert kernel_activation.read_selection(root).writer == "v1"


def test_writer_fence_is_shared_by_linked_worktrees_and_mode_0600(
    tmp_path: Path,
) -> None:
    root = _repo(tmp_path)
    linked = tmp_path / "linked"
    _git(root, "worktree", "add", "-q", "-b", "linked", str(linked))
    acquired = threading.Event()

    def contender() -> None:
        with kernel_activation.writer_fence(linked, 0, "v1"):
            acquired.set()

    with kernel_activation.writer_fence(root, 0, "v1"):
        common = Path(_git(root, "rev-parse", "--path-format=absolute", "--git-common-dir"))
        lock = common / "protocol-kernel-writer.lock"
        assert stat.S_IMODE(lock.stat().st_mode) == 0o600
        thread = threading.Thread(target=contender)
        thread.start()
        time.sleep(0.1)
        assert not acquired.is_set()
    thread.join(timeout=2)
    assert acquired.is_set()


def test_writer_fence_rereads_selector_only_after_lock_acquisition(
    tmp_path: Path,
) -> None:
    root = _repo(tmp_path)
    common = Path(_git(root, "rev-parse", "--path-format=absolute", "--git-common-dir"))
    lock_path = common / "protocol-kernel-writer.lock"
    lock_fd = os.open(lock_path, os.O_CREAT | os.O_RDWR, 0o600)
    import fcntl

    fcntl.flock(lock_fd, fcntl.LOCK_EX)
    rejected = threading.Event()

    def contender() -> None:
        try:
            with kernel_activation.writer_fence(root, 0, "v1"):
                pass
        except kernel_activation.KernelSelectionError:
            rejected.set()

    thread = threading.Thread(target=contender)
    thread.start()
    time.sleep(0.1)
    _write_mirror(root, 1, "compact")
    _select(root, _canonical(1, "compact"))
    fcntl.flock(lock_fd, fcntl.LOCK_UN)
    os.close(lock_fd)
    thread.join(timeout=2)

    assert rejected.is_set()


def test_send_event_finalizer_rejects_filename_envelope_identity_mismatch(
    tmp_path: Path,
) -> None:
    root = _repo(tmp_path)
    sent = root / "coordination/mailbox/sent"
    sent.mkdir(parents=True)
    kinds = root / "coordination/mailbox/kinds.txt"
    kinds.write_text("status\n", encoding="utf-8")
    relative = (
        "coordination/mailbox/sent/"
        "2026-07-17T01-02-03Z-director-to-operator-status.md"
    )
    candidate = sent / ".2026-07-17T01-02-03Z-director-to-operator-status.fixture.tmp"
    candidate.write_text(
        "# Operator → Director: spoofed identity\n\n"
        "**When:** 2026-07-17T01:02:03Z · **From:** operator (online)\n\n"
        "body\n\nCursor at send: 0\n",
        encoding="utf-8",
    )
    candidate.chmod(0o600)

    with pytest.raises(kernel_activation.KernelSelectionError, match="envelope"):
        kernel_activation._send_event_finalize(root, candidate, relative)

    assert candidate.exists()
    assert not (root / relative).exists()
    assert _git(root, "diff", "--cached", "--name-only") == ""


@pytest.mark.parametrize(
    ("current", "target"),
    [
        ("not-a-time", None),
        ("2026-07-17T01:00:00Z", "2026-07-17T01:02-03Z"),
    ],
)
def test_consume_finalizer_rejects_malformed_or_mixed_cursor_formats_before_mutation(
    tmp_path: Path, current: str, target: str | None
) -> None:
    root = _repo(tmp_path)
    sent = root / "coordination/mailbox/sent"
    seen = root / "coordination/mailbox/seen"
    sent.mkdir(parents=True)
    seen.mkdir()
    cursor = seen / "director.txt"
    cursor.write_text(current + "\n", encoding="ascii")
    (sent / "2026-07-17T01-02-03Z-operator-to-director-status.md").write_text(
        "fixture\n", encoding="utf-8"
    )

    with pytest.raises(kernel_activation.KernelSelectionError):
        kernel_activation._consume_events_finalize(root, "director", target)

    assert cursor.read_text(encoding="ascii") == current + "\n"
    assert _git(root, "diff", "--cached", "--name-only") == ""


@pytest.mark.parametrize(
    ("module_name", "arguments"),
    [
        (
            "protocol_capacity_board",
            ["--root", "/tmp/untrusted-reader-data", "--wave", "2"],
        ),
        ("mailbox_monitor", ["--root", "/tmp/untrusted-reader-data", "--once"]),
        ("ledger_start_guard", ["--seat", "director"]),
        ("route_lineage", ["--root", "/tmp/untrusted-reader-data"]),
        ("status", []),
        ("continuation_readiness", []),
        (
            "protocol_doctor",
            ["--root", "/tmp/untrusted-reader-data", "--wave", "2"],
        ),
    ],
)
def test_named_reader_entrypoint_denies_compact_selection_before_work(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    repo_root: Path,
    module_name: str,
    arguments: list[str],
) -> None:
    module = importlib.import_module(module_name)
    observed_roots: list[Path] = []

    def deny(root: Path, label: str) -> bool:
        observed_roots.append(Path(root).resolve())
        print(f"{label}: kernel selector: reader requires selector 0/v1", file=sys.stderr)
        return False

    monkeypatch.setattr(
        module,
        "_reader_guard",
        deny,
    )

    assert module.main(arguments) == 2
    assert observed_roots == [repo_root.resolve()]
    assert "kernel selector" in capsys.readouterr().err


def test_seat_status_entrypoint_denies_compact_selection_before_work(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str], repo_root: Path
) -> None:
    path = repo_root / ".agents/skills/four-seat-protocol/scripts/seat_status.py"
    spec = importlib.util.spec_from_file_location("phase4_seat_status", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)

    def deny(_root: Path, label: str) -> bool:
        print(f"{label}: kernel selector: reader requires selector 0/v1", file=sys.stderr)
        return False

    monkeypatch.setattr(
        module,
        "_reader_guard",
        deny,
    )

    assert module.main(["director"]) == 2
    assert "kernel selector" in capsys.readouterr().err
