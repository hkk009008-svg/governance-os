from __future__ import annotations

import hashlib
import io
import json
from pathlib import Path
import subprocess
import tarfile

import pytest

import check_coordination as cc
import status


_PRE_REMEDIATION_REVIEW_BASELINE = (
    "ead5fa5c12b898f6402c4456e7f1f49f425ce00f"
)


@pytest.fixture(autouse=True)
def _supply_synthetic_active_failure_cutover(
    tmp_path: Path, monkeypatch,
):
    """Give isolated fixture repositories an explicit synthetic cutover history."""

    real_projection_git = cc._projection_git
    synthetic_roots: set[Path] = set()
    review_cutover = cc._ACTIVE_FAILURE_CUTOVER_COMMIT
    learning_cutover = cc._LEARNING_HISTORY_CUTOVER_COMMIT
    review_state_cutover = cc._REVIEW_STATE_CUTOVER_COMMIT
    legacy_cutover = cc.compact_pair_loop.LEGACY_VERBOSE_CUTOFF
    real_projection_build = cc.git_commit_projection.CommitGraphProjection.build

    class SyntheticCutoverProjection:
        def __init__(self, projection):
            self._projection = projection
            self.identity = projection.identity
            self.object_types = projection.object_types
            self.parents = projection.parents

        @property
        def head(self):
            return self._projection.head

        def matches_root(self, root):
            return self._projection.matches_root(root)

        def require_commit(self, value, label):
            if value in {review_cutover, learning_cutover, review_state_cutover}:
                return self.head
            return self._projection.require_commit(value, label)

        def is_ancestor(self, ancestor, descendant):
            if ancestor in {review_cutover, learning_cutover, review_state_cutover}:
                ancestor = self.head
            return self._projection.is_ancestor(ancestor, descendant)

        def ancestors_of(self, value):
            if value == learning_cutover:
                return self._projection.ancestors_of("HEAD")
            if value == legacy_cutover:
                return frozenset()
            return self._projection.ancestors_of(value)

        def assert_current(self):
            return self._projection.assert_current()

    def projection_build(repo_root, candidate_object_ids, **kwargs):
        root = Path(repo_root).resolve()
        if not root.is_relative_to(tmp_path.resolve()):
            return real_projection_build(repo_root, candidate_object_ids, **kwargs)
        if real_projection_git(
            root, "cat-file", "-e", f"{review_cutover}^{{commit}}"
        ).returncode != 0:
            synthetic_roots.add(root)
        candidates = set(candidate_object_ids) - {
            review_cutover,
            learning_cutover,
            review_state_cutover,
            legacy_cutover,
        }
        return SyntheticCutoverProjection(
            real_projection_build(repo_root, candidates, **kwargs)
        )

    def projection_git(repo_root: Path, *arguments: str):
        root = Path(repo_root).resolve()
        inside_fixture = root.is_relative_to(tmp_path.resolve())
        if (
            inside_fixture
            and arguments
            == (
                "archive",
                "--format=tar",
                learning_cutover,
                "coordination/mailbox/sent",
            )
        ):
            return real_projection_git(
                root,
                "archive",
                "--format=tar",
                "HEAD",
                "coordination/mailbox/sent",
            )
        if inside_fixture and arguments == ("rev-list", learning_cutover):
            return real_projection_git(root, "rev-list", "HEAD")
        if (
            inside_fixture
            and arguments
            == (
                "ls-tree",
                "-r",
                "-z",
                "--full-tree",
                learning_cutover,
                "--",
                "coordination/mailbox/sent",
            )
        ):
            return real_projection_git(
                root,
                "ls-tree",
                "-r",
                "-z",
                "--full-tree",
                "HEAD",
                "--",
                "coordination/mailbox/sent",
            )
        if (
            inside_fixture
            and root in synthetic_roots
            and arguments[:3]
            in {
                ("merge-base", "--is-ancestor", review_cutover),
                ("merge-base", "--is-ancestor", learning_cutover),
            }
        ):
            return subprocess.CompletedProcess(arguments, 0, stdout=b"", stderr=b"")
        if (
            inside_fixture
            and root in synthetic_roots
            and len(arguments) >= 2
            and arguments[0] == "rev-list"
            and arguments[1].startswith(f"{review_cutover}..")
        ):
            return real_projection_git(
                root, "rev-list", "HEAD", "--", "coordination/mailbox/sent"
            )
        result = real_projection_git(root, *arguments)
        if (
            inside_fixture
            and arguments
            in {
                ("cat-file", "-e", f"{review_cutover}^{{commit}}"),
                ("cat-file", "-e", f"{learning_cutover}^{{commit}}"),
            }
            and result.returncode != 0
        ):
            synthetic_roots.add(root)
            return subprocess.CompletedProcess(arguments, 0, stdout=b"", stderr=b"")
        if (
            inside_fixture
            and root in synthetic_roots
            and arguments
            == ("rev-list", "--ancestry-path", f"{learning_cutover}..HEAD")
        ):
            return real_projection_git(root, "rev-list", "HEAD")
        return result

    def learning_only_projection_git(repo_root: Path, *arguments: str):
        """Keep the learning cutover synthetic while exposing review-cutover failure."""

        root = Path(repo_root).resolve()
        if arguments == ("rev-list", learning_cutover):
            return real_projection_git(root, "rev-list", "HEAD")
        if arguments == (
            "ls-tree",
            "-r",
            "-z",
            "--full-tree",
            learning_cutover,
            "--",
            "coordination/mailbox/sent",
        ):
            return real_projection_git(
                root,
                "ls-tree",
                "-r",
                "-z",
                "--full-tree",
                "HEAD",
                "--",
                "coordination/mailbox/sent",
            )
        return real_projection_git(root, *arguments)

    monkeypatch.setattr(cc, "_projection_git", projection_git)
    monkeypatch.setattr(
        cc.git_commit_projection.CommitGraphProjection,
        "build",
        staticmethod(projection_build),
    )
    return learning_only_projection_git


def _seed_coordination(
    tmp_path: Path, *, include_history_manifest: bool = True
) -> Path:
    coord = tmp_path / "coordination"
    sent = coord / "mailbox" / "sent"
    seen = coord / "mailbox" / "seen"
    sent.mkdir(parents=True)
    seen.mkdir(parents=True)
    for seat in cc.ROLES:
        (seen / f"{seat}.txt").write_text("0", encoding="utf-8")
    baselines = tmp_path / "scripts/baselines"
    baselines.mkdir(parents=True)
    (baselines / "lane_v_reports_pre_v3.json").write_text(
        json.dumps(
            {"schema_version": "lane-v-report-pre-v3-baseline/v1", "reports": []}
        ),
        encoding="utf-8",
    )
    if include_history_manifest:
        (baselines / "immutable_review_history_exceptions.json").write_text(
            json.dumps(
                {"schema_version": "immutable-review-history-exceptions/v1", "entries": []}
            ),
            encoding="utf-8",
        )
    return coord


def _write_event(coord: Path, name: str, body: str) -> None:
    (coord / "mailbox" / "sent" / name).write_text(body, encoding="utf-8")


# Hermetic environment for fixture git. The ambient VM configuration
# (~/.gitconfig commit signing through the exec-daemon ssh-keygen shim,
# core.fsmonitor daemons, /etc/gitconfig filters) must not run inside
# throwaway test repositories: with it inherited, this file's fixture
# commits produced a deterministic wall of ~29s low-CPU stalls
# (579.7s twice in a row; the same tests pass in under a second
# hermetically). Committing fixtures set their own user identity locally.
_GIT_ENV = {
    "PATH": "/usr/bin:/bin",
    "HOME": "/var/empty" if Path("/var/empty").is_dir() else "/nonexistent",
    "GIT_CONFIG_NOSYSTEM": "1",
    "GIT_CONFIG_COUNT": "1",
    "GIT_CONFIG_KEY_0": "init.defaultBranch",
    "GIT_CONFIG_VALUE_0": "main",
}


def _git(root: Path, *args: str) -> str:
    completed = subprocess.run(
        ["git", *args],
        cwd=root,
        text=True,
        capture_output=True,
        check=True,
        env=_GIT_ENV,
    )
    return completed.stdout.strip()


def _clone_pre_remediation_review_baseline(
    repo_root: Path, tmp_path: Path, name: str
) -> Path:
    """Freeze live-mailbox regression fixtures before the remediation review."""

    clone = tmp_path / name
    _git(tmp_path, "clone", "--no-local", "-q", str(repo_root), str(clone))
    _git(clone, "checkout", "--detach", "-q", _PRE_REMEDIATION_REVIEW_BASELINE)
    return clone


def _review_repo(
    tmp_path: Path, *, include_history_manifest: bool = True
) -> tuple[Path, Path, str, str]:
    coord = _seed_coordination(
        tmp_path, include_history_manifest=include_history_manifest
    )
    (coord / "mailbox/kinds.txt").write_text(
        "verification-report\nverify-request\n", encoding="utf-8"
    )
    _git(tmp_path, "init", "-q")
    _git(tmp_path, "config", "user.name", "Coord Test")
    _git(tmp_path, "config", "user.email", "coord@example.invalid")
    (tmp_path / "payload.txt").write_text("base\n", encoding="utf-8")
    _git(tmp_path, "add", ".")
    _git(tmp_path, "commit", "-q", "-m", "base")
    base = _git(tmp_path, "rev-parse", "HEAD")
    (tmp_path / "payload.txt").write_text("head\n", encoding="utf-8")
    _git(tmp_path, "add", "payload.txt")
    _git(tmp_path, "commit", "-q", "-m", "head")
    return tmp_path, coord, base, _git(tmp_path, "rev-parse", "HEAD")


def _commit_request(
    root: Path,
    base: str,
    head: str,
    *,
    timestamp: str = "2026-07-25T07-00-00Z",
    finding_refs: bool = True,
    remediates_failed_report: str | None = None,
) -> tuple[str, str]:
    path = (
        "coordination/mailbox/sent/"
        f"{timestamp}-director-to-operator-verify-request.md"
    )
    when = timestamp[:11] + timestamp[11:].replace("-", ":")
    finding_lines = () if not finding_refs else (
        "",
        "## Finding Refs",
        "",
        "- sha256:" + "1" * 64,
    )
    remediation_lines = (
        ()
        if remediates_failed_report is None
        else (f"Remediates failed report: {remediates_failed_report}",)
    )
    (root / path).write_text(
        "\n".join(
            (
                "# Director → Operator: test request",
                "",
                f"**When:** {when} · **From:** director (online)",
                "",
                "Event type: verify-request",
                f"Reviewed repository: {root}",
                f"Reviewed base: {base}",
                f"Reviewed head: {head}",
                "Author seat: director",
                "Author model: composer-2.5",
                "Assigned operator: operator",
                "Risk class: material-behavior",
                *remediation_lines,
                "",
                "## Outcome",
                "",
                "Review the exact range.",
                *finding_lines,
                "",
                "Cursor at send: 0",
                "",
            )
        ),
        encoding="utf-8",
    )
    _git(root, "add", path)
    _git(root, "commit", "-q", "-m", "verify request")
    return path, _git(root, "rev-parse", "HEAD")


