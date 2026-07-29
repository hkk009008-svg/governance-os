from __future__ import annotations

import subprocess
from collections.abc import Callable
from pathlib import Path

import pytest

import compact_pair_loop as pair


FINDING_A = (
    "coordination/mailbox/sent/"
    "2026-07-18T06-05-32Z-operator-to-director-findings.md@"
    "fedfbe37f042045e844c2a7de90437445ccd6e0e"
)
FINDING_B = (
    "coordination/mailbox/sent/"
    "2026-07-18T04-55-26Z-director2-to-coordinator-findings.md@"
    "6c11193d3ca5eb2a7214147309754241d5b884f3"
)
REQUEST_PATH = (
    "coordination/mailbox/sent/"
    "2026-07-18T08-00-00Z-director-to-operator-verify-request.md"
)
REPORT_PATH = (
    "coordination/mailbox/sent/"
    "2026-07-18T08-10-00Z-operator-to-all-verification-report.md"
)


def _git(root: Path, *args: str) -> str:
    completed = subprocess.run(
        ["env", "-u", "GIT_INDEX_FILE", "git", *args],
        cwd=root,
        check=True,
        capture_output=True,
        text=True,
    )
    return completed.stdout.strip()


def _bullet_section(heading: str, values: tuple[str, ...]) -> str:
    body = "\n".join(f"- {value}" for value in values)
    return f"## {heading}\n\n{body}\n"


def _reviewed_repository_line(value: str | None) -> str:
    return "" if value is None else f"Reviewed repository: {value}\n"


def _request_text(
    base: str,
    head: str,
    *,
    reviewed_repository: str | None = None,
    author_seat: str = "director",
    author_model: str = "gpt-5.6-sol",
    assigned_operator: str = "operator",
    risk_class: str = "material-behavior",
    abuse_class_assessment: tuple[str, ...] = (),
    finding_refs: tuple[str, ...] = (FINDING_A,),
) -> str:
    abuse_assessment = (
        ""
        if not abuse_class_assessment
        else "\n" + _bullet_section("Abuse Class Assessment", abuse_class_assessment)
    )
    return f"""\
# Pair seat -> Operator: verify outcome

**When:** 2026-07-18T08:00:00Z · **From:** {author_seat} (online)

Event type: verify-request
{_reviewed_repository_line(reviewed_repository)}Reviewed head: {head}
Reviewed base: {base}
Author seat: {author_seat}
Author model: {author_model}
Assigned operator: {assigned_operator}
Risk class: {risk_class}

## Outcome

The committed change satisfies the routed maintenance outcome.

{abuse_assessment}
{_bullet_section("Finding Refs", finding_refs)}
Cursor at send: 0
"""


def _report_text(
    base: str,
    head: str,
    trigger: str,
    *,
    reviewed_repository: str | None = None,
    verdict: str = "GO",
    request_path: str = REQUEST_PATH,
    reviewer_seat: str = "operator",
    reviewer_model: str = "gpt-5.6-terra",
    risk_class: str = "material-behavior",
    abuse_class_assessment_binding: str | None = None,
    supersedes: str | None = None,
    finding_refs: tuple[str, ...] = (FINDING_A,),
    dispositions: tuple[tuple[str, str], ...] = ((FINDING_A, "addressed"),),
    evidence: bool = True,
) -> str:
    evidence_block = ""
    if evidence:
        evidence_block = """\

## Evidence

$ independent actual-diff inspection
→ reviewed range satisfies the outcome
"""
    disposition_lines = tuple(f"{ref}: {value}" for ref, value in dispositions)
    abuse_binding = (
        ""
        if abuse_class_assessment_binding is None
        else f"Abuse Class Assessment: {abuse_class_assessment_binding}\n"
    )
    supersedes_line = "" if supersedes is None else f"Supersedes: {supersedes}\n"
    return f"""\
# Operator -> Pair seat: outcome verification

**When:** 2026-07-18T08:10:00Z · **From:** {reviewer_seat} (online)

Event type: verification-report
VERDICT: {verdict}
Verification request: {request_path}@{trigger}
{supersedes_line}{_reviewed_repository_line(reviewed_repository)}Reviewed head: {head}
Reviewed base: {base}
Reviewer seat: {reviewer_seat}
Reviewer model: {reviewer_model}
Risk class: {risk_class}
{abuse_binding}

{_bullet_section("Finding Refs", finding_refs)}
{_bullet_section("Finding Dispositions", disposition_lines)}
{evidence_block}

## Findings

None.

Cursor at send: 0
"""


def _repo(
    tmp_path: Path,
    *,
    request_path: str = REQUEST_PATH,
    author_seat: str = "director",
    author_model: str = "gpt-5.6-sol",
    assigned_operator: str = "operator",
    risk_class: str = "material-behavior",
    abuse_class_assessment: tuple[str, ...] = (),
    finding_refs: tuple[str, ...] = (FINDING_A,),
    transform_request=lambda text: text,
) -> tuple[Path, str, str, str]:
    root = tmp_path / "repo"
    root.mkdir()
    (root / "scripts").mkdir()
    (root / "scripts/feature.py").write_text("VALUE = 1\n", encoding="utf-8")
    _git(root, "init", "-q")
    _git(root, "config", "user.name", "Compact Pair Test")
    _git(root, "config", "user.email", "compact-pair@example.invalid")
    _git(root, "add", ".")
    _git(root, "commit", "-q", "-m", "chore: base")
    base = _git(root, "rev-parse", "HEAD")

    (root / "scripts/feature.py").write_text("VALUE = 2\n", encoding="utf-8")
    _git(root, "add", "scripts/feature.py")
    _git(root, "commit", "-q", "-m", "feat: candidate")
    head = _git(root, "rev-parse", "HEAD")

    request = root / request_path
    request.parent.mkdir(parents=True)
    request.write_text(
        transform_request(
            _request_text(
                base,
                head,
                author_seat=author_seat,
                author_model=author_model,
                assigned_operator=assigned_operator,
                risk_class=risk_class,
                abuse_class_assessment=abuse_class_assessment,
                finding_refs=finding_refs,
            )
        ),
        encoding="utf-8",
    )
    _git(root, "add", request_path)
    _git(root, "commit", "-q", "-m", "coord(pair): request verification")
    return root, base, head, _git(root, "rev-parse", "HEAD")


def _write_report(
    root: Path,
    base: str,
    head: str,
    trigger: str,
    *,
    report_path: str = REPORT_PATH,
    **overrides: object,
) -> Path:
    report = root / report_path
    report.write_text(
        _report_text(base, head, trigger, **overrides),
        encoding="utf-8",
    )
    return report


def test_verify_request_candidate_uses_intended_final_path_as_identity(
    tmp_path: Path,
) -> None:
    root, base, head, _trigger = _repo(tmp_path)
    candidate = root / "coordination/mailbox/sent/.request-candidate.tmp"
    candidate.write_text(_request_text(base, head), encoding="utf-8")

    request = pair.parse_verify_request_candidate(root, candidate, REQUEST_PATH)

    assert request.path == REQUEST_PATH
    assert request.trigger_commit == ""
    assert request.author_seat == "director"
    assert request.assigned_operator == "operator"
    assert request.risk_class == "material-behavior"


