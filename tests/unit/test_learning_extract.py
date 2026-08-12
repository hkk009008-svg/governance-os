"""Stage 4 gate tests: evidence-triggered drafts only, nothing else (ADR-067).

The three plan-named gates — writes-nothing-outside-scratch,
output-parses-as-candidate, no-trigger-no-candidate — run against throwaway
repositories, never the checkout under review.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parent.parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

import learning_extract  # noqa: E402
import learning_index  # noqa: E402
import protocol_mailbox  # noqa: E402


_EVIDENCE_REF = (
    "coordination/mailbox/sent/"
    "2026-07-30T01-02-03Z-director2-to-operator-verify-request.md@" + "c" * 40
)


def _throwaway_repo(tmp_path: Path) -> Path:
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
    # Mirror the real repo's partition: the index dir is a gitignored
    # workspace-scope projection (ADR-067), here as in production.
    (root / ".gitignore").write_text("coordination/learning/\n", encoding="utf-8")
    sent = root / "coordination" / "mailbox" / "sent"
    sent.mkdir(parents=True)
    (sent / "2026-07-28T01-02-03Z-director-to-operator-status.md").write_text(
        "# Director → Operator: s\n\n"
        "**When:** 2026-07-28T01:02:03Z · **From:** director (online)\n\n"
        "the flaky gate reproduced again\n\nCursor at send: 0\n",
        encoding="utf-8",
    )
    (root / "docs").mkdir()
    (root / "docs" / "HANDOFF-operator-2026-07-29-x.md").write_text(
        "# Handoff\n\nthe flaky gate reproduced under load\n", encoding="utf-8"
    )
    git("add", "-A")
    git("commit", "-q", "-m", "seed")
    return root


def _draft_kwargs(root: Path, scratch: Path, **overrides: object) -> dict:
    kwargs: dict = dict(
        root=root,
        scratch=scratch,
        trigger="user-correction",
        evidence_refs=[_EVIDENCE_REF],
        statement="Run the doctrine diff before every range submit.",
        category="procedure",
        scope="repository",
        provenance="RELAYED",
        applicability="any compact-pair range",
        exclusions="scratch worktrees",
        risk_class="material-behavior",
        producer_seat="director2",
        producer_model="claude-fable-5",
    )
    kwargs.update(overrides)
    return kwargs


def test_no_trigger_no_candidate(tmp_path: Path) -> None:
    """Anti-sediment: no qualifying evidence -> no draft, ever."""

    root = _throwaway_repo(tmp_path)
    scratch = tmp_path / "scratch"
    # Recurrence without a built index: unavailable is not evidence.
    try:
        learning_extract.draft_candidate(
            **_draft_kwargs(
                root, scratch, trigger="recurrence", recurrence_terms="flaky"
            )
        )
        raise AssertionError("unavailable index must not draft")
    except learning_extract.ExtractionRefused as refusal:
        assert "unavailable" in str(refusal)
    # Recurrence with one source only: not recurrence.
    db = root / "coordination" / "learning" / "index.sqlite"
    learning_index.build_index(root, db_path=db)
    try:
        learning_extract.draft_candidate(
            **_draft_kwargs(
                root, scratch, trigger="recurrence",
                recurrence_terms="under AND load",
            )
        )
        raise AssertionError("a single source is not recurrence")
    except learning_extract.ExtractionRefused as refusal:
        assert ">=2 distinct" in str(refusal)
    # No evidence refs at all: refused regardless of trigger.
    try:
        learning_extract.draft_candidate(
            **_draft_kwargs(root, scratch, evidence_refs=[])
        )
        raise AssertionError("no evidence refs must not draft")
    except learning_extract.ExtractionRefused:
        pass
    assert not scratch.exists() or not list(scratch.iterdir())


def test_recurrence_with_two_sources_drafts(tmp_path: Path) -> None:
    root = _throwaway_repo(tmp_path)
    learning_index.build_index(root)
    scratch = tmp_path / "scratch"
    draft_path, _body, sources = learning_extract.draft_candidate(
        **_draft_kwargs(
            root, scratch, trigger="recurrence", recurrence_terms="flaky"
        )
    )
    assert draft_path.exists()
    assert len(sources) >= 2


def test_extractor_output_parses_as_candidate(tmp_path: Path) -> None:
    root = _throwaway_repo(tmp_path)
    scratch = tmp_path / "scratch"
    _draft_path, body, _sources = learning_extract.draft_candidate(
        **_draft_kwargs(root, scratch)
    )
    path = (
        "coordination/mailbox/sent/"
        "2026-07-30T02-03-04Z-director2-to-operator-learning-candidate.md"
    )
    text = (
        "# Director2 → Operator: candidate\n\n"
        "**When:** 2026-07-30T02:03:04Z · **From:** director2 (online)\n\n"
        f"{body}\n"
        "Cursor at send: 0\n"
    )
    event = protocol_mailbox.parse_committed_event_text(f"{path}@{'d' * 40}", text)
    statement = protocol_mailbox.parse_learning_candidate_statement(event)
    assert statement.source_refs == (_EVIDENCE_REF,)
    assert statement.producer_seat == "director2"


def test_extractor_writes_nothing_outside_scratch(tmp_path: Path) -> None:
    root = _throwaway_repo(tmp_path)
    learning_index.build_index(root)  # workspace projection, pre-existing
    scratch = tmp_path / "scratch"
    before = {p for p in tmp_path.rglob("*") if p.is_file()}
    learning_extract.draft_candidate(
        **_draft_kwargs(
            root, scratch, trigger="recurrence", recurrence_terms="flaky"
        )
    )
    after = {p for p in tmp_path.rglob("*") if p.is_file()}
    created = after - before
    assert created, "the draft must exist"
    outside = {p for p in created if scratch not in p.parents}
    assert outside == set(), f"wrote outside scratch: {outside}"
    status = subprocess.run(
        ["git", "status", "--porcelain"],
        cwd=root,
        check=True,
        capture_output=True,
        env={"PATH": "/usr/bin:/bin", "HOME": str(tmp_path)},
    ).stdout.decode()
    assert status == "", f"extractor dirtied the repo: {status}"


def test_measured_claim_shape_without_instrument_mark_is_refused(
    tmp_path: Path,
) -> None:
    """Laundering defense: MEASURED + claim shape needs an instrument mark."""

    root = _throwaway_repo(tmp_path)
    scratch = tmp_path / "scratch"
    try:
        learning_extract.draft_candidate(
            **_draft_kwargs(
                root, scratch,
                statement="The pathspec guard is enforced in every checkout.",
                provenance="MEASURED",
            )
        )
        raise AssertionError("uncited MEASURED claim shape must refuse")
    except learning_extract.ExtractionRefused as refusal:
        assert "instrument mark" in str(refusal)
    # The same statement WITH a citation drafts.
    draft_path, _body, _sources = learning_extract.draft_candidate(
        **_draft_kwargs(
            root, scratch,
            statement="The pathspec guard is enforced in every checkout.",
            provenance="MEASURED",
            applicability="verified via `pytest tests/unit -q` on the range",
        )
    )
    assert draft_path.exists()


def test_cli_main_covers_both_exit_paths(tmp_path: Path) -> None:
    """The argparse wiring and exit codes are executed, not assumed."""

    root = _throwaway_repo(tmp_path)
    scratch = tmp_path / "scratch"
    common = [
        "--repo-root", str(root),
        "--scratch", str(scratch),
        "--trigger", "user-correction",
        "--statement", "Run the doctrine diff before every range submit.",
        "--category", "procedure",
        "--provenance", "RELAYED",
        "--applicability", "any compact-pair range",
        "--exclusions", "scratch worktrees",
        "--risk-class", "material-behavior",
        "--producer-seat", "director2",
        "--producer-model", "claude-fable-5",
    ]
    # Missing evidence ref: EXIT_NO_TRIGGER, and no scratch dir appears.
    assert learning_extract.main(common) == learning_extract.EXIT_NO_TRIGGER
    assert not scratch.exists()
    # With evidence: EXIT_DRAFTED and exactly one draft file.
    assert (
        learning_extract.main(common + ["--evidence-ref", _EVIDENCE_REF])
        == learning_extract.EXIT_DRAFTED
    )
    drafts = list(scratch.iterdir())
    assert len(drafts) == 1 and drafts[0].name.startswith("learning-candidate-")
