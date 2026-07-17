"""Strict provider-neutral Lane V v3 and committed-authority gate tests."""

from __future__ import annotations

import dataclasses
import builtins
import contextlib
import hashlib
import inspect
import json
import multiprocessing
import os
import stat
import subprocess
from collections.abc import Mapping
from pathlib import Path
from types import MappingProxyType, SimpleNamespace

import pytest

import verification_report_gate as gate
import kernel_activation


HEAD = "a" * 40
BASE = "b" * 40
TASK_ID = "11111111-2222-4333-8444-555555555555"
DESCRIPTOR_PATH = f"coordination/verification/scopes/{TASK_ID}.json"
DESCRIPTOR_DIGEST = "sha256:" + "c" * 64
REPORT_PATH = (
    "coordination/mailbox/sent/"
    "2026-07-13T05-00-00Z-operator-to-all-verification-report.md"
)
PRE_V3_SCHEMA = "lane-v-report-pre-v3-baseline/v1"


def _lane_v_fields(*, reviewer: str = "operator") -> list[tuple[str, str]]:
    return [
        ("Verification schema", "lane-v-report/v3"),
        ("Verification mode", "independent-lane-v"),
        ("Verification harness", "lane-v:independent-verifier"),
        ("Verification task ID", TASK_ID),
        ("Scope authority", f"{DESCRIPTOR_PATH}@{DESCRIPTOR_DIGEST}"),
        ("Trigger identity", f"shipping-commit:{HEAD}"),
        ("Reviewed head", HEAD),
        ("Reviewed base", BASE),
        ("Review profile", "independent-lane-v"),
        ("Reviewer identity", reviewer),
    ]


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
    field_lines = [f"{label}: {value}" for label, value in (fields or _lane_v_fields())]
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


@pytest.mark.parametrize("verdict", ("GO", "NITS", "FAIL"))
def test_parse_provider_neutral_v3_verdicts(verdict: str) -> None:
    report = gate.parse_lane_v_report(
        REPORT_PATH,
        _report_bytes(_lane_v_fields(), verdict=f"VERDICT: {verdict}"),
    )

    assert report.verdict == verdict
    assert tuple(report.fields) == gate.ATTESTATION_FIELDS


@pytest.mark.parametrize(
    "label",
    (
        "Authorization identity",
        "Opus receipt ID",
        "Opus scope digest",
        "Cross-model review",
        "Effective Opus model",
        "Opus finding dispositions",
        "Reconciliation guard",
        "Degraded reason",
        "Provider",
        "Model",
    ),
)
def test_v3_rejects_provider_and_receipt_fields(label: str) -> None:
    with pytest.raises(gate.ReportGateError, match="invalid_attestation"):
        gate.parse_lane_v_report(
            REPORT_PATH,
            _report_bytes([*_lane_v_fields(), (label, "forbidden")]),
        )


@pytest.mark.parametrize("reviewer", ("operator", "operator2"))
def test_v3_reviewer_identity_matches_filename_and_envelope(reviewer: str) -> None:
    path = REPORT_PATH.replace("-operator-to-", f"-{reviewer}-to-")
    report = gate.parse_lane_v_report(
        path,
        _report_bytes(
            _lane_v_fields(reviewer=reviewer),
            h1_sender=reviewer.capitalize(),
            envelope_sender=reviewer,
        ),
    )

    assert report.sender == reviewer
    assert report.fields["Reviewer identity"] == reviewer


@pytest.mark.parametrize(
    "reviewer",
    ("", "director", "coordinator", "operator-online", "Operator", "operator2 "),
)
def test_v3_reviewer_identity_rejects_noncanonical_or_other_seat(
    reviewer: str,
) -> None:
    state_accessed = False

    def parse_then_access_state() -> None:
        nonlocal state_accessed
        gate.parse_lane_v_report(
            REPORT_PATH,
            _report_bytes(_lane_v_fields(reviewer=reviewer)),
        )
        state_accessed = True

    with pytest.raises(gate.ReportGateError, match="invalid_attestation"):
        parse_then_access_state()
    assert state_accessed is False


def _provider_neutral_descriptor_mapping() -> dict[str, object]:
    return {
        "schema_version": "lane-v-scope/v1",
        "task_id": TASK_ID,
        "question_id": "provider-neutral-lane-v",
        "trigger_kind": "shipping-commit",
        "verification_mode": "independent-lane-v",
        "verification_harness": "lane-v:independent-verifier",
        "review_profile": "independent-lane-v",
        "reviewed_base": {"policy": "exact", "commit": BASE},
        "requirement_paths": ["AGENTS.md", "docs/protocol"],
        "allowed_path_roots": ["scripts", "tests/unit"],
        "verification_commands": [
            "env -u GIT_INDEX_FILE .venv/bin/python scripts/ci_smoke.py"
        ],
    }


@pytest.mark.parametrize(
    "raw",
    (
        b'{"outer":{"key":1,"key":2}}',
        b'"bad-\xff"',
        b'{"value":NaN}',
        b" " * 65_537,
    ),
)
def test_provider_neutral_strict_json_rejects_nested_duplicates_and_bad_bytes(
    raw: bytes,
) -> None:
    with pytest.raises(gate.ScopeContractError):
        gate.strict_json_loads(raw)


def test_provider_neutral_strict_json_rejects_top_level_duplicate_keys() -> None:
    with pytest.raises(gate.ScopeContractError, match="duplicate_json_key"):
        gate.strict_json_loads(b'{"task_id":"first","task_id":"second"}')


def test_provider_neutral_canonical_json_is_compact_sorted_utf8() -> None:
    assert gate.canonical_json_bytes({"z": 1, "é": "✓", "a": 2}) == (
        '{"a":2,"z":1,"é":"✓"}'.encode()
    )


@pytest.mark.parametrize(
    "bad",
    (
        "",
        ".",
        "./x",
        "x/.",
        "x/../y",
        "/x",
        "x/",
        "x//y",
        "x\\y",
        "x*",
        "x?",
        "x[0]",
        "é" * 257,
    ),
)
def test_provider_neutral_repo_path_rejects_ambiguous_or_oversize_values(
    bad: str,
) -> None:
    with pytest.raises(gate.ScopeContractError, match="invalid_repo_path"):
        gate.normalize_repo_path(bad)


def test_provider_neutral_repo_path_preserves_exact_utf8_spelling() -> None:
    nfc = "docs/caf\u00e9.md"
    nfd = "docs/cafe\u0301.md"
    assert gate.normalize_repo_path("Docs/Case.md") == "Docs/Case.md"
    assert gate.normalize_repo_path(nfc) == nfc
    assert gate.normalize_repo_path(nfd) == nfd
    assert gate.normalize_repo_path(nfc) != gate.normalize_repo_path(nfd)


def test_provider_neutral_scope_reference_trigger_and_descriptor_are_exact() -> None:
    reference = gate.parse_scope_reference(
        f"{DESCRIPTOR_PATH}@{DESCRIPTOR_DIGEST}"
    )
    assert reference == gate.ScopeReference(DESCRIPTOR_PATH, DESCRIPTOR_DIGEST)
    assert gate.canonical_trigger_identity("shipping-commit", HEAD) == (
        f"shipping-commit:{HEAD}"
    )
    descriptor = gate.ScopeDescriptor.from_mapping(
        _provider_neutral_descriptor_mapping()
    )
    assert descriptor.verification_mode == "independent-lane-v"
    assert descriptor.verification_harness == "lane-v:independent-verifier"
    assert descriptor.review_profile == "independent-lane-v"