@pytest.mark.parametrize("risk_class", ("ordinary-local", "external-effect", "invented"))
def test_new_verify_request_candidate_rejects_nonformal_risk_classes(
    tmp_path: Path, risk_class: str
) -> None:
    root, base, head, _trigger = _repo(tmp_path)
    candidate = root / "coordination/mailbox/sent/.request-candidate.tmp"
    candidate.write_text(
        _request_text(base, head, risk_class=risk_class), encoding="utf-8"
    )

    with pytest.raises(pair.CompactPairError, match="Risk class must be"):
        pair.parse_verify_request_candidate(root, candidate, REQUEST_PATH)


def test_new_verify_request_candidate_requires_explicit_risk_class(
    tmp_path: Path,
) -> None:
    root, base, head, _trigger = _repo(tmp_path)
    candidate = root / "coordination/mailbox/sent/.request-candidate.tmp"
    candidate.write_text(
        _request_text(base, head).replace("Risk class: material-behavior\n", ""),
        encoding="utf-8",
    )

    with pytest.raises(pair.CompactPairError, match="missing Risk class"):
        pair.parse_verify_request_candidate(root, candidate, REQUEST_PATH)


def test_high_risk_request_requires_abuse_assessment_and_report_binds_it(
    tmp_path: Path,
) -> None:
    root, base, head, trigger = _repo(
        tmp_path,
        risk_class="high-risk-control",
        abuse_class_assessment=("untrusted request fields cannot widen authority",),
    )
    candidate = root / "coordination/mailbox/sent/.report-candidate.tmp"
    candidate.write_text(
        _report_text(
            base,
            head,
            trigger,
            # A declared high-risk-control artifact needs a genuinely distinct
            # model family; the fixture default shares the author's.
            reviewer_model="claude-opus-5",
            risk_class="high-risk-control",
            abuse_class_assessment_binding="bound-to-request",
        ),
        encoding="utf-8",
    )

    report = pair.parse_verification_report_candidate(root, candidate, REPORT_PATH)

    assert report.risk_class == "high-risk-control"
    assert pair.validate_report(root, report) == []


def test_high_risk_candidate_rejects_missing_assessment_or_report_binding(
    tmp_path: Path,
) -> None:
    root, base, head, _trigger = _repo(tmp_path)
    request_candidate = root / "coordination/mailbox/sent/.request-candidate.tmp"
    request_candidate.write_text(
        _request_text(base, head, risk_class="high-risk-control"), encoding="utf-8"
    )
    with pytest.raises(pair.CompactPairError, match="Abuse Class Assessment"):
        pair.parse_verify_request_candidate(root, request_candidate, REQUEST_PATH)

    second_tmp = tmp_path / "bound"
    second_tmp.mkdir()
    root, base, head, trigger = _repo(
        second_tmp,
        risk_class="high-risk-control",
        abuse_class_assessment=("untrusted request fields cannot widen authority",),
    )
    report_candidate = root / "coordination/mailbox/sent/.report-candidate.tmp"
    report_candidate.write_text(
        _report_text(base, head, trigger, risk_class="high-risk-control"),
        encoding="utf-8",
    )
    with pytest.raises(pair.CompactPairError, match="bind Abuse Class Assessment"):
        pair.parse_verification_report_candidate(root, report_candidate, REPORT_PATH)


def test_report_candidate_requires_matching_explicit_risk_class(tmp_path: Path) -> None:
    root, base, head, trigger = _repo(tmp_path)
    candidate = root / "coordination/mailbox/sent/.report-candidate.tmp"
    candidate.write_text(
        _report_text(base, head, trigger).replace("Risk class: material-behavior\n", ""),
        encoding="utf-8",
    )
    with pytest.raises(pair.CompactPairError, match="missing Risk class"):
        pair.parse_verification_report_candidate(root, candidate, REPORT_PATH)

    candidate.write_text(
        _report_text(base, head, trigger, risk_class="high-risk-control", abuse_class_assessment_binding="bound-to-request"),
        encoding="utf-8",
    )
    report = pair.parse_verification_report_candidate(root, candidate, REPORT_PATH)

    assert "report Risk class does not match request" in pair.validate_report(root, report)


def test_verify_request_candidate_rejects_non_pair_author_path(
    tmp_path: Path,
) -> None:
    root, base, head, _trigger = _repo(tmp_path)
    candidate = root / "coordination/mailbox/sent/.request-candidate.tmp"
    candidate.write_text(
        _request_text(base, head, author_seat="coordinator"),
        encoding="utf-8",
    )
    coordinator_path = (
        "coordination/mailbox/sent/"
        "2026-07-18T08-00-00Z-coordinator-to-operator-verify-request.md"
    )

    with pytest.raises(pair.CompactPairError, match="path is not canonical"):
        pair.parse_verify_request_candidate(root, candidate, coordinator_path)


_DEFAULT_REPOSITORY = object()


def _cross_repo(
    tmp_path: Path,
    *,
    repository_value: object = _DEFAULT_REPOSITORY,
    transform_request: Callable[[str], str] = lambda text: text,
    range_values: Callable[[str, str], tuple[str, str]] = lambda base, head: (
        base,
        head,
    ),
) -> tuple[Path, Path, str, str, str]:
    pipeline = tmp_path / "pipeline"
    pipeline.mkdir()
    _git(pipeline, "init", "-q")
    _git(pipeline, "config", "user.name", "Compact Pair Test")
    _git(pipeline, "config", "user.email", "compact-pair@example.invalid")
    (pipeline / "README.md").write_text("pipeline\n", encoding="utf-8")
    _git(pipeline, "add", ".")
    _git(pipeline, "commit", "-q", "-m", "chore: pipeline base")

    target = tmp_path / "target"
    target.mkdir()
    _git(target, "init", "-q")
    _git(target, "config", "user.name", "Compact Pair Test")
    _git(target, "config", "user.email", "compact-pair@example.invalid")
    (target / "feature.py").write_text("VALUE = 1\n", encoding="utf-8")
    _git(target, "add", ".")
    _git(target, "commit", "-q", "-m", "chore: target base")
    base = _git(target, "rev-parse", "HEAD")
    (target / "feature.py").write_text("VALUE = 2\n", encoding="utf-8")
    _git(target, "add", "feature.py")
    _git(target, "commit", "-q", "-m", "feat: target candidate")
    head = _git(target, "rev-parse", "HEAD")

    if repository_value is _DEFAULT_REPOSITORY:
        reviewed_repository: str | None = target.as_posix()
    elif callable(repository_value):
        reviewed_repository = repository_value(target)
    else:
        assert repository_value is None or isinstance(repository_value, str)
        reviewed_repository = repository_value
    reviewed_base, reviewed_head = range_values(base, head)

    request = pipeline / REQUEST_PATH
    request.parent.mkdir(parents=True)
    request.write_text(
        transform_request(
            _request_text(
                reviewed_base,
                reviewed_head,
                reviewed_repository=reviewed_repository,
            )
        ),
        encoding="utf-8",
    )
    _git(pipeline, "add", REQUEST_PATH)
    _git(pipeline, "commit", "-q", "-m", "coord: request target review")
    return pipeline, target, base, head, _git(pipeline, "rev-parse", "HEAD")


