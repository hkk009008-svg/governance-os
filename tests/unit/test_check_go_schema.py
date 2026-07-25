from __future__ import annotations

import hashlib
import json
import os
import subprocess
from collections import Counter
from pathlib import Path

import pytest

import check_go_schema as schema
import compact_pair_loop as pair


def _manifest(*entries: tuple[str, bytes]) -> dict[str, object]:
    return {
        "schema_version": "lane-v-report-pre-v3-baseline/v1",
        "reports": [
            {"path": path, "sha256": hashlib.sha256(raw).hexdigest()}
            for path, raw in entries
        ],
    }


def _git(root: Path, *arguments: str) -> str:
    completed = subprocess.run(
        ["env", "-u", "GIT_INDEX_FILE", "git", *arguments],
        cwd=root,
        check=True,
        capture_output=True,
        text=True,
    )
    return completed.stdout.strip()


def _retired_pair(
    tmp_path: Path, *, retire: bool = True
) -> tuple[Path, schema.RawReport, dict[str, object], Path]:
    root = tmp_path / "pipeline"
    root.mkdir()
    _git(root, "init", "-q")
    _git(root, "config", "user.name", "Retired Review Test")
    _git(root, "config", "user.email", "retired-review@example.invalid")
    (root / "README.md").write_text("pipeline\n", encoding="utf-8")
    _git(root, "add", "README.md")
    _git(root, "commit", "-q", "-m", "chore: pipeline base")

    target = tmp_path / "reviewed-target"
    target.mkdir()
    _git(target, "init", "-q")
    _git(target, "config", "user.name", "Retired Review Test")
    _git(target, "config", "user.email", "retired-review@example.invalid")
    (target / "feature.py").write_text("VALUE = 1\n", encoding="utf-8")
    _git(target, "add", "feature.py")
    _git(target, "commit", "-q", "-m", "chore: target base")
    base = _git(target, "rev-parse", "HEAD")
    (target / "feature.py").write_text("VALUE = 2\n", encoding="utf-8")
    _git(target, "add", "feature.py")
    _git(target, "commit", "-q", "-m", "feat: target change")
    head = _git(target, "rev-parse", "HEAD")

    request_path = (
        "coordination/mailbox/sent/"
        "2026-07-23T11-10-00Z-director-to-operator-verify-request.md"
    )
    request = root / request_path
    request.parent.mkdir(parents=True)
    request.write_text(
        f"""\
# Director -> Operator: verify retired target fixture

**When:** 2026-07-23T11:10:00Z · **From:** director (online)

Event type: verify-request
Reviewed repository: {target.as_posix()}
Reviewed head: {head}
Reviewed base: {base}
Author seat: director
Author model: gpt-5.6-sol
Assigned operator: operator

## Outcome

Verify the exact synthetic target range.

## Finding Refs

Cursor at send: 0
""",
        encoding="utf-8",
    )
    _git(root, "add", request_path)
    _git(root, "commit", "-q", "-m", "coord: request review")
    trigger = _git(root, "rev-parse", "HEAD")

    report_path = (
        "coordination/mailbox/sent/"
        "2026-07-23T11-11-00Z-operator-to-director-verification-report.md"
    )
    report = root / report_path
    report.write_text(
        f"""\
# Operator -> Director: retired target fixture verdict

**When:** 2026-07-23T11:11:00Z · **From:** operator (online)

Event type: verification-report
VERDICT: GO
Verification request: {request_path}@{trigger}
Reviewed repository: {target.as_posix()}
Reviewed head: {head}
Reviewed base: {base}
Reviewer seat: operator
Reviewer model: gpt-5.6-terra

## Finding Refs

## Finding Dispositions

## Evidence

$ synthetic exact-range review
→ exact range satisfies the requested outcome

## Findings

None.

Cursor at send: 0
""",
        encoding="utf-8",
    )
    raw = report.read_bytes()
    request_raw = request.read_bytes()
    entry = {
        "report_path": report_path,
        "report_sha256": hashlib.sha256(raw).hexdigest(),
        "request_ref": f"{request_path}@{trigger}",
        "request_sha256": hashlib.sha256(request_raw).hexdigest(),
        "reviewed_repository": target.as_posix(),
        "reviewed_base": base,
        "reviewed_head": head,
    }
    retired_manifest = {
        "schema_version": "retired-review-targets/v1",
        "retirement_contract": (
            "coordination/mailbox/sent/"
            "2026-07-23T11-03-36Z-director-to-all-coordination.md@"
            "66809189455da6f7bbf659cf019c6589c623b854"
        ),
        "retired_worktree_shells": [],
        "entries": [entry],
    }
    if retire:
        target.rename(tmp_path / "retired-target")
    return root, schema.RawReport(report_path, raw), retired_manifest, target


