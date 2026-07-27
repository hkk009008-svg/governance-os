"""Tests for the formation-time claim discipline engine.

The grammar's tether to reality is the nine-claims fixture: every entry is a
claim actually made in the 2026-07-26/27 session, paired with the premise whose
omission produced the measured failure. The grammar exists to hand an author
that premise without recall, so the one test that matters is that it does — and
the negative control beside it is what keeps that test honest, because a
classifier that assigned every premise to every claim would pass the fixture
while teaching nothing.
"""

from __future__ import annotations

import json
import subprocess
from pathlib import Path

import pytest

from scripts import claim_check


# (claim as made, premise that would have named the miss)
NINE_MEASURED_FAILURES = (
    # Round 1: held only in the author's checkout; failed in every worktree.
    (
        "Measured, not assumed: this control is verified and passes in every checkout",
        "environment-of-record",
    ),
    # Rounds 2-3: the form list was an enumeration; :/ then :x then ://x won.
    (
        "The guard refuses every pathspec magic form; coverage is complete",
        "space-generated",
    ),
    # Round 4: trackedness of the path stood in for the committed rule bytes.
    (
        "The provenance check cites the committed rule; the reference anchors it",
        "is-the-named-document",
    ),
    # The comment that outlived its mechanism: no instrument existed any more.
    (
        "The emitted argv is checked against this set and verified against agy --help",
        "instrument-cited",
    ),
    # The preflight gate nothing on the dispatch path invoked.
    (
        "The parity gate is enforced pre-dispatch on every launch",
        "invoked-on-path",
    ),
    # The readiness assertion that recomputed all(rows) beside the rows.
    (
        "main is verified not ready when any row fails",
        "instrument-independent",
    ),
    # Three fabricated references, each forty well-formed hex characters.
    (
        "finding ref sha256:857f... and the report @2ae144202a8417c39e87426bb60da4d3d5a7b481 anchor the FAIL",
        "resolves",
    ),
    # The regex over help text deciding what a Go parser accepts.
    (
        "defined_cli_flags returns the flags the installed CLI defines and accepts",
        "authority-asked",
    ),
    # The dry-run believed free that executed a prompt.
    (
        "the probe costs nothing extra and cannot spend during dry-run",
        "behavior-observed",
    ),
)


@pytest.mark.parametrize("claim,missed", NINE_MEASURED_FAILURES)
def test_grammar_hands_the_author_the_premise_that_was_actually_missed(
    claim: str, missed: str
) -> None:
    keys = [premise.key for _, premise in claim_check.premises_for(claim)]
    assert missed in keys, (claim, keys)


def test_a_neutral_claim_gets_only_the_generic_premises() -> None:
    """The negative control that keeps the fixture above honest.

    A classifier that matched every shape on every sentence would satisfy all
    nine fixture rows while discriminating nothing — the exact combined-assert
    vacuity this repository keeps re-finding. So a sentence with no claim
    vocabulary must classify to nothing and receive only the generic premises.
    """
    claim = "the refactor moves two helpers into a shared module"
    assert claim_check.classify(claim) == []
    keys = [premise.key for _, premise in claim_check.premises_for(claim)]
    assert keys == [premise.key for premise in claim_check.GENERIC_PREMISES]


def test_every_claim_carries_the_embarrassing_command_premise() -> None:
    """Every miss in the source session was one command from detection."""
    for claim, _ in NINE_MEASURED_FAILURES:
        keys = [premise.key for _, premise in claim_check.premises_for(claim)]
        assert "embarrassing-command-run" in keys, claim


def test_probe_prompt_carries_the_claim_and_no_working_context() -> None:
    """Amnesia is the probe's entire value, so leakage is the defect to pin.

    The prompt must contain the claim and the fixed instructions — never the
    cwd, environment, or anything else that would let the reader inherit the
    author's context.
    """
    claim = "the gate is enforced on every launch"
    prompt = claim_check.build_probe_prompt(claim)

    assert claim in prompt
    assert "amnesiac" in prompt
    import os

    assert os.getcwd() not in prompt
    assert "GIT_INDEX_FILE" not in prompt


def test_record_writes_assumed_rows_for_unsupplied_premises(tmp_path: Path) -> None:
    """The blank cell exists by construction, not by diligence.

    An unstated premise is invisible; an ASSUMED row is refusable. `record`
    therefore fills every grammar premise the author did not cite, so the
    ledger shows what was skipped rather than only what was done.
    """
    ledger = tmp_path / "ledger.jsonl"
    entry = claim_check.record_entry(
        {
            "claim": "the sweep is verified on every launch",
            "premises": [
                {"key": "instrument-cited", "status": "MEASURED", "cite": "$ pytest -q → 36 passed"}
            ],
            "kills_attempted": ["deleted the call site; test failed"],
        },
        ledger,
    )

    statuses = {row["key"]: row["status"] for row in entry["premises"]}
    assert statuses["instrument-cited"] == "MEASURED"
    assert statuses["invoked-on-path"] == "ASSUMED"
    written = json.loads(ledger.read_text(encoding="utf-8").splitlines()[0])
    assert written["claim"] == entry["claim"]


