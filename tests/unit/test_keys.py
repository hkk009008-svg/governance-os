"""Unit tests for threeway.keys and threeway.keys_bootstrap.

Covers the per-seat Ed25519 trust primitives: keypair generation, public-hex
derivation, sign/verify roundtrip + tamper detection, the committed
PublicKeyRegistry, the off-repo private keystore (load_private), and the
keys_bootstrap CLI that wires both together.

Hermetic: every filesystem/env touch goes through tmp_path / monkeypatch; no
network, no real git, no writes outside the test sandbox.
"""
from __future__ import annotations

import os
from pathlib import Path
import stat
import subprocess
import sys

import pytest
from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

from threeway import keys, keys_bootstrap


def _git(root: Path, *args: str) -> str:
    env = {key: value for key, value in os.environ.items() if key != "GIT_INDEX_FILE"}
    env["GIT_CONFIG_GLOBAL"] = os.devnull
    env["GIT_CONFIG_SYSTEM"] = os.devnull
    completed = subprocess.run(
        ["git", "-C", str(root), *args],
        env=env,
        check=True,
        capture_output=True,
        text=True,
    )
    return completed.stdout.strip()


def _init_registry_repo(root: Path) -> None:
    _git(root, "init", "-q")
    _git(root, "config", "user.name", "Key Registry Test")
    _git(root, "config", "user.email", "keys@example.invalid")
    _git(root, "config", "commit.gpgsign", "false")


def _commit_registry(root: Path, message: str = "test: registry") -> None:
    _git(root, "add", ".")
    _git(root, "commit", "-q", "--allow-empty", "-m", message)


def test_generate_keypair_shape():
    priv, pub_hex = keys.generate_keypair()
    assert isinstance(priv, Ed25519PrivateKey)
    assert isinstance(pub_hex, str)
    # Raw Ed25519 public key is 32 bytes -> 64 hex chars.
    assert len(pub_hex) == 64
    # Valid lowercase hex.
    assert bytes.fromhex(pub_hex).__len__() == 32
    assert pub_hex == pub_hex.lower()


def test_public_hex_matches_generate_keypair():
    priv, pub_hex = keys.generate_keypair()
    assert keys.public_hex(priv) == pub_hex


def test_sign_verify_roundtrip():
    priv, pub_hex = keys.generate_keypair()
    message = b"load-bearing fact: GO"
    sig = keys.sign(priv, message)
    assert isinstance(sig, bytes)
    # A correct (pub, sig, message) triple verifies silently (returns None).
    assert keys.verify(pub_hex, sig, message) is None


def test_verify_rejects_wrong_message():
    priv, pub_hex = keys.generate_keypair()
    sig = keys.sign(priv, b"original message")
    with pytest.raises(InvalidSignature):
        keys.verify(pub_hex, sig, b"tampered message")


def test_verify_rejects_wrong_key():
    priv, _ = keys.generate_keypair()
    _, other_pub_hex = keys.generate_keypair()
    message = b"signed by priv, checked against a different pub"
    sig = keys.sign(priv, message)
    with pytest.raises(InvalidSignature):
        keys.verify(other_pub_hex, sig, message)


def test_registry_get_missing_raises_keyerror(tmp_path):
    _init_registry_repo(tmp_path)
    _commit_registry(tmp_path)
    reg = keys.PublicKeyRegistry(tmp_path)
    with pytest.raises(KeyError):
        reg.get("director")


def test_registry_get_returns_stripped_hex(tmp_path):
    _init_registry_repo(tmp_path)
    _, pub_hex = keys.generate_keypair()
    # Bootstrap writes the hex with a trailing newline; .get must strip it.
    (tmp_path / "director.pub").write_text(pub_hex + "\n")
    _commit_registry(tmp_path)
    reg = keys.PublicKeyRegistry(tmp_path)
    assert reg.get("director") == pub_hex


