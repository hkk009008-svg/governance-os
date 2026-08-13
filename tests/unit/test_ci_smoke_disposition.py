"""Focused fail-closed disposition tests for governance smoke."""

from __future__ import annotations

from pathlib import Path
from types import SimpleNamespace

import check_coordination
import check_doc_claims
import check_no_ceremony
import governance_verify_all as ci_smoke
import pytest


ROOT = Path(ci_smoke._REPO_ROOT)


def _issue(severity: str) -> SimpleNamespace:
    return SimpleNamespace(
        severity=severity,
        kind="fixture",
        path="coordination/fixture",
        message=f"{severity.lower()} fixture",
    )


def _drift(kind: str) -> check_doc_claims.Drift:
    return check_doc_claims.Drift(
        doc_path=str(ROOT / "ARCHITECTURE.md"),
        doc_line=10,
        target_file="scripts/fixture.py",
        target_line=20,
        kind=kind,
        symbol="fixture",
        suggested_line=21,
        fixable=kind != "ambiguous_path",
        message=f"{kind} fixture",
    )


@pytest.mark.parametrize("args", ([], ["--fast"]))
def test_ci_coordination_fatal_blocks_full_and_fast_call_sites(
    monkeypatch, args: list[str]
) -> None:
    calls: list[tuple[Path, Path]] = []

    def fatal(coordination: Path, *, docs_root: Path):
        calls.append((coordination, docs_root))
        return [_issue("FATAL")]

    monkeypatch.setenv("CI", "true")
    monkeypatch.setattr(ci_smoke, "_project_smoke", lambda: 0)
    monkeypatch.setattr(check_coordination, "run", fatal)
    monkeypatch.setattr(
        check_no_ceremony,
        "main",
        lambda: pytest.fail("FATAL disposition was bypassed"),
    )
    if not args:
        monkeypatch.setattr(ci_smoke, "_architecture_gate", lambda _root: 0)

    assert ci_smoke.main(args) == 1
    assert calls == [(ROOT / "coordination", ROOT / "docs")]


def test_coordination_advisory_warns_but_is_exit_neutral(
    monkeypatch, capsys
) -> None:
    monkeypatch.setenv("CI", "true")
    monkeypatch.setattr(check_coordination, "run", lambda *args, **kwargs: [_issue("ADVISORY")])

    assert ci_smoke._coordination_gate(ROOT) == 0
    assert "WARNING: coordination ADVISORY" in capsys.readouterr().out


def test_ci_architecture_fatal_uses_canonical_split_and_blocks_main(
    monkeypatch
) -> None:
    drift = _drift("def_drift")
    run_calls: list[tuple[list[str], Path]] = []
    split_calls: list[list[check_doc_claims.Drift]] = []
    split = check_doc_claims._split_advisories

    def run(paths: list[str], root: Path):
        run_calls.append((paths, root))
        return [drift]

    def classify(drifts: list[check_doc_claims.Drift]):
        split_calls.append(drifts)
        return split(drifts)

    monkeypatch.setenv("CI", "true")
    monkeypatch.setattr(ci_smoke, "_project_smoke", lambda: 0)
    monkeypatch.setattr(check_doc_claims, "run", run)
    monkeypatch.setattr(check_doc_claims, "_split_advisories", classify)

    assert ci_smoke.main([]) == 1
    assert run_calls == [(["ARCHITECTURE.md"], ROOT)]
    assert split_calls == [[drift]]


def test_architecture_advisory_warns_but_is_exit_neutral(
    monkeypatch, capsys
) -> None:
    drift = _drift("ambiguous_path")
    monkeypatch.setenv("CI", "true")
    monkeypatch.setattr(check_doc_claims, "run", lambda *args, **kwargs: [drift])

    assert ci_smoke._architecture_gate(ROOT) == 0
    assert "WARNING: ARCHITECTURE advisory" in capsys.readouterr().out


def test_workflow_keeps_parallel_verification_and_signer_dependencies() -> None:
    workflow = (ROOT / ".github/workflows/ci.yml").read_text(encoding="utf-8")

    assert "  smoke:\n" in workflow
    assert "  pytest:\n" in workflow
    assert "  threeway-ci-result:\n" in workflow
    assert "    needs: [smoke, pytest]\n" in workflow
    assert (
        "    if: github.event_name == 'workflow_dispatch' && "
        "vars.THREEWAY_BUS_LIVE == 'true' && github.ref == 'refs/heads/main'\n"
        in workflow
    )


def test_same_kind_advisory_flood_prints_one_summary_line(
    tmp_path, monkeypatch, capsys
):
    """More than three same-kind advisories collapse to one x-count line;
    small groups stay itemized and FATALs are never grouped."""

    import check_coordination as cc

    flood = [
        cc.CoordIssue(f"mailbox/sent/event-{index}.md", "grandfathered_review_history",
                      "ADVISORY", "exception remains active")
        for index in range(6)
    ]
    pair = [
        cc.CoordIssue("mailbox/sent/one.md", "another_kind", "ADVISORY", "first"),
        cc.CoordIssue("mailbox/sent/two.md", "another_kind", "ADVISORY", "second"),
    ]
    monkeypatch.setattr(cc, "run", lambda *args, **kwargs: flood + pair)

    assert ci_smoke._coordination_gate(tmp_path) == 0
    out = capsys.readouterr().out

    assert out.count("grandfathered_review_history") == 1
    assert "x6" in out
    assert "itemize with" in out
    assert out.count("another_kind") == 2
    assert "first" in out and "second" in out
