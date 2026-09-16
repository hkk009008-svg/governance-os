"""The orientation document set stays small, current, and free of retired surfaces."""
from __future__ import annotations

import re
from pathlib import Path

import cli


ORIENTATION_DOCS = (
    "AGENTS.md",
    "CLAUDE.md",
    "README.md",
    "ARCHITECTURE.md",
    "OPERATIONS.md",
    "DECISIONS.md",
    "coordination/README.md",
    "docs/protocol/agents/risk-classes.md",
)
# Total bytes a member reads to orient. Raise it only with a stated reason in
# the same commit. The 2026-09-15 analysis measured 29,214 bytes over 19
# files; the consolidated set measured about 14,400 bytes over 8 files.
BUDGET_BYTES = 15_000
RETIRED_SURFACES = (
    "seat", "marker metadata", "capacity packet", "RUNBOOK", "TRANSFER",
    "four-seat", "pipeline-python", ".env.example", "continuation.md",
    "peer.md", "independence-first",
)
_COMMAND = re.compile(r"bin/pipeline ((?:[a-z]+)(?: [a-z]+)?)")


def _texts(repo_root: Path) -> dict[str, str]:
    return {doc: (repo_root / doc).read_text(encoding="utf-8") for doc in ORIENTATION_DOCS}


def test_orientation_set_fits_its_budget_and_has_no_stray_protocol_files(repo_root: Path) -> None:
    total = sum(len(text.encode("utf-8")) for text in _texts(repo_root).values())
    assert total <= BUDGET_BYTES, f"orientation set is {total} bytes"
    protocol = sorted(
        path.relative_to(repo_root).as_posix()
        for path in (repo_root / "docs/protocol").rglob("*.md")
    )
    assert protocol == ["docs/protocol/agents/risk-classes.md"]


def test_orientation_docs_name_no_retired_surfaces(repo_root: Path) -> None:
    for doc, text in _texts(repo_root).items():
        for token in RETIRED_SURFACES:
            assert token not in text, (doc, token)


def test_every_documented_command_dispatches(repo_root: Path) -> None:
    for doc, text in _texts(repo_root).items():
        for match in _COMMAND.finditer(text):
            words = match.group(1).split()
            assert cli._resolve(words) is not None, (doc, match.group(0))


def test_budget_control_would_catch_the_old_document_set() -> None:
    assert 29_214 > BUDGET_BYTES