def test_registry_rejects_symlink_and_malformed_public_key(tmp_path):
    outside = tmp_path / "outside.pub"
    outside.write_text("0" * 64 + "\n", encoding="ascii")
    registry_dir = tmp_path / "registry"
    registry_dir.mkdir()
    _init_registry_repo(tmp_path)
    (registry_dir / "director.pub").symlink_to(outside)
    _commit_registry(tmp_path, "test: symlink registry")
    registry = keys.PublicKeyRegistry(registry_dir)
    with pytest.raises(KeyError, match="non-symlink"):
        registry.get("director")

    (registry_dir / "director.pub").unlink()
    (registry_dir / "director.pub").write_text("not-a-key\n", encoding="ascii")
    _commit_registry(tmp_path, "test: malformed registry")
    registry = keys.PublicKeyRegistry(registry_dir)
    with pytest.raises(KeyError, match="32-byte lowercase hex"):
        registry.get("director")


def test_registry_reads_committed_key_not_dirty_worktree_replacement(tmp_path):
    registry_dir = tmp_path / "registry"
    registry_dir.mkdir()
    _init_registry_repo(tmp_path)
    _, committed = keys.generate_keypair()
    _, replacement = keys.generate_keypair()
    path = registry_dir / "director.pub"
    path.write_text(committed + "\n", encoding="ascii")
    _commit_registry(tmp_path)
    path.write_text(replacement + "\n", encoding="ascii")

    value = keys.PublicKeyRegistry(registry_dir).get("director")

    assert value == committed
    assert value != replacement


def test_load_private_missing_raises_filenotfound(tmp_path, monkeypatch):
    monkeypatch.setenv("THREEWAY_KEYSTORE", str(tmp_path))
    with pytest.raises(FileNotFoundError):
        keys.load_private("operator")


def test_load_private_roundtrips_written_key(tmp_path, monkeypatch):
    tmp_path.chmod(0o700)
    monkeypatch.setenv("THREEWAY_KEYSTORE", str(tmp_path))
    priv, pub_hex = keys.generate_keypair()
    # Persist the private seed exactly as keys_bootstrap does (hex + newline).
    (tmp_path / "operator.ed25519").write_text(keys.private_to_hex(priv) + "\n")
    (tmp_path / "operator.ed25519").chmod(0o600)

    loaded = keys.load_private("operator")
    assert isinstance(loaded, Ed25519PrivateKey)
    # Same key -> same public hex, and signatures verify against the registry pub.
    assert keys.public_hex(loaded) == pub_hex
    sig = keys.sign(loaded, b"roundtripped seat key")
    assert keys.verify(pub_hex, sig, b"roundtripped seat key") is None


def test_bootstrap_main_writes_keys_and_returns_zero(tmp_path, capsys):
    reg = tmp_path / "registry"
    ks = tmp_path / "keystore"
    rc = keys_bootstrap.main(
        ["--registry", str(reg), "--keystore", str(ks), "--seats", "director", "ci"]
    )
    assert rc == 0

    for seat in ("director", "ci"):
        pub_path = reg / f"{seat}.pub"
        priv_path = ks / f"{seat}.ed25519"
        assert pub_path.exists()
        assert priv_path.exists()
        assert stat.S_IMODE(priv_path.stat().st_mode) == 0o600
        assert priv_path.is_file() and not priv_path.is_symlink()

    assert stat.S_IMODE(ks.stat().st_mode) == 0o700
    assert ks.is_dir() and not ks.is_symlink()

    # Only the requested seats were generated (not the full SEATS default).
    assert sorted(p.name for p in reg.glob("*.pub")) == ["ci.pub", "director.pub"]

    # The written pair is internally consistent: registry pub == pub of keystore priv.
    pub_hex = (reg / "director.pub").read_text().strip()
    priv = Ed25519PrivateKey.from_private_bytes(
        bytes.fromhex((ks / "director.ed25519").read_text().strip())
    )
    assert keys.public_hex(priv) == pub_hex
    assert len(pub_hex) == 64


