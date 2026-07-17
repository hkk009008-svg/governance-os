#!/usr/bin/env python3
"""Content-free, repository-scoped reservation kernel for manual consultation."""
from __future__ import annotations
import argparse
import fcntl
import hashlib
import json
import os
from pathlib import Path
import re
import stat
import subprocess
import sys
import tempfile
import unicodedata
MAX_CANONICAL_BYTES = 32 * 1024
STATE_NAME = "chatgpt-pro-consult.json"
LOCK_NAME = "chatgpt-pro-consult.lock"
KEY_RE = re.compile(r"[A-Za-z0-9._:/-]{1,128}\Z")
HASH_RE = re.compile(r"[0-9a-f]{64}\Z")
TERMINAL = frozenset({"reserved", "sent", "failed"})
class ConsultError(Exception):
    def __init__(self, code: str):
        self.code = code
        super().__init__(code)
def _pairs(items):
    value = {}
    for key, item in items:
        if key in value:
            raise ConsultError("invalid_json")
        value[key] = item
    return value
def _nonfinite(_value):
    raise ConsultError("invalid_json")
def _loads(raw: bytes):
    try:
        return json.loads(raw.decode("utf-8"), object_pairs_hook=_pairs, parse_constant=_nonfinite)
    except ConsultError:
        raise
    except (UnicodeDecodeError, json.JSONDecodeError, ValueError) as exc:
        raise ConsultError("invalid_json") from exc
def _secret(text: str) -> bool:
    original = unicodedata.normalize("NFKC", text)
    views = (original, " ".join(original.split()), "".join(original.split()))
    named = (
        r"-----BEGIN(?:RSA|EC|OPENSSH)?PRIVATEKEY-----",
        r"authorization:(?:basic|bearer|token|digest)?[A-Za-z0-9._~+/=-]+",
        r"(?:password|secret|token|api[_-]?key)[:=][\"']?[A-Za-z0-9._~+/=-]+",
        r"(?:AKIA|ASIA)[A-Z0-9]{16}|AIza[A-Za-z0-9_-]{20,}|ya29\.[A-Za-z0-9_-]{20,}",
        r"gh[pousr]_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,}",
        r"sk-(?:proj-)?[A-Za-z0-9_-]{20,}|xox[a-z]-[A-Za-z0-9-]{10,}",
    )
    if any(re.search(pattern, view, re.IGNORECASE) for pattern in named for view in views):
        return True
    return any(re.search(r"[A-Za-z0-9+/_=-]{80,}", view) for view in views[:2])
