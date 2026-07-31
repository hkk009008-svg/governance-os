"""Stage 5 gate tests for the read-only metrics reporter (ADR-067)."""

from __future__ import annotations

import hashlib
import subprocess
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parent.parent.parent
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from scripts import learning_metrics  # noqa: E402
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
            "Event type: verify-request\n"
            f"promotes coordination/mailbox/sent/{name_a} in Finding Refs",
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

    # The target moves: candidate A's acceptance becomes stale.
    (root / "README.md").write_text("target v2\n", encoding="utf-8")
    git("add", "README.md")
    git("-c", "user.name=F", "-c", "user.email=f@example.invalid",
        "commit", "-q", "-m", "move target")
    moved = learning_metrics.collect_metrics(root)
    assert moved["stale_accepted"] == [
        f"coordination/mailbox/sent/{name_a} (target moved: README.md)"
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