def test_bootstrap_main_loadable_via_registry_and_keystore(tmp_path, monkeypatch):
    reg = tmp_path / "registry"
    ks = tmp_path / "keystore"
    rc = keys_bootstrap.main(
        ["--registry", str(reg), "--keystore", str(ks), "--seats", "director"]
    )
    assert rc == 0
    _init_registry_repo(tmp_path)
    _commit_registry(tmp_path)

    monkeypatch.setenv("THREEWAY_KEYSTORE", str(ks))
    priv = keys.load_private("director")
    pub_hex = keys.PublicKeyRegistry(reg).get("director")

    message = b"end-to-end: bootstrap -> keystore -> registry"
    sig = keys.sign(priv, message)
    assert keys.verify(pub_hex, sig, message) is None


def test_bootstrap_complete_roster_is_idempotent_without_overwrite(tmp_path):
    reg = tmp_path / "registry"
    ks = tmp_path / "keystore"
    args = ["--registry", str(reg), "--keystore", str(ks), "--seats", "director", "ci"]
    assert keys_bootstrap.main(args) == 0
    before = {
        path: (path.read_bytes(), path.stat().st_ino)
        for path in (*reg.glob("*.pub"), *ks.glob("*.ed25519"))
    }

    assert keys_bootstrap.main(args) == 0

    after = {
        path: (path.read_bytes(), path.stat().st_ino)
        for path in (*reg.glob("*.pub"), *ks.glob("*.ed25519"))
    }
    assert after == before


def test_bootstrap_partial_roster_fails_closed_without_filling_gaps(
    tmp_path, capsys
):
    reg = tmp_path / "registry"
    ks = tmp_path / "keystore"
    reg.mkdir()
    ks.mkdir(mode=0o700)
    (reg / "director.pub").write_text("0" * 64 + "\n", encoding="ascii")

    result = keys_bootstrap.main(
        ["--registry", str(reg), "--keystore", str(ks), "--seats", "director", "ci"]
    )

    assert result == 2
    assert "partial" in capsys.readouterr().err.lower()
    assert not (reg / "ci.pub").exists()
    assert not any(ks.glob("*.ed25519"))


def test_bootstrap_mid_provision_failure_rolls_back_and_can_retry(
    tmp_path, monkeypatch, capsys
):
    reg = tmp_path / "registry"
    ks = tmp_path / "keystore"
    args = ["--registry", str(reg), "--keystore", str(ks), "--seats", "director", "ci"]
    write_exclusive = keys_bootstrap._write_exclusive
    calls = 0

    def fail_on_third_write(
        path: Path,
        value: str,
        mode: int,
        created_log: list[keys_bootstrap.CreatedFile] | None = None,
    ):
        nonlocal calls
        calls += 1
        if calls == 3:
            raise keys_bootstrap.BootstrapError("injected provision failure")
        return write_exclusive(path, value, mode, created_log)

    monkeypatch.setattr(keys_bootstrap, "_write_exclusive", fail_on_third_write)

    assert keys_bootstrap.main(args) == 2
    assert "injected provision failure" in capsys.readouterr().err
    assert not list(reg.glob("*.pub"))
    assert not list(ks.glob("*.ed25519"))

    monkeypatch.setattr(keys_bootstrap, "_write_exclusive", write_exclusive)
    assert keys_bootstrap.main(args) == 0
    assert sorted(path.name for path in reg.glob("*.pub")) == ["ci.pub", "director.pub"]
    assert sorted(path.name for path in ks.glob("*.ed25519")) == [
        "ci.ed25519",
        "director.ed25519",
    ]


def test_exclusive_key_write_removes_its_file_after_fsync_failure(
    tmp_path, monkeypatch
):
    target = tmp_path / "director.ed25519"

    def fail_fsync(_descriptor: int) -> None:
        raise OSError("injected fsync failure")

    monkeypatch.setattr(keys_bootstrap.os, "fsync", fail_fsync)

    with pytest.raises(OSError, match="injected fsync failure"):
        keys_bootstrap._write_exclusive(target, "0" * 64, 0o600)

    assert not target.exists()


