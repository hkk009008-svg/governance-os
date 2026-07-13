"""Strict Lane V report-v2 and committed-authority gate tests."""

from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path

import pytest

import verification_report_gate as gate


HEAD = "a" * 40
BASE = "b" * 40
TASK_ID = "11111111-2222-4333-8444-555555555555"
DESCRIPTOR_PATH = f"coordination/verification/scopes/{TASK_ID}.json"
DESCRIPTOR_DIGEST = "sha256:" + "c" * 64
RECEIPT_ID = "opr1:" + "d" * 64
SCOPE_DIGEST = "sha256:" + "e" * 64
GUARD_DIGEST = "sha256:" + "f" * 64
REPORT_PATH = (
    "coordination/mailbox/sent/"
    "2026-07-13T05-00-00Z-operator-to-all-verification-report.md"
)
LEGACY_SCHEMA = "lane-v-report-v1-baseline/v1"


def _codex_fields() -> list[tuple[str, str]]:
    return [
        ("Verification schema", "lane-v-report/v2"),
        ("Verification mode", "codex-lane-v"),
        ("Verification harness", "codex:lane-v-verifier"),
        ("Verification task ID", TASK_ID),
        ("Scope authority", f"{DESCRIPTOR_PATH}@{DESCRIPTOR_DIGEST}"),
        ("Trigger identity", f"shipping-commit:{HEAD}"),
        ("Reviewed head", HEAD),
        ("Reviewed base", BASE),
        ("Review profile", "codex-lane-v"),
        ("Authorization identity", "standing-policy:codex-lane-v-opus-v1"),
        ("Opus receipt ID", RECEIPT_ID),
        ("Opus scope digest", SCOPE_DIGEST),
        ("Cross-model review", "pass"),
        ("Effective Opus model", "claude-opus-4-7"),
        ("Opus finding dispositions", "none"),
        (
            "Reconciliation guard",
            json.dumps(
                {"digest": GUARD_DIGEST, "go_allowed": True},
                sort_keys=True,
                separators=(",", ":"),
            ),
        ),
        ("Degraded reason", "none"),
    ]


def _claude_fields() -> list[tuple[str, str]]:
    fields = _codex_fields()
    values = dict(fields)
    values["Verification mode"] = "claude-lane-v"
    values["Verification harness"] = "claude:lane-v-verifier"
    for label in gate.ATTESTATION_FIELDS[8:]:
        values[label] = "not-applicable"
    return [(label, values[label]) for label in gate.ATTESTATION_FIELDS]


def _report_bytes(
    fields: list[tuple[str, str]] | None = None,
    *,
    verdict: str = "VERDICT: GO",
    head: str = HEAD,
    h1_sender: str = "Operator",
    h1_recipient: str = "All",
    envelope_sender: str = "operator",
    heading: str = "## Verification Attestation",
    prefix: list[str] | None = None,
    suffix: list[str] | None = None,
) -> bytes:
    field_lines = [f"{label}: {value}" for label, value in (fields or _codex_fields())]
    lines = [
        f"# {h1_sender} → {h1_recipient}: "
        f"Lane V verification report — commit `{head}`",
        "",
        "**When:** 2026-07-13T05:00:00Z · "
        f"**From:** {envelope_sender} (online)",
        "",
        verdict,
        "",
        "## Evidence",
        "$ env -u GIT_INDEX_FILE .venv/bin/python -m pytest tests/unit -q",
        "→ 1 passed in 0.01s",
        "",
        *(prefix or ()),
        heading,
        "",
        *field_lines,
        *(suffix if suffix is not None else ["", "## Findings", "None."]),
    ]
    return ("\n".join(lines) + "\n").encode("utf-8")


def _replace_field(
    fields: list[tuple[str, str]], label: str, value: str
) -> list[tuple[str, str]]:
    return [(name, value if name == label else current) for name, current in fields]