def _normalize(raw: bytes) -> tuple[str, str]:
    value = _loads(raw)
    allowed = ({"key", "question"}, {"key", "question", "context"})
    if not isinstance(value, dict) or set(value) not in allowed:
        raise ConsultError("invalid_request")
    key, question, context = value.get("key"), value.get("question"), value.get("context", "")
    if not all(isinstance(item, str) for item in (key, question, context)):
        raise ConsultError("invalid_request")
    if not KEY_RE.fullmatch(key):
        raise ConsultError("invalid_key")
    if not question.strip():
        raise ConsultError("invalid_question")
    normalized = {"key": key, "question": question, "context": context}
    canonical = json.dumps(normalized, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    if len(canonical) > MAX_CANONICAL_BYTES:
        raise ConsultError("payload_too_large")
    if any(_secret(item) for item in (key, question, context)):
        raise ConsultError("secret_detected")
    return key, hashlib.sha256(canonical).hexdigest()
def _common(repo_root: Path | str) -> Path:
    env = os.environ.copy()
    for name in ("GIT_DIR", "GIT_WORK_TREE", "GIT_INDEX_FILE", "GIT_COMMON_DIR"):
        env.pop(name, None)
    try:
        result = subprocess.run(
            ["git", "-C", os.fspath(repo_root), "rev-parse", "--path-format=absolute", "--git-common-dir"],
            check=True, capture_output=True, text=True, env=env,
        )
        output = result.stdout.strip()
        common = Path(output)
        if not output or "\n" in output or not common.is_absolute() or not common.is_dir():
            raise ValueError
        return common
    except (OSError, subprocess.SubprocessError, UnicodeError, ValueError) as exc:
        raise ConsultError("repo_invalid") from exc
def _fixed(path: Path):
    try:
        metadata = path.lstat()
    except FileNotFoundError:
        return None
    except OSError as exc:
        raise ConsultError("io_failed") from exc
    if not stat.S_ISREG(metadata.st_mode) or stat.S_IMODE(metadata.st_mode) != 0o600:
        raise ConsultError("state_path_invalid")
    return metadata
def _bound(fd, expected, path):
    opened, current = os.fstat(fd), path.lstat()
    identity = opened.st_dev, opened.st_ino
    return (stat.S_ISREG(opened.st_mode) and stat.S_IMODE(opened.st_mode) == 0o600 and
            identity == (current.st_dev, current.st_ino) and (expected is None or identity == (expected.st_dev, expected.st_ino)))
def _read(path: Path) -> dict[str, dict[str, str]]:
    expected = _fixed(path)
    if expected is None:
        return {}
    try:
        fd = os.open(path, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK)
        if not _bound(fd, expected, path):
            os.close(fd); raise ConsultError("state_path_invalid")
        with os.fdopen(fd, "rb") as stream:
            value = _loads(stream.read())
    except ConsultError as exc:
        if exc.code == "invalid_json":
            raise ConsultError("state_corrupt") from exc
        raise
    except OSError as exc:
        raise ConsultError("io_failed") from exc
    if not isinstance(value, dict):
        raise ConsultError("state_corrupt")
    for key, record in value.items():
        if not isinstance(key, str) or not KEY_RE.fullmatch(key):
            raise ConsultError("state_corrupt")
        if not isinstance(record, dict) or set(record) != {"hash", "status"}:
            raise ConsultError("state_corrupt")
        request_hash, status_value = record.get("hash"), record.get("status")
        if not isinstance(request_hash, str) or not HASH_RE.fullmatch(request_hash):
            raise ConsultError("state_corrupt")
        if not isinstance(status_value, str) or status_value not in TERMINAL:
            raise ConsultError("state_corrupt")
    return value
def _write(common: Path, state: dict[str, dict[str, str]]) -> None:
    payload = json.dumps(state, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8") + b"\n"
    fd, temporary = -1, ""
    try:
        fd, temporary = tempfile.mkstemp(prefix=".chatgpt-pro-consult.", dir=common)
        os.fchmod(fd, 0o600)
        offset = 0
        while offset < len(payload):
            count = os.write(fd, payload[offset:])
            if not count:
                raise OSError("short write")
            offset += count
        os.fsync(fd)
        os.close(fd)
        fd = -1
        os.replace(temporary, common / STATE_NAME)
        temporary = ""
        directory_fd = os.open(common, os.O_RDONLY | getattr(os, "O_DIRECTORY", 0))
        try:
            os.fsync(directory_fd)
        finally:
            os.close(directory_fd)
    except OSError as exc:
        raise ConsultError("io_failed") from exc
    finally:
        if fd >= 0:
            try:
                os.close(fd)
            except OSError:
                pass
        if temporary:
            try:
                os.unlink(temporary)
            except OSError:
                pass
def _locked(common: Path, action):
    lock_path, lock_fd = common / LOCK_NAME, -1
    expected = _fixed(lock_path)
    try:
        lock_fd = os.open(lock_path, os.O_CREAT | os.O_RDWR | os.O_NOFOLLOW | os.O_NONBLOCK, 0o600)
        if not _bound(lock_fd, expected, lock_path):
            raise ConsultError("state_path_invalid")
        os.fchmod(lock_fd, 0o600)
        fcntl.flock(lock_fd, fcntl.LOCK_EX)
    except ConsultError:
        if lock_fd >= 0:
            os.close(lock_fd)
        raise
    except OSError as exc:
        if lock_fd >= 0:
            os.close(lock_fd)
        try:
            _fixed(lock_path)
        except ConsultError as invalid:
            raise invalid from exc
        raise ConsultError("io_failed") from exc
    try:
        return action(_read(common / STATE_NAME))
    finally:
        os.close(lock_fd)
def reserve(repo_root: Path | str, raw_payload: bytes) -> dict[str, object]:
    key, request_hash = _normalize(raw_payload)
    common = _common(repo_root)
    def apply(state):
        existing = state.get(key)
        if existing:
            if existing["hash"] != request_hash:
                raise ConsultError("key_conflict")
            return {"ok": True, "key": key, "hash": request_hash, "status": existing["status"], "created": False}
        state[key] = {"hash": request_hash, "status": "reserved"}
        _write(common, state)
        return {"ok": True, "key": key, "hash": request_hash, "status": "reserved", "created": True}
    return _locked(common, apply)
def finish(repo_root: Path | str, key: str, request_hash: str, status: str) -> dict[str, object]:
    if not isinstance(key, str) or not KEY_RE.fullmatch(key):
        raise ConsultError("invalid_key")
    if (not isinstance(request_hash, str) or not HASH_RE.fullmatch(request_hash)
            or not isinstance(status, str) or status not in {"sent", "failed"}):
        raise ConsultError("finish_rejected")
    common = _common(repo_root)
    def apply(state):
        existing = state.get(key)
        if not existing or existing["hash"] != request_hash or existing["status"] != "reserved":
            raise ConsultError("finish_rejected")
        state[key] = {"hash": request_hash, "status": status}
        _write(common, state)
        return {"ok": True, "key": key, "hash": request_hash, "status": status}
    return _locked(common, apply)
class _Parser(argparse.ArgumentParser):
    def error(self, _message):
        raise ConsultError("invalid_request")
def _arguments(argv):
    parser = _Parser(add_help=False)
    commands = parser.add_subparsers(dest="command", required=True)
    command = commands.add_parser("reserve", add_help=False)
    command.add_argument("--repo-root", required=True)
    command = commands.add_parser("finish", add_help=False)
    for name in ("repo-root", "key", "hash"):
        command.add_argument(f"--{name}", required=True)
    command.add_argument("--status", required=True, choices=("sent", "failed"))
    return parser.parse_args(argv)
def main(argv=None) -> int:
    try:
        args = _arguments(argv)
        result = (reserve(args.repo_root, sys.stdin.buffer.read()) if args.command == "reserve"
                  else finish(args.repo_root, args.key, args.hash, args.status))
        code = 0
    except ConsultError as exc:
        result = {"ok": False, "error": exc.code}
        code = 4 if exc.code in {"repo_invalid", "io_failed"} else 2
    except Exception:
        result, code = {"ok": False, "error": "io_failed"}, 4
    sys.stdout.write(json.dumps(result, ensure_ascii=False, separators=(",", ":")) + "\n")
    return code
if __name__ == "__main__":
    raise SystemExit(main())
