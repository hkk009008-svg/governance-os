"""Exercise local full-check exit status with real, isolated pytest runs."""
from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

import governance_verify_all as verifier


_SKIPPED = "import pytest\n@pytest.mark.skip(reason='control')\ndef test_skip(): pass\n"


@pytest.fixture
def isolated_suite(tmp_path: Path, repo_root: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    suite = tmp_path / "suite"
    suite.mkdir()
    shutil.copyfile(repo_root / "tests/conftest.py", suite / "conftest.py")
    (suite / "pytest.ini").write_text("[pytest]\n", encoding="utf-8")
    for key in ("PIPELINE_REQUIRE_EXECUTED_TEST", "PYTEST_ADDOPTS", "PYTEST_PLUGINS", "GIT_INDEX_FILE"):
        monkeypatch.delenv(key, raising=False)
    monkeypatch.setenv("PYTEST_DISABLE_PLUGIN_AUTOLOAD", "1")
    monkeypatch.setattr(verifier, "ROOT", suite)
    # These controls isolate the real full-check pytest invocation, not native
    # app configuration or unrelated repository mailbox contents.
    monkeypatch.setattr(verifier, "_project_smoke", lambda: 0)
    monkeypatch.setattr(verifier, "_coordination_check", lambda: 0)
    return suite


@pytest.mark.parametrize("inherited_guard", (None, "0", "1"))
def test_full_check_rejects_all_skipped_even_without_inherited_guard(
    isolated_suite: Path, monkeypatch: pytest.MonkeyPatch, capfd, inherited_guard: str | None,
) -> None:
    if inherited_guard is not None:
        monkeypatch.setenv("PIPELINE_REQUIRE_EXECUTED_TEST", inherited_guard)
    (isolated_suite / "test_control.py").write_text(_SKIPPED, encoding="utf-8")

    assert verifier.main([]) == pytest.ExitCode.TESTS_FAILED
    output = capfd.readouterr().out
    assert "1 skipped" in output
    assert "FULL CHECK — PASS" not in output


@pytest.mark.parametrize("source,expected_exit,summary", (
    ("def test_pass(): assert True\n", pytest.ExitCode.OK, "1 passed"),
    ("", pytest.ExitCode.NO_TESTS_COLLECTED, "no tests ran"),
    (
        "import pytest\n@pytest.fixture(autouse=True)\ndef bad_setup(): raise RuntimeError('setup control')\n"
        "def test_unreached(): pass\n",
        pytest.ExitCode.TESTS_FAILED, "1 error",
    ),
))
def test_full_check_preserves_real_pass_empty_and_setup_failure(
    isolated_suite: Path, capfd, source: str, expected_exit: pytest.ExitCode, summary: str,
) -> None:
    (isolated_suite / "test_control.py").write_text(source, encoding="utf-8")
    assert verifier.main([]) == expected_exit
    output = capfd.readouterr().out
    assert summary in output
    assert ("FULL CHECK — PASS" in output) is (expected_exit == pytest.ExitCode.OK)


def test_full_check_cannot_disable_execution_guard_with_pytest_addopts(
    isolated_suite: Path, monkeypatch: pytest.MonkeyPatch, capfd,
) -> None:
    (isolated_suite / "test_control.py").write_text(_SKIPPED, encoding="utf-8")
    monkeypatch.setenv("PYTEST_ADDOPTS", "--noconftest")
    assert verifier.main([]) == pytest.ExitCode.TESTS_FAILED
    output = capfd.readouterr().out
    assert "1 skipped" in output
    assert "FULL CHECK — PASS" not in output


def test_full_check_cannot_override_result_with_injected_pytest_plugin(
    isolated_suite: Path, monkeypatch: pytest.MonkeyPatch, capfd,
) -> None:
    (isolated_suite / "test_control.py").write_text(_SKIPPED, encoding="utf-8")
    (isolated_suite / "force_success.py").write_text(
        "import pytest\n@pytest.hookimpl(trylast=True)\n"
        "def pytest_sessionfinish(session, exitstatus): session.exitstatus = pytest.ExitCode.OK\n",
        encoding="utf-8",
    )
    monkeypatch.setenv("PYTHONPATH", str(isolated_suite))
    monkeypatch.setenv("PYTEST_PLUGINS", "force_success")
    assert verifier.main([]) == pytest.ExitCode.TESTS_FAILED
    output = capfd.readouterr().out
    assert "1 skipped" in output
    assert "FULL CHECK — PASS" not in output


@pytest.mark.parametrize("guard_enabled", (False, True))
def test_execution_guard_is_nonvacuous_on_real_skipped_suite(
    isolated_suite: Path, guard_enabled: bool,
) -> None:
    (isolated_suite / "test_control.py").write_text(_SKIPPED, encoding="utf-8")
    environment = os.environ.copy()
    if guard_enabled:
        environment["PIPELINE_REQUIRE_EXECUTED_TEST"] = "1"
    result = subprocess.run(
        [sys.executable, "-m", "pytest", "-q"], cwd=isolated_suite,
        env=environment, capture_output=True, text=True, check=False, timeout=20,
    )
    assert result.returncode == (pytest.ExitCode.TESTS_FAILED if guard_enabled else pytest.ExitCode.OK)
    assert "1 skipped" in result.stdout
    assert "ERROR" not in result.stdout + result.stderr
