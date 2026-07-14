"""Strict Lane V report-v2 and committed-authority gate tests."""

from __future__ import annotations

import dataclasses
import builtins
import hashlib
import json
import multiprocessing
import os
import stat
import subprocess
from collections.abc import Iterable, Mapping
from pathlib import Path
from types import MappingProxyType

import pytest

import opus_review_bridge as bridge
import opus_review_receipts as receipts
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


def _git_with_input(root: Path, raw: bytes, *args: str) -> str:
    completed = subprocess.run(
        ["env", "-u", "GIT_INDEX_FILE", "git", *args],
        cwd=root,
        check=True,
        input=raw,
        capture_output=True,
    )
    return completed.stdout.decode("ascii").strip()


def _git_object_exists(root: Path, object_name: str) -> bool:
    completed = subprocess.run(
        ["env", "-u", "GIT_INDEX_FILE", "git", "cat-file", "-e", object_name],
        cwd=root,
        check=False,
        capture_output=True,
    )
    return completed.returncode == 0


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
    _install_pipeline_markers(root)
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


def _structural_report(
    fields: list[tuple[str, str]], report_path: str
) -> gate.LaneVReport:
    sender = "operator2" if "-operator2-to-" in report_path else "operator"
    head = dict(fields)["Reviewed head"]
    return gate.parse_lane_v_report(
        report_path,
        _report_bytes(
            fields,
            head=head,
            h1_sender=sender.capitalize(),
            envelope_sender=sender,
        ),
    )


def _validate_structural_fixture(
    root: Path, fields: list[tuple[str, str]], report_path: str
) -> gate.StructuralAuthority:
    return gate.validate_structural_authority(
        root, _structural_report(fields, report_path)
    )


