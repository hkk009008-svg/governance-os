"""Per-seat Ed25519 keys.

Trust model (§6.2 / §6.4):
  * PUBLIC keys are the committed trust root: coordination/threeway/keys/<seat>.pub
    (hex of the 32-byte raw public key). Anyone can read them; they authenticate
    the *author* of every load-bearing fact.
  * PRIVATE keys live OUTSIDE the repo in a keystore dir (env THREEWAY_KEYSTORE,
    default ~/.threeway/keys), file <seat>.ed25519 (hex of the 32-byte raw seed).
    A private key (and the merge-gate credential) must NEVER be present in any
    environment that executes candidate code.
Public-key (not HMAC) signatures are mandatory so a signature *verifier* — the
merge-gate — cannot forge a *signer*.
"""
from __future__ import annotations

import os
from pathlib import Path
import re
import stat
import subprocess

from cryptography.hazmat.primitives.asymmetric.ed25519 import (
    Ed25519PrivateKey,
    Ed25519PublicKey,
)


def generate_keypair() -> tuple[Ed25519PrivateKey, str]:
    """Return (private_key, public_key_hex)."""
    priv = Ed25519PrivateKey.generate()
    return priv, _public_hex(priv.public_key())


def _public_hex(pub: Ed25519PublicKey) -> str:
    from cryptography.hazmat.primitives import serialization
    raw = pub.public_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PublicFormat.Raw,
    )
    return raw.hex()


def public_hex(priv: Ed25519PrivateKey) -> str:
    """Raw Ed25519 public-key hex derived from a private key (the registry .pub format)."""
    return _public_hex(priv.public_key())


def private_to_hex(priv: Ed25519PrivateKey) -> str:
    from cryptography.hazmat.primitives import serialization
    raw = priv.private_bytes(
        encoding=serialization.Encoding.Raw,
        format=serialization.PrivateFormat.Raw,
        encryption_algorithm=serialization.NoEncryption(),
    )
    return raw.hex()


def sign(priv: Ed25519PrivateKey, message: bytes) -> bytes:
    return priv.sign(message)


def verify(public_key_hex: str, signature: bytes, message: bytes) -> None:
    """Raise cryptography.exceptions.InvalidSignature on mismatch."""
    pub = Ed25519PublicKey.from_public_bytes(bytes.fromhex(public_key_hex))
    pub.verify(signature, message)


def _keystore_dir() -> Path:
    return Path(os.environ.get("THREEWAY_KEYSTORE", str(Path.home() / ".threeway" / "keys")))


_SEAT_NAME = re.compile(r"^[A-Za-z0-9][A-Za-z0-9-]*$")


def validate_seat_name(seat: str) -> str:
    if not isinstance(seat, str) or _SEAT_NAME.fullmatch(seat) is None:
        raise ValueError(f"invalid key seat name: {seat!r}")
    return seat


def _secure_keystore_directory(path: Path) -> None:
    try:
        metadata = path.lstat()
    except FileNotFoundError as exc:
        raise FileNotFoundError(f"private keystore directory does not exist: {path}") from exc
    if stat.S_ISLNK(metadata.st_mode):
        raise PermissionError(f"private keystore directory must not be a symlink: {path}")
    if not stat.S_ISDIR(metadata.st_mode):
        raise PermissionError(f"private keystore path is not a directory: {path}")
    if stat.S_IMODE(metadata.st_mode) != 0o700:
        raise PermissionError(f"private keystore directory must have mode 0700: {path}")


def load_private(seat: str) -> Ed25519PrivateKey:
    seat = validate_seat_name(seat)
    directory = _keystore_dir()
    _secure_keystore_directory(directory)
    path = directory / f"{seat}.ed25519"
    try:
        metadata = path.lstat()
    except FileNotFoundError as exc:
        raise FileNotFoundError(f"no private key for seat {seat!r} at {path}") from exc
    if stat.S_ISLNK(metadata.st_mode):
        raise PermissionError(f"private key must not be a symlink: {path}")
    if not stat.S_ISREG(metadata.st_mode):
        raise PermissionError(f"private key must be a regular file: {path}")
    if stat.S_IMODE(metadata.st_mode) != 0o600:
        raise PermissionError(f"private key must have mode 0600: {path}")
    try:
        value = path.read_text(encoding="ascii").strip()
    except (OSError, UnicodeError) as exc:
        raise PermissionError(f"cannot read private key securely at {path}: {exc}") from exc
    if re.fullmatch(r"[0-9a-f]{64}", value) is None:
        raise ValueError(f"private key at {path} is not one lowercase 32-byte seed")
    seed = bytes.fromhex(value)
    return Ed25519PrivateKey.from_private_bytes(seed)


