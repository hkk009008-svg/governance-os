"""Behavioral tests for the risk-aware admission gate.

Each scenario builds a throwaway repository, lands commits on and off the
authority surfaces, and asserts what the gate admits. The gate must delegate
report validity to the canonical compact_pair_loop machinery, so one scenario
proves a same-family high-risk reviewer is rejected by that delegation.
"""

from __future__ import annotations

import subprocess
from pathlib import Path

import pytest

import ci_admission_gate as gate
import protocol_mailbox
from mailbox_admission_test_support import event


REQUEST_PATH = (
    "coordination/mailbox/sent/"
    "2026-08-07T12-00-00Z-author-to-reviewer-verify-request.md"
)
REPORT_PATH = (
    "coordination/mailbox/sent/"
    "2026-08-07T12-10-00Z-reviewer-to-author-verification-report.md"
)
EVIDENCE_PATH = (
    "coordination/mailbox/sent/"
    "2026-08-07T11-55-00Z-codex-to-claude-findings.md"
)

SURFACE_PROBES = {
    ".agents/plugins/": ".agents/plugins/pipeline-team/mcp_config.json",
    ".agents/skills/": ".agents/skills/four-seat-protocol/SKILL.md",
    ".claude/agents/": ".claude/agents/readiness-bridge.md",
    ".claude/settings.json": ".claude/settings.json",
    ".claude/skills/": ".claude/skills/four-seat-protocol/SKILL.md",
    ".codex/agents/": ".codex/agents/protocol-operator.toml",
    ".codex/config.toml": ".codex/config.toml",
    ".mcp.json": ".mcp.json",
    ".github/workflows/": ".github/workflows/ci.yml",
    "config/": "config/model-families.toml",
    ":(glob)tests/**/conftest.py": "tests/conftest.py",
    "AGENTS.md": "AGENTS.md",
    "ARCHITECTURE.md": "ARCHITECTURE.md",
    "bin/pipeline": "bin/pipeline",
    "CLAUDE.md": "CLAUDE.md",
    "OPERATIONS.md": "OPERATIONS.md",
    "README.md": "README.md",
    "RUNBOOK-DAILY.md": "RUNBOOK-DAILY.md",
    "conftest.py": "conftest.py",
    "coordination/bin/": "coordination/bin/send-event",
    "coordination/mailbox/kinds.txt": "coordination/mailbox/kinds.txt",
    "docs/PROGRAM-MANUAL.md": "docs/PROGRAM-MANUAL.md",
    "docs/REMEDIATION-INVENTORY.md": "docs/REMEDIATION-INVENTORY.md",
    "docs/protocol/": "docs/protocol/agents/core.md",
    "governance.toml": "governance.toml",
    "pyproject.toml": "pyproject.toml",
    "pytest.ini": "pytest.ini",
    "requirements-dev.txt": "requirements-dev.txt",
    "pipeline/": "pipeline/ci_admission_gate.py",
    "setup.cfg": "setup.cfg",
    "sitecustomize.py": "sitecustomize.py",
    "tests/unit/test_provider_surface_map.py": "tests/unit/test_provider_surface_map.py",
    "tox.ini": "tox.ini",
    "usercustomize.py": "usercustomize.py",
}

REQUIRED_ACTIVE_AUTHORITY_SURFACES = frozenset(
    {
        ".agents/plugins/",
        ".agents/skills/",
        ".github/workflows/",
        ":(glob)tests/**/conftest.py",
        ".mcp.json",
        "AGENTS.md",
        "ARCHITECTURE.md",
        "bin/pipeline",
        "CLAUDE.md",
        "OPERATIONS.md",
        "RUNBOOK-DAILY.md",
        "conftest.py",
        "coordination/bin/",
        "docs/PROGRAM-MANUAL.md",
        "docs/protocol/",
        "governance.toml",
        "pipeline/",
        "sitecustomize.py",
        "tests/unit/test_provider_surface_map.py",
    }
)

OPTIONAL_ROOT_CONTROL_SURFACES = frozenset(
    {"conftest.py", "pytest.ini", "setup.cfg", "sitecustomize.py", "tox.ini", "usercustomize.py"}
)