@pytest.mark.parametrize(
    "reference",
    (
        DESCRIPTOR_PATH,
        f"./{DESCRIPTOR_PATH}@{DESCRIPTOR_DIGEST}",
        f"{DESCRIPTOR_PATH}@sha256:{'A' * 64}",
        f"{DESCRIPTOR_PATH}@sha256:{'1' * 63}",
    ),
)
def test_provider_neutral_scope_reference_rejects_noncanonical_values(
    reference: str,
) -> None:
    with pytest.raises(gate.ScopeContractError, match="invalid_scope_reference"):
        gate.parse_scope_reference(reference)


@pytest.mark.parametrize(
    ("kind", "commit", "path"),
    (
        ("shipping-commit", HEAD.upper(), None),
        ("shipping-commit", HEAD, "event.md"),
        ("verify-request", HEAD, None),
        ("verify-request", HEAD, "./event.md"),
        ("other", HEAD, None),
    ),
)
def test_provider_neutral_trigger_identity_rejects_noncanonical_values(
    kind: str, commit: str, path: str | None
) -> None:
    with pytest.raises(gate.ScopeContractError, match="invalid_trigger_identity"):
        gate.canonical_trigger_identity(kind, commit, path)


@pytest.mark.parametrize(
    ("mutation", "value"),
    (
        ("extra", True),
        ("task_id", "AAAAAAAA-BBBB-4CCC-8DDD-EEEEEEEEEEEE"),
        ("task_id", "11111111-2222-4333-8444-55555555555"),
        ("verification_mode", "codex-lane-v"),
        ("verification_harness", "claude:lane-v-verifier"),
        ("review_profile", "claude-lane-v"),
        ("trigger_kind", "other"),
        ("question_id", "contains/slash"),
        ("reviewed_base", {"policy": "exact", "commit": BASE.upper()}),
        ("requirement_paths", []),
        ("allowed_path_roots", ["../scripts"]),
        ("verification_commands", ["pytest tests/unit"]),
    ),
)
def test_provider_neutral_descriptor_rejects_exact_field_and_literal_abuse(
    mutation: str, value: object
) -> None:
    mapping = _provider_neutral_descriptor_mapping()
    mapping[mutation] = value
    with pytest.raises(gate.ScopeContractError, match="invalid_scope_descriptor"):
        gate.ScopeDescriptor.from_mapping(mapping)


@pytest.mark.parametrize(
    ("mutation", "value"),
    (
        ("missing", None),
        ("schema_version", 1),
        ("task_id", 1),
        ("question_id", 1),
        ("trigger_kind", 1),
        ("verification_mode", []),
        ("verification_harness", {}),
        ("review_profile", False),
        ("reviewed_base", []),
        ("requirement_paths", "AGENTS.md"),
        ("allowed_path_roots", "scripts"),
        ("verification_commands", "pytest"),
    ),
)
def test_provider_neutral_descriptor_rejects_missing_and_wrong_typed_fields(
    mutation: str, value: object
) -> None:
    mapping = _provider_neutral_descriptor_mapping()
    if mutation == "missing":
        mapping.pop("question_id")
    else:
        mapping[mutation] = value
    with pytest.raises(gate.ScopeContractError, match="invalid_scope_descriptor"):
        gate.ScopeDescriptor.from_mapping(mapping)


@pytest.mark.parametrize(
    "reviewed_base",
    (
        {"policy": "exact"},
        {"commit": BASE},
        {"policy": "exact", "commit": BASE, "extra": True},
        {"policy": "first-parent", "commit": BASE},
        {"policy": "exact", "commit": BASE.upper()},
        {"policy": "exact", "commit": 7},
    ),
)
def test_provider_neutral_descriptor_requires_exact_nested_reviewed_base(
    reviewed_base: dict[str, object],
) -> None:
    mapping = _provider_neutral_descriptor_mapping()
    mapping["reviewed_base"] = reviewed_base
    with pytest.raises(gate.ScopeContractError, match="invalid_scope_descriptor"):
        gate.ScopeDescriptor.from_mapping(mapping)


@pytest.mark.parametrize(
    ("field", "value"),
    (
        ("requirement_paths", []),
        ("requirement_paths", [f"docs/{index}" for index in range(129)]),
        ("allowed_path_roots", []),
        ("allowed_path_roots", [f"allowed/{index}" for index in range(129)]),
        ("verification_commands", []),
        (
            "verification_commands",
            [
                f"env -u GIT_INDEX_FILE .venv/bin/python scripts/check_{index}.py"
                for index in range(33)
            ],
        ),
        ("requirement_paths", ["é" * 257]),
        ("allowed_path_roots", ["é" * 257]),
        (
            "verification_commands",
            ["env -u GIT_INDEX_FILE .venv/bin/python " + "a" * 4_097],
        ),
    ),
)
def test_provider_neutral_descriptor_enforces_collection_and_item_limits(
    field: str, value: list[str]
) -> None:
    mapping = _provider_neutral_descriptor_mapping()
    mapping[field] = value
    with pytest.raises(gate.ScopeContractError, match="invalid_scope_descriptor"):
        gate.ScopeDescriptor.from_mapping(mapping)


@pytest.mark.parametrize(
    "command",
    (
        "",
        " pytest tests/unit",
        "pytest tests/unit",
        "env -u GIT_INDEX_FILE .venv/bin/python scripts/ci_smoke.py ",
        "env -u GIT_INDEX_FILE .venv/bin/python scripts/ci_smoke.py; echo bad",
        "env -u GIT_INDEX_FILE .venv/bin/python tests/*.py",
        "env -u GIT_INDEX_FILE .venv/bin/python 'unterminated",
    ),
)
def test_provider_neutral_descriptor_rejects_unsafe_commands(command: str) -> None:
    mapping = _provider_neutral_descriptor_mapping()
    mapping["verification_commands"] = [command]
    with pytest.raises(gate.ScopeContractError, match="invalid_scope_descriptor"):
        gate.ScopeDescriptor.from_mapping(mapping)


def test_provider_neutral_descriptor_deduplicates_before_limits() -> None:
    mapping = _provider_neutral_descriptor_mapping()
    mapping["requirement_paths"] = ["AGENTS.md"] * 129
    mapping["allowed_path_roots"] = ["scripts"] * 129
    mapping["verification_commands"] = [
        "env -u GIT_INDEX_FILE .venv/bin/python scripts/ci_smoke.py"
    ] * 33

    descriptor = gate.ScopeDescriptor.from_mapping(mapping)

    assert descriptor.requirement_paths == ("AGENTS.md",)
    assert descriptor.allowed_path_roots == ("scripts",)
    assert descriptor.verification_commands == (
        "env -u GIT_INDEX_FILE .venv/bin/python scripts/ci_smoke.py",
    )


def test_provider_neutral_allowed_roots_are_byte_and_component_aware() -> None:
    changed = gate.parse_name_status_z(
        b"M\0scripts/foo.py\0D\0tests/unit/old.py\0"
    )
    gate.assert_changed_path_coverage(changed, ("scripts/foo.py", "tests/unit"))
    with pytest.raises(gate.ScopeContractError, match="changed_path_not_allowed"):
        gate.assert_changed_path_coverage(changed, ("scripts/foo", "tests/unit/old"))
    with pytest.raises(gate.ScopeContractError, match="changed_path_not_allowed"):
        gate.assert_changed_path_coverage(
            gate.parse_name_status_z(b"M\0scripts/foobar/item.py\0"),
            ("scripts/foo",),
        )


@pytest.mark.parametrize(
    "raw",
    (
        b"M\0scripts/x.py",
        b"M\0",
        b"\0scripts/x.py\0",
        b"M\0\0",
        b"MM\0scripts/x.py\0",
        b"R\0old.py\0new.py\0",
        b"C\0source.py\0copy.py\0",
        b"Z\0scripts/x.py\0",
    ),
)
def test_provider_neutral_name_status_rejects_malformed_records(raw: bytes) -> None:
    with pytest.raises(gate.ScopeContractError, match="invalid_name_status"):
        gate.parse_name_status_z(raw)


