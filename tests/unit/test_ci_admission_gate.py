"""Behavioral tests for the risk-aware admission gate.

Each scenario builds a throwaway repository, lands commits on and off the
authority surfaces, and asserts what the gate admits. The gate must delegate
report validity to the canonical compact_pair_loop machinery, so one scenario
proves a same-family high-risk reviewer is rejected by that delegation.
"""

from __future__ import annotations

import subprocess
from pathlib import Path
from types import SimpleNamespace

import pytest

import ci_admission_gate as gate
import protocol_mailbox
from mailbox_admission_test_support import event


REQUEST_PATH = (
    "coordination/mailbox/sent/"
    "2026-08-07T12-00-00Z-codex-to-claude-verify-request.md"
)
REPORT_PATH = (
    "coordination/mailbox/sent/"
    "2026-08-07T12-10-00Z-claude-to-codex-verification-report.md"
)
SECOND_REQUEST_PATH = (
    "coordination/mailbox/sent/"
    "2026-08-07T12-20-00Z-codex-to-claude-verify-request.md"
)
SECOND_REPORT_PATH = (
    "coordination/mailbox/sent/"
    "2026-08-07T12-30-00Z-claude-to-codex-verification-report.md"
)
MEMBER_REQUEST_PATH = REQUEST_PATH.replace("author-to-reviewer", "codex-to-claude")
MEMBER_REPORT_PATH = REPORT_PATH.replace("reviewer-to-author", "claude-to-codex")
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
    timestamp: str = "2026-08-07T12:00:00Z",
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
# Codex → Claude: verify outcome

**When:** {timestamp} · **From:** codex (online)

