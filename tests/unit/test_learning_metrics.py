"""Stage 5 gate tests for the read-only metrics reporter (ADR-067)."""

from __future__ import annotations

import hashlib
import subprocess
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parent.parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

import learning_metrics  # noqa: E402
import protocol_mailbox  # noqa: E402

_SOURCE_REF = (
    "coordination/mailbox/sent/"
    "2026-07-28T01-02-03Z-director-to-operator-status.md@"
)


def _event_text(sender: str, recipient: str, stamp: str, body: str) -> str:
    colon = stamp[:11] + stamp[11:19].replace("-", ":") + "Z"
    return (
        f"# {sender.capitalize()} → {recipient.capitalize()}: probe\n\n"
        f"**When:** {colon} · **From:** {sender} (online)\n\n"
        f"{body}\n\n"
        "Cursor at send: 0\n"
    )


def _candidate_fields(source_ref: str, **overrides: str | None) -> dict[str, str | None]:
    fields: dict[str, str | None] = {
        "Category": "procedure",
        "Scope": "repository",
        "Statement": "Run the doctrine diff before every range submit.",
        "Proposed content hash": None,
        "Target": None,
        "Target base hash": None,
        "Source refs": source_ref,
        "Evidence provenance": "MEASURED",
        "Applicability": "any compact-pair range",
        "Exclusions": "scratch worktrees",
        "Risk class": "material-behavior",
        "Supersedes": None,
        "Producer seat": "operator",
        "Producer model": "gpt-5.6-sol",
    }
    fields.update(overrides)
    return fields


def _candidate_body(fields: dict[str, str | None]) -> str:
    lines = [
        f"Candidate ID: {protocol_mailbox.compute_learning_candidate_id(fields)}"
    ]
    lines.extend(
        f"{label}: {value}" for label, value in fields.items() if value is not None
    )
    return "\n".join(lines)