def test_go_evidence_requires_command_and_output() -> None:
    valid = """\
# Operator → All: report

VERDICT: GO

## Evidence
$ pytest -q
→ 1 passed
"""
    assert schema.go_report_violations([("valid.md", valid)]) == []

    violations = schema.go_report_violations(
        [("invalid.md", valid.replace("→ 1 passed\n", ""))]
    )
    assert any("output" in item for item in violations)


def test_current_compact_go_does_not_require_redundant_commit_or_logs_prose() -> None:
    path = (
        "coordination/mailbox/sent/"
        "2026-07-18T11-53-07Z-operator-to-director-verification-report.md"
    )
    raw = (schema.ROOT / path).read_bytes()
    parsed = pair.parse_verification_report(schema.ROOT, path)

    assert pair.validate_report(schema.ROOT, parsed) == []
    assert schema.repository_report_violations(
        schema.ROOT,
        [schema.RawReport(path, raw)],
        _manifest(),
    ) == []


@pytest.mark.parametrize("verdict", ("NITS", "FAIL"))
def test_non_go_report_does_not_claim_success_evidence(verdict: str) -> None:
    assert schema.go_report_violations(
        [("truthful.md", f"VERDICT: {verdict}\n")]
    ) == []


def test_pre_v3_bytes_are_accepted_only_by_exact_manifest_path_and_digest(
    tmp_path: Path,
) -> None:
    path = (
        "coordination/mailbox/sent/"
        "2026-07-01T00-00-00Z-operator-to-all-verification-report.md"
    )
    raw = b"# historical\n\nVERDICT: FAIL\n"
    manifest = _manifest((path, raw))

    assert schema.repository_report_violations(
        tmp_path, [schema.RawReport(path, raw)], manifest
    ) == []
    assert schema.repository_report_violations(
        tmp_path, [schema.RawReport(path, raw + b"changed\n")], manifest
    )
    assert schema.repository_report_violations(
        tmp_path,
        [schema.RawReport(path.replace("00-00-00", "00-00-01"), raw)],
        manifest,
    )


def test_manifest_rejects_duplicate_paths_and_digests(tmp_path: Path) -> None:
    path = tmp_path / "manifest.json"
    digest = "a" * 64
    path.write_text(
        json.dumps(
            {
                "schema_version": "lane-v-report-pre-v3-baseline/v1",
                "reports": [
                    {"path": "coordination/mailbox/sent/a-verification-report.md", "sha256": digest},
                    {"path": "coordination/mailbox/sent/a-verification-report.md", "sha256": digest},
                ],
            }
        ),
        encoding="utf-8",
    )

    with pytest.raises(schema.BaselineGenerationError, match="duplicate"):
        schema.load_baseline_manifest(path)


def test_filesystem_scan_reads_regular_reports_and_rejects_symlinks(
    tmp_path: Path,
) -> None:
    sent = tmp_path / "coordination/mailbox/sent"
    sent.mkdir(parents=True)
    report = sent / "2026-07-01T00-00-00Z-operator-to-all-verification-report.md"
    report.write_text("VERDICT: FAIL\n", encoding="utf-8")

    assert [item.relative_path for item in schema.scan_repository_reports(tmp_path)] == [
        report.relative_to(tmp_path).as_posix()
    ]

    report.unlink()
    outside = tmp_path / "outside"
    outside.write_text("VERDICT: GO\n", encoding="utf-8")
    report.symlink_to(outside)
    with pytest.raises(OSError):
        schema.scan_repository_reports(tmp_path)