def test_audit_flags_weak_premises_and_unkilled_claims(tmp_path: Path) -> None:
    ledger = tmp_path / "ledger.jsonl"
    claim_check.record_entry(
        {
            "claim": "the gate is enforced on every launch",
            "premises": [
                {"key": "invoked-on-path", "status": "REMEMBERED", "cite": "I am fairly sure"}
            ],
        },
        ledger,
    )

    problems = claim_check.audit_ledger(ledger)

    assert any("REMEMBERED" in problem for problem in problems)
    assert any("ASSUMED" in problem for problem in problems)
    assert any("NO-KILL" in problem for problem in problems)


def test_audit_passes_a_fully_cited_killed_claim(tmp_path: Path) -> None:
    """The positive control: a clean entry must not be flagged.

    Without this, an audit that flagged everything would satisfy the test
    above while making the ledger unusable.
    """
    ledger = tmp_path / "ledger.jsonl"
    claim = "the refactor moves two helpers into a shared module"
    claim_check.record_entry(
        {
            "claim": claim,
            "premises": [
                {"key": "falsifier-named", "status": "MEASURED", "cite": "$ pytest → red on revert"},
                {"key": "embarrassing-command-run", "status": "MEASURED", "cite": "$ grep -rn helper → 2 sites"},
            ],
            "kills_attempted": ["reverted the move; suite failed"],
        },
        ledger,
    )

    assert claim_check.audit_ledger(ledger) == []


def _throwaway_repo(tmp_path: Path) -> Path:
    """A repository built for the test, never the checkout under review."""
    root = tmp_path / "repo"
    root.mkdir()

    def git(*arguments: str) -> None:
        subprocess.run(
            ["git", *arguments],
            cwd=root,
            check=True,
            capture_output=True,
            env={"PATH": "/usr/bin:/bin", "HOME": str(tmp_path)},
        )

    git("init", "-q")
    git("config", "user.email", "probe@example.invalid")
    git("config", "user.name", "probe")
    (root / "notes.md").write_text("plain start\n", encoding="utf-8")
    git("add", "notes.md")
    git("commit", "-q", "-m", "base")
    return root


def test_sweep_flags_uncited_overclaims_and_spares_cited_ones(tmp_path: Path) -> None:
    root = _throwaway_repo(tmp_path)
    # The cited claim first: a citation may legitimately trail its claim by up
    # to two lines, so an uncited claim directly above a cited one would be
    # spared by its neighbour's citation — placement here mirrors the design
    # rather than fighting it.
    (root / "notes.md").write_text(
        "plain start\n"
        "the module is verified — per `pytest tests/unit -q`\n"
        "an unrelated middle line\n"
        "another unrelated middle line\n"
        "the gate is always enforced here\n",
        encoding="utf-8",
    )
    subprocess.run(
        ["git", "add", "notes.md"],
        cwd=root, check=True, capture_output=True,
        env={"PATH": "/usr/bin:/bin", "HOME": str(tmp_path)},
    )
    subprocess.run(
        ["git", "commit", "-q", "-m", "claims"],
        cwd=root, check=True, capture_output=True,
        env={"PATH": "/usr/bin:/bin", "HOME": str(tmp_path)},
    )

    findings = claim_check.sweep_range(root, "HEAD~1", "HEAD")

    assert len(findings) == 1, findings
    assert "always" in findings[0] or "enforced" in findings[0]
    assert "verified" not in findings[0]


def test_sweep_reports_a_broken_range_instead_of_a_clean_answer(tmp_path: Path) -> None:
    """An unanswerable diff is not a diff with no findings."""
    root = _throwaway_repo(tmp_path)

    with pytest.raises(RuntimeError):
        claim_check.sweep_range(root, "HEAD~9", "HEAD")


def test_lottery_samples_only_recorded_claims(tmp_path: Path) -> None:
    ledger = tmp_path / "ledger.jsonl"
    for text in ("claim one is measured", "claim two is enforced on every run"):
        claim_check.record_entry({"claim": text}, ledger)

    sampled = claim_check.lottery(ledger, 5)

    assert len(sampled) == 2
    assert set(sampled) == {"claim one is measured", "claim two is enforced on every run"}