def _commit_report(
    root: Path,
    base: str,
    head: str,
    request_path: str,
    request_commit: str,
    *,
    verdict: str,
    timestamp: str = "2026-07-25T07-10-00Z",
    supersedes: str | None = None,
    legacy: bool = False,
) -> tuple[str, str]:
    path = (
        "coordination/mailbox/sent/"
        f"{timestamp}-operator-to-director-verification-report.md"
    )
    when = timestamp[:11] + timestamp[11:].replace("-", ":")
    supersedes_line = () if supersedes is None else (f"Supersedes: {supersedes}",)
    risk_lines = ("Risk class: material-behavior",)
    finding_lines = () if legacy else (
        "",
        "## Finding Refs",
        "",
        "- sha256:" + "1" * 64,
        "",
        "## Finding Dispositions",
        "",
        f"- sha256:{'1' * 64}: "
        + ("addressed" if verdict != "FAIL" else "counter-evidence"),
    )
    (root / path).write_text(
        "\n".join(
            (
                f"# Operator → Director: {verdict}",
                "",
                f"**When:** {when} · **From:** operator (online)",
                "",
                "Event type: verification-report",
                f"VERDICT: {verdict}",
                f"Verification request: {request_path}@{request_commit}",
                *supersedes_line,
                f"Reviewed repository: {root}",
                f"Reviewed head: {head}",
                f"Reviewed base: {base}",
                "Reviewer seat: operator",
                "Reviewer model: claude-sonnet-5",
                *risk_lines,
                *finding_lines,
                "",
                "## Evidence",
                "",
                "$ independent actual-diff inspection",
                "→ exact range inspected",
                "",
                "## Findings",
                "",
                "None." if verdict != "FAIL" else "Remediation required.",
                "",
                "Cursor at send: 0",
                "",
            )
        ),
        encoding="utf-8",
    )
    _git(root, "add", path)
    _git(root, "commit", "-q", "-m", f"{verdict.lower()} report")
    return path, _git(root, "rev-parse", "HEAD")


def test_status_snapshot_reuses_one_committed_mailbox_projection(
    tmp_path: Path, monkeypatch
) -> None:
    root, _coord, base, head = _review_repo(tmp_path)
    _commit_request(root, base, head)
    real_projection = cc._committed_mailbox_projection
    calls: list[Path] = []

    def counted_projection(repo_root: Path):
        calls.append(Path(repo_root).resolve())
        return real_projection(repo_root)

    monkeypatch.setattr(cc, "_committed_mailbox_projection", counted_projection)

    snapshot = status.collect_orientation_snapshot(root, "operator")

    assert calls == [root.resolve()]
    assert snapshot["projection"]["head"] == _git(root, "rev-parse", "HEAD")


def test_live_seat_event_without_terminal_trigger_heading_is_accepted(tmp_path: Path):
    coord = _seed_coordination(tmp_path)
    _write_event(
        coord,
        "2026-07-07T18-01-00Z-director-to-all-status.md",
        "# Director -> All: status\n\n"
        "**When:** 2026-07-07T18:01:00Z · **From:** director\n\n"
        "The seat chain continues internally.\n\n"
        "Cursor at send: 0\n",
    )

    issues = cc.run(
        coord,
        since="2026-06-11",
        now="2026-07-07T18:02:00Z",
        docs_root=tmp_path / "docs",
    )

    assert not [issue for issue in issues if issue.severity == "FATAL"]
    assert not [issue for issue in issues if issue.kind == "missing_end_trigger"]


def test_heading_free_event_still_enforces_filename_envelope_and_cursor_guards(
    tmp_path: Path,
):
    coord = _seed_coordination(tmp_path)
    (coord / "mailbox/seen/director.txt").write_text(
        "not-a-cursor", encoding="utf-8"
    )
    _write_event(
        coord,
        "2026-07-07T18-01-00Z-director-to-director-status.md",
        "# Director -> Director: status\n\n"
        "**When:** 2026-07-07T18:00:00Z · **From:** director\n\n"
        "A malformed event remains malformed without a terminal heading.\n\n"
        "Cursor at send: 0\n",
    )

    issues = cc.run(
        coord,
        since="2026-06-11",
        now="2026-07-07T18:02:00Z",
        docs_root=tmp_path / "docs",
    )

    kinds = {issue.kind for issue in issues}
    assert {"cursor_unparseable", "self_addressed", "when_mismatch"} <= kinds
    assert "missing_end_trigger" not in kinds


def test_scalar_cursor_without_bus_reports_mailbox_fallback_unread(
    tmp_path: Path,
) -> None:
    coord = _seed_coordination(tmp_path)
    _write_event(
        coord,
        "2026-07-17T01-02-03Z-director-to-operator-status.md",
        "# Director → Operator: status\n\n"
        "**When:** 2026-07-17T01:02:03Z · **From:** director (online)\n\n"
        "body\n\n"
        "Cursor at send: 0\n",
    )

    issues = cc.run(coord, now="2026-07-17T02:00:00Z", docs_root=tmp_path / "docs")

    unread = [
        issue.message
        for issue in issues
        if issue.kind == "unread" and "operator:" in issue.message
    ]
    assert unread == ["operator: 1 unread event(s) via mailbox-fallback"]
    assert not [issue for issue in issues if issue.kind == "transport_incoherent"]


def test_partial_bus_refs_are_fatal_transport_incoherence(tmp_path: Path) -> None:
    coord = _seed_coordination(tmp_path)
    # Partial-cutover incoherence only exists under a declared signed-bus
    # transport; the mailbox default never consults these refs.
    (tmp_path / "governance.toml").write_text(
        '[coordination]\ntransport = "signed-bus"\n', encoding="utf-8"
    )
    _git(tmp_path, "init", "-q")
    _git(tmp_path, "config", "user.name", "Coord Test")
    _git(tmp_path, "config", "user.email", "coord@example.invalid")
    (tmp_path / "seed.txt").write_text("seed\n", encoding="utf-8")
    _git(tmp_path, "add", "seed.txt")
    _git(tmp_path, "commit", "-q", "-m", "seed")
    _git(
        tmp_path,
        "update-ref",
        "refs/threeway/cursors/operator",
        _git(tmp_path, "rev-parse", "HEAD"),
    )

    issues = cc.run(coord, now="2026-07-17T02:00:00Z", docs_root=tmp_path / "docs")

    fatals = [
        issue for issue in issues
        if issue.kind == "transport_incoherent" and "operator" in issue.message
    ]
    assert fatals
    assert all(issue.severity == "FATAL" for issue in fatals)


def test_review_projection_failure_is_not_an_empty_pending_queue(
    tmp_path: Path, monkeypatch
) -> None:
    coord = _seed_coordination(tmp_path)
    _git(tmp_path, "init", "-q")
    _write_event(
        coord,
        "2026-07-25T07-00-00Z-director-to-operator-verify-request.md",
        "unreadable committed projection\n",
    )
    monkeypatch.setattr(
        cc,
        "_committed_mailbox_projection",
        lambda _root: (None, "projection unavailable"),
    )

    state = cc.inspect_verify_review_state(tmp_path, coord)
    issues = cc._check_current_verify_requests(tmp_path, coord, state)

    assert state.pending == ()
    assert state.problem == "projection unavailable"
    assert [(issue.kind, issue.severity) for issue in issues] == [
        ("review_projection_unavailable", "FATAL")
    ]


def test_missing_active_failure_cutover_fails_projection_without_fail_flood(
    tmp_path: Path, monkeypatch, _supply_synthetic_active_failure_cutover,
) -> None:
    root, coord, base, head = _review_repo(tmp_path)
    request_path, request_commit = _commit_request(root, base, head)
    _commit_report(
        root, base, head, request_path, request_commit, verdict="FAIL"
    )
    monkeypatch.setattr(
        cc, "_projection_git", _supply_synthetic_active_failure_cutover
    )
    real_build = cc.git_commit_projection.CommitGraphProjection.build

    def missing_cutover(*args, **kwargs):
        projection = real_build(*args, **kwargs)
        projection.require_commit = lambda value, label: (_ for _ in ()).throw(
            cc.git_commit_projection.CommitGraphProjectionError(
                "active-failure cutover is missing"
            )
        )
        return projection

    monkeypatch.setattr(
        cc.git_commit_projection.CommitGraphProjection,
        "build",
        staticmethod(missing_cutover),
    )

    state = cc.inspect_verify_review_state(root, coord)
    issues = cc.run(
        coord,
        now="2026-07-25T08:00:00Z",
        docs_root=root / "docs",
        review_state=state,
    )

    assert state.pending == ()
    assert state.failed == ()
    assert state.problem is not None
    assert "active-failure cutover commit is unavailable" in state.problem
    assert [
        (issue.kind, issue.severity)
        for issue in issues
        if issue.kind == "review_projection_unavailable"
    ] == [
        ("review_projection_unavailable", "FATAL")
    ]


def test_missing_request_operator_mapping_is_an_explicit_projection_problem() -> None:
    operator, problem = cc._mapped_request_operator({}, "request.md@" + "a" * 40)

    assert operator is None
    assert problem == (
        "active report has no mapped request operator: request.md@" + "a" * 40
    )


def test_coordinator_cursor_files_are_not_required_or_actionable(
    tmp_path: Path,
) -> None:
    coord = _seed_coordination(tmp_path)

    issues = cc.run(coord, now="2026-07-17T02:00:00Z", docs_root=tmp_path / "docs")

    assert not [
        issue
        for issue in issues
        if issue.kind.startswith("cursor_") and "coordinator" in issue.path
    ]
    assert not [
        issue
        for issue in issues
        if issue.kind == "unread" and "coordinator:" in issue.message
    ]


