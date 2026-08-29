"""Supply-chain invariants for the candidate and trusted GitHub workflows."""
from __future__ import annotations

import os
import re
import subprocess
import sys
from pathlib import Path


CHECKOUT_SHA = "d23441a48e516b6c34aea4fa41551a30e30af803"
SETUP_PYTHON_SHA = "ece7cb06caefa5fff74198d8649806c4678c61a1"


def _workflow(repo_root: Path) -> str:
    return (repo_root / ".github/workflows/ci.yml").read_text(encoding="utf-8")


def _admission_workflow(repo_root: Path) -> str:
    return (repo_root / ".github/workflows/admission.yml").read_text(encoding="utf-8")


def _all_workflows(repo_root: Path) -> dict[str, str]:
    workflow_dir = repo_root / ".github/workflows"
    return {
        path.name: path.read_text(encoding="utf-8")
        for pattern in ("*.yml", "*.yaml")
        for path in workflow_dir.glob(pattern)
    }


def _job(workflow: str, name: str, next_name: str | None) -> str:
    start = workflow.index(f"  {name}:\n")
    end = workflow.index(f"  {next_name}:\n", start) if next_name else len(workflow)
    return workflow[start:end]


def test_actions_are_full_sha_pinned_with_version_annotations(repo_root):
    workflow = _workflow(repo_root)
    admission_workflow = _admission_workflow(repo_root)
    uses = re.findall(
        r"^\s*(?:-\s+)?uses:\s*([^\s#]+)(?:\s+#\s*(\S+))?$",
        workflow + admission_workflow,
        re.MULTILINE,
    )
    # 6 checkout / 5 setup-python across smoke, pytest, pytest-linux-hermetic,
    # lint-advisory, and admission-gate (which checks out twice). The two
    # advisory jobs (Linux hermeticity leg + non-gating lint) reuse the same
    # pinned SHAs.
    assert uses.count((f"actions/checkout@{CHECKOUT_SHA}", "v6.1.0")) == 6
    assert uses.count((f"actions/setup-python@{SETUP_PYTHON_SHA}", "v6.3.0")) == 5
    assert len(uses) == 11


def test_workflow_permissions_and_checkout_credentials_are_minimal(repo_root):
    workflow = _workflow(repo_root)
    admission_workflow = _admission_workflow(repo_root)
    assert re.search(r"^permissions:\n  contents: read$", workflow, re.MULTILINE)
    assert re.search(
        r"^permissions:\n  contents: read$", admission_workflow, re.MULTILINE
    )

    smoke = _job(workflow, "smoke", "pytest")
    pytest_job = _job(workflow, "pytest", "pytest-linux-hermetic")
    admission = _job(admission_workflow, "admission-gate", None)
    for job in (smoke, pytest_job, admission):
        assert "persist-credentials: false" in job
        assert "contents: write" not in job
    # No job in this desktop-app harness writes to the repository from CI.
    assert "contents: write" not in workflow + admission_workflow
    assert "persist-credentials: true" not in workflow + admission_workflow


def test_python_matrix_and_job_versions_are_explicit(repo_root):
    workflow = _workflow(repo_root)
    smoke = _job(workflow, "smoke", "pytest")
    pytest_job = _job(workflow, "pytest", "pytest-linux-hermetic")
    assert "python-version: '3.13'" in smoke
    assert re.search(
        r"matrix:\n\s+python-version: \['3\.11', '3\.12', '3\.13'\]",
        pytest_job,
    )
    assert "python-version: ${{ matrix.python-version }}" in pytest_job


def test_ci_installs_hash_locked_dependencies_only(repo_root):
    workflow = _workflow(repo_root)
    admission_workflow = _admission_workflow(repo_root)
    smoke = _job(workflow, "smoke", "pytest")
    pytest_job = _job(workflow, "pytest", "pytest-linux-hermetic")
    admission = _job(admission_workflow, "admission-gate", None)
    for job in (smoke, pytest_job):
        assert "pip install --require-hashes -r requirements-dev.txt" in job
        assert "cache-dependency-path: requirements-dev.txt" in job
    # The admission gate is stdlib-only by design: no dependency install
    # means no third-party code runs before the authority-surface check.
    assert "pip install" not in admission