def test_metrics_report_counts_and_advisory_warns(tmp_path: Path) -> None:
    root = tmp_path / "repo"
    root.mkdir()

    def git(*arguments: str) -> str:
        return subprocess.run(
            ["git", *arguments],
            cwd=root,
            check=True,
            capture_output=True,
            env={"PATH": "/usr/bin:/bin", "HOME": str(tmp_path)},
        ).stdout.decode()

    git("init", "-q")
    git("config", "user.email", "probe@example.invalid")
    git("config", "user.name", "probe")
    (root / "README.md").write_text("target v1\n", encoding="utf-8")
    sent = root / "coordination" / "mailbox" / "sent"
    sent.mkdir(parents=True)
    source_name = "2026-07-28T01-02-03Z-director-to-operator-status.md"
    (sent / source_name).write_text(
        _event_text("director", "operator", "2026-07-28T01-02-03Z", "observed"),
        encoding="utf-8",
    )
    git("add", "-A")
    git("-c", "user.name=F", "-c", "user.email=f@example.invalid",
        "commit", "-q", "-m", "seed")
    source_commit = git("rev-parse", "HEAD").strip()
    source_ref = f"coordination/mailbox/sent/{source_name}@{source_commit}"

    readme_hash = "sha256:" + hashlib.sha256(
        (root / "README.md").read_bytes()
    ).hexdigest()
    fields_a = _candidate_fields(
        source_ref, Target="README.md", **{"Target base hash": readme_hash}
    )
    name_a = "2026-07-29T01-00-00Z-operator-to-director-learning-candidate.md"
    (sent / name_a).write_text(
        _event_text("operator", "director", "2026-07-29T01-00-00Z",
                    _candidate_body(fields_a)),
        encoding="utf-8",
    )
    fields_b = _candidate_fields(
        source_ref, Statement="A second lesson with no promoting request."
    )
    name_b = "2026-07-29T02-00-00Z-operator-to-director-learning-candidate.md"
    (sent / name_b).write_text(
        _event_text("operator", "director", "2026-07-29T02-00-00Z",
                    _candidate_body(fields_b)),
        encoding="utf-8",
    )
    git("add", "-A")
    git("-c", "user.name=F", "-c", "user.email=f@example.invalid",
        "commit", "-q", "-m", "candidates")
    candidate_commit = git("rev-parse", "HEAD").strip()

    # Candidate B is declined first, then accepted: the counters must follow
    # each candidate's LATEST disposition and partition the disposed set.
    for stamp, name, disposition in (
        ("2026-07-30T01-00-00Z", name_a, "accepted"),
        ("2026-07-30T01-30-00Z", name_b, "declined"),
        ("2026-07-30T02-00-00Z", name_b, "accepted"),
    ):
        decision = f"{stamp}-director-to-all-decision.md"
        (sent / decision).write_text(
            _event_text(
                "director", "all", stamp,
                f"Candidate: coordination/mailbox/sent/{name}@{candidate_commit}\n"
                f"Disposition: {disposition}",
            ),
            encoding="utf-8",
        )
    request = "2026-07-30T03-00-00Z-director-to-operator-verify-request.md"
    (sent / request).write_text(
        _event_text(
            "director", "operator", "2026-07-30T03-00-00Z",
            "Event type: verify-request\n\n"
            "## Finding Refs\n\n"
            f"- coordination/mailbox/sent/{name_a}@{candidate_commit}",
        ),
        encoding="utf-8",
    )
    report = "2026-07-30T04-00-00Z-operator-to-director-verification-report.md"
    (sent / report).write_text(
        _event_text("operator", "director", "2026-07-30T04-00-00Z", "VERDICT: GO"),
        encoding="utf-8",
    )
    git("add", "-A")
    git("-c", "user.name=F", "-c", "user.email=f@example.invalid",
        "commit", "-q", "-m", "dispositions and pair thread")

    metrics = learning_metrics.collect_metrics(root)
    assert metrics["declined"] == 0, "latest disposition wins; counters partition"
    assert metrics["review_friction"] == "1/1"
    assert metrics["candidates_total"] == 2
    assert metrics["accepted"] == 2
    # Candidate A is named by the request; only B is a linkage gap — WARN, not
    # a failure (advisory by contract I5).
    assert metrics["promotion_linkage_gaps"] == [
        f"coordination/mailbox/sent/{name_b}"
    ]
    assert metrics["stale_accepted"] == []
    assert metrics["contradicted_targets"] == []
    assert metrics["index_state"] == "(unavailable: index not built)"

    # The target moves. Candidate A is LINKED (named by the request), so the
    # move is what its acceptance authorized: PROMOTED fact, never a stale
    # WARN (the first live promotion tripped the old conflated WARN forever).
    (root / "README.md").write_text("target v2\n", encoding="utf-8")
    git("add", "README.md")
    git("-c", "user.name=F", "-c", "user.email=f@example.invalid",
        "commit", "-q", "-m", "move target")
    moved = learning_metrics.collect_metrics(root)
    assert moved["promoted_target_moved"] == [
        f"coordination/mailbox/sent/{name_a} (target moved: README.md)"
    ]
    assert moved["stale_accepted"] == []

    # Candidate C: accepted against README v2, NOT named by any request. When
    # the target moves again, C is the genuinely alarming case — stale WARN.
    v2_hash = "sha256:" + hashlib.sha256(
        (root / "README.md").read_bytes()
    ).hexdigest()
    fields_c = _candidate_fields(
        source_ref, Statement="An unpromoted lesson anchored to v2.",
        Target="README.md", **{"Target base hash": v2_hash},
    )
    name_c = "2026-07-30T05-00-00Z-operator-to-director-learning-candidate.md"
    (sent / name_c).write_text(
        _event_text("operator", "director", "2026-07-30T05-00-00Z",
                    _candidate_body(fields_c)),
        encoding="utf-8",
    )
    git("add", "-A")
    git("-c", "user.name=F", "-c", "user.email=f@example.invalid",
        "commit", "-q", "-m", "candidate C")
    c_commit = git("rev-parse", "HEAD").strip()
    (sent / "2026-07-30T06-00-00Z-director-to-all-decision.md").write_text(
        _event_text(
            "director", "all", "2026-07-30T06-00-00Z",
            f"Candidate: coordination/mailbox/sent/{name_c}@{c_commit}\n"
            "Disposition: accepted",
        ),
        encoding="utf-8",
    )
    (root / "README.md").write_text("target v3\n", encoding="utf-8")
    git("add", "-A")
    git("-c", "user.name=F", "-c", "user.email=f@example.invalid",
        "commit", "-q", "-m", "accept C then move target again")
    third = learning_metrics.collect_metrics(root)
    assert third["stale_accepted"] == [
        f"coordination/mailbox/sent/{name_c} (target moved: README.md)"
    ]
    assert not any(name_c in item for item in third["promoted_target_moved"])
    assert third["promotion_linkage_gaps"] == [
        f"coordination/mailbox/sent/{name_b}",
        f"coordination/mailbox/sent/{name_c}",
    ]

    # Review-finding evasion, pinned: a NON-promoting prose mention of C in a
    # verify-request body (citation, orphaning, decline) is not linkage and
    # must not silence C's stale WARN. Only a Finding Refs ENTRY links.
    evasion = "2026-07-30T06-30-00Z-director-to-operator-verify-request.md"
    (sent / evasion).write_text(
        _event_text(
            "director", "operator", "2026-07-30T06-30-00Z",
            "Event type: verify-request\n"
            "Unrelated range. NOT promoting, explicitly DECLINED and "
            f"orphaned: coordination/mailbox/sent/{name_c}",
        ),
        encoding="utf-8",
    )
    git("add", "-A")
    git("-c", "user.name=F", "-c", "user.email=f@example.invalid",
        "commit", "-q", "-m", "non-promoting mention of C")
    mentioned = learning_metrics.collect_metrics(root)
    assert mentioned["stale_accepted"] == [
        f"coordination/mailbox/sent/{name_c} (target moved: README.md)"
    ], "a prose mention must not silence the stale WARN"

    # Candidate D proposes to supersede B. While D is UNDISPOSED (and if it
    # were declined), B retires NOTHING: a proposal replaces nothing, so B
    # keeps its linkage debt (review finding: proposal-keyed retirement let
    # any seat unilaterally clear an accepted candidate's alarms).
    fields_d = _candidate_fields(
        source_ref,
        Statement="Replacement for B per the re-issue idiom.",
        Supersedes=(
            f"coordination/mailbox/sent/{name_b}@{candidate_commit}"
        ),
    )
    name_d = "2026-07-30T07-00-00Z-operator-to-director-learning-candidate.md"
    (sent / name_d).write_text(
        _event_text("operator", "director", "2026-07-30T07-00-00Z",
                    _candidate_body(fields_d)),
        encoding="utf-8",
    )
    git("add", "-A")
    git("-c", "user.name=F", "-c", "user.email=f@example.invalid",
        "commit", "-q", "-m", "candidate D proposes to supersede B")
    d_commit = git("rev-parse", "HEAD").strip()
    proposed = learning_metrics.collect_metrics(root)
    assert proposed["retired_superseded"] == []
    assert f"coordination/mailbox/sent/{name_b}" in (
        proposed["promotion_linkage_gaps"]
    )

    # Only D's own ACCEPTANCE retires B.
    (sent / "2026-07-30T08-00-00Z-director-to-all-decision.md").write_text(
        _event_text(
            "director", "all", "2026-07-30T08-00-00Z",
            f"Candidate: coordination/mailbox/sent/{name_d}@{d_commit}\n"
            "Disposition: accepted",
        ),
        encoding="utf-8",
    )
    git("add", "-A")
    git("-c", "user.name=F", "-c", "user.email=f@example.invalid",
        "commit", "-q", "-m", "accept D")
    fourth = learning_metrics.collect_metrics(root)
    assert fourth["retired_superseded"] == [
        f"coordination/mailbox/sent/{name_b}"
    ]
    # B leaves the gap list by real retirement; C stays; the now-accepted,
    # unlinked D joins it.
    assert fourth["promotion_linkage_gaps"] == [
        f"coordination/mailbox/sent/{name_c}",
        f"coordination/mailbox/sent/{name_d}",
    ]