def test_parse_valid_codex_and_claude_reports() -> None:
    codex = gate.parse_lane_v_report(REPORT_PATH, _report_bytes())
    claude = gate.parse_lane_v_report(REPORT_PATH, _report_bytes(_claude_fields()))

    assert codex.sender == "operator"
    assert codex.verdict == "GO"
    assert codex.h1_head == HEAD
    assert tuple(codex.fields) == gate.ATTESTATION_FIELDS
    assert codex.body_digest == "sha256:" + hashlib.sha256(_report_bytes()).hexdigest()
    assert claude.fields["Verification mode"] == "claude-lane-v"
    assert claude.fields["Opus receipt ID"] == "not-applicable"


def test_verdict_literal_in_evidence_is_not_a_second_verdict() -> None:
    raw = _report_bytes(
        prefix=["$ rg 'VERDICT:' scripts", "→ one schema site", ""]
    )

    report = gate.parse_lane_v_report(REPORT_PATH, raw)

    assert report.verdict == "GO"


@pytest.mark.parametrize(
    "framed_verdict",
    [
        pytest.param("> VERDICT: FAIL", id="blockquote"),
        pytest.param("- VERDICT: FAIL", id="list-item"),
        pytest.param("### VERDICT: FAIL", id="heading"),
        pytest.param("`VERDICT: FAIL`", id="inline-code"),
        pytest.param("```VERDICT: FAIL```", id="fenced-code"),
    ],
)
def test_rejects_markdown_framed_second_verdict(framed_verdict: str) -> None:
    raw = _report_bytes(prefix=[framed_verdict, ""])

    with pytest.raises(gate.ReportGateError, match="invalid_report_verdict"):
        gate.parse_lane_v_report(REPORT_PATH, raw)


@pytest.mark.parametrize(
    "raw",
    [
        pytest.param(
            _report_bytes(heading="## Missing Attestation"), id="missing-section"
        ),
        pytest.param(
            _report_bytes(prefix=["## Verification Attestation", ""]),
            id="duplicate-section",
        ),
        pytest.param(_report_bytes(_codex_fields()[:-1]), id="missing-field"),
        pytest.param(
            _report_bytes(_codex_fields() + [_codex_fields()[-1]]),
            id="duplicate-field",
        ),
        pytest.param(
            _report_bytes([_codex_fields()[1], _codex_fields()[0], *_codex_fields()[2:]]),
            id="reordered-field",
        ),
        pytest.param(
            _report_bytes(
                [*_codex_fields()[:-1], ("Invented field", "value")]
            ),
            id="unknown-field",
        ),
        pytest.param(
            _report_bytes(
                [("**Verification schema**", "lane-v-report/v2"), *_codex_fields()[1:]]
            ),
            id="decorated-label",
        ),
        pytest.param(
            _report_bytes(
                suffix=[" continuation", "", "## Findings", "None."]
            ),
            id="continuation-after-fields",
        ),
        pytest.param(
            _report_bytes(prefix=["VERDICT: GO", ""]), id="duplicate-verdict"
        ),
        pytest.param(_report_bytes(verdict="**VERDICT: GO**"), id="off-form-verdict"),
    ],
)
def test_rejects_section_field_and_verdict_shape(raw: bytes) -> None:
    with pytest.raises(gate.ReportGateError):
        gate.parse_lane_v_report(REPORT_PATH, raw)


@pytest.mark.parametrize(
    ("relative_path", "raw"),
    [
        pytest.param(
            REPORT_PATH.replace("-operator-to-", "-director-to-"),
            _report_bytes(),
            id="non-operator-filename",
        ),
        pytest.param(
            REPORT_PATH.replace("coordination/mailbox/sent", "docs"),
            _report_bytes(),
            id="report-outside-sent-mailbox",
        ),
        pytest.param(
            REPORT_PATH,
            _report_bytes(envelope_sender="operator2"),
            id="filename-envelope-sender-mismatch",
        ),
        pytest.param(REPORT_PATH, _report_bytes(head=HEAD[:12]), id="abbreviated-h1"),
        pytest.param(REPORT_PATH, _report_bytes(head=HEAD.upper()), id="uppercase-h1"),
        pytest.param(REPORT_PATH, _report_bytes(head="9" * 40), id="h1-head-mismatch"),
        pytest.param(
            REPORT_PATH,
            _report_bytes(h1_sender="Operator2"),
            id="h1-sender-identity-mismatch",
        ),
        pytest.param(
            REPORT_PATH,
            _report_bytes(h1_recipient="Director"),
            id="h1-recipient-identity-mismatch",
        ),
    ],
)
def test_rejects_sender_and_h1_mismatches(relative_path: str, raw: bytes) -> None:
    with pytest.raises(gate.ReportGateError):
        gate.parse_lane_v_report(relative_path, raw)