def test_admission_uses_trusted_base_code_and_never_executes_candidate(repo_root):
    workflow = _workflow(repo_root)
    admission_workflow = _admission_workflow(repo_root)
    admission = _job(admission_workflow, "admission-gate", None)

    assert "  pull_request_target:\n" in admission_workflow
    assert "  pull_request:\n" not in admission_workflow
    assert "  pull_request_target:\n" not in workflow
    assert "  admission-gate:\n" not in workflow
    admission_names = re.findall(r"^    name: (.+)$", admission, re.MULTILINE)
    assert admission_names == [
        "risk-aware admission (authority surfaces; pull_request_target)"
    ]
    assert "if:" not in admission
    assert "path: trusted" in admission
    assert "path: candidate" in admission
    assert "test \"$(git -C candidate rev-parse HEAD)\" = \"$HEAD_SHA\"" in admission
    assert "python trusted/pipeline/ci_admission_gate.py --root trusted" in admission
    assert "python candidate/" not in admission
    assert "persist-credentials: true" not in admission


def test_trusted_admission_context_exists_in_exactly_one_workflow(repo_root):
    trusted_context = "risk-aware admission (authority surfaces; pull_request_target)"
    occurrences = {
        name: text.count(trusted_context)
        for name, text in _all_workflows(repo_root).items()
        if trusted_context in text
    }

    assert occurrences == {"admission.yml": 1}


def test_pr_and_trusted_admission_runs_cannot_cancel_each_other(repo_root):
    workflow = _workflow(repo_root)
    admission_workflow = _admission_workflow(repo_root)

    assert (
        "group: ${{ github.workflow }}-${{ github.event_name }}-"
        "${{ github.event.pull_request.number || github.ref }}"
    ) in workflow
    assert (
        "group: ${{ github.workflow }}-${{ github.event.pull_request.number }}"
    ) in admission_workflow


def test_pytest_job_runs_the_complete_declared_test_root(repo_root):
    """Integration contracts must not disappear behind a unit-only CI command."""

    workflow = _workflow(repo_root)
    pytest_job = _job(workflow, "pytest", "pytest-linux-hermetic")

    assert "python -m pytest tests --tb=short -q" in pytest_job
    assert "python -m pytest tests/unit" not in pytest_job
    assert "PIPELINE_REQUIRE_EXECUTED_TEST: '1'" in pytest_job


def test_ci_execution_guard_rejects_an_all_skipped_suite(
    tmp_path: Path, repo_root: Path
) -> None:
    test_file = tmp_path / "test_only_skip.py"
    test_file.write_text(
        "import pytest\n"
        "@pytest.mark.skip(reason='control')\n"
        "def test_never_executes():\n"
        "    assert True\n",
        encoding="utf-8",
    )
    env = os.environ.copy()
    env.pop("GIT_INDEX_FILE", None)
    env["PIPELINE_REQUIRE_EXECUTED_TEST"] = "1"
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "pytest",
            "-q",
            "-p",
            "tests.conftest",
            "-p",
            "no:cacheprovider",
            str(test_file),
        ],
        cwd=repo_root,
        env=env,
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode != 0, result.stdout + result.stderr


def test_requirement_inputs_and_locks_are_pinned_and_hash_locked(repo_root):
    expected_inputs = {
        "requirements-dev.in": {"pytest==9.1.1", "hypothesis==6.165.0"},
    }
    for name, expected in expected_inputs.items():
        lines = {
            line.strip()
            for line in (repo_root / name).read_text(encoding="utf-8").splitlines()
            if line.strip() and not line.startswith("#")
        }
        assert lines == expected

    for name in ("requirements-dev.txt",):
        body = (repo_root / name).read_text(encoding="utf-8")
        assert "pip-compile 7.6.0" in body
        assert "--generate-hashes" in body
        assert "--hash=sha256:" in body
        requirement_lines = [line for line in body.splitlines() if line and not line[0].isspace()]
        assert all(
            line.startswith(("#", "--", "-r ")) or "==" in line
            for line in requirement_lines
        )