def test_new_invalid_current_verify_request_is_fatal(tmp_path: Path) -> None:
    coord = _seed_coordination(tmp_path)
    (coord / "mailbox/kinds.txt").write_text(
        "verify-request\n", encoding="utf-8"
    )
    _git(tmp_path, "init", "-q")
    _git(tmp_path, "config", "user.name", "Coord Test")
    _git(tmp_path, "config", "user.email", "coord@example.invalid")
    request = (
        coord
        / "mailbox/sent/"
        "2026-07-25T06-00-00Z-coordinator-to-operator-verify-request.md"
    )
    request.write_text(
        "# Coordinator → Operator: invalid request\n\n"
        "**When:** 2026-07-25T06:00:00Z · **From:** coordinator (online)\n\n"
        "Event type: verify-request\n"
        f"Reviewed head: {'a' * 40}\n"
        f"Reviewed base: {'b' * 40}\n"
        "Author seat: coordinator\n"
        "Author model: fixture\n"
        "Assigned operator: operator\n\n"
        "## Outcome\n\n"
        "Review it.\n\n"
        "Cursor at send: 0\n",
        encoding="utf-8",
    )
    _git(tmp_path, "add", ".")
    _git(tmp_path, "commit", "-q", "-m", "invalid request")

    issues = cc.run(coord, now="2026-07-25T06:01:00Z", docs_root=tmp_path / "docs")

    invalid = [issue for issue in issues if issue.kind == "invalid_current_verify_request"]
    assert len(invalid) == 1
    assert invalid[0].severity == "FATAL"


def test_live_repo_has_no_fatal_invalid_current_verify_request(
    repo_root: Path,
) -> None:
    """No seat may be left holding an unparseable current request.

    An invalid request cannot be answered: a verdict bound to it has no
    machine-valid binding, so the work reads as accepted while nothing
    validates. The 2026-07-25 duplicate-cursor-footer request was exactly that
    case, and it was cleared by a superseding re-issue rather than by lowering
    the gate.

    A pre-cutover immutable request may still surface as ADVISORY — it is
    evidence that grants no authority, and a FATAL on an immutable artifact
    could never be cleared by anyone. Post-cutover invalid requests stay FATAL;
    that path is covered against a synthetic repository above.
    """
    issues = cc.run(
        repo_root / "coordination",
        now="2026-07-25T06:01:00Z",
        docs_root=repo_root / "docs",
    )

    invalid = [
        issue
        for issue in issues
        if issue.kind == "invalid_current_verify_request"
    ]

    assert [issue for issue in invalid if issue.severity == "FATAL"] == []
    for issue in invalid:
        assert issue.severity == "ADVISORY"
        assert "pre-cutover immutable request remains invalid" in issue.message


def test_valid_terminal_report_removes_request_from_pending(tmp_path: Path) -> None:
    root, coord, base, head = _review_repo(tmp_path)
    request_path, request_commit = _commit_request(root, base, head)
    _commit_report(
        root, base, head, request_path, request_commit, verdict="GO"
    )

    state = cc.inspect_verify_review_state(root, coord)

    assert state.pending == ()
    assert state.failed == ()


def test_valid_fail_is_terminal_but_surfaces_remediation_blocker(
    tmp_path: Path,
) -> None:
    root, coord, base, head = _review_repo(tmp_path)
    request_path, request_commit = _commit_request(root, base, head)
    report_path, report_commit = _commit_report(
        root, base, head, request_path, request_commit, verdict="FAIL"
    )

    state = cc.inspect_verify_review_state(root, coord)

    assert state.pending == ()
    assert [(item.request_path, item.request_commit) for item in state.failed] == [
        (request_path, request_commit)
    ]
    assert [(item.report_path, item.report_commit) for item in state.failed] == [
        (report_path, report_commit)
    ]


def test_newer_pending_request_does_not_hide_active_fail(tmp_path: Path) -> None:
    root, coord, base, head = _review_repo(tmp_path)
    failed_path, failed_commit = _commit_request(root, base, head)
    report_path, report_commit = _commit_report(
        root, base, head, failed_path, failed_commit, verdict="FAIL"
    )
    pending_path, pending_commit = _commit_request(
        root, base, head, timestamp="2026-07-25T08-00-00Z"
    )

    state = cc.inspect_verify_review_state(root, coord)

    assert [(item.path, item.commit) for item in state.pending] == [
        (pending_path, pending_commit)
    ]
    assert [
        (item.request_path, item.request_commit, item.report_path, item.report_commit)
        for item in state.failed
    ] == [(failed_path, failed_commit, report_path, report_commit)]


@pytest.mark.parametrize("verdict", ("GO", "NITS"))
def test_newer_request_terminal_report_does_not_clear_older_fail(
    tmp_path: Path, verdict: str,
) -> None:
    root, coord, base, head = _review_repo(tmp_path)
    failed_path, failed_commit = _commit_request(root, base, head)
    report_path, report_commit = _commit_report(
        root, base, head, failed_path, failed_commit, verdict="FAIL"
    )
    newer_path, newer_commit = _commit_request(
        root, base, head, timestamp="2026-07-25T08-00-00Z"
    )
    _commit_report(
        root,
        base,
        head,
        newer_path,
        newer_commit,
        verdict=verdict,
        timestamp="2026-07-25T08-10-00Z",
    )

    state = cc.inspect_verify_review_state(root, coord)

    assert state.pending == ()
    assert [(item.report_path, item.report_commit) for item in state.failed] == [
        (report_path, report_commit)
    ]


@pytest.mark.parametrize("verdict", ("GO", "NITS"))
def test_exact_same_request_terminal_can_clear_fail_while_newer_stays_pending(
    tmp_path: Path, verdict: str,
) -> None:
    root, coord, base, head = _review_repo(tmp_path)
    failed_path, failed_commit = _commit_request(root, base, head)
    report_path, report_commit = _commit_report(
        root, base, head, failed_path, failed_commit, verdict="FAIL"
    )
    _commit_report(
        root,
        base,
        head,
        failed_path,
        failed_commit,
        verdict=verdict,
        timestamp="2026-07-25T07-20-00Z",
        supersedes=f"{report_path}@{report_commit}",
    )
    pending_path, pending_commit = _commit_request(
        root, base, head, timestamp="2026-07-25T08-00-00Z"
    )

    state = cc.inspect_verify_review_state(root, coord)

    assert [(item.path, item.commit) for item in state.pending] == [
        (pending_path, pending_commit)
    ]
    assert state.failed == ()


def test_pre_cutover_fail_does_not_flood_active_review_state(tmp_path: Path) -> None:
    root, coord, base, head = _review_repo(tmp_path)
    legacy_path, legacy_commit = _commit_request(
        root, base, head, timestamp="2026-07-25T05-00-00Z"
    )
    _commit_report(
        root,
        base,
        head,
        legacy_path,
        legacy_commit,
        verdict="FAIL",
        timestamp="2026-07-25T05-10-00Z",
    )
    pending_path, pending_commit = _commit_request(root, base, head)

    state = cc.inspect_verify_review_state(root, coord)

    assert [(item.path, item.commit) for item in state.pending] == [
        (pending_path, pending_commit)
    ]
    assert state.failed == ()


def test_same_request_go_without_supersedes_leaves_fail_active(
    tmp_path: Path,
) -> None:
    root, coord, base, head = _review_repo(tmp_path)
    request_path, request_commit = _commit_request(root, base, head)
    fail_path, fail_commit = _commit_report(
        root, base, head, request_path, request_commit, verdict="FAIL"
    )
    _commit_report(
        root,
        base,
        head,
        request_path,
        request_commit,
        verdict="GO",
        timestamp="2026-07-25T07-20-00Z",
    )

    state = cc.inspect_verify_review_state(root, coord)

    assert state.pending == ()
    assert [(item.report_path, item.report_commit) for item in state.failed] == [
        (fail_path, fail_commit)
    ]


def test_unrelated_request_go_cannot_supersede_current_fail(
    tmp_path: Path,
) -> None:
    root, coord, base, head = _review_repo(tmp_path)
    older_path, older_commit = _commit_request(
        root, base, head, timestamp="2026-07-25T06-00-00Z"
    )
    current_path, current_commit = _commit_request(root, base, head)
    fail_path, fail_commit = _commit_report(
        root, base, head, current_path, current_commit, verdict="FAIL"
    )
    _commit_report(
        root,
        base,
        head,
        older_path,
        older_commit,
        verdict="GO",
        timestamp="2026-07-25T07-20-00Z",
        supersedes=f"{fail_path}@{fail_commit}",
    )

    state = cc.inspect_verify_review_state(root, coord)

    assert state.pending == ()
    assert [(item.report_path, item.report_commit) for item in state.failed] == [
        (fail_path, fail_commit)
    ]


def test_malformed_or_mismatched_report_does_not_clear_pending(
    tmp_path: Path,
) -> None:
    root, coord, base, head = _review_repo(tmp_path)
    request_path, request_commit = _commit_request(root, base, head)
    _commit_report(
        root,
        base,
        head,
        request_path,
        "0" * 40,
        verdict="FAIL",
    )

    state = cc.inspect_verify_review_state(root, coord)

    assert [(item.path, item.commit) for item in state.pending] == [
        (request_path, request_commit)
    ]
    assert state.failed == ()
    snapshot = status.collect_orientation_snapshot(root, "operator")
    assert snapshot["current_request"]["path"] == request_path
    assert snapshot["current_request"]["commit"] == request_commit
    assert snapshot["next_action"] == "operator reviews the exact committed request"


def test_malformed_report_does_not_clear_pending(tmp_path: Path) -> None:
    root, coord, base, head = _review_repo(tmp_path)
    request_path, request_commit = _commit_request(root, base, head)
    path = (
        "coordination/mailbox/sent/"
        "2026-07-25T07-10-00Z-operator-to-director-verification-report.md"
    )
    (root / path).write_text(
        "\n".join(
            (
                "# Operator → Director: malformed FAIL",
                "",
                "**When:** 2026-07-25T07:10:00Z · **From:** operator (online)",
                "",
                "Event type: verification-report",
                "VERDICT: FAIL",
                f"Verification request: {request_path}@{request_commit}",
                "",
                "Cursor at send: 0",
                "",
            )
        ),
        encoding="utf-8",
    )
    _git(root, "add", path)
    _git(root, "commit", "-q", "-m", "malformed report")

    state = cc.inspect_verify_review_state(root, coord)

    assert [(item.path, item.commit) for item in state.pending] == [
        (request_path, request_commit)
    ]
    assert state.failed == ()


def test_modified_terminal_event_fails_immutable_projection(tmp_path: Path) -> None:
    root, coord, base, head = _review_repo(tmp_path)
    request_path, request_commit = _commit_request(root, base, head)
    _commit_report(
        root, base, head, request_path, request_commit, verdict="FAIL"
    )
    _commit_report(
        root, base, head, request_path, request_commit, verdict="GO"
    )

    state = cc.inspect_verify_review_state(root, coord)
    issues = cc._check_current_verify_requests(root, coord, state)

    assert state.problem is not None
    assert "immutable" in state.problem
    assert [(issue.kind, issue.severity) for issue in issues] == [
        ("review_projection_unavailable", "FATAL")
    ]


