"""Supply-chain invariants for the only GitHub Actions workflow."""
from __future__ import annotations

import re
from pathlib import Path


CHECKOUT_SHA = "d23441a48e516b6c34aea4fa41551a30e30af803"
SETUP_PYTHON_SHA = "ece7cb06caefa5fff74198d8649806c4678c61a1"


def _workflow(repo_root: Path) -> str:
    return (repo_root / ".github/workflows/ci.yml").read_text(encoding="utf-8")


def _job(workflow: str, name: str, next_name: str | None) -> str:
    start = workflow.index(f"  {name}:\n")
    end = workflow.index(f"  {next_name}:\n", start) if next_name else len(workflow)
    return workflow[start:end]


def test_actions_are_full_sha_pinned_with_version_annotations(repo_root):
    workflow = _workflow(repo_root)
    uses = re.findall(r"^\s*- uses:\s*([^\s#]+)(?:\s+#\s*(\S+))?$", workflow, re.MULTILINE)
    assert uses == [
        (f"actions/checkout@{CHECKOUT_SHA}", "v6.1.0"),
        (f"actions/setup-python@{SETUP_PYTHON_SHA}", "v6.3.0"),
    ] * 3


def test_workflow_permissions_and_checkout_credentials_are_minimal(repo_root):
    workflow = _workflow(repo_root)
    assert re.search(r"^permissions:\n  contents: read$", workflow, re.MULTILINE)

    smoke = _job(workflow, "smoke", "pytest-unit")
    pytest_job = _job(workflow, "pytest-unit", "threeway-ci-result")
    signer = _job(workflow, "threeway-ci-result", None)
    for job in (smoke, pytest_job):
        assert "persist-credentials: false" in job
        assert "contents: write" not in job
    assert "permissions:\n      contents: write" in signer
    assert "persist-credentials: true" in signer


def test_python_matrix_and_job_versions_are_explicit(repo_root):
    workflow = _workflow(repo_root)
    smoke = _job(workflow, "smoke", "pytest-unit")
    pytest_job = _job(workflow, "pytest-unit", "threeway-ci-result")
    signer = _job(workflow, "threeway-ci-result", None)
    assert "python-version: '3.13'" in smoke
    assert re.search(
        r"matrix:\n\s+python-version: \['3\.11', '3\.12', '3\.13'\]",
        pytest_job,
    )
    assert "python-version: ${{ matrix.python-version }}" in pytest_job
    assert "python-version: '3.13'" in signer


def test_ci_installs_hash_locked_and_signer_uses_minimal_lock(repo_root):
    workflow = _workflow(repo_root)
    smoke = _job(workflow, "smoke", "pytest-unit")
    pytest_job = _job(workflow, "pytest-unit", "threeway-ci-result")
    signer = _job(workflow, "threeway-ci-result", None)
    for job in (smoke, pytest_job):
        assert "pip install --require-hashes -r requirements-dev.txt" in job
        assert "cache-dependency-path: requirements-dev.txt" in job
    assert "pip install --require-hashes -r requirements-governance.txt" in signer
    assert "cache-dependency-path: requirements-governance.txt" in signer
    assert "requirements-dev.txt" not in signer


def test_requirement_inputs_and_locks_are_pinned_and_hash_locked(repo_root):
    expected_inputs = {
        "requirements-governance.in": {"cryptography==50.0.0", "rfc8785==0.1.4"},
        "requirements-dev.in": {
            "-r requirements-governance.in",
            "pytest==9.1.1",
            "hypothesis==6.165.0",
        },
    }
    for name, expected in expected_inputs.items():
        lines = {
            line.strip()
            for line in (repo_root / name).read_text(encoding="utf-8").splitlines()
            if line.strip() and not line.startswith("#")
        }
        assert lines == expected

    for name in ("requirements-governance.txt", "requirements-dev.txt"):
        body = (repo_root / name).read_text(encoding="utf-8")
        assert "pip-compile 7.6.0" in body
        assert "--generate-hashes" in body
        assert "--hash=sha256:" in body
        requirement_lines = [line for line in body.splitlines() if line and not line[0].isspace()]
        assert all(
            line.startswith(("#", "--", "-r ")) or "==" in line
            for line in requirement_lines
        )


def test_signer_hardens_private_key_permissions_cross_platform(repo_root):
    signer = _job(_workflow(repo_root), "threeway-ci-result", None)
    assert "umask 077" in signer
    assert 'chmod 700 "$THREEWAY_KEYSTORE"' in signer
    assert 'chmod 600 "$THREEWAY_KEYSTORE/ci.ed25519"' in signer
    assert 'case "$(uname -s)"' in signer
    assert "Darwin)" in signer and "Linux)" in signer
    assert "stat -f '%Lp'" in signer
    assert "stat -c '%a'" in signer
    assert 'test "$KEY_MODE" = "600"' in signer
