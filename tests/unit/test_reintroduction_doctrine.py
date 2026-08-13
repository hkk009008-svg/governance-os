"""One doctrine, every consumer: byte-identical restoration is not mutation.

The 2026-08-12 delete/revert cycle broke frozen-history consumers in two
waves: the committed-mailbox projection was repaired in-flight while the two
compact-pair frozen-history helpers stayed broken until a later audit,
because the rule lived in per-consumer copies. This module is the
cross-consumer contract. Every consumer of committed-path introduction
history appears twice — tolerating a byte-identical reintroduction and
refusing a reintroduction whose bytes differ (including one laundered by
restoring the worktree copy afterward). A new consumer of the
protocol_mailbox reintroduction primitives belongs in both tests.
"""

from collections.abc import Callable
from pathlib import Path
import subprocess

import pytest

import check_coordination
import compact_pair_loop as pair

VERBOSE_REPORT = (
    "coordination/mailbox/sent/"
    "2026-07-17T13-17-10Z-operator-to-director-verification-report.md"
)
MODEL_LABEL_REPORT = (
    "coordination/mailbox/sent/"
    "2026-08-01T05-02-15Z-operator-to-director2-verification-report.md"
)


def _git(root: Path, *args: str) -> None:
    subprocess.run(
        ["env", "-u", "GIT_INDEX_FILE", "git", *args],
        cwd=root,
        check=True,
        capture_output=True,
    )


@pytest.fixture()
def clone(tmp_path: Path, repo_root: Path) -> Path:
    clone = tmp_path / "clone"
    subprocess.run(
        ["git", "clone", "-q", "--no-hardlinks", str(repo_root), str(clone)],
        check=True,
    )
    _git(clone, "config", "user.name", "Doctrine Test")
    _git(clone, "config", "user.email", "doctrine@example.invalid")
    return clone


def _delete_and_reintroduce(
    clone: Path, path: str, mutate: Callable[[bytes], bytes] | None = None
) -> None:
    """Delete the committed event, reintroduce it, optionally with different
    bytes — and in the mutated case restore the worktree copy afterward, the
    laundering shape the doctrine must refuse."""

    raw = (clone / path).read_bytes()
    _git(clone, "rm", "-q", "--", path)
    _git(clone, "commit", "-q", "-m", "test: remove committed event")
    reintroduced = raw if mutate is None else mutate(raw)
    assert mutate is None or reintroduced != raw
    (clone / path).write_bytes(reintroduced)
    _git(clone, "add", "-f", "--", path)
    _git(clone, "commit", "-q", "-m", "test: reintroduce committed event")
    if mutate is not None:
        (clone / path).write_bytes(raw)


def test_byte_identical_reintroduction_is_not_mutation(clone: Path) -> None:
    _delete_and_reintroduce(clone, VERBOSE_REPORT)
    _delete_and_reintroduce(clone, MODEL_LABEL_REPORT)

    projection, problem = check_coordination.committed_mailbox_projection(clone)
    assert problem is None
    assert projection is not None

    verbose = pair.parse_verification_report(clone, VERBOSE_REPORT)
    assert verbose.finding_refs == ()

    labelled = pair.parse_verification_report(clone, MODEL_LABEL_REPORT)
    assert labelled.frozen_model_label_exception is True


def test_changed_reintroduction_is_refused_by_every_consumer(clone: Path) -> None:
    _delete_and_reintroduce(
        clone,
        VERBOSE_REPORT,
        mutate=lambda raw: raw.replace(b"VERDICT: GO", b"VERDICT: NITS"),
    )
    _delete_and_reintroduce(
        clone,
        MODEL_LABEL_REPORT,
        mutate=lambda raw: raw.replace(
            b"Reviewer model: antigravity", b"Reviewer model: forged"
        ),
    )

    projection, problem = check_coordination.committed_mailbox_projection(clone)
    assert projection is None
    assert "reintroduced with different bytes" in problem

    with pytest.raises(pair.CompactPairError, match="historical provenance"):
        pair.parse_verification_report(clone, VERBOSE_REPORT)

    labelled = pair.parse_verification_report(clone, MODEL_LABEL_REPORT)
    assert labelled.frozen_model_label_exception is False
    assert "reviewer model shares the author model family" in pair.validate_report(
        clone, labelled
    )