def test_live_mailbox_is_valid_against_frozen_history_and_compact_current_rules() -> None:
    reports = schema.scan_repository_reports(schema.ROOT)
    manifest = schema.load_baseline_manifest(schema.DEFAULT_MANIFEST)
    retired = schema.load_retired_review_targets(schema.DEFAULT_RETIRED_MANIFEST)

    assert schema.repository_report_violations(
        schema.ROOT, reports, manifest, retired
    ) == []
    assert len(retired["entries"]) == 38
    assert Counter(
        entry["reviewed_repository"] for entry in retired["entries"]
    ) == {
        "/Users/hyungkoookkim/evidence-ledger": 26,
        (
            "/Users/hyungkoookkim/evidence-ledger/.worktrees/"
            "codex-ppl-offer-decision-m1"
        ): 11,
        (
            "/Users/hyungkoookkim/Pipeline/.worktrees/"
            "evidence-ledger-workbook-refresh-0720"
        ): 1,
    }


def test_exact_retired_review_binding_passes_without_restoring_target(
    tmp_path: Path,
) -> None:
    root, report, retired, _target = _retired_pair(tmp_path)

    assert schema.repository_report_violations(
        root, [report], _manifest(), retired
    ) == []


@pytest.mark.parametrize(
    ("field", "replacement"),
    (
        (
            "report_path",
            "coordination/mailbox/sent/"
            "2026-07-23T11-11-01Z-operator-to-director-verification-report.md",
        ),
        ("report_sha256", "0" * 64),
        (
            "request_ref",
            "coordination/mailbox/sent/"
            "2026-07-23T11-10-00Z-director-to-operator-verify-request.md@"
            + "f" * 40,
        ),
        ("request_sha256", "0" * 64),
        ("reviewed_repository", "/definitely/not/the-reviewed-target"),
        ("reviewed_base", "0" * 40),
        ("reviewed_head", "f" * 40),
    ),
)
def test_retired_review_binding_fails_on_every_exact_field_drift(
    tmp_path: Path, field: str, replacement: str
) -> None:
    root, report, retired, _target = _retired_pair(tmp_path)
    assert schema.repository_report_violations(
        root, [report], _manifest(), retired
    ) == []

    changed = json.loads(json.dumps(retired))
    changed["entries"][0][field] = replacement
    assert schema.repository_report_violations(
        root, [report], _manifest(), changed
    )


def test_retired_review_report_byte_drift_fails_closed(tmp_path: Path) -> None:
    root, report, retired, _target = _retired_pair(tmp_path)
    changed = schema.RawReport(report.relative_path, report.raw + b"\n")

    assert schema.repository_report_violations(
        root, [changed], _manifest(), retired
    )


@pytest.mark.parametrize("case", ("model", "finding", "evidence"))
def test_matching_digest_cannot_bless_structurally_invalid_retired_report(
    tmp_path: Path, case: str
) -> None:
    root, report, retired, _target = _retired_pair(tmp_path)
    text = report.raw.decode("utf-8")
    if case == "model":
        text = text.replace(
            "Reviewer model: gpt-5.6-terra",
            "Reviewer model: gpt-5.6-sol",
        )
    elif case == "finding":
        finding = (
            "coordination/mailbox/sent/"
            "2026-07-23T11-03-36Z-director-to-all-coordination.md@"
            "66809189455da6f7bbf659cf019c6589c623b854"
        )
        text = text.replace(
            "## Finding Refs\n\n",
            f"## Finding Refs\n\n- {finding}\n\n",
        ).replace(
            "## Finding Dispositions\n\n",
            f"## Finding Dispositions\n\n- {finding}: addressed\n\n",
        )
    else:
        text = text.replace("→ exact range satisfies the requested outcome\n", "")
    changed_raw = text.encode("utf-8")
    (root / report.relative_path).write_bytes(changed_raw)
    retired["entries"][0]["report_sha256"] = hashlib.sha256(changed_raw).hexdigest()

    assert schema.repository_report_violations(
        root,
        [schema.RawReport(report.relative_path, changed_raw)],
        _manifest(),
        retired,
    )


def test_retired_review_path_reappearance_fails_closed(tmp_path: Path) -> None:
    root, report, retired, _target = _retired_pair(tmp_path, retire=False)

    assert schema.repository_report_violations(
        root, [report], _manifest(), retired
    )


def test_retired_worktree_shell_must_remain_non_live(tmp_path: Path) -> None:
    root, report, retired, target = _retired_pair(tmp_path)
    target.mkdir()
    retired["retired_worktree_shells"] = [target.as_posix()]

    assert schema.repository_report_violations(
        root, [report], _manifest(), retired
    ) == []

    _git(target, "init", "-q")
    assert schema.repository_report_violations(
        root, [report], _manifest(), retired
    )