def test_cross_repository_request_and_report_bind_exact_target_range(
    tmp_path: Path,
) -> None:
    root, target, base, head, trigger = _cross_repo(tmp_path)
    request = pair.parse_verify_request(root, REQUEST_PATH, trigger)
    report = pair.parse_verification_report(
        root,
        _write_report(
            root,
            base,
            head,
            trigger,
            reviewed_repository=target.as_posix(),
        ),
    )

    assert request.reviewed_repository == target.as_posix()
    assert report.reviewed_repository == target.as_posix()
    assert pair.validate_report(root, report) == []


def test_target_commits_without_reviewed_repository_fail_in_pipeline(
    tmp_path: Path,
) -> None:
    root, _target, _base, _head, trigger = _cross_repo(
        tmp_path, repository_value=None
    )

    with pytest.raises(
        pair.CompactPairError, match="Git commit or path validation failed"
    ):
        pair.parse_verify_request(root, REQUEST_PATH, trigger)


# An absolute path belonging to some other machine. It must not exist here.
MISSING_AUTHORING_PATH = "/definitely/missing/compact-pair-target"


@pytest.mark.parametrize(
    ("repository_value", "message"),
    (
        ("target", "absolute"),
        ("/tmp/../tmp/target", "normalized"),
        # A path that is merely absent here is no longer rejected for being
        # absent: it degrades to the local root, exactly as an omitted field
        # does. The rejection moves to the range instead, which is the stricter
        # question — these fixtures keep the reviewed commits in the target
        # repository, so they do not resolve locally and the pair still fails.
        (MISSING_AUTHORING_PATH, "Git commit or path validation failed"),
    ),
)
def test_reviewed_repository_rejects_noncanonical_paths_and_unresolvable_ranges(
    tmp_path: Path, repository_value: str, message: str
) -> None:
    root, _target, _base, _head, trigger = _cross_repo(
        tmp_path, repository_value=repository_value
    )

    with pytest.raises(pair.CompactPairError, match=message):
        pair.parse_verify_request(root, REQUEST_PATH, trigger)


def test_reviewed_repository_absent_here_validates_against_the_local_root(
    tmp_path: Path,
) -> None:
    """The CI case: the recorded checkout is gone but the range is right here.

    Every event records the absolute path the review ran at, so on a runner or
    a fresh clone that path is missing while the reviewed commits are present.
    The pair must still validate, or the gate can only ever pass on the one
    machine that wrote it.
    """
    assert not Path(MISSING_AUTHORING_PATH).exists()
    root, base, head, trigger = _repo(
        tmp_path,
        transform_request=lambda text: text.replace(
            "Event type: verify-request\n",
            f"Event type: verify-request\nReviewed repository: {MISSING_AUTHORING_PATH}\n",
        ),
    )

    request = pair.parse_verify_request(root, REQUEST_PATH, trigger)

    assert request.reviewed_repository == MISSING_AUTHORING_PATH
    assert (request.reviewed_base, request.reviewed_head) == (base, head)


@pytest.mark.parametrize(
    ("case", "message"),
    (("symlink", "symlink"), ("nested", "Git worktree root")),
)
def test_reviewed_repository_rejects_symlink_and_nested_worktree_path(
    tmp_path: Path, case: str, message: str
) -> None:
    def invalid_repository(target: Path) -> str:
        if case == "symlink":
            link = target.parent / "target-link"
            link.symlink_to(target, target_is_directory=True)
            return link.as_posix()
        nested = target / "nested"
        nested.mkdir()
        return nested.as_posix()

    root, _target, _base, _head, trigger = _cross_repo(
        tmp_path, repository_value=invalid_repository
    )

    with pytest.raises(pair.CompactPairError, match=message):
        pair.parse_verify_request(root, REQUEST_PATH, trigger)


@pytest.mark.parametrize(
    "duplicate",
    (
        "Reviewed repository:\n",
        " Reviewed repository :   \n",
        "reviewed REPOSITORY: spoofed\n",
    ),
)
def test_reviewed_repository_rejects_blank_malformed_or_duplicate_header(
    tmp_path: Path, duplicate: str
) -> None:
    root, _target, _base, _head, trigger = _cross_repo(
        tmp_path,
        transform_request=lambda text: text.replace(
            "Reviewed repository: ", duplicate + "Reviewed repository: ", 1
        ),
    )

    with pytest.raises(pair.CompactPairError, match="Reviewed repository"):
        pair.parse_verify_request(root, REQUEST_PATH, trigger)


@pytest.mark.parametrize("report_repository", (None, "/tmp/different-target"))
def test_report_cannot_omit_or_substitute_request_repository(
    tmp_path: Path, report_repository: str | None
) -> None:
    root, _target, base, head, trigger = _cross_repo(tmp_path)
    report = pair.parse_verification_report(
        root,
        _write_report(
            root,
            base,
            head,
            trigger,
            reviewed_repository=report_repository,
        ),
    )
    violations = pair.validate_report(root, report)
    assert any("Reviewed repository" in item for item in violations)


def test_report_cannot_add_repository_to_pipeline_local_request(
    tmp_path: Path,
) -> None:
    root, base, head, trigger = _repo(tmp_path)
    report = pair.parse_verification_report(
        root,
        _write_report(
            root,
            base,
            head,
            trigger,
            reviewed_repository=root.as_posix(),
        ),
    )
    assert any(
        "Reviewed repository" in item for item in pair.validate_report(root, report)
    )


def test_report_rejects_duplicate_reviewed_repository_header(tmp_path: Path) -> None:
    root, target, base, head, trigger = _cross_repo(tmp_path)
    report_path = _write_report(
        root,
        base,
        head,
        trigger,
        reviewed_repository=target.as_posix(),
    )
    text = report_path.read_text(encoding="utf-8")
    report_path.write_text(
        text.replace(
            "Reviewed repository: ",
            "Reviewed repository:\nReviewed repository: ",
            1,
        ),
        encoding="utf-8",
    )
    with pytest.raises(pair.CompactPairError, match="Reviewed repository"):
        pair.parse_verification_report(root, report_path)


def test_request_bound_repository_must_remain_available_for_report(
    tmp_path: Path,
) -> None:
    root, target, base, head, trigger = _cross_repo(tmp_path)
    report = pair.parse_verification_report(
        root,
        _write_report(
            root,
            base,
            head,
            trigger,
            reviewed_repository=target.as_posix(),
        ),
    )
    target.rename(tmp_path / "moved-target")
    assert any(
        "request binding invalid" in item
        for item in pair.validate_report(root, report)
    )


@pytest.mark.parametrize(
    ("case", "message"),
    (
        ("equal", "strict ancestor"),
        ("reversed", "strict ancestor"),
        ("missing", "Git commit or path validation failed"),
    ),
)
def test_cross_repository_range_fails_closed(
    tmp_path: Path, case: str, message: str
) -> None:
    def invalid_range(base: str, head: str) -> tuple[str, str]:
        if case == "equal":
            return base, base
        if case == "reversed":
            return head, base
        return base, "f" * 40

    root, _target, _base, _head, trigger = _cross_repo(
        tmp_path, range_values=invalid_range
    )

    with pytest.raises(pair.CompactPairError, match=message):
        pair.parse_verify_request(root, REQUEST_PATH, trigger)