def _git(root: Path, *args: str) -> str:
    completed = subprocess.run(
        ["env", "-u", "GIT_INDEX_FILE", "git", *args],
        cwd=root,
        check=True,
        capture_output=True,
        text=True,
    )
    return completed.stdout.strip()


def _bullets(heading: str, values: tuple[str, ...]) -> str:
    body = "\n".join(f"- {value}" for value in values)
    return f"## {heading}\n\n{body}\n"


def _request_text(
    base: str,
    head: str,
    *,
    risk_class: str,
    finding_refs: tuple[str, ...],
) -> str:
    abuse = (
        ""
        if risk_class != "high-risk-control"
        else "\n"
        + _bullets(
            "Abuse Class Assessment",
            ("untrusted request fields cannot widen authority",),
        )
    )
    return f"""\
# Author → Reviewer: verify outcome

**When:** 2026-08-07T12:00:00Z · **From:** author (online)

Event type: verify-request
Reviewed head: {head}
Reviewed base: {base}
Author seat: author
Author model: gpt-5.6-sol
Assigned operator: reviewer
Risk class: {risk_class}

## Outcome

The committed change satisfies the routed maintenance outcome.

{abuse}
{_bullets("Finding Refs", finding_refs)}
Cursor at send: cursorless
"""


def _report_text(
    base: str,
    head: str,
    trigger: str,
    *,
    verdict: str,
    risk_class: str,
    reviewer_model: str,
    finding_refs: tuple[str, ...],
    disposition: str = "addressed",
) -> str:
    abuse_binding = (
        ""
        if risk_class != "high-risk-control"
        else "Abuse Class Assessment: bound-to-request\n"
    )
    dispositions = tuple(f"{ref}: {disposition}" for ref in finding_refs)
    return f"""\
# Reviewer → Author: outcome verification

**When:** 2026-08-07T12:10:00Z · **From:** reviewer (online)

Event type: verification-report
VERDICT: {verdict}
Verification request: {REQUEST_PATH}@{trigger}
Reviewed head: {head}
Reviewed base: {base}
Reviewer seat: reviewer
Reviewer model: {reviewer_model}
Risk class: {risk_class}
{abuse_binding}

{_bullets("Finding Refs", finding_refs)}
{_bullets("Finding Dispositions", dispositions)}

## Evidence

$ independent actual-diff inspection
→ reviewed range satisfies the outcome

## Findings

None.

Cursor at send: cursorless
"""


def _init_repo(tmp_path: Path) -> tuple[Path, str]:
    root = tmp_path / "repo"
    (root / "pipeline").mkdir(parents=True)
    (root / "pipeline/feature.py").write_text("VALUE = 1\n", encoding="utf-8")
    kinds = root / "coordination/mailbox/kinds.txt"
    kinds.parent.mkdir(parents=True)
    kinds.write_text(
        "\n".join(sorted(protocol_mailbox.KNOWN_KINDS)) + "\n",
        encoding="utf-8",
    )
    _git(root, "init", "-q")
    _git(root, "config", "user.name", "Admission Gate Test")
    _git(root, "config", "user.email", "admission-gate@example.invalid")
    _git(root, "config", "commit.gpgsign", "false")
    _git(root, "add", ".")
    _git(root, "commit", "-q", "-m", "chore: base")
    return root, _git(root, "rev-parse", "HEAD")


def _commit_file(root: Path, relative: str, content: str, message: str) -> str:
    target = root / relative
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(content, encoding="utf-8")
    _git(root, "add", relative)
    _git(root, "commit", "-q", "-m", message)
    return _git(root, "rev-parse", "HEAD")


def test_default_range_prefers_the_remote_integration_target(
    tmp_path: Path,
) -> None:
    root, stale_remote = _init_repo(tmp_path)
    _git(root, "branch", "-M", "main")
    _git(root, "update-ref", "refs/remotes/origin/main", stale_remote)
    local_main = _commit_file(root, "main.txt", "local main\n", "test: advance main")
    _git(root, "checkout", "-q", "-b", "topic")
    head = _commit_file(root, "topic.txt", "topic\n", "test: topic")

    assert local_main != stale_remote
    assert gate.resolve_range(root, None, None) == (stale_remote, head)


