from __future__ import annotations

import hashlib
import json
import os
import subprocess
from pathlib import Path

import pytest

import check_coordination as cc
import mailbox_writer
import protocol_mailbox


def _git(root: Path, *arguments: str) -> str:
    home = root.parent / "git-home"
    home.mkdir(exist_ok=True)
    env = {
        "PATH": "/usr/bin:/bin",
        "HOME": str(home),
        "LANG": "C",
        "LC_ALL": "C",
        "GIT_CONFIG_NOSYSTEM": "1",
        "GIT_CONFIG_COUNT": "3",
        "GIT_CONFIG_KEY_0": "init.defaultBranch",
        "GIT_CONFIG_VALUE_0": "main",
        "GIT_CONFIG_KEY_1": "user.name",
        "GIT_CONFIG_VALUE_1": "Learning History Test",
        "GIT_CONFIG_KEY_2": "user.email",
        "GIT_CONFIG_VALUE_2": "learning-history@example.invalid",
        "GIT_TERMINAL_PROMPT": "0",
    }
    ceiling = os.environ.get("GIT_CEILING_DIRECTORIES")
    if ceiling:
        env["GIT_CEILING_DIRECTORIES"] = ceiling
    return subprocess.run(
        ["/usr/bin/git", "-C", str(root), *arguments],
        check=True,
        capture_output=True,
        text=True,
        env=env,
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
    baselines = root / "pipeline/baselines"
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
    _git(root, "init", "-q", "-b", "main")
    _commit(root, "pre-cutover baseline")
    (root / "learning-cutover.txt").write_text("reviewed\n", encoding="utf-8")
    cutover = _commit(root, "reviewed learning-history cutover")
    monkeypatch.setattr(cc, "_LEARNING_HISTORY_CUTOVER_COMMIT", cutover)
    return root, cutover


def _event_text(sender: str, recipient: str, stamp: str, body: str) -> str:
    when = stamp[:11] + stamp[11:19].replace("-", ":") + "Z"
    return (
        f"# {sender.capitalize()} → {recipient.capitalize()}: Fixture\n\n"
        f"**When:** {when} · **From:** {sender} (online)\n\n"
        f"{body}\n\nCursor at send: cursorless\n"
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
        sender="author",
        recipient="reviewer",
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
        "Producer seat": "reviewer",
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
        sender="reviewer",
        recipient="author",
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
    sender: str = "author",
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
        f"2026-08-02T00-00-00Z-author-to-reviewer-{phantom_kind}.md@"
        + "e" * 40
    )
    overrides = {"Source refs": phantom} if broken == "source" else {"Supersedes": phantom}
    _candidate(root, real_source, **overrides)
    _commit(root, f"direct bad {broken} bypass")

    expected = "source ref does not resolve" if broken == "source" else "Supersedes ref does not resolve"
    assert any(expected in message for message in _fatal_messages(root))


def test_candidate_source_ref_rejects_historical_symlink(
    tmp_path: Path, monkeypatch
) -> None:
    root, _cutover = _repo(tmp_path, monkeypatch)
    path = (
        "coordination/mailbox/sent/"
        "2026-08-03T00-00-01Z-author-to-reviewer-status.md"
    )
    (root / path).symlink_to("../kinds.txt")
    source_commit = _commit(root, "historical symlink-shaped event")
    (root / path).unlink()
    _commit(root, "remove historical symlink-shaped event")
    _candidate(root, f"{path}@{source_commit}")
    _commit(root, "candidate cites historical symlink")

    assert any("source ref does not resolve" in message for message in _fatal_messages(root))


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
        ({}, "reviewer", "self-approval"),
        ({"Evidence provenance": "ASSUMED"}, "author", "ASSUMED"),
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
        "2026-08-02T00-00-00Z-reviewer-to-author-learning-candidate.md@"
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


def test_extinct_pre_cutover_candidate_id_can_be_reissued(
    tmp_path: Path, monkeypatch
) -> None:
    root, _initial_cutover = _repo(tmp_path, monkeypatch)
    source = _source_ref(root)
    old_path, fields = _candidate(root, source)
    _commit(root, "legacy candidate introduction")
    (root / old_path).unlink()
    cutover = _commit(root, "reviewed cutover after legacy candidate deletion")
    monkeypatch.setattr(cc, "_LEARNING_HISTORY_CUTOVER_COMMIT", cutover)

    new_path = _write_event(
        root,
        sender="reviewer",
        recipient="author",
        kind="learning-candidate",
        stamp="2026-08-03T00-00-04Z",
        body=_candidate_body(fields),
    )
    mailbox_writer.validate_event_candidate_bytes(
        root, (root / new_path).read_bytes(), new_path
    )
    _commit(root, "reissue extinct candidate ID")

    assert _fatal_messages(root) == []


def test_cutover_present_candidate_id_still_blocks_reissue(
    tmp_path: Path, monkeypatch
) -> None:
    root, _initial_cutover = _repo(tmp_path, monkeypatch)
    source = _source_ref(root)
    _old_path, fields = _candidate(root, source)
    _commit(root, "legacy candidate introduction")
    (root / "learning-cutover.txt").write_text("reviewed v2\n", encoding="utf-8")
    cutover = _commit(root, "reviewed cutover with live candidate")
    monkeypatch.setattr(cc, "_LEARNING_HISTORY_CUTOVER_COMMIT", cutover)

    new_path = _write_event(
        root,
        sender="reviewer",
        recipient="author",
        kind="learning-candidate",
        stamp="2026-08-03T00-00-04Z",
        body=_candidate_body(fields),
    )
    with pytest.raises(mailbox_writer.MailboxWriterError, match="duplicates"):
        mailbox_writer.validate_event_candidate_bytes(
            root, (root / new_path).read_bytes(), new_path
        )
    _commit(root, "bypass writer with duplicate cutover candidate ID")

    assert any("duplicate Candidate ID" in message for message in _fatal_messages(root))


def test_cutover_modified_candidate_bytes_still_block_duplicate_reissue(
    tmp_path: Path, monkeypatch
) -> None:
    root, _initial_cutover = _repo(tmp_path, monkeypatch)
    source = _source_ref(root)
    old_path, _old_fields = _candidate(root, source)
    _commit(root, "candidate A introduction")
    fields_b = _candidate_fields(source, Statement="Candidate B at cutover.")
    (root / old_path).write_text(
        _event_text(
            "reviewer",
            "author",
            "2026-08-03T00-00-02Z",
            _candidate_body(fields_b),
        ),
        encoding="utf-8",
    )
    cutover = _commit(root, "reviewed cutover with candidate B bytes")
    monkeypatch.setattr(cc, "_LEARNING_HISTORY_CUTOVER_COMMIT", cutover)

    new_path = _write_event(
        root,
        sender="reviewer",
        recipient="author",
        kind="learning-candidate",
        stamp="2026-08-03T00-00-04Z",
        body=_candidate_body(fields_b),
    )
    with pytest.raises(mailbox_writer.MailboxWriterError, match="duplicates"):
        mailbox_writer.validate_event_candidate_bytes(
            root, (root / new_path).read_bytes(), new_path
        )
    _commit(root, "bypass writer with duplicate candidate B ID")

    assert any("duplicate Candidate ID" in message for message in _fatal_messages(root))


@pytest.mark.parametrize(
    "target",
    (
        "",
        ".",
        "./README.md",
        "dir/./README.md",
        "dir/../README.md",
        "dir//README.md",
        "README.md/",
        "/README.md",
        "~user/README.md",
        "dir\\README.md",
        "README.md\x00suffix",
        "README.md\tsuffix",
        "README.md\x1fsuffix",
        "README.md\x7fsuffix",
    ),
)
def test_noncanonical_target_is_rejected_by_parser_writer_and_replay(
    tmp_path: Path, monkeypatch, target: str
) -> None:
    root, _cutover = _repo(tmp_path, monkeypatch)
    source = _source_ref(root)
    base_hash = "sha256:" + hashlib.sha256(
        (root / "README.md").read_bytes()
    ).hexdigest()
    path, _fields = _candidate(
        root,
        source,
        Target=target,
        **{"Target base hash": base_hash},
    )
    raw = (root / path).read_bytes()
    event = protocol_mailbox.parse_committed_event_text(
        f"{path}@{'0' * 40}", raw.decode("utf-8")
    )

    with pytest.raises(ValueError, match="Target"):
        protocol_mailbox.parse_learning_candidate_statement(event)
    with pytest.raises(
        mailbox_writer.MailboxWriterError, match="Target|bounded text"
    ):
        mailbox_writer.validate_event_candidate_bytes(root, raw, path)
    _commit(root, "bypass writer with noncanonical target")

    assert any("Target" in message for message in _fatal_messages(root))


def test_printable_unicode_target_remains_supported_with_cas(
    tmp_path: Path, monkeypatch
) -> None:
    root, _cutover = _repo(tmp_path, monkeypatch)
    target = root / "docs/한글.md"
    target.parent.mkdir()
    target.write_text("printable unicode target\n", encoding="utf-8")
    _commit(root, "add printable unicode target")
    source = _source_ref(root)
    base_hash = "sha256:" + hashlib.sha256(target.read_bytes()).hexdigest()
    path, _fields = _candidate(
        root,
        source,
        Target="docs/한글.md",
        **{"Target base hash": base_hash},
    )
    raw = (root / path).read_bytes()
    mailbox_writer.validate_event_candidate_bytes(root, raw, path)
    candidate_commit = _commit(root, "unicode-target candidate")
    _disposition(root, f"{path}@{candidate_commit}")
    _commit(root, "accept unicode-target candidate")

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
    _git(root, "init", "-q", "-b", "main")
    (root / "seed.txt").write_text("seed\n", encoding="utf-8")
    base = _commit(root, "base")

    _git(root, "checkout", "-q", "-b", "parallel", base)
    (root / "coordination/mailbox/sent").mkdir(parents=True)
    parallel_path = _write_event(
        root,
        sender="reviewer",
        recipient="author",
        kind="learning-candidate",
        stamp="2026-08-03T00-00-01Z",
        body="malformed parallel candidate",
    )
    parallel = _commit(root, "parallel malformed introduction")

    _git(root, "checkout", "-q", "main")
    sent = root / "coordination/mailbox/sent"
    seen = root / "coordination/mailbox/seen"
    baselines = root / "pipeline/baselines"
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
        sender="reviewer",
        recipient="author",
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
        sender="reviewer",
        recipient="author",
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


def test_wired_learning_replay_git_processes_are_candidate_count_bounded(
    tmp_path: Path, monkeypatch
) -> None:
    process_counts: list[int] = []
    for candidate_count in (0, 5, 20):
        root, _cutover = _repo(tmp_path / f"candidates-{candidate_count}", monkeypatch)
        source = _source_ref(root)
        base_hash = "sha256:" + hashlib.sha256(
            (root / "README.md").read_bytes()
        ).hexdigest()
        candidate_refs: list[str] = []
        for index in range(candidate_count):
            path, _fields = _candidate(
                root,
                source,
                stamp=f"2026-08-03T01-{index:02d}-00Z",
                Statement=f"Bounded replay candidate {index}.",
                Target="README.md",
                **{"Target base hash": base_hash},
            )
            candidate_refs.append(
                f"{path}@{_commit(root, f'candidate {index}')}"
            )
        for index, candidate_ref in enumerate(candidate_refs):
            _disposition(
                root,
                candidate_ref,
                stamp=f"2026-08-03T02-{index:02d}-00Z",
            )
        if candidate_refs:
            _commit(root, "disposition batch")

        real_popen = subprocess.Popen
        calls: list[tuple[object, ...]] = []

        def counted_popen(*args, **kwargs):
            calls.append(args)
            return real_popen(*args, **kwargs)

        with monkeypatch.context() as scoped:
            scoped.setattr(subprocess, "Popen", counted_popen)
            projection_result = cc.committed_mailbox_projection(root)
            review_state = cc.inspect_verify_review_state(
                root, projection_result=projection_result
            )
            issues = cc.run(
                root / "coordination",
                now="2026-08-03T03:00:00Z",
                docs_root=root / "docs",
                review_state=review_state,
                committed_projection=projection_result,
            )
        assert not [
            issue
            for issue in issues
            if issue.kind == "invalid_committed_learning_history"
        ]
        process_counts.append(len(calls))

    assert process_counts[0] == process_counts[1] == process_counts[2]
    # This is the complete status-style projection/review/replay seam, not
    # only the learning helper. Commit identity is checked at both projection
    # and final run boundaries, so its fixed envelope is eighteen processes.
    assert process_counts[0] <= 20


def test_prose_decision_is_not_machine_disposition(tmp_path: Path, monkeypatch) -> None:
    root, _cutover = _repo(tmp_path, monkeypatch)
    _write_event(
        root,
        sender="author",
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