def test_provider_neutral_name_status_rejects_invalid_utf8() -> None:
    with pytest.raises(gate.ScopeContractError, match="unsupported_git_path_encoding"):
        gate.parse_name_status_z(b"A\0bad-\xff.py\0")


def test_provider_neutral_changed_paths_preserve_case_and_unicode_bytes() -> None:
    nfc = "docs/caf\u00e9.md"
    nfd = "docs/cafe\u0301.md"
    raw = (
        b"A\0Scripts/example.py\0A\0scripts/example.py\0A\0"
        + nfc.encode()
        + b"\0A\0"
        + nfd.encode()
        + b"\0"
    )
    changed = gate.parse_name_status_z(raw)

    assert {item.path for item in changed} == {
        "Scripts/example.py",
        "scripts/example.py",
        nfc,
        nfd,
    }
    unicode_entries = {item.path: item.path_bytes for item in changed if item.path.startswith("docs/")}
    assert unicode_entries[nfc] != unicode_entries[nfd]
    with pytest.raises(gate.ScopeContractError, match="changed_path_not_allowed"):
        gate.assert_changed_path_coverage(changed, ("scripts", nfc))
    gate.assert_changed_path_coverage(changed, ("Scripts", "scripts", nfc, nfd))


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
        pytest.param(_report_bytes(_lane_v_fields()[:-1]), id="missing-field"),
        pytest.param(
            _report_bytes(_lane_v_fields() + [_lane_v_fields()[-1]]),
            id="duplicate-field",
        ),
        pytest.param(
            _report_bytes([_lane_v_fields()[1], _lane_v_fields()[0], *_lane_v_fields()[2:]]),
            id="reordered-field",
        ),
        pytest.param(
            _report_bytes(
                [*_lane_v_fields()[:-1], ("Invented field", "value")]
            ),
            id="unknown-field",
        ),
        pytest.param(
            _report_bytes(
                [("**Verification schema**", "lane-v-report/v3"), *_lane_v_fields()[1:]]
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
        pytest.param(
            REPORT_PATH.replace("-operator-to-", "-operator2-to-"),
            _report_bytes(
                _lane_v_fields(reviewer="operator2"),
                h1_sender="Operator2",
                envelope_sender="operator",
            ),
            id="operator2-filename-envelope-sender-mismatch",
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
        pytest.param(
            "Trigger identity",
            f"shipping-commit:{HEAD.upper()}",
            id="uppercase-trigger",
        ),
        pytest.param(
            "Reviewer identity",
            "director",
            id="non-operator-reviewer",
        ),
    ],
)
def test_rejects_invalid_structural_values(label: str, value: str) -> None:
    fields = _replace_field(_lane_v_fields(), label, value)
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
        _lane_v_fields(), "Reviewer identity", "x" * gate.ATTESTATION_LINE_MAX_BYTES
    )
    oversized_section = _replace_field(
        _replace_field(_lane_v_fields(), "Scope authority", "x" * 33_000),
        "Trigger identity",
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
        pytest.param("Verification mode", "codex-lane-v", id="provider-mode"),
        pytest.param("Verification harness", "claude:lane-v-verifier", id="provider-harness"),
        pytest.param("Review profile", "not-applicable", id="provider-profile"),
    ],
)
def test_rejects_invalid_verifier_literals(label: str, value: str) -> None:
    fields = _replace_field(_lane_v_fields(), label, value)
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
    mode: str = "independent-lane-v",
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

    assert mode == "independent-lane-v"
    harness = "lane-v:independent-verifier"
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
        "allowed_path_roots": ["coordination/verification/scopes", "scripts"],
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

    fields = _lane_v_fields(reviewer=recipient)
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
        "Review profile": "independent-lane-v",
        "Reviewer identity": recipient,
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
    ("trigger_kind", "recipient"),
    [
        ("shipping-commit", "operator"),
        ("verify-request", "operator"),
        ("shipping-commit", "operator2"),
        ("verify-request", "operator2"),
    ],
)
def test_structural_authority_accepts_committed_shipping_and_verify_request(
    tmp_path: Path, trigger_kind: str, recipient: str
) -> None:
    root, fields, report_path, head, _ = _authority_fixture(
        tmp_path / "repo",
        mode="independent-lane-v",
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
    assert authority.descriptor.verification_mode == "independent-lane-v"
    assert authority.trigger_kind == trigger_kind
    assert authority.verify_request_recipient == (
        recipient if trigger_kind == "verify-request" else None
    )
    assert authority.scope.reviewed_head == head
    assert authority.scope.changed_paths
    assert authority.scope.requirements == (
        {
            "path": "requirements/task.md",
            "blob_id": _git(root, "rev-parse", f"{head}:requirements/task.md"),
            "digest": "sha256:"
            + hashlib.sha256(b"Review the committed feature.\n").hexdigest(),
        },
    )


def _advance_shipping_fixture(
    root: Path,
    fields: list[tuple[str, str]],
    *paths: str,
) -> tuple[list[tuple[str, str]], str]:
    scope = dict(fields)["Scope authority"]
    _git(root, "add", *paths)
    _git(
        root,
        "commit",
        "-q",
        "-m",
        "feat: advance reviewed fixture",
        "-m",
        f"Lane-V-Scope: {scope}",
    )
    head = _git(root, "rev-parse", "HEAD")
    advanced = _replace_field(fields, "Reviewed head", head)
    advanced = _replace_field(advanced, "Trigger identity", f"shipping-commit:{head}")
    return advanced, head


def test_structural_authority_rejects_unrelated_changed_path_before_state_access(
    tmp_path: Path,
) -> None:
    root, fields, report_path, _, _ = _authority_fixture(tmp_path / "repo")
    unrelated = root / "outside-scope.txt"
    unrelated.write_text("not authorized\n", encoding="utf-8")
    fields, head = _advance_shipping_fixture(root, fields, "outside-scope.txt")
    report = _structural_report(fields, report_path)
    state_accessed = False

    def forbidden_store(_root: Path) -> object:
        nonlocal state_accessed
        state_accessed = True
        raise AssertionError("task state was accessed before scope rejection")

    with pytest.raises(gate.ReportGateError, match="changed_path_not_allowed"):
        gate.validate_live_report(root, report, task_store_factory=forbidden_store)

    assert report.h1_head == head
    assert state_accessed is False


def test_structural_authority_rejects_requirement_blob_mismatch_before_state_access(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    root, fields, report_path, head, _ = _authority_fixture(tmp_path / "repo")
    report = _structural_report(fields, report_path)
    feature_oid = _git(root, "rev-parse", f"{head}:scripts/feature.py")
    original = gate._git_process
    state_accessed = False

    def mismatched_requirement_blob(
        called_root: Path, *args: str, text: bool = True
    ) -> subprocess.CompletedProcess[object]:
        if args == ("rev-parse", f"{head}:requirements/task.md"):
            return subprocess.CompletedProcess(args, 0, stdout=feature_oid + "\n", stderr="")
        return original(called_root, *args, text=text)

    def forbidden_store(_root: Path) -> object:
        nonlocal state_accessed
        state_accessed = True
        raise AssertionError("task state was accessed before blob rejection")

    monkeypatch.setattr(gate, "_git_process", mismatched_requirement_blob)
    with pytest.raises(gate.ReportGateError, match="requirement_blob_mismatch"):
        gate.validate_live_report(root, report, task_store_factory=forbidden_store)

    assert state_accessed is False


def test_structural_authority_rejects_malformed_name_status_before_state_access(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    root, fields, report_path, _, _ = _authority_fixture(tmp_path / "repo")
    report = _structural_report(fields, report_path)
    original = gate._git_process
    state_accessed = False

    def malformed_diff(
        called_root: Path, *args: str, text: bool = True
    ) -> subprocess.CompletedProcess[object]:
        if "--name-status" in args:
            return subprocess.CompletedProcess(
                args, 0, stdout=b"M\0scripts/feature.py", stderr=b""
            )
        return original(called_root, *args, text=text)

    def forbidden_store(_root: Path) -> object:
        nonlocal state_accessed
        state_accessed = True
        raise AssertionError("task state was accessed before malformed diff rejection")

    monkeypatch.setattr(gate, "_git_process", malformed_diff)
    with pytest.raises(gate.ReportGateError, match="invalid_name_status"):
        gate.validate_live_report(root, report, task_store_factory=forbidden_store)

    assert state_accessed is False


@pytest.mark.parametrize("recipient", ("operator", "operator2"))
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
    recipient: str,
    malformation: str,
) -> None:
    root, lawful_fields, report_path, head, base = _authority_fixture(
        tmp_path / "repo",
        mode="independent-lane-v",
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


@pytest.mark.parametrize("recipient", ("operator", "operator2"))
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
    recipient: str,
    malformation: str,
) -> None:
    root, lawful_fields, report_path, head, _ = _authority_fixture(
        tmp_path / "repo",
        mode="independent-lane-v",
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
        ) -> gate.ScopeReference:
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
        "verifier",
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
    if mismatch == "verifier":
        values["Verification mode"] = "codex-lane-v"
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
    if mismatch == "verifier":
        with pytest.raises(gate.ReportGateError, match="invalid_attestation_value"):
            gate.parse_lane_v_report(
                report_path,
                _report_bytes(mutated, head=h1_head),
            )
        return
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
    fields = _replace_field(fields, "Reviewer identity", "operator")
    report = gate.parse_lane_v_report(
        REPORT_PATH,
        _report_bytes(fields, head=head, envelope_sender="operator"),
    )

    with pytest.raises(gate.ReportGateError, match="recipient"):
        gate.validate_live_report(root, report)


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
        task_store_factory=lambda _root: fixture.store,
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
    (root / "governance.toml").write_text(
        '[protocol.kernel]\nepoch = 0\nwriter = "v1"\n', encoding="utf-8"
    )
    (root / "scripts" / "codex_protocol_model.py").write_text(
        "# fixture\n", encoding="utf-8"
    )
    agent = root / ".claude" / "agents" / "lane-v-verifier.md"
    agent.parent.mkdir(parents=True, exist_ok=True)
    agent.write_text("---\nname: fixture\n---\nfixture\n", encoding="utf-8")


@dataclasses.dataclass(frozen=True)
class _LiveLaneVFixture:
    root: Path
    report: gate.LaneVReport
    authority: gate.StructuralAuthority
    store: gate.TaskPublicationStore
    raw: bytes


def _live_lane_v_fixture(
    root: Path,
    *,
    default_store: bool = False,
    recipient: str = "operator2",
) -> _LiveLaneVFixture:
    root, fields, report_path, head, _ = _authority_fixture(
        root,
        mode="independent-lane-v",
        trigger_kind="verify-request",
        recipient=recipient,
    )
    fields = _replace_field(fields, "Reviewer identity", recipient)
    raw = _report_bytes(
        fields,
        head=head,
        h1_sender=recipient.capitalize(),
        envelope_sender=recipient,
    )
    report = gate.parse_lane_v_report(report_path, raw)
    authority = gate.validate_structural_authority(root, report)
    store = gate.TaskPublicationStore.for_repo(
        root,
        state_root=None if default_store else root / ".task-publications",
    )
    gate.validate_live_report(
        root,
        report,
        task_store_factory=lambda _root: store,
    )
    return _LiveLaneVFixture(root, report, authority, store, raw)


_LiveCodexFixture = _LiveLaneVFixture
_LiveClaudeFixture = _LiveLaneVFixture


def _live_codex_fixture(
    root: Path, *, default_store: bool = False
) -> _LiveLaneVFixture:
    return _live_lane_v_fixture(root, default_store=default_store)


def _live_claude_fixture(root: Path) -> _LiveLaneVFixture:
    return _live_lane_v_fixture(root)
def _candidate_path(root: Path, raw: bytes, name: str = ".report.candidate.tmp") -> Path:
    sent = root / "coordination" / "mailbox" / "sent"
    sent.mkdir(parents=True, exist_ok=True)
    candidate = sent / name
    candidate.write_bytes(raw)
    candidate.chmod(0o600)
    return candidate


def test_live_validation_creates_exact_ready_task_record(
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

    assert validated.state == "ready"
    assert validated.task_id == TASK_ID
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


def test_publish_and_status_retain_exact_task_index_witness(
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


def test_publish_writer_fence_denial_precedes_task_final_and_index_mutation(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    fixture = _live_claude_fixture(tmp_path / "repo")
    candidate = _candidate_path(fixture.root, fixture.raw)
    with fixture.store.lock_task(TASK_ID) as task:
        before = task.load_existing()

    @contextlib.contextmanager
    def deny(*_args: object, **_kwargs: object):
        raise kernel_activation.KernelSelectionError("wrong writer")
        yield

    monkeypatch.setattr(gate, "writer_fence", deny)
    with pytest.raises(kernel_activation.KernelSelectionError, match="wrong writer"):
        gate.publish_candidate(
            repo_root=fixture.root,
            candidate_path=candidate,
            final_relative=fixture.report.relative_path,
            task_store_factory=lambda _root: fixture.store,
        )

    with fixture.store.lock_task(TASK_ID) as task:
        assert task.load_existing() == before
    assert candidate.exists()
    assert not (fixture.root / fixture.report.relative_path).exists()
    assert _git(fixture.root, "ls-files", "--stage", "--", fixture.report.relative_path) == ""


def test_resume_writer_fence_denial_precedes_task_final_and_index_mutation(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    fixture = _live_claude_fixture(tmp_path / "repo")
    candidate = _candidate_path(fixture.root, fixture.raw, ".interrupted.tmp")
    _begin_interrupted_publication(fixture, candidate, fixture.report.relative_path)
    with fixture.store.lock_task(TASK_ID) as task:
        before = task.load_existing()

    @contextlib.contextmanager
    def deny(*_args: object, **_kwargs: object):
        raise kernel_activation.KernelSelectionError("wrong writer")
        yield

    monkeypatch.setattr(gate, "writer_fence", deny)
    with pytest.raises(kernel_activation.KernelSelectionError, match="wrong writer"):
        gate.resume_publication(
            repo_root=fixture.root,
            task_id=TASK_ID,
            task_store_factory=lambda _root: fixture.store,
        )

    with fixture.store.lock_task(TASK_ID) as task:
        assert task.load_existing() == before
    assert candidate.exists()
    assert not (fixture.root / fixture.report.relative_path).exists()
    assert _git(fixture.root, "ls-files", "--stage", "--", fixture.report.relative_path) == ""


def _published_default_fixture(root: Path) -> _LiveLaneVFixture:
    fixture = _live_lane_v_fixture(root, default_store=True)
    candidate = _candidate_path(fixture.root, fixture.raw)
    gate.publish_candidate(
        repo_root=fixture.root,
        candidate_path=candidate,
        final_relative=fixture.report.relative_path,
    )
    return fixture


def test_read_only_published_report_validation_accepts_exact_witness(
    tmp_path: Path,
) -> None:
    fixture = _published_default_fixture(tmp_path / "repo")

    record = gate.validate_published_report(fixture.root, fixture.report)

    assert record.state == "published"
    assert record.path == fixture.report.relative_path
    assert record.candidate_digest == fixture.report.body_digest
    assert record.index_mode == "100644"
    assert record.index_stage == 0


def test_repository_report_validation_ignores_replace_refs_for_exact_head_blob(
    tmp_path: Path,
) -> None:
    fixture = _live_lane_v_fixture(tmp_path / "repo")
    report_file = fixture.root / fixture.report.relative_path
    report_file.parent.mkdir(parents=True, exist_ok=True)
    report_file.write_bytes(fixture.raw)
    _git(fixture.root, "add", fixture.report.relative_path)
    _git(fixture.root, "commit", "-q", "-m", "docs: commit Lane V report")
    exact_head = _git(fixture.root, "rev-parse", "HEAD")
    report_file.write_bytes(fixture.raw.replace(b"VERDICT: GO", b"VERDICT: NITS"))
    _git(fixture.root, "add", fixture.report.relative_path)
    attacker_tree = _git(fixture.root, "write-tree")
    attacker = subprocess.run(
        ["/usr/bin/git", "commit-tree", attacker_tree, "-p", f"{exact_head}^"],
        cwd=fixture.root,
        input="docs: replacement report\n",
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()
    _git(fixture.root, "reset", "-q", "--hard", exact_head)
    _git(fixture.root, "replace", exact_head, attacker)

    gate.validate_repository_report(fixture.root, fixture.report)

    assert not (
        fixture.root / ".codex/runtime/lane-v-report-publications/v1"
    ).exists()


@pytest.mark.parametrize("state", ["ready", "publishing"])
def test_read_only_published_report_validation_rejects_unfinished_state(
    tmp_path: Path,
    state: str,
) -> None:
    fixture = _live_lane_v_fixture(tmp_path / "repo", default_store=True)
    if state == "publishing":
        candidate = _candidate_path(fixture.root, fixture.raw)
        _begin_interrupted_publication(
            fixture, candidate, fixture.report.relative_path
        )

    with pytest.raises(gate.ReportGateError, match="task_publication_not_published"):
        gate.validate_published_report(fixture.root, fixture.report)


@pytest.mark.parametrize(
    "mutation",
    ["authority", "path", "raw-digest", "index-witness"],
)
def test_read_only_published_report_validation_rejects_wrong_witness(
    tmp_path: Path,
    mutation: str,
) -> None:
    fixture = _published_default_fixture(tmp_path / "repo")
    record_path = fixture.store.state_root / f"{TASK_ID}.json"
    value = json.loads(record_path.read_text(encoding="utf-8"))
    if mutation == "authority":
        value["authority_digest"] = "sha256:" + "9" * 64
    elif mutation == "path":
        value["path"] = value["path"].replace("05-00-00Z", "05-00-01Z")
    elif mutation == "raw-digest":
        value["candidate_digest"] = "sha256:" + "9" * 64
    else:
        value["index_blob_oid"] = "9" * len(value["index_blob_oid"])
    record_path.write_bytes(gate.canonical_json_bytes(value))

    with pytest.raises(gate.ReportGateError):
        gate.validate_published_report(fixture.root, fixture.report)


@pytest.mark.parametrize("surface", ["root", "lock", "record"])
def test_read_only_published_report_validation_rejects_unsafe_private_metadata(
    tmp_path: Path,
    surface: str,
) -> None:
    fixture = _published_default_fixture(tmp_path / "repo")
    target = {
        "root": fixture.store.state_root,
        "lock": fixture.store.state_root / f"{TASK_ID}.lock",
        "record": fixture.store.state_root / f"{TASK_ID}.json",
    }[surface]
    target.chmod(0o755 if surface == "root" else 0o644)

    with pytest.raises(gate.ReportGateError, match="unsafe"):
        gate.validate_published_report(fixture.root, fixture.report)


@pytest.mark.parametrize("surface", ["lock", "record"])
def test_read_only_published_report_validation_does_not_recreate_missing_state(
    tmp_path: Path,
    surface: str,
) -> None:
    fixture = _published_default_fixture(tmp_path / "repo")
    target = fixture.store.state_root / f"{TASK_ID}.{surface}"
    if surface == "record":
        target = target.with_suffix(".json")
    target.unlink()

    with pytest.raises(gate.ReportGateError, match="task_publication_missing"):
        gate.validate_published_report(fixture.root, fixture.report)

    assert not target.exists()


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


def test_task_publication_store_creates_private_owned_root_lock_and_record(
    tmp_path: Path,
) -> None:
    state_root = tmp_path / "state"
    store = gate.TaskPublicationStore.for_repo(tmp_path, state_root=state_root)
    root_stat = state_root.stat()
    assert stat.S_IMODE(root_stat.st_mode) == 0o700
    assert root_stat.st_uid == os.getuid()

    with store.lock_task(TASK_ID) as task:
        task.load_or_create("sha256:" + "7" * 64)

    for path in (
        state_root / f"{TASK_ID}.lock",
        state_root / f"{TASK_ID}.json",
    ):
        observed = path.stat()
        assert stat.S_ISREG(observed.st_mode)
        assert stat.S_IMODE(observed.st_mode) == 0o600
        assert observed.st_uid == os.getuid()
        assert observed.st_nlink == 1


def _install_private_state_substitution(path: Path, kind: str) -> None:
    if kind == "directory":
        path.mkdir()
    elif kind == "symlink":
        backing = path.with_suffix(".backing")
        backing.write_bytes(b"{}")
        backing.chmod(0o600)
        path.symlink_to(backing.name)
    elif kind == "fifo":
        os.mkfifo(path, 0o600)
    elif kind == "hardlink":
        backing = path.with_suffix(".backing")
        backing.write_bytes(b"{}")
        backing.chmod(0o600)
        os.link(backing, path)
    elif kind == "wrong-mode":
        path.write_bytes(b"{}")
        path.chmod(0o644)
    elif kind == "wrong-owner":
        path.write_bytes(b"{}")
        path.chmod(0o600)
    else:  # pragma: no cover - the parameter list is closed below
        raise AssertionError(kind)


@pytest.mark.parametrize(
    "kind", ("directory", "symlink", "fifo", "hardlink", "wrong-mode", "wrong-owner")
)
@pytest.mark.parametrize("target", ("lock", "record"))
def test_task_publication_store_rejects_private_state_substitutions_before_transition(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    target: str,
    kind: str,
) -> None:
    state_root = tmp_path / f"state-{target}-{kind}"
    store = gate.TaskPublicationStore.for_repo(tmp_path, state_root=state_root)
    lock_path = state_root / f"{TASK_ID}.lock"
    record_path = state_root / f"{TASK_ID}.json"
    selected = lock_path if target == "lock" else record_path

    real_fstat = gate.os.fstat

    def wrong_owner(fd: int) -> object:
        observed = real_fstat(fd)
        return SimpleNamespace(
            st_mode=observed.st_mode,
            st_uid=os.getuid() + 1,
            st_nlink=observed.st_nlink,
        )

    if target == "lock":
        _install_private_state_substitution(selected, kind)
        if kind == "wrong-owner":
            monkeypatch.setattr(gate.os, "fstat", wrong_owner)
        with pytest.raises((gate.ReportGateError, gate.ScopeContractError, OSError)):
            with store.lock_task(TASK_ID):
                pytest.fail("unsafe lock unexpectedly opened")
    else:
        with store.lock_task(TASK_ID) as task:
            _install_private_state_substitution(selected, kind)
            before = selected.lstat()
            if kind == "wrong-owner":
                monkeypatch.setattr(gate.os, "fstat", wrong_owner)
            with pytest.raises((gate.ReportGateError, gate.ScopeContractError, OSError)):
                task.load_or_create("sha256:" + "7" * 64)
            after = selected.lstat()
            assert (after.st_mode, after.st_ino) == (before.st_mode, before.st_ino)

    assert not (tmp_path / "coordination" / "mailbox" / "sent").exists()


def test_task_publication_store_rejects_wrong_mode_root_before_state_access(
    tmp_path: Path,
) -> None:
    state_root = tmp_path / "state-root-mode"
    store = gate.TaskPublicationStore.for_repo(tmp_path, state_root=state_root)
    state_root.chmod(0o755)

    with pytest.raises((gate.ReportGateError, gate.ScopeContractError, OSError)):
        with store.lock_task(TASK_ID):
            pytest.fail("unsafe private root unexpectedly opened")
    assert not (state_root / f"{TASK_ID}.json").exists()


@pytest.mark.parametrize("mutation", ("wrong-owner", "wrong-mode", "wrong-type"))
def test_task_publication_store_rejects_unsafe_root_metadata_before_state_access(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    mutation: str,
) -> None:
    state_root = tmp_path / f"state-root-{mutation}"
    state_root.mkdir(mode=0o700)
    real_fstat = gate.os.fstat

    def unsafe_root(fd: int) -> object:
        observed = real_fstat(fd)
        mode = observed.st_mode
        owner = observed.st_uid
        if mutation == "wrong-owner":
            owner += 1
        elif mutation == "wrong-mode":
            mode = stat.S_IFDIR | 0o755
        else:
            mode = stat.S_IFREG | 0o700
        return SimpleNamespace(
            st_mode=mode,
            st_uid=owner,
            st_nlink=observed.st_nlink,
            st_dev=observed.st_dev,
            st_ino=observed.st_ino,
        )

    monkeypatch.setattr(gate.os, "fstat", unsafe_root)
    with pytest.raises(gate.ScopeContractError, match="unsafe_private_directory"):
        gate._ensure_private_directory(state_root)

    assert not (state_root / f"{TASK_ID}.json").exists()


@pytest.mark.parametrize("kind", ("file", "symlink"))
def test_task_publication_store_rejects_non_directory_root_before_state_access(
    tmp_path: Path, kind: str
) -> None:
    state_root = tmp_path / f"state-root-{kind}"
    if kind == "file":
        state_root.write_text("not a directory\n", encoding="utf-8")
    else:
        backing = tmp_path / "backing-root"
        backing.mkdir(mode=0o700)
        state_root.symlink_to(backing, target_is_directory=True)

    with pytest.raises(gate.ScopeContractError, match="unsafe_private_directory"):
        gate._ensure_private_directory(state_root)


def test_private_directory_rejects_symlink_swap_to_same_observed_inode(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    state_root = tmp_path / "state-root-race"
    state_root.mkdir(mode=0o700)
    displaced = tmp_path / "state-root-observed"
    original_open = gate.os.open
    swapped = False

    def swap_before_open(path: object, flags: int, *args: object, **kwargs: object) -> int:
        nonlocal swapped
        if not swapped and os.fspath(path) == os.fspath(state_root):
            swapped = True
            state_root.rename(displaced)
            state_root.symlink_to(displaced, target_is_directory=True)
        return original_open(path, flags, *args, **kwargs)

    monkeypatch.setattr(gate.os, "open", swap_before_open)
    opened: int | None = None
    try:
        with pytest.raises(gate.ScopeContractError, match="unsafe_private_directory"):
            opened = gate._ensure_private_directory(state_root)
    finally:
        if opened is not None:
            os.close(opened)

    assert swapped is True


@pytest.mark.parametrize("target", ("lock", "record"))
@pytest.mark.parametrize("mutation", ("wrong-owner", "nlink"))
def test_task_publication_store_uses_injected_metadata_check_for_each_private_file(
    tmp_path: Path,
    target: str,
    mutation: str,
) -> None:
    state_root = tmp_path / f"state-injected-{target}-{mutation}"
    store = gate.TaskPublicationStore.for_repo(tmp_path, state_root=state_root)
    with store.lock_task(TASK_ID) as task:
        task.load_or_create("sha256:" + "7" * 64)
    record_path = state_root / f"{TASK_ID}.json"
    before = record_path.read_bytes()
    real_fstat = os.fstat

    def unsafe_file(fd: int) -> object:
        observed = real_fstat(fd)
        return SimpleNamespace(
            st_mode=observed.st_mode,
            st_uid=(os.getuid() + 1 if mutation == "wrong-owner" else observed.st_uid),
            st_nlink=(2 if mutation == "nlink" else observed.st_nlink),
        )

    unsafe_store = dataclasses.replace(store, _stat_fn=unsafe_file)
    if target == "lock":
        with pytest.raises(gate.ScopeContractError, match="unsafe_private_file"):
            with unsafe_store.lock_task(TASK_ID):
                pytest.fail("unsafe lock unexpectedly opened")
    else:
        with store.lock_task(TASK_ID) as task:
            task._store = unsafe_store
            with pytest.raises(gate.ScopeContractError, match="unsafe_private_file"):
                task.load_existing()

    assert record_path.read_bytes() == before


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
    record_path.write_bytes(gate.canonical_json_bytes(value))

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
    record_path.write_bytes(gate.canonical_json_bytes(value))

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
        task_store_factory=lambda _root: fixture.store,
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
    with fixture.store.lock_task(TASK_ID) as attempt:
        record = attempt.load_existing()
    assert record.state == "published"
    expected_oid = _git_with_input(
        fixture.root, captured, "hash-object", "--no-filters", "--stdin"
    )
    assert {field: getattr(record, field) for field in gate._TASK_WITNESS_FIELDS} == {
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
        task_id=TASK_ID,
        task_store_factory=lambda _root: fixture.store,
    )
    assert before == {
        "state": "ready",
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
        task_store_factory=lambda _root: fixture.store,
    )

    status = gate.publication_status(
        repo_root=fixture.root,
        task_id=TASK_ID,
        task_store_factory=lambda _root: fixture.store,
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
            task_id=TASK_ID,
            task_store_factory=lambda _root: fixture.store,
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
            task_store_factory=lambda _root: fixture.store,
        )
    status = gate.publication_status(
        repo_root=fixture.root,
        task_id=TASK_ID,
        task_store_factory=lambda _root: fixture.store,
    )
    assert status["state"] == "publishing"
    assert status["file_witness_match"] is True
    assert status["staged_blob_match"] is True

    published = gate.resume_publication(
        repo_root=fixture.root,
        task_id=TASK_ID,
        task_store_factory=lambda _root: fixture.store,
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
            task_store_factory=lambda _root: fixture.store,
        )
    assert candidate.read_bytes() == replacement
    assert saved.read_bytes() == fixture.raw
    with fixture.store.lock_task(TASK_ID) as attempt:
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
            task_id=TASK_ID,
            task_store_factory=lambda _root: fixture.store,
        )
    assert candidate.read_bytes() == replacement
    assert saved.read_bytes() == fixture.raw
    with fixture.store.lock_task(TASK_ID) as attempt:
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
            task_store_factory=lambda _root: fixture.store,
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
            task_id=TASK_ID,
            task_store_factory=lambda _root: fixture.store,
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
        task_store_factory=lambda _root: fixture.store,
    )
    os.link(published, candidate)

    with pytest.raises(gate.ReportGateError, match="published_witness_divergence"):
        gate.publication_status(
            repo_root=fixture.root,
            task_id=TASK_ID,
            task_store_factory=lambda _root: fixture.store,
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
            task_id=TASK_ID,
            task_store_factory=lambda _root: fixture.store,
        )
    with fixture.store.lock_task(TASK_ID) as attempt:
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
            task_id=TASK_ID,
            task_store_factory=lambda _root: fixture.store,
        )
    with fixture.store.lock_task(TASK_ID) as attempt:
        record = attempt.load_existing()
    assert record.state == "ready"
    assert record.generation == 3
    assert all(getattr(record, field) is None for field in gate._TASK_WITNESS_FIELDS)


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
            task_id=TASK_ID,
            task_store_factory=lambda _root: fixture.store,
        )

    with fixture.store.lock_task(TASK_ID) as attempt:
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
            "--task-id",
            TASK_ID,
        ]
    )

    captured = capsys.readouterr()
    assert result == 0
    assert captured.err == ""
    assert captured.out.count("\n") == 1
    assert captured.out == (
        gate.canonical_json_bytes(json.loads(captured.out)).decode("utf-8") + "\n"
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
                _lane_v_fields(reviewer="operator2"), "Verification task ID", wrong_task_id
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
            "--task-id",
            TASK_ID,
        ]
    )

    captured = capsys.readouterr()
    assert result == 6
    assert "publication_status_required" in captured.err
    assert f"--task-id {TASK_ID}" in captured.err
    with fixture.store.lock_task(TASK_ID) as attempt:
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
            "--task-id",
            TASK_ID,
        ]
    )

    captured = capsys.readouterr()
    assert result == 6
    assert "publication_status_required" in captured.err
    assert f"--task-id {TASK_ID}" in captured.err


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
            task_store_factory=lambda _root: fixture.store,
        )

    _assert_last_boundary_mutation_applied(fixture, candidate, mutation)
    with fixture.store.lock_task(TASK_ID) as attempt:
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
            task_id=TASK_ID,
            task_store_factory=lambda _root: fixture.store,
        )

    _assert_last_boundary_mutation_applied(fixture, candidate, mutation)
    with fixture.store.lock_task(TASK_ID) as attempt:
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


