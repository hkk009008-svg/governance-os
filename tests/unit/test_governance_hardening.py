from __future__ import annotations

import contextlib
import io
from pathlib import Path
from types import SimpleNamespace

import check_doc_claims
import check_placeholders
import governance_verify_all as ci_smoke
import pytest


ROOT = Path(__file__).resolve().parents[2]
ROOT_TRUTH_DOCS = (
    "README.md",
    "ARCHITECTURE.md",
    "OPERATIONS.md",
    "docs/PROGRAM-MANUAL.md",
)


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def test_root_truth_docs_are_bound_not_placeholder_allowlisted():
    allowed = check_placeholders._load_allowlist(ROOT / "pipeline/placeholder_allowlist.txt")

    for rel in ROOT_TRUTH_DOCS:
        text = (ROOT / rel).read_text(encoding="utf-8")
        assert rel not in allowed
        for token in check_placeholders.TOKENS:
            assert token not in text


def test_root_truth_docs_identify_pipeline_governance_kernel():
    combined = "\n".join((ROOT / rel).read_text(encoding="utf-8") for rel in ROOT_TRUTH_DOCS)

    assert "Pipeline is the governance kernel" in combined
    assert "evidence-ledger is the bound product target" in combined
    assert "ARCHITECTURE.md records verified governance-kernel truth" in combined


def test_sha_ref_baseline_status_detects_new_or_changed_drift(tmp_path: Path):
    known = check_doc_claims.Drift(
        doc_path=str(tmp_path / "KNOWN.md"),
        doc_line=7,
        target_file="",
        target_line=0,
        kind="sha_not_found",
        symbol="deadbee",
        suggested_line=None,
        fixable=False,
        message="`deadbee` does not resolve to a commit",
    )
    new = check_doc_claims.Drift(
        doc_path=str(tmp_path / "NEW.md"),
        doc_line=9,
        target_file="",
        target_line=0,
        kind="sha_subject_mismatch",
        symbol="badcafe",
        suggested_line=None,
        fixable=False,
        message="`badcafe` quoted subject does not match actual",
    )
    baseline_digest = check_doc_claims.sha_ref_drift_digest([known], tmp_path)

    clean_status = check_doc_claims.classify_sha_ref_baseline(
        [known],
        tmp_path,
        expected_count=1,
        expected_digest=baseline_digest,
    )
    drift_status = check_doc_claims.classify_sha_ref_baseline(
        [known, new],
        tmp_path,
        expected_count=1,
        expected_digest=baseline_digest,
    )

    assert clean_status.matches_baseline
    assert clean_status.new_or_changed_count == 0
    assert "SHA provenance is NOT CLEAN" not in clean_status.warning_line
    assert not drift_status.matches_baseline
    assert drift_status.new_or_changed_count == 1
    assert "SHA provenance is NOT CLEAN" in drift_status.warning_line


def test_ci_smoke_is_quiet_for_reviewed_sha_ref_baseline():
    buf = io.StringIO()

    with contextlib.redirect_stdout(buf):
        rc = ci_smoke.main()

    out = buf.getvalue()
    assert rc == 0
    assert "SHA provenance is NOT CLEAN" not in out
    assert "baselined stale commit-SHA" not in out
