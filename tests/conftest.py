"""Shared fixtures for the governance-OS unit suite.

Importability (flat ``import <pipeline-module>``) comes from
``[tool.pytest.ini_options] pythonpath = [".", "pipeline"]`` in pyproject.toml,
so test modules import directly without sys.path shims.
Flat form is the one convention for pipeline/ modules — see
tests/unit/test_import_identity.py.
"""
from __future__ import annotations

import os
from pathlib import Path

import pytest


_executed_call_reports = 0


@pytest.fixture(autouse=True, scope="session")
def git_ceiling_protects_enclosing_repository(
    tmp_path_factory: pytest.TempPathFactory,
) -> None:
    """Keep test git subprocesses from discovering the surrounding repository.

    Scratch directories (``tmp_path``) may live inside a real checkout — this
    repo's own convention is an in-worktree ``.pytest-verify-tmp/``. Without a
    ceiling, git invoked in a non-repository scratch directory walks up, finds
    the enclosing Pipeline checkout, and confidently reports (or worse, could
    mutate) *its* state, so "this path is not a repository" tests fail.
    Mirror git's own test-lib: pin GIT_CEILING_DIRECTORIES to the scratch
    base temporary directory for the whole session. Repositories the tests
    create inside their own tmp_path stay fully functional because discovery
    below the ceiling is unaffected.
    """

    basetemp = str(tmp_path_factory.getbasetemp().resolve())
    existing = os.environ.get("GIT_CEILING_DIRECTORIES")
    os.environ["GIT_CEILING_DIRECTORIES"] = (
        f"{basetemp}:{existing}" if existing else basetemp
    )
    global _executed_call_reports
    _executed_call_reports = 0


def pytest_runtest_logreport(report) -> None:
    global _executed_call_reports
    if report.when == "call" and not report.skipped:
        _executed_call_reports += 1


def pytest_sessionfinish(session, exitstatus) -> None:
    """CI and local full checks must execute a test, not merely collect skips."""

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