def _expected_candidate_witness(
    root: Path, candidate: Path, raw: bytes, final_relative: str
) -> dict[str, object]:
    observed = candidate.stat()
    return {
        "path": final_relative,
        "candidate_digest": "sha256:" + hashlib.sha256(raw).hexdigest(),
        "candidate_name": candidate.name,
        "candidate_device": observed.st_dev,
        "candidate_inode": observed.st_ino,
        "index_blob_oid": _git_with_input(
            root, raw, "hash-object", "--no-filters", "--stdin"
        ),
        "index_mode": "100644",
        "index_stage": 0,
    }


@pytest.mark.parametrize("candidate_case", ["fresh", "substituted", "stored"])
def test_existing_publishing_state_cleans_only_distinct_fresh_candidate(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    candidate_case: str,
) -> None:
    fixture = _live_lane_v_fixture(tmp_path / "repo")
    store = fixture.store
    gate.validate_live_report(
        fixture.root,
        fixture.report,
        task_store_factory=lambda _root: store,
    )
    stored_candidate = _candidate_path(
        fixture.root, fixture.raw, ".stored-witness.tmp"
    )
    stored_witness = _expected_candidate_witness(
        fixture.root,
        stored_candidate,
        fixture.raw,
        fixture.report.relative_path,
    )
    with store.lock_task(TASK_ID) as attempt:
        attempt.load_existing()
        attempt.begin_publication(
            *(stored_witness[field] for field in gate._TASK_WITNESS_FIELDS)
        )

    stored_identity = (
        stored_candidate.stat().st_dev,
        stored_candidate.stat().st_ino,
    )
    candidate = (
        stored_candidate
        if candidate_case == "stored"
        else _candidate_path(fixture.root, fixture.raw, ".fresh-unowned.tmp")
    )
    foreign_raw = b"foreign substituted object\n"
    cleanup_calls = 0
    real_cleanup = gate._cleanup_unbound_candidate

    def cleanup_after_optional_substitution(
        captured: object, sent_fd: int
    ) -> None:
        nonlocal cleanup_calls
        cleanup_calls += 1
        if candidate_case == "substituted":
            replacement = candidate.with_name(".foreign-substitute.tmp")
            replacement.write_bytes(foreign_raw)
            replacement.chmod(0o600)
            os.replace(replacement, candidate)
        real_cleanup(captured, sent_fd)

    monkeypatch.setattr(
        gate, "_cleanup_unbound_candidate", cleanup_after_optional_substitution
    )
    with pytest.raises(gate.ReportGateError) as excinfo:
        gate.publish_candidate(
            repo_root=fixture.root,
            candidate_path=candidate,
            final_relative=fixture.report.relative_path,
            task_store_factory=lambda _root: store,
        )

    assert excinfo.value.reason == "publication_resume_required"
    assert cleanup_calls == (0 if candidate_case == "stored" else 1)
    with store.lock_task(TASK_ID) as attempt:
        observed = attempt.load_existing()
    assert observed.state == "publishing"
    assert gate._stored_publication_witness(observed) == stored_witness
    assert (
        stored_candidate.stat().st_dev,
        stored_candidate.stat().st_ino,
    ) == stored_identity
    if candidate_case == "substituted":
        assert candidate.read_bytes() == foreign_raw
    elif candidate_case == "fresh":
        assert not candidate.exists()