def _mint_evidence(root: Path) -> str:
    commit = _commit_file(
        root,
        EVIDENCE_PATH,
        "Event type: findings\nNo blocking findings.\n",
        "coord: cited evidence",
    )
    return f"{EVIDENCE_PATH}@{commit}"


def _land_pair(
    root: Path,
    reviewed_base: str,
    reviewed_head: str,
    *,
    verdict: str = "GO",
    risk_class: str = "high-risk-control",
    reviewer_model: str = "claude-opus-4-7",
    disposition: str = "addressed",
) -> None:
    refs = (_mint_evidence(root),)
    _commit_file(
        root,
        REQUEST_PATH,
        _request_text(
            reviewed_base, reviewed_head, risk_class=risk_class, finding_refs=refs
        ),
        "review: request verification",
    )
    trigger = _git(root, "rev-parse", "HEAD")
    _commit_file(
        root,
        REPORT_PATH,
        _report_text(
            reviewed_base,
            reviewed_head,
            trigger,
            verdict=verdict,
            risk_class=risk_class,
            reviewer_model=reviewer_model,
            finding_refs=refs,
            disposition=disposition,
        ),
        "review: publish verdict",
    )


def test_range_without_authority_surfaces_is_admitted(tmp_path: Path) -> None:
    root, base = _init_repo(tmp_path)
    _commit_file(root, "src/feature.py", "VALUE = 2\n", "feat: ordinary")
    head = _git(root, "rev-parse", "HEAD")

    outcome = gate.evaluate(root, base, head)

    assert outcome.admitted
    assert outcome.authority_commits == {}
    assert "admitted without review requirement" in gate.render(outcome)


def test_gate_wires_the_exact_frozen_forward_reader_route(
    monkeypatch, repo_root: Path
) -> None:
    path = (
        "coordination/mailbox/sent/"
        "2026-08-28T02-43-08Z-operator-to-director-verification-report.md"
    )
    raw = event(path).replace(b"Cursor at send: cursorless", b"Cursor at send: 0")
    commit, calls = "3" * 40, []
    monkeypatch.setattr(
        gate.mailbox_review_admission,
        "_is_exact_frozen_forward_reader_route",
        lambda *args: calls.append(args) or True,
    )
    gate._validate_current_envelope(
        repo_root, raw, path, protocol_mailbox.KNOWN_KINDS, commit
    )
    assert calls == [("verification-report", "operator", "director", path, commit, raw)]
    monkeypatch.setattr(
        gate.mailbox_review_admission,
        "_is_exact_frozen_forward_reader_route",
        lambda *_args: False,
    )
    with pytest.raises(gate.pair.CompactPairError, match="formal review role route"):
        gate._validate_current_envelope(
            repo_root, raw, path, protocol_mailbox.KNOWN_KINDS, commit
        )


def test_every_declared_trust_or_effect_surface_is_matched_non_vacuously(
    tmp_path: Path, repo_root: Path, monkeypatch
) -> None:
    assert len(gate.AUTHORITY_SURFACES) == len(set(gate.AUTHORITY_SURFACES))
    assert REQUIRED_ACTIVE_AUTHORITY_SURFACES <= set(gate.AUTHORITY_SURFACES)
    assert set(SURFACE_PROBES) == set(gate.AUTHORITY_SURFACES)
    assert len(SURFACE_PROBES) == len(set(SURFACE_PROBES.values()))
    assert OPTIONAL_ROOT_CONTROL_SURFACES <= set(SURFACE_PROBES)
    assert all(
        (repo_root / path).is_file()
        for surface, path in SURFACE_PROBES.items()
        if surface not in OPTIONAL_ROOT_CONTROL_SURFACES
    )
    root, base = _init_repo(tmp_path)
    for surface, path in sorted(SURFACE_PROBES.items()):
        head = _commit_file(root, path, f"probe: {surface}\n", f"probe: {surface}")
        monkeypatch.setattr(gate, "AUTHORITY_SURFACES", (surface,))

        commits = gate.authority_commits(root, base, head)

        assert commits == {head: (path,)}, surface
        base = head


