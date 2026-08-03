from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path

import pytest

import check_coordination as cc
import protocol_mailbox


def _git(root: Path, *arguments: str) -> str:
    return subprocess.run(
        ["/usr/bin/git", "-C", str(root), *arguments],
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()


def _commit(root: Path, message: str) -> str:
    _git(root, "add", "-A")
    _git(
        root,
        "-c",
        "user.name=Learning History Test",
        "-c",
        "user.email=learning-history@example.invalid",
        "commit",
        "-q",
        "-m",
        message,
    )
    return _git(root, "rev-parse", "HEAD")


def _repo(tmp_path: Path, monkeypatch) -> tuple[Path, str]:
    root = tmp_path / "repo"
    sent = root / "coordination/mailbox/sent"
    seen = root / "coordination/mailbox/seen"
    baselines = root / "scripts/baselines"
    sent.mkdir(parents=True)
    seen.mkdir()
    baselines.mkdir(parents=True)
    (sent / ".gitkeep").write_text("", encoding="utf-8")
    for seat in cc.ROLES:
        (seen / f"{seat}.txt").write_text("0\n", encoding="utf-8")
    (root / "coordination/mailbox/kinds.txt").write_text(
        "decision\nlearning-candidate\nstatus\nverification-report\n"
        "verify-request\n",
        encoding="utf-8",
    )
    (baselines / "lane_v_reports_pre_v3.json").write_text(
        json.dumps(
            {"schema_version": "lane-v-report-pre-v3-baseline/v1", "reports": []}
        ),
        encoding="utf-8",
    )
    (baselines / "immutable_review_history_exceptions.json").write_text(
        json.dumps(
            {
                "schema_version": "immutable-review-history-exceptions/v1",
                "entries": [],
            }
        ),
        encoding="utf-8",
    )
    (root / "README.md").write_text("target v1\n", encoding="utf-8")
    _git(root, "init", "-q")
    _commit(root, "pre-cutover baseline")
    (root / "learning-cutover.txt").write_text("reviewed\n", encoding="utf-8")
    cutover = _commit(root, "reviewed learning-history cutover")
    monkeypatch.setattr(cc, "_LEARNING_HISTORY_CUTOVER_COMMIT", cutover)
    return root, cutover


def _event_text(sender: str, recipient: str, stamp: str, body: str) -> str:
    when = stamp[:11] + stamp[11:19].replace("-", ":") + "Z"
    return (
        f"# {sender} to {recipient}\n\n"
        f"**When:** {when} · **From:** {sender} (online)\n\n"
        f"{body}\n\nCursor at send: 0\n"
    )


def _write_event(
    root: Path,
    *,
    sender: str,
    recipient: str,
    kind: str,
    stamp: str,
    body: str,
) -> str:
    path = (
        "coordination/mailbox/sent/"
        f"{stamp}-{sender}-to-{recipient}-{kind}.md"
    )
    (root / path).write_text(
        _event_text(sender, recipient, stamp, body), encoding="utf-8"
    )
    return path


def _source_ref(root: Path, stamp: str = "2026-08-03T00-00-01Z") -> str:
    path = _write_event(
        root,
        sender="director",
        recipient="operator",
        kind="status",
        stamp=stamp,
        body="Source evidence.",
    )
    commit = _commit(root, "source evidence")
    return f"{path}@{commit}"


def _candidate_fields(
    source_ref: str, **overrides: str | None
) -> dict[str, str | None]:
    fields: dict[str, str | None] = {
        "Category": "procedure",
        "Scope": "repository",
        "Statement": "Replay committed learning events.",
        "Proposed content hash": None,
        "Target": None,
        "Target base hash": None,
        "Source refs": source_ref,
        "Evidence provenance": "MEASURED",
        "Applicability": "committed mailbox history",
        "Exclusions": "pre-cutover introductions",
        "Risk class": "material-behavior",
        "Supersedes": None,
        "Producer seat": "operator",
        "Producer model": "fixture-model",
    }
    fields.update(overrides)
    return fields


def _candidate_body(
    fields: dict[str, str | None], *, candidate_id: str | None = None
) -> str:
    identity = candidate_id or protocol_mailbox.compute_learning_candidate_id(fields)
    return "\n".join(
        [f"Candidate ID: {identity}"]
        + [f"{label}: {value}" for label, value in fields.items() if value is not None]
    )


def _candidate(
    root: Path,
    source_ref: str,
    *,
    stamp: str = "2026-08-03T00-00-02Z",
    candidate_id: str | None = None,
    **overrides: str | None,
) -> tuple[str, dict[str, str | None]]:
    fields = _candidate_fields(source_ref, **overrides)
    path = _write_event(
        root,
        sender="operator",
        recipient="director",
        kind="learning-candidate",
        stamp=stamp,
        body=_candidate_body(fields, candidate_id=candidate_id),
    )
    return path, fields


def _candidate_ref(root: Path, source_ref: str, **overrides: str | None) -> str:
    path, _fields = _candidate(root, source_ref, **overrides)
    commit = _commit(root, "learning candidate")
    return f"{path}@{commit}"


def _disposition(
    root: Path,
    candidate_ref: str,
    *,
    sender: str = "director",
    disposition: str = "accepted",
    stamp: str = "2026-08-03T00-00-03Z",
) -> str:
    return _write_event(
        root,
        sender=sender,
        recipient="all",
        kind="decision",
        stamp=stamp,
        body=f"Candidate: {candidate_ref}\nDisposition: {disposition}",
    )


def _history_issues(root: Path) -> list[cc.CoordIssue]:
    projection, problem = cc._committed_mailbox_projection(root)
    assert problem is None
    assert projection is not None
    return cc._check_committed_learning_history(root, projection)


def _fatal_messages(root: Path) -> list[str]:
    return [issue.message for issue in _history_issues(root) if issue.severity == "FATAL"]


def test_direct_committed_malformed_candidate_is_fatal(
    tmp_path: Path, monkeypatch
) -> None:
    root, _cutover = _repo(tmp_path, monkeypatch)
    source = _source_ref(root)
    _candidate(root, source, candidate_id="f" * 64)
    _commit(root, "direct malformed candidate bypass")

    assert any("normalized payload" in message for message in _fatal_messages(root))


@pytest.mark.parametrize("broken", ["source", "supersedes"])
def test_unresolvable_candidate_refs_are_fatal(
    tmp_path: Path, monkeypatch, broken: str
) -> None:
    root, _cutover = _repo(tmp_path, monkeypatch)
    real_source = _source_ref(root)
    phantom_kind = "status" if broken == "source" else "learning-candidate"
    phantom = (
        "coordination/mailbox/sent/"
        f"2026-08-02T00-00-00Z-director-to-operator-{phantom_kind}.md@"
        + "e" * 40
    )
    overrides = {"Source refs": phantom} if broken == "source" else {"Supersedes": phantom}
    _candidate(root, real_source, **overrides)
    _commit(root, f"direct bad {broken} bypass")

    expected = "source ref does not resolve" if broken == "source" else "Supersedes ref does not resolve"
    assert any(expected in message for message in _fatal_messages(root))


def test_duplicate_candidate_ids_in_one_commit_are_fatal(
    tmp_path: Path, monkeypatch
) -> None:
    root, _cutover = _repo(tmp_path, monkeypatch)
    source = _source_ref(root)
    _candidate(root, source, stamp="2026-08-03T00-00-02Z")
    _candidate(root, source, stamp="2026-08-03T00-00-03Z")
    _commit(root, "same-commit duplicate bypass")

    assert any("duplicate Candidate ID" in message for message in _fatal_messages(root))


@pytest.mark.parametrize(
    ("candidate_overrides", "sender", "expected"),
    [
        ({}, "operator", "self-approval"),
        ({"Evidence provenance": "ASSUMED"}, "director", "ASSUMED"),
        (
            {"Category": "governance-rule", "Risk class": "material-behavior"},
            "director",
            "high-risk-control floor",
        ),
    ],
)
def test_direct_committed_invalid_dispositions_are_fatal(
    tmp_path: Path,
    monkeypatch,
    candidate_overrides: dict[str, str],
    sender: str,
    expected: str,
) -> None:
    root, _cutover = _repo(tmp_path, monkeypatch)
    ref = _candidate_ref(root, _source_ref(root), **candidate_overrides)
    _disposition(root, ref, sender=sender)
    _commit(root, "direct invalid disposition bypass")

    assert any(expected in message for message in _fatal_messages(root))


def test_disposition_candidate_must_resolve(tmp_path: Path, monkeypatch) -> None:
    root, _cutover = _repo(tmp_path, monkeypatch)
    phantom = (
        "coordination/mailbox/sent/"
        "2026-08-02T00-00-00Z-operator-to-director-learning-candidate.md@"
        + "e" * 40
    )
    _disposition(root, phantom)
    _commit(root, "direct phantom disposition bypass")

    assert any("Candidate does not resolve" in message for message in _fatal_messages(root))


def test_target_cas_uses_disposition_introduction_commit_bytes(
    tmp_path: Path, monkeypatch
) -> None:
    root, _cutover = _repo(tmp_path, monkeypatch)
    base_hash = "sha256:" + hashlib.sha256((root / "README.md").read_bytes()).hexdigest()
    ref = _candidate_ref(
        root,
        _source_ref(root),
        Target="README.md",
        **{"Target base hash": base_hash},
    )
    (root / "README.md").write_text("target v2 in disposition commit\n", encoding="utf-8")
    _disposition(root, ref)
    _commit(root, "same-commit target mutation and disposition bypass")

    assert any("target base hash is stale" in message for message in _fatal_messages(root))


@pytest.mark.parametrize("change", ["modified", "deleted"])
def test_post_cutover_learning_event_is_immutable(
    tmp_path: Path, monkeypatch, change: str
) -> None:
    root, _cutover = _repo(tmp_path, monkeypatch)
    path, _fields = _candidate(root, _source_ref(root))
    _commit(root, "valid candidate introduction")
    if change == "modified":
        (root / path).write_text("changed after introduction\n", encoding="utf-8")
    else:
        (root / path).unlink()
    _commit(root, f"{change} immutable candidate")

    assert any(change in message for message in _fatal_messages(root))


@pytest.mark.parametrize("change", ["modified", "deleted"])
def test_cutover_baseline_candidate_bytes_are_immutable(
    tmp_path: Path, monkeypatch, change: str
) -> None:
    root, _initial_cutover = _repo(tmp_path, monkeypatch)
    path, _fields = _candidate(root, _source_ref(root))
    _commit(root, "legacy candidate introduction")
    (root / "learning-cutover.txt").write_text("reviewed v2\n", encoding="utf-8")
    cutover = _commit(root, "reviewed cutover after candidate introduction")
    monkeypatch.setattr(cc, "_LEARNING_HISTORY_CUTOVER_COMMIT", cutover)
    if change == "modified":
        (root / path).write_text("changed after cutover\n", encoding="utf-8")
    else:
        (root / path).unlink()
    _commit(root, f"{change} cutover candidate")

    assert any(change in message for message in _fatal_messages(root))


def test_unchanged_malformed_cutover_bytes_are_semantically_grandfathered(
    tmp_path: Path, monkeypatch
) -> None:
    root, _initial_cutover = _repo(tmp_path, monkeypatch)
    path, fields = _candidate(root, _source_ref(root))
    _commit(root, "legacy valid candidate introduction")
    valid_id = protocol_mailbox.compute_learning_candidate_id(fields)
    malformed = (root / path).read_text(encoding="utf-8").replace(
        valid_id, "f" * 64, 1
    )
    (root / path).write_text(malformed, encoding="utf-8")
    cutover = _commit(root, "reviewed cutover with malformed legacy bytes")
    monkeypatch.setattr(cc, "_LEARNING_HISTORY_CUTOVER_COMMIT", cutover)
    (root / "after.txt").write_text("after cutover\n", encoding="utf-8")
    _commit(root, "post-cutover unrelated change")

    assert _fatal_messages(root) == []


def test_candidate_introduced_and_deleted_before_cutover_is_grandfathered(
    tmp_path: Path, monkeypatch
) -> None:
    root, _initial_cutover = _repo(tmp_path, monkeypatch)
    path, _fields = _candidate(
        root, _source_ref(root), candidate_id="f" * 64
    )
    _commit(root, "legacy malformed candidate introduction")
    (root / path).unlink()
    cutover = _commit(root, "reviewed cutover after legacy candidate deletion")
    monkeypatch.setattr(cc, "_LEARNING_HISTORY_CUTOVER_COMMIT", cutover)

    assert _fatal_messages(root) == []


@pytest.mark.parametrize("change", ["modified", "deleted"])
def test_cutover_baseline_disposition_bytes_are_immutable(
    tmp_path: Path, monkeypatch, change: str
) -> None:
    root, _initial_cutover = _repo(tmp_path, monkeypatch)
    ref = _candidate_ref(root, _source_ref(root))
    path = _disposition(root, ref)
    _commit(root, "legacy disposition introduction")
    (root / "learning-cutover.txt").write_text("reviewed v2\n", encoding="utf-8")
    cutover = _commit(root, "reviewed cutover after disposition introduction")
    monkeypatch.setattr(cc, "_LEARNING_HISTORY_CUTOVER_COMMIT", cutover)
    if change == "modified":
        (root / path).write_text("changed after cutover\n", encoding="utf-8")
    else:
        (root / path).unlink()
    _commit(root, f"{change} cutover disposition")

    assert any(change in message for message in _fatal_messages(root))


def test_old_base_parallel_branch_introduction_is_not_grandfathered(
    tmp_path: Path, monkeypatch
) -> None:
    root = tmp_path / "repo"
    root.mkdir()
    _git(root, "init", "-q")
    (root / "seed.txt").write_text("seed\n", encoding="utf-8")
    base = _commit(root, "base")

    _git(root, "checkout", "-q", "-b", "parallel", base)
    (root / "coordination/mailbox/sent").mkdir(parents=True)
    parallel_path = _write_event(
        root,
        sender="operator",
        recipient="director",
        kind="learning-candidate",
        stamp="2026-08-03T00-00-01Z",
        body="malformed parallel candidate",
    )
    parallel = _commit(root, "parallel malformed introduction")

    _git(root, "checkout", "-q", "main")
    sent = root / "coordination/mailbox/sent"
    seen = root / "coordination/mailbox/seen"
    baselines = root / "scripts/baselines"
    sent.mkdir(parents=True)
    seen.mkdir()
    baselines.mkdir(parents=True)
    for seat in cc.ROLES:
        (seen / f"{seat}.txt").write_text("0\n", encoding="utf-8")
    (root / "coordination/mailbox/kinds.txt").write_text(
        "decision\nlearning-candidate\nstatus\nverification-report\nverify-request\n",
        encoding="utf-8",
    )
    (baselines / "lane_v_reports_pre_v3.json").write_text(
        json.dumps({"schema_version": "lane-v-report-pre-v3-baseline/v1", "reports": []}),
        encoding="utf-8",
    )
    (baselines / "immutable_review_history_exceptions.json").write_text(
        json.dumps({"schema_version": "immutable-review-history-exceptions/v1", "entries": []}),
        encoding="utf-8",
    )
    cutover = _commit(root, "reviewed cutover")
    monkeypatch.setattr(cc, "_LEARNING_HISTORY_CUTOVER_COMMIT", cutover)
    _git(root, "merge", "-q", "--no-ff", parallel, "-m", "merge parallel history")
    assert (root / parallel_path).exists()

    assert any("invalid" in message for message in _fatal_messages(root))

    _write_event(
        root,
        sender="operator",
        recipient="director",
        kind="learning-candidate",
        stamp="2026-08-03T00-00-02Z",
        body="malformed descendant candidate",
    )
    _commit(root, "descendant malformed introduction")

    assert len([message for message in _fatal_messages(root) if "invalid" in message]) == 2


def test_old_base_branch_add_delete_merged_after_cutover_is_fatal(
    tmp_path: Path, monkeypatch
) -> None:
    root, cutover = _repo(tmp_path, monkeypatch)
    base = _git(root, "rev-parse", f"{cutover}^")
    _git(root, "checkout", "-q", "-b", "extinct-parallel", base)
    (root / "coordination/mailbox/sent").mkdir(parents=True, exist_ok=True)
    path = _write_event(
        root,
        sender="operator",
        recipient="director",
        kind="learning-candidate",
        stamp="2026-08-03T00-00-09Z",
        body="malformed extinct parallel candidate",
    )
    _commit(root, "parallel candidate introduction")
    (root / path).unlink()
    parallel_tip = _commit(root, "parallel candidate deletion")
    _git(root, "checkout", "-q", "main")
    _git(
        root,
        "merge",
        "-q",
        "--no-ff",
        parallel_tip,
        "-m",
        "merge extinct parallel history",
    )

    assert any("deleted" in message for message in _fatal_messages(root))


def test_prose_decision_is_not_machine_disposition(tmp_path: Path, monkeypatch) -> None:
    root, _cutover = _repo(tmp_path, monkeypatch)
    _write_event(
        root,
        sender="director",
        recipient="all",
        kind="decision",
        stamp="2026-08-03T00-00-03Z",
        body="Candidate: Jane Doe\nDisposition: hired",
    )
    _commit(root, "ordinary prose decision")

    assert _fatal_messages(root) == []


def test_post_cutover_non_utf8_decision_fails_closed(
    tmp_path: Path, monkeypatch
) -> None:
    root, _cutover = _repo(tmp_path, monkeypatch)
    ref = _candidate_ref(root, _source_ref(root))
    path = _disposition(root, ref)
    (root / path).write_bytes((root / path).read_bytes() + b"\xff\n")
    _commit(root, "direct non-UTF-8 disposition bypass")

    issues = cc.run(
        root / "coordination", git_root=root, docs_root=root / "docs"
    )
    assert any(
        issue.severity == "FATAL" and "not UTF-8" in issue.message
        for issue in issues
    )


def test_run_wires_committed_learning_history_gate(tmp_path: Path, monkeypatch) -> None:
    root, _cutover = _repo(tmp_path, monkeypatch)
    _candidate(root, _source_ref(root), candidate_id="f" * 64)
    _commit(root, "direct malformed candidate bypass")

    issues = cc.run(
        root / "coordination",
        git_root=root,
        docs_root=root / "docs",
    )

    assert any(
        issue.kind == "invalid_committed_learning_history"
        and issue.severity == "FATAL"
        for issue in issues
    )