def test_task_begin_post_replace_fsync_failure_retains_witnessed_candidate(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
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
    expected = _expected_candidate_witness(
        fixture.root, candidate, fixture.raw, fixture.report.relative_path
    )
    state_directory = store.state_root.stat()
    injected = _inject_fsync_error(
        monkeypatch,
        lambda metadata: stat.S_ISDIR(metadata.st_mode)
        and (metadata.st_dev, metadata.st_ino)
        == (state_directory.st_dev, state_directory.st_ino),
    )

    with pytest.raises(gate.ReportGateError, match="publication_resumable"):
        gate.publish_candidate(
            repo_root=fixture.root,
            candidate_path=candidate,
            final_relative=fixture.report.relative_path,
            task_store_factory=lambda _root: store,
        )

    assert injected["raised"] is True
    with store.lock_task(TASK_ID) as task:
        record = task.load_existing()
    assert record.state == "publishing"
    assert gate._stored_publication_witness(record) == expected
    assert candidate.exists()


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
            task_store_factory=lambda _root: fixture.store,
        )

    assert injected["raised"] is True
    assert not (fixture.root / fixture.report.relative_path).exists()
    with fixture.store.lock_task(TASK_ID) as attempt:
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
            task_store_factory=lambda _root: fixture.store,
        )

    assert injected["raised"] is True
    assert (fixture.root / fixture.report.relative_path).stat().st_nlink == 2
    with fixture.store.lock_task(TASK_ID) as attempt:
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
            task_id=TASK_ID,
            task_store_factory=lambda _root: fixture.store,
        )

    assert injected["raised"] is True
    with fixture.store.lock_task(TASK_ID) as attempt:
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
            task_id=TASK_ID,
            task_store_factory=lambda _root: fixture.store,
        )

    assert injected["raised"] is True
    with fixture.store.lock_task(TASK_ID) as attempt:
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
            task_store_factory=lambda _root: fixture.store,
        )
    with fixture.store.lock_task(TASK_ID) as attempt:
        record = attempt.load_existing()
    expected_state = (
        "ready"
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
            task_id=TASK_ID,
            task_store_factory=lambda _root: fixture.store,
        )
        assert published == fixture.root / fixture.report.relative_path
    elif record.state == "published":
        status = gate.publication_status(
            repo_root=fixture.root,
            task_id=TASK_ID,
            task_store_factory=lambda _root: fixture.store,
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
            task_id=TASK_ID,
            task_store_factory=lambda _root: fixture.store,
        )
    with fixture.store.lock_task(TASK_ID) as attempt:
        record = attempt.load_existing()
    expected_state = "published" if checkpoint == "resume_after_published" else "publishing"
    assert record.state == expected_state

    monkeypatch.setattr(gate, "_publication_checkpoint", lambda _label: None)
    if record.state == "publishing":
        published = gate.resume_publication(
            repo_root=fixture.root,
            task_id=TASK_ID,
            task_store_factory=lambda _root: fixture.store,
        )
        assert published == fixture.root / fixture.report.relative_path
    else:
        status = gate.publication_status(
            repo_root=fixture.root,
            task_id=TASK_ID,
            task_store_factory=lambda _root: fixture.store,
        )
        assert status["state"] == "published"


