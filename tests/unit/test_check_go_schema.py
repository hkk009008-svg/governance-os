from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path

import pytest

import check_go_schema as schema
import compact_pair_loop as pair


def _manifest(*entries: tuple[str, bytes]) -> dict[str, object]:
    return {
        "schema_version": "lane-v-report-pre-v3-baseline/v1",
        "reports": [
            {"path": path, "sha256": hashlib.sha256(raw).hexdigest()}
            for path, raw in entries
        ],
    }


def test_go_evidence_requires_command_output_and_durable_subject() -> None:
    valid = """\
# Operator → All: report commit `abcdef1`

VERDICT: GO

## Evidence
$ pytest -q
→ 1 passed
"""
    assert schema.go_report_violations([("valid.md", valid)]) == []

    violations = schema.go_report_violations(
        [("invalid.md", valid.replace("→ 1 passed\n", ""))]
    )
    assert any("output" in item for item in violations)


@pytest.mark.parametrize("verdict", ("NITS", "FAIL"))
def test_non_go_report_does_not_claim_success_evidence(verdict: str) -> None:
    assert schema.go_report_violations(
        [("truthful.md", f"VERDICT: {verdict}\n")]
    ) == []


def test_pre_v3_bytes_are_accepted_only_by_exact_manifest_path_and_digest(
    tmp_path: Path,
) -> None:
    path = (
        "coordination/mailbox/sent/"
        "2026-07-01T00-00-00Z-operator-to-all-verification-report.md"
    )
    raw = b"# historical\n\nVERDICT: FAIL\n"
    manifest = _manifest((path, raw))

    assert schema.repository_report_violations(
        tmp_path, [schema.RawReport(path, raw)], manifest
    ) == []
    assert schema.repository_report_violations(
        tmp_path, [schema.RawReport(path, raw + b"changed\n")], manifest
    )
    assert schema.repository_report_violations(
        tmp_path,
        [schema.RawReport(path.replace("00-00-00", "00-00-01"), raw)],
        manifest,
    )


def test_manifest_rejects_duplicate_paths_and_digests(tmp_path: Path) -> None:
    path = tmp_path / "manifest.json"
    digest = "a" * 64
    path.write_text(
        json.dumps(
            {
                "schema_version": "lane-v-report-pre-v3-baseline/v1",
                "reports": [
                    {"path": "coordination/mailbox/sent/a-verification-report.md", "sha256": digest},
                    {"path": "coordination/mailbox/sent/a-verification-report.md", "sha256": digest},
                ],
            }
        ),
        encoding="utf-8",
    )

    with pytest.raises(schema.BaselineGenerationError, match="duplicate"):
        schema.load_baseline_manifest(path)


def test_filesystem_scan_reads_regular_reports_and_rejects_symlinks(
    tmp_path: Path,
) -> None:
    sent = tmp_path / "coordination/mailbox/sent"
    sent.mkdir(parents=True)
    report = sent / "2026-07-01T00-00-00Z-operator-to-all-verification-report.md"
    report.write_text("VERDICT: FAIL\n", encoding="utf-8")

    assert [item.relative_path for item in schema.scan_repository_reports(tmp_path)] == [
        report.relative_to(tmp_path).as_posix()
    ]

    report.unlink()
    outside = tmp_path / "outside"
    outside.write_text("VERDICT: GO\n", encoding="utf-8")
    report.symlink_to(outside)
    with pytest.raises(OSError):
        schema.scan_repository_reports(tmp_path)

def test_live_mailbox_is_valid_against_frozen_history_and_compact_current_rules() -> None:
    reports = schema.scan_repository_reports(schema.ROOT)
    manifest = schema.load_baseline_manifest(schema.DEFAULT_MANIFEST)

    assert schema.repository_report_violations(schema.ROOT, reports, manifest) == []


def test_report_compatibility_is_narrow_across_each_frozen_generation() -> None:
    pre_v3_path = (
        "coordination/mailbox/sent/"
        "2026-07-07T09-52-13Z-operator-to-all-verification-report.md"
    )
    historical_v3_path = (
        "coordination/mailbox/sent/"
        "2026-07-17T04-59-08Z-operator-to-all-verification-report.md"
    )
    verbose_compact_path = (
        "coordination/mailbox/sent/"
        "2026-07-17T13-17-10Z-operator-to-director-verification-report.md"
    )
    pre_v3 = (schema.ROOT / pre_v3_path).read_bytes()
    historical_v3 = (schema.ROOT / historical_v3_path).read_bytes()
    verbose_compact = (schema.ROOT / verbose_compact_path).read_bytes()

    assert schema.repository_report_violations(
        schema.ROOT,
        [schema.RawReport(pre_v3_path, pre_v3)],
        _manifest((pre_v3_path, pre_v3)),
    ) == []
    assert schema.repository_report_violations(
        schema.ROOT,
        [schema.RawReport(historical_v3_path, historical_v3)],
        _manifest(),
    ) == []
    assert schema.repository_report_violations(
        schema.ROOT,
        [schema.RawReport(verbose_compact_path, verbose_compact)],
        _manifest(),
    ) == []
    parsed = pair.parse_verification_report(schema.ROOT, verbose_compact_path)
    assert parsed.finding_refs == ()
    assert parsed.finding_dispositions == ()


def test_baseline_generation_surface_is_retired() -> None:
    assert not hasattr(schema, "generate_baseline")
    assert schema.main(["--generate-baseline", "elsewhere.json"]) != 0


def test_scan_rejects_fifo_without_blocking(tmp_path: Path) -> None:
    if not hasattr(os, "mkfifo"):
        pytest.skip("FIFO unavailable")
    sent = tmp_path / "coordination/mailbox/sent"
    sent.mkdir(parents=True)
    os.mkfifo(sent / "2026-07-01T00-00-00Z-operator-to-all-verification-report.md")

    with pytest.raises(OSError):
        schema.scan_repository_reports(tmp_path)
