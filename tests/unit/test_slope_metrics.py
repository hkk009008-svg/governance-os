"""Behavior tests for the read-only quality-slope reporter."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parent.parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

import slope_metrics  # noqa: E402

_SENT = "coordination/mailbox/sent"
_HEX_A = "a" * 40
_HEAD_C = "c" * 40
_HEAD_D = "d" * 40
_HEAD_E = "e" * 40
_HEAD_F = "f" * 40
_HEAD_9 = "9" * 40


def _git_env(tmp_path: Path) -> dict[str, str]:
    return {"PATH": "/usr/bin:/bin", "HOME": str(tmp_path)}


def _init_repo(tmp_path: Path) -> Path:
    root = tmp_path / "repo"
    root.mkdir()
    env = _git_env(tmp_path)
    subprocess.run(["git", "init", "-q"], cwd=root, check=True, env=env)
    subprocess.run(
        ["git", "config", "user.email", "probe@example.invalid"],
        cwd=root, check=True, env=env,
    )
    subprocess.run(
        ["git", "config", "user.name", "probe"], cwd=root, check=True, env=env
    )
    return root


def _commit(root: Path, tmp_path: Path, message: str, when: str) -> str:
    env = _git_env(tmp_path)
    env["GIT_AUTHOR_DATE"] = when
    env["GIT_COMMITTER_DATE"] = when
    subprocess.run(["git", "add", "-A"], cwd=root, check=True, env=env)
    subprocess.run(
        ["git", "commit", "-q", "-m", message], cwd=root, check=True, env=env
    )
    out = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=root, check=True, env=env, capture_output=True,
    )
    return out.stdout.decode().strip()


def _request(name: str, head: str | None, remediates: str | None = None) -> str:
    lines = ["Event type: verify-request", f"Reviewed base: {_HEX_A}"]
    if head is not None:
        lines.append(f"Reviewed head: {head}")
    lines.append("Risk class: material-behavior")
    if remediates is not None:
        lines.append(f"Remediates failed report: {_SENT}/{remediates}@{_HEX_A}")
    return "\n".join(lines) + "\n"


def _report(
    verdict: str,
    request_name: str | None,
    head: str,
    supersedes: str | None = None,
) -> str:
    lines = ["Event type: verification-report", f"VERDICT: {verdict}"]
    if request_name is not None:
        lines.append(f"Verification request: {_SENT}/{request_name}@{_HEX_A}")
    lines.append(f"Reviewed head: {head}")
    lines.append(f"Reviewed base: {_HEX_A}")
    if supersedes is not None:
        lines.append(f"Supersedes: {_SENT}/{supersedes}@{_HEX_A}")
    return "\n".join(lines) + "\n"


REQ1 = "2026-01-15T10-00-00Z-director-to-operator-verify-request.md"
REP1 = "2026-01-15T10-30-00Z-operator-to-director-verification-report.md"
REQ2 = "2026-01-20T10-00-00Z-director-to-operator-verify-request.md"
REP2F = "2026-01-20T11-00-00Z-operator-to-director-verification-report.md"
REP2G = "2026-01-20T12-00-00Z-operator-to-director-verification-report.md"
REQ3 = "2026-01-21T10-00-00Z-director-to-operator-verify-request.md"
REP3F = "2026-01-21T11-00-00Z-operator-to-director-verification-report.md"
REP3G = "2026-01-21T12-00-00Z-operator-to-director-verification-report.md"
REQ4 = "2026-01-22T10-00-00Z-director-to-operator-verify-request.md"
REP4F = "2026-01-22T11-00-00Z-operator-to-director-verification-report.md"
REQ5 = "2026-01-22T12-00-00Z-director-to-operator-verify-request.md"
REP5G = "2026-01-22T13-00-00Z-operator-to-director-verification-report.md"
REQ6 = "2026-01-23T10-00-00Z-director-to-operator-verify-request.md"
REPX = "2026-01-24T10-00-00Z-operator-to-all-verification-report.md"


def _build_two_window_repo(tmp_path: Path) -> tuple[Path, str, str]:
    root = _init_repo(tmp_path)
    (root / "README.md").write_text("plain fixture readme\n", encoding="utf-8")
    tests_dir = root / "tests" / "unit"
    tests_dir.mkdir(parents=True)
    (tests_dir / "test_base.py").write_text(
        "def test_base():\n    assert True\n", encoding="utf-8"
    )
    first = _commit(root, tmp_path, "base", "2026-01-19T09:00:00 +0000")

    sent = root / _SENT
    sent.mkdir(parents=True)
    (sent / REQ1).write_text(_request(REQ1, head=first), encoding="utf-8")
    (sent / REP1).write_text(_report("GO", REQ1, head=first), encoding="utf-8")
    (sent / REQ2).write_text(_request(REQ2, head=_HEAD_C), encoding="utf-8")
    (sent / REP2F).write_text(_report("FAIL", REQ2, head=_HEAD_C), encoding="utf-8")
    (sent / REP2G).write_text(
        _report("GO", REQ2, head=_HEAD_D, supersedes=REP2F), encoding="utf-8"
    )
    (sent / REQ3).write_text(_request(REQ3, head=_HEAD_E), encoding="utf-8")
    (sent / REP3F).write_text(_report("FAIL", REQ3, head=_HEAD_E), encoding="utf-8")
    (sent / REP3G).write_text(_report("GO", REQ3, head=_HEAD_E), encoding="utf-8")
    (sent / REQ4).write_text(_request(REQ4, head=_HEAD_F), encoding="utf-8")
    (sent / REP4F).write_text(_report("FAIL", REQ4, head=_HEAD_F), encoding="utf-8")
    (sent / REQ5).write_text(
        _request(REQ5, head=_HEAD_9, remediates=REP4F), encoding="utf-8"
    )
    (sent / REP5G).write_text(_report("GO", REQ5, head=_HEAD_9), encoding="utf-8")
    (sent / REQ6).write_text(_request(REQ6, head=None), encoding="utf-8")
    (sent / REPX).write_text(_report("GO", None, head=_HEAD_9), encoding="utf-8")

    docs = root / "docs"
    docs.mkdir()
    (docs / "note.md").write_text(
        "This change is guaranteed to hold everywhere.\n", encoding="utf-8"
    )
    (tests_dir / "test_pinned.py").write_text(
        "import pytest\n\n\n"
        "@pytest.mark.xfail(strict=True, reason='pinned defect')\n"
        "def test_pinned():\n    assert False\n\n\n"
        "def test_mentions_pin_in_string():\n"
        "    text = \"@pytest.mark.xfail(strict=True, reason='quoted')\"\n"
        "    assert text\n",
        encoding="utf-8",
    )
    ledger_dir = root / "logs" / "claims"
    ledger_dir.mkdir(parents=True)
    rows = [
        {
            "claim": "window one claim",
            "when": "2026-01-15T12:00:00+00:00",
            "premises": [{"status": "MEASURED"}, {"status": "ASSUMED"}],
        },
        {
            "claim": "window two claim",
            "when": "2026-01-20T12:00:00Z",
            "premises": [{"status": "INFERRED"}],
        },
        {"claim": "undated claim", "premises": [{"status": "MEASURED"}]},
    ]
    (ledger_dir / "ledger.jsonl").write_text(
        "".join(json.dumps(row) + "\n" for row in rows), encoding="utf-8"
    )
    second = _commit(root, tmp_path, "events", "2026-01-26T09:00:00 +0000")
    return root, first, second


def test_two_window_slope_counts_chains_heads_and_context(tmp_path: Path) -> None:
    root, first, second = _build_two_window_repo(tmp_path)
    slope = slope_metrics.collect_slope(
        root, commit="HEAD", windows=2, window_days=7
    )

    assert slope["commit"] == second
    assert slope["warnings"] == []
    assert set(slope["not_measurable"]) == {
        "requirement_retention_over_steps",
        "recovery_after_compaction",
        "hook_intervention_precision",
    }

    totals = slope["totals"]
    assert totals["requests"] == 6
    assert totals["reports"] == 8
    assert totals["verdicts"] == {"GO": 5, "NITS": 0, "FAIL": 3, "unparsed": 0}
    assert totals["reports_without_request_ref"] == 1
    assert totals["fail_chains"]["fails"] == 3
    assert totals["fail_chains"]["closed_head_changed"] == 2
    assert totals["fail_chains"]["closed_same_head"] == 1
    assert totals["fail_chains"]["no_recorded_closure"] == 0
    assert totals["fail_chains"]["closure_routes"] == {
        "supersedes": 1,
        "same_request": 1,
        "remediation_request": 1,
    }
    assert totals["events_before_first_window"] == {"requests": 0, "reports": 0}

    older, newer = slope["series"]
    assert older["requests"] == 1
    assert older["reports"] == 1
    assert older["first_pass"] == {"go": 1, "total": 1}
    assert older["review_latency_median_seconds"] == 1800.0
    assert older["reviewed_heads"] == {
        "landed": 1, "unlanded": 0, "unresolvable": 0
    }
    assert older["fail_chains"]["fails"] == 0
    assert older["boundary_commit"] == first
    assert older["pins_open"] == 0
    assert older["overclaim"]["flags"] == 0
    assert older["claims_ledger"] == {
        "rows": 1, "premises": {"MEASURED": 1, "ASSUMED": 1}
    }

    assert newer["requests"] == 5
    assert newer["reports"] == 7
    assert newer["verdicts"] == {"GO": 4, "NITS": 0, "FAIL": 3, "unparsed": 0}
    assert newer["first_pass"] == {"go": 1, "total": 4}
    assert newer["reviewed_heads"] == {
        "landed": 0, "unlanded": 4, "unresolvable": 1
    }
    assert newer["fail_chains"]["fails"] == 3
    assert newer["fail_chains"]["no_recorded_closure"] == 0
    assert newer["fail_chains"]["remediation_requests"] == 1
    assert newer["fail_chains"]["median_closure_seconds"] == 3600.0
    assert newer["boundary_commit"] == second
    assert newer["pins_open"] == 1, (
        "anchored decorator counts once; the quoted fixture mention must not"
    )
    assert newer["overclaim"]["flags"] >= 1
    assert newer["overclaim"]["range"] == f"{first[:12]}..{second[:12]}"
    assert any("docs/note.md" in item for item in newer["overclaim"]["examples"])
    assert newer["claims_ledger"] == {"rows": 1, "premises": {"INFERRED": 1}}


def test_minimal_repo_without_events_or_ledger(tmp_path: Path) -> None:
    root = _init_repo(tmp_path)
    (root / "README.md").write_text("empty fixture\n", encoding="utf-8")
    _commit(root, tmp_path, "init", "2026-01-26T09:00:00 +0000")
    slope = slope_metrics.collect_slope(
        root, commit="HEAD", windows=2, window_days=7
    )
    assert slope["totals"]["requests"] == 0
    assert slope["totals"]["reports"] == 0
    assert slope["warnings"] == []
    newest = slope["series"][-1]
    assert newest["claims_ledger"] is None
    assert newest["requests"] == 0
    assert newest["fail_chains"]["fails"] == 0


def test_main_is_advisory_and_json_renders(tmp_path: Path, capsys) -> None:
    root, _, second = _build_two_window_repo(tmp_path)
    exit_code = slope_metrics.main(
        ["--repo-root", str(root), "--windows", "2", "--window-days", "7", "--json"]
    )
    assert exit_code == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["commit"] == second
    assert payload["sources"]

    exit_code = slope_metrics.main(
        ["--repo-root", str(root), "--windows", "2", "--window-days", "7"]
    )
    assert exit_code == 0
    text = capsys.readouterr().out
    assert "quality slope at" in text
    assert "not measurable:" in text