@pytest.mark.parametrize(
    ("label", "value"),
    [
        pytest.param(
            "Verification task ID",
            "AAAAAAAA-BBBB-4CCC-8DDD-EEEEEEEEEEEE",
            id="bad-uuid",
        ),
        pytest.param("Scope authority", f"{DESCRIPTOR_PATH}@sha256:{'A' * 64}", id="bad-scope-digest"),
        pytest.param("Opus receipt ID", "opr1:" + "A" * 64, id="bad-receipt-id"),
        pytest.param("Opus scope digest", "sha256:" + "A" * 64, id="bad-opus-digest"),
        pytest.param(
            "Reconciliation guard",
            '{"go_allowed":true,"digest":"' + GUARD_DIGEST + '"}',
            id="noncanonical-json",
        ),
        pytest.param(
            "Reconciliation guard",
            '{"digest":"' + GUARD_DIGEST + '","digest":"' + GUARD_DIGEST + '","go_allowed":true}',
            id="duplicate-json-key",
        ),
    ],
)
def test_rejects_invalid_structural_values(label: str, value: str) -> None:
    fields = _replace_field(_codex_fields(), label, value)
    with pytest.raises(gate.ReportGateError):
        gate.parse_lane_v_report(REPORT_PATH, _report_bytes(fields))


@pytest.mark.parametrize(
    "suffix",
    [
        pytest.param([""], id="extra-framing-blank"),
        pytest.param(["", "### Subheading"], id="level-three-heading"),
        pytest.param(["", "prose"], id="prose-after-fields"),
        pytest.param(["", "", "## Findings"], id="two-blanks-before-heading"),
    ],
)
def test_rejects_invalid_attestation_termination(suffix: list[str]) -> None:
    with pytest.raises(gate.ReportGateError):
        gate.parse_lane_v_report(REPORT_PATH, _report_bytes(suffix=suffix))


def test_rejects_invalid_utf8_carriage_return_nul_and_raw_caps() -> None:
    invalid_utf8 = _report_bytes() + b"\xff"
    carriage_return = _report_bytes().replace(b"VERDICT: GO\n", b"VERDICT: GO\r\n")
    nul = _report_bytes().replace(b"None.\n", b"No\x00ne.\n")
    oversized_line = _replace_field(
        _codex_fields(), "Opus finding dispositions", "x" * gate.ATTESTATION_LINE_MAX_BYTES
    )
    oversized_section = _replace_field(
        _replace_field(_codex_fields(), "Authorization identity", "x" * 33_000),
        "Effective Opus model",
        "y" * 33_000,
    )

    for raw in (
        invalid_utf8,
        carriage_return,
        nul,
        _report_bytes(oversized_line),
        _report_bytes(oversized_section),
    ):
        with pytest.raises(gate.ReportGateError):
            gate.parse_lane_v_report(REPORT_PATH, raw)


@pytest.mark.parametrize(
    ("label", "value"),
    [
        pytest.param("Verification harness", "claude:lane-v-verifier", id="codex-harness"),
        pytest.param("Review profile", "not-applicable", id="codex-profile"),
        pytest.param("Cross-model review", "unknown", id="codex-status"),
        pytest.param("Effective Opus model", "not-available", id="pass-model"),
        pytest.param("Degraded reason", "timeout", id="pass-reason"),
    ],
)
def test_rejects_invalid_codex_mode_combinations(label: str, value: str) -> None:
    fields = _replace_field(_codex_fields(), label, value)
    with pytest.raises(gate.ReportGateError):
        gate.parse_lane_v_report(REPORT_PATH, _report_bytes(fields))