def test_reporter_is_read_only(tmp_path: Path) -> None:
    root = tmp_path / "repo"
    root.mkdir()
    subprocess.run(
        ["git", "init", "-q"], cwd=root, check=True, capture_output=True,
        env={"PATH": "/usr/bin:/bin", "HOME": str(tmp_path)},
    )
    for args in (["config", "user.email", "p@example.invalid"],
                 ["config", "user.name", "p"]):
        subprocess.run(["git", *args], cwd=root, check=True,
                       capture_output=True,
                       env={"PATH": "/usr/bin:/bin", "HOME": str(tmp_path)})
    (root / "coordination" / "mailbox" / "sent").mkdir(parents=True)
    (root / "coordination" / "mailbox" / "sent" / ".gitkeep").write_text("")
    subprocess.run(["git", "add", "-A"], cwd=root, check=True,
                   capture_output=True,
                   env={"PATH": "/usr/bin:/bin", "HOME": str(tmp_path)})
    subprocess.run(["git", "commit", "-q", "-m", "seed"], cwd=root, check=True,
                   capture_output=True,
                   env={"PATH": "/usr/bin:/bin", "HOME": str(tmp_path)})
    before = {p: p.stat().st_mtime_ns for p in root.rglob("*") if p.is_file()}
    learning_metrics.collect_metrics(root)
    after = {p: p.stat().st_mtime_ns for p in root.rglob("*") if p.is_file()}
    assert before == after, "the reporter must not write or touch anything"


