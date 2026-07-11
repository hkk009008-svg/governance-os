"""The committed comparator corpus must match expected.json exactly."""
from __future__ import annotations

from pathlib import Path

import route_compat

FIXTURES = Path(__file__).resolve().parent.parent / "fixtures" / "route_compat"


def test_corpus_matches_expectations(tmp_path):
    report = route_compat.run_corpus(FIXTURES)
    mismatches = [case for case in report["cases"] if not case["matches_expectation"]]
    assert report["all_match"], mismatches


def test_report_is_machine_readable(tmp_path):
    report = route_compat.run_corpus(FIXTURES)
    assert report["schema"] == "governance.route-compat-report/1"
    assert len(report["cases"]) == 9
    for case in report["cases"]:
        assert set(case) >= {
            "name", "legacy_valid", "legacy_gates", "structured_valid",
            "structured_issues", "divergence", "matches_expectation",
        }