@pytest.mark.parametrize("target", ("request", "report"))
def test_deleted_canonical_review_event_fails_projection(
    tmp_path: Path, target: str,
) -> None:
    root, coord, base, head = _review_repo(tmp_path)
    request_path, request_commit = _commit_request(root, base, head)
    report_path, _report_commit = _commit_report(
        root, base, head, request_path, request_commit, verdict="FAIL"
    )
    deleted = request_path if target == "request" else report_path
    _git(root, "rm", "-q", deleted)
    _git(root, "commit", "-q", "-m", f"delete {target}")

    state = cc.inspect_verify_review_state(root, coord)
    issues = cc._check_current_verify_requests(root, coord, state)

    assert state.pending == ()
    assert state.failed == ()
    assert state.problem is not None
    assert deleted in state.problem
    assert [(issue.kind, issue.severity) for issue in issues] == [
        ("review_projection_unavailable", "FATAL")
    ]


def test_renamed_terminal_report_fails_projection(tmp_path: Path) -> None:
    root, coord, base, head = _review_repo(tmp_path)
    request_path, request_commit = _commit_request(root, base, head)
    report_path, _report_commit = _commit_report(
        root, base, head, request_path, request_commit, verdict="FAIL"
    )
    renamed = report_path.replace("-verification-report.md", "-status.md")
    _git(root, "mv", report_path, renamed)
    _git(root, "commit", "-q", "-m", "rename terminal report")

    state = cc.inspect_verify_review_state(root, coord)

    assert state.pending == ()
    assert state.failed == ()
    assert state.problem is not None
    assert report_path in state.problem


@pytest.mark.parametrize("mutation", ("removed", "empty", "duplicate"))
def test_mutated_report_request_binding_fails_projection_before_filtering(
    tmp_path: Path, mutation: str,
) -> None:
    root, coord, base, head = _review_repo(tmp_path)
    request_path, request_commit = _commit_request(root, base, head)
    report_path, _report_commit = _commit_report(
        root, base, head, request_path, request_commit, verdict="FAIL"
    )
    report = root / report_path
    text = report.read_text(encoding="utf-8")
    binding = f"Verification request: {request_path}@{request_commit}"
    if mutation == "removed":
        text = text.replace(binding + "\n", "")
    elif mutation == "empty":
        text = text.replace(binding, "Verification request: ")
    else:
        text = text.replace(binding, binding + "\n" + binding)
    report.write_text(text, encoding="utf-8")
    _git(root, "add", report_path)
    _git(root, "commit", "-q", "-m", f"mutate binding {mutation}")

    state = cc.inspect_verify_review_state(root, coord)

    assert state.pending == ()
    assert state.failed == ()
    assert state.problem is not None
    assert "immutable" in state.problem


def test_dirty_worktree_deletion_does_not_hide_committed_fail(tmp_path: Path) -> None:
    root, coord, base, head = _review_repo(tmp_path)
    request_path, request_commit = _commit_request(root, base, head)
    report_path, report_commit = _commit_report(
        root, base, head, request_path, request_commit, verdict="FAIL"
    )
    (root / request_path).unlink()
    (root / report_path).unlink()

    state = cc.inspect_verify_review_state(root, coord)

    assert state.problem is None
    assert state.pending == ()
    assert [(item.report_path, item.report_commit) for item in state.failed] == [
        (report_path, report_commit)
    ]


def test_nonexistent_reviewed_range_does_not_clear_pending(tmp_path: Path) -> None:
    root, coord, _base, _head = _review_repo(tmp_path)
    base, head = "0" * 40, "f" * 40
    request_path, request_commit = _commit_request(root, base, head)
    _commit_report(
        root, base, head, request_path, request_commit, verdict="GO"
    )

    state = cc.inspect_verify_review_state(root, coord)

    assert state.failed == ()
    assert len(state.pending) == 1
    assert state.pending[0].path == request_path
    assert state.pending[0].valid is False
    assert state.pending[0].problem


@pytest.mark.parametrize("verdict", ("GO", "NITS"))
def test_valid_same_request_superseding_report_clears_fail(
    tmp_path: Path, verdict: str,
) -> None:
    root, coord, base, head = _review_repo(tmp_path)
    request_path, request_commit = _commit_request(root, base, head)
    fail_path, fail_commit = _commit_report(
        root, base, head, request_path, request_commit, verdict="FAIL"
    )
    _commit_report(
        root,
        base,
        head,
        request_path,
        request_commit,
        verdict=verdict,
        timestamp="2026-07-25T07-20-00Z",
        supersedes=f"{fail_path}@{fail_commit}",
    )

    state = cc.inspect_verify_review_state(root, coord)

    assert state.pending == ()
    assert state.failed == ()


@pytest.mark.parametrize("verdict", ("GO", "NITS"))
def test_explicit_different_request_remediation_clears_active_fail(
    tmp_path: Path, verdict: str,
) -> None:
    root, coord, base, head = _review_repo(tmp_path)
    failed_path, failed_request_commit = _commit_request(root, base, head)
    fail_path, fail_commit = _commit_report(
        root,
        base,
        head,
        failed_path,
        failed_request_commit,
        verdict="FAIL",
    )
    (root / "payload.txt").write_text("remediated\n", encoding="utf-8")
    _git(root, "add", "payload.txt")
    _git(root, "commit", "-q", "-m", "fix: remediate active fail")
    remediation_head = _git(root, "rev-parse", "HEAD")
    failed_ref = f"{fail_path}@{fail_commit}"
    request_path, request_commit = _commit_request(
        root,
        fail_commit,
        remediation_head,
        timestamp="2026-07-25T08-00-00Z",
        remediates_failed_report=failed_ref,
    )
    _commit_report(
        root,
        fail_commit,
        remediation_head,
        request_path,
        request_commit,
        verdict=verdict,
        timestamp="2026-07-25T08-10-00Z",
        supersedes=failed_ref,
    )

    state = cc.inspect_verify_review_state(root, coord)

    assert state.problem is None
    assert state.pending == ()
    assert state.failed == ()


def test_sibling_branch_remediation_report_cannot_clear_active_fail(
    tmp_path: Path,
) -> None:
    """A report must descend from the exact request commit it names.

    Tree projection alone sees both sibling events after their branches merge.
    Without introduction ancestry, the report can bind bytes from the sibling
    request object and launder the active FAIL despite never observing that
    request in its own history.
    """

    root, coord, base, head = _review_repo(tmp_path)
    failed_path, failed_request_commit = _commit_request(root, base, head)
    fail_path, fail_commit = _commit_report(
        root,
        base,
        head,
        failed_path,
        failed_request_commit,
        verdict="FAIL",
    )
    (root / "payload.txt").write_text("remediated\n", encoding="utf-8")
    _git(root, "add", "payload.txt")
    _git(root, "commit", "-q", "-m", "fix: remediate active fail")
    common = _git(root, "rev-parse", "HEAD")
    failed_ref = f"{fail_path}@{fail_commit}"

    _git(root, "switch", "-q", "-c", "request-branch")
    request_path, request_commit = _commit_request(
        root,
        fail_commit,
        common,
        timestamp="2026-07-25T08-00-00Z",
        remediates_failed_report=failed_ref,
    )

    _git(root, "switch", "-q", "-c", "report-branch", common)
    _report_path, report_commit = _commit_report(
        root,
        fail_commit,
        common,
        request_path,
        request_commit,
        verdict="GO",
        timestamp="2026-07-25T08-10-00Z",
        supersedes=failed_ref,
    )
    ancestry = subprocess.run(
        [
            "env",
            "-u",
            "GIT_INDEX_FILE",
            "git",
            "merge-base",
            "--is-ancestor",
            request_commit,
            report_commit,
        ],
        cwd=root,
        capture_output=True,
        check=False,
    )
    assert request_commit != report_commit
    assert ancestry.returncode == 1
    _git(root, "merge", "-q", "--no-ff", "-m", "merge sibling events", "request-branch")

    state = cc.inspect_verify_review_state(root, coord)

    assert state.problem is None
    assert [(item.path, item.commit) for item in state.pending] == [
        (request_path, request_commit)
    ]
    assert [(item.report_path, item.report_commit) for item in state.failed] == [
        (fail_path, fail_commit)
    ]


def test_different_request_remediation_cannot_reuse_inactive_fail(
    tmp_path: Path,
) -> None:
    root, coord, base, head = _review_repo(tmp_path)
    failed_path, failed_request_commit = _commit_request(root, base, head)
    fail_path, fail_commit = _commit_report(
        root,
        base,
        head,
        failed_path,
        failed_request_commit,
        verdict="FAIL",
    )
    failed_ref = f"{fail_path}@{fail_commit}"
    _commit_report(
        root,
        base,
        head,
        failed_path,
        failed_request_commit,
        verdict="GO",
        timestamp="2026-07-25T07-20-00Z",
        supersedes=failed_ref,
    )
    (root / "payload.txt").write_text("later\n", encoding="utf-8")
    _git(root, "add", "payload.txt")
    _git(root, "commit", "-q", "-m", "fix: later work")
    remediation_head = _git(root, "rev-parse", "HEAD")
    request_path, request_commit = _commit_request(
        root,
        fail_commit,
        remediation_head,
        timestamp="2026-07-25T08-00-00Z",
        remediates_failed_report=failed_ref,
    )
    _commit_report(
        root,
        fail_commit,
        remediation_head,
        request_path,
        request_commit,
        verdict="GO",
        timestamp="2026-07-25T08-10-00Z",
        supersedes=failed_ref,
    )

    state = cc.inspect_verify_review_state(root, coord)

    assert [(item.path, item.commit) for item in state.pending] == [
        (request_path, request_commit)
    ]
    assert state.failed == ()


