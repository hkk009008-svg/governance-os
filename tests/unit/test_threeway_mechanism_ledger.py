"""Coverage for scripts/threeway_mechanism_ledger.py (previously only run in smoke)."""

from __future__ import annotations

from pathlib import Path

import pytest

import threeway_mechanism_ledger as ledger
from threeway import LOAD_BEARING_KINDS

ROOT = Path(__file__).resolve().parents[2]


def test_rows_cover_exactly_the_load_bearing_kinds() -> None:
    rows = ledger.collect_mechanisms()
    assert set(rows) == set(LOAD_BEARING_KINDS)


def test_cited_emitter_and_test_files_exist() -> None:
    rows = ledger.collect_mechanisms()
    for row in rows.values():
        for test in row.tests:
            assert (ROOT / test).is_file(), (row.kind, test)
        if row.emitters:
            emitter = row.emitters[0].split()[0]
            assert (ROOT / emitter).is_file(), (row.kind, emitter)


def test_render_is_deterministic_and_has_a_row_per_kind() -> None:
    rows = ledger.collect_mechanisms()
    first = ledger.render_markdown(rows)
    assert ledger.render_markdown(rows) == first
    for kind in LOAD_BEARING_KINDS:
        assert f"| `{kind}` |" in first
    assert "(no dedicated test)" in first  # some kinds are honestly untested


def test_check_passes_against_the_committed_ledger() -> None:
    assert ledger.main(["--check"]) == 0


def test_check_detects_a_stale_committed_ledger(monkeypatch, capsys) -> None:
    real = ledger.render_markdown

    def _drifted(rows):
        return real(rows) + "\nstale trailing line\n"

    monkeypatch.setattr(ledger, "render_markdown", _drifted)
    assert ledger.main(["--check"]) == 1
    assert "stale" in capsys.readouterr().err.lower()


def test_collect_detects_missing_kind(monkeypatch) -> None:
    trimmed = dict(ledger._ROWS)
    trimmed.pop(next(iter(trimmed)))
    monkeypatch.setattr(ledger, "_ROWS", trimmed)
    with pytest.raises(AssertionError, match="ledger drift"):
        ledger.collect_mechanisms()
