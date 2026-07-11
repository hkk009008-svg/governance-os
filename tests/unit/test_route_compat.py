"""The committed comparator corpus must match expected.json exactly."""
from __future__ import annotations

import json
import shutil
from pathlib import Path

import pytest

import route_compat
from test_route_manifest import _route

FIXTURES = Path(__file__).resolve().parent.parent / "fixtures" / "route_compat"


def _mini_corpus(tmp_path: Path, route_relpath: str) -> Path:
    """A one-case synthetic corpus whose expected.json pins a hostile route_relpath."""
    fixtures = tmp_path / "fixtures"
    (fixtures / "packets").mkdir(parents=True)
    case_dir = fixtures / "cases" / "escape-case"
    case_dir.mkdir(parents=True)
    (case_dir / "route.json").write_text(json.dumps(_route()), encoding="utf-8")
    expected = {
        "escape-case": {
            "legacy_valid": False,
            "structured_valid": False,
            "divergence": None,
            "route_relpath": route_relpath,
        }
    }
    (fixtures / "expected.json").write_text(json.dumps(expected), encoding="utf-8")
    return fixtures


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


# --- F3: expected.json route_relpath must be confined to the corpus root ---


def test_run_corpus_rejects_absolute_route_relpath(tmp_path):
    fixtures = _mini_corpus(tmp_path, str(tmp_path / "abs_escape.md"))
    with pytest.raises(ValueError):
        route_compat.run_corpus(fixtures)


def test_run_corpus_rejects_escaping_route_relpath(tmp_path):
    fixtures = _mini_corpus(tmp_path, "../escape.md")
    with pytest.raises(ValueError):
        route_compat.run_corpus(fixtures)


# --- F5: drifted legacy failure gates must break all_match, not just validity ---


def test_tampered_legacy_gates_breaks_all_match(tmp_path):
    dst = tmp_path / "fixtures"
    shutil.copytree(FIXTURES, dst)
    expected = json.loads((dst / "expected.json").read_text(encoding="utf-8"))
    expected["missing-side-effect-token"]["legacy_gates"] = ["G99"]
    (dst / "expected.json").write_text(json.dumps(expected), encoding="utf-8")
    report = route_compat.run_corpus(dst)
    assert not report["all_match"]