def test_different_request_fail_report_cannot_clear_active_fail(
    tmp_path: Path,
) -> None:
    root, coord, base, head = _review_repo(tmp_path)
    failed_path, failed_request_commit = _commit_request(root, base, head)
    fail_path, fail_commit = _commit_report(
        root,
        base,
        head,
        failed_path,
        failed_request_commit,
        verdict="FAIL",
    )
    (root / "payload.txt").write_text("attempted\n", encoding="utf-8")
    _git(root, "add", "payload.txt")
    _git(root, "commit", "-q", "-m", "fix: attempted remediation")
    remediation_head = _git(root, "rev-parse", "HEAD")
    failed_ref = f"{fail_path}@{fail_commit}"
    request_path, request_commit = _commit_request(
        root,
        fail_commit,
        remediation_head,
        timestamp="2026-07-25T08-00-00Z",
        remediates_failed_report=failed_ref,
    )
    _commit_report(
        root,
        fail_commit,
        remediation_head,
        request_path,
        request_commit,
        verdict="FAIL",
        timestamp="2026-07-25T08-10-00Z",
        supersedes=failed_ref,
    )

    state = cc.inspect_verify_review_state(root, coord)

    assert [(item.path, item.commit) for item in state.pending] == [
        (request_path, request_commit)
    ]
    assert [(item.report_path, item.report_commit) for item in state.failed] == [
        (fail_path, fail_commit)
    ]


def test_review_projection_uses_bounded_git_processes(
    tmp_path: Path, monkeypatch,
) -> None:
    root, coord, base, head = _review_repo(tmp_path)
    current_path, current_commit = _commit_request(root, base, head)
    template = (root / current_path).read_text(encoding="utf-8")
    unrelated: list[str] = []
    for minute in range(40):
        stamp = f"2026-07-24T06-{minute:02d}-00Z"
        when = f"2026-07-24T06:{minute:02d}:00Z"
        path = (
            "coordination/mailbox/sent/"
            f"{stamp}-director-to-operator-verify-request.md"
        )
        (root / path).write_text(
            template.replace(
                "**When:** 2026-07-25T07:00:00Z",
                f"**When:** {when}",
            ),
            encoding="utf-8",
        )
        unrelated.append(path)
    _git(root, "add", *unrelated)
    _git(root, "commit", "-q", "-m", "unrelated old requests")

    real_run = subprocess.run
    calls = 0

    def counted_run(*args, **kwargs):
        nonlocal calls
        calls += 1
        return real_run(*args, **kwargs)

    monkeypatch.setattr(cc.subprocess, "run", counted_run)
    state = cc.inspect_verify_review_state(root, coord)

    assert [(item.path, item.commit) for item in state.pending] == [
        (current_path, current_commit)
    ]
    # One bounded cutover tree projection and one ancestor-set query extend
    # the constant projection budget without making it mailbox-size dependent.
    assert calls <= 14


def test_production_snapshot_process_count_is_candidate_independent(
    tmp_path: Path, monkeypatch,
) -> None:
    """The real orientation seam must not fork Git once per valid request."""

    fixtures: list[Path] = []
    for request_count in (1, 8):
        root, _coord, base, head = _review_repo(
            tmp_path / f"snapshot-{request_count}"
        )
        for index in range(request_count):
            request_path, request_commit = _commit_request(
                root,
                base,
                head,
                timestamp=f"2026-08-03T14-{index * 2:02d}-00Z",
            )
            _commit_report(
                root,
                base,
                head,
                request_path,
                request_commit,
                verdict="GO",
                timestamp=f"2026-08-03T14-{index * 2 + 1:02d}-00Z",
            )
        fixtures.append(root)

    process_counts: list[int] = []
    for root in fixtures:
        calls: list[tuple[str, ...]] = []
        real_popen = subprocess.Popen

        def counted_popen(*args, **kwargs):
            calls.append(tuple(str(part) for part in args[0]))
            return real_popen(*args, **kwargs)

        with monkeypatch.context() as scoped:
            scoped.setattr(subprocess, "Popen", counted_popen)
            snapshot = status.collect_orientation_snapshot(root, "coordinator")
            assert snapshot["gate"]["fatal"] == 0, snapshot["blocker"]
        process_counts.append(len(calls))

    assert process_counts[0] == process_counts[1]
    # Fixed snapshot setup currently measures 34 process launches in this
    # fixture. Leave bounded headroom without turning timing into a gate.
    assert process_counts[0] <= 40


def test_replace_ref_cannot_rewrite_committed_fail_projection(tmp_path: Path) -> None:
    root, coord, base, head = _review_repo(tmp_path)
    request_path, request_commit = _commit_request(root, base, head)
    report_path, report_commit = _commit_report(
        root, base, head, request_path, request_commit, verdict="FAIL"
    )
    original_head = _git(root, "rev-parse", "HEAD")
    report = root / report_path
    report.write_text(
        report.read_text(encoding="utf-8")
        .replace("# Operator → Director: FAIL", "# Operator → Director: GO")
        .replace("VERDICT: FAIL", "VERDICT: GO"),
        encoding="utf-8",
    )
    _git(root, "add", report_path)
    replacement_tree = _git(root, "write-tree")
    _git(root, "restore", "--staged", "--worktree", "--", report_path)
    replacement_commit = _git(
        root,
        "commit-tree",
        replacement_tree,
        "-p",
        _git(root, "rev-parse", f"{original_head}^"),
        "-m",
        "replacement GO tree",
    )
    _git(root, "replace", original_head, replacement_commit)
    assert "VERDICT: GO" in _git(root, "show", f"HEAD:{report_path}")

    state = cc.inspect_verify_review_state(root, coord)

    assert state.problem is None
    assert state.pending == ()
    assert [(item.report_path, item.report_commit) for item in state.failed] == [
        (report_path, report_commit)
    ]


def test_run_fails_closed_when_head_changes_after_projection(tmp_path: Path) -> None:
    root, coord, base, head = _review_repo(tmp_path)
    _commit_request(root, base, head)
    projection_result = cc.committed_mailbox_projection(root)
    state = cc.inspect_verify_review_state(
        root, coord, projection_result=projection_result
    )
    assert state.problem is None
    _git(root, "commit", "--allow-empty", "-q", "-m", "move HEAD")

    issues = cc.run(
        coord,
        docs_root=root / "docs",
        review_state=state,
        committed_projection=projection_result,
    )

    assert [
        (issue.kind, issue.severity)
        for issue in issues
        if issue.kind == "commit_projection_identity_drift"
    ] == [("commit_projection_identity_drift", "FATAL")]


def test_delete_then_identical_reintroduction_keeps_earliest_introduction(
    tmp_path: Path,
) -> None:
    """A revert restoring identical bytes is not mutation (2026-08-12 incident).

    The live corpus was deleted wholesale and byte-identically restored by a
    merge revert; every event then carried two `--diff-filter=A`
    introductions. Immutability is a property of bytes, so the projection
    keeps the earliest introduction fact instead of failing closed.
    """

    root, _coord, base, head = _review_repo(tmp_path)
    request_path, request_commit = _commit_request(root, base, head)
    manifest_path = cc._ARCHIVE_HISTORY_EXCEPTIONS
    original_bytes = (root / request_path).read_bytes()
    manifest_bytes = (root / manifest_path).read_bytes()

    _git(root, "rm", "-q", request_path, manifest_path)
    _git(root, "commit", "-q", "-m", "remove corpus")
    (root / request_path).parent.mkdir(parents=True, exist_ok=True)
    (root / request_path).write_bytes(original_bytes)
    (root / manifest_path).parent.mkdir(parents=True, exist_ok=True)
    (root / manifest_path).write_bytes(manifest_bytes)
    _git(root, "add", request_path, manifest_path)
    _git(root, "commit", "-q", "-m", "revert restore")

    projection, problem = cc.committed_mailbox_projection(root)

    assert problem is None
    assert projection is not None
    introduction_commit, introduced_blob = projection.introductions[request_path]
    assert introduction_commit == request_commit
    assert introduced_blob == _git(
        root, "rev-parse", f"{request_commit}:{request_path}"
    )
    commit, immutable_problem = cc._immutable_event(projection, request_path)
    assert immutable_problem is None
    assert commit == request_commit


def test_reintroduction_with_different_bytes_stays_fatal(tmp_path: Path) -> None:
    root, _coord, base, head = _review_repo(tmp_path)
    request_path, _request_commit = _commit_request(root, base, head)
    mutated = (root / request_path).read_text(encoding="utf-8").replace(
        "Review the exact range.", "Review a different range."
    )

    _git(root, "rm", "-q", request_path)
    _git(root, "commit", "-q", "-m", "remove corpus")
    (root / request_path).parent.mkdir(parents=True, exist_ok=True)
    (root / request_path).write_text(mutated, encoding="utf-8")
    _git(root, "add", request_path)
    _git(root, "commit", "-q", "-m", "reintroduce with changed bytes")

    projection, problem = cc.committed_mailbox_projection(root)

    assert projection is None
    assert problem is not None
    assert request_path in problem
    assert "different bytes" in problem


def test_conversational_reintroduction_with_different_bytes_keeps_projection(
    tmp_path: Path,
) -> None:
    """Conversational kinds were never byte-gated by this projection.

    Nine live coordination/findings events carry pre-enforcement mutations
    that the 2026-08-12 delete/revert cycle surfaced as differing
    introductions; the review-event and manifest gates stay closed while
    legible history stays projectable.
    """

    root, coord, base, head = _review_repo(tmp_path)
    _commit_request(root, base, head)
    status_path = (
        "coordination/mailbox/sent/"
        "2026-07-25T08-00-00Z-director-to-all-status.md"
    )
    _write_event(
        coord,
        Path(status_path).name,
        "# Director status\n\n"
        "**When:** 2026-07-25T08:00:00Z · **From:** director (online)\n\n"
        "Original body.\n\nCursor at send: 0\n",
    )
    _git(root, "add", status_path)
    _git(root, "commit", "-q", "-m", "status event")
    earliest = _git(root, "rev-parse", "HEAD")

    _git(root, "rm", "-q", status_path)
    _git(root, "commit", "-q", "-m", "remove corpus")
    (root / status_path).parent.mkdir(parents=True, exist_ok=True)
    _write_event(
        coord,
        Path(status_path).name,
        "# Director status\n\n"
        "**When:** 2026-07-25T08:00:00Z · **From:** director (online)\n\n"
        "Pre-enforcement mutated body.\n\nCursor at send: 0\n",
    )
    _git(root, "add", status_path)
    _git(root, "commit", "-q", "-m", "reintroduce mutated conversational event")

    projection, problem = cc.committed_mailbox_projection(root)

    assert problem is None
    assert projection is not None
    assert projection.introductions[status_path][0] == earliest