def test_publish_candidate_rejects_validation_failure_before_state_or_final(
    tmp_path: Path,
) -> None:
    fixture = _live_codex_fixture(tmp_path / "repo")
    invalid = fixture.raw.replace(
        b"Reviewer identity: operator2", b"Reviewer identity: operator"
    )
    candidate = _candidate_path(fixture.root, invalid)

    with pytest.raises(gate.ReportGateError):
        gate.publish_candidate(
            repo_root=fixture.root,
            candidate_path=candidate,
            final_relative=fixture.report.relative_path,
            task_store_factory=lambda _root: fixture.store,
        )

    assert not (fixture.root / fixture.report.relative_path).exists()
    with fixture.store.lock_task(TASK_ID) as attempt:
        record = attempt.load_existing()
    assert record.state == "ready"


def test_publish_candidate_public_replay_and_fresh_file_exists_cancel_fail(
    tmp_path: Path,
) -> None:
    replay = _live_codex_fixture(tmp_path / "replay")
    first = _candidate_path(replay.root, replay.raw, ".first.tmp")
    gate.publish_candidate(
        repo_root=replay.root,
        candidate_path=first,
        final_relative=replay.report.relative_path,
        task_store_factory=lambda _root: replay.store,
    )
    second = _candidate_path(replay.root, replay.raw, ".second.tmp")
    with pytest.raises(gate.ReportGateError, match="published"):
        gate.publish_candidate(
            repo_root=replay.root,
            candidate_path=second,
            final_relative=replay.report.relative_path,
            task_store_factory=lambda _root: replay.store,
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
            task_store_factory=lambda _root: collision.store,
        )
    with collision.store.lock_task(TASK_ID) as attempt:
        record = attempt.load_existing()
    assert record.state == "ready"
    assert record.generation == 3
    assert final.read_bytes() == collision.raw


