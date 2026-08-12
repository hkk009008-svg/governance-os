"""Shared fixtures for the governance-OS unit suite.

Root-module importability (``import threeway``, ``import scripts.X``) comes from
``[tool.pytest.ini_options] pythonpath = ["."]`` in pyproject.toml, so test
modules can import the packages directly without a sys.path shim.
"""
from __future__ import annotations

import os
from pathlib import Path

import pytest


_executed_call_reports = 0


def pytest_configure(config) -> None:
    global _executed_call_reports
    _executed_call_reports = 0


def pytest_runtest_logreport(report) -> None:
    global _executed_call_reports
    if report.when == "call" and not report.skipped:
        _executed_call_reports += 1


def pytest_sessionfinish(session, exitstatus) -> None:
    """CI must not accept a collected suite in which every test was skipped."""

    if (
        os.environ.get("PIPELINE_REQUIRE_EXECUTED_TEST") == "1"
        and int(session.exitstatus) == 0
        and _executed_call_reports == 0
    ):
        session.exitstatus = pytest.ExitCode.TESTS_FAILED


@pytest.fixture
def repo_root() -> Path:
    """Absolute path to the repository root (parent of tests/)."""
    return Path(__file__).resolve().parent.parent


@pytest.fixture
def signer_keypair():
    """A fresh Ed25519 keypair as (private_key, public_key_hex)."""
    from threeway import keys
    return keys.generate_keypair()