def test_rejects_claude_report_with_any_codex_specific_value() -> None:
    fields = _replace_field(_claude_fields(), "Opus receipt ID", RECEIPT_ID)
    with pytest.raises(gate.ReportGateError):
        gate.parse_lane_v_report(REPORT_PATH, _report_bytes(fields))


def _git(root: Path, *args: str) -> str:
    completed = subprocess.run(
        ["env", "-u", "GIT_INDEX_FILE", "git", *args],
        cwd=root,
        check=True,
        capture_output=True,
        text=True,
    )
    return completed.stdout.strip()


def _authority_fixture(
    root: Path,
    *,
    mode: str = "codex-lane-v",
    trigger_kind: str = "shipping-commit",
    recipient: str = "operator",
) -> tuple[Path, list[tuple[str, str]], str, str, str]:
    root.mkdir()
    (root / "requirements").mkdir()
    (root / "requirements" / "task.md").write_text(
        "Review the committed feature.\n", encoding="utf-8"
    )
    (root / "scripts").mkdir()
    (root / "scripts" / "feature.py").write_text("VALUE = 'base'\n", encoding="utf-8")
    _git(root, "init", "-q")
    _git(root, "config", "user.name", "Report Gate Fixture")
    _git(root, "config", "user.email", "report-gate@example.invalid")
    _git(root, "add", ".")
    _git(root, "commit", "-q", "-m", "chore: base")
    base = _git(root, "rev-parse", "HEAD")

    harness = (
        "codex:lane-v-verifier"
        if mode == "codex-lane-v"
        else "claude:lane-v-verifier"
    )
    descriptor = {
        "schema_version": "lane-v-scope/v1",
        "task_id": TASK_ID,
        "question_id": "report-gate-fixture",
        "trigger_kind": trigger_kind,
        "verification_mode": mode,
        "verification_harness": harness,
        "review_profile": mode,
        "reviewed_base": {"policy": "exact", "commit": base},
        "requirement_paths": ["requirements/task.md"],
        "allowed_path_roots": ["scripts"],
        "verification_commands": [
            "env -u GIT_INDEX_FILE .venv/bin/python scripts/ci_smoke.py"
        ],
    }
    descriptor_file = root / DESCRIPTOR_PATH
    descriptor_file.parent.mkdir(parents=True)
    descriptor_raw = (json.dumps(descriptor, indent=2) + "\n").encode()
    descriptor_file.write_bytes(descriptor_raw)
    descriptor_digest = "sha256:" + hashlib.sha256(descriptor_raw).hexdigest()
    scope_authority = f"{DESCRIPTOR_PATH}@{descriptor_digest}"
    _git(root, "add", DESCRIPTOR_PATH)
    _git(root, "commit", "-q", "-m", "docs: bind report authority")

    (root / "scripts" / "feature.py").write_text(
        "VALUE = 'reviewed'\n", encoding="utf-8"
    )
    _git(root, "add", "scripts/feature.py")
    commit_args = ["commit", "-q", "-m", "feat: reviewed change"]
    if trigger_kind == "shipping-commit":
        commit_args.extend(("-m", f"Lane-V-Scope: {scope_authority}"))
    _git(root, *commit_args)
    head = _git(root, "rev-parse", "HEAD")

    trigger_commit = head
    trigger_path: str | None = None
    if trigger_kind == "verify-request":
        trigger_path = (
            "coordination/mailbox/sent/"
            f"2026-07-13T05-01-00Z-director-to-{recipient}-verify-request.md"
        )
        event = root / trigger_path
        event.parent.mkdir(parents=True)
        recipient_title = "Operator2" if recipient == "operator2" else "Operator"
        event.write_text(
            f"# Director → {recipient_title}: verify report fixture\n\n"
            "**When:** 2026-07-13T05:01:00Z · **From:** director (online)\n\n"
            "Event type: verify-request\n"
            f"Reviewed head: {head}\n"
            f"Reviewed base: {base}\n"
            f"Lane-V-Scope: {scope_authority}\n",
            encoding="utf-8",
        )
        _git(root, "add", trigger_path)
        _git(root, "commit", "-q", "-m", "coord: request verification")
        trigger_commit = _git(root, "rev-parse", "HEAD")

    fields = _codex_fields() if mode == "codex-lane-v" else _claude_fields()
    updates = {
        "Verification mode": mode,
        "Verification harness": harness,
        "Verification task ID": TASK_ID,
        "Scope authority": scope_authority,
        "Trigger identity": (
            f"shipping-commit:{trigger_commit}"
            if trigger_path is None
            else f"verify-request:{trigger_commit}:{trigger_path}"
        ),
        "Reviewed head": head,
        "Reviewed base": base,
    }
    fields = [(label, updates.get(label, value)) for label, value in fields]
    report_path = REPORT_PATH.replace("-operator-to-", f"-{recipient}-to-")
    return root, fields, report_path, head, base