def test_authority_commit_without_report_is_blocked(tmp_path: Path) -> None:
    root, base = _init_repo(tmp_path)
    touched = _commit_file(
        root, "pipeline/mailbox_writer.py", "POLICY = 1\n", "feat: writer policy"
    )
    head = _git(root, "rev-parse", "HEAD")

    outcome = gate.evaluate(root, base, head)

    assert not outcome.admitted
    assert touched in outcome.uncovered
    assert "pipeline/mailbox_writer.py" in outcome.uncovered[touched]
    assert "BLOCKED" in gate.render(outcome)


def test_new_script_cannot_shadow_the_gate_outside_admission(
    tmp_path: Path,
) -> None:
    root, base = _init_repo(tmp_path)
    touched = _commit_file(
        root,
        "pipeline/subprocess.py",
        "raise SystemExit('shadowed')\n",
        "test: add import shadow",
    )

    commits = gate.authority_commits(root, base, touched)

    assert commits == {touched: ("pipeline/subprocess.py",)}


def test_merge_resolution_only_authority_change_is_detected(
    tmp_path: Path,
) -> None:
    root, _ = _init_repo(tmp_path)
    base = _commit_file(
        root,
        "pipeline/mailbox_writer.py",
        "POLICY = 0\n",
        "test: establish protected policy",
    )
    main_branch = _git(root, "branch", "--show-current")
    _commit_file(root, "main.txt", "main\n", "test: main side")
    _git(root, "checkout", "-q", "-b", "side", base)
    _commit_file(root, "side.txt", "side\n", "test: topic side")
    _git(root, "checkout", "-q", main_branch)
    _git(root, "merge", "--no-ff", "--no-commit", "side")
    (root / "pipeline" / "mailbox_writer.py").write_text(
        "POLICY = 1\n", encoding="utf-8"
    )
    _git(root, "add", "pipeline/mailbox_writer.py")
    _git(root, "commit", "-q", "-m", "test: merge resolution changes policy")
    head = _git(root, "rev-parse", "HEAD")

    commits = gate.authority_commits(root, base, head)

    assert commits[head] == ("pipeline/mailbox_writer.py",)


def test_valid_high_risk_go_report_admits_range(tmp_path: Path) -> None:
    root, base = _init_repo(tmp_path)
    reviewed_head = _commit_file(
        root, "pipeline/mailbox_writer.py", "POLICY = 1\n", "feat: writer policy"
    )
    _land_pair(root, base, reviewed_head)
    head = _git(root, "rev-parse", "HEAD")

    outcome = gate.evaluate(root, base, head)

    assert outcome.admitted, gate.render(outcome)
    assert [coverage.verdict for coverage in outcome.coverages] == ["GO"]


def test_candidate_only_request_and_report_admit_while_checkout_stays_at_base(
    tmp_path: Path,
) -> None:
    """CI validates fetched candidate objects, not files in its checkout."""

    root, base = _init_repo(tmp_path)
    reviewed_head = _commit_file(
        root, "pipeline/mailbox_writer.py", "POLICY = 1\n", "feat: writer policy"
    )
    _land_pair(root, base, reviewed_head)
    candidate_head = _git(root, "rev-parse", "HEAD")

    _git(root, "checkout", "-q", "--detach", base)
    assert not (root / REQUEST_PATH).exists()
    assert not (root / REPORT_PATH).exists()

    outcome = gate.evaluate(root, base, candidate_head)

    assert outcome.admitted, gate.render(outcome)
    assert [coverage.verdict for coverage in outcome.coverages] == ["GO"]


def test_fail_verdict_does_not_admit(tmp_path: Path) -> None:
    root, base = _init_repo(tmp_path)
    reviewed_head = _commit_file(
        root, "pipeline/mailbox_writer.py", "WRITER = 1\n", "feat: writer"
    )
    _land_pair(root, base, reviewed_head, verdict="FAIL")
    head = _git(root, "rev-parse", "HEAD")

    outcome = gate.evaluate(root, base, head)

    assert not outcome.admitted
    assert any("FAIL" in reason for _, reason in outcome.skipped_reports)


