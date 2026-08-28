#!/usr/bin/env python3
"""Validate frozen historical report bytes and current compact pair reports."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import stat
import sys

import git_runner
from dataclasses import dataclass
from pathlib import Path, PurePosixPath

import compact_pair_loop


ROOT = Path(__file__).resolve().parent.parent
DEFAULT_MANIFEST = ROOT / "pipeline/baselines/lane_v_reports_pre_v3.json"
DEFAULT_RETIRED_MANIFEST = ROOT / "pipeline/baselines/retired_review_targets.json"
MANIFEST_SCHEMA = "lane-v-report-pre-v3-baseline/v1"
RETIRED_MANIFEST_SCHEMA = "retired-review-targets/v1"
RETIREMENT_CONTRACT_REF = (
    "coordination/mailbox/sent/"
    "2026-07-23T11-03-36Z-director-to-all-coordination.md@"
    "66809189455da6f7bbf659cf019c6589c623b854"
)
HISTORICAL_V3_CUTOFF = "a546f059fc8f3e324cf102e242bdc9840de93880"
MAX_MANIFEST_BYTES = 1_048_576

VERDICT_GO_RE = re.compile(r"^VERDICT: GO$", re.MULTILINE)
EVIDENCE_RE = re.compile(r"^## Evidence\s*$", re.MULTILINE)
COMMAND_RE = re.compile(r"^\$ \S", re.MULTILINE)
OUTPUT_RE = re.compile(r"^→ \S", re.MULTILINE)


class BaselineGenerationError(RuntimeError):
    """The frozen historical manifest is malformed or unavailable."""


class RetiredReviewTargetsError(RuntimeError):
    """The exact retired-review manifest is malformed or unavailable."""


@dataclass(frozen=True)
class RawReport:
    relative_path: str
    raw: bytes


def _strict_object(pairs: list[tuple[str, object]]) -> dict[str, object]:
    value: dict[str, object] = {}
    for key, item in pairs:
        if key in value:
            raise BaselineGenerationError(f"duplicate manifest key: {key}")
        value[key] = item
    return value


def _strict_retired_object(pairs: list[tuple[str, object]]) -> dict[str, object]:
    value: dict[str, object] = {}
    for key, item in pairs:
        if key in value:
            raise RetiredReviewTargetsError(f"duplicate retired manifest key: {key}")
        value[key] = item
    return value


def _read_regular(path: Path, *, maximum: int) -> bytes:
    nofollow = getattr(os, "O_NOFOLLOW", 0)
    if not nofollow:
        raise OSError("O_NOFOLLOW unavailable")
    descriptor = os.open(
        path,
        os.O_RDONLY
        | nofollow
        | getattr(os, "O_CLOEXEC", 0)
        | getattr(os, "O_NONBLOCK", 0),
    )
    try:
        opened = os.fstat(descriptor)
        if not stat.S_ISREG(opened.st_mode) or opened.st_size > maximum:
            raise OSError(f"not one bounded regular file: {path}")
        raw = os.read(descriptor, opened.st_size + 1)
        after = os.fstat(descriptor)
        if len(raw) != opened.st_size or (opened.st_dev, opened.st_ino, opened.st_size) != (
            after.st_dev,
            after.st_ino,
            after.st_size,
        ):
            raise OSError(f"file changed while reading: {path}")
        return raw
    finally:
        os.close(descriptor)


def parse_baseline_manifest_bytes(raw: bytes) -> dict[str, object]:
    """Validate committed baseline bytes without consulting the worktree."""

    if len(raw) > MAX_MANIFEST_BYTES:
        raise BaselineGenerationError("historical manifest exceeds size limit")
    try:
        value = json.loads(raw, object_pairs_hook=_strict_object)
    except (json.JSONDecodeError, UnicodeDecodeError) as exc:
        raise BaselineGenerationError(f"invalid historical manifest: {exc}") from exc
    if not isinstance(value, dict) or value.get("schema_version") != MANIFEST_SCHEMA:
        raise BaselineGenerationError("invalid historical manifest schema")
    entries = value.get("reports")
    if not isinstance(entries, list):
        raise BaselineGenerationError("historical manifest reports must be a list")
    paths: set[str] = set()
    digests: set[str] = set()
    for entry in entries:
        if not isinstance(entry, dict) or set(entry) != {"path", "sha256"}:
            raise BaselineGenerationError("invalid historical manifest entry")
        report_path = entry["path"]
        digest = entry["sha256"]
        if (
            not isinstance(report_path, str)
            or not report_path.startswith("coordination/mailbox/sent/")
            or not report_path.endswith("-verification-report.md")
            or PurePosixPath(report_path).as_posix() != report_path
            or not isinstance(digest, str)
            or re.fullmatch(r"[0-9a-f]{64}", digest) is None
        ):
            raise BaselineGenerationError("invalid historical manifest path or digest")
        if report_path in paths or digest in digests:
            raise BaselineGenerationError("duplicate historical manifest path or digest")
        paths.add(report_path)
        digests.add(digest)
    return value


def load_baseline_manifest(path: Path = DEFAULT_MANIFEST) -> dict[str, object]:
    raw = _read_regular(path, maximum=MAX_MANIFEST_BYTES)
    return parse_baseline_manifest_bytes(raw)


def _validate_retired_review_targets(value: object) -> dict[str, object]:
    if not isinstance(value, dict) or set(value) != {
        "schema_version",
        "retirement_contract",
        "retired_worktree_shells",
        "entries",
    }:
        raise RetiredReviewTargetsError("invalid retired manifest object")
    if value["schema_version"] != RETIRED_MANIFEST_SCHEMA:
        raise RetiredReviewTargetsError("invalid retired manifest schema")
    if value["retirement_contract"] != RETIREMENT_CONTRACT_REF:
        raise RetiredReviewTargetsError("retired manifest contract drift")
    retired_worktree_shells = value["retired_worktree_shells"]
    if (
        not isinstance(retired_worktree_shells, list)
        or len(retired_worktree_shells) != len(set(retired_worktree_shells))
    ):
        raise RetiredReviewTargetsError("invalid retired worktree shells")
    for shell in retired_worktree_shells:
        if (
            not isinstance(shell, str)
            or not Path(shell).is_absolute()
            or Path(shell).as_posix() != shell
            or any(component in {"", ".", ".."} for component in Path(shell).parts)
            or any(character in shell for character in "*?[")
        ):
            raise RetiredReviewTargetsError("invalid retired worktree shell")
    entries = value["entries"]
    if not isinstance(entries, list):
        raise RetiredReviewTargetsError("retired manifest entries must be a list")
    expected_keys = {
        "report_path",
        "report_sha256",
        "request_ref",
        "request_sha256",
        "reviewed_repository",
        "reviewed_base",
        "reviewed_head",
    }
    report_paths: set[str] = set()
    request_refs: set[str] = set()
    reviewed_repositories: set[str] = set()
    for entry in entries:
        if not isinstance(entry, dict) or set(entry) != expected_keys:
            raise RetiredReviewTargetsError("invalid retired manifest entry")
        if not all(isinstance(entry[key], str) for key in expected_keys):
            raise RetiredReviewTargetsError("retired manifest fields must be strings")
        report_path = entry["report_path"]
        report_digest = entry["report_sha256"]
        request_ref = entry["request_ref"]
        request_path, separator, request_commit = request_ref.rpartition("@")
        request_digest = entry["request_sha256"]
        repository = entry["reviewed_repository"]
        repository_path = Path(repository)
        base = entry["reviewed_base"]
        head = entry["reviewed_head"]
        if compact_pair_loop.REPORT_RE.fullmatch(report_path) is None:
            raise RetiredReviewTargetsError("invalid retired report path")
        if (
            re.fullmatch(r"[0-9a-f]{64}", report_digest) is None
            or re.fullmatch(r"[0-9a-f]{64}", request_digest) is None
        ):
            raise RetiredReviewTargetsError("invalid retired artifact digest")
        if (
            not separator
            or compact_pair_loop.REQUEST_RE.fullmatch(request_path) is None
            or compact_pair_loop.SHA_RE.fullmatch(request_commit) is None
        ):
            raise RetiredReviewTargetsError("invalid retired request ref")
        if (
            not repository_path.is_absolute()
            or repository_path.as_posix() != repository
            or any(component in {"", ".", ".."} for component in repository_path.parts)
            or any(character in repository for character in "*?[")
        ):
            raise RetiredReviewTargetsError("invalid retired repository path")
        if (
            compact_pair_loop.SHA_RE.fullmatch(base) is None
            or compact_pair_loop.SHA_RE.fullmatch(head) is None
            or base == head
        ):
            raise RetiredReviewTargetsError("invalid retired reviewed range")
        if report_path in report_paths or request_ref in request_refs:
            raise RetiredReviewTargetsError("duplicate retired manifest entry")
        report_paths.add(report_path)
        request_refs.add(request_ref)
        reviewed_repositories.add(repository)
    if not set(retired_worktree_shells).issubset(reviewed_repositories):
        raise RetiredReviewTargetsError(
            "retired worktree shell has no exact manifest entry"
        )
    return value


def load_retired_review_targets(
    path: Path = DEFAULT_RETIRED_MANIFEST,
) -> dict[str, object]:
    raw = _read_regular(path, maximum=MAX_MANIFEST_BYTES)
    try:
        value = json.loads(raw, object_pairs_hook=_strict_retired_object)
    except (json.JSONDecodeError, UnicodeDecodeError) as exc:
        raise RetiredReviewTargetsError(f"invalid retired manifest: {exc}") from exc
    return _validate_retired_review_targets(value)


def _canonical_scan_directory(root: Path, directory: Path | None) -> tuple[Path, str]:
    root = root.resolve()
    expected = root / "coordination/mailbox/sent"
    selected = expected if directory is None else directory
    if not selected.is_absolute():
        selected = root / selected
    try:
        relative = selected.relative_to(root).as_posix()
    except ValueError as exc:
        raise OSError("report directory is outside repository") from exc
    if relative != "coordination/mailbox/sent":
        raise OSError("report directory must be coordination/mailbox/sent")
    current = root
    for component in ("coordination", "mailbox", "sent"):
        current = current / component
        if current.is_symlink():
            raise OSError("report directory traverses symlink")
    return selected, relative


def scan_repository_reports(root: Path, directory: Path | None = None) -> list[RawReport]:
    selected, relative = _canonical_scan_directory(root, directory)
    if not selected.exists():
        return []
    reports: list[RawReport] = []
    for name in sorted(os.listdir(selected)):
        if not name.endswith("-verification-report.md"):
            continue
        raw = _read_regular(selected / name, maximum=compact_pair_loop.MAX_EVENT_BYTES)
        reports.append(RawReport(f"{relative}/{name}", raw))
    return reports


def _git_blob(root: Path, commit: str, path: str) -> bytes | None:
    completed = git_runner.run_git(
        root, ("show", f"{commit}:{path}"), mode="authority"
    )
    return completed.stdout if completed.returncode == 0 else None


def _exact_historical_v3(root: Path, report: RawReport) -> bool:
    if b"Verification schema: lane-v-report/v3" not in report.raw:
        return False
    return _git_blob(root, HISTORICAL_V3_CUTOFF, report.relative_path) == report.raw


def _evidence_block(text: str) -> str:
    match = EVIDENCE_RE.search(text)
    if match is None:
        return ""
    tail = text[match.end() :]
    next_heading = re.search(r"^## \S", tail, re.MULTILINE)
    return text[match.start() : match.end() + (next_heading.start() if next_heading else len(tail))]


def go_report_violations(named_reports: list[tuple[str, str]]) -> list[str]:
    violations: list[str] = []
    for name, text in named_reports:
        if VERDICT_GO_RE.search(text) is None:
            continue
        evidence = _evidence_block(text)
        if not evidence:
            violations.append(f"{name}: GO missing Evidence section")
        if COMMAND_RE.search(evidence) is None:
            violations.append(f"{name}: GO evidence missing command")
        if OUTPUT_RE.search(evidence) is None:
            violations.append(f"{name}: GO evidence missing output")
        if "wave_gate_check" in evidence and not re.search(
            r"(?:--runxfail|\b[0-9]+ (?:passed|failed|xfailed|xpassed|error)\b)",
            evidence,
        ):
            violations.append(f"{name}: wave gate is not executed regression evidence")
    return violations


def _retired_report_violations(
    root: Path,
    report: RawReport,
    entry: dict[str, str],
    retired_worktree_shells: frozenset[str],
) -> list[str]:
    prefix = f"{report.relative_path}: retired binding"
    violations: list[str] = []
    if hashlib.sha256(report.raw).hexdigest() != entry["report_sha256"]:
        violations.append(f"{prefix} report digest drift")
    absolute = root / report.relative_path
    try:
        if absolute.read_bytes() != report.raw:
            violations.append(f"{prefix} scanned report bytes changed")
        parsed = compact_pair_loop.parse_verification_report(root, absolute)
    except (OSError, UnicodeError, compact_pair_loop.CompactPairError) as exc:
        return violations + [f"{prefix} invalid report: {exc}"]

    request_ref = f"{parsed.request_path}@{parsed.request_commit}"
    exact_report_fields = {
        "request_ref": request_ref,
        "reviewed_repository": parsed.reviewed_repository,
        "reviewed_base": parsed.reviewed_base,
        "reviewed_head": parsed.reviewed_head,
    }
    for field, observed in exact_report_fields.items():
        if observed != entry[field]:
            violations.append(f"{prefix} {field} drift")

    request_raw = _git_blob(root, parsed.request_commit, parsed.request_path)
    if request_raw is None:
        violations.append(f"{prefix} request ref is unavailable")
    elif hashlib.sha256(request_raw).hexdigest() != entry["request_sha256"]:
        violations.append(f"{prefix} request digest drift")

    structure = compact_pair_loop.validate_report_structure(root, parsed)
    # These bytes are already bound by exact report/request digests in the
    # retired manifest. NITS predated the current success-outcome restriction;
    # reapplying that later rule would rewrite history rather than validate it.
    if parsed.verdict == "NITS":
        structure = [
            item for item in structure
            if item != "NITS cannot carry unresolved hard-boundary findings"
        ]
    violations.extend(f"{prefix} {item}" for item in structure)
    try:
        request = compact_pair_loop.parse_verify_request_structure(
            root, parsed.request_path, parsed.request_commit
        )
    except compact_pair_loop.CompactPairError as exc:
        violations.append(f"{prefix} invalid request: {exc}")
    else:
        exact_request_fields = {
            "reviewed_repository": request.reviewed_repository,
            "reviewed_base": request.reviewed_base,
            "reviewed_head": request.reviewed_head,
        }
        for field, observed in exact_request_fields.items():
            if observed != entry[field]:
                violations.append(f"{prefix} request {field} drift")

    repository = Path(entry["reviewed_repository"])
    if repository.as_posix() in retired_worktree_shells:
        try:
            metadata = os.lstat(repository)
        except FileNotFoundError:
            # A shell is the inert directory `git worktree remove` leaves on the
            # machine that retired the target. No other machine ever created it,
            # so demanding it exist made this branch pass only where the
            # retirement happened. Absence is accepted for the same reason the
            # non-shell branch below accepts it, and it settles the question
            # this check actually asks — whether the target came back — more
            # firmly than an inert directory does: nothing is there to be live.
            pass
        except OSError as exc:
            violations.append(f"{prefix} retired worktree shell drift: {exc}")
        else:
            if not stat.S_ISDIR(metadata.st_mode):
                violations.append(f"{prefix} retired worktree shell is not a directory")
            else:
                # Ceiling-pinned: the probe asks whether ``repository`` is
                # itself live. Without the pin, a retired shell directory
                # inside a real checkout reports the enclosing repository
                # and produces a false "reappeared" violation.
                live = git_runner.run_git(
                    repository,
                    ("rev-parse", "--show-toplevel"),
                    mode="authority",
                )
                if live.returncode == 0:
                    violations.append(
                        f"{prefix} reviewed repository has reappeared"
                    )
    else:
        try:
            os.lstat(repository)
        except FileNotFoundError:
            pass
        except OSError as exc:
            violations.append(f"{prefix} target absence is not provable: {exc}")
        else:
            violations.append(f"{prefix} reviewed repository has reappeared")

    try:
        text = report.raw.decode("utf-8")
    except UnicodeDecodeError as exc:
        violations.append(f"{prefix} report is not UTF-8: {exc}")
    else:
        violations.extend(go_report_violations([(report.relative_path, text)]))
    return violations


def repository_report_violations(
    root: Path,
    reports: list[RawReport],
    manifest: dict[str, object],
    retired_manifest: dict[str, object] | None = None,
) -> list[str]:
    entries = manifest.get("reports")
    if manifest.get("schema_version") != MANIFEST_SCHEMA or not isinstance(entries, list):
        return ["invalid historical manifest"]
    expected = {entry["path"]: entry["sha256"] for entry in entries if isinstance(entry, dict)}
    observed = {report.relative_path: report for report in reports}
    violations = [f"historical report missing: {path}" for path in expected.keys() - observed.keys()]
    retired_entries: dict[str, dict[str, str]] = {}
    if retired_manifest is not None:
        try:
            validated_retired = _validate_retired_review_targets(retired_manifest)
        except RetiredReviewTargetsError as exc:
            return violations + [f"invalid retired review targets: {exc}"]
        retired_entries = {
            entry["report_path"]: entry
            for entry in validated_retired["entries"]
            if isinstance(entry, dict)
        }
        retired_worktree_shells = frozenset(
            validated_retired["retired_worktree_shells"]
        )
        violations.extend(
            f"retired report missing: {path}"
            for path in retired_entries.keys() - observed.keys()
        )
    for report in reports:
        digest = hashlib.sha256(report.raw).hexdigest()
        if report.relative_path in expected:
            if digest != expected[report.relative_path]:
                violations.append(f"historical baseline drift: {report.relative_path}")
            continue
        if _exact_historical_v3(root, report):
            continue
        retired_entry = retired_entries.get(report.relative_path)
        if retired_entry is not None:
            violations.extend(
                _retired_report_violations(
                    root, report, retired_entry, retired_worktree_shells
                )
            )
            continue
        absolute = root / report.relative_path
        try:
            if absolute.read_bytes() != report.raw:
                raise compact_pair_loop.CompactPairError("scanned bytes changed")
            parsed = compact_pair_loop.parse_verification_report(root, absolute)
            violations.extend(
                f"{report.relative_path}: {item}"
                for item in compact_pair_loop.validate_report(root, parsed)
            )
            text = report.raw.decode("utf-8")
        except (OSError, UnicodeError, compact_pair_loop.CompactPairError) as exc:
            violations.append(f"{report.relative_path}: invalid compact report: {exc}")
            continue
        violations.extend(go_report_violations([(report.relative_path, text)]))
    return violations


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="check_go_schema.py")
    parser.add_argument("directory", nargs="?")
    arguments, unknown = parser.parse_known_args(argv)
    if unknown:
        print("GO-SCHEMA CHECK — FAIL: retired option: " + " ".join(unknown))
        return 1
    try:
        directory = Path(arguments.directory) if arguments.directory else None
        reports = scan_repository_reports(ROOT, directory)
        manifest = load_baseline_manifest()
        retired_manifest = load_retired_review_targets()
        violations = repository_report_violations(
            ROOT, reports, manifest, retired_manifest
        )
    except (
        OSError,
        UnicodeError,
        BaselineGenerationError,
        RetiredReviewTargetsError,
    ) as exc:
        print(f"GO-SCHEMA CHECK — FAIL: {exc}")
        return 1
    if violations:
        print(f"GO-SCHEMA CHECK — FAIL: {len(violations)} violation(s)")
        for violation in violations:
            print(f"  ! {violation}")
        return 1
    print(
        "GO-SCHEMA CHECK — PASS: "
        f"{len(reports)} report(s) passed frozen-history and compact-pair validation."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