@pytest.mark.parametrize(
    ("mode", "trigger_kind", "recipient"),
    [
        ("codex-lane-v", "shipping-commit", "operator"),
        ("codex-lane-v", "shipping-commit", "operator2"),
        ("claude-lane-v", "verify-request", "operator2"),
    ],
)
def test_structural_authority_accepts_committed_shipping_and_verify_request(
    tmp_path: Path, mode: str, trigger_kind: str, recipient: str
) -> None:
    root, fields, report_path, head, _ = _authority_fixture(
        tmp_path / "repo",
        mode=mode,
        trigger_kind=trigger_kind,
        recipient=recipient,
    )
    raw = _report_bytes(
        fields,
        head=head,
        h1_sender=recipient.capitalize(),
        envelope_sender=recipient,
        prefix=["Verification mode: prose-cannot-select-a-provider", ""],
    )
    report = gate.parse_lane_v_report(report_path, raw)

    authority = gate.validate_structural_authority(root, report)

    assert isinstance(authority, gate.StructuralAuthority)
    assert authority.descriptor.verification_mode == mode
    assert authority.trigger_kind == trigger_kind
    assert authority.verify_request_recipient == (
        recipient if trigger_kind == "verify-request" else None
    )


@pytest.mark.parametrize(
    "mismatch",
    [
        "provider",
        "task",
        "scope-path",
        "scope-digest",
        "trigger",
        "head",
        "base",
    ],
)
def test_structural_authority_rejects_report_descriptor_trigger_mismatch(
    tmp_path: Path, mismatch: str
) -> None:
    root, fields, report_path, head, base = _authority_fixture(tmp_path / "repo")
    values = dict(fields)
    h1_head = head
    if mismatch == "provider":
        values["Verification mode"] = "claude-lane-v"
        values["Verification harness"] = "claude:lane-v-verifier"
        for label in gate.ATTESTATION_FIELDS[8:]:
            values[label] = "not-applicable"
    elif mismatch == "task":
        values["Verification task ID"] = "aaaaaaaa-bbbb-4ccc-8ddd-eeeeeeeeeeee"
    elif mismatch == "scope-path":
        values["Scope authority"] = (
            "coordination/verification/scopes/"
            "aaaaaaaa-bbbb-4ccc-8ddd-eeeeeeeeeeee.json@" + DESCRIPTOR_DIGEST
        )
    elif mismatch == "scope-digest":
        path = values["Scope authority"].split("@", 1)[0]
        values["Scope authority"] = path + "@sha256:" + "0" * 64
    elif mismatch == "trigger":
        values["Trigger identity"] = f"shipping-commit:{base}"
    elif mismatch == "head":
        values["Reviewed head"] = base
        h1_head = base
    elif mismatch == "base":
        values["Reviewed base"] = head
    mutated = [(label, values[label]) for label in gate.ATTESTATION_FIELDS]
    report = gate.parse_lane_v_report(
        report_path,
        _report_bytes(mutated, head=h1_head),
    )

    with pytest.raises(gate.ReportGateError):
        gate.validate_structural_authority(root, report)