def test_nits_with_unresolved_hard_boundary_does_not_admit(tmp_path: Path) -> None:
    root, base = _init_repo(tmp_path)
    reviewed_head = _commit_file(
        root, "pipeline/mailbox_writer.py", "WRITER = 1\n", "feat: writer"
    )
    _land_pair(
        root,
        base,
        reviewed_head,
        verdict="NITS",
        disposition="unresolved-hard-boundary",
    )
    head = _git(root, "rev-parse", "HEAD")

    outcome = gate.evaluate(root, base, head)

    assert not outcome.admitted
    assert any(
        "NITS cannot carry unresolved hard-boundary findings" in reason
        for _, reason in outcome.skipped_reports
    )


def test_new_retired_role_report_cannot_admit_a_range(tmp_path: Path) -> None:
    root, base = _init_repo(tmp_path)
    reviewed_head = _commit_file(
        root, "pipeline/mailbox_writer.py", "POLICY = 1\n", "feat: writer policy"
    )
    refs = (_mint_evidence(root),)
    legacy_request = REQUEST_PATH.replace("author-to-reviewer", "director-to-operator")
    legacy_report = REPORT_PATH.replace("reviewer-to-author", "operator-to-director")
    request_text = (
        _request_text(
            base, reviewed_head, risk_class="high-risk-control", finding_refs=refs
        )
        .replace("# Author → Reviewer", "# Director → Operator")
        .replace("**From:** author", "**From:** director")
        .replace("Author seat: author", "Author seat: director")
        .replace("Assigned operator: reviewer", "Assigned operator: operator")
        .replace("Cursor at send: cursorless", "Cursor at send: 0")
    )
    _commit_file(root, legacy_request, request_text, "review: legacy request")
    trigger = _git(root, "rev-parse", "HEAD")
    report_text = (
        _report_text(
            base,
            reviewed_head,
            trigger,
            verdict="GO",
            risk_class="high-risk-control",
            reviewer_model="claude-opus-4-6-thinking",
            finding_refs=refs,
        )
        .replace("# Reviewer → Author", "# Operator → Director")
        .replace("**From:** reviewer", "**From:** operator")
        .replace(f"Verification request: {REQUEST_PATH}@", f"Verification request: {legacy_request}@")
        .replace("Reviewer seat: reviewer", "Reviewer seat: operator")
        .replace("Cursor at send: cursorless", "Cursor at send: 0")
    )
    _commit_file(root, legacy_report, report_text, "review: legacy report")
    head = _git(root, "rev-parse", "HEAD")

    outcome = gate.evaluate(root, base, head)

    assert not outcome.admitted
    assert any(
        "formal review role route" in reason
        for _, reason in outcome.skipped_reports
    )


def test_legacy_request_and_current_report_cannot_cross_generations(
    tmp_path: Path,
) -> None:
    root, base = _init_repo(tmp_path)
    reviewed_head = _commit_file(
        root, "pipeline/mailbox_writer.py", "POLICY = 1\n", "feat: writer policy"
    )
    refs = (_mint_evidence(root),)
    legacy_request = REQUEST_PATH.replace("author-to-reviewer", "director-to-operator")
    request_text = (
        _request_text(
            base, reviewed_head, risk_class="high-risk-control", finding_refs=refs
        )
        .replace("# Author → Reviewer", "# Director → Operator")
        .replace("**From:** author", "**From:** director")
        .replace("Author seat: author", "Author seat: director")
        .replace("Assigned operator: reviewer", "Assigned operator: operator")
        .replace("Cursor at send: cursorless", "Cursor at send: 0")
    )
    _commit_file(root, legacy_request, request_text, "review: legacy request")
    trigger = _git(root, "rev-parse", "HEAD")
    report_text = _report_text(
        base,
        reviewed_head,
        trigger,
        verdict="GO",
        risk_class="high-risk-control",
        reviewer_model="claude-opus-4-6-thinking",
        finding_refs=refs,
    ).replace(
        f"Verification request: {REQUEST_PATH}@",
        f"Verification request: {legacy_request}@",
    )
    _commit_file(root, REPORT_PATH, report_text, "review: current report")
    head = _git(root, "rev-parse", "HEAD")

    outcome = gate.evaluate(root, base, head)

    assert not outcome.admitted
    assert any(
        "reviewer seat is not the assigned Operator" in reason
        for _, reason in outcome.skipped_reports
    )