def _begin_interrupted_publication(
    fixture: _LiveCodexFixture,
    candidate: Path,
    relative: str,
) -> gate.TaskPublicationRecord:
    observed = candidate.stat()
    raw = candidate.read_bytes()
    digest = "sha256:" + hashlib.sha256(raw).hexdigest()
    blob_oid = _git_with_input(
        fixture.root, raw, "hash-object", "--no-filters", "--stdin"
    )
    gate.validate_live_report(
        fixture.root,
        fixture.report,
        task_store_factory=lambda _root: fixture.store,
    )
    with fixture.store.lock_task(TASK_ID) as attempt:
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
            task_store_factory=lambda _root: absent.store,
        )
    published = gate.resume_publication(
        repo_root=absent.root,
        task_id=TASK_ID,
        task_store_factory=lambda _root: absent.store,
    )
    assert published == absent.root / absent.report.relative_path
    assert not old_absent.exists()
    assert not new_absent.exists()
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
        task_id=TASK_ID,
        task_store_factory=lambda _root: exact.store,
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
            task_id=TASK_ID,
            task_store_factory=lambda _root: fixture.store,
        )

    with fixture.store.lock_task(TASK_ID) as attempt:
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
            task_store_factory=lambda _root: fixture.store,
        )
    assert not (fixture.root / fixture.report.relative_path).exists()
    with fixture.store.lock_task(TASK_ID) as attempt:
        assert attempt.load_existing().state == "ready"


