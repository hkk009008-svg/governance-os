"""Unit tests for threeway.keys and threeway.keys_bootstrap.

Covers the per-seat Ed25519 trust primitives: keypair generation, public-hex
derivation, sign/verify roundtrip + tamper detection, the committed
PublicKeyRegistry, the off-repo private keystore (load_private), and the
keys_bootstrap CLI that wires both together.

Hermetic: every filesystem/env touch goes through tmp_path / monkeypatch; no
network, no real git, no writes outside the test sandbox.
"""
from __future__ import annotations

import pytest
from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

from threeway import keys, keys_bootstrap


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
    reg = keys.PublicKeyRegistry(tmp_path)
    with pytest.raises(KeyError):
        reg.get("director")


def test_registry_get_returns_stripped_hex(tmp_path):
    _, pub_hex = keys.generate_keypair()
    # Bootstrap writes the hex with a trailing newline; .get must strip it.
    (tmp_path / "director.pub").write_text(pub_hex + "\n")
    reg = keys.PublicKeyRegistry(tmp_path)
    assert reg.get("director") == pub_hex


def test_load_private_missing_raises_filenotfound(tmp_path, monkeypatch):
    monkeypatch.setenv("THREEWAY_KEYSTORE", str(tmp_path))
    with pytest.raises(FileNotFoundError):
        keys.load_private("operator")


def test_load_private_roundtrips_written_key(tmp_path, monkeypatch):
    monkeypatch.setenv("THREEWAY_KEYSTORE", str(tmp_path))
    priv, pub_hex = keys.generate_keypair()
    # Persist the private seed exactly as keys_bootstrap does (hex + newline).
    (tmp_path / "operator.ed25519").write_text(keys.private_to_hex(priv) + "\n")

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

    monkeypatch.setenv("THREEWAY_KEYSTORE", str(ks))
    priv = keys.load_private("director")
    pub_hex = keys.PublicKeyRegistry(reg).get("director")

    message = b"end-to-end: bootstrap -> keystore -> registry"
    sig = keys.sign(priv, message)
    assert keys.verify(pub_hex, sig, message) is None