class PublicKeyRegistry:
    """Object-addressed committed trust root: maps seat -> public-key hex."""

    def __init__(self, registry_dir: str | Path, revision: str = "HEAD"):
        self._dir = Path(registry_dir)
        self._revision = revision
        self._binding: tuple[Path, str, str] | None = None

    @staticmethod
    def _git(repo: Path, *args: str) -> bytes:
        env = os.environ.copy()
        env.pop("GIT_INDEX_FILE", None)
        env["GIT_CONFIG_GLOBAL"] = os.devnull
        env["GIT_CONFIG_SYSTEM"] = os.devnull
        env["GIT_NO_REPLACE_OBJECTS"] = "1"
        completed = subprocess.run(
            ["git", "--no-optional-locks", "-C", str(repo), *args],
            env=env,
            capture_output=True,
            check=False,
        )
        if completed.returncode != 0:
            detail = (completed.stderr or completed.stdout).decode(
                "utf-8", errors="replace"
            ).strip()
            raise KeyError(detail or f"git {' '.join(args)} failed")
        return completed.stdout

    def _committed_binding(self) -> tuple[Path, str, str]:
        if self._binding is not None:
            return self._binding
        try:
            metadata = self._dir.lstat()
        except FileNotFoundError as exc:
            raise KeyError(f"public-key registry directory is absent: {self._dir}") from exc
        if stat.S_ISLNK(metadata.st_mode) or not stat.S_ISDIR(metadata.st_mode):
            raise KeyError(
                f"public-key registry must be a regular non-symlink directory: {self._dir}"
            )
        repo_text = self._git(self._dir, "rev-parse", "--show-toplevel").decode(
            "utf-8", errors="strict"
        ).strip()
        repo = Path(repo_text).resolve()
        try:
            relative_dir = self._dir.resolve().relative_to(repo).as_posix()
        except (OSError, ValueError) as exc:
            raise KeyError(f"public-key registry is outside its Git repository: {self._dir}") from exc
        if relative_dir == ".":
            relative_dir = ""
        commit = self._git(
            repo, "rev-parse", "--verify", f"{self._revision}^{{commit}}"
        ).decode("ascii").strip()
        if re.fullmatch(r"[0-9a-f]{40,64}", commit) is None:
            raise KeyError(f"registry revision did not resolve to a commit: {self._revision}")
        self._binding = (repo, relative_dir, commit)
        return self._binding

    def get(self, seat: str) -> str:
        seat = validate_seat_name(seat)
        repo, relative_dir, commit = self._committed_binding()
        relative = f"{relative_dir}/{seat}.pub" if relative_dir else f"{seat}.pub"
        record = self._git(repo, "ls-tree", "-z", commit, "--", relative)
        rows = [row for row in record.split(b"\0") if row]
        if len(rows) != 1:
            raise KeyError(
                f"no committed public key for seat {seat!r} at {commit[:12]}:{relative}"
            )
        try:
            header, recorded_path = rows[0].split(b"\t", 1)
            mode, object_type, oid = header.decode("ascii").split()
        except (ValueError, UnicodeError) as exc:
            raise KeyError(f"invalid committed registry tree entry for {seat!r}") from exc
        try:
            decoded_path = recorded_path.decode("utf-8", errors="strict")
        except UnicodeError as exc:
            raise KeyError(f"invalid committed registry path for {seat!r}") from exc
        if decoded_path != relative:
            raise KeyError(f"committed registry path mismatch for {seat!r}")
        if mode not in {"100644", "100755"} or object_type != "blob":
            raise KeyError(
                "committed public key must be a regular non-symlink blob, "
                f"not mode {mode}: {relative}"
            )
        try:
            value = self._git(repo, "cat-file", "blob", oid).decode("ascii").strip()
        except (KeyError, UnicodeError) as exc:
            raise KeyError(f"cannot read committed public key for {seat!r}: {exc}") from exc
        if re.fullmatch(r"[0-9a-f]{64}", value) is None:
            raise KeyError(f"committed public key for {seat!r} is not 32-byte lowercase hex")
        return value