@pytest.mark.parametrize(
    ("mode", "trigger_kind", "recipient"),
    [
        ("codex-lane-v", "shipping-commit", "operator"),
        ("codex-lane-v", "verify-request", "operator"),
        ("claude-lane-v", "shipping-commit", "operator2"),
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


@pytest.mark.parametrize("mode", ("codex-lane-v", "claude-lane-v"))
@pytest.mark.parametrize(
    "malformation",
    (
        "missing-field",
        "duplicate-field",
        "short-sha",
        "uppercase-sha",
        "stale-commit",
        "uncommitted-event",
        "misplaced-event",
        "mismatched-scope",
    ),
)
def test_verify_request_authority_rejections_flip_to_one_lawful_trigger(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    mode: str,
    malformation: str,
) -> None:
    recipient = "operator" if mode == "codex-lane-v" else "operator2"
    root, lawful_fields, report_path, head, base = _authority_fixture(
        tmp_path / "repo",
        mode=mode,
        trigger_kind="verify-request",
        recipient=recipient,
    )
    values = dict(lawful_fields)
    _, trigger_commit, trigger_path = values["Trigger identity"].split(":", 2)
    malformed_fields = lawful_fields

    if malformation in {
        "missing-field",
        "duplicate-field",
        "short-sha",
        "uppercase-sha",
        "mismatched-scope",
    }:
        event_path = root / trigger_path
        event_text = event_path.read_text(encoding="utf-8")
        if malformation == "missing-field":
            event_text = event_text.replace(
                f"Lane-V-Scope: {values['Scope authority']}\n", ""
            )
        elif malformation == "duplicate-field":
            event_text = event_text.replace(
                "Event type: verify-request\n",
                "Event type: verify-request\nEvent type: verify-request\n",
            )
        elif malformation == "short-sha":
            event_text = event_text.replace(
                f"Reviewed head: {head}", f"Reviewed head: {head[:12]}"
            )
        elif malformation == "uppercase-sha":
            event_text = event_text.replace(
                f"Reviewed base: {base}", f"Reviewed base: {base.upper()}"
            )
        else:
            event_text = event_text.replace(
                f"Lane-V-Scope: {values['Scope authority']}",
                f"Lane-V-Scope: {DESCRIPTOR_PATH}@sha256:{'0' * 64}",
            )
        event_path.write_text(event_text, encoding="utf-8")
        _git(root, "add", trigger_path)
        _git(root, "commit", "--amend", "-q", "-m", "coord: request verification")
        malformed_commit = _git(root, "rev-parse", "HEAD")
        malformed_fields = _replace_field(
            lawful_fields,
            "Trigger identity",
            f"verify-request:{malformed_commit}:{trigger_path}",
        )
    elif malformation == "stale-commit":
        stale_tree = _git(root, "rev-parse", f"{trigger_commit}^{{tree}}")
        before_reviewed_head = _git(root, "rev-parse", f"{head}^")
        stale_commit = _git_with_input(
            root,
            b"coord: stale verification request\n",
            "commit-tree",
            stale_tree,
            "-p",
            before_reviewed_head,
        )
        malformed_fields = _replace_field(
            lawful_fields,
            "Trigger identity",
            f"verify-request:{stale_commit}:{trigger_path}",
        )
    elif malformation == "uncommitted-event":
        uncommitted_path = trigger_path.replace("05-01-00Z", "05-02-00Z")
        (root / uncommitted_path).write_text(
            (root / trigger_path).read_text(encoding="utf-8"), encoding="utf-8"
        )
        malformed_fields = _replace_field(
            lawful_fields,
            "Trigger identity",
            f"verify-request:{trigger_commit}:{uncommitted_path}",
        )
    else:
        misplaced_path = trigger_path.replace(
            "coordination/mailbox/sent/", "coordination/mailbox/drafts/"
        )
        misplaced_event = root / misplaced_path
        misplaced_event.parent.mkdir(parents=True)
        misplaced_event.write_bytes((root / trigger_path).read_bytes())
        _git(root, "add", misplaced_path)
        _git(root, "commit", "-q", "-m", "coord: misplace verification request")
        misplaced_commit = _git(root, "rev-parse", "HEAD")
        malformed_fields = _replace_field(
            lawful_fields,
            "Trigger identity",
            f"verify-request:{misplaced_commit}:{misplaced_path}",
        )

    malformed_values = dict(malformed_fields)
    _, malformed_commit, malformed_path = malformed_values[
        "Trigger identity"
    ].split(":", 2)
    if malformation in {"stale-commit", "misplaced-event"}:
        assert _git_object_exists(root, f"{malformed_commit}:{malformed_path}")
        assert _git(
            root, "rev-parse", f"{malformed_commit}:{malformed_path}"
        ) == _git(
            root, "rev-parse", f"{trigger_commit}:{trigger_path}"
        )
        expected_parent = (
            _git(root, "rev-parse", f"{head}^")
            if malformation == "stale-commit"
            else trigger_commit
        )
        assert _git(root, "rev-parse", f"{malformed_commit}^") == expected_parent

    expected_reason, expected_detail = {
        "missing-field": (
            "invalid_verify_request",
            "committed verify-request requires one exact Lane-V-Scope",
        ),
        "duplicate-field": (
            "invalid_verify_request",
            "committed verify-request requires one exact Event type",
        ),
        "short-sha": (
            "invalid_verify_request",
            "Reviewed head does not agree",
        ),
        "uppercase-sha": (
            "invalid_verify_request",
            "Reviewed base does not agree",
        ),
        "stale-commit": (
            "invalid_structural_authority",
            "verify-request trigger commit must be an ancestor",
        ),
        "uncommitted-event": (
            "invalid_structural_authority",
            "committed verify-request is missing at "
            f"{malformed_commit}:{malformed_path}",
        ),
        "misplaced-event": (
            "invalid_verify_request",
            "verify-request must be a sent mailbox event",
        ),
        "mismatched-scope": (
            "invalid_verify_request",
            "Scope authority does not agree",
        ),
    }[malformation]
    with pytest.raises(gate.ReportGateError) as rejection:
        _validate_structural_fixture(root, malformed_fields, report_path)
    assert rejection.value.reason == expected_reason
    assert rejection.value.detail == expected_detail

    if malformation == "stale-commit":
        require_strict_ancestor = gate._require_strict_ancestor

        def bypass_trigger_temporal_guard(
            repo_root: Path,
            ancestor: str,
            descendant: str,
            label: str,
        ) -> None:
            if label != "verify-request trigger commit":
                require_strict_ancestor(repo_root, ancestor, descendant, label)

        with monkeypatch.context() as temporal_guard:
            temporal_guard.setattr(
                gate, "_require_strict_ancestor", bypass_trigger_temporal_guard
            )
            unguarded = _validate_structural_fixture(
                root, malformed_fields, report_path
            )
        assert unguarded.trigger_commit == malformed_commit
        assert unguarded.trigger_path == malformed_path

    lawful = _validate_structural_fixture(root, lawful_fields, report_path)
    assert lawful.trigger_kind == "verify-request"
    assert lawful.trigger_commit == trigger_commit


@pytest.mark.parametrize("mode", ("codex-lane-v", "claude-lane-v"))
@pytest.mark.parametrize(
    "malformation",
    (
        "missing-trailer",
        "duplicate-trailer",
        "body-plus-trailer",
        "body-only",
        "non-terminal",
        "mismatched-trailer",
        "non-shipping-subject",
        "stale-commit",
    ),
)
def test_shipping_authority_rejections_flip_to_one_lawful_trigger(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    mode: str,
    malformation: str,
) -> None:
    recipient = "operator" if mode == "codex-lane-v" else "operator2"
    root, lawful_fields, report_path, head, _ = _authority_fixture(
        tmp_path / "repo",
        mode=mode,
        trigger_kind="shipping-commit",
        recipient=recipient,
    )
    scope_authority = dict(lawful_fields)["Scope authority"]
    malformed_fields = lawful_fields

    if malformation == "stale-commit":
        _git(
            root,
            "commit",
            "--allow-empty",
            "-q",
            "-m",
            "fix: alternate reviewed change",
            "-m",
            f"Lane-V-Scope: {scope_authority}",
        )
        stale_commit = _git(root, "rev-parse", "HEAD")
        malformed_fields = _replace_field(
            lawful_fields,
            "Trigger identity",
            f"shipping-commit:{stale_commit}",
        )
    else:
        subject = (
            "docs: reviewed change"
            if malformation == "non-shipping-subject"
            else "feat: reviewed change"
        )
        amend_args = ["commit", "--amend", "-q", "-m", subject]
        if malformation == "duplicate-trailer":
            amend_args.extend(
                ("-m", f"Lane-V-Scope: {scope_authority}\nLane-V-Scope: {scope_authority}")
            )
        elif malformation == "body-plus-trailer":
            amend_args.extend(
                (
                    "-m",
                    f"Authority context\nLane-V-Scope: {scope_authority}",
                    "-m",
                    f"Lane-V-Scope: {scope_authority}",
                )
            )
        elif malformation == "body-only":
            amend_args.extend(
                ("-m", f"Authority context\nLane-V-Scope: {scope_authority}")
            )
        elif malformation == "non-terminal":
            amend_args.extend(
                (
                    "-m",
                    f"Lane-V-Scope: {scope_authority}",
                    "-m",
                    "Context after the authority line",
                )
            )
        elif malformation == "mismatched-trailer":
            amend_args.extend(
                ("-m", f"Lane-V-Scope: {DESCRIPTOR_PATH}@sha256:{'0' * 64}")
            )
        elif malformation == "non-shipping-subject":
            amend_args.extend(("-m", f"Lane-V-Scope: {scope_authority}"))
        _git(root, *amend_args)
        malformed_head = _git(root, "rev-parse", "HEAD")
        malformed_fields = _replace_field(
            malformed_fields, "Reviewed head", malformed_head
        )
        malformed_fields = _replace_field(
            malformed_fields,
            "Trigger identity",
            f"shipping-commit:{malformed_head}",
        )

    expected_reason, expected_detail = {
        "missing-trailer": (
            "invalid_shipping_trigger",
            "shipping commit requires the report's exact Lane-V-Scope trailer",
        ),
        "duplicate-trailer": (
            "invalid_shipping_trigger",
            "shipping commit requires the report's exact Lane-V-Scope trailer",
        ),
        "body-plus-trailer": (
            "invalid_shipping_trigger",
            "shipping commit requires the report's exact Lane-V-Scope trailer",
        ),
        "body-only": (
            "invalid_shipping_trigger",
            "shipping commit requires the report's exact Lane-V-Scope trailer",
        ),
        "non-terminal": (
            "invalid_shipping_trigger",
            "shipping commit requires the report's exact Lane-V-Scope trailer",
        ),
        "mismatched-trailer": (
            "invalid_shipping_trigger",
            "shipping commit requires the report's exact Lane-V-Scope trailer",
        ),
        "non-shipping-subject": (
            "invalid_shipping_trigger",
            "shipping subject must be feat, fix, or refactor",
        ),
        "stale-commit": (
            "invalid_shipping_trigger",
            "shipping trigger must equal Reviewed head",
        ),
    }[malformation]
    with pytest.raises(gate.ReportGateError) as rejection:
        _validate_structural_fixture(root, malformed_fields, report_path)
    assert rejection.value.reason == expected_reason
    assert rejection.value.detail == expected_detail

    if malformation == "stale-commit":
        shipping_scope = gate._shipping_scope

        def bypass_shipping_head_equality(
            repo_root: Path,
            report: gate.LaneVReport,
            trigger_commit: str,
        ) -> receipts.ScopeReference:
            fields = MappingProxyType(
                {**report.fields, "Reviewed head": trigger_commit}
            )
            return shipping_scope(
                repo_root,
                dataclasses.replace(report, fields=fields),
                trigger_commit,
            )

        with monkeypatch.context() as head_equality:
            head_equality.setattr(
                gate, "_shipping_scope", bypass_shipping_head_equality
            )
            unguarded = _validate_structural_fixture(
                root, malformed_fields, report_path
            )
        assert unguarded.trigger_commit == stale_commit

    lawful = _validate_structural_fixture(root, lawful_fields, report_path)
    assert lawful.trigger_kind == "shipping-commit"
    assert lawful.trigger_commit == head


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


def test_live_publication_git_uses_absolute_positive_environment(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    fixture = _live_codex_fixture(tmp_path / "repo")
    candidate = _candidate_path(fixture.root, fixture.raw)
    attacker = tmp_path / "attacker-bin"
    attacker.mkdir()
    marker = tmp_path / "attacker-git-ran"
    fake_git = attacker / "git"
    fake_git.write_text(
        f"#!/bin/sh\n/usr/bin/touch {marker}\nexit 99\n", encoding="utf-8"
    )
    fake_git.chmod(0o755)
    hostile_home = tmp_path / "hostile-home"
    hostile_xdg = tmp_path / "hostile-xdg"
    hostile_home.mkdir()
    hostile_xdg.mkdir()
    (hostile_home / ".gitconfig").write_text(
        "[filter \"hostile\"]\n\tclean = /usr/bin/false\n", encoding="utf-8"
    )
    monkeypatch.setenv("PATH", str(attacker))
    monkeypatch.setenv("HOME", str(hostile_home))
    monkeypatch.setenv("XDG_CONFIG_HOME", str(hostile_xdg))
    monkeypatch.setenv("GIT_CONFIG_GLOBAL", str(hostile_home / ".gitconfig"))
    monkeypatch.setenv("PYTHONPATH", str(tmp_path / "shadow"))
    monkeypatch.setenv("BASH_ENV", str(tmp_path / "hostile-bash-env"))
    monkeypatch.setenv("DYLD_INSERT_LIBRARIES", str(tmp_path / "hostile.dylib"))

    published = gate.publish_candidate(
        repo_root=fixture.root,
        candidate_path=candidate,
        final_relative=fixture.report.relative_path,
        receipt_store_factory=lambda _root: fixture.store,
    )

    assert published.read_bytes() == fixture.raw
    assert not marker.exists()
    staged = subprocess.run(
        ["/usr/bin/git", "-C", str(fixture.root), "show", ":" + fixture.report.relative_path],
        check=True,
        capture_output=True,
        env={"PATH": "/usr/bin:/bin", "LANG": "C", "LC_ALL": "C"},
    ).stdout
    assert staged == fixture.raw


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


def _repository_identity(root: Path) -> str:
    common = Path(
        _git(root, "rev-parse", "--path-format=absolute", "--git-common-dir")
    ).resolve()
    return "sha256:" + hashlib.sha256(str(common).encode("utf-8")).hexdigest()


def _install_pipeline_markers(root: Path) -> None:
    (root / "AGENTS.md").write_text("fixture\n", encoding="utf-8")
    (root / "scripts" / "codex_protocol_model.py").write_text(
        "# fixture\n", encoding="utf-8"
    )
    agent = root / ".claude" / "agents" / "lane-v-verifier.md"
    agent.parent.mkdir(parents=True, exist_ok=True)
    agent.write_text("---\nname: fixture\n---\nfixture\n", encoding="utf-8")


@dataclasses.dataclass(frozen=True)
class _LiveCodexFixture:
    root: Path
    report: gate.LaneVReport
    authority: gate.StructuralAuthority
    store: receipts.ReceiptStore
    scope: receipts.ReviewScope
    reconciliation: bridge.ReconciliationReceiptResult
    raw: bytes


def _live_codex_fixture(
    root: Path,
    *,
    status: str = "pass",
    verdict: str = "GO",
    unavailable_reason: str = "process_failed",
    finding_severity: str = "minor",
    recipient: str = "operator",
    trigger_kind: str = "shipping-commit",
    default_store: bool = False,
) -> _LiveCodexFixture:
    root, fields, report_path, head, base = _authority_fixture(
        root,
        trigger_kind=trigger_kind,
        recipient=recipient,
    )
    preliminary = gate.parse_lane_v_report(
        report_path,
        _report_bytes(
            fields,
            head=head,
            h1_sender=recipient.capitalize(),
            envelope_sender=recipient,
        ),
    )
    authority = gate.validate_structural_authority(root, preliminary)
    _install_pipeline_markers(root)

    descriptor_blob = _git(
        root,
        "rev-parse",
        f"{authority.trigger_commit}:{authority.reference.descriptor_path}",
    )
    requirement_path = "requirements/task.md"
    requirement_raw = (root / requirement_path).read_bytes()
    trigger_blob = (
        _git(
            root,
            "rev-parse",
            f"{authority.trigger_commit}:{authority.trigger_path}",
        )
        if authority.trigger_path is not None
        else None
    )
    scope = receipts.ReviewScope(
        repository_identity=_repository_identity(root),
        task_id=authority.descriptor.task_id,
        question_id=authority.descriptor.question_id,
        trigger_kind=authority.trigger_kind,
        trigger_identity=authority.trigger_identity,
        trigger_commit=authority.trigger_commit,
        trigger_path=authority.trigger_path,
        trigger_blob_id=trigger_blob,
        descriptor_path=authority.reference.descriptor_path,
        descriptor_digest=authority.reference.descriptor_digest,
        descriptor_blob_id=descriptor_blob,
        review_profile=authority.descriptor.review_profile,
        verification_mode=authority.descriptor.verification_mode,
        verification_harness=authority.descriptor.verification_harness,
        authorization_identity="standing-policy:codex-lane-v-opus-v1",
        reviewed_head=head,
        requested_base=base,
        effective_base=base,
        changed_paths=(
            receipts.ChangedPath("M", "scripts/feature.py", b"scripts/feature.py"),
        ),
        requirements=(
            {
                "path": requirement_path,
                "blob_id": _git(root, "rev-parse", f"{head}:{requirement_path}"),
                "digest": "sha256:" + hashlib.sha256(requirement_raw).hexdigest(),
            },
        ),
        allowed_path_roots=authority.descriptor.allowed_path_roots,
        verification_commands=authority.descriptor.verification_commands,
    )
    store = receipts.ReceiptStore.for_repo(
        root, state_root=None if default_store else root / ".receipt-state"
    )
    finding = bridge.Finding(
        id="finding-1",
        severity=finding_severity,
        claim="fixture claim",
        location="scripts/feature.py:1",
        evidence="fixture evidence",
        reproduction="fixture reproduction",
    )
    if status == "unavailable":
        review = bridge.OpusReview.unavailable(
            reviewed_head=head,
            reviewed_base=base,
            review_profile=receipts.CODEX_MODE,
            authorization_source="standing-policy:codex-lane-v-opus-v1",
            reason=unavailable_reason,
        )
        dispositions: tuple[bridge.FindingDisposition, ...] = ()
    else:
        review = bridge.OpusReview(
            reviewed_head=head,
            reviewed_base=base,
            review_profile=receipts.CODEX_MODE,
            effective_model="claude-opus-4-7",
            status=status,
            findings=(finding,) if status == "issues" else (),
            authorization_source="standing-policy:codex-lane-v-opus-v1",
            unavailable_reason=None,
        )
        dispositions = (
            (bridge.FindingDisposition("finding-1", "confirmed", "confirmed"),)
            if status == "issues"
            else ()
        )
    with store.lock_attempt(scope, blocking=False) as attempt:
        attempt.reserve_or_load(scope)
        attempt.record_review(review.to_dict())
    reconciliation = bridge.reconcile_receipt(
        repo_root=root,
        receipt_id=receipts.compute_attempt_key(scope),
        expected_head=head,
        expected_base=base,
        codex_verdict=verdict,
        dispositions=dispositions,
        store_factory=lambda _root: store,
    )
    values = dict(fields)
    values.update(reconciliation.report_fields)
    bound_fields = [(label, values[label]) for label in gate.ATTESTATION_FIELDS]
    raw = _report_bytes(
        bound_fields,
        verdict=f"VERDICT: {verdict}",
        head=head,
        h1_sender=recipient.capitalize(),
        envelope_sender=recipient,
    )
    report = gate.parse_lane_v_report(report_path, raw)
    return _LiveCodexFixture(
        root=root,
        report=report,
        authority=authority,
        store=store,
        scope=scope,
        reconciliation=reconciliation,
        raw=raw,
    )


@pytest.mark.parametrize(
    ("status", "verdict", "reason", "severity"),
    [
        ("pass", "GO", "process_failed", "minor"),
        ("unavailable", "GO", "process_failed", "minor"),
        ("issues", "NITS", "process_failed", "minor"),
        ("issues", "FAIL", "process_failed", "critical"),
    ],
)
def test_live_codex_binding_accepts_exact_reconciled_report(
    tmp_path: Path,
    status: str,
    verdict: str,
    reason: str,
    severity: str,
) -> None:
    fixture = _live_codex_fixture(
        tmp_path / "repo",
        status=status,
        verdict=verdict,
        unavailable_reason=reason,
        finding_severity=severity,
    )

    validated = gate.validate_live_report(
        fixture.root,
        fixture.report,
        receipt_store_factory=lambda _root: fixture.store,
    )

    assert validated == fixture.authority


def test_live_codex_binding_rejects_legacy_underclassified_reconciliation(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    production_reconcile = bridge._reconcile_review

    def legacy_permissive_reconcile(
        codex_verdict: str,
        review: bridge.OpusReview,
        dispositions: Iterable[bridge.FindingDisposition],
        *,
        expected_head: str,
        expected_base: str | None,
    ) -> bridge.Reconciliation:
        fail_result = production_reconcile(
            "FAIL",
            review,
            dispositions,
            expected_head=expected_head,
            expected_base=expected_base,
        )
        return dataclasses.replace(
            fail_result, codex_verdict=codex_verdict, go_allowed=False
        )

    with monkeypatch.context() as legacy:
        legacy.setattr(
            bridge, "_reconcile_review", legacy_permissive_reconcile
        )
        fixture = _live_codex_fixture(
            tmp_path / "repo",
            status="issues",
            verdict="NITS",
            finding_severity="important",
        )

    with pytest.raises(gate.ReportGateError, match="invalid_live_receipt"):
        gate.validate_live_report(
            fixture.root,
            fixture.report,
            receipt_store_factory=lambda _root: fixture.store,
        )


@pytest.mark.parametrize("mutation", ["unknown", "wrong-type"])
def test_live_codex_binding_rejects_malformed_scope_before_comparison(
    tmp_path: Path, mutation: str
) -> None:
    fixture = _live_codex_fixture(tmp_path / "repo")
    record_path = next(fixture.store.state_root.glob("*.json"))
    value = json.loads(record_path.read_text(encoding="utf-8"))
    if mutation == "unknown":
        value["scope"]["unknown"] = "field"
    else:
        value["scope"]["reviewed_head"] = 7
    scope_digest = "sha256:" + hashlib.sha256(
        receipts.canonical_json_bytes(value["scope"])
    ).hexdigest()
    value["scope_digest"] = scope_digest
    record_path.write_bytes(receipts.canonical_json_bytes(value))
    fields = dict(fixture.report.fields)
    fields["Opus scope digest"] = scope_digest

    with pytest.raises(gate.ReportGateError, match="invalid_live_receipt"):
        gate.validate_live_report(
            fixture.root,
            _mutated_report(fixture.report, fields=fields),
            receipt_store_factory=lambda _root: fixture.store,
        )


def _mutated_report(
    report: gate.LaneVReport,
    *,
    fields: Mapping[str, str] | None = None,
    **changes: object,
) -> gate.LaneVReport:
    if fields is not None:
        changes["fields"] = MappingProxyType(dict(fields))
    return dataclasses.replace(report, **changes)


@pytest.mark.parametrize(
    ("label", "value"),
    [
        ("Verification task ID", "aaaaaaaa-bbbb-4ccc-8ddd-eeeeeeeeeeee"),
        ("Verification harness", "claude:lane-v-verifier"),
        ("Scope authority", f"{DESCRIPTOR_PATH}@sha256:" + "0" * 64),
        ("Trigger identity", "shipping-commit:" + "0" * 40),
        ("Reviewed head", "0" * 40),
        ("Reviewed base", "1" * 40),
        ("Review profile", "claude-lane-v"),
        ("Authorization identity", "user-task:other"),
        ("Opus receipt ID", "opr1:" + "0" * 64),
        ("Opus scope digest", "sha256:" + "0" * 64),
        ("Cross-model review", "unavailable"),
        ("Effective Opus model", "claude-opus-4-8"),
        ("Opus finding dispositions", "{}"),
        (
            "Reconciliation guard",
            json.dumps(
                {"digest": "sha256:" + "0" * 64, "go_allowed": True},
                sort_keys=True,
                separators=(",", ":"),
            ),
        ),
        ("Degraded reason", "timeout"),
    ],
)
def test_live_codex_binding_rejects_each_changed_report_claim(
    tmp_path: Path, label: str, value: str
) -> None:
    fixture = _live_codex_fixture(tmp_path / "repo")
    fields = dict(fixture.report.fields)
    fields[label] = value

    with pytest.raises(gate.ReportGateError):
        gate.validate_live_report(
            fixture.root,
            _mutated_report(fixture.report, fields=fields),
            receipt_store_factory=lambda _root: fixture.store,
        )


@pytest.mark.parametrize("verdict", ["NITS", "FAIL"])
def test_live_codex_binding_rejects_exact_stored_verdict_substitution(
    tmp_path: Path, verdict: str
) -> None:
    stored_verdict = "FAIL" if verdict == "NITS" else "NITS"
    fixture = _live_codex_fixture(
        tmp_path / "repo", status="issues", verdict=stored_verdict
    )

    with pytest.raises(gate.ReportGateError, match="verdict"):
        gate.validate_live_report(
            fixture.root,
            _mutated_report(fixture.report, verdict=verdict),
            receipt_store_factory=lambda _root: fixture.store,
        )


def test_live_codex_checks_verdict_before_go_allowed_consistency(tmp_path: Path) -> None:
    fixture = _live_codex_fixture(tmp_path / "repo")
    fields = dict(fixture.report.fields)
    guard = json.loads(fields["Reconciliation guard"])
    guard["go_allowed"] = False
    fields["Reconciliation guard"] = json.dumps(
        guard, sort_keys=True, separators=(",", ":")
    )

    with pytest.raises(gate.ReportGateError, match="verdict_mismatch"):
        gate.validate_live_report(
            fixture.root,
            _mutated_report(fixture.report, fields=fields, verdict="FAIL"),
            receipt_store_factory=lambda _root: fixture.store,
        )


@pytest.mark.parametrize("sender", ["director", "coordinator", "operator3"])
def test_live_report_sender_is_always_an_operator(tmp_path: Path, sender: str) -> None:
    fixture = _live_codex_fixture(tmp_path / "repo")

    with pytest.raises(gate.ReportGateError, match="sender"):
        gate.validate_live_report(
            fixture.root,
            _mutated_report(fixture.report, sender=sender),
            receipt_store_factory=lambda _root: fixture.store,
        )


@pytest.mark.parametrize("state", ["missing", "reserved", "reviewed"])
def test_live_codex_binding_rejects_nonreconciled_receipt_state(
    tmp_path: Path, state: str
) -> None:
    fixture = _live_codex_fixture(tmp_path / "repo")
    other = receipts.ReceiptStore.for_repo(
        fixture.root, state_root=fixture.root / f".{state}-state"
    )
    if state != "missing":
        with other.lock_attempt(fixture.scope, blocking=False) as attempt:
            attempt.reserve_or_load(fixture.scope)
            if state == "reviewed":
                with fixture.store.lock_receipt(
                    fixture.reconciliation.receipt_id, blocking=False
                ) as source:
                    review = source.load_existing().review
                assert review is not None
                attempt.record_review(review)

    with pytest.raises((gate.ReportGateError, receipts.ReceiptStateError)):
        gate.validate_live_report(
            fixture.root,
            fixture.report,
            receipt_store_factory=lambda _root: other,
        )


def test_live_verify_request_sender_must_equal_authorized_operator(tmp_path: Path) -> None:
    fixture = _live_codex_fixture(
        tmp_path / "repo",
        recipient="operator2",
        trigger_kind="verify-request",
    )

    gate.validate_live_report(
        fixture.root,
        fixture.report,
        receipt_store_factory=lambda _root: fixture.store,
    )
    with pytest.raises(gate.ReportGateError, match="recipient"):
        gate.validate_live_report(
            fixture.root,
            _mutated_report(fixture.report, sender="operator"),
            receipt_store_factory=lambda _root: fixture.store,
        )


@dataclasses.dataclass(frozen=True)
class _LiveClaudeFixture:
    root: Path
    report: gate.LaneVReport
    authority: gate.StructuralAuthority
    raw: bytes


def _live_claude_fixture(root: Path) -> _LiveClaudeFixture:
    root, fields, report_path, head, _ = _authority_fixture(
        root,
        mode=receipts.CLAUDE_MODE,
        trigger_kind="verify-request",
        recipient="operator2",
    )
    raw = _report_bytes(
        fields,
        head=head,
        h1_sender="Operator2",
        envelope_sender="operator2",
    )
    report = gate.parse_lane_v_report(report_path, raw)
    authority = gate.validate_structural_authority(root, report)
    return _LiveClaudeFixture(root, report, authority, raw)


def _candidate_path(root: Path, raw: bytes, name: str = ".report.candidate.tmp") -> Path:
    sent = root / "coordination" / "mailbox" / "sent"
    sent.mkdir(parents=True, exist_ok=True)
    candidate = sent / name
    candidate.write_bytes(raw)
    candidate.chmod(0o600)
    return candidate


def test_non_codex_live_validation_creates_exact_ready_task_record(
    tmp_path: Path,
) -> None:
    fixture = _live_claude_fixture(tmp_path / "repo")
    store = gate.TaskPublicationStore.for_repo(
        fixture.root, state_root=fixture.root / ".task-publications"
    )

    validated = gate.validate_live_report(
        fixture.root,
        fixture.report,
        task_store_factory=lambda _root: store,
    )

    assert validated == fixture.authority
    with store.lock_task(TASK_ID) as task:
        record = task.load_existing()
    assert record.state == "ready"
    assert record.generation == 1
    assert record.task_id == TASK_ID
    assert record.authority_digest.startswith("sha256:")
    assert (
        record.path,
        record.candidate_digest,
        record.candidate_name,
        record.candidate_device,
        record.candidate_inode,
        record.index_blob_oid,
        record.index_mode,
        record.index_stage,
    ) == (None, None, None, None, None, None, None, None)


@pytest.mark.parametrize("replacement", ["missing", "directory", "symlink"])
def test_gate_rejects_missing_or_replaced_pipeline_marker_before_state_access(
    tmp_path: Path, replacement: str
) -> None:
    fixture = _live_claude_fixture(tmp_path / "repo")
    marker = fixture.root / "AGENTS.md"
    marker.unlink()
    if replacement == "directory":
        marker.mkdir()
    elif replacement == "symlink":
        target = tmp_path / "attacker-marker"
        target.write_text("attacker\n", encoding="utf-8")
        marker.symlink_to(target)

    with pytest.raises(gate.ReportGateError, match="invalid_repository"):
        gate.validate_live_report(fixture.root, fixture.report)

    assert not (
        fixture.root / ".codex/runtime/lane-v-report-publications/v1"
    ).exists()


def test_non_codex_publish_and_status_retain_exact_task_index_witness(
    tmp_path: Path,
) -> None:
    fixture = _live_claude_fixture(tmp_path / "repo")
    store = gate.TaskPublicationStore.for_repo(
        fixture.root, state_root=fixture.root / ".task-publications"
    )
    candidate = _candidate_path(fixture.root, fixture.raw)

    published = gate.publish_candidate(
        repo_root=fixture.root,
        candidate_path=candidate,
        final_relative=fixture.report.relative_path,
        task_store_factory=lambda _root: store,
    )

    assert published.read_bytes() == fixture.raw
    with store.lock_task(TASK_ID) as task:
        record = task.load_existing()
    assert record.state == "published"
    assert record.generation == 3
    assert record.path == fixture.report.relative_path
    assert record.index_mode == "100644"
    assert record.index_stage == 0
    assert isinstance(record.index_blob_oid, str)
    status = gate.publication_status(
        repo_root=fixture.root,
        task_id=TASK_ID,
        task_store_factory=lambda _root: store,
    )
    assert status["state"] == "published"
    assert status["file_witness_match"] is True
    assert status["staged_blob_match"] is True


def _task_store_fixture(
    root: Path,
) -> tuple[
    _LiveClaudeFixture,
    gate.TaskPublicationStore,
    tuple[str, str, str, int, int, str, str, int],
]:
    fixture = _live_claude_fixture(root)
    store = gate.TaskPublicationStore.for_repo(
        fixture.root, state_root=fixture.root / ".task-publications"
    )
    gate.validate_live_report(
        fixture.root,
        fixture.report,
        task_store_factory=lambda _root: store,
    )
    candidate = _candidate_path(fixture.root, fixture.raw)
    observed = candidate.stat()
    witness = (
        fixture.report.relative_path,
        "sha256:" + hashlib.sha256(fixture.raw).hexdigest(),
        candidate.name,
        observed.st_dev,
        observed.st_ino,
        _git_with_input(
            fixture.root, fixture.raw, "hash-object", "--no-filters", "--stdin"
        ),
        "100644",
        0,
    )
    return fixture, store, witness


def test_task_publication_store_enforces_authority_and_exact_transitions(
    tmp_path: Path,
) -> None:
    fixture = _live_claude_fixture(tmp_path / "repo")
    store = gate.TaskPublicationStore.for_repo(
        fixture.root, state_root=fixture.root / ".task-publications"
    )
    gate.validate_live_report(
        fixture.root,
        fixture.report,
        task_store_factory=lambda _root: store,
    )
    candidate = _candidate_path(fixture.root, fixture.raw)
    observed = candidate.stat()
    digest = "sha256:" + hashlib.sha256(fixture.raw).hexdigest()
    oid = _git_with_input(
        fixture.root, fixture.raw, "hash-object", "--no-filters", "--stdin"
    )
    witness = (
        fixture.report.relative_path,
        digest,
        candidate.name,
        observed.st_dev,
        observed.st_ino,
        oid,
        "100644",
        0,
    )
    with store.lock_task(TASK_ID) as task:
        ready = task.load_existing()
        publishing = task.begin_publication(*witness)
        assert task.begin_publication(*witness) == publishing
        with pytest.raises(gate.ReportGateError, match="replay"):
            task.begin_publication(*witness[:-3], "f" * 40, "100644", 0)
        cancelled = task.cancel_publication(*witness, publishing.generation)
        restarted = task.begin_publication(*witness)
        finished = task.finish_publication(*witness)
    assert ready.generation == 1
    assert publishing.generation == 2
    assert cancelled.state == "ready" and cancelled.generation == 3
    assert restarted.state == "publishing" and restarted.generation == 4
    assert finished.state == "published" and finished.generation == 5
    with store.lock_task(TASK_ID) as task:
        with pytest.raises(gate.ReportGateError, match="task_authority_conflict"):
            task.load_or_create("sha256:" + "9" * 64)


def test_task_cancel_requires_exact_integer_generation_and_exact_witness(
    tmp_path: Path,
) -> None:
    fixture, store, witness = _task_store_fixture(tmp_path / "repo")
    with store.lock_task(TASK_ID) as task:
        ready = task.load_existing()
        with pytest.raises(gate.ReportGateError, match="replay"):
            task.cancel_publication(*witness, ready.generation)
        publishing = task.begin_publication(*witness)
        for generation in (2.0, True, publishing.generation + 2):
            with pytest.raises(gate.ReportGateError, match="replay"):
                task.cancel_publication(*witness, generation)
        changed = list(witness)
        changed[1] = "sha256:" + "9" * 64
        with pytest.raises(gate.ReportGateError, match="replay"):
            task.cancel_publication(*changed, publishing.generation)
        task.finish_publication(*witness)
        with pytest.raises(gate.ReportGateError, match="replay"):
            task.cancel_publication(*witness, publishing.generation + 1)
    with store.lock_task(TASK_ID) as task:
        assert task.load_existing().state == "published"


@pytest.mark.parametrize(
    "mutation",
    ["device-float", "inode-float", "device-bool", "inode-bool"],
)
def test_task_recovery_requires_exact_integer_observed_inode_witness(
    tmp_path: Path,
    mutation: str,
) -> None:
    fixture, store, witness = _task_store_fixture(tmp_path / "repo")
    device: object = witness[3]
    inode: object = witness[4]
    if mutation == "device-float":
        device = float(device)
    elif mutation == "inode-float":
        inode = float(inode)
    elif mutation == "device-bool":
        device = True
    else:
        inode = False
    with store.lock_task(TASK_ID) as task:
        task.load_existing()
        task.begin_publication(*witness)
        with pytest.raises(gate.ReportGateError, match="invalid_task_publication"):
            task.recover_publication(witness[0], witness[1], device, inode)
        assert task.load_existing().state == "publishing"


@pytest.mark.parametrize(
    "case",
    [
        "unknown-field",
        "ready-nonnull",
        "publishing-null",
        "published-null",
        "generation-bool",
        "generation-minimum",
        "generation-parity",
        "generation-float",
        "device-bool",
        "inode-float",
        "stage-bool",
        "mode-nonstring",
    ],
)
def test_task_publication_store_rejects_full_malformed_record_matrix(
    tmp_path: Path,
    case: str,
) -> None:
    fixture, store, witness = _task_store_fixture(tmp_path / "repo")
    record_path = store.state_root / f"{TASK_ID}.json"
    value = json.loads(record_path.read_text(encoding="utf-8"))
    witness_mapping = dict(zip(gate._TASK_WITNESS_FIELDS, witness, strict=True))
    if case == "unknown-field":
        value["unknown"] = "field"
    elif case == "ready-nonnull":
        value["path"] = witness[0]
    elif case in {"publishing-null", "published-null"}:
        value["state"] = case.split("-", 1)[0]
        value["generation"] = 2 if value["state"] == "publishing" else 3
    elif case == "generation-bool":
        value["generation"] = True
    elif case == "generation-minimum":
        value["generation"] = 0
    elif case == "generation-parity":
        value["generation"] = 2
    elif case == "generation-float":
        value["generation"] = 1.0
    else:
        value["state"] = "publishing"
        value["generation"] = 2
        value.update(witness_mapping)
        if case == "device-bool":
            value["candidate_device"] = True
        elif case == "inode-float":
            value["candidate_inode"] = 1.0
        elif case == "stage-bool":
            value["index_stage"] = False
        else:
            value["index_mode"] = 100644
    record_path.write_bytes(receipts.canonical_json_bytes(value))

    with store.lock_task(TASK_ID) as task:
        with pytest.raises(gate.ReportGateError, match="invalid_task_publication"):
            task.load_existing()


def test_task_recovery_negative_matrix_and_authority_conflict_remain_closed(
    tmp_path: Path,
) -> None:
    fixture, store, witness = _task_store_fixture(tmp_path / "repo")
    with store.lock_task(TASK_ID) as task:
        ready = task.load_existing()
        with pytest.raises(gate.ReportGateError, match="transition"):
            task.recover_publication(witness[0], None, None, None)
        task.begin_publication(*witness)
        other_path = witness[0].replace("05-00-00Z", "05-00-01Z")
        assert other_path != witness[0]
        with pytest.raises(gate.ReportGateError, match="replay"):
            task.recover_publication(other_path, None, None, None)
        with pytest.raises(gate.ReportGateError, match="invalid_task_publication"):
            task.recover_publication(witness[0], None, witness[3], None)
        with pytest.raises(gate.ReportGateError, match="replay"):
            task.recover_publication(
                witness[0], "sha256:" + "9" * 64, witness[3], witness[4]
            )
        assert (
            task.recover_publication(witness[0], witness[1], witness[3], witness[4])
            == "finalize"
        )
    with store.lock_task(TASK_ID) as task:
        assert task.load_existing().state == "publishing"
        with pytest.raises(gate.ReportGateError, match="task_authority_conflict"):
            task.load_or_create("sha256:" + "9" * 64)


def test_task_publication_store_rejects_malformed_index_witness(
    tmp_path: Path,
) -> None:
    fixture = _live_claude_fixture(tmp_path / "repo")
    store = gate.TaskPublicationStore.for_repo(
        fixture.root, state_root=fixture.root / ".task-publications"
    )
    gate.validate_live_report(
        fixture.root,
        fixture.report,
        task_store_factory=lambda _root: store,
    )
    record_path = store.state_root / f"{TASK_ID}.json"
    value = json.loads(record_path.read_text(encoding="utf-8"))
    value["state"] = "publishing"
    value["generation"] = 2
    value.update(
        {
            "path": fixture.report.relative_path,
            "candidate_digest": "sha256:" + "1" * 64,
            "candidate_name": ".candidate.tmp",
            "candidate_device": 1,
            "candidate_inode": 1,
            "index_blob_oid": "a" * 40,
            "index_mode": "100644",
            "index_stage": False,
        }
    )
    record_path.write_bytes(receipts.canonical_json_bytes(value))

    with store.lock_task(TASK_ID) as task:
        with pytest.raises(gate.ReportGateError, match="invalid_task_publication"):
            task.load_existing()


def test_publish_candidate_creates_exact_no_replace_hard_link(
    tmp_path: Path,
) -> None:
    fixture = _live_codex_fixture(tmp_path / "repo")
    candidate = _candidate_path(fixture.root, fixture.raw)
    before = candidate.stat()
    captured = candidate.read_bytes()

    published = gate.publish_candidate(
        repo_root=fixture.root,
        candidate_path=candidate,
        final_relative=fixture.report.relative_path,
        receipt_store_factory=lambda _root: fixture.store,
    )

    assert published == fixture.root / fixture.report.relative_path
    assert published.read_bytes() == captured
    assert not candidate.exists()
    after = published.stat()
    assert (after.st_dev, after.st_ino, after.st_nlink) == (
        before.st_dev,
        before.st_ino,
        1,
    )
    with fixture.store.lock_receipt(fixture.reconciliation.receipt_id) as attempt:
        record = attempt.load_existing()
    assert record.state == "published"
    expected_oid = _git_with_input(
        fixture.root, captured, "hash-object", "--no-filters", "--stdin"
    )
    assert record.publication == {
        "path": fixture.report.relative_path,
        "candidate_digest": "sha256:" + hashlib.sha256(captured).hexdigest(),
        "candidate_name": ".report.candidate.tmp",
        "candidate_device": before.st_dev,
        "candidate_inode": before.st_ino,
        "index_blob_oid": expected_oid,
        "index_mode": "100644",
        "index_stage": 0,
    }
    assert _git(fixture.root, "ls-files", "--stage", "--", fixture.report.relative_path) == (
        f"100644 {expected_oid} 0\t{fixture.report.relative_path}"
    )
    assert subprocess.run(
        ["env", "-u", "GIT_INDEX_FILE", "git", "cat-file", "blob", expected_oid],
        cwd=fixture.root,
        check=True,
        capture_output=True,
    ).stdout == captured


def test_publication_status_is_sanitized_and_published_resume_is_rejected(
    tmp_path: Path,
) -> None:
    fixture = _live_codex_fixture(tmp_path / "repo")
    before = gate.publication_status(
        repo_root=fixture.root,
        receipt_id=fixture.reconciliation.receipt_id,
        receipt_store_factory=lambda _root: fixture.store,
    )
    assert before == {
        "state": "reconciled",
        "path": None,
        "file_witness_match": False,
        "index_blob_oid": None,
        "staged_blob_match": False,
    }
    candidate = _candidate_path(fixture.root, fixture.raw)
    gate.publish_candidate(
        repo_root=fixture.root,
        candidate_path=candidate,
        final_relative=fixture.report.relative_path,
        receipt_store_factory=lambda _root: fixture.store,
    )

    status = gate.publication_status(
        repo_root=fixture.root,
        receipt_id=fixture.reconciliation.receipt_id,
        receipt_store_factory=lambda _root: fixture.store,
    )

    assert status["state"] == "published"
    assert status["path"] == fixture.report.relative_path
    assert status["file_witness_match"] is True
    assert status["staged_blob_match"] is True
    assert isinstance(status["index_blob_oid"], str)
    assert set(status) == {
        "state",
        "path",
        "file_witness_match",
        "index_blob_oid",
        "staged_blob_match",
    }
    with pytest.raises(gate.ReportGateError, match="published state"):
        gate.resume_publication(
            repo_root=fixture.root,
            receipt_id=fixture.reconciliation.receipt_id,
            receipt_store_factory=lambda _root: fixture.store,
        )


def test_status_and_resume_converge_already_correct_index_after_interruption(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    fixture = _live_codex_fixture(tmp_path / "repo")
    candidate = _candidate_path(fixture.root, fixture.raw)

    def fail_after_index(label: str) -> None:
        if label == "after_index_update":
            raise RuntimeError("injected post-index crash")

    monkeypatch.setattr(gate, "_publication_checkpoint", fail_after_index)
    with pytest.raises(gate.ReportGateError, match="publication_resumable"):
        gate.publish_candidate(
            repo_root=fixture.root,
            candidate_path=candidate,
            final_relative=fixture.report.relative_path,
            receipt_store_factory=lambda _root: fixture.store,
        )
    status = gate.publication_status(
        repo_root=fixture.root,
        receipt_id=fixture.reconciliation.receipt_id,
        receipt_store_factory=lambda _root: fixture.store,
    )
    assert status["state"] == "publishing"
    assert status["file_witness_match"] is True
    assert status["staged_blob_match"] is True

    published = gate.resume_publication(
        repo_root=fixture.root,
        receipt_id=fixture.reconciliation.receipt_id,
        receipt_store_factory=lambda _root: fixture.store,
    )
    assert published == fixture.root / fixture.report.relative_path


def test_fresh_cleanup_reproves_candidate_basename_before_unlink(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    fixture = _live_codex_fixture(tmp_path / "repo")
    candidate = _candidate_path(fixture.root, fixture.raw)
    saved = candidate.with_name(".saved-original.tmp")
    replacement = b"unrelated replacement must survive\n"

    def swap_name(label: str) -> None:
        if label == "before_candidate_unlink":
            candidate.rename(saved)
            candidate.write_bytes(replacement)
            candidate.chmod(0o600)

    monkeypatch.setattr(gate, "_publication_checkpoint", swap_name)
    with pytest.raises(gate.ReportGateError, match="publication_resumable"):
        gate.publish_candidate(
            repo_root=fixture.root,
            candidate_path=candidate,
            final_relative=fixture.report.relative_path,
            receipt_store_factory=lambda _root: fixture.store,
        )
    assert candidate.read_bytes() == replacement
    assert saved.read_bytes() == fixture.raw
    with fixture.store.lock_receipt(fixture.reconciliation.receipt_id) as attempt:
        assert attempt.load_existing().state == "publishing"


def test_resume_cleanup_reproves_candidate_basename_before_unlink(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    fixture = _live_codex_fixture(tmp_path / "repo")
    candidate = _candidate_path(fixture.root, fixture.raw, ".interrupted.tmp")
    _begin_interrupted_publication(
        fixture, candidate, fixture.report.relative_path
    )
    saved = candidate.with_name(".saved-interrupted.tmp")
    replacement = b"resume replacement must survive\n"

    def swap_name(label: str) -> None:
        if label == "resume_before_candidate_unlink":
            candidate.rename(saved)
            candidate.write_bytes(replacement)
            candidate.chmod(0o600)

    monkeypatch.setattr(gate, "_publication_checkpoint", swap_name)
    with pytest.raises(gate.ReportGateError, match="candidate_changed"):
        gate.resume_publication(
            repo_root=fixture.root,
            receipt_id=fixture.reconciliation.receipt_id,
            receipt_store_factory=lambda _root: fixture.store,
        )
    assert candidate.read_bytes() == replacement
    assert saved.read_bytes() == fixture.raw
    with fixture.store.lock_receipt(fixture.reconciliation.receipt_id) as attempt:
        assert attempt.load_existing().state == "publishing"


def test_fresh_link_reproves_candidate_basename_immediately_before_link(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    fixture = _live_codex_fixture(tmp_path / "repo")
    candidate = _candidate_path(fixture.root, fixture.raw)
    saved = candidate.with_name(".saved-before-link.tmp")
    replacement = b"foreign fresh link target\n"

    def swap_name(label: str) -> None:
        if label == "before_link":
            candidate.rename(saved)
            candidate.write_bytes(replacement)
            candidate.chmod(0o600)

    monkeypatch.setattr(gate, "_publication_checkpoint", swap_name)
    with pytest.raises(gate.ReportGateError):
        gate.publish_candidate(
            repo_root=fixture.root,
            candidate_path=candidate,
            final_relative=fixture.report.relative_path,
            receipt_store_factory=lambda _root: fixture.store,
        )

    assert not (fixture.root / fixture.report.relative_path).exists()
    assert candidate.read_bytes() == replacement
    assert saved.read_bytes() == fixture.raw


def test_resume_link_reproves_candidate_basename_immediately_before_link(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    fixture = _live_codex_fixture(tmp_path / "repo")
    candidate = _candidate_path(fixture.root, fixture.raw, ".interrupted.tmp")
    _begin_interrupted_publication(
        fixture, candidate, fixture.report.relative_path
    )
    saved = candidate.with_name(".saved-before-resume-link.tmp")
    replacement = b"foreign resume link target\n"

    def swap_name(label: str) -> None:
        if label == "resume_before_link":
            candidate.rename(saved)
            candidate.write_bytes(replacement)
            candidate.chmod(0o600)

    monkeypatch.setattr(gate, "_publication_checkpoint", swap_name)
    with pytest.raises(gate.ReportGateError):
        gate.resume_publication(
            repo_root=fixture.root,
            receipt_id=fixture.reconciliation.receipt_id,
            receipt_store_factory=lambda _root: fixture.store,
        )

    assert not (fixture.root / fixture.report.relative_path).exists()
    assert candidate.read_bytes() == replacement
    assert saved.read_bytes() == fixture.raw


def test_published_status_rejects_surviving_candidate_and_two_link_final(
    tmp_path: Path,
) -> None:
    fixture = _live_codex_fixture(tmp_path / "repo")
    candidate = _candidate_path(fixture.root, fixture.raw)
    published = gate.publish_candidate(
        repo_root=fixture.root,
        candidate_path=candidate,
        final_relative=fixture.report.relative_path,
        receipt_store_factory=lambda _root: fixture.store,
    )
    os.link(published, candidate)

    with pytest.raises(gate.ReportGateError, match="published_witness_divergence"):
        gate.publication_status(
            repo_root=fixture.root,
            receipt_id=fixture.reconciliation.receipt_id,
            receipt_store_factory=lambda _root: fixture.store,
        )


@pytest.mark.parametrize("index_kind", ["exact", "mismatch"])
def test_absent_resume_refuses_to_clear_any_staged_index_entry(
    tmp_path: Path, index_kind: str
) -> None:
    fixture = _live_codex_fixture(tmp_path / "repo")
    candidate = _candidate_path(fixture.root, fixture.raw, ".interrupted.tmp")
    _begin_interrupted_publication(
        fixture, candidate, fixture.report.relative_path
    )
    candidate.unlink()
    staged_raw = fixture.raw if index_kind == "exact" else b"foreign staged bytes\n"
    oid = _git_with_input(
        fixture.root,
        staged_raw,
        "hash-object",
        "-w",
        "--no-filters",
        "--stdin",
    )
    _git(
        fixture.root,
        "update-index",
        "--add",
        "--cacheinfo",
        f"100644,{oid},{fixture.report.relative_path}",
    )

    with pytest.raises(gate.ReportGateError, match="index_entry_conflict"):
        gate.resume_publication(
            repo_root=fixture.root,
            receipt_id=fixture.reconciliation.receipt_id,
            receipt_store_factory=lambda _root: fixture.store,
        )
    with fixture.store.lock_receipt(fixture.reconciliation.receipt_id) as attempt:
        assert attempt.load_existing().state == "publishing"


def test_absent_resume_clears_only_without_index_and_ignores_object_only_leftover(
    tmp_path: Path,
) -> None:
    fixture = _live_codex_fixture(tmp_path / "repo")
    candidate = _candidate_path(fixture.root, fixture.raw, ".interrupted.tmp")
    _begin_interrupted_publication(
        fixture, candidate, fixture.report.relative_path
    )
    _git_with_input(
        fixture.root,
        fixture.raw,
        "hash-object",
        "-w",
        "--no-filters",
        "--stdin",
    )
    candidate.unlink()

    with pytest.raises(gate.ReportGateError, match="reservation cleared"):
        gate.resume_publication(
            repo_root=fixture.root,
            receipt_id=fixture.reconciliation.receipt_id,
            receipt_store_factory=lambda _root: fixture.store,
        )
    with fixture.store.lock_receipt(fixture.reconciliation.receipt_id) as attempt:
        record = attempt.load_existing()
    assert record.state == "reconciled"
    assert record.generation == 5
    assert record.publication is None


@pytest.mark.parametrize("appearance", ["candidate", "final", "index"])
def test_absent_resume_rechecks_names_and_index_immediately_before_clear(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    appearance: str,
) -> None:
    fixture = _live_codex_fixture(tmp_path / "repo")
    candidate = _candidate_path(fixture.root, fixture.raw, ".interrupted.tmp")
    _begin_interrupted_publication(
        fixture, candidate, fixture.report.relative_path
    )
    candidate.unlink()
    final = fixture.root / fixture.report.relative_path

    def introduce_state(label: str) -> None:
        if label != "resume_before_absent_directory_fsync":
            return
        if appearance == "candidate":
            candidate.write_bytes(b"new candidate\n")
            candidate.chmod(0o600)
        elif appearance == "final":
            final.write_bytes(b"new final\n")
            final.chmod(0o600)
        else:
            oid = _git_with_input(
                fixture.root,
                b"new staged bytes\n",
                "hash-object",
                "-w",
                "--no-filters",
                "--stdin",
            )
            _git(
                fixture.root,
                "update-index",
                "--add",
                "--cacheinfo",
                f"100644,{oid},{fixture.report.relative_path}",
            )

    monkeypatch.setattr(gate, "_publication_checkpoint", introduce_state)
    with pytest.raises(gate.ReportGateError):
        gate.resume_publication(
            repo_root=fixture.root,
            receipt_id=fixture.reconciliation.receipt_id,
            receipt_store_factory=lambda _root: fixture.store,
        )

    with fixture.store.lock_receipt(fixture.reconciliation.receipt_id) as attempt:
        assert attempt.load_existing().state == "publishing"


def test_status_cli_emits_one_canonical_json_line(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    fixture = _live_codex_fixture(tmp_path / "repo", default_store=True)
    candidate = _candidate_path(fixture.root, fixture.raw)
    gate.publish_candidate(
        repo_root=fixture.root,
        candidate_path=candidate,
        final_relative=fixture.report.relative_path,
    )

    result = gate.main(
        [
            "status",
            "--repo-root",
            str(fixture.root),
            "--receipt-id",
            fixture.reconciliation.receipt_id,
        ]
    )

    captured = capsys.readouterr()
    assert result == 0
    assert captured.err == ""
    assert captured.out.count("\n") == 1
    assert captured.out == (
        receipts.canonical_json_bytes(json.loads(captured.out)).decode("utf-8") + "\n"
    )
    assert set(json.loads(captured.out)) == {
        "state",
        "path",
        "file_witness_match",
        "index_blob_oid",
        "staged_blob_match",
    }


@pytest.mark.parametrize(
    "mutation",
    [
        pytest.param("delete", id="deleted-final"),
        pytest.param("malformed", id="malformed-final"),
        pytest.param("symlink", id="symlink-final"),
        pytest.param("different-valid", id="different-valid-final"),
    ],
)
def test_publish_cli_diagnostic_uses_locked_identity_after_final_swap(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    mutation: str,
) -> None:
    fixture = _live_claude_fixture(tmp_path / "repo")
    candidate = _candidate_path(fixture.root, fixture.raw)
    wrong_task_id = "99999999-8888-4777-8666-555555555555"
    original_publish = gate._publish_candidate_result

    def publish_then_mutate(**kwargs: object) -> object:
        result = original_publish(**kwargs)
        published = result.path
        if mutation == "delete":
            published.unlink()
        elif mutation == "malformed":
            published.write_bytes(b"not a report\n")
        elif mutation == "symlink":
            target = tmp_path / "attacker-report"
            target.write_bytes(b"not a report\n")
            published.unlink()
            published.symlink_to(target)
        else:
            fields = _replace_field(
                _claude_fields(), "Verification task ID", wrong_task_id
            )
            fields = _replace_field(
                fields,
                "Scope authority",
                "coordination/verification/scopes/"
                f"{wrong_task_id}.json@{DESCRIPTOR_DIGEST}",
            )
            published.write_bytes(
                _report_bytes(
                    fields,
                    head=fixture.report.h1_head,
                    h1_sender="Operator2",
                    envelope_sender="operator2",
                )
            )
        return result

    def lose_stdout(label: str) -> None:
        if label == "before_stdout":
            raise RuntimeError("injected stdout loss")

    monkeypatch.setattr(gate, "_publish_candidate_result", publish_then_mutate)
    monkeypatch.setattr(gate, "_publication_checkpoint", lose_stdout)

    result = gate.main(
        [
            "publish",
            "--repo-root",
            str(fixture.root),
            "--candidate",
            str(candidate),
            "--final-relative",
            fixture.report.relative_path,
        ]
    )

    captured = capsys.readouterr()
    assert result == 6
    assert "publication_status_required" in captured.err
    assert f"--task-id {TASK_ID}" in captured.err
    assert wrong_task_id not in captured.err
    records = list(
        (fixture.root / ".codex/runtime/lane-v-report-publications/v1").glob(
            "*.json"
        )
    )
    assert len(records) == 1
    assert json.loads(records[0].read_text(encoding="utf-8"))["state"] == "published"


@pytest.mark.parametrize(
    "checkpoint",
    ["resume_after_published", "before_stdout", "after_stdout"],
)
def test_resume_cli_post_publish_failures_require_status_with_supplied_id(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
    checkpoint: str,
) -> None:
    fixture = _live_codex_fixture(tmp_path / "repo", default_store=True)
    candidate = _candidate_path(fixture.root, fixture.raw, ".interrupted.tmp")
    _begin_interrupted_publication(
        fixture, candidate, fixture.report.relative_path
    )

    def crash_at(label: str) -> None:
        if label == checkpoint:
            raise RuntimeError(f"injected crash at {checkpoint}")

    monkeypatch.setattr(gate, "_publication_checkpoint", crash_at)
    result = gate.main(
        [
            "resume",
            "--repo-root",
            str(fixture.root),
            "--receipt-id",
            fixture.reconciliation.receipt_id,
        ]
    )

    captured = capsys.readouterr()
    assert result == 6
    assert "publication_status_required" in captured.err
    assert f"--receipt-id {fixture.reconciliation.receipt_id}" in captured.err
    with fixture.store.lock_receipt(fixture.reconciliation.receipt_id) as attempt:
        assert attempt.load_existing().state == "published"


def test_resume_cli_stdout_write_failure_requires_status_with_supplied_id(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    fixture = _live_codex_fixture(tmp_path / "repo", default_store=True)
    candidate = _candidate_path(fixture.root, fixture.raw, ".interrupted.tmp")
    _begin_interrupted_publication(
        fixture, candidate, fixture.report.relative_path
    )
    real_print = builtins.print

    def fail_stdout(*args: object, **kwargs: object) -> None:
        if kwargs.get("file") is None:
            raise BrokenPipeError("injected stdout write failure")
        real_print(*args, **kwargs)

    monkeypatch.setattr(builtins, "print", fail_stdout)
    result = gate.main(
        [
            "resume",
            "--repo-root",
            str(fixture.root),
            "--receipt-id",
            fixture.reconciliation.receipt_id,
        ]
    )

    captured = capsys.readouterr()
    assert result == 6
    assert "publication_status_required" in captured.err
    assert f"--receipt-id {fixture.reconciliation.receipt_id}" in captured.err


def _mutate_last_publication_boundary(
    fixture: _LiveCodexFixture,
    candidate: Path,
    mutation: str,
) -> None:
    final = fixture.root / fixture.report.relative_path
    if mutation == "final":
        final.write_bytes(b"foreign final bytes\n")
    elif mutation == "foreign-index":
        oid = _git_with_input(
            fixture.root,
            b"foreign staged bytes\n",
            "hash-object",
            "-w",
            "--no-filters",
            "--stdin",
        )
        _git(
            fixture.root,
            "update-index",
            "--add",
            "--cacheinfo",
            f"100644,{oid},{fixture.report.relative_path}",
        )
    elif mutation == "absent-index":
        _git(
            fixture.root,
            "update-index",
            "--force-remove",
            "--",
            fixture.report.relative_path,
        )
    else:
        candidate.write_bytes(b"foreign candidate basename\n")
        candidate.chmod(0o600)


def _assert_last_boundary_mutation_applied(
    fixture: _LiveCodexFixture,
    candidate: Path,
    mutation: str,
) -> None:
    if mutation == "final":
        assert (
            fixture.root / fixture.report.relative_path
        ).read_bytes() == b"foreign final bytes\n"
    elif mutation == "foreign-index":
        staged = _git(
            fixture.root,
            "ls-files",
            "--stage",
            "--",
            fixture.report.relative_path,
        )
        oid = _git_with_input(
            fixture.root,
            b"foreign staged bytes\n",
            "hash-object",
            "--no-filters",
            "--stdin",
        )
        assert staged == f"100644 {oid} 0\t{fixture.report.relative_path}"
    elif mutation == "absent-index":
        assert (
            _git(
                fixture.root,
                "ls-files",
                "--stage",
                "--",
                fixture.report.relative_path,
            )
            == ""
        )
    else:
        assert candidate.read_bytes() == b"foreign candidate basename\n"


@pytest.mark.parametrize(
    "mutation", ["final", "foreign-index", "absent-index", "candidate"]
)
def test_fresh_last_pre_publish_guard_rejects_mutation(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    mutation: str,
) -> None:
    fixture = _live_codex_fixture(tmp_path / "repo")
    candidate = _candidate_path(fixture.root, fixture.raw)

    def mutate(label: str) -> None:
        if label == "before_published":
            _mutate_last_publication_boundary(fixture, candidate, mutation)

    monkeypatch.setattr(gate, "_publication_checkpoint", mutate)
    with pytest.raises(gate.ReportGateError):
        gate.publish_candidate(
            repo_root=fixture.root,
            candidate_path=candidate,
            final_relative=fixture.report.relative_path,
            receipt_store_factory=lambda _root: fixture.store,
        )

    _assert_last_boundary_mutation_applied(fixture, candidate, mutation)
    with fixture.store.lock_receipt(fixture.reconciliation.receipt_id) as attempt:
        assert attempt.load_existing().state == "publishing"


@pytest.mark.parametrize(
    "mutation", ["final", "foreign-index", "absent-index", "candidate"]
)
def test_resume_last_pre_publish_guard_rejects_mutation(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    mutation: str,
) -> None:
    fixture = _live_codex_fixture(tmp_path / "repo")
    candidate = _candidate_path(fixture.root, fixture.raw, ".interrupted.tmp")
    _begin_interrupted_publication(
        fixture, candidate, fixture.report.relative_path
    )

    def mutate(label: str) -> None:
        if label == "resume_before_published":
            _mutate_last_publication_boundary(fixture, candidate, mutation)

    monkeypatch.setattr(gate, "_publication_checkpoint", mutate)
    with pytest.raises(gate.ReportGateError):
        gate.resume_publication(
            repo_root=fixture.root,
            receipt_id=fixture.reconciliation.receipt_id,
            receipt_store_factory=lambda _root: fixture.store,
        )

    _assert_last_boundary_mutation_applied(fixture, candidate, mutation)
    with fixture.store.lock_receipt(fixture.reconciliation.receipt_id) as attempt:
        assert attempt.load_existing().state == "publishing"


def _inject_fsync_error(
    monkeypatch: pytest.MonkeyPatch,
    predicate: object,
) -> dict[str, bool]:
    real_fsync = gate.os.fsync
    observed = {"raised": False}

    def fail_selected(fd: int) -> None:
        metadata = os.fstat(fd)
        if not observed["raised"] and predicate(metadata):
            observed["raised"] = True
            raise OSError(5, "injected fsync failure")
        real_fsync(fd)

    monkeypatch.setattr(gate.os, "fsync", fail_selected)
    return observed


def test_candidate_fsync_oserror_before_link_never_publishes(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    fixture = _live_codex_fixture(tmp_path / "repo")
    candidate = _candidate_path(fixture.root, fixture.raw)
    inode = candidate.stat().st_ino
    injected = _inject_fsync_error(
        monkeypatch,
        lambda metadata: metadata.st_ino == inode and metadata.st_nlink == 1,
    )

    with pytest.raises(gate.ReportGateError):
        gate.publish_candidate(
            repo_root=fixture.root,
            candidate_path=candidate,
            final_relative=fixture.report.relative_path,
            receipt_store_factory=lambda _root: fixture.store,
        )

    assert injected["raised"] is True
    assert not (fixture.root / fixture.report.relative_path).exists()
    with fixture.store.lock_receipt(fixture.reconciliation.receipt_id) as attempt:
        assert attempt.load_existing().state == "publishing"


def test_linked_final_fsync_oserror_after_link_never_publishes(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    fixture = _live_codex_fixture(tmp_path / "repo")
    candidate = _candidate_path(fixture.root, fixture.raw)
    inode = candidate.stat().st_ino
    injected = _inject_fsync_error(
        monkeypatch,
        lambda metadata: metadata.st_ino == inode and metadata.st_nlink == 2,
    )

    with pytest.raises(gate.ReportGateError):
        gate.publish_candidate(
            repo_root=fixture.root,
            candidate_path=candidate,
            final_relative=fixture.report.relative_path,
            receipt_store_factory=lambda _root: fixture.store,
        )

    assert injected["raised"] is True
    assert (fixture.root / fixture.report.relative_path).stat().st_nlink == 2
    with fixture.store.lock_receipt(fixture.reconciliation.receipt_id) as attempt:
        assert attempt.load_existing().state == "publishing"


def test_recovery_file_fsync_oserror_never_publishes(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    fixture = _live_codex_fixture(tmp_path / "repo")
    candidate = _candidate_path(fixture.root, fixture.raw, ".interrupted.tmp")
    _begin_interrupted_publication(
        fixture, candidate, fixture.report.relative_path
    )
    inode = candidate.stat().st_ino
    injected = _inject_fsync_error(
        monkeypatch,
        lambda metadata: metadata.st_ino == inode and metadata.st_nlink == 2,
    )

    with pytest.raises(gate.ReportGateError):
        gate.resume_publication(
            repo_root=fixture.root,
            receipt_id=fixture.reconciliation.receipt_id,
            receipt_store_factory=lambda _root: fixture.store,
        )

    assert injected["raised"] is True
    with fixture.store.lock_receipt(fixture.reconciliation.receipt_id) as attempt:
        assert attempt.load_existing().state == "publishing"


def test_absent_recovery_directory_fsync_oserror_never_clears_or_publishes(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    fixture = _live_codex_fixture(tmp_path / "repo")
    candidate = _candidate_path(fixture.root, fixture.raw, ".interrupted.tmp")
    _begin_interrupted_publication(
        fixture, candidate, fixture.report.relative_path
    )
    candidate.unlink()
    sent = fixture.root / "coordination/mailbox/sent"
    sent_inode = sent.stat().st_ino
    injected = _inject_fsync_error(
        monkeypatch,
        lambda metadata: stat.S_ISDIR(metadata.st_mode)
        and metadata.st_ino == sent_inode,
    )

    with pytest.raises(gate.ReportGateError):
        gate.resume_publication(
            repo_root=fixture.root,
            receipt_id=fixture.reconciliation.receipt_id,
            receipt_store_factory=lambda _root: fixture.store,
        )

    assert injected["raised"] is True
    with fixture.store.lock_receipt(fixture.reconciliation.receipt_id) as attempt:
        assert attempt.load_existing().state == "publishing"


_PUBLISH_CRASH_CHECKPOINTS = (
    "before_publishing",
    "after_publishing",
    "before_candidate_fsync",
    "after_candidate_fsync",
    "before_link",
    "after_link",
    "before_linked_final_fsync",
    "after_linked_final_fsync",
    "before_link_directory_fsync",
    "after_link_directory_fsync",
    "before_object_write",
    "after_object_write",
    "before_index_update",
    "after_index_update",
    "before_stage_verification",
    "after_stage_verification",
    "before_final_revalidation",
    "after_final_revalidation",
    "before_candidate_unlink",
    "after_candidate_unlink",
    "before_cleanup_directory_fsync",
    "after_cleanup_directory_fsync",
    "after_candidate_cleanup",
    "before_completed_final_fsync",
    "after_completed_final_fsync",
    "before_index_fsync",
    "before_index_file_fsync",
    "after_index_file_fsync",
    "before_index_directory_fsync",
    "after_index_directory_fsync",
    "after_index_fsync",
    "before_published",
    "after_published",
)


@pytest.mark.parametrize("checkpoint", _PUBLISH_CRASH_CHECKPOINTS)
def test_publish_crash_matrix_never_grants_premature_published(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, checkpoint: str
) -> None:
    fixture = _live_codex_fixture(tmp_path / "repo")
    candidate = _candidate_path(fixture.root, fixture.raw)

    def crash_at(label: str) -> None:
        if label == checkpoint:
            raise RuntimeError(f"injected crash at {checkpoint}")

    monkeypatch.setattr(gate, "_publication_checkpoint", crash_at)
    with pytest.raises(gate.ReportGateError):
        gate.publish_candidate(
            repo_root=fixture.root,
            candidate_path=candidate,
            final_relative=fixture.report.relative_path,
            receipt_store_factory=lambda _root: fixture.store,
        )
    with fixture.store.lock_receipt(fixture.reconciliation.receipt_id) as attempt:
        record = attempt.load_existing()
    expected_state = (
        "reconciled"
        if checkpoint == "before_publishing"
        else "published"
        if checkpoint == "after_published"
        else "publishing"
    )
    assert record.state == expected_state

    monkeypatch.setattr(gate, "_publication_checkpoint", lambda _label: None)
    if record.state == "publishing":
        published = gate.resume_publication(
            repo_root=fixture.root,
            receipt_id=fixture.reconciliation.receipt_id,
            receipt_store_factory=lambda _root: fixture.store,
        )
        assert published == fixture.root / fixture.report.relative_path
    elif record.state == "published":
        status = gate.publication_status(
            repo_root=fixture.root,
            receipt_id=fixture.reconciliation.receipt_id,
            receipt_store_factory=lambda _root: fixture.store,
        )
        assert status["file_witness_match"] is True
        assert status["staged_blob_match"] is True
    else:
        assert not (fixture.root / fixture.report.relative_path).exists()
        assert _git(
            fixture.root, "ls-files", "--stage", "--", fixture.report.relative_path
        ) == ""


_RESUME_CRASH_CHECKPOINTS = (
    "resume_before_candidate_fsync",
    "resume_after_candidate_fsync",
    "resume_before_link",
    "resume_after_link",
    "resume_before_final_fsync",
    "resume_after_final_file_fsync",
    "resume_before_directory_fsync",
    "resume_after_directory_fsync",
    "resume_after_final_fsync",
    "resume_before_object_write",
    "resume_after_object_write",
    "resume_before_index_update",
    "resume_after_index_update",
    "resume_before_stage_verification",
    "resume_before_final_revalidation",
    "resume_after_final_revalidation",
    "resume_before_candidate_unlink",
    "resume_after_candidate_unlink",
    "resume_before_cleanup_directory_fsync",
    "resume_after_cleanup_directory_fsync",
    "resume_before_completed_final_fsync",
    "resume_after_completed_final_fsync",
    "resume_before_index_fsync",
    "before_index_file_fsync",
    "after_index_file_fsync",
    "before_index_directory_fsync",
    "after_index_directory_fsync",
    "resume_after_index_fsync",
    "resume_before_published",
    "resume_after_published",
)


@pytest.mark.parametrize("checkpoint", _RESUME_CRASH_CHECKPOINTS)
def test_resume_crash_matrix_remains_idempotent(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, checkpoint: str
) -> None:
    fixture = _live_codex_fixture(tmp_path / "repo")
    candidate = _candidate_path(fixture.root, fixture.raw, ".interrupted.tmp")
    _begin_interrupted_publication(
        fixture, candidate, fixture.report.relative_path
    )

    def crash_at(label: str) -> None:
        if label == checkpoint:
            raise RuntimeError(f"injected resume crash at {checkpoint}")

    monkeypatch.setattr(gate, "_publication_checkpoint", crash_at)
    with pytest.raises(gate.ReportGateError):
        gate.resume_publication(
            repo_root=fixture.root,
            receipt_id=fixture.reconciliation.receipt_id,
            receipt_store_factory=lambda _root: fixture.store,
        )
    with fixture.store.lock_receipt(fixture.reconciliation.receipt_id) as attempt:
        record = attempt.load_existing()
    expected_state = "published" if checkpoint == "resume_after_published" else "publishing"
    assert record.state == expected_state

    monkeypatch.setattr(gate, "_publication_checkpoint", lambda _label: None)
    if record.state == "publishing":
        published = gate.resume_publication(
            repo_root=fixture.root,
            receipt_id=fixture.reconciliation.receipt_id,
            receipt_store_factory=lambda _root: fixture.store,
        )
        assert published == fixture.root / fixture.report.relative_path
    else:
        status = gate.publication_status(
            repo_root=fixture.root,
            receipt_id=fixture.reconciliation.receipt_id,
            receipt_store_factory=lambda _root: fixture.store,
        )
        assert status["state"] == "published"


def test_publish_candidate_rejects_validation_failure_before_state_or_final(
    tmp_path: Path,
) -> None:
    fixture = _live_codex_fixture(tmp_path / "repo")
    invalid = fixture.raw.replace(b"VERDICT: GO", b"VERDICT: NITS")
    candidate = _candidate_path(fixture.root, invalid)

    with pytest.raises(gate.ReportGateError):
        gate.publish_candidate(
            repo_root=fixture.root,
            candidate_path=candidate,
            final_relative=fixture.report.relative_path,
            receipt_store_factory=lambda _root: fixture.store,
        )

    assert not (fixture.root / fixture.report.relative_path).exists()
    with fixture.store.lock_receipt(fixture.reconciliation.receipt_id) as attempt:
        record = attempt.load_existing()
    assert record.state == "reconciled"


def test_publish_candidate_public_replay_and_fresh_file_exists_cancel_fail(
    tmp_path: Path,
) -> None:
    replay = _live_codex_fixture(tmp_path / "replay")
    first = _candidate_path(replay.root, replay.raw, ".first.tmp")
    gate.publish_candidate(
        repo_root=replay.root,
        candidate_path=first,
        final_relative=replay.report.relative_path,
        receipt_store_factory=lambda _root: replay.store,
    )
    second = _candidate_path(replay.root, replay.raw, ".second.tmp")
    with pytest.raises(gate.ReportGateError, match="published"):
        gate.publish_candidate(
            repo_root=replay.root,
            candidate_path=second,
            final_relative=replay.report.relative_path,
            receipt_store_factory=lambda _root: replay.store,
        )

    collision = _live_codex_fixture(tmp_path / "collision")
    candidate = _candidate_path(collision.root, collision.raw)
    final = collision.root / collision.report.relative_path
    final.write_bytes(collision.raw)
    final.chmod(0o600)
    with pytest.raises(gate.ReportGateError, match="exists"):
        gate.publish_candidate(
            repo_root=collision.root,
            candidate_path=candidate,
            final_relative=collision.report.relative_path,
            receipt_store_factory=lambda _root: collision.store,
        )
    with collision.store.lock_receipt(collision.reconciliation.receipt_id) as attempt:
        record = attempt.load_existing()
    assert record.state == "reconciled"
    assert record.generation == 5
    assert final.read_bytes() == collision.raw


def _begin_interrupted_publication(
    fixture: _LiveCodexFixture,
    candidate: Path,
    relative: str,
) -> receipts.ReceiptRecord:
    observed = candidate.stat()
    raw = candidate.read_bytes()
    digest = "sha256:" + hashlib.sha256(raw).hexdigest()
    blob_oid = _git_with_input(
        fixture.root, raw, "hash-object", "--no-filters", "--stdin"
    )
    with fixture.store.lock_receipt(fixture.reconciliation.receipt_id) as attempt:
        attempt.load_existing()
        return attempt.begin_publication(
            relative,
            digest,
            candidate.name,
            observed.st_dev,
            observed.st_ino,
            blob_oid,
            "100644",
            0,
        )


def test_public_publish_rejects_interruption_and_explicit_resume_converges(
    tmp_path: Path,
) -> None:
    absent = _live_codex_fixture(tmp_path / "absent")
    old_absent = _candidate_path(absent.root, absent.raw, ".old-absent.tmp")
    _begin_interrupted_publication(absent, old_absent, absent.report.relative_path)
    new_absent = _candidate_path(absent.root, absent.raw, ".new-absent.tmp")
    with pytest.raises(gate.ReportGateError, match="explicit resume"):
        gate.publish_candidate(
            repo_root=absent.root,
            candidate_path=new_absent,
            final_relative=absent.report.relative_path,
            receipt_store_factory=lambda _root: absent.store,
        )
    published = gate.resume_publication(
        repo_root=absent.root,
        receipt_id=absent.reconciliation.receipt_id,
        receipt_store_factory=lambda _root: absent.store,
    )
    assert published == absent.root / absent.report.relative_path
    assert not old_absent.exists()
    assert new_absent.exists()
    assert _git(absent.root, "ls-files", "--stage", "--", absent.report.relative_path)

    exact = _live_codex_fixture(tmp_path / "exact")
    old_raw = exact.raw.replace(
        b"2026-07-13T05:00:00Z", b"2026-07-13T04:59:59Z"
    )
    old_exact = _candidate_path(exact.root, old_raw, ".old-exact.tmp")
    older_relative = exact.report.relative_path.replace("05-00-00Z", "04-59-59Z")
    _begin_interrupted_publication(exact, old_exact, older_relative)
    older_final = exact.root / older_relative
    os.link(old_exact, older_final)
    recovered = gate.resume_publication(
        repo_root=exact.root,
        receipt_id=exact.reconciliation.receipt_id,
        receipt_store_factory=lambda _root: exact.store,
    )
    assert recovered == older_final
    assert recovered.stat().st_nlink == 1
    assert not old_exact.exists()
    assert _git(exact.root, "ls-files", "--stage", "--", older_relative)


def test_publish_candidate_recovery_rejects_equal_bytes_different_inode(
    tmp_path: Path,
) -> None:
    fixture = _live_codex_fixture(tmp_path / "repo")
    old = _candidate_path(fixture.root, fixture.raw, ".old.tmp")
    _begin_interrupted_publication(fixture, old, fixture.report.relative_path)
    final = fixture.root / fixture.report.relative_path
    final.write_bytes(fixture.raw)
    final.chmod(0o600)
    with pytest.raises(gate.ReportGateError, match="recovery"):
        gate.resume_publication(
            repo_root=fixture.root,
            receipt_id=fixture.reconciliation.receipt_id,
            receipt_store_factory=lambda _root: fixture.store,
        )

    with fixture.store.lock_receipt(fixture.reconciliation.receipt_id) as attempt:
        record = attempt.load_existing()
    assert record.state == "publishing"


@pytest.mark.parametrize(
    "unsafe",
    ["relative", "dotdot", "other-parent", "symlink", "directory", "fifo", "mode", "nlink"],
)
def test_publish_candidate_rejects_unsafe_candidate_without_state_change(
    tmp_path: Path, unsafe: str
) -> None:
    fixture = _live_codex_fixture(tmp_path / "repo")
    valid = _candidate_path(fixture.root, fixture.raw, ".valid.tmp")
    candidate: Path
    if unsafe == "relative":
        candidate = Path("coordination/mailbox/sent/.valid.tmp")
    elif unsafe == "dotdot":
        candidate = valid.parent / ".." / "sent" / valid.name
    elif unsafe == "other-parent":
        other = fixture.root / "other"
        other.mkdir()
        candidate = other / valid.name
        candidate.write_bytes(fixture.raw)
        candidate.chmod(0o600)
    elif unsafe == "symlink":
        candidate = valid.with_name(".symlink.tmp")
        candidate.symlink_to(valid)
    elif unsafe == "directory":
        candidate = valid.with_name(".directory.tmp")
        candidate.mkdir()
        candidate.chmod(0o600)
    elif unsafe == "fifo":
        candidate = valid.with_name(".fifo.tmp")
        os.mkfifo(candidate, 0o600)
    elif unsafe == "mode":
        candidate = valid
        candidate.chmod(0o644)
    else:
        candidate = valid
        os.link(candidate, valid.with_name(".extra-link.tmp"))

    with pytest.raises(gate.ReportGateError):
        gate.publish_candidate(
            repo_root=fixture.root,
            candidate_path=candidate,
            final_relative=fixture.report.relative_path,
            receipt_store_factory=lambda _root: fixture.store,
        )
    assert not (fixture.root / fixture.report.relative_path).exists()
    with fixture.store.lock_receipt(fixture.reconciliation.receipt_id) as attempt:
        assert attempt.load_existing().state == "reconciled"


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