def test_mode_only_pipeline_dispatcher_change_is_a_wired_authority_control(
    tmp_path: Path, monkeypatch,
) -> None:
    root, _ = _init_repo(tmp_path)
    base = _commit_file(root, "bin/pipeline", "#!/bin/sh\n", "test: add dispatcher")
    dispatcher = root / "bin/pipeline"
    dispatcher.chmod(0o755)
    _git(root, "add", "bin/pipeline")
    _git(root, "commit", "-q", "-m", "test: make dispatcher executable")
    head = _git(root, "rev-parse", "HEAD")

    outcome = gate.evaluate(root, base, head)
    assert not outcome.admitted
    assert outcome.authority_commits == {head: ("bin/pipeline",)}

    monkeypatch.setattr(
        gate,
        "AUTHORITY_SURFACES",
        tuple(item for item in gate.AUTHORITY_SURFACES if item != "bin/pipeline"),
    )
    reverted = gate.evaluate(root, base, head)
    assert reverted.admitted
    assert reverted.authority_commits == {}


def test_material_behavior_report_does_not_admit_authority_surface(
    tmp_path: Path,
) -> None:
    root, base = _init_repo(tmp_path)
    reviewed_head = _commit_file(
        root, "coordination/bin/send-event", "#!/bin/sh\n", "feat: writer shim"
    )
    _land_pair(
        root,
        base,
        reviewed_head,
        risk_class="material-behavior",
        reviewer_model="gpt-5.6-terra",
    )
    head = _git(root, "rev-parse", "HEAD")

    outcome = gate.evaluate(root, base, head)

    assert not outcome.admitted
    assert any(
        "require an explicit high-risk-control" in reason
        for _, reason in outcome.skipped_reports
    )


def test_same_family_high_risk_reviewer_is_rejected_by_canonical_validator(
    tmp_path: Path,
) -> None:
    root, base = _init_repo(tmp_path)
    reviewed_head = _commit_file(
        root, "pipeline/mailbox_writer.py", "POLICY = 1\n", "feat: writer policy"
    )
    _land_pair(root, base, reviewed_head, reviewer_model="gpt-5.6-terra")
    head = _git(root, "rev-parse", "HEAD")

    outcome = gate.evaluate(root, base, head)

    assert not outcome.admitted
    assert any(
        "model family" in reason for _, reason in outcome.skipped_reports
    )


def test_report_not_covering_the_authority_commit_does_not_admit(
    tmp_path: Path,
) -> None:
    root, base = _init_repo(tmp_path)
    reviewed_head = _commit_file(
        root, "pipeline/feature.py", "VALUE = 2\n", "feat: ordinary reviewed work"
    )
    _land_pair(root, base, reviewed_head)
    touched = _commit_file(
        root, "pipeline/mailbox_writer.py", "POLICY = 2\n", "feat: unreviewed policy"
    )
    head = _git(root, "rev-parse", "HEAD")

    outcome = gate.evaluate(root, base, head)

    assert not outcome.admitted
    assert touched in outcome.uncovered


def test_empty_range_and_cli_exit_codes(tmp_path: Path) -> None:
    root, base = _init_repo(tmp_path)
    _commit_file(root, "pipeline/mailbox_writer.py", "POLICY = 1\n", "feat: policy")
    head = _git(root, "rev-parse", "HEAD")

    assert gate.main(["--root", str(root), "--base", head, "--head", head]) == 0
    assert gate.main(["--root", str(root), "--base", base, "--head", head]) == 1
