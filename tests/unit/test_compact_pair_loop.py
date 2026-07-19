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
    finding_refs: tuple[str, ...] = (FINDING_A,),
) -> str:
    return f"""\
# Pair seat -> Operator: verify outcome

**When:** 2026-07-18T08:00:00Z · **From:** {author_seat} (online)

Event type: verify-request
{_reviewed_repository_line(reviewed_repository)}Reviewed head: {head}
Reviewed base: {base}
Author seat: {author_seat}
Author model: {author_model}
Assigned operator: {assigned_operator}

## Outcome

The committed change satisfies the routed maintenance outcome.

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
    return f"""\
# Operator -> Pair seat: outcome verification

**When:** 2026-07-18T08:10:00Z · **From:** {reviewer_seat} (online)

Event type: verification-report
VERDICT: {verdict}
Verification request: {request_path}@{trigger}
{_reviewed_repository_line(reviewed_repository)}Reviewed head: {head}
Reviewed base: {base}
Reviewer seat: {reviewer_seat}
Reviewer model: {reviewer_model}

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


@pytest.mark.parametrize(
    ("repository_value", "message"),
    (
        ("target", "absolute"),
        ("/tmp/../tmp/target", "normalized"),
        ("/definitely/missing/compact-pair-target", "repository"),
    ),
)
def test_reviewed_repository_rejects_noncanonical_or_missing_paths(
    tmp_path: Path, repository_value: str, message: str
) -> None:
    root, _target, _base, _head, trigger = _cross_repo(
        tmp_path, repository_value=repository_value
    )

    with pytest.raises(pair.CompactPairError, match=message):
        pair.parse_verify_request(root, REQUEST_PATH, trigger)


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

    assert "reviewer model equals author model" in pair.validate_report(root, report)


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