def test_new_unlisted_unavailable_report_still_fails_closed(tmp_path: Path) -> None:
    root, report, retired, _target = _retired_pair(tmp_path)
    new_path = (
        "coordination/mailbox/sent/"
        "2026-07-23T11-12-00Z-operator-to-director-verification-report.md"
    )
    new_report = schema.RawReport(new_path, report.raw)

    assert schema.repository_report_violations(
        root, [report, new_report], _manifest(), retired
    )


def test_retired_manifest_rejects_malformed_and_duplicate_entries(
    tmp_path: Path,
) -> None:
    root, _report, retired, _target = _retired_pair(tmp_path)
    manifest_path = root / "retired.json"
    malformed = json.loads(json.dumps(retired))
    malformed["entries"][0]["wildcard"] = "*"
    manifest_path.write_text(json.dumps(malformed), encoding="utf-8")
    with pytest.raises(schema.RetiredReviewTargetsError):
        schema.load_retired_review_targets(manifest_path)

    duplicated = json.loads(json.dumps(retired))
    duplicated["entries"].append(duplicated["entries"][0])
    manifest_path.write_text(json.dumps(duplicated), encoding="utf-8")
    with pytest.raises(schema.RetiredReviewTargetsError, match="duplicate"):
        schema.load_retired_review_targets(manifest_path)


def test_report_compatibility_is_narrow_across_each_frozen_generation() -> None:
    pre_v3_path = (
        "coordination/mailbox/sent/"
        "2026-07-07T09-52-13Z-operator-to-all-verification-report.md"
    )
    historical_v3_path = (
        "coordination/mailbox/sent/"
        "2026-07-17T04-59-08Z-operator-to-all-verification-report.md"
    )
    verbose_compact_path = (
        "coordination/mailbox/sent/"
        "2026-07-17T13-17-10Z-operator-to-director-verification-report.md"
    )
    pre_v3 = (schema.ROOT / pre_v3_path).read_bytes()
    historical_v3 = (schema.ROOT / historical_v3_path).read_bytes()
    verbose_compact = (schema.ROOT / verbose_compact_path).read_bytes()

    assert schema.repository_report_violations(
        schema.ROOT,
        [schema.RawReport(pre_v3_path, pre_v3)],
        _manifest((pre_v3_path, pre_v3)),
    ) == []
    assert schema.repository_report_violations(
        schema.ROOT,
        [schema.RawReport(historical_v3_path, historical_v3)],
        _manifest(),
    ) == []
    assert schema.repository_report_violations(
        schema.ROOT,
        [schema.RawReport(verbose_compact_path, verbose_compact)],
        _manifest(),
    ) == []
    parsed = pair.parse_verification_report(schema.ROOT, verbose_compact_path)
    assert parsed.finding_refs == ()
    assert parsed.finding_dispositions == ()


def test_baseline_generation_surface_is_retired() -> None:
    assert not hasattr(schema, "generate_baseline")
    assert schema.main(["--generate-baseline", "elsewhere.json"]) != 0


def test_scan_rejects_fifo_without_blocking(tmp_path: Path) -> None:
    if not hasattr(os, "mkfifo"):
        pytest.skip("FIFO unavailable")
    sent = tmp_path / "coordination/mailbox/sent"
    sent.mkdir(parents=True)
    os.mkfifo(sent / "2026-07-01T00-00-00Z-operator-to-all-verification-report.md")

    with pytest.raises(OSError):
        schema.scan_repository_reports(tmp_path)


# An absolute path on the machine that authored the event. It must never exist
# on the machine running these tests — that is the whole point of the case.
AUTHORING_MACHINE_PATH = "/nonexistent-authoring-machine/pipeline"