def test_verify_request_recipient_must_equal_report_sender(tmp_path: Path) -> None:
    root, fields, _, head, _ = _authority_fixture(
        tmp_path / "repo", trigger_kind="verify-request", recipient="operator2"
    )
    report = gate.parse_lane_v_report(
        REPORT_PATH,
        _report_bytes(fields, head=head, envelope_sender="operator"),
    )

    with pytest.raises(gate.ReportGateError, match="recipient"):
        gate.validate_structural_authority(root, report)


def test_structural_git_ignores_inherited_git_selectors(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    root, fields, report_path, head, _ = _authority_fixture(tmp_path / "repo")
    report = gate.parse_lane_v_report(report_path, _report_bytes(fields, head=head))
    monkeypatch.setenv("GIT_DIR", str(tmp_path / "attacker.git"))
    monkeypatch.setenv("GIT_WORK_TREE", str(tmp_path / "attacker-worktree"))
    monkeypatch.setenv("GIT_OBJECT_DIRECTORY", str(tmp_path / "attacker-objects"))
    monkeypatch.setenv("GIT_INDEX_FILE", str(tmp_path / "attacker-index"))

    authority = gate.validate_structural_authority(root, report)

    assert authority.trigger_commit == head


def test_structural_git_ignores_replace_refs(tmp_path: Path) -> None:
    root, fields, report_path, head, base = _authority_fixture(tmp_path / "repo")
    report = gate.parse_lane_v_report(report_path, _report_bytes(fields, head=head))
    tree = _git(root, "rev-parse", f"{head}^{{tree}}")
    attacker = subprocess.run(
        ["git", "commit-tree", tree, "-p", base],
        cwd=root,
        input="chore: attacker replacement\n",
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()
    _git(root, "replace", head, attacker)

    authority = gate.validate_structural_authority(root, report)

    assert authority.trigger_commit == head


def _legacy_manifest(*entries: tuple[str, str]) -> dict[str, object]:
    return {
        "schema_version": LEGACY_SCHEMA,
        "reports": [
            {"path": path, "sha256": digest} for path, digest in entries
        ],
    }


def test_legacy_manifest_accepts_exact_shape_and_defers_changed_digest() -> None:
    digest = hashlib.sha256(b"legacy body\n").hexdigest()
    manifest = _legacy_manifest((REPORT_PATH, digest))

    assert gate.legacy_manifest_violations(manifest, [REPORT_PATH]) == []


@pytest.mark.parametrize(
    "manifest",
    [
        pytest.param({}, id="missing-top-fields"),
        pytest.param(
            {"schema_version": "wrong", "reports": []}, id="wrong-schema"
        ),
        pytest.param(
            {"schema_version": LEGACY_SCHEMA, "reports": "not-a-list"},
            id="reports-not-list",
        ),
        pytest.param(
            {
                "schema_version": LEGACY_SCHEMA,
                "reports": [{"path": REPORT_PATH, "sha256": "A" * 64}],
            },
            id="uppercase-digest",
        ),
        pytest.param(
            {
                "schema_version": LEGACY_SCHEMA,
                "reports": [
                    {"path": REPORT_PATH, "sha256": "1" * 64},
                    {"path": REPORT_PATH, "sha256": "2" * 64},
                ],
            },
            id="duplicate-path",
        ),
        pytest.param(
            {
                "schema_version": LEGACY_SCHEMA,
                "reports": [
                    {"path": REPORT_PATH, "sha256": "1" * 64},
                    {
                        "path": REPORT_PATH.replace("05-00-00", "05-00-01"),
                        "sha256": "1" * 64,
                    },
                ],
            },
            id="duplicate-digest",
        ),
    ],
)
def test_legacy_manifest_rejects_invalid_shape_and_duplicates(
    manifest: object,
) -> None:
    assert gate.legacy_manifest_violations(manifest, [REPORT_PATH])


def test_legacy_manifest_reports_missing_paths_but_not_digest_drift() -> None:
    manifest = _legacy_manifest((REPORT_PATH, "1" * 64))

    missing = gate.legacy_manifest_violations(manifest, [])
    present_with_changed_digest = gate.legacy_manifest_violations(
        manifest, [REPORT_PATH]
    )

    assert missing == [f"{REPORT_PATH}: missing historical baseline report"]
    assert present_with_changed_digest == []
