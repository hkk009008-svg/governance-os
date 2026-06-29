"""Shared fixtures for the governance-OS unit suite.

Root-module importability (``import threeway``, ``import scripts.X``) comes from
``[tool.pytest.ini_options] pythonpath = ["."]`` in pyproject.toml, so test
modules can import the packages directly without a sys.path shim.
"""
from __future__ import annotations

from pathlib import Path

import pytest


@pytest.fixture
def repo_root() -> Path:
    """Absolute path to the repository root (parent of tests/)."""
    return Path(__file__).resolve().parent.parent


@pytest.fixture
def signer_keypair():
    """A fresh Ed25519 keypair as (private_key, public_key_hex)."""
    from threeway import keys
    return keys.generate_keypair()
