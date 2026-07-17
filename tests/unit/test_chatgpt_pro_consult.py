from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import stat
import subprocess
import sys

import pytest

import chatgpt_pro_consult as consult


VALID = {
    "key": "design:compact-consult/v1",
    "question": "Which invariant is most likely to fail?",
    "context": "Compare terminal reservation with retry behavior.",
}

SECRET_CASES = (
    "-----BEGIN PRIVATE KEY-----",
    "Authorization: Bearer abcdefghijklmnopqrstuvwxyz",
    "api_key = abcdefghijklmnopqrstuvwxyz",
    "AKIAABCDEFGHIJKLMNOP",
    "ghp_abcdefghijklmnopqrstuvwxyz123456",
    "sk-proj-abcdefghijklmnopqrstuvwxyz123456",
)

SCRIPT = Path(__file__).parents[2] / "scripts" / "chatgpt_pro_consult.py"


def _git(repo: Path, *args: str) -> str:
    env = os.environ.copy()
    env.pop("GIT_INDEX_FILE", None)
    return subprocess.run(
        ["git", "-C", str(repo), *args],
        check=True,
        capture_output=True,
        text=True,
        env=env,
    ).stdout.strip()


@pytest.fixture
def repo(tmp_path: Path) -> Path:
    root = tmp_path / "repo"
    root.mkdir()
    _git(root, "init", "-q")
    _git(root, "config", "user.email", "test@example.com")
    _git(root, "config", "user.name", "Test User")
    _git(root, "commit", "--allow-empty", "-q", "-m", "initial")
    return root


def _raw(value: dict[str, object]) -> bytes:
    return json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")


def _request(**changes: object) -> bytes:
    value = dict(VALID)
    value.update(changes)
    return _raw(value)


def _paths(repo: Path) -> tuple[Path, Path]:
    common = Path(_git(repo, "rev-parse", "--path-format=absolute", "--git-common-dir"))
    return common / consult.STATE_NAME, common / consult.LOCK_NAME


def _error(repo: Path, raw: bytes, code: str) -> None:
    with pytest.raises(consult.ConsultError) as exc:
        consult.reserve(repo, raw)
    assert exc.value.code == code
    assert str(exc.value) == code


def _state(key: str, request_hash: str, status: str, **extra: object) -> bytes:
    record: dict[str, object] = {"hash": request_hash, "status": status}
    record.update(extra)
    return _raw({key: record}) + b"\n"


def test_reserve_accepts_exact_request_and_hashes_exact_strings(repo: Path):
    canonical = _raw(VALID)
    result = consult.reserve(repo, canonical)

    assert result == {
        "ok": True,
        "key": VALID["key"],
        "hash": hashlib.sha256(canonical).hexdigest(),
        "status": "reserved",
        "created": True,
    }


def test_reserve_defaults_only_absent_context_to_empty_string(repo: Path):
    absent = dict(VALID)
    absent.pop("context")
    first = consult.reserve(repo, _raw(absent))
    explicit = consult.reserve(repo, _request(context=""))
    changed = dict(absent, key="design:compact-consult/changed", context="text")
    empty_other = dict(absent, key="design:compact-consult/empty")
    changed_result = consult.reserve(repo, _raw(changed))
    empty_result = consult.reserve(repo, _raw(empty_other))

    assert first["hash"] == explicit["hash"]
    assert changed_result["hash"] != empty_result["hash"]


@pytest.mark.parametrize(
    ("raw", "code"),
    (
        (_request(extra="unknown"), "invalid_request"),
        (
            b'{"key":"design:compact-consult/v1","question":"one",'
            b'"question":"two"}',
            "invalid_json",
        ),
        (_request(key=1), "invalid_request"),
        (_request(question=None), "invalid_request"),
        (_request(context=[]), "invalid_request"),
        (_raw({"question": "missing key"}), "invalid_request"),
        (_raw({"key": "missing-question"}), "invalid_request"),
    ),
)
def test_reserve_rejects_unknown_duplicate_and_wrong_typed_fields(
    repo: Path, raw: bytes, code: str
):
    _error(repo, raw, code)


def test_reserve_rejects_invalid_key_empty_question_and_oversize_canonical_json(
    repo: Path,
):
    _error(repo, _request(key="bad key"), "invalid_key")
    _error(repo, _request(key="a" * 129), "invalid_key")
    _error(repo, _request(question="   \n\t"), "invalid_question")
    _error(repo, _request(question="x" * (consult.MAX_CANONICAL_BYTES + 1)), "payload_too_large")


@pytest.mark.parametrize(
    "text",
    SECRET_CASES
    + tuple(" \n".join(secret) for secret in SECRET_CASES)
    + ("api_key： abcdefghijklmnopqrstuvwxyz",),
)
def test_named_secrets_are_rejected_in_original_collapsed_and_compact_views(
    repo: Path, text: str
):
    _error(repo, _request(context=text), "secret_detected")


def test_generic_long_token_scans_original_and_collapsed_but_not_compact_view(
    repo: Path,
):
    _error(repo, _request(context="z" * 80), "secret_detected")
    accepted = consult.reserve(
        repo,
        _request(key="design:compact-consult/words", context=" ".join(["abcd"] * 20)),
    )
    assert accepted["created"] is True


def test_local_rejection_creates_no_lock_or_state(repo: Path):
    state_path, lock_path = _paths(repo)
    _error(repo, _request(question=""), "invalid_question")
    assert not state_path.exists()
    assert not lock_path.exists()


def test_state_and_lock_are_regular_mode_0600_files(repo: Path):
    consult.reserve(repo, _raw(VALID))
    for path in _paths(repo):
        metadata = path.lstat()
        assert stat.S_ISREG(metadata.st_mode)
        assert stat.S_IMODE(metadata.st_mode) == 0o600


