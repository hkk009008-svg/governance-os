"""Tests for the executable Wave gate inventory contract."""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest

import wave_gate_check


ROOT = Path(__file__).resolve().parents[2]


def test_default_wave2_inventory_exists_for_gate():
    """The default Wave 2 gate must not fail from a missing inventory file."""
    proc = subprocess.run(
        [sys.executable, "scripts/wave_gate_check.py", "2"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )

    combined = f"{proc.stdout}\n{proc.stderr}"
    assert proc.returncode != 2
    assert "inventory not found" not in combined


def test_wave_with_no_inventory_rows_is_unmet(tmp_path: Path) -> None:
    inventory = tmp_path / "inventory.md"
    inventory.write_text(
        "| id | subsystem | file:line | severity | priority | fail-mode | repro | "
        "xfail-pin | lane-owner | shared-lock | wave | status | verifier | notes |\n"
        "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|\n",
        encoding="utf-8",
    )

    report = wave_gate_check.gate_report(inventory, 2, product_oracle_paths=[])

    assert report["verdict"] == "UNMET"
    assert report["counts"] == {}
    assert report["blockers"][0]["block_reason"] == "wave has no inventory rows"


def test_ordinary_passing_test_cannot_impersonate_strict_xfail_pin(
    tmp_path: Path, monkeypatch
) -> None:
    tests = tmp_path / "tests"
    tests.mkdir()
    (tests / "test_false_green.py").write_text(
        "def test_ordinary_pass():\n    assert True\n", encoding="utf-8"
    )
    inventory = tmp_path / "inventory.md"
    inventory.write_text(
        "| id | subsystem | file:line | severity | priority | fail-mode | repro | "
        "xfail-pin | lane-owner | shared-lock | wave | status | verifier | notes |\n"
        "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|\n"
        "| P1 | gate | scripts/wave_gate_check.py | MAJOR | P1 | false green | "
        "control | tests/test_false_green.py::test_ordinary_pass | local | none | "
        "1 | done | local | ordinary pass must not clear gate |\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(wave_gate_check, "_REPO_ROOT", tmp_path)

    report = wave_gate_check.gate_report(
        inventory, 1, product_oracle_paths=[], runner=lambda _: pytest.fail("must not run")
    )

    assert report["verdict"] == "UNMET"
    assert report["selectors"] == []
    assert "not decorated" in report["blockers"][0]["block_reason"]


def test_disabled_xfail_marker_cannot_clear_wave_gate(
    tmp_path: Path, monkeypatch
) -> None:
    tests = tmp_path / "tests"
    tests.mkdir()
    (tests / "test_disabled_pin.py").write_text(
        "import pytest\n"
        "@pytest.mark.xfail(False, strict=True, reason='disabled')\n"
        "def test_disabled_pin():\n"
        "    assert True\n",
        encoding="utf-8",
    )
    inventory = tmp_path / "inventory.md"
    inventory.write_text(
        "| id | subsystem | file:line | severity | priority | fail-mode | repro | "
        "xfail-pin | lane-owner | shared-lock | wave | status | verifier | notes |\n"
        "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|\n"
        "| P1 | gate | scripts/wave_gate_check.py | MAJOR | P1 | false green | "
        "control | tests/test_disabled_pin.py::test_disabled_pin | local | none | "
        "1 | done | local | disabled marker must not clear gate |\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(wave_gate_check, "_REPO_ROOT", tmp_path)

    report = wave_gate_check.gate_report(inventory, 1, product_oracle_paths=[])

    assert report["verdict"] == "UNMET"
    assert report["selectors"] == []
    assert "condition must be absent" in report["blockers"][0]["block_reason"]


@pytest.mark.parametrize(
    "module_body",
    (
        "class FakeMark:\n"
        "    def xfail(self, **_kwargs):\n"
        "        return lambda function: function\n"
        "class FakePytest:\n"
        "    mark = FakeMark()\n"
        "pytest = FakePytest()\n"
        "@pytest.mark.xfail(strict=True, reason='fake')\n"
        "def test_pin():\n"
        "    assert True\n",
        "import pytest\n"
        "@pytest.mark.skip(reason='disabled')\n"
        "@pytest.mark.xfail(strict=True, reason='pin')\n"
        "def test_pin():\n"
        "    assert True\n",
        "import pytest\n"
        "@pytest.fixture(autouse=True)\n"
        "def stop_before_call():\n"
        "    pytest.skip('disabled in setup')\n"
        "@pytest.mark.xfail(strict=True, reason='pin')\n"
        "def test_pin():\n"
        "    assert True\n",
    ),
)
def test_runtime_marker_or_skip_evasion_cannot_clear_wave_gate(
    tmp_path: Path, monkeypatch, module_body: str
) -> None:
    tests = tmp_path / "tests"
    tests.mkdir()
    (tests / "test_runtime_pin.py").write_text(module_body, encoding="utf-8")
    inventory = tmp_path / "inventory.md"
    inventory.write_text(
        "| id | subsystem | file:line | severity | priority | fail-mode | repro | "
        "xfail-pin | lane-owner | shared-lock | wave | status | verifier | notes |\n"
        "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|\n"
        "| P1 | gate | scripts/wave_gate_check.py | MAJOR | P1 | false green | "
        "control | tests/test_runtime_pin.py::test_pin | local | none | "
        "1 | done | local | runtime control |\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(wave_gate_check, "_REPO_ROOT", tmp_path)

    report = wave_gate_check.gate_report(inventory, 1, product_oracle_paths=[])

    assert report["verdict"] == "UNMET"
    assert report["pytest_blocking"] is True
    assert report["pytest"]["exit_code"] != 0
