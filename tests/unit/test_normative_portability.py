"""Current instructions are checkout-portable without rewriting history."""
from __future__ import annotations

import hashlib
import re
from pathlib import Path


NORMATIVE_SURFACES = (
    "README.md",
    "OPERATIONS.md",
    "CLAUDE.md",
    "coordination/README.md",
    "docs/protocol/codex/continuation.md",
    "docs/protocol/codex/ledger-cli-adoption.md",
    "docs/protocol/claude/ledger-cli-adoption.md",
    "docs/protocol/threeway/HEADLESS-REVIEW.md",
)

HISTORICAL_SENTINELS = {
    "docs/superpowers/plans/2026-07-18-chatgpt-pro-consult-fd-first-toctou.md":
        "9ddb4355cde9e9e1675722d0f9bb97957e03992fe44870b67ed7d3adb970628b",
    "coordination/capacity/packets/2026-07-12-ledger-ppl-recommendation-evaluation-director-implementation.json":
        "7ec702ba587bc693909c681ce0c2a38eb2b319499f4c6c0262898a642fcdaea2",
}


def test_normative_current_surfaces_have_no_literal_user_home(repo_root: Path):
    pattern = re.compile(r"/Users/[^/\s]+")
    for relative in NORMATIVE_SURFACES:
        body = (repo_root / relative).read_text(encoding="utf-8")
        assert not pattern.search(body), relative


def test_portability_cutover_does_not_rewrite_historical_artifacts(repo_root: Path):
    for relative, expected in HISTORICAL_SENTINELS.items():
        actual = hashlib.sha256((repo_root / relative).read_bytes()).hexdigest()
        assert actual == expected, relative


def test_headless_cursor_status_uses_cursor_seat(repo_root: Path):
    body = (repo_root / "docs/protocol/threeway/HEADLESS-REVIEW.md").read_text(
        encoding="utf-8"
    )
    assert "coordination/bin/cursor-seat status" in body
    status_lines = [line for line in body.splitlines() if "status" in line.lower()]
    assert all("target_binding.py" not in line for line in status_lines)