def test_created_file_rollback_restores_a_concurrent_replacement(
    tmp_path, monkeypatch
):
    target = tmp_path / "director.ed25519"
    target.write_text("created\n", encoding="ascii")
    metadata = target.stat()
    created = (target, metadata.st_dev, metadata.st_ino)
    rename = keys_bootstrap.os.rename
    replacement_inode = None

    def swap_then_rename(source, destination):
        nonlocal replacement_inode
        if Path(source) == target:
            target.unlink()
            target.write_text("replacement\n", encoding="ascii")
            replacement_inode = target.stat().st_ino
        return rename(source, destination)

    monkeypatch.setattr(keys_bootstrap.os, "rename", swap_then_rename)

    failure = keys_bootstrap._remove_created_file(created)

    assert failure is not None
    assert "replacement was restored" in failure
    assert target.read_text(encoding="ascii") == "replacement\n"
    assert target.stat().st_ino == replacement_inode


def test_bootstrap_interrupt_rolls_back_completed_writes(
    tmp_path, monkeypatch
):
    reg = tmp_path / "registry"
    ks = tmp_path / "keystore"
    args = ["--registry", str(reg), "--keystore", str(ks), "--seats", "director", "ci"]
    write_exclusive = keys_bootstrap._write_exclusive
    calls = 0

    def interrupt_on_third_write(
        path: Path,
        value: str,
        mode: int,
        created_log: list[keys_bootstrap.CreatedFile] | None = None,
    ):
        nonlocal calls
        calls += 1
        if calls == 3:
            raise KeyboardInterrupt
        return write_exclusive(path, value, mode, created_log)

    monkeypatch.setattr(keys_bootstrap, "_write_exclusive", interrupt_on_third_write)

    with pytest.raises(KeyboardInterrupt):
        keys_bootstrap.main(args)

    assert not list(reg.glob("*.pub"))
    assert not list(ks.glob("*.ed25519"))


def test_bootstrap_interrupt_after_write_returns_still_rolls_it_back(
    tmp_path, monkeypatch
):
    reg = tmp_path / "registry"
    ks = tmp_path / "keystore"
    args = ["--registry", str(reg), "--keystore", str(ks), "--seats", "director"]
    write_exclusive = keys_bootstrap._write_exclusive

    def interrupt_after_write(
        path: Path,
        value: str,
        mode: int,
        created_log: list[keys_bootstrap.CreatedFile] | None = None,
    ):
        result = write_exclusive(path, value, mode, created_log)
        raise KeyboardInterrupt

    monkeypatch.setattr(keys_bootstrap, "_write_exclusive", interrupt_after_write)

    with pytest.raises(KeyboardInterrupt):
        keys_bootstrap.main(args)

    assert not list(reg.glob("*.pub"))
    assert not list(ks.glob("*.ed25519"))


@pytest.mark.parametrize(
    ("registry_rel", "keystore_rel"),
    (("shared", "shared"), ("registry", "registry/private"), ("private/registry", "private")),
)
def test_bootstrap_rejects_equal_or_nested_key_directories(
    tmp_path, capsys, registry_rel: str, keystore_rel: str
):
    reg = tmp_path / registry_rel
    ks = tmp_path / keystore_rel

    result = keys_bootstrap.main(
        ["--registry", str(reg), "--keystore", str(ks), "--seats", "director"]
    )

    assert result == 2
    assert "separate, non-nested" in capsys.readouterr().err
    assert not list(tmp_path.rglob("*.pub"))
    assert not list(tmp_path.rglob("*.ed25519"))


def test_bootstrap_refuses_to_chmod_preexisting_insecure_keystore(
    tmp_path, capsys
):
    reg = tmp_path / "registry"
    ks = tmp_path / "keystore"
    reg.mkdir()
    ks.mkdir(mode=0o755)
    ks.chmod(0o755)

    result = keys_bootstrap.main(
        ["--registry", str(reg), "--keystore", str(ks), "--seats", "director"]
    )

    assert result == 2
    assert "0700" in capsys.readouterr().err
    assert stat.S_IMODE(ks.stat().st_mode) == 0o755
    assert list(reg.iterdir()) == []
    assert list(ks.iterdir()) == []