def _pair_naming_an_unavailable_repository(
    tmp_path: Path, *, reachable: bool
) -> tuple[Path, schema.RawReport]:
    """Build a pair whose Reviewed repository path does not exist here.

    This is the shape every event authored on a developer machine has once it
    reaches CI: the reviewed range is in *this* repository, but the recorded
    path points at a checkout that only existed where the review ran. With
    ``reachable`` false the recorded range is absent from this repository too,
    which must still fail.
    """
    root = tmp_path / "pipeline"
    root.mkdir()
    _git(root, "init", "-q")
    _git(root, "config", "user.name", "Portability Test")
    _git(root, "config", "user.email", "portability@example.invalid")
    (root / "feature.py").write_text("VALUE = 1\n", encoding="utf-8")
    _git(root, "add", "feature.py")
    _git(root, "commit", "-q", "-m", "chore: base")
    base = _git(root, "rev-parse", "HEAD")
    (root / "feature.py").write_text("VALUE = 2\n", encoding="utf-8")
    _git(root, "add", "feature.py")
    _git(root, "commit", "-q", "-m", "feat: reviewed change")
    head = _git(root, "rev-parse", "HEAD")
    if not reachable:
        base, head = "0" * 40, "f" * 40

    request_path = (
        "coordination/mailbox/sent/"
        "2026-07-25T10-00-00Z-director-to-operator-verify-request.md"
    )
    request = root / request_path
    request.parent.mkdir(parents=True)
    request.write_text(
        f"""\
# Director -> Operator: portability fixture

**When:** 2026-07-25T10:00:00Z · **From:** director (online)

Event type: verify-request
Reviewed repository: {AUTHORING_MACHINE_PATH}
Reviewed head: {head}
Reviewed base: {base}
Author seat: director
Author model: gpt-5.6-sol
Assigned operator: operator

## Outcome

Verify the exact range recorded against an absent authoring checkout.

## Finding Refs

Cursor at send: 0
""",
        encoding="utf-8",
    )
    _git(root, "add", request_path)
    _git(root, "commit", "-q", "-m", "coord: request review")
    trigger = _git(root, "rev-parse", "HEAD")

    report_path = (
        "coordination/mailbox/sent/"
        "2026-07-25T10-01-00Z-operator-to-director-verification-report.md"
    )
    report = root / report_path
    report.write_text(
        f"""\
# Operator -> Director: portability fixture verdict

**When:** 2026-07-25T10:01:00Z · **From:** operator (online)

Event type: verification-report
VERDICT: GO
Verification request: {request_path}@{trigger}
Reviewed repository: {AUTHORING_MACHINE_PATH}
Reviewed head: {head}
Reviewed base: {base}
Reviewer seat: operator
Reviewer model: gpt-5.6-terra

## Finding Refs

## Finding Dispositions

## Evidence

$ synthetic exact-range review
→ exact range satisfies the requested outcome

## Findings

None.

Cursor at send: 0
""",
        encoding="utf-8",
    )
    return root, schema.RawReport(report_path, report.read_bytes())


def test_authoring_machine_path_is_absent_so_the_fixtures_are_not_vacuous() -> None:
    # If this path ever exists, both tests below stop exercising the absent
    # -checkout branch and start passing for the ordinary reason instead.
    assert not Path(AUTHORING_MACHINE_PATH).exists()


def test_pair_naming_an_absent_authoring_checkout_still_validates(
    tmp_path: Path,
) -> None:
    root, report = _pair_naming_an_unavailable_repository(tmp_path, reachable=True)

    assert schema.repository_report_violations(root, [report], _manifest(), None) == []


def test_absent_authoring_checkout_does_not_skip_range_validation(
    tmp_path: Path,
) -> None:
    root, report = _pair_naming_an_unavailable_repository(tmp_path, reachable=False)

    violations = schema.repository_report_violations(root, [report], _manifest(), None)
    assert [item for item in violations if "request binding invalid" in item], violations


def test_retired_worktree_shell_absent_here_is_accepted(tmp_path: Path) -> None:
    """The CI case: the inert shell exists only where the target was retired.

    `git worktree remove` leaves the shell behind on one machine. A runner or a
    fresh clone never had it, and refusing the binding there made this branch
    pass only on the machine that did the retiring.
    """
    root, report, retired, target = _retired_pair(tmp_path)
    retired["retired_worktree_shells"] = [target.as_posix()]
    assert not target.exists()

    assert schema.repository_report_violations(
        root, [report], _manifest(), retired
    ) == []


def test_absent_shell_still_fails_when_the_target_reappears(tmp_path: Path) -> None:
    root, report, retired, target = _retired_pair(tmp_path)
    retired["retired_worktree_shells"] = [target.as_posix()]
    target.mkdir()
    _git(target, "init", "-q")

    assert schema.repository_report_violations(root, [report], _manifest(), retired)