def test_projection_refuses_head_move_between_identity_and_mailbox_reads(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    root, coord, base, head = _review_repo(tmp_path)
    _commit_request(root, base, head)
    pinned_head = _git(root, "rev-parse", "HEAD")
    raced_path = (
        "coordination/mailbox/sent/"
        "2026-08-03T15-00-00Z-director-to-all-status.md"
    )
    real_projection_git = cc._projection_git
    observed_revisions: list[str] = []
    moved = False

    def racing_projection_git(repo_root: Path, *arguments: str):
        nonlocal moved
        if arguments and arguments[0] in {"log", "archive"}:
            observed_revisions.extend(
                value for value in arguments if value == pinned_head
            )
        if arguments and arguments[0] == "log" and not moved:
            moved = True
            _write_event(
                coord,
                Path(raced_path).name,
                "# Director race status\n\n"
                "**When:** 2026-08-03T15:00:00Z · **From:** director (online)\n\n"
                "Race-only B event.\n\nCursor at send: 0\n",
            )
            _git(root, "add", raced_path)
            _git(root, "commit", "-q", "-m", "race HEAD")
        return real_projection_git(repo_root, *arguments)

    monkeypatch.setattr(cc, "_projection_git", racing_projection_git)
    projection, problem = cc.committed_mailbox_projection(root)

    assert projection is None
    assert problem is not None
    assert "identity changed before commit graph projection" in problem
    assert _git(root, "rev-parse", "HEAD") != pinned_head
    assert observed_revisions == [pinned_head, pinned_head]
    literal_archive = real_projection_git(
        root,
        "archive",
        "--format=tar",
        "HEAD",
        "coordination/mailbox/sent",
        cc._ARCHIVE_KINDS_PATH,
        cc._ARCHIVE_REPORT_BASELINE,
        cc._ARCHIVE_HISTORY_EXCEPTIONS,
    )
    literal_files, literal_problem = cc._parse_mailbox_archive(
        literal_archive.stdout
    )
    assert literal_problem is None
    assert literal_files is not None and raced_path in literal_files
    pinned_archive = real_projection_git(
        root,
        "archive",
        "--format=tar",
        pinned_head,
        "coordination/mailbox/sent",
        cc._ARCHIVE_KINDS_PATH,
        cc._ARCHIVE_REPORT_BASELINE,
        cc._ARCHIVE_HISTORY_EXCEPTIONS,
    )
    pinned_files, pinned_problem = cc._parse_mailbox_archive(
        pinned_archive.stdout
    )
    assert pinned_problem is None
    assert pinned_files is not None and raced_path not in pinned_files


def test_projection_git_scrubs_ambient_repository_and_config_overrides(
    tmp_path: Path, monkeypatch,
) -> None:
    root, _coord, _base, _head = _review_repo(tmp_path)
    expected = _git(root, "rev-parse", "HEAD")
    poisoned = {
        "GIT_INDEX_FILE": "/missing/index",
        "GIT_DIR": "/missing/git-dir",
        "GIT_WORK_TREE": "/missing/work-tree",
        "GIT_OBJECT_DIRECTORY": "/missing/objects",
        "GIT_ALTERNATE_OBJECT_DIRECTORIES": "/missing/alternate",
        "GIT_REPLACE_REF_BASE": "refs/hostile/replace/",
        "GIT_CONFIG_COUNT": "1",
        "GIT_CONFIG_KEY_0": "core.repositoryformatversion",
        "GIT_CONFIG_VALUE_0": "999",
        "GIT_CONFIG_GLOBAL": "/missing/global-config",
        "GIT_CONFIG_SYSTEM": "/missing/system-config",
        "GIT_CONFIG_NOSYSTEM": "0",
    }
    for name, value in poisoned.items():
        monkeypatch.setenv(name, value)

    result = cc._projection_git(root, "rev-parse", "HEAD")

    assert result.returncode == 0
    assert result.stdout.decode().strip() == expected


def test_legacy_reports_do_not_add_per_artifact_git_processes(
    tmp_path: Path, monkeypatch,
) -> None:
    fixtures: list[tuple[Path, Path, str, str | None]] = []
    for report_count in (0, 5, 20):
        root, coord, base, head = _review_repo(tmp_path / f"reports-{report_count}")
        request_path, request_commit = _commit_request(
            root, base, head, finding_refs=False
        )
        fail_path = None
        for index in range(report_count):
            path, _commit = _commit_report(
                root,
                base,
                head,
                request_path,
                request_commit,
                verdict="FAIL" if index == 0 else "GO",
                timestamp=f"2026-07-25T07-{index + 10:02d}-00Z",
                legacy=True,
            )
            fail_path = fail_path or path
        _git(root, "commit", "--allow-empty", "-q", "-m", "legacy cutoff")
        fixtures.append((root, coord, _git(root, "rev-parse", "HEAD"), fail_path))

    process_counts: list[int] = []
    for root, coord, cutoff, fail_path in fixtures:
        calls: list[tuple[str, ...]] = []
        real_run = subprocess.run

        def counted_run(*args, **kwargs):
            calls.append(tuple(args[0]))
            return real_run(*args, **kwargs)

        with monkeypatch.context() as scoped:
            scoped.setattr(cc.compact_pair_loop, "LEGACY_VERBOSE_CUTOFF", cutoff)
            scoped.setattr(cc.subprocess, "run", counted_run)
            state = cc.inspect_verify_review_state(root, coord)
        process_counts.append(len(calls))
        assert not [command for command in calls if "show" in command]
        if fail_path is None:
            assert len(state.pending) == 1
            assert state.failed == ()
        else:
            assert state.pending == ()
            assert [item.report_path for item in state.failed] == [fail_path]

    assert process_counts[0] == process_counts[1] == process_counts[2]
    assert process_counts[0] <= 14


def _history_exception_entry(
    path: str,
    introduction_commit: str,
    introduction_blob: str,
    accepted_current_blob: str,
    accepted_current_sha256: str,
) -> dict[str, str]:
    is_report = path.endswith("-verification-report.md")
    return {
        "path": path,
        "artifact_class": (
            "pre-v3-report-schema-repair"
            if is_report
            else "pre-enforcement-request-schema-format"
        ),
        "introduction_commit": introduction_commit,
        "introduction_blob": introduction_blob,
        "accepted_current_blob": accepted_current_blob,
        "accepted_current_sha256": accepted_current_sha256,
        "digest_authority": (
            "scripts/baselines/lane_v_reports_pre_v3.json"
            if is_report
            else "scripts/baselines/immutable_review_history_exceptions.json"
        ),
        "reason": "measured pre-enforcement fixture repair",
    }


def _commit_history_exception(
    root: Path,
    path: str,
    introduction_commit: str,
) -> dict[str, str]:
    raw = (root / path).read_bytes()
    entry = _history_exception_entry(
        path,
        introduction_commit,
        _git(root, "rev-parse", f"{introduction_commit}:{path}"),
        _git(root, "rev-parse", f"HEAD:{path}"),
        hashlib.sha256(raw).hexdigest(),
    )
    baselines = root / "scripts/baselines"
    if path.endswith("-verification-report.md"):
        (baselines / "lane_v_reports_pre_v3.json").write_text(
            json.dumps(
                {
                    "schema_version": "lane-v-report-pre-v3-baseline/v1",
                    "reports": [
                        {"path": path, "sha256": entry["accepted_current_sha256"]}
                    ],
                }
            ),
            encoding="utf-8",
        )
    (baselines / "immutable_review_history_exceptions.json").write_text(
        json.dumps(
            {"schema_version": "immutable-review-history-exceptions/v1", "entries": [entry]}
        ),
        encoding="utf-8",
    )
    _git(root, "add", "scripts/baselines")
    _git(root, "commit", "-q", "-m", "bind exact history exception")
    return entry


@pytest.mark.parametrize("mutation", ("delete", "rename", "change", "reintroduce"))
def test_frozen_history_manifest_refuses_committed_lifecycle_mutation(
    tmp_path: Path, mutation: str,
) -> None:
    root, coord, base, head = _review_repo(tmp_path)
    _commit_request(root, base, head)
    relative = "scripts/baselines/immutable_review_history_exceptions.json"
    manifest = root / relative
    original = manifest.read_bytes()
    if mutation == "delete":
        _git(root, "rm", "-q", relative)
        _git(root, "commit", "-q", "-m", "delete history manifest")
    elif mutation == "rename":
        _git(root, "mv", relative, relative + ".moved")
        _git(root, "commit", "-q", "-m", "rename history manifest")
    elif mutation == "change":
        manifest.write_bytes(original + b"\n")
        _git(root, "add", relative)
        _git(root, "commit", "-q", "-m", "mutate history manifest")
    else:
        # A byte-identical restore is tolerated since the 2026-08-12
        # delete/revert repair; the pinned laundering vector is
        # reintroduction with different bytes.
        _git(root, "rm", "-q", relative)
        _git(root, "commit", "-q", "-m", "delete history manifest")
        manifest.write_bytes(original + b"\n")
        _git(root, "add", relative)
        _git(root, "commit", "-q", "-m", "reintroduce mutated history manifest")

    state = cc.inspect_verify_review_state(root, coord)
    issues = cc._check_current_verify_requests(root, coord, state)

    assert state.problem is not None
    assert relative in state.problem
    assert state.pending == ()
    assert state.failed == ()
    assert [(issue.kind, issue.severity) for issue in issues] == [
        ("review_projection_unavailable", "FATAL")
    ]


def test_replace_ref_and_ambient_git_env_cannot_hide_manifest_mutation(
    tmp_path: Path, monkeypatch,
) -> None:
    root, coord, base, head = _review_repo(tmp_path)
    _commit_request(root, base, head)
    relative = "scripts/baselines/immutable_review_history_exceptions.json"
    manifest = root / relative
    introduced = manifest.read_bytes()
    manifest.write_bytes(introduced + b"\n")
    _git(root, "add", relative)
    _git(root, "commit", "-q", "-m", "mutate history manifest")
    mutated_head = _git(root, "rev-parse", "HEAD")

    manifest.write_bytes(introduced)
    _git(root, "add", relative)
    replacement_tree = _git(root, "write-tree")
    _git(root, "restore", "--staged", "--worktree", "--", relative)
    replacement_commit = _git(
        root,
        "commit-tree",
        replacement_tree,
        "-p",
        _git(root, "rev-parse", f"{mutated_head}^"),
        "-m",
        "replacement frozen manifest tree",
    )
    _git(root, "replace", mutated_head, replacement_commit)
    assert _git(root, "show", f"HEAD:{relative}").encode() == introduced
    for name, value in {
        "GIT_DIR": "/missing/git-dir",
        "GIT_WORK_TREE": "/missing/work-tree",
        "GIT_OBJECT_DIRECTORY": "/missing/objects",
        "GIT_REPLACE_REF_BASE": "refs/hostile/replace/",
        "GIT_CONFIG_COUNT": "1",
        "GIT_CONFIG_KEY_0": "core.repositoryformatversion",
        "GIT_CONFIG_VALUE_0": "999",
    }.items():
        monkeypatch.setenv(name, value)

    state = cc.inspect_verify_review_state(root, coord)

    assert state.problem == (
        "immutable-history exception manifest changed after introduction: "
        + relative
    )
    assert state.pending == ()
    assert state.failed == ()


def test_exact_history_exception_surfaces_advisory_and_preserves_fail(
    tmp_path: Path,
) -> None:
    root, coord, base, head = _review_repo(
        tmp_path, include_history_manifest=False
    )
    request_path, request_commit = _commit_request(root, base, head)
    report_path, report_commit = _commit_report(
        root, base, head, request_path, request_commit, verdict="FAIL"
    )
    report = root / report_path
    report.write_text(
        report.read_text(encoding="utf-8").replace(
            "# Operator → Director: FAIL", "# Operator → Director: amended FAIL"
        ),
        encoding="utf-8",
    )
    _git(root, "add", report_path)
    _git(root, "commit", "-q", "-m", "pre-enforcement report repair")
    _commit_history_exception(root, report_path, report_commit)

    state = cc.inspect_verify_review_state(root, coord)
    issues = cc._check_current_verify_requests(root, coord, state)

    assert state.problem is None
    assert [item.report_path for item in state.failed] == [report_path]
    assert state.grandfathered_history == (report_path,)
    assert [
        (issue.kind, issue.severity)
        for issue in issues
        if issue.kind == "grandfathered_review_history"
    ] == [("grandfathered_review_history", "ADVISORY")]


def _rewrite_exception_and_companion_for_current_report(
    root: Path,
    entry: dict[str, str],
) -> None:
    report_path = entry["path"]
    raw = (root / report_path).read_bytes()
    entry["accepted_current_blob"] = _git(root, "hash-object", report_path)
    entry["accepted_current_sha256"] = hashlib.sha256(raw).hexdigest()
    baselines = root / "scripts/baselines"
    (baselines / "lane_v_reports_pre_v3.json").write_text(
        json.dumps(
            {
                "schema_version": "lane-v-report-pre-v3-baseline/v1",
                "reports": [
                    {"path": report_path, "sha256": entry["accepted_current_sha256"]}
                ],
            }
        ),
        encoding="utf-8",
    )
    (baselines / "immutable_review_history_exceptions.json").write_text(
        json.dumps(
            {"schema_version": "immutable-review-history-exceptions/v1", "entries": [entry]}
        ),
        encoding="utf-8",
    )


@pytest.mark.parametrize("rewrite_manifest", (False, True))
def test_frozen_exception_authority_refuses_event_and_companion_co_update(
    tmp_path: Path, rewrite_manifest: bool,
) -> None:
    root, coord, base, head = _review_repo(
        tmp_path, include_history_manifest=False
    )
    request_path, request_commit = _commit_request(root, base, head)
    report_path, report_commit = _commit_report(
        root, base, head, request_path, request_commit, verdict="FAIL"
    )
    report = root / report_path
    report.write_text(
        report.read_text(encoding="utf-8").replace("Remediation required.", "Repair recorded."),
        encoding="utf-8",
    )
    _git(root, "add", report_path)
    _git(root, "commit", "-q", "-m", "pre-enforcement report repair")
    entry = _commit_history_exception(root, report_path, report_commit)

    report.write_text(
        report.read_text(encoding="utf-8")
        .replace("# Operator → Director: FAIL", "# Operator → Director: GO")
        .replace("VERDICT: FAIL", "VERDICT: GO"),
        encoding="utf-8",
    )
    _git(root, "add", report_path)
    if rewrite_manifest:
        _rewrite_exception_and_companion_for_current_report(root, entry)
        _git(root, "add", "scripts/baselines")
    else:
        lane = root / "scripts/baselines/lane_v_reports_pre_v3.json"
        companion = json.loads(lane.read_text(encoding="utf-8"))
        companion["reports"][0]["sha256"] = hashlib.sha256(
            report.read_bytes()
        ).hexdigest()
        lane.write_text(json.dumps(companion), encoding="utf-8")
        _git(root, "add", str(lane.relative_to(root)))
    _git(root, "commit", "-q", "-m", "attempt authority co-update")

    state = cc.inspect_verify_review_state(root, coord)

    assert state.problem is not None
    assert state.pending == ()
    assert state.failed == ()


def test_frozen_six_refuse_active_fail_go_plus_seventh_exception(
    repo_root: Path, tmp_path: Path,
) -> None:
    clone = tmp_path / "clone"
    _git(tmp_path, "clone", "--no-local", "-q", str(repo_root), str(clone))
    _git(clone, "config", "user.name", "Coord Test")
    _git(clone, "config", "user.email", "coord@example.invalid")
    report_path = (
        "coordination/mailbox/sent/"
        "2026-07-27T03-26-01Z-operator2-to-director2-verification-report.md"
    )
    report_commit = "e0fbefdb56af03b8c04b6df58245f7533a3d83c0"
    report = clone / report_path
    report.write_text(
        report.read_text(encoding="utf-8")
        .replace("VERDICT: FAIL", "VERDICT: GO")
        .replace(": counter-evidence", ": addressed"),
        encoding="utf-8",
    )
    _git(clone, "add", report_path)
    raw = report.read_bytes()
    manifest_path = clone / "scripts/baselines/immutable_review_history_exceptions.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest["entries"].append(
        _history_exception_entry(
            report_path,
            report_commit,
            _git(clone, "rev-parse", f"{report_commit}:{report_path}"),
            _git(clone, "hash-object", report_path),
            hashlib.sha256(raw).hexdigest(),
        )
    )
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
    lane_path = clone / "scripts/baselines/lane_v_reports_pre_v3.json"
    lane = json.loads(lane_path.read_text(encoding="utf-8"))
    lane["reports"].append(
        {"path": report_path, "sha256": hashlib.sha256(raw).hexdigest()}
    )
    lane_path.write_text(json.dumps(lane), encoding="utf-8")
    _git(clone, "add", "scripts/baselines")
    _git(clone, "commit", "-q", "-m", "attempt seventh exception")

    state = cc.inspect_verify_review_state(clone)

    assert state.problem is not None
    assert state.pending == ()
    assert state.failed == ()