@pytest.mark.parametrize("target", ("registry", "keystore"))
def test_bootstrap_rejects_symlink_key_targets_without_overwrite(
    tmp_path, capsys, target: str
):
    reg = tmp_path / "registry"
    ks = tmp_path / "keystore"
    reg.mkdir()
    ks.mkdir(mode=0o700)
    outside = tmp_path / "outside"
    outside.write_text("do not replace\n", encoding="utf-8")
    if target == "registry":
        (reg / "director.pub").symlink_to(outside)
    else:
        (ks / "director.ed25519").symlink_to(outside)

    result = keys_bootstrap.main(
        ["--registry", str(reg), "--keystore", str(ks), "--seats", "director"]
    )

    assert result == 2
    assert "partial" in capsys.readouterr().err.lower()
    assert outside.read_text(encoding="utf-8") == "do not replace\n"


@pytest.mark.parametrize("mode", (0o644, 0o660))
def test_load_private_rejects_insecure_file_permissions(tmp_path, monkeypatch, mode):
    tmp_path.chmod(0o700)
    monkeypatch.setenv("THREEWAY_KEYSTORE", str(tmp_path))
    priv, _ = keys.generate_keypair()
    path = tmp_path / "operator.ed25519"
    path.write_text(keys.private_to_hex(priv) + "\n", encoding="ascii")
    path.chmod(mode)

    with pytest.raises(PermissionError, match="0600"):
        keys.load_private("operator")


def test_load_private_rejects_symlink_and_insecure_directory(tmp_path, monkeypatch):
    real_dir = tmp_path / "real"
    real_dir.mkdir(mode=0o700)
    priv, _ = keys.generate_keypair()
    real = real_dir / "operator.ed25519"
    real.write_text(keys.private_to_hex(priv) + "\n", encoding="ascii")
    real.chmod(0o600)
    linked_dir = tmp_path / "linked"
    linked_dir.symlink_to(real_dir, target_is_directory=True)
    monkeypatch.setenv("THREEWAY_KEYSTORE", str(linked_dir))
    with pytest.raises(PermissionError, match="symlink"):
        keys.load_private("operator")

    monkeypatch.setenv("THREEWAY_KEYSTORE", str(real_dir))
    real_dir.chmod(0o755)
    with pytest.raises(PermissionError, match="0700"):
        keys.load_private("operator")


def test_cutover_rejects_partial_roster_before_irreversible_step(
    tmp_path: Path, repo_root: Path
) -> None:
    registry = tmp_path / "coordination" / "threeway" / "keys"
    registry.mkdir(parents=True)
    (registry / "director.pub").write_text("0" * 64 + "\n", encoding="ascii")
    keystore = tmp_path / "keystore"
    keystore.mkdir(mode=0o700)
    env = os.environ.copy()
    env.update(
        {
            "PYTHON": sys.executable,
            "PYTHONPATH": str(repo_root),
            "THREEWAY_KEYSTORE": str(keystore),
        }
    )

    completed = subprocess.run(
        [str(repo_root / "scripts" / "execute_threeway_cutover.sh"), "--yes"],
        cwd=tmp_path,
        env=env,
        text=True,
        capture_output=True,
        check=False,
    )

    assert completed.returncode != 0
    assert "partial" in completed.stderr.lower()
    assert "[2/2]" not in completed.stdout


def test_cutover_stops_after_provisioning_until_public_roster_is_committed(
    tmp_path: Path, repo_root: Path
) -> None:
    repo = tmp_path / "repo"
    repo.mkdir()
    _init_registry_repo(repo)
    _git(repo, "commit", "-q", "--allow-empty", "-m", "test: empty base")
    keystore = tmp_path / "keystore"
    env = os.environ.copy()
    env.update(
        {
            "PYTHON": sys.executable,
            "PYTHONPATH": str(repo_root),
            "THREEWAY_KEYSTORE": str(keystore),
        }
    )

    completed = subprocess.run(
        [str(repo_root / "scripts" / "execute_threeway_cutover.sh"), "--yes"],
        cwd=repo,
        env=env,
        text=True,
        capture_output=True,
        check=False,
    )

    assert completed.returncode == 3
    assert "public-key roster is new" in completed.stderr
    assert "[2/2]" not in completed.stdout
    assert list((repo / "coordination/threeway/keys").glob("*.pub"))
    assert _git(repo, "for-each-ref", "--format=%(refname)", "refs/threeway") == ""