def test_malformed_learning_events_remain_visible_in_metrics(tmp_path: Path) -> None:
    root = tmp_path / "repo"
    sent = root / "coordination/mailbox/sent"
    sent.mkdir(parents=True)
    subprocess.run(["/usr/bin/git", "-C", str(root), "init", "-q"], check=True)
    candidate = "2026-08-03T01-00-00Z-operator-to-director-learning-candidate.md"
    decision = "2026-08-03T01-01-00Z-director-to-all-decision.md"
    (sent / candidate).write_text(
        _event_text(
            "operator",
            "director",
            "2026-08-03T01-00-00Z",
            "Candidate ID: malformed",
        ),
        encoding="utf-8",
    )
    phantom = (
        "coordination/mailbox/sent/"
        "2026-08-03T00-00-00Z-operator-to-director-learning-candidate.md@"
        + "e" * 40
    )
    (sent / decision).write_text(
        _event_text(
            "director",
            "all",
            "2026-08-03T01-01-00Z",
            f"Candidate: {phantom}\nDisposition: hired",
        ),
        encoding="utf-8",
    )
    subprocess.run(["/usr/bin/git", "-C", str(root), "add", "-A"], check=True)
    subprocess.run(
        [
            "/usr/bin/git",
            "-C",
            str(root),
            "-c",
            "user.name=Metrics Test",
            "-c",
            "user.email=metrics@example.invalid",
            "commit",
            "-q",
            "-m",
            "malformed learning events",
        ],
        check=True,
    )

    metrics = learning_metrics.collect_metrics(root)

    assert metrics["candidate_events"] == {
        "seen": 1,
        "parse_valid": 0,
        "malformed": 1,
    }
    assert metrics["disposition_events"] == {
        "seen": 1,
        "parse_valid": 0,
        "malformed": 1,
    }
    assert metrics["candidate_event_errors"][0]["path"].endswith(candidate)
    assert "Candidate ID" in metrics["candidate_event_errors"][0]["error"]
    assert metrics["disposition_event_errors"][0]["path"].endswith(decision)
    assert "Disposition" in metrics["disposition_event_errors"][0]["error"]


def test_non_utf8_machine_disposition_is_recorded_not_crashed(tmp_path: Path) -> None:
    root = tmp_path / "repo"
    sent = root / "coordination/mailbox/sent"
    sent.mkdir(parents=True)
    subprocess.run(["/usr/bin/git", "-C", str(root), "init", "-q"], check=True)
    path = "2026-08-03T02-00-00Z-director-to-all-decision.md"
    phantom = (
        "coordination/mailbox/sent/"
        "2026-08-03T00-00-00Z-operator-to-director-learning-candidate.md@"
        + "e" * 40
    )
    raw = _event_text(
        "director",
        "all",
        "2026-08-03T02-00-00Z",
        f"Candidate: {phantom}\nDisposition: accepted",
    ).encode("utf-8") + b"\xff\n"
    (sent / path).write_bytes(raw)
    subprocess.run(["/usr/bin/git", "-C", str(root), "add", "-A"], check=True)
    subprocess.run(
        [
            "/usr/bin/git",
            "-C",
            str(root),
            "-c",
            "user.name=Metrics Test",
            "-c",
            "user.email=metrics@example.invalid",
            "commit",
            "-q",
            "-m",
            "non-UTF-8 disposition",
        ],
        check=True,
    )

    metrics = learning_metrics.collect_metrics(root)

    assert metrics["disposition_events"] == {
        "seen": 1,
        "parse_valid": 0,
        "malformed": 1,
    }
    assert metrics["disposition_event_errors"][0]["path"].endswith(path)
    assert "UTF-8" in metrics["disposition_event_errors"][0]["error"]


def test_non_utf8_inside_disposition_marker_is_not_concealed(tmp_path: Path) -> None:
    root = tmp_path / "repo"
    sent = root / "coordination/mailbox/sent"
    sent.mkdir(parents=True)
    subprocess.run(["/usr/bin/git", "-C", str(root), "init", "-q"], check=True)
    path = "2026-08-03T03-00-00Z-director-to-all-decision.md"
    phantom = (
        "coordination/mailbox/sent/"
        "2026-08-03T00-00-00Z-operator-to-director-learning-candidate.md@"
        + "e" * 40
    )
    prefix = _event_text(
        "director",
        "all",
        "2026-08-03T03-00-00Z",
        f"Candidate: {phantom}\nPLACEHOLDER accepted",
    ).encode("utf-8")
    (sent / path).write_bytes(prefix.replace(b"PLACEHOLDER", b"Dispo\xffsition:"))
    subprocess.run(["/usr/bin/git", "-C", str(root), "add", "-A"], check=True)
    subprocess.run(
        [
            "/usr/bin/git",
            "-C",
            str(root),
            "-c",
            "user.name=Metrics Test",
            "-c",
            "user.email=metrics@example.invalid",
            "commit",
            "-q",
            "-m",
            "concealed non-UTF-8 disposition",
        ],
        check=True,
    )

    metrics = learning_metrics.collect_metrics(root)

    assert metrics["disposition_events"] == {
        "seen": 1,
        "parse_valid": 0,
        "malformed": 1,
    }
    assert metrics["disposition_event_errors"][0]["path"].endswith(path)
    assert "UTF-8" in metrics["disposition_event_errors"][0]["error"]
