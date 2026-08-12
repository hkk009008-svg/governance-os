"""Tests for the AGY read-only observer's optional orientation view."""

from __future__ import annotations

import agy_observer


def test_summarize_bus_can_prepend_compact_snapshot(monkeypatch, capsys, tmp_path):
    orientation = {"generated_at": "2026-08-04T00:00:00Z"}
    monkeypatch.setattr(
        agy_observer.status,
        "collect_orientation_snapshot",
        lambda repo_root: orientation,
    )
    monkeypatch.setattr(
        agy_observer.status,
        "render_orientation_snapshot",
        lambda snapshot: "Rendered snapshot\n",
    )

    summary = agy_observer.summarize_bus(tmp_path, snapshot=True)

    assert summary["total_events"] == 0
    assert capsys.readouterr().out == (
        "=== Compact Orientation Snapshot ===\n"
        "Rendered snapshot\n"
        "=== RAW Event Bus Summary ===\n"
        "Bus is currently empty.\n"
    )


def test_main_forwards_snapshot_option(monkeypatch, tmp_path):
    observed = []
    monkeypatch.setattr(
        agy_observer,
        "summarize_bus",
        lambda repo_dir, snapshot=False: observed.append((repo_dir, snapshot)),
    )

    assert agy_observer.main(["--repo-dir", str(tmp_path), "--snapshot"]) == 0
    assert observed == [(str(tmp_path), True)]