@pytest.mark.parametrize("corruption", ("path", "digest", "introduction"))
def test_history_exception_refuses_binding_corruption(
    tmp_path: Path, corruption: str,
) -> None:
    root, coord, base, head = _review_repo(
        tmp_path, include_history_manifest=False
    )
    request_path, request_commit = _commit_request(root, base, head)
    report_path, report_commit = _commit_report(
        root, base, head, request_path, request_commit, verdict="FAIL"
    )
    report = root / report_path
    report.write_text(
        report.read_text(encoding="utf-8").replace("Remediation required.", "Repair recorded."),
        encoding="utf-8",
    )
    _git(root, "add", report_path)
    _git(root, "commit", "-q", "-m", "pre-enforcement report repair")
    entry = _commit_history_exception(root, report_path, report_commit)
    if corruption == "path":
        entry["path"] = report_path.replace("07-10-00Z", "07-11-00Z")
    elif corruption == "digest":
        entry["accepted_current_sha256"] = "0" * 64
    else:
        entry["introduction_blob"] = "0" * 40
    manifest = root / "scripts/baselines/immutable_review_history_exceptions.json"
    manifest.write_text(
        json.dumps(
            {"schema_version": "immutable-review-history-exceptions/v1", "entries": [entry]}
        ),
        encoding="utf-8",
    )
    _git(root, "add", str(manifest.relative_to(root)))
    _git(root, "commit", "-q", "-m", f"corrupt exception {corruption}")

    state = cc.inspect_verify_review_state(root, coord)

    assert state.problem is not None
    assert state.pending == ()
    assert state.failed == ()


@pytest.mark.parametrize("evasion", ("delete", "change"))
def test_history_exception_refuses_later_artifact_evasion(
    tmp_path: Path, evasion: str,
) -> None:
    root, coord, base, head = _review_repo(
        tmp_path, include_history_manifest=False
    )
    request_path, request_commit = _commit_request(root, base, head)
    report_path, report_commit = _commit_report(
        root, base, head, request_path, request_commit, verdict="FAIL"
    )
    report = root / report_path
    report.write_text(
        report.read_text(encoding="utf-8").replace("Remediation required.", "Repair recorded."),
        encoding="utf-8",
    )
    _git(root, "add", report_path)
    _git(root, "commit", "-q", "-m", "pre-enforcement report repair")
    _commit_history_exception(root, report_path, report_commit)
    if evasion == "delete":
        _git(root, "rm", "-q", report_path)
    else:
        report.write_text(
            report.read_text(encoding="utf-8") + "later drift\n", encoding="utf-8"
        )
        _git(root, "add", report_path)
    _git(root, "commit", "-q", "-m", f"later artifact {evasion}")

    state = cc.inspect_verify_review_state(root, coord)

    assert state.problem is not None
    assert state.pending == ()
    assert state.failed == ()


@pytest.mark.parametrize(
    "mutation",
    (
        {"schema_version": "wrong", "entries": []},
        {
            "schema_version": "immutable-review-history-exceptions/v1",
            "entries": [
                _history_exception_entry(
                    "../bad-verification-report.md", "1" * 40, "2" * 40, "3" * 40, "4" * 64
                )
            ],
        },
    ),
)
def test_history_exception_loader_rejects_schema_and_noncanonical_paths(
    mutation: dict[str, object],
) -> None:
    exceptions, problem = cc._parse_history_exceptions(json.dumps(mutation).encode())

    assert exceptions is None
    assert problem is not None


def test_history_exception_loader_rejects_duplicate_paths() -> None:
    entry = _history_exception_entry(
        "coordination/mailbox/sent/"
        "2026-07-01T00-00-00Z-operator-to-director-verification-report.md",
        "1" * 40,
        "2" * 40,
        "3" * 40,
        "4" * 64,
    )
    raw = json.dumps(
        {
            "schema_version": "immutable-review-history-exceptions/v1",
            "entries": [entry, entry],
        }
    ).encode()

    exceptions, problem = cc._parse_history_exceptions(raw)

    assert exceptions is None
    assert problem is not None
    assert "duplicate" in problem


def _tar_bytes(*members: tuple[tarfile.TarInfo, bytes]) -> bytes:
    output = io.BytesIO()
    with tarfile.open(fileobj=output, mode="w:") as archive:
        for member, raw in members:
            member.size = len(raw)
            archive.addfile(member, io.BytesIO(raw))
    return output.getvalue()


