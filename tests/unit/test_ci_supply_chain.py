from __future__ import annotations

import re


CHECKOUT_SHA = "d23441a48e516b6c34aea4fa41551a30e30af803"
SETUP_PYTHON_SHA = "ece7cb06caefa5fff74198d8649806c4678c61a1"


def _read(root: Path, name: str) -> str:
    return (root / ".github/workflows" / name).read_text(encoding="utf-8")


def test_actions_are_pinned_and_permissions_are_read_only(repo_root) -> None:
    workflows = _read(repo_root, "ci.yml") + _read(repo_root, "admission.yml")
    assert f"actions/checkout@{CHECKOUT_SHA}" in workflows
    assert f"actions/setup-python@{SETUP_PYTHON_SHA}" in workflows
    assert not re.search(r"uses:\s+[^\s]+@(?![0-9a-f]{40}\b)", workflows)
    assert "contents: write" not in workflows
    assert "persist-credentials: true" not in workflows


def test_ci_produces_every_protected_context_without_advisory_greenwashing(
    repo_root,
) -> None:
    workflow = _read(repo_root, "ci.yml")
    assert workflow.count("runs-on:") == 2
    assert "continue-on-error" not in workflow
    assert "|| true" not in workflow
    assert "name: ci_smoke (governance gates + runtime invariants)" in workflow
    assert "name: pytest tests (Python ${{ matrix.python-version }})" in workflow
    assert "python-version: ['3.11', '3.12', '3.13']" in workflow
    assert "bin/pipeline check --fast" in workflow
    assert "python -m pytest tests --tb=short -q" in workflow


def test_ci_installs_only_hash_locked_test_dependencies(repo_root) -> None:
    workflow = _read(repo_root, "ci.yml")
    assert "pip install --require-hashes -r requirements-dev.txt" in workflow
    requirements = (repo_root / "requirements-dev.txt").read_text(encoding="utf-8")
    assert "--hash=sha256:" in requirements


def test_trusted_admission_never_executes_candidate_code(repo_root) -> None:
    workflow = _read(repo_root, "admission.yml")
    assert "pull_request_target:" in workflow
    assert "path: trusted" in workflow and "path: candidate" in workflow
    assert "python trusted/pipeline/ci_admission_gate.py" in workflow
    assert "python candidate/" not in workflow
    assert "pip install" not in workflow