def test_cross_repository_merge_base_error_fails_closed(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    root, _target, _base, _head, trigger = _cross_repo(tmp_path)
    real_run = pair.subprocess.run

    def fail_merge_base(*args, **kwargs):
        command = args[0]
        if "merge-base" in command and "--is-ancestor" in command:
            return subprocess.CompletedProcess(command, 2, b"", b"fatal")
        return real_run(*args, **kwargs)

    monkeypatch.setattr(pair.subprocess, "run", fail_merge_base)
    with pytest.raises(pair.CompactPairError, match="Git ancestry validation failed"):
        pair.parse_verify_request(root, REQUEST_PATH, trigger)


def test_minimal_request_and_report_bind_range_identity_outcome_and_findings(
    tmp_path: Path,
) -> None:
    root, base, head, trigger = _repo(tmp_path)
    request = pair.parse_verify_request(root, REQUEST_PATH, trigger)
    report = pair.parse_verification_report(
        root, _write_report(root, base, head, trigger)
    )

    assert request.reviewed_base == base
    assert request.reviewed_head == head
    assert request.outcome == "The committed change satisfies the routed maintenance outcome."
    assert request.finding_refs == (FINDING_A,)
    assert report.evidence
    assert report.finding_refs == request.finding_refs
    assert report.finding_dispositions == ((FINDING_A, "addressed"),)
    assert pair.validate_report(root, report) == []


def test_operator_can_author_request_for_distinct_operator2_reviewer(
    tmp_path: Path,
) -> None:
    request_path = REQUEST_PATH.replace("director-to-operator", "operator-to-operator2")
    report_path = REPORT_PATH.replace("operator-to-all", "operator2-to-operator")
    root, base, head, trigger = _repo(
        tmp_path,
        request_path=request_path,
        author_seat="operator",
        assigned_operator="operator2",
    )
    report = pair.parse_verification_report(
        root,
        _write_report(
            root,
            base,
            head,
            trigger,
            report_path=report_path,
            request_path=request_path,
            reviewer_seat="operator2",
        ),
    )

    assert pair.validate_report(root, report) == []


@pytest.mark.parametrize("label", ("Author model", "Reviewer model"))
@pytest.mark.parametrize("replacement", ("", "   "))
def test_system_visible_model_fields_must_be_nonblank(
    tmp_path: Path, label: str, replacement: str
) -> None:
    if label == "Author model":
        root, _, _, trigger = _repo(
            tmp_path,
            transform_request=lambda text: text.replace(
                "Author model: gpt-5.6-sol", f"Author model: {replacement}"
            ),
        )
        with pytest.raises(pair.CompactPairError, match="Author model"):
            pair.parse_verify_request(root, REQUEST_PATH, trigger)
    else:
        root, base, head, trigger = _repo(tmp_path)
        with pytest.raises(pair.CompactPairError, match="Reviewer model"):
            pair.parse_verification_report(
                root,
                _write_report(
                    root, base, head, trigger, reviewer_model=replacement
                ),
            )


@pytest.mark.parametrize("label", ("Author model", "Reviewer model"))
def test_system_visible_model_fields_cannot_be_omitted(
    tmp_path: Path, label: str
) -> None:
    if label == "Author model":
        root, _, _, trigger = _repo(
            tmp_path,
            transform_request=lambda text: text.replace(
                "Author model: gpt-5.6-sol\n", ""
            ),
        )
        with pytest.raises(pair.CompactPairError, match="Author model"):
            pair.parse_verify_request(root, REQUEST_PATH, trigger)
    else:
        root, base, head, trigger = _repo(tmp_path)
        report_path = _write_report(root, base, head, trigger)
        report_path.write_text(
            report_path.read_text(encoding="utf-8").replace(
                "Reviewer model: gpt-5.6-terra\n", ""
            ),
            encoding="utf-8",
        )
        with pytest.raises(pair.CompactPairError, match="Reviewer model"):
            pair.parse_verification_report(root, report_path)


@pytest.mark.parametrize(
    "duplicate",
    (
        "Reviewer model:\n",
        " Reviewer model :   \n",
        "reviewer MODEL: spoofed\n",
    ),
)
def test_reviewer_model_rejects_blank_malformed_or_whitespace_duplicate(
    tmp_path: Path, duplicate: str
) -> None:
    root, base, head, trigger = _repo(tmp_path)
    report_path = _write_report(root, base, head, trigger)
    report_path.write_text(
        report_path.read_text(encoding="utf-8").replace(
            "Reviewer model: gpt-5.6-terra\n",
            duplicate + "Reviewer model: gpt-5.6-terra\n",
        ),
        encoding="utf-8",
    )

    with pytest.raises(pair.CompactPairError, match="Reviewer model"):
        pair.parse_verification_report(root, report_path)


@pytest.mark.parametrize(
    "duplicate",
    (
        "Author model:\n",
        " Author model :   \n",
        "author MODEL: spoofed\n",
    ),
)
def test_author_model_rejects_blank_malformed_or_whitespace_duplicate(
    tmp_path: Path, duplicate: str
) -> None:
    root, _, _, trigger = _repo(
        tmp_path,
        transform_request=lambda text: text.replace(
            "Author model: gpt-5.6-sol\n",
            duplicate + "Author model: gpt-5.6-sol\n",
        ),
    )

    with pytest.raises(pair.CompactPairError, match="Author model"):
        pair.parse_verify_request(root, REQUEST_PATH, trigger)


@pytest.mark.parametrize(
    ("heading", "duplicate"),
    (
        ("Finding Refs", "## Finding Refs \n"),
        ("Finding Refs", "### finding refs\n"),
        ("Finding Dispositions", " ## FINDING   DISPOSITIONS : \n"),
    ),
)
def test_finding_sections_reject_normalized_or_malformed_duplicate_headings(
    tmp_path: Path, heading: str, duplicate: str
) -> None:
    root, base, head, trigger = _repo(tmp_path)
    report_path = _write_report(root, base, head, trigger)
    report_path.write_text(
        report_path.read_text(encoding="utf-8").replace(
            f"## {heading}\n", duplicate + f"## {heading}\n"
        ),
        encoding="utf-8",
    )

    with pytest.raises(pair.CompactPairError, match=heading):
        pair.parse_verification_report(root, report_path)


def test_explicit_empty_finding_ref_sections_are_valid(tmp_path: Path) -> None:
    root, base, head, trigger = _repo(tmp_path, finding_refs=())
    report = pair.parse_verification_report(
        root,
        _write_report(
            root,
            base,
            head,
            trigger,
            finding_refs=(),
            dispositions=(),
        ),
    )

    assert report.finding_refs == ()
    assert report.finding_dispositions == ()
    assert pair.validate_report(root, report) == []


def test_same_seat_cannot_approve_its_own_work(tmp_path: Path) -> None:
    request_path = REQUEST_PATH.replace("director-to-operator", "operator-to-operator")
    root, base, head, trigger = _repo(
        tmp_path,
        request_path=request_path,
        author_seat="operator",
        assigned_operator="operator",
    )
    report = pair.parse_verification_report(
        root,
        _write_report(root, base, head, trigger, request_path=request_path),
    )

    assert "reviewer seat equals author seat" in pair.validate_report(root, report)


def test_same_model_across_operator_seats_is_not_independent(tmp_path: Path) -> None:
    request_path = REQUEST_PATH.replace("director-to-operator", "operator-to-operator2")
    report_path = REPORT_PATH.replace("operator-to-all", "operator2-to-operator")
    root, base, head, trigger = _repo(
        tmp_path,
        request_path=request_path,
        author_seat="operator",
        author_model="GPT-5.6-SOL",
        assigned_operator="operator2",
        risk_class="high-risk-control",
        abuse_class_assessment=("untrusted request fields cannot widen authority",),
    )
    report = pair.parse_verification_report(
        root,
        _write_report(
            root,
            base,
            head,
            trigger,
            report_path=report_path,
            request_path=request_path,
            reviewer_seat="operator2",
            reviewer_model="gpt-5.6-sol",
            risk_class="high-risk-control",
            abuse_class_assessment_binding="bound-to-request",
        ),
    )

    assert "reviewer model shares the author model family" in pair.validate_report(
        root, report
    )


@pytest.mark.parametrize(
    ("author_model", "reviewer_model"),
    (
        # Every pair below was accepted by the previous casefolded string
        # inequality. The first is the dominant pairing in the committed
        # corpus: 84 `gpt-5.6-sol` authors against 65 `gpt-5.6-terra`
        # reviewers, i.e. one model family reviewing itself.
        ("gpt-5.6-sol", "gpt-5.6-terra"),
        ("gpt-5.6-terra", "codex-gpt-5.6-terra"),
        ("gpt-5.6-sol", "GPT-5 Codex"),
        ("antigravity-gemini-3.6", "gemini-3.6-flash"),
        ("claude-opus-5", "claude-sonnet-5"),
    ),
)
def test_high_risk_control_rejects_same_family_reviewer(
    tmp_path: Path, author_model: str, reviewer_model: str
) -> None:
    """A harness prefix or version suffix must not buy model independence."""
    request_path = REQUEST_PATH.replace("director-to-operator", "operator-to-operator2")
    report_path = REPORT_PATH.replace("operator-to-all", "operator2-to-operator")
    root, base, head, trigger = _repo(
        tmp_path,
        request_path=request_path,
        author_seat="operator",
        author_model=author_model,
        assigned_operator="operator2",
        risk_class="high-risk-control",
        abuse_class_assessment=("untrusted request fields cannot widen authority",),
    )
    report = pair.parse_verification_report(
        root,
        _write_report(
            root,
            base,
            head,
            trigger,
            report_path=report_path,
            request_path=request_path,
            reviewer_seat="operator2",
            reviewer_model=reviewer_model,
            risk_class="high-risk-control",
            abuse_class_assessment_binding="bound-to-request",
        ),
    )

    assert "reviewer model shares the author model family" in pair.validate_report(
        root, report
    )


@pytest.mark.parametrize(
    ("author_model", "reviewer_model"),
    (
        ("gpt-5.6-sol", "claude-opus-5"),
        ("gpt-5.6-sol", "antigravity-gemini-3.6"),
        ("claude-opus-5", "gpt-5.6-terra"),
        ("grok-4.5", "composer-2.5"),
    ),
)
def test_high_risk_control_accepts_distinct_family_reviewer(
    tmp_path: Path, author_model: str, reviewer_model: str
) -> None:
    """Genuinely distinct families must still pass; the fix is not a blanket deny."""
    request_path = REQUEST_PATH.replace("director-to-operator", "operator-to-operator2")
    report_path = REPORT_PATH.replace("operator-to-all", "operator2-to-operator")
    root, base, head, trigger = _repo(
        tmp_path,
        request_path=request_path,
        author_seat="operator",
        author_model=author_model,
        assigned_operator="operator2",
        risk_class="high-risk-control",
        abuse_class_assessment=("untrusted request fields cannot widen authority",),
    )
    report = pair.parse_verification_report(
        root,
        _write_report(
            root,
            base,
            head,
            trigger,
            report_path=report_path,
            request_path=request_path,
            reviewer_seat="operator2",
            reviewer_model=reviewer_model,
            risk_class="high-risk-control",
            abuse_class_assessment_binding="bound-to-request",
        ),
    )

    assert not [
        violation
        for violation in pair.validate_report(root, report)
        if "model family" in violation
    ]


def test_material_behavior_permits_same_model_for_non_author_reviewer(
    tmp_path: Path,
) -> None:
    request_path = REQUEST_PATH.replace("director-to-operator", "operator-to-operator2")
    report_path = REPORT_PATH.replace("operator-to-all", "operator2-to-operator")
    root, base, head, trigger = _repo(
        tmp_path,
        request_path=request_path,
        author_seat="operator",
        author_model="GPT-5.6-SOL",
        assigned_operator="operator2",
    )
    report = pair.parse_verification_report(
        root,
        _write_report(
            root,
            base,
            head,
            trigger,
            report_path=report_path,
            request_path=request_path,
            reviewer_seat="operator2",
            reviewer_model="gpt-5.6-sol",
        ),
    )

    assert pair.validate_report(root, report) == []


@pytest.mark.parametrize(
    ("finding_refs", "dispositions", "expected"),
    (
        ((), (), "finding refs changed"),
        ((FINDING_A, FINDING_A), ((FINDING_A, "addressed"),), "unique"),
        (
            (FINDING_B, FINDING_A),
            ((FINDING_B, "addressed"), (FINDING_A, "addressed")),
            "finding refs changed",
        ),
    ),
)
def test_report_cannot_drop_duplicate_or_reorder_finding_refs(
    tmp_path: Path,
    finding_refs: tuple[str, ...],
    dispositions: tuple[tuple[str, str], ...],
    expected: str,
) -> None:
    root, base, head, trigger = _repo(
        tmp_path, finding_refs=(FINDING_A, FINDING_B)
    )
    report_path = _write_report(
        root,
        base,
        head,
        trigger,
        finding_refs=finding_refs,
        dispositions=dispositions,
    )
    if expected == "unique":
        with pytest.raises(pair.CompactPairError, match=expected):
            pair.parse_verification_report(root, report_path)
    else:
        report = pair.parse_verification_report(root, report_path)
        assert any(expected in item for item in pair.validate_report(root, report))


def test_report_requires_exactly_one_disposition_for_each_ref(tmp_path: Path) -> None:
    root, base, head, trigger = _repo(
        tmp_path, finding_refs=(FINDING_A, FINDING_B)
    )
    report_path = _write_report(
        root,
        base,
        head,
        trigger,
        finding_refs=(FINDING_A, FINDING_B),
        dispositions=((FINDING_A, "addressed"),),
    )

    with pytest.raises(pair.CompactPairError, match="exactly one disposition"):
        pair.parse_verification_report(root, report_path)


def test_new_report_cannot_omit_finding_disposition_section(tmp_path: Path) -> None:
    root, base, head, trigger = _repo(tmp_path)
    report_path = _write_report(root, base, head, trigger)
    text = report_path.read_text(encoding="utf-8")
    disposition_section = _bullet_section(
        "Finding Dispositions", (f"{FINDING_A}: addressed",)
    )
    report_path.write_text(text.replace(disposition_section, ""), encoding="utf-8")

    with pytest.raises(pair.CompactPairError, match="Finding Dispositions"):
        pair.parse_verification_report(root, report_path)


def test_go_requires_evidence_and_resolved_hard_boundaries(tmp_path: Path) -> None:
    root, base, head, trigger = _repo(tmp_path)
    no_evidence = pair.parse_verification_report(
        root, _write_report(root, base, head, trigger, evidence=False)
    )
    unresolved = pair.parse_verification_report(
        root,
        _write_report(
            root,
            base,
            head,
            trigger,
            dispositions=((FINDING_A, "unresolved-hard-boundary"),),
        ),
    )

    assert "GO requires evidence" in pair.validate_report(root, no_evidence)
    assert "GO cannot carry unresolved hard-boundary findings" in pair.validate_report(
        root, unresolved
    )


def test_go_evidence_requires_observation_and_result_lines(tmp_path: Path) -> None:
    root, base, head, trigger = _repo(tmp_path)
    report_path = _write_report(root, base, head, trigger)
    text = report_path.read_text(encoding="utf-8")
    text = text.replace(
        "$ independent actual-diff inspection\n→ reviewed range satisfies the outcome",
        "Reviewed it.",
    )
    report_path.write_text(text, encoding="utf-8")
    report = pair.parse_verification_report(root, report_path)

    assert "GO requires evidence" in pair.validate_report(root, report)


def test_go_evidence_rejects_bare_command_and_result_markers(tmp_path: Path) -> None:
    root, base, head, trigger = _repo(tmp_path)
    report_path = _write_report(root, base, head, trigger)
    text = report_path.read_text(encoding="utf-8")
    text = text.replace(
        "$ independent actual-diff inspection\n→ reviewed range satisfies the outcome",
        "$ \n→ ",
    )
    report_path.write_text(text, encoding="utf-8")
    report = pair.parse_verification_report(root, report_path)

    assert "GO requires evidence" in pair.validate_report(root, report)


@pytest.mark.parametrize("verdict", ("NITS", "FAIL"))
def test_truthful_non_go_preserves_findings_without_success_evidence(
    tmp_path: Path, verdict: str
) -> None:
    root, base, head, trigger = _repo(tmp_path)
    report = pair.parse_verification_report(
        root,
        _write_report(
            root,
            base,
            head,
            trigger,
            verdict=verdict,
            evidence=False,
            dispositions=((FINDING_A, "unresolved-hard-boundary"),),
        ),
    )

    assert pair.validate_report(root, report) == []


def test_report_rejects_wrong_assignment_request_and_range(tmp_path: Path) -> None:
    root, base, head, trigger = _repo(tmp_path)
    wrong_assignment = pair.parse_verification_report(
        root,
        _write_report(
            root,
            base,
            head,
            trigger,
            report_path=REPORT_PATH.replace("operator-to-all", "operator2-to-all"),
            reviewer_seat="operator2",
        ),
    )
    wrong_range = pair.parse_verification_report(
        root, _write_report(root, base, base, trigger)
    )

    assert any("assigned Operator" in item for item in pair.validate_report(root, wrong_assignment))
    assert any("Reviewed head" in item for item in pair.validate_report(root, wrong_range))


def test_request_requires_exact_committed_path_and_strict_range(tmp_path: Path) -> None:
    root, _, head, trigger = _repo(tmp_path)
    request = pair.parse_verify_request(root, REQUEST_PATH, trigger)
    assert request.trigger_commit == trigger
    with pytest.raises(pair.CompactPairError, match="added by trigger commit"):
        pair.parse_verify_request(root, REQUEST_PATH, head)


def test_report_parser_accepts_only_operator_output_paths(tmp_path: Path) -> None:
    root, base, head, trigger = _repo(tmp_path)
    director_path = REPORT_PATH.replace("-operator-to-", "-director-to-")
    path = root / director_path
    path.write_text(_report_text(base, head, trigger), encoding="utf-8")

    with pytest.raises(pair.CompactPairError, match="canonical Operator"):
        pair.parse_verification_report(root, path)


def test_already_committed_verbose_report_has_narrow_empty_ref_compatibility(
    repo_root: Path,
) -> None:
    path = (
        "coordination/mailbox/sent/"
        "2026-07-17T13-17-10Z-operator-to-director-verification-report.md"
    )
    report = pair.parse_verification_report(repo_root, path)

    assert report.finding_refs == ()
    assert report.finding_dispositions == ()
    assert pair.validate_report(repo_root, report) == []


def test_legacy_compatibility_does_not_accept_mutated_verbose_bytes(
    repo_root: Path,
) -> None:
    path = (
        "coordination/mailbox/sent/"
        "2026-07-17T13-17-10Z-operator-to-director-verification-report.md"
    )
    raw = (repo_root / path).read_bytes().replace(b"VERDICT: GO", b"VERDICT: NITS")

    with pytest.raises(pair.CompactPairError, match="Finding Refs"):
        pair._parse_verification_report_bytes(repo_root, path, raw)


def test_real_verbose_request_retains_empty_ref_compatibility(repo_root: Path) -> None:
    path = (
        "coordination/mailbox/sent/"
        "2026-07-17T09-18-33Z-director-to-operator-verify-request.md"
    )
    trigger = "d62808f62f9e93dbfe8d235db2550749cf94fb6a"

    request = pair.parse_verify_request(repo_root, path, trigger)

    assert request.finding_refs == ()


def test_recommitted_identical_verbose_request_loses_legacy_compatibility(
    tmp_path: Path, repo_root: Path
) -> None:
    clone = tmp_path / "clone"
    subprocess.run(
        ["git", "clone", "-q", "--no-hardlinks", str(repo_root), str(clone)],
        check=True,
    )
    _git(clone, "config", "user.name", "Compact Pair Test")
    _git(clone, "config", "user.email", "compact-pair@example.invalid")
    path = (
        "coordination/mailbox/sent/"
        "2026-07-17T09-18-33Z-director-to-operator-verify-request.md"
    )
    raw = (clone / path).read_bytes()
    _git(clone, "rm", "-q", "--", path)
    _git(clone, "commit", "-q", "-m", "test: remove historical request")
    (clone / path).write_bytes(raw)
    _git(clone, "add", "-f", "--", path)
    _git(clone, "commit", "-q", "-m", "test: replay historical request")
    replay_trigger = _git(clone, "rev-parse", "HEAD")

    with pytest.raises(pair.CompactPairError, match="historical provenance"):
        pair.parse_verify_request(clone, path, replay_trigger)


COMPOSED_PATH = (
    "coordination/mailbox/sent/"
    "2026-07-26T08-00-00Z-director-to-operator-verify-request.md"
)


def _compose_repo(tmp_path: Path) -> tuple[Path, str, str]:
    root = tmp_path / "compose"
    root.mkdir()
    (root / "feature.py").write_text("VALUE = 1\n", encoding="utf-8")
    _git(root, "init", "-q")
    _git(root, "config", "user.name", "Compose Test")
    _git(root, "config", "user.email", "compose@example.invalid")
    _git(root, "add", ".")
    _git(root, "commit", "-q", "-m", "chore: base")
    base = _git(root, "rev-parse", "HEAD")

    (root / "feature.py").write_text("VALUE = 2\n", encoding="utf-8")
    _git(root, "add", "feature.py")
    _git(root, "commit", "-q", "-m", "feat: candidate")
    return root, base, _git(root, "rev-parse", "HEAD")


def _publish_as_send_event(root: Path, body: str) -> Path:
    """Wrap a composed body exactly as `coordination/bin/send-event` does."""
    candidate = root / "candidate.tmp"
    candidate.write_text(
        "# Director → Operator: composed request\n\n"
        "**When:** 2026-07-26T08:00:00Z · **From:** director (online)\n\n"
        f"{body}\n\nCursor at send: 0\n",
        encoding="utf-8",
    )
    candidate.chmod(0o600)
    return candidate


def test_composed_request_round_trips_through_the_candidate_parser(
    tmp_path: Path,
) -> None:
    """The composer and the parser must not be able to drift apart.

    Authors previously reconstructed this format by reading
    `_parse_verify_request_bytes` and copying an older event. If a future
    parser change is not mirrored in `compose_request`, this round trip is what
    fails instead of the next author's publication attempt.
    """
    root, base, head = _compose_repo(tmp_path)
    body = pair.compose_request(
        root,
        author_seat="director",
        author_model="claude-opus-5",
        assigned_operator="operator2",
        risk_class="high-risk-control",
        base_rev="HEAD~1",
        head_rev="HEAD",
        outcome="Composed outcome under test.",
        abuse_assessments=("Composer emits a body the parser rejects.",),
        finding_refs=(FINDING_A,),
    )

    candidate = _publish_as_send_event(root, body)
    request = pair.parse_verify_request_candidate(
        root,
        candidate,
        COMPOSED_PATH.replace("-to-operator-", "-to-operator2-"),
    )

    assert request.reviewed_base == base
    assert request.reviewed_head == head
    assert request.author_seat == "director"
    assert request.author_model == "claude-opus-5"
    assert request.assigned_operator == "operator2"
    assert request.risk_class == "high-risk-control"
    assert request.risk_class_explicit is True
    assert request.outcome == "Composed outcome under test."
    assert request.abuse_class_assessment == (
        "Composer emits a body the parser rejects.",
    )
    assert request.finding_refs == (FINDING_A,)
    assert pair.validate_request_candidate(root, request) == []


def test_compose_resolves_revisions_so_authors_never_transcribe_shas(
    tmp_path: Path,
) -> None:
    root, base, head = _compose_repo(tmp_path)
    body = pair.compose_request(
        root,
        author_seat="director",
        author_model="claude-opus-5",
        assigned_operator="operator",
        risk_class="material-behavior",
        base_rev="HEAD~1",
        head_rev="HEAD",
        outcome="Range resolution under test.",
    )

    assert f"Reviewed base: {base}" in body
    assert f"Reviewed head: {head}" in body
    assert "HEAD" not in body
    assert "## Abuse Class Assessment" not in body
    assert "## Finding Refs" not in body


@pytest.mark.parametrize("risk_class", ("ordinary-local", "external-effect", "invented"))
def test_compose_refuses_risk_classes_that_carry_no_formal_review(
    tmp_path: Path, risk_class: str
) -> None:
    root, _, _ = _compose_repo(tmp_path)
    with pytest.raises(pair.CompactPairError, match="Risk class must be"):
        pair.compose_request(
            root,
            author_seat="director",
            author_model="claude-opus-5",
            assigned_operator="operator",
            risk_class=risk_class,
            base_rev="HEAD~1",
            head_rev="HEAD",
            outcome="Rejected risk class.",
        )


@pytest.mark.parametrize(
    ("author", "operator", "expected"),
    (
        ("coordinator", "operator", "Author seat must be"),
        ("director", "director2", "Assigned operator must be"),
    ),
)
def test_compose_refuses_seats_outside_the_pair(
    tmp_path: Path, author: str, operator: str, expected: str
) -> None:
    root, _, _ = _compose_repo(tmp_path)
    with pytest.raises(pair.CompactPairError, match=expected):
        pair.compose_request(
            root,
            author_seat=author,
            author_model="claude-opus-5",
            assigned_operator=operator,
            risk_class="material-behavior",
            base_rev="HEAD~1",
            head_rev="HEAD",
            outcome="Rejected seat.",
        )


def test_compose_refuses_high_risk_without_an_abuse_assessment(
    tmp_path: Path,
) -> None:
    root, _, _ = _compose_repo(tmp_path)
    with pytest.raises(pair.CompactPairError, match="Abuse Class Assessment"):
        pair.compose_request(
            root,
            author_seat="director",
            author_model="claude-opus-5",
            assigned_operator="operator",
            risk_class="high-risk-control",
            base_rev="HEAD~1",
            head_rev="HEAD",
            outcome="Missing assessment.",
        )


@pytest.mark.parametrize(
    ("kwargs", "expected"),
    (
        ({"outcome": "   "}, "Outcome must be nonempty"),
        ({"finding_refs": ("docs/notes.md@abc",)}, "immutable full-SHA"),
        ({"finding_refs": (FINDING_A, FINDING_A)}, "must be unique"),
        ({"base_rev": "HEAD"}, "strict ancestor"),
        ({"base_rev": "--upload-pack=touch"}, "must be one git revision"),
    ),
)
def test_compose_rejects_malformed_inputs_before_emitting_anything(
    tmp_path: Path, kwargs: dict[str, object], expected: str
) -> None:
    """A composer that emitted an invalid body would only move the failure.

    Every rejection here is one the parser would also make; catching it at
    composition means the author never publishes it and never has to burn a
    review round discovering it.
    """
    root, _, _ = _compose_repo(tmp_path)
    arguments: dict[str, object] = {
        "author_seat": "director",
        "author_model": "claude-opus-5",
        "assigned_operator": "operator",
        "risk_class": "material-behavior",
        "base_rev": "HEAD~1",
        "head_rev": "HEAD",
        "outcome": "Rejected input.",
    }
    arguments.update(kwargs)
    with pytest.raises(pair.CompactPairError, match=expected):
        pair.compose_request(root, **arguments)


def test_compose_refuses_a_self_addressed_routing_the_writer_would_reject(
    tmp_path: Path, repo_root: Path
) -> None:
    """Operator-to-itself composed cleanly while being unpublishable.

    `coordination/bin/send-event` refuses a self-addressed event before it
    builds a candidate, so `_compose_self_check` — which simulates the envelope
    rather than invoking the writer — never reached that boundary. Membership
    was checked for each seat independently and equality never was.
    """
    root, _, _ = _compose_repo(tmp_path)
    with pytest.raises(pair.CompactPairError, match="must differ"):
        pair.compose_request(
            root,
            author_seat="operator",
            author_model="gpt-5",
            assigned_operator="operator",
            risk_class="material-behavior",
            base_rev="HEAD~1",
            head_rev="HEAD",
            outcome="Self-addressed routing.",
        )

    writer = (repo_root / "coordination/bin/send-event").read_text(encoding="utf-8")
    assert "refusing self-addressed event" in writer


def test_compose_refuses_a_range_assembled_from_two_repository_states(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A ref that moves between the two resolutions widened the range silently.

    Base and head were resolved in separate Git calls. Moving `HEAD` between
    them produced ends read from different repository states — still a strict
    ancestor pair, so every later check passed while the request bound
    concurrent work its author never reviewed.
    """
    root, base, head = _compose_repo(tmp_path)

    real = pair._resolve_rev
    calls: list[str] = []

    def moving(root_arg: Path, value: str, label: str) -> str:
        calls.append(label)
        resolved = real(root_arg, value, label)
        # Simulate a concurrent commit landing after the first pair is read.
        if len(calls) == 3:
            _git(root, "commit", "-q", "--allow-empty", "-m", "feat: concurrent")
        return resolved

    monkeypatch.setattr(pair, "_resolve_rev", moving)
    with pytest.raises(pair.CompactPairError, match="moved while composing"):
        pair.compose_request(
            root,
            author_seat="director",
            author_model="claude-opus-5",
            assigned_operator="operator",
            risk_class="material-behavior",
            base_rev="HEAD~1",
            head_rev="HEAD",
            outcome="Moving ref under test.",
        )

    # Non-vacuity: the same call with a quiet repository still composes, so the
    # refusal above is the drift check firing rather than the fixture failing.
    monkeypatch.setattr(pair, "_resolve_rev", real)
    body = pair.compose_request(
        root,
        author_seat="director",
        author_model="claude-opus-5",
        assigned_operator="operator",
        risk_class="material-behavior",
        base_rev=base,
        head_rev=head,
        outcome="Quiet repository.",
    )
    assert f"Reviewed base: {base}" in body
    assert f"Reviewed head: {head}" in body


SECOND_REPORT_PATH = (
    "coordination/mailbox/sent/"
    "2026-07-18T08-20-00Z-operator-to-all-verification-report.md"
)
OPERATOR2_REPORT_PATH = (
    "coordination/mailbox/sent/"
    "2026-07-18T08-15-00Z-operator2-to-all-verification-report.md"
)


def _commit_report(
    root: Path,
    base: str,
    head: str,
    trigger: str,
    *,
    report_path: str = REPORT_PATH,
    **overrides: object,
) -> tuple[str, str]:
    _write_report(root, base, head, trigger, report_path=report_path, **overrides)
    _git(root, "add", report_path)
    _git(root, "commit", "-q", "-m", "coord(pair): report verification")
    return report_path, _git(root, "rev-parse", "HEAD")


def test_report_supersedes_round_trip_and_binds(tmp_path: Path) -> None:
    root, base, head, trigger = _repo(tmp_path)
    orphan_path, orphan_commit = _commit_report(root, base, head, trigger)
    reference = f"{orphan_path}@{orphan_commit}"
    candidate = _write_report(
        root, base, head, trigger, report_path=SECOND_REPORT_PATH, supersedes=reference
    )
    report = pair.parse_verification_report_candidate(
        root, str(candidate), SECOND_REPORT_PATH
    )
    assert report.supersedes == (orphan_path, orphan_commit)
    assert pair.validate_report_structure(root, report) == []
    assert pair.validate_report(root, report) == []


def test_report_supersedes_must_name_a_report_path(tmp_path: Path) -> None:
    root, base, head, trigger = _repo(tmp_path)
    candidate = _write_report(
        root,
        base,
        head,
        trigger,
        report_path=SECOND_REPORT_PATH,
        supersedes=f"{REQUEST_PATH}@{trigger}",
    )
    with pytest.raises(pair.CompactPairError, match="not a canonical verification-report"):
        pair.parse_verification_report_candidate(root, str(candidate), SECOND_REPORT_PATH)


def test_report_supersedes_requires_full_sha(tmp_path: Path) -> None:
    root, base, head, trigger = _repo(tmp_path)
    orphan_path, orphan_commit = _commit_report(root, base, head, trigger)
    candidate = _write_report(
        root,
        base,
        head,
        trigger,
        report_path=SECOND_REPORT_PATH,
        supersedes=f"{orphan_path}@{orphan_commit[:12]}",
    )
    with pytest.raises(pair.CompactPairError, match="full lowercase commit SHA"):
        pair.parse_verification_report_candidate(root, str(candidate), SECOND_REPORT_PATH)


def test_report_supersedes_never_names_itself(tmp_path: Path) -> None:
    root, base, head, trigger = _repo(tmp_path)
    candidate = _write_report(
        root,
        base,
        head,
        trigger,
        report_path=SECOND_REPORT_PATH,
        supersedes=f"{SECOND_REPORT_PATH}@{'0' * 40}",
    )
    with pytest.raises(pair.CompactPairError, match="must not name the report itself"):
        pair.parse_verification_report_candidate(root, str(candidate), SECOND_REPORT_PATH)


def test_report_supersedes_duplicate_field_rejected(tmp_path: Path) -> None:
    root, base, head, trigger = _repo(tmp_path)
    orphan_path, orphan_commit = _commit_report(root, base, head, trigger)
    reference = f"{orphan_path}@{orphan_commit}"
    candidate = root / SECOND_REPORT_PATH
    candidate.write_text(
        _report_text(
            base, head, trigger, supersedes=reference
        ).replace(
            f"Supersedes: {reference}",
            f"Supersedes: {reference}\nSupersedes: {reference}",
        ),
        encoding="utf-8",
    )
    with pytest.raises(pair.CompactPairError, match="duplicate Supersedes"):
        pair.parse_verification_report_candidate(root, str(candidate), SECOND_REPORT_PATH)


def test_superseded_commit_must_introduce_the_report(tmp_path: Path) -> None:
    root, base, head, trigger = _repo(tmp_path)
    orphan_path, _ = _commit_report(root, base, head, trigger)
    (root / "scripts/feature.py").write_text("VALUE = 3\n", encoding="utf-8")
    _git(root, "add", "scripts/feature.py")
    _git(root, "commit", "-q", "-m", "feat: unrelated later work")
    wrong_commit = _git(root, "rev-parse", "HEAD")
    candidate = _write_report(
        root,
        base,
        head,
        trigger,
        report_path=SECOND_REPORT_PATH,
        supersedes=f"{orphan_path}@{wrong_commit}",
    )
    report = pair.parse_verification_report_candidate(
        root, str(candidate), SECOND_REPORT_PATH
    )
    violations = pair.validate_report_structure(root, report)
    assert any("introduction commit" in violation for violation in violations)
    # Non-vacuity: the true introduction commit binds cleanly (same fixture).
    correct = _write_report(
        root,
        base,
        head,
        trigger,
        report_path=SECOND_REPORT_PATH,
        supersedes=f"{orphan_path}@{_git(root, 'rev-parse', 'HEAD~1')}",
    )
    correct_report = pair.parse_verification_report_candidate(
        root, str(correct), SECOND_REPORT_PATH
    )
    assert pair.validate_report_structure(root, correct_report) == []


def test_supersession_is_seat_scoped(tmp_path: Path) -> None:
    root, base, head, trigger = _repo(tmp_path)
    orphan_path, orphan_commit = _commit_report(
        root,
        base,
        head,
        trigger,
        report_path=OPERATOR2_REPORT_PATH,
        reviewer_seat="operator2",
    )
    candidate = _write_report(
        root,
        base,
        head,
        trigger,
        report_path=SECOND_REPORT_PATH,
        reviewer_seat="operator",
        supersedes=f"{orphan_path}@{orphan_commit}",
    )
    report = pair.parse_verification_report_candidate(
        root, str(candidate), SECOND_REPORT_PATH
    )
    violations = pair.validate_report_structure(root, report)
    assert any("only its own verdicts" in violation for violation in violations)
    # Non-vacuity: same-seat supersession carries no such violation (the
    # round-trip test asserts the full clean pass on this fixture shape).