@pytest.mark.parametrize(
    ("name", "kind"),
    (
        ("/coordination/mailbox/kinds.txt", "file"),
        ("coordination/mailbox/sent/../escape.md", "file"),
        ("coordination/mailbox/sent/link.md", "symlink"),
    ),
)
def test_mailbox_archive_rejects_unsafe_members(name: str, kind: str) -> None:
    member = tarfile.TarInfo(name)
    if kind == "symlink":
        member.type = tarfile.SYMTYPE
        member.linkname = "coordination/mailbox/kinds.txt"

    files, problem = cc._parse_mailbox_archive(_tar_bytes((member, b"body\n")))

    assert files is None
    assert problem is not None


def test_mailbox_archive_rejects_duplicate_paths() -> None:
    name = "coordination/mailbox/kinds.txt"

    files, problem = cc._parse_mailbox_archive(
        _tar_bytes((tarfile.TarInfo(name), b"one\n"), (tarfile.TarInfo(name), b"two\n"))
    )

    assert files is None
    assert problem is not None
    assert "duplicate" in problem


def test_mailbox_archive_rejects_non_utf8_event_bytes() -> None:
    name = (
        "coordination/mailbox/sent/"
        "2026-07-25T07-10-00Z-operator-to-director-verification-report.md"
    )

    files, problem = cc._parse_mailbox_archive(
        _tar_bytes((tarfile.TarInfo(name), b"\xff\xfe"))
    )

    assert files is None
    assert problem is not None
    assert "UTF-8" in problem


def test_projection_wires_strict_archive_parser(
    tmp_path: Path, monkeypatch,
) -> None:
    root, coord, _base, _head = _review_repo(tmp_path)
    member = tarfile.TarInfo("coordination/mailbox/sent/hostile.md")
    member.type = tarfile.SYMTYPE
    member.linkname = "coordination/mailbox/kinds.txt"
    hostile_archive = _tar_bytes((member, b""))
    real_projection_git = cc._projection_git

    def hostile_projection_git(repo_root: Path, *arguments: str):
        if arguments and arguments[0] == "archive":
            return subprocess.CompletedProcess(
                args=arguments,
                returncode=0,
                stdout=hostile_archive,
                stderr=b"",
            )
        return real_projection_git(repo_root, *arguments)

    monkeypatch.setattr(cc, "_projection_git", hostile_projection_git)

    state = cc.inspect_verify_review_state(root, coord)

    assert state.problem is not None
    assert "unexpected member type" in state.problem


def test_pre_remediation_snapshot_surfaces_failed_review_and_history_exceptions(
    repo_root: Path, tmp_path: Path,
) -> None:
    baseline = _clone_pre_remediation_review_baseline(
        repo_root, tmp_path, "pre-remediation-snapshot"
    )
    request_path = (
        "coordination/mailbox/sent/"
        "2026-07-27T02-57-16Z-director2-to-operator2-verify-request.md"
    )
    request_commit = "eb05a76f79599b93cbc8dafa0ce1e4a42d6d5e7f"
    report_path = (
        "coordination/mailbox/sent/"
        "2026-07-27T03-26-01Z-operator2-to-director2-verification-report.md"
    )
    report_commit = "e0fbefdb56af03b8c04b6df58245f7533a3d83c0"

    state = cc.inspect_verify_review_state(baseline)
    projection, projection_problem = cc._committed_mailbox_projection(baseline)
    snapshot = status.collect_orientation_snapshot(baseline, "operator2")

    assert projection_problem is None
    assert projection is not None
    assert projection.introductions[cc._ARCHIVE_HISTORY_EXCEPTIONS] == (
        "14ddd1f78c5ba46775c44882b1725adf5cc72ec7",
        "9e6808ff83f9c9cc88b87ea05fce4331fa715a2c",
    )
    assert state.problem is None
    assert (request_path, request_commit) not in {
        (item.path, item.commit) for item in state.pending
    }
    assert (request_path, request_commit, report_path, report_commit) in {
        (
            item.request_path,
            item.request_commit,
            item.report_path,
            item.report_commit,
        )
        for item in state.failed
    }
    assert len(state.grandfathered_history) == 6
    assert snapshot["current_request"] is None
    assert snapshot["failed_review"] == {
        "request_path": request_path,
        "request_commit": request_commit,
        "report_path": report_path,
        "report_commit": report_commit,
        "assigned_operator": "operator2",
    }
    assert snapshot["gate"] == {
        "status": "FAIL",
        "fatal": 0,
        "advisory": 7,
        "failed_review": 1,
    }
    assert "remediate failed review" in snapshot["next_action"]


def test_post_cutover_fail_and_newer_pending_coexist_with_live_e0fb_baseline(
    repo_root: Path, tmp_path: Path,
) -> None:
    clone = _clone_pre_remediation_review_baseline(
        repo_root, tmp_path, "post-cutover"
    )
    _git(clone, "config", "user.name", "Coord Test")
    _git(clone, "config", "user.email", "coord@example.invalid")
    source_request_path = (
        "coordination/mailbox/sent/"
        "2026-07-27T02-57-16Z-director2-to-operator2-verify-request.md"
    )
    source_report_path = (
        "coordination/mailbox/sent/"
        "2026-07-27T03-26-01Z-operator2-to-director2-verification-report.md"
    )
    request_path = (
        "coordination/mailbox/sent/"
        "2026-08-03T12-10-00Z-director2-to-operator2-verify-request.md"
    )
    request_body = (clone / source_request_path).read_text(encoding="utf-8").replace(
        "**When:** 2026-07-27T02:57:16Z",
        "**When:** 2026-08-03T12:10:00Z",
        1,
    )
    (clone / request_path).write_text(request_body, encoding="utf-8")
    _git(clone, "add", "-f", request_path)
    _git(clone, "commit", "-q", "-m", "post-cutover request")
    request_commit = _git(clone, "rev-parse", "HEAD")

    report_path = (
        "coordination/mailbox/sent/"
        "2026-08-03T12-20-00Z-operator2-to-director2-verification-report.md"
    )
    report_body = (clone / source_report_path).read_text(encoding="utf-8")
    report_body = report_body.replace(
        "**When:** 2026-07-27T03:26:01Z",
        "**When:** 2026-08-03T12:20:00Z",
        1,
    ).replace(
        f"Verification request: {source_request_path}@"
        "eb05a76f79599b93cbc8dafa0ce1e4a42d6d5e7f",
        f"Verification request: {request_path}@{request_commit}",
        1,
    )
    (clone / report_path).write_text(report_body, encoding="utf-8")
    _git(clone, "add", "-f", report_path)
    _git(clone, "commit", "-q", "-m", "post-cutover fail")
    report_commit = _git(clone, "rev-parse", "HEAD")

    pending_path = (
        "coordination/mailbox/sent/"
        "2026-08-03T12-30-00Z-director2-to-operator2-verify-request.md"
    )
    pending_body = request_body.replace(
        "**When:** 2026-08-03T12:10:00Z",
        "**When:** 2026-08-03T12:30:00Z",
        1,
    )
    (clone / pending_path).write_text(pending_body, encoding="utf-8")
    _git(clone, "add", "-f", pending_path)
    _git(clone, "commit", "-q", "-m", "newer pending request")
    pending_commit = _git(clone, "rev-parse", "HEAD")

    state = cc.inspect_verify_review_state(clone)

    assert state.problem is None
    assert [(item.path, item.commit) for item in state.pending] == [
        (pending_path, pending_commit)
    ]
    assert (request_path, request_commit, report_path, report_commit) in {
        (
            item.request_path,
            item.request_commit,
            item.report_path,
            item.report_commit,
        )
        for item in state.failed
    }
    assert any(item.report_commit == "e0fbefdb56af03b8c04b6df58245f7533a3d83c0" for item in state.failed)


@pytest.mark.parametrize(
    "report_timestamp",
    ("2026-08-03T13-00-00Z", "2026-07-31T08-07-00Z"),
)
def test_post_cutover_fail_for_pre_cutover_request_survives_newer_request(
    repo_root: Path, tmp_path: Path, report_timestamp: str,
) -> None:
    clone = _clone_pre_remediation_review_baseline(
        repo_root, tmp_path, f"report-boundary-{report_timestamp}"
    )
    _git(clone, "config", "user.name", "Coord Test")
    _git(clone, "config", "user.email", "coord@example.invalid")
    request_path = (
        "coordination/mailbox/sent/"
        "2026-07-31T08-05-55Z-director2-to-operator-verify-request.md"
    )
    request_commit = "bc7914bfe0326dea701153fb8fc76af2cf19fd0f"
    source_report_path = (
        "coordination/mailbox/sent/"
        "2026-07-31T08-08-59Z-operator-to-director2-verification-report.md"
    )
    report_path = (
        "coordination/mailbox/sent/"
        f"{report_timestamp}-operator-to-director2-verification-report.md"
    )
    report_when = report_timestamp[:11] + report_timestamp[11:].replace("-", ":")
    report_body = (clone / source_report_path).read_text(encoding="utf-8").replace(
        "**When:** 2026-07-31T08:08:59Z",
        f"**When:** {report_when}",
        1,
    )
    (clone / report_path).write_text(report_body, encoding="utf-8")
    _git(clone, "add", "-f", report_path)
    _git(clone, "commit", "-q", "-m", "post-cutover fail for older request")
    report_commit = _git(clone, "rev-parse", "HEAD")

    source_pending_path = (
        "coordination/mailbox/sent/"
        "2026-07-31T08-11-42Z-director2-to-operator-verify-request.md"
    )
    pending_path = (
        "coordination/mailbox/sent/"
        "2026-08-03T13-10-00Z-director2-to-operator-verify-request.md"
    )
    pending_body = (clone / source_pending_path).read_text(
        encoding="utf-8"
    ).replace(
        "**When:** 2026-07-31T08:11:42Z",
        "**When:** 2026-08-03T13:10:00Z",
        1,
    )
    (clone / pending_path).write_text(pending_body, encoding="utf-8")
    _git(clone, "add", "-f", pending_path)
    _git(clone, "commit", "-q", "-m", "newer request after older-request fail")
    pending_commit = _git(clone, "rev-parse", "HEAD")

    state = cc.inspect_verify_review_state(clone)

    assert state.problem is None
    assert (pending_path, pending_commit) in {
        (item.path, item.commit) for item in state.pending
    }
    assert (request_path, request_commit, report_path, report_commit) in {
        (
            item.request_path,
            item.request_commit,
            item.report_path,
            item.report_commit,
        )
        for item in state.failed
    }