Event type: verify-request
Reviewed head: {head}
Reviewed base: {base}
Author seat: codex
Author model: gpt-5.6-sol
Assigned operator: claude
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
    timestamp: str = "2026-08-07T12:10:00Z",
    request_path: str = REQUEST_PATH,
) -> str:
    abuse_binding = (
        ""
        if risk_class != "high-risk-control"
        else "Abuse Class Assessment: bound-to-request\n"
    )
    dispositions = tuple(f"{ref}: {disposition}" for ref in finding_refs)
    return f"""\
# Claude → Codex: outcome verification

**When:** {timestamp} · **From:** claude (online)

Event type: verification-report
VERDICT: {verdict}
Verification request: {request_path}@{trigger}
Reviewed head: {head}
Reviewed base: {base}
Reviewer seat: claude
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
    request_path: str = REQUEST_PATH,
    report_path: str = REPORT_PATH,
    timestamps: tuple[str, str] = ("2026-08-07T12:00:00Z", "2026-08-07T12:10:00Z"),
    finding_refs: tuple[str, ...] | None = None,
) -> None:
    refs = finding_refs or (_mint_evidence(root),)
    _commit_file(
        root,
        request_path,
        _request_text(
            reviewed_base,
            reviewed_head,
            risk_class=risk_class,
            finding_refs=refs,
            timestamp=timestamps[0],
        ),
        "review: request verification",
    )
    trigger = _git(root, "rev-parse", "HEAD")
    _commit_file(
        root,
        report_path,
        _report_text(
            reviewed_base,
            reviewed_head,
            trigger,
            verdict=verdict,
            risk_class=risk_class,
            reviewer_model=reviewer_model,
            finding_refs=refs,
            disposition=disposition,
            timestamp=timestamps[1],
            request_path=request_path,
        ),
        "review: publish verdict",
    )


def _land_remediation_pair(
    root: Path,
    reviewed_base: str,
    reviewed_head: str,
    failed_report_commit: str,
) -> None:
    refs = (f"{EVIDENCE_PATH}@{_git(root, 'log', '--format=%H', '-1', '--', EVIDENCE_PATH)}",)
    request_path = REQUEST_PATH.replace("12-00-00", "12-20-00")
    report_path = REPORT_PATH.replace("12-10-00", "12-30-00")
    failed_ref = f"{REPORT_PATH}@{failed_report_commit}"
    request_text = _request_text(
        reviewed_base,
        reviewed_head,
        risk_class="high-risk-control",
        finding_refs=refs,
    ).replace(
        "2026-08-07T12:00:00Z", "2026-08-07T12:20:00Z"
    ).replace(
        "Risk class: high-risk-control\n",
        f"Risk class: high-risk-control\nRemediates failed report: {failed_ref}\n",
    )
    _commit_file(root, request_path, request_text, "review: request remediation")
    trigger = _git(root, "rev-parse", "HEAD")
    report_text = _report_text(
        reviewed_base,
        reviewed_head,
        trigger,
        verdict="GO",
        risk_class="high-risk-control",
        reviewer_model="claude-opus-4-7",
        finding_refs=refs,
    ).replace(
        "2026-08-07T12:10:00Z", "2026-08-07T12:30:00Z"
    ).replace(
        f"Verification request: {REQUEST_PATH}@",
        f"Verification request: {request_path}@",
    ).replace(
        "Risk class: high-risk-control\n",
        f"Risk class: high-risk-control\nSupersedes: {failed_ref}\n",
    )
    _commit_file(root, report_path, report_text, "review: publish remediation verdict")


def _land_member_pair(
    root: Path,
    reviewed_base: str,
    reviewed_head: str,
    *,
    request_replacement: tuple[str, str] | None = None,
    report_replacement: tuple[str, str] | None = None,
    report_path: str = MEMBER_REPORT_PATH,
) -> None:
    refs = (_mint_evidence(root),)
    request_text = (
        _request_text(
            reviewed_base, reviewed_head,
            risk_class="high-risk-control", finding_refs=refs,
        )
        .replace("# Author → Reviewer:", "# Codex → Claude:")
        .replace("**From:** author", "**From:** codex")
        .replace("Author seat: author", "Author seat: codex")
        .replace("Assigned operator: reviewer", "Assigned operator: claude")
    )
    if request_replacement is not None:
        request_text = request_text.replace(*request_replacement)
    _commit_file(root, MEMBER_REQUEST_PATH, request_text, "review: request by member")
    trigger = _git(root, "rev-parse", "HEAD")
    report_text = (
        _report_text(
            reviewed_base, reviewed_head, trigger, verdict="GO",
            risk_class="high-risk-control", reviewer_model="claude-opus-4-7",
            finding_refs=refs,
        )
        .replace("**From:** reviewer", "**From:** claude")
        .replace(
            f"Verification request: {REQUEST_PATH}@",
            f"Verification request: {MEMBER_REQUEST_PATH}@",
        )
        .replace("Reviewer seat: reviewer", "Reviewer seat: claude")
    )
    if report_replacement is not None:
        report_text = report_text.replace(*report_replacement)
    recipient = protocol_mailbox.EVENT_NAME_RE.fullmatch(
        Path(report_path).name
    ).group("recipient")
    report_text = report_text.replace(
        "# Claude → Codex:", f"# Claude → {recipient.capitalize()}:"
    )
    _commit_file(root, report_path, report_text, "review: verdict by member")


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
    with pytest.raises(gate.pair.CompactPairError, match="publisher must be"):
        gate._validate_current_envelope(
            repo_root, raw, path, protocol_mailbox.KNOWN_KINDS, commit
        )


def test_member_route_cutover_opens_the_writer(tmp_path: Path) -> None:
    root, base = _init_repo(tmp_path)
    reviewed_head = _commit_file(
        root, "pipeline/mailbox_writer.py", "POLICY = 1\n", "feat: writer policy"
    )
    _land_member_pair(root, base, reviewed_head)

    outcome = gate.evaluate(root, base, _git(root, "rev-parse", "HEAD"))

    assert outcome.admitted, gate.render(outcome)
    assert gate.mailbox_writer.new_write_envelope_problem(
        "verify-request", "codex", "claude"
    ) is None
    assert gate.mailbox_writer.new_write_envelope_problem(
        "verification-report", "claude", "codex"
    ) is None


@pytest.mark.parametrize(
    ("request_replacement", "report_replacement", "report_path", "reason"),
    (
        (("Author model: gpt-5.6-sol", "Author model: gemini-3.7-flash-high"), None,
         MEMBER_REPORT_PATH, "author model family does not match author member"),
        (None, ("Reviewer model: claude-opus-4-7", "Reviewer model: gpt-5.6-sol"),
         MEMBER_REPORT_PATH, "reviewer model family does not match reviewer member"),
        (None, None, MEMBER_REPORT_PATH.replace("-to-codex-", "-to-agy-"),
         "report recipient does not match request author"),
    ),
)
def test_member_route_forward_reader_rejects_identity_laundering(
    tmp_path: Path,
    request_replacement: tuple[str, str] | None,
    report_replacement: tuple[str, str] | None,
    report_path: str,
    reason: str,
) -> None:
    root, base = _init_repo(tmp_path)
    reviewed_head = _commit_file(
        root, "pipeline/mailbox_writer.py", "POLICY = 1\n", "feat: writer policy"
    )
    _land_member_pair(
        root, base, reviewed_head,
        request_replacement=request_replacement,
        report_replacement=report_replacement,
        report_path=report_path,
    )

    outcome = gate.evaluate(root, base, _git(root, "rev-parse", "HEAD"))

    assert not outcome.admitted
    assert any(reason in detail for _, detail in outcome.skipped_reports)


@pytest.mark.parametrize(
    ("kind", "sender", "recipient"),
    (
        ("verify-request", "codex", "reviewer"),
        ("verify-request", "codex", "codex"),
        ("verification-report", "agy", "codex"),
        ("verification-report", "claude", "claude"),
        ("verification-report", "reviewer", "codex"),
    ),
)
def test_member_route_forward_reader_rejects_mixing_and_self_review(
    kind: str, sender: str, recipient: str,
) -> None:
    assert protocol_mailbox.formal_review_route_problem(kind, sender, recipient)


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


def test_supersession_uses_explicit_candidate_head_when_checkout_stays_at_base(
    tmp_path: Path,
) -> None:
    root, base = _init_repo(tmp_path)
    reviewed_head = _commit_file(
        root, "src/ordinary.py", "VALUE = 2\n", "feat: ordinary reviewed work"
    )
    _land_pair(root, base, reviewed_head, verdict="FAIL")
    failed_report_commit = _git(root, "rev-parse", "HEAD")
    fixed_head = _commit_file(
        root, "pipeline/mailbox_writer.py", "POLICY = 1\n", "fix: authority control"
    )
    _land_remediation_pair(root, reviewed_head, fixed_head, failed_report_commit)
    candidate_head = _git(root, "rev-parse", "HEAD")
    replacement_path = REPORT_PATH.replace("12-10-00", "12-30-00")
    replacement_raw = _git(root, "show", f"{candidate_head}:{replacement_path}").encode()
    replacement = gate.pair.parse_verification_report_committed_bytes(
        root, replacement_path, replacement_raw
    )

    _git(root, "checkout", "-q", "--detach", base)

    # Non-vacuity: the ambient/default validator reproduces the trusted-CI bug.
    assert any(
        "not in this history" in violation
        for violation in gate.pair.validate_report(root, replacement)
    )
    outcome = gate.evaluate(root, base, candidate_head)

    assert outcome.admitted, gate.render(outcome)


def test_explicit_candidate_head_rejects_request_from_sibling_history(
    tmp_path: Path,
) -> None:
    root, base = _init_repo(tmp_path)
    refs = (_mint_evidence(root),)
    reviewed_head = _commit_file(
        root, "src/ordinary.py", "VALUE = 2\n", "feat: ordinary reviewed work"
    )
    main_branch = _git(root, "branch", "--show-current")
    _git(root, "checkout", "-q", "-b", "sibling-request")
    trigger = _commit_file(
        root,
        REQUEST_PATH,
        _request_text(
            base,
            reviewed_head,
            risk_class="high-risk-control",
            finding_refs=refs,
        ),
        "review: request on sibling",
    )
    _git(root, "checkout", "-q", main_branch)
    candidate_head = _commit_file(
        root,
        REPORT_PATH,
        _report_text(
            base,
            reviewed_head,
            trigger,
            verdict="GO",
            risk_class="high-risk-control",
            reviewer_model="claude-opus-4-7",
            finding_refs=refs,
        ),
        "review: report with sibling request",
    )
    report = gate.pair.parse_verification_report(
        root, REPORT_PATH
    )

    violations = gate.pair.validate_report(
        root, report, history_head=candidate_head
    )

    assert "request binding invalid: request trigger commit is not in this history" in violations


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


def test_tree_identical_merge_is_detected_from_its_feature_parent(
    tmp_path: Path,
) -> None:
    root, _ = _init_repo(tmp_path)
    main_branch = _git(root, "branch", "--show-current")
    _git(root, "checkout", "-q", "-b", "feature")
    feature = _commit_file(
        root,
        "pipeline/mailbox_writer.py",
        "POLICY = 1\n",
        "feat: writer policy",
    )
    _git(root, "checkout", "-q", main_branch)
    _git(root, "merge", "--no-ff", "-q", "-m", "merge: feature", "feature")
    merge = _git(root, "rev-parse", "HEAD")

    assert _git(root, "rev-parse", f"{merge}^2") == feature
    assert _git(root, "rev-list", f"{feature}..{merge}") == merge
    assert _git(root, "rev-parse", f"{feature}^{{tree}}") == _git(
        root, "rev-parse", f"{merge}^{{tree}}"
    )
    assert _git(root, "diff", "--name-only", f"{merge}^1", merge) == (
        "pipeline/mailbox_writer.py"
    )
    assert _git(root, "diff", "--name-only", feature, merge) == ""
    commits = gate.authority_commits(root, feature, merge)

    assert commits == {merge: ("pipeline/mailbox_writer.py",)}


def test_tree_identical_merge_with_only_ordinary_changes_is_not_authority(
    tmp_path: Path,
) -> None:
    root, _ = _init_repo(tmp_path)
    main_branch = _git(root, "branch", "--show-current")
    _git(root, "checkout", "-q", "-b", "feature")
    feature = _commit_file(root, "src/ordinary.py", "VALUE = 1\n", "feat: ordinary")
    _git(root, "checkout", "-q", main_branch)
    _git(root, "merge", "--no-ff", "-q", "-m", "merge: feature", "feature")
    merge = _git(root, "rev-parse", "HEAD")

    assert _git(root, "rev-parse", f"{feature}^{{tree}}") == _git(
        root, "rev-parse", f"{merge}^{{tree}}"
    )
    assert gate.authority_commits(root, feature, merge) == {}


def test_authority_changes_on_a_treesame_merged_side_are_not_pruned(
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
    _git(root, "checkout", "-q", "-b", "feature", base)
    changed = _commit_file(
        root,
        "pipeline/mailbox_writer.py",
        "POLICY = 1\n",
        "test: change protected policy",
    )
    reverted = _commit_file(
        root,
        "pipeline/mailbox_writer.py",
        "POLICY = 0\n",
        "test: revert protected policy",
    )
    _git(root, "checkout", "-q", main_branch)
    _git(root, "merge", "--no-ff", "-q", "-m", "merge: feature", "feature")
    merge = _git(root, "rev-parse", "HEAD")

    assert _git(root, "rev-parse", f"{merge}^{{tree}}") == _git(
        root, "rev-parse", f"{merge}^1^{{tree}}"
    )
    commits = gate.authority_commits(root, base, merge)

    assert commits == {
        changed: ("pipeline/mailbox_writer.py",),
        reverted: ("pipeline/mailbox_writer.py",),
    }


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


@pytest.mark.parametrize("fresh_verdict", ("GO", "NITS"))
@pytest.mark.parametrize("tamper", ("delete", "modify", "type"))
def test_unsuperseded_current_fail_blocks_a_fresh_admitting_verdict(
    tmp_path: Path, fresh_verdict: str, tamper: str,
) -> None:
    root, base = _init_repo(tmp_path)
    reviewed_head = _commit_file(
        root, "pipeline/mailbox_writer.py", "WRITER = 1\n", "feat: writer"
    )
    refs = (_mint_evidence(root),)
    _land_pair(
        root, base, reviewed_head, verdict="FAIL",
        disposition="counter-evidence", finding_refs=refs,
    )
    _land_pair(
        root, base, reviewed_head, verdict=fresh_verdict,
        request_path=SECOND_REQUEST_PATH, report_path=SECOND_REPORT_PATH,
        timestamps=("2026-08-07T12:20:00Z", "2026-08-07T12:30:00Z"),
        finding_refs=refs,
    )
    head = _git(root, "rev-parse", "HEAD")

    outcome = gate.evaluate(root, base, head)

    assert not outcome.admitted, gate.render(outcome)
    assert outcome.uncovered == {}
    assert [path for path, _ in outcome.blocking_failures] == [REPORT_PATH]
    tamper_base = head
    (root / "pipeline/mailbox_writer.py").write_text("WRITER = 2\n", encoding="utf-8")
    _git(root, "add", "pipeline/mailbox_writer.py")
    if tamper == "delete":
        _git(root, "rm", "-q", REPORT_PATH)
    elif tamper == "modify":
        (root / REPORT_PATH).write_text("changed\n", encoding="utf-8")
        _git(root, "add", REPORT_PATH)
    else:
        (root / REPORT_PATH).unlink()
        (root / REPORT_PATH).symlink_to("missing-report")
        _git(root, "add", REPORT_PATH)
    _git(root, "commit", "-q", "-m", f"test: {tamper} immutable FAIL")
    with pytest.raises(gate.AdmissionError, match="immutable review artifact"):
        gate.evaluate(root, tamper_base, _git(root, "rev-parse", "HEAD"))


def test_remediation_coverage_inherits_only_the_superseded_reports_range(
    tmp_path: Path,
) -> None:
    root, base = _init_repo(tmp_path)
    original = _commit_file(root, "pipeline/original.py", "x = 1\n", "original")
    fix = _commit_file(root, "pipeline/fix.py", "x = 2\n", "remediation")
    unrelated_head = _commit_file(root, "src/unrelated.py", "x = 3\n", "unrelated")
    failed_ref = (REPORT_PATH, "1" * 40)
    unrelated_ref = (SECOND_REPORT_PATH, "2" * 40)
    Report = SimpleNamespace
    failed = Report(reviewed_base=base, reviewed_head=original, supersedes=None)
    unrelated = Report(reviewed_base=fix, reviewed_head=unrelated_head, supersedes=None)
    remediation = Report(reviewed_base=original, reviewed_head=fix, supersedes=failed_ref)

    assert gate._coverage_commits(
        root, remediation, {failed_ref: failed, unrelated_ref: unrelated}
    ) == frozenset({original, fix})


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
    legacy_request = REQUEST_PATH.replace("codex-to-claude", "director-to-operator")
    legacy_report = REPORT_PATH.replace("claude-to-codex", "operator-to-director")
    request_text = (
        _request_text(
            base, reviewed_head, risk_class="high-risk-control", finding_refs=refs
        )
        .replace("# Codex → Claude", "# Director → Operator")
        .replace("**From:** codex", "**From:** director")
        .replace("Author seat: codex", "Author seat: director")
        .replace("Assigned operator: claude", "Assigned operator: operator")
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
        .replace("# Claude → Codex", "# Operator → Director")
        .replace("**From:** claude", "**From:** operator")
        .replace(f"Verification request: {REQUEST_PATH}@", f"Verification request: {legacy_request}@")
        .replace("Reviewer seat: claude", "Reviewer seat: operator")
        .replace("Cursor at send: cursorless", "Cursor at send: 0")
    )
    _commit_file(root, legacy_report, report_text, "review: legacy report")
    head = _git(root, "rev-parse", "HEAD")

    outcome = gate.evaluate(root, base, head)

    assert not outcome.admitted
    assert any(
        "publisher must be codex or claude" in reason
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
    legacy_request = REQUEST_PATH.replace("codex-to-claude", "director-to-operator")
    request_text = (
        _request_text(
            base, reviewed_head, risk_class="high-risk-control", finding_refs=refs
        )
        .replace("# Codex → Claude", "# Director → Operator")
        .replace("**From:** codex", "**From:** director")
        .replace("Author seat: codex", "Author seat: director")
        .replace("Assigned operator: claude", "Assigned operator: operator")
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
        reviewer_model="claude-opus-4-6-thinking",
    )
    head = _git(root, "rev-parse", "HEAD")

    outcome = gate.evaluate(root, base, head)

    assert not outcome.admitted
    assert any(
        "require an explicit high-risk-control" in reason
        for _, reason in outcome.skipped_reports
    )


def test_reviewer_member_model_mismatch_is_rejected_by_canonical_validator(
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
        "reviewer model family does not match reviewer member" in reason
        for _, reason in outcome.skipped_reports
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