@pytest.mark.parametrize("path_index", (0, 1), ids=("state", "lock"))
def test_state_and_lock_symlinks_are_rejected_without_mutation(
    repo: Path, path_index: int
):
    fixed = _paths(repo)[path_index]
    target = repo / f"target-{path_index}"
    target.write_bytes(b"preserve-this")
    fixed.symlink_to(target)

    _error(repo, _raw(VALID), "state_path_invalid")
    assert fixed.is_symlink()
    assert target.read_bytes() == b"preserve-this"


@pytest.mark.parametrize(
    "corrupt",
    (
        b"{not-json\n",
        _state(VALID["key"], "a" * 64, "reserved", extra=True),
        _state(VALID["key"], "invalid", "reserved"),
        _state("bad key", "a" * 64, "reserved"),
        _state(VALID["key"], "a" * 64, "queued"),
    ),
)
def test_corrupt_or_structurally_invalid_state_is_not_rewritten(
    repo: Path, corrupt: bytes
):
    state_path, _ = _paths(repo)
    state_path.write_bytes(corrupt)
    state_path.chmod(0o600)

    _error(repo, _raw(VALID), "state_corrupt")
    assert state_path.read_bytes() == corrupt


def test_same_hash_reports_existing_state_and_changed_content_conflicts(repo: Path):
    first = consult.reserve(repo, _raw(VALID))
    again = consult.reserve(repo, _raw(VALID))
    assert again == dict(first, created=False)

    _error(repo, _request(question="Changed question"), "key_conflict")


@pytest.mark.parametrize("status", ("sent", "failed"))
def test_finish_allows_only_reserved_to_sent_or_failed(repo: Path, status: str):
    request = dict(VALID, key=f"design:compact-consult/{status}")
    reserved = consult.reserve(repo, _raw(request))
    result = consult.finish(repo, request["key"], reserved["hash"], status)
    assert result == {
        "ok": True,
        "key": request["key"],
        "hash": reserved["hash"],
        "status": status,
    }


@pytest.mark.parametrize(
    ("terminal", "proposed"),
    (("sent", "sent"), ("sent", "failed"), ("failed", "sent"), ("failed", "failed")),
)
def test_finish_rejects_unknown_key_stale_hash_and_every_terminal_transition(
    repo: Path, terminal: str, proposed: str
):
    reserved = consult.reserve(repo, _raw(VALID))
    state_path, _ = _paths(repo)

    before = state_path.read_bytes()
    with pytest.raises(consult.ConsultError, match="^finish_rejected$"):
        consult.finish(repo, "unknown", reserved["hash"], proposed)
    assert state_path.read_bytes() == before

    with pytest.raises(consult.ConsultError, match="^finish_rejected$"):
        consult.finish(repo, VALID["key"], "0" * 64, proposed)
    assert state_path.read_bytes() == before

    consult.finish(repo, VALID["key"], reserved["hash"], terminal)
    terminal_bytes = state_path.read_bytes()
    with pytest.raises(consult.ConsultError, match="^finish_rejected$"):
        consult.finish(repo, VALID["key"], reserved["hash"], proposed)
    assert state_path.read_bytes() == terminal_bytes


def test_finish_write_failure_leaves_reserved_terminal(repo: Path, monkeypatch):
    reserved = consult.reserve(repo, _raw(VALID))
    state_path, _ = _paths(repo)
    before = state_path.read_bytes()

    def fail_replace(source: object, destination: object) -> None:
        raise OSError("simulated write failure")

    monkeypatch.setattr(consult.os, "replace", fail_replace)
    with pytest.raises(consult.ConsultError, match="^io_failed$"):
        consult.finish(repo, VALID["key"], reserved["hash"], "sent")
    assert state_path.read_bytes() == before
    assert consult.reserve(repo, _raw(VALID))["created"] is False


def test_two_worktrees_share_one_state_file(repo: Path, tmp_path: Path):
    linked = tmp_path / "linked"
    _git(repo, "worktree", "add", "-q", "-b", "linked", str(linked))

    first = consult.reserve(repo, _raw(VALID))
    second = consult.reserve(linked, _raw(VALID))
    assert second == dict(first, created=False)
    assert _paths(repo)[0] == _paths(linked)[0]


def test_two_processes_reserving_same_key_create_exactly_one_record(repo: Path):
    command = [sys.executable, str(SCRIPT), "reserve", "--repo-root", str(repo)]
    raw = _raw(VALID)
    processes = [
        subprocess.Popen(command, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        for _ in range(2)
    ]
    results = [process.communicate(raw) for process in processes]

    assert [process.returncode for process in processes] == [0, 0]
    decoded = [json.loads(stdout) for stdout, _ in results]
    assert sorted(item["created"] for item in decoded) == [False, True]
    assert all(stderr == b"" for _, stderr in results)
    state_path, _ = _paths(repo)
    assert list(json.loads(state_path.read_bytes())) == [VALID["key"]]


def test_cli_errors_are_json_and_do_not_echo_rejected_content(repo: Path):
    sentinel = "UNIQUE_REJECTED_SENTINEL_938104"
    raw = _request(context=f"Authorization: Bearer {sentinel}")
    result = subprocess.run(
        [sys.executable, str(SCRIPT), "reserve", "--repo-root", str(repo)],
        input=raw,
        capture_output=True,
    )

    assert result.returncode == 2
    assert json.loads(result.stdout) == {"ok": False, "error": "secret_detected"}
    assert sentinel.encode() not in result.stdout
    assert sentinel.encode() not in result.stderr
    assert result.stderr == b""