def _pre_v3_manifest(*entries: tuple[str, str]) -> dict[str, object]:
    return {
        "schema_version": PRE_V3_SCHEMA,
        "reports": [
            {"path": path, "sha256": digest} for path, digest in entries
        ],
    }


def test_pre_v3_manifest_accepts_exact_shape_and_defers_changed_digest() -> None:
    digest = hashlib.sha256(b"legacy body\n").hexdigest()
    manifest = _pre_v3_manifest((REPORT_PATH, digest))

    assert gate.pre_v3_manifest_violations(manifest, [REPORT_PATH]) == []


@pytest.mark.parametrize(
    "manifest",
    [
        pytest.param({}, id="missing-top-fields"),
        pytest.param(
            {"schema_version": "wrong", "reports": []}, id="wrong-schema"
        ),
        pytest.param(
            {"schema_version": PRE_V3_SCHEMA, "reports": "not-a-list"},
            id="reports-not-list",
        ),
        pytest.param(
            {
                "schema_version": PRE_V3_SCHEMA,
                "reports": [{"path": REPORT_PATH, "sha256": "A" * 64}],
            },
            id="uppercase-digest",
        ),
        pytest.param(
            {
                "schema_version": PRE_V3_SCHEMA,
                "reports": [
                    {"path": REPORT_PATH, "sha256": "1" * 64},
                    {"path": REPORT_PATH, "sha256": "2" * 64},
                ],
            },
            id="duplicate-path",
        ),
        pytest.param(
            {
                "schema_version": PRE_V3_SCHEMA,
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
def test_pre_v3_manifest_rejects_invalid_shape_and_duplicates(
    manifest: object,
) -> None:
    assert gate.pre_v3_manifest_violations(manifest, [REPORT_PATH])


def test_pre_v3_manifest_reports_missing_paths_but_not_digest_drift() -> None:
    manifest = _pre_v3_manifest((REPORT_PATH, "1" * 64))

    missing = gate.pre_v3_manifest_violations(manifest, [])
    present_with_changed_digest = gate.pre_v3_manifest_violations(
        manifest, [REPORT_PATH]
    )

    assert missing == [f"{REPORT_PATH}: missing historical baseline report"]
    assert present_with_changed_digest == []


def test_task_publisher_and_status_reject_injected_legacy_reconciled_state(
    tmp_path: Path,
) -> None:
    legacy = SimpleNamespace(state="reconciled")

    with pytest.raises(gate.ReportGateError, match="invalid_publication_state"):
        gate._locked_publish_new(
            attempt=SimpleNamespace(),
            record=legacy,
            root=tmp_path,
            final_relative=REPORT_PATH,
            candidate=SimpleNamespace(raw=b"must not be read"),
            sent_fd=-1,
            git=SimpleNamespace(),
            set_candidate_ownership=lambda _owned: None,
        )
    with pytest.raises(gate.ReportGateError, match="invalid_publication_state"):
        gate._status_locked(record=legacy, sent_fd=None, git=SimpleNamespace())


def test_task_record_validation_rejects_direct_legacy_state_injection() -> None:
    record = gate.TaskPublicationRecord(
        task_id=TASK_ID,
        authority_digest="sha256:" + "7" * 64,
        state="reconciled",
        generation=1,
        path=None,
        candidate_digest=None,
        candidate_name=None,
        candidate_device=None,
        candidate_inode=None,
        index_blob_oid=None,
        index_mode=None,
        index_stage=None,
    )

    with pytest.raises(gate.ReportGateError, match="invalid_task_publication"):
        gate._validate_task_record(record, record.authority_digest)


def test_task4_gate_source_has_no_legacy_reconciled_state_acceptance() -> None:
    source = inspect.getsource(gate)

    assert '"reconciled"' not in source
